from functools import partial
import numpy as np

from gdsfactory.cross_section import cross_section, Section
import gdsfactory as gf

from pylayout.components import ring, attach_grating_coupler, gc_silicon_1550nm
from cornerstone import Spec, LAYER, cs_gc_silicon_1550nm

def main():
    radius = 5
    max_length = 675
    width = 0.45
    
    step = 0.005
    
    gap_dict = {
        4.5: [18, np.arange(0.2, 0.32 + step, step)],
        5: [18, np.arange(0.2, 0.32 + step, step)],
        6: [18, np.arange(0.2, 0.32 + step, step)],
        7: [18, np.arange(0.278, 0.398 + step, step)],
        8: [18, np.arange(0.308, 0.428 + step, step)],
        9: [18, np.arange(0.338, 0.458 + step, step)],
        10: [18, np.arange(0.378, 0.498 + step, step)],
    }
    
    diameter = [20]
    radius = np.array(diameter) / 2
    
    wg = partial(
        cross_section,
        width=width,
        offset=0,
        radius_min=Spec.r_min,
        layer=LAYER.WG,
        cladding_layers=(LAYER.WG_ETCH,),
        cladding_offsets=(5.5,),
    )
    
    grating_coupler = partial(
        gc_silicon_1550nm,
        layer_trench=LAYER.GRATING,
        cross_section=wg
    )
    
    cladding_width = 8
    
    
    ring_lists = []
    for radii in radius:
        angle, gaps = gap_dict[radii]
        gaps = list(reversed(np.round(gaps, 4)))
        for gap in gaps:
            ring_wg = partial(
                cross_section,
                width=0.45,
                offset=0,
                radius_min=Spec.r_min,
                layer=LAYER.WG,
                sections=[
                    Section(
                        width=radii,
                        offset= -radii/2,
                        layer=LAYER.WG_ETCH
                    ),
                    Section(
                        name="ring",
                        width=cladding_width + width/2,
                        offset=(cladding_width + width/2) /2,
                        layer=LAYER.WG_ETCH
                    ),
                ]
            )
            
            c = ring(
                wg=wg,
                ring_wg=ring_wg,
                radius=radii,
                gap=gap,
                int_angle=angle,
                max_length=max_length,
                cladding_rfill=True,
            )
            
            
            c = attach_grating_coupler(c, grating_coupler, ["o1", "o2"])
            base = gf.Component()
            c_ref = base.add_ref(c)
            c_ref.drotate(90)
            ring_lists.append(base)
        
    ring_lists = list(reversed(ring_lists))
    c = gf.grid(
        ring_lists,
        shape=(len(radius), len(gaps)),
        spacing = (101, 290),
        align_x="xmin",
    )
    
    c.show()
    
if __name__ == "__main__":
    main()