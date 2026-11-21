# HANDOFF of A-emd-pbh

Written for a reader with no memory, by the lead of batch 2b (wave 3), 2026-11-21 ~00:40 PST.

State in three lines: G0 is signed (2026-11-19). G1 is complete for sign-off: the independent
gate review recommends PASS WITH RESERVATIONS, its one condition (C20, these owner files) is
closed, and every helper's analysis reruns bit for bit (`stage/REVIEW-wave3.md`). G2 is under
way on the spherical ball: BH-1R (relaxed 1+log lapse, one static level of M/16) has a
persistent apparent horizon from t = 10.875 whose mass follows the exact mass of its slice to
better than 1e-3 after t ~ 11.7 (runs_ball, re-checked); its independent check (verify_bh) and
the three-mesh series (conv_ball, card job queued) are open.

Owner: A-emd-pbh, branch `track/A-emd-pbh`, worktree `/data/haiyangw/nrpic/wt/A-emd-pbh`.
Run next: `cd /data/haiyangw/nrpic/wt/A-emd-pbh && git merge --no-edit main && git status --short && harness/bin/nrpic-run status | grep -v completed && squeue -u $USER && harness/bin/nrpic-ctx inbox`
  (then: read the batch-2b reports of runs_ball and conv_ball in
  `/data/haiyangw/nrpic/scratch/orch/wave3_reports/A-emd-pbh.md`, re-check their finished
  analyses as in `analysis/review_wave3.py`, and start the packages below that are still open).

Files to read first: `STATUS.md`; `stage/REVIEW-wave3.md` (what is confirmed, the finder-tolerance
finding, the answers to the reviewer); `stage/G1/GATE_REVIEW.md` sections 5-6 (reservations
carried to G2); `PLAN-wave3.md` (round 1: six packages and their card caps); `RISKS.md` rows
1, 17, 18, 23, 24; the package journals named below.

## Packages and what remains

| Package | State at 2026-11-21 00:40 PST | What remains (restart from) |
|---|---|---|
| `g1close/` | done (batch 1) | nothing |
| G1 verifier, gate review | done | nothing; the reviewer's script is now in `stage/G1/gate_review/` |
| `runs_ball/` | done in batch 2b (00:29 PST; entries 11-20, README results table); re-checked by the lead (REVIEW-wave3 section 2b, run A-20261121-082814-6fadb30) | its entry 20 lists what is open: labels of the `_box` turnaround figures; BH-1R at a second refined resolution (that is conv_ball); excision near MeshBlock corners (a hypothesis, README request to core); the finder at uniform M/8 with BH-1R's settings and `hmean_tol_0 = 1e30` |
| `conv_ball/` | running in batch 2b (DESIGN, predictions, decks, `converge.py`, `analyse.py` committed by it) | `conv_ball/JOURNAL.md` last entry: prep runs of the nested lattices, processor smoke tests, card job 1 (A, B, A-N8, A-N64, A-R1.25, A-L32, B-N8; about 0.2 card-hours), chain for member C (about 1.3 card-hours); executable `scratch/core/exe/core_gauge` for every member. Set `hmean_tol_0 = 1e30` and `<fastflow> diagnostics = true` (needs a core-v0.5 executable; if the series stays on core_gauge, read the finder from the line diagnostics) |
| `verify_bh/` | cut 2026-11-20 14:34, no registered run | `verify_bh/JOURNAL.md` entry 2: submit c1_exact, c2_initial, c3_horizon bh_smr, c4_lines, c5_shells with `nrpic-run submit --package tracks/A-emd-pbh/verify_bh`, then VERIFIER.md sections 1-3, figures, README, then section 4 (comparison with runs_ball entries 11-12). 0 card-hours, about an hour |
| `szekeres/` round 1 | cut; its file run A-20261120-223422-8cc4241 closed by the lead (exit 0, mass converged to 2e-10) | `szekeres/JOURNAL.md` entry 9: registered repeat of the eps choice (P16), one card job of 58 min for N = 64, 128, 256 to tau = 40 (P17-P23), the 8-per-cell check (needs `run_cpu_members.py` to accept NAME=DIR members); about 1.0-1.5 card-hours |
| `periodic_threshold/` round 1 | cut; data run A-20261120-223123-f436c39 closed by the lead (prediction D3 holds); four files uncommitted: `JOURNAL.md` (one-line time fix), `inputs/peak_leak.athinput`, `scripts/ltb_reference.py`, `scripts/ltbref.py` | read the four files, commit them with their package, run the LTB reference (registered), smoke-test the leak deck on processors, write predictions, one card job (cap 2.5 card-hours). Use `hmean_tol_0 = 1e30`, finder diagnostics, `alpha_exc` relative to the mean lapse (core message 20261120T223017Z items 1, 3), and the guard (core-v0.5) |

Card jobs of this owner queued or running at the end of this session: none seen in `squeue`
(the helpers of runs_ball and conv_ball may have submitted since: check `squeue` and their
manifests; their outputs land in `scratch/A-emd-pbh/<run id>/`).

## Decisions pending

- orch: sign-off of G1 (outbox 20261121T080815Z__to-orch__g1-sign-off-and-waivers and its
  follow-up: the runs_ball manifests are closed, no waiver is needed).
- core: re-triage of the 2026-11-15 requests that core-v0.4/v0.5 now serve (gauge, guard, step
  limit, AMR, periodic finder, region norms); still open: phase-1 periodic generator for
  mu >= 0.5 (core/id-solver-2), full K_ij and gamma_ij in the dumps (Szekeres eigenvalue test).
- kb: conformal flatness of the comoving Szekeres slice; its apparent horizon against R = 2M.
- core answered on 2026-11-21 (inbox, acknowledged): the K_ij eigenvalue test of the Szekeres hole
  can use `variable = adm` with `double_precision = true` (adm_gxx..adm_Kzz, not yet checked by
  core in nrpic_cosmo); the finder at four cells per horizon radius is sensitive at the 5e-3
  level, so a first small surface counts only after consecutive searches agree; Newtonian energy
  drift explained (RISKS row 16); requests still deferred: phase-1 generator, refined-level
  solve (core/id-solver-2), special-relativistic push (core/newton-2), finder spin projection;
  the K_ref lapse and softplus lapse are declined (`cosmo_gauge.md` 7.1).

## Traps

- `hmean_tol_0 = 100` in every existing deck can stop the finder at its first iteration
  (RISKS row 23); "no detection" is not "no horizon".
- Helpers share this worktree: commit path-limited (`git commit -- <paths>`), never `git add -A`;
  `nrpic-run submit --package <dir>` so that other packages' changes do not block a run.
- Szekeres scripts write figures into `szekeres/figures/` as well as the run directory: a rerun
  rewrites tracked PNGs (the lead's re-check redirects `common.FIGDIR`).
- Card runs on core-v0.3/core_gauge executables run on with non-finite fields and exit 0; read
  the first non-finite record. core-v0.5 stops them with exit status 3.
- Hand-registered runs of waves 1-2 (`runs_ball/runreg.py`, `periodic_threshold/scripts/register_run.py`,
  `newton/register.py`, `criteria/runlog.py`) are closed with their own tools.
- AthenaK's finder summary: core-v0.5 writes it into the run directory; older executables write
  it into the working directory (run from the run directory).
- Periodic background time: t/t_H = ((1 + tau/2)^2/6)^(3/2) for eps_i = 1 (tau = code time).
- Kill processes by numeric PID only; never `pkill -f`.
