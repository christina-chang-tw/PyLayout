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
from pylayout.components import ring, straight_with_heater, circular_bend_180, attach_grating_coupler
from pylayout.routing import route_pads_to_ring

def ramzi_design_1ring_draft1(
    radius: float = 10,
    wg: CrossSectionSpec = rib_450,
    pn: CrossSectionSpec = pn_450_with_metal,
    int_len: float = 5.5,
    gap: float = 0.2,
    arm_length: float = 500,
    arm_distance: float = 130,
    heater_length: float = 350,
    dist_pn_to_wg: float = 1.5,
    dist_between_vias: float = 2.75
):
    c = gf.Component()

    wg = gf.get_cross_section(wg)
    pn = gf.get_cross_section(pn)
    mmi_arm_gap = 2.69

    def add_ring(cs1: CrossSectionSpec, cs2: CrossSectionSpec,
                 radius: float, gap: float, int_len: float):
        r = ring(wg=cs1, pn=cs2, radius=radius, gap=gap, int_len=int_len,
                           dist_pn_to_wg=dist_pn_to_wg, dist_between_vias=dist_between_vias, metal_layer=LAYER.METAL)
        pads = gf.grid([metal_pad] * 3, spacing=(25, 25))
        return route_pads_to_ring(r, pads, {
            "1_0_e4": "METAL_TOP_p1",
            "2_0_e4": "METAL_BOT_p1",
            "0_0_e4": "METAL_BOT_p2",
        })

    ring_ref = c.add_ref(add_ring(wg, pn, radius, gap, int_len)).mirror_y()

    st_mzi = gf.path.straight(length=(arm_length - heater_length) / 2).extrude(wg)
    st_ring = gf.path.straight(length=(arm_length - 2 * radius) / 2).extrude(wg)
    mzi_heater = straight_with_heater(length=heater_length,
                                      wg=heater(width=wg.width),
                                      filament=filament(width=Spec.mzi_heater_width),
                                      gap_between_pads=50, 
                                      metal_cs=metal_trace)

    ltst_ref, rtst_ref = [c.add_ref(st_ring) for _ in range(2)]
    lbst_ref, rbst_ref = [c.add_ref(st_mzi) for _ in range(2)]
    mzi_heater_ref = c.add_ref(mzi_heater)

    bend_radius = (arm_distance - mmi_arm_gap) / 4
    bend = circular_bend_180(radius=bend_radius, cs=wg)
    ltbend_ref, lbbend_ref, rtbend_ref, rbbend_ref = [c.add_ref(bend) for _ in range(4)]
    lbbend_ref.mirror_y()
    rtbend_ref.mirror_x()
    rbbend_ref.mirror_x().mirror_y()

    mmi = SOI220nm_1550nm_TE_RIB_2x1_MMI()
    lmmi_ref, rmmi_ref = [c.add_ref(mmi) for _ in range(2)]

    inout_st = gf.path.straight(length=100).extrude(wg)
    in_st_ref, out_st_ref = [c.add_ref(inout_st) for _ in range(2)]

    connections = [
        (lmmi_ref, "o1", in_st_ref, "o2"),
        (lbbend_ref, "o1", lmmi_ref, "o2"),
        (lbst_ref, "o1", lbbend_ref, "o2"),
        (mzi_heater_ref, "o1", lbst_ref, "o2"),
        (rbst_ref, "o1", mzi_heater_ref, "o2"),
        (rbbend_ref, "o1", rbst_ref, "o2"),
        (ltbend_ref, "o2", lmmi_ref, "o3"),
        (ltst_ref, "o1", ltbend_ref, "o1"),
        (ring_ref, "o1", ltst_ref, "o2"),
        (rtst_ref, "o1", ring_ref, "o2"),
        (rtbend_ref, "o1", rtst_ref, "o2"),
        (rmmi_ref, "o2", rtbend_ref, "o1"),
        (rmmi_ref, "o3", rbbend_ref, "o2"),
        (out_st_ref, "o1", rmmi_ref, "o1")
    ]

    for conn in connections:
        conn[0].connect(conn[1], conn[2].ports[conn[3]])

    c.add_port(name="o1", port=in_st_ref.ports["o1"])
    c.add_port(name="o2", port=out_st_ref.ports["o2"])

    c = attach_grating_coupler(c, cs_gc_silicon_1550nm, ["o1", "o2"])
    return c

if __name__ == "__main__":
    c = ramzi_design_1ring_draft1()
    c.show()