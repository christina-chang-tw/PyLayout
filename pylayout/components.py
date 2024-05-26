from dataclasses import dataclass

import gdsfactory as gf
from gdsfactory.technology import LayerLevel
from gdsfactory.port import Port

from pylayout.layers.cornerstone import SOI_220nm
from pylayout.methods import Methods

@dataclass
class Info:
    """
    Storing information about a structure
    """
    width: float=None
    cross_section: gf.cross_section.CrossSection=None
    radius: float=None
    layer: LayerLevel=None


class Components(gf.Component):
    def __init__(self, cs: float=None):
        self.cs = cs

    @staticmethod
    def outline(x: float, y: float):
        outline = gf.Component("outline")
        rect = gf.components.rectangle(
            size=(x, y),
            layer=SOI_220nm.OUTLINE,
            centered=True
        )
        outline.add_ref(rect)
        return outline

    @staticmethod
    def cross_section(
        width: float=0.45,
        offset: float=0,
        layer: LayerLevel=None,
        radius: float=15,
    ):
        return gf.cross_section.cross_section(
            width=width,
            offset=offset,
            layer=layer,
            bbox_offsets=(0, 0, 0, 0),
            port_types=("optical", "optical"),
            radius=radius,
        )

    def ring_single(
        self,
        gap: float,
        radius: float,
        layer: LayerLevel,
        width: float=0.45,
        angle_resolution: int=2.5,
    ):
        ring_single = gf.Component("ring_single")
        ring = gf.components.ring(
            radius=radius,
            width=width,
            angle_resolution=angle_resolution,
            layer=layer
        )
        ring_ref = ring_single.add_ref(ring)

        bus = gf.components.rectangle(
            size=(2*radius, width),
            layer=layer,
            centered=True,
            port_type="optical",
            port_orientations=(180, 0),
        )
        ring_ref.ymin = bus.ymax + gap
        ring_single.add_ref(bus)

        ring_single.add_port(name="o1", port=bus.ports["o1"])
        ring_single.add_port(name="o2", port=bus.ports["o2"])

        return ring_single
   
    @staticmethod
    def coupler_asymmetric(
        gap: float,
        dx: float,
        dy: float,
        cross_section: gf.cross_section.CrossSection,
    ) -> gf.Component:
        elem = gf.components.coupler_asymmetric(gap=gap, dx=dx, dy=dy, cross_section=cross_section)
        
        elem.ports["o1"].center = (elem.ports["o1"].center[0], elem.ports["o2"].center[1])
        elem.ports["o1"].width = cross_section.width

        port4 = Port(name="o4", width=cross_section.width,
                     center=(elem.ports["o1"].center[0], elem.ports["o1"].center[1] - (gap + cross_section.width)),
                     orientation=180, layer=cross_section.layer, port_type="optical")
        elem.add_port(port=port4)

        return elem
       
   
    def asymmetric_coupler_2x2(
        self,
        gap: float,
        dy: float,
        clen: float,
        dx: float=10
    ) -> gf.Component:
        coupler = gf.Component("asymmetric_coupler_2x2")
        right = Components.coupler_asymmetric(gap=gap, dx=dx, dy=dy, cross_section=self.cs)
        straight = gf.components.coupler_straight(length=clen, gap=gap, cross_section=self.cs)

        right_ref = coupler.add_ref(right)
        left_ref = Methods.symmetry(coupler, right, x0=right_ref.xmin-clen/2)
        
        straight_ref = coupler.add_ref(straight)
        
        straight_ref.ymax = right_ref.ymax
        Methods.connect(straight_ref, ["o1", "o4"], right_ref, ["o1", "o4"])
        Methods.connect(straight_ref, ["o2", "o3"], left_ref, ["o1", "o4"])

        Methods.add_ports(coupler, ["rs", "rb"], right_ref, ["o2", "o3"])
        Methods.add_ports(coupler, ["ls", "lb"], left_ref, ["o2", "o3"])

        return coupler






def RAMZI_2x1_MZI():
    base = gf.Component("Base")
    outline = Components.outline(100, 100)

    # create a cross-section
    cs = Components.cross_section(layer=SOI_220nm.ETCH1)
    comp = Components(cs=cs)

    gap = [1, 2, 3, 4, 5]
    obj_list = Methods.gen_objects(
        gf.components.coupler_asymmetric,
        gap=gap,
        dx=5,
        dy=5,
        cross_section=cs
    )

    c = gf.grid(
        obj_list, 
        spacing=(10, 10),
        shape=(len(obj_list), 1),
        align_x="x",
        align_y="y"
    )
        
    base << outline
    base << c

    ref = gf.ComponentReference(base)
    ref.center = (0, 0)
    base.show()

if __name__ == "__main__":
    RAMZI_2x1_MZI()