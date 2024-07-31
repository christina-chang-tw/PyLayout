import numpy as np

import gdsfactory as gf
from gdsfactory.typings import CrossSectionSpec, Component, ComponentReference, LayerSpec, Dict, Port, List

from pylayout.methods import make_even_number
from ..basic.pn_section import ring_pn_section
from ..basic.coupler import ring_coupler_path

def _handle_pn_section(
    c: Component,
    radius: float,
    wg: CrossSectionSpec,
    pn: CrossSectionSpec,
    outer_rrect_ref: ComponentReference,
    dist_pn_to_wg: float,
    dist_y: float,
    dist_between_vias: float,
    dist_to_pad: float,
    heater_percent: float,
    metal_layer: LayerSpec = None,
):
    """
    Handle PN section

    Args:
        c (Component): Component
        radius (float): Radius
        wg (CrossSectionSpec): Waveguide cross section
        pn (CrossSectionSpec): PN cross section
        outer_rrect_ref (ComponentReference): Reference to the outer rectangle
        dist_pn_to_wg (float): Distance from PN to waveguide
        dist_between_vias (float): Distance between vias
        dist_to_pad (float): Distance to pad
        heater_percent (float): Heater percent
        metal_layer (LayerSpec): Metal layer
    
    Returns:
        None
    """
    cladding_width = (wg.sections[-1].width - wg.width) / 2
    y = np.round(outer_rrect_ref.dymin + cladding_width, 3) - dist_pn_to_wg if dist_y is None else dist_y
    pn_section = ring_pn_section(radius=radius, pn=pn, y=y, heater_percent=heater_percent)
    c.add_ref(pn_section)

    circ_cs = next((x for x in pn.sections if x.name == "METAL_TOP"), None)
    circ_r = radius - circ_cs.offset + circ_cs.width / 2
    ydiff = y - circ_r
    circ = gf.components.circle(radius=circ_r, layer=metal_layer)
    circ_ref = c.add_ref(circ)

    ports = {x.name: x for x in pn_section.ports if "metal".upper() in x.name.upper() or "heater".upper() in x.name.upper()}
    pn_layer_map = {x.name.upper(): x.layer for x in pn.sections}

    height_electrodes = 0.01*dist_to_pad

    for name, port in ports.items():
        if "heater".upper() in name.upper() and "heater_metal".upper() in pn_layer_map.keys():
            x = _handle_heater_ports(c, pn_layer_map, name, port,
                                     ports, dist_between_vias, dist_to_pad, ports["METAL_BOT_p1"].dy + 1.1)

        else:
            rect = gf.components.rectangle(size=(port.dwidth, height_electrodes), layer=port.layer, port_type="electrical")
            rect_ref = c.add_ref(rect)
            rect_ref.connect("e4", port)
            x = min(np.absolute(rect_ref.dxmin), np.absolute(rect_ref.dxmax))
            c.add_port(name=name, port=rect_ref.ports["e2"])


    rectx = max(3, 2*(x - dist_between_vias)) # because heater section will be last added, so x will be the x of the heater section if there is a heater
    percent = 0.06 if any("heater".upper() in port for port in ports) else 0.03
    recty = make_even_number(circ_r + ydiff + percent * dist_to_pad)
    circ_rec_ref = c.add_ref(gf.components.rectangle(size=(rectx, recty), layer=metal_layer))
    circ_rec_ref.dx = circ_ref.dx
    circ_rec_ref.dymin = circ_ref.dy
    c.add_port("METAL_TOP_p1", circ_rec_ref.ports["e2"])


def _handle_heater_ports(
    c: Component,
    pn_layer_map: Dict,
    name: str,
    port: Port,
    ports: List[Port],
    dist_between_vias: float,
    dist_to_pad: float,
    y: float
) -> float:
    """
    Handle heater ports

    Args:
        c (Component): Component
        pn_layer_map (Dict): Layer map
        name (str): Name of the port
        port (Port): Port
        ports (List[Port]): List of ports
        dist_between_vias (float): Distance between vias
        dist_to_pad (float): Distance to pad
    
    Returns:
        float: Distance
    """
    height_heater = 0.04 * dist_to_pad

    heater_ref = c.add_ref(gf.components.rectangle(size=(port.dwidth, height_heater), layer=port.layer, port_type="electrical"))
    metal_layer = pn_layer_map["heater_metal".upper()]
    heater_metal_ref = c.add_ref(gf.components.rectangle(size=(port.dwidth, height_heater), layer=metal_layer, port_type="electrical"))

    pt = ports["METAL_BOT_p1" if "p1" in name else "METAL_BOT_p2"]
    heater_ref.dx = pt.dx - pt.dwidth / 2 - dist_between_vias - heater_ref.dxsize/2 if "p1" in name else pt.dx + pt.dwidth / 2 + dist_between_vias + heater_ref.dxsize/2
    heater_ref.dy = y
    heater_metal_ref.dx = heater_ref.dx
    heater_metal_ref.dy = heater_ref.dy

    gf.routing.route_quad(c, heater_ref.ports["e4"], port, layer=port.layer)
    gf.routing.route_quad(c, heater_metal_ref.ports["e4"], port, layer=metal_layer)

    c.add_port(name="HEATER_METAL_" + name.split("_")[-1], port=heater_ref.ports["e2"])
    x = min(np.absolute(heater_ref.dxmin), np.absolute(heater_ref.dxmax))
    return x


@gf.cell
def ring(
    wg: CrossSectionSpec = "rib",
    pn: CrossSectionSpec = None,
    radius: float = 15,
    gap: float = 0.25,
    int_len: float = None,
    int_angle: float = None,
    ring_angle: float = 360,
    dist_pn_to_wg: float = None,
    dist_y: float = None,
    dist_to_pad: float = 55,
    dist_between_vias: float = 2.75,
    heater_percent: float = 0.8,
    max_length: float = None,
) -> gf.Component:
    """
    Create a ring component with a single waveguide

    Args:
        wg (CrossSectionSpec): Waveguide cross section
        pn (CrossSectionSpec): PN cross section
        radius (float): Radius
        gap (float): Gap
        int_len (float): Interaction length
        int_angle (float): Interaction angle
        ring_angle (float): Ring angle
        dist_pn_to_wg (float): Distance from PN to waveguide
        dist_to_pad (float): Distance to pad
        dist_between_vias (float): Distance between vias
        heater_percent (float): Heater percent
        metal_layer (LayerSpec): Metal layer

    Returns:
        gf.Component: Ring component
    """

    if (int_len is not None) + (int_angle is not None) != 1:
        raise ValueError("Provide either interaction length or interaction angle, but not both.")
    
    wg = gf.get_cross_section(wg)
    if pn:
        pn = gf.get_cross_section(pn)
        metal_layer = next((x.layer for x in pn.sections if "METAL" in x.name.upper()), None)
    
    gap = gf.snap.snap_to_grid(gap, nm=1, grid_factor=1)
    
    angle = (int_len / (2 * np.pi * (radius + gap + wg.width)) * 360) if int_len else int_angle
    if angle > 180:
        raise ValueError("Interaction length is too large")
    
    inner_arc, outer_arc =  ring_coupler_path(radius, gap, wg, angle, ring_angle)

    if max_length:
        straight_length = (max_length - outer_arc.dsize[0]) / 2
        outer_arc = gf.Path(
            [
                gf.path.straight(length=straight_length),
                outer_arc,
                gf.path.straight(length=straight_length)
            ]
        )

    c = gf.Component()

    inner_arc_ref = c.add_ref(inner_arc.extrude(wg))
    outer_arc_ref = c.add_ref(outer_arc.extrude(wg))
    inner_arc_ref.dx, inner_arc_ref.dy = 0, 0
    outer_arc_ref.dx = inner_arc_ref.dx
    outer_arc_ref.dymax = inner_arc_ref.dymax + gap + wg.width

    if pn:
        _handle_pn_section(c, radius, wg, pn, outer_arc_ref, dist_pn_to_wg, dist_y, dist_between_vias, dist_to_pad, heater_percent=heater_percent, metal_layer=metal_layer)

    c.add_port("o1", port=outer_arc_ref.ports["o1"])
    c.add_port("o2", port=outer_arc_ref.ports["o2"])

    if ring_angle < 360:
        c.add_port("o3", port=inner_arc_ref.ports["o1"])
        c.add_port("o4", port=inner_arc_ref.ports["o2"])
    
    c.flatten()
    return c