import gdsfactory as gf
from gdsfactory.typings import CrossSectionSpec, ComponentSpec, List, Component

from cornerstone import (
    filament,
    rib_450,
    SOI220nm_1550nm_TE_RIB_2x1_MMI,
    cs_gc_silicon_1550nm,
    metal_trace,
    heater
)
from cornerstone import CornerstoneSpec as Spec
from pylayout.components import straight_with_heater, attach_grating_coupler, mmi_splitter

@gf.cell
def mzi_heater(
    wg: CrossSectionSpec,
    filament: CrossSectionSpec,
    heater_length: int = 350,
    arm_length: int = 500,
    arm_gap: float = 100,
    mmi: ComponentSpec = SOI220nm_1550nm_TE_RIB_2x1_MMI,
) -> Component:
    """
    Create a straight waveguide with a heater on top.

    Args:
        cs (CrossSectionSpec): Waveguide cross section.
        filament (CrossSectionSpec): Filament cross section
        heater_length (int): Length of the heater.
        arm_length (int): MZI arm length
        arm_gap (float): Gap between the MZI arms.
        mmi: MMI component.
    
    Returns:
        Component: Component with a straight waveguide and a heater on top.
    """
    c = gf.Component()

    wg = gf.get_cross_section(wg)
    filament = gf.get_cross_section(filament)
    mmi = gf.get_component(mmi)

    bst_ref = c.add_ref(gf.path.straight(length=arm_length).extrude(wg))

    splitter = mmi_splitter(mmi, cs=wg, arm_distance=arm_gap)
    lsplitter_ref, rsplitter_ref = c.add_ref(splitter), c.add_ref(splitter)

    mzi_heater = straight_with_heater(
                    length=arm_length,
                    heater_length=heater_length,
                    wg=wg,
                    filament=filament,
                    gap_between_pads=50, 
                    metal_cs=metal_trace
                )
    mzi_heater_ref = c.add_ref(mzi_heater)
    mzi_heater_ref.mirror_y()
    
    mzi_heater_ref.connect("o1", lsplitter_ref.ports["o2"])
    rsplitter_ref.connect("o3", mzi_heater_ref.ports["o2"])
    bst_ref.connect("o1", lsplitter_ref.ports["o3"])

    c.add_port("o1", port=lsplitter_ref.ports["o1"])
    c.add_port("o2", port=rsplitter_ref.ports["o1"])

    c = attach_grating_coupler(c, cs_gc_silicon_1550nm)

    c.flatten()
    return c

def pack(component_list: List[Component], spacing: float = 25) -> Component:
    """
    Pack a list of components with a given spacing.

    Args:
        component_list (List[Component]): List of components to pack.
        spacing (float): Spacing between components.

    Returns:
        gf.Component: Component with the packed components.
    """
    c = gf.Component()
    temp_min = 0
    for component in component_list:
        c_ref = c.add_ref(component)
        c_ref.dxmin = temp_min + spacing
        temp_min = c_ref.dxmax
    return c


if __name__ == "__main__":
    heater_lengths = [250, 500, 750]
    component_lists = []
    for heater_length in heater_lengths:
        c = mzi_heater(wg=rib_450, filament=filament(width=Spec.mzi_heater_width),
                       arm_length=heater_length + 100, heater_length=heater_length, arm_gap=130)
        component_lists.append(c)
    
    spacing = 25
    c = pack(component_list=component_lists, spacing=spacing)

    c.show()