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
