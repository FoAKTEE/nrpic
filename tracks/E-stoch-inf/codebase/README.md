# codebase: design review of the scalar field with stochastic sources in AthenaK (E-pre-2)

Helper package of owner E-stoch-inf, under decision 0010 (Track E builds on this
repository's AthenaK; core writes the scalar field on `core/scalar-field`). This
directory holds the design review that the implementation needs, the reference
algorithms it is to be checked against, and the checks behind the review's claims. It
contains no simulation code.

## Contents

| Path | What |
|---|---|
| `DESIGN_REVIEW.md` | the review: the code as it is (Z4c variables, Tmunu, task list, integrator, boundaries, refinement, how `dyn_grmhd` and the particles fill Tmunu); scalar-field equations in the code's variables and signs; the stochastic kicks and where they enter; the window and noise in a periodic box without a Fourier library; what is shared with Track B and what the field-to-particle hand-over needs; the test ladder; the compute estimate; the outside codes; requests |
| `JOURNAL.md` | predictions written before each check, outcomes after (D1 to D4) |
| `ref/synth.py` | reference algorithms: ball of wave vectors, Hermitian draws, separable MeshBlock synthesis, operation counts, stencil symbols of `utils/finite_diff.hpp`, window and its derivatives, stage times of the low-storage RK4 of `driver/driver.cpp` |
| `ref/d1_memory.py` | D1: memory fit of vacuum Z4c (processor runs) and extrapolation |
| `ref/d2_synthesis.py` | D2: synthesis against `numpy.fft.ifftn`; operation table |
| `ref/d3_momentum.py` | D3: first-order momentum constraint of the kick with the sixth-order stencil, projector in k against k_eff |
| `ref/d4_stages_window.py` | D4: RK4()4[2S] stage times and order, window derivatives, number of touched modes |
| `ref/cost.py` | compute estimate (card-hours, memory) for the two test cases |
| `inputs/mem.athinput` | input of the D1 runs (copy) |
| `figs/` | figures of D1 to D4 (PNG) and their result tables (`d1.json` to `d4.json`, `cost.json`) |

## Runs

| Run id | What |
|---|---|
| E-stoch-inf-20261115-122727-a1c2237 | D1: five AthenaK runs of periodic vacuum Z4c on one core (`.work/build_cpu_c1/src/athena`, `z4c_linear_wave`, meshes 32^3 and 64^3, MeshBlocks 16^3 to 64^3, 4 cycles) |
| E-stoch-inf-20261115-123936-b2ec5c7 | analysis of D1, checks D2 to D4, cost table (first attempt with `python3 -I` failed at the numpy import; logs kept in `attempt1/`) |

Manifests: `tracks/E-stoch-inf/runs/<run_id>/manifest.json`. Outputs:
`/data/haiyangw/nrpic/scratch/E-stoch-inf/<run_id>/`. No card time was used.

## How to rerun

```
# D1 (processor, about 4 min on one core)
R=/data/haiyangw/nrpic/scratch/E-stoch-inf/<new run id>; mkdir -p $R; cp inputs/mem.athinput $R/
cd $R; export OMP_NUM_THREADS=1; EXE=/data/haiyangw/nrpic/.work/build_cpu_c1/src/athena
for b in 64 32 16; do mkdir mb$b; (cd mb$b; /usr/bin/time -v $EXE -i ../mem.athinput \
  meshblock/nx1=$b meshblock/nx2=$b meshblock/nx3=$b > athena.log 2> time.log); done
for b in 32 16; do mkdir n32mb$b; (cd n32mb$b; /usr/bin/time -v $EXE -i ../mem.athinput \
  mesh/nx1=32 mesh/nx2=32 mesh/nx3=32 meshblock/nx1=$b meshblock/nx2=$b meshblock/nx3=$b \
  > athena.log 2> time.log); done
# analysis and checks (about 1.5 min; numpy, scipy, matplotlib of the system Python)
cd tracks/E-stoch-inf/codebase/ref; OUT=<output dir>
python3 d1_memory.py $R $OUT; python3 d4_stages_window.py $OUT
python3 d3_momentum.py $OUT; python3 d2_synthesis.py $OUT
python3 cost.py $OUT $OUT/d1.json $OUT/d2.json
```

The scripts import the figure style from `python/nrpic/figstyle.py` through a relative
path. They read no downloaded data, so they run without `-I`.

## Results in one screen

- D1: vacuum Z4c memory is 7 MB + 687 B per interior cell + 1257 B per ghost cell (five
  runs, each within 1 percent). 256^3 with the scalar field needs about 20 GB on one card;
  512^3 does not fit. Throughput is 1.5e4 zone-cycles/s per core.
- D2: the separable MeshBlock synthesis equals the FFT to 1.2e-14 of the rms and is
  bitwise independent of the MeshBlock size. At 256^3 with n_max = 64 it costs 149
  complex multiply-adds per cell (128^3 MeshBlocks).
- D3: the kick's projector built from k violates the discrete momentum constraint at first
  order, by up to 6.9e-3 at k_max; built from the stencil's k_eff, by 1e-15.
- D4: the driver's RK4 evaluates its stages at c = (0, 1.194, 0.431, 1). A time-dependent
  source must be evaluated there to keep order 4; at the step start the order drops
  to 1.
- Cost: 0.36 to 0.51 card-hours per 256^3 realisation at Courant 0.25, or 3.6 to 5.1 at
  0.025.

## Requests

Details and reasons: `DESIGN_REVIEW.md` section 11.

To core:
- R1 Scalar-field class in the numerical-relativity task list, with Tmunu from the
  stage's chi and gt, and `Z4c_ExplRK` waiting for the field's right-hand side.
- R2 Additive Tmunu (field and particles together), also in the constraints and their
  statistics.
- R3 Kicks on Khat, At_ij and Pi at the stage times, with the sign-safe Pi kick and the
  projector in the stencil's k_eff; off by default and bitwise neutral when off.
- R4 Noise without a Fourier library: alpha_n from `core/rng` stream 3 with
  entity = wave numbers, mode amplitudes per |k| integrated in the same stages, and the
  per-MeshBlock synthesis checked against `ref/synth.py`. cuFFT only as a measured
  fallback.
- R5 A stage time for every stage task, or the mode equations integrated in lockstep.
- R6 Double-precision output, constraint statistics independent of the particle module
  (with P1's [H], [M]), exact restart of the field and the noise state.
- R7 SPEC section 10 item 3 (GPU FFT) is replaced by R4.
- R8 `NRCOSMO2` initial-data file (phi, Pi added), or the in-code initial slice.

To Track B:
- R9 Agree on `NRCOSMO2` and on shared box-mean, spectrum and constraint tools. Say when
  the in-code CTTK or projection solve is planned (needed by E only at the hand-over).

To the owner:
- R10 Courant factor 0.25 for G1 unless L6 shows a dependence. Level 0 or 1 backreaction
  as a stated difference from P1.
