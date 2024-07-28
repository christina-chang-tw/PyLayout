import gdsfactory as gf
from gdsfactory.typings import CrossSectionSpec, Component

from .truncated_circle import truncated_circle_bool

@gf.cell
def ring_pn_section(
    radius: float,
    pn: CrossSectionSpec,
    y: float, # distance from the center of the ring to the straight arc
    heater_percent: float=0.7,
) -> Component:
    c = gf.Component()

    for sec in pn.sections:
        temp_y = y
        if gf.get_layer(sec.layer) == 3 \
            or gf.get_layer(sec.layer) == 5:
            continue

        # need to exclude heater metal
        if "heater_metal".upper() in sec.name.upper():
            continue

        outer_r = radius - sec.offset + sec.width/2
        inner_r = radius - sec.offset - sec.width/2

        # life is too hard...too disgusting...
        if "heater".upper() in sec.name.upper():
            arc = gf.path.arc(radius=radius, angle=heater_percent*360, start_angle=90+(1-heater_percent)*180)
            # make crossection from a section
            cs = gf.cross_section.CrossSection(sections=[sec])
            arc = arc.extrude(cs)
            ref = c.add_ref(arc)
            ref.dx, ref.dymin = 0, -radius-sec.width/2
            c.add_port("HEATER_p2", ref.ports["e1"])
            c.add_port("HEATER_p1", ref.ports["e2"])
        else:
            pn_ring = truncated_circle_bool(inner_r, outer_r, temp_y, sec.layer, port_prefix=sec.name)
            ref = c.add_ref(pn_ring)
            c.add_ports(ref.ports)

    c.flatten()
    return c