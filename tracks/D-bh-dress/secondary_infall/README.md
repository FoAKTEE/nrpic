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

## Wave 3: toward the self-similar regime (helper secondary_infall, 2026-11-20/21)

One Newtonian-mode run to a/a_i = 30 on core's threaded processor build
(`/data/haiyangw/nrpic/scratch/core/exe/core_build-openmp/athena_cpu`, six threads, 0
card-hours), against shells matched to the same mesh and the self-similar solution of
test 2; and R8, the wave-2 run N128Lc repeated unchanged on the threaded build, as the check
of that build at a/a_i = 4 and 8. Design, predictions and outcomes: `JOURNAL.md` from "Wave 3"
(entries 2026-11-20T22:25Z to the end); every number below has its run id there.

### Set-up of the run to a/a_i = 30 (P192)

The wave-2 set-up scaled up: eps = 0.03 (t_i = 22.2 M), clump of 19952 particles (mass 1,
r < 0.3 M) at a cell centre with the dust lattice symmetric about it, 500 248 dust particles
on the lattice for 3 M <= r < 36.2 M (1.1 times the initial radius of the shell that turns
around at a/a_i = 30), isolated box +-854 M (1.12 times the radius of the dust edge at the
end), nx = 192 (MeshBlocks 64^3), dx = 8.896 M, to t = 3629 M (a/a_i = 30); snapshots every
9.612 M (as N128Lc), restart files every 600 M. lambda_min = 4 dx/r_ta = 0.063 at
a/a_i = 30 (r_ta = 569 M), 0.144 at 16, 0.36 at 8. Because the dust ball spans only 4.1 cells
at t = 0, two shell references bracket the run: "kernel" (the measured clump kernel applied
to all enclosed mass) and "hybrid" (kernel for the seed, dust unsoftened outside 0.5 dx).

### Files (wave 3)

| File | What it is |
|---|---|
| `nm_design.py` | design table: box, mesh, lambda_min and particle counts for candidate set-ups (closed-form turnaround) |
| `nm_cost.py` | step count of a run from its matched shells, calibrated on N128Lc's history |
| `nm_late.py` | shared late-time comparison: 0.1-dex bins to 2048 M, self-similar solution binned in the run's bins, local slopes, the range [max(4 dx/r_ta, 0.03), 0.3] |
| `nm_predict.py` | predictions from the shell references and the self-similar solution (masses, ratios, profile, slopes) |
| `nm_shells.py` | (extended) `--law hybrid`, `--snap_dt` |
| `nm_run.py` | (extended) `--threads`, `--bind` (six least busy cores of one node, OMP_PROC_BIND=true, OMP_PLACES=cores inside that mask), `--snap_dt`, `--rst_dt` |
| `nm_analyze.py` | (extended) bins to 2048 M, growth to a/a_i = 30, the "late" comparison per a/a_i, figures `nm_late_profiles_<run>`, `nm_late_growth`, table `nm_late.txt` |
| `nm_threadcheck.py` | a run against another of the same input: inputs, history, particles by tag, masses, profiles |
| `nm_jsondiff.py` | regression of the analysis script: two nm_analysis.json compared leaf by leaf |
| `nm_kernelcmp.py` | measured clump kernels side by side (vertex against cell centre) |
| `nm_lost.py` | which particles leave the box, against the exact Newtonian apocentres; dust edge against its closed-form orbit |
| `nm_energy.py` | energy of single-stream, uncrossed dust shells against t = 0 (exactly conserved in spherical Newtonian gravity): the force error each shell has felt |
| `nm_field.py` | (extended) measures relative to the clump when the configuration is shifted; cell-centre kernel file `kernel_nx<N>_cc.txt` |
| `kernel_nx64_cc.txt`, `kernel_nx128_cc.txt` | the clump kernel with the clump at a CELL CENTRE (run D-20261121-084407-ffb542d); `kernel_nx*.txt` without `_cc` are the wave-2 kernels, measured at a mesh VERTEX |
| `figs/w3_*.png` | copies of the wave-3 figures (run ids in the table below) |

### Runs (wave 3)

| What | Run id | Figure |
|---|---|---|
| design table | D-20261120-222358-e98ffbd | |
| timing of the a/a_i = 30 set-up (0.66 s per step, six threads) | D-20261120-222405-ce8922c | |
| shells of P192, vertex kernel: kernel, hybrid, Plummer, point | D-20261120-222511-34be8a8, -222758-acc6929, -222513-9849530, -222515-c2ef5b8 | |
| step model (3250-3520 steps) | D-20261121-075022-87d85b7 | `figs/w3_cost.png` |
| predictions P from the shells | D-20261121-075105-2cff004 | `figs/w3_P192_predict_profiles.png` |
| P192 production, FAILED at start (MeshBlock 96^3 refused) | D-20261121-075341-6310218 | |
| **P192 production run to a/a_i = 30** (2914 steps, 0.70 h, six threads) | **D-20261121-075559-31835c4** | |
| P192 analysis (vertex-kernel shells) | D-20261121-083847-95e881c | |
| R8: N128Lc rerun on the threaded build (1763 steps, 1609 s, three threads) | D-20261120-222550-e472402 | |
| R8 against N128Lc | D-20261121-083851-b5b9acc | `figs/w3_R8_threadcheck.png` |
| extended nm_analyze.py: regression on N128Lc, R8 analysed | D-20261121-083858-c59f5d3 | |
| cell-centre field runs nx 64, 128; field analysis; kernel comparison | D-20261121-084354-f534489, -084357-8b3a981, -084407-ffb542d, -084434-557b3e9 | `figs/w3_kernel_vertex_cellcentre.png` |
| shells of P192, cell-centre kernel: kernel_cc, hybrid_cc, kernel_cc64 | D-20261121-084453-961e836, -084454-3f1fa54, -084455-b4c1f70 | |
| P192 analysis with all shells and the flag-free estimators | D-20261121-084720-b6aaa6e | `figs/w3_P192_late_profiles.png`, `figs/w3_P192_late_growth.png`, `figs/w3_P192_estimators.png`, `figs/w3_P192_phase.png` |
| lost particles of P192; the same for N128Lc | D-20261121-084720-32f2f10, D-20261121-085120-cbc7ecc | `figs/w3_P192_lost.png` |
| shell energies of P192 and N128Lc | D-20261121-085254-a303729, -085255-a2f2550 | `figs/w3_P192_energy.png` |
| Q16 shells (kernel_cc, hybrid_cc, kernel_cc64) and predictions | D-20261121-085559-5551b3e, -085600-c436f4a, -085602-01fbcdf, -085620-70d2fe8 | |
| **Q16 production run to a/a_i = 16** (edge 6.85 cells out) | **D-20261121-085652-7e189a2** | |

### Results (wave 3)

**Threaded build (R8 against N128Lc, same particle file and deck).** [VERIFIED] Every
statistic is the same: M_ta and the dress identical to all printed digits at every snapshot
(4.8159 and 2.1537 M at a/a_i = 8), the binned profile identical to 1.6e-14 at a/a_i = 3.97
and within 5.1e-4 at 8.00, clump centres of mass apart by 5.5e-6 dx, the same 1763 steps,
first history record within 1e-13. Individual particles are not reproduced: the
difference grows from rounding (1e-15 dx) to 1.8 dx (largest; median 1.3e-8 dx) by a/a_i = 8,
the solver-tolerance differences between thread counts amplified by orbits through the
softened centre [JUDGEMENT on the amplification]. Cost: 0.91 s per step on three threads
against about 3 s on one core of the release build.

**Regression of the extended analysis.** [VERIFIED] On N128Lc the extended `nm_analyze.py`
reproduces all 617 numeric leaves of the wave-2 analysis D-20261115-190541-e27453d to 3.4e-14.

**The reference kernel depends on where the clump sits.** [VERIFIED] With the clump at a cell
centre (the production set-up since wave 2) the mesh force inside one cell is 2 to 8 times the
force with the clump at a vertex (f = g_r r^2/GM = 0.50-0.59 against 0.075 at q = r/dx = 0.5;
overshoot 1.28-1.42 at q = 1); Plummer s_eff = 0.31 dx against 0.61 dx. The wave-2 shells used
the vertex kernel; that did not matter for N128Lc (ball 8.9 cells), it does at dx = 8.9 M:
with the cell-centre kernel the shells follow P192 to 0.7-1.2 % in M_ta at a/a_i = 2-4 (vertex
kernel: 3-7 %).

**P192, the run to a/a_i = 30** (eps = 0.03, nx 192, dx = 8.896 M, R_edge = 36.2 M = 4.1 cells,
last snapshot a/a_i = 29.97). Run value, in brackets the shells with the cell-centre kernel,
hybrid_cc / kernel_cc (masses in M; `nm_analysis.json` of D-20261121-084720-b6aaa6e):

| a/a_i | M_ta | dress | dress/M_ta | M_ta/(M a/a_i) |
|---|---|---|---|---|
| 4 | 2.589 (2.597 / 2.594) | 0.791 (0.800 / 0.805) | 0.306 | 0.647 |
| 8 | 4.826 (4.796 / 4.747) | 2.161 (2.154 / 2.154) | 0.448 | 0.603 |
| 12 | 7.061 (7.021 / 6.887) | 3.541 (3.523 / 3.490) | 0.501 | 0.588 |
| 16 | 9.443 (9.242 / 9.064) | 4.935 (4.901 / 4.807) | 0.523 | 0.590 |
| 24 | 14.550 (13.710 / 13.405) | 7.822 (7.684 / 7.514) | 0.538 | 0.606 |
| 29.97 | 17.024 (17.047 / 16.599) | 10.199 (9.757 / 9.558) | 0.599 | 0.568 |

- Up to a/a_i ~ 12 the run follows the hybrid_cc shells within 0.6 % in M_ta and the dress
  (1.0 % at 4). From a/a_i ~ 14 on it turns around more mass than every shell law (+6.1 % at
  24; all shell laws agree among themselves within 2 % there), and by 29.97 it is back on the
  closed form (17.07 M), while the dress is 4.5 % high [VERIFIED: estimators free of the flag
  history give the same numbers to 0.3 %].
- Cause [VERIFIED by the shell energies, run D-20261121-085254-a303729]: during the first
  expansion (by a/a_i = 1.8, while the ball spans 4-6 cells) the shells in the outer cell of
  the initial ball changed their energy and kept the change afterwards: r0 = 27-32 M (0.5-1
  cell inside the edge) became 3-6 % more bound and turn around up to 8 % early; the
  outermost 0.15 cell (r0 > 33 M) became 14-62 % less bound; deeper shells (r0 < 24 M) changed
  by 0.1-0.3 %. The sign change lies by chance at r_last(30) = 32.9 M, hence the agreement of
  M_ta at 30. The over-energetic edge runs out of the box: 16 462 dust particles (0.70 M, all
  with r0 > 35 M, beyond r_last) leave from a/a_i = 23.6 on; exact gravity keeps every one of
  them inside (run D-20261121-084720-32f2f10). In N128Lc (ball 8.9 cells) the same groups
  change by at most 0.2 %. The mechanism inside the cell (deposit and gather of a sharp edge
  one cell wide, four cells from a cell-centred point mass) is [JUDGEMENT].
- Profile against the self-similar solution, lambda = r/r_ta in [lambda_min, 0.3],
  lambda_min = max(4 dx/r_ta, 0.03): at 29.97 (lambda_min = 0.063, 7 bins) ratios 0.98, 0.94,
  0.88, 0.82, 0.97, 1.38, 1.29 (largest deviation 38 %, rms 20 %); at 16.03 (0.142, 4 bins)
  0.95, 0.89, 0.67, 0.80 (33 %, rms 20 %). The shells, at the same resolution, stay within
  16-24 % (rms 11-14 %). The run's excess at lambda = 0.2-0.25 and its dip at 0.23 (16) come
  from the edge shells above [JUDGEMENT: their orbits are where the deviation is; not
  separated per bin]. Local slope at 29.97: mean -2.41 against the self-similar -2.44 on the
  same bins; least-squares slope -2.27 against -2.53.
- Predictions P: P6 (cost) and parts of P1, P2, P4, P5 hold; the profile (P3), the
  least-squares slope, the masses at 8 and 16, the dress at 30, the momentum and the
  particle count fail (JOURNAL 08:43Z).

**Q16, the run to a/a_i = 16 with the edge repaired as far as nx = 192 allows** (edge
1.2 r_last, R_edge = 31.7 M = 6.85 cells, box +-444 M, dx = 4.625 M, 2580 steps, 1844 s on six
threads; last snapshot a/a_i = 15.96). Run value, in brackets hybrid_cc / kernel_cc shells
(`nm_analysis.json` of D-20261121-092757-34faefa):

| a/a_i | M_ta | dress | dress/M_ta | M_ta/(M a/a_i) |
|---|---|---|---|---|
| 4 | 2.597 (+0.18 / +0.42 %) | 0.795 (+0.47 / +0.84 %) | 0.306 | 0.649 |
| 8 | 4.815 (+0.16 / +0.58 %) | 2.148 (-0.05 / +0.31 %) | 0.446 | 0.602 |
| 12 | 7.047 (+0.17 / +0.62 %) | 3.541 (+0.20 / +0.73 %) | 0.502 | 0.587 |
| 15.96 | 9.302 (+0.80 / +1.28 %) | 4.911 (+0.11 / +0.64 %) | 0.528 | 0.583 |

- [VERIFIED] Every shell inside r_last(16) keeps its energy within 0.4 % (run
  D-20261121-092757-ed934e7); the edge layer outside it changes by -2 to +16 %, ten times less
  than in P192, and the shells just outside r_last that became 1-2 % more bound account for
  the M_ta excess of +0.8 % at 16 [JUDGEMENT on the attribution]. No particle is lost.
- [VERIFIED] Profile against the self-similar solution at 15.96 on lambda = 0.075-0.3 (6 bins):
  0.96, 0.99, 1.04, 0.98, 0.84, 0.93: largest deviation 16 %, rms 7.6 %; the matched shells at
  the same resolution deviate by 15-20 % (rms 10-13 %). Local slope: mean -2.55 against the
  self-similar -2.50 on the same bins, least squares -2.66 against -2.58. At a/a_i = 8 the
  two bins in range ([0.19, 0.3]) are within 3.6 %.
- Inside lambda ~ 0.05 the run (like the shells) lies below the self-similar profile: the seed
  and the mesh softening (4 dx = 18.5 M = 0.075 r_ta) dominate there (`figs/w3_Q16_late_profiles.png`).
- Predictions Q16 (JOURNAL 08:56Z): energy, dress, ratios, profile, slopes, particles and clump
  hold; M_ta at 16 (+0.8 % against the band's +0.5 %) and the step count (2580 against
  2000-2500) fail.
- Figures: `figs/w3_Q16_late_profiles.png`, `figs/w3_Q16_late_growth.png`,
  `figs/w3_Q16_estimators.png`, `figs/w3_Q16_energy.png`.

**Wave-2 dress at a/a_i = 2 (the verifier's finding).** With the cell-centre kernel N128Lc's
dress at 2 lies +1.6 to +1.8 % above the shells instead of +3.1 to +3.3 % (run
D-20261121-092852-a0c75f0): about half of the verifier's 0.5-3.3 % is the reference's
vertex kernel [VERIFIED]; the rest is not explained.

### What D-pre-3 shows

Wording (a), the sheet's "reproduce the r^(-9/4) profile":
- [VERIFIED] The self-similar solution itself is not r^(-9/4) where any run resolves it: its
  local density slope on lambda = 0.06-0.3 is -2.3 to -2.9 with caustic steps (mean -2.44 to
  -2.50 on the bins used here), and -9/4 is its asymptote below lambda ~ 1e-4 (slope of m 0.741
  on [1e-4, 1e-3], 0.705 on [3e-3, 3e-2]; test 2, D-bh-dress-20261115-123813-97afeea).
- [VERIFIED] The runs resolve lambda >= 0.075 (Q16 at a/a_i = 16), >= 0.063 (P192 at 30),
  >= 0.11 (N128Lc at 8), three and a half decades above that regime. On the resolved range the
  run's slope agrees with the self-similar slope (Q16: -2.55 against -2.50), not with -9/4.
- [JUDGEMENT] No uniform-mesh Newtonian run of this set-up can show r^(-9/4): at a/a_i = 30,
  lambda = 1e-4 is r = 0.06 M, inside the softened core and inside r = 2 M; lambda = 1e-4 reaches
  r = 10 M only near a/a_i ~ 1.5e3 (r_ta grows as (a/a_i)^(4/3)). The code has not reached and
  is not claimed to reach r^(-9/4). Wording (a) is not met.

Wording (b), the track's proposal, accepted by the orchestrator (coord/DECISIONS/0021 item 2):
growth against matched shells and the approach to the self-similar m(lambda):
- [VERIFIED] Growth: the turnaround mass and the dress of AthenaK's Newtonian mode follow
  shells with the same (measured, cell-centre) mesh force within 0.2-0.6 % (M_ta) and 0.5 %
  (dress) from a/a_i = 3 to 12 in Q16 (0.8 % at 16), in N128Lc to 0.3 % at a/a_i = 4-8 (wave
  2, re-checked here), and in P192 to 0.6 % up to a/a_i ~ 12; the threaded processor build
  gives the same statistics as the release (R8).
- [VERIFIED] Approach to the self-similar solution: dress/M_ta rises 0.31, 0.45, 0.50, 0.53 at
  a/a_i = 4, 8, 12, 16 toward 0.625, and M_ta/(M a/a_i) falls 0.65, 0.60, 0.59, 0.58 toward
  0.565, as the shells do (Q16); the density profile in units of r_ta is within 16 % (rms 8 %)
  of the seeded self-similar rho(lambda) on lambda = 0.075-0.3 at a/a_i = 16 (Q16), within 23 %
  on 0.11-0.3 at 8 (N128Lc, 0.1-dex bins), and below it inside lambda ~ 0.05.
- [JUDGEMENT] What is not shown: the approach on lambda = 0.01-0.06 that the shells reach by
  a/a_i ~ 30 (RUNS.md line 17). The run to a/a_i = 30 (P192) cannot show it: its turnaround
  shells after a/a_i ~ 12 started within one cell of the edge of the initial ball and had
  their energies changed by -6 to +62 % during the first expansion (VERIFIED, see above), so
  its late masses and profile test the set-up, not the approach. A clean a/a_i = 30 run needs
  the initial ball resolved by about nine cells with its edge at least two cells outside
  r_last(30) (as N128Lc had), which a uniform 192^3 isolated box cannot hold (it needs
  roughly nx = 400 or a refined centre).

### Not done (wave 3)

- No clean run beyond a/a_i = 16; P192's late part is a documented set-up failure, not a result.
- No run with the fixed point mass (`newton_pm_mass`, in release core-v0.4; whether the
  threaded executable of core-v0.5 carries it was not checked); the clump stand-in at a cell
  centre is what ran.
- The mechanism of the edge-layer energy error inside one cell (deposit and gather of a sharp
  edge near a cell-centred point mass) is not separated; the edge of the dust running 5-13 %
  ahead of its closed-form orbit (N128Lc, Q16) is measured, not explained.
- No convergence in dx of Q16 (one resolution); the profile comparison has 6 bins.

### Requests (wave 3)

1. D-bh-dress lead: for stage/G1 C7 (D-pre-3, judged per decision 0021 item 2): evidence is
   N128Lc (wave 2) and Q16 (D-20261121-085652-7e189a2, analysis -092757-34faefa); P192
   (D-20261121-075559-31835c4) is to be cited only with its set-up failure. Erratum for the
   wave-2 claims: the matched shells there used the vertex kernel while the runs had the
   clump at a cell centre; this explains about half of the dress excess at a/a_i = 2 that the
   verifier found (D-20261121-092852-a0c75f0); masses from a/a_i = 3 on are unaffected.
2. core (newtonian_mode.md, sections 5.2 and 6): (a) the near-field kernel of a compact mass
   depends on its position in the cell: at a cell centre the force inside one cell is 2 to 8
   times that at a vertex, Plummer s_eff 0.31 against 0.61 dx (runs D-20261121-084354-f534489,
   -084357-8b3a981, -084407-ffb542d); (b) a uniform ball whose radius is only four cells
   imprints energy errors of -6 to +62 % on the particles in its outer cell during the first
   expansion (D-20261121-085254-a303729); at 6.85 cells -2 to +16 %, at 8.9 cells below 0.2 %
   inside the edge layer. A line on the resolution needed at sharp edges would help other
   tracks with ball set-ups (A, C).
3. core: whether `newton_pm_mass` works in the threaded executable `athena_cpu_omp` of
   core-v0.5; a rerun of Q16 with it would remove the clump's self-interaction (wave-2
   request 1, now served in the release).
### How to rerun (wave 3)

From the worktree root (`wt/D-bh-dress`), package committed, `.venv` present. Each line is one
registered run (`harness/bin/nrpic-run submit --kind scouting --gate G1 --package $P --cores N
[--background] --purpose "..." -- <command>`, written `reg N <command>` below; output
directories as in the run table above):

    P=tracks/D-bh-dress/secondary_infall; S=/data/haiyangw/nrpic/scratch/D-bh-dress
    X=/data/haiyangw/nrpic/scratch/core/exe/core_build-openmp/athena_cpu
    SS=$S/D-bh-dress-20261115-123813-97afeea/selfsimilar_profile.npz
    # the run to a/a_i = 30 (0.7 h on six threads) and to 16 (Q16)
    reg 6 python3 $P/nm_run.py --kind infall --nx 192 --mb 64 --L 854 --aend 30 --edge_fac 1.1 --dtmax 2.0 \
          --shift_cells 0.5 0.5 0.5 --snap_dt 9.612185332430899 --rst_dt 600 --threads 6 --bind --exe $X
    reg 6 python3 $P/nm_run.py --kind infall --nx 192 --mb 64 --L 444 --aend 16 --edge_fac 1.2 --dtmax 1.0 \
          --shift_cells 0.5 0.5 0.5 --snap_dt 9.612185332430899 --rst_dt 300 --threads 6 --bind --exe $X
    # R8: N128Lc on the threaded build (three threads), and the check
    reg 3 python3 $P/nm_run.py --kind infall --nx 128 --L 176 --aend 8 --dtmax 0.5 --shift_cells 0.5 0.5 0.5 --bind --exe $X
    reg 1 python3 $P/nm_threadcheck.py --out '$NRPIC_RUN_DIR' --a N128Lc:$S/D-20261115-171507-d1058a9 --b R8:<R8 dir>
    # cell-centre kernel: one-step field runs (release processor build) and their analysis
    reg 1 python3 $P/nm_run.py --out '$NRPIC_RUN_DIR' --kind field --nx 64 --L 68 --onestep --shift_cells 0.5 0.5 0.5
    reg 1 python3 $P/nm_run.py --out '$NRPIC_RUN_DIR' --kind field --nx 128 --L 68 --onestep --shift_cells 0.5 0.5 0.5
    reg 1 python3 $P/nm_field.py --out '$NRPIC_RUN_DIR' --run cc64:<dir> --run cc128:<dir>
    # matched shells (law kernel or hybrid; kernel_nx128_cc.txt; dx of the run; setup.json of the run)
    reg 1 python3 $P/nm_shells.py --out '$NRPIC_RUN_DIR' --setup <run>/setup.json --law hybrid \
          --kernel $P/kernel_nx128_cc.txt --dx 8.895833333333334 --label P192_hybridcc --snap_dt 9.612185332430899
    # predictions, analysis, diagnostics
    reg 1 python3 $P/nm_predict.py --out '$NRPIC_RUN_DIR' --setup <run>/setup.json --dx <dx> --selfsim $SS \
          --ref hybrid_cc:<shells dir>/nm_shells_<label> ... --at 8 16 30
    reg 1 python3 $P/nm_analyze.py --out '$NRPIC_RUN_DIR' --run P192:<run> --ref P192:hybrid_cc:<prefix> ... \
          --selfsim $SS --late_at 4 8 16 30
    reg 1 python3 $P/nm_lost.py   --out '$NRPIC_RUN_DIR' --run <run>
    reg 1 python3 $P/nm_energy.py --out '$NRPIC_RUN_DIR' --run <run> --groups 20 24 27 29 31 32 33 35 36.3

Wall times: P192 2504 s (2914 steps, six threads); R8 1609 s (three threads); shells with a
kernel 8-22 s, point-mass shells 1.7 h (one core); analyses 20-60 s each.
