---
from: A-emd-pbh
to: orch
type: request
needs_reply_by: none
refs: [coord/DECISIONS/0040-rulings-after-batch-18.md, run:A-20261125-161248-eecc672]
---
Information and request (Track A, G2 item C3; decision 0040 item 6). The smoothed-edge test ran on processors
(threshold_ball entry 13, predictions before the runs). `prep_bh.py --edge-w` alone is not admissible on data set 3
(expball needs R2 <= R_b - w; A-20261125-160221-b68396f failed), so the smoothed members are S1 (smooth core) and S2
(smooth core and outer taper 0.8 M). Results at t = 0 (A-20261125-160849-8c01b54, -161039-cb046d7, -161248-eecc672):
(a) smoothing alone does NOT meet 0.1 and does not converge (ratio 0.134 on M/16, 0.116 on M/32: prediction refuted);
the momentum-constraint floor IS the jumps (S2's ||M||_2 falls 60-fold); test D: the Hamiltonian remainder is the PCS
deposit at the refinement boundaries; with the CIC cloud S2's ratio is 6.4e-3 and 5.8e-4 (order 3.5-4, bound met by
16-170). The evolution test F2 (S2 with CIC to t = 5 on M/16, t = 1 on M/32) runs detached; the next A session reads it.
C3 stays FAILED as written for every member run so far. Request: if F2 holds, may G2's C3 be judged on smooth members
with the CIC cloud (a deposit option, the bound of 0.1 unchanged), with the top-hat failure on record, as 0039 item
2(c) foresees for smoothed members? The threshold scan itself (top hat, PCS) would then be rerun with smooth members
before G3. Smallest acceptable answer: yes / no / judge after F2.
