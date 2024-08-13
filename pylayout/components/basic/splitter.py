import numpy as np

import gdsfactory as gf
from gdsfactory.typings import Component, CrossSectionSpec

from . import circular_bend_180

@gf.cell
def mmi_splitter(
    mmi: Component,
    st_length: float = 50,
    wg: CrossSectionSpec = "rib",
    arm_distance: float = 130
) -> Component:
    """
    An MMI splitter with a straight waveguide connected to the input of MMI and two bend arms connected to the output of the MMI. The bend arms have a maximum distance specified by arm distance.

    Args:
        mmi [gf.Component]: MMI component
        st_length [float]: Straight waveguide length
        cs [CrossSectionSpec]: Cross section of the waveguides
        arm_distance [float]: Maximum distance between the bend arms
    
    Returns:
        gf.Component: MMI splitter component
    """
    c = gf.Component()

    wg = gf.get_cross_section(wg)

    mmi_ref = c.add_ref(gf.get_component(mmi))
    st_ref = c.add_ref(gf.path.straight(length=st_length).extrude(wg))

    mmi_arm_gap = abs(mmi_ref.ports["o2"].dy - mmi_ref.ports["o3"].dy) - wg.width
    bend_radius = (arm_distance - mmi_arm_gap) / 4
    bend = circular_bend_180(radius=bend_radius, cs=wg)
    
    tbend_ref = c.add_ref(bend)
    bbend_ref = c.add_ref(bend).mirror_y()

    mmi_ref.connect("o1", st_ref.ports["o2"])
    tbend_ref.connect("o1", mmi_ref.ports["o3"])
    bbend_ref.connect("o1", mmi_ref.ports["o2"])

    for name, port in zip(("o1", "o2", "o3"), (st_ref.ports["o1"], tbend_ref.ports["o2"], bbend_ref.ports["o2"])):
        c.add_port(name=name, port=port)

    c.flatten()
    return c

@gf.cell
def coupler_2x2(
    gap: float,
    length: float,
    arm_distance: float,
    cs: CrossSectionSpec,
    st_length: float=50,
):
    c = gf.Component()
    cs = gf.get_cross_section(cs)
    splitter = gf.components.coupler(gap=gap, length=float(length), dx=1.5*(arm_distance-gap)/2, cross_section=cs, dy=arm_distance+cs.width)
    splitter_ref = c.add_ref(splitter)
    st = gf.path.straight(length=st_length).extrude(cs)
    ltst_ref, lbst_ref = [c.add_ref(st) for _ in range(2)]

    ltst_ref.connect("o2", splitter_ref.ports["o1"])
    lbst_ref.connect("o2", splitter_ref.ports["o2"])

    c.add_port(name="o1", port=ltst_ref.ports["o1"])
    c.add_port(name="o2", port=lbst_ref.ports["o1"])
    c.add_port(name="o3", port=splitter_ref.ports["o3"])
    c.add_port(name="o4", port=splitter_ref.ports["o4"])

    c.flatten()
    return c


def main():
    from cornerstone.cross_section import rib_450
    from cornerstone import cs_gc_silicon_1550nm
    from . import attach_grating_coupler
    from ..advanced import add_norm_wg

    lengths = np.arange(8, 14, 1)
    gaps = [0.2, 0.25]
    np.random.default_rng().shuffle(lengths)

    gap_lists = []
    for gap in gaps:
        lists = []
        for length in lengths:
            c = gf.Component()
            st = gf.path.straight(length=50).extrude(rib_450)
            coupler = coupler_2x2(gap=gap, length=length, arm_distance=120, cs=rib_450)
            st_ref1 = c.add_ref(st)
            st_ref2 = c.add_ref(st)
            coupler_ref = c.add_ref(coupler)

            st_ref1.connect("o1", coupler_ref.ports["o3"])
            st_ref2.connect("o1", coupler_ref.ports["o4"])
            c.add_port(name="o1", port=coupler_ref.ports["o1"])
            c.add_port(name="o2", port=coupler_ref.ports["o2"])
            c.add_port(name="o3", port=st_ref1["o2"])
            c.add_port(name="o4", port=st_ref2["o2"])
            c = attach_grating_coupler(c, cs_gc_silicon_1550nm, ["o1", "o2", "o3", "o4"])
            c.flatten()
            lists.append(c)

        c = gf.grid(
            lists,
            shape=(len(lists), 1),
            spacing=30,
        )

        c = add_norm_wg(c, cs_gc_silicon_1550nm, rib_450, sides="S", rpos=40)
        gap_lists.append(c)

    print(gap_lists)
    c = gf.grid(
        gap_lists,
        shape=(1, len(gap_lists)),
        spacing=30,
    )

    c.show()

if __name__ == "__main__":
    main()

    
