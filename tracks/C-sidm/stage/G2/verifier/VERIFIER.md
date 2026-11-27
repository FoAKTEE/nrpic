# Fresh verifier of gate G2, Track C (checklist item C18)

Helper session of batch 33, 2026-11-27 (09:00-09:40 UTC). Processors only, one core per run,
no card run. Decision 0016 item 4, ruling 0041 item 3, ruling 0045 item 5.

What I was given and read before recomputing: RERUN.md, the list "What the verifier should
recompute first" of OPEN.md, Table VI of the note (`tab:ledgerG2`, note/main.tex:311-334), the
scope text (scope/SCOPE.md:124-140 and 323-330), the lead's predictions as committed before
the runs (git show 12183c5d5, b7007c99a, 77a69997a, f261c3ec4, a5b72829a), the King ansatz of
arXiv:2009.08163 (paper.tex:631-686, Table 1 at 948-960), coord/INTERFACES/collisions.md
(equation 1, history columns). I did not read the outcome entries of the lead's journals,
REVIEW-wave3.md, the verdict column of CHECKLIST.md, STAGE_REPORT.md, EVIDENCE.md or
VERIFY_RESULTS.* before section 10, nor the lead's analysis scripts (only the run-id lists in
their manifests' commands).

Registered runs of this package (manifests under `tracks/C-sidm/runs/`, outputs under
`scratch/C-sidm/<run_id>/`):

| Run | What | Figure |
|---|---|---|
| C-20261127-090849-dcfc1ae | V1: own King sequence (`scripts/king_seq.py`) | `fig_v1_king_sequence.png` |
| C-20261127-090942-697c4b3 | V2-V5: own history reader, fates, bands, floors, decks, horizon files, collision counts and budgets (`scripts/fates.py`) | `fig_v2_fates.png` |
| C-20261127-090913-97ee992 | V4.c: own expected collision rate from particles and metric at t = 0 (`scripts/collrate.py`) | none (five numbers; see section 4) |
| C-20261127-091307-f068e91 | X.1-X.7: block A controls and seeds, D2 control band, NS.1, D2eta1 guard stop, momentum and rest mass of the collision steps (`scripts/extras.py`) | covered by `fig_v2_fates.png` |

Superseded, kept on record: C-20261127-090908-0053e80 (the V2-V5 run before panel (d) of the
figure was limited to the lapse range; same numbers), C-20261127-091102-fd0c31b and
C-20261127-091139-4b789b6 (earlier passes of extras.py; their numbers reappear in the last pass).

Every history file read (50 files) matched the sha256 its run recorded in `sha256sums.txt`
(run C-20261127-090942-697c4b3, `sha_checks`). Each reader was tested first on a case with a
known answer (below). The figures were read before any number was relied on.

## Summary

| # | Claim (source) | Verdict |
|---|---|---|
| 1 | Turning point of the King (b = 1) family y_max = 0.334032; bracket members 0.324, 0.344 on either side | REPRODUCED to 6 digits (0.3340322); members at -3.00 and +2.98 per cent in y0, Z(0) 0.4953 and 0.5285 around 0.5119 |
| 2a | Marker times 252.31 (N6b344), 217.97 (A16b344), 252.41 (N6b344e1), 229.79 (A344s1i) M | REPRODUCED to all printed digits (252.311, 217.972, 252.413, 229.791) |
| 2b | N6b324, A16b324, N6b324e1, A324s1i, N6c hold 600 M | REPRODUCED: no record below 0.3 to 600.0 M (lowest alpha_min 0.641 to 0.659) |
| 2c | Every collapse time is the lapse marker; no run had the horizon finder | REPRODUCED: no horizon file in any of the 20 output directories read, no `<fastflow>`/`<ahf>` block in any deck |
| 2d | Central lapse of the stable members within the band (20 M means, +-0.03) | REPRODUCED: N6b324 [-0.0119, +0.0150], A16b324 [-0.0171, +0.0107], A324s1i [-0.0248, -0.0024]; eta1 - eta2 at most 1.40e-5 |
| 2e | Leg decks differ only in mesh or shift_eta; N = 1e6 members share sampler and seed of N6c | REPRODUCED (deck diffs and IC commands, section 2) |
| 3a | Controls: 295.78 M (1e4), 534.81 M (1e5), none by 600 M (1e6) | REPRODUCED (295.785, 534.814; N6c lowest alpha_min 0.6586) |
| 3b | Constraint floors fall as 1/N | REPRODUCED for the quantity used: `H-norm2` = integral of H^2 dV, 100-300 M means 7.68e-2, 7.86e-3, 7.90e-4 (9.8 and 9.9 per decade); H itself falls as N^-1/2 |
| 3c | "The controls' collapses are particle noise" | CONSISTENT, NOT SHOWN as a mechanism; a finite-N origin IS shown (section 3) |
| 4a | CC2 collapse 206.64 (M/4), 163.41 (M/8), 158.42 (M/16), 164.01 M (shift_eta 1) | REPRODUCED (206.642 = mean of 206.556 and 206.728; 163.407; 158.424; 164.012) |
| 4b | Measured / expected collision rate 1.0008 | REPRODUCED for D2f2s1 over (0, t_c] (1.00080); not a property of every member: 0.9885 to 1.0008 over the six M/8 and M/16 members, two at z = -3.3 and -3.8 (section 4) |
| 4c | Expected rate (computed by me) | The code's sum_P equals my rate from particles and metric at t = 0 to 1.1e-4 (D2f2s1), within 0.8 per cent at the first step and 0.33 per cent over the first M for all five members |
| 4d | Collision energy budget closes to 3e-16 (below 3.5e-16) | REPRODUCED: sum of dH over sum M H to first excision 2.84e-16 to 3.17e-16 (M/8, M/16, eta1); momentum below 4e-19 and rest mass exact (X.7) |
| 4e | Seed pair 2.24 M against the bar of 2 M: D2.3 seed part FAILED as written | REPRODUCED: 165.645 - 163.407 = 2.238 M |
| 5 | Location of the threshold converges, collapse time does not (13.6 per cent) | Arithmetic REPRODUCED (13.61 per cent); what G2 can claim: section 5 |

Predictions that failed as written, checked from my numbers: A.4 FAILED (confirmed), NS.2
FAILED (confirmed), D2.2 FAILED (confirmed: -20.9 per cent against 10), D2.3 seed-pair part
FAILED (confirmed), D2eta1 FAILED as a run (guard stop at 190.375 M, confirmed). BA.3 is NOT
failed as written: it predicted that A.4 stays failed, and A324s1c crosses at 599.99 M with a
500-600 M mean change of -0.102 (X.2). Section 6 lists every prediction I judged.

## 1. Equilibrium sequence and turning point (V1)

Solver (`scripts/king_seq.py`, run C-20261127-090849-dcfc1ae): f = (exp(1 - E/E0) - 1)_+,
isotropic (paper.tex:634-636); density, pressure and number density as integrals over
eps = cosh s with 200-point Gauss-Legendre quadrature; the field equation of paper.tex:670-673
with the mass and rest mass integrated alongside (DOP853, rtol 1e-12) to the surface y = 0;
E_b = (N - M)/N (paper.tex:922); Z(0) = e^y0 / sqrt(1 - 2M/R) - 1.

Tests first: (T1) with constant density g = rho0, h = rho0 (e^y - 1), the integrator gives
2M/R of the Schwarzschild interior solution, 1 - (e^y0/(3e^y0 - 2))^2, to 3.5e-12 for
y0 = 0.05, 0.2, 0.5, 1.0; (T2) the King quadrature obeys the hydrostatic identity
dh/dy = g + h to 2.7e-8 (central differences). Both pass.

| Quantity | Verifier | Claimed | Printed (2009.08163) |
|---|---|---|---|
| y_max (first maximum of E_b) | 0.3340322 (0.33403220 with coarse settings) | 0.334032 | 0.334 (paper.tex:953) |
| E_b at y_max | 0.035589 | 0.03559 (tab:parameters) | |
| R/M at y_max | 13.630 | 13.63 | |
| Z(0) at y_max | 0.51191 | 0.5119 | |
| y_zero (first zero of E_b) | 0.78452 | | 0.784 (paper.tex:953) |
| y0 = 0.324: E_b, Z(0), R/M, (y0 - y_max)/y_max | 0.0355637, 0.49529, 13.794, -3.00 % | | |
| y0 = 0.344: E_b, Z(0), R/M, (y0 - y_max)/y_max | 0.0355644, 0.52851, 13.481, +2.98 % | | |

[VERIFIED] The turning point is reproduced to six digits by an independent solver; the two
bracket members straddle it symmetrically (their E_b lie 2.49e-5 and 2.42e-5 below the
maximum), at a distance of 0.010 in y0 (target of SCOPE.md:325: 0.01 in y_c) and 0.017 in
Z(0) (target 0.02). The figure shows E_b against y0 with the printed maximum and zero, and
the neighbourhood of the maximum with the two members.

## 2. Fates at a million particles and what the marker shows (V2)

Reader (`scripts/fates.py`, run C-20261127-090942-697c4b3): comment lines skipped anywhere;
restart rule (a row whose time is not later than the last kept row replaces every kept row
from its time on); crossing = first record with alpha_min (column 16) below 0.3, linear
between that record and the one before. Self-test on a synthetic history with a false dip in a
first segment and a continuation from 100 M: crossing 233.3333 M exact, one restart seen (the
first segment alone would give 120.25 M). Continuations were met in N4c (4), N6c (6), A16b324
(8), A324s1c (8), A334s2c (4), A334s3c (4); every threshold run has 2401 rows to 600.0 M.

| Run | N | Mesh, gauge | Claimed | Verifier | First excision | Lowest alpha_min |
|---|---|---|---|---|---|---|
| N6b344 | 1e6 | M/8, eta 2 | 252.31 | 252.311 | 259.75 | 0.022 |
| A16b344 | 1e6 | M/16, eta 2 | 217.97 | 217.972 | 224.75 | 0.0097 |
| N6b344e1 | 1e6 | M/8, eta 1 | 252.41 | 252.413 | 260.00 | 0.032 |
| A344s1i | 1e5 | M/8, eta 2 | 229.79 | 229.791 | 237.25 | 0.014 |
| N6b324 | 1e6 | M/8, eta 2 | holds | holds (600.0 M) | none | 0.656 |
| A16b324 | 1e6 | M/16, eta 2 | holds | holds | none | 0.651 |
| N6b324e1 | 1e6 | M/8, eta 1 | holds | holds | none | 0.656 |
| A324s1i | 1e5 | M/8, eta 2 | holds | holds | none | 0.641 |

Bands (20 M block means of alpha_c - alpha_c(0), alpha_c = alpha_probe at the origin, 0-600 M):
N6b324 [-0.0119, +0.0150], A16b324 [-0.0171, +0.0107], N6b324e1 [-0.0119, +0.0150], A324s1i
[-0.0248, -0.0024] (all equal to Table VI to its digits); largest |N6b324e1 - N6b324| block
difference 1.40e-5 (claimed 1.4e-5). [VERIFIED]

Decks (section 2e): N6b344 -> A16b344 and N6b324 -> A16b324 add `<refined_region3>` of level 8
inside |x| < 1.95 M and double ndiag, hist_dcycle, cstat_dcycle, traj_dcycle (output cadence in
cycles at the halved step: the same cadence in time); N6b344 -> N6b344e1 and N6b324 ->
N6b324e1 change only shift_eta 2.0 -> 1.0. N6c -> N6b344/N6b324 change only the particle and
table files; their IC runs (C-20261124-130731-e1d24de, C-20261125-115759-77a6999,
C-20261125-120426-f261c3e) ran make_ic_seeds.py with `--seeds 1 --N 1000000`, the later two
with `--tag` added, and the script differs between their commits only by that option (git diff
e1d24de 77a6999). [VERIFIED]

What the marker can show and what it cannot [JUDGEMENT, from the histories]:
- It shows that the slice develops a region where the 1+log lapse falls below 0.3. In the six
  collapsing threshold runs the lowest lapse then falls to 0.01-0.03 within about 10-20 M and
  stays there to 600 M (figure, panels a, b), and every particle of the run is eventually
  excised (n_excised reaches N; the first excision, alpha < alpha_exc = 0.1 at a particle,
  follows the crossing by 6.8-7.6 M). Collapse of the whole cluster is the only reading of
  these runs I find; none of them comes back. (For the collisional runs I read the lapse, panel
  d, but not the excision counts.)
- It does not show a trapped surface, a horizon mass, or when a horizon forms. The time is a
  property of the slicing: both gauge legs keep the 1+log lapse and change only the shift
  damping, which (by symmetry) hardly acts at the centre, so the 0.04 per cent agreement of
  N6b344 and N6b344e1 is not a test of slicing dependence. The mesh dependence of the marker
  time (13.6 per cent) is a property of the marker, not of a horizon.
- "Holds 600 M" says nothing after 600 M. At N = 1e5 the cut matters: the unkicked control of
  the stable member, A324s1c, crosses at 599.99 M (X.1), and its kicked twin A324s1i is still
  falling at 600 M (raw alpha_c - alpha_c(0) about -0.028, panel c).

## 3. Controls without the kick (V3)

| Run | N | Claimed t_c | Verifier t_c | H-norm2, 100-300 M | H_mean (cstat), 100-300 M |
|---|---|---|---|---|---|
| N4c | 1e4 | 295.78 | 295.785 | 7.68e-2 | 9.33e-4 |
| A334s1c | 1e5 | 534.81 | 534.814 | 7.86e-3 | 3.09e-4 |
| N6c | 1e6 | none | none (lowest alpha_min 0.6586) | 7.90e-4 | 9.83e-5 |

`H-norm2` (cc.z4c.user.hst) is the volume integral of H^2 (athenak/src/outputs/history.cpp:61,
`vol*SQR(H)`), a squared quantity: its 1/N fall (factors 9.78 and 9.95) and the N^-1/2 fall of
the mean |H| of cc.cstat.hst (factors 3.02 and 3.14, against sqrt(10) = 3.16) say the same
thing: the constraint violation of the controls is that of white sampling noise. [VERIFIED]

Further, from the seed controls of block A (X.6, run C-20261127-091307-f068e91): the threshold
model at N = 1e5 crosses at 534.81 (seed 1), 585.79 (seed 2) and 563.29 M (seed 3; its history
now reaches 600 M), mean 561.3 M, sample sd 25.5 M; the N = 1e5 controls of the bracket models
cross at 549.26 M (0.344) and 599.99 M (0.324), all one seed. [VERIFIED]

Is "the controls' collapses are particle noise" shown? [JUDGEMENT]
- Shown: the control lifetime depends on N far more than on the seed (295.8 M at 1e4 against
  561.3 +- 25.5 M at 1e5, ten standard deviations of the seed spread), and the mesh-only reading
  NS.2 (t_c(1e6) in [455, 615] M) is refuted by N6c. So the collapse of the controls is a
  finite-N effect, not an N-independent defect of the M/8 scheme.
- Consistent but not shown: the mechanism. With one seed at 1e4 and at 1e6, the runs do not
  separate noise-seeded growth of a marginal mode (a random effect) from an N-dependent bias of
  the sampled equilibrium (a deterministic effect of the stratified sample). A logarithmic law
  t_c = a + b log10 N, which noise-seeded exponential growth gives, fits the two collapses with
  b = 266 M per decade and predicts about 827 M at N = 1e6, consistent with N6c holding to
  600 M; but two points fix the line, so this is a consistency, not a test. The 1/N fall of the
  floor shows that the noise is there, not that it causes the collapse.
- What would show it: a second seed of N4c (a spread of tens of M at 1e4 would be the noise
  signature) and N6c continued to about 900 M (a crossing near 800 M would test the log law).
  Both are requests, not done here.

## 4. Collisional members (V4)

Collapse times (run C-20261127-090942-697c4b3), CC2 at Kn_c = 10:

| Run | Mesh, collision cell, gauge | Claimed | Verifier |
|---|---|---|---|
| M4s1, M4s2 (C-20261120-221846-797bdbe) | M/4, M/4, eta 2 | 206.64 (mean) | 206.556, 206.728; mean 206.642 |
| D2f2s1 | M/8, M/4 | 163.41 | 163.407 |
| D2f2s2 | M/8, M/4, other collision seed | 165.65 | 165.645 |
| D2f1s1 | M/8, M/8 | 164.01 | 164.013 |
| D2f4s1 | M/8, M/2 | 165.97 | 165.967 |
| M16 | M/16, M/4 | 158.42 | 158.424 |
| D2eta1 | M/8, M/4, eta 1 | 164.01 | 164.012 (run ends at 190.375 M: guard stop, exit status 3, non-finite fields) |
| D2ctl | M/8, no collisions | none | none; mean change 280-300 M -0.0049 |

Collisions per particle per M over 0-100 M (two per collision, N = 1e5): 8.857e-3 (D2f2s1),
8.865e-3 (M16), 8.782e-3 (D2eta1), 8.851e-3 (f1), 8.675e-3 (f4), 8.828e-3 (seed 2) - the
claimed 8.857, 8.865, 8.782e-3 to their digits. [VERIFIED]

Expected rate computed by me (`scripts/collrate.py`, run C-20261127-090913-97ee992): from the
positions and covariant momenta of every particle at t = 0 (cc.traj.bin), the metric at each
particle (cc.trajmet.bin), the masses (snapshot 0) and the deck (coll_sigma = 18.608,
coll_cell_factor, refined regions), the sum over collision cells of sigma_m M alpha /
(sqrt(gamma) V) times the sum over all pairs of the Moller speed (equation 1 of
collisions.md, summed over the random pairs the operator tests). Tests: Moller speed against
sqrt(|v1 - v2|^2 - |v1 x v2|^2) to 6.7e-16; cell pair sum against a double loop to 2.2e-16.
Cells outside 8 M carry 3e-5 of the rate, so the assumed level there does not matter.

| Run | Verifier rate (per M, t = 0) | Code sum_P, first step | Ratio | Code, first M / verifier |
|---|---|---|---|---|
| D2f2s1 | 379.221 | 379.261 | 1.00011 | 1.00169 |
| D2f1s1 | 381.185 | 384.228 | 1.00798 | 0.99948 |
| D2f4s1 | 376.595 | 378.853 | 1.00600 | 1.00326 |
| M16 | 377.583 | 377.188 | 0.99895 | 1.00228 |
| D2eta1 | 379.221 | 379.261 | 1.00011 | 1.00169 |

[VERIFIED] The code's expectation sum_P is the rate of equation 1 for the actual particles and
metric: one step of the code samples N/2 pairs, so a single step scatters by tenths of a per
cent (more with the small cells of f = 1, at most 8 particles per cell); the first M (32 steps)
agrees to 0.33 per cent while the cluster has begun to contract.

Counted collisions against sum_P (count test; z = (n - P)/sqrt(P)):

| Run | 0-100 M | (0, t_c] | (0, t_c], rejected pairs added | (t_c, t_c + 8 M] | same, rejected added |
|---|---|---|---|---|---|
| D2f2s1 | 1.00016 (z +0.03) | 1.00080 (+0.27) | 1.00335 (+1.11) | 0.850 (-25.1) | 0.990 (-1.73) |
| D2f2s2 | 1.00612 (+1.28) | 0.99414 (-1.95) | 0.99650 (-1.17) | 0.863 (-22.9) | 1.004 (+0.62) |
| D2f1s1 | 1.00048 (+0.10) | 0.99816 (-0.61) | 0.99941 (-0.19) | 0.898 (-16.5) | 0.995 (-0.88) |
| D2f4s1 | 0.99198 (-1.68) | 0.98995 (-3.34) | 0.99441 (-1.86) | 0.796 (-34.5) | 0.998 (-0.38) |
| M16 | 0.99937 (-0.13) | 0.99827 (-0.56) | 1.00046 (+0.15) | 0.865 (-21.6) | 1.007 (+1.12) |
| D2eta1 | 0.99619 (-0.80) | 0.98847 (-3.83) | 0.99096 (-3.00) | 0.860 (-23.6) | 1.005 (+0.83) |

"Rejected" = accepted pairs left unscattered for want of a root (column 34) plus detailed-
balance rejections (column 36). No probability was truncated (n_trunc = 0, largest pair
probability 0.03, one sub-step) in any window.
- [VERIFIED] 1.0008 is D2f2s1 over (0, t_c]; it is the best of the six members, not their
  typical value. Over the same window the six lie between 0.9885 and 1.0008. Two members fall
  short at more than three standard errors (f4: -3.34, the "z = -3.39 at f = 4" of OPEN.md
  reproduced to the window; eta1: -3.83, still -3.00 with the rejected pairs added). The
  sqrt(P) error is an upper bound (the variance of a sum of Bernoulli draws is sum P(1 - P)),
  so these z are if anything understated. [JUDGEMENT] A deficit of about one per cent before
  t_c in two of six runs is small for the physics but is not "the rate equals the expected one":
  the claim should name the run and window, or the count test should be stated as passed in
  four of six members.
- [VERIFIED] After the crossing the counted collisions fall 10-20 per cent short of sum_P; the
  rejected pairs account for the gap to within 1 per cent. The operator then rejects a few per
  cent of the accepted pairs, which is expected in the collapse but means the measured rate
  after t_c is not the expected one.

Budgets (to the first excision, columns 32-33 and 21-25 of cc.coll.hst, X.7):

| Run | sum dH / sum M H | sum abs(dH) / sum M H | sum dP_i / sum M H (largest) | sum abs(dP) / sum M H | rest mass span |
|---|---|---|---|---|---|
| D2f2s1 | 3.05e-16 | 3.06e-16 | 3.6e-19 | 1.22e-16 | 0 |
| D2f2s2 | 3.06e-16 | 3.08e-16 | 3.2e-19 | 1.23e-16 | 0 |
| D2f1s1 | 2.84e-16 | 2.87e-16 | 2.3e-19 | 1.20e-16 | 0 |
| D2f4s1 | 3.17e-16 | 3.18e-16 | 2.0e-19 | 1.24e-16 | 0 |
| M16 | 2.89e-16 | 2.95e-16 | 3.9e-19 | 1.08e-16 | 0 |
| D2eta1 | 3.04e-16 | 3.06e-16 | 2.4e-19 | 1.26e-16 | 0 |
| M4s1, M4s2 | 3.92e-16, 4.27e-16 | 4.20e-16, 4.42e-16 | - | - | - |

[VERIFIED] The canonical energy sum M(alpha W - beta^i u_i) of the colliding particles, with
the metric at each particle, is conserved by the collision steps to 3e-16 of its value over
about 1.3e5 collisions; the covariant momentum to 4e-19 (signed) and the rest mass exactly.
The signed sum of dH nearly equals its absolute sum: the residue is a one-signed rounding drift
of about 2e-21 M per collision. [JUDGEMENT] This is the conservation of the operator's own
pairwise quantities in a curved metric, which is what the G2 phrase of SCOPE.md:327-328
("budgets close to the round-off of pairwise conservation plus the measured collisionless
drift") asks for its first half; the second half, a budget of the whole system including the
collisionless drift, is not in the package (the note's own item iii: no energy diagnostic of
the whole spacetime).

Observation: M4s2 (M/4 seed 2) leaves the lapse range after its first excision (alpha_min
-2.7e8 at 216.5 M, 335 non-finite rows); its column `dE_particles` sums to 250 times sum M H
to the first excision. Neither touches its t_c (206.73 M, before), but the M/4 member of the
mesh series ended in a broken state that no G2 text mentions.

Mesh series of the collisional collapse: 206.64 -> 163.41 -> 158.42 M; differences 43.23 and
4.99 M, ratio 8.7. The spread on M/8 over seed, collision cell and gauge is 163.41-165.97 M
(sd 1.1 M, range 2.56 M), so M/8 to M/16 (4.99 M) is two to four times that spread. M/4 is
outside the asymptotic range (as the note says); with two meshes in range no order and no
extrapolation can be read. [JUDGEMENT]

## 5. Location against collapse time: what G2 can claim (V5)

(252.311 - 217.972)/252.311 = 13.61 per cent (M/8 to M/16 at N = 1e6, unstable member);
252.413 vs 252.311 = +0.04 per cent (shift damping); 229.791 at N = 1e5 vs 252.311 at 1e6.

[JUDGEMENT] What the runs support:
1. A bracket, not a located threshold: on M/8 and M/16 at N = 1e6, and with shift_eta 1 and 2
   on M/8, the model 0.344 collapses and 0.324 holds to 600 M, one seed each. The turning point
   0.3340322 lies inside, so the code's threshold agrees with the turning-point criterion to
   +-0.010 in y0 (+-0.017 in Z(0)), which meets the numerical target of SCOPE.md:325-326 if a
   bracket of that width counts as agreement.
2. Not a convergence of the location in the sense of SCOPE.md:124-130: the scope asks for "a
   located threshold, not a bracket" from the growth rate of the radial mode, and for its
   convergence in N, mesh and gauge or outer boundary. What converges here is a two-member fate
   table; the threshold could move anywhere inside (0.324, 0.344) between meshes without any
   run noticing. The collapse time of the unstable member, the one continuous quantity, moves
   by 13.6 per cent between the two meshes (two meshes, no order).
3. The gauge leg is weak by construction: shift damping does not change the 1+log slicing and
   acts little at the centre; no run varied the slicing or the outer boundary (SCOPE.md:130
   names "domain 512 M against 1024 M; one alternative slicing").
4. The N = 1e5 leg of the bracket depends on the 600 M cut: the stable model's own control
   collapses at 599.99 M there. The bracket at N = 1e5 is the fate of the kicked members at
   600 M, not a stable/unstable separation.
5. Families: SCOPE.md:323-325 names the monoenergetic and the King b = 0.1 families for G2; the
   package covers the King b = 1 family (y0 of 2009.08163) only. The charter's G2 phrase ("the
   collisionless threshold reproduces the literature value with three-way convergence") is met
   for one family as a +-3 per cent bracket around the printed y_max = 0.334.

## 6. The lead's predictions, as written before the runs, judged from my numbers

| Prediction (commit) | Bar as written | Verifier number | Verdict |
|---|---|---|---|
| D2.1 (12183c5d5) | collisions per particle per M independent of f within 5 % | f1 8.851e-3, f2 8.857e-3, f4 8.675e-3 (2.1 %) | HELD |
| D2.2 | t_c(f = 2, M/8) within 10 % of 206.64 | 163.41 (-20.9 %) | FAILED |
| D2.3 | t_c(f1), t_c(f4) within 10 % of t_c(f2); seed pair within 2 M | +0.37 %, +1.57 %; pair 2.24 M | cell part HELD, seed part FAILED |
| D2 control | no collapse in 300 M; change at 280-300 M in [-0.010, +0.002] | none; -0.0049 | HELD |
| A.4 | no control collapses | 534.81, 549.26, 599.99 M | FAILED |
| NS.1 (b7007c99a) | N6c no collapse; change at 400 M above -0.005 | none; +0.0066/+0.0055/+0.0045 (380-400, 390-410, 400-420) | HELD |
| NS.2 | t_c(1e6) in [455, 615] | no crossing | FAILED |
| NS.3 | relaxation: N = 1e4 collapse before 300 M | 295.78 | HELD (by 4.2 M) |
| M16.1 | t_c(M/16) in [140, 170] | 158.42 | HELD |
| M16.2 | rate within 5 % of 8.86e-3 | 8.865e-3 | HELD |
| B17.4 (77a69997a) | eta1: t_c within 5 % of 163.41, rate within 5 % | +0.37 %, -0.85 % | HELD |
| B17.5 (f261c3ec4) | N6b344 collapses, t_c in [200, 400] | 252.31 | HELD |
| B17.6 | N6b324 holds, band +-0.03 | [-0.0119, +0.0150] | HELD |
| BA.1 (a5b72829a) | A324s1c t_c in [570, 600] or none | 599.99 | HELD |
| BA.3 | A.4 stays failed with all three seed-1 controls | all three cross before 600 M | HELD (not failed, see summary) |
| B20.1 | A16b324 holds, band +-0.03 | [-0.0171, +0.0107] | HELD |
| B20.2 | A16b344 same fate, t_c within 20 % | 13.61 % | HELD |
| B20.3 | eta1: same fates, t_c within 5 %, stable difference below 0.01 | +0.04 %; 1.4e-5 | HELD |
| D2eta1 (the run) | 220 M planned | guard stop at 190.375 M (exit 3) | FAILED as a run; t_c unaffected |

B17.1-B17.3 were withdrawn before submission (f261c3ec4) and have no run; A.1-A.3, BA.2 and
the H.* predictions were not judged here.

## 7. Findings beyond the claims

1. BA.3 is listed among the failures (task text; OPEN.md line 6) but held as written (X.2).
2. The collision count test is passed by four of six members before t_c, not by all (section 4);
   the quoted 1.0008 is the best member.
3. A334s3c's history now reaches 600 M (crossing 563.29 M); the batch-20 note that it ends at
   0.25 M is out of date.
4. The M/4 seed-2 collisional run is broken after its first excision (section 4, observation).
5. N = 1e5 fates near 600 M are cut-dependent (A324s1c 599.99 M).
6. The gauge leg changes the shift damping only; slicing and outer boundary were not varied.

## 8. Not checked

- The 15 block A runs beyond the six controls and two kicked members read here (BA.2, A.1-A.3).
- The conductivity series (1.020 +- 0.004) and the heat tests: G1 material, not recomputed.
- Card-hours of the manifests; the note's figures other than by the numbers behind them.
- Whether the history files equal the outputs of the decks (I trust the run directories'
  sha256 lists, which matched); no run was repeated.
- A full byte check of the run directories: the lead's `nrpic-stage verify C-sidm G2 --full`
  (section 9) does that.

## 9. The lead's full checksum pass

`harness/bin/nrpic-stage verify C-sidm G2 --full` (pid 3893805, started 00:53 PST): still
running at 01:13 PST (20 min) with an empty log `scratch/C-sidm/tmp/verify_full_g2.log`; left
alone. Its state at the end of this session is in the README.
