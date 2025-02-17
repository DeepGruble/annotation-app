from streamlit_drawable_canvas import st_canvas
from enum import Enum
import os
import streamlit as st
from PIL import Image
from colormaps import *
from streamlit_theme import st_theme
import pandas as pd
from st_aggrid import GridOptionsBuilder, AgGrid, JsCode
from st_aggrid.shared import ColumnsAutoSizeMode

from io import BytesIO
import base64



class ImgeType(Enum):
    BITEWING = "bitewing"
    COLOR_PANORAMIC = "color_panoramic"
    COLOR_ZOOM = "color_zoom"
    PANORAMIC = "panoramic"
    PERIAPICAL = "periapical"
    
    
def pil_image_to_data_url(img):
    """
    Convert a PIL image to a data URL.
    """

    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"
    
    
# TODO: This value depends on the page entered by the user
IMAGE_TYPE = ImgeType.COLOR_PANORAMIC

# Has to be set as the first streamlit command
st.set_page_config(layout="wide", page_title=f"Numbering Tool - {IMAGE_TYPE.value}")

# Detect whicj theme is being used
try:
    theme = st_theme()["base"]
    theme_colors = colormap_light if theme == "light" else colormap_dark
except:
    theme_colors = colormap_light

# Read the css style template
css_path = os.path.join(os.path.dirname(__file__), "style_template.css")
if os.path.exists(css_path):
    with open(css_path, "r") as f:
        css_template = f.read()
    css = css_template.format(**theme_colors)
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
else:
    st.warning("CSS template not found. Please check the path.")


base_dir = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(base_dir, "temp_images")
SAVE_PATH = "output"
if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)


def read_images(image_type=None):
    """
    Read images from the specified directory.
    :param image_type: The type of images to read
    """
    images = []
    image_paths = os.path.join(DATA_PATH, image_type.value) if image_type else DATA_PATH
    for image_file in os.listdir(image_paths):
        images.append(
            Image.open(os.path.join(image_paths, image_file)).convert("RGB")
        )
    return images

# Initialize the session state
if "images" not in st.session_state:
    # Read the images from the dataset
    st.session_state.images = read_images()
    st.session_state.current_image_index = 0
    st.session_state.annotation_df = pd.DataFrame(columns=["tooth_number", "left", "top", "width", "height", "cropped_image"])
    st.session_state.tooth_number = 1  # Default tooth number
    st.session_state.processed_object_count = 0
            

def get_current_image():
    """
    Get the current image from the list of images based on the current index.
    """
    if st.session_state.current_image_index < len(st.session_state.images):
        return st.session_state.images[st.session_state.current_image_index]
    else:
        return None



# ===============================================================
# Streamlit UI
# ===============================================================

# Sidebar for controls
with st.sidebar:
    
    st.markdown("### Progress")
    st.progress((st.session_state.current_image_index + 1) / len(st.session_state.images))
    st.write(f"Image {st.session_state.current_image_index + 1} of {len(st.session_state.images)}")
    
    st.divider()
    
    #  Create a grid of buttons for tooth selection
    st.markdown("### Tooth Selection")
    st.markdown("Select the tooth number to annotate:")
    
    st.markdown('<div class="tooth-buttons">', unsafe_allow_html=True)
    
    cols = st.columns(16)
    for i, tooth in enumerate(list(range(1, 33))):
        with cols[i % 16]:
            st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)
 
            if st.button(f"{tooth}", key=f"button{tooth}"):
                st.session_state.tooth_number = tooth
                print(f"Tooth {tooth} selected")
                # st.rerun()        
    st.markdown('</div>', unsafe_allow_html=True)  # Close the div wrapper
    
    st.divider()
    
    column_1, column_2 = st.columns(2)
    with column_1:
        if st.button("Submit", type="primary"):
            pass

    with column_2:
        if st.button("Skip", type="primary"):
            pass  # Add saving logic here


# Display current image and progress
current_image = get_current_image()
if current_image is not None:

    SCALE = 2.5
    
    TARGET_IMAGE_SIZE = 500
        
    resized_image = current_image.resize((TARGET_IMAGE_SIZE, TARGET_IMAGE_SIZE), Image.LANCZOS)
    print(f"Image size: {resized_image.size}")

    # Display the canvas with the overlayed image
    canvas_result = st_canvas(
        fill_color="",
        stroke_width=2,
        background_color="#FFFFFF",
        update_streamlit=True,
        stroke_color=theme_colors["primary"],
        background_image=current_image,
        width=TARGET_IMAGE_SIZE,
        height=TARGET_IMAGE_SIZE,
        drawing_mode="rect",
        key="canvas",
    )
            
    # Handle canvas result
    if canvas_result and canvas_result.json_data is not None:
        objects = canvas_result.json_data["objects"]
        new_objects = objects[st.session_state.processed_object_count:]
        
        for obj in new_objects:
            
            height, width = obj["height"], obj["width"]
            left, top = obj["left"], obj["top"]
            
            
            cropped_image = resized_image.crop((left, top, left + width, top + height))
            data_url = pil_image_to_data_url(cropped_image)
            
            row = {
                "tooth_number": st.session_state.tooth_number,
                "left": left,
                "top": top,
                "width": width,
                "height": height,
                "cropped_image": data_url,
            }
            # Add the row to the dataframe st.session_state.annotation_df
            st.session_state.annotation_df.loc[len(st.session_state.annotation_df)] = row
               
        st.session_state.processed_object_count = len(objects)
        
    st.divider()
    st.markdown("### Tooth Annotations")
    
    if not st.session_state.annotation_df.empty:
    
        print(st.session_state.annotation_df)
        
        # Create the cellRenderer for the image column
        render_image = JsCode('''
            function renderImage(params) {
                // Create a new image element
                var img = new Image();

                // Set the src property to the value of the cell (should be a URL pointing to an image)
                img.src = params.value;

                // Set the width and height of the image to 50 pixels
                img.width = 50;
                img.height = 50;

                // Return the image element
                return img;
            }
        '''
        )
        options_builder = GridOptionsBuilder.from_dataframe(st.session_state.annotation_df)
        options_builder.configure_column("cropped_image", cellRenderer=render_image)
        grid_options = options_builder.build()
        
        grid_options = AgGrid(
            st.session_state.annotation_df,
            allow_unsafe_jscode=True,
            gridOptions=grid_options,
            theme="streamlit",
            height=200, width=500
        )

 
else:
    st.warning("No images to display. Please check the image directory.")
    

        
        