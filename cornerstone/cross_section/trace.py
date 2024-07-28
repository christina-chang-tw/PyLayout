from functools import partial

from gdsfactory.cross_section import cross_section
from cornerstone.cross_section import CornerstoneSpec
from cornerstone import LAYER

metal = partial(
    cross_section,
    offset=0,
    radius_min=CornerstoneSpec.r_min,
    port_names=("e1", "e2"),
    port_types=("electrical", "electrical"),
)

filament = partial(
    cross_section,
    offset=0,
    radius_min=CornerstoneSpec.r_min,
    layer=LAYER.FILAMENT,
    port_names=("e1", "e2"),
    port_types=("electrical", "electrical"),
)

metal_trace = metal(width=80, layer=LAYER.METAL)
