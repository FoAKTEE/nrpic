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

Run `lw3d_dump_N32` (run id in `tables/dump_check.json`; manifest in
`tracks/B-emd-gw/runs/`), output directory
`/data/haiyangw/nrpic/scratch/B-emd-gw/<run_id>/`:

- Problem: TT wave `z4c_linear_wave`, k = (1, 0, 0) cycles per unit length, A = 1e-6,
  box [-1/2, 1/2]^3, 32^3 cells, one MeshBlock, ng = 4, conformal-time lapse, zero shift;
  t = 0 to 2 (two periods), dumps every 1/16 (33 dumps).
  Exact solution: `refsol.tt_exact(x, y, z, t, 1, 0, 0, 1e-6)`:
  gamma_yy - 1 = -(gamma_zz - 1) = -A sin(2 pi (x - t)), K_yy = -K_zz = -pi A cos(...)
  (K_ij = At_ij at first order).
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

(filled in after the runs; see `tables/`)

## Requests

(see end of file)
