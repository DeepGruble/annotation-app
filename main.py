import streamlit as st
from streamlit_drawable_canvas import st_canvas
from enum import Enum
import os
import matplotlib.pyplot as plt
from PIL import Image
import random
import numpy as np
from model import load_sam2
from model import ModelSize


# Color palette:
# https://coolors.co/b74f6f-adbdff-3185fc-34e5ff-35281d

# ===============================================================
# Constants
# ===============================================================

# Path to the dataset
IMAGE_PATH = "C:\\Users\\MajaGojska\\Desktop\\classification_dataset_split\\train"
# Where the segmentation masks will be saved
SEGMENTATION_MASKS_PATH = "C:\\Users\\MajaGojska\\Desktop\\classification_dataset_masks\\train"

class ImgeType(Enum):
    BITEWING = "bitewing"
    COLOR_PANORAMIC = "color_panoramic"
    COLOR_ZOOM = "color_zoom"
    PANORAMIC = "panoramic"
    PERIAPICAL = "periapical"

# ===============================================================
# Initialize the session state
# ===============================================================
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

if "images" not in st.session_state:
    st.session_state.images = read_images()
    st.session_state.current_image_index = 0
    st.session_state.prompts = []
    st.session_state.mask = None
    st.session_state.tooth_number = 1  # Default tooth number
    
    # Initialize the SAM2 model
    st.session_state.model = load_sam2(model_size=ModelSize.LARGE)
    print("Model initialized successfully")


def get_current_image():
    """
    Get the current image from the list of images based on the current index.
    """
    if st.session_state.current_image_index < len(st.session_state.images):
        return st.session_state.images[st.session_state.current_image_index]
    else:
        return None


def process_clicks(points, image):
    image_np = np.array(image)
    st.session_state.model.set_image(image_np)
    
    # Prepare the prompt
    input_point = np.array(points)
    input_label = np.array([1] * len(points))
    
    # Generate the segmentation mask
    masks, _, _ = st.session_state.model.predict(input_point, input_label)
    return masks[0]


def overlay_mask(image, mask, color):
    """
    Overlay the mask on the image.
    :param image: The image to overlay the mask on
    :param mask: The mask to overlay (binary mask)
    :param color: The color to use for the overlay
    """
    image_np = np.array(image)
    overlayed_image = image_np.copy()
    overlayed_image[mask == 1] = color
    return Image.fromarray(overlayed_image) 

# ===============================================================
# Streamlit UI
# ===============================================================
st.set_page_config(layout="wide", page_title="Object Segmentation with SAM2")

# Custom CSS for styling: buttons, progress bar, and headers
st.markdown(
    """
    <style>
    .stButton button {
        background-color: #ADBDFF;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
        border: 1px solid #ADBDFF;
    }
    .stButton button:hover {
        background-color: #3185fc;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
        border: 1px solid #3185fc;
    }
    .stProgress > div > div > div {
        background-color: #ADBDFF;
    }
    .stMarkdown h1 {
        color: #4CAF50;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar for controls
with st.sidebar:
    st.header("Settings")
    image_type = st.selectbox(
        "Select Image Type",
        [img_type.value for img_type in ImgeType],
        index=3,  # Default to PANORAMIC
    )

    # Tooth numbers and their corresponding colors
    tooth_colormap = plt.get_cmap("hsv", 32)
    TOOTH_COLORS = {i + 1: tooth_colormap(i / 32)[:3] for i in range(32)}
            
    # Selectbox for tooth number
    tooth_number = st.selectbox(
        "Select Tooth Number",
        list(TOOTH_COLORS.keys()),
        index=0,  # Default to tooth number 1
    )
    st.session_state.tooth_number = tooth_number

    if st.button("Reload Images"):
        st.session_state.images = read_images(ImgeType(image_type))
        st.session_state.current_image_index = 0
        st.session_state.prompt = None
        st.session_state.mask = None

# Main content
st.title("Object Segmentation with SAM2")
st.markdown("Draw on the image to generate a segmentation mask.")

# Display current image and progress
current_image = get_current_image()
if current_image is not None:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### Current Image")
        RESIZE_FACTOR = 2.5
        current_image = current_image.resize((int(224 * RESIZE_FACTOR), int(224 * RESIZE_FACTOR)))

        # Overlay the mask on the current image if it exists
        if st.session_state.mask is not None:
            overlayed_image = overlay_mask(current_image, st.session_state.mask, TOOTH_COLORS[st.session_state.tooth_number])
        else:
            overlayed_image = current_image

        # Display the canvas with the overlayed image
        canvas_result = st_canvas(
            fill_color="",
            stroke_width=4,
            background_color="#FFFFFF",
            update_streamlit=True,
            stroke_color="red",
            background_image=overlayed_image,
            width=current_image.size[0],
            height=current_image.size[1],
            drawing_mode="circle",
            key="canvas",
        )
        
        col1a, col1b, col1c = st.columns(3)
        with col1a:
            if st.button("Show Mask"):
                st.session_state.mask = process_clicks(st.session_state.prompts, current_image)
                st.rerun()

        with col1b:
            if st.button("Save Mask"):
                pass  # Add saving logic here

        with col1c:
            if st.button("Clear Mask"):
                st.session_state.prompts = []
                st.session_state.mask = None
                st.rerun()
            
    with col2:
        st.markdown("### Progress")
        st.progress((st.session_state.current_image_index + 1) / len(st.session_state.images))
        st.write(f"Image {st.session_state.current_image_index + 1} of {len(st.session_state.images)}")

    # Handle canvas result
    if canvas_result and canvas_result.json_data is not None:
        objects = canvas_result.json_data["objects"]
        if objects:
            last_object = objects[-1]
            x = last_object["left"] + last_object["radius"]
            y = last_object["top"] + last_object["radius"]
            if (x, y) not in st.session_state.prompts:
                st.session_state.prompts.append((x, y))
                
else:
    st.warning("No images to display. Please check the image directory.")