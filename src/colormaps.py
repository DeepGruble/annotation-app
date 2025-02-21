def rgb_to_hex(rgb):
    """
    Convert an RGB tuple to a hex color string.
    """
    return '#%02x%02x%02x' % (int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))


def hex_to_rgb(hex):
    """
    Convert a hex color string to an RGB tuple (0-255 range).
    """
    return tuple(int(hex[i:i+2], 16) for i in (1, 3, 5))


def blend_hex_colors(hex1, hex2, ratio=0.5):
    # Convert hex to RGB (0-255 range)
    rgb1 = hex_to_rgb(hex1)
    rgb2 = hex_to_rgb(hex2)

    # Blend the colors
    blended_rgb = tuple(int(rgb1[i] * (1 - ratio) + rgb2[i] * ratio) for i in range(3))

    # Convert back to hex
    return f"#{blended_rgb[0]:02X}{blended_rgb[1]:02X}{blended_rgb[2]:02X}"

colormap_dark = {
    "text": "#f0ebfa",
    "background": "#06030c",
    "background2": "#272630",
    "primary": "#68EDC6",
    "secondary": "#ADBDFF",
    "accent": "#3185FC",
}
colormap_dark["partial"] = blend_hex_colors(colormap_dark["secondary"], colormap_dark["accent"], 0.5)

colormap_light = {
    "text": "#0a0514",
    "background": "#f6f3fc",
    "background2": "#f2f2f2",
    "primary": "#8AA1FF",
    "secondary": "#BCE784",
    "accent": "#5DD39E",
}
colormap_light["partial"] = blend_hex_colors(colormap_light["secondary"], colormap_light["accent"], 0.5)


# Alternative Color palette for the UI:
# https://coolors.co/b74f6f-adbdff-3185fc-34e5ff-35281d



