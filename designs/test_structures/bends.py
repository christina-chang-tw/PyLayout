import numpy as np
import gdsfactory as gf
from gdsfactory.typings import List, CrossSectionSpec

from . import rng
from pylayout.components import attach_grating_coupler, pn_section_ring
from pylayout.cross_section import rib_cs450, pn_cs

def bend_loss(
    radius: float,
    no_of_rings: np.ndarray,
    cs: CrossSectionSpec=rib_cs450,
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
    max_length = 4*radius*max(no_of_rings) + 2*st_len
    for no in no_of_rings:       
        path = gf.Path()
        path += gf.path.straight(length=st_len)
        for _ in range(no):
            path += gf.path.arc(radius=radius, angle=90)
            path += gf.path.arc(radius=radius, angle=-90)
            path += gf.path.arc(radius=radius, angle=-90)
            path += gf.path.arc(radius=radius, angle=90)
        path += gf.path.straight(length=max_length-st_len-4*radius*no)
        path = c.add_ref(path.extrude(cs))
        c.add_ports(path.ports)
        c = attach_grating_coupler(c, ["o1", "o2"])
        component_list.append(c)

    return component_list

def bend_loss_pn(
    radius: float=15,
    no_of_rings: np.ndarray,
    cs: CrossSectionSpec=rib_cs450,
    pn_cs: CrossSectionSpec=pn_cs,
) -> List[gf.Component]:
    """
    Bend loss test structures with pn junctions. Within one full ring of the bend,
    only half of it will have the pn junction. It also conpensates for the additional non-doped
    ring sections.

    Args:
        radius: Radius of the ring.
        no_of_rings: List of number of rings.
        cs: Cross section of the ring.
        pn_cs: Cross section of the pn junction.
    
    Returns:
        List of bend loss test structures with pn junctions.
    """
    cs = gf.get_cross_section(cs)
    pn_cs = gf.get_cross_section(pn_cs)
    st_len = 100
    rng.shuffle(no_of_rings)

    component_list = []
    
    max_len = 4*radius*max(no_of_rings) + 2*st_len
    pn_ring = pn_section_ring(pn=pn_cs, radius=radius, y=0)
    length = 2*(CrossSectionSpec.low_doped_width - radius) + 1

    arc360 = gf.Path()
    arc360 += gf.path.arc(radius=radius, angle=90)
    arc360 += gf.path.arc(radius=radius, angle=-90)
    arc360 += gf.path.arc(radius=radius, angle=-90)
    arc360 += gf.path.arc(radius=radius, angle=90)
    
    for no in no_of_rings:
        c = gf.Component()
        
        path = gf.Path()
        path += gf.path.straight(length=st_len)
        
        for i in range(no):
            path += arc360
            pn_ring_ref = c.add_ref(pn_ring)
            pn_ring_ref.mirror_y()
            pn_ring_ref.dymin = radius

            # add a straight to prevent overlapping
            if radius < CrossSectionSpec.low_doped_width:
                path += gf.path.straight(length=length)
                pn_ring_ref.dx = st_len + (2 + 4*i)*radius + length*i
            else:
                pn_ring_ref.dx = st_len + (2 + 4*i)*radius

        for i in np.arange(max(no_of_rings) - no):
            angle1 = 90 if i % 2 == 0 else -90
            angle2 = - angle1
            path += gf.path.arc(radius=radius, angle=angle1)
            path += gf.path.arc(radius=radius, angle=angle2)
            # add a straight to prevent overlapping
            if radius < CrossSectionSpec.low_doped_width:
                path += gf.path.straight(length=length)

        path += gf.path.straight(length=max_len-path.dsize[0]+st_len)
        path = c.add_ref(path.extrude(cs))
        c.add_ports(path.ports)

        c = attach_grating_coupler(c, ["o1", "o2"])
        component_list.append(c)

    return component_list

def main():
    no_of_rings = np.linspace(1, 6, 6)
    radius = 15
    cs = rib_cs450

    component_list = bend_loss(radius, no_of_rings, cs)

    c = gf.Component()
    c = gf.grid(
        component_list,
        spacing=(500, 86),
        shape=(6, 2),
        align_x="xmin",
        align_y="y"
    )
    
    c.show()

if __name__ == "__main__":
    main()