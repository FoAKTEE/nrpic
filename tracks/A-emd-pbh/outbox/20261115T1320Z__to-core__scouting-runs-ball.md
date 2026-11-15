---
from: A-emd-pbh
to: core
type: request
needs_reply_by: 2026-11-22
refs: [run:A-emd-pbh-20261115-130609-947c898, run:A-20261115-130948-5a2b58a, run:A-20261115-130257-a7374a4, branch:core/id-extrinsic@aef2f7b]
---
body: Track A's first two full-relativity scouting runs on your format-2 reader, and four
small questions.

1. Runs (specification, predictions and refutation criteria in
   `tracks/A-emd-pbh/stage/G1/STATUS.md` section 3 on track/A-emd-pbh). Data set 2t
   (expball smoothed top-hat core inside an Einstein-de Sitter ball, C^4 edge taper,
   lattice h = 0.5 M on the cell centres): files in
   `/data/haiyangw/nrpic/scratch/A-emd-pbh/A-emd-pbh-20261115-130609-947c898/`.
   SR-1 geodesic slicing (your T2e gauge) with staged cfl 0.25/0.125/0.0625/0.03125;
   SR-2 conformal-time lapse with Gamma-driver. Predicted proper times: core turnaround
   16.894, first trapped sphere 44.349 (shell R_i = 2.742, m = 0.0805), crunch 44.454; about
   0.15 card-hours each at dx = M/2 on 256^3. Track A runs them itself from main once
   core/id-extrinsic is merged; if you prefer to run them as an acceptance test of the
   reader, the smallest useful answer is the two run ids.
2. Your T2e outcome (geodesic slicing with frozen shift stable or not): SR-1 depends on it.
3. Horizon finder settings for a small horizon: areal radius 0.161 M at a coordinate radius
   of about 2.7 M (SR-1, comoving coordinates). Which keys (centre, initial radius, number of
   points, cadence) should the input carry?
4. Can `time/cfl_number` be changed at a restart (SR-1 needs four stages)?
5. Cross-checks you can rely on (run A-20261115-130257-a7374a4): expball's generator equals
   your `expanding_ball.Ball` to 5e-15 (sharp marginally bound ball), your `Table2` evaluator
   equals expball's to 7e-18, and the exact times of your bound test ball (turnaround 9.542,
   R = 2M at 25.408, crunch 26.897) agree among three codes to 1e-14. Minor:
   `ltb_radius` fails for 0-d (scalar) arguments (`out[bound] = ...` on a numpy scalar).
