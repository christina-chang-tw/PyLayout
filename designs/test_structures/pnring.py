import numpy as np

import gdsfactory as gf
from gdsfactory.typings import List, CrossSectionSpec, Component

from . import rng
from pylayout.components import ring, attach_grating_coupler, add_norm_wg
from pylayout.routing import route_pads_to_ring
from cornerstone import (
    rib_450,
    metal_pad,
    pn_450_with_metal,
    cs_gc_silicon_1550nm
)
from .straight import straight

@gf.cell
def single_ring_pn(
    rc: Component,
    pad_spacing: float = 25,
):
    """
    A single ring with PN junction test structure.

    Args:
        radius (float): Radius of the ring.
        angle (float): Angle of the outer arc.
        gap (float): Gap between the inner ring and the outer arc.
        dist_pn_to_wg (float): Distance between the PN junction and the waveguide.
        wg (gf.typings.CrossSectionSpec): Cross section of the ring.
        pn (gf.typings.CrossSectionSpec): Cross section of the PN junction.
        max_length (float): Maximum length of the test structure.
        pad_spacing (float): Spacing between the pads.
    """
    c = gf.Component()
    r = gf.get_component(rc)
    
    pads = [metal_pad, metal_pad, metal_pad]
    pads = gf.grid(pads, spacing=(pad_spacing, pad_spacing))
    routing = {
        "0_0_e4": "METAL_BOT_p2",
        "1_0_e4": "METAL_TOP_p1",
        "2_0_e4": "METAL_BOT_p1",
    }
    r = route_pads_to_ring(r, pads, routing)
    ring_ref = c.add_ref(r)

    c.add_port(name="o1", port=ring_ref.ports["o1"])
    c.add_port(name="o2", port=ring_ref.ports["o2"])

    c.flatten()
    return c

@gf.cell
def single_ring_pn_with_gc(
    rc: Component,
    pad_spacing: float = 25,
):
    """
    A single ring with PN junction test structure.

    Args:
        radius (float): Radius of the ring.
        angle (float): Angle of the outer arc.
        gap (float): Gap between the inner ring and the outer arc.
        dist_pn_to_wg (float): Distance between the PN junction and the waveguide.
        wg (gf.typings.CrossSectionSpec): Cross section of the ring.
        pn (gf.typings.CrossSectionSpec): Cross section of the PN junction.
        max_length (float): Maximum length of the test structure.
        pad_spacing (float): Spacing between the pads.
    """
    r = gf.get_component(rc)
    
    single_ring = single_ring_pn(rc=r, pad_spacing=pad_spacing)
    c = attach_grating_coupler(single_ring, cs_gc_silicon_1550nm, ["o1", "o2"])

    c.flatten()
    
    return c

def main():
    wg = rib_450
    radius = 5
    angle = 16
    dist_pn_to_wg = None
    dist_y = 2
    max_length = 550

    # r=5, disty=2
    # r=6, disty=2.45
    gaps = [0.20, 0.21, 0.22, 0.23, 0.24, 0.25]
    component_lists = []

    for gap in gaps:
        component_lists.append(single_ring_pn(wg=wg, pn=pn_450_with_metal,
                            dist_pn_to_wg=dist_pn_to_wg, dist_y=dist_y, max_length=max_length, radius=radius, angle=angle, gap=gap))
        
    c = gf.grid(
        component_lists,
        shape=(2, 3),
        spacing=15,
        align_y="center"
    )
    c.show()

if __name__ == "__main__":
    main()