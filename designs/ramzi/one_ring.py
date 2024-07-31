import numpy as np
from functools import partial

import gdsfactory as gf
from gdsfactory.typings import CrossSectionSpec

from cornerstone import (
    metal_pad,
    rib_450,
    pn_450_with_metal,
    filament,
    heater,
    metal_trace,
    LAYER,
    SOI220nm_1550nm_TE_RIB_2x1_MMI,
    cs_gc_silicon_1550nm
)
from cornerstone import CornerstoneSpec as Spec
from pylayout.components import ring, straight_with_heater, attach_grating_coupler, mmi_splitter, coupler_2x2
from pylayout.routing import route_pads_to_ring
from ..test_structures import straight

def ramzi_one_ring(
    radius: float = 10,
    wg: CrossSectionSpec = rib_450,
    pn: CrossSectionSpec = pn_450_with_metal,
    mzi_heater: CrossSectionSpec = heater,
    int_len: float = None,
    int_angle: float = None,
    gap: float = 0.2,
    arm_length: float = 500,
    arm_distance: float = 130,
    heater_length: float = 350,
    heater_percent: float = 0.8,
    dist_pn_to_wg: float = 1.5,
    dist_y: float = None,
    dist_between_vias: float = 2.75
):
    c = gf.Component()

    wg = gf.get_cross_section(wg)
    pn = gf.get_cross_section(pn)
    mzi_heater = gf.get_cross_section(mzi_heater)

    def add_ring(cs1: CrossSectionSpec, cs2: CrossSectionSpec,
                 radius: float, gap: float, int_len: float, int_angle: float, dist_pn_to_wg: float, dist_y: float, dist_between_vias: float, heater_percent: float):
        r = ring(wg=cs1, pn=cs2, radius=radius, gap=gap, int_len=int_len, int_angle=int_angle,
                           dist_pn_to_wg=dist_pn_to_wg, dist_between_vias=dist_between_vias, heater_percent=heater_percent, dist_y=dist_y)
        pads = gf.grid([metal_pad] * 3, spacing=(25, 25))
        return route_pads_to_ring(r, pads, {
            "1_0_e4": "METAL_TOP_p1",
            "2_0_e4": "METAL_BOT_p1",
            "0_0_e4": "METAL_BOT_p2",
        })

    ring_ref = c.add_ref(add_ring(wg, pn, radius, gap, int_len,
                                  int_angle, dist_pn_to_wg=dist_pn_to_wg, dist_y=dist_y, dist_between_vias=dist_between_vias, heater_percent=heater_percent)).mirror_y()

    st_mzi = gf.path.straight(length=(arm_length - heater_length) / 2).extrude(wg)
    st_ring = gf.path.straight(length=(arm_length - 2 * radius) / 2).extrude(wg)
    mzi_heater = straight_with_heater(length=heater_length,
                                      wg=wg,
                                      filament=mzi_heater,
                                      gap_between_pads=50, 
                                      metal_cs=metal_trace)

    ltst_ref, rtst_ref = [c.add_ref(st_ring) for _ in range(2)]
    lbst_ref, rbst_ref = [c.add_ref(st_mzi) for _ in range(2)]
    mzi_heater_ref = c.add_ref(mzi_heater)

    splitter = mmi_splitter(arm_distance=arm_distance, mmi=SOI220nm_1550nm_TE_RIB_2x1_MMI(), cs=wg)
    lsplitter_ref, rsplitter_ref = [c.add_ref(splitter) for _ in range(2)]

    connections = [
        (ltst_ref, "o1", lsplitter_ref, "o2"),
        (ring_ref, "o2", ltst_ref, "o2"),
        (rtst_ref, "o1", ring_ref, "o1"),
        (rsplitter_ref, "o3", rtst_ref, "o2"),
        (lbst_ref, "o1", lsplitter_ref, "o3"),
        (mzi_heater_ref, "o1", lbst_ref, "o2"),
        (rbst_ref, "o1", rsplitter_ref, "o2"),
    ]

    for conn in connections:
        conn[0].connect(conn[1], conn[2].ports[conn[3]])

    c.add_port(name="o1", port=lsplitter_ref.ports["o1"])
    c.add_port(name="o2", port=rsplitter_ref.ports["o1"])

    c = attach_grating_coupler(c, cs_gc_silicon_1550nm(), ["o1", "o2"])
    temp = gf.Component()
    c_ref = temp.add_ref(c)
    st = straight(c_ref.dxsize - cs_gc_silicon_1550nm().dxsize*2, cs=wg, gc=cs_gc_silicon_1550nm())
    st_ref = temp.add_ref(st)
    st_ref.dx = c_ref.dx
    st_ref.dymax = c_ref.dymax - 40

    return temp

def ramzi_one_ring_2x2(
    radius: float = 10,
    wg: CrossSectionSpec = rib_450,
    pn: CrossSectionSpec = pn_450_with_metal,
    mzi_heater: CrossSectionSpec = heater,
    int_len: float = None,
    int_angle: float = None,
    gap: float = 0.2,
    coupler_gap: float = 0.25,
    coupler_length: float = 5,
    arm_length: float = 500,
    arm_distance: float = 130,
    heater_length: float = 350,
    heater_percent: float = 0.8,
    dist_pn_to_wg: float = 1.5,
    dist_y: float = None,
    dist_between_vias: float = 2.75
):
    c = gf.Component()

    wg = gf.get_cross_section(wg)
    pn = gf.get_cross_section(pn)
    mzi_heater = gf.get_cross_section(mzi_heater)

    def add_ring(cs1: CrossSectionSpec, cs2: CrossSectionSpec,
                 radius: float, gap: float, int_len: float, int_angle: float, dist_pn_to_wg: float, dist_y: float, dist_between_vias: float, heater_percent: float):
        r = ring(wg=cs1, pn=cs2, radius=radius, gap=gap, int_len=int_len, int_angle=int_angle,
                           dist_pn_to_wg=dist_pn_to_wg, dist_between_vias=dist_between_vias, heater_percent=heater_percent, dist_y=dist_y)
        pads = gf.grid([metal_pad] * 3, spacing=(25, 25))
        return route_pads_to_ring(r, pads, {
            "1_0_e4": "METAL_TOP_p1",
            "2_0_e4": "METAL_BOT_p1",
            "0_0_e4": "METAL_BOT_p2",
        })

    r = add_ring(wg, pn, radius, gap, int_len,
                                  int_angle, dist_pn_to_wg=dist_pn_to_wg, dist_y=dist_y, dist_between_vias=dist_between_vias, heater_percent=heater_percent)
    ring_ref = c.add_ref(r).mirror_y()

    st_mzi = gf.path.straight(length=(arm_length - heater_length) / 2).extrude(wg)
    st_ring = gf.path.straight(length=(arm_length - 2 * radius) / 2).extrude(wg)
    mzi_heater = straight_with_heater(length=heater_length,
                                      wg=wg,
                                      filament=mzi_heater,
                                      gap_between_pads=50, 
                                      metal_cs=metal_trace)

    ltst_ref, rtst_ref = [c.add_ref(st_ring) for _ in range(2)]
    lbst_ref, rbst_ref = [c.add_ref(st_mzi) for _ in range(2)]
    mzi_heater_ref = c.add_ref(mzi_heater)

    
    lsplitter_ref = c.add_ref(coupler_2x2(gap=coupler_gap, length=coupler_length, arm_distance=arm_distance, cs=wg))
    rsplitter_ref = c.add_ref(mmi_splitter(arm_distance=arm_distance, mmi=SOI220nm_1550nm_TE_RIB_2x1_MMI(), cs=wg))
    rsplitter_ref.mirror_x()

    connections = [
        (ltst_ref, "o1", lsplitter_ref, "o3"),
        (ring_ref, "o2", ltst_ref, "o2"),
        (rtst_ref, "o1", ring_ref, "o1"),
        (rsplitter_ref, "o2", rtst_ref, "o2"),
        (lbst_ref, "o1", lsplitter_ref, "o4"),
        (mzi_heater_ref, "o1", lbst_ref, "o2"),
        (rbst_ref, "o1", rsplitter_ref, "o3"),
    ]

    for conn in connections:
        conn[0].connect(conn[1], conn[2].ports[conn[3]])

    c.add_port(name="o1", port=lsplitter_ref.ports["o1"])
    c.add_port(name="o2", port=lsplitter_ref.ports["o2"])
    c.add_port(name="o3", port=rsplitter_ref.ports["o1"])

    c = attach_grating_coupler(c, cs_gc_silicon_1550nm(), ["o1", "o2", "o3"])

    temp = gf.Component()
    c_ref = temp.add_ref(c)
    st = straight(c_ref.dxsize - cs_gc_silicon_1550nm().dxsize*2, cs=wg, gc=cs_gc_silicon_1550nm())
    st_ref = temp.add_ref(st)
    st_ref.dx = c_ref.dx
    st_ref.dymax = c_ref.dymax - 40

    return temp

if __name__ == "__main__":
    wg = rib_450
    pn = pn_450_with_metal
    heater = filament
    heater_length = 400
    arm_distance = 120
    radius = 10
    angle = 20
    arm_length = 500
    dist_to_wg = 0.79
    dist_y = None
    coupler_gap = 0.25
    variables = ((0.28, 9), (0.28, 11), (0.28, 13), (0.315, 9.5), (0.315, 11.5), (0.315, 13.5), (0.34, 10.5), (0.34, 12.5), (0.34, 14.5))

    gaps = (0.28, 0.315, 0.34)

    ramzi = partial(
        ramzi_one_ring_2x2,
        wg=wg,
        pn=pn,
        mzi_heater=heater,
        heater_length=heater_length,
        arm_distance=arm_distance,
        radius=radius,
        int_angle=angle,
        arm_length=arm_length,
        dist_pn_to_wg=dist_to_wg,
        dist_y=dist_y,
        coupler_gap=coupler_gap
    )
    component_lists = []

    for gap, cl in variables:
        c = ramzi(gap=gap, coupler_length=cl)
        component_lists.append(c)

    c = gf.grid(
        components=component_lists,
        spacing=20,
        shape=(3, 3),
        align_x="center"
    )
    base = gf.Component()
    c_ref = base.add_ref(c)

    base.show()