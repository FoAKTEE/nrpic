# ud_comp: Fig. 1 top

Source: `refs/arxiv_1908.05683/src/ud_comp.eps` (matplotlib 1.5.1, vector). Paper: East, Wojtak & Pretorius, arXiv:1908.05683.

## What is plotted
|delta_obs| at the point of minimum density (void centre) against the proper-time scale factor a_p of the observer there, for dbar = 0.0025, 0.005, 0.01, 0.05 (bottom to top). Black solid = GR, red dashed = Newtonian (tetrahedral phase-space density). Default resolutions.

## Files
* `ud_comp.csv`: long format, columns `curve, segment, a_p, abs_delta_obs, visible, canvas_edge` (see the header comments).
* `curves.csv`: one row per curve with colour, line style and metadata.
* `check_ud_comp.png`: the original EPS rendered with ghostscript (left) next to a replot of the CSV in data coordinates with the same axis limits and scales (right).

## Calibration
Curves are the stroked PostScript polylines; colour and dash pattern come from the setrgbcolor/setdash state; axes from the clip box; data coordinates from a least-squares fit of the major tick positions (tick marks paired with their labels in drawing order).
* x: log axis: pos = 80.665667 + 197.116200 * f(v); ticks used: 1@80.666, 10@277.782, 100@474.898; max |residual| = 0.0001 pt
* y: log axis: pos = 408.397983 + 173.755950 * f(v); ticks used: 0.01@60.886, 0.1@234.642, 1@408.398; max |residual| = 0.0000 pt
* Axes box in data units: x in [1.0001, 280.1], y in [0.010001, 0.99989].

## Accuracy
matplotlib simplified the paths with a tolerance of 1/9 pt (vertices within 0.11 pt of a straight run were dropped); coordinates are written to 1e-6 pt and the tick fit residual is < 1e-3 pt. Reading error: x +-0.13% (0.0006 dex), y +-0.15% (0.0006 dex). Between vertices the curve is the straight line that was drawn (in display coordinates).

## Curves

| curve | colour | line | meaning | a_p range | points |
|---|---|---|---|---|---|
| `GR_dbar0.0025` | black | solid | model=GR; dbar=0.0025; point=underdensity (minimum density); resolution=default (GR: 96 points per wavelength; Newtonian: N=196^3); density_estimator=GR particle deposit on grid | 1-256.3 | 45 |
| `Newt_dbar0.0025` | red | dashed [6 6] | model=Newtonian; dbar=0.0025; point=underdensity (minimum density); resolution=default (GR: 96 points per wavelength; Newtonian: N=196^3); density_estimator=tetrahedral (phase-space) cells | 1-265.8 | 48 |
| `GR_dbar0.005` | black | solid | model=GR; dbar=0.005; point=underdensity (minimum density); resolution=default (GR: 96 points per wavelength; Newtonian: N=196^3); density_estimator=GR particle deposit on grid | 1-172.1 | 49 |
| `Newt_dbar0.005` | red | dashed [6 6] | model=Newtonian; dbar=0.005; point=underdensity (minimum density); resolution=default (GR: 96 points per wavelength; Newtonian: N=196^3); density_estimator=tetrahedral (phase-space) cells | 1-147.3 | 47 |
| `GR_dbar0.01` | black | solid | model=GR; dbar=0.01; point=underdensity (minimum density); resolution=default (GR: 96 points per wavelength; Newtonian: N=196^3); density_estimator=GR particle deposit on grid | 1-96.31 | 46 |
| `Newt_dbar0.01` | red | dashed [6 6] | model=Newtonian; dbar=0.01; point=underdensity (minimum density); resolution=default (GR: 96 points per wavelength; Newtonian: N=196^3); density_estimator=tetrahedral (phase-space) cells | 1-102.1 | 43 |
| `GR_dbar0.05` | black | solid | model=GR; dbar=0.05; point=underdensity (minimum density); resolution=default (GR: 96 points per wavelength; Newtonian: N=196^3); density_estimator=GR particle deposit on grid | 1-19.28 | 35 |
| `Newt_dbar0.05` | red | dashed [6 6] | model=Newtonian; dbar=0.05; point=underdensity (minimum density); resolution=default (GR: 96 points per wavelength; Newtonian: N=196^3); density_estimator=tetrahedral (phase-space) cells | 1-22.73 | 126 |

## Derived numbers
`values_at_ap.csv`: |delta_obs| of GR and Newtonian at a_p = 1, 2, 5, 10, 20, 50, 100 where plotted.

## Checks
* At a_p = 1 the GR curves start at |delta_obs| = 6.644 dbar for all four amplitudes. Linear theory for the
  longitudinal-gauge density of the k = pi H0/2 mode gives 3 dbar (1 + 3H0^2/k^2) = 3 dbar (1 + 12/pi^2) = 6.648 dbar
  (the 3 is 1 + 0.9 + 1.1 at the void), so the y calibration is right to < 0.1%.
* Caption: "Newtonian and GR curves ... essentially indistinguishable": max |Newt/GR - 1| over the common range is
  2.0%, 2.3%, 2.2% for dbar = 0.0025, 0.005, 0.01 and 3.9% for 0.05 (the latter at a_p = 1, where the Newtonian
  initial value is 0.319 against 0.332 for GR).

