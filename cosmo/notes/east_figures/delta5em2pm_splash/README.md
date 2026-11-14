# delta5em2pm_splash: Fig. 2 top left (dbar=0.05)

Source: `refs/arxiv_1908.05683/src/delta5em2pm_splash.eps` (matplotlib 1.5.1, vector). Paper: East, Wojtak & Pretorius, arXiv:1908.05683.

## What is plotted
Coordinate distance d (>= 0) from the point of maximum density, divided by the box length L, of 12 fiducial particles against their own proper-time scale factor a_p. Top half: +d/L from the GR run; bottom half: -d/L from the Newtonian run. Colour = initial displacement direction (red x, green y, blue z); line style = initial distance (solid L/32, dotted L/16, dashed L/8, dash-dot L/4).

## Files
* `delta5em2pm_splash.csv`: long format, columns `curve, segment, a_p, plotted_y (= +d/L top half, -d/L bottom half), visible, canvas_edge` (see the header comments).
* `curves.csv`: one row per curve with colour, line style and metadata.
* `check_delta5em2pm_splash.png`: the original EPS rendered with ghostscript (left) next to a replot of the CSV in data coordinates with the same axis limits and scales (right).

## Calibration
Curves are the stroked PostScript polylines; colour and dash pattern come from the setrgbcolor/setdash state; axes from the clip box; data coordinates from a least-squares fit of the major tick positions (tick marks paired with their labels in drawing order).
* x: lin axis: pos = 62.448556 + 27.173133 * f(v); ticks used: 2@116.795, 4@171.141, 6@225.487, 8@279.834, 10@334.180, 12@388.526, 14@442.872, 16@497.219, 18@551.565; max |residual| = 0.0004 pt
* y: lin axis: pos = 237.870700 + 696.806000 * f(v); ticks used: -0.2@98.510, -0.1@168.190, 0@237.871, 0.1@307.551, 0.2@377.232; max |residual| = 0.0003 pt
* Axes box in data units: x in [0.99994, 17.998], y in [-0.26, 0.25994].

## Accuracy
matplotlib simplified the paths with a tolerance of 1/9 pt (vertices within 0.11 pt of a straight run were dropped); coordinates are written to 1e-6 pt and the tick fit residual is < 1e-3 pt. Reading error: x +-0.0041 data units, y +-0.00016 data units. Between vertices the curve is the straight line that was drawn (in display coordinates).

## Curves

| curve | colour | line | meaning | a_p range | points |
|---|---|---|---|---|---|
| `GR_x_d0_0.03125` | red | solid | half=top (plotted +d/L); model=GR; resolution=default (96 points per wavelength; caption of Fig. 7 implies N=384^3 particles); dbar=0.05; direction=x; d0_nominal=0.03125; d0_plotted=0.03125 | 1-17.9 | 27 |
| `GR_x_d0_0.0625` | red | dotted [1 3] | half=top (plotted +d/L); model=GR; resolution=default (96 points per wavelength; caption of Fig. 7 implies N=384^3 particles); dbar=0.05; direction=x; d0_nominal=0.0625; d0_plotted=0.0625 | 1-17.89 | 39 |
| `GR_x_d0_0.125` | red | dashed [6 6] | half=top (plotted +d/L); model=GR; resolution=default (96 points per wavelength; caption of Fig. 7 implies N=384^3 particles); dbar=0.05; direction=x; d0_nominal=0.125; d0_plotted=0.125 | 1-17.89 | 48 |
| `GR_x_d0_0.25` | red | dash-dot [3 5 1 5] | half=top (plotted +d/L); model=GR; resolution=default (96 points per wavelength; caption of Fig. 7 implies N=384^3 particles); dbar=0.05; direction=x; d0_nominal=0.25; d0_plotted=0.25 | 1-18 | 44 |
| `GR_y_d0_0.03125` | green (mpl "g") | solid | half=top (plotted +d/L); model=GR; resolution=default (96 points per wavelength; caption of Fig. 7 implies N=384^3 particles); dbar=0.05; direction=y; d0_nominal=0.03125; d0_plotted=0.03125 | 1-17.9 | 30 |
| `GR_y_d0_0.0625` | green (mpl "g") | dotted [1 3] | half=top (plotted +d/L); model=GR; resolution=default (96 points per wavelength; caption of Fig. 7 implies N=384^3 particles); dbar=0.05; direction=y; d0_nominal=0.0625; d0_plotted=0.0625 | 1-17.88 | 42 |
| `GR_y_d0_0.125` | green (mpl "g") | dashed [6 6] | half=top (plotted +d/L); model=GR; resolution=default (96 points per wavelength; caption of Fig. 7 implies N=384^3 particles); dbar=0.05; direction=y; d0_nominal=0.125; d0_plotted=0.125 | 1-17.91 | 48 |
| `GR_y_d0_0.25` | green (mpl "g") | dash-dot [3 5 1 5] | half=top (plotted +d/L); model=GR; resolution=default (96 points per wavelength; caption of Fig. 7 implies N=384^3 particles); dbar=0.05; direction=y; d0_nominal=0.25; d0_plotted=0.25 | 1-18.01 | 41 |
| `GR_z_d0_0.03125` | blue | solid | half=top (plotted +d/L); model=GR; resolution=default (96 points per wavelength; caption of Fig. 7 implies N=384^3 particles); dbar=0.05; direction=z; d0_nominal=0.03125; d0_plotted=0.03125 | 1-17.89 | 31 |
| `GR_z_d0_0.0625` | blue | dotted [1 3] | half=top (plotted +d/L); model=GR; resolution=default (96 points per wavelength; caption of Fig. 7 implies N=384^3 particles); dbar=0.05; direction=z; d0_nominal=0.0625; d0_plotted=0.0625 | 1-17.86 | 44 |
| `GR_z_d0_0.125` | blue | dashed [6 6] | half=top (plotted +d/L); model=GR; resolution=default (96 points per wavelength; caption of Fig. 7 implies N=384^3 particles); dbar=0.05; direction=z; d0_nominal=0.125; d0_plotted=0.125 | 1-17.97 | 59 |
| `GR_z_d0_0.25` | blue | dash-dot [3 5 1 5] | half=top (plotted +d/L); model=GR; resolution=default (96 points per wavelength; caption of Fig. 7 implies N=384^3 particles); dbar=0.05; direction=z; d0_nominal=0.25; d0_plotted=0.25 | 1-18 | 42 |
| `Newt_x_d0_0.03125` | red | solid | half=bottom (plotted -d/L); model=Newtonian; resolution=default (N=196^3); dbar=0.05; direction=x; d0_nominal=0.03125; d0_plotted=0.0312 | 1-10.86 | 103 |
| `Newt_x_d0_0.0625` | red | dotted [1 3] | half=bottom (plotted -d/L); model=Newtonian; resolution=default (N=196^3); dbar=0.05; direction=x; d0_nominal=0.0625; d0_plotted=0.06248 | 1-10.82 | 103 |
| `Newt_x_d0_0.125` | red | dashed [6 6] | half=bottom (plotted -d/L); model=Newtonian; resolution=default (N=196^3); dbar=0.05; direction=x; d0_nominal=0.125; d0_plotted=0.12491 | 1-11.1 | 104 |
| `Newt_x_d0_0.25` | red | dash-dot [3 5 1 5] | half=bottom (plotted -d/L); model=Newtonian; resolution=default (N=196^3); dbar=0.05; direction=x; d0_nominal=0.25; d0_plotted=0.24996 | 1-13.56 | 112 |
| `Newt_y_d0_0.03125` | green (mpl "g") | solid | half=bottom (plotted -d/L); model=Newtonian; resolution=default (N=196^3); dbar=0.05; direction=y; d0_nominal=0.03125; d0_plotted=0.03125 | 1-10.85 | 103 |
| `Newt_y_d0_0.0625` | green (mpl "g") | dotted [1 3] | half=bottom (plotted -d/L); model=Newtonian; resolution=default (N=196^3); dbar=0.05; direction=y; d0_nominal=0.0625; d0_plotted=0.06256 | 1-10.84 | 103 |
| `Newt_y_d0_0.125` | green (mpl "g") | dashed [6 6] | half=bottom (plotted -d/L); model=Newtonian; resolution=default (N=196^3); dbar=0.05; direction=y; d0_nominal=0.125; d0_plotted=0.12492 | 1-11.15 | 104 |
| `Newt_y_d0_0.25` | green (mpl "g") | dash-dot [3 5 1 5] | half=bottom (plotted -d/L); model=Newtonian; resolution=default (N=196^3); dbar=0.05; direction=y; d0_nominal=0.25; d0_plotted=0.24998 | 1-13.87 | 113 |
| `Newt_z_d0_0.03125` | blue | solid | half=bottom (plotted -d/L); model=Newtonian; resolution=default (N=196^3); dbar=0.05; direction=z; d0_nominal=0.03125; d0_plotted=0.03125 | 1-10.85 | 103 |
| `Newt_z_d0_0.0625` | blue | dotted [1 3] | half=bottom (plotted -d/L); model=Newtonian; resolution=default (N=196^3); dbar=0.05; direction=z; d0_nominal=0.0625; d0_plotted=0.0624 | 1-10.83 | 103 |
| `Newt_z_d0_0.125` | blue | dashed [6 6] | half=bottom (plotted -d/L); model=Newtonian; resolution=default (N=196^3); dbar=0.05; direction=z; d0_nominal=0.125; d0_plotted=0.12506 | 1-10.92 | 103 |
| `Newt_z_d0_0.25` | blue | dash-dot [3 5 1 5] | half=bottom (plotted -d/L); model=Newtonian; resolution=default (N=196^3); dbar=0.05; direction=z; d0_nominal=0.25; d0_plotted=0.24993 | 1-13.27 | 111 |

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
* The Newtonian run ends at a_p = 10.8-11.2 for the three inner particle sets and 13.3-13.9 for d0 = L/4; no
  Newtonian particle reaches the centre. GR particles with d0 <= L/8 reach their first minimum at a_p = 16.2-17.7.
* The GR d0 = L/4 curves rise above the axes (to the page edge, d/L = 0.28, between a_p ~ 4.2 and 7.5); that part is
  missing from the file (two segments per curve).
* GR initial (gauge) oscillation: d rises by 8-12% above d0 by a_p ~ 5.5 before falling.

