import gdsfactory as gf
from gdsfactory.typings import Component

from . import rng
from pylayout.components import ring_coupler_path
from cornerstone import rib_450, cs_gc_silicon_1550nm

def cross_coupling(
    radius: float=15,
    gap: float=0.2,
    angle: float=20,
    ring_angle: float=180,
    wg: gf.typings.CrossSectionSpec=rib_450,
    max_length: float=None,
) -> Component:
    """
    Cross coupling test structures. A test structure will look like this.
    The bend section consists of an inner half ring with the outer arc consists of three same radius arc.
    The middle outer arc is determined by the angle that is given and the Rout = Rinner + gap + cs.width
      -----
      -----
      |   |
    ---   ---

    Args:
        radius: Radius of the ring.
        gap: Gap between the inner ring and the outer arc.
        angle: Angle of the outer arc.
        cs: Cross section of the ring.
        max_length: Maximum length of the test structure.
    
    Returns:
        List of cross coupling test structures.
    """
    c = gf.Component()

    max_length = radius * 4 + 500 if max_length is None else max_length
    wg = gf.get_cross_section(wg)

    inner_arc, outer_arc = ring_coupler_path(radius, gap, wg, angle, ring_angle=ring_angle)
    outer_arc = gf.Path(
        [
            gf.path.straight(length=(max_length-outer_arc.dsize[0])/2),
            outer_arc,
            gf.path.straight(length=(max_length-outer_arc.dsize[0])/2),
        ]
    )

    if 2*radius < 50:
        inner_arc = gf.Path(
            [
                gf.path.straight(length=50 - 2*radius),
                inner_arc,
                gf.path.straight(length=50 - 2*radius),
            ]
        )

    inner_arc = gf.Path(
        [
            gf.path.straight(length=(max_length-inner_arc.dsize[0])/2),
            gf.path.arc(radius, angle=-ring_angle/2),
            inner_arc,
            gf.path.arc(radius, angle=-ring_angle/2),
            gf.path.straight(length=(max_length-inner_arc.dsize[0])/2),
        ]
    )
    inner_arc.drotate(180)

    outer_arc.dx = inner_arc.dx
    outer_arc.dymax = inner_arc.dymax + gap + wg.width

    outer_arc_ref = c.add_ref(outer_arc.extrude(wg))
    inner_arc_ref = c.add_ref(inner_arc.extrude(wg))

    c.add_port(name="o1", port=outer_arc_ref.ports["o1"])
    c.add_port(name="o2", port=inner_arc_ref.ports["o1"])
    c.add_port(name="o3", port=outer_arc_ref.ports["o2"])
    c.add_port(name="o4", port=inner_arc_ref.ports["o2"])
    
    c.flatten()
    return c


def main():
    couplings =  [0.28, 0.3, 0.316, 0.34, 0.35, 0.38, 0.4, 0.42, 0.45]
    import numpy as np
    from pylayout.components import add_norm_wg, attach_grating_coupler

    np.random.default_rng().shuffle(couplings)
    c_list = []
    for idx, coupling in enumerate(couplings):
        c = cross_coupling(
            radius=10,
            gap=coupling,
            angle=20,
            wg=rib_450,
            max_length=500,
        )
        c = attach_grating_coupler(c, cs_gc_silicon_1550nm, ["o1", "o2", "o3", "o4"])

        if idx % 5 == 0:
            c = add_norm_wg(c, cs_gc_silicon_1550nm, rib_450, 30, "N")
        c_list.append(c)

    c = gf.grid(
        reversed(c_list),
        shape=(len(c_list), 1),
        spacing=10,
        align_y="center"
    )
    c.show()

if __name__ == "__main__":
    main()