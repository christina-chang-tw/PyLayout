from dataclasses import dataclass

from gdsfactory.typings import Layer

@dataclass
class SOI_220nm:
    """
    Cornerstone SOI run layer definition
    """
    ETCH1: Layer = (6, 0)
    ETCH2_L: Layer = (3, 0) # Si etch 2 light
    ETCH2_D: Layer = (4, 0) # Si etch 2 dark
    ETCH3: Layer = (5, 0)
    FILAMENTS: Layer = (39, 0)
    PADS: Layer = (41, 0)
    OUTLINE: Layer = (99, 0)
    LABELS: Layer = (100, 0)

@dataclass
class SiN:
    """
    Cornerstone SiN run layer definition
    """
    ETCH1_L: Layer = (203, 0) # Si etch 1 light
    ETCH1_D: Layer = (204, 0) # Si etch 1 dark
    FILAMENTS: Layer = (39, 0)
    PADS: Layer = (41, 0)
    OUTLINE: Layer = (99, 0)
    LABELS: Layer = (100, 0)
    CLADDING: Layer = (22, 0) # cladding opening dark

@dataclass
class GOS:
    """
    Cornerstone Ge-on-Si run layer definition
    """
    BLEED: Layer = (98, 0)
    ETCH1_L: Layer = (303, 0) # Ge etch 1 light
    ETCH1_D: Layer = (304, 0) # Ge etch 1 dark
    OUTLINE: Layer = (99, 0)
    LABELS: Layer = (100, 0)

@dataclass
class Si_Suspended:
    """
    Cornerstone suspended Si run layer definition
    """
    ETCH1: Layer = (404, 0) # suspended Si etch 1
    OUTLINE: Layer = (99, 0)
    LABELS: Layer = (100, 0)

@dataclass
class SOI_340nm:
    """
    Cornerstone SOI run layer definition
    """
    ETCH1: Layer = (6, 0)
    ETCH2_L: Layer = (3, 0)
    ETCH2_D: Layer = (4, 0)
    FILAMENTS: Layer = (39, 0)
    PADS: Layer = (41, 0)
    OUTLINE: Layer = (99, 0)
    LABELS: Layer = (100, 0)