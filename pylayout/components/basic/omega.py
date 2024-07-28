import gdsfactory as gf
from gdsfactory.typings import Component, CrossSectionSpec

@gf.cell
def omega_shape(
    extra_length: float,
    cs: CrossSectionSpec,
    const_length: float=100
) -> Component:
    """
    This creates a structure that takes in the form of an omega shape. Mainly for creating equal length for bends test structures.

          |--- length1 --------------|
          |                          |
          |--|        |---length2----|
             |        |
    in  -----|        |-----  out
    """
    c = gf.Component()

    long_st = const_length * 3 + extra_length / 2
    short_st = const_length + extra_length / 2

    path_list = [
        (const_length, 180), (const_length, -180), 
        (long_st, -180), (short_st, 180), (const_length, 0)
    ]

    path = gf.Path()
    for length, angle in path_list:
        path += gf.path.straight(length=length)
        if angle:
            path += gf.path.arc(radius=10, angle=angle)

    ref = c.add_ref(path.extrude(cs))
    c.add_ports(ref.ports)

    return c