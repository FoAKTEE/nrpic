# Lead review of the wave-2 helper packages of D-bh-dress

Lead session of 2026-11-15 (19:10-20:40 UTC). Rechecked from the artefacts (registered
outputs, figures, manifests), not from the helpers' reports. My predictions were written
into `../JOURNAL.md` (entry "lead-wave2 ... predictions", W1-W10) before the checks ran.
Review scripts: `review_wave2/` (written without the helpers' analysis code). Paths are
relative to `tracks/D-bh-dress/`; run outputs are under
`/data/haiyangw/nrpic/scratch/D-bh-dress/<run_id>/`.

| Check | Run | Outcome |
|---|---|---|
| W1-W4 es_runs: closed forms, 1+log model, particle files, mesh | D-20261115-193819-df9f812 (`es_check.png`, looked at) | all held |
| W5 spike: stationarity from the snapshots, C_crit | D-20261115-193844-df4523c (`spike_check.png`, looked at) | held |
| W6 secondary_infall: M_ta and dress from the snapshots | D-20261115-193823-88f7f86 (`infall_check.png`, looked at) | held |
| W7-W9 verifier: McVittie, capture speeds, MeshBlock counts | D-20261115-193821-8e70d61 (`verifier_check.png`, looked at) | held (W8 with the static-observer speed) |
| W10 note: clean compile, ledger rerun, three numbers | D-20261115-193951-be7b41d | held |
| superseded: first es_check run (literal `{out}` argument) | D-20261115-193755-3a53b08 | outputs moved into its run directory |

`nrpic-run verify` on every wave-2 run: PASS for 51 runs; the exceptions are listed under
"Housekeeping" below.

## 1. es_runs (ES-1 and V-1, first full-relativity runs)

Confirmed:
- [VERIFIED] Data set of run D-20261115-170213-d2c2131: `es.nrp` holds 696828 particles,
  exactly 140 with m = 1e-30 (the tracers; none with m = 0), dust mass 1.73967237 M against
  the continuum 1.73967253 M (-9.0e-8), dust at rest (u_i = 0), dust radii 36.23-59.76 M;
  `v1.nrp` holds the same 140 tracers at the same positions. (W3)
- [VERIFIED] Crossing times of R = 2M from my own cycloid with the slice energy
  E = -M(1 - f^2)/R0: 14.8269, 34.4423, 244.7364 M for R0 = 6, 10, 20 M; the helper's values
  differ by 3e-6 M. Wall (36^1.5 + 1.5 sqrt(2) tau)^(2/3) identical. (W1)
- [VERIFIED] Homogeneous 1+log model: my ODE gives alpha = 10.761, tau = 1251.4 M,
  a = 5.088 at t = 200 M, equal to the helper's table to 1e-11. (W2)
- [VERIFIED] 344 MeshBlocks: my own leaf count of the deck (56 per level 0-4, 64 at level 5)
  equals AthenaK's log of smoke run D-20261115-172413-6412daf. (W4)
- [VERIFIED] In the release source, m = 0 makes a null particle: the helper's run
  D-20261115-172821-f800e34 (figure looked at) and, independently, core's runs
  core-20261115-152835-920d573 and card run core-20261115-154030-5ba192a
  (`scratch/core/exe/core_requests-adf/READY`, correction 1). The wave-1 blocker R1 is an
  input convention; ES-1 and V-1 carry m = 1e-30 and are not affected.
- Figures looked at: `es_runs/figs/data_compare.png`, `offline_check_1d_es.png`,
  `tracer_mass_check.png`.

Not confirmed (pending):
- ES-1 (D-20261115-172726-60ba4c2, Slurm 4472) started 19:35 UTC; V-1
  (D-20261115-172730-c6d151b, Slurm 4473) at 19:47 UTC. Partial ES-1 history at
  t = 38 M: 696800 particles (the 28 tracers of groups 0-1 removed, as A5 predicted),
  M_AH = 1.0009-1.0011 since t = 15 M, minimum lapse 0.026. The three numbers of the
  package (drift against the control, wall against the closed form, crossing times in the
  run) do not exist until both runs end: `es_runs/tools/finish.sh`.
- [TO VERIFY] The finder's mean coordinate radius of the horizon is 2.0 M at t = 20-30 M
  and 2.6 M at t = 37 M (D-pre-4 at M/8: 1.34 M at 50 M). If it keeps growing it leaves the
  M/8 region (|x| < 6 M) before t = 200 M; watch `horizon_summary` column 11.

Wrong or weak:
- The wave-1 prediction 4 (`G1/STATUS.md`: "alpha to about 4.9 by tau = 200 M") mixed
  proper and coordinate time; the helper's A2 states it against coordinate time (alpha 10.8
  and tau 1251 M at t = 200 M). Kept as written (predictions are not edited); the outcome
  will be judged on A2.
- [JUDGEMENT, examined and dismissed] Whether the dust leaves the box: with zero initial
  shift the plateau dust is at rest in the coordinates (the slice normal is the dust's
  velocity and alpha is uniform there), so its areal radius grows to about 265-305 M by
  t = 200 M while its coordinate radius stays below 60 M. The snapshots will show it.
- ES-1G (core's lapse_leak) is not run: `scratch/core/exe/core_gauge/` does not exist.
  Decision: not in this wave; it runs (about 1 card-hour, inside D's 30 card-hours of
  decision 0014) as soon as core publishes the executable.

## 2. spike (Kerr spike, D-pre-2)

Confirmed:
- [VERIFIED] Stationarity of the a = 0.8 run D-bh-dress-20261115-172611-1e40191 from the
  snapshots with my own reader and Boyer-Lindquist radius: late/early-half count ratios
  0.997, 1.005, 0.999, 1.000, 1.000 in 0-4, 4-6, 6-10, 10-16, 16-40 Gm; mean L_z in 0-4 Gm
  2.260 (t = 0) and 2.267 (late half); 48000 particles at every snapshot; smallest r
  2.29 Gm. (W5)
- [VERIFIED] C_crit(a = 0.75, E = 0.97, L_z = 2) = 10.3209 at r_u = 2.834 Gm from my own
  Carter C_V; C_V(30 Gm) = 7.0887 is the 7.09 the registered check printed (endpoint).
- Figures looked at: `kerr_ref_hernquist.png`, `kerr_main_profile.png`,
  `slice_control.png`.

Fixed (small): `spike/kerr_reference.py` evaluates the caption check at r = 15 Gm inside
the bound region (commit 3a53b08); the registered run -171615-8adbbdd still holds 7.09 and
the next rerun prints 10.32.

Not confirmed:
- [TO VERIFY] The Hernquist Kerr curves 4 % (a = 0.8 peak) to 18 % (inner edge) below
  FdRW. I did not redo the action matching at L_z != 0; a second agent is still needed.
- [TO VERIFY] FdRW's constant-f theta = pi/3 curve inside 8 Gm.
- New, [TO VERIFY]: the time-averaged counts of the three inner ranges are all below the
  reference: 0.959, 0.982, 0.990 of expected (z = -1.1, -0.9, -1.0;
  `kerr_main_analysis.json` of D-bh-dress-20261115-174954-786ddcc), while t = 0 is
  0.929, 1.019, 0.992. Each is within noise, the common sign is not; a second seed (or
  4x the particles inside 10 Gm) decides whether the sampler or the reference is 1-3 %
  off at r < 10 Gm.
- The particle budget for a self-gravitating spike (8.6e7 inside 16 Gm) rests on a noise
  law extrapolated from the cluster test [JUDGEMENT], as the helper says.

Small defect not fixed: `spike/figs/slice_control.png` has overlapping y tick labels where
the panels touch (cosmetic).

## 3. secondary_infall (Newtonian mode, D-pre-3)

Confirmed:
- [VERIFIED] With my own implementation of the stated definitions on the snapshots:
  N128c M_ta 2.59656 M, dress 0.79755 M; N64c 2.59656, 0.79662; N128Lc 4.81587, 2.15366 at
  a/a_i = 8: all within 0.07 % of the helper's 2.597, 0.797, 4.816, 2.154. The mass inside
  the outermost zero of the mean radial velocity is 0.998 M_ta in all three runs, so the
  turnaround definition is not what sets M_ta. (W6)
- Figures looked at: `nm_profiles.png`, `nm_selfsim.png`, `nm_clumpstab.png`.

Observation from `nm_clumpstab.png`: the clump alone, displaced by 0.05 dx from a cell
centre, oscillates about it with a total momentum |sum m v| of 0.01-0.1 M c, and from a
vertex up to about 0.3 M c: the mesh self-force of a sub-cell object does not conserve
momentum. In the production runs (cell centre, no offset) the centre of mass stays within
6.6e-4 dx. This supports the helper's request that core document it and publish the point
mass; `newton_pm_*` is now in `scratch/core/exe/core_requests-adf/` (READY item 5), so N128c
can be rerun with a fixed point mass.

Not confirmed: the self-similar comparison beyond the figure (not recomputed); the cause of
the dust beyond the outermost caustic (untested, as the helper says).

Wrong: nothing found. The criterion of `scope/SCOPE.md` ("slope -9/4 +- 0.05 on
[2 dx, r_ta/2]") is wrong, see section 5 (C4).

## 4. note (working note v0)

Confirmed (W10, run D-20261115-193951-be7b41d): a clean copy of the tracked
note compiles with latexmk to 10 pages, 0 undefined references, 0 overfull boxes;
`ledger.py` rerun gives `ledger.tex`, `parameters.tex`, `claims.md`, `claims.json` byte for
byte; drift 2.952888e-4 (M/8), wall 46.99-74.29 M, spike peak 0.86990e8 at 7.579 Gm equal
the run outputs. Claims remark 1 (0.654 against 0.625) checked in the two run outputs.
Pages 1-3 read.

Fixed (small): `note/main.tex` Sec. III C said the growing lapse "shortens the time step".
The Z4c step is set by the finest cell (`athenak/src/z4c/z4c_newdt.cpp`) and the ES inputs
set no `dt_expansion` (`particles/nrpic.cpp:1314-1346`); the sentence now says that a
coordinate step advances the dust by alpha times as much proper time. Recompiled (10 pages,
clean); manuscript checker: 2 of 16 checks with candidates, both in the ledger appendix and
the registration scripts (the guide's exception).

Not done: the paper-writing reviewers of step 4; journal data of the 11 references.

## 5. verifier (fresh context, stage/G0/VERIFIER.md)

| Claim | Verifier | Lead check | What the track does |
|---|---|---|---|
| C1 ES slice | CONFIRMED (only eps = 5.58e-3 exists) | not rechecked | data sets at eps = 0.01, 0.03 before G2 |
| C1b release reproduces t = 0 | CONFIRMED | not rechecked | R7 closed for t = 0 |
| C2 D-pre-4 floor | CONFIRMED for the drift; excursions common to M/8 and M/16, finder offset changes sign, M/8 in transient at 50 M | figure `v2_drift.png` looked at: as stated | floor of ES-1 taken from V-1 (running); floor windows from t0 = 100 M; boundary control stays open (R4) |
| C3 turnaround numbers | CONFIRMED | lead's closed form of wave 1 agrees | none |
| C4 r^-9/4 | NOT CONFIRMED as a G1 criterion: only the asymptote (lambda << 1e-2); an exact code fails "-9/4 +- 0.05 on [2 dx, r_ta/2]" | `v4b_compare.png` looked at | D-pre-3 is judged against the self-similar m(lambda) and the matched shells (G1/STATUS.md); proposal to orch |
| C5 capture | CONFIRMED with a correction: speeds 0.221 (16.1 M), 0.113 (33.4 M), not 0.12-0.25 | W8: 0.2210, 0.1130 (static observer; L/r_ta is 0.2266, 0.1137) | numbers replaced in G1/STATUS.md |
| C6 constant-f spike | CONFIRMED; "3" and "15 percent" are SFW's prose | 2.590 and 9.22 % in run -145636-5259f48 | criteria restated to 2.59 and 9.2 % |
| C7 McVittie | CONFIRMED: -1.20e-3, -1.10e-2, -0.151 | W7: -1.2024e-3, -1.0998e-2, -0.15105 | the null test with matter subtracts or bounds this term (G2) |
| C8 cost | WRONG beyond M/16: 3200, 4712 (7848) MeshBlocks, not 456, 512 | W9: AthenaK's own logs of run -171953-908afff | G2 re-costed before submission; ladder and block size chosen with `-m` counts; G2 estimate about 28 of 30 card-hours until then |
| Weak point 3 (G1 numbers rounded or prose) | | | corrected in G1/STATUS.md (remarks of the note's claims check included) |
| Weak point 4 (definitional McVittie term) | | | G2 criterion text to state it (outbox to orch) |

The verifier's own defect (time-averaged density of `v4_shells.py` limited to
r < 0.06 r_ta, unused) is recorded, not fixed.

## Housekeeping found by `nrpic-run verify`

- Nine verifier runs registered by hand have no `sha256sums.txt` (D-20261115-171508-94e8cb1,
  -171532-ba23a99, -171534-ff5b0e9, -171543-d966aba, -171545-d7e01a7, -171733-633d422,
  -171818-a5aefe8, -171953-908afff, -173149-7c6dd72); their outputs are not checksummed.
- Inputs changed since the run: `secondary_infall/nm_run.py` (vertex runs -170700, -170703,
  -170706) and `nm_analyze.py` (analyses -174734, -180251, -185248, -190403); the final
  analyses -190541 and -190543 verify.
- Files added after finish: `v1_es_slice.png` (-170002-8cefc3e), the moved
  `es.horizon_summary_0.txt.from_cwd` (-170326-dfb2a02).
- `nrpic-run submit` does not substitute `{out}`; my run D-20261115-193755-3a53b08 wrote into
  `<worktree>/{out}/` (moved into its run directory, superseded). The verifier saw the same
  with `$NRPIC_RUN_DIR`. Scripts should read `NRPIC_RUN_DIR` themselves.
