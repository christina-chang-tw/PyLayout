from functools import partial

import numpy as np
import gdsfactory as gf
from gdsfactory.typings import Union, List

from . import rng
from pylayout.components import ring, attach_grating_coupler
from cornerstone import rib_450, cs_gc_silicon_1550nm

def cross_coupling(
    radius: float=15,
    gap: Union[float, np.ndarray]=0.22,
    angle: Union[float, np.ndarray]=20,
    wg: gf.typings.CrossSectionSpec=rib_450,
    max_length: float=None,
) -> List[gf.Component]:
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
    # see if the gap is a list or the angle is a list
    if isinstance(gap, float) and isinstance(angle, float):
        gap, angle = [gap], [angle]
    if isinstance(gap, Union[list, np.ndarray]) and not isinstance(angle, Union[list, np.ndarray]):
        rng.shuffle(gap)
        angle = [angle] * len(gap)
    if isinstance(angle, Union[list, np.ndarray]) and not isinstance(gap, Union[list, np.ndarray]):
        rng.shuffle(angle)
        gap = [gap] * len(angle)

    max_length = radius * 4 + 500 if max_length is None else max_length
    wg = gf.get_cross_section(wg)

    ring180 = partial(
        ring,
        wg=wg,
        radius=radius,
        ring_angle=180,
    )
    tst = gf.path.straight(length=(max_length-2*radius)/2).extrude(wg)
    bst = gf.path.straight(length=(max_length-4*radius)/2).extrude(wg)
    st = gf.path.straight(length=max_length).extrude(wg)

    component_list = []
    for idx, (g, a) in enumerate(zip(gap, angle)):
        c = gf.Component()
        csection = ring180(gap=g, int_angle=a)
        csection_ref = c.add_ref(csection)
        csection_ref.dcenter = (0, 0)

        half_bend = gf.path.arc(radius=radius, angle=90, start_angle=-90).extrude(wg)
        lbend_ref, rbend_ref = [c.add_ref(half_bend) for _ in range(2)]
        rbend_ref.mirror_x()

        ltst_ref, rtst_ref = [c.add_ref(tst) for _ in range(2)]
        lbst_ref, rbst_ref = [c.add_ref(bst) for _ in range(2)]

        ltst_ref.connect("o2", csection_ref, "o1")
        rtst_ref.connect("o1", csection_ref, "o2")
        lbend_ref.connect("o1", csection_ref, "o3")
        rbend_ref.connect("o1", csection_ref, "o4")

        # because the ring is quite small so this increases the grating coupler gap!
        if 2*radius < 50:
            extra_st = gf.path.straight(length=50).extrude(wg)
            extra_lst_ref = c.add_ref(extra_st)
            extra_rst_ref = c.add_ref(extra_st)
            extra_lst_ref.connect("o1", csection_ref, "o3")
            extra_rst_ref.connect("o1", csection_ref, "o4")
            lbend_ref.connect("o1", extra_lst_ref, "o2")
            rbend_ref.connect("o1", extra_rst_ref, "o2")

        lbst_ref.connect("o2", lbend_ref, "o2")
        rbst_ref.connect("o1", rbend_ref, "o2")

        c.add_port(name="o1", port=ltst_ref.ports["o1"])
        c.add_port(name="o2", port=rtst_ref.ports["o2"])
        c.add_port(name="o3", port=lbst_ref.ports["o1"])
        c.add_port(name="o4", port=rbst_ref.ports["o2"])

        if idx % 5 == 0:
            st_ref = c.add_ref(st)
            st_ref.dx, st_ref.dy = csection_ref.dx, rtst_ref.dymax + 40
            c.add_port(name="o5", port=st_ref.ports["o1"])
            c.add_port(name="o6", port=st_ref.ports["o2"])
            c = attach_grating_coupler(c, cs_gc_silicon_1550nm, ["o1", "o2", "o3", "o4", "o5", "o6"])
        else:
            c = attach_grating_coupler(c, cs_gc_silicon_1550nm, ["o1", "o2", "o3", "o4"])

        component_list.append(c)

    component_list = list(reversed(component_list))
    return component_list

def main():
    component_list = cross_coupling(
        radius=30,
        gap=np.linspace(0.22, 0.3, 5),
        angle=20,
        max_length=5000,
    )

    c = gf.grid(
        component_list,
        spacing=(15, 15),
        shape=(len(component_list), 1),
        align_x="x",
    )

    c.flatten()
    c.show()

if __name__ == "__main__":
    main()