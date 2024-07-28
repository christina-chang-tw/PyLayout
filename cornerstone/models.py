from os.path import dirname
from pathlib import Path
from functools import partial

import gdsfactory as gf

from pylayout.components import gc_silicon_1550nm

from cornerstone.layer import LAYER
from cornerstone.cross_section import rib, CornerstoneSpec

GDS_PATH = Path(dirname(__file__)) / 'GDSII_2022.gds'

add_ports_optical = partial(
    gf.add_ports.add_ports_from_markers_inside, pin_layer=(3,0), port_layer=(3,0)
)
add_ports = gf.compose(add_ports_optical)
import_gds = partial(gf.import_gds, post_process=add_ports)

@gf.cell
def SOI220nm_1550nm_TE_MZI_Modulator() -> gf.Component:
    return gf.import_gds(GDS_PATH, cellname='SOI220nm_1550nm_TE_MZI_Modulator')

@gf.cell
def SOI220nm_1550nm_TE_RIB_2x1_MMI() -> gf.Component:
    c = gf.import_gds(GDS_PATH, cellname='SOI220nm_1550nm_TE_RIB_2x1_MMI')
    x, y = c.dx, c.dy
    length = 92.7
    sep = 2.69
    wg_width = 0.45
    c.add_port(name='o1', center=(x+length/2, y), width=wg_width, orientation=0, layer=LAYER.WG)
    c.add_port(name='o2', center=(x-length/2, y+(sep+wg_width)/2), width=wg_width, orientation=180, layer=LAYER.WG)
    c.add_port(name='o3', center=(x-length/2, y-(sep+wg_width)/2), width=wg_width, orientation=180, layer=LAYER.WG)
    return c

@gf.cell
def SOI220nm_1550nm_TE_RIB_2x2_MMI() -> gf.Component:
    c = gf.import_gds(GDS_PATH, cellname='SOI220nm_1550nm_TE_RIB_2x2_MMI')
    x, y = c.dx, c.dy
    length = 104.8
    sep = 1.58
    wg_width = 0.45
    c.add_port(name='o1', center=(x-length/2, y+(sep+wg_width)/2), width=wg_width, orientation=180, layer=LAYER.WG)
    c.add_port(name='o2', center=(x-length/2, y-(sep-wg_width)/2), width=wg_width, orientation=180, layer=LAYER.WG)
    c.add_port(name='o3', center=(x+length/2, y-(sep+wg_width)/2), width=wg_width, orientation=0, layer=LAYER.WG)
    c.add_port(name='o4', center=(x+length/2, y+(sep-wg_width)/2), width=wg_width, orientation=0, layer=LAYER.WG)
    return c

@gf.cell
def SOI220nm_1550nm_TE_RIB_90_Degree_Bend() -> gf.Component:
    return gf.import_gds(GDS_PATH, cellname='SOI220nm_1550nm_TE_RIB_90_Degree_Bend')

@gf.cell
def SOI220nm_1550nm_TE_RIB_Waveguide() -> gf.Component:
    return gf.import_gds(GDS_PATH, cellname='SOI220nm_1550nm_TE_RIB_Waveguide')

@gf.cell
def SOI220nm_1550nm_TE_RIB_Waveguide_Crossing() -> gf.Component:
    return gf.import_gds(GDS_PATH, cellname='SOI220nm_1550nm_TE_RIB_Waveguide_Crossing')

@gf.cell
def SOI220nm_1550nm_TE_STRIP_2x1_MMI() -> gf.Component:
    return gf.import_gds(GDS_PATH, cellname='SOI220nm_1550nm_TE_STRIP_2x1_MMI')

@gf.cell
def SOI220nm_1550nm_TE_STRIP_2x2_MMI() -> gf.Component:
    return gf.import_gds(GDS_PATH, cellname='SOI220nm_1550nm_TE_STRIP_2x2_MMI')

@gf.cell
def SOI220nm_1550nm_TE_RIB_Grating_Coupler() -> gf.Component:
    c = gf.import_gds(GDS_PATH, cellname='SOI220nm_1550nm_TE_RIB_Grating_Coupler')
    c.add_port(name='o1', center=(c.dxmax, c.dy), width=0.45, orientation=0, layer=LAYER.WG)
    return c

@gf.cell
def SOI220nm_1550nm_TE_STRIP_90_Degree_Bend() -> gf.Component:
    return gf.import_gds(GDS_PATH, cellname='SOI220nm_1550nm_TE_STRIP_90_Degree_Bend')

@gf.cell
def SOI220nm_1550nm_TE_STRIP_Waveguide() -> gf.Component:
    return gf.import_gds(GDS_PATH, cellname='SOI220nm_1550nm_TE_STRIP_Waveguide')

@gf.cell
def SOI220nm_1550nm_TE_STRIP_Waveguide_Crossing() -> gf.Component:
    return gf.import_gds(GDS_PATH, cellname='SOI220nm_1550nm_TE_STRIP_Waveguide_Crossing')

@gf.cell
def SOI220nm_1550nm_TE_STRIP_Grating_Coupler() -> gf.Component:
    c = gf.import_gds(GDS_PATH, cellname='SOI220nm_1550nm_TE_STRIP_Grating_Coupler')
    
    length = 392.0
    width = 10.0
    wg_width = 0.45
    c.add_port(name='o1', center=(c.dx+length/2, c.dy), width=wg_width, orientation=180, layer=LAYER.WG)
    c.add_port(name='o2', center=(c.dx-length/2, c.dy), width=width, orientation=0, layer=LAYER.WG)

    return c

@gf.cell
def SOI220nm_1550nm_TM_STRIP_Grating_Coupler() -> gf.Component:
    return import_gds(GDS_PATH, cellname='SOI220nm_1550nm_TM_STRIP_Grating_Coupler')


cs_gc_silicon_1550nm = partial(
    gc_silicon_1550nm,
    layer_trench=LAYER.GRATING,
    cross_section=rib(width=0.45),
    cladding_cross_section=rib(
        width=0.45 + CornerstoneSpec.c_ext*2,
        layer=LAYER.RIB_PROTECT,
    )
)