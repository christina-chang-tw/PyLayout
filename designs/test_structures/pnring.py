import numpy as np

import gdsfactory as gf
from gdsfactory.typings import List, CrossSectionSpec

from . import rng
from pylayout.components import ring, attach_grating_coupler
from pylayout.routing import route_pads_to_ring
from cornerstone import (
    rib_450,
    metal_pad,
    pn_450_with_metal,
    cs_gc_silicon_1550nm
)

def ring_pn_offset(
    radius: float=10,
    angle: float=20,
    gap: float=0.37,
    dist_pn_to_wg: float=0.79,
    wg: CrossSectionSpec=rib_450,
    pn: CrossSectionSpec=pn_450_with_metal,
    offsets: np.ndarray=[0],
    max_length: float=550,
    pad_spacing: float=25,
) -> List[gf.Component]:
    """
    Different PN doping offset test structures.

    Args:
        radius (float): Radius of the ring.
        angle (float): Angle of the outer arc.
        gap (float): Gap between the inner ring and the outer arc.
        wg (gf.typings.CrossSectionSpec): Cross section of the ring.
        offsets (np.ndarray): List of different PN doping offsets.
        max_length (float): Maximum length of the test structure.
        pad_spacing (float): Spacing between the pads.

    Returns:
        List of different PN doping offset test structures.
    """
    wg = gf.get_cross_section(wg)
    rng.shuffle(offsets)
    
    component_list = []
    ring_st = gf.path.straight(length=max_length/2 - radius).extrude(wg)
    st = gf.path.straight(length=max_length).extrude(wg)
    pads = [metal_pad, metal_pad, metal_pad]
    pads = gf.grid(pads, spacing=(pad_spacing, pad_spacing))

    for idx, offset in enumerate(offsets):
        c = gf.Component()
        
        r = ring(
            wg=wg, pn=pn(offset_low_doping=offset),
            radius=radius, gap=gap, int_angle=angle,
            dist_pn_to_wg=dist_pn_to_wg
        )
        
        lst_ref, rst_ref = [c.add_ref(ring_st) for _ in range(2)]

        pads_routing = {
            "0_0_e4": "METAL_BOT_p2",
            "1_0_e4": "METAL_TOP_p1",
            "2_0_e4": "METAL_BOT_p1",
        }
        
        r = route_pads_to_ring(r, pads, pads_routing)
        ring_ref = c.add_ref(r)
        ring_ref.mirror_y()
        lst_ref.connect("o2", ring_ref.ports["o1"])
        rst_ref.connect("o1", ring_ref.ports["o2"])

        c.add_port(name="o1", port=lst_ref.ports["o1"])
        c.add_port(name="o2", port=rst_ref.ports["o2"])

        if idx % 5 == 0:
            st_ref = c.add_ref(st)
            st_ref.dx, st_ref.dy = ring_ref.dx, rst_ref.dymax + 40
            c.add_port(name="o3", port=st_ref.ports["o1"])
            c.add_port(name="o4", port=st_ref.ports["o2"])
            c = attach_grating_coupler(c, cs_gc_silicon_1550nm, ["o1", "o2", "o3", "o4"])
        else:
            c = attach_grating_coupler(c, cs_gc_silicon_1550nm, ["o1", "o2"])

        component_list.append(c)
    
    component_list = list(reversed(component_list))

    return component_list

def ring_pn_via_distance(
    radius: float=10,
    gap: float=0.25,
    angle: float=20,
    dist_pn_to_wg: float=0.79,
    via_gaps: np.ndarray=None,
    wg: CrossSectionSpec=rib_450,
    pn: CrossSectionSpec=pn_450_with_metal,
    pad_spacing: float=25,
) -> List[gf.Component]:
    """
    Vary the medium to via gap to test the difference in bandwidth performance.

    Args:
        radius (float): Radius of the ring.
        gap (float): Gap between the inner ring and the outer arc.
        angle (float): Angle of the outer arc.
        dist_pn_to_wg (float): Distance between the PN junction and the waveguide.
        via_gaps (np.ndarray): List of different medium to via gaps.
        wg (gf.typings.CrossSectionSpec): Cross section of the ring.
        pn_wg (gf.typings.CrossSectionSpec): Cross section of the PN junction.
        pad_spacing (float): Spacing between the pads.

    Returns:
        List of different medium to via gap test structures.
    """
    wg = gf.get_cross_section(wg)

    rng.shuffle(via_gaps)

    component_list = []

    st = gf.path.straight(length=250).extrude(wg)
    pads = [metal_pad, metal_pad, metal_pad]
    pads = gf.grid(pads, spacing=pad_spacing)

    for via_gap in via_gaps:
        c = gf.Component()
        r = ring(
            wg=wg,
            pn=pn(gap_medium_to_via=via_gap),
            radius=radius,
            gap=gap,
            int_angle=angle,
            dist_pn_to_wg=dist_pn_to_wg
        )
        
        routing = {
            "0_0_e4": "METAL_BOT_p2",
            "1_0_e4": "METAL_TOP_p1",
            "2_0_e4": "METAL_BOT_p1",
        }
        r = route_pads_to_ring(r, pads, routing)
        ring_ref = c.add_ref(r)
        st_left_ref, st_right_ref = [c.add_ref(st) for _ in range(2)]
        st_left_ref.connect("o2", ring_ref.ports["o1"])
        st_right_ref.connect("o1", ring_ref.ports["o2"])

        test_st = gf.path.straight(length=c.dxsize).extrude(wg)
        test_st_ref = c.add_ref(test_st)
        test_st_ref.dx = ring_ref.dx
        test_st_ref.dymin = ring_ref.dymin - 30

        c.add_port(name="o1", port=st_left_ref.ports["o1"])
        c.add_port(name="o2", port=st_right_ref.ports["o2"])
        c.add_port(name="o3", port=test_st_ref.ports["o1"])
        c.add_port(name="o4", port=test_st_ref.ports["o2"])
        c = attach_grating_coupler(c, ["o1", "o2", "o3", "o4"])

        component_list.append(c)

    return component_list

def main():
    offsets = np.linspace(0, 0.5, 6)
    wg = rib_450
    component_list = ring_pn_offset(offsets=offsets, wg=wg, pn=pn_450_with_metal)
    c = gf.Component()
    c = gf.grid(
        component_list,
        spacing=(500, 86),
        shape=(len(component_list), 1),
        align_x="xmin",
        align_y="y"
    )
    
    c.show()

if __name__ == "__main__":
    main()