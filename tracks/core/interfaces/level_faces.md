# The deposit at faces between refinement levels: two corrections without an option

Owner core. Branch `core/faces-finder` (batch 34a, 2026-11-27), candidate for release
core-v0.9; proposal for `coord/INTERFACES/level_faces.md`. Items 0 and 0b of
`tracks/core/NEXT_SOURCE.md`; Track A's request `pcs-deposit-refinement-boundary` and
decision 0047 item 2(a) (the retest of the constraint floor after these fixes). Evidence
and every number: `tracks/core/JOURNAL-faces-finder.md` (entries 1, 3, 4, 5); scripts
`tracks/core/analysis/faces_finder/dep_compare.py`, `comp_cons.py`,
`tracks/core/analysis/deposit_levels/dep_levels.py`. Executables:
`/data/haiyangw/nrpic/scratch/core/exe/core_faces-finder/` (READY there).

Neither change has an option. Both act only on a mesh with refinement
(`<mesh_refinement> refinement = static | adaptive`), and only in runs that set one of

```
<particles>
deposit_fine_shape = true        # with deposit_shape = cic            (correction 1)
deposit_comp_c     = c > 0       # with any cloud, any c2 and limit    (correction 2)
```

A run on a uniform mesh, and a run on a refined mesh without these two settings, writes
the bytes of release core-v0.8 (section 4).

## 1. Linear cloud with `deposit_fine_shape`: no share beside the cloud unless the cloud is held at the cap [VERIFIED]

With `deposit_fine_shape` a linear cloud (CIC) whose lattice cell covers finer leaf cells
gives each leaf the integral of its assignment function (the tent) plus a constant, and
the lattice cells on either side of the cloud, which carry no weight, get a share that
sums to zero. That share is one half of a scheme: for a regular lattice of particles it
is cancelled by the shares of the clouds that own the cell, laid on the same lattice.
The owners lie on the same lattice only when it is the lattice of the level cap
(`deposit_max_level`, `deposit_ppc`), on which the clouds of every finer block are held.
Without a cap the clouds of a finer block lie on the finer lattice, and release core-v0.8
left the half share in place: a dipole of -1/8 and +1/8 of the density in the two fine
cells next to a level face (lead's run core-20261126-022953-21b8455, case `cic_fs`).

Now a lattice cell beside a linear cloud is visited only if the cloud's lattice is the
lattice of its cap (`particles/nrpic.cpp`, `NrpicDepositSources`, one line before the
fine-shape branch). Consequences:

- Without a cap `deposit_fine_shape` does nothing with any cloud (as the interface
  `cosmo_amr.md` says it should): the table of `cic_fs` equals that of `cic` byte for
  byte, where core-v0.8 differs in the two cells x1 = 7.25, 7.75 by +-0.125 (run
  core-20261127-234848-7d666df). In the three-dimensional test the smallest energy
  density of the run rises from -1.46e-3 to 0 (run core-20261127-234843-fa6c2e9, case
  `cic_fs`).
- With a cap, clouds on the cap lattice are as before (case `cic_capfs` byte-identical).
  A cloud on a lattice coarser than its cap (a coarse block next to a finer one, both at
  or below the cap) no longer leaves a share in the finer block.
- Quadratic and cubic clouds never had the side cells: unchanged.

The lead's proposal was a flag "this cloud was capped". It would have skipped the share
of a cloud whose own cells are leaves of the cap level while its neighbours, capped, own
the finer cell beside it, and a regular lattice would have lost uniformity there
[by reading; not run].

## 2. Compensation of the cloud: one flux through a face between levels [VERIFIED]

The compensation pass (`deposit_comp_c`, with `deposit_comp_c2` and
`deposit_comp_limit`) is u - (F_{i+1/2} - F_{i-1/2}) in each direction, on every
MeshBlock, with ghost values of the other level at a level face. The flux through such a
face was computed twice, by the coarse block and by the fine blocks, from different
data, so what left one side did not enter the other. The two fluxes do not differ by
truncation error only: the pass is u - c d2 u in cells of the level (it undoes a cloud as
wide as the cell of the level), so the flux per area, c dx^2 du/dx, is four times larger
on the coarse side. No flux is consistent with both sides.

Now (`particles/nrpic_levelface.cpp`, `NrpicCompensateLevelFaces`; called from
`NrpicCompensateLimited`):

1. The flux of the fine side counts for both sides. After the pass of one direction the
   coarse cell at a level face gives back the flux it used and takes the sum of the
   fluxes of the four fine faces, weighted by the volumes (in units of the update,
   F_coarse = 1/8 of the sum). The fine cells keep their pass. With the limiter the
   fine fluxes carry the limiter of the fine cells.
2. On a mesh with refinement the ghost cells are filled before each of the three
   directions (three exchanges per deposit instead of one). With one exchange the pass
   along x1 also acts in the ghost cells so that the passes along x2 and x3 find their
   neighbours; a block's ghost copy of a corrected cell (or of a prolongated one) is then
   not what its neighbour holds, and two blocks of one level disagree on the flux through
   their common face. The first form of this change, without the extra exchanges, left
   an error of 3.4e-5 (run core-20261127-234454-3c39b48).
3. On a mesh with refinement the plain pass (no `deposit_comp_c2`, no limiter), which on
   a uniform mesh is taken as a product of three stencils, is taken in the same flux
   form, so that it is corrected too.

What changes in the fields, on a refined mesh with `deposit_comp_c > 0`:

- the coarse cells at level faces, by c times the jump of the deposit there (in the
  planar test of a uniform lattice: -0.0076 and -0.0338 of the density at the two faces;
  the largest energy density of the three-dimensional test changes by 5e-3 relative with
  the cubic cloud and c2, by 1e-5 with the linear cloud);
- cells next to a level edge or corner at the level of prolongation differences (they
  now see ghost values exchanged after each direction);
- with the plain pass, every cell at rounding level (3e-16 relative in the largest
  density of the test), because three passes in turn replace one product.

Tests (processors, release core-v0.8 against this branch):

| Test | core-v0.8 | this branch | Run |
|---|---|---|---|
| Uniform lattice across a plane face, cubic cloud, c = 1/6, c2 = 0.4667: sum of E dx on a line (32 expected) | 32.04131944 | 31.999999999999996 | core-20261127-234848-7d666df |
| The same: cells that differ between the builds | | the two coarse cells at x1 = -8.5, +8.5 only | same |
| 10^4 random particles moving across a cube in a cube (three levels, faces, edges, corners), 11 records: largest error of the integral of E over the mesh against the sum of m W, cubic cloud with c2 (Track A's settings) | 9.9e-4 | 2.7e-14 | core-20261127-234843-fa6c2e9 |
| the same with the limiter (1/6) | 3.6e-4 | 2.1e-14 | same |
| quadratic cloud, plain pass c = 1/8 | 6.4e-4 | 3.3e-14 | same |
| linear cloud, plain pass c = 1/12 | 2.4e-4 | 2.1e-14 | same |
| momentum integrals, the four cases (error over the sum of m W) | 5.9e-5 to 1.5e-4 | below 1e-15 | same |
| no compensation; uniform mesh with either pass | | histories byte-identical | same |

Figures: `fig_dep_compare.png`, `fig_comp_cons.png` in the two run directories.

## 3. What these changes do not do

- The deposit itself is not uniform at a level face for a lattice of particles (lead's
  test: deviations of 0.19 to 0.21 of the density in the cells at the face for the
  quadratic and cubic cloud without compensation; with compensation 0.37 before and 0.34
  now in the coarse cell at the face). Conservation is restored; the ripple at the face
  is not removed. Whether it is the cause of Track A's constraint floor is for the
  track's retest to say (decision 0047 item 2(a)); core has not run Track A's set-up.
- The coarse cell at a level face now carries a first-order error of the pass for a
  density gradient across the face ((3/4) c dx du/dx by the choice of the fine flux);
  before, the pass was locally consistent on both sides and not conservative. No choice
  of the flux avoids both.
- With the limiter the coarse cell takes fluxes limited by the fine cells; the bound
  that keeps the energy density positive (limit at most 1/6) is not proved for that
  cell [JUDGEMENT; no negative density seen in the limited case of the test].
- Several ranks: a fine block on another rank is not reached, and that face keeps the two
  fluxes (not conservative there). Not tested on several ranks. The source filter
  (`nfilter`, `filter_compensate`) is not touched: it acts on the sources themselves and
  was never conservative across levels (history columns 24 to 27 record it).
- Cost: two more ghost exchanges of the ten source components per deposit on a refined
  mesh with compensation, and for the plain pass three directional passes in place of
  one product. On processors, in a test that evolves no metric (the deposit is all of
  its time; serial build, indicative): cubic cloud with c2 11.9 s before and 12.1 s now;
  linear cloud with the plain pass 5.3 s and 10.7 s (run core-20261127-234843-fa6c2e9).
  Not timed on a card in this session.

## 4. Which runs change, and the byte regression

Changed: runs on a refined mesh with `deposit_comp_c > 0` (all cells at rounding level
for the plain pass, the coarse cells at level faces and the cells near level edges by
the amounts above), and runs on a refined mesh with `deposit_fine_shape` and the linear
cloud (fine cells beside clouds that are not on the cap lattice). Track A's nested
static meshes with the cubic cloud and compensation are of the first kind: every such
run changes from its first deposit on.

Unchanged: everything else. Of the twelve set-ups (75 items) of the byte regression
`analysis/release/regress_v04.py`, three have refinement (`dep`, `os`, `c3`) and none of
them sets `deposit_comp_c` or `deposit_fine_shape` (they use `nfilter`, the source
filter); the cosmology set-ups with compensation of the filter are on uniform meshes. So
no item may differ. Result: section 5 of the journal and the READY file.
