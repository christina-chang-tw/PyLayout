from functools import partial

from gdsfactory.cross_section import cross_section
from cornerstone.cross_section import Spec
from cornerstone import LAYER

metal = partial(
    cross_section,
    offset=0,
    radius_min=Spec.r_min,
    port_names=("e1", "e2"),
    port_types=("electrical", "electrical"),
    layer=LAYER.METAL,
)

filament = partial(
    cross_section,
    width=Spec.mzi_heater_width,
    offset=0,
    radius_min=Spec.r_min,
    layer=LAYER.FILAMENT,
    port_names=("e1", "e2"),
    port_types=("electrical", "electrical"),
)
