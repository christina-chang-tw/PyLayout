import gdsfactory as gf
from gdsfactory.typings import CrossSectionSpec

@gf.cell
def circular_bend_180(radius: float, cs: CrossSectionSpec):
    """
    This create an 180 bend made of circular bends like this:
                       ---- o2
                       |    
                o1  ---|
    """
    c = gf.Component()

    path = gf.Path()
    path += gf.path.arc(radius=radius, angle=90)
    path += gf.path.arc(radius=radius, angle=-90)

    path = path.extrude(cs)
    c.add_ref(path)
    c.add_ports(path.ports)

    return c

@gf.cell
def circular_bend_360(radius, cs: CrossSectionSpec):
    """
    This create an 180 bend made of circular bends like this:
                       ------
                       |    |
                o1  ---|    |--- o2
    """
    c = gf.Component()

    path = gf.Path()
    angles = [90, -90, -90, 90]
    for angle in angles:
        path += gf.path.arc(radius=radius, angle=angle)
    path = path.extrude(cs)
    c.add_ref(path)
    c.add_ports(path.ports)

    return c