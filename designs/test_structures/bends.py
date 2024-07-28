import numpy as np
import gdsfactory as gf
from gdsfactory.typings import List, CrossSectionSpec

from . import rng
from pylayout.components import attach_grating_coupler, ring_pn_section
from cornerstone import rib_450, pn, cs_gc_silicon_1550nm
from cornerstone import CornerstoneSpec as Spec

def bend_loss(
    radius: float,
    no_of_rings: np.ndarray,
    cs: CrossSectionSpec = rib_450,
) -> List[gf.Component]:
    """
    Bend loss test structures.

    Args:
        radius: Radius of the ring.
        no_of_rings: List of number of rings.
        cs: Cross section of the ring.
    
    Returns:
        List of bend loss test structures.
    """
    cs = gf.get_cross_section(cs)
    component_list = []
    rng.shuffle(no_of_rings)

    st_len = 100
    max_length = 4 * radius * max(no_of_rings) + 2 * st_len
    
    for no in no_of_rings:
        path = gf.Path()
        path += gf.path.straight(length=st_len)
        
        for _ in np.arange(no):
            for angle in [90, -90, -90, 90]:
                path += gf.path.arc(radius=radius, angle=angle)
        
        path += gf.path.straight(length=max_length - st_len - 4 * radius * no)
        c = gf.Component()
        path_ref = c.add_ref(path.extrude(cs))
        c.add_ports(path_ref.ports)
        
        c = attach_grating_coupler(c, cs_gc_silicon_1550nm, ["o1", "o2"])
        component_list.append(c)

    return component_list

def bend_loss_pn(
    radius: float = 15,
    no_of_rings: np.ndarray = np.array([10]),
    wg: CrossSectionSpec = rib_450,
    pn: CrossSectionSpec = pn,
) -> List[gf.Component]:
    """
    Bend loss test structures with pn junctions.

    Args:
        radius: Radius of the ring.
        no_of_rings: List of number of rings.
        wg: Cross section of the ring.
        pn: Cross section of the pn junction.
    
    Returns:
        List of bend loss test structures with pn junctions.
    """
    wg = gf.get_cross_section(wg)
    pn = gf.get_cross_section(pn)
    st_len = 100
    rng.shuffle(no_of_rings)

    component_list = []
    max_len = 4 * radius * max(no_of_rings) + 2 * st_len
    pn_ring = ring_pn_section(pn=pn, radius=radius, y=0)
    low_doped_width = Spec.low_doped_width
    length = 2 * (low_doped_width - radius) + 1

    arc360 = gf.Path()
    for angle in [90, -90, -90, 90]:
        arc360 += gf.path.arc(radius=radius, angle=angle)

    for no in no_of_rings:
        c = gf.Component()
        path = gf.Path()
        path += gf.path.straight(length=st_len)

        for i in np.arange(no):
            path += arc360
            pn_ring_ref = c.add_ref(pn_ring)
            pn_ring_ref.mirror_y()
            pn_ring_ref.dymin = radius

            if radius < low_doped_width:
                path += gf.path.straight(length=length)
                pn_ring_ref.dx = st_len + (2 + 4 * i) * radius + length * i
            else:
                pn_ring_ref.dx = st_len + (2 + 4 * i) * radius

        for i in np.arange(max(no_of_rings) - no):
            angles = [90, -90] if i % 2 == 0 else [-90, 90]
            for angle in angles:
                path += gf.path.arc(radius=radius, angle=angle)
                if radius < low_doped_width:
                    path += gf.path.straight(length=length)

        path += gf.path.straight(length=max_len - path.dsize[0] + st_len)
        path_ref = c.add_ref(path.extrude(wg))
        c.add_ports(path_ref.ports)
        c = attach_grating_coupler(c, cs_gc_silicon_1550nm, ["o1", "o2"])
        component_list.append(c)

    return component_list

def main():
    no_of_rings = np.linspace(1, 6, 6)
    radius = 15
    cs = rib_450

    component_list = bend_loss_pn(radius, no_of_rings, cs)

    c = gf.grid(
        component_list,
        spacing=(50, 50),
        shape=(len(no_of_rings), 1),
        align_x="x",
    )
    
    c.show()

if __name__ == "__main__":
    main()