import numpy as np

import gdsfactory as gf
from gdsfactory.typings import List, Component, CrossSectionSpec, Port

def strategy1(
    c: Component,
    start_x: float,
    start_y: float, # before extrusion
    port: Port,
    xsize: float,
    ysize: float,
    cs: CrossSectionSpec,
    layers: List
):
    """
    Routing strategy 1. Not expecting the starting point to be a port
    ----
        \\
         \\
          |
          |
    Args:
        lengths: lengths of the segments [horizontal, diagonal, straight]
        start_x: x coordinate of the start point
        start_y: y coordinate of the start point
        cs: cross section
        port: port to connect to
    """
    path = gf.Path()
    angles = [0, -45, -45]
    lengths = [xsize - cs.width, cs.width/np.sqrt(2), ysize - cs.width]
    for length, angle in zip(lengths, angles):
        path.end_angle += angle
        path += gf.path.straight(length=length)
    path_ref = c.add_ref(path.extrude(cs))
    path_ref.dxmin = start_x
    path_ref.dymax = start_y + cs.width/2

    for layer in layers:
        gf.routing.route_quad(c, port, path_ref.ports["e2"], layer=layer)

def strategy2(
    c: Component,
    port1: Port,
    port2: Port,
    first_st_len: float,
    xsize: float,
    ysize: float,
    cs: CrossSectionSpec,
    layers: List=None,
    gap: float=0,
):
    """
    Routing strategy 2. Expecting the starting point to be a port.

    The second port if is a heater, use layers argument to route over different layers
    ----
    Args:
        lengths: lengths of the segments [horizontal, diagonal, straight]
        port1: port to connect to
        port2: port to connect to
        cs: cross section
    |
    |
    \\
     \\
      -----
           \\
            \\
             |
             |
    
    """
    angles = [0, +45, +45, -45, -45]
    path = gf.Path()
    path.start_angle = 0
    ysize = ysize - gap
    lengths = [first_st_len, cs.width/np.sqrt(2), xsize - 2*cs.width, cs.width/np.sqrt(2), ysize - first_st_len - cs.width]
    for length, angle in zip(lengths, angles):
        path.end_angle += angle
        path += gf.path.straight(length=length)

    ref = c.add_ref(path.extrude(cs))
    ref.drotate(-90)
    ref.dxmin = port1.dx - cs.width/2
    ref.dymax = port1.dy - gap
    gf.routing.route_quad(c, port1, ref.ports["e1"], layer=port1.layer)

    layers = layers if layers else [port2.layer]
    for layer in layers:
        gf.routing.route_quad(c, port2, ref.ports["e2"], layer=layer)


@gf.cell
def route_pads_to_ring(
    ring: Component,
    pads: Component,
    routing: dict[str, str],
    align_pad_number: int=None,
    pad_width: float=75,
    pad_gap: float=25,
    gap: float=55
) -> Component:
    """
    Route pads to a ring component

    Args:
        ring: ring component
        pads: pads component
        routing: routing dictionary
        align_pad_num: number of pads to align
        pad_width: pad width
        pad_gap: pad gap
        gap: gap between ring
    
    Returns:
        gf.Component: Component with pads connected to the ring
    """
    if align_pad_number is None:
        num = (pads.dxsize/(pad_width + pad_gap))/2
        align_pad_number = np.ceil(num) if num > 1 else 1.5

    c = gf.Component()
    ring_ref = c.add_ref(ring)
    pads_ref = c.add_ref(pads)

    # assume all pad width are the same!
    pads_ref.dxmin = ring_ref.dx - pad_width*(align_pad_number - 1 + 1/2) - pad_gap*(align_pad_number-1)
    pads_ref.dymin = ring_ref.dymax + gap

    for pp_name, r_name in routing.items():
        ring_port = ring.ports[r_name]
        gf.routing.route_quad(c, ring_port, pads_ref.ports[pp_name], layer=pads_ref.ports[pp_name].layer)

    c.add_ports(ring_ref.ports, prefix="ring_")
    c.add_ports(pads_ref.ports, prefix="pad_")
    c.add_port("o1", port=ring.ports["o1"])
    c.add_port("o2", port=ring.ports["o2"])

    c.flatten()

    return c