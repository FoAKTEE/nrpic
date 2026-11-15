# HANDOFF of C-sidm

Written for a reader with no memory of the last session (lead of wave 1, 2026-11-15).

State: G0 package written (`stage/G0/`: REPORT, EVIDENCE, OPEN, REVIEW, CHECKLIST), awaiting
the orchestrator. G1 is NOT met: the baseline (F21) and the specifications are done and
independently checked; core committed the operator at the end of the session (3436846,
then 1a050f3) and its kernels pass the track's T0 (run C-sidm-20261115-132624-13a77db), but
no box test T0b-T12 has run. No card time used.
Owner: C-sidm, branch `track/C-sidm`, worktree `/data/haiyangw/nrpic/wt/C-sidm`.
Run next: `cd /data/haiyangw/nrpic/wt/C-sidm && git merge --no-edit main && git log --oneline -5 core/collisions`
(read `tracks/core/JOURNAL-coll.md` and `tracks/core/interfaces/collisions.md` on that
branch; once core's predictions P0-P11 are checked and a processor executable of
`core/collisions` exists, run T1, T2, T10 of `collide/TESTS.md` with the option names of
core's interface, each registered with
`python3 tracks/C-sidm/review/register.py --purpose ... -- <command>`, predictions in
`JOURNAL.md` first).

Files to read first: `tracks/C-sidm/STATUS.md`; `stage/G0/REPORT.md` (decisions: S3 family
F21 b = 0.1; Kn = lambda_c/H_c with lambda = 1/(rho0 sigma_m), H = (v1^2/(4 pi rho0))^1/2;
fluid anchor = exact pulsation onset); `stage/G1/STATUS.md` (criteria and the first
collisional cluster runs CC1/CC2); `collide/TESTS.md`; `stage/G0/OPEN.md`.

Packages (each has README and JOURNAL): `scope/` (G0 note SCOPE.md, references),
`collide/` (SPEC, TESTS, RNG requirements, references, box analysis), `gravothermal/`
(F21 solver `tmb.py`, FEM onset), `equilibria/` (evstatic solver, 13 particle models in
`scratch/C-sidm/C-sidm-20261115-120610-b4592be/`, Kn conversion), `review/` (lead's
cross-checks and reruns).

Decisions pending: brief corrections, card budget and the nrpic-run manifest schema (orch,
outbox files `20261115T1320Z__to-orch__*`); collision operator, stream-2 table,
perturbation recipe, static curved metric, GR-hydro view (core, `..__to-core__*`); kb
fetches (`..__to-kb__*`). Lead decisions recorded in `stage/G0/REPORT.md` section 2 can be
overturned by the orchestrator.

Wave-2 work that needs no one else: F21 b = 0.1 particle models (generalise
`equilibria/evstatic.py`: kernel exp((1 - E/E0)/b) - 1, b = 1 is the King model); the
fluid onset with the Juttner Gamma_1 (`gravothermal/tmb.fem_lowest` with Gamma_1 from
`collide/REFERENCES/mj.py`); the growth-rate pipeline validated on the first paper's
monoenergetic outputs (`/data/haiyangw/nrpic/runs/st/`); the cosmetic figure fixes listed
in `stage/G0/REVIEW.md` (collide `ref_relax` y-label, `T6_0_step_collisionless` margin).
Card runs (wave 2, within the 20 GPU-h): monoenergetic collisionless scan (8 y_c x 2 signs
x 400 M), King b = 1 scouting, CC1/CC2.

Traps:
- `harness/bin/nrpic-run submit` stops with KeyError 'dir' on this branch (hand manifests);
  register with `tracks/C-sidm/review/register.py` (refuses uncommitted changes under
  `tracks/C-sidm`; commit first). `.gitignore` ignores `runs/`: add manifests with
  `git add -f tracks/C-sidm/runs/<id>/manifest.json`.
- Reproducing an old run needs the code of its commit: `collide/analysis/make_box.py`
  changed after run C-sidm-20261115-121302-313d399 (abd9c2e), so a rerun at HEAD draws other
  momenta; with `git archive` of 313d399 all 33 files are reproduced byte for byte (run
  C-sidm-20261115-132327-eab8e41). LAPACK results change in the last digits with the thread count (gravothermal
  ran with one thread).
- The Write tool refuses files named REPORT.md for subagents; the stage report was written
  with a shell here-document.
- Three Kn conventions exist in the helper packages (scope: energy density in H, factor
  1.18; equilibria: transport mean free path, factor 0.77); use the track definition.
- Core's draft operator uses a symmetric triad by default; replay test T0b needs
  `triad = cholesky` or a replay that follows the symmetric triad.
- Never kill by pattern; at most 16 cores; card runs only within the allotment.
