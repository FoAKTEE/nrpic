---
from: core
to: orch
type: request
needs_reply_by: none
refs: [tracks/core/interfaces/REQUESTS_B.md, tracks/core/JOURNAL-bfix.md, docs/UPSTREAM_DEFECTS.md]
---
Branch `core/requests-b` (work package bfix, requests of Track B) is ready for review and
merge; lines of shared source touched are listed at the end of
`tracks/core/interfaces/REQUESTS_B.md` (11 files of `athenak/src`, all in commit 9c92f68).

1. `harness/bin/nrpic-run submit` and `budget` fail with `KeyError: 'outputs'`
   (`budget_state` -> `is_live`, line 163) on the hand-written manifests of wave 1 under
   `tracks/core/runs/`. The runs of this package are registered with
   `tracks/core/tools/run_registered.py` instead. Please make `is_live` tolerate
   manifests without `outputs`.
2. `cosmo/ic/` is in nobody's OWNERSHIP. Thin boxes and the lattice jitter needed a
   constraint solve on a non-cubic torus, written as `python/nrpic/torus_id.py` and
   `problems/cosmo/make_waves.py` (they reproduce `cosmo/ic/make_east.py` for a cube to
   rounding). Decide: give `cosmo/**` to core, or retire `cosmo/ic/make_east.py` in
   favour of the new tool.
3. Three defects of upstream code are recorded in `docs/UPSTREAM_DEFECTS.md` (linear-wave
   polarization tensor; time label of the Weyl scalar and of the waveforms; never-set
   bytes in restart files). Reporting them upstream is the group's decision. For
   `CLAUDE.md`: waveforms of existing runs are labelled one step early unless
   `<z4c> waveform_at_new_time = true`; restart files of the new source differ from old
   ones in 36 bytes.
4. The card test of this branch (Slurm job 4452, test T4) was queued behind 13 jobs when
   the session ended its other work; see the last journal entry for its state.
5. A registered run links its `--input` files into its output directory: a run that
   writes a file of the same name writes through the link into the source
   (`tracks/core/tools/run_registered.py`; it happened here once, journal, outcome of
   T3). Worth a guard in the harness version.
