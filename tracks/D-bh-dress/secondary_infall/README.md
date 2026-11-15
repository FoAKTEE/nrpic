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

### Results (run ids in `JOURNAL.md`, wave 2)

Runs with the clump at a cell centre: N128c (dx = 1.06 M, D-20261115-171503-4262f03), N64c
(2.125 M, -171505-62940f4), both to a/a_i = 4; N128Lc (2.75 M, box +-176 M, -171507-d1058a9) to
a/a_i = 8. Reference: the shells of `shells.py` with the measured mesh kernel at the same
times (`nm_shells.py`); final analysis D-20261115-190541-e27453d.

Run value, in brackets the kernel shells matched to that run (masses in M; from
`nm_growth_cellcentre.txt`, interpolated to the round a/a_i):

| | N128c | N64c | N128Lc |
|---|---|---|---|
| M_ta at a/a_i = 2 | 1.5063 (1.5065) | 1.5064 (1.5058) | 1.5077 (1.5059) |
| M_ta at a/a_i = 4 | 2.5966 (2.5956) | 2.5966 (2.5934) | 2.5962 (2.5937) |
| M_ta at a/a_i = 8 | | | 4.8159 (4.8019) |
| dress at a/a_i = 2 | 0.1744 (0.1735) | 0.1736 (0.1712) | 0.1751 (0.1694) |
| dress at a/a_i = 4 | 0.7975 (0.7976) | 0.7966 (0.7954) | 0.7977 (0.7940) |
| dress at a/a_i = 8 | | | 2.1537 (2.1515) |
| largest M_ta deviation after a/a_i = 1.5 | 0.10 % | 0.12 % | 0.31 % |
| profile, 4 dx to r_ta, outside the caustic bins | 12 % (rms 6.5 %) at 4 | 6.3 % at 4 | 26 % (rms 14 %) at 8 |

- Growth of the bound mass: the turnaround mass and the dress agree with the matched shell
  reference to 0.1-0.3 % and 0.01-0.15 % at the end (0.5 % for N128Lc at a/a_i = 4), and the
  three runs agree with each other to 0.2 % at a/a_i = 4, independent of dx from 1.06 to 2.75 M
  (`figs/nm_growth.png`). The three force laws of the reference differ at the end by up to
  1.4 % (M_ta) and 1.9 % (dress), Plummer lowest; at a/a_i = 2 the Plummer dress lies up to
  9 % below the kernel's (N128L, s = 1.68 M). The wave-1 numbers (Plummer s = 0.5 M: 2.593
  and 0.796 M at a/a_i = 4) agree with N128c within 0.2 %.
- Density profile: agrees with the matched shells within the bin scatter from 4 dx to
  r_ta except at the outermost caustic (16-20 M at a/a_i = 4), where the run has 1.3-1.9 times
  the reference: in N128c a few per cent of the dress lie up to 2.4 dx beyond the shells'
  caustic (r_sp99 18.4 against 15.9 M; r_sp90 agrees within 0.3 dx); cause open
  (`figs/nm_profiles.png`, `figs/nm_phase.png`).
- Against the self-similar solution (wave-1 test 2): at a/a_i = 4 the profile in units of
  r_ta lies at 0.46-0.93 of the self-similar rho/rho_b for lambda = 0.1-0.3; at a/a_i = 8
  (N128Lc) within 25 % on [0.1, 0.3], and still below inside lambda ~ 0.06 (slope about -1.7,
  not -9/4, where the seed dominates); the caustic is at lambda ~ 0.4 as in the solution
  (`figs/nm_selfsim.png`). Masses: dress/M_ta = 0.307 (a/a_i = 4) and 0.447 (8) against the
  self-similar 0.625; M_ta/(M a/a_i) = 0.649 and 0.602, approaching 0.565 from above; local
  growth exponent of the dress 1.70 at 4 and 1.25 at 8. The r^(-9/4) regime is not reached by
  a/a_i = 8; it needs the second Newtonian-mode run of `RUNS.md` (a/a_i = 30-100), which a
  uniform mesh on processors cannot afford.
- Runs with the clump at a mesh vertex (N128, N64, N128L): masses still within 1 % (M_ta) and
  2.3 % (dress), but the clump leaves the vertex at a/a_i = 1.75, 2.8, 3.4, the inner dress is
  heated and the caustic destroyed (`figs/nm_profiles_vertex.png`, `figs/nm_phase_vertex.png`,
  `figs/nm_clump_vertex.png`).
- Field calibration and clump stability: `figs/nm_field.png`, `figs/nm_clumpstab.png`;
  `kernel_nx64.txt`, `kernel_nx128.txt` (measured kernels), `nm_growth_cellcentre.txt` (growth
  tables of the three cell-centred runs with their references).

### Not done

- No run with a fixed point mass (core's executable was not published); the clump stand-in
  is what was run. The cause of the dust tail beyond the caustic in N128c is not established.
- No run to a/a_i = 30-100 (the self-similar regime); no refined mesh (multigrid octets
  unverified, interface section 6); no card run (0 card-hours used).
- Energy is not a usable check with the clump (its sub-cell self-interaction does not conserve
  K + W); no other conservation test of the dust alone was made.
- `harness/bin/nrpic-run` was used for the first four runs only; the rest are hand-registered
  (`nm_register.py`), see Requests.

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

### Requests (wave 2)

1. core: the fixed point mass of the Newtonian mode (outbox newtonian-mode-point-mass; work
   package on `core/requests-adf`) is needed, with evidence now: a compact clump at a mesh
   vertex is linearly unstable (e-folding about 2.5 M at dx = 2.125 M, scaling like
   (dx^3/GM)^(1/2); runs D-20261115-171245-a89f225, -170700-b2c6d6e, -170703-46ddffa,
   -170706-71431c6), at a cell centre stable, and its sub-cell self-interaction does not
   conserve energy (S1-C, D-20261115-171247-cde0674). Please add to
   `coord/INTERFACES/newtonian_mode.md` (sections 5.2 and 6) that a vertex is an unstable
   equilibrium of the self-force for a compact massive object and that the energy of such an
   object is not conserved. Once the executable is published this package reruns N128c with
   it (one line in `nm_run.py`: the clump replaced by `newton_pm_mass`).
2. core: whether the same self-force instability applies in the relativistic mode to compact
   particle clumps (shared deposit and gather kernels); relevant for clump binaries (Track F)
   and collapsed cores (Track C) [TO VERIFY; not tested here].
3. orch (harness): `nrpic-run submit --package` refuses the run when an untracked file lies
   in the worktree root (here `es.horizon_summary_0.txt`, written into the cwd by another
   helper's AthenaK run); it could record such files as it does for `tracks/<ID>/`. Twenty-four
   runs of this package were registered by hand instead (`nm_register.py`); their manifests
   carry `registered_by` and lack the environment hashes that `submit` records.
4. D-bh-dress lead: the outcome for `stage/G1/STATUS.md` (D-pre-3, AthenaK Newtonian mode):
   the first Newtonian-mode run agrees with the matched shell reference (masses 0.1-0.3 %,
   profile within the bin scatter outside the caustic); the self-similar regime is not
   reached; the hole stand-in must sit at a cell centre. The other helper whose run writes
   `es.horizon_summary_0.txt` into the worktree root should run AthenaK with `-d`.
5. core or orch: the processor executable is Serial (one core); these runs are particle-bound
   (about 3 s per step for 520k particles), so an OpenMP processor build would shorten them.
