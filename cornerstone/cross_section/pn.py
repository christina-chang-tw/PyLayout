from functools import partial

from pylayout.cross_section import _pn
from cornerstone.cross_section import Spec
from cornerstone import LAYER

pn = partial(
    _pn,
    layer=LAYER.WG,
    layer_slab=LAYER.RIB_PROTECT,
    gap_medium_doping=Spec.medium_doped_gap,
    gap_medium_to_via=Spec.medium_to_via_gap,
    width_low_doping=Spec.low_doped_width,
    width_slab=Spec.slab_width,
    layer_p=LAYER.LOW_P,
    layer_pp=LAYER.HIGH_P,
    layer_n=LAYER.LOW_N,
    layer_np=LAYER.HIGH_N,
    width_via=Spec.via_width,
    gap_metal_to_via=Spec.metal_to_via_gap,
)

pn_450_with_metal_and_heater = partial(
    pn,
    width=0.45,
    layer_heater=LAYER.FILAMENT,
    layer_heater_pad=LAYER.METAL,
    width_heater=Spec.ring_heater_width,
    layer_metal=LAYER.METAL,
    layer_via=LAYER.VIA,
    via_min_distance=Spec.min_via_distance
)

pn_450_with_heater = partial(
    pn,
    width=0.45,
    layer_heater=LAYER.FILAMENT,
    width_heater=Spec.ring_heater_width,
    via_min_distance=Spec.min_via_distance,
)

pn_450_with_metal = partial(
    pn,
    width=0.45,
    layer_metal=LAYER.METAL,
    layer_via=LAYER.VIA,
    via_min_distance=Spec.min_via_distance
)