from pylayout.components import ring

from cornerstone import (
    pn_450_with_metal
)

c = ring(pn=pn_450_with_metal, int_angle = 20, metal_layer=(13, 0))
c.show()