# 10m2_cnst_conv: Fig. 6 (appendix)

Source: `refs/arxiv_1908.05683/src/10m2_cnst_conv.eps` (matplotlib 1.5.1, vector). Paper: East, Wojtak & Pretorius, arXiv:1908.05683.

## What is plotted
L2 norm of the generalized-harmonic constraint C_a = H_a - Box x_a (divided by L^2) against the volume-averaged scale factor <a>, dbar = 0.01, three GR resolutions, rescaled assuming second-order convergence (factors 1, 2.25, 4 as in the legend).

## Files
* `10m2_cnst_conv.csv`: long format, columns `curve, segment, a_avg, scaled_constraint_norm, visible, canvas_edge` (see the header comments).
* `curves.csv`: one row per curve with colour, line style and metadata.
* `check_10m2_cnst_conv.png`: the original EPS rendered with ghostscript (left) next to a replot of the CSV in data coordinates with the same axis limits and scales (right).

## Calibration
Curves are the stroked PostScript polylines; colour and dash pattern come from the setrgbcolor/setdash state; axes from the clip box; data coordinates from a least-squares fit of the major tick positions (tick marks paired with their labels in drawing order).
* x: lin axis: pos = 109.048833 + 5.072124 * f(v); ticks used: 0@109.049, 20@210.491, 40@311.934, 60@413.376, 80@514.819, 100@616.261, 120@717.704, 140@819.146; max |residual| = 0.0003 pt
* y: log axis: pos = 562.964100 + 83.875600 * f(v); ticks used: 1e-05@143.586, 0.0001@227.462, 0.001@311.337, 0.01@395.213; max |residual| = 0.0003 pt
* Axes box in data units: x in [-0.0096278, 139.99], y in [2e-06, 0.010013].

## Accuracy
matplotlib simplified the paths with a tolerance of 1/9 pt (vertices within 0.11 pt of a straight run were dropped); coordinates are written to 1e-6 pt and the tick fit residual is < 1e-3 pt. Reading error: x +-0.022 data units, y +-0.31% (0.0013 dex). Between vertices the curve is the straight line that was drawn (in display coordinates).

## Curves

| curve | colour | line | meaning | a_avg range | points |
|---|---|---|---|---|---|
| `Ldx64` | black | solid | L_over_dx=64; Ncell_cuberoot=1; N_particles=64^3; plotted_scale_factor=1.0; dbar=0.01; note=plotted value = (L2 norm of C_a)/L^2 x factor | 1.035-140 | 206 |
| `Ldx96` | blue | dashed [6 6] | L_over_dx=96; Ncell_cuberoot=2; N_particles=192^3; plotted_scale_factor=2.25; dbar=0.01; note=plotted value = (L2 norm of C_a)/L^2 x factor | 1.022-140 | 195 |
| `Ldx128` | green (mpl "g") | dash-dot [3 5 1 5] | L_over_dx=128; Ncell_cuberoot=4; N_particles=512^3; plotted_scale_factor=4.0; dbar=0.01; note=plotted value = (L2 norm of C_a)/L^2 x factor | 1.016-81.77 | 166 |

## Derived numbers
`values_at_a.csv`: plotted (rescaled) and raw (= plotted / factor) norms at selected <a>.

## Notes
* The rescaled curves do not overlap for <a> < ~80: the implied convergence order between L/dx = 64 and 96 is
  3.7-3.8 for <a> < 5 and ~5.5 for 20 < <a> < 60, and 3.3-4.3 between 96 and 128; the 64 and 96 curves meet only for
  <a> > ~95 (order ~2 there), where the caption says finite-particle error takes over.
* All three curves start with a spike at <a> ~ 1.04-1.07 (plotted 3.96e-3, 1.86e-3, 1.21e-3). The L/dx = 128 curve
  ends at <a> = 81.8.

