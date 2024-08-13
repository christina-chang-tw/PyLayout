from pathlib import Path

import gdsfactory as gf
from gdsfactory.technology import (
    LayerLevel,
    LayerMap,
    LayerStack,
    LogicalLayer,
)
from gdsfactory.typings import Layer


class LayerMapCornerstone(LayerMap):

    WG: Layer=(3,0)
    WG_ETCH: Layer=(4,0)
    RIB_PROTECT: Layer=(5,0) # extend at least 5um out from WG
    GRATING: Layer=(6,0)
    SI_ETCH2_PROTECT: Layer=(61,0)
    SI_ETCH4: Layer=(42,0)
    SI_ETCH5: Layer=(60,0)

    # Dopings
    LOW_P: Layer=(7,0)
    LOW_N: Layer=(8,0)
    HIGH_P: Layer=(9,0)
    HIGH_N: Layer=(11,0)

    VIA: Layer=(12,0)
    METAL: Layer=(13,0)
    FILAMENT: Layer=(39,0)
    HEATER_PAD: Layer=(41,0)

    OUTLINE: Layer=(99,0)
    LABELS: Layer=(100,0)

    SIN_ETCH1_L: Layer=(203,0)
    SIN_ETCH1_D: Layer=(204,0)
    GE_ETCH1_L: Layer=(303,0)
    GE_ETCH1_D: Layer=(304,0)
    SI_SUSPENDED: Layer=(404,0)

    BLANK: Layer=(0,0)

LAYER = LayerMapCornerstone

def get_layer_stack(
    thickness_wg: float = 220E-03,
    thickness_slab: float = 100E-03,
    zmin_heater: float = 1.1,
    thickness_heater: float = 700E-03,
    zmin_metal: float = 1.1,
    thickness_metal: float = 700E-03,
) -> LayerStack:
    """Returns LayerStack.

    based on paper https://www.degruyter.com/document/doi/10.1515/nanoph-2013-0034/html

    Args:
        thickness_wg: waveguide thickness in um.
        thickness_slab: slab thickness in um.
        zmin_heater: TiN heater.
        thickness_heater: TiN thickness.
        zmin_metal: metal thickness in um.
        thickness_metal: metal2 thickness.
    """

    return LayerStack(
        layers=dict(
            core=LayerLevel(
                layer=LogicalLayer(layer=LAYER.WG),
                thickness=thickness_wg,
                zmin=0.0,
                material="si",
                info={"mesh_order": 1},
                sidewall_angle=10,
                width_to_z=0.5,
            ),
            slab=LayerLevel(
                layer=LogicalLayer(layer=LAYER.RIB_PROTECT),
                thickness=thickness_slab,
                zmin=0.0,
                material="si",
                info={"mesh_order": 1},
                sidewall_angle=10,
                width_to_z=0.5,
            ),
            heater=LayerLevel(
                layer=LogicalLayer(layer=LAYER.FILAMENT),
                thickness=thickness_heater,
                zmin=zmin_heater,
                material="TiN",
                info={"mesh_order": 1},
            ),
            metal=LayerLevel(
                layer=LogicalLayer(layer=LAYER.METAL),
                thickness=thickness_metal,
                zmin=zmin_metal + thickness_metal,
                material="Aluminum",
                info={"mesh_order": 2},
            ),
        )
    )


LAYER_STACK = get_layer_stack()
LAYER_VIEWS = gf.technology.LayerViews(f"{Path().absolute()}/cornerstone/layers.yaml")


class Tech:
    radius_sc = 5
    radius_so = 5
    radius_rc = 25
    radius_ro = 25
    width_sc = 0.45
    width_so = 0.40
    width_rc = 0.45
    width_ro = 0.40


TECH = Tech()