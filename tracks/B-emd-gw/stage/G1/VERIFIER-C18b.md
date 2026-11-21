# VERIFIER-C18b: second verifier of G1 item C18 of B-emd-gw (2026-11-21)

Package `stage/G1/verifier_c18b/` (decision 0023 item 2). Scope: the rows of the working
note's ledger (`note/tables/ledger.tex`, line numbers of that file at commit e17a5e4e) that
had no independent value: lines 34-36, 49-63, 70-71, 124, 199, 217. Every value below was
recomputed by my own scripts from the registered raw outputs, or, for analytic rows, from my
own derivation; processors only, 0 card-hours. Verdicts: CONFIRMED (my value agrees with the
printed one to its digits), NOT CONFIRMED (the printed value is not what the row says it is),
WRONG (the value is false). Labels: every number here is [VERIFIED] by the run named with it
unless marked otherwise.

## 1. How it was done, and the limits of independence

- Read: CLAUDE.md, CHARTER to "Owners", decisions 0010 and 0023, the coverage list of
  VERIFIER-C18.md (its section 5) and the one list of REVIEW-wave3.md (section "Batch 4a"),
  the ledger, the manifests of the cited runs. Not read: STATUS, HANDOFF, journals, the
  leads' reviews beyond that list.
- The producing scripts (ledger.py, analyze_pancake.py, regime_estimates.py, lead_checks.py,
  g1data.py, conv_compare.py, make_waves.py/torus_id.py) were read only for the definitions
  of the quantities. No code of the track or of the first verifier was imported; `vlib.py`
  was not used (my own restart reader replaces it).
- Raw inputs: AthenaK trajectories, snapshots, histories, NRFIELD2 and restart dumps; the
  Newtonian `newton.npz`; the initial-data tool's `fields.bin`/`particles.nrp`; AthenaK logs;
  Slurm accounting. Formats from docs/FORMATS.md and the writers in athenak/src.
- Limit: line 217 is a bookkeeping row about two reductions of the same per-dump diagnostics
  (the case JSON files of the analysis runs); my check is a third reduction of those files,
  not a recomputation of the per-dump values from the dumps (the first verifier did that for
  lines 197-216).

Registered runs (all `kind = scouting`, gate G1, local, 1-4 cores):

| run id | script | rows |
|---|---|---|
| B-20261121-165713-459347e | scripts/pancake.py, first pass | superseded (Newtonian sheet at x = 1.008 L not wrapped into the box: my reader error) |
| B-20261121-170003-23f500e | scripts/pancake.py | 49-60 |
| B-20261121-170159-535438f | scripts/small_rows.py | 34-36, 61, 63, 70, 71 |
| B-20261121-170611-c616c57 | scripts/residuals.py | 199 |
| B-20261121-171152-4241a93 | scripts/weyl.py | 124 |
| B-20261121-171519-ad8f227 | scripts/r2second.py | 217 |

## 2. Verdicts per ledger line

| line | quantity (short) | printed | mine | verdict |
|---|---|---|---|---|
| 34 | omega_vir/(c k1), delta 0.0025-0.05, L = 4 | 0.81, 3.57 | 0.810, 3.569 on the 60-point delta grid of the definition (delta = 0.00255, 0.0495); 0.802, 3.586 at the stated endpoints | CONFIRMED (1 per cent; see 3a) |
| 35 | card-hours, delta 0.01 to a = 140 | 0.0175, 0.362, 5.79, 0.362 | 0.01750, 0.3617, 5.787, 0.3617 | CONFIRMED |
| 36 | the same, delta 0.0025 to a = 560 | 0.0366, 0.757, 12.1, 0.757 | 0.03662, 0.7567, 12.11, 0.7567 | CONFIRMED |
| 49 | first crossing of exact Zel'dovich sheets, 64 | 21 | 21.029 | CONFIRMED |
| 50 | relativistic crossing, L1, 32/64/96 | 21.8, 21.4, 21.3 | 21.808, 21.379, 21.267 | CONFIRMED |
| 51 | Newtonian crossing, 32/64 | 21.5, 21.2 | 21.547, 21.222 | CONFIRMED |
| 52 | L4 label; L4 proper time; L1 proper time | 22.8, 22.3, 21.3 | 22.846, 22.280, 21.348 | CONFIRMED |
| 53 | GR - Newton at a = 10 (L1 32, 64); GR - Zel (96); L4; ratio | 0.00322, 0.0032, 0.0032, 0.0517, 16.1 | 0.003216, 0.003203, 0.003202, 0.05168, 16.14 | CONFIRMED |
| 54 | GR - Zel at a = 10, 64 cells, 1 and 2 per cell | 0.0032, 0.00321 | 0.003195, 0.003205 | CONFIRMED |
| 55 | Newton - Zel at a = 10: 64; 32; 32 two per cell | 0.00102, 0.00205, 0.000408 | 0.0010155, 0.0020504, 0.00040795 | CONFIRMED |
| 56 | mean H relative, a = 10, 15; one and two per cell | 0.000158, 0.00129, 3.22e-5, 4.25e-5 | 1.576e-4, 1.289e-3, 3.216e-5, 4.249e-5 (records nearest a, at a = 9.96, 15.02) | CONFIRMED (see 3b) |
| 57 | mean M relative, a = 15 | 0.211, 0.00631 | 0.2112, 0.006310 | CONFIRMED |
| 58 | ratios one to two per cell, a = 15 | 30.3, 33.5 | 30.35, 33.47 | CONFIRMED |
| 59 | largest mean H after crossing, a = 22-42 | 0.00706, 0.00203 | 0.00751 (a = 22.56), 0.00254 (a = 23.31) over all records; 0.00706, 0.00203 over the five dump epochs 22, 25, 30, 35, 41.9 | NOT CONFIRMED as worded (see 3c) |
| 60 | plane symmetry: spread of x over a plane; transverse velocity | 4.51e-14, 1.25e-12 | 4.508e-14 (from the x-line observer of each plane; full range 7.3e-14), 1.254e-12 | CONFIRMED |
| 61 | card-hours of the pancake jobs | 0.284, 0.197, 0.481 | sacct: 1023 s and 710 s on one card: 0.2842, 0.1972, 0.4814 | CONFIRMED |
| 63 | lapse error a = 4, a = 36; H at a = 36 | 1.91e-7, 7e-8, 6.05e-8 | 1.914e-7, 7.002e-8, 6.046e-8 | CONFIRMED (provenance note 3d) |
| 70 | ellipsoid energy, quadrature vs closed form | 2.22e-16 | 0 at 50 digits (mpmath third derivative and quadrature); 1.1e-16 in double precision | CONFIRMED (agreement at rounding; the printed digits are one rounding unit) |
| 71 | second-order lapse, t = 10, A = 1e-6: conformal; 1+log | -1.64e-10, -9.87e-10 | -1.6449e-10, -9.8696e-10 (closed form -pi^2 A^2 t^2/6, -pi^2 A^2 t^2; ODE) | CONFIRMED |
| 124 | median gauge difference a <= 64: magnetic Weyl; flat TT strain | 0.00121, 0.0139 | 0.001205, 0.01385 (13 common restart dumps) | CONFIRMED (see 3e) |
| 199 | jittered data: momentum residual 0.3, 0.1, none; Hamiltonian residual | 0.000763, 0.000283, 3.12e-17, 3.7e-11 | 7.6287e-4, 2.8278e-4, 4.9e-17, 3.699e-11 | CONFIRMED (see 3f) |
| 217 | second reading: numbers compared; largest relative difference | 30, 1.96e-12 | 30; 1.9607e-12 with the track's ODE tolerance | CONFIRMED (see 3g) |

Lines 48 and 62 are section headers. All rows: 22 numbered lines with 58 numbers; 56 numbers
CONFIRMED, line 59's two numbers NOT CONFIRMED as worded, none WRONG.

## 3. Qualifications and findings

a. Line 34. With Delta_vir = 18 pi^2 [BACKGROUND], omega_GW = 2 sqrt(Delta/2) H_c and
   a_c = 1.686/(3 delta) = 0.562/delta (my own reading; cosmo/TESTLOG.md:139 states 0.56/delta),
   the ratio is 12 sqrt(delta/0.56): 0.802 and 3.586 at the endpoints of the stated range. The
   printed 0.81 and 3.57 are the values at the extreme points of the 60-point grid inside the
   range. A 1 per cent effect on an order-of-magnitude estimate; the note may print "0.80-3.6"
   or keep its numbers with "on a grid of delta".
b. Line 56. The "a = 10" values are those of the cstat record nearest a = 10 (a = 9.96). At
   a = 10.00 (interpolated, and from my own mean |H| of the field dump at a = 9.999) they are
   1.64e-4 and 3.6e-5, 4 and 12 per cent higher: the two-per-cell curve oscillates by a factor
   of about three around a = 10 (figure `figs/pancake_c18b.png`, panel c). The second digit of
   the two-per-cell value at "a = 10" is not robust; the conclusions (ratios ~30) are.
c. Line 59. The printed values are the largest of the five dump epochs, not the largest over
   a = 22-42: over all records the largest are 0.00751 and 0.00254 (6 and 25 per cent higher).
   Suggested wording: "largest at the dumps a = 22, 25, 30, 35, 42" or print 0.0075, 0.0025.
   The code's column Hr_mean is what its header says: my own cell average of |H| over the
   sum-of-squares scale from the NRFIELD2 dumps equals it to 1e-9 where dump and record
   coincide (a = 1, 25).
d. Line 63. The two history files match the checksums of manifest B-emd-gw-20261115-115414-7ffbde1;
   the cstat.hst of runs/cosmo/dtexp_test/lim that gives the third value (sha256 ed6353a8...)
   is not among that manifest's checksummed inputs.
e. Line 124. The window a <= 64 excludes the dump at a = 64.07 (t = 14.008); with it the
   medians are 0.00185 and 0.0157. The magnetic part passes through zero near a = 6 and 42
   (figure `figs/weyl_c18b.png`), where the relative difference spikes; the median of 13 is
   robust to those. My B_ij is the full nonlinear sym eps_i^{kl} D_k K_lj with spectral
   derivatives (the track's uses sixth-order differences): the agreement does not depend on
   the derivative scheme at this mode.
f. Line 199. The momentum residuals agree with id.json to 4e-15 relative. The Hamiltonian
   residual depends on how psi is interpolated to the particles (it enters only through the
   Lorentz factor): 3.699e-11 with a cubic B-spline (the printed value), 1.0e-9 with cubic
   Lagrange, 3.0e-9 with linear interpolation; all negligible against the largest term (1.04).
   Finding [VERIFIED, run B-20261121-170611-c616c57]: the momentum residual lies on the Nyquist
   planes of the mesh (1 - 4e-10 of its power for jitter 0.3), i.e. it is the part of the
   jittered lattice's momentum source at the mesh frequency that spectral first derivatives
   cannot represent; what the code's differences do with that part was not checked.
g. Line 217. The 30 pairs are lines 201 (6), 202 (6), 204 (3), 205 (3), 211 (4), 212 (4),
   209 (4). Every printed value equals the comparison files to its three digits. My third
   reduction agrees with the files exactly for 22 numbers; the eight departure ratios R depend
   on the solution g(tau) of the box-mode ODE: with my tolerance (rtol 1e-12) they differ by
   up to 1.6e-9, with the track's (rtol 1e-11, atol 1e-14) by 1.96e-12, the printed value.
h. Sub-prediction failed (journal entry 2): the exact-sheet crossing is 21.029, not 21.0004:
   a lattice point sits on the density peak, so the first crossing pair is one-sided and
   a - 1 = (1/delta)(1 + (k Delta)^2/6). The printed "21" is unaffected.

## 4. What was not checked

- Lines outside the package's list. In particular the round-3 items the lead's review also
  routed here (P16' per-shell fractions, P16'(v)) are not ledger rows and were not done.
- The physical correctness of the cost model beyond its own inputs (the throughput of
  8-particle-per-cell runs, card memory) and of the infall law a_c = 0.56/delta beyond the
  linear threshold (both [JUDGEMENT] estimates of the scope).
- What AthenaK's finite differences make of the Nyquist-plane momentum residual of the
  jittered data (3f).

## 5. Requests

- To the B lead (note v3): reword or recompute line 59 (3c); optionally lines 34 and 56
  (3a, 3b); add the cstat.hst of dtexp_test/lim to the inputs of the run behind line 63, or
  cite it with its checksum (3d).
- None to other owners.
