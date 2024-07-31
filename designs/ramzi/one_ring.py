import numpy as np
from functools import partial

import gdsfactory as gf
from gdsfactory.typings import Component

from cornerstone import (
    rib_450,
    pn_450_with_metal,
    filament,
    heater,
    SOI220nm_1550nm_TE_RIB_2x1_MMI,
    cs_gc_silicon_1550nm
)
from cornerstone import CornerstoneSpec as Spec
from pylayout.components import straight_with_heater, attach_grating_coupler, mmi_splitter, ring, add_norm_wg, coupler_2x2
from pylayout.methods import connect_all

from ..test_structures import straight, single_ring_pn


@gf.cell
def ramzi_one_ring(
    ring: Component,
    mzi_heater: Component,
    mmi: Component,

):
    c = gf.Component()

    mzi_heater = gf.get_component(mzi_heater)
    ring = gf.get_component(ring)
    mmi = gf.get_component(mmi)

    ring_ref = c.add_ref(ring)
    ring_ref.mirror_y()
    mzi_heater_ref = c.add_ref(mzi_heater)

    splitter = mmi
    lsplitter_ref, rsplitter_ref = [c.add_ref(splitter) for _ in range(2)]

    connections = [
        (ring_ref, "o2", lsplitter_ref, "o2"),
        (mzi_heater_ref, "o1", lsplitter_ref, "o3"),
        (rsplitter_ref, "o3", ring_ref, "o1"),
    ]

    connect_all(connections)

    c.add_port(name="o1", port=lsplitter_ref.ports["o1"])
    c.add_port(name="o2", port=rsplitter_ref.ports["o1"])

    c = attach_grating_coupler(c, cs_gc_silicon_1550nm(), ["o1", "o2"])
    
    c = add_norm_wg(c=c, gc=cs_gc_silicon_1550nm, cs=wg, rpos=-40, sides="N")
    return c

@gf.cell
def ramzi_one_ring_2x1(
    ring: Component,
    mzi_heater: Component,
    mmi: Component,
    coupler: Component,
):
    c = gf.Component()

    ring = gf.get_component(ring)
    mzi_heater = gf.get_component(mzi_heater)
    mmi = gf.get_component(mmi)
    coupler = gf.get_component(coupler)

    ring_ref = c.add_ref(ring)
    mzi_heater_ref = c.add_ref(mzi_heater)

    lsplitter_ref = c.add_ref(coupler)
    rsplitter_ref = c.add_ref(mmi)
    rsplitter_ref.mirror_x()

    connections = [
        (ring_ref, "o1", lsplitter_ref, "o3"),
        (rsplitter_ref, "o2", ring_ref, "o2"),
        (mzi_heater_ref, "o2", lsplitter_ref, "o4"),
    ]

    connect_all(connections)

    c.add_port(name="o1", port=lsplitter_ref.ports["o1"])
    c.add_port(name="o2", port=lsplitter_ref.ports["o2"])
    c.add_port(name="o3", port=rsplitter_ref.ports["o1"])

    c = attach_grating_coupler(c, cs_gc_silicon_1550nm(), ["o1", "o2", "o3"])

    c = add_norm_wg(c=c, gc=cs_gc_silicon_1550nm, cs=wg, rpos=-40, sides="N")

    return c

if __name__ == "__main__":
    wg = rib_450
    pn = pn_450_with_metal
    heater = filament
    heater_length = 400
    arm_distance = 120
    radius = 10
    angle = 20
    arm_length = 500
    dist_pn_to_wg = 0.79
    dist_y = None
    coupler_gap = 0.25

    single_r = partial(
        ring,
        radius=radius,
        int_angle=angle,
        gap=0.2,
        dist_pn_to_wg=dist_pn_to_wg,
        wg=wg,
        pn=pn,
        max_length=arm_length
    )
    
    r = partial(single_ring_pn,
        rc=single_r,
        pad_spacing=25
    )

    mmi = partial(mmi_splitter,
        arm_distance=arm_distance,
        mmi=SOI220nm_1550nm_TE_RIB_2x1_MMI,
        cs=wg
    )

    coupler = partial(coupler_2x2,
        gap=coupler_gap,
        length=50,
        arm_distance=arm_distance,
        cs=wg,
        st_length=50
    )

    mzi_heater = partial(straight_with_heater,
        wg=wg,
        heater=heater,
        heater_length=heater_length,
        length=arm_length,
    )

    c = ramzi_one_ring_2x1(
        ring=r,
        mzi_heater=mzi_heater,
        mmi=mmi,
        coupler=coupler
    )


    c.show()