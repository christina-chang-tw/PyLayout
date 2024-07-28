import numpy as np

import gdsfactory as gf
from gdsfactory.typings import LayerSpec, Component

from pylayout.methods import make_even_number
from .polygon import regular_polygon

@gf.cell
def truncated_circle_poly(inner_r: float, outer_r: float, y: float, layer: LayerSpec) -> Component:
    """
    Create a truncated circle using polygons.

    Args:
        inner_r [float]: inner radius of the circle.
        outer_r [float]: outer radius of the circle.
        y [float]: y coordinate of the truncation point.
        layer [LayerSpec]: layer of the circle.

    Returns:
        Component: truncated circle.
    """
    if outer_r < inner_r:
        raise ValueError("Outer radius must be larger than inner radius")
    
    if inner_r > y and outer_r > y:
        width = make_even_number(np.sqrt(outer_r**2 - y**2) - np.sqrt(inner_r**2 - y**2))
        outer_r = np.sqrt((width + np.sqrt(inner_r**2 - y**2))**2 + y**2)

    def calculate_theta(r, y):
        return 2 * np.arcsin(np.sqrt(r**2 - y**2) / r) if r > y else 0

    outer_theta = calculate_theta(outer_r, y)
    inner_theta = calculate_theta(inner_r, y)

    def create_polygon(r, theta, layer):
        phi = 2 * np.pi - theta
        points = regular_polygon(0, 0, r, phi, start_angle=np.pi/2 + theta/2)
        return gf.Component().add_polygon(points, layer=layer)

    outer_polygon = create_polygon(outer_r, outer_theta, layer)
    inner_polygon = create_polygon(inner_r, inner_theta, layer)

    c = gf.boolean(outer_polygon, inner_polygon, operation="-", layer1=layer, layer2=layer, layer=layer)

    c.flatten()
    return c

@gf.cell
def truncated_circle_bool(
    inner_r: float,
    outer_r: float,
    y: float,
    layer: LayerSpec,
    port_prefix: str = None
) -> gf.Component:
    """
    Create a truncated circle using boolean operations.

    Args:
        inner_r [float]: inner radius of the circle.
        outer_r [float]: outer radius of the circle.
        y [float]: y coordinate of the truncation point.
        layer [LayerSpec]: layer of the circle.
        port_prefix [str]: prefix of the ports.

    Returns:
        gf.Component: truncated circle.
    """
    if outer_r < inner_r:
        raise ValueError("Outer radius must be larger than inner radius")
    if outer_r <= 0:
        raise ValueError("Outer radius should be >= 0")

    c = gf.Component()

    
    if inner_r > y and outer_r > y:
        width = make_even_number(np.sqrt(outer_r**2 - y**2) - np.sqrt(inner_r**2 - y**2))
        rin_x = np.sqrt(inner_r**2 - y**2)
        outer_r = np.sqrt((width + rin_x)**2 + y**2)
    inner_r, outer_r = map(np.round, [inner_r, outer_r], [3, 3])
    
    circ = gf.components.circle(radius=outer_r, layer=layer)

    if inner_r > 0:
        inner_c = gf.components.circle(radius=inner_r, layer=layer)
        circ = gf.boolean(circ, inner_c, operation="A-B", layer=layer)

    rect = gf.components.rectangle(size=(2*outer_r, 2*outer_r), layer=layer)
    temp = gf.Component()
    rect_ref = temp.add_ref(rect)
    circle_ref = temp.add_ref(circ)
    rect_ref.dx = circle_ref.dx
    rect_ref.dymin = circle_ref.dy + y

    truncated_circle = gf.boolean(circle_ref, rect_ref, operation="A-B", layer=layer)
    c.add_ref(truncated_circle)

    if inner_r > y and outer_r > y:
        x_center = (np.sqrt(outer_r**2 - y**2) + np.sqrt(inner_r**2 - y**2)) / 2

        c.add_port(name=f"{port_prefix}_p1", center=(x_center, y), width=width, orientation=90, layer=layer, port_type="electrical")
        c.add_port(name=f"{port_prefix}_p2", center=(-x_center, y), width=width, orientation=90, layer=layer, port_type="electrical")

    c.flatten()
    return c