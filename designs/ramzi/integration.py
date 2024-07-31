import gdsfactory as gf
from gdsfactory.typings import CrossSectionSpec

from pylayout.components import dice_marker

from designs.test_structures import single_ring_pn, single_ring_heater_gsgsg, single_ring_heater_gssg, straight
from cornerstone import rib_450, pn_450_with_metal_and_heater, pn_450_with_metal, filament, LAYER, cs_gc_silicon_1550nm

from .dual_rings import ramzi_dual_rings_gsgsg_gsgsg, ramzi_dual_rings_gsgsg_gssg
from .one_ring import ramzi_one_ring

@gf.cell
def integrate_all_structures(
    wg: CrossSectionSpec,
    pn_ring: CrossSectionSpec,
    pn_heater: CrossSectionSpec,
    mzi_heater: CrossSectionSpec,
    radius: float,
    gap: float,
    angle: float,
    arm_distance: float,
    heater_length: float,
    heater_percent: float,
    dist_pn_to_wg: float,
    dist_y: float,
    one_ring_ramzi_arm_length: float,
    dual_ring_ramzi_arm_length: float,
    singles_length: float,
    spacing: float,
):
    c = gf.Component()

    # test structures

    coupler_length = cs_gc_silicon_1550nm().dxsize

    t_pnring = single_ring_pn(
        radius=radius,
        angle=angle,
        gap=gap,
        dist_pn_to_wg=dist_pn_to_wg,
        wg=wg,
        pn=pn_ring,
        max_length=singles_length,
        dist_y=dist_y,
        heater_percent=heater_percent
    )
    temp1 = gf.Component()
    t_pnring_ref = temp1.add_ref(t_pnring)
    st = straight(length=t_pnring_ref.dxsize - coupler_length*2, cs=wg, gc=cs_gc_silicon_1550nm)
    ref = temp1.add_ref(st)
    ref.dymax, ref.dx = t_pnring_ref.dymax - 40, t_pnring_ref.dx

    t_gsgsg_ring = single_ring_heater_gsgsg(
        radius=radius,
        angle=angle,
        gap=gap,
        dist_pn_to_wg=dist_pn_to_wg,
        wg=wg,
        pn=pn_heater,
        max_length=singles_length,
        dist_y=dist_y,
        heater_percent=heater_percent
    )
    temp5 = gf.Component()
    t_gsgsg_ring_ref = temp5.add_ref(t_gsgsg_ring)
    st = straight(length=t_gsgsg_ring_ref.dxsize - coupler_length*2, cs=wg, gc=cs_gc_silicon_1550nm)
    ref = temp5.add_ref(st)
    ref.dymax, ref.dx = t_gsgsg_ring_ref.dymax - 40, t_gsgsg_ring_ref.dx

    t_gssg_ring = single_ring_heater_gssg(
        radius=radius,
        angle=angle,
        gap=gap,
        dist_pn_to_wg=dist_pn_to_wg,
        wg=wg,
        pn=pn_heater,
        max_length=singles_length,
        dist_y=dist_y,
        heater_percent=heater_percent
    )


    ramzi_1ring = ramzi_one_ring(
        radius=radius,
        wg=wg,
        pn=pn_ring,
        mzi_heater=mzi_heater,
        int_angle=angle,
        gap=gap,
        arm_length=one_ring_ramzi_arm_length,
        arm_distance=arm_distance,
        heater_length=heater_length,
        dist_pn_to_wg=dist_pn_to_wg,
        heater_percent=heater_percent,
        dist_y=dist_y
    )
    temp2 = gf.Component()
    ramzi_1ring_ref = temp2.add_ref(ramzi_1ring)
    st = straight(length=ramzi_1ring_ref.dxsize - coupler_length*2, cs=wg, gc=cs_gc_silicon_1550nm)
    ref = temp2.add_ref(st)
    ref.dymax, ref.dx = ramzi_1ring_ref.dymax - 40, ramzi_1ring_ref.dx

    ramzi_2rings_gsgsg = ramzi_dual_rings_gsgsg_gsgsg(
        wg=wg,
        pn_heater=pn_heater,
        pn_ring=pn_ring,
        mzi_heater=mzi_heater,
        radius=radius,
        gap=gap,
        int_angle=angle,
        arm_length=dual_ring_ramzi_arm_length,
        arm_distance=arm_distance,
        heater_length=heater_length,
        dist_pn_to_wg=dist_pn_to_wg,
        dist_y=dist_y,
        heater_percent=heater_percent
    )
    temp3 = gf.Component()
    ramzi_2rings_gsgsg_ref = temp3.add_ref(ramzi_2rings_gsgsg)
    st = straight(length=ramzi_2rings_gsgsg_ref.dxsize - coupler_length*2, cs=wg, gc=cs_gc_silicon_1550nm)
    ref = temp3.add_ref(st)
    ref.dymax, ref.dx = ramzi_2rings_gsgsg_ref.dymax - 40, ramzi_2rings_gsgsg_ref.dx

    ramzi_2rings_gsgsg_gssg = ramzi_dual_rings_gsgsg_gssg(
        wg=wg,
        pn_heater=pn_heater,
        pn_ring=pn_ring,
        mzi_heater=mzi_heater,
        radius=radius,
        gap=gap,
        int_angle=angle,
        arm_length=dual_ring_ramzi_arm_length,
        arm_distance=arm_distance,
        heater_length=heater_length,
        dist_pn_to_wg=dist_pn_to_wg,
        dist_y=dist_y,
        heater_percent=heater_percent
    )
    temp4 = gf.Component()
    ramzi_2rings_gsgsg_gssg_ref = temp4.add_ref(ramzi_2rings_gsgsg_gssg)
    st = straight(length=ramzi_2rings_gsgsg_ref.dxsize - coupler_length*2, cs=wg, gc=cs_gc_silicon_1550nm)
    ref = temp4.add_ref(st)
    ref.dymax, ref.dx = ramzi_2rings_gsgsg_gssg_ref.dymax - 40, ramzi_2rings_gsgsg_gssg_ref.dx

    xmax = 0
    for com in [temp1, temp2, temp3, temp4]:
        com_ref = c.add_ref(com)
        com_ref.dxmin = xmax + spacing
        com_ref.dymax = 0
        xmax = com_ref.dxmax

    c.flatten()
    
    return c

if __name__ == "__main__":
    wg = rib_450
    pn_heater = pn_450_with_metal_and_heater
    pn = pn_450_with_metal
    mzi_heater = filament
    arm_distance = 110
    angle = 20
    heater_length = 400
    one_ring_ramzi_arm_length = 500
    dual_ring_ramzi_arm_length = 850
    dist_to_wg = None
    dist_between_vias = 2.75
    heater_percent = 0.7
    singles_length = 550
    spacing = 30
    marker_spacing = 20
    dist_y = None

    design_vars = [
        (7, [0.2, 0.23, 0.25, 0.28, 0.3, 0.32], 0.7, 5.6),
        (10, [0.3, 0.35, 0.38, 0.4, 0.42, 0.45], 0.78, 0.79)
    ]
    r1, gap1, h1, dy1 = design_vars[0]
    r2, gap2, h2, dy2 = design_vars[1]

    c = gf.Component()
    ysizes = []
    ymin = 0
    for g1, g2 in zip(gap1, gap2):
        c1 = integrate_all_structures(
            wg=wg,
            pn_ring=pn,
            pn_heater=pn_heater,
            mzi_heater=mzi_heater,
            radius=r1,
            gap=g1,
            angle=angle,
            arm_distance=arm_distance,
            heater_length=heater_length,
            dist_pn_to_wg=dist_to_wg,
            dist_y=dy1,
            heater_percent=h1,
            one_ring_ramzi_arm_length=one_ring_ramzi_arm_length,
            dual_ring_ramzi_arm_length=dual_ring_ramzi_arm_length,
            singles_length=singles_length,
            spacing=spacing
        )
        c2 = integrate_all_structures(
            wg=wg,
            pn_ring=pn,
            pn_heater=pn_heater,
            mzi_heater=mzi_heater,
            radius=r2,
            gap=g2,
            angle=angle,
            arm_distance=arm_distance,
            heater_length=heater_length,
            dist_pn_to_wg=dy2,
            dist_y=dist_y,
            heater_percent=h2,
            one_ring_ramzi_arm_length=one_ring_ramzi_arm_length,
            dual_ring_ramzi_arm_length=dual_ring_ramzi_arm_length,
            singles_length=singles_length,
            spacing=spacing
        )

        c1_ref = c.add_ref(c1)
        c2_ref = c.add_ref(c2)
        c2_ref.dxmin = c1_ref.dxmax + spacing
        c1_ref.dymax = ymin - spacing
        c2_ref.dymax = c1_ref.dymax
        ymin = c.dymin
        ysizes.append(c.dysize)

    # place the marker to the left and right of it
    marker = dice_marker(layer=LAYER.METAL)
    xmin, xmax = c.dxmin, c.dxmax
    ymax = c.dymax
    ysizes.insert(0, 0)
    for i, ysize in enumerate(ysizes):
        marker1_ref, marker2_ref = [c.add_ref(marker) for _ in range(2)]
        marker1_ref.dxmax = xmin - marker_spacing
        marker2_ref.dxmin = xmax + marker_spacing
        marker1_ref.dymin = ymax + marker_spacing if i == 0 else ymax + marker_spacing - ysize - spacing
        marker2_ref.dymin = marker1_ref.dymin

    c.show()


