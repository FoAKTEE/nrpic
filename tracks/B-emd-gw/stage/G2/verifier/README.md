# stage/G2/verifier: fresh verifier of gate G2, Track B (batch 35, 2026-11-27)

Helper package of owner B-emd-gw (checklist item C18; decisions 0016 item 4, 0046 item 2,
0048 item 3). Processors only, no card run. The report is `VERIFIER.md` in this directory
(the lead copies it to `stage/G2/VERIFIER.md`, which this helper may not write).

## Contents

| Path | What |
|---|---|
| `JOURNAL.md` | predictions V0-V8 written before any recomputation (commit 7778f837a), outcomes after |
| `VERIFIER.md` | the report: per claim reproduced / not reproduced / not checkable, what G2 can claim, and a last section against the lead's verdicts |
| `scripts/vlib.py` | my readers (AthenaK binary mesh dumps from `athenak/src/outputs/binary.cpp`, particle snapshots from `docs/FORMATS.md`, history files), flat TT projector, friends-of-friends |
| `scripts/v0_tests.py` | V0: the readers, projector and FoF on analytic cases (synthetic dump in shuffled meshblocks, synthetic snapshot, random TT / pure-gauge / trace fields, Gaussian clumps across the periodic face) |
| `scripts/v1_waves.py` | V1: waves F (flat, k = 2 pi (1,1,1)) and X (matter-era standing mode) from the raw dumps against my exact solutions |
| `scripts/v2_strain.py` | V2/V3: band strain 256^3 against 128^3 (Gamma driver) and the high-k ratio of the two gauges, from the analysis files and from the raw dumps |
| `scripts/v3_constraints.py` | V5/V6: constraint ratios of the mesh pairs and the particle leg, the 256^3 zero-shift stop |
| `scripts/v4_shear.py` | V7: shearing dust, series 7 and L2: Delta, differences, order, Richardson value, closed-form cos(theta_lin), stream crossing from the particle snapshots |
| `scripts/v5_halos.py` | V4: FoF catalogues with equal masses, GR against the Newtonian mode, 256^3 against 128^3 |
| `scripts/figstyle.py` | copy of `python/nrpic/figstyle.py` |
| `figs/` | the figures of the registered runs, copied here (PNG) |

## Registered runs

| Run | What |
|---|---|
| `B-20261128-021054-577fc9d` | V0 analytic tests (all pass) |
| `B-20261128-021125-515c0cc` | V1 waves F and X, N = 16, 32, 48, 64 |
| `B-20261128-021335-a7a2a49` | V5/V6 first reading (figure unreadable: superseded by the next) |
| `B-20261128-021515-a6306af` | V5/V6 second reading: figure, pairing sensitivity, last records |
| `B-20261128-021337-d0c2105` | V7 shearing dust |
| `B-20261128-021349-a57f21e` | V2/V3 first attempt: FAILED (int32 overflow in my reader on a 256^3 meshblock; the file part had run) |
| `B-20261128-021412-072e411` | V2/V3 after the reader fix |
| `B-20261128-021413-6b4d7a1` | V4 FoF catalogues |

## How to rerun

```
cd /data/haiyangw/nrpic/wt/B-emd-gw
P=tracks/B-emd-gw/stage/G2/verifier; S=/data/haiyangw/nrpic/scratch/B-emd-gw
R="harness/bin/nrpic-run submit --kind scouting --gate G2 --package $P --cores 2 --purpose ..."
$R -- python3 $P/scripts/v0_tests.py '$NRPIC_RUN_DIR'
$R -- python3 $P/scripts/v1_waves.py '$NRPIC_RUN_DIR' F:16=$S/B-20261119-142016-ee73a03/N16 ... X:64=$S/B-20261119-142124-feb2daf/expN64
$R -- python3 $P/scripts/v3_constraints.py '$NRPIC_RUN_DIR' $S
$R -- python3 $P/scripts/v4_shear.py '$NRPIC_RUN_DIR' N7_64=$S/B-20261126-222544-f3a5176/N7_n64_ppc4 ...
$R -- python3 $P/scripts/v2_strain.py '$NRPIC_RUN_DIR' $S
$R -- python3 $P/scripts/v5_halos.py '$NRPIC_RUN_DIR' zs128_a121=$S/B-20261123-014847-f295ab4/pop.part.00020.bin ...
```
The full argument lists are in each run's `manifest.json` (field `command`). Wall times:
V0-V1, V3-V4 seconds; V5 about 2 minutes (two 256^3 catalogues, 16.8 million particles);
V2 several minutes (four 256^3 dumps of 2.95 GB).

## Requests

- To the lead (B-emd-gw): copy `VERIFIER.md` to `stage/G2/VERIFIER.md` (the file the stage
  check looks for); the wording corrections listed in its section 6.
- None to other owners.
