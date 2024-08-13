import gdsfactory as gf
from gdsfactory.typings import Component, CrossSectionSpec, Tuple

from ..basic.gc import attach_grating_coupler

@gf.cell
def add_norm_wg(
    c: Component,
    gc: Component,
    cs: CrossSectionSpec,
    rpos: float=0,
    sides: str="N",
) -> Component:
    """
    Add a normalisation waveguide to the component.

    Args:
        c [Component]: component to add the normalisation waveguide
        gc [float]: grating coupler length for the normalisation waveguide
        cs [CrossSectionSpec]: cross section of the normalisation waveguide
        rpos [float]: relative position
        side [str]: side to place the normalisation waveguide, "N" for top, "S" for bottom, "W" for left, "E" for right
    
    Returns:
        [Component]: component with the normalisation waveguide
    """
    cell = gf.Component()
    c, gc = gf.get_component(c), gf.get_component(gc)
    cs = gf.get_cross_section(cs)
    ref = cell.add_ref(c)

    def place_wg(is_vertical: bool, length: float, coord: Tuple, rotate: bool):
        wg = gf.path.straight(length=length - gc.dxsize*2).extrude(cs)
        wg = attach_grating_coupler(wg, gc, ["o1", "o2"])
        wg_ref = cell.add_ref(wg)
        if rotate:
            wg_ref.drotate(90)
        wg_ref.dx = coord[0] if is_vertical else ref.dx
        wg_ref.dy = ref.dy if is_vertical else coord[1]

    side_params = {
        "N": (False, ref.dxsize, (None, ref.dymax + rpos), False),
        "S": (False, ref.dxsize, (None, ref.dymin - rpos), False),
        "W": (True, ref.dysize, (ref.dxmin - rpos, None), True),
        "E": (True, ref.dysize, (ref.dxmax + rpos, None), True),
    }

    if any((side for side in sides if side.upper() not in side_params)):
        raise ValueError(f"Invalid side parameter: {sides}")

    for side in sides:
        if side in side_params:
            is_vertical, length, coord, rotate = side_params.get(side, (False, 0, (0, 0), False))
            place_wg(is_vertical, length, coord, rotate)

    cell.flatten()
    return cell

