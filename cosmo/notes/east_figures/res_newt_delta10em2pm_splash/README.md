# res_newt_delta10em2pm_splash: Fig. 7 bottom (appendix, Newtonian)

Source: `refs/arxiv_1908.05683/src/res_newt_delta10em2pm_splash.eps` (matplotlib 1.5.1, vector). Paper: East, Wojtak & Pretorius, arXiv:1908.05683.

## What is plotted
As Fig. 2 (dbar = 0.01), Newtonian only: top half +d/L from N=128^3, bottom half -d/L from N=196^3 (caption).

## Files
* `res_newt_delta10em2pm_splash.csv`: long format, columns `curve, segment, a_p, plotted_y (= +d/L top half, -d/L bottom half), visible, canvas_edge` (see the header comments).
* `curves.csv`: one row per curve with colour, line style and metadata.
* `check_res_newt_delta10em2pm_splash.png`: the original EPS rendered with ghostscript (left) next to a replot of the CSV in data coordinates with the same axis limits and scales (right).

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
| `Newtlow_x_d0_0.03125` | red | solid | half=top (plotted +d/L); model=Newtonian; resolution=low (caption: N=128^3); dbar=0.01; direction=x; d0_nominal=0.03125; d0_plotted=0.03124 | 1-90.71 | 37 |
| `Newtlow_x_d0_0.0625` | red | dotted [1 3] | half=top (plotted +d/L); model=Newtonian; resolution=low (caption: N=128^3); dbar=0.01; direction=x; d0_nominal=0.0625; d0_plotted=0.06245 | 1-90.89 | 41 |
| `Newtlow_x_d0_0.125` | red | dashed [6 6] | half=top (plotted +d/L); model=Newtonian; resolution=low (caption: N=128^3); dbar=0.01; direction=x; d0_nominal=0.125; d0_plotted=0.12491 | 1-92.25 | 44 |
| `Newtlow_x_d0_0.25` | red | dash-dot [3 5 1 5] | half=top (plotted +d/L); model=Newtonian; resolution=low (caption: N=128^3); dbar=0.01; direction=x; d0_nominal=0.25; d0_plotted=0.25 | 1-94.73 | 43 |
| `Newtlow_y_d0_0.03125` | green (mpl "g") | solid | half=top (plotted +d/L); model=Newtonian; resolution=low (caption: N=128^3); dbar=0.01; direction=y; d0_nominal=0.03125; d0_plotted=0.03116 | 1-90.71 | 34 |
| `Newtlow_y_d0_0.0625` | green (mpl "g") | dotted [1 3] | half=top (plotted +d/L); model=Newtonian; resolution=low (caption: N=128^3); dbar=0.01; direction=y; d0_nominal=0.0625; d0_plotted=0.06253 | 1-90.65 | 41 |
| `Newtlow_y_d0_0.125` | green (mpl "g") | dashed [6 6] | half=top (plotted +d/L); model=Newtonian; resolution=low (caption: N=128^3); dbar=0.01; direction=y; d0_nominal=0.125; d0_plotted=0.12504 | 1-91.87 | 45 |
| `Newtlow_y_d0_0.25` | green (mpl "g") | dash-dot [3 5 1 5] | half=top (plotted +d/L); model=Newtonian; resolution=low (caption: N=128^3); dbar=0.01; direction=y; d0_nominal=0.25; d0_plotted=0.24992 | 1-94.73 | 41 |
| `Newtlow_z_d0_0.03125` | blue | solid | half=top (plotted +d/L); model=Newtonian; resolution=low (caption: N=128^3); dbar=0.01; direction=z; d0_nominal=0.03125; d0_plotted=0.03126 | 1-91.08 | 37 |
| `Newtlow_z_d0_0.0625` | blue | dotted [1 3] | half=top (plotted +d/L); model=Newtonian; resolution=low (caption: N=128^3); dbar=0.01; direction=z; d0_nominal=0.0625; d0_plotted=0.06259 | 1-90.95 | 39 |
| `Newtlow_z_d0_0.125` | blue | dashed [6 6] | half=top (plotted +d/L); model=Newtonian; resolution=low (caption: N=128^3); dbar=0.01; direction=z; d0_nominal=0.125; d0_plotted=0.12496 | 1-90.9 | 46 |
| `Newtlow_z_d0_0.25` | blue | dash-dot [3 5 1 5] | half=top (plotted +d/L); model=Newtonian; resolution=low (caption: N=128^3); dbar=0.01; direction=z; d0_nominal=0.25; d0_plotted=0.24992 | 1-94.73 | 43 |
| `Newthigh_x_d0_0.03125` | red | solid | half=bottom (plotted -d/L); model=Newtonian; resolution=high (caption: N=196^3); dbar=0.01; direction=x; d0_nominal=0.03125; d0_plotted=0.03132 | 1-90.22 | 35 |
| `Newthigh_x_d0_0.0625` | red | dotted [1 3] | half=bottom (plotted -d/L); model=Newtonian; resolution=high (caption: N=196^3); dbar=0.01; direction=x; d0_nominal=0.0625; d0_plotted=0.06257 | 1-90.35 | 38 |
| `Newthigh_x_d0_0.125` | red | dashed [6 6] | half=bottom (plotted -d/L); model=Newtonian; resolution=high (caption: N=196^3); dbar=0.01; direction=x; d0_nominal=0.125; d0_plotted=0.12501 | 1-91.62 | 45 |
| `Newthigh_x_d0_0.25` | red | dash-dot [3 5 1 5] | half=bottom (plotted -d/L); model=Newtonian; resolution=high (caption: N=196^3); dbar=0.01; direction=x; d0_nominal=0.25; d0_plotted=0.25008 | 1-94.73 | 43 |
| `Newthigh_y_d0_0.03125` | green (mpl "g") | solid | half=bottom (plotted -d/L); model=Newtonian; resolution=high (caption: N=196^3); dbar=0.01; direction=y; d0_nominal=0.03125; d0_plotted=0.0313 | 1-90.04 | 37 |
| `Newthigh_y_d0_0.0625` | green (mpl "g") | dotted [1 3] | half=bottom (plotted -d/L); model=Newtonian; resolution=high (caption: N=196^3); dbar=0.01; direction=y; d0_nominal=0.0625; d0_plotted=0.06255 | 1-90.22 | 42 |
| `Newthigh_y_d0_0.125` | green (mpl "g") | dashed [6 6] | half=bottom (plotted -d/L); model=Newtonian; resolution=high (caption: N=196^3); dbar=0.01; direction=y; d0_nominal=0.125; d0_plotted=0.12508 | 1-91.54 | 45 |
| `Newthigh_y_d0_0.25` | green (mpl "g") | dash-dot [3 5 1 5] | half=bottom (plotted -d/L); model=Newtonian; resolution=high (caption: N=196^3); dbar=0.01; direction=y; d0_nominal=0.25; d0_plotted=0.25005 | 1-94.73 | 41 |
| `Newthigh_z_d0_0.03125` | blue | solid | half=bottom (plotted -d/L); model=Newtonian; resolution=high (caption: N=196^3); dbar=0.01; direction=z; d0_nominal=0.03125; d0_plotted=0.03126 | 1-90.3 | 35 |
| `Newthigh_z_d0_0.0625` | blue | dotted [1 3] | half=bottom (plotted -d/L); model=Newtonian; resolution=high (caption: N=196^3); dbar=0.01; direction=z; d0_nominal=0.0625; d0_plotted=0.0625 | 1-90.43 | 39 |
| `Newthigh_z_d0_0.125` | blue | dashed [6 6] | half=bottom (plotted -d/L); model=Newtonian; resolution=high (caption: N=196^3); dbar=0.01; direction=z; d0_nominal=0.125; d0_plotted=0.12501 | 1-91.53 | 46 |
| `Newthigh_z_d0_0.25` | blue | dash-dot [3 5 1 5] | half=bottom (plotted -d/L); model=Newtonian; resolution=high (caption: N=196^3); dbar=0.01; direction=z; d0_nominal=0.25; d0_plotted=0.25002 | 1-94.23 | 43 |

## Derived numbers
`turning_points.csv`, one row per particle: initial plotted distance d0; a_p where d first drops below 0.1 d0 and
0.05 d0 (robust infall markers); the first crossing = first local minimum of d after d < 0.15 d0, with the a_p
interval over which the drawn d stays within max(5e-4, 0.02 d0) of that minimum; up to four following turning points
(hysteresis max(5e-4, 0.04 d0)); end point. d >= 0 is a distance (the GR half never goes below 0 and the Newtonian
half never above 0), so a crossing is a near-zero minimum, not a sign change.

Sampling: the Newtonian curves have one vertex per output (spacing ~1.3 in a_p near a_p ~ 57 for dbar = 0.01, ~2.7
near 115 for 0.005, ~5.6 near 230 for 0.0025), so Newtonian crossing times are uncertain by about half that spacing.
GR curves are sampled finely but matplotlib dropped vertices on near-straight stretches.

