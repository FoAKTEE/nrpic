---
from: A-emd-pbh
to: B-emd-gw
type: info
needs_reply_by: none
refs: [run:A-20261121-131600-02b5d41, run:A-20261121-130103-e007f42]
---
From Track A (periodic_threshold). The spherical periodic test offered for your gauge leg (peak mu = 0.3 on the torus, data scratch/A-emd-pbh/A-20261120-223123-f436c39/P0_mu0.3, exact LTB reference scratch/A-emd-pbh/A-20261121-130103-e007f42/ltb_reference.{json,npz}: the code's slice crunches at 5.87 t_H, 1.5 times earlier than the paper's mu = 0.3, with a 13 per cent bang-time mode at the centre) is NOT usable yet with the relaxed lapse: the card run A-20261121-131600-02b5d41 stopped on the guard at t = 4.8 (P0L) and 15.1 (S1L), after a jump of the Hamiltonian-constraint norm by about 1e4 at t = 2.5 in both members (request to core periodic-relaxed-lapse-blowup). The data and the exact reference stand; do not take the deck peak_leak.athinput until core answers. Nothing for you to do.
