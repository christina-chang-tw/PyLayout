import gdsfactory as gf

def test_ring_heater_width():
    radius = 10
    heater_widths = [0.9, 1.8, 2.7, 3.6]
    xmax = 500

    st = gf.path.straight(length=xmax/2 - radius).extrude(rib_cs450)
    component_list = []
    for width in heater_widths:
        c = gf.Component()
        ring = ring(
            wg=rib_cs450,
            pn=pn_cs450_with_heater(width_heater=width),
            radius=radius,
            gap=0.37,
            int_angle=20,
            dist_pn_to_wg=0.79
        )
        pads = [metal_pad, metal_pad]
        pads = gf.grid(pads, spacing=(25, 25))
        routing = {
            "0_0_e4": "HEATER_METAL_p2",
            "1_0_e4": "HEATER_METAL_p1",
        }
        ring = ring_pn_pad(ring, pads, routing)
        ring_ref = c.add_ref(ring)
        lst_ref, rst_ref = [c.add_ref(st) for _ in range(2)]
        lst_ref.connect("o2", ring_ref.ports["o1"])
        rst_ref.connect("o1", ring_ref.ports["o2"])

        c.add_port(name="o1", port=lst_ref.ports["o1"])
        c.add_port(name="o2", port=rst_ref.ports["o2"])
        c = attach_grating_coupler(c, ["o1", "o2"])
        component_list.append(c)

    c = gf.grid(
        component_list,
        spacing=30,
        shape=(2, 2),
        align_x="x",
    )
    return c


def test_ring_metal_heater_distance():
    radius = 10
    gaps = [0.35, 0.37]
    angle = 20
    component_list = []

    # version 1 - with heater
    for gap in gaps:
        c = gf.Component()
        ring = ring(
            wg=rib_cs450,
            pn=partial(pn_cs,
                width=0.45,
                layer_heater=LAYER.VIA,
                width_heater=CrossSectionSpec.ring_heater_width,
                layer_metal=LAYER.METAL,
                layer_via=LAYER.VIA,
                via_min_distance=CrossSectionSpec.min_via_distance,
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
        st = gf.path.straight(length=250).extrude(rib_cs450)
        ring = ring_pn_pad(ring, pads, routing)
        ring_ref = c.add_ref(ring)
        st_left_ref = c.add_ref(st)
        st_right_ref = c.add_ref(st)
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

        # version 2 - without heater but same structure
        c = gf.Component()
        ring = ring(
            wg=rib_cs450,
            pn=partial(pn_cs,
                width=0.45,
                layer_heater=LAYER.BLANK,
                width_heater=CrossSectionSpec.ring_heater_width,
                layer_metal=LAYER.METAL,
                layer_via=LAYER.VIA,
                via_min_distance=CrossSectionSpec.min_via_distance,
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
        st = gf.path.straight(length=250).extrude(rib_cs450)
        ring = ring_pn_pad(ring, pads, routing)
        ring_ref = c.add_ref(ring)
        st_left_ref = c.add_ref(st)
        st_right_ref = c.add_ref(st)
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

        # version 3 - normal case
        c = gf.Component()
        ring = ring(
            wg=rib_cs450,
            pn=partial(pn_cs,
                width=0.45,
                layer_metal=LAYER.METAL,
                layer_via=LAYER.VIA,
                via_min_distance=CrossSectionSpec.min_via_distance,
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
        st = gf.path.straight(length=250).extrude(rib_cs450)
        ring = ring_pn_pad(ring, pads, routing)
        ring_ref = c.add_ref(ring)
        st_left_ref = c.add_ref(st)
        st_right_ref = c.add_ref(st)
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

    c = gf.grid(
        component_list,
        spacing=30,
        shape=(len(gaps), 3),
        align_x="x",
    )

    return c