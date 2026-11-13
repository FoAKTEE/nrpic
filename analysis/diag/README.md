# Diagnostic figures

All scripts use `python/nrpic/figstyle.py`, write a PDF and a PNG to `figs/`, print the
numbers they plot, and accept `--out NAME` (file name without extension, relative to
`figs/` or absolute). Run directories may be absolute or relative to the repository
root; a run argument is `<label>=<rundir>` (the label may contain `=`).

## Scripts

| script | shows | call |
|---|---|---|
| `common.py` | readers: `read_nrpic_hst`, `read_horizon`, `read_traj`, `read_curv_slice`, `read_snapshot` (unchanged) plus `read_athena_hst`, `read_curv_hst`, `read_traj_tagged` (de-duplicated per tag), `snapshot_files/times`, `initial_radius_by_tag`, `parse_cli`, `ks_schwarzschild`, `inv_sym3`, `floor_log` | imported |
| `mesh_static.py` | circular orbit (r = 8 M) in the mesh-sampled Kerr-Schild metric: orbit, r - 8M, E and L_z errors against the exact metric, deposition identity | `python3 mesh_static.py [rundir]` |
| `dep_smr.py` | deposition identity residuals for E and S_x,y,z, all variants, exact zeros on a stated floor | `python3 dep_smr.py [label=dir ...]` (default: the six runs in `runs/dev/dep_smr`) |
| `curvature.py` | Kretschmann scalar of a Brill-Lindquist puncture against 48 M^2/R^6: I(r), relative error (r), error maps in the plane | `python3 curvature.py [ng2=dir ng4=dir]` (default `runs/dev/curv/ng2`, `ng4`) |
| `bench.py` | Z4c zone-cycles/s against MeshBlock size and nghost | `python3 bench.py [benchdir]` |
| `os_history.py` | dust collapse: central lapse and density against the analytic solution, rest mass, horizon mass (pre-existing; now skips runs without output and has the lapse legend at lower left) | `python3 os_history.py label=dir ... --out NAME` |
| `os_snapshots.py` | particles projected onto x-z at six times, coloured by initial radius (by tag), horizon circle | `python3 os_snapshots.py label=dir ... [--times t1,..] [--base os]` |
| `os_constraints.py` | (int H^2 dV)^1/2, (int M_i M^i dV)^1/2 and number of MeshBlocks against t, first horizon marked | `python3 os_constraints.py label=dir ... [--base os]` |
| `cluster_history.py` | clusters (basename `st`): central lapse vs equilibrium, Lagrangian radii 10..90 % about the centre of mass (median thick) vs equilibrium, particle and mass losses, constraint norms, centre of mass, momentum-sum drift | `python3 cluster_history.py label=dir ... [--yc Y] [--every K]` |
| `tracers.py` | tracers around an evolved black hole (`punc.traj.bin`, `punc.trajmet.bin`): x-y and x-z orbits, L_z/L_z(0)-1, E/E(0)-1 with E = alpha W - beta^i u_i from the recorded metric, areal radius | `python3 tracers.py [label=]rundir [--base punc] [--tags 0,1]` |
| `synth_tracers.py` | test aid: writes `punc.traj.bin`/`punc.trajmet.bin` for the six tracers of `tracers_single.athinput` integrated in static isotropic Schwarzschild | `python3 synth_tracers.py outdir` |
| `snapshots_3d.py` | row of 3D scatter panels coloured by initial radius, common view, scale bar at true length; `--cut` removes the near half, `--common` one scale | `python3 snapshots_3d.py rundir --times t1,t2,.. [--elev --azim --cut --common]` |

## Task-1 figures (inspected by eye)

**`figs/mesh_static.png`** (`runs/dev/mesh_static`, 3002 trajectory records, t = 300 M,
2.11 orbits). The orbit lies on the exact circle; r - 8M is a single epicycle of
amplitude 5.8e-4 M (0 to 1.15e-3 M) with the Schwarzschild radial period
2 pi / [Omega (1 - 6M/r)^1/2] = 284 M, i.e. the exact initial data are very slightly
non-circular in the interpolated metric, with no secular drift; the small kinks sit
where the orbit runs almost parallel to the grid lines (phi = 2-10 deg after each
axis). |E/E_exact - 1| <= 8.4e-7 and |L_z/L_z,exact - 1| <= 5.1e-6, both cycle-to-cycle
interpolation noise without drift; phase error -1.6e-3 rad at the end. The deposition
identity holds to 1.0e-15 (283 of 301 records exactly 0). Pusher: <= 5 iterations, none
unconverged.

**`figs/dep_smr.png`** (six variants). GPU runs (nocap, cap1, cap0, cap1_filt2;
82 records to t = 8): E residual exactly 0 in every record; S_i residuals <= 5e-15
relative to sum m u_i, ~25 % of records exactly 0, all below the roundoff scale
eps sum m|u_i| / |sum m u_i| = 1.5-3e-14 (dotted). CPU adaptive-cloud-level runs
(cpu_adapt, cpu_adapt_min1_max2; 31 records to t = 3): E residual up to 4.1e-13 and
5.4e-14, S_i up to 2.3e-12 and 5.3e-13, never 0 - two to three orders above the GPU
runs and above the roundoff scale. cap1 and cap1_filt2 have bit-identical integral
columns: the history integrals are summed before the filter (see "Issues").

**`figs/curvature_puncture.png`** (rerun here: `runs/dev/curv/ng2`, `ng4`, CPU build
`.work/build_check`, t = 0, dx = 0.25 M). The plane is y0 = 0.125 M (recovered from
sqrt(gamma) = psi^6 and from alpha = psi^-2, both 0.125000000000). Away from the puncture
and the outer boundary the median relative error is 2.7e-3 (r = 4-6 M) for nghost = 2
(2nd-order FD) and 1.2e-6 for nghost = 4 (6th order), 1.4e-7 beyond 6 M. Within about
1 M of the puncture the error is O(1-50) for both (I up to 40 against an exact maximum of
0.75), and the cells within nghost cells of the outer boundary have errors up to 0.94
(ng2) and 1.4 (ng4): the error maps show the boundary frame (1 cell wide for ng2, 3 for
ng4). Consequently the `max|I|` column of `curv.hst` (17.5 and 39.6) is a puncture
artefact, not a physical maximum.

**`figs/z4c_bench.png`** (`runs/dev/bench`, one A100, 128^3 cells, 20 cycles).
nghost = 4: 1.52, 1.86, 2.00, 1.97 x 10^7 zone-cycles/s for MeshBlocks of 16, 32, 64,
128^3; nghost = 2: 2.70 and 3.48 x 10^7 for 16 and 32^3 (no larger blocks run). The
rate from cycles 5-20 alone agrees within 0.3 %, so set-up is not included.

**`figs/os_history.png`** (static mesh `runs/dev/os_smr_gpu` to t = 10; AMR with the
cloud at the finest level `runs/os/amr_n26` to t = 25.9, cancelled before tlim = 30;
added for comparison `runs/os/amr_n26_cap3`, cloud capped at level 3, to t = 16.1;
`runs/os/amr_n26_adapt` has no output yet - its job `os_adapt` is queued (4104 at
04:12) and its `athena.log` link points to a file not yet written; rerun the three OS
scripts with it once it has data). The central lapse follows the Staley bound
to tau_c = 3.3 and then stays far above it (0.66 at tau_c = 5 against 0.35) in all
runs. E_c follows the cycloid within 0.3 % in the finest-level AMR run up to
tau_c = 5 (5.5 % low at tau_c = 5.7), while the runs with cloud size h are high: static
4-8 %, capped 9-12 % at tau_c = 5-7. At t = 7.29 (tau_c = 5.73) the finest-level run drops from E_c/E_0 = 1.47 to
0.42, exactly when the mesh grows 288 -> 344 MeshBlocks (a level with dx = h/4 appears
at the centre, finer than the particle lattice); a second drop at t = 15.53 (344 -> 400).
The capped run shows neither drop. Particles are excised from t = 19.10, all
9328 (rest mass 1.1687) by t = 19.76. The horizon appears at t = 16.33 with
M_AH = 0.962, peaks at 0.977 (t = 16.7) and then decreases to 0.969 at t = 25.9.

**`figs/os_snapshots.png`** (same runs, t = 0, 4, 8, 11, 15, 19). The lattice contracts
smoothly and stays spherical: on the outer shell the ratio r/r_0 differs by 2 % between
particles on the axes and on the diagonals at t = 19 (0.092 vs 0.090), and r/r_0 spans
0.088-0.102 over all particles. From t ~ 8 the projected lattice columns smear radially
(non-homologous coordinate motion). At t = 19 the whole cloud (max r = 0.38 M) lies
inside the horizon (mean coordinate radius 1.10 M, circle).

**`figs/os_constraints.png`**. ||H|| starts at 0.31 (the particle lattice against the
smooth table data) in all runs. Both AMR runs double ||H|| and ||M|| at the first regrid
(t = 0.64, 232 -> 288 MeshBlocks) relative to the static mesh (0.25 vs 0.13 at t = 3).
The finest-level run jumps by x6 at t = 7.29 (to 2.0), coinciding with the E_c drop;
the capped run has no jump but reaches the same level (~1) by t = 10. ||H|| peaks at
2.3 at t = 17.5 (after the horizon) and decays to 0.92 by t = 25.9.

## Tools of task 2, and what they were tested on

- `cluster_history.py`: on the live run `runs/st/yc0819_dev` (y_c = 0.819, N = 10^4;
  figure `figs/cluster_history_yc0819_dev.png`, data to t = 221 M at the time of
  writing, rerun it for newer data) and, to exercise excision and empty snapshots, on
  the dust-collapse runs with `--base os` (`figs/cluster_history_test_os.png`).
  Initial Lagrangian radii agree with `STModel(0.819).Finv` to 1e-3 M and alpha_c(0)
  = 0.80939 with the model's 0.80908.
- `tracers.py`: on `runs/geodesic/kerr_mesh/inc_mid_mesh_dx0.25` (`--base geo`, one
  particle, Kerr a = 0.9 on the mesh: |dE/E| <= 3.6e-9, |dL_z/L_z| <= 8.2e-6;
  `figs/tracers_test_kerr_mesh.png`) and on synthetic data from `synth_tracers.py`
  (six particles, static isotropic Schwarzschild; recovers R = 7.0417, 9.0312, 11.025
  and E = 0.945053, 0.952697, 0.959479 of the input comments, conservation 1e-11;
  `figs/tracers_test_synthetic.png`). No `punc` run exists yet (job `tracers1` queued);
  a CPU rerun was tried and stopped (about 80 s per cycle).
- `snapshots_3d.py`: on `runs/os/amr_n26` (`--cut`, `figs/snapshots_3d_test_os_amr_n26.png`)
  and `runs/st/yc0819_dev` (`--common`, `figs/snapshots_3d_test_st.png`).

## Issues found while making the figures

- History integrals int_E, int_S_i of `<base>.nrpic.hst` are accumulated in the
  deposit kernel before `NrpicFilterSources`, so the filter's conservation is not
  tested (cap1 and cap1_filt2 agree bit for bit).
- The adaptive-cloud-level CPU runs conserve the deposit only to 1e-13..1e-12, the GPU
  runs (older build `build_gpu_v2`, no adaptive level) to roundoff.
- Finest-level deposition on cells finer than the particle lattice (amr_n26 after
  t = 7.29) produces a factor-3.5 drop of the central density and a x6 jump of ||H||.
- Apparent-horizon mass of amr_n26 is 2.3-3.8 % below M_ADM and decreases after
  its peak (0.977 at t = 16.7 to 0.969 at t = 25.9; finder settings
  `flow_iterations = 200`, `mass_tol = 1e-3`).
- `curv.hst` from `.work/build_check` writes max E = -1.797693134862316e+308 (parsed as
  -inf) with varying garbage coordinates when nothing is deposited; the guard in
  `nrpic_curvature.cpp` is newer than that executable (source 03:41:26, binary
  03:40:56). The slice file does not record the plane position y0.
- Tracer 4 of `tracers_single.athinput` ("eccentric, 0.8 L_circ") has L = 3.29 M <
  2 sqrt(3) M, so it plunges (synthetic integration: reaches alpha = 0.05 at t = 131 M).
- The dev cluster `yc0819_dev` (stable side; binding-energy maximum at y_c = 0.680)
  breathes strongly: alpha_c 0.8094 -> 0.8376 (t = 112) -> 0.8135 (t = 223), r_50 up
  to +16 %; whether this is the response to `vpert = 0.01` needs a vpert = 0 control.
  Its centre of mass drifts by 0.15 M, as expected from the uncorrected initial net
  momentum sum m u = (-1.3, 4.0, 9.0) x 10^-4.
- Format gaps: `docs/FORMATS.md` documents only `.nrp` and `.tab`, none of the run
  outputs (`nrpic.hst`, `traj.bin`, `trajmet.bin`, `part.*.bin` with its ncycle field,
  `curv.*`); CPU run directories of `dep_smr` keep neither the command line nor the
  input, and the GPU copies of `deposit_smr.athinput` predate the current file; the
  z4c "norm2" columns are unnormalised integrals of the squares; the run with
  tlim = 300 ends with a 2.8e-13 M step, which leaves two trajectory records 3e-13 M
  apart.
