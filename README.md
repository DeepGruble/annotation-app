## Deployment

App is currently deployed via Streamlit cloud ([Link](https://annotation-app-qn7tayj2q3oyon9kkbnfry.streamlit.app/)). Whenever the changes in the code are pushed to the main branch, the app is automatically updated.

Additionally, the app will be deployed on Azure App Service ([How?](https://learn.microsoft.com/en-us/answers/questions/1470782/how-to-deploy-a-streamlit-application-on-azure-app))

# App Overview

User Tasks:
- **Teeth Numbering [Peter: Tooth Tagging/Numbering]**
- **Tooth Anomaly Annotation [Peter: Tooth Anomaly Annotation]** _(Specify classes to be annotated)_


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

1) ~~Save the bounding boxes after user clicks the submit button.~~
2) Add functionality to delete the bounding boxes (both from canvas and from the list of bounding boxes).
3) (*) Add functionality to edit the bounding boxes.
4) ~~Add functionality to skip the image.~~
5) Zoom in/out functionality.
6) ~~Automatic app deployment using streamlit website (https://share.streamlit.io/new)~~


# Google cloud

1. Data Storage
* Use Cloud Storage to store images.
* Use Cloud Functions / Cloud Run to receive and process images from client systems.

2. Annotation System:
* Deploy Streamlit annotation tool on Cloud Run 
  * Need to add a Dockerfile for this
  ```bash
  # Build Docker image
  gcloud builds submit --tag gcr.io/[YOUR_PROJECT_ID]/annotation-app

  # Deploy to cloud Run
  gcloud run deploy annotation-app \
  --image gcr.io/[YOUR_PROJECT_ID]/streamlit-annotation-app \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
  ```

* Store annotation results in Firestore or BigQuery.

3. Model Training & Evaluation:
* Use Vertex AI for managed model training.
* Store model weights and logs in Cloud Storage.
* Evaluate performance and store metrics in BigQuery or Cloud Monitoring.

4. Iteration & Automation:
* Automate the pipeline using Cloud Composer (Airflow) or Cloud Functions to trigger training/evaluation when enough new annotated data is available.
