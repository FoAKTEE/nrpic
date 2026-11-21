# Verifier report: Track D (D-bh-dress), gate G1, checklist item C17

Verifier: helper `verifier_g1` of D-bh-dress, wave 3, 2026-11-20 (fresh context; I produced
none of the material). Package: `tracks/D-bh-dress/verifier_g1/` (scripts, `JOURNAL.md`
with every prediction written before its run and every outcome, `README.md` with how to
rerun). All my runs are processor analyses registered with `harness/bin/nrpic-run`, 0
card-hours. Before these verdicts were committed I did not read `stage/**`, the track's
`JOURNAL.md`, `STATUS.md`, `HANDOFF.md`, `RISKS.md`, `PLAN-wave3.md`, `analysis/lead_checks/`,
or any package's `JOURNAL.md`. The note was read only at commit 78d470ca.

Verdicts: CONFIRMED = recomputed with my own code and an attempt to break it failed;
NOT CONFIRMED = not checked (reason given); WRONG = with evidence. Qualified verdicts say
what part holds. Every number carries a run id (mine: `D-20261120-222209-871e07f`,
`D-20261121-031031-e23da04`, `D-20261121-031711-0d79cb3`, `D-20261121-033209-9c0bd44`,
`D-20261121-034048-17427b0`, `D-20261121-035106-0c619ee`, `D-20261121-040417-8a3c402`,
`D-20261121-035114-8a3cb38`; after the verdicts `D-20261121-040636-e8d5352`,
`D-20261121-040826-9d5051a`).

## Summary

| Claim | Verdict |
|---|---|
| V1 wall tracers within 2.2e-3 (ES-1), 1.6e-3 (V-1) of R_w(tau), tau <= 200 M | CONFIRMED (2.196e-3, 1.594e-3); holds only on the stated window |
| V1 R0 = 6, 10 M reach 2M at 14.8263, 34.4368 M; exact 14.8269, 34.4423 | CONFIRMED |
| V1 horizon drift 3.40e-4, 1.37e-4 (100-200 M); 9.3e-5, 4.2e-5 (100-165 M) | CONFIRMED (exactly; single-sample reference moves it up to 12 per cent) |
| V1 no dust particle enters the bubble | CONFIRMED at the nine snapshots, with a qualification on how the wall is drawn between tracer directions |
| V2 M_ta at a/a_i = 2, 4, 8 within 0.1-0.5 per cent of a kernel-matched shell reference | CONFIRMED (<= 0.03 per cent at the round epochs, <= 0.43 per cent over a/a_i >= 1.5) |
| V2 dress at a/a_i = 4, 8 within 0.1-0.5 per cent | CONFIRMED (0.11-0.43 per cent) |
| V2 dress at a/a_i = 2 within 0.1-0.5 per cent | WRONG as worded: 1.6, 2.3, 3.1 per cent above my kernel shells (N128c, N64c, N128Lc) |
| V2 profile within 25 per cent of self-similar on lambda in [0.1, 0.3] at a/a_i = 8 | CONFIRMED marginally: 25.9 per cent (25.2-25.4 with other solver settings, 33-35 with r_ta +-3 per cent) |
| V3 constant f at a = 0.5, 0.8 within 0.88, 0.95 per cent | CONFIRMED (0.85, 0.88 per cent; 0.34 per cent for r >= 5 Gm) |
| V3 Hernquist within 1.4-1.5 per cent at a = 0 | CONFIRMED approximately (1.67 per cent for r >= 5 Gm, peak -0.55 per cent) |
| V3 Hernquist on the axis within 1.5 per cent | NOT CONFIRMED (axis not computed) |
| V3 4 per cent below FdRW at the a = 0.8 equatorial peak | CONFIRMED (-4.5 per cent; mine within 0.6 per cent of the track's reference); [JUDGEMENT] the difference lies in FdRW's curve |
| V4 late/early density ratio 0.998-1.003 | CONFIRMED (0.997-1.005, each range within 1.4 sigma of 1) |
| V4 invariants conserved to 1e-5 | CONFIRMED (7.9e-6, 1.7e-9, 9.5e-6) |
| V4 inner-range time averages 1-4 per cent below the reference, same sign | CONFIRMED (3.1, 1.8, 0.9 per cent) after a correction of my own reference found post-verdict; each within sampling noise |
| V5 numerical ledger at 78d470ca | 34 rows recomputed or recounted agree, 2 differ without a defect, 2 not comparable, 8 NOT CONFIRMED (not done); no row WRONG |
| V6 wave-1 baselines | CONFIRMED through V5 rows (spike peak, GS ratios, D-pre-4 drift) |

## V1. ES-1 and V-1 (runs D-20261115-172726-60ba4c2, D-20261115-172730-c6d151b)

My run D-20261120-222209-871e07f (`v1_es.py`, JOURNAL entry 1). Readers of `traj.bin`,
`trajmet.bin` (17 doubles per record, `athenak/src/particles/nrpic_io.cpp:811-814, 926`) and
`part.*.bin` (`:940-978`) written from the source; exact curves from the data set
D-20261115-170213-d2c2131 through its table and particle files only (Misner-Sharp mass and
energy per tracer, closed-form radial geodesic); areal radius of a tracer from the evolved
3-metric at the particle.

- Wall tracers (tags 56-69), max over tau <= 200 M of |R/R_w - 1|: ES-1 2.196e-3, V-1
  1.594e-3; a second areal-radius definition gives the same digits. CONFIRMED. Attempt to
  break: over the whole run (tau to 283 M in ES-1, 250 M in V-1) the error grows to 1.7e-2 and
  7.2e-3; tau = 200 M is reached at t = 137.5 M. The bound is a statement about the window.
- Crossing of R = 2M: my exact proper times 14.82693 and 34.44232 M (claims 14.8269,
  34.4423). Run, mean over 14 tracers: 14.82634 (linear interpolation) / 14.82652 (cubic),
  34.43675 / 34.43683 (ES-1); V-1 identical to 2e-4; spread over tracers 1.6e-4 and 4e-4 M.
  CONFIRMED (the claimed 14.8263 is my linear value, 34.4368 my cubic one).
- Horizon-mass drift: 3.400e-4 (ES-1), 1.368e-4 (V-1) over 100-200 M; 9.35e-5, 4.21e-5
  over 100-165 M. CONFIRMED. Attempt to break: with the mean over 95-105 M as reference
  instead of the single sample at 100 M: 3.82e-4, 1.32e-4, 9.2e-5, 3.7e-5 (changes up to 12
  per cent).
- No dust in the bubble: no dust tag disappears (696688 dust particles in each of the nine
  snapshots t = 0, 25, ..., 200 M); the 42 removed particles are tracers 0-41. With the wall
  drawn between the 14 wall tracers by the angular shape of the innermost dust layer, the
  smallest dust-wall margin is 0.136 M at t = 200 M; model-free within 6 degrees of a wall
  tracer 0.126 M. CONFIRMED at the snapshot times, with a qualification: a naive test
  against the nearest of the 14 wall directions fails at t >= 175 M (-0.061 M at 200 M)
  because the wall's coordinate radius differs by 0.57 M between axis and diagonal; the claim
  needs the wall model to be stated. Between snapshots nothing was checked.

## V2. D-pre-3 in AthenaK's Newtonian mode (runs N128c D-20261115-171503-4262f03, N64c -171505-62940f4, N128Lc -171507-d1058a9)

My runs D-20261121-031031-e23da04 and D-20261121-031711-0d79cb3 (`v2_infall.py`,
`v2_selfsim.py`, JOURNAL entry 2). Definitions written before computing: centre = mass
centre of the clump; dress = dust whose shell (initial-radius bin) has, at half or more,
passed through the centre (far side of the initial direction); M_ta = clump + dust inside the
outermost initial radius whose median radial velocity has crossed zero. My shell reference:
3000 shells built from the snapshot-0 lattice, leapfrog, reflection at the centre, three force
laws, of which "measured kernel on all enclosed mass" (`kernel_nx*.txt` of the track, the only
input taken from its analysis) is converged (dt 0.01 and 0.005 identical to four digits);
"point mass, s = 0.25 M" as a second law.

| run, a/a_i | M_ta run (mine) | my kernel shells | dress run (mine) | my kernel shells | my point shells |
|---|---|---|---|---|---|
| N128c, 2 | 1.5058 | 1.5058 | 0.1749 | 0.1721 | 0.1739 |
| N128c, 4 | 2.5955 | 2.5961 | 0.7990 | 0.7958 | 0.7958 |
| N64c, 2 | 1.5060 | 1.5059 | 0.1741 | 0.1702 | 0.1739 |
| N64c, 4 | 2.5955 | 2.5952 | 0.7957 | 0.7948 | 0.7958 |
| N128Lc, 2 | 1.5056 | 1.5059 | 0.1749 | 0.1696 | 0.1740 |
| N128Lc, 4 | 2.5940 | 2.5938 | 0.7955 | 0.7930 | 0.7952 |
| N128Lc, 8 | 4.8159 | 4.8155 | 2.1527 | 2.1435 | 2.1677 |

(run D-20261121-031711-0d79cb3, `v2_results.json`). My run values equal the claimed ones
(README table, section "Wave 2") within 0.14 per cent (M_ta) and 0.3 per cent (dress); half the
number of initial-radius bins changes them by at most 0.1 and 0.4 per cent.

- M_ta: CONFIRMED. Run against my kernel shells <= 0.03 per cent at the round epochs; largest
  deviation over a/a_i >= 1.5: 0.14 (N128c), 0.27 (N64c), 0.43 (N128Lc) per cent.
- Dress at a/a_i = 4 and 8: CONFIRMED, +0.11 to +0.43 per cent.
- Dress at a/a_i = 2: WRONG as worded. The runs lie 1.6, 2.3 and 3.1 per cent above my
  converged kernel shells; the track's own table (README "Wave 2") shows 0.5, 1.4 and 3.4 per
  cent for the same three runs, so "0.1-0.5 per cent" does not describe a/a_i = 2. The early
  dress depends on the force law at the centre: against my point shells the runs are within
  0.6 per cent. Largest dress deviation for a/a_i >= 3: 0.9-1.2 per cent (figure
  `v2_growth_ratio.png`).
- Attempt to break that broke my own reference: "kernel on the clump, unsoftened dust" fell
  5-19 per cent below every run and grew worse with a smaller step (2.4575 -> 2.4020 at
  a/a_i = 4, dt 0.01 -> 0.002); it is not the run's physics (the mesh softens the dust too)
  and is not used; cause open.
- Profile against my self-similar solution (seedless Bertschinger-type equation, my own
  fixed-point iteration; outermost caustic 0.3630 at tau_max = 500): N128Lc at a/a_i = 8,
  eight bins on [0.1, 0.3]: 0.741, 0.864, 1.048, 1.171, 1.138, 1.017, 0.798, 0.927, i.e.
  25.9 per cent at most (innermost bin). CONFIRMED marginally: 25.2 and 25.4 per cent against
  the two other solver settings; 32.5 and 34.5 per cent if r_ta is moved by -3 or +3 per cent.
  My reference itself moves individual bins by up to 4 per cent between tau_max = 200 and 500.
  At a/a_i = 4 (N128c, N64c) the profile lies at 0.41-1.05 of the solution, as the README says.
  Compared with `secondary_infall/selfsimilar.py`: not done (no time); my number stands alone.

## V3. Kerr spike reference (run D-bh-dress-20261115-171615-8adbbdd)

My run D-20261121-033209-9c0bd44 (`v3_kerr.py`, JOURNAL entry 3): density in the equatorial
plane from the invariants (E, C, Lz) with the current and density of FdRW
(kb-data/raw/arxiv/1707.06302/v2/src/kerrdm.tex:396-416), capture from the root structure of
the radial quartic, Hernquist matching by equal radial actions and L = |Lz| + I_theta/(2 pi)
(:523-553), Hernquist DF (:864-874) in delta = 1 - eps~; my own digitiser of
`fig_rho_a.pgf` and `fig_rho_hern.pgf`. Checks: V = R/r^4; I_theta(a = 0) = 2 pi (L - |Lz|);
Hernquist action against direct quadrature to 2e-9; printed Jacobian (:347) against finite
differences (ratio 1.00000000); constant-f density against an independent quadrature over
the local momentum of the zero-angular-momentum observer: 1.0005 at the a = 0.8 peak, 5e-5 at
r = 12. My first version over-counted for a != 0 (equatorial plunging orbits with both inner
roots inside r_+); found by the local-frame check, fixed before the registered run.

- Constant f, largest deviation from FdRW's figure over the digitised range: 0.85 per cent
  (a = 0.5), 0.88 per cent (a = 0.8); 0.34 per cent for r >= 5 Gm; peaks +0.15 and +0.14 per
  cent. CONFIRMED.
- Hernquist a = 0: 1.67 per cent for r >= 5 Gm (2.6 per cent at 4.4 Gm, the inner edge),
  median -0.56 per cent; peak 2.4256e18 at 7.735 Gm against 2.4391e18 at 7.730. CONFIRMED
  approximately (the claim's 1.4 per cent is the track's curve; mine sits 0.5-1.7 per cent
  below FdRW at every spin from 20 to 38 Gm). Caveat: at a = 0 my Lz scan found up to 23
  disjoint intervals at some radius (root classification near degenerate roots); doubling the
  quadrature moved the a = 0 peak by 7e-5.
- On the axis: NOT CONFIRMED (I did not compute theta = 0).
- Hernquist a = 0.8, equatorial peak: mine 3.8999e18 at 5.04 Gm, FdRW 4.0826e18 at 5.07 Gm
  (-4.5 per cent), the track's 3.9217e18 (mine -0.56 per cent); a = 0.5: -1.3 per cent.
  CONFIRMED. Where the difference lies [JUDGEMENT, reasons]: not in the comparison (my
  digitiser gives the track's digitised peaks to four digits; FdRW's constant-f curves, which
  need no action matching, agree to 0.15 per cent; the a = 0 Hernquist curve, which needs
  the matching but no spin, agrees to 0.55 per cent at the peak), not in the track's
  reference (two independent implementations of the printed prescription agree to 0.6 per
  cent; doubling my quadrature changes the peak by 5e-4; replacing the polar-action matching
  by L = sqrt(C) changes it by 0.1 per cent). It grows with spin (-0.55, -1.3, -4.5 per cent
  at a = 0, 0.5, 0.8) and FdRW's a = 0.8 curve has a narrow bump at its maximum that neither
  reference has (figure `v3_hern_a0.8.png`). So the difference lies in FdRW's curve or in an
  unstated detail of their computation.
- Parameter not found in the paper's text: hole mass 4e6 Msun (taken from the track's
  `kerr_lib.py:288`; kerrdm.tex:127 says only "M_BH >~ 4e6 Msun") [TO VERIFY]; with it the
  a = 0 peak agrees to 0.55 per cent.

## V4. AthenaK stationarity in Kerr a = 0.8 (run D-bh-dress-20261115-172611-1e40191)

My run D-20261121-034048-17427b0 (`v4_kerr_stat.py`, JOURNAL entry 4): all 12 x 201
snapshots read with my reader; E = alpha W - beta^i u_i, Lz = x u_y - y u_x and Q from the
Kerr-Schild state with my formulas (geometry from `athenak/src/particles/nrpic_metrics.hpp:22-85`).

- Late/early (snapshots 101-200 over 1-100): 0.9966 (0-4 M), 1.0054 (4-6), 0.9988 (6-10),
  0.9998 (10-16), 1.0003 (16-40); block (1000 M) standard errors of the ratio 1.1, 0.39, 0.13,
  0.10, 0.06 per cent. CONFIRMED: stationary within 1.4 sigma in every range (the claimed
  0.998-1.003 uses another split; mine differ from it by up to 0.002).
- Invariants, maximum over 48000 particles and 20000 M: |dE/E| 7.88e-6, |dLz| 1.66e-9,
  |dQ|/max(Q,1) 9.46e-6; no non-finite snapshot; smallest radius 2.2878 M. CONFIRMED.
- Inner-range time averages against the reference: CONFIRMED, but not independently (see
  the correction below). With my corrected reference (run D-20261121-040826-9d5051a: 136.4,
  601.6, 2469.2, 5366.5, 22580.2 expected in 0-4, 4-6, 6-10, 10-16, 16-40 M; the track's 137.8,
  601.4, 2472.6, 5362.7, 22574.1) the time averages lie 3.1, 1.8, 0.9 per cent below in the
  three inner ranges and within 0.15 per cent in the outer two; at t = 0: -6.1, +1.9, -0.7 per
  cent. Same sign in the inner ranges, sizes as claimed. Each is within the sampling noise of a
  fixed set of orbits (Poisson 8.6, 4.1, 2.0 per cent), so the common sign alone is weak
  evidence of a bias.
- Correction, recorded openly: the verdict I first committed (102d696b) was "WRONG in
  magnitude" with a reference 13, 5.5, 1.2 per cent above the track's. That reference was
  wrong: my function returned the number per dr dtheta dphi and I integrated it over
  cos(theta), dropping a 1/sin(theta) (JOURNAL entry 8). I found it only after the verdicts,
  by comparing my local values with the track's grid (run D-20261121-040636-e8d5352 and a
  point-by-point check: ratio 0.995 sin(theta) at every r), i.e. with the track's material in
  view; the corrected reference is my own code, but the finding of the error was not blind.
  Runs D-20261121-034048-17427b0 (reference numbers only), D-20261121-035106-0c619ee and
  D-20261121-040417-8a3c402 carry the error and are superseded for the reference counts;
  their counts and invariants stand.

## V5. The numerical ledger of the note at 78d470ca

My run D-20261121-035114-8a3cb38 (`v5_ledger.py`, JOURNAL entry 5); the full row table is
`v5_ledger.md` in that run directory. "independent" = my code from the raw output (table
rows, particle file, snapshots, finder output, closed forms); "recount" = read off the run's
log/JSON/manifest and recounted (orders = log ratio of stored residual maxima); I did not
rerun any of the track's analyses.

| Ledger part | Rows | Result |
|---|---|---|
| 1 Einstein-Straus data set (D-bh-dress-20261115-043445-b782009 and its checks) | m_p, a; H, 1/H; rho0; dust and total mass; HR; rows, particles, tracers; lattice vs continuum; mass inside the wall; R_w(tau); a and 1 + 6 ln a at 200 M; proper times 14.83, 34.44, 244.74 | independent, all agree to the printed digits (e.g. a = 0.9765922286, m_p = M/a = 1.0239688282; H = 0.00558116; rho0 = 3.71818e-6 from the Hamiltonian constraint on the table rows; M_tot 15.59280; tau 14.8269, 34.4423, 244.736) |
| | density residuals of the table (2.22e-5 bubble, 1.68e-7 plateau) | independent; my 4th-order differences give 3.4e-7 and 8.1e-10: the ledger's values are upper bounds |
| | 48 + 48 symbolic identities; 3D orders 3.85-4.07; radial 3.96, 3.99; AthenaK t = 0 orders 5.29, 4.69 and 4.94, 3.20; E - rho 1.14e-13 | recount, agree |
| | box "mid transition" orders 5.88, 5.76; cost model 1.37, 2.87, 11.3; "wall radius against the closed form" 6.66e-16 | NOT CONFIRMED (not done) |
| 2 Horizon-mass floor (D-bh-dress-20261115-121313/121314-284ec4f) | M_AH/M - 1 at 100 M; drift of the 20 M mean 50 -> 490 M (2.9529e-4, 3.6743e-5); largest change on [50, 210] (8.22e-6); 5 M peak to peak (9.33e-5, 9.28e-5); spin (1.784e-7, 5.646e-9) | independent from `punc.horizon_summary_0.txt`, all agree |
| | card-hours 0.654, 1.523 | recount (manifests), agree |
| | smallest detectable change (two rows) | NOT CONFIRMED (the helper's statistical method not rebuilt) |
| 3 Spike in the probe limit | constant-f peak 0.86999e8 (position 7.554 against 7.58 Gm: flat maximum); GS ratios 2.58997, 0.09207; Hernquist a = 0 peak 2.4256e18 at 7.735 (-0.47 per cent) | independent, agree (position: not a meaningful digit) |
| | deviation from FdRW a = 0 on 5-39 Gm: 1.67 per cent (ledger 1.01) | independent; differs because the ledger number belongs to the track's curve, mine 0.5-0.7 per cent lower at large r; not a defect |
| | AthenaK Schwarzschild spike (D-bh-dress-20261115-123755-25227d4): 48000 particles, 20000 M; |dE/E| 1.3328e-6, |dL/L| 1.9329e-10; count 4-6 Gm second half 0.985 against my reference (ledger 0.976) | independent, agree (count within 1 per cent) |
| | chi^2 median 0.98; SFW Fig. 1 read-off and deviation; loss-cone probes | NOT CONFIRMED (not done) |
| 4 Secondary infall | M_ta (eps = 0.01) 1.525424, 2.628154, 4.870985; centre mass 1.19019, 1.82763, 3.21526; coefficients 0.2627, 0.55811, 0.56475; r_ta 74.56, 33.41, 16.06, 7.198; absorbed mass and doubling 4.507 (centre-arrival approximation) | independent closed form, agree |
| | self-similar slopes 0.741, 0.705; lambda_1 0.3553, mass inside 0.654 | not comparable: my solution is seedless (lambda_1 0.3630, mass 0.686); a central mass moves lambda_1 inward (0.3580 at tau_max = 30), so the seeded value is plausible but not reproduced |
| | lambda^(9/4) rho/rho_b; passed fraction 0.6247; captured fractions; radiation era | NOT CONFIRMED (not done) |

No ledger row is WRONG.

## V6. Wave-1 baselines (through V5)

- Schwarzschild spike: peak 0.8699e8 GeV/cm^3 (mine 0.86999e8; position 7.55-7.58 on a flat
  maximum); ratio 2.590 over Gondolo-Silk (mine 2.58997 from GS eq. (6) quoted in
  1305.2619 SFWpaper.tex:440-443, maximum (4 pi f0/3)(1/(2c))^(3/2) at r = 2c); +9.2 per cent
  when the edge moves from 8 to 4 Gm (mine 9.207). CONFIRMED. Note: SFW's prose says "a factor
  of three" and "about 15 per cent higher" (SFWpaper.tex:443); with the same formula the
  numbers are 2.59 and 9.2 per cent [JUDGEMENT: SFW's words are rounded readings of their
  figure].
- D-pre-4 drift 50 -> 490 M: +2.9529e-4 (M/8), +3.6743e-5 (M/16) from the raw finder output.
  CONFIRMED.

## What I did not do

- Theta = 0 Hernquist curve (V3 axis claim); comparison with `secondary_infall/selfsimilar.py`;
  the eight ledger rows marked "not done"; reruns of the track's wave-1 analyses.
- V1 dust check between snapshots.

## Comparison with the track's own checks (written after the verdicts of 102d696b)

Read after the verdicts: `stage/G1/STATUS.md`, `stage/G1/OPEN.md`, `stage/REVIEW-wave2.md`
sections 2-3, `spike/analyze_kerr.py` and `spike/kerr_expected.py` (expected counts).

- V1: the G1 status reports the same wall bound, crossing offsets "within 6e-4 and 5.6e-3 M"
  (mine 5.9e-4 and 5.5e-3) and the same drift numbers, reproduced by the lead's own code
  (D-20261119-151039-b2ce968). New from me: "no dust enters" depends on how the wall is drawn
  between the 14 tracer directions, and was checked at snapshots only.
- V2: the lead's own implementation agreed with the helper to 0.07 per cent at a/a_i = 4 and 8
  (REVIEW-wave2 section 3); mine agrees to 0.3 per cent with different definitions. Neither the
  lead nor the status looked at the dress at a/a_i = 2, where "0.1-0.5 per cent" does not hold
  (my 1.6-3.1, the track's own table 0.5-3.4 per cent). The profile statement ("within 25 per
  cent only at a/a_i = 8") agrees with my 25.9 per cent.
- V3: the lead did not redo the action matching at L_z != 0 and asked for a second agent
  (REVIEW-wave2 section 2, OPEN item 1). Done here: my implementation agrees with the track's
  reference to 0.6 per cent at the a = 0.8 peak; the 4.5 per cent to FdRW is common to both
  and, by the reasons in V3, belongs to FdRW's curve [JUDGEMENT]. OPEN item 1 can be closed for
  the Kerr reference; the axis curve remains unchecked by me.
- V4: the lead's own late/early ratios (0.997, 1.005, 0.999, 1.000, 1.000) equal mine; the
  inner offsets (0.959, 0.982, 0.990 of expected; t = 0 0.929, 1.019, 0.992) equal mine to 1
  per cent after my correction. The lead's reading "each within noise, the common sign not"
  stands; I add the Poisson size of a fixed sample (8.6, 4.1, 2.0 per cent).
- V5: the ledger agrees with the outputs wherever I could recompute it; the ledger generator's
  own claim check (claims.json at 78d470ca) already flags the locator of "dress 0.625 M_ta",
  which I did not test.

## Requests (to the lead of D-bh-dress)

1. V2: reword the G1 claim so that "0.1-0.5 per cent" applies to M_ta at a/a_i = 2, 4, 8 and
   to the dress from a/a_i about 3 on; the dress at a/a_i = 2 differs by 0.5-3.4 per cent
   (the track's own table) and depends on the central force law.
2. V2: state the profile bound as "about 25 per cent, sensitive to r_ta" rather than "within
   25 per cent".
3. V3: the 4.5 per cent at the a = 0.8 peak belongs to FdRW's curve [JUDGEMENT]; say so with
   the reasons above; name the source of the hole mass 4e6 Msun.
4. V4: nothing to correct in the track's reference (my first objection was my error, see V4).
   The inner deficits are 1-2 sigma each; the lead's proposal of a second seed (REVIEW-wave2
   section 2) remains the way to decide whether the sampler is biased at r < 10 Gm.
5. Ledger: say which radius "wall radius against the closed form" compares; mark the
   table-density residuals as upper bounds; describe the self-similar model (seed) so that
   its rows can be checked.
