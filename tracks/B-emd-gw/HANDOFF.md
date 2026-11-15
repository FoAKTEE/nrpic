# HANDOFF of B-emd-gw

Written for a reader with no memory of the last session (lead session of 2026-11-15, end
of wave 2). Rewritten at the end of every session.

State in three lines: wave 2 ran four helper packages (first_source: the crossed-wave GW
source in full GR on cards and processors; newton_tests: AthenaK's Newtonian mode against
exact references; note: working note v0 and schematics; verifier: a fresh check of wave 1)
and the lead rechecked all of them from the raw outputs (`stage/REVIEW-wave2.md`). G0 is
resubmitted with every item PASS or NA in the lead's judgement; G1 is not met.
Owner: B-emd-gw, branch `track/B-emd-gw`, worktree `/data/haiyangw/nrpic/wt/B-emd-gw`.
Run next: `cd /data/haiyangw/nrpic/wt/B-emd-gw && git merge --no-edit main && harness/bin/nrpic-ctx inbox --show`

Files to read first: `STATUS.md`; `stage/REVIEW-wave2.md` (what is confirmed and what is
not); `stage/G1/OPEN.md` (what G1 lacks); `stage/G1/STATUS.md`; `first_source/README.md` and
`first_source/JOURNAL.md` (the scan, its runs, the gauge piece); `newton_tests/README.md`;
`stage/G0/VERIFIER.md` section 3 (the three weakest points of the plan); `scope/SCOPE.md`
sections 6 and 8 (criteria and risks, amended in wave 2).

Next work, in order:
1. G1 criterion 1. Oblique wave k = (1, 1, 1) and a free TT wave in the expanding box, both
   diagnostics (gw_diag TT projection and fixed-direction Psi_4). Core's sign fix is on
   `core/requests-b` (executables `scratch/core/exe/core_requests-b/`, read its READY; usable
   for scouting, decision 0013; example input `problems/tests/lw_oblique.athinput` on that
   branch). Spec: `periodic_z4c/inputs/lw_3d.athinput`. At the same time flip `xy` and `yz`
   in `periodic_z4c/analysis/refsol.py` tt_polarization (core's note). Processors suffice up
   to 64^3; use A = 1e-5 beyond 64 cells (core's T9: the Psi_4 floor grows as 1/A).
2. Noise floor and convergence of the first source: the jittered-lattice null
   (`problems/cosmo/make_waves.py --jitter A --jitter-axes y,z --seed N` on core/requests-b;
   read REQUESTS_B.md section 5 first), the scan at 1, 8, 27 particles per cell and 128^3,
   and delta = 0.0025 to widen the second-order window. About 1 card-hour; inputs and
   scripts in `first_source/` (`inputs/crossed.athinput`, `scripts/build_ic.sh`,
   `scripts/analyze_scan.py`). Write predictions first.
3. G1 products: updated architecture schematic and a data-flow diagram (paperfig.py, copy in
   `note/scripts/`), the scan and Newtonian tests in Sec. IV-V of `note/main.tex` (run ids in
   `note/scripts/common.py`, rerun `note/scripts/run_all.py` through nrpic-run, recompile,
   checker), `gauge_piece_total` of `first_source/fslib/gauge.py` into `gw_diag` with its tests,
   then an independent verifier of the wave-2 G1 runs; then `nrpic-stage collect/verify/report
   B-emd-gw G1`.

Decisions pending: orch on the verifier file name (VERIFIER.md), on the wave-1 manifests and
the moved-output run that fail `nrpic-stage verify`'s runs check, on reviewer agents for the
note, and the G0 gate itself; core on the per-species Newtonian history (blocks N2), a
fourth-order Laplacian option, an OpenMP processor build, the release of core/requests-b.

Traps:
- Analyses run through `harness/bin/nrpic-run submit --kind scouting --gate G1 ... --
  python3 <script>` with the worktree's `.venv` (exists). nrpic-run does not expand variables
  in argv: scripts must read `NRPIC_RUN_DIR` from the environment. Background runs need
  `harness/bin/nrpic-run finish <run_id>` afterwards.
- The worktree must be clean for every submit (untracked files count): commit scripts and
  predictions first.
- Never edit a script while a job executes it (first_source lost a run that way); never wrap
  `nrpic-run submit` in `timeout`.
- The flat TT strain of the zero-shift runs carries a spatial-gauge piece; report raw and
  `gauge_piece_total`-corrected values. The cross terms with the box's homogeneous anisotropy
  h0 are essential (without them the correction makes things five times worse).
- `.bin` z4c dumps of release core-v0.3 are single precision: fine for the box modes (4e-5),
  not for the null of tilde A; core/requests-b adds `double_precision = true`.
- Restart dumps with 2.1M particles are 380 MB each (12 GB per run); scratch/B-emd-gw holds
  74 GB now.
- nrpic-stage report looks for `VERIFIER_REPORT.md`; the verifier's file is `VERIFIER.md`
  (request to orch). Agent sessions avoid creating files named *REPORT.md.
- Manifests under `tracks/B-emd-gw/runs/` are tracked (no `git add -f` since 0013's sync).
- Never kill by pattern; kill by numeric pid, `scancel`, or the chain helper.
