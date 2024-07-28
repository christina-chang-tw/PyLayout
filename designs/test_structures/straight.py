import numpy as np
import gdsfactory as gf
from gdsfactory.typings import List, CrossSectionSpec

from pylayout.components import attach_grating_coupler
from pylayout.methods import gen_uuid
from cornerstone import rib_450
from . import rng

def straight(
    lengths: np.ndarray,
    cs: CrossSectionSpec = rib_450,
) -> List[gf.Component]:
    """
    Straight waveguide test structures.

    Args:
        lengths: List of lengths of the straight waveguides.
        cs: Cross section of the straight waveguides.
    
    Returns:
        List of straight waveguides.
    """
    cs = gf.get_cross_section(cs)
    rng.shuffle(lengths)

    component_lists = []

    for length in lengths:
        temp = gf.Component()
        path = gf.path.straight(length=length)
        temp.add_ref(path.extrude(cs))
        component_lists.append(temp)

    return component_lists

def main():
    lengths = np.linspace(100, 1000, 6)
    rng.shuffle(lengths)
    cs = rib_450

    component_lists = straight(lengths, cs)
    c = gf.grid(
        component_lists,
        spacing=(500, 86),
        shape=(6, 1),
        align_x="xmin",
        align_y="y"
    )
    
    c.show()

if __name__ == "__main__":
    main()