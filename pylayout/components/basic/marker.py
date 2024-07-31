import gdsfactory as gf
from gdsfactory.typings import LayerSpec

@gf.cell
def dice_marker(
    width: float = 20,
    length: float = 820,
    spacing: float = 180,
    marker_gap: float = 60,
    layer: LayerSpec = (0, 0)
) -> gf.Component:
    """
    Create a dice marker for photonic circuit layout.

    Args:
        width [float]: Width of the markers.
        length [float]: Length of the markers.
        spacing [float]: Spacing between markers.
        marker_gap [float]: Gap between mirrored markers.
        layer [gf.LayerSpec]: Layer specification.

    Returns:
        gf.Component: Dice marker component.
    """
    c = gf.Component()

    rect = gf.cross_section.ComponentAlongPath(
        component=gf.c.rectangle(size=(width, width), centered=True, layer=layer),
        spacing=spacing + width,
        padding=0,
        offset=-width
    )

    x = gf.CrossSection(
        sections=[gf.Section(width=width, offset=0, layer=layer)],
        components_along_path=[rect]
    )

    path = gf.Path()
    path += gf.path.straight(length=length)

    mark1_ref, mark2_ref = [c.add_ref(path.extrude(x)) for _ in range(2)]
    mark2_ref.mirror_y()
    mark2_ref.dx = mark1_ref.dx
    mark2_ref.dymin = mark1_ref.dymax + marker_gap
    
    c.flatten()
    return c