# Interface proposal: extrinsic curvature of moving and rotating matter clumps

Status: PROPOSED by core (branch `core/clump-curvature`, 2026-11-15). For the
orchestrator (acceptance into `coord/INTERFACES/`), Track F (clump binaries), Track D
and the first paper (two overdensities in a cluster). Implements section 3 of
`coord/notes/design_wave2_initial_data.md`.
Evidence: `tracks/core/JOURNAL-clump.md` (derivation, predictions, outcomes), run
manifests under `tracks/core/runs/`, analysis and figures under
`tracks/core/analysis/clump/`. Units G = c = 1. Labels: [VERIFIED] measured in a
registered run or checked symbolically; [BACKGROUND]; [JUDGEMENT]; [TO VERIFY].

## 1. What exists

In the problem generator `nrpic_cf` (conformally flat data, `gamma_ij = psi^4 delta_ij`,
`psi = 1 + sum_c u_c`), a component of type `gaussian` may now carry a linear momentum
and a spin. The generator then adds to `K_ij` the Bowen-York curvature smeared with the
Gaussian, which solves the momentum constraint for a clump whose particles carry that
momentum density. It adds linearly to the Bowen-York curvature of punctures and to the
curvature of a table of format 2. Without the new parameters the generator behaves
bit-identically (test R).

Source: `athenak/src/pgen/nrpic/nrpic_clump_curvature.hpp` (moments, curvature, reader),
hooks in `nrpic_cf.cpp` and `nrpic_bowen_york.hpp` (section 9). Reference twin and
generator: `python/nrpic/smeared_bowen_york.py`, `python/nrpic/clumps.py`,
`problems/ic/make_ic.py`. No elliptic solver is involved.

## 2. Parameters

In `<problem>` with `pgen_name = nrpic_cf`, for a component `<c>` of type `gaussian`
(`comp<c>_mass`, `comp<c>_sigma`, `comp<c>_x1..3` as before):

| Parameter | Meaning | Default |
|---|---|---|
| `comp<c>_p1`, `_p2`, `_p3` | momentum P of the clump: `sum_p m_p u_(i,p)` of its particles (Cartesian, covariant) | 0 |
| `comp<c>_s1`, `_s2`, `_s3` | spin S of the clump about its centre | 0 |

A component whose six values are all zero gets no curvature (identical to leaving them
out). `comp<c>_corr` on a Gaussian is an error (corrections of psi exist for punctures
only). The command line can change only parameters that the input file has: list the
six with value 0 if a variant is to switch them on.

Examples: `problems/clump/clump_moving.athinput` (momentum, evolved 2 M),
`problems/clump/clump_spin.athinput` (spin, data only),
`problems/tests/clump_static.athinput` (test input), `problems/jeans/jeans_mc.athinput`
(the first paper's two overdensities with curvature; prepared, not run).

## 3. The data

With `K_ij = psi^-2 Abar_ij`, `K = 0`, the momentum constraint of the code,
`D_j K^ij - D^i K = 8 pi S^i`, is `d_j Abar_ij = 8 pi Stilde_i` with
`Stilde_i = psi^6 S_i = sum_p m_p u_(i,p) delta^3(x - x_p)`, the coordinate density of
the covariant particle momentum (flat indices; psi drops out). For a Gaussian
`g = (2 pi sigma^2)^(-3/2) exp(-r^2/(2 sigma^2))` about `x_c`, `t = r/(sqrt 2 sigma)`,
`n = (x - x_c)/r` [VERIFIED symbolically, `analysis/clump/derive_smeared_by.py`]:

    Stilde_i = P_i g:
      Abar_ij = 3 Q/(2 r^2) [P_i n_j + P_j n_i - (delta_ij - n_i n_j) P.n]
              + I4/(2 r^4)  [P_i n_j + P_j n_i + (delta_ij - 5 n_i n_j) P.n],
      Q  = erf(t) - (2/sqrt pi) t exp(-t^2),                    (enclosed fraction)
      I4 = 3 sigma^2 [erf(t) - (2/sqrt pi)(t + 2 t^3/3) exp(-t^2)]   (enclosed second moment)
    Stilde_i = (S x (x - x_c))_i g/(2 sigma^2):
      Abar_ij = 3 C/r^3 [(S x n)_i n_j + (S x n)_j n_i],   C = Q - (4 pi/3) r^3 g.

Below `t = 0.5` the code uses the power series of Q, I4, C (the closed forms cancel).
Far away the curvature is that of a Bowen-York puncture with the same P and S plus the
regular term `3 sigma^2/(2 r^4) [..]`; `P_ADM = P`, `J_ADM = S` (surface integrals,
2e-14). The first two lines hold for any spherical profile with its own Q and I4
(section 8, item 1).

### What the particles must carry

`comp<c>_p1..3` must equal the momentum `sum m u_i` of the clump's particles. Two rules
in the generator (`--clump-momentum-rule`, `python/nrpic/clumps.clump_particles`):

- `gaussian` (default of the model `clumps`): every particle carries the same share,
  `m_p u_(i,p) = [P_i + (S x d_p)_i/(2 sigma^2)]/N`, and the energy
  `m_p W_p = (m_c/N) psi` that the Hamiltonian constraint fixes, so
  `m_p = sqrt((m_c psi/N)^2 - |m_p u_p|^2/psi^4)`. The momentum density is the Gaussian
  and the momentum constraint holds in the continuum. The orthonormal speed is
  `|P + S x d/(2 sigma^2)|/(m_c psi^3)`: slower where psi is larger, as on the boosted
  slice of a static body (speed `V alpha/psi^2`). [JUDGEMENT for the comparison]
- `velocity` (the first paper's rule, default of `jeans`): one orthonormal velocity,
  `Stilde_i = m_c v_i psi^3 g`. The curvature of `P = sum m u` then leaves
  `8 pi m_c v (psi^3 - <psi^3>) g`: 3.4 percent of the uncorrected residual for a clump
  with `psi - 1 = 0.08` at its centre, 2.1 percent in the first paper's data.
  [VERIFIED: tests T4, T5]

### Satisfied

- Momentum constraint in the continuum, for any number of Gaussian clumps (rule
  `gaussian`) and Bowen-York punctures. On the mesh the residual is what the particle
  cloud and the source filter do to the Gaussian (it converges away with the cell
  size), plus particle noise. [VERIFIED: T1, T3]
- Hamiltonian constraint for the matter at any speed (the generator's
  `m_p W_p = (m_c/N) psi`), as before.

### Violated, and by how much

- Hamiltonian constraint: `H = -psi^-12 Abar_ij Abar_ij`, second order in P and S,
  exactly (algebraic). Peak 7.65e-4 for `m = 0.2`, `sigma = 1`, `P/m = 0.3`, against
  0.43 for the matter term `16 pi E`; it adds 4.5 percent to the residual that the
  deposit of the matter leaves on 128 cells. The mass that a correction of psi would
  add is `(1/16 pi) int psi^-7 Abar^2 = 1.034 psi^-7 P^2/sigma + 0.094 psi^-7
  S^2/sigma^3` per clump (6.0e-4 M for both clumps of the first paper's case). No
  correction is implemented. [VERIFIED: T2]
- Cross terms `Abar_c : Abar_j` of several bodies: part of the same second order.
- Particle noise: the curvature removes the smooth part only. In the first paper's
  data (10^4 particles on cells down to M/64) the smooth part is 7 percent of the
  squared momentum-constraint norm. [VERIFIED: T5]

## 4. Generator

`problems/ic/make_ic.py` (writes particles `.nrp` and a JSON with the `<problem>` block):

    make_ic.py clumps --gaussian m,sigma,x,y,z,px,py,pz[,sx,sy,sz] [--gaussian ...]
                      [--puncture m,x,y,z[,px,py,pz[,sx,sy,sz]]] --N <per clump>
                      [--sampler stratified|mc|lattice --lattice-h h]
                      [--clump-momentum-rule gaussian|velocity]
    make_ic.py jeans ... --clump-curvature [--clump-momentum-rule velocity|gaussian]

`clumps`: isolated Gaussian clumps with momentum and spin and optional Brill-Lindquist
or Bowen-York punctures (`python/nrpic/clumps.GaussianClumps`); species = index of the
clump; `psi = 1 + sum u_c` (Gaussians and `m/2r` of punctures; a correction of a
puncture's psi is not included in the particle masses). `--sampler lattice` puts
weighted particles on a lattice (noise-free deposit, for tests). The JSON gives
`comp<c>_p1..3` as the sums over the particles. `jeans --clump-curvature` adds the
clumps' momenta to the JSON; without the new options the model writes the same bytes
as before (the particle file and table of run `jeans/n1e4_v19` are reproduced,
sha256 7270917f..., 7ea9ca27...). [VERIFIED]

Python reference: `python/nrpic/smeared_bowen_york.py` (`moments`, `abar`, `abar2`,
`momentum_density`, `second_order_mass`).

## 5. Cost

Closed forms per cell (one `erf`, one `exp` per clump): nothing next to the evolution.

## 6. Tests

Predictions and outcomes in full, including the failed ones: `tracks/core/JOURNAL-clump.md`.
Scripts and figures: `tracks/core/analysis/clump/` (`derive_smeared_by.py`,
`check_smeared_by.py`, `predict.py`, `run_static.py` + `static_check.py`,
`run_jeans_t0.py` + `jeans_t0_check.py`, `regress.py`, `card_check.py`; `figs/*.png`).
Single clump: `m = 0.2`, `sigma = 1` (psi = 1.08 at the centre), box [-8, 8]^3,
`nghost = 4`, linear cloud, four filter passes with compensation, particles on a
weighted lattice unless said. Norms as in the history file. All on processors.

| Test | Result | Runs |
|---|---|---|
| Derivation | every identity holds symbolically (Poisson equations, vector equation, both closed forms, divergence, trace, `Abar^2`, series, limits) | `derive_smeared_by.py` (no run) |
| P0, Python reference | divergence against `8 pi Stilde_i` 2e-11 (momentum), 3e-11 (spin); `P_ADM = P`, `J_ADM = S` 2e-14; far field Bowen-York plus regular term 3e-16; sigma -> 0 Bowen-York | `check_smeared_by.py` (no run) |
| T1, momentum constraint against resolution, `P/m = 0.3` | uncorrected M-norm 0.1529, 0.1631, 0.1651 at 32, 64, 128 cells (closed form 0.1651); with curvature 0.01936, 3.07e-3, 9.4e-5: ratio 0.127, 0.0188, 5.7e-4 (predicted from the cloud and filter 0.130, 0.0202, 7.0e-4), orders 2.7 and 5.0; without filter 0.040, 0.011, 4.7e-7; curvature term alone 0.1871082 against the closed form 0.1871082; linear in P to five digits; wrong sign gives 2.012 times the uncorrected norm | `core-20261115-154632-e1a4d0c` |
| T1, equal-mass particles, 64 cells | with curvature 0.0139, 5.2e-3, 3.2e-3 for 10^4, 10^5, 10^6 particles (noise falls below the continuum part 3.1e-3 at 10^6); without 0.163 | same |
| T2, Hamiltonian residual | `H(with) - H(without) = -psi^-12 Abar^2` to 3e-7 of its peak; norm 6.096e-4, 2.438e-3, 5.486e-3 for P = 0.02, 0.04, 0.06 as predicted (1 : 4 : 9) | same |
| T3, spin `S = 0.04` | uncorrected 0.0569 (closed form 0.0570); ratio with curvature 0.229, 0.032, 1.1e-3 | `core-20261115-154749-e1a4d0c` |
| T4, rule `velocity` | ratio 0.099, 0.015, 0.034 at 32, 64, 128 cells; the fine-mesh value is the psi^3 variation (predicted 0.034) | `core-20261115-154842-e1a4d0c` |
| T6, evolved 2 M, 64 cells | M-norm 1.4e-3 rising to 9e-3 with curvature against 0.164 falling to 0.090 without (ratio at most 0.08); H-norm flat at 0.026 to 0.030 with curvature, rising from 0.028 to 0.171 without | `core-20261115-154935-e1a4d0c` |
| T5, first paper's two overdensities at t = 0 (mesh and particles of `jeans/n1e4_v19`) | record of the run reproduced in six digits; with curvature My-norm2 0.263081 to 0.241924 and M-norm2 0.191587 to 0.178041 (predicted smooth parts 0.0211, 0.0135); projection of M_y on the smooth field 1.001 to 0.021 (0.0013 with rule `gaussian`) | `core-20261115-155020-e1a4d0c` |
| Examples | `clump_moving.athinput` one cycle, `clump_spin.athinput` data, generator commands of their headers | `core-20261115-160625-1311116` |
| R, old inputs unchanged (processors) | RESULT_R | `core-20261115-174445-36616db`, `core-20261115-174439-7359389` |
| G, card | release card executable and this branch's give identical data files for `regress_cf` (16 files) and `by_static` (5); records at t = 0 of `clump_static` on the card (64 cells without and with curvature, 128 with, spin at 64) equal the processor records in all printed digits | `core-20261115-163141-ee2a188` (Slurm job 4443, 0.006 card-hours) |
| I, rerun input | `jeans_mc.athinput` equals what `n1e4_v19` used (input plus 35 overrides, 176 parameters) but for the six clump momenta and the comment text | `core-20261115-174714-25dc565` |

## 7. The first paper's two overdensities

`problems/jeans/jeans_mc.athinput` is the configuration of `jeans/n1e4_v19` with its
command-line overrides written in and `comp1_p1..3`, `comp2_p1..3` set to the momenta
of the run's own particles (same particle file and table). It is prepared and not run;
the data at t = 0 are test T5. Prediction, written before any run
(`JOURNAL-clump.md`): the remnant-mass excess of 2.5 percent stays
(`M_AH(100 M) = 1.025 +- 0.010`; refuted below 1.010), because the masses the
violation can misplace are second order (2.1e-3 M kinetic, 6.0e-4 M curvature); the
remnant's angular momentum rises (S(100 M) above 0.105, against 0.089); the common
horizon comes later than 57 M. [JUDGEMENT]

Prepared: `tracks/core/analysis/clump/rerun_jeans_mc.sh` submits it through
`harness/bin/nrpic-run` as one registered chain on one card (`--gpu-hours 8`, segments
of 50 min, at most 8; `n1e4_v19` needed 5.4 card-hours with an older executable), with
the particle file and table of `n1e4_v19` staged read-only in
`scratch/core/clump-rerun/inputs/` and the card executable published from this branch.
`--control` submits the same input, particles and executable with the clump momenta
zero: the executable is not the one of `n1e4_v19` and card runs with deposition are not
reproducible, so the effect of the curvature is the difference rerun minus control
(predicted below 0.010 in `M_AH(100 M)`, above 0.015 in S; journal, "Prediction for the
control of the rerun"). Figure of the predictions on the record of `n1e4_v19`:
`analysis/clump/figs/fig_clump_rerun_prediction.png` (run `core-20261115-175038-c703977`).
`--dry-run` prints the manifest without starting anything.

## 8. Limits and open items

1. Gaussian components only. The curvature of a moving `table` component (an
   equilibrium cluster, what Track F asks for) is the same two lines with Q and I4 of
   the table's conformal source (`Q = -2 r^2 u'/M`, `I4 = -(2/M)[r^4 u' - 2 r^3 u + 6
   int_0^r r'^2 u dr']`), and the particles get `Delta u_i = (P_i/M_c) W(r)/psi` on top
   of their isotropic momenta; not implemented, not tested. [JUDGEMENT]
2. No correction of psi for the second-order Hamiltonian residual (section 3). The
   multipole table of the puncture correction could carry one.
3. psi used for the particle masses in `GaussianClumps` leaves out the corrections of
   punctures (`comp<c>_corr`); a clump next to a corrected puncture has a mismatch of
   that size in its Hamiltonian constraint. [TO VERIFY]
4. A layer of cells at an outflow boundary carries a momentum-constraint residual of
   its own whenever `K_ij` does not vanish there (1.1e-5 at 8 sigma for `P = 0.06`;
   M-norm 4e-5 at 128 cells); seen in T1, cause not tested; with a Bowen-York puncture
   it would be the same. [TO VERIFY]
5. Evolved only once and briefly (T6, 2 M, one clump, processors). Whether a moving
   clump keeps its profile for 200 M (Track F's acceptance test) is not tested: a cold
   Gaussian clump collapses; that test needs an equilibrium clump (item 1).
6. The sum of the covariant particle momenta drifts by 1.6 percent in 2 M with the
   curvature and 1.3 percent without (T6): my prediction that the curvature reduces
   the drift failed; not understood.
7. Spin: data tested (T3), no evolution.
8. Not run: refined meshes with the single clump (T5 covers a refined mesh at t = 0),
   more than one rank.

## 9. Lines touched in shared files

- `athenak/src/pgen/nrpic/nrpic_cf.cpp`: additions only, 19 lines (line numbers of the
  branch): 39-41, three comment lines at the end of the file header; 64,
  `#include "pgen/nrpic/nrpic_clump_curvature.hpp"` after the include of
  `nrpic_bowen_york.hpp`; 499-500, the reader call after
  `const DvceArray1D<Real> bytab = ...`; 595-607, thirteen lines after the
  `if (by.curv) { ... }` block of the main loop (curvature, added with `+=`).
- `athenak/src/pgen/nrpic/nrpic_bowen_york.hpp`, `BYRead`: lines 336-337 added after
  `if (!any) continue;` (a Gaussian component is skipped) and line 340, the text of the
  error message that follows.
- New file `athenak/src/pgen/nrpic/nrpic_clump_curvature.hpp`; nothing added to
  `CMakeLists.txt`.
- `python/nrpic/clumps.py`: docstring paragraph, `__all__`, new function
  `clump_particles`, option `momentum` of `JeansModel.sample` (the loop over the two
  clumps), new class `GaussianClumps` at the end. `problems/ic/make_ic.py`: model
  `clumps`, options `--clump-curvature`, `--clump-momentum-rule`, `--gaussian`,
  `--puncture`, `--lattice-h`, `--lattice-rcut`. New: `python/nrpic/smeared_bowen_york.py`,
  `problems/clump/*.athinput`, `problems/tests/clump_static.athinput`,
  `problems/jeans/jeans_mc.athinput`.
