# res_delta10em2pm_splash: Fig. 7 top (appendix, GR)

Source: `refs/arxiv_1908.05683/src/res_delta10em2pm_splash.eps` (matplotlib 1.5.1, vector). Paper: East, Wojtak & Pretorius, arXiv:1908.05683.

## What is plotted
As Fig. 2 (dbar = 0.01), GR only: top half +d/L from the low-resolution run (caption: N=128^3), bottom half -d/L from the high-resolution run (caption: N=384^3).

## Files
* `res_delta10em2pm_splash.csv`: long format, columns `curve, segment, a_p, plotted_y (= +d/L top half, -d/L bottom half), visible, canvas_edge` (see the header comments).
* `curves.csv`: one row per curve with colour, line style and metadata.
* `check_res_delta10em2pm_splash.png`: the original EPS rendered with ghostscript (left) next to a replot of the CSV in data coordinates with the same axis limits and scales (right).

## Calibration
Curves are the stroked PostScript polylines; colour and dash pattern come from the setrgbcolor/setdash state; axes from the clip box; data coordinates from a least-squares fit of the major tick positions (tick marks paired with their labels in drawing order).
* x: lin axis: pos = 91.732700 + 5.122905 * f(v); ticks used: 0@91.733, 20@194.191, 40@296.649, 60@399.107, 80@501.565; max |residual| = 0.0002 pt
* y: lin axis: pos = 237.870700 + 696.806000 * f(v); ticks used: -0.2@98.510, -0.1@168.190, 0@237.871, 0.1@307.551, 0.2@377.232; max |residual| = 0.0003 pt
* Axes box in data units: x in [-0.00052704, 91.998], y in [-0.26, 0.25994].

## Accuracy
matplotlib simplified the paths with a tolerance of 1/9 pt (vertices within 0.11 pt of a straight run were dropped); coordinates are written to 1e-6 pt and the tick fit residual is < 1e-3 pt. Reading error: x +-0.022 data units, y +-0.00016 data units. Between vertices the curve is the straight line that was drawn (in display coordinates).

## Curves

| curve | colour | line | meaning | a_p range | points |
|---|---|---|---|---|---|
| `GRlow_x_d0_0.03125` | red | solid | half=top (plotted +d/L); model=GR; resolution=low (caption: N=128^3); dbar=0.01; direction=x; d0_nominal=0.03125; d0_plotted=0.03125 | 1-92 | 36 |
| `GRlow_x_d0_0.0625` | red | dotted [1 3] | half=top (plotted +d/L); model=GR; resolution=low (caption: N=128^3); dbar=0.01; direction=x; d0_nominal=0.0625; d0_plotted=0.0625 | 1-92 | 51 |
| `GRlow_x_d0_0.125` | red | dashed [6 6] | half=top (plotted +d/L); model=GR; resolution=low (caption: N=128^3); dbar=0.01; direction=x; d0_nominal=0.125; d0_plotted=0.125 | 1-92 | 69 |
| `GRlow_x_d0_0.25` | red | dash-dot [3 5 1 5] | half=top (plotted +d/L); model=GR; resolution=low (caption: N=128^3); dbar=0.01; direction=x; d0_nominal=0.25; d0_plotted=0.25 | 1-92 | 79 |
| `GRlow_y_d0_0.03125` | green (mpl "g") | solid | half=top (plotted +d/L); model=GR; resolution=low (caption: N=128^3); dbar=0.01; direction=y; d0_nominal=0.03125; d0_plotted=0.03125 | 1-92 | 36 |
| `GRlow_y_d0_0.0625` | green (mpl "g") | dotted [1 3] | half=top (plotted +d/L); model=GR; resolution=low (caption: N=128^3); dbar=0.01; direction=y; d0_nominal=0.0625; d0_plotted=0.0625 | 1-92 | 50 |
| `GRlow_y_d0_0.125` | green (mpl "g") | dashed [6 6] | half=top (plotted +d/L); model=GR; resolution=low (caption: N=128^3); dbar=0.01; direction=y; d0_nominal=0.125; d0_plotted=0.125 | 1-92 | 67 |
| `GRlow_y_d0_0.25` | green (mpl "g") | dash-dot [3 5 1 5] | half=top (plotted +d/L); model=GR; resolution=low (caption: N=128^3); dbar=0.01; direction=y; d0_nominal=0.25; d0_plotted=0.25 | 1-92 | 76 |
| `GRlow_z_d0_0.03125` | blue | solid | half=top (plotted +d/L); model=GR; resolution=low (caption: N=128^3); dbar=0.01; direction=z; d0_nominal=0.03125; d0_plotted=0.03125 | 1-92.01 | 35 |
| `GRlow_z_d0_0.0625` | blue | dotted [1 3] | half=top (plotted +d/L); model=GR; resolution=low (caption: N=128^3); dbar=0.01; direction=z; d0_nominal=0.0625; d0_plotted=0.0625 | 1-92.01 | 50 |
| `GRlow_z_d0_0.125` | blue | dashed [6 6] | half=top (plotted +d/L); model=GR; resolution=low (caption: N=128^3); dbar=0.01; direction=z; d0_nominal=0.125; d0_plotted=0.125 | 1-92 | 68 |
| `GRlow_z_d0_0.25` | blue | dash-dot [3 5 1 5] | half=top (plotted +d/L); model=GR; resolution=low (caption: N=128^3); dbar=0.01; direction=z; d0_nominal=0.25; d0_plotted=0.25 | 1-92.01 | 79 |
| `GRhigh_x_d0_0.03125` | red | solid | half=bottom (plotted -d/L); model=GR; resolution=high (caption: N=384^3); dbar=0.01; direction=x; d0_nominal=0.03125; d0_plotted=0.03125 | 1-92.01 | 43 |
| `GRhigh_x_d0_0.0625` | red | dotted [1 3] | half=bottom (plotted -d/L); model=GR; resolution=high (caption: N=384^3); dbar=0.01; direction=x; d0_nominal=0.0625; d0_plotted=0.0625 | 1-92 | 61 |
| `GRhigh_x_d0_0.125` | red | dashed [6 6] | half=bottom (plotted -d/L); model=GR; resolution=high (caption: N=384^3); dbar=0.01; direction=x; d0_nominal=0.125; d0_plotted=0.125 | 1-92.01 | 83 |
| `GRhigh_x_d0_0.25` | red | dash-dot [3 5 1 5] | half=bottom (plotted -d/L); model=GR; resolution=high (caption: N=384^3); dbar=0.01; direction=x; d0_nominal=0.25; d0_plotted=0.25 | 1-92 | 86 |
| `GRhigh_y_d0_0.03125` | green (mpl "g") | solid | half=bottom (plotted -d/L); model=GR; resolution=high (caption: N=384^3); dbar=0.01; direction=y; d0_nominal=0.03125; d0_plotted=0.03125 | 1-92 | 41 |
| `GRhigh_y_d0_0.0625` | green (mpl "g") | dotted [1 3] | half=bottom (plotted -d/L); model=GR; resolution=high (caption: N=384^3); dbar=0.01; direction=y; d0_nominal=0.0625; d0_plotted=0.0625 | 1-92.01 | 57 |
| `GRhigh_y_d0_0.125` | green (mpl "g") | dashed [6 6] | half=bottom (plotted -d/L); model=GR; resolution=high (caption: N=384^3); dbar=0.01; direction=y; d0_nominal=0.125; d0_plotted=0.125 | 1-92 | 81 |
| `GRhigh_y_d0_0.25` | green (mpl "g") | dash-dot [3 5 1 5] | half=bottom (plotted -d/L); model=GR; resolution=high (caption: N=384^3); dbar=0.01; direction=y; d0_nominal=0.25; d0_plotted=0.25 | 1-92.01 | 80 |
| `GRhigh_z_d0_0.03125` | blue | solid | half=bottom (plotted -d/L); model=GR; resolution=high (caption: N=384^3); dbar=0.01; direction=z; d0_nominal=0.03125; d0_plotted=0.03125 | 1-92 | 41 |
| `GRhigh_z_d0_0.0625` | blue | dotted [1 3] | half=bottom (plotted -d/L); model=GR; resolution=high (caption: N=384^3); dbar=0.01; direction=z; d0_nominal=0.0625; d0_plotted=0.0625 | 1-92 | 57 |
| `GRhigh_z_d0_0.125` | blue | dashed [6 6] | half=bottom (plotted -d/L); model=GR; resolution=high (caption: N=384^3); dbar=0.01; direction=z; d0_nominal=0.125; d0_plotted=0.125 | 1-91.96 | 78 |
| `GRhigh_z_d0_0.25` | blue | dash-dot [3 5 1 5] | half=bottom (plotted -d/L); model=GR; resolution=high (caption: N=384^3); dbar=0.01; direction=z; d0_nominal=0.25; d0_plotted=0.25 | 1-92 | 85 |

## Derived numbers
`turning_points.csv`, one row per particle: initial plotted distance d0; a_p where d first drops below 0.1 d0 and
0.05 d0 (robust infall markers); the first crossing = first local minimum of d after d < 0.15 d0, with the a_p
interval over which the drawn d stays within max(5e-4, 0.02 d0) of that minimum; up to four following turning points
(hysteresis max(5e-4, 0.04 d0)); end point. d >= 0 is a distance (the GR half never goes below 0 and the Newtonian
half never above 0), so a crossing is a near-zero minimum, not a sign change.

Sampling: the Newtonian curves have one vertex per output (spacing ~1.3 in a_p near a_p ~ 57 for dbar = 0.01, ~2.7
near 115 for 0.005, ~5.6 near 230 for 0.0025), so Newtonian crossing times are uncertain by about half that spacing.
GR curves are sampled finely but matplotlib dropped vertices on near-straight stretches.

