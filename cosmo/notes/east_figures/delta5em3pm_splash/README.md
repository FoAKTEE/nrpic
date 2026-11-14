# delta5em3pm_splash: Fig. 2 bottom left (dbar=0.005)

Source: `refs/arxiv_1908.05683/src/delta5em3pm_splash.eps` (matplotlib 1.5.1, vector). Paper: East, Wojtak & Pretorius, arXiv:1908.05683.

## What is plotted
Coordinate distance d (>= 0) from the point of maximum density, divided by the box length L, of 12 fiducial particles against their own proper-time scale factor a_p. Top half: +d/L from the GR run; bottom half: -d/L from the Newtonian run. Colour = initial displacement direction (red x, green y, blue z); line style = initial distance (solid L/32, dotted L/16, dashed L/8, dash-dot L/4).

## Files
* `delta5em3pm_splash.csv`: long format, columns `curve, segment, a_p, plotted_y (= +d/L top half, -d/L bottom half), visible, canvas_edge` (see the header comments).
* `curves.csv`: one row per curve with colour, line style and metadata.
* `check_delta5em3pm_splash.png`: the original EPS rendered with ghostscript (left) next to a replot of the CSV in data coordinates with the same axis limits and scales (right).

## Calibration
Curves are the stroked PostScript polylines; colour and dash pattern come from the setrgbcolor/setdash state; axes from the clip box; data coordinates from a least-squares fit of the major tick positions (tick marks paired with their labels in drawing order).
* x: lin axis: pos = 86.342714 + 3.279130 * f(v); ticks used: 20@151.925, 40@217.508, 60@283.091, 80@348.673, 100@414.256, 120@479.838, 140@545.421; max |residual| = 0.0005 pt
* y: lin axis: pos = 237.870700 + 696.806000 * f(v); ticks used: -0.2@98.510, -0.1@168.190, 0@237.871, 0.1@307.551, 0.2@377.232; max |residual| = 0.0003 pt
* Axes box in data units: x in [0.99944, 142.99], y in [-0.26, 0.25994].

## Accuracy
matplotlib simplified the paths with a tolerance of 1/9 pt (vertices within 0.11 pt of a straight run were dropped); coordinates are written to 1e-6 pt and the tick fit residual is < 1e-3 pt. Reading error: x +-0.034 data units, y +-0.00016 data units. Between vertices the curve is the straight line that was drawn (in display coordinates).

## Curves

| curve | colour | line | meaning | a_p range | points |
|---|---|---|---|---|---|
| `GR_x_d0_0.03125` | red | solid | half=top (plotted +d/L); model=GR; resolution=default (96 points per wavelength; caption of Fig. 7 implies N=384^3 particles); dbar=0.005; direction=x; d0_nominal=0.03125; d0_plotted=0.03125 | 1-143 | 28 |
| `GR_x_d0_0.0625` | red | dotted [1 3] | half=top (plotted +d/L); model=GR; resolution=default (96 points per wavelength; caption of Fig. 7 implies N=384^3 particles); dbar=0.005; direction=x; d0_nominal=0.0625; d0_plotted=0.0625 | 1-143 | 41 |
| `GR_x_d0_0.125` | red | dashed [6 6] | half=top (plotted +d/L); model=GR; resolution=default (96 points per wavelength; caption of Fig. 7 implies N=384^3 particles); dbar=0.005; direction=x; d0_nominal=0.125; d0_plotted=0.125 | 1-143 | 56 |
| `GR_x_d0_0.25` | red | dash-dot [3 5 1 5] | half=top (plotted +d/L); model=GR; resolution=default (96 points per wavelength; caption of Fig. 7 implies N=384^3 particles); dbar=0.005; direction=x; d0_nominal=0.25; d0_plotted=0.25 | 1-143 | 64 |
| `GR_y_d0_0.03125` | green (mpl "g") | solid | half=top (plotted +d/L); model=GR; resolution=default (96 points per wavelength; caption of Fig. 7 implies N=384^3 particles); dbar=0.005; direction=y; d0_nominal=0.03125; d0_plotted=0.03125 | 1-143 | 30 |
| `GR_y_d0_0.0625` | green (mpl "g") | dotted [1 3] | half=top (plotted +d/L); model=GR; resolution=default (96 points per wavelength; caption of Fig. 7 implies N=384^3 particles); dbar=0.005; direction=y; d0_nominal=0.0625; d0_plotted=0.0625 | 1-143 | 38 |
| `GR_y_d0_0.125` | green (mpl "g") | dashed [6 6] | half=top (plotted +d/L); model=GR; resolution=default (96 points per wavelength; caption of Fig. 7 implies N=384^3 particles); dbar=0.005; direction=y; d0_nominal=0.125; d0_plotted=0.125 | 1-143 | 54 |
| `GR_y_d0_0.25` | green (mpl "g") | dash-dot [3 5 1 5] | half=top (plotted +d/L); model=GR; resolution=default (96 points per wavelength; caption of Fig. 7 implies N=384^3 particles); dbar=0.005; direction=y; d0_nominal=0.25; d0_plotted=0.25 | 1-143 | 62 |
| `GR_z_d0_0.03125` | blue | solid | half=top (plotted +d/L); model=GR; resolution=default (96 points per wavelength; caption of Fig. 7 implies N=384^3 particles); dbar=0.005; direction=z; d0_nominal=0.03125; d0_plotted=0.03125 | 1-143 | 31 |
| `GR_z_d0_0.0625` | blue | dotted [1 3] | half=top (plotted +d/L); model=GR; resolution=default (96 points per wavelength; caption of Fig. 7 implies N=384^3 particles); dbar=0.005; direction=z; d0_nominal=0.0625; d0_plotted=0.0625 | 1-143 | 42 |
| `GR_z_d0_0.125` | blue | dashed [6 6] | half=top (plotted +d/L); model=GR; resolution=default (96 points per wavelength; caption of Fig. 7 implies N=384^3 particles); dbar=0.005; direction=z; d0_nominal=0.125; d0_plotted=0.125 | 1-143 | 56 |
| `GR_z_d0_0.25` | blue | dash-dot [3 5 1 5] | half=top (plotted +d/L); model=GR; resolution=default (96 points per wavelength; caption of Fig. 7 implies N=384^3 particles); dbar=0.005; direction=z; d0_nominal=0.25; d0_plotted=0.25 | 1-143 | 67 |
| `Newt_x_d0_0.03125` | red | solid | half=bottom (plotted -d/L); model=Newtonian; resolution=default (N=196^3); dbar=0.005; direction=x; d0_nominal=0.03125; d0_plotted=0.03267 | 1-142.8 | 26 |
| `Newt_x_d0_0.0625` | red | dotted [1 3] | half=bottom (plotted -d/L); model=Newtonian; resolution=default (N=196^3); dbar=0.005; direction=x; d0_nominal=0.0625; d0_plotted=0.06389 | 1-143 | 29 |
| `Newt_x_d0_0.125` | red | dashed [6 6] | half=bottom (plotted -d/L); model=Newtonian; resolution=default (N=196^3); dbar=0.005; direction=x; d0_nominal=0.125; d0_plotted=0.12637 | 1-143.3 | 33 |
| `Newt_x_d0_0.25` | red | dash-dot [3 5 1 5] | half=bottom (plotted -d/L); model=Newtonian; resolution=default (N=196^3); dbar=0.005; direction=x; d0_nominal=0.25; d0_plotted=0.25132 | 1-145.1 | 30 |
| `Newt_y_d0_0.03125` | green (mpl "g") | solid | half=bottom (plotted -d/L); model=Newtonian; resolution=default (N=196^3); dbar=0.005; direction=y; d0_nominal=0.03125; d0_plotted=0.03269 | 1-142.7 | 24 |
| `Newt_y_d0_0.0625` | green (mpl "g") | dotted [1 3] | half=bottom (plotted -d/L); model=Newtonian; resolution=default (N=196^3); dbar=0.005; direction=y; d0_nominal=0.0625; d0_plotted=0.0639 | 1-142.7 | 30 |
| `Newt_y_d0_0.125` | green (mpl "g") | dashed [6 6] | half=bottom (plotted -d/L); model=Newtonian; resolution=default (N=196^3); dbar=0.005; direction=y; d0_nominal=0.125; d0_plotted=0.12634 | 1-143.3 | 32 |
| `Newt_y_d0_0.25` | green (mpl "g") | dash-dot [3 5 1 5] | half=bottom (plotted -d/L); model=Newtonian; resolution=default (N=196^3); dbar=0.005; direction=y; d0_nominal=0.25; d0_plotted=0.25141 | 1-145.1 | 30 |
| `Newt_z_d0_0.03125` | blue | solid | half=bottom (plotted -d/L); model=Newtonian; resolution=default (N=196^3); dbar=0.005; direction=z; d0_nominal=0.03125; d0_plotted=0.03274 | 1-142.9 | 27 |
| `Newt_z_d0_0.0625` | blue | dotted [1 3] | half=bottom (plotted -d/L); model=Newtonian; resolution=default (N=196^3); dbar=0.005; direction=z; d0_nominal=0.0625; d0_plotted=0.06382 | 1-142.7 | 30 |
| `Newt_z_d0_0.125` | blue | dashed [6 6] | half=bottom (plotted -d/L); model=Newtonian; resolution=default (N=196^3); dbar=0.005; direction=z; d0_nominal=0.125; d0_plotted=0.12634 | 1-143.2 | 33 |
| `Newt_z_d0_0.25` | blue | dash-dot [3 5 1 5] | half=bottom (plotted -d/L); model=Newtonian; resolution=default (N=196^3); dbar=0.005; direction=z; d0_nominal=0.25; d0_plotted=0.25129 | 1-145 | 31 |

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
* The Newtonian particles start at d/L = 0.0327, 0.0639, 0.1264, 0.2513 instead of 1/32, 1/16, 1/8, 1/4 (an offset of
  +0.0013 to +0.0015 L in all 12 curves); every other panel starts at the nominal values to 1e-4.

