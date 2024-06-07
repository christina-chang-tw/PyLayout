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
        """
        Draw an outline of the entire chip

        Args:
            x [float]: float: width of the chip
            y [float]: float: height of the chip
        
        Returns:
            gf.Component: outline of the chip
        """
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
    ) -> gf.cross_section.CrossSection:
        """
        Create a template for the cross-section of a waveguide.

        Args:
            width [float]: float: width of the waveguide
            offset [float]: float: offset of the waveguide
            layer [LayerLevel]: LayerLevel: layer of the waveguide
            radius [float]: float: radius of the waveguide
        
        Returns:
            gf.cross_section.CrossSection: cross-section of the waveguide
        """
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
        curve: bool=False,
    ):
        """
        Draw a single ring resonator with coupling region = 0 with its a bus waveguide.

        Args:
            gap [float]: float: gap between the ring and the bus
            radius [float]: float: radius of the ring
            layer [LayerLevel]: LayerLevel: layer of the ring
            width [float]: float: width of the bus waveguide
            angle_resolution [int]: int: angle resolution of the ring
            curve [bool]: bool: True for a curved bus waveguide

        Returns:
            gf.Component: single ring resonator with a bus waveguide
        """
        ring_single = gf.Component(uid('ring_single'))
        ring = gf.components.ring(
            radius=radius,
            width=width,
            angle_resolution=angle_resolution,
            layer=layer
        )
        ring_ref = ring_single.add_ref(ring)

        if curve:
            bus_r = gf.components.bend_s(
                size=(2*radius, 2),
                npoints=111,
                cross_section=self.cs,
            )
            bus_r_ref = ring_single.add_ref(bus_r)
            bus_l_ref = Methods.symmetry(ring_single, bus_r, x0=bus_r.xmin)

            bus_r_ref.ymax = ring_ref.ymin - gap
            bus_r_ref.xmin = ring_ref.x

            Methods.connect(bus_l_ref, "o2", bus_r_ref, "o1")
            ring_single.add_port(name="o1", port=bus_l_ref.ports["o1"])
            ring_single.add_port(name="o2", port=bus_r_ref.ports["o2"])

            
            # bus_l_ref.xmin = ring_single.xmin
        else:
            bus = gf.components.straight(
                length=2*radius,
                npoints=2,
                cross_section=self.cs
            )
            bus_ref = ring_single.add_ref(bus)
            bus_ref.ymax = ring_ref.ymin - gap
            bus_ref.xmin = ring_ref.xmin
            
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
        coupler = gf.Component(uid("asymmetric_coupler_2x2"))
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