import gdsfactory as gf
from gdsfactory.typings import CrossSectionSpec, Component, Port, ComponentReference

def straight_with_heater(
    length: int=500,
    heater_length: int=350,
    wg: CrossSectionSpec = "rib",
    heater: CrossSectionSpec = "rib",
    metal_cs: CrossSectionSpec = None,
    gap_filament_to_pad: int = 70,
    gap_between_pads: int = 55,
):
    """
    Create a straight waveguide with a heater on top.

    Args:
        length (int): Length of the waveguide.
        wg (CrossSectionSpec): Waveguide cross section.
        filament (CrossSectionSpec): Filament cross section.
        metal_cs (CrossSectionSpec): Metal cross section.
        gap_filament_to_pad (int): Gap between filament and pad.
        gap_between_pads (int): Gap between pads.
        metal_layer (LayerSpec): Metal layer.
        filament_layer (LayerSpec): Filament layer.
    
    Returns:
        gf.Component: Component with a straight waveguide and a heater on top.
    """
    c = gf.Component()

    wg, heater = map(gf.get_cross_section, [wg, heater])

    waveguide = gf.path.straight(length=length).extrude(wg)
    waveguide_ref = c.add_ref(waveguide)

    extra_heater_length = 1
    h = gf.Path([
        gf.path.straight(length=extra_heater_length),
        gf.path.arc(radius=heater.width, angle=-90),
        gf.path.straight(length=heater_length),
        gf.path.arc(radius=heater.width, angle=-90),
        gf.path.straight(length=extra_heater_length)
    ]).extrude(heater)
    heater_ref = c.add_ref(h)
    heater_ref.drotate(90)
    heater_ref.dx, heater_ref.dymax = waveguide_ref.dx, waveguide_ref.dy + heater.width/2

    def place_metal(ref: ComponentReference, dx: float, dymin: float, port1: str, port2: str):
        ref.dx, ref.dymin = dx, dymin
        gf.routing.route_quad(c, ref.ports[port1], heater_ref.ports[port2], layer=metal_cs.layer)
        gf.routing.route_quad(c, ref.ports[port1], heater_ref.ports[port2], layer=heater.layer)

    if metal_cs is not None:
        metal_cs = gf.get_cross_section(metal_cs)
        metal_path = gf.Path().append([
            gf.path.straight(length=(heater_length / 2 - gap_between_pads / 2 + 5 - (metal_cs.width / 2 + 10))),
            gf.path.arc(radius=(metal_cs.width / 2 + 10), angle=90),
            gf.path.straight(length=20)
        ])
        metal_path = metal_path.extrude(metal_cs)

        lmetal_ref = c.add_ref(metal_path).mirror_x()
        place_metal(lmetal_ref, heater_ref.dxmin - metal_cs.width/2 + lmetal_ref.dxsize/2,
                    heater_ref.dymax - heater.width - gap_filament_to_pad - metal_cs.width, port1="e2", port2="e1")
        rmetal_ref = c.add_ref(metal_path)
        place_metal(rmetal_ref, heater_ref.dxmax + metal_cs.width/2 - rmetal_ref.dxsize/2, 
                    heater_ref.dymax - heater.width - gap_filament_to_pad - metal_cs.width, port1="e2", port2="e2")


    c.add_port("o1", port=waveguide_ref.ports["o1"])
    c.add_port("o2", port=waveguide_ref.ports["o2"])
    c.add_port("e1", port=heater_ref.ports["e1"])
    c.add_port("e2", port=heater_ref.ports["e2"])

    c.flatten()
    return c