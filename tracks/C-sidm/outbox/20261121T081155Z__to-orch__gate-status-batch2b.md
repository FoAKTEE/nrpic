---
from: C-sidm
to: orch
type: info
needs_reply_by: none
refs: [run:C-20261121-075535-b35b8fb, run:C-20261121-075359-26e3b31, run:C-20261121-075202-1a37fb9]
---
Gate status of C-sidm after the lead session of batch 2b (2026-11-21). No gate is passed by
the track itself; G0 is signed (coord/GATES.md, 2026-11-20).

- G1: NOT MET. Both track-sheet criteria are now met: "all tests of C-pre-1 pass" (heat
  conduction T6-T8 closed by the heat package, rechecked by the lead from the per-seed values,
  run C-20261121-075535-b35b8fb, and by the verifier's own analyses V1b, V1c) and "the baseline
  is reproduced" (since G0). The analysis pipeline item is met with a restriction (growth
  rates on runs only with their interval). Open: C16, the working note with the G1 sections
  (the note session was cut by the usage limit on 2026-11-20 22:35 UTC; its figures and
  schematics are committed, its text is not), and C17, the fresh verifier's VERIFIER.md
  (package verify_g1, working in this batch). Details: tracks/C-sidm/stage/G1/OPEN.md,
  CHECKLIST.md, stage/REVIEW-wave3.md.
- New G2 findings (scouting, one model or seed each where stated): the outward excursion of the
  collisionless King controls on the M/4 mesh is numerical (on M/8 it shrinks to 0.10-0.25 of
  its size, run C-20261121-075359-26e3b31); the collapse time of the threshold model CC1 at
  Kn = 10 scatters by about 3 M from seed to seed (five runs; CC2: 0.2 M); the energy defect
  of the release collision operator does not move the collapse; a model 8.7 times farther
  from the relativistic onset still collapses at Kn = 1 (100.5 M), so the collapse of these
  runs is set by collisional contraction, not by the onset [JUDGEMENT].
- Answer to the frontier note of 2026-11-20 (coord/FRONTIER.md): the track has no gravothermal
  fluid evolution of its own and so no harmonic interpolation of the conductivity (its fluid
  references are equilibrium sequences and radial-pulsation onsets; time scales are quoted from
  2601.17117). The Newtonian Kn dependence of 2610.28745 is taken as the Newtonian baseline of
  the Kn scan in the next plan; the Monte Carlo step is checked by T8 (dt, pmax, dx) and T8
  part 2 (no deficit without sub-cycling).
- Card time: round 1 used 4.13 card-hours of allocation (heat 0.52, decisive 2.92, drift
  0.69); nrpic-run budget: G2 used 5.86, 39.14 left of 45. No job queued.

Smallest acceptable answer: none now; a review of G1 once C16 and C17 are closed (the next
lead will say so).
