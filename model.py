# Python for the SAM2 model: 3.11.0
from enum import Enum
import os
from sam2.build_sam import build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor

class ModelSize(Enum):
    TINY = "tiny"
    SMALL = "small"
    LARGE = "large"
    BASE_PLUS = "base_plus"
    
# Path to the SAM2 model
SAM_PATH = "C:\\Users\\MajaGojska\\Documents\\sam2"


def get_config_name(model_size):
    """
    Get the name of the configuration file for the specified model size
    :param model_size: The model size
    :return: The name of the configuration file
    """
    model_id = model_size.value[0] if model_size != ModelSize.BASE_PLUS else "b+"
    return f"sam2.1_hiera_{model_id}.yaml"


def load_sam2(model_size=ModelSize.TINY):

    checkpoint = f"sam2.1_hiera_{model_size.value}.pt"
    checkpoint_path = SAM_PATH + "\\checkpoints\\" + checkpoint
    if not os.path.exists(checkpoint_path):
        raise ValueError(f"Checkpoint file {checkpoint_path} does not exist")
        
    model_cfg_path = SAM_PATH + "\\sam2\\configs\\sam2.1\\" + get_config_name(model_size)
    if not os.path.exists(model_cfg_path):
        raise ValueError(f"Model config file {model_cfg_path} does not exist")
    
    predictor = SAM2ImagePredictor(build_sam2(model_cfg_path, checkpoint_path, device="cpu"))
    return predictor

if __name__ == "__main__":
    model = load_sam2()
    print("Model initialized successfully")