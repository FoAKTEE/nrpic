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
