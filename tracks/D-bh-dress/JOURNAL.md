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

## 2026-11-15T15:20Z  session lead-wave1 (Opus)  commits 5fdc744..(this commit)  runs D-bh-dress-20261115-065141-5fdc744, -145546-5259f48, -145610-5259f48, -145611-5259f48, -145636-5259f48, -145950-23fa1c7

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
