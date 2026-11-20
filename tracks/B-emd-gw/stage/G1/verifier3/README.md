# stage/G1/verifier3: independent verifier of G1 criterion 1 (tests F and X) and of the spatial-gauge piece

Helper package of B-emd-gw, wave 3 round 1 (2026-11-20). Written in a fresh context from the
artefacts (inputs, initial-data script, raw dumps); the producers' conclusions were read only
after my own numbers were committed (JOURNAL.md says when).

## Contents

| Path | What |
|---|---|
| `JOURNAL.md` | predictions before each step, outcomes after |
| `VERIFIER.md` | the verifier's report (written last) |
| `scripts/figstyle.py` | copy of `harness/style/figstyle.py` |
| `scripts/v1_exact.py` | V1: exact solutions of F and X, symbolic and numerical checks |
| (more rows are added as the scripts exist) | |

## How to rerun

Every script reads `NRPIC_RUN_DIR` and is run through the harness from the worktree root:

```
harness/bin/nrpic-run submit --kind scouting --gate G1 --package tracks/B-emd-gw/stage/G1/verifier3 \
  --purpose "..." --launcher local -- python3 tracks/B-emd-gw/stage/G1/verifier3/scripts/<script>.py
```

## Requests

(none yet)
