# delta1em2_dl_newt_gr: Fig. 4 row 1 right (dbar=0.01)

Source: `refs/arxiv_1908.05683/src/delta1em2_dl_newt_gr.eps` (matplotlib 1.5.1, vector). Paper: East, Wojtak & Pretorius, arXiv:1908.05683.

## What is plotted
|D_L^Newt(z)/D_L^GR(z) - 1| for the same rays as the left column: solid = rays emitted at the OD, dashed = rays emitted at the UD, colour = emission time a_em (legend).

## Files
* `delta1em2_dl_newt_gr.csv`: long format, columns `curve, segment, z, abs_DL_Newt_over_DL_GR_minus_1, visible, canvas_edge` (see the header comments).
* `curves.csv`: one row per curve with colour, line style and metadata.
* `check_delta1em2_dl_newt_gr.png`: the original EPS rendered with ghostscript (left) next to a replot of the CSV in data coordinates with the same axis limits and scales (right).

## Calibration
Curves are the stroked PostScript polylines; colour and dash pattern come from the setrgbcolor/setdash state; axes from the clip box; data coordinates from a least-squares fit of the major tick positions (tick marks paired with their labels in drawing order).
* x: log axis: pos = 390.333650 + 149.946550 * f(v); ticks used: 0.01@90.441, 0.1@240.387, 1@390.334, 10@540.280; max |residual| = 0.0004 pt
* y: log axis: pos = 401.917600 + 83.773200 * f(v); ticks used: 0.0001@66.825, 0.001@150.598, 0.01@234.371, 0.1@318.144, 1@401.918; max |residual| = 0.0004 pt
* Axes box in data units: x in [0.0099999, 9.9938], y in [0.00010001, 1.0003].

## Accuracy
matplotlib simplified the paths with a tolerance of 1/9 pt (vertices within 0.11 pt of a straight run were dropped); coordinates are written to 1e-6 pt and the tick fit residual is < 1e-3 pt. Reading error: x +-0.17% (0.0007 dex), y +-0.31% (0.0013 dex). Between vertices the curve is the straight line that was drawn (in display coordinates).

## Curves

| curve | colour | line | meaning | z range | points |
|---|---|---|---|---|---|
| `OD_aem1` | maroon | solid | ray=emitted at OD towards UD; a_em_label=1; dbar=0.01; quantity=|D_L^Newt/D_L^GR - 1| | 0.08872-6.735 | 314 |
| `UD_aem1` | chartreuse | dashed [6 6] | ray=emitted at UD towards OD; a_em_label=1; dbar=0.01; quantity=|D_L^Newt/D_L^GR - 1| | 0.08872-6.197 | 330 |
| `OD_aem28` | red | solid | ray=emitted at OD towards UD; a_em_label=28; dbar=0.01; quantity=|D_L^Newt/D_L^GR - 1| | 0.002456-0.8393 | 185 |
| `UD_aem27` | forestgreen | dashed [6 6] | ray=emitted at UD towards OD; a_em_label=27; dbar=0.01; quantity=|D_L^Newt/D_L^GR - 1| | 0.002456-0.7348 | 211 |
| `OD_aem43` | chocolate | solid | ray=emitted at OD towards UD; a_em_label=43; dbar=0.01; quantity=|D_L^Newt/D_L^GR - 1| | 0.002456-0.6783 | 146 |
| `UD_aem44` | lightseagreen | dashed [6 6] | ray=emitted at UD towards OD; a_em_label=44; dbar=0.01; quantity=|D_L^Newt/D_L^GR - 1| | 0.002456-0.7955 | 238 |
| `OD_aem52` | darkorange | solid | ray=emitted at OD towards UD; a_em_label=52; dbar=0.01; quantity=|D_L^Newt/D_L^GR - 1| | 0.002456-0.6315 | 109 |
| `UD_aem52` | aqua/cyan | dashed [6 6] | ray=emitted at UD towards OD; a_em_label=52; dbar=0.01; quantity=|D_L^Newt/D_L^GR - 1| | 0.002456-0.7705 | 202 |

## Notes
* Dips to zero (sign changes of the difference) go below the axes; the drawn path continues to the page edge
  (1.55e-5 or 1.43e-5) and is broken there, so a curve can have several segments; canvas_edge = 1 marks the cut points.
* `values_at_z.csv`: values at z = 0.1, 0.5, 1, 2 (every pass), and the maximum over the visible range.

