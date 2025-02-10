from streamlit_drawable_canvas import st_canvas
from enum import Enum
import os
import matplotlib.pyplot as plt
from SAM2_model import load_sam2
from SAM2_model import ModelSize
from segmentation_utils import *

class ImgeType(Enum):
    BITEWING = "bitewing"
    COLOR_PANORAMIC = "color_panoramic"
    COLOR_ZOOM = "color_zoom"
    PANORAMIC = "panoramic"
    PERIAPICAL = "periapical"
    

# TODO: This value depends on the page entered by the user
IMAGE_TYPE = ImgeType.COLOR_PANORAMIC

st.set_page_config(layout="wide", page_title=f"Numbering Tool - {IMAGE_TYPE.value}")


# Color palette for the UI:
# https://coolors.co/b74f6f-adbdff-3185fc-34e5ff-35281d

# Path to the dataset
IMAGE_PATH = "C:\\Users\\MajaGojska\\Desktop\\classification_dataset_split\\train"
# Where the segmentation masks will be saved
SEGMENTATION_MASKS_PATH = "C:\\Users\\MajaGojska\\Desktop\\classification_dataset_masks\\train"


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
    st.session_state.prompts = []
    st.session_state.mask = None
    st.session_state.tooth_number = 1  # Default tooth number
    
    # Initialize the SAM2 model
    st.session_state.model = load_sam2(model_size=ModelSize.TINY)
    print("Model initialized successfully")
    

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

# Custom CSS for styling: buttons, progress bar, and headers
st.markdown(
    """
    <style>
    
    /* Main style button */
    .stButton>button {
        background-color: #ADBDFF;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 10px;
        border: 1px solid #ADBDFF;
    }
    .stButton>button:hover {
        background-color: #3185fc;
        border: 1px solid #3185fc;
        color: white;
    }
    .stButton>button:active {
        background-color: #3185fc;
        border: 1px solid #3185fc;
        color: white;
    }
    
    /* Tooth selection buttons */
    .tooth-buttons {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        
    }
    .tooth-buttons .stButton>button {
        background-color:rgb(0, 0, 0) !important;
        color: black;
        border-radius: 5px;
        padding: 5px 10px;
        margin: 5px;
        border: 1px solid #ADBDFF;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar for controls
with st.sidebar:

    # Tooth selection
    # Tooth numbers and their corresponding colors
    tooth_colormap = plt.get_cmap("hsv", 32)
    # Dictionary mapping tooth numbers to colors
    tooth_colors_dict = {i + 1: tooth_colormap(i / 32)[:3] for i in range(32)}
    
    #  Create a grid of buttons for tooth selection
    st.markdown("### Tooth Selection")
    
    st.markdown('<div class="tooth-buttons">', unsafe_allow_html=True)
    
    st.markdown("""
        <style>.element-container:has(#button-after) + div button {
            background-color: transparent;
            font-size: 8px !important;
            color: white;
            border: 1px solid ##34E5FF;
            height: 10px;
            width: 30px;
            0px;
            border-radius: 3px;
            padding: 2px;
            cursor: pointer;
            
            
            
        }</style>""", 
        unsafe_allow_html=True)
    
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
    

    stroke_width = st.slider("Stroke Width", 1, 10, 2)
    

# Main content
st.title("Numbering Tool")

# Display current image and progress
current_image = get_current_image()
if current_image is not None:
    col1, col2 = st.columns([3, 1])
    with col1:
        RESIZE_FACTOR = 2.5
        current_image = current_image.resize((int(224 * RESIZE_FACTOR), int(224 * RESIZE_FACTOR)))

        # Overlay the mask on the current image if it exists
        if st.session_state.mask is not None:
            overlayed_image = overlay_mask(current_image, st.session_state.mask, color=tooth_colors_dict[st.session_state.tooth_number])
        else:
            overlayed_image = current_image

        # Display the canvas with the overlayed image
        canvas_result = st_canvas(
            fill_color="",
            stroke_width=stroke_width,
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
            if st.button("Show Mask", type="primary"):
                st.session_state.mask = process_clicks(st.session_state.prompts, current_image)
                st.rerun()

        with col1b:
            if st.button("Save Mask", type="primary"):
                pass  # Add saving logic here
            
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