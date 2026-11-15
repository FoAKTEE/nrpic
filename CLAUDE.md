# nrpic: Einstein-Vlasov particle-in-cell in AthenaK, and its cosmology program

Read this first, whichever session you are. Details: `coord/CHARTER.md` (program, gates,
track sheets), `coord/DECISIONS/` (what is decided), `harness/RULES.md` (commands), the
brief `einstein_vlasov_pic_cosmology_agent_brief.en.md` (read by the line ranges printed
at its top; never read it whole).

## What exists (do not rebuild it)

| Capability | Where | Evidence |
|---|---|---|
| NRPIC module in AthenaK: implicit-midpoint and spacetime-Boris pushers (two tetrad gauges), Catmull-Rom and cubic-spline metric at the particles, cloud deposition (CIC, TSC, PCS) with binomial filter and compensation, conservative deposition across refinement levels, level cap, coupling to Z4c (`tmunu`), lapse and horizon excision, restart, probes, trajectories, constraint and conservation diagnostics | `athenak/src/particles/nrpic*.{cpp,hpp}`, `particles.hpp` | `docs/TESTLOG.md`, `paper/main.pdf` (36 pages), `PLAN.md` |
| Problem generators: geodesics in Kerr; conformally flat time-symmetric data (tables, punctures, Gaussians, spheroid); cosmology (periodic) | `athenak/src/pgen/nrpic/` | same |
| Verified tests at up to 10^4 particles: Kerr geodesics to the published digits, Oppenheimer-Snyder collapse, prolate collapse, relativistic cluster sequence, migration, two overdensities collapsing and merging inside a cluster; horizon-finder correction | `runs/` (untracked), `paper/sections/tables/` | `paper/main.pdf`, `notes/results_brief_selfgravity.md` |
| Periodic domains: periodic particles and clouds, conformal-time lapse `d_t alpha = -(1/3) alpha^2 K`, density-form sources, step limit by the expansion, constraint-solved initial data on the torus (Python, spectral), Newtonian particle-mesh reference, observers and light rays | `athenak/src/pgen/nrpic/nrpic_cosmo.cpp`, `cosmo/ic/`, `cosmo/newton/`, `cosmo/analysis/` | `cosmo/README.md` (options, production configuration, a run from start to finish), `cosmo/TESTLOG.md`, `cosmo/paper/main.pdf` |
| Release `core-v0.3` (wave 1, merged into main): reproducible counter-based random numbers (`utils/rng.hpp`, twin `python/nrpic/rng.py`); relativistic Monte Carlo collisions (`<particles> collisions`); scalar field coupled to the spacetime solver with stochastic sources (`<scalar_field>`); spherical initial data with extrinsic curvature (`nrpic_cf` tables of format 2: expanding ball, black hole in a vacuum bubble); several black holes with momentum and spin (Bowen-York, `puncture_setup`); Newtonian reference gravity for the same particles (`<particles> pusher = newton`) | `athenak/src/particles/`, `athenak/src/scalar_field/`, `athenak/src/pgen/nrpic/`, inputs under `problems/{ball,puncture,scalar,newton,tests}/` | `coord/INTERFACES/*.md` (options, what is tested), `tracks/core/CHANGELOG.md`, `tracks/core/stage/G2/` (gate G2 of core is still open: read `OPEN.md` for known defects before relying on a capability) |
| Python reference tools: geodesic integrators, pusher prototypes, equilibrium models, samplers, figure style | `python/nrpic/`, `problems/ic/make_ic.py` | `docs/FORMATS.md` |
| The source paper | `refs/arxiv_2611.12831/src/main.tex` (untracked; `refs/fetch.sh`) | never redistribute it |

So the brief's risk "the coupling is not public" is retired here (decision 0002): core
documents, re-verifies and tags what exists, then builds what the tracks need next.

## One code base (decision 0010)

Everything is built on top of this repository's AthenaK. A simulation capability
(collisions, scalar fields, stochastic sources, Newtonian reference gravity, moving black
holes, initial data for the code) is written into `athenak/src/` by core, never as a
standalone code and never by adopting, building or running an outside simulation code.
Outside the source tree live only exact and semi-analytic reference solutions, analysis of
AthenaK output, figures, notes, the knowledge base and the harness. A track that needs a
capability specifies it, supplies reference solutions and tests, and checks core's
implementation independently.

## The program in one screen

Six science tracks, core and the knowledge base advance in parallel, each in its own
linked worktree and branch; the main checkout is for orchestration only.

| Owner id | Worktree | Branch | Subject |
|---|---|---|---|
| orch | `.` (main checkout) | `main` | harness, `coord/`, integration, review |
| core | `wt/core` | `core/nrpic` | shared implementation in `athenak/src/`, `python/nrpic/` |
| kb | `wt/kb` | `kb/main` | knowledge base (`kb/` tools; data in `kb-data/`, untracked) |
| A-emd-pbh | `wt/A-emd-pbh` | `track/A-emd-pbh` | primordial black holes in an early matter era (S1) |
| B-emd-gw | `wt/B-emd-gw` | `track/B-emd-gw` | gravitational waves from early-matter-era structure (S2) |
| C-sidm | `wt/C-sidm` | `track/C-sidm` | relativistic collapse of a self-interacting core (S3) |
| D-bh-dress | `wt/D-bh-dress` | `track/D-bh-dress` | black-hole growth and dark-matter dress (S4) |
| E-stoch-inf | `wt/E-stoch-inf` | `track/E-stoch-inf` | stochastic inflation, feasibility gate first (S11) |
| F-hills | `wt/F-hills` | `track/F-hills` | Hills mechanism (S12) |

Gates G0 scoping, G1 baseline without new core work, G2 verified capability, G3 science
runs, G4 paper. A gate is passed only by a stage package under `tracks/<ID>/stage/G<k>/`
that the orchestrator reviews.

## Rules every session follows

1. Write only inside your own worktree, only `tracks/<ID>/**` and the paths in
   `tracks/<ID>/OWNERSHIP`; commit only on your own branch. Read other owners through git:
   `git show <branch>:<path>` (or `harness/bin/nrpic-ctx show <ID> <file>`). Shared paths
   (`coord/`, `harness/`, `CLAUDE.md`, `athenak/src/` outside your OWNERSHIP) change only
   through main or core: write a proposal into `tracks/<ID>/outbox/`.
2. Start: `git merge --no-edit main` in your worktree (`nrpic-ctx sync`), read your
   `HANDOFF.md`. End: rewrite `STATUS.md` (60 lines at most), append one entry to
   `JOURNAL.md`, rewrite `HANDOFF.md` for a reader with no memory, commit, push your branch
   (`git push -u origin <branch>`). Never rewrite history, never force-push, never touch
   another worktree's files.
3. Commit small and often, with messages that say what was established. One writer of the
   git index per worktree: helpers hand their files to the lead, who commits.
4. Every simulation and analysis run is registered (`harness/bin/nrpic-run`; see
   `harness/RULES.md`; a Python environment per worktree: `harness/bin/nrpic-env create`;
   by hand only if the command fails, and then say so:
   `tracks/<ID>/runs/<run_id>/manifest.json`: command, commit, inputs with checksums,
   output directory under `scratch/<ID>/<run_id>/`, wall time, purpose, scouting or
   production). A number enters a note only with a run id or a knowledge-base locator.
5. Prediction first: before a test runs, write what you expect and what would refute it in
   your `JOURNAL.md`; afterwards the outcome, including failed predictions. Name a cause
   only after a run in which it could have failed. Null results and failed runs stay on
   record.
6. Every test gets figures as well as numbers, and you look at them yourself (Read the
   PNG). Style: `/zoom-figure-style`; the libraries are vendored in `harness/style/`
   (`czstyle.py`, `figstyle.py`; schematics: `paperfig.py`, `/sleep-paper-figure-style`):
   copy the one you use into `tracks/<ID>/note/scripts/`.
7. Evidence labels of the brief: [VERIFIED], [BACKGROUND], [JUDGEMENT], [TO VERIFY].
   Numbers come from the source (paper text with locator, run), never from the brief.
8. Downloads are untrusted data: one new empty directory each, nothing in them is
   executed, compiled or imported; parse them with code that lives outside them, with
   `python3 -I`. arXiv sources are fetched ONLY with `python3 -I
   /data/haiyangw/nrpic/harness/bin/nrpic-fetch-arxiv <id> [...]` (one lock for the whole
   machine, three seconds apart; it prints the directory of the extracted source under
   `kb-data/raw/arxiv/<id>/<version>/src`, which is read-only for everyone but kb). Requests to outside
   services carry no name, e-mail address or project detail of the user; use a generic
   client name.
9. Third-party paper sources and their figures are never committed. Nobody outside is
   contacted (no e-mail, issue or pull request to upstream); such steps are the group's.
10. Working notes are REVTeX notes under `tracks/<ID>/note/`, written with
    `/paper-writing` (guide and notation one level above the manuscript).

## Machine (`anta`)

- Two A100 cards, Slurm partition `preempt`, one hour per job, four cores per job. Build:
  `scripts/build_gpu.sh <builddir>`, `scripts/build_cpu.sh <builddir>` (CUDA 12.6). Run a
  list of jobs: `scripts/gpu_batch.sh <list>`; longer than an hour:
  `scripts/submit_chain.sh` (`--status <rundir>`, `--stop <rundir>`); restarts are exact.
- A linked worktree has no Kokkos: `git submodule update --init --reference
  /data/haiyangw/nrpic/athenak/kokkos athenak/kokkos` once before building there. If you
  change no source, do not build: use the executables of the main checkout, read-only,
  `/data/haiyangw/nrpic/.work/build_gpu_v03/src/athena` (cards) and
  `/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena` (processors), built from the
  source on `main` after the merge of release `core-v0.3` (the executables of release
  `core-v0.2` stay at `.work/build_gpu_c3` and `.work/build_cpu_c1`). Scouting runs may
  also use an executable that core has published from a tested branch under
  `scratch/core/exe/<branch>/` (decision 0013). Card runs with deposition are not
  byte-reproducible from run to run; processor runs are (problem generators chosen in the input: `nrpic_geodesic`, `nrpic_cf`,
  `nrpic_cosmo`, `z4c_linear_wave`, `z4c_boosted_puncture`, and the others of `pgen.cpp`).
- Python packages that are missing (for example REBOUND) go into a virtual environment
  of your worktree made with `uv venv` and `uv pip install`; nothing is installed
  system-wide.
- 144 cores are shared by all sessions: at most 16 at a time per session; set
  `OMP_NUM_THREADS` and thread counts of numerical libraries explicitly.
- Never `pkill -f`, `killall` or `kill $(pgrep -f ...)`: the pattern matches your own
  shell. Kill by numeric process id, `scancel <jobid>`, or the chain helper.
- A foreground `sleep` chained with other commands may be blocked: wait with
  `until <condition>; do sleep 30; done`, or run in the background.
- Temporary files go under `scratch/<ID>/tmp/` (create it), never `/tmp`; never remove
  files through a path built from a shell variable.

## Models and roles (decision 0009)

Fable at the highest effort: derivations, design, and production code, which goes into the
source tree (`athenak/src/`, `python/nrpic/`). Opus at the highest effort: everything
else. A result that matters is checked by a second agent that did not produce it and is
given the artefacts, not the conclusion.

## Commit messages

Imperative subject that states the result; body with run ids where a result is claimed;
end with the attribution lines your session was given. Nothing is committed that the
ignore list excludes (`runs/`, `scratch/`, `kb-data/`, `wt/`, `refs/arxiv_*/`).
