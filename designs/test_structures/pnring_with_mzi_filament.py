import gdsfactory as gf
from gdsfactory.typings import ComponentFactory, Component, List, CrossSectionSpec, LayerSpec

from cornerstone import metal_pad, filament, rib_450, pn_450_with_metal, metal

from pylayout.components import ring, straight_with_filament
from pylayout.routing import route_pads_to_ring, strategy1, strategy2
from pylayout.methods import connect_all
from pylayout.cross_section import MSpec

def ring_and_mzi_heater(
    r: Component,
    mzi_heater: Component,
    wg: CrossSectionSpec = "rib",
    metal: CrossSectionSpec = None,
    pads: List[Component] = [metal_pad]*5,
    pad_spacing: float = MSpec.pad_spacing,
    pad_width: float = MSpec.pad_width,
    ring_to_pad_gap: float = 50,
    max_length: float = 1200,
    dist_ring_to_mzi: float = 150,
    lst_length: float = 100,
    filament_layer: LayerSpec = (0, 0),
):
    """
    This design has a ring with an mzi heater and it uses a gsgsg pad.
    """
    r = gf.get_component(r)
    mzi_heater = gf.get_component(mzi_heater)
    wg = gf.get_cross_section(wg)

    straight_length = max_length - dist_ring_to_mzi - r.dxsize - mzi_heater.dxsize - lst_length
    if straight_length < 0:
        raise ValueError("Please increase the maximum length")

    c = gf.Component()

    routing = {
        "0_0_e4": "METAL_BOT_p2",
        "1_0_e4": "METAL_TOP_p1",
        "2_0_e4": "METAL_BOT_p1",
    }

    pads = gf.grid(pads, spacing=(pad_spacing, pad_spacing))
    r = route_pads_to_ring(ring=r, pads=pads, routing=routing, 
            align_pad_number=2, pad_width=pad_width, gap=ring_to_pad_gap)
    
    ring_ref = c.add_ref(r)
    mzi_heater_ref = c.add_ref(mzi_heater)
    inter_st_ref = c.add_ref(gf.path.straight(length=dist_ring_to_mzi).extrude(wg))
    lst_ref = c.add_ref(gf.path.straight(length=lst_length).extrude(wg))
    rst_ref = c.add_ref(gf.path.straight(length=straight_length).extrude(wg))

    connections = [
        (ring_ref, "o1", lst_ref, "o2"),
        (inter_st_ref, "o1", ring_ref, "o2"),
        (mzi_heater_ref, "o2", inter_st_ref, "o2"),
        (rst_ref, "o1", mzi_heater_ref, "o1"),
    ]
    
    connect_all(connections)

    port = ring_ref.ports["pad_4_0_e1"]
    xsize = mzi_heater_ref.ports["e1"].dx + metal.width/2 - port.dx
    ysize = port.dy - port.dwidth/2 + metal.width - mzi_heater_ref.ports["e1"].dy - 9
    strategy1(
        c, start_x=port.dx, start_y=port.dy - port.dwidth/2 + metal.width/2,
        port=mzi_heater_ref.ports["e1"], xsize=xsize, ysize=ysize, cs=metal, layers=[metal.layer, filament_layer]
    )

    xsize = mzi_heater_ref.ports["e2"].dx - ring_ref.ports["pad_3_0_e4"].dx + metal.width
    if xsize - 2*metal.width > 0:
        ysize = ring_ref.ports["pad_3_0_e4"].dy - mzi_heater_ref.ports["e2"].dy - 9
        strategy2(c, port1=ring_ref.ports["pad_3_0_e4"], port2=mzi_heater_ref.ports["e2"], first_st_len=10, xsize=xsize, ysize=ysize, cs=metal, layers=[metal.layer, filament_layer], gap=7)
    else:
        rect_ref = c.add_ref(gf.components.rectangle(size=(metal.width, 10), layer=metal.layer))
        rect_ref.dx = mzi_heater_ref.ports["e2"].dx
        rect_ref.dymin = mzi_heater_ref.ports["e2"].dy + 6
        gf.routing.route_quad(c, ring_ref.ports["pad_3_0_e4"], rect_ref.ports["e2"], layer=metal.layer)
        gf.routing.route_quad(c, rect_ref.ports["e4"], mzi_heater_ref.ports["e2"], layer=metal.layer)
        gf.routing.route_quad(c, rect_ref.ports["e4"], mzi_heater_ref.ports["e2"], layer=filament_layer)

    c.add_port("o1", lst_ref.ports["o1"])
    c.add_port("o2", rst_ref.ports["o2"])

    c.flatten()

    return c

if __name__ == "__main__":
    r = ring(wg=rib_450, pn=pn_450_with_metal, int_angle=20, dist_pn_to_wg=1)
    mzi_heater = straight_with_filament(wg=rib_450, heater=filament)
    c = ring_and_mzi_heater(r=r, mzi_heater=mzi_heater, wg=rib_450, metal=metal(width=20), filament_layer=(39, 0))
    c.show()