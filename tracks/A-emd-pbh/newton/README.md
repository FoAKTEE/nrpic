# Work package `newton` of track A (A-pre-3 under decision 0010)

The Newtonian precursor of the threshold scan. Wave 1 (2026-11-15, morning) wrote the
semi-analytic references, their validation and the scan design; wave 2 (same day,
afternoon) ran the first cases in AthenaK's Newtonian mode (`<particles> pusher =
newton`, release `core-v0.3`, `coord/INTERFACES/newtonian_mode.md`) with the release
processor executable and one card job. No simulation code is written here (decision 0010):
the gravity, deposit and push are AthenaK's; this directory holds references, a particle
file writer that feeds the code, the run driver, the analysis and the results.

## Contents

| File | What it is |
|---|---|
| `PAPER_SETUP.md` | the set-up of arXiv:2605.04487 (homogeneous ball, Zel'dovich deformation, EdS background) with source line numbers |
| `SCAN.md` | design of the scan (sections 1-6, wave 1); results of the first points in the code (section 7) and the proposed range of the full-relativity scan (section 8, wave 2) |
| `tophat.py`, `ellipsoid.py` | references: the cycloid through any (R, dR/dt); the cold homogeneous ellipsoid (isolated, embedded, added placements; end-point SR estimate; hoop proxy) |
| `validate.py`, `scan_refs.py` | wave 1: checks P1-P7 of the references; reference tables over (e, p) |
| `compare_snapshots.py` | wave 1: semi-axes from AthenaK snapshots; self-test on synthetic snapshots |
| `make_deformed_ball.py` | wave 2: writes the Zel'dovich-deformed homogeneous ball in the existing particle format (`.nrp`) with a JSON of the references of the sampled ball; the work-around for what the generators lack (below) |
| `newton_campaign.py` | wave 2: the cases (top-hat, scan, card), particle files, AthenaK command lines (release processor executable, `problems/newton/isolated.athinput` plus overrides), runs them in parallel; `--prepare-only` writes the list of a card batch |
| `analyze_newton.py` | wave 2: reads `newton.newton.hst` of each case; radius or semi-axes from the second-moment tensor about the centre of mass; turnaround, infall and collapse times against the cycloid; first collapse, axes, hoop ratio against the isolated ellipsoid; tables and figures |
| `gr_range.py` | wave 2: the proposed range of the full-relativity scan (hoop amplitude, ball-radius limit, SR delay, infall speed, seeds) |
| `register.py` | wave 2: registers a run by hand (manifest under `../runs/<run_id>/`) when `harness/bin/nrpic-run` refuses (see Requests) |
| `run_and_register.py` | wave 1: registers runs of the reference scripts |
| `figs/`, `tables/` | figures and tables copied from the registered runs (wave-2 files are named `*newton*` and `gr_scan_range.csv`) |
| `manifests/` | wave-1 copies of manifests (the ignore rule is fixed on main; manifests now live in `../runs/`) |
| `JOURNAL.md` | predictions before each test and outcomes after it (entries 1-4 wave 1, 5-8 wave 2) |

## What the particle generators lack for the deformed ball (wave 2, exact)

Neither generator of the repository can write the initial data of the scan:

1. `problems/newton/make_ic.py` (core's Newtonian test generator) has the models `point`,
   `ball`, `wave` (line 46). Its `ball` is a lattice ball at rest with an optional uniform
   velocity and rigid rotation, `u = velocity + omega x (x - c)` (line 84). It lacks:
   (a) an anisotropic position map x_i = a0 (1 - a0 lambda_i) xi_i (the Zel'dovich
   deformation); (b) a velocity field linear in position with a diagonal, non-isotropic
   matrix, v_i = H0 a0 (1 - 2 a0 lambda_i) xi_i (Hubble flow plus peculiar velocity); a
   rigid rotation is antisymmetric and a uniform velocity is constant, so neither can
   express it; (c) parameters in (delta_L, e, p) or (alpha, beta, gamma) with the start
   a0 = 1/(2 alpha) and t0 = t_k a0^(3/2); (d) a random rotation of the lattice against the
   deformation axes; (e) the volume radius of the sampled lattice ball in the metadata,
   which the references need (it moves the cycloid collapse time by +0.31 per cent for
   lattice spacing 0.05, JOURNAL entry 5); (f) an optional background shell with Hubble
   velocity and a species id (SCAN.md section 1; not needed for the first points).
2. `problems/ic/make_ic.py` (relativistic generator) has `os`, `st`, `prolate`, `jeans`
   (line 67); its ball sampler `python/nrpic/sampling.py` sample_os (line 117) is Oppenheimer-Snyder dust at rest (u_i = 0). For the
   full-relativity deformed ball it lacks the same map and velocities, the covariant u_i
   of the A-pre-1 slicing, and the constraint solve after the deformation (core's wave-2
   initial-data work, decision 0010 item 4).

Work-around in this directory: `make_deformed_ball.py` writes the existing `.nrp` format
(`python/nrpic/io.py` write_nrp) with (a)-(e) and centring (centre of mass and net
momentum removed). It feeds the code; it does not simulate. The smallest change to
core's generator that would replace it: two options of `ball`, `--axes S1 S2 S3`
(x = c + S xi) and `--vgrad D1 D2 D3` (v = D xi), plus `--rotate SEED` and the volume
radius in the JSON (Requests).

## Rerun

From the worktree root (`.venv` of the worktree: numpy, scipy, matplotlib):

    # processors (one core per case; J cases at once); output in $NRPIC_RUN_DIR or --out
    .venv/bin/python tracks/A-emd-pbh/newton/register.py local --purpose "..." --cores 6 \
        -- .venv/bin/python tracks/A-emd-pbh/newton/newton_campaign.py --campaign tophat --jobs 6
    .venv/bin/python tracks/A-emd-pbh/newton/register.py local --purpose "..." --cores 5 \
        -- .venv/bin/python tracks/A-emd-pbh/newton/newton_campaign.py --campaign scan --jobs 5
    # card: particle files and batch list, then one Slurm job (25 min limit)
    .venv/bin/python tracks/A-emd-pbh/newton/register.py local --purpose "..." \
        -- .venv/bin/python tracks/A-emd-pbh/newton/newton_campaign.py --campaign card --prepare-only
    .venv/bin/python tracks/A-emd-pbh/newton/register.py batch --purpose "..." \
        --list <prepare run dir>/batch.list --wall 00:25:00
    .venv/bin/python tracks/A-emd-pbh/newton/register.py finish <batch run id>
    # analysis and range (seconds)
    .venv/bin/python tracks/A-emd-pbh/newton/register.py local --purpose "..." -- \
        .venv/bin/python tracks/A-emd-pbh/newton/analyze_newton.py \
        --tophat <tophat run dir> [<card run dir>] --scan <scan run dir> [<card run dir>] \
        --prep <prepare run dir> --out <dir>
    .venv/bin/python tracks/A-emd-pbh/newton/gr_range.py --results <dir>/newton_results.json --out <dir>

With `harness/bin/nrpic-run submit --launcher local` instead of `register.py local` when the
worktree is clean (the cost run was registered that way). Wave-1 reruns: `run_and_register.py`.

## Runs (wave 2)

| Run id | What | Resources |
|---|---|---|
| A-20261115-152758-1579711 | cost per cycle, 30 cycles of five cases (registered with `nrpic-run`) | 5 cores, 428 s |
| A-emd-pbh-20261115-153409-dc27b98 | top-hat: mesh {32,64,128}^3 x lattice {0.1,0.05,0.025}, cfl check (10 cases) | 6 cores, 2301 s |
| A-emd-pbh-20261115-153415-dc27b98 | scan: 13 cases (e, p, amplitude, rotation, 64^3, lattice 0.05) | 5 cores, 4023 s |
| A-emd-pbh-20261115-153424-dc27b98 | particle files and batch list of the card job (no simulation) | 1 core, 3 s |
| A-emd-pbh-20261115-153437-dc27b98 | card: top-hat 64^3 and 128^3, e = 0.2, each 2.1e6 particles (Slurm 4435) | 0.169 card-hours |
| A-emd-pbh-20261115-164420-4528861 | final analysis (tables, figures); supersedes -161309-9d3703a, -161537-aa788d9, -162554-d32d331, -164220-dd9fec7 | 1 core, 24 s |
| A-emd-pbh-20261115-164757-b8bc9a3 | range of the full-relativity scan; supersedes -164450-4528861 | 1 core, 5 s |
| A-emd-pbh-20261115-161253-b8c1dc9 | failed analysis (option the script did not have); kept on record | 1 core |

All except the first registered by hand with `register.py` (Requests). Outputs under
`/data/haiyangw/nrpic/scratch/A-emd-pbh/<run id>/`, each case in its own directory with
`ball.json` (parameters and references), `case.json` (command, wall time) and the AthenaK
output.

## What was established (wave 2)

1. **What the generators lack for the deformation** is listed above; the work-around
   `make_deformed_ball.py` feeds the code with the existing `.nrp` format. The lattice ball
   must carry its own volume radius into the reference (0.31 per cent in the top-hat
   collapse time at lattice spacing 0.05; JOURNAL entry 5).
2. **Spherical top-hat against the cycloid** (runs -153409-dc27b98, card -153437-dc27b98;
   SCAN.md section 7): turnaround, radius, infall time and softened collapse converge at
   second order in the mesh; at 128^3 with 2.7e5 particles t_ta +7.2e-4, R_max +4.3e-4,
   t(R = 0.25 R_max) +8.4e-4, collapse +2.6e-4; 2.1e6 particles change them by 1e-5; the
   lattice must stay below about one cell or the particles dominate the error (3.4e4: 2e-3;
   4.2e3: up to 1.5e-2); the step is not limiting (8e-5); energy 9.5e-5.
   `figs/fig_newton_tophat.png`, `fig_newton_tophat_conv.png`, `tables/newton_tophat.csv`.
3. **First scan points against the isolated ellipsoid** (run -153415-dc27b98, card): at
   128^3 with 2.7e5 particles the first collapse is along the predicted axis in all 14 runs
   and its time is within 2.2e-4 to 6.3e-4 of the reference for e = 0.05-0.3 (1.5e-3 for
   the spindle p = -e), the other axes within 1.2e-3, the hoop ratio within 6.1e-4, the
   second collapse within 6.4e-4; second order in the mesh; converged in particle number
   (9e-6); independent of the lattice orientation (4e-6); the three amplitudes agree to
   5e-7 (scale freedom of the code). The Newtonian hoop amplitudes from the code: 0.3597,
   0.5925, 0.8547, 0.9685 (e = 0.05-0.3, p = 0), 0.9194 and 0.8636 (e = 0.2, p = +-0.2).
   `figs/fig_newton_scan_*.png`, `fig_newton_snap_*.png`, `tables/newton_scan.csv`.
4. **Energy through the crossing** (refuted prediction, JOURNAL entry 8): conserved to
   <= 1.9e-4 up to 0.9 t_1, but off by 1e-3 to 3e-2 at the crossing and by up to 5e-2 after
   the third collapse; cause not established. The times and axes are unaffected.
5. **Proposed range of the full-relativity scan** (run -164757-b8bc9a3; SCAN.md section 8,
   `tables/gr_scan_range.csv`, `figs/fig_newton_gr_range.png`): seeds delta_L,th x {0.5,
   0.7, 1, 1.4, 2} for e in {0, 0.05, 0.1, 0.2, 0.3} and p = +-0.1 at e = 0.2; at the hoop
   amplitude the Newtonian infall speed exceeds c (1.01-1.24 c; spindle 2.3 c) and SR
   delays t_1 by 6-14 per cent, so the hoop line marks the region, not the threshold;
   resolution dx = M/9 to M/21 over the patch at the start for the accuracy reached here;
   >= 2.7e5 lattice particles per patch; a run needs >= 3 t_0 from the paper's start; the
   expanding ball holds the hoop amplitude with a 1.5 R_L shell only for e <= 0.1 and a
   start later than the paper's (supports decision 0013).
6. **Cost**: processors 2.8 s per cycle at 128^3 with 2.7e5 particles (9.5 s with 2.1e6,
   13.3 s at 256^3); card 0.37 s per cycle at 128^3 with 2.1e6 particles. This package used
   0.169 card-hours (of the 0.5 allowed) and 7.4 core-hours.

## What was established (wave 1, unchanged)

1. Top-hat reference: the cycloid through Zel'dovich data matches direct integration to
   5e-12 in the turnaround and collapse times (run A-emd-pbh-20261115-113103-9832afd).
2. Ellipsoid reference: coefficients equal the spheroid closed forms to 1.3e-13; spherical
   limit equals the cycloid to 1e-11; plane limit converges to Zel'dovich as 10^-k; the
   Zel'dovich hoop of 1609.01588 reproduced to 3e-15; the problem with the paper's start
   is scale free to 1e-13 (same run).
3. The start convention of 2605.04487 reproduces its four printed start times; its two
   printed event times are matched to +0.9 and +0.1 per cent only by the "added" placement
   [JUDGEMENT on the paper's code; `PAPER_SETUP.md`, JOURNAL entry 3].
4. Newtonian hoop line delta_L,th = h_1 delta_L (isolated, p = 0): 0.089 at e = 0.01,
   0.359 at 0.05, 0.592 at 0.1, 0.855 at 0.2, 0.968 at 0.3 (run
   A-emd-pbh-20261115-113152-cd9539e).
5. End-point SR kinematics delays the first collapse by 0.7-0.9, 1.4-1.8, 4-5 and 13-17
   per cent at delta_L = 0.05, 0.1, 0.3, 1 (same run, `tables/sr_estimate.csv`).
6. The snapshot analysis recovers the first-collapse time of a synthetic run to 1.2e-5
   (run A-emd-pbh-20261115-113822-87cba08).

## Open

- Not run: the shell series (block D of section 2), the "added" placement and the SR
  push (the mode has neither; acceptance (iii) of SCAN.md section 5), refined meshes in
  the Newtonian mode (a trial in core's interface, not verified), 256^3 (13 s per cycle
  on a processor; 0.5-1 card-hour per run estimated, not measured), the virialised state
  (needs a larger box: e = 0.05 lost 0.64 per cent of its mass through the faces after the
  third collapse, and the rotated lattice: the aligned one leaves a cubic pattern).
- The energy excursion at the crossing (JOURNAL entry 8, (g)) is not explained.
- The wave-1 open points stand: the appendix cases of 2605.04487 under the "added" reading
  [TO VERIFY]; the end-point SR model is an estimate; the paper's softening is not modelled.
- The vertex estimator of t_1 was corrected after an interim analysis (first minimum only);
  the extrapolation estimator, independent of it, agrees to 2.4e-4 at 128^3.

## Requests

- core (`problems/newton/make_ic.py`): two options of `ball`, `--axes S1 S2 S3` (x = c + S xi)
  and `--vgrad D1 D2 D3` (v = D xi), plus `--rotate SEED` and the volume radius of the
  lattice ball in the JSON; or adopt `make_deformed_ball.py` (formulas and checks here).
  For the full-relativity deformed ball: the same map with covariant u_i on the A-pre-1
  slicing and the constraint solve after the deformation (decision 0010 item 4).
- core (Newtonian mode): optional external acceleration -(4 pi/3) G rho_b(t) r for the
  "added" placement and an optional SR push u = gamma v (acceptance (iii), comparison with
  2605.04487); a look at the energy excursion when particles cross in a sheet thinner than
  a cell (W of the particle sum, column 6 of `newton.hst`): numbers in JOURNAL entry 8.
- orch (harness): `nrpic-run submit` refuses whenever any helper of the same owner has an
  untracked file in the shared worktree, so parallel helpers cannot use it; every run of
  this package after the first was registered by hand with `register.py` (same fields,
  `notes` says why). Proposed: check only the paths the run's inputs and command name, or
  allow `--allow-untracked` for files outside them.
- A lead: take section 8 of SCAN.md into the scope of the threshold scan (seeds, shapes,
  resolution, run length); decide whether the ball runs at e <= 0.1 start later than the
  paper's start (exact ellipsoid state) to fit a 1.5 R_L shell.
