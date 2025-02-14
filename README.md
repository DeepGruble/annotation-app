
### User Tasks

- **Teeth Numbering [Peter: Tooth Tagging/Numbering]**
- **Tooth Anomaly Annotation [Peter: Tooth Anomaly Annotation]** _(Specify classes to be annotated)_

## App Overview

### 1. Dashboard Overview

The main dashboard should provide an overview of the annotation progress for each task:

- **Progress Visualization:**
  - Display the distribution of annotated images by image type and annotation task.
  - Show the number of remaining images for each task. [Peter: Number/%]
  
- **Task Actions:**
  - Provide _Start Annotation_ buttons for both tasks.
  - Disable buttons if there are no images left to annotate.

### 2. Annotation Pages

#### (A) Tooth Numbering Annotation

- **User Interface:**
  - Users select teeth numbers from a color-coded menu. 
  - Users can choose different image types from the settings page.
  - A progress bar should indicate annotation completion status.
  - Users can exit annotation and return to the main dashboard.

##### Annotation Process

- **Segmentation Annotation**
  1. Select the tooth number.
  2. Click multiple points on the tooth in the image.
  3. Click the submit button.
  4. A segmentation mask overlays the image.
  5. Users can cycle through alternative segmentation masks with lower confidence using arrow keys.
  6. Users can save or discard the annotation and retry.
  7. Users can also skip the image.

- **Bounding Box Annotation**
  1. Select the tooth number.
  2. Draw a bounding box around the tooth.
  3. Users can redo or save the annotation.
  4. Users may also skip the image.

#### (B) Tooth Anomaly Annotation

- **User Interface:**
  - Display all relevant images for a case along with journal entries.
  - Users select anomaly types from a predefined menu.
  - (*) Users can add a new anomaly type with an additional comment justifying the choice.
  - A progress bar should indicate annotation completion status.
  - Users can exit the process and return to the dashboard if not all images in a case are annotated.
  - If all images in a case are annotated, users proceed to the next case.

----------------------------------------

# Tasks TODO:

1) Save the bounding boxes after user clicks the submit button.
2) Add functionality to delete the bounding boxes (both from canvas and from the list of bounding boxes).
3) (*) Add functionality to edit the bounding boxes.
4) Add functionality to skip the image.
5) Zoom in/out functionality.
6) Automatic app deployment using streamlit website (https://share.streamlit.io/new)
