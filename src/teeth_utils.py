from enum import Enum


class ImgeType(Enum):
    BITEWING = "bitewing"
    COLOR_PANORAMIC = "color_panoramic"
    COLOR_ZOOM = "color_zoom"
    PANORAMIC = "panoramic"
    PERIAPICAL = "periapical"


DANISH_NUMBERING = [
    # Top row, left to right, left side
    "8+", "7+", "6+", "5+", "4+", "3+", "2+", "1+",
    # Top row, left to right, right side
    "+1", "+2", "+3", "+4", "+5", "+6", "+7", "+8",
    
    # Bottom row, left to right, left side
    "8-", "7-", "6-", "5-", "4-", "3-", "2-", "1-",
    # Bottom row, left to right, right side
    "-1", "-2", "-3", "-4", "-5", "-6", "-7", "-8"
]

INTERNATIONAL_NUMBERING = [
    # Top row, left to right, left side
    "18", "17", "16", "15", "14", "13", "12", "11",
    # Top row, left to right, right side
    "21", "22", "23", "24", "25", "26", "27", "28",
    
    # Bottom row, left to right, left side
    "48", "47", "46", "45", "44", "43", "42", "41",
    # Bottom row, left to right, right side
    "31", "32", "33", "34", "35", "36", "37", "38"
]

IMAGE_TYPE = ImgeType.COLOR_PANORAMIC
NUMBERING_SYSTEM = DANISH_NUMBERING
