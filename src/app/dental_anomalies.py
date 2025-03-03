from annotation_template import *
from annotations import ToothNumberAnnotations, AnnomalyAnnotations

DANISH_LABELS = [
    "Tandkrone", "Protese", "Plastfylding", "Plastisk Opbygning", "Støbt opbygning"
]

INTERNATIONAL_LABELS = [
    "Crown", "Denture", "Filling", "Composite Build-up", "Cast Build-up"
]

LABELS = {
    "Danish": DANISH_LABELS,
    "International": INTERNATIONAL_LABELS
}


coco_annotation = AnnomalyAnnotations()
init_session_state(coco_annotation)
annotation_page("Dental Numbering Annotation", LABELS)