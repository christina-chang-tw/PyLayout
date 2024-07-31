import gdsfactory as gf
from gdsfactory.typings import CrossSectionSpec

def ring_coupler_path(
    radius: float = 15,
    gap: float = 0.2,
    wg: CrossSectionSpec = "rib",
    angle: float = 20,
    ring_angle: float = 360,
):
    outer_radius = radius + gap + wg.width
    outer_arc = gf.Path([
        gf.path.arc(outer_radius, angle / 2),
        gf.path.arc(outer_radius, -angle),
        gf.path.arc(outer_radius, angle / 2)
    ])

    straight_segment_length = 2 * radius - outer_arc.dsize[0]

    if straight_segment_length > 0:
        outer_arc = gf.Path([
            gf.path.straight(length=straight_segment_length / 2),
            outer_arc,
            gf.path.straight(length=straight_segment_length / 2)
        ])

    inner_arc = gf.path.arc(radius, angle=ring_angle)
    return inner_arc, outer_arc


@gf.cell
def ring_coupler(
    radius: float = 15,
    gap: float = 0.2,
    wg: CrossSectionSpec = "rib",
    angle: float = 20,
    ring_angle: float = 360,
):
    """
    Create a ring coupler component.

    Args:
        radius: Radius of the ring.
        gap: Gap between the ring and the waveguide.
        wg: Waveguide cross section.
        angle: Angle of the ring.
        ring_angle: Angle of the ring.

    .. code::

        import gdsfactory as gf

        c = gf.components.ring_coupler(radius=10, gap=0.2, wg=gf.cross_section.metal)
        c.plot()

    """
    c = gf.Component()
    wg = gf.get_cross_section(wg)

    # Create the outer arc path with possible straight segments
    inner_arc, outer_arc = ring_coupler_path(radius, gap, wg, angle, ring_angle)

    # Add the arcs to the component and align them
    outer_arc_ref = c.add_ref(outer_arc, name="outer_arc")
    inner_arc_ref = c.add_ref(inner_arc, name="inner_arc")
    outer_arc_ref.dx = inner_arc_ref.dx
    outer_arc_ref.dymax = inner_arc_ref.dymax + gap + wg.width

    c.flatten()
    return c