from streamlit_drawable_canvas import st_canvas
import os
import streamlit as st
from PIL import Image
from streamlit_theme import st_theme
import pandas as pd
from io import BytesIO
import base64
import time
import math

from colormaps import *


# Constants
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PATH = os.path.join(ROOT, "temp_images")
SAVE_PATH = os.path.join(ROOT, "output")
if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)

# Defines the canvas size
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

def get_current_image():
    """
    Get the current image from the list of images based on the current index.
    """
    if st.session_state.current_image_index < len(st.session_state.images):
        return st.session_state.images[st.session_state.current_image_index]
    return None

def reset_session_state():
    """
    Reset the session state (clear the annotation dataframe and reset the tooth number).
    """
    st.session_state.processed_object_count = 0
    st.session_state.tooth_number = 1       # Default tooth number
    st.session_state.annotation_df = pd.DataFrame(columns=[
        "label", 
        "x_min", "y_min", 
        "width", "height", 
        "cropped_image"])
    # Update the canvas key to clear the canvas
    st.session_state.canvas_key = f"canvas_{st.session_state.current_image_index}"
    st.rerun()

def next_image():
    """
    Move to the next image in the list and reset the annotation dataframe.
    """
    st.session_state.current_image_index += 1
    if st.session_state.current_image_index >= len(st.session_state.images):
        st.success("All images have been annotated.")
        st.stop()
    reset_session_state()
    
    
def previous_image():
    """
    Move to the previous image in the list and reset the annotation dataframe.
    """
    st.session_state.current_image_index -= 1
    reset_session_state()
    
    
def delete_annotation(idx):
    st.session_state.annotation_df.drop(idx, inplace=True)
    st.session_state.annotation_df.reset_index(drop=True, inplace=True)
    st.rerun()
    
def annotation_exists(x_min, y_min, width, height):
    if st.session_state.annotation_df[
        (st.session_state.annotation_df["x_min"] == x_min) &
        (st.session_state.annotation_df["y_min"] == y_min) &
        (st.session_state.annotation_df["width"] == width) &
        (st.session_state.annotation_df["height"] == height)
        ].empty:
        return False
    return True
    
    
def submit_annotation():
    # FIXME: Theese have to be unique
    image_id = st.session_state.current_image_index
    
    # Add the current image to the coco data
    # FIXME: Not sure about the TARGET_IMAGE_SIZE
    # It depends on how the anotated images will be saved and whther they will be resized before or after
    st.session_state.coco_data.add_image(
        image_id, f"image_{image_id}.jpg", 
        image_size=(TARGET_IMAGE_SIZE, TARGET_IMAGE_SIZE))   

    for idx, row in st.session_state.annotation_df.iterrows():
        st.session_state.coco_data.add_annotation(
            idx, image_id, row["label"], 
            [row["x_min"], row["y_min"], row["width"], row["height"]])
        
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
    
    
def toggle_help():
    # Create a pop up window with the help text
    pass


def init_session_state(coco_annotations):
    if "images" not in st.session_state:
        # Read the images from the dataset
        st.session_state.images = read_images()
        # Initialize the current image index (index of the current image being displayed)
        st.session_state.current_image_index = 0
        # Initialize the annotation dataframe
        st.session_state.annotation_df = pd.DataFrame(columns=[
            "label", 
            "x_min", "y_min", 
            "width", "height", 
            "cropped_image"])
        # Set default label number
        st.session_state.label_id = 0  
        st.session_state.current_labels = None
        # Helps to keep track of the number of objects processed in the canvas
        st.session_state.processed_object_count = 0
        st.session_state.coco_data = coco_annotations
        st.session_state.canvas_key = "canvas"
        
        
def build_html_table(dataframe):     
    
    # Start HTML string for table   
    html = f"""     
    <table>       
        <tr>
            <th>Label</th>         
            <th>Bbox</th>                
            <th>Cropped Image</th>   
        </tr>"""
    
    for _, row in dataframe.iterrows():         
        label_id = row["label"]
        label = st.session_state.current_labels[label_id]
        x_min, y_min = row["x_min"], row["y_min"]    
        width, height = row["width"], row["height"]         
        cropped = row["cropped_image"]
        bbox = f"[{x_min}, {y_min}, {width}, {height}]"

        html += f"""         
        <tr>          
            <td>{label}</td>           
            <td>{bbox}</td>
            <td> 
                <img src="{cropped}" alt="Cropped" style="height: 50px; width: auto;"/>
            </td>
        </tr> """
    
    html += "</table>"
    return html

        
def create_sidebar(labels):
    with st.sidebar:
    
        # 1. Progress bar for the annotation process
        st.markdown("### Annotation Progress")
        progress_value = (st.session_state.current_image_index + 1) / len(st.session_state.images)
        st.progress(progress_value)
        
        num_remaining_images = len(st.session_state.images) - (st.session_state.current_image_index + 1)
        st.markdown(f"""
            <div style="display: flex; justify-content: space-between;">
                <span>Image <b>{st.session_state.current_image_index + 1}</b> of <b>{len(st.session_state.images)}</b></span>
                <span><b>{num_remaining_images}</b> remaining</span>
            </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        # ===============================================================
        
        #  3. Create a grid of buttons for tooth selection
        radio = st.radio(
                label="System Settings", 
                options=list(labels.keys())
        )
        st.session_state.current_labels = labels[radio] 
        st.divider()       
        # ===============================================================
        
        #  3. Create a grid of buttons for tooth selection
        st.markdown("### Select the Label to Annotate")
        
        labels = st.session_state.current_labels
        nrows = 2
        ncols = int(math.ceil(len(labels) // nrows))
        cols = st.columns(ncols)
        for i, label in enumerate(labels):
            with cols[i % ncols]:
                st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)
                if st.button(f"{label}", key=f"{i}"):
                    st.session_state.label_id = i
                    print(f"Label {label} selected")
                
        st.divider()
        # ===============================================================
        
         # 4. User Action Buttons
        st.markdown("### Actions")
        
        if st.button("Submit", type="primary", use_container_width=True):
            submit_annotation()
            
        # Help button
        if st.button("Toggle Help", use_container_width=True, type="primary"):
            toggle_help()
            
        # Create two columns for the next and previous buttons
        col1, col2 = st.columns(2)
        with col1:
            # Disable the Previous button if we're at the first image
            prev_disabled = st.session_state.current_image_index <= 0
            if st.button("Previous Image", use_container_width=True, disabled=prev_disabled, type="primary"):
                previous_image()
        with col2:
            # Disable the Next button if we're at the last image
            next_disabled = st.session_state.current_image_index >= len(st.session_state.images) - 1
            if st.button("Next Image", use_container_width=True, disabled=next_disabled, type="primary"):
                next_image()
        
def create_main_page():
    # Display current image and progress
    current_image = get_current_image()
    if current_image is None:
        st.error("No images found.")
        return
        
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
                "left": row["x_min"], "top": row["y_min"],
                "width": row["width"], "height": row["height"],
                "fill": "rgba(0,0,0,0)", "stroke": "#cf0029", "strokeWidth": 2
            }
            for _, row in st.session_state.annotation_df.iterrows()]})
        
         # Handle canvas result
    if canvas_result and canvas_result.json_data is not None:
        objects = canvas_result.json_data["objects"]
        new_objects = objects[st.session_state.processed_object_count:]
        
        for obj in new_objects:
            
            height, width = obj["height"], obj["width"]
            x_min, y_min = obj["left"], obj["top"]
            # Check if the annotation already exists
            if annotation_exists(x_min, y_min, width, height):
                continue
            
            cropped_image = resized_image.crop((x_min, y_min, x_min + width, y_min + height))
            data_url = pil_image_to_data_url(cropped_image)
            
            row = {
                "label": st.session_state.label_id,
                "x_min": x_min, "y_min": y_min,
                "width": width, "height": height,
                "cropped_image": data_url,
            }
            # Add the row to the dataframe st.session_state.annotation_df
            st.session_state.annotation_df.loc[len(st.session_state.annotation_df)] = row
               
        st.session_state.processed_object_count = len(objects)
        st.divider()
        
        # Build the HTML table
        if st.session_state.annotation_df.empty: 
            st.write("No annotations yet.") 
        else: 
            table_html = build_html_table(st.session_state.annotation_df) 
            # Display the table with unsafe_allow_html=True 
            st.markdown(table_html, unsafe_allow_html=True)
            
            # Button to remove the last annotation
            if st.button("Remove Last Annotation", type="primary"):
                # Remove the last row from the annotation dataframe and redraw the UI
                if not st.session_state.annotation_df.empty:
                    st.session_state.annotation_df.drop(st.session_state.annotation_df.index[-1], inplace=True)
                    st.rerun()

def set_theme():
    # Detect which theme is being used
    # FIXME: This is not an elegant solution
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
        
# Main annotation function
def annotation_page(title, labels, custom_css=None):
    st.set_page_config(layout="wide", page_title=title)
    st.session_state.current_labels = labels["Danish"]
    
    set_theme()
    
    if custom_css:
        st.markdown(f"<style>{custom_css}</style>", unsafe_allow_html=True)
    
    # ===============================================================
    # SIDEBAR
    # ===============================================================
    create_sidebar(labels)
                
    # ===============================================================
    # MAIN PAGE
    # =============================================================== 
    create_main_page()