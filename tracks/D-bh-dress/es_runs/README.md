# es_runs: first full-relativity runs of Track D (ES-1 and its vacuum control V-1)

Helper package of owner D-bh-dress, wave 2. The black hole in a vacuum bubble inside an
expanding dust ball (Einstein-Straus type, D-pre-1), evolved in this repository's AthenaK
(release `core-v0.3`, card executable `.work/build_gpu_v03/src/athena`), with its matched
vacuum control V-1. Specification and pass criteria: `stage/G1/STATUS.md`, section "The
first full-relativity run"; predictions restated in `JOURNAL.md` before the runs.

State: being built (this file is rewritten at the end of the package).

## Contents

| Path | What |
|---|---|
| `make_data.py` | data sets: ES with the outer dust edge at 60 M (through `einstein_straus/make_es.py`), V-1 (same f(R), no dust), exact references, numbers for the predictions |
| `tools/offline_check_es.py` | offline constraint check of both tables (`einstein_straus/offline_check.py`, figures redirected) |
| `JOURNAL.md` | predictions before each test, outcomes after |
