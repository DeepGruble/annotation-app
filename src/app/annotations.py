import os
import json
from abc import ABC, abstractmethod


class Annotations(ABC):
    
    def __init__(self, type):
        self.type = type
        self.images = []
        self.annotations = []
        self.categories = self.initialize_categories()

    @abstractmethod
    def initialize_categories(self):
        pass
    
    def add_image(self, image_id, file_name, image_size=None):
        image_dict ={
            "id": image_id,
            "file_name": file_name,
        }
        if image_size:
            image_dict["width"] = image_size[0]
            image_dict["height"] = image_size[1]
        self.images.append(image_dict)
        
    def add_annotation(self, annotation_id, image_id, category_id, bbox):
        self.annotations.append({
            "id": annotation_id,
            "image_id": image_id,
            "category_id": category_id,
            "bbox": bbox,
            "area": bbox[2] * bbox[3],
            "iscrowd": 0
        })
    
    def save_annotations(self, save_path):
        save_folder = os.path.join(save_path, self.type)
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)
            
        try:
            with open(save_folder + "/annotations.json", "w") as f:
                json.dump({
                    "images": self.images,
                    "annotations": self.annotations,
                    "categories": self.categories
                }, f, indent=4)  # Add indentation for readability
            return True
        except Exception as e:
            print(f"Error saving annotations: {e}")
            return False


class ToothNumberAnnotations(Annotations):
    
    def __init__(self):
        super().__init__("tooth_numbers")
        
        
    def initialize_categories(self):
        categories = [] 
        for i in range(1, 33):
            categories.append({
                "id": i,
                "name": f"tooth_{i}",
                "supercategory": "tooth"
            })
        return categories
    
    

class AnnomalyAnnotations(Annotations):
    
    def __init__(self):
        super().__init__("anomalies")
        
    def initialize_categories(self):
        categories = [] 
        # FIXME: A placeholder for the anomaly categories
        anomalies = ["caries", "crown", "cavity", "missing", "filling", "bridge", "other"]
        for i in range(len(anomalies)):
            categories.append({
                "id": i,
                "name": anomalies[i],
                "supercategory": "anomaly"
            })
        return categories