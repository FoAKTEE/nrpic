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

PENDING: filled from the outcomes in `JOURNAL-clump2.md`.

## 7. Track F's request

PENDING.

## 8. Limits and open items

PENDING.

## 9. Lines touched in shared files

PENDING.

## 10. Executables for scouting runs (decision 0013)

PENDING.
