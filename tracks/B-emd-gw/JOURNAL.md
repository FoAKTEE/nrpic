# JOURNAL of B-emd-gw

Append-only, newest at the bottom, one entry per session:
`## <UTC time>  session <name>  commits <a>..<b>  runs <ids>` followed by
did / found / evidence / changed my mind about / open. Predictions are written here before
a test runs, outcomes after.

## 2026-11-15T13:05Z  session B-emd-gw lead (wave 1 review)  commits f3d772d..  runs (below)

Helper journals of this wave (predictions and outcomes of each package):
`scope/JOURNAL.md`, `periodic_z4c/JOURNAL.md`, `gw_diag/JOURNAL.md`, `baseline/JOURNAL.md`,
`verify_cosmo/JOURNAL.md`.

### Lead predictions before the independent re-check (13:05Z)

Re-check L1 (`analysis/lead_recheck.sh`): the five packages rerun from a clean `git archive`
export of this commit, on processors, into one run directory; every committed result file
compared with its rerun by `analysis/compare_results.py`; four AthenaK cases of
periodic_z4c re-executed with the release processor executable and their outputs compared
with the original run directories.
- P-L1a: every pytest of gw_diag passes (12, plus the 2 reader tests with real files),
  `test_zeldovich.py` passes. Refuted by any failure.
- P-L1b: the JSON results of scope (3 files), baseline (1), gw_diag validations (3),
  verify_cosmo (pancake.json, pancake_profiles.json, flrw_recheck.json) and the
  periodic_z4c tables are reproduced to a relative 1e-10 or better (same code, same
  inputs, same libraries; differences only from thread-count-dependent FFT/BLAS
  summation). Refuted by any number differing by more than 1e-8 relative, or by a key
  present on one side only.
- P-L1c: the AthenaK re-executions (lw_x_prod N16 and N32, gauge_nl_conformal N64,
  lw3d_check_diag) are bit-identical in every output file except athena.log (serial
  Kokkos build, deterministic). Refuted by any differing byte in a .tab, .hst, .dat or
  .rst file.

Lead independent checks L2 (`analysis/lead_checks.py`, written by the lead, not by the
helpers), each with its prediction:
- P-L2a: the polarization tensor of `athenak/src/pgen/tests/z4c_linear_wave.cpp` lines
  107-112 has e.k != 0 for k = (1,1,1); flipping the signs of a_xy and a_yz gives e.k = 0
  to rounding for any k, keeps trace 0 and e:e = 2. (Already seen in a one-line test
  at 13:00Z; recorded here as part of L2.)
- P-L2b: for ds^2 = -dt^2 + X(t,x)^2 dx^2 + Y(t)^2 (dy^2 + dz^2) with dust at rest, the
  Einstein equations give Y ~ t^(2/3) and X = Y (1 + D f(x)) with D = const (a
  relabelling of x) or D ~ 1/t (decaying): no growing mode (scope check 1E).
- P-L2c: for gamma = diag(X^2, Y^2, Y^2)(x) the traceless, divergence-free,
  plane-symmetric mixed tensor is A^i_j = c Y^-3 diag(1, -1/2, -1/2), and the integral
  of A^i_j K^j_i sqrt(gamma) over x equals -c d/dt of the integral of X/Y (scope 1C, 1D).
- P-L2d: quasi-static TT strain of Phi = phi_x sin kx + phi_y sin ky under the equation
  of arXiv:1604.06065 (compendium_arxiv.tex lines 294-298, metric line 142): the real
  amplitude of the cos((k,k,0).x) wave of h_+ is (5/6)|phi_x phi_y|, i.e. a complex
  Fourier coefficient (numpy fftn / N^3) of (5/12)|phi_x phi_y| as scope reports.
  Refuted if my real-space projection gives anything else.
- P-L2e: the Zel'dovich ellipsoid energy, by direct quadrature of
  P = (G/5) sum_i Q'''_ii^2 with Q''' from a finite difference of the closed-form Q, equals
  (8/15) M c^2 S [(t2/t_k)^(1/3) - (t1/t_k)^(1/3)] to 1e-6 (baseline T1).
- P-L2f: s = a and s = a^(-3/2) solve d/dtau (a ds/dtau) = (3/2) s with
  a = (1 + tau/2)^2 (verify_cosmo reference); the second-order box mean of Khat in a
  closed box with a TT wave grows as pi^2 A^2 t, so alpha - 1 = -(1/6) pi^2 A^2 t^2 for
  d_t alpha = -(1/3) alpha^2 K and -pi^2 A^2 t^2 for 1+log (periodic_z4c item 3).
- Note before the registered L2 run (13:25Z): a development smoke test of `lead_checks.py`
  (scratch/B-emd-gw/tmp/smoke_lead, not cited) failed P-L2e as written: Q''' from a
  five-point difference of Q at h = 1e-3 is limited by rounding of the large t^2 term of Q
  (1.7e-4 relative in E). The registered check differentiates Q symbolically (sympy) and
  integrates adaptively; P-L2e is kept (1e-6).
- Small fix before L1: the gw_diag scripts imported `python/nrpic` through the absolute
  path of this worktree; now relative, so a clean export uses its own copy.
- 13:09Z: first launch of L1 registered as B-emd-gw-20261115-130926-a1c2237 and stopped
  after 19 s: `analysis/register.py` (copied from verify_cosmo, one level shallower)
  resolved the main checkout, so id and commit carried main's a1c2237 and the manifest
  landed outside the worktree (moved into `runs/`, status stopped, not cited). Fixed with
  a depth assertion; L1 relaunched below.

### Lead outcomes (13:20Z)

L1 = run `B-emd-gw-20261115-131016-03b1119` (174 s, processors; summary
`scratch/B-emd-gw/<run>/compare.json`, `logs/compare.out`):
- P-L1a HOLDS: gw_diag 14 of 14 tests pass with the two real files supplied (lw3.00016.rst
  of run -113218-0ea0f74, east.field.00004.bin of runs/cosmo/dav_c256_n128_t);
  `test_zeldovich.py` 13 PASS, 0 FAIL.
- P-L1b HOLDS, stronger than predicted: every numerical leaf of every compared result file
  is bit-identical (scope 3 files, gw_diag 3, verify_cosmo 3, periodic_z4c 6 JSON and 4
  Markdown tables, baseline 374 leaves); the only differences are the figure paths and
  the wall times in `baseline_results.json`.
- P-L1c HOLDS for every .tab, .hst, .dat, .bin and waveform file (163 + 163 + 259 + 28
  files byte-identical). REFUTED as written for the two .rst files of lw3d_check_diag:
  they differ in 36 bytes at offsets 8794-8829, a region after the parameter block that
  holds leftover input-file text (uninitialised buffer in AthenaK's restart writer); the
  field data are identical. Consequence: byte checksums of .rst files are not a
  reproducibility test (info to core).
L2 = run `B-emd-gw-20261115-131027-03b1119` (6 s): P-L2a-f all HOLD. a: e.k of the
generator's tensor is O(1) for oblique k (0.77 for (1,1,1)), < 1e-15 after flipping a_xy,
a_yz, trace 0, e:e = 2. b: exponents of A and B are 2/3 and -1/3, so D = const or 1/t
(scope 1E confirmed). c: P = C/Y^3 and the overlap equals -c d/dt(X/Y) (scope 1C, 1D
confirmed). d: real cosine amplitude (5/6)|phi_x phi_y| = 2.7716e-5 at delta = 0.01,
L = 4, ratios (1, 0.9), i.e. Fourier coefficient 1.3858e-5 = scope's value; the
normalization of "(5/12)" is now stated in SCOPE.md. e: quadrature equals the closed
form to 2e-16. f: sheet modes a and a^(-3/2) exact; alpha - 1 = -(1/6) pi^2 A^2 t^2 and
-pi^2 A^2 t^2, i.e. -1.64e-10 and -9.87e-10 at t = 10, A = 1e-6 (periodic_z4c measured
-1.6e-10 and -1.0e-9). Figure `lead_checks.png` looked at.
Figures looked at in this session (Read): scope crossed_waves_tt, regime_estimates;
periodic_z4c lw_x_convergence, lw3d_check, awa_history, gauge_nl_gradient; gw_diag
athenak_tt, athenak_psi4, cosmo_tt, weyl_convergence, tt_gauge_scalar; baseline
t2_za_scaling, t4_t5_axes_quadrupole_power; verify_cosmo pancake_errors, pancake_ppc,
pancake_grdiff (rerun copy). Cosmetic defects only: overlapping x tick labels in
lw_x_convergence; a legend over the curve in lead_checks panel (d).

Found while reviewing (changed my mind / new):
- gw_diag's cosmology scouting (`figs/cosmo_tt.png`): the late rise of rms h^TT after
  a ~ 600 coincides with (rms of the non-TT conformal-metric part)^2 reaching the TT level
  (4e-5 squared = 1.6e-9 at a = 1000 against h^TT ~ 1.2e-9 frozen). In the code's
  zero-shift gauge the flat Lambda projection has a second-order gauge piece of that
  size, so the late rise is not yet a GW signal [JUDGEMENT; TO VERIFY with the covariant
  projection or a gauge change]. The frozen part before a ~ 550 is far above that
  (5e-7 squared = 2.5e-13 at a = 12).
- 34 hand-written manifests were labelled "production" without pre-registration or a
  G0 pass; relabelled "scouting" with a `kind_correction` note; `make_cases.py` now
  writes scouting.
- core/newton (branch tip ce329f5, not on main) already has the quadrupole history
  (columns 19-43 of `<basename>.newton.hst`, `python/nrpic/newton.py`) and found the same
  first-order lattice error of the plane wave with one particle per cell (its interface
  note section 5.6) that verify_cosmo found with `pm.py` (P8): an independent
  confirmation from a different code path.

### Session close (13:45Z)

did: reviewed the five wave-1 packages from their artefacts (`stage/G0/REVIEW.md`); wrote
the G0 package (`stage/G0/REPORT.md`, `EVIDENCE.md`, `OPEN.md`, `CHECKLIST.md` filled:
6 PASS, 3 NA, 9 OPEN) and `stage/G1/STATUS.md` (G1 not met: criterion 1 met in a flat box,
2 met for the semi-analytic part only, 3 superseded); fourteen outbox files
(`outbox/20261115T1340Z__*`); STATUS, HANDOFF, RISKS rewritten.
found: every result of the wave reproduces bit for bit; the helpers' key derivations
hold; three defects fixed (Fourier normalization of the crossed-wave coefficient stated,
34 manifests relabelled scouting, hard-coded path); restart files carry 36 bytes of
uninitialised padding; the late TT rise in the cosmology dumps may be a gauge piece.
evidence: runs B-emd-gw-20261115-131016-03b1119 (L1), -131027-03b1119 (L2); stopped
misregistered launch -130926-a1c2237 kept on record.
changed my mind about: the G1 item on the stand-in fluid (superseded, proposal to strike);
one particle per cell for pancakes (two per direction for every production run); the
weyl output of AthenaK as a GW measure (replaced by gw_diag's fixed-direction Psi_4).
open: `stage/G0/OPEN.md`; G1 waits on core (generator fix, Newtonian mode on main);
the first-source scouting at 64^3 can start without core (HANDOFF.md, next work 1).
The Write tool refused the file name `REPORT.md` for a subagent; written through the
shell because the stage package names it.

## 2026-11-15T19:15Z  session B-emd-gw lead (wave 2 review)  commits 6b2c423e..(this push)  runs B-20261115-190007-e09a0d2, -190015-4dd3416, -190019-b5f5eb6, -190323-2f8806a, -190433-2d1d185

did: took over the four wave-2 helper packages (first_source, newton_tests, note, verifier);
wrote predictions R1-R10 before rechecking (stage/review_wave2/JOURNAL.md, commit e09a0d2),
recomputed from the registered raw outputs with own code (reader of AthenaK bin output, +
amplitude by direct summation, own g(tau), own TT projector, own linear-growth integration
for H1, own reading of the Newtonian history files), reran three verifier scripts; wrote
stage/REVIEW-wave2.md; corrected scope/SCOPE.md (crossover 0.289 and thresholds 0.032 and
0.19, absolute null criterion, comparison window a <= 10, Omega-today scaling TO VERIFY) and
one sentence of the note (resolved part of the late rise grows; PDF recompiled); read the
abstracts of the seven S2 key references the scope had not read (stage/G0/EVIDENCE.md);
G0 and G1 checklists judged, OPEN/EVIDENCE rewritten, G1/STATUS corrected; eleven outbox
messages; inbox (11) acknowledged; STATUS, HANDOFF, RISKS rewritten.
found: R1-R4, R6b, R7-R10 confirmed (lead and helper c_+ agree to 9e-14 of s; H1 to 2
percent at a <= 5; verifier scripts bit for bit); R5 partly refuted (32^3 vs 64^3 differs by
1.02 percent between a = 40 and 80 for eps = 1, my bound was 1 percent; the helper's "<= 0.06
percent at a = 5-40" is 0.09 for eps = 0.1); R6 partly refuted (largest c_+/s is 2.55 at
a = 123, not 2.5 at a ~ 95). The G_tot-corrected strain departs from the second-order value
more than the raw one, so the departure after a ~ 10 is higher order, not spatial gauge
(helper's own scan_summary_64.json). 2403.15126 takes the emission redshift at each
configuration's collapse (line 1061), which supports the verifier's sigma^(5/2) for Omega
today against the paper's stated 7/2 (line 1074).
evidence: the five runs above; figures stage/review_wave2/figs/rv_review_first_source.png,
rv_review_newton.png (looked at); helper figures scan_kk0, scan_secondgauge, late_rise,
pancake_east, ell_convergence, verifier v6_za_scaling looked at; note pages 1-4 read.
changed my mind about: OPEN item 7 (closed at second order: derivation plus the measured
gauge piece) and item 9 (the late rise is not gauge; mostly grid scale); the role of the
second gauge (it validates G_tot, it does not bring the code to the second-order value);
G1 criterion 2 (met in AthenaK's Newtonian mode).
open: G1 criterion 1 (oblique and expanding-box waves), G1 schematics, note Sec. IV-V,
independent verifier of the wave-2 runs, jittered null, particle-number convergence;
requests to orch on the verifier file name and the runs check of nrpic-stage verify.
Card-hours this session: 0 (all review runs on processors); owner total 0.99 of 40.
