# East, Wojtak & Pretorius (arXiv:1908.05683): numbers read from the figures

Curves of every figure of the paper, extracted for a quantitative comparison with our code. Per-figure data, calibration and accuracy are in `cosmo/notes/east_figures/<eps name>/` (`<name>.csv`, `curves.csv`, derived-number CSVs, `README.md`, and `check_<name>.png` comparing the original rendering with a replot of the extracted numbers). The scripts are in `.work/east_fig_tools/`; run order `extract_all.py`, `analyze.py`, `replot.py`, `extra_checks.py`, `gen_docs.py` (helpers `psparse.py`, `calib.py`), all with `python3 -E` from that folder.

**All 20 figures are vector graphics** (19 matplotlib 1.5.1, 1 gnuplot 5.2); no figure contains a raster image. Every number below is therefore **vector**: read from the PostScript polylines, calibrated on the tick marks. Nothing was traced from pixels.

## Conventions
* a_p = (3 tau H0/2 + 1)^(2/3), with tau the proper time of the observer or particle concerned (so different curves have different a_p at the same coordinate time).
* dbar: amplitude in delta_N = sum_i dbar_i sin(k x^i), dbar_i = dbar (1, 0.9, 1.1) for (x, y, z), k = pi H0/2.
* L: box length = one wavelength = 4/H0 (Fig. 6 legend "L/dx = 96" and the text "96 points across the wavelength"; the Fig. 3 initial speeds also require L = 2 pi/k).
* d: coordinate distance (>= 0) of a fiducial particle from the point of maximum density.
* GR = Einstein-Vlasov run; Newt = GADGET-2 run (density from the tetrahedral phase-space estimator unless "CIC").

## Accuracy
matplotlib 1.5 simplifies paths before writing them: a vertex is dropped when it lies within 1/9 pt of a straight run, so the drawn line is within 0.11 pt of the data. Coordinates carry 6 decimals and the tick fits have residuals below 1e-3 pt, so 0.11 pt is the reading error. In data units:

| figure | x axis | x error | y axis | y error |
|---|---|---|---|---|
| Fig. 1 top (`ud_comp`) | log 1-280.1 | +-0.13% (0.0006 dex) | log 0.01-0.9999 | +-0.15% (0.0006 dex) |
| Fig. 1 middle (`od_comp`) | log 1-280.1 | +-0.13% (0.0006 dex) | log 0.01-9.995e+06 | +-0.66% (0.0029 dex) |
| Fig. 1 bottom (`delta10m2_comp_all`) | lin 0.001329-140 | +-0.033 data units | log 0.05-1e+04 | +-0.39% (0.0017 dex) |
| Fig. 2 top left (dbar=0.05) (`delta5em2pm_splash`) | lin 0.9999-18 | +-0.0041 data units | lin -0.26-0.2599 | +-0.00016 data units |
| Fig. 2 top right (dbar=0.01) (`delta10em2pm_splash`) | lin 0.9997-92.8 | +-0.022 data units | lin -0.26-0.2599 | +-0.00016 data units |
| Fig. 2 bottom left (dbar=0.005) (`delta5em3pm_splash`) | lin 0.9994-143 | +-0.034 data units | lin -0.26-0.2599 | +-0.00016 data units |
| Fig. 2 bottom right (dbar=0.0025) (`delta2p5em3pm_splash`) | lin 0.9992-255.5 | +-0.061 data units | lin -0.26-0.2599 | +-0.00016 data units |
| Fig. 7 top (appendix, GR) (`res_delta10em2pm_splash`) | lin -0.000527-92 | +-0.022 data units | lin -0.26-0.2599 | +-0.00016 data units |
| Fig. 7 bottom (appendix, Newtonian) (`res_newt_delta10em2pm_splash`) | lin -0.000527-92 | +-0.022 data units | lin -0.26-0.2599 | +-0.00016 data units |
| Fig. 3 (`rel_eff`) | log 0.0003146-0.5109 | +-0.06% (0.0002 dex) | log 9.997e-06-0.1 | +-0.08% (0.0003 dex) |
| Fig. 4 row 1 left (dbar=0.01) (`delta1em2_dl_comp_frw`) | log 0.01-9.994 | +-0.17% (0.0008 dex) | symlog -30.01-29.93 | +-2.7e-05 absolute inside |y|<1e-2, +-0.68% of |y| outside |
| Fig. 4 row 1 right (dbar=0.01) (`delta1em2_dl_newt_gr`) | log 0.01-9.994 | +-0.17% (0.0007 dex) | log 0.0001-1 | +-0.31% (0.0013 dex) |
| Fig. 4 row 2 left (dbar=0.005) (`delta5em3_dl_comp_frw`) | log 0.01-9.994 | +-0.17% (0.0008 dex) | symlog -30.01-29.93 | +-2.7e-05 absolute inside |y|<1e-2, +-0.68% of |y| outside |
| Fig. 4 row 2 right (dbar=0.005) (`delta5em3_dl_newt_gr`) | log 0.01-9.994 | +-0.17% (0.0007 dex) | log 0.0001-1 | +-0.31% (0.0013 dex) |
| Fig. 4 row 3 left (dbar=0.0025) (`delta2p5em3_dl_comp_frw`) | log 0.01-9.994 | +-0.17% (0.0008 dex) | symlog -30.01-29.93 | +-2.7e-05 absolute inside |y|<1e-2, +-0.68% of |y| outside |
| Fig. 4 row 3 right (dbar=0.0025) (`delta2p5em3_dl_newt_gr`) | log 0.01-9.994 | +-0.17% (0.0007 dex) | log 0.0001-1 | +-0.31% (0.0013 dex) |
| Fig. 5 (dbar=0.05) (`delta5em2_dl_comp_frw`) | log 0.01-9.994 | +-0.17% (0.0008 dex) | symlog -30.01-29.93 | +-2.7e-05 absolute inside |y|<1e-2, +-0.68% of |y| outside |
| Fig. 8 top (appendix, rays from OD) (`delta1em2_dl_newt_gr_res_ou`) | log 0.01-9.994 | +-0.17% (0.0007 dex) | log 9.999e-05-1.998 | +-0.32% (0.0014 dex) |
| Fig. 8 bottom (appendix, rays from UD) (`delta1em2_dl_newt_gr_res_uo`) | log 0.01-9.994 | +-0.17% (0.0007 dex) | log 9.999e-05-1.998 | +-0.32% (0.0014 dex) |
| Fig. 6 (appendix) (`10m2_cnst_conv`) | lin -0.009628-140 | +-0.022 data units | log 2e-06-0.01001 | +-0.31% (0.0013 dex) |

A second, often larger, limit is the sampling of the underlying data: Newtonian curves have one vertex per snapshot (Delta a_p ~ 1.3 near a_p ~ 57 for dbar = 0.01), which bounds how well a crossing time can be located. Interpolated values (crossings, values at given a_p or z) are taken along the drawn line in display coordinates, i.e. log-log interpolation on log axes.

## Fig. 1 top: void (minimum density), |delta_obs|(a_p)  [vector, +-0.15%]

| dbar | model | a_p=1 | a_p=2 | a_p=5 | a_p=10 | a_p=20 | a_p=50 | a_p=100 | end of curve (a_p, value) |
|---|---|---|---|---|---|---|---|---|---|
| 0.0025 | GR | 0.0166 | 0.0182 | 0.0377 | 0.0717 | 0.1350 | 0.2909 | 0.4628 | (256.3, 0.721) |
| 0.0025 | Newt | 0.0166 | 0.0182 | 0.0373 | 0.0706 | 0.1333 | 0.2852 | 0.4581 | (265.8, 0.726) |
| 0.005 | GR | 0.0332 | 0.0363 | 0.0743 | 0.1375 | 0.2476 | 0.4679 | 0.6667 | (172.1, 0.792) |
| 0.005 | Newt | 0.0332 | 0.0363 | 0.0730 | 0.1350 | 0.2422 | 0.4614 | 0.6558 | (147.3, 0.750) |
| 0.01 | GR | 0.0664 | 0.0727 | 0.1440 | 0.2528 | 0.4173 | 0.6745 | - | (96.3, 0.824) |
| 0.01 | Newt | 0.0662 | 0.0721 | 0.1418 | 0.2495 | 0.4103 | 0.6655 | 0.8238 | (102.1, 0.828) |
| 0.05 | GR | 0.3323 | 0.3535 | 0.5548 | 0.7367 | - | - | - | (19.3, 0.867) |
| 0.05 | Newt | 0.3191 | 0.3490 | 0.5538 | 0.7402 | 0.8720 | - | - | (22.7, 0.888) |

Newt/GR - 1 at the same a_p: dbar=0.0025: +0.1%, +0.3%, -1.2%, -1.5%, -1.2%, -2.0%, -1.0%; dbar=0.005: -0.0%, -0.1%, -1.7%, -1.8%, -2.2%, -1.4%, -1.6%; dbar=0.01: -0.4%, -0.8%, -1.5%, -1.3%, -1.7%, -1.3%; dbar=0.05: -4.0%, -1.3%, -0.2%, +0.5% (a_p = 1, 2, 5, ... in order). Largest |Newt/GR - 1| over the common range: 2.0% (dbar=0.0025, at a_p=50), 2.3% (dbar=0.005, at a_p=32), 2.2% (dbar=0.01, at a_p=42), 3.9% (dbar=0.05, at a_p=1).

## Fig. 1 middle: halo (maximum density), |delta_obs|(a_p)  [vector; a_p +-0.13%, |delta_obs| +-0.7%]

First maximum = first local maximum followed by a drop > 0.05 dex; plateau = median [min-max] of |delta_obs| from the first maximum to the end of the curve.

| dbar | model | a_p at 1 | a_p at 10 | a_p at 100 | a_p at 1000 | first max: a_p, value | plateau median [min-max] | end: a_p, value |
|---|---|---|---|---|---|---|---|---|
| 0.0025 | GR | 76.93 | 173.30 | 220.99 | - | none before end | - | 255.17, 499.3 |
| 0.0025 | Newtonian | 76.06 | 170.14 | 210.86 | 219.40 | 244.66, 1.073e+05 | 1.18e+05 [5.244e+04-2.484e+05] | 262.82, 1.18e+05 |
| 0.005 | GR | 39.08 | 88.28 | 112.19 | - | 127.75, 536.4 | 540.5 [453.3-792.8] | 171.08, 659.8 |
| 0.005 | Newtonian | 37.51 | 83.42 | 102.65 | 108.53 | 121.67, 5.413e+05 | 4.063e+05 [9.261e+04-6.676e+05] | 142.77, 4.063e+05 |
| 0.01 | GR | 20.20 | 45.78 | 58.01 | 86.98 | 66.11, 612.6 | 749.2 [545.2-1085] | 92.90, 1060 |
| 0.01 | Newtonian | 19.35 | 42.82 | 52.42 | 54.98 | 57.46, 3.261e+05 | 2.873e+06 [2.113e+05-4.415e+06] | 90.42, 4.084e+06 |
| 0.01 | Newtonian CIC | 19.67 | 43.16 | 53.89 | 59.60 | none before end | - | 90.42, 2440 |
| 0.05 | GR | 5.09 | 11.87 | 15.14 | - | none before end | - | 16.80, 235.9 |
| 0.05 | Newtonian | 4.36 | 9.06 | 10.60 | 10.86 | none before end | - | 10.86, 1087 |
| 0.05 | Newtonian CIC | 4.20 | 8.76 | 10.67 | - | none before end | - | 10.86, 156.4 |

Notes: GR dbar = 0.0025 is still rising at the end (499 at a_p = 255.2); GR dbar = 0.05 levels off at 236-237 for a_p = 16.4-16.8 (end of run); the Newtonian dbar = 0.05 run stops at a_p = 10.86 (|delta_obs| = 1087, CIC 156); the CIC dbar = 0.01 curve rises slowly to 2440 at a_p = 90.4 without a maximum.

Ratio of GR to Newtonian a_p at the same |delta_obs|:

| dbar | at 1 | at 10 | at 100 |
|---|---|---|---|
| 0.0025 | 1.011 | 1.019 | 1.048 |
| 0.005 | 1.042 | 1.058 | 1.093 |
| 0.01 | 1.043 | 1.069 | 1.107 |
| 0.05 | 1.169 | 1.310 | 1.429 |

## Fig. 1 bottom: dbar = 0.01 halo, resolutions and fluid vs particles  [vector; a_p +-0.03, |delta_obs| +-0.4%]

| curve (legend) | a_p at 1 | a_p at 10 | a_p at 100 | a_p at 1000 | first max: a_p, value | plateau median [min-max] | end: a_p, value |
|---|---|---|---|---|---|---|---|
| GR OD (blue, solid) | 20.58 | 45.92 | 58.94 | 69.57 | 75.36, 1128 | 1121 [515.7-1670] | 131.59, 1265 |
| GR OD High Res. (green, solid) | 20.19 | 45.61 | 57.21 | 63.75 | 69.51, 1550 | 1265 [1061-1724] | 78.73, 1724 |
| GR OD Fluid (red, solid) | 19.94 | 44.55 | 55.85 | 62.08 | 72.12, 1.22e+04 | 1.118e+04 [8544-1.22e+04] | 73.16, 8544 |
| GR OD Fluid High Res. (cyan, solid) | 19.94 | 44.59 | 55.17 | 58.84 | - | - | 62.58, 2.349e+04 |
| Newt. OD (red, dashed) | 19.53 | 43.11 | 52.71 | 55.15 | 56.15, 1.164e+04 | 2.349e+04 [5592-2.349e+04] | 60.87, 2.349e+04 |
| Newt. OD High Res. (black, dashed) | 19.38 | 42.82 | 52.43 | 54.99 | - | - | 56.00, 2.349e+04 |
| Newt. OD CIC (blue, dashed) | 19.70 | 43.17 | 53.89 | 59.60 | - | - | 90.42, 2440 |

Values above 1e4 are outside the axes (hidden in the paper) and the paths stop at the page edge, 2.35e4. "Newt. OD High Res." is the default N = 196^3 run (identical to Fig. 1 middle to 0.004 dex), so "Newt. OD" is N = 128^3. The Fig. 1 middle GR dbar = 0.01 curve lies between "GR OD" and "GR OD High Res." (see contradictions below). Fluid vs particles (default resolution): a_p at |delta_obs| = 100 is 55.85 (fluid) vs 58.94 (particles).

## Fig. 2 (and Fig. 7): fiducial particles, d/L against a_p  [vector; d/L +-1.6e-4]

Each panel: 24 curves = 2 models (GR top half, plotted +d/L; Newtonian bottom half, plotted -d/L) x 3 directions (red x, green y, blue z) x 4 initial distances d0 = L/32, L/16, L/8, L/4 (solid, dotted, dashed, dash-dot). Plotted ranges: y in [-0.26, 0.26] for all panels; x (a_p) in
* Fig. 2 top left (dbar=0.05): [1, 18]; curves end at a_p = 17.86-18.01 (top half), 10.82-13.87 (bottom half)
* Fig. 2 top right (dbar=0.01): [1, 92.8]; curves end at a_p = 91.96-92.8 (top half), 90.04-95.51 (bottom half)
* Fig. 2 bottom left (dbar=0.005): [0.999, 143]; curves end at a_p = 143-143 (top half), 142.7-145.1 (bottom half)
* Fig. 2 bottom right (dbar=0.0025): [0.999, 255.5]; curves end at a_p = 255.1-255.5 (top half), 263.4-264.3 (bottom half)
* Fig. 7 top (appendix, GR): [-0.000527, 92]; curves end at a_p = 92-92.01 (top half), 91.96-92.01 (bottom half)
* Fig. 7 bottom (appendix, Newtonian): [-0.000527, 92]; curves end at a_p = 90.65-94.73 (top half), 90.04-94.73 (bottom half)

Initial distances read from the curves: d0/L = 0.03125, 0.0625, 0.125, 0.25 (+-1e-4) in every panel except the Newtonian half of dbar = 0.005, which starts at 0.0327, 0.0639, 0.1264, 0.2513.

Crossing times. a_min = first local minimum of d after d < 0.15 d0 (the crossing); a_10 = a_p where d first falls below 0.1 d0 (a robust infall marker that does not depend on the sampling near zero). Mean over the x, y, z particles [min-max]; "-" = not reached before the curve ends. Uncertainty of a_min (half the a_p interval over which the drawn d stays within max(5e-4, 0.02 d0) of its minimum, `bracket_lo/hi` in turning_points.csv): typically +-0.3 (dbar = 0.05), +-0.75 (0.01), +-1.5 (0.005), +-3 (0.0025) in both models, up to +-17 for small-d0 Newtonian particles that settle at d ~ 0; the Newtonian snapshot spacing near the crossing is ~1.3, 2.8, 5.7 for dbar = 0.01, 0.005, 0.0025. a_10 is good to about +-0.3 (0.01), +-0.6, +-1.2 and is the better number to compare with. GR/Newt a_10 = ratio of the means; "*" = only the directions present in both models.

| dbar | d0/L | GR a_min | Newt a_min | GR a_10 | Newt a_10 | GR/Newt a_10 |
|---|---|---|---|---|---|---|
| 0.0025 | 0.03125 | 245.9 [241.6-250.1] | 229.4 [222.0-233.1] | 235.0 [226.6-243.3] | 220.0 [213.1-226.6] | 1.068 |
| 0.0025 | 0.0625 | 248.0 [243.6-252.4] | 229.4 [227.5-233.2] | 237.3 [228.5-245.9] | 223.9 [217.2-230.5] | 1.060 |
| 0.0025 | 0.125 | 253.9 | 245.1 [239.1-251.2] | 243.9 [239.2-248.5] | 237.7 [230.2-245.6] | 1.043* |
| 0.0025 | 0.25 | - | - | - | - | - |
| 0.005 | 0.03125 | 126.0 [122.2-129.4] | 116.1 [113.3-118.9] | 119.4 [115.2-123.2] | 112.1 [109.2-114.4] | 1.065 |
| 0.005 | 0.0625 | 127.3 [123.4-130.7] | 117.0 [113.3-121.6] | 120.7 [116.5-124.6] | 113.4 [110.4-116.1] | 1.064 |
| 0.005 | 0.125 | 132.3 [128.2-136.1] | 121.8 [118.9-124.7] | 126.1 [122.0-129.9] | 119.3 [116.1-122.5] | 1.057 |
| 0.005 | 0.25 | - | - | - | - | - |
| 0.01 | 0.03125 | 64.7 [63.0-66.2] | 57.9 [56.1-60.0] | 61.7 [59.7-63.4] | 55.7 [54.2-57.0] | 1.109 |
| 0.01 | 0.0625 | 65.4 [63.6-66.9] | 60.1 [57.5-64.0] | 62.4 [60.4-64.0] | 56.4 [54.9-57.8] | 1.106 |
| 0.01 | 0.125 | 67.9 [66.0-69.4] | 60.2 [58.8-61.6] | 65.2 [63.2-66.8] | 59.4 [57.9-60.9] | 1.097 |
| 0.01 | 0.25 | 86.6 [83.9-88.9] | 77.3 [74.6-79.6] | 83.6 [80.9-85.9] | 75.9 [73.8-77.9] | 1.101 |
| 0.05 | 0.03125 | 16.5 [16.2-16.7] | - | 15.9 [15.5-16.2] | 10.7 [10.5-10.8] | 1.485* |
| 0.05 | 0.0625 | 16.6 [16.3-16.9] | - | 16.0 [15.6-16.3] | 10.6 [10.5-10.7] | 1.508* |
| 0.05 | 0.125 | 17.4 [17.1-17.7] | - | 16.8 [16.5-17.1] | - | - |
| 0.05 | 0.25 | - | - | - | - | - |

Per-direction values (x, y, z) of a_min, in that order:

* dbar = 0.0025: GR L/32: 250.06, -, 241.64; GR L/16: 252.42, -, 243.62; GR L/8: -, -, 253.87; GR L/4: -, -, -; Newt L/32: 233.14, 233.13, 221.98; Newt L/16: 227.53, 233.18, 227.54; Newt L/8: 245.08, 251.17, 239.13; Newt L/4: -, -, -
* dbar = 0.005: GR L/32: 126.45, 129.40, 122.24; GR L/16: 127.65, 130.74, 123.38; GR L/8: 132.60, 136.07, 128.23; GR L/4: -, -, -; Newt L/32: 118.85, 116.07, 113.31; Newt L/16: 116.07, 121.63, 113.31; Newt L/8: 121.76, 124.69, 118.89; Newt L/4: -, -, -
* dbar = 0.01: GR L/32: 65.03, 66.24, 62.97; GR L/16: 65.74, 66.88, 63.58; GR L/8: 68.13, 69.42, 66.05; GR L/4: 86.88, 88.93, 83.94; Newt L/32: 57.46, 60.04, 56.13; Newt L/16: 57.47, 58.76, 63.96; Newt L/8: 60.19, 61.57, 58.84; Newt L/4: 77.85, 79.56, 74.59
* dbar = 0.05: GR L/32: 16.75, 16.44, 16.20; GR L/16: 16.90, 16.61, 16.34; GR L/8: 17.74, 17.38, 17.08; GR L/4: -, -, -; Newt L/32: -, -, -; Newt L/16: -, -, -; Newt L/8: -, -, -; Newt L/4: -, -, -

Turning points after the first crossing (dbar = 0.01; a_p, d/L), from `delta10em2pm_splash/turning_points.csv`:

| particle | GR: cross; next turning points | Newt: cross; next turning points |
|---|---|---|
| x, L/32 | min 65.03 (0.0003); max 75.87 (0.0071); min 85.42 (0.0013) | min 57.46 (0.0012) |
| y, L/32 | min 66.24 (0.0004); max 76.53 (0.0074); min 85.90 (0.0013) | min 60.04 (0.0007) |
| z, L/32 | min 62.97 (0.0001); max 75.00 (0.0069); min 85.23 (0.0001) | min 56.13 (0.0004) |
| x, L/16 | min 65.74 (0.0006); max 76.10 (0.0143); min 86.22 (0.0014) | min 57.47 (0.0024) |
| y, L/16 | min 66.88 (0.0006); max 76.92 (0.0147); min 86.73 (0.0015) | min 58.76 (0.0017); max 60.00 (0.0065); min 61.26 (0.0013); max 62.55 (0.0044); min 65.18 (0.0003) |
| z, L/16 | min 63.58 (0.0001); max 74.83 (0.0138); min 84.72 (0.0001) | min 63.96 (0.0011) |
| x, L/8 | min 68.13 (0.0012); max 77.46 (0.0280); min 88.75 (0.0019) | min 60.19 (0.0063); max 62.89 (0.0133); min 65.66 (0.0063); max 67.10 (0.0126); min 74.48 (0.0053) |
| y, L/8 | min 69.42 (0.0013); max 78.62 (0.0272); min 89.57 (0.0021) | min 61.57 (0.0064); max 64.24 (0.0179); min 67.15 (0.0037); max 71.55 (0.0143); min 72.96 (0.0058) |
| z, L/8 | min 66.05 (0.0001); max 76.23 (0.0292); min 86.75 (0.0001) | min 58.84 (0.0056) |
| x, L/4 | min 86.88 (0.0023) | min 77.85 (0.0080); max 87.53 (0.0605) |
| y, L/4 | min 88.93 (0.0027) | min 79.56 (0.0083); max 89.33 (0.0701) |
| z, L/4 | min 83.94 (0.0000) | min 74.59 (0.0128); max 83.36 (0.0491); min 90.72 (0.0072) |

Small-d0 Newtonian particles stay within d < 0.003 L after reaching the centre (no resolvable second apocentre), so their "first minimum" can be one or two snapshots after a_10; use a_10 or a_05 for them.

Fig. 7 (resolution, dbar = 0.01): a_min mean over x, y, z [range]:

| d0/L | GR low (N=128^3) | GR high (N=384^3) | Newt low (128^3) | Newt high (196^3) |
|---|---|---|---|---|
| 0.03125 | 66.8 [64.9-68.6] | 64.7 [63.0-66.2] | 57.5 [56.1-58.8] | 57.9 [56.1-60.0] |
| 0.0625 | 67.4 [65.4-69.0] | 65.4 [63.6-66.9] | 57.9 [57.5-58.8] | 60.1 [57.5-64.0] |
| 0.125 | 69.8 [67.8-71.5] | 67.9 [66.0-69.4] | 60.7 [60.2-61.6] | 60.2 [58.8-61.6] |
| 0.25 | 88.1 [85.4-90.6] | 86.6 [83.9-89.0] | 77.9 [75.8-79.8] | 77.3 [74.6-79.6] |

First apocentre after the crossing, GR low vs high (dbar = 0.01, d0 = L/8): x 84.7 vs 77.5, y - vs 78.6, z 82.5 vs 76.2 (the resolution dependence grows after the first crossing, as the appendix says).

## Fig. 3: |d_OD^Newt - d_OD^GR|/L against |v_infall|  [vector (gnuplot); +-0.06% in |v|, +-0.08% in the difference]

* x: |v_infall|, the magnitude of the infall speed in the Newtonian run in units of c, log axis 3.15e-4 to 0.511 (ticks 0.001, 0.01, 0.1). y: |d_OD^Newt - d_OD^GR|/L, log axis 1e-5 to 0.1. Each curve stops at the first Newtonian halo crossing (caption); gnuplot clips at the axes box.
* Curves (all x-direction particles, see check): 
  * dbar=0.0025, d_OD(a_p=1)/L=0.031 (purple): |v| from 0.000315 to 0.00573; |dd|/L = 1.1e-05 at the start, 0.00342 at the last point (|v| = 0.00573); largest value away from the axes edges 0.00342 at |v| = 0.00573.
  * dbar=0.01, d_OD(a_p=1)/L=0.063 (teal green): |v| from 0.00247 to 0.143; |dd|/L = 6.6e-05 at the start, 0.0133 at the last point (|v| = 0.143); largest value away from the axes edges 0.0133 at |v| = 0.143.
  * dbar=0.01, d_OD(a_p=1)/L=0.25 (as labelled) (orange): |v| from 0.00644 to 0.511; |dd|/L = 8e-05 at the start, 0.0518 at the last point (|v| = 0.511); largest value away from the axes edges 0.0404 at |v| = 0.32.
* Upper envelope of the three curves (max |dd|/L in 0.25-dex bins of |v|): 0.00032-0.00056: 0.00019, 0.00056-0.001: 0.00041, 0.001-0.0018: 0.00055, 0.0018-0.0032: 0.00071, 0.0032-0.0056: 0.0024, 0.0056-0.01: 0.0034, 0.01-0.018: 0.0085, 0.018-0.032: 0.0085, 0.032-0.056: 0.014, 0.056-0.1: 0.01, 0.1-0.18: 0.029, 0.18-0.32: 0.035.
* In words (all three curves together): |dd|/L stays < 0.0003 for |v| < 0.000691, < 0.001 for |v| < 0.00405, < 0.003 for |v| < 0.00573, < 0.01 for |v| < 0.0413, < 0.03 for |v| < 0.185; the curves pass through zero (deep dips) several times, so the envelope, not individual values, is the meaningful quantity.

## Figs. 4, 5 and 8: luminosity distance along fiducial rays  [vector; z +-0.17%; left column +-2.7e-5 inside |y|<0.01 and +-0.7% of |y| outside; right column +-0.3%]

* Left column (and Fig. 5): y = D_L/D_L^LFRW - 1, symlog axis from -30 to +30: linear for |y| < 1e-2 (linthresh 1e-2, linscale 1, i.e. the 0-1e-2 stretch is as long as 1.11 decades), log outside; x = z, log, 0.01-10. Right column: |D_L^Newt/D_L^GR - 1|, log 1e-4 to 1 (Fig. 8: 1e-4 to 2); x = z, log, 0.01-10.
* Rays: emitted at the overdensity towards the underdensity (OD->UD) or the reverse, at emission times labelled a_em ~ 1, 28, 43, 52 (OD) and 1, 27, 44, 52 (UD) for dbar = 0.01; 1, 28, 58, 112 / 1, 28, 58, 111 for 0.005; 1, 28, 59, 163 / 1, 28, 58, 162 for 0.0025; 1, 8 (OD) and 1, 9, 14 (UD) for 0.05. The a_em ~ 1 rays have their first drawn point at z = 0.089 (0.028-0.030 for dbar = 0.05); later rays start at z = 0.0022 (hidden below z = 0.01).
* Values below: "a/b" means the ray passes that z twice (blueshift near the halo); "-" = z not reached.

### dbar = 0.01 (Fig. 4 top row)

| ray (a_em) | z range drawn [visible part] | GR: y at z=0.1, 0.5, 1, 2 | Newt: y at z=0.1, 0.5, 1, 2 | |dD/D| (right column) at z=0.1, 0.5, 1, 2 | max |dD/D| visible (z) |
|---|---|---|---|---|---|
| OD->UD (1) | 0.0887-6.73 [0.0887-6.73] | -0.007651, -0.005053, -0.00484, -0.01113 | -0.007621, -0.004636, -0.004123, -0.01041 | 2.102e-05, 0.0004057, 0.0007372, 0.0007144 | 0.00145 (z=5.1) |
| UD->OD (1) | 0.0887-6.2 [0.0887-6.2] | 0.006561, 0.003764, 0.003416, 0.00942 | 0.006602, 0.004127, 0.004163, 0.01026 | 3.935e-05, 0.0003815, 0.0007483, 0.0008397 | 0.00188 (z=5.05) |
| OD->UD (28) | 0.00222-0.839 [0.01-0.839] | 0.6052, 0.006361, -, - | 0.6501, 0.0005959, -, - | 0.02835, 0.005678, -, - | 0.0967 (z=0.0273) |
| UD->OD (27) | 0.00222-0.735 [0.01-0.735], z turns back (ends at 0.695) | -0.1608, -0.1728, -, - | -0.1577, -0.1744, -, - | 0.003798, 0.002735, -, - | 0.0679 (z=0.735) |
| OD->UD (43) | 0.00222-0.678 [0.01-0.678] | 0.7537, -0.07293, -, - | 0.7585, -0.08319, -, - | 0.002805, 0.01106, -, - | 0.103 (z=0.0113) |
| UD->OD (44) | 0.00222-0.796 [0.01-0.796], z turns back (ends at 0.482) | -0.2051, -0.2516/0.1871, -, - | -0.2026, -0.26/0.1801, -, - | 0.002868, 0.01005/0.005913, -, - | 0.0567 (z=0.776) |
| OD->UD (52) | 0.00222-0.632 [0.01-0.632] | 0.6764, -0.1242, -, - | 0.6276, -0.1466, -, - | 0.02896, 0.02578, -, - | 0.0316 (z=0.169) |
| UD->OD (52) | 0.00222-0.771 [0.01-0.771], z turns back (ends at 0.408) | -0.2215, -0.2881/0.03401, -, - | -0.2176, -0.2974/0.03307, -, - | 0.004269, 0.0118/0.0007905, -, - | 0.0492 (z=0.746) |

### dbar = 0.005 (Fig. 4 middle row)

| ray (a_em) | z range drawn [visible part] | GR: y at z=0.1, 0.5, 1, 2 | Newt: y at z=0.1, 0.5, 1, 2 | |dD/D| (right column) at z=0.1, 0.5, 1, 2 | max |dD/D| visible (z) |
|---|---|---|---|---|---|
| OD->UD (1) | 0.0887-6.6 [0.0887-6.6] | -0.003854, -0.002541, -0.002417, -0.005537 | -0.003725, -0.002304, -0.002073, -0.005177 | 0.0001302, 0.0002111, 0.0003366, 0.0003849 | 0.0011 (z=5.29) |
| UD->OD (1) | 0.0887-6.33 [0.0887-6.33] | 0.003224, 0.001857, 0.001699, 0.004748 | 0.003396, 0.002118, 0.002068, 0.005209 | 0.0001685, 0.0002487, 0.0003737, 0.000462 | 0.00141 (z=5.18) |
| OD->UD (28) | 0.00222-0.793 [0.01-0.793] | 0.2106, 0.02266, -, - | 0.218, 0.02198, -, - | 0.006693, 0.0006754, -, - | 0.00677 (z=0.0916) |
| UD->OD (28) | 0.00222-0.729 [0.01-0.729] | -0.103, -0.08089, -, - | -0.1029, -0.08231, -, - | 0.0007514, 0.001694, -, - | 0.00763 (z=0.0115) |
| OD->UD (58) | 0.00222-0.538 [0.01-0.538] | 0.4778, -0.0515, -, - | 0.4904, -0.0514, -, - | 0.008715, 0.0001879, -, - | 0.0542 (z=0.0239) |
| UD->OD (58) | 0.00222-0.488 [0.01-0.488] | -0.1673, -, -, - | -0.1657, -, -, - | 0.001647, -, -, - | 0.0284 (z=0.488) |
| OD->UD (112) | 0.00222-0.0997 [0.01-0.0997] | -, -, -, - | -, -, -, - | -, -, -, - | 0.0349 (z=0.067) |
| UD->OD (111) | 0.00222-0.185 [0.01-0.185] | -0.2287, -, -, - | -0.2283, -, -, - | 0.0005892, -, -, - | 0.00829 (z=0.177) |

### dbar = 0.0025 (Fig. 4 bottom row)

| ray (a_em) | z range drawn [visible part] | GR: y at z=0.1, 0.5, 1, 2 | Newt: y at z=0.1, 0.5, 1, 2 | |dD/D| (right column) at z=0.1, 0.5, 1, 2 | max |dD/D| visible (z) |
|---|---|---|---|---|---|
| OD->UD (1) | 0.0898-6.51 [0.0898-6.51] | -0.002025, -0.001366, -0.001298, -0.002857 | -0.00183, -0.00114, -0.00105, -0.002575 | 0.0001962, 0.0002322, 0.0002651, 0.0002837 | 0.000298 (z=1.41) |
| UD->OD (1) | 0.0898-6.39 [0.0898-6.39] | 0.001508, 0.0008298, 0.0007582, 0.002294 | 0.001738, 0.001039, 0.001042, 0.002594 | 0.0002334, 0.0002161, 0.0002601, 0.000299 | 0.000328 (z=2.5) |
| OD->UD (28) | 0.00222-0.774 [0.01-0.774] | 0.08586, 0.0176, -, - | 0.08583, 0.0176, -, - | 0.000156, 1.811e-05, -, - | 0.00702 (z=0.0113) |
| UD->OD (28) | 0.00222-0.742 [0.01-0.742] | -0.05989, -0.03378, -, - | -0.06023, -0.03402, -, - | 8.698e-05, 0.0002974, -, - | 0.00537 (z=0.0133) |
| OD->UD (59) | 0.00222-0.518 [0.01-0.518] | 0.2037, -0.02509, -, - | 0.2104, -0.02475, -, - | 0.005602, 0.0003467, -, - | 0.0077 (z=0.011) |
| UD->OD (58) | 0.00222-0.491 [0.01-0.491] | -0.1064, -, -, - | -0.1073, -, -, - | 0.0001305, -, -, - | 0.00689 (z=0.0104) |
| OD->UD (163) | 0.00222-0.305 [0.01-0.305] | 0.3088, -, -, - | 0.3288, -, -, - | 0.0153, -, -, - | 0.0546 (z=0.011) |
| UD->OD (162) | 0.00253-0.311 [0.01-0.311] | -0.2, -, -, - | -0.2005, -, -, - | 0.0006452, -, -, - | 0.0193 (z=0.311) |

### dbar = 0.05 (Fig. 5, left-column quantity only)

| ray (a_em) | z range drawn [visible part] | GR: y at z=0.1, 0.5, 1, 2 | Newt: y at z=0.1, 0.5, 1, 2 | reconstructed GR-Newt s=(1+y_N)/(1+y_GR)-1: max |s| (z) |
|---|---|---|---|---|
| OD->UD (1) | 0.0284-8.17 [0.0284-8.17] | -0.04624, -0.03599, -0.03519, -0.06445 | -0.04846, -0.0256, -0.01863, -0.05234 | +0.0191 (z=1.32) |
| UD->OD (1) | 0.0305-5.25 [0.0305-5.25] | 0.03219, 0.01582, 0.01211, 0.03634 | 0.02316, 0.01712, 0.02199, 0.04739 | -0.0466 (z=4.61) |
| OD->UD (8) | 0.00222-1.96 [0.01-1.96] | 1.115, 0.06191, -0.2091, - | 1.972, -0.027, -0.315, - | +10.1 (z=0.01) |
| UD->OD (9) | 0.00222-1.85 [0.01-1.85] | -0.1882, -0.226, -0.2558, - | -0.185, -0.2232, -0.282, - | -0.206 (z=1.85) |
| UD->OD (14) | 0.00222-0.535 [0.01-0.535] | -0.2327, -0.2811, -, - | -0.2321, -0.2894, -, - | -0.0147 (z=0.535) |

For Fig. 5 there is no right-column panel; the last column is the GR-Newtonian difference rebuilt from the two left-column curves (precision ~1% of 1+|y| where |y| > 0.01). For dbar <= 0.01 this reconstruction agrees with the plotted right column to a few 1e-4 absolute (e.g. dbar = 0.01, OD a_em 28, z = 0.1: 0.0280 rebuilt vs 0.0284 plotted; dbar = 0.0025, OD a_em 163: 0.0153 vs 0.0153).

Largest GR-Newtonian differences (right column, inside the axes, z >= 0.01):

* dbar = 0.01: OD_aem43 0.103 at z = 0.0113; OD_aem28 0.0967 at z = 0.0273; UD_aem27 0.0679 at z = 0.735; UD_aem44 0.0567 at z = 0.776; UD_aem52 0.0492 at z = 0.746; OD_aem52 0.0316 at z = 0.169; UD_aem1 0.00188 at z = 5.05; OD_aem1 0.00145 at z = 5.1. Fraction of drawn (visible) vertices below 1%: OD_aem1 100%, UD_aem1 100%, OD_aem28 68%, UD_aem27 96%, OD_aem43 44%, UD_aem44 83%, OD_aem52 19%, UD_aem52 88%.
* dbar = 0.005: OD_aem58 0.0542 at z = 0.0239; OD_aem112 0.0349 at z = 0.067; UD_aem58 0.0284 at z = 0.488; UD_aem111 0.00829 at z = 0.177; UD_aem28 0.00763 at z = 0.0115; OD_aem28 0.00677 at z = 0.0916; UD_aem1 0.00141 at z = 5.18; OD_aem1 0.0011 at z = 5.29. Fraction of drawn (visible) vertices below 1%: OD_aem1 100%, UD_aem1 100%, OD_aem28 100%, UD_aem28 100%, OD_aem58 68%, UD_aem58 96%, OD_aem112 0%, UD_aem111 100%.
* dbar = 0.0025: OD_aem163 0.0546 at z = 0.011; UD_aem162 0.0193 at z = 0.311; OD_aem59 0.0077 at z = 0.011; OD_aem28 0.00702 at z = 0.0113; UD_aem58 0.00689 at z = 0.0104; UD_aem28 0.00537 at z = 0.0133; UD_aem1 0.000328 at z = 2.5; OD_aem1 0.000298 at z = 1.41. Fraction of drawn (visible) vertices below 1%: OD_aem1 100%, UD_aem1 100%, OD_aem28 100%, UD_aem28 100%, OD_aem59 100%, UD_aem58 100%, OD_aem163 42%, UD_aem162 78%.
* dbar = 0.05 (rebuilt from Fig. 5): OD a_em 8: s = +10 at z = 0.01 (Newtonian D_L 11x the GR one), +1.36 at z = 0.05, +0.41 at 0.1, -0.08 at 0.5, -0.13 at 1; UD a_em 9: -0.21 at z = 1.85 (end of ray), +0.002 to +0.008 for z <= 0.5; a_em ~ 1 rays: up to 1.9% (OD, z = 1.3) and 4.7% (UD, z = 4.6).

Fig. 8 (dbar = 0.01, resolution): maximum |dD/D| inside the axes, high vs low resolution:

| ray | high res: max (z) | low res: max (z) | at z = 0.1 high / low | at z = 0.5 high / low |
|---|---|---|---|---|
| OD_aem1 | 0.00154 (5.1) | 0.00232 (6.02) | 9.8e-05 / 9.76e-05 | 0.000298 / 0.000428 |
| OD_aem28 | 0.0955 (0.0273) | 0.0704 (0.0383) | 0.0281 / 0.0268 | 0.00565 / 0.00508 |
| OD_aem43 | 0.103 (0.0112) | 0.0967 (0.0122) | 0.00325 / 0.00196 | 0.0109 / 0.00824 |
| OD_aem52 | 0.0302 (0.175) | 0.0294 (0.265) | 0.0273 / 0.0207 | 0.0248 / 0.0258 |
| UD_aem1 | 0.00197 (5.05) | 0.00243 (5.55) | 4.13e-05 / 0.000149 | 0.00029 / 0.000479 |
| UD_aem27 | 0.0717 (0.736) | 0.282 (0.737) | 0.00379 / 0.00248 | 0.00264 / 0.00262 |
| UD_aem44 | 0.0538 (0.798) | 0.0462 (0.79) | 0.00274 / 0.00372 | 0.0101/0.00806 / 0.00978 |
| UD_aem52 | 0.0469 (0.786) | 0.0407 (0.761) | 0.0043 / 0.004 | 0.0117/0.012 / 0.0118/0.0125 |

## Fig. 6: constraint convergence (dbar = 0.01)  [vector; <a> +-0.02, norm +-0.3%]

x = <a>, volume-averaged scale factor, linear 0-140; y = <|C_a|>/L^2 as plotted, i.e. multiplied by 1, 2.25, 4 for L/dx = 64 (N_cell^(1/3) = 1, 64^3 particles), 96 (2, 192^3), 128 (4, 512^3); log axis 2e-6 to 1e-2. Curves start at <a> = 1.02-1.035; L/dx = 128 ends at <a> = 81.8.

| <a> | 64: plotted (raw) | 96: plotted (raw) | 128: plotted (raw) |
|---|---|---|---|
| 1.5 | 0.000585 (0.000585) | 0.00029 (0.000129) | 0.0002 (4.99e-05) |
| 2 | 0.000562 (0.000562) | 0.000271 (0.00012) | 0.000182 (4.55e-05) |
| 3 | 0.000324 (0.000324) | 0.000155 (6.9e-05) | 0.000104 (2.6e-05) |
| 5 | 0.00015 (0.00015) | 7.32e-05 (3.25e-05) | 4.92e-05 (1.23e-05) |
| 10 | 6.47e-05 (6.47e-05) | 2.39e-05 (1.06e-05) | 1.67e-05 (4.17e-06) |
| 20 | 5.35e-05 (5.35e-05) | 1.33e-05 (5.89e-06) | 8.5e-06 (2.12e-06) |
| 30 | 3.11e-05 (3.11e-05) | 7.3e-06 (3.24e-06) | 4.31e-06 (1.08e-06) |
| 40 | 4.86e-05 (4.86e-05) | 1.16e-05 (5.14e-06) | 7.47e-06 (1.87e-06) |
| 60 | 4.23e-05 (4.23e-05) | 1.05e-05 (4.66e-06) | 5.49e-06 (1.37e-06) |
| 80 | 4.85e-05 (4.85e-05) | 2.78e-05 (1.24e-05) | 4.53e-05 (1.13e-05) |
| 100 | 5.39e-05 (5.39e-05) | 5.77e-05 (2.57e-05) | - |
| 120 | 4.75e-05 (4.75e-05) | 4.45e-05 (1.98e-05) | - |
| 140 | 7.29e-05 (7.29e-05) | 4.7e-05 (2.09e-05) | - |

The rescaled curves overlap only for L/dx = 64 and 96 at <a> > ~95; earlier the raw norms imply convergence order 3.7-5.6 (64->96) and 3.2-4.3 (96->128), i.e. faster than the second order used for the rescaling.

## Calibration checks against statements in the text

1. Fig. 1 top/middle: every GR curve starts at |delta_obs|(a_p = 1) = 6.644 dbar (all four amplitudes, both points); linear theory for the longitudinal-gauge density of this mode gives 3 dbar (1 + 12/pi^2) = 6.648 dbar. Agreement 0.06%.
2. Fig. 1 top caption ("Newtonian and GR ... essentially indistinguishable"): largest |Newt/GR - 1| is 2.0-2.3% for dbar <= 0.01 and 3.9% for 0.05 (at a_p = 1); about 1.5 pt on the page, below the 2 pt line width.
3. Fig. 1 middle text ("collapse ... slightly earlier for the Newtonian case, and this difference increases" with dbar): GR/Newt a_p at |delta_obs| = 10 is 1.019, 1.058, 1.069, 1.310 for dbar = 0.0025, 0.005, 0.01, 0.05.
4. "Saturation density significantly larger for the Newtonian case" and "with CIC ... much closer to the GR result": plateau medians 5e2-7.5e2 (GR, dbar = 0.005, 0.01), 1.2e5-2.9e6 (Newtonian), CIC 2.4e3 at a_p = 90 for dbar = 0.01.
5. Fig. 1 bottom text ("finite resolution tends to lead [to] an underestimate of the density"; "collapse happens faster in the Newtonian case" even so): a_p at |delta_obs| = 100: GR 58.94 -> 57.21 (high res), GR fluid 55.85 -> 55.17, Newtonian 52.71 -> 52.43; the best GR (55.2) is still later than the Newtonian (52.4).
6. Fig. 2 caption (red/green/blue = x/y/z): with dbar_i = dbar (1, 0.9, 1.1) the z particles should fall in first and the y particles last. a_10 is ordered z < x < y in every panel and both models (e.g. dbar = 0.01, d0 = L/8: GR 63.2, 65.5, 66.8; Newtonian 57.9, 59.4, 60.9), except GR dbar = 0.05 where y falls in before x (z 15.5, y 16.0, x 16.2 for d0 = L/32).
7. Fig. 2 caption ("initial oscillations in the GR curves"): GR d rises above d0 by 8-12% (dbar = 0.05), 1.2-2.1% (0.01), 0.6-1.1% (0.005), 0.3-0.5% (0.0025) by a_p ~ 5-7; Newtonian curves decrease monotonically from the start.
8. Fig. 2 text (discrepancy grows with dbar): GR/Newt ratio of the mean a_10 for d0 = L/16 is 1.060 (dbar=0.0025), 1.064 (dbar=0.005), 1.106 (dbar=0.01); for d0 = L/8 - (dbar=0.0025), 1.057 (dbar=0.005), 1.097 (dbar=0.01); for dbar = 0.05 the Newtonian x and z particles with d0 <= L/16 reach 0.1 d0 at a_p = 10.5-10.8, just before the run stops, against 15.5-16.3 in GR (ratio ~1.5), and the other Newtonian particles never do.
9. Fig. 3: initial speeds equal (H0 dbar/k) sin(k d0) for x particles to 1% (3.15e-4, 2.47e-3, 6.44e-3 read vs 3.11e-4, 2.44e-3, 6.37e-3), confirming the legend, k = pi H0/2 and L = 4/H0; the end values match |d_N - d_GR| rebuilt from Fig. 2 (0.0133 vs 0.0132-0.0145; 0.0034 vs 0.0022-0.0036).
10. Fig. 4 text (OD rays emitted late: GR D_L slightly smaller than Newtonian at small z, larger at larger z): from the left column, s = D_N/D_GR - 1 for dbar = 0.01 is +0.092/+0.028/-0.006 (a_em 28, z = 0.02/0.1/0.5) and +0.068/+0.003/-0.011 (a_em 43): positive at small z, negative beyond the dip, as stated; for a_em 52 s is positive only for z < ~0.03.
11. Fig. 4 text (blueshift near the overdensity, top panel): z turns back along the UD->OD rays of dbar = 0.01 with a_em 27, 44, 52 (z_max 0.735, 0.796, 0.771; ray ends at 0.695, 0.482, 0.408); no UD ray turns back for dbar = 0.005 or 0.0025.
12. Fig. 4 text ("in most cases subpercent"; UD rays subpercent "until the overdensity is approached"): UD rays stay below 1% over 78-100% of their drawn vertices and exceed it only over the last part of the ray, towards the halo; the a_em ~ 1 rays stay below 0.2% everywhere; OD rays emitted after collapse reach 3-10% (dbar = 0.01: 9.7%, 10.3%, 3.2%; 0.005: 5.4%, 3.5%; 0.0025: 5.5% for the last ray) at small z.
13. Appendix (resolution changes the first crossing much less than GR vs Newtonian): dbar = 0.01, d0 = L/8, x: GR 70.08 (low) vs 68.13 (high), Newtonian 60.25 vs 60.19, GR - Newt 7.9. Subsequent oscillations differ more (first GR apocentre 84.7 vs 77.5).
14. Fig. 6 caption factors: 2.25 = (96/64)^2 and 4.00 = (128/64)^2, as printed in the legend.
15. Fig. 7 vs Fig. 2: the "High res." halves reproduce Fig. 2 (dbar = 0.01): Newtonian exactly, GR to <= 3.4e-4 in d/L.

## Figures versus text: contradictions and tensions

1. **Fig. 8 caption** says "similar to the top left panel of Fig. 4", but the plotted quantity, |D_L^Newt/D_L^GR - 1|, is that of the top *right* panel.
2. **GR particle numbers are inconsistent.** Text: default 96 points per wavelength with 4^3 particles per cell (384^3). Fig. 6 legend: L/dx = 64, 96, 128 with N_cell^(1/3) = 1, 2, 4, i.e. 64^3, 192^3, 512^3 particles (the 96-point run has 2^3 per cell). Fig. 7 caption: GR 128^3 and 384^3. Fig. 8 caption: GR 192^3 and 512^3. Fig. 2 equals the Fig. 7 "high" run (384^3 by that caption).
3. **Fig. 1 bottom "GR OD" is not the default GR run of Fig. 1 middle**: the middle-panel GR dbar = 0.01 curve differs from both bottom-panel GR particle curves by up to 0.3-0.4 dex after collapse and lies between them in collapse time (|delta_obs| = 100 at a_p 58.0 vs 58.9 "GR OD" and 57.2 "High Res."). Their resolutions are not stated. Likewise "Newt. OD" in the bottom panel is the low-resolution (128^3) run and "Newt. OD High Res." the default 196^3 run, which the legend wording does not make clear.
4. **"15-fold increase of scale factor"** for the Newtonian dbar = 0.05 run cannot be matched to the plotted a_p: the Newtonian curves end at a_p = 10.86 (halo density), 10.8-11.2 and 13.3-13.9 (particles) and 22.7 (void density). A void observer at a_p = 22.7 would need a proper time 1.86x the background time if the background scale factor were 15, far more than a potential |psi| < 1/2 allows; so either "15" refers to another clock or the void curve runs longer.
5. **Initial-condition match at dbar = 0.05**: the text says the mass corrections "guarantee a high-accuracy match" of the Newtonian and GR initial conditions, but at a_p = 1 the Newtonian |delta_obs| is 0.347 (halo) and 0.319 (void) against 0.332 for GR (+4.5%, -4.0%). For dbar = 0.01 the mismatch is +0.8% / -0.4%, smaller amplitudes less.
6. **Eq. (1) vs the stated extremum positions** (text only): with delta_N = sum dbar_i sin(k x^i) the density contrast is zero at (0,0,0) and (pi/k, pi/k, pi/k), not maximal/minimal; the stated positions need cos(k x^i) (and then v^i proportional to sin(k x^i), not cos). The figures are consistent with |v| = (H0 dbar_i/k) sin(k d) at distance d from the peak.
7. **Newtonian dbar = 0.005 particle offsets**: in Fig. 2 bottom left the Newtonian particles start 0.0013-0.0015 L farther out than the nominal L/32, L/16, L/8, L/4 used everywhere else (GR half of the same panel is nominal).
8. **Fig. 6**: the rescaled curves do not coincide at <a> < ~80 (convergence faster than the assumed second order), which the caption does not mention; they coincide (64 vs 96) only at late times, where the caption says particle noise dominates.
9. **Fig. 2, dbar = 0.05 GR**: y particles fall in before x particles although dbar_y = 0.9 dbar < dbar_x (all other panels and the Newtonian runs follow z, x, y).

## Not extracted or not recoverable

* Parts of curves outside the page were never written to the EPS: Fig. 1 bottom above |delta_obs| = 2.35e4 (both Newtonian curves, the high-resolution fluid curve, the fluid peak region), Fig. 2 dbar = 0.05 GR d0 = L/4 curves above d/L = 0.28 (a_p ~ 4.2-7.5), Fig. 3 orange curve beyond |v| = 0.511, right-column D_L dips below 1.55e-5 (1.43e-5 in Fig. 8). Hidden-but-present parts (outside the axes, inside the page) are in the CSVs with visible = 0.
* The underlying sample times: matplotlib dropped vertices on near-straight stretches, so the CSV vertices are not the simulation output times (except where the curve bends at every sample, e.g. the Newtonian particle curves).
* Newtonian crossing times to better than about half a snapshot spacing (~0.7 in a_p for dbar = 0.01, ~3 for 0.0025).
* The resolution of the Fig. 1 bottom GR curves and which GR particle number each figure used (inconsistent statements, see above).
* Fig. 3: which simulation output each point corresponds to (only |v| is given), and the y and z particles (not plotted).
* Fig. 5 has no GR-Newtonian panel; differences there are rebuilt from the left-column curves with ~1% precision.
* Absolute D_L or z of the rays (only ratios to the LFRW solution and between models are plotted); the exact emission times beyond the rounded legend values (a_em ~ 1, 27, 28, ...).
* The Newtonian potential psi and the GR metric (not plotted); the a_p <-> coordinate-time relation for each curve.

