from torchvision.models import efficientnet_v2_m, EfficientNet_V2_M_Weights
import torch
import pytorch_lightning as pl
from torch.optim import Adam
from sklearn.metrics import f1_score
import torch.nn.functional as F
from torchvision import transforms


LABELS = [
    "Periapical", 
    "Color Zoom", 
    "Panoramic", 
    "Bitewing", 
    "Color Panoramic"]



def get_accuracy(preds, labels):
    return torch.tensor(torch.sum(preds == labels).item() / len(preds))


def log_perfromance(outputs, labels, type='train', class_weights=None):
    _, preds = torch.max(outputs, 1)
    
    return {
        f'{type}_accuracy': get_accuracy(preds, labels),
        f'{type}_loss': F.cross_entropy(outputs, labels, weight=class_weights),
        f'{type}_f1': torch.tensor(f1_score(labels.cpu(), preds.cpu(), average='macro'))
    }


class Classification(pl.LightningModule):

    def __init__(self, num_classes, class_weights=None):
        """
        param num_classes: Number of classes in the dataset
        """
        super(Classification, self).__init__()

        self.model = efficientnet_v2_m(weights=EfficientNet_V2_M_Weights.IMAGENET1K_V1)
        # Modify the classifier to match the number of classes
        self.model.classifier[1] = torch.nn.Linear(self.model.classifier[1].in_features, num_classes)
        
        # Convert to tensor if class weights are provided
        self.class_weights = class_weights


    def forward(self, x):
        return self.model(x)

    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=1e-4)


    def training_step(self, batch, batch_idx):
        images, labels = batch
        
        # Get multiclass loss
        outputs = self(images)
        performance_dict = log_perfromance(
            outputs, labels, type='train', class_weights=self.class_weights)
        self.log_dict(performance_dict)

        return performance_dict['train_loss']   


    def validation_step(self, batch, batch_idx):
        images, labels = batch
        
        # Get multiclass loss
        outputs = self(images)

        performance_dict = log_perfromance(
            outputs, labels, type='val')
        self.log_dict(performance_dict)

        return performance_dict['val_loss']
    
    def test_step(self, batch, batch_idx):
        images, labels = batch
        
        # Get multiclass loss
        outputs = self(images)

        performance_dict = log_perfromance(
            outputs, labels, type='test')
        self.log_dict(performance_dict)

        return performance_dict['test_loss']
    
    
def load_model(model_path):
    """
    Load the model from the specified path
    :param model_name: Name of the model file
    :return: The loaded model
    """
    
    classification_model = Classification(num_classes=5)
    state_dict = torch.load(model_path, map_location=torch.device("cpu"))
    classification_model.load_state_dict(state_dict)
            
    return classification_model


def prepare_images(images):
    MEAN = [0.5, 0.5, 0.5]
    STD = [0.5, 0.5, 0.5]

    image_transforms = transforms.Compose([
        transforms.ToTensor(),         # Convert image to PyTorch tensor
        transforms.Normalize(mean=MEAN, std=STD),  # Normalize the tensor
        transforms.Resize((224, 224))  # Resize the image to 224x224 pixels
    ])
    
    return [image_transforms(image) for image in images]
    

def inference(model, images):
    """
    Perform inference on the images using the model
    :param model: The model to perform inference with
    :param images: List of PIL images to perform inference on
    """
    # Preprocess the images
    images = prepare_images(images)

    # Convert the images to a tensor
    images = torch.stack(images)

    # Perform inference
    outputs = model(images)  # Raw logits
    probabilities = F.softmax(outputs, dim=1)  # Convert to probabilities

   # Get the predicted class and confidence scores
    confidences, preds = torch.max(probabilities, 1)
    # Round the confidence scores
    confidences = [round(conf.item(), 3) for conf in confidences]

    preds_classes = [LABELS[pred] for pred in preds.tolist()]  # Convert to class   

    return list(zip(preds_classes, confidences))