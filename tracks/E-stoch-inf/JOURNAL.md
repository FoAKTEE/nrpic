# JOURNAL of E-stoch-inf

Append-only, newest at the bottom, one entry per session:
`## <UTC time>  session <name>  commits <a>..<b>  runs <ids>` followed by
did / found / evidence / changed my mind about / open. Predictions are written here before
a test runs, outcomes after.

## 2026-11-15T13:55Z  session lead (Opus)  commits e303538..  runs see below

Lead session of the first wave. The four helpers (spec = E-pre-1, codebase = E-pre-2,
langevin = E-pre-3, noise = E-pre-4) finished; their journals are
`spec/JOURNAL.md`, `codebase/JOURNAL.md`, `langevin/JOURNAL.md`, `noise/JOURNAL.md`.
This entry records the lead's independent check of their artefacts, the check of core's
implementation on `core/scalar-field` (836ac86), and the G0 package.

### Predictions, written before the lead's runs (13:55Z)

L-R (reruns, `analysis/lead/rerun_helper.sh`, one registered run per package). Every
deterministic script reproduces its helper's numbers: numeric JSON leaves identical or
within 1e-9 relative (same code, same seeds, same machine). The langevin quadratic
reference rerun with 1e5 instead of 1e6 realisations (other effective sample): var/var_lin
at sigma = 0.01 within 3 of its standard errors (about 0.004) of the helper's 0.9981, and
sigma = 1 within 0.01 of 1.4492. Refuted by any deterministic leaf off by more than 1e-9
or a statistical one off by more than 3 standard errors.

L-B (`analysis/lead/lead_bg.py`, own integrator and own fixing formula, not the helper's).
Quadratic: phi0 = -14.0950, m = 1.73494e-6, eps1(N*) = 1.1107e-2 and V(N*) = 2.690e-2
(Mpl = 100 units) to 4 digits; inflection: USR (eps2 > 3) from about 2.5 to 6.5 e-folds
after N*, eps1 minimum near 1e-12. One slow-roll mode leaving at N* + 1.5: with metric
perturbations P_R(N_f) within 2 percent of H^2/(8 pi^2 eps1) at exit and a super-horizon
slope of ln P below 2e-3 per e-fold (3 to 6 e-folds after exit); without them a slope
within 15 percent of -4 eps1. Refuted by a digit mismatch of the background or slopes
outside these bands.

L-N (`analysis/lead/lead_dn.py`, iterated first-passage integrals, not the helper's
recursion). V2 of 2206.11234: <N> = 9.38603 and var N = 4.52154 to 1e-4 relative.
Refuted by a larger difference.

L-I (derivation, no run). The delta-Pi erratum of SPEC 5.3 follows from P2's own
dictionary (main_V2PRD.tex 297-313): delta Pi = d/dt delta phi^NR - phidot Psi_G with
chi^NR = int (Psi_G - Psi_B) dt; at t* (chi_0 = 0) the extra term is -sqrt(2 eps1) Mpl H
Psi_B whatever Psi_G is. Refuted if the dictionary gives a different term.

L-U (core's generator, `analysis/lead/u_runs.py`, runs U1-U8 of noise/NOISE_SPEC.md
section 9 with core's processor executable `wt/core-scalar/.work/exe/athena_cpu_836ac86`,
read only). Every deterministic test of the validator passes: A0 format, A1 exact
reconstruction from the keys (to 1e-11 of the rms; the dumps are double precision), A5,
A6, A8, A10, A11 (1, 8, 64 MeshBlocks bit-identical), A12 (restart at cycle 150
bit-identical), A13 (N = 32 against N = 64), A15 (seeds); the statistical tests pass at
the family-wise level 1e-3/D. Refuted by any deterministic failure; a single statistical
failure with all deterministic tests passing is read by the rule of NOISE_SPEC 10 (repeat
on U8). A smoke run of 4 cycles first measures the time per run.

13:58Z, smoke L-U0 (run E-20261115-135218-bdf4710; nrpic-run names runs with the short
owner id "E"): 4 cycles of the 64^3 base case took 78 s of processor time, 1.35e4
zone-cycles per second (the processor build of core's executable runs serially; Z4c
dominates). The 64^3 x 300-cycle base case would cost about 95 min per run, nine runs.
Change before the runs: a scaled base case `inputs/u_base32.athinput` (N = 32, nmax2 = 100,
hubble 1.1, 120 cycles, dumps every 40, restart at 60; U3 = 64 MeshBlocks of 8^3; U5a/U5b
N = 16 and 32 with nmax2 = 36). The predictions of L-U stand unchanged for this case;
statistical tests at shells with fewer than 100 effective modes report "n/a" by the
validator's rule. The 64^3 x 300 base case stays pending (card or a longer processor run).

### Outcomes so far (14:05Z)

- L-R spec (run E-20261115-135531-0c4e629): holds. All 1182 numeric leaves of
  summary/quadratic/inflection/norm_test identical bit for bit; ic_check identical.
- L-R noise (run E-20261115-135532-5ec2b09, exit 1): holds for every deterministic result
  (T-N0 bit-identity on 153684 + 2000 keys, self-test 49 leaves, T-N8 112 leaves identical;
  T-N1 counts; T-N5 reader bitwise across 1/8/64 MeshBlocks, 5.4e-8, axes 7e-2). The exit 1
  is one leaf: the maximum deviation of the library logarithm, 6.2e-13 against 1.16e-12
  (median 1.1e-15 in both), an environment property of numpy.log, not of the code path.
  Prediction refuted as worded for that one leaf; no consequence.
- L-R codebase (run E-20261115-140116-87c1cc5, exit 1): holds; d1, d3, d4, cost identical;
  in d2 only the six wall-clock "seconds" leaves differ (timings).
- L-B (run E-20261115-135532-3f958a1): holds. phi0 -14.094995, m 1.734945e-6, eps1(N*)
  1.110706e-2, V(N*) 2.69006e-2; inflection USR 2.5237 to 6.5498, eps1 min 9.72e-13 at 8.33.
  SR mode leaving at N* + 1.5: full P_R(N_f) = 1.0108, slope -5.8e-4/e-fold; without metric
  perturbations slope -0.0519 against -4 eps1 = -0.0513 (1.2 percent).
- L-N (same run): holds. <N> = 9.385995 +- 3e-6, var N = 4.5215404 +- 3e-9 (helper: 9.38603,
  4.521540).
- L-I (derivation): holds; written into SPEC 5.3. The printed eq. (17) has a Psi_G term
  (zero in the geodesic gauge, P2:490) where the Psi_B term belongs; it drops the chi-dot
  term of its own dictionary.
- L-U (run E-20261115-135523-a32c3a6): all nine AthenaK runs completed (U1-U3, U5a/b, U6-U8
  in 290-315 s each, U5a 37 s, U4 restart 137 s). Validations: Markov Heaviside passes
  everything; Markov tanh passes A0, A2-A8, A10 and FAILS A1 (exact reconstruction:
  1.07e-10 of the rms against 1e-11, worst stoch_c2 at cycle 120); the frozen validation
  did not run: the validator read U5a (N = 16) with U1's nmax2 = 100 and stopped ("cut
  reaches the Nyquist plane"). The second is a defect of the validator (it would have hit
  the specification's own base case, nmax2 = 256 at N = 32, the same way); fixed by the
  lead: `--res-lo-input`, `--res-hi-input`.

### Predictions before the follow-up runs (14:06Z)

L-U2 (`analysis/lead/lu_diag.py` on U6 and U1). The A1 excess of U6 is the conditioning
of sqrt(W(t) - W(t - dt)) for modes long past crossing (W near 1; both code and reference
form the difference naively, with libm and numpy exponentials that may differ by an ulp).
Expected: on modes with dW > 1e-6 the coefficient difference is below 1e-13 of the base
amplitude; on every mode it stays below the conditioning line 3 x 2u/(2 sqrt(dW)), u =
1.1e-16; in U1 (frozen, dW enters linearly) the A1 value is below 1e-11. Refuted by a large
difference on a mode with dW > 1e-6 (that would point to keys, times or the stage
bookkeeping) or by points above the line.

L-U3 (`analysis/lead/lu_validate.sh` on the outputs of E-20261115-135523-a32c3a6, each run
with its own input): frozen validation passes A0-A10 and A11 (1, 8, 64 MeshBlocks
bit-identical), A12 (restart at cycle 60 bit-identical), A13 (N = 16 against 32 within
eps_m), A15 (seeds); Markov Heaviside passes; Markov tanh fails A1 only, as before (the
contract is not loosened after seeing data). Refuted by any other failure.
