import numpy as np
import gdsfactory as gf
from gdsfactory.typings import List, CrossSectionSpec

from . import rng
from pylayout.components import attach_grating_coupler, ring_pn_section, add_norm_wg
from cornerstone import rib_450, pn, cs_gc_silicon_1550nm
from .straight import straight


def _bend_360(radius: float) -> gf.Path:
    """
    Create a 360 degree bend.

    Args:
        radius: Radius of the bend.
    
    Returns:
        360 degree bend.
    """
    path = gf.Path()
    angles = [90, -90, -90, 90]
    for angle in angles:
        path += gf.path.arc(radius=radius, angle=angle)
    return path

def bend_loss(
    radius: float,
    no_of_rings: np.ndarray,
    wg: CrossSectionSpec = rib_450,
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
    wg = gf.get_cross_section(wg)
    component_list = []
    rng.shuffle(no_of_rings)

    st_len = 100
    max_length = 4 * radius * max(no_of_rings) + 2 * st_len
    
    for no in no_of_rings:
        path = gf.Path()
        path += gf.path.straight(length=st_len)
        
        for _ in np.arange(no):
            path += _bend_360(radius)
        
        path += gf.path.straight(length=max_length - st_len - 4 * radius * no)
        c = gf.Component()
        path_ref = c.add_ref(path.extrude(wg))
        c.add_ports(path_ref.ports)
        c = attach_grating_coupler(c, cs_gc_silicon_1550nm, ["o1", "o2"])
        component_list.append(c)

    st = straight(length=max_length, gc=cs_gc_silicon_1550nm, cs=wg)
    component_list.extend([st, st])

    component_list = list(reversed(component_list))
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
    st_len = 200
    rng.shuffle(no_of_rings)

    component_list = []
    pn_ring = ring_pn_section(pn=pn, radius=radius, y=0)
    length = pn_ring.dxsize/2 - radius + 1

    max_length = (4*radius + length)*max(no_of_rings) + 2 * st_len

    for i, no in enumerate(no_of_rings):
        c = gf.Component()
        path = gf.Path()
        path += gf.path.straight(length=st_len)

        for i in np.arange(no):
            path += _bend_360(radius)
            pn_ring_ref = c.add_ref(pn_ring)
            pn_ring_ref.mirror_y()
            pn_ring_ref.dymin = radius

            if radius < pn_ring.dxsize - 1:
                path += gf.path.straight(length=length)
                pn_ring_ref.dx = st_len + (2 + 4 * i) * radius + length * i
            else:
                pn_ring_ref.dx = st_len + (2 + 4 * i) * radius

        # make sure undoped regions have the same number count
        for i in np.arange(max(no_of_rings) - no):
            angles = [90, -90] if i % 2 == 0 else [-90, 90]
            for i, angle in enumerate(angles):
                path += gf.path.arc(radius=radius, angle=angle)
                if radius < pn_ring.dxsize - 1 and i == 1:
                    path += gf.path.straight(length=length)

        path += gf.path.straight(length=max_length - path.dsize[0])
        path_ref = c.add_ref(path.extrude(wg))
        c.add_ports(path_ref.ports)
        c = attach_grating_coupler(c, cs_gc_silicon_1550nm, ["o1", "o2"])

        component_list.append(c)

    st = straight(length=max_length, gc=cs_gc_silicon_1550nm, cs=wg)
    component_list.extend([st, st])
    component_list = list(reversed(component_list))
    return component_list

def main():
    start = 1
    step = 3
    num = 4
    no_of_rings = np.arange(start, step*num + start, step)
    radius = 4
    cs = rib_450

    component_list = bend_loss(radius, no_of_rings, wg=cs)

    c = gf.grid(
        component_list,
        spacing=30,
        shape=(3, 2),
        align_x="x",
    )
   
    c.show()

if __name__ == "__main__":
    main()