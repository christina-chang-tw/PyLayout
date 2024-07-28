from functools import partial

import numpy as np

import gdsfactory as gf
from gdsfactory.typings import List, Component, LayerSpec, CrossSectionSpec
from gdsfactory.components.grating_coupler_elliptical import grating_tooth_points
from gdsfactory.functions import DEG2RAD

@gf.cell
def grating_coupler_elliptical_trenches(
    polarization: str = "te",
    taper_length: float = 16.6,
    taper_angle: float = 30.0,
    trenches_extra_angle: float = 9.0,
    wavelength: float = 1.53,
    fiber_angle: float = 15.0,
    grating_line_width: float = 0.343,
    neff: float = 2.638,  # tooth effective index
    ncladding: float = 1.443,  # cladding index
    layer_trench: LayerSpec | None = "SHALLOW_ETCH",
    p_start: int = 26,
    n_periods: int = 30,
    end_straight_length: float = 0.2,
    cross_section: CrossSectionSpec = "strip",
    **kwargs,
) -> Component:
    r"""Returns Grating coupler with defined trenches.

    Some foundries define the grating coupler by a shallow etch step (trenches)
    Others define the slab that they keep (see grating_coupler_elliptical)

    Args:
        polarization: 'te' or 'tm'.
        taper_length: taper length from straight I/O.
        taper_angle: grating flare angle.
        trenches_extra_angle: extra angle for the trenches.
        wavelength: grating transmission central wavelength.
        fiber_angle: fibre polish angle in degrees.
        grating_line_width: of the 220 ridge.
        neff: tooth effective index.
        ncladding: cladding index.
        layer_trench: for the trench.
        p_start: first tooth.
        n_periods: number of grating teeth.
        end_straight_length: at the end of straight.
        cross_section: cross_section spec.
        kwargs: cross_section settings.


    .. code::

                      fiber

                   /  /  /  /
                  /  /  /  /
                _|-|_|-|_|-|___
        WG  o1  ______________|

    """
    xs = gf.get_cross_section(cross_section, **kwargs)
    wg_width = xs.width
    layer = xs.layer

    # Compute some ellipse parameters
    sthc = np.sin(fiber_angle * DEG2RAD)
    d = neff**2 - ncladding**2 * sthc**2
    a1 = wavelength * neff / d
    b1 = wavelength / np.sqrt(d)
    x1 = wavelength * ncladding * sthc / d

    a1 = round(a1, 3)
    b1 = round(b1, 3)
    x1 = round(x1, 3)

    period = float(a1 + x1)
    trench_line_width = period - grating_line_width

    c = gf.Component()

    # Make each grating line
    for p in range(p_start, p_start + n_periods + 1):
        pts = grating_tooth_points(
            p * a1,
            p * b1,
            p * x1,
            width=trench_line_width,
            taper_angle=taper_angle + trenches_extra_angle,
        )
        c.add_polygon(pts, layer_trench)

    # Make the taper
    p_taper = p_start - 1
    p_taper_eff = p_taper
    a_taper = a1 * p_taper_eff
    # b_taper = b1 * p_taper_eff
    x_taper = x1 * p_taper_eff

    for sec in xs.sections:
        x_output = a_taper + x_taper - taper_length + grating_line_width / 2
        xmax = x_output + taper_length + n_periods * period + 3 + sec.width
        y = sec.width / 2 + np.tan(taper_angle / 2 * np.pi / 180) * xmax
        pts = [
            (x_output, -sec.width / 2),
            (x_output, +sec.width / 2),
            (xmax, +y),
            (xmax + end_straight_length, +y),
            (xmax + end_straight_length, -y),
            (xmax, -y),
        ]
        c.add_polygon(pts, sec.layer)

    c.add_port(
        name="o1",
        center=(x_output, 0),
        width=wg_width,
        orientation=180,
        layer=layer,
        cross_section=xs,
    )
    c.info["period"] = float(np.round(period, 3))
    c.info["polarization"] = polarization
    c.info["wavelength"] = wavelength
    xs.add_bbox(c)

    x = np.round(taper_length + period * n_periods / 2, 3)
    c.add_port(
        name="o2",
        center=(x, 0),
        width=10,
        orientation=0,
        layer=layer,
        port_type=f"vertical_{polarization}",
    )
    return c


gc_silicon_1550nm = partial(
    grating_coupler_elliptical_trenches,
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

def attach_grating_coupler(obj: Component, gc: Component, ports: List[str]=None) -> Component:
    """
    Attach grating couplers to the component

    Args:
        obj [gf.Component]: gf.Component: component to attach the grating couplers
        ports [list]: list: list of ports of the component

    Returns:
        gf.Component: component with the grating couplers attached
    """
    if ports is None:
        ports = [x.name for x in obj.ports]

    c = gf.Component()
    gc = gf.get_component(gc)
    obj_ref = c.add_ref(obj)

    for port in ports:
        gc_ref = c.add_ref(gc)
        gc_ref.connect("o1", obj_ref, port)

    c.flatten()
    return c