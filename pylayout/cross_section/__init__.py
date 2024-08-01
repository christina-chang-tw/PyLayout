from .pn import _pn
from .heater import _heater

from dataclasses import dataclass

@dataclass
class CrossSectionSpecs:
    # waveguide definition
    c_ext: float # cladding extrusion
    r_min: float # minimum radius
    slab_width: float
    # low/medium doping definition
    low_doped_width: float
    medium_doped_width: float
    medium_doped_gap: float
    # via/metal definition
    medium_to_via_gap: float
    via_width: float
    metal_to_via_gap: float
    metal_trace_width: float
    min_via_distance: float

    # heater definition
    mzi_heater_width: float
    ring_heater_width: float


@dataclass
class MetalSpecs:
    pad_width: float = 75
    pad_height: float = 75
    pad_spacing: float = 100

import yaml
import os
from pathlib import Path

with open(os.curdir / Path(r'specs/metal.yml'), 'r', encoding="utf-8") as f:
    data = yaml.safe_load(f)

MSpec = MetalSpecs(**data)