# secondary_infall: D-pre-3 of Track D (helper package)

Newtonian secondary infall of collisionless dust onto a point mass (the black hole) in an
Einstein-de Sitter background, as semi-analytic references and a spherical-shell
reference calculation (decision 0010: no standalone simulation code), and (wave 2) the
particle version in AthenaK's Newtonian mode (release core-v0.3, `<particles> pusher =
newton`): section "Wave 2" below. From the references it fixes the parameters of the
AthenaK runs: `RUNS.md`.

Units G = c = 1, M = initial mass of the hole, eps = H_i M, t_i = 2/(3 eps). The set-up is
the scoping run's (`../scope/`): uniform dust in the unperturbed Hubble flow at t_i around
the seed.

## What is here

| File | What it is |
|---|---|
| `JOURNAL.md` | predictions written before each run, outcomes after (also the failed ones) |
| `RUNS.md` | the first Newtonian-mode run and the first full-relativity run, parameters, predicted numbers and profiles, cost |
| `common.py` | figure style loader, checksums, closed-form radial Kepler orbit (turnaround and collapse times) |
| `register_run.py` | runs one script as a registered run (manifest under `../runs/<run_id>/`, output under `scratch/D-bh-dress/<run_id>/`); refuses to run with uncommitted changes in this directory |
| `rd_checks.py` | test 1: radiation-era turnaround and the radial-orbit factor against what 1901.08528 and 2106.07480 print |
| `selfsimilar.py` | test 2: the self-similar collisionless infall onto a point-mass seed (Bertschinger type), fixed-point iteration |
| `shells.py` | test 3: spherical dust shells with shell crossing; centre passing (Newtonian-mode reference) or absorbing (capture by the hole, full-relativity proxy); optional tangential velocity dispersion with capture for L < 4 M_bh |
| `analyze.py` | combines tests 2 and 3, checks against the closed forms, growth curves, predicted profiles, run-parameter table with the scoping cost model |
| `figs/` | copies of the figures of the registered runs (run ids below) |
| `run_plan_D-bh-dress-20261115-125613-248fdaf.txt` | the run-parameter and cost table of the analysis run (copied from its output) |

## Figures (all looked at; run ids in `JOURNAL.md`)

- `figs/rd_checks.png`, `figs/rd_boost_mc.png`: test 1 (run D-bh-dress-20261115-122051-bf0d6b1).
- `figs/selfsimilar.png`: test 2 (run D-bh-dress-20261115-123813-97afeea).
- `figs/growth.png`, `figs/profiles_eps0.01.png`, `figs/profiles_eps0.03.png`,
  `figs/selfsim_check.png`, `figs/phase_space.png`, `figs/angular_momentum.png`: test 3 and
  the run plan (analysis run named in `JOURNAL.md`).

## How to rerun

From the worktree root (`wt/D-bh-dress`), with the package committed (the helper refuses
otherwise), one core each:

    S=tracks/D-bh-dress/secondary_infall
    python3 $S/register_run.py $S/rd_checks.py "test 1"
    python3 $S/register_run.py $S/selfsimilar.py "test 2" -- --taumax 300
    for c in absorb_e0.01 absorb_e0.03 pass_e0.01_s0.5 pass_e0.03_s0.5 pass_e0.1_s0.5_a100 \
             absorbL_e0.01_sig0.02 absorbL_e0.01_sig0.05 absorbL_e0.01_sig0.1 absorbL_e0.01_sig0.2 \
             absorb_e0.03_rw3 pass_e0.03_s0.5_rw3; do
        python3 $S/register_run.py $S/shells.py "test 3 $c" -- --config $c; done
    python3 $S/register_run.py $S/analyze.py "analysis" -- --ss <test-2 output dir> \
        --shells <the test-3 output dirs>

Wall times on one core: test 1 15 s, test 2 2 min, shells 2 s to 11 min each, analysis 6 s.
Python 3.10 with numpy 2.2, scipy 1.15, matplotlib 3.10 (no extra packages).

## Requests

Wave 1: see `RUNS.md`, section "Requests to other owners". Wave 2: section "Wave 2",
"Requests" below.

## Wave 2: the first Newtonian-mode run (helper newton_infall)

The first Newtonian-mode run of `RUNS.md` section 3, in AthenaK's Newtonian mode
(`coord/INTERFACES/newtonian_mode.md`), release processor executable
`/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena` (core-v0.3), one core per run, 0 card-hours.
Set-up: eps = 0.03 (t_i = 22.2 M), seed of mass M = 1, uniform cold dust in the Hubble flow
v = eps x for 3 M <= r < 18.35 M (1.2 x the initial radius of the shell that turns around at
a/a_i = 4; 24.5 M for the run to a/a_i = 8), isolated box with the multipole boundary, the code
in physical coordinates (a = 1), time t = t_cosmic - t_i. Predictions and outcomes:
`JOURNAL.md` from "Wave 2"; every number below has its run id there.

### The hole is a clump of particles, and what that changes

The release has no fixed point mass (request `outbox/20261115T1510Z__to-core__newtonian-mode-point-mass.md`;
core has it in work on `core/requests-adf`, no executable published when this ran). The hole
is a cold clump of 19952 equal-mass particles (total mass 1) inside r < 0.3 M. Measured
consequences:
1. Softening fixed by the mesh: the clump's force (runs F1) is almost zero inside 0.5 dx,
   overshoots M/r^2 by up to 30 % at 1.3-2 dx and is within 1 % beyond 4 dx (rms 8e-3) and
   1e-3 beyond 16 dx. A Plummer fit gives s_eff = 0.61 dx at both resolutions, but describes the
   kernel poorly; the shell reference therefore uses the measured kernel (`kernel_nx*.txt`).
2. Self-force: a compact mass at a mesh VERTEX is an unstable equilibrium (e-folding about
   2.5 M at dx = 2.125 M, scaling like (dx^3/GM)^(1/2)); it runs off and oscillates between
   neighbouring vertices at up to 0.3-0.5 c. At a CELL CENTRE it is stable, but an offset of
   0.05 dx already gives it 0.11 c (runs S1). The production set-up therefore puts the clump
   at a cell centre with the dust lattice symmetric about it; there the clump stays within
   2e-5 dx of the centre. In the runs with the clump at a vertex the global masses are
   unaffected, but the inner dress is heated: density inside 2 M low by 2-7, caustic
   smeared, dust flung out at up to 0.8 c (`figs/nm_phase_vertex.png`).
3. Energy: the clump's sub-cell self-interaction does not conserve energy (K + W of the clump
   alone drifts by 5 % of its |W|), so K + W is no check of the dust here.
4. A fixed point mass would remove 2 and 3 and let the softening be chosen; with a random
   (not lattice-symmetric) dust the clump would be kicked off the cell centre and jiggle.

### Files

| File | What it is |
|---|---|
| `nm_ic.py` | particle files: clump + dust lattice (+ tracers), and `setup.json` with every derived parameter |
| `nm_infall.athinput` | AthenaK input (isolated, multipole boundary, Newtonian mode); the mesh and times are set by `nm_run.py` |
| `nm_run.py` | one AthenaK run: particle file, executable, overrides; `--onestep` for the field measurement, `--shift_cells` to centre on a cell |
| `nm_field.py` | field calibration of the clump (tracers after one step): errors by distance, Plummer fit, measured kernel |
| `nm_clumpstab.py` | clump displacement and momentum against time (vertex and cell-centre stability) |
| `nm_shells.py` | the shell reference of `shells.py` matched to a run: measured mesh kernel, Plummer s_eff, or near point mass, at the run's snapshot times |
| `nm_analyze.py` | turnaround mass, dress, profiles, clump, conservation from the snapshots, against the matched shells and the self-similar solution; figures |
| `nm_register.py` | hand registration of runs (manifest, commit, detached run, `finish`), used because `harness/bin/nrpic-run submit` refused (Requests) |
| `figs/nm_*.png` | copies of the figures of the registered analysis runs |

### How to rerun

From the worktree root, package committed. Each line is one registered run (one core):

    S=tracks/D-bh-dress/secondary_infall; P=".venv/bin/python"; X=/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena
    reg() { $P $S/nm_register.py start --purpose "$1" --input $S/nm_infall.athinput --input $X -- "${@:2}"; }
    # field calibration (F1, F2) and the timing probe
    reg F1-64  $P $S/nm_run.py --kind field --nx 64 --L 68 --onestep
    reg F1-128 $P $S/nm_run.py --kind field --nx 128 --L 68 --onestep
    reg F2     $P $S/nm_run.py --kind fieldfull --nx 128 --L 68 --onestep
    reg nm_field $P $S/nm_field.py --run "nx=64:<F1-64 dir>" --run "nx=128:<F1-128 dir>" --run "nx=128 with dust:<F2 dir>"
    # clump stability (S1)
    reg S1-V $P $S/nm_run.py --kind field --nx 64 --L 68 --tlim 40 --dtmax 0.1 --cfl 0 --nsnap 40 --shift_cells 0.05 0 0
    reg S1-C $P $S/nm_run.py --kind field --nx 64 --L 68 --tlim 40 --dtmax 0.1 --cfl 0 --nsnap 40 --shift_cells 0.55 0.5 0.5
    # infall, clump at a cell centre (drop --shift_cells for the vertex runs)
    reg N128c  $P $S/nm_run.py --kind infall --nx 128 --L 68  --aend 4 --shift_cells 0.5 0.5 0.5
    reg N64c   $P $S/nm_run.py --kind infall --nx 64  --L 68  --aend 4 --shift_cells 0.5 0.5 0.5
    reg N128Lc $P $S/nm_run.py --kind infall --nx 128 --L 176 --aend 8 --dtmax 0.5 --shift_cells 0.5 0.5 0.5
    # matched shell references (setup.json of the run, kernel file of nm_field)
    reg shells $P $S/nm_shells.py --setup <run>/setup.json --label N128_kernel --law kernel --kernel <nm_field>/kernel_nx128.txt --dx 1.0625
    #   (also --law plummer --soft 0.6489 | --law point --soft 0.05; N64: kernel_nx64, dx 2.125, s 1.2932; N128L: kernel_nx128, dx 2.75, s 1.68)
    reg nm_analyze $P $S/nm_analyze.py --run "N128c:<dir>" ... --ref "N128c:kernel:<shells dir>/nm_shells_N128_kernel" ... \
        --selfsim scratch/D-bh-dress/D-bh-dress-20261115-123813-97afeea/selfsimilar_profile.npz
    $P $S/nm_register.py finish <run_id>      # after each run

Wall times on one core of the loaded machine: one-step runs 1-7 s; S1 75 s; N64 26-30 min
(2.2 s per step, the 520k particles dominate); N128 and N128L 1-2 h (about 3 s per step);
shells 2 s to 12 min; analysis 35 s.
