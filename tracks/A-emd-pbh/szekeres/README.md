# szekeres: exact dust solutions without symmetry (verification row of the brief, line 851)

Work package of a helper of A-emd-pbh, wave 3a (2026-11-19). Reference solution, its checks
and the design of the code test; nothing here is a simulation code (decision 0010). The
row of the brief's verification suite: "Szekeres-type dust solutions | Nonlinear evolution
without symmetry | Exact solution; arXiv:1708.09143 | A, B". The reference is fetched to
`kb-data/raw/arxiv/1708.09143/v4/src/simsilun_rev.tex` (Bolejko 2017, section 2.4, lines
283-357: the quasi-spherical Szekeres metric and its fluid scalars).

Results and outcomes: `JOURNAL.md` (predictions first, outcomes after, failed predictions
included). The test design for AthenaK: `DESIGN.md`.

## What is here

| path | content |
|---|---|
| `szekeres/universal.py` | the universal function of dust collapse with simultaneous bang time, R = M^(1/3) t^(2/3) g(lambda), lambda = k t^(2/3)/M^(2/3): l = ln g and two derivatives (Taylor series of 40 terms for abs(lambda) < 0.5, cycloid forms beyond); its inverse |
| `szekeres/model.py` | the quasi-spherical Szekeres model: LTB functions M(r), k(r) from a profile of the mean contrast (simultaneous bang time, pure growing mode), the dipole b(r) = -(P', Q', S')/S, evolution R(t, r) with R', Rdot, Rdot' in closed form, density, Theta, Sigma, Weyl scalar W, K^r_r, K^p_p, gamma_rr, crunch, turnaround and R = 2M times, regularity margins |
| `szekeres/confmap.py` | conformally flat Cartesian coordinates of a slice t = const (ODE in ln r on the hyperboloid of the Szekeres dipole functions, non-concentric-sphere embedding); psi, K^i_j, rho at any Cartesian point; inverse map |
| `szekeres/mesh.py` | finite-difference Hamiltonian and momentum residuals of the slice on a cell-centred Cartesian mesh (stencils of order 2, 4, 6, as `expball/expball/mesh.py`) |
| `szekeres/codeid.py` | initial data for AthenaK: the NRCOSMO1 field file of `nrpic_cosmo id = file` and the particle file (one particle per cell centre, at rest) |
| `inputs/szekeres_geodesic.athinput` | the AthenaK deck: periodic [-8, 8]^3, geodesic slicing, CIC, field dumps with constraints |
| `sym/sym_szekeres.py` | symbolic checks (sympy): Einstein equations, fluid scalars against the paper, electric and magnetic Weyl, 3+1 constraints, Cotton tensor (conformal flatness), the identities behind the conformal map |
| `sym/gen_series.py` | the Taylor coefficients of l(lambda) (mpmath, 50 digits) |
| `tests/test_szekeres.py` | 15 unit tests (LTB limit against `expball`, direct integration, silent-universe equations of the paper, map pull-back, regularity, round trip of the files for the code) |
| `scripts/` | the registered runs: `run_ltb_limit.py`, `run_mesh_constraints.py`, `run_dipole_order.py`, `run_slice_evolution.py`, `run_error_budget.py`, `run_code_geodesic.py` (AthenaK); `common.py` (models, run directory, figure style `python/nrpic/figstyle.py`) |
| `figures/` | figures of the registered runs (PNG and PDF) |
| `DESIGN.md` | how the solution becomes a test of AthenaK: initial-data path, gauge, invariants, predicted errors |
| `JOURNAL.md` | predictions and outcomes |

## How to rerun (from this directory; numpy, scipy, sympy, mpmath, matplotlib)

    export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4
    python3 sym/sym_szekeres.py --fast          # 32 checks, about 3 min (exact rational points)
    python3 sym/sym_szekeres.py --only E        # the map identities, fully symbolic, seconds
    python3 -m pytest -q tests/                 # 15 tests, about 1.5 min
    python3 scripts/run_ltb_limit.py
    python3 scripts/run_dipole_order.py
    python3 scripts/run_slice_evolution.py
    python3 scripts/run_mesh_constraints.py --nmax 256 --workers 12
    python3 scripts/run_error_budget.py
    python3 scripts/run_code_geodesic.py --N 32 64 --tlim 2 --field-times 0.5 1 2   # AthenaK, processors

Registered through `harness/bin/nrpic-run submit --package tracks/A-emd-pbh/szekeres`
(manifests under `tracks/A-emd-pbh/runs/<run_id>/`, outputs under
`scratch/A-emd-pbh/<run_id>/`). Run ids and numbers: section "Results" below.

## The reference model

Expanding-ball data set 2 of `expball` (H = 1/16, t_i = 2/(3H), smoothed top-hat: mean
contrast 1 inside R1 = 2.4, Einstein-de Sitter from R2 = 6 on, simultaneous bang time)
with a dipole b(r) = (eps/r) h(u) e(u), u = (r - 2.4)/3.6, h a C-infinity bump of height 1,
e(u) turning from z towards x while turning about z (P', Q', S' all non-zero; no
symmetry), eps = 0.1. The dipole acts only where M/r^3 or k/r^2 vary: in the homogeneous
core and in the Einstein-de Sitter exterior a Szekeres dipole is a coordinate effect (the
density M'/M - 3 b.n over R'/R - b.n is then homogeneous), so the model is a Szekeres hole
of label radius 6 cut into Einstein-de Sitter, an exact solution that tiles a periodic box.

## Results

Every number with its run; predictions and outcomes in JOURNAL.md (entries 1 to 6).

| what | outcome | run / check |
|---|---|---|
| Einstein equations, Theta, sigma = Sigma e, E = W e (paper's signs), H_ab = 0, 3+1 constraints, K = -Theta | 32 symbolic checks pass at exact rational points (negative controls fail as they must) | `sym/sym_szekeres.py --fast`, run A-20261119-152233-d31f783 |
| conformal flatness of the comoving slice | Cotton tensor = 0 for arbitrary R, k, S, P, Q (the task text expected the opposite); k = 0: flat; explicit conformal map verified symbolically and by pull-back (1e-8) | same run; `tests/` |
| LTB limit against `expball` (data set 2) | initial slice to 4e-15; R(tau) of 400 shells to 2.2e-14 up to 0.9 of the core crunch (2.2e-12 at 0.1 per cent before it); turnaround, crunch, R = 2M times to 7e-15; isotropic radius 5e-12, psi 1.5e-12 | A-20261119-151501-9cff966, `figures/fig_ltb_limit.png` |
| silent-universe equations of the paper along elements | reproduce the exact evolution to 2e-11 (Theta), 3e-12 (rho) up to tau = 40 | A-20261119-152232-3d29cc1 (repeat A-20261119-153842-a1db5d6), unit test |
| finite-difference constraints of the Szekeres slice on Cartesian meshes, h = 0.47 ... 0.059 | Hamiltonian L2 (all cells, /16 pi rho_b): order 2: 1.5e-2, 4.1e-3, 1.0e-3, 2.6e-4 (orders 1.89, 1.96, 1.99); order 4: 6.1e-3, 7.2e-4, 6.0e-5, 4.2e-6 (3.09, 3.57, 3.84). Momentum order 4: 4.9e-2, 9.7e-3, 1.1e-3, 9.2e-5 (2.33, 3.10, 3.61). LTB limit within 2 per cent of these: the map adds no error | A-20261119-152252-2ae031e (figure repeat A-20261119-153846-81db254), `fig_mesh_constraints.png`, `fig_residual_maps.png` |
| what a spherical (format-2) table misses | first order in eps (slopes 1.000 +- 0.007): max dpsi = 0.0044 eps, drho = 1.84 eps rho_b, dK = 1.43 eps H, shells' centres move 1.93 eps | A-20261119-151501-3e344a4, `fig_dipole_order.png` |
| regularity of the reference model (eps = 0.1) | (R'/R)/abs(b) >= 10, (M'/3M)/abs(b) >= 3.9 up to the core crunch (tau = 44.45); densities 0.39 ... 2.0 of the background at t_i, up to 19.5 at tau = 30 | A-20261119-151501-986153a (layout repeat A-20261119-153841-e1484db), `fig_slice_maps.png`, `fig_evolution.png` |
| response of an element to initial errors (error budget) | a relative error 1e-6 in the initial density gives dK of 1e-6 H_i (tau = 10), 7.5e-6 (tau = 30), 8e-5 (tau = 40) in the core, below 5e-7 H_i outside the collapsing region; density scale 0.55 at t_i, 0.17 at tau = 40 (code coordinates) | A-20261119-152232-3d29cc1, `fig_error_budget.png` |
| first AthenaK run (processors, core-v0.3, geodesic slicing, N = 32; N = 64 only at tau = 0) | at tau = 0 the code holds the data exactly (K to 5e-16, E to 6e-8, chi to 3e-8: float32 dumps); constraint monitor 9.8e-3 (N = 32) and 8.6e-4 (N = 64) of 16 pi rho_b over the shell; alpha stays 1 to 2e-13; at N = 32 the evolution departs (K off by 15 per cent at tau = 10) and fails between tau = 24 and 28 | A-20261119-152010-94a9461, `fig_code_geodesic_run1_tau40.png` |
| short convergence run N = 32, 64 to tau = 2, with and without dissipation | every error falls by about 3 per halving (K in the shell 3.9e-2 -> 1.3e-2 at tau = 2; rms H 0.30 -> 0.095 of 16 pi rho); dissipation reduces the error; the early constraint growth is a truncation effect of the under-resolved shell | A-20261119-153832-7097718, `fig_code_geodesic.png`, `fig_code_geodesic_profiles.png` |

## Not done, limits

- The convergence test of AthenaK in its asymptotic range (128^3, 256^3 to tau = 40) was not
  run: the processor build is too slow (64^3 to tau = 2 took 21 minutes) and this package
  had no card-hours. Only geodesic slicing was run; the production gauge of Track A
  (secondary test, DESIGN section 4) and the convergence in the particle number were not.
- `id_solve` / `id_vector` of core/id-solver(-2) were not run on this data (DESIGN
  section 3 has the prediction).
- The fully symbolic (not random-point) form of the Einstein-equation and constraint
  checks did not finish within 50 minutes and was abandoned; the checks are exact rational
  evaluations at three random points per component, plus exact evaluation of the Cotton
  tensor for explicit functions.
- The apparent horizon of a Szekeres collapse need not be the sphere R = 2M [TO VERIFY in
  the literature through kb]; `horizon_time` gives the LTB value only.
- Whether conformal flatness of the comoving Szekeres slice is stated in the literature
  was not looked up.
- `model.py` exposes gamma_rr, R and the dipole scalar; the full metric in (r, p, q) needs
  S, P, Q, which `confmap.py` tabulates (normalised at r_out); there is no separate
  function for it (the pull-back test builds it).

## Requests

- **lead of A-emd-pbh**: the card convergence series of DESIGN section 7 (64^3, 128^3,
  256^3 with one MeshBlock per card or the card's usual blocks, to tau = 40, dumps at 10,
  20, 30, 40; `scripts/run_code_geodesic.py` takes `--N`, `--tlim`, `--field-times` and
  needs only the executable path changed to the card build); estimated under one
  card-hour in total [JUDGEMENT]. Choose eps (0.1 here).
- **core**: (1) the full K_ij and gamma_ij in the field dumps (eigenvalue test: KT is
  uniform on a shell, KL is not); (2) whether the trajectory output carries proper time
  (secondary test in other gauges); (3) a first test of `id_solve` with `nrpic_cosmo
  id = file` can use this hole (files from `szekeres/codeid.py`); (4) note: on the
  processor build the cost of the particle module grows with MeshBlocks times particles
  (64^3 in 16^3 blocks: over 100 s a cycle; one block: about 40 s) [measured in runs
  A-20261119-152010-94a9461 and A-20261119-153832-7097718 on a loaded machine].
- **Track B** (co-owner of the row): the model, map and files serve a periodic set-up as
  they are.
