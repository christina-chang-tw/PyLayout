import gdsfactory as gf
from gdsfactory.typings import CrossSectionSpec

from pylayout.components import ring, attach_grating_coupler
from pylayout.routing import route_pads_to_ring
from cornerstone import pn, pn_450_with_heater, rib_450, LAYER, metal_pad, cs_gc_silicon_1550nm
from cornerstone import CornerstoneSpec as Spec

@gf.cell
def test_ring_heater_width(
    radius: float = 10,
    angle: float = 20,
    gap: float = 0.3,
    dist_to_pn_wg: float = 0.79,
    cs: CrossSectionSpec = rib_450,
    heater_width: float = 0.9,
    max_length: float = 500,
):
    cs = gf.get_cross_section(cs)
    st = gf.path.straight(length=max_length/2 - radius).extrude(cs)

    c = gf.Component()
    r = ring(
        wg=cs,
        pn=pn_450_with_heater(width_heater=heater_width),
        radius=radius,
        gap=gap,
        int_angle=angle,
        dist_pn_to_wg=dist_to_pn_wg
    )
    pads = [metal_pad, metal_pad]
    pads = gf.grid(pads, spacing=(25, 25))
    routing = {
        "0_0_e4": "HEATER_METAL_p2",
        "1_0_e4": "HEATER_METAL_p1",
    }
    r = route_pads_to_ring(r, pads, routing)
    ring_ref = c.add_ref(r)
    lst_ref, rst_ref = [c.add_ref(st) for _ in range(2)]
    lst_ref.connect("o2", ring_ref.ports["o1"])
    rst_ref.connect("o1", ring_ref.ports["o2"])

    c.add_port(name="o1", port=lst_ref.ports["o1"])
    c.add_port(name="o2", port=rst_ref.ports["o2"])
    c = attach_grating_coupler(c, cs_gc_silicon_1550nm, ["o1", "o2"])

    c.flatten()
    return c

@gf.cell
def test_ring_metal_heater_distance(
    radius: float = 10,
    gap: float = 0.35,
    angle: float = 20,
    dist_to_pn_wg: float = 0.79,
    cs: CrossSectionSpec = rib_450,
):
    cs = gf.get_cross_section(cs)
    # version 1 - with heater
    c = gf.Component()
    r = ring(
        wg=cs,
        pn=pn(
            width=0.45,
            layer_heater=LAYER.VIA,
            width_heater=Spec.ring_heater_width,
            layer_metal=LAYER.METAL,
            layer_via=LAYER.VIA,
            via_min_distance=Spec.min_via_distance,
        ),
        radius=radius,
        gap=gap,
        int_angle=angle,
        dist_pn_to_wg=dist_to_pn_wg,
    )
    pads = [metal_pad, metal_pad, metal_pad]
    pads = gf.grid(pads, spacing=(25, 25))
    routing = {
        "0_0_e4": "METAL_BOT_p2",
        "1_0_e4": "METAL_TOP_p1",
        "2_0_e4": "METAL_BOT_p1",
    }
    st = gf.path.straight(length=250).extrude(cs)
    r = route_pads_to_ring(r, pads, routing)
    ring_ref = c.add_ref(r)
    st_left_ref = c.add_ref(st)
    st_right_ref = c.add_ref(st)
    st_left_ref.connect("o2", ring_ref.ports["o1"])
    st_right_ref.connect("o1", ring_ref.ports["o2"])

    test_st = gf.path.straight(length=c.dxsize).extrude(cs)
    test_st_ref = c.add_ref(test_st)
    test_st_ref.dx = ring_ref.dx
    test_st_ref.dymin = ring_ref.dymin - 30

    c.add_port(name="o1", port=st_left_ref.ports["o1"])
    c.add_port(name="o2", port=st_right_ref.ports["o2"])
    c.add_port(name="o3", port=test_st_ref.ports["o1"])
    c.add_port(name="o4", port=test_st_ref.ports["o2"])
    c = attach_grating_coupler(c, ["o1", "o2", "o3", "o4"])

    # version 2 - without heater but same structure
    c = gf.Component()
    r = ring(
        wg=cs,
        pn=pn(
            width=0.45,
            layer_heater=LAYER.BLANK,
            width_heater=Spec.ring_heater_width,
            layer_metal=LAYER.METAL,
            layer_via=LAYER.VIA,
            via_min_distance=Spec.min_via_distance,
        ),
        radius=radius,
        gap=gap,
        int_angle=angle,
        dist_to_pn_wg=dist_to_pn_wg,
    )
    pads = [metal_pad, metal_pad, metal_pad]
    pads = gf.grid(pads, spacing=(25, 25))
    routing = {
        "0_0_e4": "METAL_BOT_p2",
        "1_0_e4": "METAL_TOP_p1",
        "2_0_e4": "METAL_BOT_p1",
    }
    st = gf.path.straight(length=250).extrude(cs)
    r = route_pads_to_ring(r, pads, routing)
    ring_ref = c.add_ref(r)
    st_left_ref = c.add_ref(st)
    st_right_ref = c.add_ref(st)
    st_left_ref.connect("o2", ring_ref.ports["o1"])
    st_right_ref.connect("o1", ring_ref.ports["o2"])

    test_st = gf.path.straight(length=c.dxsize).extrude(cs)
    test_st_ref = c.add_ref(test_st)
    test_st_ref.dx = ring_ref.dx
    test_st_ref.dymin = ring_ref.dymin - 30

    c.add_port(name="o1", port=st_left_ref.ports["o1"])
    c.add_port(name="o2", port=st_right_ref.ports["o2"])
    c.add_port(name="o3", port=test_st_ref.ports["o1"])
    c.add_port(name="o4", port=test_st_ref.ports["o2"])
    c = attach_grating_coupler(c, ["o1", "o2", "o3", "o4"])

    # version 3 - normal case
    c = gf.Component()
    r = ring(
        wg=cs,
        pn=pn(
            width=0.45,
            layer_metal=LAYER.METAL,
            layer_via=LAYER.VIA,
            via_min_distance=Spec.min_via_distance,
        ),
        radius=radius,
        gap=gap,
        int_angle=angle,
    )
    pads = [metal_pad, metal_pad, metal_pad]
    pads = gf.grid(pads, spacing=(25, 25))
    routing = {
        "0_0_e4": "METAL_BOT_p2",
        "1_0_e4": "METAL_TOP_p1",
        "2_0_e4": "METAL_BOT_p1",
    }
    st = gf.path.straight(length=250).extrude(cs)
    r = route_pads_to_ring(r, pads, routing)
    ring_ref = c.add_ref(r)
    st_left_ref = c.add_ref(st)
    st_right_ref = c.add_ref(st)
    st_left_ref.connect("o2", ring_ref.ports["o1"])
    st_right_ref.connect("o1", ring_ref.ports["o2"])

    test_st = gf.path.straight(length=c.dxsize).extrude(cs)
    test_st_ref = c.add_ref(test_st)
    test_st_ref.dx = ring_ref.dx
    test_st_ref.dymin = ring_ref.dymin - 30

    c.add_port(name="o1", port=st_left_ref.ports["o1"])
    c.add_port(name="o2", port=st_right_ref.ports["o2"])
    c.add_port(name="o3", port=test_st_ref.ports["o1"])
    c.add_port(name="o4", port=test_st_ref.ports["o2"])
    c = attach_grating_coupler(c, cs_gc_silicon_1550nm, ["o1", "o2", "o3", "o4"])

    return c