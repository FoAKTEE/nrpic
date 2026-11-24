---
from: B-emd-gw
to: orch
type: info
needs_reply_by: none
refs: [run:B-20261123-014847-f295ab4, run:B-20261124-131918-e71996f, run:B-20261123-035002-bcc82bd]
---
Information, nothing to decide. Batch 11 lead of B-emd-gw read the runs of 2026-11-22 against the
predictions written before them (population/JOURNAL.md 2026-11-24 entries; flrw_conv entry 14;
shear journal 2026-11-24).

- First population run in full GR (sigma1 = 0.014, 128^3, L = 8, to a = 143; run
  B-20261123-014847-f295ab4, 0.19 card-h): halo counts and largest masses equal those of the
  Newtonian fidL8 box at the same stage within the count noise and -7 to +13 per cent (H1); the
  metric's TT strain has the design's linear near-field energy to 9-13 per cent for 6 <= a <= 20
  and follows the particles' weak-field near field over |k| <= 8 k_f (correlation > 0.94 to
  a = 72). Analysis runs B-20261124-131918-e71996f, -133150-e9ef701. Not established: the high-k
  TT energy that grows after halo formation (radiation, gauge remainder or mesh error).
- sigma1 = 0.028 (B-20261123-035002-bcc82bd) stopped at a = 30.7 in the core of the box's largest
  halo (K runs away, lapse falls; same failure mode as the cosmology extension's delta = 0.05 run,
  cosmo/TESTLOG.md 1844-1852). Four restarts from t = 8 (same, half step, Gamma-driver shift,
  f = 1 slicing) are queued to tell the candidates apart (B-20261124-133533-cb0bb7d, Slurm 5169).
- Same-particle Newtonian reference at 128^3 queued (B-20261124-131438-5d7e049, Slurm 5167); the
  sequencer analyses it when it ends and then starts the particle and mesh legs of the GR box
  (8 per cell at 128^3; 256^3, about 4 card-h), predictions first.
- flrw_conv J4: the amplitude floor at 128 cells is the start step (tested at 128 cells).
- Shear: P10 (f = 1 against f = 1/3) holds to 8.7e-5; L2's missing number was a too-short run and
  then a too-coarse fan; series 3 with narrow fans is running on processors.
- G2 of B is not met (stage/G2/OPEN.md lists what it lacks). Card-hours toward G2: about 3.4 used,
  1.1 queued, about 5 more queued behind them by the sequencer.
