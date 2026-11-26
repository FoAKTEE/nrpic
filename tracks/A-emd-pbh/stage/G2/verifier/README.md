# Fresh verifier of gate G2, Track A (item C18)

Work package of batch 29 (decision 0046 item 1), 2026-11-26. Processors only, no card run, one core per run.
The report is `../VERIFIER.md`; predictions and outcomes are in `JOURNAL.md` (entries 0-4, predictions committed
before each reader ran).

## What is here

| file | what |
|---|---|
| `JOURNAL.md` | predictions V1-V5 (entry 1), V1.5-V1.6 (entry 3), outcomes (entries 2 and 4) |
| `scripts/szk_verify.py` | Szekeres: per-element closed-form reference (simultaneous-bang Szekeres), its test against the integrated dust equations, reader of NRCOSMO1 / NRPIC001 / NRFIELD2 files, shell/core/outside errors of K and E, the invariant non-spherical signal, orders, figure |
| `scripts/szk_hcon.py` | Szekeres: shell rms of H/(16 pi rho_b) and max |alpha - 1| per dump, orders |
| `scripts/a2_verify.py` | triaxial peaks: snapshot reader (NRPSNAP1 with per-particle proper time), sign of det(dx/dq), axis brackets, Zel'dovich deformation tensor at the centre, dust clock of the crossing cell, synthetic-lattice test, figure |
| `scripts/p0l6_verify.py` | P0L6: trajectory and metric reader, areal radius of the round sphere through each tracked particle, own cycloid (tested), errors to turnaround and to trapping, finder status timeline, trapped tracks, figure |
| `scripts/ltb_crossing.py` | shell crossing of the exact LTB reference B before tau = 141 |
| `scripts/c3_verify.py` | C3: line ratio ||H||/||16 pi E|| (weights x^2 dx, x > 0) from the line outputs, with a weights test, orders, figure |
| `scripts/table5_check.py` | every Table V row against its manifest and registered output; conv_ball member C spot check |
| `scripts/figstyle.py` | copy of `harness/style/figstyle.py` |

## Runs (registered; outputs and figures under `scratch/A-emd-pbh/<run>/`)

| run | script | figure |
|---|---|---|
| A-20261126-222856-952faf8 | szk_verify.py, members N64, N128, N256 | fig_szk_verify.png |
| A-20261126-224402-693c506 | szk_hcon.py | |
| A-20261126-223151-8310871 | a2_verify.py, S1L, S1L-h, N-z, N-z128 | fig_a2_verify.png |
| A-20261126-223655-77df724 | p0l6_verify.py | fig_p0l6_verify.png |
| A-20261126-223953-c6606f6 | ltb_crossing.py, defective first version (one bang time) | |
| A-20261126-224045-9d8fe53 | ltb_crossing.py | |
| A-20261126-223246-89959bc | c3_verify.py, 13 members | fig_c3_verify.png |
| A-20261126-223902-c94b32f | table5_check.py, failed (inf in an output) | |
| A-20261126-223909-6859df2 | table5_check.py | |

How to rerun: the command of each run is in its manifest (`tracks/A-emd-pbh/runs/<run>/manifest.json`); from the
worktree root, `harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/A-emd-pbh/stage/G2/verifier
--cores 1 -- bash -c '<command of the manifest>'`. The Szekeres reader needs about 45 minutes on one core and 3.5 GB
for N256; the others take seconds to a minute.

## Requests

- To the lead of A-emd-pbh: (1) state in the note which non-spherical signal Table V uses (same code cell, with the
  displacement of the shell centres) and add the invariant one, or soften "far below" at tau 30; (2) replace "through
  turnaround and collapse" for the P0L6 shells by "to turnaround within 3 per cent", with the collapse-phase
  departures (up to 42 per cent at r0 = 1.52); (3) the dust clock of A2/A2H can be read from the snapshots (they carry
  each particle's proper time): correct A2X (ii) "not decidable"; (4) Table V's orders "1.5, 2" for the detection
  time should carry the range of CHECKLIST C2 (1.2-1.5, 1.75-2.1); (5) add P18 for N256 at tau 40 and AZ1's first
  clause to OPEN.md's list of failed predictions; (6) read the log of the full stage verify started by this package
  (`scratch/A-emd-pbh/tmp/stage-verify-full-verifier-20261126-141818.log`) when it ends.
- To core: none new (the finder's false acceptance and stall are already requested by the lead, outbox
  finder-false-accept-and-stall-p0l6).
