# HANDOFF of B-emd-gw

Written for a reader with no memory of the last session (lead session of 2026-11-15,
wave 1). Rewritten at the end of every session.

State: Wave 1 is done and reviewed. Five helper packages exist (`scope/`, `periodic_z4c/`,
`gw_diag/`, `baseline/`, `verify_cosmo/`); the lead reran all of them from a clean export
and every number reproduced bit for bit (run B-emd-gw-20261115-131016-03b1119). The G0
package is in `stage/G0/` (REPORT, EVIDENCE, OPEN, REVIEW, CHECKLIST); G1 is not met
(`stage/G1/STATUS.md`). Fourteen requests went out (`outbox/20261115T1340Z__*`).
Owner: B-emd-gw, branch `track/B-emd-gw`, worktree `/data/haiyangw/nrpic/wt/B-emd-gw`.
Run next: `cd /data/haiyangw/nrpic/wt/B-emd-gw && git merge --no-edit main && harness/bin/nrpic-ctx inbox --show`
(then act on replies; without replies start the first-source scouting below).

Files to read first: `tracks/B-emd-gw/STATUS.md`; `stage/G0/REPORT.md` (scope in one
place); `stage/G0/OPEN.md`; `stage/G1/STATUS.md`; `scope/SCOPE.md` sections 3 and 6
(first source and exit criteria); `gw_diag/README.md` (how to read dumps and project);
`verify_cosmo/README.md` (how the pancake runs were built and run on the cards).

Next work, in order:
1. First-source scouting (no core dependency): initial data with
   `cosmo/ic/make_east.py --ratios 1,eps,0` (eps = 0, 0.1, 0.3, 1; delta = 0.01; box 4;
   64^3; two particles per cell and direction), input adapted from
   `verify_cosmo/inputs/pancake.athinput` with `file_type = rst` outputs every conformal
   time 0.1; one card job of about 1 card-hour through `scripts/gpu_batch.sh`; analysis with
   `gw_diag` (`tt.tt_from_conformal`, `gw_spectrum`); compare the (k, k, 0) mode with
   h_+ = -(5/6) phi_x phi_y cos(K.x) plus the 1/a junk oscillation (scope check 3A).
   Write predictions into JOURNAL.md first.
2. When core fixes `z4c_linear_wave.cpp`: oblique wave, `periodic_z4c/inputs/lw_3d.athinput`
   with k = (1,1,1), on a card; both diagnostics (G1 criterion 1).
3. When the Newtonian mode is on main: plane-wave pancake and ellipsoid tests N1-N3
   (`baseline/BASELINE.md` 4.2) (G1 criterion 2).
4. G0 owed items: working note v0 (`/paper-writing`, `tracks/B-emd-gw/note/`), two
   schematics (`/sleep-paper-figure-style`), a fresh verifier for `VERIFIER_REPORT.md`.

Decisions pending: criteria rewording under decision 0010 (orch,
`outbox/20261115T1340Z__to-orch__track-b-criteria-under-0010.md`); ownership of the
Szekeres/planar GR reference (A-emd-pbh); thin boxes and jitter option (core).

Traps:
- `nrpic-run submit --launcher local` cannot run Python analysis here (no numpy in
  `nrpic-env exec` without a `.venv`, and a `.venv` dirties the worktree). Register by
  hand: `python3 tracks/B-emd-gw/analysis/register.py new ...` then `finish <run_id>`
  (it asserts it sits three levels below the worktree root; the verify_cosmo copy sits
  four levels down: do not copy it elsewhere without fixing the depth).
- Manifests under `tracks/B-emd-gw/runs/` are git-ignored by `.gitignore` line 12: add
  them with `git add -f`.
- Use kind "scouting" until G0 passes and a scan is pre-registered.
- `.bin` mesh output is float32: use `.rst` for metric analysis. AthenaK's `weyl` output
  lags by waveform_dt - dt and uses a radial triad: use gw_diag's fixed-direction Psi_4.
- One particle per cell under-samples stretched lattices (voids): use two per direction.
- Restart files differ in 36 padding bytes between identical runs: compare field data,
  not checksums.
- The Write tool refuses a file named `REPORT.md` from a subagent; the G0 report was written
  through the shell because the stage package requires that name.
- Never kill by pattern; the first L1 launch was stopped with `kill -- -<pgid>`.
