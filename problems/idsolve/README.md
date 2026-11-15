# Tests of the initial-data solver of the code

Option `<particles> id_solve = true` (source `athenak/src/particles/nrpic_idsolve.cpp`,
Robin faces of the multigrid solver in `athenak/src/multigrid/multigrid_robin.cpp`).
Interface, design, results and limits: `tracks/core/interfaces/id_solver.md`.

| File | Purpose |
|---|---|
| `make_ic.py` | particle files: `gaussian` (known solution), `strain` (triaxial ball), `wave` (torus) |
| `gaussian.athinput` | Gaussian density at rest, K = 0, Robin faces, against the exact psi of `nrpic_cf` |
| `ball.athinput` | expanding dust ball with the curvature of its table of format 2 (`problems/ic/make_ball.py`) |
| `torus.athinput` | plane wave in a homogeneous expanding universe (`nrpic_cosmo`), against `cosmo/ic` |

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
