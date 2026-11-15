# newton_tests (helper package of B-emd-gw, wave 2)

The Newtonian baseline of Track B run in AthenaK's Newtonian mode (release core-v0.3,
`<particles> pusher = newton`, `coord/INTERFACES/newtonian_mode.md`): the plane-wave
pancake against the exact Zel'dovich solution up to shell crossing, and the homogeneous
ellipsoid with the quadrupole history against the semi-analytic baseline of wave 1
(`../baseline/`) and the (2 alpha)^(7/2) scaling. Predictions and outcomes: `JOURNAL.md`.

State: in progress (this file is rewritten when the results are in).

| Path | Content |
|---|---|
| `JOURNAL.md` | predictions (before each run) and outcomes |
| `inputs/pancake.athinput` | periodic expanding box, numerics of `cosmo/newton/pm.py` in the verify_cosmo pancake |
| `inputs/ellipsoid.athinput` | isolated domain, multipole boundary, no expansion |
| `scripts/make_particles.py` | particle files: `pancake-east`, `pancake-sin`, `ellipsoid` |
| `scripts/run_case.sh` | one AthenaK run in `$NRPIC_RUN_DIR/<name>/` (generator, then the processor executable) |
| `scripts/run_selfsim.sh` | the three rescaled ellipsoid runs of test N3 |

## Requests

(filled in when the package closes)
