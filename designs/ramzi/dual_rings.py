from functools import partial

import gdsfactory as gf
from gdsfactory.typings import CrossSectionSpec, Component

from cornerstone import (
    pn_450_with_metal_and_heater,
    pn_450_with_metal,
    rib_450,
    filament,
    heater,
    metal,
    SOI220nm_1550nm_TE_RIB_2x1_MMI,
    LAYER,
    cs_gc_silicon_1550nm
)
from pylayout.components import ring, straight_with_filament, attach_grating_coupler, mmi_splitter
from pylayout.methods import connect_all
from ..test_structures import ring_and_mzi_heater, single_ring_filament_gssg

@gf.cell
def ramzi_dual_rings(
    ring: Component,
    ring_and_heater: Component,
    splitter: Component,
    wg: CrossSectionSpec=None
) -> Component:
    """
    Dual ring test structure with a splitter.

    Args:
        ring [gf.Component]: Single ring with a heater.
        ring_and_heater [gf.Component]: Single ring and a straight with a filament.
        splitter [gf.Component]: MMI splitter.
        wg [gf.typings.CrossSectionSpec]: Waveguide cross section for if you have the two arms not being the same distance

    Returns:
        [gf.Component]: Dual ring test structure with a splitter.
    """
    c = gf.Component()

    ring = gf.get_component(ring)
    r_and_h = gf.get_component(ring_and_heater)
    splitter = gf.get_component(splitter)

    size_diff = abs(r_and_h.ports["o1"].dx - r_and_h.ports["o2"].dx) - abs(ring.ports["o1"].dx - ring.ports["o2"].dx)
    
    if size_diff > 0:
        temp = gf.Component()
        wg = gf.get_cross_section(wg)
        st = gf.path.straight(length=size_diff).extrude(wg)
        r_ref, st_ref = temp.add_ref(ring), temp.add_ref(st)
        st_ref.connect("o2", r_ref.ports["o1"])
        temp.add_port("o1", port=r_ref.ports["o2"])
        temp.add_port("o2", port=st_ref.ports["o2"])
        ring = temp

    ring_ref, r_and_h_ref = c.add_ref(ring), c.add_ref(r_and_h)
    lsplitter_ref, rsplitter_ref = c.add_ref(splitter), c.add_ref(splitter)

    connections = [
        (r_and_h_ref, "o1", lsplitter_ref, "o2"),
        (rsplitter_ref, "o3", r_and_h_ref, "o2"),
        (ring_ref, "o1", lsplitter_ref, "o3"),
    ]

    connect_all(connections)

    c.add_port(name="o1", port=lsplitter_ref.ports["o1"])
    c.add_port(name="o2", port=rsplitter_ref.ports["o1"])
    c = attach_grating_coupler(c, cs_gc_silicon_1550nm, ["o1", "o2"])

    c.flatten()
    return c

if __name__ == "__main__":
    wg = rib_450
    pn_heater = pn_450_with_metal_and_heater
    pn = pn_450_with_metal
    arm_distance = 110
    radius = 10
    angle = 20
    gap = 0.2
    heater_length = 400
    arm_length = 1000
    dist_to_wg = 0.79
    dist_between_vias = 2.75
    heater_percent = 0.78

    rheater = gf.compose(single_ring_filament_gssg, partial(
        ring,
        wg=wg,
        pn=pn_450_with_metal_and_heater,
        radius=radius,
        gap=gap,
        int_angle=angle,
        dist_pn_to_wg=dist_to_wg,
        dist_between_vias=dist_between_vias,
        heater_percent=heater_percent,
        max_length=400
    ))

    r = partial(
        ring,
        wg=wg,
        pn=pn,
        radius=radius,
        gap=gap,
        int_angle=angle,
        dist_pn_to_wg=dist_to_wg,
        dist_between_vias=dist_between_vias,
    )

    heater = partial(
        straight_with_filament,
        wg=wg,
        filament=filament,
        filament_length=heater_length,
    )

    r_and_h = partial(
        ring_and_mzi_heater,
        r=r,
        mzi_heater=heater,
        wg=wg,
        metal=metal(width=20),
        filament_layer=LAYER.FILAMENT,
        max_length=arm_length
    )

    splitter = partial(
        mmi_splitter,
        arm_distance=arm_distance,
        mmi=SOI220nm_1550nm_TE_RIB_2x1_MMI,
        wg=wg
    )

    dual_ring = partial(
        ramzi_dual_rings,
        ring=rheater,
        ring_and_heater=r_and_h,
        splitter=splitter,
        wg=wg
    )

    c = dual_ring()  

    c.show()