# JOURNAL of D-bh-dress

Append-only, newest at the bottom, one entry per session:
`## <UTC time>  session <name>  commits <a>..<b>  runs <ids>` followed by
did / found / evidence / changed my mind about / open. Predictions are written here before
a test runs, outcomes after.

## 2026-11-15T14:55Z  session lead-wave1 (Opus)  predictions of the lead's re-checks, written before they run

Helpers' journals: `scope/JOURNAL.md`, `einstein_straus/JOURNAL.md`, `spike/JOURNAL.md`,
`secondary_infall/JOURNAL.md`, `puncture_drift/JOURNAL.md`. The lead re-checks each package
from its artefacts; scripts under `analysis/lead_checks/`, runs registered.

Already run before this entry was written (recorded honestly, no prediction on file):
the 48 symbolic identities of D-pre-1 (rerun D-bh-dress-20261115-065141-5fdc744, local-time
stamp, see below) and my own quadrature of a, m_p (scratch/D-bh-dress/tmp/lead/es_check_a.py).

- L1 (D-pre-4, `analysis/lead_checks/drift_recheck.py`, own code on the raw
  `punc.horizon_summary_0.txt`): the drift of a 20 M running mean between 50 and 490 M is
  +3.0e-4 (M/8) and +3.7e-5 (M/16) within 20 per cent; at M/16 max |D| on [50, 210] M is
  below 2.5e-5; the 5 M running mean swings about 9e-5 peak to peak in 220-255 M at BOTH
  resolutions (within 30 per cent of each other); |S|/M^2 after 5 M below 3.3e-7 / 5.7e-9.
  Refuted by: a drift that differs by more than 20 per cent, or excursions that differ by
  more than 30 per cent between resolutions (then the boundary attribution weakens).
- L2 (scope): rerunning `scope/scoping_estimates.py` reproduces every number of
  `scoping_table.txt` of run D-bh-dress-20261115-120304-795eee9 to all printed digits
  (deterministic code). Refuted by any differing digit.
- L3 (D-pre-2): rerunning `spike/spike_reference.py` reproduces the peaks 0.8699e8 GeV/cm^3
  at 7.58 Gm (constant f) and 2.44e18 at 7.75 Gm (Hernquist, canonical action) to 4 digits.
- L4 (D-pre-3, own closed form, `analysis/lead_checks/infall_recheck.py`): cold dust in
  the unperturbed Hubble flow around a seed M in EdS, shell energy E = -M/r_i, enclosed
  mass mu = M + eps^2 r_i^3/2, radial Kepler cycloid. Predicted: M_ta/M = 1.525 and 2.628
  at a/a_i = 2, 4 for every eps (to 1e-3); the mass that has reached r = 0 by a/a_i = 2 lies
  within 2 per cent below the helper's absorbed mass 1.193 (absorption at 2 M_bh happens
  slightly earlier than arrival at r = 0); coefficient (M_ta - M)/(M a/a_i) -> 0.5648.
  Refuted by: M_ta off by more than 1e-3, or the collapse mass more than 2 per cent away.
- L5 (analytic, second-agent check of `secondary_infall/RUNS.md` section 1): the LTB
  mapping E(r) = -M/r, M(r) = M + (4 pi/3) rho_i r^3 satisfies the Hamiltonian and
  momentum constraints on the dust's synchronous slice and gives K_ij = -H_i gamma_ij in
  the dust. I expect it to hold only if dust reaches r = 0 or the hole carries the mass
  of the removed core (an "over-massive" hole), otherwise E differs from -M/r.
- L6 (analytic, second-agent check of `scope/REFERENCES.md` section 2): McVittie apparent
  horizon at 1 - 2m/R = H^2 R^2, so d ln M_AH / d ln a = -12 (mH)^2 in EdS.

### Outcomes of L1-L6 (lead, 2026-11-15T15:05Z)

- D-pre-1 symbolic rerun D-bh-dress-20261115-065141-5fdc744 (this id is LOCAL time, UTC-8,
  as are the eight einstein_straus ids 0426xx-0434xx: `einstein_straus/nrun.py` used
  datetime.now(); fixed to UTC in 5259f48, ids not renamed because they are referenced):
  48 of 48 identities pass, same count as D-bh-dress-20261115-042626-f3da881. My own
  quadrature (scratch/D-bh-dress/tmp/lead/es_check_a.py, written without es_model.py):
  a = 0.9765922286441, m_p = 1.023968828206, u(0) = -0.0234077713559, rbar_throat =
  0.52425608057, equal to es.json to 1e-13. H R_w^3 check: sharp-wall ES H = 5.590e-3/M
  for R_w = 40 M against 5.581e-3 of the smooth-edge data (expected: rho_0 fixed at 44 M).
  Figures looked at: es_expansions, es_reference, check_3d, code_t0. Confirmed.
- L1 confirmed (run D-bh-dress-20261115-145546-5259f48, `lead_drift_recheck.png` looked
  at): drift 50 -> 490 M of the 20 M mean +2.95e-4 (M/8), +3.67e-5 (M/16), as the helper;
  M/16 max |D| on [50, 210] M 8.2e-6; 5 M mean peak-to-peak in 220-255 M 9.33e-5 (M/8),
  9.28e-5 (M/16); raw 300-340 M 1.52e-4 / 1.48e-4; |S|/M^2 after 5 M 1.8e-7 / 5.6e-9.
  Floor recomputed by hand from these: 8.2e-6 + D_fs 8.0e-6 + 2 sqrt(2) 3.5e-6 = 2.6e-5,
  agreeing with the helper's 2.5e-5 at T = 156 M. Defect found: `figs/drift_floor.png`
  draws the conservative floor (sigma over 50-500 M, about 5e-5), not the headline
  2.0-2.5e-5; README annotated.
- L2 confirmed (run D-bh-dress-20261115-145611-5259f48): `scoping_table.txt` identical.
- L3 confirmed (run D-bh-dress-20261115-145636-5259f48): `reference_table.txt` identical
  except the wall time; peaks 0.86990e8 GeV/cm^3 at 7.579 Gm, 2.4374e18 at 7.746 Gm.
  Source locators checked: FdRW `kerrdm.tex:918-919` footnote (missing r^2/Delta in SFW
  eq. 3.19) and SFW `SFWpaper.tex:443` ("a factor of three smaller at its peak", and the
  8Gm -> 4Gm sentence). New: SFW's "factor of three" is 2.59 from their own curve (the
  package's peak ratio); added to the kb request.
- L4 confirmed (run D-bh-dress-20261115-145610-5259f48, `lead_infall_recheck.png` looked
  at): M_ta/M = 1.52542, 2.62815, 4.87098 at a/a_i = 2, 4, 8 for all eps; mass that has
  reached r = 0: 1.19019, 1.82763, 3.21526 (0.24, 0.02, 0.12 per cent below the helper's
  absorption-at-2M values, as predicted); coefficient 0.55811 at a/a_i = 100, limit
  0.56475. The helper's M_ta = 2.630 and 4.875 are 7e-4 and 8e-4 relative above the
  closed form (shell-sampling or snapshot timing; immaterial). The secondary_infall
  helper's remark on scope/JOURNAL.md is not a defect: "over a quadrupling 1.63 M" is
  the dust that turned around (2.63 M with the hole), as the preceding sentence states.
- L5 confirmed with a condition (by hand): with E = -M/r and M(r) = M + (4 pi/3) rho_i r^3
  the dust's synchronous slice has KT = KL = -H_i, (dR/dl)^2 = 1 + 2E = 1 - 2M/r, and the
  Misner-Sharp relation (dR/dl)^2 = 1 - 2m/R + R^2 KT^2 holds identically, so both
  constraints are satisfied (momentum: KL = d(R KT)/dR with KT = -H). With a vacuum core
  of areal radius r_c the same E(r) needs a hole of Misner-Sharp mass
  M + (4 pi/3) rho_i r_c^3 = M (1 + 13.5 eps^2) for r_c = 3 M ("over-massive"), and inside
  r_c a vacuum f-slice with f(r_c) = H r_c (r_c/2M_h)^(1/2) (KT continuous), f(2M_h) = 0.
  Each shell then follows the radial Kepler law exactly in proper time and areal radius;
  the apparent-horizon mass on any spherical slice is m of the shell at R = 2m. The
  mapping in `secondary_infall/RUNS.md` section 1 is correct with this condition.
- L6 confirmed (by hand): McVittie radial null rays dR/dt = f^(1/2)(HR +- f^(1/2)),
  f = 1 - 2m/R; apparent horizon f = H^2 R^2, R_AH = 2m(1 + 4 m^2 H^2 + O(m^4 H^4)),
  d ln M_AH/d ln a = 4 m^2 d(H^2)/d ln a = -12 (mH)^2 in EdS. The REFERENCES.md text
  called the stalling family "outgoing"; corrected.
- Further review findings (no rerun): (i) the einstein_straus README said the 1+log
  lapse grows like exp(6Ht) in the dust; along the dust alpha = 1 + 6 ln a (d tau =
  alpha dt), about 4.9 at tau = 200 M (run D-bh-dress-20261115-145950-23fa1c7); README
  corrected. (ii) The D-pre-4 floor belongs to an asymptotically flat vacuum puncture with
  the boundary at 128 M and the standard puncture gauge; the first Einstein-Straus run
  has dust, a Painleve-Gullstrand exterior, the boundary at 180-256 M and possibly another
  lapse, so its floor must come from a matched vacuum control (same table without dust),
  not from D-pre-4 alone [JUDGEMENT]. (iii) The tracer side finding of puncture_drift
  (release card executable, run D-bh-dress-20261115-143918-a5c125a, figure looked at) is
  a blocker for trusting any particle push on cards until core explains it. (iv) The
  scope cost model shows that the D-pre-1 data set as generated (dust to 106 M) costs
  11.3 card-hours at M/16 for 200 M; with the outer dust edge at 60 M, 2.9 (M/16) and 1.4
  (M/8) (run D-bh-dress-20261115-145950-23fa1c7).
- Caveat on these checks: I read the helpers' reports before checking, so they are not
  an artefact-only verification in the sense of CLAUDE.md (models and roles); a fresh
  verifier is still needed for the gate (stage/G0/OPEN.md).

## 2026-11-15T15:20Z  session lead-wave1 (Opus)  commits 5259f48..d157621  runs D-bh-dress-20261115-065141-5fdc744, -145546-5259f48, -145610-5259f48, -145611-5259f48, -145636-5259f48, -145950-23fa1c7

- did: merged main (up to date); re-checked the five helper packages from their artefacts
  (predictions L1-L6 and outcomes above); fixed three wording defects (McVittie ray family
  in scope/REFERENCES.md; 1+log lapse growth in einstein_straus/README.md; the floor
  figure note in puncture_drift/README.md) and the local-time run ids of
  einstein_straus/nrun.py; wrote stage/G0 (REPORT, EVIDENCE, OPEN, CHECKLIST) and
  stage/G1 (STATUS, CHECKLIST) with the first full-relativity run ES-1 and its
  prediction; 12 outbox files; STATUS, HANDOFF, RISKS.
- found: everything the helpers claimed that I re-ran was reproduced (symbolic identities
  48/48; drift +2.95e-4 / +3.67e-5; scoping table and spike reference identical; infall
  masses within 1e-3 by my own closed form). New: the ES data set as generated costs 11.3
  card-hours at M/16 for 200 M (dust to 106 M), 2.9 with the outer edge at 60 M; along
  the dust the 1+log lapse grows as 1 + 6 ln a, not exponentially; the McVittie drift
  formula is right but the ray family was mislabelled; the LTB mapping of D-pre-3 holds
  only with an over-massive hole when a vacuum core is cut out.
- evidence: runs above; figures looked at by the lead: einstein_straus es_expansions,
  es_reference, check_3d, code_t0; spike ref_hernquist, stationarity_profile;
  secondary_infall selfsimilar, growth; puncture_drift drift_floor, tracer_check; lead
  lead_drift_recheck, lead_infall_recheck, first_run_plan.
- changed my mind about: the D-pre-4 floor as the floor of the null test. It is the floor
  of an asymptotically flat vacuum puncture; ES-1 needs a matched vacuum control V-1.
- open: Kerr spike; AthenaK Newtonian-mode run; ES-1 and V-1 (blocked by core); working
  note v0, schematics, fresh verifier; boundary control for the D-pre-4 excursions. No
  card job submitted (no card-hours named for this session); no pending runs.
- helpers' journals: scope/JOURNAL.md, einstein_straus/JOURNAL.md, spike/JOURNAL.md,
  secondary_infall/JOURNAL.md, puncture_drift/JOURNAL.md.

## 2026-11-15T19:30Z  session lead-wave2 (Opus)  predictions of the lead's wave-2 re-checks, written before they run

Scripts in `stage/review_wave2/` (mine, written without the helpers' analysis code; they
read only registered outputs). Each check names the helper's claim and what refutes it.

- W1 (es_runs, closed forms) My own cycloid with the slice energy E = -M(1 - f^2)/R0
  (f of `es_model.EinsteinStrausBH.f`, outgoing start dR/dtau = f sqrt(2M/R0)) gives the
  crossings of R = 2M at tau = 14.83 (R0 = 6), 34.44 (10), 244.7 M (20) and the wall
  (36^1.5 + 1.5 sqrt(2) tau)^(2/3) = 46.99, 56.80, 65.84, 74.29 M at tau = 50..200 M.
  Refuted by a difference above 0.01 M from `es_runs/results/predictions.json`.
- W2 (es_runs, 1+log model) My integration of d alpha/dt = 6 alpha H(a), da/dt = alpha H a
  (EdS, H = H0 a^-1.5, H0 = 5.58116e-3) gives alpha = 1 + 6 ln a and at t = 200 M
  alpha = 10.8, tau = 1.25e3 M; refuted by more than 1 per cent from the helper's table.
  [JUDGEMENT] With zero initial shift the plateau dust is at rest in the coordinates, so
  no dust reaches the outer boundary even though its areal radius grows about fivefold.
- W3 (es_runs, data) es.nrp holds 696828 particles, of which exactly 140 have m = 1e-30
  (the tracers) and the rest sum to 1.73967 M; v1.nrp holds the same 140 tracers only.
  Refuted by any tracer with m = 0 or a dust mass off by more than 1e-6.
- W4 (es_runs, mesh) my own leaf count of the input geometry is 344 MeshBlocks, equal to
  the number in the smoke run's log; refuted by any other number.
- W5 (spike, K2) my own counts by Boyer-Lindquist radius from the Kerr-Schild snapshots of
  run D-bh-dress-20261115-172611-1e40191 (a = 0.8): late-half over early-half mean counts
  within 1 per cent in 4-6, 6-10, 10-16 Gm, mean Lz in 0-4 Gm 2.27 +- 0.05; my own C_V
  from the Carter radial potential has its local minimum 10.3 at a = 0.75, E = 0.97,
  Lz = 2 (FdRW caption). Refuted by a ratio off by more than 2 per cent or C_crit off by
  more than 0.05.
- W6 (secondary_infall) my own implementation of the definitions in nm_analyze.py
  (turned: v_r < 0 at some snapshot; passed: other side of the centre or outgoing after
  turning) on the snapshots of N128c (D-20261115-171503-4262f03) gives M_ta = 2.597 M and
  dress 0.797 M at a/a_i = 4 to 0.3 per cent; the mass inside the outermost zero of the
  mean radial velocity is within 10 per cent of M_ta [JUDGEMENT]. Refuted beyond these.
- W7 (verifier C7) McVittie: x = R_AH/(2m) solves x = 1 + 4 h^2 x^3, and
  d ln M_AH/d ln a = -12 h^2 x^2/(1 - 12 h^2 x^2) (my derivation, EdS H ~ a^-1.5):
  -1.20e-3, -1.10e-2, -0.151 at h = 0.01, 0.03, 0.1, as the verifier printed; refuted by
  a difference in the third digit.
- W8 (verifier C5) capture of a particle at radial rest at r_ta in Schwarzschild: the
  threshold L solves (1 - 2/r_ta)(1 + L^2/r_ta^2) = V_max(L); L/r_ta = 0.221 at
  16.1 M and 0.113 at 33.4 M as the verifier printed; refuted beyond 0.002.
- W9 (verifier C8) the MeshBlock counts 3200 (M/32) and 4712 (M/64) are in the logs of
  run D-20261115-171953-908afff as printed by AthenaK itself; refuted by other numbers.
- W10 (note) the note compiles from a clean copy with latexmk to 10 pages; the ledger
  script reproduces the ledger table byte for byte; three ledger numbers I pick (the drift
  +2.95e-4, the wall at tau = 200 M, the spike peak 0.8699e8) equal the run outputs.

## 2026-11-19T15:20Z  session lead-wave2b (Opus)  predictions of the lead's wave-2b re-checks, written before they run

Outcomes of W1-W10 (lead-wave2, 2026-11-15): in `stage/REVIEW-wave2.md` sections 1-5 (that
session was cut off before its journal entry; this entry and the next close it).
Script `stage/review_wave2/es_finish_check.py` (mine; written without opening the helper's
`analyse.py`, `es_extra.py` or `probe_fronts.py`); it reads only the registered outputs of
ES-1 (D-20261115-172726-60ba4c2) and V-1 (D-20261115-172730-c6d151b). Exact references from
`es_runs/results/predictions.json` (checked as W1).

- Y1 horizon mass (column 3 of the finder summaries): M_AH(100 M) - 1 = +9.55e-4 (ES-1),
  +9.37e-4 (V-1); max over 100 <= t <= 200 M of |M_AH(t)/M_AH(100 M) - 1| = 3.40e-4 and
  1.37e-4; max |drift(ES-1) - drift(V-1)| = 2.04e-4, 1.49 times V-1's floor, below the 3
  of the refutation criterion. Refuted by a relative difference above 2 per cent in any of
  these or a ratio of 3 or more.
- Y2 wall (tags 56-69): my own areal radius R = r sqrt(B), B = (tr gamma - n.gamma.n)/2
  (tangential part of gamma_ij at the particle, positions from `traj.bin`, metric and
  proper time from `trajmet.bin`), against (36^1.5 + 1.5 sqrt(2) tau)^(2/3): max relative
  error for tau <= 200 M 2.2e-3 (ES-1), 1.6e-3 (V-1), each within 10 per cent of these
  numbers, both below the 1 per cent of criterion 2. Refuted beyond either.
- Y3 crossings of R = 2M, linear interpolation in tau: groups R0 = 6 and 10 M (tags 0-27)
  14.826 and 34.437 M within 0.01 M of the helper's numbers (exact 14.8269, 34.4423 M);
  group R0 = 20 M (tags 28-41) crosses in ES-1 near t = 177 M at tau = 244.1-244.5 M and not
  in V-1 by t = 200 M. Refuted beyond 0.01 M or by another crossing pattern.
- Y4 1+log lapse (history column 13, probe at x = 46 M): 1.292, 1.662, 1.636 at t = 10, 25,
  50 M (A2's model 1.377, 2.096, 3.577); proper time of the +x tracer of R0 = 48 M at
  t = 200 M 279.5-279.9 M. Refuted beyond 1e-3 in the lapse or 0.5 M in tau.
- Y5 dust and wall, last snapshot of ES-1 (t = 200 M) and the snapshot at t = 100 M: for each
  of the 14 wall tracers, every dust particle within 10 degrees of its direction lies
  outside it in coordinate radius by more than 0.1 M. Refuted by any dust particle inside.
- Y6 cost from the manifests: 0.769 + 0.672 = 1.44 card-hours. ES-1G (Slurm 4636) has used
  no card time at the time of the check.

Outcome of Y1-Y6 (run D-20261119-151039-b2ce968; the same numbers and a figure with legible
titles in D-20261119-151119-58b2102, `es_finish_check.png` looked at). My first run
D-20261119-151012-b4afa8a read S_x (trajmet column 15) as the proper time (my index slip:
the proper time is column 13): its Y2-Y4 are void, Y1, Y5, Y6 are the same; it stays on
record, superseded.
- Y1 HELD: M_AH(100 M) - 1 = +9.55e-4 / +9.37e-4; max |drift| over 100-200 M 3.40e-4 /
  1.37e-4 (both at t ~ 196-200 M; over 100-165 M 9.3e-5 / 4.2e-5); max |ES-1 - V-1| 2.04e-4
  = 1.49 x V-1's floor; the two horizon masses split by more than 1e-9 from t = 19.5 M.
- Y2 HELD: wall, tau <= 200 M, max |R/R_w - 1| = 2.196e-3 (ES-1, axis tracers), 1.594e-3
  (V-1, diagonal tracers), my areal radius from the tangential part of gamma_ij.
- Y3 HELD: ES-1 14.8263 and 34.4368 M (V-1 14.8263, 34.4365) against exact 14.8269 and
  34.4423 M; group R0 = 20 M in ES-1: 14 of 14 cross, mean tau 244.33 M at mean t = 177.3 M
  (exact tau 244.74 M); in V-1 none, largest tau at the end 243.43 M.
- Y4 HELD: plateau probe 1.2921, 1.6619, 1.6355 at t = 10, 25, 50 M against my own model
  1.377, 2.096, 3.577 (the A2 failure is real); tau of group R0 = 48 M at t = 200 M
  279.49-279.88 M (V-1: 248.53-248.62 M).
- Y5 HELD: smallest margin of dust outside the wall tracer's 10-degree cone 0.154 M
  (t = 100 M) and 0.126 M (t = 200 M), on the diagonal tracers; 0.38 M on the axis tracers;
  no dust inside. (The helper's fitted-wall margin 0.136 M at 200 M is the same picture.)
- Y6 HELD: 0.7694 + 0.6719 = 1.441 card-hours; `nrpic-run budget`: G1 used 3.62, reserved
  0.98 (ES-1G, Slurm 4636 still pending at 15:12 UTC), left 25.40 of 30.

## 2026-11-19T15:35Z  session lead-wave2b (Opus)  commits 6bd89c14..(this entry)  runs D-20261119-151012-b4afa8a (superseded), D-20261119-151039-b2ce968, D-20261119-151119-58b2102

Closes the cut-off lead session of wave 2 as well (its outcomes W1-W10 are in
`stage/REVIEW-wave2.md` sections 1-5; it wrote no journal entry, STATUS or HANDOFF).
- did: merged main (decision 0016, wave-2b harness); read the brief ranges (S4, track sheet,
  gates, context protocol); rechecked the wave-2b helper `es_finish` from its artefacts with
  my own script (Y1-Y6, predictions above); looked at eleven of its figures and at mine;
  `nrpic-run verify` on ES-1, V-1 and all twelve analysis and pre-flight runs (PASS); wrote
  `stage/REVIEW-wave2.md` sections 6-9; recollected the G0 and G1 checklists, set G0 C17 to
  PASS (VERIFIER.md, 0016 items 1 and 4) and G1 C2 to PASS (ES pipeline on AthenaK output),
  rewrote G1 STATUS/OPEN/REVIEW/EVIDENCE and G0 OPEN; ran nrpic-stage verify and report for
  G0 and G1; posted two requests (orch: verifier and rulings for G1; core: the ES test outcome
  in core_gauge/READY); rewrote STATUS, HANDOFF, RISKS. No inbox messages were waiting.
- found: every number of the helper's outcome I recomputed agrees (drift windows to the
  printed digits, wall 2.196e-3 / 1.594e-3, crossings 14.8263 / 34.4368 M, the 1+log lapse,
  dust outside the wall by at least 0.126 M, 1.44 card-hours). New from my check: the
  horizon's coordinate radius stays below 2.6 M, inside the M/8 region (closes the wave-2
  [TO VERIFY]).
- evidence: runs above; figures `es_finish_check.png` (mine) and the helper's
  `horizon_mass`, `wall`, `lapse_probes`, `axis_profiles`, `extra_horizon`,
  `extra_tracers_vs_t`, `probe_fronts_t100_V-1`, `es1g_model`, `preflight`.
- changed my mind about: ES-1 as the null test. With 1+log it is a vacuum-bubble benchmark
  (wall, crossings, horizon against the control), not a null test in expanding dust; that
  needs a slicing that follows the dust (ES-1G). And the floor: on the ES mesh it is set by a
  late common drift of open cause, not by the D-pre-4 number.
- failed on my side: run D-20261119-151012-b4afa8a read S_x as the proper time (index slip);
  superseded within a minute, kept on record.
- decided: ES-1G prediction G1 judged as written on R0 = 40 and 48 M (R0 = 48 M reported
  separately); late-drift controls after ES-1G in the order V-1 with the boundary at 384 M,
  then V-1 at M/16; no card run submitted in this session (none allotted).
- open: ES-1G (Slurm 4636, queued, 0.98 card-hours reserved); cause of the late drift; G1
  items C7 (orch ruling), C9 (schematic), C17 (fresh verifier); the wave-3a package
  `flux_tools/` (unreviewed).
- addendum (15:50Z): `nrpic-stage verify` (G0 and G1, `--no-checksums`, commit b7777f44,
  after merging main again: decision 0018) fails only `runs`, for the queued ES-1G
  (status submitted); the note's claims check was rerun first (D-20261119-154336-1480741)
  because the rewrite of stage/G1/STATUS.md moved its line locators (values unchanged).
  `nrpic-stage report`: G0 verdict FAIL for that one reason only (lead's note in the
  report: complete for review); G1 FAIL (C7, C9, C17 open; no verifier). A first full G0
  verify on e3d014f was stopped by PID (stale commit) and a full G1 verify on 792b185 was
  stopped by PID after main moved.

## 2026-11-21T06:35Z  session lead-wave3-batch2a (Opus)  predictions of the lead's wave-3 re-checks, written before they run

State found: main merged (release core-v0.4); G0 signed (coord/GATES.md, 2026-11-20); no D
job in Slurm; four runs left open by the cut burst of 2026-11-20 (point shells
D-20261120-222515-c2ef5b8, R8 D-20261120-222550-e472402, drift pre-flight
D-20261120-222820-94f20b3, card run (b) V-1B D-20261120-222625-63abd72: chain DONE (tlim) at
16:43 PST) all ended with exit 0 and were closed by me with `nrpic-run finish` (V-1B: 0.7775
card-hours, drift_controls' Pb5 predicted 0.78 +- 10 per cent). Packages finished since the
wave-2b lead: es_runs (ES-1G closed), verifier_g1 (VERIFIER.md). Cut and still open:
flux_tools (ES-F not submitted), drift_controls (V-1B not analysed), secondary_infall (runs
of wave 3 not analysed), note (v1 text and figures, PDF not rebuilt).
Script `stage/review_wave3/wave3_check.py` (mine; readers copied from my predecessor's
`stage/review_wave2/es_finish_check.py`, not from the helpers' code); it reads only
registered outputs. File layouts: header of the finder summaries (`# 1:iter 2:time 3:mass
... 11:meanradius 12:minradius`), traj.bin 8 doubles and trajmet.bin 17 doubles
(`athenak/src/particles/nrpic_io.cpp:803-814`, proper time index 12), `docs/FORMATS.md`
(`.nrp`).

- Z1 ES-1G horizon (D-20261119-142633-6f72922, `es.horizon_summary_0.txt`): M_AH(100 M) - 1
  = +1.141e-3; drift M(t)/M(100) - 1 over 100-199.5 M reaches +6.96e-3 (minimum -4.17e-4);
  mean coordinate radius 1.40 M at t = 25 M and 0.78 M at 199.5 M. Refuted by a difference
  in the third digit.
- Z2 ES-1G tracers (traj/trajmet): wall tags 56-69, my areal radius r sqrt(B) against
  (36^1.5 + 1.5 sqrt(2) tau)^(2/3): max |R/R_w - 1| over the whole run at most 1.7e-4
  (tau to about 206 M); group R0 = 6 M (tags 0-13) crosses R = 2M at tau 14.8261 (exact
  14.82692, claimed error -8.6e-4 M, I accept +-2e-4 M of that); group R0 = 48 M (tags
  84-97) proper time at the last record (t = 200 M) 205.3 M +- 0.3 M. Refuted beyond these.
- Z3 V-1B (D-20261120-222625-63abd72), drift_controls' prediction Pb1 (entry 2): D(199.5 M)
  from t0 = 100 M above -5e-5. My own odds [JUDGEMENT]: 60 per cent that Pb1 holds, given
  that ES-1G's exterior mass is lost from the faces inward (es_runs K1) but V-1 has no
  exterior matter; I expect at least the sign of V-1's late drift (-1.37e-4) to be reduced
  in size by half. Also Pb2: V-1B and V-1 masses separate by more than 1e-6 between 110 and
  165 M. This is a first reading for the lead's plan; drift_controls' full judgement
  (Pb1-Pb5 with compare_runs.py) stays with the package.
- Z4 verifier V2 (dress at a/a_i = 2): the track's own table (secondary_infall/README.md
  lines 104-111) gives dress deviations at a/a_i = 2 of +0.5, +1.4, +3.4 per cent for N128c,
  N64c, N128Lc against the kernel shells, so the "0.1-0.5 per cent" wording is wrong at
  a/a_i = 2 and holds at 4 and 8; recomputed from `nm_growth_cellcentre.txt` if it carries
  both columns. Refuted if the table gives below 0.5 per cent for all three.
- Z5 flux_tools (data run D-20261119-145022-2208a19, `esf.nrp`, `energy_by_tag.npy`):
  850724 records, 140 with m = 1e-30, all u_i = 0; sum of dust masses 2.815600140293471
  (`esf.json` lattice_rest_mass) to 1e-12 relative; sum of m (1 - 2M/R0)^(1/2), i.e.
  m times energy_by_tag, 2.738654513324783 (lattice_misner_sharp) to 1e-12; both 4.1-4.3e-7
  below the continuum values. Refuted beyond 1e-10.
- Z6 figures I look at before relying on them: es_runs figs/es1g judge_horizon.png and
  slicemass_ES-1G.png; verifier_g1's v2_growth_ratio.png and v3_hern_a0.8.png; flux_tools
  check_esf_construction.png; note figures/schem_architecture.png (G1 item C9: must show
  core's wave-2 capabilities and the ES run chain, no text outside its block); my own
  wave3_check.png.

Outcome of Z1-Z6 (run D-20261121-063617-3f2036f, `wave3_check.json`, `wave3_check.png` looked
at; a development pass of the same script into scratch/D-bh-dress/tmp/w3dev was not registered
and gave the same numbers; its only change was the tick labels of panel d).
- Z1 HELD: M_AH(100 M) - 1 = +1.1410e-3; drift maximum +6.963e-3 at 199.5 M, minimum -4.167e-4
  at 126 M, range on 100-165 M [-4.17e-4, +9.46e-4]; mean coordinate radius 1.398 M (25 M),
  0.776 M (199.5 M).
- Z2 HELD: wall max |R/R_w - 1| = 1.676e-4 over the whole run (tau to 206.4 M); R0 = 6 M: 14 of
  14 cross, mean error -8.51e-4 M (range -8.62e-4 to -8.43e-4); R0 = 10 M: -4.98e-3 to
  +0.91e-3 M; R0 = 48 M at t = 200 M: tau 205.320-205.326 M.
- Z3 Pb1 HELD (my 60 per cent odds were on the right side): V-1B drift from 100 M within
  [-4.84e-5, +1.97e-5] over 100-199.5 M, D(199.5 M) = -9.2e-6 against V-1's -1.363e-4. Pb2
  HELD: V-1B and V-1 equal to rounding until ~90 M, apart by 1e-9 at 116 M and 1e-6 at 133 M.
  Pb5 HELD: 0.7775 card-hours. The late drift of V-1 is the outer boundary. Not by me: Pb3,
  Pb4 (package drift_controls).
- Z4 HELD: dress against the kernel shells at a/a_i = 2: +0.55, +1.40, +3.31 per cent (N128c,
  N64c, N128Lc); at 4: -0.01, +0.15, +0.47; at 8: +0.10; largest for a/a_i >= 3: 0.28, 0.68,
  1.03 per cent. M_ta within 0.12 per cent at 2 and 4, 0.29 at 8. The verifier's V2 is right.
- Z5 HELD exactly: 850724 records, 140 tracers, every u_i = 0; dust rest mass and the
  energy-weighted sum equal `esf.json` bit for bit (2.815600140293471, 2.738654513324783).
- Z6: all eight figures consistent with the numbers (REVIEW-wave3 sections 1-6); defects:
  judge_horizon.png top legend over the data (cosmetic, not fixed).
- Side finding (no prediction of mine): the drift pre-flight's processor re-search at 150 M
  differs from the card summary by 3.1e-8 relative, so drift_controls' C1 (1e-8) is refuted as
  written; recorded for the package.

## 2026-11-21T06:45Z  session lead-wave3-batch2a (Opus)  commits 68db5e73..(this entry)  runs D-20261121-063617-3f2036f; closed D-20261120-222515-c2ef5b8, -222550-e472402, -222820-94f20b3, -222625-63abd72

- did: merged main (release core-v0.4); read CLAUDE.md, charter to "Owners", decisions
  0016-0020, the brief ranges, the wave-3 reports and batch-1 results; found four runs left
  "running"/"submitted" by the cut burst, all ended with exit 0 (V-1B on the card DONE at
  16:43 PST), closed them; committed drift_controls' stranded step-1A outputs (byte-identical
  to D-20261120-222107-cc4937b); rechecked es_runs, verifier_g1 and the finished parts of
  flux_tools, drift_controls, secondary_infall and note from the artefacts (Z1-Z6, all held);
  wrote stage/REVIEW-wave3.md; put the verifier's report into stage/G1 (C17 PASS), marked the
  redrawn schematic (C9 PASS), corrected the D-pre-3 dress wording (verifier V2), stated the
  Kerr gap and hole mass per V3; C16 reopened (note v1 not compiled); seven outbox messages,
  eight inbox messages acknowledged; STATUS, HANDOFF, RISKS rewritten.
- found: the late common horizon drift of V-1 (R13) is the outer boundary: with the faces at
  +-384 M (V-1B) it is gone, floor 4.8e-5 over 100-200 M at M/8. ES-1G's +7e-3 growth comes
  with the exterior lost through the faces: the same cause is likely, not tested.
- evidence: D-20261121-063617-3f2036f (lead), D-20261120-222625-63abd72 (V-1B),
  D-20261119-142633-6f72922 (ES-1G); `nrpic-run verify` PASS on 17 wave-3 runs.
- changed my mind about: R13 was ranked "cause unknown, boundary hypothesis failed its probe
  tests" (wave 2b); the direct control settles it for V-1. The probe tests of wave 2b looked
  for the wrong signature.
- open: G1 NOT met (C7 ruling at orch, C16 note); packages flux_tools, drift_controls,
  secondary_infall, note unfinished (HANDOFF); no card job queued; card-hours 5.19 used.
