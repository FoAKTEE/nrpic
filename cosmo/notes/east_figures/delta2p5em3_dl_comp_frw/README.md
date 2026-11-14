# delta2p5em3_dl_comp_frw: Fig. 4 row 3 left (dbar=0.0025)

Source: `refs/arxiv_1908.05683/src/delta2p5em3_dl_comp_frw.eps` (matplotlib 1.5.1, vector). Paper: East, Wojtak & Pretorius, arXiv:1908.05683.

## What is plotted
D_L(z)/D_L^LFRW(z) - 1 along fiducial null rays emitted at the overdensity (OD) towards the underdensity (UD), or vice versa, at several emission times a_em (legend). Coloured solid = GR; black dashed = Newtonian OD->UD; black dash-dot = Newtonian UD->OD (each black curve is drawn right after the GR curve of the same ray and shares its z end points). Vertical axis: symlog, linear within +-1e-2, log outside.

## Files
* `delta2p5em3_dl_comp_frw.csv`: long format, columns `curve, segment, z, DL_over_DL_LFRW_minus_1, visible, canvas_edge` (see the header comments).
* `curves.csv`: one row per curve with colour, line style and metadata.
* `check_delta2p5em3_dl_comp_frw.png`: the original EPS rendered with ghostscript (left) next to a replot of the CSV in data coordinates with the same axis limits and scales (right).

## Calibration
Curves are the stroked PostScript polylines; colour and dash pattern come from the setrgbcolor/setdash state; axes from the clip box; data coordinates from a least-squares fit of the major tick positions (tick marks paired with their labels in drawing order).
* x: log axis: pos = 392.166700 + 148.113400 * f(v); ticks used: 0.01@95.940, 0.1@244.053, 1@392.167, 10@540.280; max |residual| = 0.0003 pt
* y: symlog axis: pos = 239.692467 + 37.676049 * f(v) (linthresh=0.01, linscale_adj=1.11113); ticks used: -10@84.801, -1@122.477, -0.1@160.154, -0.01@197.830, 0@239.692, 0.01@281.555, 0.1@319.231, 1@356.908, 10@394.584; max |residual| = 0.0006 pt
* Axes box in data units: x in [0.01, 9.9938], y in [-30.01, 29.927].

## Accuracy
matplotlib simplified the paths with a tolerance of 1/9 pt (vertices within 0.11 pt of a straight run were dropped); coordinates are written to 1e-6 pt and the tick fit residual is < 1e-3 pt. Reading error: x +-0.17% (0.0008 dex), y +-2.7e-05 absolute inside |y|<1e-2, +-0.68% of |y| outside. Between vertices the curve is the straight line that was drawn (in display coordinates).

## Curves

| curve | colour | line | meaning | z range | points |
|---|---|---|---|---|---|
| `GR_OD_aem1` | maroon | solid | model=GR; ray=emitted at OD towards UD; a_em_label=1; dbar=0.0025 | 0.08982-6.514 | 28 |
| `Newt_OD_aem1` | black | dashed [6 6] | model=Newtonian; ray=emitted at OD towards UD; a_em_label=1; dbar=0.0025 | 0.08982-6.514 | 26 |
| `GR_UD_aem1` | chartreuse | solid | model=GR; ray=emitted at UD towards OD; a_em_label=1; dbar=0.0025 | 0.08981-6.394 | 29 |
| `Newt_UD_aem1` | black | dash-dot [3 5 1 5] | model=Newtonian; ray=emitted at UD towards OD; a_em_label=1; dbar=0.0025 | 0.08981-6.394 | 30 |
| `GR_OD_aem28` | red | solid | model=GR; ray=emitted at OD towards UD; a_em_label=28; dbar=0.0025 | 0.002216-0.7744 | 36 |
| `Newt_OD_aem28` | black | dashed [6 6] | model=Newtonian; ray=emitted at OD towards UD; a_em_label=28; dbar=0.0025 | 0.002216-0.7744 | 43 |
| `GR_UD_aem28` | forestgreen | solid | model=GR; ray=emitted at UD towards OD; a_em_label=28; dbar=0.0025 | 0.002216-0.742 | 34 |
| `Newt_UD_aem28` | black | dash-dot [3 5 1 5] | model=Newtonian; ray=emitted at UD towards OD; a_em_label=28; dbar=0.0025 | 0.002216-0.742 | 37 |
| `GR_OD_aem59` | chocolate | solid | model=GR; ray=emitted at OD towards UD; a_em_label=59; dbar=0.0025 | 0.002216-0.518 | 41 |
| `Newt_OD_aem59` | black | dashed [6 6] | model=Newtonian; ray=emitted at OD towards UD; a_em_label=59; dbar=0.0025 | 0.002216-0.518 | 43 |
| `GR_UD_aem58` | lightseagreen | solid | model=GR; ray=emitted at UD towards OD; a_em_label=58; dbar=0.0025 | 0.002216-0.4914 | 32 |
| `Newt_UD_aem58` | black | dash-dot [3 5 1 5] | model=Newtonian; ray=emitted at UD towards OD; a_em_label=58; dbar=0.0025 | 0.002216-0.4914 | 42 |
| `GR_OD_aem163` | darkorange | solid | model=GR; ray=emitted at OD towards UD; a_em_label=163; dbar=0.0025 | 0.002216-0.3046 | 114 |
| `Newt_OD_aem163` | black | dashed [6 6] | model=Newtonian; ray=emitted at OD towards UD; a_em_label=163; dbar=0.0025 | 0.002216-0.3046 | 114 |
| `GR_UD_aem162` | aqua/cyan | solid | model=GR; ray=emitted at UD towards OD; a_em_label=162; dbar=0.0025 | 0.002532-0.3112 | 119 |
| `Newt_UD_aem162` | black | dash-dot [3 5 1 5] | model=Newtonian; ray=emitted at UD towards OD; a_em_label=162; dbar=0.0025 | 0.002532-0.3112 | 119 |

## Notes
* The y axis is matplotlib symlog with linthresh = 1e-2 and linscale = 1 (fitted from the ticks: the 0 to 1e-2 stretch
  is 1/(1-1/10) = 1.111 decades long). Values inside +-1e-2 are linear.
* Curves run in ray order (from the emitter); z is not monotonic along some UD->OD rays (blueshift near the halo), so
  do not sort by z. Points at z < 0.01 (down to 0.0022) are drawn outside the axes and hidden in the paper (visible = 0).
* `values_at_z.csv`: values at z = 0.1, 0.5, 1, 2 (every pass of the ray through that z).

