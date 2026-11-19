# Interface proposal: equilibrium clusters that move (table components with a bulk momentum)

Status: PROPOSED by core (branch `core/clump-table`, 2026-11-19; work package clump2, the
second pass of `moving_clumps.md`). For the orchestrator (acceptance into
`coord/INTERFACES/`) and Track F (object (b): two equilibrium clumps with bulk momenta,
request `track/F-hills:tracks/F-hills/outbox/20261115T1507Z__to-core__moving-clump-initial-data.md`).
Evidence: `tracks/core/JOURNAL-clump2.md` (derivation, predictions written before each
run, outcomes including the failed ones), run manifests under `tracks/core/runs/`,
scripts and figures under `tracks/core/analysis/clump2/`. Units G = c = 1. Labels:
[VERIFIED] measured in a registered run or checked to round-off; [BACKGROUND];
[JUDGEMENT]; [TO VERIFY].

## 1. What exists

A component of type `table` (format 1, a radial table of `psi - 1` and the lapse: the
relativistic cluster models of `make_ic.py st`) of the problem generator `nrpic_cf` may
now move. Three additions, each switched on separately:

1. **Curvature** that solves the momentum constraint for the cluster's actual momentum
   density: the static cluster on the *maximal* slice of its boosted spacetime, to first
   order in the speed. The code reads the radial moments of the momentum density from a
   "boost table" (format `bst1`, `docs/FORMATS.md`) and builds `K_ij = psi^-2 Abar_ij`,
   `K = 0`. It adds linearly to the curvature of punctures, Gaussian clumps and other
   moving tables.
2. **Correction of psi** at second order in the speed (kinetic energy of the bulk motion
   and `Abar_ij Abar_ij`), from a spherical radial solve per cluster: a multipole table
   (monopole and quadrupole about the direction of motion) in the format of the puncture
   corrections (`mp1`), added to psi.
3. **Comoving shift** (optional): the shift of coordinates that move with the cluster.

The particles are boosted consistently by the generator (`problems/ic/make_ic.py
boosted`, `python/nrpic/boosted_cluster.py`), which writes the radial table, the boost
table, the correction table, the particles and the `<problem>` block. Several clusters
(and punctures) are superposed with a first-order scaling of each cluster into the
others' conformal factor. Without the new parameters the generator is bit-identical to
release core-v0.3 (test R).

Source: `athenak/src/pgen/nrpic/nrpic_clump_table.hpp` (reader, curvature, shift); hooks
in `nrpic_cf.cpp` and `nrpic_bowen_york.hpp` (section 9). No elliptic solver is involved
(section 8 says what the mesh solver of `core/id-solver` would add).

## 2. Parameters

In `<problem>` with `pgen_name = nrpic_cf`, for a component `<c>` of type `table`
(format 1; `comp<c>_file`, `comp<c>_x1..3` as before):

| Parameter | Meaning | Default |
|---|---|---|
| `comp<c>_boost_file` | boost table of the cluster (format `bst1`); without it none of the parameters below is read | absent |
| `comp<c>_p1`, `_p2`, `_p3` | momentum P of the cluster: `sum m u_i` of its particles (covariant, Cartesian). The coordinate velocity far away is `V = P/pmass` (`pmass` from the table header) | 0 |
| `comp<c>_corr` | `none` or `table`: second-order correction of psi | `none` |
| `comp<c>_corr_file` | `table`: the correction table (format `mp1`) | none |
| `comp<c>_corr_axis1..3` | `table`: symmetry axis of the correction; default the axis in the file header, else the direction of P | from file |
| `comp<c>_boost_shift` | `true`: add the comoving shift `beta^i = -(V^i ba + n^i (V.n) bb)` | `false` |

A component with a boost file and zero momentum gets nothing (identical to the cluster at
rest). A table of format 2 cannot carry a boost table (fatal error). The command line can
change only parameters the input file has: list them with value 0 / `none` / `false` if
a variant is to switch them on. Use `lapse = table` (one cluster: its static lapse) or
`lapse = isotropic` (several clusters: `(2 - psi)/psi`, within 0.002 of the static lapse
times `1 - M_other/d` at the centres of the binary of test TE).

Examples: `problems/clump/cluster_moving.athinput` (one cluster, 50 M, card),
`problems/clump/cluster_binary.athinput` (two clusters on a quasi-circular orbit, card),
`problems/tests/clump_table_static.athinput` and `problems/tests/clump_table_binary.athinput`
(data at t = 0, processors). Each header gives the generator command.

## 3. The data

Derivation in full: `JOURNAL-clump2.md`, session clump2-1, "Derivation". In short: the
static isotropic cluster `ds^2 = -alpha_0^2 dt^2 + psi_0^4 dx^2` (energy density rho,
pressure P) seen on the slice `t~ = t + T(x)`, `T -> V.x` far away, is conformally flat
with psi_0 to O(V^2), and maximal if `d_i (A d_i T) = 0`, `A = (alpha_0 psi_0)^2`. With
`T = (V.n) F(r)`: `(r^2 A F')' = 2 A F`; outside the matter `F = r + m + m^2/r +
kappa/(r (r - m))`, m = M/2. The plain boost `F = r` is not maximal. Then, with
`w_i = d_i T = V_i F/r + n_i (V.n)(F' - F/r)`:

    Stilde_i = psi^6 S_i = psi_0^6 (rho + P) alpha_0 w_i,
    Abar_ij = 3 Q/(2 r^2) [V_i n_j + V_j n_i - (delta_ij - n_i n_j) V.n]
            + I4/(2 r^4)  [V_i n_j + V_j n_i + (delta_ij - 5 n_i n_j) V.n],
    Q(r) = 4 pi int_0^r (s_a + s_b/3) r'^2,   I4(r) = 4 pi int_0^r (s_a - s_b) r'^4

for any l = 1 momentum density `V_i s_a + n_i (V.n) s_b` (the Gaussian closed form of
`moving_clumps.md` is the special case). The table stores Q and I4 per unit momentum, so
the code applies `P = pmass V`. `Q(inf) = M`, the ADM mass: the momentum of the data is
`M V` to round-off, as for the boosted spacetime; the plain boost would give 0.947 M V
for the y_c = 0.819 cluster. [VERIFIED: PA2, run `core-20261119-144026-3d7d4e7`]

**Particles** (generator rule): a static sample (x, `u_i = psi_0^2 q_i`, m_0) becomes
`u~_i = u_i + E w_i(x)`, `E = alpha_0 W`, and `m~ = m_0 (1 + w.xdot)` (the weight with
which a world line crosses the new slice). Its momentum density is the `Stilde_i` above
exactly for any isotropic distribution; without the weights the pressure part is
missing (2.8 per cent of the momentum of the y_c = 0.819 cluster). The parameter of the
generator is the speed v of the clump: the linear rule is applied with `V = W_v v`.
[VERIFIED: PA5, 10^5 particles, sum m u/(M V) = 1.00004 +- 0.0022]

**Second order.** `psi = psi_0 + V^2 [y_0(r) + y_2(r) P_2(cos theta)]` from two radial
equations, `lap dpsi - 2 pi psi_0^4 (rho + 6P) dpsi = -pi psi_0^5 (rho + P) wbar^2 -
psi_0^-7 Abar^2/8`, written as the `mp1` table. The added mass is `0.984 M V^2/2` for
y_c = 0.819. The particles do not change with the correction. [VERIFIED: PA6]

**Comoving shift.** With zero shift the matter starts with the coordinate velocity
`alpha_0^2 psi_0^-4 w`, 0.474 V at the centre of the y_c = 0.819 cluster. The option
`comp<c>_boost_shift` sets `beta^i = -(V^i - alpha_0^2 psi_0^-4 w^i)`, which falls off as
`3 m V/r`.

**Several bodies.** Near cluster c the others add an almost constant `lam_c - 1` to psi.
The generator writes each cluster in the coordinates scaled by `lam_c^2` (positions
shrink by `lam^2`, `u(r) = lam u^(lam^2 r)`, covariant momenta and P by `lam^2`, Q and
I4 rescaled) and multiplies each particle mass so that `m W/psi` equals the isolated
value in the psi of all bodies. `--cluster-p` gives a cluster by its momentum (what a
three-body set-up specifies).

### Satisfied

- Momentum constraint in the continuum, for any number of clusters, Gaussian clumps and
  punctures (it is linear). On the mesh the residual is what the cloud and the source
  filter do to the profile, plus particle noise. [VERIFIED: TB2, TD2; section 6]
- Hamiltonian constraint to second order in V for an isolated cluster with the
  correction. [VERIFIED: TB3]

### Violated, and by how much

- Hamiltonian constraint: without the correction a residual of second order (continuum
  interior norm 3.1e-3 at v = 0.1, 0.031 at v = 0.3, against 0.91 for the matter term
  `16 pi E`); with it, terms of order V^4 (1.6 per cent of the second-order term at
  v = 0.3). [VERIFIED: PA6, TB3]
- Cross terms of several bodies: `Abar_c : Abar_j` in the Hamiltonian constraint, the
  tidal variation of the others' psi across a cluster (the scaling uses its value at the
  centre), and the second-order corrections superposed linearly.
- Not conformally flat at O(V^2) (the Lorentz contraction of the profile and the
  non-conformally-flat part of the boosted metric are left out; they violate no
  constraint at that order, they are gauge and a small change of the object).
- Particle noise: the curvature removes the smooth part only. [VERIFIED: TB6]

## 4. Generator

    make_ic.py boosted --cluster yc,mass,x,y,z,vx,vy,vz [--cluster ...]
                       [--cluster-p yc,mass,x,y,z,px,py,pz ...]
                       [--puncture m,x,y,z[,px,py,pz[,sx,sy,sz]] ...]
                       --N <per cluster> [--seed s] [--sampler stratified|mc|quiet
                       --lattice-h h] [--no-psi-correction] [--boost-shift]
                       --prefix <stem> --out <dir>

`mass` is the ADM mass of the isolated cluster, `yc` the model of `st_cluster.STModel`.
Written per cluster k: `<stem>_c<k>.tab` (radial table, format 1), `<stem>_c<k>.bst`
(boost table), `<stem>_c<k>_corr.tab` (correction); `<stem>.nrp` (species = k) and
`<stem>.json` with `athenak.problem` (the `<problem>` block; `comp<c>_p1..3` are the sums
over the particles, which differ from the continuum P by the sampling) and the
first-order and corrected ADM masses. `--sampler quiet`: weighted lattice with six
momenta per site (noise-free deposit, for tests). The net momentum of the sample is kept
(each cluster carries P).

Python reference: `python/nrpic/boosted_cluster.py` (`BoostedST`: slice function,
moments, momentum density, curvature, shift, particle rule, correction, table writers;
`BoostedClusters`: several clusters and punctures, psi, curvature, sampling, problem
block).

## 5. Cost

Per cell and cluster two cubic interpolations (four with the shift) and the correction
(one multipole evaluation): nothing next to the evolution.

## 6. Tests

Predictions and outcomes in full, including the failed ones: `tracks/core/JOURNAL-clump2.md`.
Scripts: `tracks/core/analysis/clump2/` (`check_boost.py`, `predict_boost.py`,
`run_boost_static.py` + `boost_static_check.py` + `tb_residual_diag.py`,
`run_binary_static.py` + `binary_static_check.py`, `run_t0_records.py`,
`boost_evolution_check.py`, `binary_evolution_check.py`, `run_cpu_tests.sh`); figures are
in the run directories (`scratch/core/<run_id>/`) and copied to `figs/`. Cluster y_c =
0.819 (the stable cluster of the first paper: R = 9.964 M, rbar_s = 8.936 M, alpha_c =
0.809), ADM mass 1. Processor tests on a uniform box [-16, 16]^3 (one cluster) with
`nghost = 4`, linear cloud, four filter passes with compensation, the quiet lattice
(spacing 0.25, six momenta per site) unless said; norms as in the history file,
restricted to r < 14 ("interior").

| Test | Result | Runs |
|---|---|---|
| PA, Python reference | slice function matches the vacuum closed form to 3e-13; `Q(inf)/M - 1 = -9e-15` (plain boost 0.947); curvature equals `psi^6 (Lbar beta)/(2 alpha)` of the boosted static solution to 4e-11; divergence equals `8 pi Stilde` to 6e-11; 10^5 boosted particles carry `1.00004 +- 0.0022` of `M V` (2.8 per cent less without the weights); radial equations of the correction solved to 4e-7; added mass `0.984 M V^2/2` | `core-20261119-144026-3d7d4e7` |
| TB1, momentum constraint without curvature | interior M-norm 0.981, 0.995, 0.9995 of the continuum value at 32, 64, 128 cells; ratio v = 0.3/0.1 3.129 (continuum 3.129) | cases `core-20261119-151457-7a855d8`, analysis `core-20261119-155912-1fda7e0` |
| TB2, with the boost table | M-norm 0.070, 0.034, 0.015 of the uncorrected one (first order: the edge of the cluster); the same to four digits at v = 0.1 and 0.3; curvature term equal to the continuum to 4e-6 at 128 cells | same |
| TB3, Hamiltonian at second order | residual added by the motion equal to the continuum second-order value (0.973-0.998); ratio v = 0.3/0.1 9.69 (predicted 9.79); with the correction 0.078-0.097 of it is left (predicted below 0.08 and 0.05 at 64 and 128 cells: **missed**), second order in v and not falling with the cell size; 76-95 per cent of it within 1 M of the surface, a factor 40 removed elsewhere; projection on the uncorrected residual -0.02 to 0.002 | same, diagnostic `core-20261119-160318-b9d749c` |
| TB4, whole-box history norms | H-norm with correction 4.3 per cent above the cluster at rest (predicted within 2: **missed**; the faces of the box dominate the whole-box norm already at rest); M-norms of `curv` and `corr` 1.04 per cent apart (predicted 1) | same |
| TB5, fields | psi^4, K_ij, beta^i, lapse of the code equal the Python reference at every cell to 6e-8 (single-precision dumps); trace K 3e-18 | same |
| TB6, 10^4 equal-mass particles | M-norm2 0.01395 -> 0.00133, the drop equal to the smooth part 0.01275 within 1 per cent; projection of M_x on the smooth field 0.995 -> -0.004; H-norm unchanged within 2 per cent (noise) | same |
| TD, two clusters at t = 0 | x = -20, +20, Newtonian circular momenta 0.1182, cell 0.5: H-norm near a cluster 1.027 times that of the isolated cluster; M-norm ratio 0.0348 (one cluster 0.0341); correction leaves 0.073 of the second-order residual (one cluster 0.078) | same |
| R, old inputs unchanged (processors) | release core-v0.3 and this branch: byte-identical data files for `regress_cf` (16 files), `cf_table_regress` (9), `by_static` (5) | `core-20261119-153230-3e858c9` |
| R, the first paper's two overdensities (two cycles) | PENDING (end of `core-20261119-151457-7a855d8`) | |
| G, card against processor at t = 0 | PENDING (card jobs 4649, 4657; processor part `core-20261119-160021-b153852`) | |
| TC, one cluster moving for 50 M on a card | PENDING (Slurm 4649, `core-20261119-145433-8c4083d`) | |
| TE, binary on a quasi-circular orbit, 250 M on a card | PENDING (Slurm 4657, `core-20261119-155219-32602d2`) | |

## 7. Track F's request

Object (b) of Track F: two equilibrium clumps of mass 0.05 M_BH each, compactness 0.05
to 0.1, with bulk momenta, beside a heavy puncture with momentum. What this provides:
`make_ic.py boosted --cluster-p yc,mass,x,y,z,px,py,pz` (twice) `--puncture
m,x,y,z,px,py,pz`, with the cluster model chosen by y_c (compactness `M/R` 0.100 for
y_c = 0.819; a smaller y_c gives a less compact cluster: `st_cluster.STModel(yc)`), the
mass scaled by `mass`. The momentum constraint is solved for clusters and puncture
together (linear); the Hamiltonian constraint for each cluster to second order in its
speed; the cross terms (cluster-cluster and cluster-puncture curvatures, the puncture's
tidal field across a clump) are not solved. F's acceptance tests: the momentum
constraint against the closed form for P/m up to 0.3 is TB (one clump; the residual is
the deposit, first order in the cell size); "an isolated moving clump keeps its profile
for 200 M" is TC for 50 M at v = 0.1 and 0.3 (PENDING). In F's units (clump mass 0.05
M_BH) 200 M_BH are 4000 clump masses: not run.

## 8. Limits and open items

1. **Correction leftover at the surface** (TB3): 8 to 10 per cent of the second-order
   Hamiltonian residual remains within about 1 M of the cluster's surface and does not
   fall with the cell size; a lattice test is running (journal). Elsewhere the
   correction removes a factor 40. [VERIFIED for the numbers; cause TO VERIFY]
2. **Cross terms of several bodies** are not solved (section 3). This is where the
   elliptic solver of `core/id-solver` belongs: it takes `Abar_ij` from `adm.vK_dd` (so
   it already sees the boost-table curvature) and the energy density of the deposited
   particles, and solves the Hamiltonian constraint for psi with the particles' u_i and
   rest masses held. What clusters need from it: (a) static refined meshes (the clusters
   need cells of M/2 inside a domain of +-1024 M; work package idsolve2, goal 3);
   (b) punctures in the solve (Track F's heavy hole; idsolve2 goal 4); (c) the energy
   density recomputed with the solved psi for moving particles (`W = (1 +
   psi^-4 u_i u_i)^(1/2)`), which the derivation here relies on (its `-6 P dpsi` term);
   (d) the vector equation (`id_vector`) on refined meshes, to remove the deposit's
   share of the momentum-constraint residual. With these the correction tables become a
   good first guess and the cross terms and the sampling noise are removed. For an
   isolated cluster the radial solve is exact to the stated order and costs nothing.
   [JUDGEMENT]
3. **Lorentz contraction** and the non-conformally-flat part of the boosted metric at
   O(v^2) are left out: the object is a slightly different (still constrained) cluster,
   not the exact boosted one. At v = 0.3 the contraction is 4.6 per cent along the motion.
4. **Particles are not changed by the correction** of psi (their rule uses psi_0 and
   alpha_0); the derivation includes the resulting `-6 P dpsi` term.
5. **Gauge.** With zero shift the cluster starts slower in coordinates (0.47 v at the
   centre); `comp<c>_boost_shift` starts with the comoving shift. Which is better for a
   long run is test TC (PENDING).
6. **Summed particle momentum.** `sum m u_i` depends on the slice at first order in v and
   in the potential (0.947 M V on the plain boosted slice, M V on the maximal one); its
   drift in an evolution with 1+log slicing is predicted (TC4 and its supplement) and
   PENDING.
7. One rank only (the particle module); refined meshes only in the card inputs.
8. A table component of format 2 cannot carry a boost table.

## 9. Lines touched in shared files

- `athenak/src/pgen/nrpic/nrpic_cf.cpp` (additions only, 34 lines; line numbers of this
  branch): 42-44, three comment lines at the end of the file header; 68,
  `#include "pgen/nrpic/nrpic_clump_table.hpp"` after the include of
  `nrpic_clump_curvature.hpp`; 505-515, the reader call after the one of the Gaussian
  clumps (`ClumpRead`) and the check against a table of format 2; 591-593, the correction
  loop after the loop of the puncture corrections in the sum of psi; 626-641, the block
  `if (tcl.n > 0) { ... }` after the curvature of the Gaussian clumps (curvature and
  shift, added with `+=`).
- `athenak/src/pgen/nrpic/nrpic_bowen_york.hpp`, `BYRead`: lines 338-339 added after the
  line that skips a Gaussian component (a table component with a boost file is skipped).
- New file `athenak/src/pgen/nrpic/nrpic_clump_table.hpp`; nothing added to
  `CMakeLists.txt`.
- `problems/ic/make_ic.py`: docstring, model `boosted`, options `--cluster`,
  `--cluster-p`, `--no-psi-correction`, `--boost-shift` (one new argument group, one new
  branch of the model switch, one print block). New: `python/nrpic/boosted_cluster.py`,
  `problems/clump/cluster_moving.athinput`, `problems/clump/cluster_binary.athinput`,
  `problems/tests/clump_table_static.athinput`, `problems/tests/clump_table_binary.athinput`.
- `docs/FORMATS.md`: a section "Boost table of a table component" at the end.
- `tracks/core/analysis/clump/regress.py` (of the first pass): executables by absolute
  path.

## 10. Executables for scouting runs (decision 0013)

`/data/haiyangw/nrpic/scratch/core/exe/core_clump-table/`: `athena_gpu`, `athena_cpu`,
`COMMIT`, `examples/`, `generator/`, `SHA256SUMS`, `READY` (options, one example each,
what is tested and what is not). Published by `tracks/core/analysis/clump2/publish_exe.sh`.
