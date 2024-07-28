import numpy as np

import gdsfactory as gf
from gdsfactory.typings import Component

from ..basic.marker import dice_marker

@gf.cell
def place_dice_marker(c: Component, sides: str, spacing: int = 25) -> Component:
    """
    Placing dice marker on each side of the component

    Args:
        c [Component]: component to be placed with dice marker
        sides [str]: list of sides to place the dice marker, "t" for top, "b" for bottom, "l" for left, "r" for right
    """
    packed = gf.Component()
    ref = packed.add_ref(c)
    marker = dice_marker()
    marker_spacing = 1180

    def place_markers(is_vertical, length, coord, rotate=False):
        num = np.floor(length / (marker_spacing + marker.dxsize))
        end_spacing = (length - num * marker_spacing - (num - 1) * marker.dxsize) / 2
        for i in range(int(num)):
            mk_ref = packed.add_ref(marker)
            if rotate:
                mk_ref.drotate(90)
            mk_ref.dx = coord[0] if is_vertical else end_spacing + (i + 1) * marker.dxsize + i * marker_spacing
            mk_ref.dy = end_spacing + (i + 1) * marker.dxsize + i * marker_spacing if is_vertical else coord[1]

    side_params = {
        "t": (False, ref.dxsize, (None, ref.dymax + spacing + marker.dysize / 2), False),
        "b": (False, ref.dxsize, (None, ref.dymin - spacing - marker.dysize / 2), False),
        "l": (True, ref.dysize, (ref.dxmin - spacing - marker.dysize / 2, None), True),
        "r": (True, ref.dysize, (ref.dxmax + spacing + marker.dysize / 2, None), True),
    }

    for side in sides:
        if side in side_params:
            is_vertical, length, coord, rotate = side_params.get(side, (False, 0, (0, 0), False))
            place_markers(is_vertical, length, coord, rotate)

    packed.flatten()
    return packed