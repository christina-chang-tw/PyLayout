import numpy as np

import gdsfactory as gf
from gdsfactory.typings import LayerSpec

from .polygon import regular_polygon

@gf.cell
def medal_shape(
    rect_width: float,
    rect_height: float,
    trap_short_width: float,
    trap_height: float,
    midrect_height: float,
    radius: float,
    layer: LayerSpec=(0,0),
):
    """
    This create a medal shape structure. If this is for a metal layer, then please also specify a via layer
           
                    |---rect width---|
                    |                | rect height
                    |                |
                     \\            //
                      \\          //   trap height
                       ------------    trap short width
                       |          |    midrect height
                       |----------|    
                      /            \\
                     /              \\
                    |                |  radius
                    \\              //
                     \\            //  
                       ------------


    Args:
        rect_width [float]: width of the rectangular part
        rect_height [float]: height of the rectangular part
        trap_short_width [float]: width of the trapezium part
        trap_height [float]: height of the trapezium part
        midrect_height [float]: height of the middle rectangular part
        radius [float]: radius of the circular part
    """
    c = gf.Component()

    circ_y = - rect_height - trap_height - midrect_height - np.sqrt(radius**2 - (trap_short_width/2)**2)
    half_ang = np.arcsin((trap_short_width/2)/radius)
    
    poly_pts = regular_polygon(x=rect_width/2, y=circ_y, radius=radius, angle=-2*(np.pi-half_ang), start_angle=np.pi/2-half_ang)
    
    points = [
        [0, 0],
        [rect_width, 0],
        [rect_width, -rect_height],
        [(rect_width + trap_short_width)/2, -rect_height-trap_height],
        [(rect_width + trap_short_width)/2, -rect_height-trap_height-midrect_height],
    ]

    points.extend(poly_pts)
    points += [
        [(rect_width - trap_short_width)/2, -rect_height-trap_height-midrect_height],
        [(rect_width - trap_short_width)/2, -rect_height-trap_height],
        [0, -rect_height],
    ]
    c.add_polygon(points, layer=layer)

    c.flatten()
    return c