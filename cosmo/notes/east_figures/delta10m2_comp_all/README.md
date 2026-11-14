# delta10m2_comp_all: Fig. 1 bottom

Source: `refs/arxiv_1908.05683/src/delta10m2_comp_all.eps` (matplotlib 1.5.1, vector). Paper: East, Wojtak & Pretorius, arXiv:1908.05683.

## What is plotted
|delta_obs| at the maximum-density point for dbar = 0.01 (linear a_p axis) for several resolutions and for particle versus pressureless-fluid GR matter.

## Files
* `delta10m2_comp_all.csv`: long format, columns `curve, segment, a_p, abs_delta_obs, visible, canvas_edge` (see the header comments).
* `curves.csv`: one row per curve with colour, line style and metadata.
* `check_delta10m2_comp_all.png`: the original EPS rendered with ghostscript (left) next to a replot of the CSV in data coordinates with the same axis limits and scales (right).

## Calibration
Curves are the stroked PostScript polylines; colour and dash pattern come from the setrgbcolor/setdash state; axes from the clip box; data coordinates from a least-squares fit of the major tick positions (tick marks paired with their labels in drawing order).
* x: lin axis: pos = 80.665583 + 3.322584 * f(v); ticks used: 0@80.666, 20@147.117, 40@213.569, 60@280.021, 80@346.472, 100@412.924, 120@479.376, 140@545.827; max |residual| = 0.0004 pt
* y: log axis: pos = 143.017962 + 66.345014 * f(v); ticks used: 0.1@76.673, 1@143.018, 10@209.363, 100@275.708, 1000@342.053, 10000@408.398; max |residual| = 0.0000 pt
* Axes box in data units: x in [0.0013293, 140.01], y in [0.049998, 10001].

## Accuracy
matplotlib simplified the paths with a tolerance of 1/9 pt (vertices within 0.11 pt of a straight run were dropped); coordinates are written to 1e-6 pt and the tick fit residual is < 1e-3 pt. Reading error: x +-0.033 data units, y +-0.39% (0.0017 dex). Between vertices the curve is the straight line that was drawn (in display coordinates).

## Curves

| curve | colour | line | meaning | a_p range | points |
|---|---|---|---|---|---|
| `GR` | blue | solid | model=GR; matter=particles; dbar=0.01; point=overdensity; resolution=default (96 points per wavelength) | 1-131.6 | 115 |
| `GR_highres` | green (mpl "g") | solid | model=GR; matter=particles; dbar=0.01; point=overdensity; resolution=high (presumably 128 points per wavelength, 4/3 x default) | 1-78.73 | 97 |
| `GR_fluid` | red | solid | model=GR; matter=pressureless fluid; dbar=0.01; point=overdensity; resolution=default (96 points per wavelength) | 1-73.16 | 71 |
| `GR_fluid_highres` | cyan (mpl "c") | solid | model=GR; matter=pressureless fluid; dbar=0.01; point=overdensity; resolution=high (presumably 128 points per wavelength) | 1-62.58 | 57 |
| `Newt` | red | dashed [6 6] | model=Newtonian; matter=particles (tetrahedral density); dbar=0.01; point=overdensity; resolution=see README: identical to Fig.1 middle Newtonian dbar=0.01 (N=196^3 default) | 1-60.87 | 50 |
| `Newt_highres` | black | dashed [6 6] | model=Newtonian; matter=particles (tetrahedral density); dbar=0.01; point=overdensity; resolution=labelled High Res.; N not stated | 1-56 | 45 |
| `NewtCIC` | blue | dashed [6 6] | model=Newtonian; matter=particles (CIC density); dbar=0.01; point=overdensity; resolution=default N=196^3 | 1-90.42 | 63 |

## Identification of the resolutions
* "Newt. OD High Res." (black dashed) coincides with the Newtonian dbar = 0.01 curve of Fig. 1 middle (the default
  N = 196^3 run) to 0.004 dex, so "Newt. OD" (red dashed) is the lower-resolution run (N = 128^3 in the text).
* "GR OD" (blue) and "GR OD High Res." (green) both differ from the GR dbar = 0.01 curve of Fig. 1 middle, which lies
  between them (a_p at |delta_obs| = 100: 58.9, 57.2 and 58.0). The paper does not state their particle numbers;
  Fig. 6 suggests the GR runs used 64^3, 192^3, 512^3 particles for L/dx = 64, 96, 128, and Fig. 7 implies 384^3 for
  the default; so "GR OD" is plausibly L/dx = 96 with 192^3 particles and "High Res." L/dx = 128 with 512^3 (not stated).
* The fluid curves stop or leave the plot at shell crossing ("GR OD Fluid" peaks at 1.22e4 at a_p = 72.1, ends at 73.2;
  the high-resolution fluid curve leaves the page at 2.35e4, a_p = 62.6).

## Derived numbers
`crossings.csv`, same definitions as Fig. 1 middle. Values above the axes top (1e4) up to the page edge (2.35e4) are
present in the file but hidden in the paper (visible = 0).

