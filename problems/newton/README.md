# Newtonian mode of the particle module: inputs and tests

The Newtonian mode (`<particles> pusher = newton`,
`athenak/src/particles/nrpic_newton.cpp`) moves the particles of the NRPIC module in
the potential of their own rest mass, with the deposit, filter, compensation and
interpolation of the relativistic mode. Interface, options, output columns and the
results of the tests below: `tracks/core/interfaces/newtonian_mode.md`.

| File | Purpose |
|---|---|
| `isolated.athinput` | isolated domain, multipole boundary of the multigrid solver, no expansion |
| `periodic.athinput` | periodic box, comoving coordinates, matter-dominated scale factor |
| `isolated_smr.athinput` | `isolated.athinput` with one static refinement level: a trial, not verified (interface note, section 6) |
| `analyze_conservation.py` | test T6: moving, rotating ball: conservation laws, six components of the second moment |
| `make_ic.py` | particle files of the tests: point mass with tracers, homogeneous ball, plane wave |
| `analyze_field.py` | tests T1 and T2: field of a point mass and of a ball against the exact fields |
| `analyze_collapse.py` | test T3: cold collapse of a ball against the cycloid, energy, second moment |
| `analyze_wave.py` | test T4: plane wave against Zel'dovich, `cosmo/newton/pm.py` and the numpy scheme |
| `../../python/nrpic/newton.py` | exact solutions, readers, the scheme of the code in numpy |
| `../../tracks/core/tools/compare_restart.py` | test T5: a continued run against the uninterrupted one |
| `../../tracks/core/tools/regress_relativistic.py` | regression of the relativistic mode between two executables |

## Running the tests

`EXE` is an executable built from this tree (`scripts/build_cpu.sh`,
`scripts/build_gpu.sh`). A parameter that is not in the input file cannot be added on
the command line; both inputs list every option of the mode.

```
# particle files
python3 make_ic.py point --out point.nrp --center 0.031 0.017 -0.011
python3 make_ic.py ball  --out ball_field.nrp --center 0.031 0.017 -0.011 --spacing 0.015625
python3 make_ic.py ball  --out ball64.nrp --spacing 0.0625 --ntracer 0
python3 make_ic.py wave  --out wave32.nrp --n 32

# T1, T2: one step of 1e-6; the momentum after the step over the step is the acceleration
EXE -i isolated.athinput mesh/nx1=64 mesh/nx2=64 mesh/nx3=64 time/nlim=1 \
    particles/dt=1e-6 particles/snap_dt=1e-6 particles/particle_file=point.nrp
python3 analyze_field.py point --ic point.json --run 32:DIR32 --run 64:DIR64 --run 128:DIR128 --out OUT

# T3: collapse to 0.9 free-fall times
EXE -i isolated.athinput mesh/nx1=64 mesh/nx2=64 mesh/nx3=64 time/tlim=1.0 \
    particles/dt=0.002 particles/snap_dt=0.05 particles/particle_file=ball64.nrp
python3 analyze_collapse.py --run "N = 64:ball64:DIR" --out OUT

# T4: plane wave through shell crossing (a = 4 at t = 2)
EXE -i periodic.athinput particles/particle_file=wave32.nrp
python3 analyze_wave.py --run "N = 32:wave32:DIR" --out OUT

# T5: restart (dump every 0.4), then continue in another directory
EXE -i isolated.athinput ... output1/dt=0.4
EXE -r rst/newton.00001.rst        # needs .rst, .rst.prt and .rst.prt.nwt side by side
python3 ../../tracks/core/tools/compare_restart.py FULL_DIR CONTINUED_DIR
```

MeshBlocks must be cubes with a power-of-two size (a restriction of the multigrid
solver); with `nx = 32` use `meshblock/nx1=16` and so on.

## What the tests established

Run ids, numbers and figures: `tracks/core/interfaces/newtonian_mode.md`, section 5, and
`tracks/core/JOURNAL-newton.md` (predictions and outcomes, including the failed ones).
