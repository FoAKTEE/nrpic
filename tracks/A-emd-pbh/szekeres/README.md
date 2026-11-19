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
| `sym/sym_szekeres.py` | symbolic checks (sympy): Einstein equations, fluid scalars against the paper, electric and magnetic Weyl, 3+1 constraints, Cotton tensor (conformal flatness), the identities behind the conformal map |
| `sym/gen_series.py` | the Taylor coefficients of l(lambda) (mpmath, 50 digits) |
| `tests/test_szekeres.py` | 14 unit tests (LTB limit against `expball`, direct integration, silent-universe equations of the paper, map pull-back, regularity) |
| `scripts/` | the registered runs: `run_ltb_limit.py`, `run_mesh_constraints.py`, `run_dipole_order.py`, `run_slice_evolution.py`; `common.py` (models, run directory, figure style `python/nrpic/figstyle.py`) |
| `figures/` | figures of the registered runs (PNG and PDF) |
| `DESIGN.md` | how the solution becomes a test of AthenaK: initial-data path, gauge, invariants, predicted errors |
| `JOURNAL.md` | predictions and outcomes |

## How to rerun (from this directory; numpy, scipy, sympy, mpmath, matplotlib)

    export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4
    python3 sym/sym_szekeres.py --fast          # 32 checks, about 3 min (exact rational points)
    python3 sym/sym_szekeres.py --only E        # the map identities, fully symbolic, seconds
    python3 -m pytest -q tests/                 # 14 tests, about 1 min
    python3 scripts/run_ltb_limit.py
    python3 scripts/run_dipole_order.py
    python3 scripts/run_slice_evolution.py
    python3 scripts/run_mesh_constraints.py --nmax 256 --workers 12

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

(filled in below after the runs; see JOURNAL.md entry 2 onwards)

## Requests

See the end of DESIGN.md (section 7) for what is needed from core and from the lead.
