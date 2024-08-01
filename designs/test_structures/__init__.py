import numpy as np
rng = np.random.default_rng()

from designs.test_structures.bends import bend_loss, bend_loss_pn
from designs.test_structures.coupling import cross_coupling
from designs.test_structures.dummy import dummy_waveguide
from designs.test_structures.pnring import single_ring_pn
from designs.test_structures.pnring_with_filament import single_ring_filament_gssg, single_ring_filament_gs, single_ring_filament_gsgsg
from designs.test_structures.straight_with_filament import waveguide_with_filament
from designs.test_structures.straight import straight
from designs.test_structures.pnring_with_mzi_filament import ring_and_mzi_heater