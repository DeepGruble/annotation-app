from annotation_template import *
from annotations import AnnomalyAnnotations

DANISH_LABELS = [
    "Tandkrone", "Protese", "Plastfylding", "Plastisk Opbygning", "Støbt opbygning"
]

ENGLISH_LABELS = [
    "Crown", "Denture", "Filling", "Composite Build-up", "Cast Build-up"
]

LABELS = {
    "Danish": DANISH_LABELS,
    "English": ENGLISH_LABELS
}

css = """
.element-container:has(#button-after) + div button {
    height: 40px;
    width: 150px;
    padding: 0 0px 0 0px !important;
}
"""

coco_annotation = AnnomalyAnnotations()
init_session_state(coco_annotation)
annotation_page("Dental Numbering Annotation", LABELS, custom_css=css)