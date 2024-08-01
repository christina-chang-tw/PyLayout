from functools import partial

import gdsfactory as gf
from gdsfactory.typings import CrossSectionSpec, Component, List

from pylayout.components import ring, attach_grating_coupler, add_norm_wg
from pylayout.routing import route_pads_to_ring
from pylayout.cross_section import MSpec
from cornerstone import pn, pn_450_with_metal, pn_450_with_metal_and_heater, rib_450, LAYER, metal_pad, cs_gc_silicon_1550nm
from cornerstone import Spec
from ..test_structures import single_ring_pn

def single_ring_filament_gsgsg(
    r: Component,
    pads: Component = gf.grid([metal_pad, metal_pad, metal_pad, metal_pad, metal_pad], spacing=MSpec.pad_spacing),
    dist_to_pad: float = 50
) -> Component:
    """
    A single ring with heater test structure.
    
    Args:
        radius (float): Radius of the ring.
        angle (float): Angle of the outer arc.
        gap (float): Gap between the inner ring and the outer arc.
        dist_pn_to_wg (float): Distance between the PN junction and the waveguide.
        cs (gf.typings.CrossSectionSpec): Cross section of the ring.
        heater_width (float): Width of the heater.
        max_length (float): Maximum length of the test structure.
    """
    c = gf.Component()
    r = gf.get_component(r)
    pads = gf.get_component(pads)

    routing = {
        "1_0_e4": "METAL_TOP_p1",
        "3_0_e4": "HEATER_METAL_p1",
        "4_0_e4": "METAL_BOT_p1",     
    }

    r = route_pads_to_ring(r, pads, routing)
    ring_ref = c.add_ref(r)

    xsize = abs(ring_ref.ports["ring_HEATER_METAL_p2"].dx + ring_ref.ports["ring_HEATER_METAL_p2"].dwidth/2 - ring_ref.ports["ring_METAL_BOT_p2"].dx + ring_ref.ports["ring_METAL_BOT_p2"].dwidth/2)
    ysize = 0.04 * dist_to_pad
    rect = gf.components.rectangle(size=(xsize, ysize), layer=LAYER.METAL)
    rect_ref = c.add_ref(rect)
    rect_ref.dymax = ring_ref.ports["ring_HEATER_METAL_p2"].dy
    rect_ref.dxmax = ring_ref.ports["ring_HEATER_METAL_p2"].dx + ring_ref.ports["ring_HEATER_METAL_p2"].dwidth/2
    gf.routing.route_quad(
        c, rect_ref.ports["e2"], ring_ref.ports["pad_0_0_e4"],
        layer=LAYER.METAL
    )

    c.add_port(name="o1", port=ring_ref.ports["o1"])
    c.add_port(name="o2", port=ring_ref.ports["o2"])
    
    c.flatten()
    return c

@gf.cell
def single_ring_filament_gssg(
    r: Component,
    pads: Component = gf.grid([metal_pad, metal_pad, metal_pad, metal_pad], spacing=MSpec.pad_spacing),
    dist_to_pad: float = 50
) -> Component:
    """
    A single ring with heater test structure.
    
    Args:
        radius (float): Radius of the ring.
        angle (float): Angle of the outer arc.
        gap (float): Gap between the inner ring and the outer arc.
        dist_to_pn_wg (float): Distance between the PN junction and the waveguide.
        cs (gf.typings.CrossSectionSpec): Cross section of the ring.
        heater_width (float): Width of the heater.
        max_length (float): Maximum length of the test structure.
    """
    c = gf.Component()
    r = gf.get_component(r)
    pads = gf.get_component(pads)

    routing = {
        "1_0_e4": "METAL_TOP_p1",
        "2_0_e4": "HEATER_METAL_p1",
        "3_0_e4": "METAL_BOT_p1",     
    }
    r = route_pads_to_ring(r, pads, routing)
    ring_ref = c.add_ref(r)

    xsize = abs(ring_ref.ports["ring_HEATER_METAL_p2"].dx + ring_ref.ports["ring_HEATER_METAL_p2"].dwidth/2 - ring_ref.ports["ring_METAL_BOT_p2"].dx + ring_ref.ports["ring_METAL_BOT_p2"].dwidth/2)
    ysize = 0.04 * dist_to_pad
    rect = gf.components.rectangle(size=(xsize, ysize), layer=LAYER.METAL)
    rect_ref = c.add_ref(rect)
    rect_ref.dymax = ring_ref.ports["ring_HEATER_METAL_p2"].dy
    rect_ref.dxmax = ring_ref.ports["ring_HEATER_METAL_p2"].dx + ring_ref.ports["ring_HEATER_METAL_p2"].dwidth/2
    gf.routing.route_quad(
        c, rect_ref.ports["e2"], ring_ref.ports["pad_0_0_e4"],
        layer=LAYER.METAL
    )

    c.add_port(name="o1", port=ring_ref.ports["o1"])
    c.add_port(name="o2", port=ring_ref.ports["o2"])

    c.flatten()
    return c


@gf.cell
def single_ring_filament_gs(
    r: Component,
    pads: Component = gf.grid([metal_pad, metal_pad], spacing=MSpec.pad_spacing),
) -> Component:
    c = gf.Component()
    r = gf.get_component(r)
    pads = gf.get_component(pads)

    routing = {
        "0_0_e4": "HEATER_METAL_p2",
        "1_0_e4": "HEATER_METAL_p1",
    }
    r = route_pads_to_ring(r, pads, routing)
    ring_ref = c.add_ref(r)

    c.add_port(name="o1", port=ring_ref.ports["o1"])
    c.add_port(name="o2", port=ring_ref.ports["o2"])

    c.flatten()
    return c


def ring_filament_to_pn_distance(
    radius: float = 10,
    gap: float = 0.35,
    angle: float = 20,
    dist_pn_to_wg: float = 0.79,
    dist_y: float=None,
    wg: CrossSectionSpec = rib_450,
    heater_percent: float=0.78,
    max_length: float = 600,
) -> List[Component]:
    wg = gf.get_cross_section(wg)

    component_list = []

    r_with_heater = partial(
        ring,
        wg=wg,
        pn=pn_450_with_metal_and_heater,
        radius=radius,
        gap=gap,
        int_angle=angle,
        dist_pn_to_wg=dist_pn_to_wg,
        max_length=max_length,
        heater_percent=heater_percent,
        dist_y=dist_y
    )

    r = partial(
        ring,
        wg=wg,
        pn=pn_450_with_metal,
        radius=radius,
        gap=gap,
        int_angle=angle,
        dist_y=dist_y,
        dist_pn_to_wg=dist_pn_to_wg,
        max_length=max_length
    )

    # version 1 - with heater
    c = single_ring_filament_gsgsg(
        r=r_with_heater
    )
    c = attach_grating_coupler(c, cs_gc_silicon_1550nm, ["o1", "o2"])
    c = add_norm_wg(c, cs_gc_silicon_1550nm, wg, rpos=-40, sides="N")
    component_list.append(c)
    
    # version 2 - without heater but same structure
    c = gf.Component()
    r = ring(
        wg=wg,
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
        dist_pn_to_wg=dist_pn_to_wg,
        dist_y=dist_y,
        max_length=max_length
    )
    pads = [metal_pad, metal_pad, metal_pad]
    pads = gf.grid(pads, spacing=(25, 25))
    routing = {
        "0_0_e4": "METAL_BOT_p2",
        "1_0_e4": "METAL_TOP_p1",
        "2_0_e4": "METAL_BOT_p1",
    }
    c = route_pads_to_ring(r, pads, routing)
    c = attach_grating_coupler(c, cs_gc_silicon_1550nm, ["o1", "o2"])
    c = add_norm_wg(c, cs_gc_silicon_1550nm, wg, rpos=-40, sides="N")
    component_list.append(c)

    # version 3 - normal case
    c = single_ring_pn(r=r)
    c = attach_grating_coupler(c, cs_gc_silicon_1550nm, ["o1", "o2"])
    c = add_norm_wg(c, cs_gc_silicon_1550nm, wg, rpos=-40, sides="N")
    component_list.append(c)

    return component_list

if __name__ == "__main__":

    radius = 7
    gaps_7um = [0.27, 0.29, 0.31]
    gaps_10um = [0.37, 0.39, 0.41]

    # radius = 10, dist_pn_to_wg = 0.79, heater_percent = 0.78
    # radius = 7, dist_y = 5.6, heater_percent = 0.7

    component_list = []
    com_list = ring_filament_to_pn_distance(
        heater_percent=0.78,
        radius = radius,
        gap=0.2,
        angle=20,
        dist_pn_to_wg = 0.79,
        max_length=1000,
    )

    c = gf.grid(
        com_list,
        shape=(1, 3),
        spacing=(25, 25)
    )
    c.remove_layers(layers=[(0,0)])

    c.show()