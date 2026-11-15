# stage/G0: verifier files (wave 2)

This directory holds the G0 stage package of B-emd-gw (CHECKLIST.md, EVIDENCE.md,
OPEN.md, REPORT.md, REVIEW.md: the lead's) and, from wave 2, the independent verifier's
files listed here. The verifier writes only `VERIFIER.md`, `JOURNAL.md`, this README and
`verifier/`.

| Path | What |
|---|---|
| `VERIFIER.md` | per claim C1-C8: CONFIRMED / NOT CONFIRMED / WRONG with evidence; the three weakest points of the plan; comparison with REVIEW.md (written afterwards) |
| `JOURNAL.md` | predictions written before each check, outcomes after, failed and misdirected runs |
| `verifier/scripts/v1_symbolic.py` | sympy: item 3 (C1), check 1E (C4), slicing (C5) |
| `verifier/scripts/v2_crossed.py` | second-order TT strain of crossed waves, own source and projector (C2) |
| `verifier/scripts/v3_junk.py` | junk TT, exact Bessel solution and numerical integration (C3) |
| `verifier/scripts/v4_lw_runs.sh`, `v4_lw_analysis.py` | AthenaK linear waves on processors, own analysis (C6) |
| `verifier/inputs/lw_oblique.athinput` | copy of `periodic_z4c/inputs/lw_x.athinput` with k = (1,1,0) (C6 break test) |
| `verifier/scripts/v5_gwdiag.py` | gw_diag TT and Psi_4 on own analytic fields, gauge nulls and AthenaK output (C7) |
| `verifier/scripts/v6_za_scaling.py` | sigma scaling of the Zel'dovich spectrum of 2403.15126, own mpmath code (C8) |
| `verifier/scripts/v7_track_tests.sh`, `v7_compare.py` | rerun of the track's tests, scope and baseline scripts; comparison with committed results |
| `verifier/scripts/v8_drift.sh` | amplitude scaling of the homogeneous drift seen in C6 |

Outputs (figures included) are in `scratch/B-emd-gw/<run id>/`, not committed.

## Runs (manifests in `tracks/B-emd-gw/runs/<run id>/`)

| Run id | Script | Claim |
|---|---|---|
| B-20261115-165114-277a0eb | v1_symbolic.py | C1, C4, C5 |
| B-20261115-165119-efd5ee7 | v2_crossed.py | C2 |
| B-20261115-165123-9cb1745 | v3_junk.py | C3 |
| B-20261115-165056-835fddf | v4_lw_runs.sh (+ analysis) | C6 |
| B-20261115-170431-c49964c | v8_drift.sh | C6 (drift) |
| B-20261115-170546-4507b05 | v5_gwdiag.py - <v4 run dir> | C7 |
| B-20261115-170518-c1b61a3 | v6_za_scaling.py | C8 |
| B-20261115-165608-171ff45 | v7_track_tests.sh | reruns of the track's own tests and scripts |
| B-20261115-165526-23d8541 | v7_track_tests.sh (first version) | on record: pytest part aborted (test_zeldovich.py is a script) |
| B-20261115-170526-a53d364 | v5_gwdiag.py (wrong argument) | on record, not used: output in scratch/B-emd-gw/v5_placeholder/ |

## How to rerun

From the worktree root, with the worktree's `.venv` (`harness/bin/nrpic-env create --no-kokkos`):

```text
P=tracks/B-emd-gw/stage/G0
harness/bin/nrpic-run submit --kind scouting --gate G0 --launcher local --package $P --cores 1 \
    --purpose "..." -- python3 $P/verifier/scripts/v1_symbolic.py      # likewise v2, v3, v6
harness/bin/nrpic-run submit --kind scouting --gate G1 --launcher local --package $P --cores 8 \
    --purpose "..." -- bash $P/verifier/scripts/v4_lw_runs.sh          # about 13 min, 8 processes
harness/bin/nrpic-run submit ... -- python3 $P/verifier/scripts/v5_gwdiag.py - scratch/B-emd-gw/<v4 run id>
harness/bin/nrpic-run submit ... -- bash $P/verifier/scripts/v7_track_tests.sh
harness/bin/nrpic-run submit ... -- bash $P/verifier/scripts/v8_drift.sh
```

Each script also takes an output directory as its first argument for a run outside the
harness. The AthenaK runs use the processor executable of release core-v0.3,
`/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena`, read-only. No card time was used.

## Requests

- core: fix the sign of a_xy and a_yz in `athenak/src/pgen/tests/z4c_linear_wave.cpp`
  lines 108 and 111 (oblique waves are not TT; measured in run B-20261115-165056-835fddf).
  The track's outbox already carries this request (`outbox/20261115T1340Z__to-core__z4c-linear-wave-polarization.md`);
  this is independent confirmation, not a new request.
- B-emd-gw lead: (1) correct the TT-fraction crossover in SCOPE.md risk 1 (0.289, not
  0.18); (2) take the full second-order solution from the code's own initial data
  (static part plus the Bessel junk of C3) as the pre-shell-crossing reference, and
  restate the G1-G3 criterion of SCOPE.md section 6 with the window where third-order
  terms stay below the target; (3) cite 2403.15126 for the emitted-spectrum scaling
  (lines 1005, 1031), not for Omega today (line 1074), or check the paper's ensemble
  definition; (4) OPEN item 7 can be closed at second order by the argument of
  VERIFIER.md C5 (or tested numerically on the first-source runs).
- None for orch or kb. No harness command failed.
