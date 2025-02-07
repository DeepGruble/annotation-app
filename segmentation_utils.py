import streamlit as st
import numpy as np
from PIL import Image


def process_clicks(points, image):
    """
    Process the clicked points and generate the segmentation mask.
    :param points: The list of clicked points
    :param image: The image to generate the mask for
    """
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


