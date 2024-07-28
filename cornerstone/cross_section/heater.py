from functools import partial

from pylayout.cross_section import _heater
from cornerstone.cross_section import CornerstoneSpec
from cornerstone import LAYER

heater = partial(
    _heater,
    layer=LAYER.WG,
    layer_slab=LAYER.RIB_PROTECT,
    layer_heater=LAYER.FILAMENT,
    width_heater=CornerstoneSpec.mzi_heater_width,
    width_slab=CornerstoneSpec.slab_width
)

heater_450 = partial(
    heater,
    width=0.45,
)