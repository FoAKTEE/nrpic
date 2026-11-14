# od_comp: Fig. 1 middle

Source: `refs/arxiv_1908.05683/src/od_comp.eps` (matplotlib 1.5.1, vector). Paper: East, Wojtak & Pretorius, arXiv:1908.05683.

## What is plotted
|delta_obs| at the point of maximum density (halo centre) against a_p, for dbar = 0.0025, 0.005, 0.01, 0.05 (right to left). Black solid = GR, red dashed = Newtonian (tetrahedral density), magenta dotted = Newtonian with a CIC density estimate (only dbar = 0.01 and 0.05). Default resolutions.

## Files
* `od_comp.csv`: long format, columns `curve, segment, a_p, abs_delta_obs, visible, canvas_edge` (see the header comments).
* `curves.csv`: one row per curve with colour, line style and metadata.
* `check_od_comp.png`: the original EPS rendered with ghostscript (left) next to a replot of the CSV in data coordinates with the same axis limits and scales (right).

## Calibration
Curves are the stroked PostScript polylines; colour and dash pattern come from the setrgbcolor/setdash state; axes from the clip box; data coordinates from a least-squares fit of the major tick positions (tick marks paired with their labels in drawing order).
* x: log axis: pos = 80.665667 + 197.116200 * f(v); ticks used: 1@80.666, 10@277.782, 100@474.898; max |residual| = 0.0001 pt
* y: log axis: pos = 138.110866 + 38.612398 * f(v); ticks used: 0.01@60.886, 0.1@99.499, 1@138.111, 10@176.723, 100@215.336, 1000@253.948, 10000@292.560, 100000@331.173, 1e+06@369.785, 1e+07@408.398; max |residual| = 0.0005 pt
* Axes box in data units: x in [1.0001, 280.1], y in [0.010002, 9.9954e+06].

## Accuracy
matplotlib simplified the paths with a tolerance of 1/9 pt (vertices within 0.11 pt of a straight run were dropped); coordinates are written to 1e-6 pt and the tick fit residual is < 1e-3 pt. Reading error: x +-0.13% (0.0006 dex), y +-0.66% (0.0029 dex). Between vertices the curve is the straight line that was drawn (in display coordinates).

## Curves

| curve | colour | line | meaning | a_p range | points |
|---|---|---|---|---|---|
| `GR_dbar0.0025` | black | solid | model=GR; dbar=0.0025; point=overdensity (maximum density); resolution=default (GR: 96 points per wavelength; Newtonian: N=196^3); density_estimator=GR particle deposit on grid | 1-255.2 | 55 |
| `Newt_dbar0.0025` | red | dashed [6 6] | model=Newtonian; dbar=0.0025; point=overdensity (maximum density); resolution=default (GR: 96 points per wavelength; Newtonian: N=196^3); density_estimator=tetrahedral (phase-space) cells | 1-262.8 | 56 |
| `GR_dbar0.005` | black | solid | model=GR; dbar=0.005; point=overdensity (maximum density); resolution=default (GR: 96 points per wavelength; Newtonian: N=196^3); density_estimator=GR particle deposit on grid | 1-171.1 | 82 |
| `Newt_dbar0.005` | red | dashed [6 6] | model=Newtonian; dbar=0.005; point=overdensity (maximum density); resolution=default (GR: 96 points per wavelength; Newtonian: N=196^3); density_estimator=tetrahedral (phase-space) cells | 1-142.8 | 58 |
| `GR_dbar0.01` | black | solid | model=GR; dbar=0.01; point=overdensity (maximum density); resolution=default (GR: 96 points per wavelength; Newtonian: N=196^3); density_estimator=GR particle deposit on grid | 1-92.9 | 84 |
| `Newt_dbar0.01` | red | dashed [6 6] | model=Newtonian; dbar=0.01; point=overdensity (maximum density); resolution=default (GR: 96 points per wavelength; Newtonian: N=196^3); density_estimator=tetrahedral (phase-space) cells | 1-90.42 | 70 |
| `NewtCIC_dbar0.01` | magenta (mpl "m") | dotted [1 3] | model=Newtonian CIC; dbar=0.01; point=overdensity (maximum density); resolution=default (GR: 96 points per wavelength; Newtonian: N=196^3); density_estimator=CIC | 1-90.42 | 65 |
| `GR_dbar0.05` | black | solid | model=GR; dbar=0.05; point=overdensity (maximum density); resolution=default (GR: 96 points per wavelength; Newtonian: N=196^3); density_estimator=GR particle deposit on grid | 1-16.8 | 47 |
| `Newt_dbar0.05` | red | dashed [6 6] | model=Newtonian; dbar=0.05; point=overdensity (maximum density); resolution=default (GR: 96 points per wavelength; Newtonian: N=196^3); density_estimator=tetrahedral (phase-space) cells | 1-10.86 | 103 |
| `NewtCIC_dbar0.05` | magenta (mpl "m") | dotted [1 3] | model=Newtonian CIC; dbar=0.05; point=overdensity (maximum density); resolution=default (GR: 96 points per wavelength; Newtonian: N=196^3); density_estimator=CIC | 1-10.86 | 103 |

## Derived numbers
`crossings.csv`: a_p where |delta_obs| first reaches 1, 10, 100, 1000; first maximum (first local maximum followed by a
drop of more than 0.05 dex); median/min/max of |delta_obs| from that maximum to the end ("plateau"); end point and
global maximum.

## Checks
* GR curves start at 6.644 dbar at a_p = 1 (same as the void, as linear theory requires for |delta|).
* The Newtonian dbar = 0.01 curve is identical (max 0.004 dex) to the "Newt. OD High Res." curve of Fig. 1 bottom,
  and the CIC dbar = 0.01 curve to "Newt. OD CIC" there.
* The GR dbar = 0.01 curve here is *not* identical to "GR OD" of Fig. 1 bottom (up to 0.3 dex apart after collapse;
  |delta_obs| = 100 at a_p = 58.0 here, 58.9 for "GR OD", 57.2 for "GR OD High Res.").

