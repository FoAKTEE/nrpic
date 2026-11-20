# conv_ball: G2 convergence series of horizon formation in the expanding ball (Track A)

Helper package of A-emd-pbh, wave 3 round 1. State: PAUSED during design (JOURNAL.md entry 2);
no simulation of the series has run yet.

## What is here

| path | content |
|---|---|
| `JOURNAL.md` | what was read, design inputs with run ids, where the work stopped |
| `scripts/common.py`, `compare.py`, `fields.py`, `summary3.py`, `prep_bh.py`, `bh.athinput`, `bh_smr.athinput` | copies of `runs_ball/` at commit 9cddbfc6 (header line says so); `common.py` path fix; `prep_bh.py` gained `--M`, `--edge-w`, `--nested` (marked `conv_ball:`) |
| `scripts/geometry_probe.py` | coordinate radii of the shell groups, finder radius, cost and memory of a finished run (run A-20261120-222355-cc8e0af on BH-1R) |
| `scripts/nested.py` | nested static geometry, nested particle lattice on expball's model, cost and memory model calibrated on BH-1R |
| `scripts/design_calc.py` | design table of all members (mesh, particles, memory, card time), figure |
| `scripts/make_decks.py`, `decks/` | AthenaK decks `nest<HF>_L<OUTER>.athinput` of the series |

## How to rerun

See JOURNAL.md entry 2 for the next commands. Runs are registered with
`harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/A-emd-pbh/conv_ball ...`.

## Requests

None yet.
