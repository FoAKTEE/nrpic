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
