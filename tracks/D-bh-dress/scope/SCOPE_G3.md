# SCOPE of Track D at G3: growth law and the dress profile (written before any G3 production run)

Owner D-bh-dress. Written 2026-11-27 by the lead of batch 34 under decision 0045 item 2, before any
production run of G3, for an independent review that reads it next. No production run is queued before
that review; the only card run of this session is the excision-guard test EG8 (scouting, `excguard/`,
queue entry q0085), which the decision puts first. Every number here carries its source (run id, file
and line, or decision); numbers not yet measured are labelled [JUDGEMENT] or [TO VERIFY]. Numbers in
the criteria are fixed by this text: a later change is a dated amendment below the text, with its
reason, and does not rewrite a criterion after a run has been read.

Sources: brief S4 (lines 394-405) and sheet 9.7 (lines 766-783); `scope/SCOPE.md` sections 1, 3, 5;
`stage/G2/GATE_REVIEW.md` section 5 (the reservations that are conditions here); `stage/G2/VERIFIER.md`
section 4; `coord/INTERFACES/finder_stop.md`; g2long JOURNAL entries 5, 6, 19, 24, 27.

## 1. Claims of G3

The sheet asks at G3 for "three-way convergence of the growth law and the spike profile; the upper limit
from the null test" (brief line 779). Decision 0045 item 2 names the growth law of a black hole fed by dark
matter and the profile of the dress it leaves. Three claims, in order of weight:

- **Claim G (growth law).** The apparent-horizon mass M_AH of a black hole of initial mass M fed by cold
  collisionless dust from the Hubble flow of the data ES-F (flux_tools/esf_data.py, data run
  D-20261121-203042-82deeec: plateau density rho0 = 3.71818e-6 M^-2, H = 5.58116e-3/M, shells with the
  Newtonian energy -M/R0, dust from 3-5 M to 52-60 M, M_tot = 3.7387 M) as a function of the proper time
  of the matter it swallows, converged in cell size (three members inside the convergent regime) and in
  particle number (three members), against the exact Lemaitre-Tolman-Bondi growth M_LTB(tau) = m(R0) at
  tau_H(R0) (`esf_growth.csv` of the data run). The scale factor of the unperturbed flow,
  a(tau) = (1 + 3 H tau / 2)^(2/3), relabels tau; the growth law is quoted as M_AH(a) beside the exact
  curve, the Newtonian cold-infall expectation (note eq. for M_ta, SCOPE section 4) and a
  Zel'dovich-Novikov-type fit (2608.13206, SCOPE section 5), the last two as comparisons, not criteria.
- **Claim D (dress profile).** The profile of the matter around the growing hole in the strong field,
  from 1.5 areal horizon radii to 40 M, at the times the runs reach, against the exact LTB profile of the
  same data. In this cold, spherical set-up every shell that turns around is captured (capture for
  L < 4M; note section II B and the secondary-infall baseline: "the black hole captures nearly all
  infalling matter" at the turnaround radii a full-relativity run reaches), so the dress the hole leaves
  at a given time is the profile of the shells still falling in; it is the strong-field profile that
  Newtonian dress calculations cannot give and that the exact solution can check. A bound, non-captured
  dress needs matter with angular momentum above the capture limit and new initial data; it is not part
  of this scope (section 8).
- **Claim N (null test, the sheet's upper limit).** The upper limit k_95 on a coupling exponent of a
  vacuum black hole (SCOPE section 3, wording of 3.6), read with the converged finder.

## 2. Set-up common to every G3 run (the conditions of decision 0045 item 2)

- Executable: release core-v0.8, `.work/build_gpu_v08/src/athena` (cards), `.work/build_cpu_v08/src/athena`
  (processor smoke tests and re-searches).
- Converged finder with its diagnostics in every run: `<fastflow> polish_iterations_0 = 100`,
  `mass_tol_0 = 1e-5`, `flow_iterations_0 = 400`, `diagnostics = true` (finder_stop.md sections 1, 2, 6:
  within 6.3e-9 of the tight rule on Track D's dumps, card and processors agree to 2.2e-16). Every horizon
  number is read with the status file: a search that is not found is dropped, never read from the
  repeated summary line. Angular grid `ntheta = 16, lmax = 8` in every member (the offset of this grid,
  -1.80e-4 to -1.85e-4 against ntheta 32/lmax 16 on the vacuum puncture [Track D runs
  D-20261124-130935-fdca920, D-20261124-140606-286a302], cancels between members and is carried as a bias
  against the exact solution; measured once more in G3 by a processor re-search of four restart files of
  G-8 at ntheta 32).
- Horizon excision on to the end: `ah_exc_factor = 0.8` with `ah_exc_max_growth = 8` at
  `initial_radius_0 = 0.8` (guard radius 6.4 M) if EG8's prediction E1 holds; otherwise FK's remedy
  (`initial_radius_0 = 1.6`, guard 6.4 M with the default factor 4), which G2 verified (g2long entry 19:
  all 119848 removals by reason 3 to 399.5 M). A run in which a dust removal after the first 2 M of a
  segment is by reason 2 is flagged and its growth after that time is not counted.
- The horizon stays inside the finest level for the whole run, in every member: the finest level must
  cover a cube of +-6 M (FK's smallest horizon radius reaches 4.53 M at 399.5 M, g2long entry 19). This is
  true of the M/8 deck (64 blocks of 3 M on level 7, g2long entry 4). It is NOT true of G2's M/16 member
  FL16, whose level 8 covers +-3 M (64 blocks of 1.5 M): its horizon left level 8 near 200 M
  [JUDGEMENT from the radii; TO VERIFY by the block list and the summary radii of FL16]. G2's late M/16 -
  M/8 offset (+5.8e-4 mean over 250-299 M, GATE_REVIEW section 5 item 1) may come from it; G3's members
  are built so that it cannot.
- Gauge: plain 1+log lapse with the Gamma-driver shift (shift_Gamma 0.75), cfl 0.25, no lapse_leak
  (decision 0025 item 3); outer faces +-768 M; restart every 25 M (about 8 minutes of card time at M/8);
  tlim 400 M; data, tracers (tags 0-139, m = 1e-30) and outputs of ES-FL.
- Envelopes, not single samples: every comparison between members or with the exact solution is quoted
  as the maximum and the mean of the quantity over windows (50 M of coordinate time, or 10 M bins of
  tau_rem) together with its scatter, never as the value at a few named times.

## 3. Members (the ladder)

| Id | Mesh at the horizon | Particles | Change from G-8 | Purpose |
|---|---|---|---|---|
| G-8 | M/8 (ES-FL hierarchy, level 7 to +-6 M) | N (850724) | none (EG8's deck, tlim 400 M) | base member |
| G-12 | M/12: the whole hierarchy refined by 1.5 (root 144 cells over +-768 M, blocks of 24) | N | root nx 96 -> 144 | third mesh member inside the regime |
| G-16 | M/16: level 8 added over +-6 M | N | refined region of level 8 +-5.9 M | finest mesh member |
| G-8-4N | M/8 | 4N (3402632, data D-20261124-130942-29c5de2) | particle file | particle leg |
| G-8-16N | M/8 | 16N (about 1.36e7; data to be made by esf_data.py at lattice h/2.52) | particle file | particle leg |
| G-8-e1 | M/8 | N | `shift_eta = 1.0` (from 2.0) | gauge leg |
| V-8 | M/8 vacuum control (V-1L's deck with the converged finder, tlim 400 M) | 140 tracers | finder, diagnostics | finder floor on core-v0.8 |

Why M/12 and not M/32: a level 9 that holds the horizon to 4.5 M needs about 4096 blocks and four times
the steps of M/8, some 36 times its cost [JUDGEMENT from block counts], far beyond the allotment; M/4 is
outside the convergent regime (decisions 0039 item 4, 0041 item 4). With h = 1/8, 1/12, 1/16 the ratio of
successive differences is (1 - (2/3)^p)/((2/3)^p - (1/2)^p): 2.86 for p = 2, 1.96 for p = 1, 5.9 for p = 4.
G-12 refines every level, G-16 only the innermost; the two refinements differ away from the hole, which is
stated with the results (the growth is read at the horizon, inside the finest level of each).

Smoke tests on processors before any card run of a new deck (two cycles; the block count by level; the
finest level covers +-6 M; the finder found at t = 0 within 3e-4 of ES-F's 0.9915; for G-8-16N the memory
of the particle file and of the card). Cost of each new deck from its smoke test (zone-cycles per second
and blocks) before it is queued; a deck whose measured cost exceeds its cap below by more than 30 per cent
is not queued without an amendment.

## 4. Claim G: statistic, estimator, criteria, refutation

Statistic. For each removed dust particle (tags >= 140, reason 3) with proper time at removal tau_rem,
r(tau_rem) = M_AH(first found search at or after t_rem) / M_LTB(tau_rem) - 1 (G2's (iii), as
`g2runs/tools/esf_criteria.py` reads it, with the status file added).
Estimator. The median of r in 10 M bins of tau_rem with at least 20 removals (e_h(bin)), and its
envelope E_h = max over bins with tau_rem in [50 M, tau_end] of |e_h|. Second form, free of the removal
rule: Delta M_h(t) = M_AH(t) - M_AH(20 M) of the members, differences between members as window
envelopes (max |.| and mean over 50 M windows).

Criteria (fixed now):
- G3-G1 (accuracy). Every counted bin of every member at N or above within +-0.5 per cent
  (G2's band was +-1 per cent; with excision kept on FK's bins lay in [+0.162, +0.249] per cent, g2long
  entry 19). Refuted if a counted bin of any member is outside +-0.5 per cent; the growth law is then
  quoted at the G2 band only.
- G3-G2 (mesh convergence toward the exact solution). With the shell-lead correction of section 6
  applied, E_16 < E_12 < E_8 and the window means of e_h ordered the same way in at least 80 per cent of
  the 10 M bins after 100 M; the observed order from the three members p_G in [0.5, 4]. Refuted if the
  ordering fails or p_G is outside that range: then no order is claimed and the mesh error is quoted as
  the envelope of |e_8 - e_16|.
- G3-G3 (mesh convergence of the growth, free of the exact solution). The window envelopes of
  D_8,12 = Delta M_8 - Delta M_12 and D_12,16 = Delta M_12 - Delta M_16 after 100 M satisfy
  env(D_8,12) > env(D_12,16) in every 50 M window, with ratio within [1.5, 8]. Refuted otherwise.
- G3-G4 (particle number). At M/8 the window rms of M_AH(4N) - M_AH(16N) is below that of
  M_AH(N) - M_AH(4N) in every 50 M window after 50 M, ratio in [1.4, 3] (2 for noise falling as N^-1/2;
  G2 gave 1.9-3.1 for N/4, N, 4N, conv3 D-20261126-055249-505b079); the window means of e_h of N, 4N, 16N
  agree within 0.1 per cent. Refuted if the ordering fails in any window or the ratio leaves [1.2, 4].
- G3-G5 (growth law). The logarithmic slope s_h(a) = d ln M_AH / d ln a over windows of 0.1 in ln a of
  the finest member equals the exact s_LTB(a) within 0.03 in every window from tau = 50 M to tau_end, and
  the three mesh members' slopes are ordered toward it. Refuted if any window of G-16 misses by more than
  0.03.

## 5. Claim D: statistic, estimator, criteria, refutation

Statistic. The areal radius of labelled shells: every dust particle carries its Lagrangian label R0
(`esf_labels.npz` of the data run). At each snapshot (snap_dt 25 M) the particles of the run are binned
by label (bins of 1 M in R0 from 6 to 52 M); the coordinate radius of each is mapped to an areal radius
with the tangential metric of the z = 0 slice dump nearest in time (R = r sqrt(gamma_yy) on the x axis,
spherical symmetry [JUDGEMENT, checked by the same map on the y axis]); the proper time of the bin is that
of the tracers of the nearest label (trajmet index 12). The exact profile is the cycloid R(tau; R0) of
each shell. The dress profile is the enclosed rest mass outside the horizon,
m_d(< R) = sum of the rest masses of particles with areal radius between R_AH and R,
read against the exact m_d,LTB(< R) at the same proper times, and the density
rho(R) = dm_d / (4 pi R^2 dR) in logarithmic bins of R from 1.5 R_AH to 40 M.
Estimator. The ratio q(R, t) = m_d(< R) / m_d,LTB(< R) - 1 per bin and snapshot; its envelope over the
snapshots from 100 M to tau_end; the logarithmic slope of rho over 1.5 R_AH to 10 M and 10 to 40 M.

Criteria (fixed now):
- G3-D1 (accuracy). |q| <= 2 per cent in every bin with at least 400 particles, at every snapshot from
  100 M, at G-16 and at G-8-16N, with the lead correction of section 6 applied to the exact side. Refuted
  if a bin misses; the profile is then quoted with its measured offset.
- G3-D2 (convergence). The envelopes of q order as M/8 > M/12 > M/16 and N > 4N > 16N in each radial
  bin within 10 M of the horizon. Refuted if either ordering fails in more than one bin in five.
- G3-D3 (slope). The inner slope d ln rho / d ln R over 1.5 R_AH to 10 M of the finest member equals the
  exact one within 0.05 at every snapshot from 100 M. Refuted otherwise.
- The map from coordinate to areal radius is tested first on t = 0 data (areal radius of the data R0 to
  1e-3 relative, as the verifier's tangential-metric reading gave 2e-6 M, VERIFIER section 4.1); refuted,
  and Claim D not read, if it misses.

## 6. The lead of the shells (a bias carried in every profile read from removal times)

Known [VERIFIED for the tracers, VERIFIER section 4.1, run D-20261126-062436-72c04d3]: the numerical
shells run ahead of the exact LTB solution by about 0.2 per cent of their proper time at R0 = 28 M: 0.78 M
in ES-FL and FK (M/8, N), 0.55 M in FN4 (M/8, 4N), 0.40 M in FL16 (M/16, N); at R0 = 20 M 0.17, 0.10,
0.045 M; at R0 = 10 M below 0.01 M. It builds up around turnaround.

Estimator. Delta tau_lead(R0) = tau_exact(R; R0) - tau_run(R; R0) at the areal radius R = R_max(R0)/2 on
the way in, the median over the tracers of that label, with the scatter of the tracers; for R0 = 10, 20,
28 M in every member (the verifier's method: areal radius from the tangential metric along the trajmet
records, proper time index 12).
Carried as a bias. Every quantity read from removal times (r of Claim G, D4, the accreted-mass profile)
is shown twice, with tau_rem and with tau_rem + Delta tau_lead(R0) (interpolated in R0); the bias on r is
dM_LTB/dtau x Delta tau_lead / M_AH (about 6e-4 at M/8, N, VERIFIER section 4.1) and is quoted beside each
result. Claim D's exact side uses tau + Delta tau_lead in the same way.
Test that could show it does not converge (G3-L1). At R0 = 28 M: Delta tau_lead(M/8) > Delta tau_lead(M/12)
> Delta tau_lead(M/16) and Delta tau_lead(N) > Delta tau_lead(4N) > Delta tau_lead(16N), each step larger
than the combined tracer scatter. Prediction from the G2 numbers with first order in h at N: M/12 at
0.53 M (0.40 + 0.38 x (1/12 - 1/16)/(1/8 - 1/16)), refuted as convergent if G-12's value lies outside
[0.40, 0.78] M or if either ordering fails. If it fails, the lead is quoted as an unremoved systematic of
every profile, with its size at the finest member.

## 7. Claim N: the null test read with the converged finder

Statistic and estimator as SCOPE section 3.2 (Delta ln M_AH of the benchmark ES-1L minus its control
V-1L, converted to k(eps, a_f) and the upper limit k_95). The G2 floor with the production finder is
2.28e-4 at M/8 and 1.99e-4 at M/16; with the converged re-search at most 7.3e-5 (fp_analyse
D-20261124-172508-c847ee4). G3 reads the limit from re-searches with core-v0.8's polishing of the restart
files of ES-1L, V-1L (M/8) and their M/16 pairs, on processors (no card), every search with its status.
Criterion G3-N1: the converged difference stays below 1.0e-4 at every re-searched time from 100 M at both
meshes, and the two meshes give limits within a factor 2. Refuted if a re-searched difference exceeds
2.0e-4 (the floor is then not the finder's). Wording: SCOPE section 3.6, with "ordinary black holes".

## 8. What G3 does not claim, and why

- A bound, non-captured dress (the spike of brief S4 for warm or rotating matter). It needs shells with
  tangential speeds above about 4M/r_ta (note section II B), that is data with angular momentum whose
  constraints the format-2 table carries only through the energy density, a new data generator and a new
  reference (the probe-limit spike of D-pre-2 is for a fixed black hole). It is specified, with its own
  criteria and review, after Claim G and D are read: a dated amendment of this text, not a run of it.
- A gauge leg with another slicing. The relaxed lapse makes the horizon mass of a vacuum black hole grow
  and `lapse_leak_hole` is a mitigation, not a cure (`stage/G2/OPEN.md` section 2, CLAUDE.md release
  core-v0.7); harmonic or frozen slicing does not avoid the puncture singularity in the way 1+log does
  [BACKGROUND]. The gauge leg is therefore a change of the shift (G-8-e1, shift_eta 1 instead of 2) with
  the same slicing. Criterion G3-E1: the gauge-invariant quantities (e_h per bin, Delta tau_lead at
  R0 = 28 M, q of Claim D) of G-8-e1 differ from G-8's by less than G-8 differs from G-16 (window
  envelopes). Refuted otherwise; then the gauge dependence is quoted as a systematic at its size.
- Binaries of dressed black holes (with F, after G3).

## 9. Predictions written before the runs (refutations in sections 4-7)

P-G1: e_h of every member in [+0.05, +0.30] per cent before the lead correction, [-0.10, +0.25] after it.
P-G2: E_8 - E_16 about 0.1 per cent [JUDGEMENT from the lead's bias of 6e-4 and its halving at M/16].
P-D1: q within +-1 per cent at G-16 from 100 M except in the innermost bin, where the lead acts most.
P-L1: Delta tau_lead(R0 = 28 M): G-8 0.78 +- 0.1 M (as ES-FL and FK), G-12 0.53 +- 0.1 M, G-16 0.40 +- 0.1 M,
      G-8-4N 0.55 +- 0.1 M, G-8-16N 0.40 +- 0.15 M.
P-E1: G-8-e1 within half the G-8 - G-16 differences.
P-V1: V-8's horizon mass constant within 1e-4 from 20 to 400 M with the converged finder (G2's converged
      re-search: at most 7.3e-5).
P-C: costs within 30 per cent of section 10.

## 10. Card budget (60 card-hours toward G3, decision 0045) and order

Estimates [JUDGEMENT] from G2's measured costs: ES-FL 2.60 card-hours to 500 M (5.2e-3 per M), FN4 3.19
to 400 M, V-1L 2.24 to 500 M (EVIDENCE.md), and from block counts times steps for the new meshes (G-12:
about 3.4 times the blocks and 1.5 times the steps of M/8; G-16: about 2.5 times the blocks and twice the
steps). Every new deck's cost is measured on its smoke test before it is queued.

| Order | Run | Estimate | Cap |
|---|---|---|---|
| 0 | EG8 (scouting, queued q0085, 260 M) | 1.4 | 2.5 |
| 1 | G-8 (400 M) and V-8 (400 M) | 2.2 + 1.8 | 3 + 2.5 |
| 2 | G-16 (400 M) | 10 | 13 |
| 3 | G-12 (400 M) | 10.5 | 13 |
| 4 | G-8-4N, G-8-16N (400 M) | 3.2 + 5.5 | 4 + 7 |
| 5 | G-8-e1 (400 M) | 2.2 | 3 |
| - | reserve: preemption repeats and one rerun of a failed member | - | 12 |
| | total | 36.8 | 60 |

Re-searches of Claim N and the angular-grid measurement run on processors (at most 6 cores). Order: G-8
and V-8 first (cheap, the base of every comparison); G-16 before G-12 (if G-16 fails G3-G1, the mesh leg is
redesigned before the costlier half is spent); the particle leg after the mesh leg; the gauge leg last. Two
D jobs at most in the queue at once; priority 2 for the members, 5 for the reserve.
