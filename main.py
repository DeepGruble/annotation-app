from streamlit_drawable_canvas import st_canvas
from enum import Enum
import os
import matplotlib.pyplot as plt
import streamlit as st
from PIL import Image



class ImgeType(Enum):
    BITEWING = "bitewing"
    COLOR_PANORAMIC = "color_panoramic"
    COLOR_ZOOM = "color_zoom"
    PANORAMIC = "panoramic"
    PERIAPICAL = "periapical"
    
    
# TODO: This value depends on the page entered by the user
IMAGE_TYPE = ImgeType.COLOR_PANORAMIC

st.set_page_config(layout="wide", page_title=f"Numbering Tool - {IMAGE_TYPE.value}")

# Read the css style template
css_path = os.path.join(os.path.dirname(__file__), "style_template.css")
if os.path.exists(css_path):
    with open(css_path, "r") as f:
        css_template = f.read()
    css = css_template
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
else:
    st.warning("CSS template not found. Please check the path.")



    




# Color palette for the UI:
# https://coolors.co/b74f6f-adbdff-3185fc-34e5ff-35281d

# Path to the dataset
IMAGE_PATH = "C:\\Users\\MajaGojska\\Desktop\\classification_dataset_split\\train"
# Where the labels are stored
LABEL_PATH = "C:\\Users\\MajaGojska\\Desktop\\classification_dataset_labels\\train"
if not os.path.exists(LABEL_PATH):
    os.makedirs(LABEL_PATH)


def read_images(image_type=ImgeType.PANORAMIC):
    """
    Read images from the specified directory.
    :param image_type: The type of images to read
    """
    images = []
    image_files = os.listdir(os.path.join(IMAGE_PATH, image_type.value))
    for image_file in image_files:
        images.append(
            Image.open(os.path.join(IMAGE_PATH, image_type.value, image_file)).convert("RGB")
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
    
def rgb_to_hex(rgb):
    """
    Convert an RGB tuple to a hex color string.
    """
    return '#%02x%02x%02x' % (int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))


# ===============================================================
# Streamlit UI
# ===============================================================

# Sidebar for controls
with st.sidebar:
    
    st.markdown("### Progress")
    st.progress((st.session_state.current_image_index + 1) / len(st.session_state.images))
    st.write(f"Image {st.session_state.current_image_index + 1} of {len(st.session_state.images)}")

    # Tooth selection
    # Tooth numbers and their corresponding colors
    tooth_colormap = plt.get_cmap("hsv", 32)
    # Dictionary mapping tooth numbers to colors
    tooth_colors_dict = {i + 1: tooth_colormap(i / 32)[:3] for i in range(32)}
    
    #  Create a grid of buttons for tooth selection
    st.markdown("### Tooth Selection")
    st.markdown("Select the tooth number to annotate:")
    
    st.markdown('<div class="tooth-buttons">', unsafe_allow_html=True)
    
    cols = st.columns(16)
    for i, tooth in enumerate(list(range(1, 33))):
        with cols[i % 16]:
            color = tooth_colors_dict[tooth]
            st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)
 
            if st.button(f"{tooth}", key=f"button{tooth}"):
                st.session_state.tooth_number = tooth
                print(f"Tooth {tooth} selected")
                st.rerun()        
    st.markdown('</div>', unsafe_allow_html=True)  # Close the div wrapper
    
    # Add the zoom slider
    zoom = st.slider("Zoom", min_value=1., max_value=8., value=1., step=0.1)



# Main content
#st.title("Numbering Annotation Tool")

# Display current image and progress
current_image = get_current_image()
if current_image is not None:

        
    width = int(current_image.width * zoom)
    height = int(current_image.height * zoom)
    print(width, height)

    # Display the canvas with the overlayed image
    canvas_result = st_canvas(
        fill_color="",
        stroke_width=2,
        background_color="#FFFFFF",
        update_streamlit=True,
        stroke_color=rgb_to_hex(tooth_colors_dict[st.session_state.tooth_number]),
        background_image=current_image,
        width=width * 2,
        height=height * 2,
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