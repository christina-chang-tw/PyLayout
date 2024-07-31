import gdsfactory as gf

c = gf.Component()

mmi = gf.components.mmi2x2(width_mmi=10, gap_mmi=3)
mmi1 = c.create_vinst(mmi)  # create a virtual instance
mmi2 = c.create_vinst(mmi)  # create a virtual instance

mmi2.dmove((100, 10))
mmi2.drotate(30)

routes = gf.routing.route_bundle_all_angle(
    c,
    mmi1.ports.filter(orientation=0),
    [mmi2.ports["o2"], mmi2.ports["o1"]],
)
c.show()
c