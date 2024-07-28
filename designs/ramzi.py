def ramzi_design_1ring_draft1(
    radius: float=10,
    int_len: float=5.5,
    gap: float=0.2,
    arm_length: float=500,
    arm_distance: float=130,
    heater_length: float=350
):
    c = gf.Component()

    mmi_arm_gap = 2.69

    ring = ring(
        wg=rib_cs450,
        pn=pn_cs450_without_heater,
        radius=radius,
        gap=gap,
        int_len=int_len,
        dist_pn_to_wg=1.5,
        dist_between_vias=2.75,
    )
    pads = [metal_pad, metal_pad, metal_pad]
    pads = gf.grid(pads, spacing=(25, 25))
    pads_routing = {
        "1_0_e4": "METAL_TOP_p1",
        "2_0_e4": "METAL_BOT_p1",
        "0_0_e4": "METAL_BOT_p2",
    }
    ring_ref = c.add_ref(ring_pn_pad(ring, pads, pads_routing))
    ring_ref.mirror_y()

    st_mzi = gf.path.straight(length=(arm_length-heater_length)/2).extrude(rib_cs450)
    st_ring = gf.path.straight(length=(arm_length-2*radius)/2).extrude(rib_cs450)
    mzi_heater = straight_with_heater(length=heater_length, filament=filament(width=CrossSectionSpec.mzi_heater_width), gap_between_pads=50, metal_cs=heater_pad_cs, metal_layer=LAYER.METAL)

    ltst_ref, rtst_ref = [c.add_ref(st_ring) for _ in range(2)]
    lbst_ref, rbst_ref = [c.add_ref(st_mzi) for _ in range(2)]
    mzi_heater_ref = c.add_ref(mzi_heater)

    bend_radius = (arm_distance - mmi_arm_gap)/4
    bend = circular_bend_180(radius=bend_radius, cs=rib_cs450)
    ltbend_ref, lbbend_ref, rtbend_ref, rbbend_ref = [c.add_ref(bend) for _ in range(4)]
    lbbend_ref.mirror_y()
    rtbend_ref.mirror_x()
    rbbend_ref.mirror_x().mirror_y()

    mmi = SOI220nm_1550nm_TE_RIB_2x1_MMI()
    rmmi_ref = c.add_ref(mmi)
    lmmi_ref = c.add_ref(mmi)

    inout_st = gf.path.straight(length=100)
    in_st_ref = c.add_ref(inout_st.extrude(rib_cs450))
    out_st_ref = c.add_ref(inout_st.extrude(rib_cs450))

    lmmi_ref.connect("o1", in_st_ref.ports["o2"])
    lbbend_ref.connect("o1", lmmi_ref.ports["o2"])
    lbst_ref.connect("o1", lbbend_ref.ports["o2"])
    mzi_heater_ref.connect("o1", lbst_ref.ports["o2"])
    rbst_ref.connect("o1", mzi_heater_ref.ports["o2"])
    rbbend_ref.connect("o1", rbst_ref.ports["o2"])

    ltbend_ref.connect("o2", lmmi_ref.ports["o3"])
    ltst_ref.connect("o1", ltbend_ref.ports["o1"])
    ring_ref.connect("o1", ltst_ref.ports["o2"])
    rtst_ref.connect("o1", ring_ref.ports["o2"])
    rtbend_ref.connect("o1", rtst_ref.ports["o2"])
    
    rmmi_ref.connect("o2", rtbend_ref.ports["o1"])
    rmmi_ref.connect("o3", rbbend_ref.ports["o2"])
    out_st_ref.connect("o1", rmmi_ref.ports["o1"])

    c.add_port(name="o1", port=in_st_ref.ports["o1"])
    c.add_port(name="o2", port=out_st_ref.ports["o2"])

    c = attach_grating_coupler(c, ["o1", "o2"])
    return c



if __name__ == "__main__":
    c = gf.Component()
    ref1 = c.add_ref(ramzi_design_2rings_draft1())
    ref2 = c.add_ref(ramzi_design_1ring_draft1())
    ref2.dymax = ref1.dymin - 100

    c.show()