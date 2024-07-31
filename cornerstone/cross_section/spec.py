from dataclasses import dataclass

@dataclass
class CornerstoneSpec:
    # waveguide definition
    c_ext: float = 5 # cladding extrusion
    r_min: float = 3 # minimum radius
    slab_width: float = 2 * c_ext + 0.45
    # low/medium doping definition
    low_doped_width: float = 12
    medium_doped_width: float = 8.8
    medium_doped_gap: float = 1.12
    # via/metal definition
    medium_to_via_gap: float = 1.475
    via_width: float = 5
    metal_to_via_gap: float = 0.5
    metal_trace_width: float = 7
    min_via_distance: float = 3.15

    # heater definition
    mzi_heater_width: float = 4
    ring_heater_width: float = 2.5