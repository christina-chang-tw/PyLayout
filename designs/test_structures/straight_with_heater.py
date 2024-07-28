import gdsfactory as gf
from gdsfactory.typings import CrossSectionSpec, Component, List

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
    length: int = 500,
    heater_length: int = 350,
    arm_gap: float = 100,
) -> Component:
    """
    Create a straight waveguide with a heater on top.

    Args:
        cs (CrossSectionSpec): Waveguide cross section.
        filament (CrossSectionSpec): Filament cross section
        length (int): Length of the waveguide.
        heater_length (int): Length of the heater.
    
    Returns:
        gf.Component: Component with a straight waveguide and a heater on top.
    """
    c = gf.Component()

    wg = gf.get_cross_section(wg)
    filament = gf.get_cross_section(filament)

    st = gf.path.straight(length=length).extrude(wg)
    short_st = gf.path.straight(length=(length-heater_length)/2).extrude(wg)
    lshort_ref, rshort_ref = c.add_ref(short_st), c.add_ref(short_st)
    bst_ref = c.add_ref(st)

   
    splitter = mmi_splitter(SOI220nm_1550nm_TE_RIB_2x1_MMI, cs=wg, arm_distance=arm_gap)
    lsplitter_ref, rsplitter_ref = c.add_ref(splitter), c.add_ref(splitter)

    mzi_heater = straight_with_heater(length=heater_length,
                                      wg=heater,
                                      filament=filament,
                                      gap_between_pads=50, 
                                      metal_cs=metal_trace)
    mzi_heater_ref = c.add_ref(mzi_heater)
    mzi_heater_ref.mirror_y()
    
    lshort_ref.connect("o1", lsplitter_ref.ports["o2"])
    mzi_heater_ref.connect("o1", lshort_ref.ports["o2"])
    rshort_ref.connect("o1", mzi_heater_ref.ports["o2"])
    bst_ref.connect("o1", lsplitter_ref.ports["o3"])
    rsplitter_ref.connect("o3", rshort_ref.ports["o2"])

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
                       length=heater_length + 100, heater_length=heater_length, arm_gap=130)
        component_lists.append(c)
    
    spacing = 25
    c = pack(component_list=component_lists, spacing=spacing)

    c.show()