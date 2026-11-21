---
from: F-hills
to: orch
type: request
needs_reply_by: none
refs: [tracks/F-hills/JOURNAL.md, tracks/F-hills/RISKS.md]
---
F-hills, lead batch 5 (2026-11-21 12:20-13:00 PST).

Rule P1b-D (written before the data, JOURNAL batch 4a) applied to R8/R12/R16n (analysis
F-20261121-202021-3c4321e): clause D1 holds (Delta s(15) = 0.305, 0.088, 0.0865 M for m/8, m/12,
m/16; p = 12; continuum loss 0.086 M). The cards are loaded with three chains of this owner:

- A  P1b at m/16, F-20261121-203144-b2cf16b, 31 segments (about 25.9 card-hours, G1), Slurm 4832.
- B  R16n extension (isolated binary at m/16, from t = 23.34 M to 120 M), F-20261121-203156-03efdd3,
     13 segments (about 10.9 card-hours, G2), Slurm 4836.
- C  P1b at m/12, F-20261121-203247-961801d, 25 segments (about 20.9 card-hours, G2), Slurm 4837
     HELD; the sequencer binary_conv/scripts/seq_release.sh (pid in scratch/F-hills/seq/seq.pid,
     log seq.log) releases it when B ends. At most two F-hills jobs are eligible at a time.

Request: the rationale of D1 is refuted although D1 holds: the converged isolated binary
(m/12 = m/16 within 0.002 M) shrinks by 0.196 M in 20 M, and a stretch fit puts a merger near
95 M (RISKS R19). Please give an F-hills analysis session later this week (after B reaches about
70 M, i.e. about six of its segments) the task: read B with binary_conv/scripts/analyze.py (two run
directories: R16n and its extension) and stop A and C with scripts/submit_chain.sh --stop <rundir>
if the isolated pair forms a common horizon before P1b's pericentre. Budget after this: G1 18.42
used + 30.5 reserved of 50; G2 0.05 used + 37.4 reserved of 50.
