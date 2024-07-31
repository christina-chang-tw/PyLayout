from pathlib import Path

import numpy as np
from PIL import Image, ImageOps
import gdsfactory as gf
from gdsfactory.typings import Component, LayerSpec

@gf.cell
def draw_chip_art_from_image(
    filepath: Path,
    threshold: int=200,
    size: tuple=None,
    layer: LayerSpec=(0, 0),
) -> Component:
    """
    Draw chip art from an image

    Args:
        filepath [Path]: Path: path to the image file

    Returns:
        Component: chip art component
    """
    image = Image.open(filepath)
    image = ImageOps.grayscale(image)
    image = ImageOps.autocontrast(image)
    threshold = 200
    image = image.point(lambda p: p > threshold and 255)
    image = image.convert('1')  # Convert to 1-bit pixels

    if size is not None:
        image = image.resize(size)

    image_array = np.array(image)
    rows, cols = image_array.shape

    c = gf.Component()
    for row in range(rows):
        for col in range(cols):
            temp = gf.Component()
            if image_array[row, col] == 0:  # Assuming black pixel
                temp.add_polygon([(0,0),(0,1),(1,1),(1,0)], layer=layer)
                c.add_ref(temp).dmove([col, rows - row])

    c.flatten()
    return c
