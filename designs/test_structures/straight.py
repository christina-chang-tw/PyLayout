import numpy as np
import gdsfactory as gf
from gdsfactory.typings import List, CrossSectionSpec, Component

from pylayout.components import attach_grating_coupler
from pylayout.methods import gen_uuid
from cornerstone import rib_450, cs_gc_silicon_1550nm
from . import rng

@gf.cell
def straight(
    length: float,
    gc: Component,
    cs: CrossSectionSpec = rib_450,
) -> Component:
    """
    Straight waveguide test structures.

    Args:
        length: The length of the straight waveguides.
        cs: Cross section of the straight waveguides.
    
    Returns:
        List of straight waveguides.
    """
    cs = gf.get_cross_section(cs)

    c = gf.path.straight(length=length)
    c = c.extrude(cs)
    c = attach_grating_coupler(c, gc, ["o1", "o2"])

    return c

def main():
    lengths = np.linspace(100, 1000, 6)
    rng.shuffle(lengths)
    cs = rib_450

    component_list = []

    for length in lengths:
        c = straight(length, gc=cs_gc_silicon_1550nm, cs=cs)
        component_list.append(c)

    c = gf.grid(
        component_list,
        spacing=(500, 86),
        shape=(6, 1),
        align_x="xmin",
        align_y="y"
    )
    
    # c.show()

if __name__ == "__main__":
    main()