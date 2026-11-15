# periodic_z4c: the spacetime solver alone in a periodic box (B-pre-1)

Helper package of owner B-emd-gw. The Z4c solver of this repository's AthenaK, release
processor executable `/data/haiyangw/nrpic/.work/build_cpu_c1/src/athena` (built from
`main`; no build here), in periodic vacuum boxes: a linear gravitational wave over ten
box crossings at four resolutions, the gauge wave of the Apples-with-Apples suite, and a
record of the lapse and shift options, linear (against an exact linearized solution)
and nonlinear (gauge shocks). Predictions and outcomes: `JOURNAL.md`. Results: section
"Results" below (filled from `tables/*.md`).

## Contents

| Path | What |
|---|---|
| `inputs/lw_x.athinput` | TT wave along x (`z4c_linear_wave`), thin box N x 4 x 4, production numerics of the cosmology runs |
| `inputs/lw_3d.athinput` | same wave in a cubic box [-1/2,1/2]^3: metric dumps for gw_diag, and the oblique-data check |
| `inputs/gauge.athinput` | vacuum box started from a file through `nrpic_cosmo` (`id = file`): gauge wave and pure-gauge data |
| `make_cases.py` | writes the initial-data files (`scratch/B-emd-gw/ids/`) and the case lists `cases/*.json` |
| `launch.py` | runs a case list on processors, one registered run per case (manifest in `tracks/B-emd-gw/runs/<run_id>/`, output in `scratch/B-emd-gw/<run_id>/`) |
| `analysis/athena_dumps.py` | readers: `read_tab` (1D tables), `read_rst` (restart files, the only double-precision full-mesh dump), `read_bin` (float32 mesh output), `z4c_to_adm` |
| `analysis/refsol.py` | exact and semi-analytic references: TT wave and the generator's polarization tensor; the gauge wave in proper-length coordinates; the linearized lapse/shift system; writer of the `NRCOSMO1` file |
| `analysis/predict_lw.py` | prediction of the TT-wave errors from the Fourier symbol of the code's stencils, dissipation and RK4 |
| `analysis/ana_lw.py`, `ana_check3d.py`, `ana_awa.py`, `ana_gauge.py`, `ana_dump.py` | analyses; write `figs/` and `tables/` |
| `figs/` | figures (PDF and PNG, project style `python/nrpic/figstyle.py`) |
| `tables/` | tables of the results (`.md` for reading, `.json` for scripts) |
| `JOURNAL.md` | predictions written before each set of runs, outcomes after |

## How to rerun

```
cd tracks/B-emd-gw/periodic_z4c
python3 make_cases.py                            # id files and case lists
python3 launch.py cases/lw_x_prod.json -P 4      # one set; others: lw_x_ref, lw_x_nodiss,
                                                 # lw_x_roundoff, lw3d_check, lw3d_dump,
                                                 # awa_gw, gauge_lin, gauge_nl, gauge_nl_res
cd analysis
python3 ana_lw.py; python3 ana_check3d.py; python3 ana_awa.py; python3 ana_gauge.py; python3 ana_dump.py
```

The analyses find the runs through the manifests (latest finished run of each case
name). One core per run (Kokkos Serial build), about 1.4e4 zone-cycles per second.

## Metric dumps for the gw_diag package

Run `lw3d_dump_N32`, run id **B-emd-gw-20261115-113218-0ea0f74** (manifest
`tracks/B-emd-gw/runs/B-emd-gw-20261115-113218-0ea0f74/manifest.json`), output directory
`/data/haiyangw/nrpic/scratch/B-emd-gw/B-emd-gw-20261115-113218-0ea0f74/`:

- Problem: TT wave `z4c_linear_wave`, k = (1, 0, 0) cycles per unit length, A = 1e-6,
  box [-1/2, 1/2]^3, 32^3 cells, one MeshBlock, ng = 4, conformal-time lapse, zero shift;
  t = 0 to 2 (two periods), dumps every 1/16 (33 dumps).
  Exact solution: `refsol.tt_exact(x, y, z, t, 1, 0, 0, 1e-6)`:
  gamma_yy - 1 = -(gamma_zz - 1) = -A sin(2 pi (x - t)), K_yy = -K_zz = -pi A cos(...)
  (K_ij = At_ij at first order).
- Minimal use:
  ```
  import sys; sys.path.insert(0, "tracks/B-emd-gw/periodic_z4c/analysis")
  import athena_dumps as ad, refsol as rs
  d = ad.read_rst(".../rst/lw3.00016.rst")       # t = d["time"], arrays [z, y, x]
  adm = ad.z4c_to_adm(d)                          # adm["g_yy"], adm["K_yy"], ...
  ```
- `rst/lw3.NNNNN.rst`: restart files, double precision, all 22 Z4c variables with ghost
  cells. Read with `athena_dumps.read_rst(path)` (arrays [z, y, x], cell centres in
  `d["x"], d["y"], d["z"]`); ADM metric and curvature with `athena_dumps.z4c_to_adm(d)`.
- `bin/lw3.{z4c,adm,con,weyl}.NNNNN.bin`: AthenaK binary output, float32. Use only for
  fields that vanish in the background (off-diagonal metric, At_ij, K_ij, constraints,
  psi4): float32 cannot hold 1 + 1e-6. `athena_dumps.read_bin(path)`.
- Weyl scalar: `weyl_rpsi4`, `weyl_ipsi4` of AthenaK use a tetrad built from the radial
  direction about the origin (`athenak/src/z4c/z4c_calculate_weyl_scalars.cpp` lines
  254-273); for a plane wave the result depends on the position (`figs/dump_check.png`:
  Re psi4 nearly vanishes where the wave moves towards the origin). Zero in the first
  dump (computed only after the first step, at `waveform_dt`).
- Validation: `analysis/ana_dump.py`, `figs/dump_check.png`, `tables/dump_check.json`.
- Why an axis-aligned wave: the generator's polarization tensor is not transverse for
  oblique k (Results, item 2). An oblique wave needs the fix requested below.

## Results

Labels as in the brief: [VERIFIED] = read from the code or measured in a run named
here; [JUDGEMENT] = my inference. Every number below has its run id in the table cited.

1. **Linear TT wave along x, ten crossings, measured orders** (`tables/lw_x.md`,
   `figs/lw_x_history.png`, `figs/lw_x_convergence.png`) [VERIFIED].

   | numerics | N | amplitude error | phase error (rad) | order amp | order phase |
   |---|---|---|---|---|---|
   | production (ng 4, Courant 0.25, KO 0.5, conformal lapse) | 16 | -1.72e-4 | -2.49e-4 | | |
   | | 32 | -1.49e-6 | -6.25e-6 | 6.85 | 5.32 |
   | | 64 | -1.48e-8 | -2.63e-7 | 6.65 | 4.57 |
   | | 128 | floor (roundoff, item 4) | -8.6e-8 | | |
   | upstream input (ng 3, Courant 0.3, KO 1, 1+log + Gamma driver) | 16 | -8.79e-3 | -8.29e-3 | | |
   | | 32 | -2.84e-4 | -5.23e-4 | 4.95 | 3.99 |
   | | 64 | -8.92e-6 | -3.26e-5 | 4.99 | 4.00 |
   | | 128 | -2.43e-7 | -1.18e-6 (floor) | 5.20 | |

   Up to 64 cells every error equals, to better than 1 percent (10 percent for the
   production phase at 64), the prediction from the Fourier symbol of the code's
   stencils, Kreiss-Oliger term and RK4 (`analysis/predict_lw.py`, written before the
   runs): amplitude error from the dissipation (order 2 ng - 1 = 7 and 5), phase error
   from the sixth- (fourth-) order second derivative and RK4 (order 4 at fine grids).
   Without dissipation (production, N = 32, 64) the amplitude error is RK4's,
   -1.21e-7 and -3.5e-9 (order 5.1). The lapse and shift are not excited at first
   order, so the gauge does not matter here.

2. **The oblique data of `z4c_linear_wave` are not a gravitational wave**
   (`tables/lw3d_check.json`, `figs/lw3d_check.png`, `JOURNAL.md`) [VERIFIED]. The
   polarization tensor (`athenak/src/pgen/tests/z4c_linear_wave.cpp` lines 107-112) has
   the wrong sign of a_xy and a_yz: it is transverse only for k along an axis. For
   k = (1,1,1), the default of `athenak/inputs/tests/linear_wave_z4c.athinput`, the
   initial data violate the Hamiltonian and momentum constraints at first order:
   integral of H^2 = 1.385e-9 and of M^2 = 1.558e-9 at A = 1e-6 (predicted from the
   tensor: 1.385e-9 and 1.559e-9), against 4e-22 and 1e-22 for k = (1,0,0). The
   oblique 3D convergence test therefore waits for the fix (Requests).

3. **Second-order backreaction in a closed box** [VERIFIED by the numbers,
   interpretation JUDGEMENT]. The fields that vanish at first order (alpha - 1, chi - 1,
   Khat, Theta, gt_xx - 1) grow as A^2 t^2 independently of the resolution: the box
   mean of Khat rises as pi^2 A^2 t (the mean of alpha At_ij At^ij, the wave's energy
   acting on the homogeneous mode), and alpha - 1 = -(1/6) pi^2 A^2 t^2 under the
   conformal-time lapse, -pi^2 A^2 t^2 under 1+log (measured -1.6e-10 and -1.0e-9 at
   t = 10, A = 1e-6). Under the conformal-time lapse the coordinate light speed is
   unaffected (alpha chi^(1/2) is constant).

4. **Floor at 128 cells: rounding of 1 + h** (`tables/lw_x_roundoff.md`,
   `figs/lw_x_roundoff.png`) [VERIFIED]. The departure of the phase from the prediction
   at N = 128, t = 10 scales as 1/A: -7.3e-8 and -6.1e-7 rad (production, A = 1e-6,
   1e-7), +9.1e-7 and +9.2e-6 (ng 3 numerics); at A = 1e-5 the second-order terms
   (item 3) dominate instead (-1.3e-6). A ~ 1e-6 and N <= 64 give clean convergence.

5. **Gauge wave (Apples with Apples), harmonic slicing, zero shift** (`tables/awa.md`,
   `figs/awa_history.png`, `figs/awa_long.png`). Not runnable with the release
   executables in its own generator (`z4c_gauge_wave.cpp` defines `UserProblem`); run
   here through `nrpic_cosmo` in the proper-length coordinate X of the initial slice,
   where the slice is flat (derivation and exact solution: `analysis/refsol.py`, item
   2; box length 0.99999374985350931 for A = 0.01, 0.99937352871153029 for A = 0.1).
   Measured (production numerics: ng 4, Courant 0.25, KO 0.5, damp_kappa1 0.02)
   [VERIFIED]:

   | A | N | max error gamma_XX / A at t = 20 | max error alpha / A | max abs H | order gamma | order H |
   |---|---|---|---|---|---|---|
   | 0.01 | 50 | 5.77e-6 | 1.36e-6 | 4.0e-7 | | |
   | | 100 | 1.14e-7 | 1.02e-7 | 6.7e-9 | 5.66 | 5.92 |
   | | 200 | 1.52e-7 (floor) | 2.42e-7 | 1.2e-9 (floor) | - | - |
   | 0.1 | 50 | 1.94e-4 | 7.66e-5 | 9.8e-5 | | |
   | | 100 | 3.08e-6 | 1.23e-6 | 1.7e-6 | 5.98 | 5.89 |
   | | 200 | 1.16e-7 | 7.04e-8 | 2.8e-8 | 4.74 | 5.90 |

   The initial data satisfy the constraints to rounding: at N = 200 the evaluated
   |H| sits at 6e-10 from t = 0 for both amplitudes, which is the floor that the
   A = 0.01, N = 200 run never leaves ([JUDGEMENT]: rounding of the second derivatives
   of 1 + H at 200 cells, as in item 4; the absolute error of gamma_XX there is 1.5e-9).
   Long runs at N = 50 (ten times longer, 200 crossings): no failure; the error of
   gamma_XX / A grows from 5.8e-6 (t = 20) to 8.8e-4 (t = 200) at A = 0.01 and from
   1.9e-4 to 9.4e-2 at A = 0.1, faster than linearly (about t^2.3 and t^2.6 between
   t = 50 and 200), with |H| at t = 200 of 5.7e-6 and 4.1e-3. The standard asks for
   1000 crossings; not run.

6. **Record of the lapse and shift options in a periodic vacuum box** (`tables/gauge.md`,
   `figs/gauge_linear.png`, `figs/gauge_nl_profiles.png`, `figs/gauge_nl_gradient.png`)
   [VERIFIED unless marked]. Pure-gauge data (flat slice, K_xx = kappa sin 2 pi x):

   | option (`<z4c>`) | d_t alpha (zero shift) | linear gauge speed | linear: max departure from the linearized system / kappa | kappa = 1.5, N = 128 |
   |---|---|---|---|---|
   | harmonic: `lapse_harmonic = 1`, `lapse_oplog = 0` | -alpha^2 K | 1 | 1.2e-7 | smooth, periodic with the crossing time; alpha chi^(3/2) = 1 to 1.7e-8 |
   | 1+log: `lapse_oplog = 2` (default) | -2 alpha K | sqrt 2 | 1.2e-6 | steepens, kinks, runs to t = 10 |
   | conformal time: `lapse_harmonic = 1/3` (cosmology production) | -(1/3) alpha^2 K | 1/sqrt 3 | 2.7e-7 | gauge shock near t = 2, Theta ~ 1 afterwards, non-finite at t = 2.75 (N = 128) |
   | volume: `lapse_volume = 1/3` | -(1/3) chi^(-1/2) alpha K | 1/sqrt 3 | 2.9e-7 | gauge shock, non-finite at t = 2.94 |
   | K driver: `lapse_kdriver = 1` on conformal time | adds -mu alpha_max alpha (Khat - <Khat>) | sqrt(1/3 + mu) | 1.6e-6 | runs to t = 10 |
   | geodesic: all zero | 0 | 0 (gamma_xx drifts linearly) | 5.9e-7 | not run |
   | Gamma driver `shift_Gamma = 1, shift_eta = 2` with 1+log (AthenaK default gauge) | | shift mode -eta/2 +- i sqrt(4 mu_S k^2/3 - eta^2/4) | 1.1e-6 (N = 64), order 4.3 from 32 to 64 | runs to t = 10, shift up to 0.33 |
   | Gamma driver `0.75, eta 1` with conformal time | | as above | 1.9e-7 | not run |
   | `shift_alpha2Gamma = 1, shift_H = 1` with harmonic slicing | | 1 (double) | 8.1e-8; the shift is not excited | not run |

   [JUDGEMENT] The production lapse of the cosmology runs is not shock-avoiding: in a
   vacuum box an inhomogeneous K of 1.5 on one wavelength (K/k ~ 0.24) produces a gauge
   shock within two crossings; the resolution study (N = 64, 128, 256) shows the
   gradients converge to t = 1.5 and then grow with N, the failure time does not
   converge (N = 256 survives to t = 4 with Theta ~ 1 to 3), so the solution after the
   shock is invalid at every resolution. Harmonic slicing is the shock-free member of
   the family here; 1+log and the K driver survive ten crossings at this amplitude.

7. **Dumps for gw_diag**: section above; validation `tables/dump_check.json`: largest
   error of gt_ij 2.7e-5 A over two periods (dominated by the second-order fields of
   item 3), At_ij 4.3e-6 pi A; Fourier amplitude of h_+ off by -3.0e-7 and its phase
   by 1.25e-6 rad at t = 2, the values of item 1 at 32 cells.

## Not done

- Oblique 3D wave convergence (blocked by item 2; also about 7 hours per 64^3 run on one
  core, so it belongs on a card once the generator is fixed).
- The robust-stability (noise) test of the Apples-with-Apples suite in a Minkowski box
  for each gauge (the generator `nrpic_cosmo` has `noise_amp`; not run here; cosmo C5
  test A did it in an expanding background, `cosmo/TESTLOG.md`).
- The gauge wave to the 1000 crossings of the standard (200 here, N = 50), and a
  shock-formation time for the conformal-time lapse from a semi-analytic
  (characteristic) reference.

## Requests

- **core** (source change in `athenak/src/pgen/tests/z4c_linear_wave.cpp`): flip the
  signs of `axy` and `ayz` (lines 108 and 111) so that e_ij = theta-hat theta-hat -
  phi-hat phi-hat with phi measured as in the file; check: `refsol.tt_check` returns
  e.k = 0 for every k, and the lw3d_check case k = (1,1,1) then gives constraint norms
  below 1e-20. Spec and reference solution for the oblique test after the fix:
  `inputs/lw_3d.athinput` with k = (1,1,1), `refsol.tt_exact`, `analysis/ana_dump.py`.
  Optional: make the error routine `Z4cLinearWaveErrors` compare with the exact
  solution at the final time instead of the initial data.
- **core** (optional): register `z4c_gauge_wave` (and `z4c_stability`) as named built-in
  problem generators, so that the standard input `athenak/inputs/z4c/awa/` runs with the
  release executables; the X-coordinate route of this package works meanwhile.
- **core** (optional, later): a double-precision option for the bin output (the only
  double-precision full-mesh dump is now the restart file), and, if Track B needs
  waves far below h ~ 1e-7 at 128 cells per wavelength, evolving the metric
  perturbation separately from the background (item 4).
- **orch**: the ignore pattern `runs/` of `.gitignore` also matches
  `tracks/<ID>/runs/`, so run manifests must be force-added (done here with
  `git add -f` on the manifest files only; the kb branch does the same). Suggest
  `/runs/`.
- **kb**: locate in the source the Apples-with-Apples gauge-wave results for BSSN/Z4c at
  A = 0.1 (growth over 1000 crossings), to compare with item 5.
