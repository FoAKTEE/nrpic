# delta10em2pm_splash: Fig. 2 top right (dbar=0.01)

Source: `refs/arxiv_1908.05683/src/delta10em2pm_splash.eps` (matplotlib 1.5.1, vector). Paper: East, Wojtak & Pretorius, arXiv:1908.05683.

## What is plotted
Coordinate distance d (>= 0) from the point of maximum density, divided by the box length L, of 12 fiducial particles against their own proper-time scale factor a_p. Top half: +d/L from the GR run; bottom half: -d/L from the Newtonian run. Colour = initial displacement direction (red x, green y, blue z); line style = initial distance (solid L/32, dotted L/16, dashed L/8, dash-dot L/4).

## Files
* `delta10em2pm_splash.csv`: long format, columns `curve, segment, a_p, plotted_y (= +d/L top half, -d/L bottom half), visible, canvas_edge` (see the header comments).
* `curves.csv`: one row per curve with colour, line style and metadata.
* `check_delta10em2pm_splash.png`: the original EPS rendered with ghostscript (left) next to a replot of the CSV in data coordinates with the same axis limits and scales (right).

## Calibration
Curves are the stroked PostScript polylines; colour and dash pattern come from the setrgbcolor/setdash state; axes from the clip box; data coordinates from a least-squares fit of the major tick positions (tick marks paired with their labels in drawing order).
* x: lin axis: pos = 84.464500 + 5.157070 * f(v); ticks used: 20@187.606, 40@290.747, 60@393.889, 80@497.030; max |residual| = 0.0003 pt
* y: lin axis: pos = 237.870700 + 696.806000 * f(v); ticks used: -0.2@98.510, -0.1@168.190, 0@237.871, 0.1@307.551, 0.2@377.232; max |residual| = 0.0003 pt
* Axes box in data units: x in [0.9997, 92.796], y in [-0.26, 0.25994].

## Accuracy
matplotlib simplified the paths with a tolerance of 1/9 pt (vertices within 0.11 pt of a straight run were dropped); coordinates are written to 1e-6 pt and the tick fit residual is < 1e-3 pt. Reading error: x +-0.022 data units, y +-0.00016 data units. Between vertices the curve is the straight line that was drawn (in display coordinates).

## Curves

| curve | colour | line | meaning | a_p range | points |
|---|---|---|---|---|---|
| `GR_x_d0_0.03125` | red | solid | half=top (plotted +d/L); model=GR; resolution=default (96 points per wavelength; caption of Fig. 7 implies N=384^3 particles); dbar=0.01; direction=x; d0_nominal=0.03125; d0_plotted=0.03125 | 1-92.8 | 44 |
| `GR_x_d0_0.0625` | red | dotted [1 3] | half=top (plotted +d/L); model=GR; resolution=default (96 points per wavelength; caption of Fig. 7 implies N=384^3 particles); dbar=0.01; direction=x; d0_nominal=0.0625; d0_plotted=0.0625 | 1-92.62 | 61 |
| `GR_x_d0_0.125` | red | dashed [6 6] | half=top (plotted +d/L); model=GR; resolution=default (96 points per wavelength; caption of Fig. 7 implies N=384^3 particles); dbar=0.01; direction=x; d0_nominal=0.125; d0_plotted=0.125 | 1-92.24 | 83 |
| `GR_x_d0_0.25` | red | dash-dot [3 5 1 5] | half=top (plotted +d/L); model=GR; resolution=default (96 points per wavelength; caption of Fig. 7 implies N=384^3 particles); dbar=0.01; direction=x; d0_nominal=0.25; d0_plotted=0.25 | 1-92.51 | 84 |
| `GR_y_d0_0.03125` | green (mpl "g") | solid | half=top (plotted +d/L); model=GR; resolution=default (96 points per wavelength; caption of Fig. 7 implies N=384^3 particles); dbar=0.01; direction=y; d0_nominal=0.03125; d0_plotted=0.03125 | 1-92.79 | 42 |
| `GR_y_d0_0.0625` | green (mpl "g") | dotted [1 3] | half=top (plotted +d/L); model=GR; resolution=default (96 points per wavelength; caption of Fig. 7 implies N=384^3 particles); dbar=0.01; direction=y; d0_nominal=0.0625; d0_plotted=0.0625 | 1-92.61 | 58 |
| `GR_y_d0_0.125` | green (mpl "g") | dashed [6 6] | half=top (plotted +d/L); model=GR; resolution=default (96 points per wavelength; caption of Fig. 7 implies N=384^3 particles); dbar=0.01; direction=y; d0_nominal=0.125; d0_plotted=0.125 | 1-92.3 | 81 |
| `GR_y_d0_0.25` | green (mpl "g") | dash-dot [3 5 1 5] | half=top (plotted +d/L); model=GR; resolution=default (96 points per wavelength; caption of Fig. 7 implies N=384^3 particles); dbar=0.01; direction=y; d0_nominal=0.25; d0_plotted=0.25 | 1-92.62 | 78 |
| `GR_z_d0_0.03125` | blue | solid | half=top (plotted +d/L); model=GR; resolution=default (96 points per wavelength; caption of Fig. 7 implies N=384^3 particles); dbar=0.01; direction=z; d0_nominal=0.03125; d0_plotted=0.03125 | 1-92.79 | 42 |
| `GR_z_d0_0.0625` | blue | dotted [1 3] | half=top (plotted +d/L); model=GR; resolution=default (96 points per wavelength; caption of Fig. 7 implies N=384^3 particles); dbar=0.01; direction=z; d0_nominal=0.0625; d0_plotted=0.0625 | 1-92.52 | 57 |
| `GR_z_d0_0.125` | blue | dashed [6 6] | half=top (plotted +d/L); model=GR; resolution=default (96 points per wavelength; caption of Fig. 7 implies N=384^3 particles); dbar=0.01; direction=z; d0_nominal=0.125; d0_plotted=0.125 | 1-91.96 | 78 |
| `GR_z_d0_0.25` | blue | dash-dot [3 5 1 5] | half=top (plotted +d/L); model=GR; resolution=default (96 points per wavelength; caption of Fig. 7 implies N=384^3 particles); dbar=0.01; direction=z; d0_nominal=0.25; d0_plotted=0.25 | 1-92.34 | 87 |
| `Newt_x_d0_0.03125` | red | solid | half=bottom (plotted -d/L); model=Newtonian; resolution=default (N=196^3); dbar=0.01; direction=x; d0_nominal=0.03125; d0_plotted=0.03132 | 1-90.22 | 35 |
| `Newt_x_d0_0.0625` | red | dotted [1 3] | half=bottom (plotted -d/L); model=Newtonian; resolution=default (N=196^3); dbar=0.01; direction=x; d0_nominal=0.0625; d0_plotted=0.06257 | 1-90.35 | 38 |
| `Newt_x_d0_0.125` | red | dashed [6 6] | half=bottom (plotted -d/L); model=Newtonian; resolution=default (N=196^3); dbar=0.01; direction=x; d0_nominal=0.125; d0_plotted=0.12501 | 1-91.62 | 45 |
| `Newt_x_d0_0.25` | red | dash-dot [3 5 1 5] | half=bottom (plotted -d/L); model=Newtonian; resolution=default (N=196^3); dbar=0.01; direction=x; d0_nominal=0.25; d0_plotted=0.25008 | 1-95.51 | 43 |
| `Newt_y_d0_0.03125` | green (mpl "g") | solid | half=bottom (plotted -d/L); model=Newtonian; resolution=default (N=196^3); dbar=0.01; direction=y; d0_nominal=0.03125; d0_plotted=0.0313 | 1-90.04 | 37 |
| `Newt_y_d0_0.0625` | green (mpl "g") | dotted [1 3] | half=bottom (plotted -d/L); model=Newtonian; resolution=default (N=196^3); dbar=0.01; direction=y; d0_nominal=0.0625; d0_plotted=0.06255 | 1-90.22 | 42 |
| `Newt_y_d0_0.125` | green (mpl "g") | dashed [6 6] | half=bottom (plotted -d/L); model=Newtonian; resolution=default (N=196^3); dbar=0.01; direction=y; d0_nominal=0.125; d0_plotted=0.12508 | 1-91.54 | 45 |
| `Newt_y_d0_0.25` | green (mpl "g") | dash-dot [3 5 1 5] | half=bottom (plotted -d/L); model=Newtonian; resolution=default (N=196^3); dbar=0.01; direction=y; d0_nominal=0.25; d0_plotted=0.25005 | 1-95.51 | 41 |
| `Newt_z_d0_0.03125` | blue | solid | half=bottom (plotted -d/L); model=Newtonian; resolution=default (N=196^3); dbar=0.01; direction=z; d0_nominal=0.03125; d0_plotted=0.03126 | 1-90.3 | 35 |
| `Newt_z_d0_0.0625` | blue | dotted [1 3] | half=bottom (plotted -d/L); model=Newtonian; resolution=default (N=196^3); dbar=0.01; direction=z; d0_nominal=0.0625; d0_plotted=0.0625 | 1-90.43 | 39 |
| `Newt_z_d0_0.125` | blue | dashed [6 6] | half=bottom (plotted -d/L); model=Newtonian; resolution=default (N=196^3); dbar=0.01; direction=z; d0_nominal=0.125; d0_plotted=0.12501 | 1-91.53 | 46 |
| `Newt_z_d0_0.25` | blue | dash-dot [3 5 1 5] | half=bottom (plotted -d/L); model=Newtonian; resolution=default (N=196^3); dbar=0.01; direction=z; d0_nominal=0.25; d0_plotted=0.25002 | 1-94.23 | 43 |

## Derived numbers
`turning_points.csv`, one row per particle: initial plotted distance d0; a_p where d first drops below 0.1 d0 and
0.05 d0 (robust infall markers); the first crossing = first local minimum of d after d < 0.15 d0, with the a_p
interval over which the drawn d stays within max(5e-4, 0.02 d0) of that minimum; up to four following turning points
(hysteresis max(5e-4, 0.04 d0)); end point. d >= 0 is a distance (the GR half never goes below 0 and the Newtonian
half never above 0), so a crossing is a near-zero minimum, not a sign change.

Sampling: the Newtonian curves have one vertex per output (spacing ~1.3 in a_p near a_p ~ 57 for dbar = 0.01, ~2.7
near 115 for 0.005, ~5.6 near 230 for 0.0025), so Newtonian crossing times are uncertain by about half that spacing.
GR curves are sampled finely but matplotlib dropped vertices on near-straight stretches.

## Notes
* Identical (<= 3e-4 in d/L) to the "High res." half of Fig. 7 top (GR) and exactly identical to the "High res." half
  of Fig. 7 bottom (Newtonian), so this panel uses the GR N = 384^3 and Newtonian N = 196^3 runs of the Fig. 7 caption.

