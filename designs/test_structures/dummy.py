import gdsfactory as gf

from pylayout.components import attach_grating_coupler
from pylayout.cross_section import rib_cs450


def dummy_waveguide(
    length: float=550,
    cs: gf.typings.CrossSectionSpec=rib_cs450,
) -> gf.Component:
    """
    Dummy straight waveguide test structure. The idea is to prevent possible fabrication
    errors due to the density difference between different areas of the chip.

    Args:
        length (float): Length of the straight waveguide.
        cs (gf.typings.CrossSectionSpec): Cross section of the straight waveguide.
    
    Returns:
        Straight waveguide test structure
    """
    cs = gf.get_cross_section(cs)

    st = gf.path.straight(length=length).extrude(cs)
    st = attach_grating_coupler(st, ["o1", "o2"])
    return st

def main():
    st = dummy_waveguide()
    st.show()

if __name__ == "__main__":
    main()