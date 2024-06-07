import gdsfactory as gf

from pylayout.components import Components
from pylayout.layers.cornerstone import SOI_220nm
from pylayout.methods import Methods

@gf.cell
def RAMZI_2x2_MZI(
    cs: gf.CrossSection,
    coupler_gap: float,
    coupler_length: float,
    ring_gap: float,
    straight_length: float,
    arm_distance: float,
):
    base = gf.Component("RAMZI_2x2_MZI")
    ### MZI section #######################################
    mzi_section = gf.Component("MZI")

    # middle sections (straights + bend waveguides)
    straight_lt = gf.components.rectangle(
        size=(20, 0.45),
        layer=SOI_220nm.ETCH1,
        centered=True,
        port_type="optical",
        port_orientations=(180, 0)
    )
    straight_t = gf.components.rectangle(
        size=(straight_length, 0.45),
        layer=SOI_220nm.ETCH1,
        centered=True,
        port_type="optical",
        port_orientations=(180, 0)
    )
    straight_lt_ref = mzi_section.add_ref(straight_lt)
    straight_lb = straight_lt.copy("straight_lb")
    straight_lb_ref = mzi_section.add_ref(straight_lb)
    straight_rt = straight_lt.copy("straight_r")
    straight_rt_ref = mzi_section.add_ref(straight_rt)
    straight_rb = straight_lt.copy("straight_rb")
    straight_rb_ref = mzi_section.add_ref(straight_rb)

    straight_t_ref = mzi_section.add_ref(straight_t)
    straight_b = straight_t.copy("straight_b")
    straight_b_ref = mzi_section.add_ref(straight_b)

    input_coupler = gf.components.coupler(
        gap=coupler_gap,
        length=coupler_length,
        dy=arm_distance+cs.width,
        dx=5,
        cross_section=cs
    )
    input_coupler_ref = mzi_section.add_ref(input_coupler)
    output_coupler = input_coupler.copy("output_coupler")
    output_coupler_ref = mzi_section.add_ref(output_coupler)
    straight_lb_ref.x = straight_lt_ref.x
    straight_rb_ref.x = straight_rt_ref.x
    straight_t_ref.x = straight_b_ref.x
    straight_b_ref.ymax = straight_t_ref.ymin - arm_distance
    input_coupler_ref.connect("o3", straight_t_ref.ports["o1"])
    input_coupler_ref.connect("o4", straight_b_ref.ports["o1"])
    output_coupler_ref.connect("o1", straight_b_ref.ports["o2"])
    output_coupler_ref.connect("o2", straight_t_ref.ports["o2"])
    straight_lb_ref.connect("o1", input_coupler_ref.ports["o1"])
    straight_lt_ref.connect("o1", input_coupler_ref.ports["o2"])
    straight_rb_ref.connect("o1", output_coupler_ref.ports["o4"])
    straight_rt_ref.connect("o1", output_coupler_ref.ports["o3"])

    # ring section
    ring = gf.components.ring(
        radius=cs.radius,
        width=cs.width,
        angle_resolution=2.5,
        layer=SOI_220nm.ETCH1
    )
    ring_ref = base.add_ref(ring)
    ring_ref.ymin = straight_t_ref.ymax + ring_gap

    base.add_ref(mzi_section)
    return base
    

def RAMZI_1x1_MZI(
    cs: gf.CrossSection,
    coupler_gap: float,
    ring_gap: float,
    straight_length: float,
    arm_distance: float
):
    base = gf.Component("RAMZI_1x1_MZI")
  
    ### MZI section #######################################
    mzi_section = gf.Component("MZI")

    # middle sections (straights + bend waveguides)
    straight_l = gf.components.rectangle(
        size=(20, 0.45),
        layer=SOI_220nm.ETCH1,
        centered=True,
        port_type="optical",
        port_orientations=(180, 0)
    )
    straight_t = gf.components.rectangle(
        size=(straight_length, 0.45),
        layer=SOI_220nm.ETCH1,
        centered=True,
        port_type="optical",
        port_orientations=(180, 0)
    )
    straight_l_ref = mzi_section.add_ref(straight_l)
    straight_r = straight_l.copy("straight_r")
    straight_r_ref = mzi_section.add_ref(straight_r)
    straight_b = straight_t.copy("straight_b")
    straight_b_ref = mzi_section.add_ref(straight_b)
    straight_t_ref = mzi_section.add_ref(straight_t)

    input_ts = gf.components.bend_s(size=(50, (arm_distance-coupler_gap)/2), npoints=111, cross_section=cs)
    input_ts_ref = mzi_section.add_ref(input_ts)
    _, input_bs_ref = Methods.symmetry(mzi_section, name="mmi_input_bs", com1=input_ts, y0=input_ts.ymin)
    _, output_ts_ref = Methods.symmetry(mzi_section, name="mmi_output_ts", com1=input_ts, x0=input_ts.xmax)
    output_bs = input_ts.copy("output_bs")
    output_bs_ref = mzi_section.add_ref(output_bs)
    straight_b_ref.x = straight_t_ref.x
    straight_b_ref.ymax = straight_t_ref.ymin - arm_distance
    input_ts_ref.connect("o2", straight_t_ref.ports["o1"])
    input_bs_ref.connect("o2", straight_b_ref.ports["o1"])
    output_ts_ref.connect("o1", straight_t_ref.ports["o2"])
    output_bs_ref.connect("o1", straight_b_ref.ports["o2"])

    # input splitter
    width_taper = 1.8
    input_splitter = gf.components.mmi1x2(
        width_taper=width_taper,
        length_taper=15,
        length_mmi=32,
        width_mmi=width_taper*2+coupler_gap,
        gap_mmi=coupler_gap-width_taper+cs.width,
        cross_section=cs
    )
    input_splitter_ref = mzi_section.add_ref(input_splitter)
    
    # output combiner
    _, output_combiner_ref = Methods.symmetry(mzi_section, name="output_combiner", com1=input_splitter, xport="o1")
    
    
    input_splitter_ref.connect("o2", input_ts_ref.ports["o1"])
    input_splitter_ref.connect("o3", input_bs_ref.ports["o1"])
    straight_l_ref.connect("o1", input_splitter_ref.ports["o1"])
    
    output_combiner_ref.connect("o2", output_ts_ref.ports["o2"])
    output_combiner_ref.connect("o3", output_bs_ref.ports["o2"])
    straight_r_ref.connect("o1", output_combiner_ref.ports["o1"])
    
    # ring section
    ring = gf.components.ring(
        radius=cs.radius,
        width=cs.width,
        angle_resolution=2.5,
        layer=SOI_220nm.ETCH1
    )
    ring_ref = base.add_ref(ring)
    ring_ref.ymin = straight_t_ref.ymax + ring_gap
    ring_ref.x = straight_t_ref.x
    
    base.add_ref(mzi_section)
    return base

def main():
    base = gf.Component("Base")
    outline = Components.outline(100, 100)
    cs = Components.cross_section(width=0.45, layer=SOI_220nm.ETCH1, radius=10)

    ramzi = RAMZI_1x1_MZI(
        cs=cs,
        coupler_gap=2.5,
        ring_gap=0.5,
        straight_length=20,
        arm_distance=10
    )

    base.add_ref(ramzi)
    ref = gf.ComponentReference(base)
    ref.center = (0, 0)
    base.show()

if __name__ == "__main__":
    main()