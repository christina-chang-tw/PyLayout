import gdsfactory as gf
from gdsfactory.typings import Component, CrossSectionSpec

from . import circular_bend_180

@gf.cell
def mmi_splitter(
    mmi: Component,
    st_length: float = 50,
    cs: CrossSectionSpec = "rib",
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

    cs = gf.get_cross_section(cs)

    mmi_ref = c.add_ref(gf.get_component(mmi))
    st_ref = c.add_ref(gf.path.straight(length=st_length).extrude(cs))

    mmi_arm_gap = abs(mmi_ref.ports["o2"].dy - mmi_ref.ports["o3"].dy) - cs.width
    bend_radius = (arm_distance - mmi_arm_gap) / 4
    bend = circular_bend_180(radius=bend_radius, cs=cs)
    
    tbend_ref = c.add_ref(bend)
    bbend_ref = c.add_ref(bend).mirror_y()

    mmi_ref.connect("o1", st_ref.ports["o2"])
    tbend_ref.connect("o1", mmi_ref.ports["o3"])
    bbend_ref.connect("o1", mmi_ref.ports["o2"])

    for name, port in zip(("o1", "o2", "o3"), (st_ref.ports["o1"], tbend_ref.ports["o2"], bbend_ref.ports["o2"])):
        c.add_port(name=name, port=port)

    c.flatten()
    return c