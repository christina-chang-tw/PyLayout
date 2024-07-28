import numpy as np

import gdsfactory as gf
from gdsfactory.typings import List, CrossSectionSpec

from . import rng
from pylayout.components import ring, attach_grating_coupler, ring_pn_pad
from pylayout.cross_section import rib_cs450, pn_cs, metal_pad
from pylayout.cornerstone.layer import LAYER

def ring_pn_offset(
    radius: float=10,
    angle: float=20,
    gap: float=0.37,
    dist_pn_to_wg: float=0.79,
    cs: CrossSectionSpec=rib_cs450,
    offsets: np.ndarray,
    max_length: float=550,
    pad_spacing: float=25,
) -> List[gf.Component]:
    """
    Different PN doping offset test structures.

    Args:
        radius (float): Radius of the ring.
        angle (float): Angle of the outer arc.
        gap (float): Gap between the inner ring and the outer arc.
        cs (gf.typings.CrossSectionSpec): Cross section of the ring.
        offsets (np.ndarray): List of different PN doping offsets.
        max_length (float): Maximum length of the test structure.
        pad_spacing (float): Spacing between the pads.

    Returns:
        List of different PN doping offset test structures.
    """
    cs = gf.get_cross_section(cs)
    rng.shuffle(offsets)
    
    component_list = []
    ring_st = gf.path.straight(length=max_length/2 - radius).extrude(cs)
    st = gf.path.straight(length=max_length).extrude(cs)
    pads = [metal_pad, metal_pad, metal_pad]
    pads = gf.grid(pads, spacing=(pad_spacing, pad_spacing))

    for idx, offset in enumerate(offsets):
        c = gf.Component()
        ring = ring(
            wg=cs, pn=pn_cs(layer_metal=LAYER.METAL, layer_via=LAYER.VIA, offset_low_doping=offset),
            radius=radius, gap=gap, int_angle=angle,
            dist_pn_to_wg=dist_pn_to_wg
        )
        
        lst_ref, rst_ref = [c.add_ref(ring_st) for _ in range(2)]

        pads_routing = {
            "0_0_e4": "METAL_BOT_p2",
            "1_0_e4": "METAL_TOP_p1",
            "2_0_e4": "METAL_BOT_p1",
        }
        
        ring = ring_pn_pad(ring, pads, pads_routing)
        ring_ref = c.add_ref(ring)
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
            c = attach_grating_coupler(c, ["o1", "o2", "o3", "o4"])
        else:
            c = attach_grating_coupler(c, ["o1", "o2"])

        component_list.append(c)
    
    component_list = list(reversed(component_list))

    return component_list

def ring_pn_via_distance(
    radius: float=10,
    gap: float=0.25,
    angle: float=20,
    dist_pn_to_wg: float=0.79,
    via_gaps: np.ndarray=None,
    cs: CrossSectionSpec=rib_cs450,
    pn_cs: CrossSectionSpec=pn_cs,
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
        cs (gf.typings.CrossSectionSpec): Cross section of the ring.
        pn_cs (gf.typings.CrossSectionSpec): Cross section of the PN junction.
        pad_spacing (float): Spacing between the pads.

    Returns:
        List of different medium to via gap test structures.
    """
    cs = gf.get_cross_section(cs)
    pn_cs = gf.get_cross_section(pn_cs)

    rng.shuffle(via_gaps)

    component_list = []

    st = gf.path.straight(length=250).extrude(rib_cs450)
    pads = [metal_pad, metal_pad, metal_pad]
    pads = gf.grid(pads, spacing=pad_spacing)

    for via_gap in via_gaps:
        c = gf.Component()
        ring = ring(
            wg=rib_cs450,
            pn=pn_cs(gap_medium_to_via=via_gap),
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
        ring = ring_pn_pad(ring, pads, routing)
        ring_ref = c.add_ref(ring)
        st_left_ref, st_right_ref = [c.add_ref(st) for _ in range(2)]
        st_left_ref.connect("o2", ring_ref.ports["o1"])
        st_right_ref.connect("o1", ring_ref.ports["o2"])

        test_st = gf.path.straight(length=c.dxsize).extrude(rib_cs450)
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
    cs = rib_cs450
    component_list = ring_pn_offset(offsets=offsets, cs=cs)
    c = gf.Component()
    c.add_ref(component_list)
    c = gf.grid(
        c,
        spacing=(500, 86),
        shape=(6, 1),
        align_x="xmin",
        align_y="y"
    )
    
    c.show()

if __name__ == "__main__":
    main()