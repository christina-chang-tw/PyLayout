import numpy as np
rng = np.random.default_rng()

from designs.test_structures.bends import bend_loss, bend_loss_pn
from designs.test_structures.coupling import cross_coupling
from designs.test_structures.dummy import dummy_waveguide
from designs.test_structures.pnring import single_ring_pn
from designs.test_structures.pnring_with_heater import ring_metal_heater_distance, single_ring_heater_gsgsg, single_ring_heater_gs, single_ring_heater_gssg
from designs.test_structures.straight_with_heater import straight_with_heater
from designs.test_structures.straight import straight