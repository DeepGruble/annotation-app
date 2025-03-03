import os
import json

class Annotations:
    
    def __init__(self):
        self.images = []
        self.annotations = []
        self.categories = self.initialize_categories()
        
    def initialize_categories(self):
        categories = [] 
        for i in range(1, 33):
            categories.append({
                "id": i,
                "name": f"tooth_{i}",
                "supercategory": "tooth"
            })
        return categories
    
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
        try:
            with open(os.path.join(save_path, "annotations.json"), "w") as f:
                json.dump({
                    "images": self.images,
                    "annotations": self.annotations,
                    "categories": self.categories
                }, f, indent=4)  # Add indentation for readability
            return True
        except Exception as e:
            print(f"Error saving annotations: {e}")
            return False
