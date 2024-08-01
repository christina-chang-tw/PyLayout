from functools import partial

import numpy as np

import gdsfactory as gf
from gdsfactory.typings import CrossSectionSpec, Dict, Component, CrossSection

from cornerstone import (
    metal_pad,
    pn_450_with_metal_and_heater,
    pn_450_with_metal,
    rib_450,
    filament,
    heater,
    metal,
    Spec,
    SOI220nm_1550nm_TE_RIB_2x1_MMI,
    LAYER,
    cs_gc_silicon_1550nm
)
from pylayout.components import ring, straight_with_filament, attach_grating_coupler, mmi_splitter
from pylayout.routing import route_pads_to_ring, strategy1, strategy2

def ramzi_dual_rings_gsgsg_gsgsg(
    wg: CrossSectionSpec = None,
    pn_heater: CrossSectionSpec = None,
    pn_ring: CrossSectionSpec = None,
    mzi_heater: CrossSectionSpec = None,
    arm_distance: float = 110,
    radius: float = 10,
    gap: float = 0.2,
    int_len: float = None,
    int_angle: float = None,
    heater_length: float = 250,
    arm_length: float = 800,
    dist_pn_to_wg: float = 0.79,
    dist_y: float = None,
    dist_between_vias: float = 2.75,
    heater_percent: float = 0.75
):
    if arm_length < 2 * radius:
        raise ValueError("Arm length should be greater than 2*radius")

    c = gf.Component()
    wg, pn_heater, pn_ring, mzi_heater = map(gf.get_cross_section, [wg, pn_heater, pn_ring, mzi_heater])

    def add_ring(wg: CrossSectionSpec, pn: CrossSectionSpec, radius: float,
                 gap: float, int_len: float, int_angle: float, routing: Dict, 
                 pads: Component=None, align_pad_number=None, heater_percent=None):
        r = ring(wg=wg, pn=pn, radius=radius, gap=gap, int_len=int_len, int_angle=int_angle,
                           dist_pn_to_wg=dist_pn_to_wg, dist_between_vias=dist_between_vias,
                           dist_y=dist_y, heater_percent=heater_percent)
        pads = gf.grid([metal_pad] * 5, spacing=(25, 25)) if pads is None else pads
        return route_pads_to_ring(r, pads, routing, align_pad_number=align_pad_number)

    rheater_routing = {
        "1_0_e4": "METAL_TOP_p1",
        "3_0_e4": "HEATER_METAL_p1",
        "4_0_e4": "METAL_BOT_p1",    
    }
    r_routing = {
        "2_0_e4": "METAL_BOT_p2",
        "3_0_e4": "METAL_TOP_p1",
        "4_0_e4": "METAL_BOT_p1",
    }
    ring_heater_full = add_ring(wg, pn_heater, radius, gap, int_len, int_angle, rheater_routing, heater_percent=heater_percent)
    ring_full = add_ring(wg, pn_ring, radius, gap, int_len, int_angle, r_routing, align_pad_number=4)
    
    ring_heater_full_ref = c.add_ref(ring_heater_full)
    ring_full_ref = c.add_ref(ring_full).mirror_y()
    ring_full_ref.dx = ring_heater_full_ref.dx

    extra_length = arm_length - 2 * radius - heater_length - 50
    if extra_length < 0:
        raise ValueError("Arm length should be greater than 2*radius + heater_length")

    mzi_heater_ref = c.add_ref(straight_with_filament(length=heater_length, wg=wg,
        filament=mzi_heater, gap_between_pads=50)).mirror_y()

    st_short = gf.path.straight(length=extra_length * 1/5).extrude(wg)
    st_inter = gf.path.straight(length=extra_length * 3/5).extrude(wg)
    st_long2 = gf.path.straight(length=heater_length + st_short.dxsize).extrude(wg)

    ltst_ref, lbst_ref, rtst_ref = [c.add_ref(st_short) for _ in range(3)]
    rbst_ref = c.add_ref(st_long2)
    tinter_ref, binter_ref = [c.add_ref(st_inter) for _ in range(2)]

    mmi = mmi_splitter(SOI220nm_1550nm_TE_RIB_2x1_MMI, 50, wg, arm_distance)
    lmmi_splitter_ref, rmmi_splitter_ref = [c.add_ref(mmi) for _ in range(2)]
    rmmi_splitter_ref.mirror_y()

    connections = [
        (lbst_ref, "o1", lmmi_splitter_ref, "o3"),
        (ring_heater_full_ref, "o2", lbst_ref, "o2"),
        (binter_ref, "o1", ring_heater_full_ref, "o1"),
        (rbst_ref, "o1", binter_ref, "o2"),
        (ltst_ref, "o1", lmmi_splitter_ref, "o2"),
        (ring_full_ref, "o2", ltst_ref, "o2"),
        (tinter_ref, "o1", ring_full_ref, "o1"),
        (mzi_heater_ref, "o1", tinter_ref, "o2"),
        (rtst_ref, "o1", mzi_heater_ref, "o2"),
        (rmmi_splitter_ref, "o2", rtst_ref, "o2"),
    ]
    for c1, p1, c2, p2 in connections:
        c1.connect(p1, c2.ports[p2])

    cs = metal(width=20, layer=LAYER.METAL)
    port = ring_full_ref.ports["pad_0_0_e1"]
    xsize = mzi_heater_ref.ports["e2"].dx + cs.width/2 - port.dx
    ysize = port.dy - port.dwidth/2 + cs.width - mzi_heater_ref.ports["e2"].dy - 9
    strategy1(
        c, start_x=port.dx, start_y=port.dy - port.dwidth/2 + cs.width/2,
        port=mzi_heater_ref.ports["e2"], xsize=xsize, ysize=ysize, cs=cs, layers=[LAYER.METAL, LAYER.FILAMENT]
    )
    xsize = mzi_heater_ref.ports["e1"].dx - ring_full_ref.ports["pad_1_0_e4"].dx + cs.width
    ysize = ring_full_ref.ports["pad_1_0_e4"].dy - mzi_heater_ref.ports["e1"].dy - 9
    strategy2(c, port1=ring_full_ref.ports["pad_1_0_e4"], port2=mzi_heater_ref.ports["e1"], first_st_len=10, xsize=xsize, ysize=ysize, cs=cs, layers=[LAYER.METAL, LAYER.FILAMENT], gap=7)


    xsize = ring_heater_full_ref.ports["ring_METAL_BOT_p2"].dx + ring_heater_full_ref.ports["ring_METAL_BOT_p2"].dwidth/2 - ring_heater_full_ref.ports["ring_HEATER_METAL_p2"].dx + ring_heater_full_ref.ports["ring_HEATER_METAL_p2"].dwidth/2
    ysize = 3
    rect = gf.components.rectangle(size=(xsize, ysize), layer=LAYER.METAL)
    rect_ref = c.add_ref(rect)
    rect_ref.dymin = ring_heater_full_ref.ports["ring_HEATER_METAL_p2"].dy
    rect_ref.dxmin = ring_heater_full_ref.ports["ring_HEATER_METAL_p2"].dx - ring_heater_full_ref.ports["ring_HEATER_METAL_p2"].dwidth/2
    gf.routing.route_quad(
        c, rect_ref.ports["e4"], ring_heater_full_ref.ports["pad_0_0_e4"],
        layer=LAYER.METAL
    )

    c.add_port(name="o1", port=lmmi_splitter_ref.ports["o1"])
    c.add_port(name="o2", port=rmmi_splitter_ref.ports["o1"])

    c = attach_grating_coupler(c, cs_gc_silicon_1550nm, ["o1", "o2"])
    c.flatten()
    return c


def ramzi_dual_rings_gsgsg_gssg(
    wg: CrossSectionSpec = None,
    pn_heater: CrossSectionSpec = None,
    pn_ring: CrossSectionSpec = None,
    mzi_heater: CrossSectionSpec = None,
    arm_distance: float = 110,
    radius: float = 10,
    gap: float = 0.2,
    int_angle: float = None,
    int_len: float = None,
    heater_length: float = 250,
    arm_length: float = 800,
    dist_pn_to_wg: float = 0.79,
    dist_y: float=0.8, 
    dist_between_vias: float = 2.75,
    heater_percent: float = 0.75
):
    if arm_length < 2 * radius:
        raise ValueError("Arm length should be greater than 2*radius")

    c = gf.Component()
    wg, pn_heater, pn_ring, mzi_heater = map(gf.get_cross_section, [wg, pn_heater, pn_ring, mzi_heater])

    def add_ring(wg: CrossSectionSpec, pn: CrossSectionSpec, radius: float,
                 gap: float, clength: float, cangle: float, routing: Dict, pads: Component=None, align_pad_number=None, heater_percent=None):
        r = ring(wg=wg, pn=pn, radius=radius, gap=gap, int_len=clength, int_angle=cangle,
                           dist_pn_to_wg=dist_pn_to_wg, dist_between_vias=dist_between_vias,
                           heater_percent=heater_percent, dist_y=dist_y)
        pads = gf.grid([metal_pad] * 5, spacing=(25, 25)) if pads is None else pads
        return route_pads_to_ring(r, pads, routing, align_pad_number=align_pad_number)

    rheater_routing = {
        "1_0_e4": "METAL_TOP_p1",
        "2_0_e4": "HEATER_METAL_p1",
        "3_0_e4": "METAL_BOT_p1",    
    }
    r_routing = {
        "2_0_e4": "METAL_BOT_p2",
        "3_0_e4": "METAL_TOP_p1",
        "4_0_e4": "METAL_BOT_p1",
    }
    pads = gf.grid([metal_pad] * 4, spacing=(25, 25))
    ring_heater_full = add_ring(wg, pn_heater, radius, gap, int_len, int_angle, rheater_routing, pads=pads, heater_percent=heater_percent)
    ring_full = add_ring(wg, pn_ring, radius, gap, int_len, int_angle, r_routing, align_pad_number=4)
    
    ring_heater_full_ref = c.add_ref(ring_heater_full)
    ring_full_ref = c.add_ref(ring_full).mirror_y()
    ring_full_ref.dx = ring_heater_full_ref.dx

    extra_length = arm_length - 2 * radius - heater_length - 50
    if extra_length < 0:
        raise ValueError("Arm length should be greater than 2*radius + heater_length")

    mzi_heater_ref = c.add_ref(straight_with_filament(length=heater_length, wg=wg,
        filament=mzi_heater, gap_between_pads=50)).mirror_y()

    st_short = gf.path.straight(length=extra_length * 1/5).extrude(wg)
    st_inter = gf.path.straight(length=extra_length * 3/5).extrude(wg)
    st_long2 = gf.path.straight(length=heater_length + st_short.dxsize).extrude(wg)

    ltst_ref, lbst_ref, rtst_ref = [c.add_ref(st_short) for _ in range(3)]
    rbst_ref = c.add_ref(st_long2)
    tinter_ref, binter_ref = [c.add_ref(st_inter) for _ in range(2)]

    mmi = mmi_splitter(SOI220nm_1550nm_TE_RIB_2x1_MMI, 50, wg, arm_distance)
    lmmi_splitter_ref, rmmi_splitter_ref = [c.add_ref(mmi) for _ in range(2)]
    rmmi_splitter_ref.mirror_y()

    connections = [
        (lbst_ref, "o1", lmmi_splitter_ref, "o3"),
        (ring_heater_full_ref, "o2", lbst_ref, "o2"),
        (binter_ref, "o1", ring_heater_full_ref, "o1"),
        (rbst_ref, "o1", binter_ref, "o2"),
        (ltst_ref, "o1", lmmi_splitter_ref, "o2"),
        (ring_full_ref, "o2", ltst_ref, "o2"),
        (tinter_ref, "o1", ring_full_ref, "o1"),
        (mzi_heater_ref, "o1", tinter_ref, "o2"),
        (rtst_ref, "o1", mzi_heater_ref, "o2"),
        (rmmi_splitter_ref, "o2", rtst_ref, "o2"),
    ]
    for c1, p1, c2, p2 in connections:
        c1.connect(p1, c2.ports[p2])

    cs = metal(width=20, layer=LAYER.METAL)
    port = ring_full_ref.ports["pad_0_0_e1"]
    xsize = mzi_heater_ref.ports["e2"].dx + cs.width/2 - port.dx
    ysize = port.dy - port.dwidth/2 + cs.width - mzi_heater_ref.ports["e2"].dy - 9
    strategy1(
        c, start_x=port.dx, start_y=port.dy - port.dwidth/2 + cs.width/2,
        port=mzi_heater_ref.ports["e2"], xsize=xsize, ysize=ysize, cs=cs, layers=[LAYER.METAL, LAYER.FILAMENT]
    )
    xsize = mzi_heater_ref.ports["e1"].dx - ring_full_ref.ports["pad_1_0_e4"].dx + cs.width
    ysize = ring_full_ref.ports["pad_1_0_e4"].dy - mzi_heater_ref.ports["e1"].dy - 9
    strategy2(c, port1=ring_full_ref.ports["pad_1_0_e4"], port2=mzi_heater_ref.ports["e1"], first_st_len=10, xsize=xsize, ysize=ysize, cs=cs, layers=[LAYER.METAL, LAYER.FILAMENT], gap=7)


    xsize = ring_heater_full_ref.ports["ring_METAL_BOT_p2"].dx + ring_heater_full_ref.ports["ring_METAL_BOT_p2"].dwidth/2 - ring_heater_full_ref.ports["ring_HEATER_METAL_p2"].dx + ring_heater_full_ref.ports["ring_HEATER_METAL_p2"].dwidth/2
    ysize = 3
    rect = gf.components.rectangle(size=(xsize, ysize), layer=LAYER.METAL)
    rect_ref = c.add_ref(rect)
    rect_ref.dymin = ring_heater_full_ref.ports["ring_HEATER_METAL_p2"].dy
    rect_ref.dxmin = ring_heater_full_ref.ports["ring_HEATER_METAL_p2"].dx - ring_heater_full_ref.ports["ring_HEATER_METAL_p2"].dwidth/2
    gf.routing.route_quad(
        c, rect_ref.ports["e4"], ring_heater_full_ref.ports["pad_0_0_e4"],
        layer=LAYER.METAL
    )

    c.add_port(name="o1", port=lmmi_splitter_ref.ports["o1"])
    c.add_port(name="o2", port=rmmi_splitter_ref.ports["o1"])

    c = attach_grating_coupler(c, cs_gc_silicon_1550nm, ["o1", "o2"])
    c.flatten()
    return c

if __name__ == "__main__":
    wg = rib_450
    pn_heater = pn_450_with_metal_and_heater
    pn = pn_450_with_metal
    arm_distance = 110
    radius = 10
    angle = 20
    heater_length = 250
    arm_length = 800
    dist_to_wg = 0.79
    dist_between_vias = 2.75
    heater_percent = 0.78

    dual_ring = partial(
        ramzi_dual_rings_gsgsg_gsgsg,
        cs=wg,
        pn_heater=pn_heater,
        pn_ring=pn,
        arm_distance=arm_distance,
        radius=radius,
        int_angle=angle,
        heater_length=heater_length,
        arm_length=arm_length,
        dist_pn_to_wg=dist_to_wg,
        dist_between_vias=dist_between_vias,
        heater_percent=heater_percent
    )

    gaps = np.arange(0.2, 0.32, 0.02)
    component_lists = []

    for gap in gaps:
        c = dual_ring(gap=gap)
        component_lists.append(c)      

    c = gf.grid(
        components=component_lists,
        spacing=40,
        shape=(len(gaps), 1),
        align_x="center"
    )
    base = gf.Component()
    c_ref = base.add_ref(c)
    c_ref.drotate(90)
    base.show()