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
    CornerstoneSpec,
    SOI220nm_1550nm_TE_RIB_2x1_MMI,
    LAYER,
    cs_gc_silicon_1550nm
)
from pylayout.components import ring, straight_with_heater, attach_grating_coupler, mmi_splitter
from pylayout.routing import route_pads_to_ring, strategy1, strategy2

@gf.cell
def ramzi_design_2rings_draft1(
    cs: CrossSectionSpec = None,
    pn1: CrossSectionSpec = None,
    pn2: CrossSectionSpec = None,
    arm_distance: float = 110,
    radius: float = 10,
    gap: float = 0.2,
    int_len: float = 5.5,
    heater_length: float = 250,
    arm_length: float = 800,
    dist_pn_to_wg: float = 0.79,
    dist_between_vias: float = 2.75,
    heater_percent: float = 0.78
):
    if arm_length < 2 * radius:
        raise ValueError("Arm length should be greater than 2*radius")

    c = gf.Component()
    cs, pn1, pn2 = map(gf.get_cross_section, [cs, pn1, pn2])

    def add_ring(wg: CrossSectionSpec, pn: CrossSectionSpec, radius: float,
                 gap: float, int_len: float, routing: Dict, pads: Component=None, align_pad_number=None, heater_percent=None):
        r = ring(wg=wg, pn=pn, radius=radius, gap=gap, int_len=int_len,
                           dist_pn_to_wg=dist_pn_to_wg, dist_between_vias=dist_between_vias,
                           heater_percent=heater_percent, metal_layer=LAYER.METAL)
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
    ring_heater_full = add_ring(cs, pn1, radius, gap, int_len, rheater_routing, heater_percent=heater_percent)
    ring_full = add_ring(cs, pn2, radius, gap, int_len, r_routing, align_pad_number=4)
    
    ring_heater_full_ref = c.add_ref(ring_heater_full)
    ring_full_ref = c.add_ref(ring_full).mirror_y()
    ring_full_ref.dx = ring_heater_full_ref.dx

    extra_length = arm_length - 2 * radius - heater_length - 50
    if extra_length < 0:
        raise ValueError("Arm length should be greater than 2*radius + heater_length")

    mzi_heater_ref = c.add_ref(straight_with_heater(length=heater_length, wg=heater(width=0.45),
        filament=filament(width=CornerstoneSpec.mzi_heater_width), gap_between_pads=50)).mirror_y()

    st_short = gf.path.straight(length=extra_length * 1/5).extrude(cs)
    st_inter = gf.path.straight(length=extra_length * 3/5).extrude(cs)
    st_long2 = gf.path.straight(length=heater_length + st_short.dxsize).extrude(cs)

    ltst_ref, lbst_ref, rtst_ref = [c.add_ref(st_short) for _ in range(3)]
    rbst_ref = c.add_ref(st_long2)
    tinter_ref, binter_ref = [c.add_ref(st_inter) for _ in range(2)]

    mmi = mmi_splitter(SOI220nm_1550nm_TE_RIB_2x1_MMI, 50, cs, arm_distance)
    lmmi_splitter_ref, rmmi_splitter_ref = [c.add_ref(mmi) for _ in range(2)]
    rmmi_splitter_ref.mirror_y()

    connections = [
        (lbst_ref, "o1", lmmi_splitter_ref, "o3"),
        (ring_heater_full_ref, "o1", lbst_ref, "o2"),
        (binter_ref, "o1", ring_heater_full_ref, "o2"),
        (rbst_ref, "o1", binter_ref, "o2"),
        (ltst_ref, "o1", lmmi_splitter_ref, "o2"),
        (ring_full_ref, "o1", ltst_ref, "o2"),
        (tinter_ref, "o1", ring_full_ref, "o2"),
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
    c = ramzi_design_2rings_draft1(rib_450, pn_450_with_metal_and_heater, pn_450_with_metal)
    c.show()