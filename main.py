from streamlit_drawable_canvas import st_canvas
from enum import Enum
import os
import matplotlib.pyplot as plt
import streamlit as st
from PIL import Image
from colormaps import *
from streamlit_theme import st_theme


class ImgeType(Enum):
    BITEWING = "bitewing"
    COLOR_PANORAMIC = "color_panoramic"
    COLOR_ZOOM = "color_zoom"
    PANORAMIC = "panoramic"
    PERIAPICAL = "periapical"
    
    
# TODO: This value depends on the page entered by the user
IMAGE_TYPE = ImgeType.COLOR_PANORAMIC

# Has to be set as the first streamlit command
st.set_page_config(layout="wide", page_title=f"Numbering Tool - {IMAGE_TYPE.value}")

# Detect whicj theme is being used
theme = st_theme()["base"]
print(f"Current theme: {theme}")
if theme == "light":
    theme_colors = colormap_light
else:
    theme_colors = colormap_dark

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
    st.session_state.labels = []
    st.session_state.tooth_number = 1  # Default tooth number
    

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
                st.rerun()        
    st.markdown('</div>', unsafe_allow_html=True)  # Close the div wrapper



# Main content
#st.title("Numbering Annotation Tool")

# Display current image and progress
current_image = get_current_image()
if current_image is not None:

    SCALE = 2.5
    
    TARGET_IMAGE_SIZE = 500
        
    current_image.thumbnail((TARGET_IMAGE_SIZE, TARGET_IMAGE_SIZE), Image.LANCZOS)
    print(f"Image size: {current_image.size}")

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
    
    column_1, column_2 = st.columns(2)
    with column_1:
        if st.button("Submit", type="primary"):
            pass

    with column_2:
        if st.button("Skip", type="primary"):
            pass  # Add saving logic here
            
        

    # Handle canvas result
    if canvas_result and canvas_result.json_data is not None:
        objects = canvas_result.json_data["objects"]
        if objects:
            last_object = objects[-1]
            
            height = last_object["height"]
            width = last_object["width"]
            
            left = last_object["left"]
            top = last_object["top"]
            
            label = {
                "tooth_number": st.session_state.tooth_number,
                "left": left,
                "top": top,
                "width": width,
                "height": height,
            }
            print(label)
            if label not in st.session_state.labels:
               st.session_state.labels.append(label)
                
else:
    st.warning("No images to display. Please check the image directory.")