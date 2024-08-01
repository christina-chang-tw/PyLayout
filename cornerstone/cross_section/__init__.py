import yaml
import os
from pathlib import Path

from dataclasses import dataclass
from pylayout.cross_section import CrossSectionSpecs

# default to the cs_spec.yml
filepath = os.curdir / Path(r'cornerstone/cross_section/cs_spec.yml')
with open(filepath, 'r', encoding="utf-8") as f:
    data = yaml.load(f, Loader=yaml.FullLoader)
Spec = CrossSectionSpecs(**data)

from .heater import heater, heater_450
from .pads import metal_pad, heater_pad
from .pn import pn, pn_450_with_metal_and_heater, pn_450_with_heater, pn_450_with_metal
from .trace import metal, filament
from .wg import rib, rib_450
