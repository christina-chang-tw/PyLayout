from pylayout.components import straight_with_heater
from cornerstone import (
    rib_450,
    filament,
    metal_trace,
    CornerstoneSpec
)


c = straight_with_heater(500, rib_450, filament(width=CornerstoneSpec.mzi_heater_width), metal_trace)
c.show()