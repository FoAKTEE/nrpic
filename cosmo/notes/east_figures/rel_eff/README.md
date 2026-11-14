# rel_eff: Fig. 3

Source: `refs/arxiv_1908.05683/src/rel_eff.eps` (gnuplot 5.2, vector). Paper: East, Wojtak & Pretorius, arXiv:1908.05683.

## What is plotted
|d_OD^Newt - d_OD^GR|/L for three fiducial particles of Fig. 2 against the magnitude of the infall velocity from the Newtonian run, up to the first Newtonian halo crossing. gnuplot figure.

## Files
* `rel_eff.csv`: long format, columns `curve, segment, abs_v_infall, abs_dNewt_minus_dGR_over_L, visible, canvas_edge` (see the header comments).
* `curves.csv`: one row per curve with colour, line style and metadata.
* `check_rel_eff.png`: the original EPS rendered with ghostscript (left) next to a replot of the CSV in data coordinates with the same axis limits and scales (right).

## Calibration
Curves are the stroked PostScript polylines; colour and dash pattern come from the setrgbcolor/setdash state; axes from the clip box; data coordinates from a least-squares fit of the major tick positions (tick marks paired with their labels in drawing order).
* x: log axis: pos = 8669.333333 + 2082.500000 * f(v); ticks used: 0.001@2422.000, 0.01@4504.000, 0.1@6587.000; max |residual| = 0.3333 pt
* y: log axis: pos = 8712.700000 + 1473.700000 * f(v); ticks used: 1e-05@1344.000, 0.0001@2818.000, 0.001@4292.000, 0.01@5765.000, 0.1@7239.000; max |residual| = 0.4000 pt
* Axes box in data units: x in [0.00031463, 0.51093], y in [9.9969e-06, 0.1].

## Accuracy
gnuplot writes integer coordinates in 0.05 pt units and does not simplify paths, so the reading error is +-0.025 pt: x +-0.06% (0.0002 dex), y +-0.08% (0.0003 dex).

## Curves

| curve | colour | line | meaning | abs_v_infall range | points |
|---|---|---|---|---|---|
| `dbar0.0025_d0_0.031` | purple (gnuplot 0.58,0,0.83) | solid | dbar=0.0025; d0_label=0.031; plot_block=1; quantity=|d_OD^Newt - d_OD^GR|/L vs |v_infall| (Newtonian), up to first Newtonian halo crossing | 0.0003146-0.005726 | 220 |
| `dbar0.01_d0_0.063` | teal green (gnuplot 0,0.62,0.45) | solid | dbar=0.01; d0_label=0.063; plot_block=2; quantity=|d_OD^Newt - d_OD^GR|/L vs |v_infall| (Newtonian), up to first Newtonian halo crossing | 0.002466-0.1433 | 165 |
| `dbar0.01_d0_0.25` | orange (gnuplot 0.9,0.62,0) | solid | dbar=0.01; d0_label=0.25; plot_block=3; quantity=|d_OD^Newt - d_OD^GR|/L vs |v_infall| (Newtonian), up to first Newtonian halo crossing | 0.006445-0.5109 | 178 |

## Checks
* The first point of each curve is the initial Zel'dovich speed of an x-displaced particle,
  |v| = (H0 dbar / k) sin(k d0) with k = 2 pi / L and H0/k = 2/pi: predicted 3.11e-4, 2.44e-3, 6.37e-3; read
  3.15e-4, 2.47e-3, 6.44e-3 (1% agreement). This confirms the x calibration, L = one wavelength = 4/H0, and that the
  third curve is dbar = 0.01 with d0 = L/4 as labelled (dbar = 0.05 would start at 3.2e-2). All three are x-direction
  particles (y and z would start 10% lower/higher).
* Rebuilding |d_N - d_GR|/L from Fig. 2 at the first Newtonian crossing gives 0.0132-0.0145 (dbar = 0.01, d0 = L/16, x and
  y directions) against 0.0133 at the end of the teal curve, and 0.0022-0.0036 (dbar = 0.0025, d0 = L/32) against
  0.0034 at the end of the purple curve.

## Notes
* The orange curve leaves the plot at the right edge (|v| = 0.511, value 0.052); the rest of it is not in the file.
* Each curve ends with a vertical segment (purple at |v| = 0.0057, teal and orange where marked), i.e. |dd| keeps
  changing while |v| does not.
* `envelope.csv`: upper envelope and median of the three curves in bins of |v| (0.25 dex).

