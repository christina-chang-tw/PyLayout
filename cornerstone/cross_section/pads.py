from functools import partial

import gdsfactory as gf

from pylayout.cross_section import MSpec
from cornerstone import LAYER

metal_pad = partial(
    gf.components.pad,
    size=(MSpec.pad_width, MSpec.pad_height),
    layer=LAYER.METAL,
)

heater_pad = partial(
    gf.components.pad,
    size=(MSpec.pad_width, MSpec.pad_height),
    layer=LAYER.HEATER_PAD,
)

metal_pad_array = partial(
    gf.components.array,
    component=metal_pad(),
    spacing=(MSpec.pad_width, MSpec.pad_height),
    rows=1,
    centered=True,
)

heater_pad_array = partial(
    gf.components.array,
    component=heater_pad(),
    spacing=(MSpec.pad_spacing, MSpec.pad_spacing),
    rows=1,
    centered=True,
)
