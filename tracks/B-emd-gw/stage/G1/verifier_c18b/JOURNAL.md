# JOURNAL of stage/G1/verifier_c18b (second verifier of G1 item C18, B-emd-gw)

## 2026-11-21 08:55 PST — entry 1: scope and predictions (written before any recomputation)

Scope (decision 0023 item 2; package brief in the batch-4b task): the ledger rows of
`tracks/B-emd-gw/note/tables/ledger.tex` still without an independent value, lines 34-36,
49-63, 70-71, 124, 199, 217. Read so far: CLAUDE.md, CHARTER to "Owners", decisions 0010 and
0023, the coverage list of VERIFIER-C18.md (section 5 only) and the one-row list of
REVIEW-wave3.md, the ledger itself, the manifests of the cited runs, and the producing
scripts only for the definitions of the quantities (ledger.py, analyze_pancake.py,
regime_estimates.py, lead_checks.py e/f, g1data.py Weyl block, make_waves.py/torus_id.py
residuals). Nothing of their code is imported; each value is recomputed by my own scripts
under `scripts/` from the raw outputs (AthenaK trajectories, snapshots, histories, field and
restart dumps; the Newtonian `newton.npz`; the tool's `fields.bin`/`particles.nrp`; Slurm
logs), or for the analytic rows from my own derivation.

General prediction: every recomputed value agrees with the printed value to the printed
digits (three significant figures, rounding of the last digit allowed). Refuted for a row if
my value differs by more than one unit of the last printed digit and the difference is not
explained by a stated choice of the definition (interpolation, sampling). Specific
expectations and refutation criteria:

- P1 (line 34): omega_vir/(c k1) = 2 sqrt(Delta_vir/2) H_c(a_c) / k1 with
  Delta_vir = 18 pi^2, a_c = 0.56/delta, H_c = a^-1/2, k1 = 2 pi/4 is 12 sqrt(delta/0.56):
  0.802 at delta = 0.0025 and 3.586 at delta = 0.05. Expect the ledger's 0.81 and 3.57 to be
  the values at the first and last points of a sampled delta grid inside the range (so
  1 per cent from the closed-form endpoints). Refuted if no sampling reproduces 0.81 and
  3.57, or if the closed form itself is off (I check Delta_vir and the virial relation
  omega^2 = (Delta/2) H^2 myself, and a_c = 0.56/delta against the cosmo/TESTLOG locator).
- P2 (lines 35-36): card-hours = steps x cells / rate, steps = ceil(t_end/(0.25 L/n)),
  t_end = 2(sqrt(a_end) - 1), rates from the two cited AthenaK logs. Expect the eight values
  to the printed digits, and the rate model to predict the wall time of the measured pancake
  runs (Slurm job 4373, same 1-particle-per-cell configuration) within 30 per cent.
- P3 (lines 49-61, pancake): from the trajectories of the tracked x-line particles and the
  Newtonian newton.npz, with my own reader and my own exact Zel'dovich sheets:
  first crossing of exact sheets 21.0 (continuum 1 + 1/delta = 21, discreteness raises it
  by about (k Delta)^2/24 ~ 4e-4); relativistic coordinate-label crossings 21.8, 21.4, 21.3
  within 0.05; Newtonian 21.5, 21.2 within 0.05; position differences at a = 10 to the
  printed digits; the four-Hubble-radius over one-Hubble-radius ratio near 16 = (L4/L1)^2
  (the relativistic correction scales as (k/H)^-2); constraint means from the code's
  cstat.hst to the printed digits, and the cstat column "Hr_mean" equal (within a few per
  cent) to my own mean |H| / (16 pi <E>) from the NRFIELD2 dumps at the same time if that
  is the code's normalization (if not, I record the normalization I find); plane symmetry
  below 1e-13 L and 1e-11 in u_perp from the snapshots; card-hours from the Slurm logs
  (0.284 = 17 min 03 s on one card; the second job 0.197).
- P4 (line 63): from the cited history files (checksums against the manifest first):
  |alpha/(1 + t/2)^2 - 1| largest 1.91e-7 (flrw_n32_cpu_sd, a <= 4) and 7.0e-8
  (dtexp_test/lim, a <= 36); last Hr_max of dtexp_test/lim 6.05e-8.
- P5 (line 70): closed form E = (8/15) M S (t2^(1/3) - t1^(1/3)) holds exactly (my own
  derivation: Q''' is proportional to t^(-1/3) because the a^3 = t^2 term has no third
  derivative); my quadrature with a different method (Gauss-Legendre in u = t^(1/3), or
  mpmath) agrees to <= 1e-13. The printed 2.22e-16 is one unit of rounding; I expect to
  confirm "agreement at rounding", not the digits of the rounding itself.
- P6 (line 71): with <K> = <K_ij K^ij> t = pi^2 A^2 t (vacuum torus, alpha = 1 + O(A^2)),
  conformal lapse delta alpha = -pi^2 A^2 t^2 / 6 = -1.645e-10, 1+log
  delta alpha = -pi^2 A^2 t^2 = -9.87e-10 at t = 10, A = 1e-6 (A the strain amplitude of
  h_yy = -h_zz). Refuted if my derivation gives another factor.
- P7 (line 124): from the double-precision restart dumps of cw_eps1 and cw_eps1_gd
  (B-20261115-165353-b592d43) with my own B_ij = sym-tracefree eps_i^{kl} D_k K_lj and my
  own TT strain: median relative gauge difference over common dumps with 1.5 < a <= 64 of
  the cross part of B at K1 = (k, k, 0) about 1e-3 and of the flat TT strain about 1.4e-2,
  each within 30 per cent of the printed 0.00121 and 0.0139 (a median of ratios depends on
  the exact component and phase convention; a factor two would refute).
- P8 (line 199): from fields.bin (psi, K, Ahat) and particles.nrp of the three initial-data
  sets with my own PCS deposit, the code's compensation pass (NrpicCompensateLimited,
  c = 1/6, c2 = 7/15) and my own spectral derivatives: Hamiltonian residual at the 1e-11
  level (<= 1e-10) for all three if my deposit is the tool's; momentum residual about
  7.6e-4, 2.8e-4 for jitter 0.3, 0.1 (within 20 per cent: the value is a maximum over the
  mesh and sits in the modes near the mesh frequency, where the treatment of the Nyquist
  modes matters) and at rounding (< 1e-15) for the unjittered lattice.
- P9 (line 217): the pairs compared are 30 (6 + 6 + 3 + 3 + 4 + 4 + 4 over lines 201, 202,
  204, 205, 211, 212, 209); the helper's comparison files (163037, 164017) agree with the
  values the ledger prints to the printed digits, and with my own reduction of the same
  per-dump diagnostics to <= 1e-10.

What I will not do: rerun AthenaK (no source changed; the rows are about existing runs),
use a card (0 card-hours), read the leads' reviews, STATUS, HANDOFF or journals.

## 2026-11-21 09:05 PST — entry 2: outcomes of P1-P6 (runs B-20261121-170003-23f500e, B-20261121-170159-535438f)

Run B-20261121-165713-459347e (first pancake pass) is superseded: it did not wrap the
Newtonian sheet that starts at x = 1.008 L into the box, so the Newtonian crossings came out
negative and the relativistic-minus-Newtonian differences were 14 (a reader error of mine,
visible at once; the relativistic numbers of that run were already right).

- P1 (line 34): held in substance. 12 sqrt(delta/0.56) = 0.802, 3.586 at the endpoints of the
  stated range; the printed 0.81, 3.57 are the values at the first and last points of the
  60-point grid inside the range (delta = 0.00255, 0.0495): 0.810, 3.569. a_c = 1.686/(3 delta)
  = 0.562/delta, my own reading of the threshold, agrees with the 0.56 of cosmo/TESTLOG.md:139.
- P2 (lines 35-36): held. All eight values to the printed digits (0.0175, 0.362, 5.79, 0.362;
  0.0366, 0.757, 12.1, 0.757). Rates from cells x cycles / cpu time of the two logs (checksums
  match the manifest): 5.770348e6 and 4.467126e6 (the code printed 4.467127e6); dt = 0.25 L/n is
  what the logs show (the 64^3 log starts with smaller, expansion-limited steps: 1404 cycles
  where the model counts 1387, so the measured 64^3 run took 0.01772 card-hours against the
  estimate 0.0175). The model also predicts the pancake jobs: L1_n96 834 s against 834 s
  measured, L1_n64 128 s against 135 s; the two small ones (8 s, 32 s against 13 s, 40 s) are
  dominated by start-up. Within 30 per cent for the runs that matter.
- P3 (lines 49-60): held for every printed number, with three qualifications.
  Crossings: exact sheets 21.03 (printed 21); relativistic 21.81, 21.38, 21.27 (21.8, 21.4,
  21.3); Newtonian 21.55, 21.22 (21.5, 21.2); four Hubble radii 22.85, proper time 22.28,
  one Hubble radius 21.35 (22.8, 22.3, 21.3). Position differences at a = 10 (both runs
  interpolated to a = 10 exactly): 0.003216, 0.003203, 0.003202 (96 cells vs Zel'dovich),
  0.05168, ratio 16.14 (0.00322, 0.0032, 0.0032, 0.0517, 16.1); 64 cells one and two per cell
  0.003195, 0.003205 (0.0032, 0.00321); Newtonian 0.001016, 0.002050, 0.000408 (0.00102,
  0.00205, 0.000408). Constraints (code's cstat.hst, nearest record): Hr 1.576e-4, 1.289e-3,
  3.216e-5, 4.249e-5; Mr 0.2112, 0.00631; ratios 30.35, 33.47; plane symmetry 4.51e-14,
  1.25e-12. Card-hours: sacct 1023 s and 710 s on one card: 0.284, 0.197, 0.481.
  My sub-prediction "discreteness raises the exact-sheet crossing by ~4e-4" FAILED: it is
  +0.029, because a lattice point sits on the density peak, so the first pair is one-sided:
  a - 1 = (1/delta)(1 + (k Delta)^2/6) with k Delta = 0.0935 (not the symmetric /24). The
  printed "21" is unaffected.
  Qualification 1 (line 59): "largest mean |H| after crossing, a = 22-42" is the largest of
  the five dump epochs a = 22, 25, 30, 35, 41.9 (0.00706, 0.00203). Over all cstat records in
  22 <= a <= 42 the largest is 0.00751 (a = 22.56) and 0.00254 (a = 23.31): 6 and 25 per cent
  higher. Figure pancake_c18b.png panel (c) shows the peaks between the epochs.
  Qualification 2 (line 56): the "a = 10" values are those of the record nearest a = 10
  (a = 9.96). At a = 10.00 (interpolated, and from my own dump-based mean) they are 1.64e-4
  and 3.6e-5, 4 and 12 per cent higher: the two-per-cell curve oscillates by a factor of
  about three around a = 10 (panel c), so the second digit at "a = 10" is not robust.
  Qualification 3: the code's Hr_mean column is |H| / sqrt(R^2 + (2K^2/3)^2 + (A.A)^2 +
  (16 pi E)^2) averaged over cells (nrpic_io.cpp NrpicWriteConstraintStats); my own value from
  the NRFIELD2 dumps (A.A dropped) equals it to 1e-9 relative where dump and record coincide
  (a = 1, 25), so the column is what its header says.
- P4 (line 63): held: 1.914e-7, 7.002e-8, 6.046e-8 (1.91e-7, 7e-8, 6.05e-8); both history
  files match the manifest checksums. The cstat.hst of dtexp_test/lim that gives the third
  value is not among the manifest's checksummed inputs (sha256 ed6353a8...; provenance gap).
- P5 (line 70): held: closed form and mpmath quadrature of the third derivative at 50 digits
  agree to 0 at 50 digits; a Gauss-Legendre double-precision quadrature 1.1e-16. The printed
  2.22e-16 is a rounding unit: confirmed as "agreement at rounding", not as digits.
- P6 (line 71): held: -1.6449e-10 (conformal), -9.8696e-10 (1+log), closed form and ODE.

## 2026-11-21 09:25 PST — entry 3: outcomes of P7-P9 (runs B-20261121-170611-c616c57, B-20261121-171152-4241a93, B-20261121-171519-ad8f227)

- P8 (line 199): held. Own PCS deposit + the code's compensation pass + spectral derivatives
  give momentum residuals 7.628667399551e-4, 2.827786570410e-4 (id.json: the same to 4e-15
  relative) and 4.9e-17 for the unjittered lattice (id.json 3.1e-17: rounding). The deposit
  integrates to the particle sum to 4e-16. The Hamiltonian residual came out 1.0e-9 and
  3.3e-10 for the jittered cases with my first choice of psi at the particles (tensor cubic
  Lagrange): a sub-prediction that FAILED (expected ~1e-11). Cause shown by a run that could
  have failed: with the cubic B-spline interpolant (scipy ndimage order 3) the residuals are
  3.6990e-11, 4.4963e-12, 4.782e-12, equal to id.json to four digits; with linear
  interpolation 3.0e-9. The jittered psi has grid-scale structure (the interpolants differ by
  2.8e-5 at the particles), which enters E through W - 1 ~ 2e-5. So the printed 3.7e-11 is the
  residual for the tool's interpolant; any other reasonable interpolant gives <= 3e-9, still
  negligible against the largest term (1.04). New finding: the momentum residual sits on the
  Nyquist planes of the mesh (share of its power 1 - 4e-10 for jitter 0.3): it is the part of
  the jittered momentum source at the mesh frequency, which spectral first derivatives
  cannot represent and the vector solve therefore drops.
- P7 (line 124): held. Own restart reader (checked: t = 0 dump equals the code's field dump
  for chi to float32 rounding 5.9e-8 and for Khat, Theta, alpha exactly; det(gtilde) - 1
  <= 8.9e-16 and gtilde^ij Atilde_ij <= 5.4e-20 at all 46 dumps) and own full nonlinear B_ij
  (checked on an analytic TT wave: cross amplitude to 5e-16). Medians over the 13 common dumps
  with 1.5 < a <= 64: magnetic Weyl 0.001205, flat TT strain 0.01385 (printed 0.00121, 0.0139).
  Sensitivity: the dump at t = 14.008 has a = 64.07 and falls just outside the window; with it
  (14 dumps) the medians are 0.00185 and 0.0157. The B_x amplitude passes through zero near
  a = 6 and 42, where the relative difference spikes (figure weyl_c18b.png); the median is
  robust to those two.
- P9 (line 217): held. 30 pairs (6 + 6 + 3 + 3 + 4 + 4 + 4). Every printed value agrees with
  the comparison files to its three digits (largest relative difference 3.8e-3 = rounding,
  e.g. 1.0 for 1.0038). My own reduction agrees with the files exactly for 22 numbers and to
  <= 1.6e-9 for the eight departure ratios R; with the integration tolerance of the track's
  reference ODE (rtol 1e-11, atol 1e-14) instead of my 1e-12 the largest difference is
  1.9607e-12, the printed 1.96e-12. So the second reading's agreement sits at the shared ODE
  tolerance; the R values themselves carry ~1.6e-9 from it, far below the printed digits.
