# HANDOFF of E-stoch-inf

State in three lines: Track E (stochastic inflation in NR, S11) has submitted its G0
package (feasibility gate) and recommends to continue; the group's decision is pending.
Core has written the scalar field with the stochastic hook on `core/scalar-field`
(836ac86); its noise generator passed Track E's validation on processors. G1 (slow-roll
reproduction) waits for core's initial slice at N*, diagnostics and a card build.

Run next (after core delivers; check with `git log --oneline core/scalar-field -5` and the
replies to `tracks/E-stoch-inf/outbox/20261115T1410Z__to-core__*.md`):

    cd /data/haiyangw/nrpic/wt/E-stoch-inf && git merge --no-edit main && \
    harness/bin/nrpic-ctx inbox --show

Then, for the noise only (no core change needed), to repeat the validation on a newer
processor executable of core (replace EXE):

    harness/bin/nrpic-run submit --kind scouting --gate G1 --cores 8 --background \
      --input tracks/E-stoch-inf/analysis/lead/inputs/u_base32.athinput --input EXE \
      --purpose "noise unit test U1-U8 on core EXE" -- bash -c 'python3 \
      tracks/E-stoch-inf/analysis/lead/u_runs.py --exe EXE --base \
      tracks/E-stoch-inf/analysis/lead/inputs/u_base32.athinput --out "$NRPIC_RUN_DIR" \
      --threads 1 --jobs 8 --u5-nmax2 36'

(about 6 min; then `bash tracks/E-stoch-inf/analysis/lead/lu_validate.sh <rundir> <outdir>`
inside a registered run; `nrpic-run finish <run_id>` closes a background run).

Files to read first: `STATUS.md`; `spec/scope/SCOPE.md` (owner's scope v1: parameter
ranges, the owner's decisions and thresholds A1-A8, test plan, recommendation, timeline);
`stage/G0/OPEN.md`; `stage/G1/STATUS.md`; `spec/SPEC.md` (equations, errata, section 10
requests); `codebase/DESIGN_REVIEW.md` sections 5, 8 (kicks, test ladder L0-L9);
`noise/NOISE_SPEC.md` sections 9-10; `langevin/README.md`; `JOURNAL.md` (last entry).

Decisions pending: the group's G0 decision (continue / shrink / downgrade); confirmation
of the owner's choices in SCOPE 4 (Courant 0.25, backreaction level 0, thresholds,
downgrade at 5 card-hours per 256^3 realisation).

Traps:
- The processor build of core is serial: 1.35e4 zone-cycles/s; 64^3 x 300 cycles costs
  95 min per run. Use N = 32 on processors, cards for anything larger.
- Core's executable lives in another worktree (`wt/core-scalar/.work/exe/`); use it read
  only, record its sha256 (the run manifest does), and never build in another worktree.
- `nrpic-run local` uses the worktree venv (`.venv`, made with `harness/bin/nrpic-env
  create --no-kokkos`); system python3 has no numpy in that environment. Submit refuses a
  dirty worktree: commit before every submit; background runs are closed with
  `nrpic-run finish`.
- Manifest statuses must be completed/failed/stopped, or `nrpic-run budget` crashes.
- Run ids: `E-<stamp>-<commit>` from nrpic-run, `E-stoch-inf-<stamp>-<commit>` from the
  helpers' registrars; both are valid records.
- The validator compares U5a/U5b with their own input files (`--res-lo-input`,
  `--res-hi-input`); with U1's input it stops at the Nyquist check.
- The tool guard refuses files named REPORT.md for subagents; the G0 scoping lives in
  `spec/scope/SCOPE.md`.
- The langevin scripts write their JSON and figures into `langevin/results/` and
  `langevin/fig/` as well as into the run directory: a rerun with other arguments
  overwrites the committed reference files (it happened in run E-20261115-140502-f70b223;
  restored with `git checkout`). Check `git status` after any langevin run.
- Never read the brief whole; line ranges: S11 445-465, track sheet 785-802, M11 544-547.
