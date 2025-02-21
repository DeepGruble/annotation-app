from streamlit_drawable_canvas import st_canvas
import os
import streamlit as st
from PIL import Image
from streamlit_theme import st_theme
import pandas as pd
from io import BytesIO
import base64
import time

from teeth_utils import *
from colormaps import *
from annotations import Annotations

# Constants
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(ROOT, "temp_images")
SAVE_PATH = os.path.join(ROOT, "output")
if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)

TARGET_IMAGE_SIZE = 500

    
def pil_image_to_data_url(img):
    """
    Convert a PIL image to a data URL.
    :param img: The PIL image to convert
    :return: The data URL string
    """
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"


def read_images(image_type=None):
    """
    Read images from the specified directory.
    :param image_type: The type of images to read
    :return: A list of PIL images
    """
    images = []
    image_paths = os.path.join(DATA_PATH, image_type.value) if image_type else DATA_PATH
    for image_file in os.listdir(image_paths):
        images.append(
            Image.open(os.path.join(image_paths, image_file)).convert("RGB")
        )
    return images
    

# Has to be set as the first streamlit command
st.set_page_config(layout="wide", page_title=f"Numbering Tool - {IMAGE_TYPE.value}")

# Detect which theme is being used
try:
    theme = st_theme()["base"]
    theme_colors = colormap_light if theme == "light" else colormap_dark
except:
    theme_colors = colormap_light

# Read the css style template and set the theme colors
css_path = os.path.join(os.path.dirname(__file__), "style_template.css")
if os.path.exists(css_path):
    with open(css_path, "r") as f:
        css_template = f.read()
    css = css_template.format(**theme_colors)
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
else:
    st.warning("CSS template not found. Please check the path.")


# Initialize the session state
if "images" not in st.session_state:
    # Read the images from the dataset
    st.session_state.images = read_images()
    # Initialize the current image index (index of the current image being displayed)
    st.session_state.current_image_index = 0
    # Initialize the annotation dataframe
    st.session_state.annotation_df = pd.DataFrame(columns=[
        "tooth_number", 
        "x_min", "y_min", 
        "width", "height", 
        "cropped_image"])
    # Set default tooth number
    st.session_state.tooth_number = 1  
    st.session_state.processed_object_count = 0
    st.session_state.coco_data = Annotations()
    st.session_state.canvas_key = "canvas"

def get_current_image():
    """
    Get the current image from the list of images based on the current index.
    """
    if st.session_state.current_image_index < len(st.session_state.images):
        return st.session_state.images[st.session_state.current_image_index]
    return None

def next_image():
    st.session_state.current_image_index += 1
    if st.session_state.current_image_index >= len(st.session_state.images):
        # FIXME: This needs to be more sophisticated
        st.success("All images have been annotated.")
        st.stop()
    st.session_state.processed_object_count = 0
    st.session_state.annotation_df = pd.DataFrame(columns=[
        "tooth_number", "x_min", "y_min", "width", "height", "cropped_image"])
    st.session_state.tooth_number = 1
    # Update the canvas key to clear the canvas
    st.session_state.canvas_key = f"canvas_{st.session_state.current_image_index}"
    st.rerun()

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
    
    # Allow the user to select the numbering system
    numbering_system_radio = st.radio("Numbering System", ["Danish", "International"])
    NUMBERING_SYSTEM = DANISH_NUMBERING if numbering_system_radio == "Danish" else INTERNATIONAL_NUMBERING
    
    st.markdown("Select the tooth number to annotate:")
    
    # Open a div wrapper
    st.markdown('<div class="tooth-buttons">', unsafe_allow_html=True)
    cols = st.columns(16)
    for i, tooth in enumerate(list(range(1, 33))):
        with cols[i % 16]:
            st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)
            tooth_name = NUMBERING_SYSTEM[i]
            if st.button(f"{tooth_name}", key=f"button{tooth}"):
                st.session_state.tooth_number = tooth
                print(f"Tooth {tooth} selected")
    # Close the div wrapper
    st.markdown('</div>', unsafe_allow_html=True)  
    
    st.divider()
    
     # Main buttons
    column_1, column_2 = st.columns(2)
    with column_1:
        if st.button("Submit", type="primary"):
            
            # FIXME: Theese have to be unique
            # This image should be either stored in a database with unique id or this image should be saved now in a dedicated folder
            image_id = st.session_state.current_image_index
            
            # Add this image to the coco data
            st.session_state.coco_data.add_image(image_id, f"image_{image_id}.jpg")
        
            for idx, row in st.session_state.annotation_df.iterrows():
                st.session_state.coco_data.add_annotation(
                    idx, 
                    image_id, row["tooth_number"], 
                    [row["x_min"], row["y_min"], 
                     row["width"], row["height"]])
                
            if st.session_state.coco_data.save_annotations(SAVE_PATH):
                # Create a placeholder for the success message
                success_placeholder = st.empty()
                success_placeholder.success("Annotations saved successfully.")
                # Wait for n seconds
                time.sleep(1)
                # Clear the success message
                success_placeholder.empty()
            else:
                st.error("Failed to save annotations.")
        
            # Show the next image
            next_image()

    with column_2:
        if st.button("Skip", type="primary"):
            # Show the next image
            next_image()
            
            
def delete_annotation(idx):
    st.session_state.annotation_df.drop(idx, inplace=True)
    st.session_state.annotation_df.reset_index(drop=True, inplace=True)
    st.rerun()

def build_html_table(dataframe):     
    
    # Start HTML string for table   
    html = f"""     
    <table>       
        <tr>
            <th>Number</th>         
            <th>Bbox</th>                
            <th>Tooth Image</th>   
        </tr>"""
    
    for idx, row in dataframe.iterrows():         
        tooth_number = NUMBERING_SYSTEM[row["tooth_number"] - 1]     
        x_min, y_min = row["x_min"], row["y_min"]    
        width, height = row["width"], row["height"]         
        cropped = row["cropped_image"]
        
        bbxo = f"[{x_min}, {y_min}, {width}, {height}]"

        html += f"""         
        <tr>          
            <td>{tooth_number}</td>           
            <td>{bbxo}</td>
            <td> 
                <img src="{cropped}" alt="Cropped" style="height: 50px; width: auto;"/>
            </td>
        </tr> """
    
    html += "</table>"
    return html


# Display current image and progress
current_image = get_current_image()
if current_image is not None:
    
    resized_image = current_image.resize((TARGET_IMAGE_SIZE, TARGET_IMAGE_SIZE), Image.LANCZOS)

    # Display the canvas with the overlayed image
    canvas_result = st_canvas(
        fill_color="",
        stroke_width=2,
        background_color="#FFFFFF",
        update_streamlit=True,
        stroke_color="#cf0029",
        background_image=resized_image,
        width=TARGET_IMAGE_SIZE,
        height=TARGET_IMAGE_SIZE,
        drawing_mode="rect",
        key=st.session_state.canvas_key,
        initial_drawing={
        "version": "4.4.0",
        "objects": [
            {
                "type": "rect",
                "left": row["x_min"],
                "top": row["y_min"],
                "width": row["width"],
                "height": row["height"],
                "fill": "rgba(0,0,0,0)",
                "stroke": "#cf0029",
                "strokeWidth": 2
            }
            for _, row in st.session_state.annotation_df.iterrows()
        ]
    },
    )
            
    # Handle canvas result
    if canvas_result and canvas_result.json_data is not None:
        objects = canvas_result.json_data["objects"]
        new_objects = objects[st.session_state.processed_object_count:]
        
        for obj in new_objects:
            
            height, width = obj["height"], obj["width"]
            x_min, y_min = obj["left"], obj["top"]
            
            cropped_image = resized_image.crop((x_min, y_min, x_min + width, y_min + height))
            data_url = pil_image_to_data_url(cropped_image)
            
            row = {
                "tooth_number": st.session_state.tooth_number,
                "x_min": x_min, "y_min": y_min,
                "width": width, "height": height,
                "cropped_image": data_url,
            }
            # Add the row to the dataframe st.session_state.annotation_df
            st.session_state.annotation_df.loc[len(st.session_state.annotation_df)] = row
               
        st.session_state.processed_object_count = len(objects)
        
        st.divider()


        if st.session_state.annotation_df.empty: 
            st.write("No annotations yet.") 
        else: 
            table_html = build_html_table(st.session_state.annotation_df) 
            # Display the table with unsafe_allow_html=True 
            st.markdown(table_html, unsafe_allow_html=True)
            
             # Button to remove the last annotation
            if st.button("Remove Last Annotation"):
                # Remove the last row from the annotation dataframe and redraw the UI
                if not st.session_state.annotation_df.empty:
                    st.session_state.annotation_df.drop(st.session_state.annotation_df.index[-1], inplace=True)
                    st.rerun()

else:
    st.warning("No images to display. Please check the image directory.")
    
    
# Zoom in
# click and build a bounding box around the tooth
# normalize the coordiantes -> ok
# Move stuff to .css file
# Save and remove the annotations
        # weak labelling for object detetion (?)
        
        
        

    