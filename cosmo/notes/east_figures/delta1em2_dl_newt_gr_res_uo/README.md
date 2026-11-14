# delta1em2_dl_newt_gr_res_uo: Fig. 8 bottom (appendix, rays from UD)

Source: `refs/arxiv_1908.05683/src/delta1em2_dl_newt_gr_res_uo.eps` (matplotlib 1.5.1, vector). Paper: East, Wojtak & Pretorius, arXiv:1908.05683.

## What is plotted
As the top panel for rays emitted at the UD (black a_em 1, blue 27, red 44, green 52).

## Files
* `delta1em2_dl_newt_gr_res_uo.csv`: long format, columns `curve, segment, z, abs_DL_Newt_over_DL_GR_minus_1, visible, canvas_edge` (see the header comments).
* `curves.csv`: one row per curve with colour, line style and metadata.
* `check_delta1em2_dl_newt_gr_res_uo.png`: the original EPS rendered with ghostscript (left) next to a replot of the CSV in data coordinates with the same axis limits and scales (right).

## Calibration
Curves are the stroked PostScript polylines; colour and dash pattern come from the setrgbcolor/setdash state; axes from the clip box; data coordinates from a least-squares fit of the major tick positions (tick marks paired with their labels in drawing order).
* x: log axis: pos = 390.333650 + 149.946550 * f(v); ticks used: 0.01@90.441, 0.1@240.387, 1@390.334, 10@540.280; max |residual| = 0.0004 pt
* y: log axis: pos = 388.362000 + 80.384300 * f(v); ticks used: 0.0001@66.825, 0.001@147.209, 0.01@227.593, 0.1@307.978, 1@388.362; max |residual| = 0.0004 pt
* Axes box in data units: x in [0.0099999, 9.9938], y in [9.9986e-05, 1.9977].

## Accuracy
matplotlib simplified the paths with a tolerance of 1/9 pt (vertices within 0.11 pt of a straight run were dropped); coordinates are written to 1e-6 pt and the tick fit residual is < 1e-3 pt. Reading error: x +-0.17% (0.0007 dex), y +-0.32% (0.0014 dex). Between vertices the curve is the straight line that was drawn (in display coordinates).

## Curves

| curve | colour | line | meaning | z range | points |
|---|---|---|---|---|---|
| `UD_aem1_highres` | black | solid | ray=emitted at UD towards OD; a_em_label=1; resolution=high: GR N=512^3 vs Newtonian N=196^3; dbar=0.01; quantity=|D_L^Newt/D_L^GR - 1| | 0.06503-6.19 | 347 |
| `UD_aem1_lowres` | black | dotted [1 3] | ray=emitted at UD towards OD; a_em_label=1; resolution=low: GR N=192^3 vs Newtonian N=128^3; dbar=0.01; quantity=|D_L^Newt/D_L^GR - 1| | 0.08872-6.197 | 302 |
| `UD_aem27_highres` | blue | solid | ray=emitted at UD towards OD; a_em_label=27; resolution=high: GR N=512^3 vs Newtonian N=196^3; dbar=0.01; quantity=|D_L^Newt/D_L^GR - 1| | 0.002456-0.7361 | 208 |
| `UD_aem27_lowres` | blue | dotted [1 3] | ray=emitted at UD towards OD; a_em_label=27; resolution=low: GR N=192^3 vs Newtonian N=128^3; dbar=0.01; quantity=|D_L^Newt/D_L^GR - 1| | 0.002456-0.7528 | 235 |
| `UD_aem44_highres` | red | solid | ray=emitted at UD towards OD; a_em_label=44; resolution=high: GR N=512^3 vs Newtonian N=196^3; dbar=0.01; quantity=|D_L^Newt/D_L^GR - 1| | 0.002456-0.8009 | 215 |
| `UD_aem44_lowres` | red | dotted [1 3] | ray=emitted at UD towards OD; a_em_label=44; resolution=low: GR N=192^3 vs Newtonian N=128^3; dbar=0.01; quantity=|D_L^Newt/D_L^GR - 1| | 0.002456-0.8143 | 222 |
| `UD_aem52_highres` | green (mpl "g") | solid | ray=emitted at UD towards OD; a_em_label=52; resolution=high: GR N=512^3 vs Newtonian N=196^3; dbar=0.01; quantity=|D_L^Newt/D_L^GR - 1| | 0.002456-0.826 | 181 |
| `UD_aem52_lowres` | green (mpl "g") | dotted [1 3] | ray=emitted at UD towards OD; a_em_label=52; resolution=low: GR N=192^3 vs Newtonian N=128^3; dbar=0.01; quantity=|D_L^Newt/D_L^GR - 1| | 0.002456-0.7921 | 203 |

## Notes
* Dips to zero (sign changes of the difference) go below the axes; the drawn path continues to the page edge
  (1.55e-5 or 1.43e-5) and is broken there, so a curve can have several segments; canvas_edge = 1 marks the cut points.
* `values_at_z.csv`: values at z = 0.1, 0.5, 1, 2 (every pass), and the maximum over the visible range.
* The caption calls this "similar to the top left panel of Fig. 4", but the quantity is that of the top right panel.
* The high-resolution curves are close to but not identical with Fig. 4 top right (median |log ratio| 0.005-0.03 dex
  for a_em >= 28, 0.07 dex for the a_em ~ 1 rays whose values are ~1e-3).

