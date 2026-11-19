# Tests of the initial-data solver of the code

Option `<particles> id_solve = true` (source `athenak/src/particles/nrpic_idsolve.cpp`,
Robin faces of the multigrid solver in `athenak/src/multigrid/multigrid_robin.cpp`).
Interface, design, results and limits: `tracks/core/interfaces/id_solver.md`.

| File | Purpose |
|---|---|
| `make_ic.py` | particle files: `gaussian` (known solution), `strain` (triaxial ball), `boost` (a copy with u_x set), `shift`, `zeldovich` (triaxial Zel'dovich displacement of a ball with its momenta), `wave` (torus; `--nest` for a finer lattice in a refined cube, `--velocity` for the momenta of the growing mode), `shell` (a Gaussian shell of particles, the matter of the puncture tests) |
| `gaussian.athinput` | Gaussian density at rest, K = 0, Robin faces, against the exact psi of `nrpic_cf` |
| `ball.athinput` | expanding dust ball with the curvature of its table of format 2 (`problems/ic/make_ball.py`) |
| `torus.athinput` | plane wave in a homogeneous expanding universe (`nrpic_cosmo`), against `cosmo/ic` |
| `puncture.athinput` | second pass: one Bowen-York puncture (m = 1, P = 0.5 along x), vacuum; psi = 1 + m/2r + u with u solved; with `particle_file` a shell of matter around it (`make_ic.py shell`) |
| `gaussian_boost.athinput` | the Gaussian with every particle moving (u_x = 0.1): the vector equation (`id_vector = true`) against a semi-analytic continuum solution |

The scripts that run the tests, compare with the references and draw the figures are in
`tracks/core/analysis/idsolve/` (`run_tests.py`, `analyze_*.py`); predictions and
outcomes in `tracks/core/JOURNAL-idsolve.md`.

One run from start to finish (processor build, about 10 s):

```
python3 problems/idsolve/make_ic.py gaussian --h 0.5 --out $D
cd $D && athena -i <repo>/problems/idsolve/gaussian.athinput mesh/nx1=32 mesh/nx2=32 \
    mesh/nx3=32 particles/particle_file=gauss_h0p5.nrp
cat gauss.idsolve.txt       # one record per Newton iteration, last line: summary
```

The vector equation (`<particles> id_vector = true`, interface section 10): the
recommended residual is the constraint monitor, `id_vector_residual = code` (add the line
to the `<particles>` block; `gaussian_boost.athinput` keeps the stencil form that tests
V1 and V2 used). Example:

```
python3 problems/idsolve/make_ic.py gaussian --h 0.5 --out $D
python3 problems/idsolve/make_ic.py boost --in $D/gauss_h0p5.nrp --u 0.1 --out $D
cd $D && athena -i <repo>/problems/idsolve/gaussian_boost.athinput mesh/nx1=32 \
    mesh/nx2=32 mesh/nx3=32 particles/particle_file=gauss_h0p5_u0p1.nrp
tail -2 gboost.idsolve.txt  # summaries of the scalar and the vector part
```

Second pass (`tracks/core/interfaces/id_solver2.md`, journal `tracks/core/JOURNAL-idsolve2.md`,
test scripts `tracks/core/analysis/idsolve2/`): far field at the faces (`id_far`, on by
default on a mesh with no periodic face), refined meshes (static refinement:
add `<mesh_refinement> refinement = static` and `<refined_regionN>` blocks), punctures
of `nrpic_cf` in the solve, CMC data on the torus (`torus.athinput` with
`<problem> id = file`). A puncture in vacuum, start to finish (processor build, about
10 s at 32 cells):

```
cd $D && athena -i <repo>/problems/idsolve/puncture.athinput mesh/nx1=32 mesh/nx2=32 \
    mesh/nx3=32 meshblock/nx1=16 meshblock/nx2=16 meshblock/nx3=16
tail -3 punc.idsolve.txt   # summary and the far-field line (M_psi, P_ADM, J_ADM)
```

With matter: `python3 problems/idsolve/make_ic.py shell --h 0.5 --out $D` and a line
`particle_file = shell_h0p5.nrp` in the `<particles>` block of a copy of the input (an
option absent from the input file cannot be set on the command line).
