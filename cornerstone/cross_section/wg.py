from functools import partial

from gdsfactory.cross_section import cross_section
from cornerstone.cross_section import Spec
from cornerstone import LAYER

rib = partial(
    cross_section,
    offset=0,
    radius_min=Spec.r_min,
    layer=LAYER.WG,
    cladding_layers=(LAYER.RIB_PROTECT,),
    cladding_offsets=(Spec.c_ext,),
)

rib_450 = partial(
    rib,
    width=0.45
)