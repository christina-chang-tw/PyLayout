import gdsfactory as gf
from gdsfactory.typings import LayerSpec

@gf.cell
def outline(width: float=100, height: float=100, layer: LayerSpec=(0.0)) -> gf.Component:
    """
    Create a rectangle outline

    Args:
        width: width of the rectangle
        height: height of the rectangle
    """
    c = gf.components.rectangle(
        size=(width, height),
        layer=layer,
        centered=True
    )
    c.flatten()
    return c