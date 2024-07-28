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
from pylayout.components import ring, straight_with_heater, circular_bend_180, attach_grating_coupler, mmi_splitter
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

    splitter = mmi_splitter(arm_distance=arm_distance, mmi=SOI220nm_1550nm_TE_RIB_2x1_MMI(), cs=wg)
    lsplitter_ref, rsplitter_ref = [c.add_ref(splitter) for _ in range(2)]

    connections = [
        (ltst_ref, "o1", lsplitter_ref, "o2"),
        (ring_ref, "o1", ltst_ref, "o2"),
        (rtst_ref, "o1", ring_ref, "o2"),
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
    return c

if __name__ == "__main__":
    c = ramzi_design_1ring_draft1()
    c.show()