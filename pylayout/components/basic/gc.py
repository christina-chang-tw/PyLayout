from functools import partial

import gdsfactory as gf
from gdsfactory.typings import List, Component

gc_silicon_1550nm = partial(
    gf.components.grating_coupler_elliptical_trenches,
    polarization="te",
    taper_length=24.5,
    taper_angle=27,
    trenches_extra_angle=12,
    wavelength=1.55,
    fiber_angle=45,
    grating_line_width=0.315,
    neff=3.48,
    ncladding=1.444,
    p_start=40,
    n_periods=30,
    end_straight_length=0,
)

def attach_grating_coupler(obj: Component, gc: Component, ports: List[str]) -> Component:
    """
    Attach grating couplers to the component

    Args:
        obj [gf.Component]: gf.Component: component to attach the grating couplers
        ports [list]: list: list of ports of the component

    Returns:
        gf.Component: component with the grating couplers attached
    """
    c = gf.Component()
    gc = gf.get_component(gc)
    obj_ref = c.add_ref(obj)

    for port in ports:
        gc_ref = c.add_ref(gc)
        gc_ref.connect("o1", obj_ref, port)

    c.flatten()
    return c