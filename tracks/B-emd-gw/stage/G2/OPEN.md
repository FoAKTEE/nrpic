# What G2 of B-emd-gw still lacks (batch 34, 2026-11-27 15:35 PST)

Batch 34 ran and judged the two runs decision 0046 item 2 requires before G2, and the GM analysis:
- C1 (0046 2a): shearing dust without stream crossing at N_y = 64, 128, 256 (series 7,
  B-20261126-222544-f3a5176, judged by B-20261126-230056-294b265; shear/JOURNAL 2026-11-26 15:02):
  no crossing before t_A (N7a holds), Delta converges in the mesh (ratio of differences 0.40, finest
  minus Richardson -1.4e-5; N7b Delta part holds), value +0.0538 (N7c holds). L2 as run stays FAILED
  on record. Open beside it: the constraint floor of series 7 (Mr 1.6e-4 not falling between
  N_y = 128 and 256; N7b constraint part failed as written, cause not named).
- C3 (0046 2b): the 64^3 member at eight per cell (q0070, B-20261127-232258-37c6773, judged by
  B-20261127-232628-1361e3b; population/JOURNAL 2026-11-27 15:28): Hr_mean 64/128 1.64-2.34 after
  a = 36 and never below 1.2 at a >= 49 (C3a not refuted; fails as written before a = 31, 1.32 at
  a = 25); Mr_mean 64/128 1.71-2.16 at a = 49-139 (C3b holds). M4, GM4 stay FAILED on record.
- C2, C11 (GM2, GM3; B-20261127-232236-7ab7aa2, population/JOURNAL 2026-11-27 15:24): band strain
  256^3/128^3 in the Gamma-driver gauge within 1.1 per cent to a = 64 and 2.8 per cent to a = 132
  (GM2 band part holds); Omega over all shells 0.85 at a = 121 (predicted 1.0-2.0, not refuted:
  fails as written); halo counts below the 128^3 catalogue at every epoch, outside the band at
  a = 121, largest mass 1.32 and 1.13 at a = 64, 121 (GM3 fails in part).

| Item | State (CHECKLIST.md) | What remains |
|---|---|---|
| C1 | PASS under 0046 2(a); L2 as run FAILED on record | ruling of the gate review on the series-7 constraint floor |
| C2 | PASS for the strain the track reads; GM3 halo counts FAILED in part on record | ruling: the halo catalogue is not mesh-converged at one particle per cell (both gauges); G3 runs at eight per cell |
| C3 | PASS under 0046 2(b) and 0039 2(c); M4, GM4, C3a early part FAILED on record | caveat: the 64/128 pair sits at coarser spacing than 128/256 |
| C5 | PASS (STAGE_REPORT + EVIDENCE + OPEN) | none |
| C11 | PASS | none |
| C17 | PASS (note v4, checker, compile) | none |
| C18 | OPEN | a fresh-context verifier (requested from the orchestrator) |

Failures on record (no further run needed): X3 (setup error), the time part of GD1 and of N1p, the
particle leg's chain cut at a = 94.8; N4 as written (cause found), GN2 after a = 36, NB1, VC1 second
part, VC2 side statements, the defective first band run; M1 (B-20261125-093500-242d3a3 closed
failed), M4, GN1 of batch 21 withdrawn, the slip a' = 4a in S2/S3; GM4 first part, M2 largest masses
at a = 64-72, M3 first part at a = 100, Q1 high-k part; batch 29: the series-7 design claim "no
crossing before tlim" and N7b constraint part, the C3 step-1 wall-time expectation; batch 34: GM2
Omega part, GM3 counts at a = 121 and largest masses at a = 64, 121, C3a before a = 31, the step-1
wall time (61 min against 30-60).

What the fresh verifier should recompute first (C18): (1) C3 from the two cstat histories
(`pop.cstat.hst` of B-20261127-232258-37c6773 against B-20261124-223926-33194d9 joined with
B-20261125-221742-5100a22/p8_cont), with its own interpolation; (2) series 7 Delta and the
Richardson value from the three rays.json of B-20261126-222544-f3a5176, and the crossing time from
the particle snapshots; (3) GM2 band strain from the two analysis files (B-20261126-221911-a0531db
against B-20261125-115558-2ab4161), and GM3 counts with its own FoF on one catalogue; (4) the ledger
rows of Table VIII.

G2 package complete for an independent review in the lead's judgement: what remains open is the
failures above with rulings 0046 item 2 and 0039 item 2(c), the GM3 ruling asked for, and C18.
No card run is needed.
