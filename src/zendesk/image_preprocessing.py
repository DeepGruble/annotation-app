import pytesseract
import matplotlib.pyplot as plt
import numpy as np
import cv2
from pytesseract import Output

"""
This module contains method for preprocessing X ray images before feeding them to the model.
The preprocessing steps include removing the black regions from the image as well as removing any text present in the image.
"""


# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"


def get_text_bounding_boxes(image):
    """
    Get the bounding boxes around text regions in the image using pytesseract.
    :param image: The image to process.
    """
    # Conver the image to a numpy array
    if not isinstance(image, np.ndarray):
        image = np.array(image)
    return pytesseract.image_to_data(image, output_type=Output.DICT)


def plot_text_bounding_boxes(image, boxes, ax):
    """
    Plot bounding boxes around text regions on the image and annotate them with
    the confidence score and extracted words.
    :param image: The image to plot the bounding boxes on.
    :param boxes: The bounding boxes and text extracted from the image.
    """
    if image.shape[-1] == 3:  # Check if the image has 3 channels (RGB)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    n_boxes = len(boxes['level'])
    for i in range(n_boxes):
        (x, y, w, h) = (
            boxes['left'][i], boxes['top'][i], 
            boxes['width'][i], boxes['height'][i]
        )
        text = boxes['text'][i]
        conf = boxes['conf'][i]

        # Only annotate words that have non-empty text and a confidence score greater than 0
        if text.strip() and int(conf) > 50:
            # Draw the bounding box
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 150, 0), 3)
            
            # Annotate with the text and confidence score
            # label = f"{round(conf, 2)}% conf"
            # cv2.putText(image, label, (x, y + 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (38, 76, 255), 2, cv2.LINE_AA)

    # Convert back to RGB for displaying with matplotlib
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    ax.imshow(image)
    ax.axis('off')


def remove_text(image, boxes, confidence_threshold=50):
    """
    Remove text regions from the image by overlaying black rectangles on the text regions.
    :param image: The image to process.
    :param boxes: The bounding boxes and text extracted from the image.
    :param confidence_threshold: The confidence threshold to determine if a text region should be removed.
    """

    # Create a mask to black out the text regions
    mask = np.ones_like(image) * 255
    n_boxes = len(boxes['level'])
    for i in range(n_boxes):
        text = boxes['text'][i]
        conf = boxes['conf'][i]
        (x, y, w, h) = (
            boxes['left'][i], boxes['top'][i], 
            boxes['width'][i], boxes['height'][i]
        )
        if text.strip() and int(conf) > confidence_threshold:
            # Black out the text region
            mask[y:y+h, x:x+w] = 0
    
    # Apply the mask to the image
    return cv2.bitwise_and(image, mask)


def thresholding_crop(image, type='median', threshold=1):
    """
    Crop the top and bottom parts of the image based on a pixel intensity threshold.
    Processes from both top and bottom, stopping once a valid row is found in each direction.

    :param image: The image to process (expected in BGR format).
    :param type: The method to calculate row intensity ('median' or 'mean').
    :param threshold: The threshold value to determine if a row is part of the foreground.
    :return: Cropped image with background rows removed from top and bottom.
    """
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Calculate the row intensity values based on the specified type
    if type == 'median':
        row_val = np.median(gray, axis=1)
    else:
        row_val = np.mean(gray, axis=1)

    # Create a boolean array where True indicates the row meets or exceeds the threshold
    valid_rows = row_val >= threshold

    # Initialize top and bottom indices
    top = None
    bottom = None

    # Find the first valid row from the top
    for i in range(len(valid_rows)):
        if valid_rows[i]:
            top = i
            break

    # Find the first valid row from the bottom
    for i in range(len(valid_rows)-1, -1, -1):
        if valid_rows[i]:
            bottom = i
            break

    # If no valid rows are found, return the original image
    if top is None or bottom is None:
        # No valid rows found based on the threshold. Returning the original image.
        return image

    # Ensure that top is above bottom
    if top > bottom:
        # Top index is below bottom index. Returning the original image
        return image

    # Crop the image between the top and bottom indices (inclusive)
    cropped_image = image[top:bottom + 1, :]

    return cropped_image


def improve_contrast(image, alpha=1.0, beta=0):
    """
    Apply a contrast adjustment to the image using the formula:
    g(x) = alpha * f(x) + beta
    where f(x) is the pixel intensity value, and alpha and beta are the contrast adjustment parameters.
    :param image: The image to adjust the contrast of.
    :param alpha: The contrast adjustment factor.
    :param beta: The brightness adjustment factor.
    :return: The image with adjusted contrast.
    """
    adjusted = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    return adjusted


def padded_resize(image, target_size=(224, 224), pad_value=0):
    """
    Resize the image to the target size while maintaining the original aspect ratio.
    The resized image is padded with the specified value to fill the remaining space.
    :param image: The image to resize.
    :param target_size: The target size of the resized image.
    :param pad_value: The value to pad the image with.
    """
    # Calculate the aspect ratio of the original image
    h, w = image.shape[:2]
    aspect_ratio = w / h

    # Calculate the aspect ratio of the target size
    target_w, target_h = target_size
    target_aspect_ratio = target_w / target_h

    # Resize the image while maintaining the original aspect ratio
    if aspect_ratio > target_aspect_ratio:
        # Resize based on width
        new_w = target_w
        new_h = int(new_w / aspect_ratio)
    else:
        # Resize based on height
        new_h = target_h
        new_w = int(new_h * aspect_ratio)

    resized = cv2.resize(image, (new_w, new_h))

    # Pad the resized image to the target size
    pad_h = (target_h - new_h) // 2
    pad_w = (target_w - new_w) // 2
    
    # If image is RGB, make the pad_value a tuple
    if len(resized.shape) == 3:
        pad_value = (pad_value, pad_value, pad_value)
    padded = cv2.copyMakeBorder(resized, pad_h, pad_h, pad_w, pad_w, cv2.BORDER_CONSTANT, value=pad_value)

    return padded



# FINAL METHOD TO BE USED IN THE PIPELINE
def preprocess_image(image, text_confidence_threshold=50, crop_threshold=40, target_size=(224, 224)):
    """
    Preprocess the image by removing text regions and background rows.
    :param image: The image to preprocess.
    :param text_confidence_threshold: The confidence threshold to determine if a text region should be removed.
    :param crop_threshold: The threshold value to determine if a row is part of the foreground.
    :return: The preprocessed image.
    """

    # Extract text bounding boxes for the text regions in the image
    bounding_boxes = get_text_bounding_boxes(image)
    # Overlay black rectangles on the text regions with a confidence score greater than the threshold
    image_no_text = remove_text(image, bounding_boxes, confidence_threshold=text_confidence_threshold)
    image_no_text = improve_contrast(image_no_text, alpha=0.7, beta=0.)
    # Crop the image to remove the background row by row
    cropped_image = thresholding_crop(image_no_text, type='average', threshold=crop_threshold)
    
    if target_size is not None:
        # Resize the image to the target size
        cropped_image = padded_resize(cropped_image, target_size=target_size)
    return cropped_image


if __name__ == '__main__':
    img_path = "C:/Users/mjgoj/Desktop/DeepGruble/insurance_X_rays_images_Felix/images/v3.jpg"
    image = cv2.imread(img_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    fig, ax = plt.subplots(1, 2, figsize=(12, 6))
    ax[0].imshow(image)
    ax[0].axis('off')
    ax[0].set_title('Original Image')

    # Preprocess the image
    preprocessed_image = preprocess_image(image, text_confidence_threshold=50, crop_threshold=40, target_size=(256, 256))
    ax[1].imshow(preprocessed_image, cmap='gray')
    ax[1].axis('off')
    ax[1].set_title('Preprocessed Image')

    plt.tight_layout()
    plt.show()