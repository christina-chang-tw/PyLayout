from functools import partial

import gdsfactory as gf
import numpy as np

from cornerstone import rib_450, cs_gc_silicon_1550nm
from pylayout.components import attach_grating_coupler

def main():
    
    straight_length = np.linspace(100, 1000, 6)
    
    straight = partial(gf.components.straight, cross_section=rib_450)
    bend = partial(gf.components.bend_euler, cross_section=rib_450)
    splitter = partial(gf.components.mmi1x2, cross_section=rib_450, length_taper=20, length_mmi=10)
    
    components = []
    for length in straight_length:
        mzi = gf.components.mzi(
            bend=bend,
            straight=straight,
            splitter=splitter,
            cross_section=rib_450,
            length_x=length,
            delta_length=0.0,
        )
        mzi = attach_grating_coupler(mzi, gc=cs_gc_silicon_1550nm, ports=["o1", "o2"])
        mzi.flatten()
        components.append(mzi)
    
    c = gf.grid(
        components=components,
        spacing=(0, 10),
        shape=(len(components), 1),
        align_x="center",
        align_y="center",
    )
    c.show()


if __name__ == "__main__":
    main()