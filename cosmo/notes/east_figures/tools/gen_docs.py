"""Write README.md for every figure folder and the top-level SUMMARY.md."""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
_REPO = _os.path.abspath(_os.path.join(_HERE, '..', '..', '..', '..'))

import os
import sys
import pickle
import numpy as np

sys.path.insert(0, _HERE + '/')
from extract_all import Curve  # noqa: F401,E402
import analyze as A  # noqa: E402

st, R = A.st, A.R
OUT = A.OUT
WORK = A.WORK
SG = pickle.load(open(os.path.join(WORK, 'signed.pkl'), 'rb'))
TOL = 1.0 / 9.0      # matplotlib path.simplify_threshold in pt


def acc(axis, gnu=False):
    e = 0.5 if gnu else TOL       # gnuplot: integer coords in 0.05 pt units -> +-0.5 unit
    if axis.kind == 'log':
        dex = e / axis.B
        return '+-%.2f%% (%.4f dex)' % ((10 ** dex - 1) * 100, dex)
    if axis.kind == 'lin':
        return '+-%.2g data units' % (e / axis.B)
    lin = e / (axis.B * axis.c / A_LT)
    dex = e / axis.B
    return '+-%.1e absolute inside |y|<1e-2, +-%.2f%% of |y| outside' % (lin, (10 ** dex - 1) * 100)


A_LT = 1e-2


def fmt(v, f='%.4g'):
    return '-' if v is None else f % v


def mean_rng(vals, f='%.1f'):
    v = [x for x in vals if x is not None]
    if not v:
        return '-'
    if len(v) == 1:
        return f % v[0]
    return (f + ' [' + f + '-' + f + ']') % (np.mean(v), min(v), max(v))


FIGNO = {
    'ud_comp': 'Fig. 1 top', 'od_comp': 'Fig. 1 middle', 'delta10m2_comp_all': 'Fig. 1 bottom',
    'delta5em2pm_splash': 'Fig. 2 top left (dbar=0.05)', 'delta10em2pm_splash': 'Fig. 2 top right (dbar=0.01)',
    'delta5em3pm_splash': 'Fig. 2 bottom left (dbar=0.005)', 'delta2p5em3pm_splash': 'Fig. 2 bottom right (dbar=0.0025)',
    'rel_eff': 'Fig. 3',
    'delta1em2_dl_comp_frw': 'Fig. 4 row 1 left (dbar=0.01)', 'delta1em2_dl_newt_gr': 'Fig. 4 row 1 right (dbar=0.01)',
    'delta5em3_dl_comp_frw': 'Fig. 4 row 2 left (dbar=0.005)', 'delta5em3_dl_newt_gr': 'Fig. 4 row 2 right (dbar=0.005)',
    'delta2p5em3_dl_comp_frw': 'Fig. 4 row 3 left (dbar=0.0025)', 'delta2p5em3_dl_newt_gr': 'Fig. 4 row 3 right (dbar=0.0025)',
    'delta5em2_dl_comp_frw': 'Fig. 5 (dbar=0.05)', '10m2_cnst_conv': 'Fig. 6 (appendix)',
    'res_delta10em2pm_splash': 'Fig. 7 top (appendix, GR)', 'res_newt_delta10em2pm_splash': 'Fig. 7 bottom (appendix, Newtonian)',
    'delta1em2_dl_newt_gr_res_ou': 'Fig. 8 top (appendix, rays from OD)', 'delta1em2_dl_newt_gr_res_uo': 'Fig. 8 bottom (appendix, rays from UD)'}

WHAT = {
    'ud_comp': ('|delta_obs| at the point of minimum density (void centre) against the proper-time scale factor a_p of the '
                'observer there, for dbar = 0.0025, 0.005, 0.01, 0.05 (bottom to top). Black solid = GR, red dashed = '
                'Newtonian (tetrahedral phase-space density). Default resolutions.'),
    'od_comp': ('|delta_obs| at the point of maximum density (halo centre) against a_p, for dbar = 0.0025, 0.005, 0.01, 0.05 '
                '(right to left). Black solid = GR, red dashed = Newtonian (tetrahedral density), magenta dotted = '
                'Newtonian with a CIC density estimate (only dbar = 0.01 and 0.05). Default resolutions.'),
    'delta10m2_comp_all': ('|delta_obs| at the maximum-density point for dbar = 0.01 (linear a_p axis) for several resolutions '
                           'and for particle versus pressureless-fluid GR matter.'),
    'rel_eff': ('|d_OD^Newt - d_OD^GR|/L for three fiducial particles of Fig. 2 against the magnitude of the infall '
                'velocity from the Newtonian run, up to the first Newtonian halo crossing. gnuplot figure.'),
    '10m2_cnst_conv': ('L2 norm of the generalized-harmonic constraint C_a = H_a - Box x_a (divided by L^2) against the '
                       'volume-averaged scale factor <a>, dbar = 0.01, three GR resolutions, rescaled assuming second-order '
                       'convergence (factors 1, 2.25, 4 as in the legend).'),
}
for n in ['delta5em2pm_splash', 'delta10em2pm_splash', 'delta5em3pm_splash', 'delta2p5em3pm_splash']:
    WHAT[n] = ('Coordinate distance d (>= 0) from the point of maximum density, divided by the box length L, of 12 fiducial '
               'particles against their own proper-time scale factor a_p. Top half: +d/L from the GR run; bottom half: '
               '-d/L from the Newtonian run. Colour = initial displacement direction (red x, green y, blue z); line style = '
               'initial distance (solid L/32, dotted L/16, dashed L/8, dash-dot L/4).')
WHAT['res_delta10em2pm_splash'] = ('As Fig. 2 (dbar = 0.01), GR only: top half +d/L from the low-resolution run (caption: N=128^3), '
                                   'bottom half -d/L from the high-resolution run (caption: N=384^3).')
WHAT['res_newt_delta10em2pm_splash'] = ('As Fig. 2 (dbar = 0.01), Newtonian only: top half +d/L from N=128^3, bottom half -d/L from '
                                        'N=196^3 (caption).')
for n in ['delta1em2_dl_comp_frw', 'delta5em3_dl_comp_frw', 'delta2p5em3_dl_comp_frw', 'delta5em2_dl_comp_frw']:
    WHAT[n] = ('D_L(z)/D_L^LFRW(z) - 1 along fiducial null rays emitted at the overdensity (OD) towards the underdensity (UD), '
               'or vice versa, at several emission times a_em (legend). Coloured solid = GR; black dashed = Newtonian OD->UD; '
               'black dash-dot = Newtonian UD->OD (each black curve is drawn right after the GR curve of the same ray and '
               'shares its z end points). Vertical axis: symlog, linear within +-1e-2, log outside.')
for n in ['delta1em2_dl_newt_gr', 'delta5em3_dl_newt_gr', 'delta2p5em3_dl_newt_gr']:
    WHAT[n] = ('|D_L^Newt(z)/D_L^GR(z) - 1| for the same rays as the left column: solid = rays emitted at the OD, dashed = '
               'rays emitted at the UD, colour = emission time a_em (legend).')
WHAT['delta1em2_dl_newt_gr_res_ou'] = ('|D_L^Newt/D_L^GR - 1| for dbar = 0.01, rays emitted at the OD, at two resolutions: solid = '
                                       'high (GR N=512^3 vs Newtonian N=196^3), dotted = low (GR N=192^3 vs Newtonian N=128^3); '
                                       'colour = a_em (black 1, blue 28, red 43, green 52).')
WHAT['delta1em2_dl_newt_gr_res_uo'] = ('As the top panel for rays emitted at the UD (black a_em 1, blue 27, red 44, green 52).')

XY = {'ud_comp': ('a_p', 'abs_delta_obs'), 'od_comp': ('a_p', 'abs_delta_obs'), 'delta10m2_comp_all': ('a_p', 'abs_delta_obs'),
      'rel_eff': ('abs_v_infall', 'abs_dNewt_minus_dGR_over_L'), '10m2_cnst_conv': ('a_avg', 'scaled_constraint_norm')}


def xy(n):
    if n in XY:
        return XY[n]
    if 'splash' in n:
        return ('a_p', 'plotted_y (= +d/L top half, -d/L bottom half)')
    if 'comp_frw' in n:
        return ('z', 'DL_over_DL_LFRW_minus_1')
    return ('z', 'abs_DL_Newt_over_DL_GR_minus_1')


def meta_str(c):
    skip = {'legend'}
    return '; '.join('%s=%s' % (k, v) for k, v in c.meta.items() if k not in skip)


# ------------------------------------------------------------------ READMEs
SPECIFIC = {}
SPECIFIC['ud_comp'] = """
## Derived numbers
`values_at_ap.csv`: |delta_obs| of GR and Newtonian at a_p = 1, 2, 5, 10, 20, 50, 100 where plotted.

## Checks
* At a_p = 1 the GR curves start at |delta_obs| = 6.644 dbar for all four amplitudes. Linear theory for the
  longitudinal-gauge density of the k = pi H0/2 mode gives 3 dbar (1 + 3H0^2/k^2) = 3 dbar (1 + 12/pi^2) = 6.648 dbar
  (the 3 is 1 + 0.9 + 1.1 at the void), so the y calibration is right to < 0.1%.
* Caption: "Newtonian and GR curves ... essentially indistinguishable": max |Newt/GR - 1| over the common range is
  2.0%, 2.3%, 2.2% for dbar = 0.0025, 0.005, 0.01 and 3.9% for 0.05 (the latter at a_p = 1, where the Newtonian
  initial value is 0.319 against 0.332 for GR).
"""
SPECIFIC['od_comp'] = """
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
"""
SPECIFIC['delta10m2_comp_all'] = """
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
"""
SPLASH_NOTE = """
## Derived numbers
`turning_points.csv`, one row per particle: initial plotted distance d0; a_p where d first drops below 0.1 d0 and
0.05 d0 (robust infall markers); the first crossing = first local minimum of d after d < 0.15 d0, with the a_p
interval over which the drawn d stays within max(5e-4, 0.02 d0) of that minimum; up to four following turning points
(hysteresis max(5e-4, 0.04 d0)); end point. d >= 0 is a distance (the GR half never goes below 0 and the Newtonian
half never above 0), so a crossing is a near-zero minimum, not a sign change.

Sampling: the Newtonian curves have one vertex per output (spacing ~1.3 in a_p near a_p ~ 57 for dbar = 0.01, ~2.7
near 115 for 0.005, ~5.6 near 230 for 0.0025), so Newtonian crossing times are uncertain by about half that spacing.
GR curves are sampled finely but matplotlib dropped vertices on near-straight stretches.
"""
for n in ['delta5em2pm_splash', 'delta10em2pm_splash', 'delta5em3pm_splash', 'delta2p5em3pm_splash',
          'res_delta10em2pm_splash', 'res_newt_delta10em2pm_splash']:
    SPECIFIC[n] = SPLASH_NOTE
SPECIFIC['delta5em2pm_splash'] += """
## Notes
* The Newtonian run ends at a_p = 10.8-11.2 for the three inner particle sets and 13.3-13.9 for d0 = L/4; no
  Newtonian particle reaches the centre. GR particles with d0 <= L/8 reach their first minimum at a_p = 16.2-17.7.
* The GR d0 = L/4 curves rise above the axes (to the page edge, d/L = 0.28, between a_p ~ 4.2 and 7.5); that part is
  missing from the file (two segments per curve).
* GR initial (gauge) oscillation: d rises by 8-12% above d0 by a_p ~ 5.5 before falling.
"""
SPECIFIC['delta10em2pm_splash'] += """
## Notes
* Identical (<= 3e-4 in d/L) to the "High res." half of Fig. 7 top (GR) and exactly identical to the "High res." half
  of Fig. 7 bottom (Newtonian), so this panel uses the GR N = 384^3 and Newtonian N = 196^3 runs of the Fig. 7 caption.
"""
SPECIFIC['delta5em3pm_splash'] += """
## Notes
* The Newtonian particles start at d/L = 0.0327, 0.0639, 0.1264, 0.2513 instead of 1/32, 1/16, 1/8, 1/4 (an offset of
  +0.0013 to +0.0015 L in all 12 curves); every other panel starts at the nominal values to 1e-4.
"""
SPECIFIC['rel_eff'] = """
## Checks
* The first point of each curve is the initial Zel'dovich speed of an x-displaced particle,
  |v| = (H0 dbar / k) sin(k d0) with k = 2 pi / L and H0/k = 2/pi: predicted 3.11e-4, 2.44e-3, 6.37e-3; read
  3.15e-4, 2.47e-3, 6.44e-3 (1% agreement). This confirms the x calibration, L = one wavelength = 4/H0, and that the
  third curve is dbar = 0.01 with d0 = L/4 as labelled (dbar = 0.05 would start at 3.2e-2). All three are x-direction
  particles (y and z would start 10% lower/higher).
* Rebuilding |d_N - d_GR|/L from Fig. 2 at the first Newtonian crossing gives 0.0132-0.0145 (dbar = 0.01, d0 = L/16, x and
  y directions) against 0.0133 at the end of the teal curve, and 0.0022-0.0036 (dbar = 0.0025, d0 = L/32) against
  0.0034 at the end of the purple curve.

## Notes
* The orange curve leaves the plot at the right edge (|v| = 0.511, value 0.052); the rest of it is not in the file.
* Each curve ends with a vertical segment (purple at |v| = 0.0057, teal and orange where marked), i.e. |dd| keeps
  changing while |v| does not.
* `envelope.csv`: upper envelope and median of the three curves in bins of |v| (0.25 dex).
"""
SPECIFIC['10m2_cnst_conv'] = """
## Derived numbers
`values_at_a.csv`: plotted (rescaled) and raw (= plotted / factor) norms at selected <a>.

## Notes
* The rescaled curves do not overlap for <a> < ~80: the implied convergence order between L/dx = 64 and 96 is
  3.7-3.8 for <a> < 5 and ~5.5 for 20 < <a> < 60, and 3.3-4.3 between 96 and 128; the 64 and 96 curves meet only for
  <a> > ~95 (order ~2 there), where the caption says finite-particle error takes over.
* All three curves start with a spike at <a> ~ 1.04-1.07 (plotted 3.96e-3, 1.86e-3, 1.21e-3). The L/dx = 128 curve
  ends at <a> = 81.8.
"""
DL_LEFT_NOTE = """
## Notes
* The y axis is matplotlib symlog with linthresh = 1e-2 and linscale = 1 (fitted from the ticks: the 0 to 1e-2 stretch
  is 1/(1-1/10) = 1.111 decades long). Values inside +-1e-2 are linear.
* Curves run in ray order (from the emitter); z is not monotonic along some UD->OD rays (blueshift near the halo), so
  do not sort by z. Points at z < 0.01 (down to 0.0022) are drawn outside the axes and hidden in the paper (visible = 0).
* `values_at_z.csv`: values at z = 0.1, 0.5, 1, 2 (every pass of the ray through that z).
"""
DL_RIGHT_NOTE = """
## Notes
* Dips to zero (sign changes of the difference) go below the axes; the drawn path continues to the page edge
  (1.55e-5 or 1.43e-5) and is broken there, so a curve can have several segments; canvas_edge = 1 marks the cut points.
* `values_at_z.csv`: values at z = 0.1, 0.5, 1, 2 (every pass), and the maximum over the visible range.
"""
for n in st:
    if 'comp_frw' in n:
        SPECIFIC[n] = DL_LEFT_NOTE
    elif '_dl_newt_gr' in n:
        SPECIFIC[n] = DL_RIGHT_NOTE
SPECIFIC['delta1em2_dl_newt_gr_res_ou'] = DL_RIGHT_NOTE + """* The caption calls this "similar to the top left panel of Fig. 4", but the quantity is that of the top right panel.
* The high-resolution curves are close to but not identical with Fig. 4 top right (median |log ratio| 0.005-0.03 dex
  for a_em >= 28, 0.07 dex for the a_em ~ 1 rays whose values are ~1e-3).
"""
SPECIFIC['delta1em2_dl_newt_gr_res_uo'] = SPECIFIC['delta1em2_dl_newt_gr_res_ou']


def write_values_at_z(n):
    D = R['dl'][n]
    with open(os.path.join(OUT, n, 'values_at_z.csv'), 'w') as f:
        f.write('# values of the plotted quantity where each ray passes z (several values = several passes, in ray order);\n')
        f.write('# z_min/z_max over drawn points (incl. hidden z<0.01); max_visible = largest value inside the axes and its z\n')
        f.write('curve,z_min,z_max,z_first_point,z_last_point,z_nonmonotonic,at_z0.1,at_z0.5,at_z1,at_z2,max_visible,z_at_max_visible\n')
        for c in st[n]['curves']:
            M = D[c.id]
            vals = [';'.join('%.5g' % v for v in M['vals'][z]) for z in A.ZS]
            mx = M.get('max_vis', (None, None))
            f.write('%s,%.5g,%.5g,%.5g,%.5g,%d,%s,%s,%s,%s,%s,%s\n' % (
                c.id, M['zmin'], M['zmax'], M['z_first'], M['z_last'], int(M['nonmono']), *vals,
                fmt(mx[0], '%.5g') if mx[0] is not None else '', fmt(mx[1], '%.5g') if mx[1] is not None else ''))


for n, v in st.items():
    if '_dl_' in n:
        write_values_at_z(n)
    X, Y = v['Xaxis'], v['Yaxis']
    gnu = (n == 'rel_eff')
    xc, yc = xy(n)
    lines = ['# %s: %s' % (n, FIGNO[n]), '',
             'Source: `refs/arxiv_1908.05683/src/%s.eps` (%s, vector). Paper: East, Wojtak & Pretorius, '
             'arXiv:1908.05683.' % (n, 'gnuplot 5.2' if gnu else 'matplotlib 1.5.1'), '',
             '## What is plotted', WHAT[n], '',
             '## Files',
             '* `%s.csv`: long format, columns `curve, segment, %s, %s, visible, canvas_edge` (see the header comments).' % (n, xc, yc),
             '* `curves.csv`: one row per curve with colour, line style and metadata.',
             '* `check_%s.png`: the original EPS rendered with ghostscript (left) next to a replot of the CSV in data '
             'coordinates with the same axis limits and scales (right).' % n, '',
             '## Calibration',
             'Curves are the stroked PostScript polylines; colour and dash pattern come from the setrgbcolor/setdash state; '
             'axes from the clip box; data coordinates from a least-squares fit of the major tick positions (tick marks '
             'paired with their labels in drawing order).',
             '* x: %s' % X.describe(), '* y: %s' % Y.describe(),
             '* Axes box in data units: x in [%.5g, %.5g], y in [%.5g, %.5g].' % (*v['box']['xlim'], *v['box']['ylim']), '',
             '## Accuracy',
             ('gnuplot writes integer coordinates in 0.05 pt units and does not simplify paths, so the reading error is '
              '+-0.025 pt: x %s, y %s.' % (acc(X, True), acc(Y, True))) if gnu else
             ('matplotlib simplified the paths with a tolerance of 1/9 pt (vertices within 0.11 pt of a straight run were '
              'dropped); coordinates are written to 1e-6 pt and the tick fit residual is < 1e-3 pt. Reading error: x %s, '
              'y %s. Between vertices the curve is the straight line that was drawn (in display coordinates).' % (acc(X), acc(Y))),
             '', '## Curves', '', '| curve | colour | line | meaning | %s range | points |' % xc, '|---|---|---|---|---|---|']
    for c in v['curves']:
        lines.append('| `%s` | %s | %s | %s | %.4g-%.4g | %d |' % (c.id, c.color, c.dash, meta_str(c), np.nanmin(c.x), np.nanmax(c.x), len(c.x)))
    lines.append(SPECIFIC.get(n, ''))
    open(os.path.join(OUT, n, 'README.md'), 'w').write('\n'.join(lines) + '\n')

# ------------------------------------------------------------------ SUMMARY
S = []
w = S.append
w('# East, Wojtak & Pretorius (arXiv:1908.05683): numbers read from the figures')
w('')
w('Curves of every figure of the paper, extracted for a quantitative comparison with our code. Per-figure data, '
  'calibration and accuracy are in `cosmo/notes/east_figures/<eps name>/` (`<name>.csv`, `curves.csv`, derived-number CSVs, '
  '`README.md`, and `check_<name>.png` comparing the original rendering with a replot of the extracted numbers). The '
  'scripts are in `.work/east_fig_tools/`; run order `extract_all.py`, `analyze.py`, `replot.py`, `extra_checks.py`, '
  '`gen_docs.py` (helpers `psparse.py`, `calib.py`), all with `python3 -E` from that folder.')
w('')
w('**All 20 figures are vector graphics** (19 matplotlib 1.5.1, 1 gnuplot 5.2); no figure contains a raster image. Every '
  'number below is therefore **vector**: read from the PostScript polylines, calibrated on the tick marks. Nothing was '
  'traced from pixels.')
w('')
w('## Conventions')
w('* a_p = (3 tau H0/2 + 1)^(2/3), with tau the proper time of the observer or particle concerned (so different curves '
  'have different a_p at the same coordinate time).')
w('* dbar: amplitude in delta_N = sum_i dbar_i sin(k x^i), dbar_i = dbar (1, 0.9, 1.1) for (x, y, z), k = pi H0/2.')
w('* L: box length = one wavelength = 4/H0 (Fig. 6 legend "L/dx = 96" and the text "96 points across the wavelength"; '
  'the Fig. 3 initial speeds also require L = 2 pi/k).')
w('* d: coordinate distance (>= 0) of a fiducial particle from the point of maximum density.')
w('* GR = Einstein-Vlasov run; Newt = GADGET-2 run (density from the tetrahedral phase-space estimator unless "CIC").')
w('')
w('## Accuracy')
w('matplotlib 1.5 simplifies paths before writing them: a vertex is dropped when it lies within 1/9 pt of a straight run, '
  'so the drawn line is within 0.11 pt of the data. Coordinates carry 6 decimals and the tick fits have residuals below '
  '1e-3 pt, so 0.11 pt is the reading error. In data units:')
w('')
w('| figure | x axis | x error | y axis | y error |')
w('|---|---|---|---|---|')
for n, v in st.items():
    gnu = n == 'rel_eff'
    w('| %s (`%s`) | %s %.4g-%.4g | %s | %s %.4g-%.4g | %s |' % (
        FIGNO[n], n, v['Xaxis'].kind, *v['box']['xlim'], acc(v['Xaxis'], gnu), v['Yaxis'].kind, *v['box']['ylim'], acc(v['Yaxis'], gnu)))
w('')
w('A second, often larger, limit is the sampling of the underlying data: Newtonian curves have one vertex per snapshot '
  '(Delta a_p ~ 1.3 near a_p ~ 57 for dbar = 0.01), which bounds how well a crossing time can be located. Interpolated '
  'values (crossings, values at given a_p or z) are taken along the drawn line in display coordinates, i.e. log-log '
  'interpolation on log axes.')
w('')

# ---- Fig 1 top
w('## Fig. 1 top: void (minimum density), |delta_obs|(a_p)  [vector, +-0.15%]')
w('')
w('| dbar | model | ' + ' | '.join('a_p=%g' % a for a in A.APS) + ' | end of curve (a_p, value) |')
w('|---|---|' + '---|' * len(A.APS) + '---|')
for amp in [0.0025, 0.005, 0.01, 0.05]:
    for model, idx in [('GR', 2), ('Newt', 3)]:
        vals = [r[idx] for r in R['ud_rows'] if r[0] == amp]
        c = A.cur('ud_comp', '%s_dbar%g' % (model, amp))
        w('| %g | %s | %s | (%.1f, %.3f) |' % (amp, model, ' | '.join(fmt(x, '%.4f') for x in vals), c.x[-1], c.y[-1]))
w('')
w('Newt/GR - 1 at the same a_p: ' + '; '.join(
    'dbar=%g: %s' % (amp, ', '.join('%+.1f%%' % (100 * (r[3] / r[2] - 1)) for r in R['ud_rows'] if r[0] == amp and r[2] and r[3]))
    for amp in [0.0025, 0.005, 0.01, 0.05]) + ' (a_p = 1, 2, 5, ... in order). Largest |Newt/GR - 1| over the common range: ' +
    ', '.join('%.1f%% (dbar=%g, at a_p=%.0f)' % (100 * v[0], k, v[1]) for k, v in R['ud_maxrel'].items()) + '.')
w('')

# ---- Fig 1 middle
w('## Fig. 1 middle: halo (maximum density), |delta_obs|(a_p)  [vector; a_p +-0.13%, |delta_obs| +-0.7%]')
w('')
w('First maximum = first local maximum followed by a drop > 0.05 dex; plateau = median [min-max] of |delta_obs| from the '
  'first maximum to the end of the curve.')
w('')
w('| dbar | model | a_p at 1 | a_p at 10 | a_p at 100 | a_p at 1000 | first max: a_p, value | plateau median [min-max] | end: a_p, value |')
w('|---|---|---|---|---|---|---|---|---|')
for amp in [0.0025, 0.005, 0.01, 0.05]:
    for model in ['GR', 'Newt', 'NewtCIC']:
        cid = '%s_dbar%g' % (model, amp)
        if cid not in R['od']:
            continue
        M = R['od'][cid]
        fm = M['first_max']
        pl = M['plateau']
        w('| %g | %s | %s | %s | %s | %s | %s | %s | %.2f, %.4g |' % (
            amp, {'GR': 'GR', 'Newt': 'Newtonian', 'NewtCIC': 'Newtonian CIC'}[model],
            *[fmt(M['cross'][L], '%.2f') for L in A.LEV],
            '%.2f, %.4g' % fm if fm else 'none before end',
            '%.4g [%.4g-%.4g]' % pl[:3] if pl else '-', *M['end']))
w('')
w('Notes: GR dbar = 0.0025 is still rising at the end (499 at a_p = 255.2); GR dbar = 0.05 levels off at 236-237 for '
  'a_p = 16.4-16.8 (end of run); the Newtonian dbar = 0.05 run stops at a_p = 10.86 (|delta_obs| = 1087, CIC 156); the '
  'CIC dbar = 0.01 curve rises slowly to 2440 at a_p = 90.4 without a maximum.')
w('')
w('Ratio of GR to Newtonian a_p at the same |delta_obs|:')
w('')
w('| dbar | at 1 | at 10 | at 100 |')
w('|---|---|---|---|')
for amp in [0.0025, 0.005, 0.01, 0.05]:
    g = R['od']['GR_dbar%g' % amp]['cross']
    nn = R['od']['Newt_dbar%g' % amp]['cross']
    w('| %g | %s |' % (amp, ' | '.join('%.3f' % (g[L] / nn[L]) for L in [1, 10, 100])))
w('')

# ---- Fig 1 bottom
w('## Fig. 1 bottom: dbar = 0.01 halo, resolutions and fluid vs particles  [vector; a_p +-0.03, |delta_obs| +-0.4%]')
w('')
w('| curve (legend) | a_p at 1 | a_p at 10 | a_p at 100 | a_p at 1000 | first max: a_p, value | plateau median [min-max] | end: a_p, value |')
w('|---|---|---|---|---|---|---|---|')
for c in st['delta10m2_comp_all']['curves']:
    M = R['od_all'][c.id]
    fm, pl = M['first_max'], M['plateau']
    w('| %s (%s, %s) | %s | %s | %s | %s | %s | %s | %.2f, %.4g |' % (
        c.meta['legend'], c.color.split(' (')[0], c.dash.split(' [')[0], *[fmt(M['cross'][L], '%.2f') for L in A.LEV],
        '%.2f, %.4g' % fm if fm else '-', '%.4g [%.4g-%.4g]' % pl[:3] if pl else '-', *M['end']))
w('')
w('Values above 1e4 are outside the axes (hidden in the paper) and the paths stop at the page edge, 2.35e4. "Newt. OD '
  'High Res." is the default N = 196^3 run (identical to Fig. 1 middle to 0.004 dex), so "Newt. OD" is N = 128^3. The '
  'Fig. 1 middle GR dbar = 0.01 curve lies between "GR OD" and "GR OD High Res." (see contradictions below). '
  'Fluid vs particles (default resolution): a_p at |delta_obs| = 100 is 55.85 (fluid) vs 58.94 (particles).')
w('')

# ---- Fig 2
w('## Fig. 2 (and Fig. 7): fiducial particles, d/L against a_p  [vector; d/L +-1.6e-4]')
w('')
w('Each panel: 24 curves = 2 models (GR top half, plotted +d/L; Newtonian bottom half, plotted -d/L) x 3 directions '
  '(red x, green y, blue z) x 4 initial distances d0 = L/32, L/16, L/8, L/4 (solid, dotted, dashed, dash-dot). Plotted '
  'ranges: y in [-0.26, 0.26] for all panels; x (a_p) in')
for n in ['delta5em2pm_splash', 'delta10em2pm_splash', 'delta5em3pm_splash', 'delta2p5em3pm_splash',
          'res_delta10em2pm_splash', 'res_newt_delta10em2pm_splash']:
    v = st[n]
    gend = [c.x[-1] for c in v['curves'] if c.meta['half'].startswith('top')]
    nend = [c.x[-1] for c in v['curves'] if c.meta['half'].startswith('bottom')]
    w('* %s: [%.3g, %.4g]; curves end at a_p = %.4g-%.4g (top half), %.4g-%.4g (bottom half)' % (
        FIGNO[n], *v['box']['xlim'], min(gend), max(gend), min(nend), max(nend)))
w('')
w('Initial distances read from the curves: d0/L = 0.03125, 0.0625, 0.125, 0.25 (+-1e-4) in every panel except the '
  'Newtonian half of dbar = 0.005, which starts at 0.0327, 0.0639, 0.1264, 0.2513.')
w('')
w('Crossing times. a_min = first local minimum of d after d < 0.15 d0 (the crossing); a_10 = a_p where d first falls '
  'below 0.1 d0 (a robust infall marker that does not depend on the sampling near zero). Mean over the x, y, z particles '
  '[min-max]; "-" = not reached before the curve ends. Uncertainty of a_min (half the a_p interval over which the drawn d '
  'stays within max(5e-4, 0.02 d0) of its minimum, `bracket_lo/hi` in turning_points.csv): typically +-0.3 (dbar = 0.05), '
  '+-0.75 (0.01), +-1.5 (0.005), +-3 (0.0025) in both models, up to +-17 for small-d0 Newtonian particles that settle at '
  'd ~ 0; the Newtonian snapshot spacing near the crossing is ~1.3, 2.8, 5.7 for dbar = 0.01, 0.005, 0.0025. a_10 is '
  'good to about +-0.3 (0.01), +-0.6, +-1.2 and is the better number to compare with. GR/Newt a_10 = ratio of the means; '
  '"*" = only the directions present in both models.')
w('')
w('| dbar | d0/L | GR a_min | Newt a_min | GR a_10 | Newt a_10 | GR/Newt a_10 |')
w('|---|---|---|---|---|---|---|')
for n, amp in [('delta2p5em3pm_splash', 0.0025), ('delta5em3pm_splash', 0.005), ('delta10em2pm_splash', 0.01), ('delta5em2pm_splash', 0.05)]:
    D = R['splash'][n]
    for d0 in [0.03125, 0.0625, 0.125, 0.25]:
        g = [D['GR_%s_d0_%g' % (d, d0)] for d in 'xyz']
        nn = [D['Newt_%s_d0_%g' % (d, d0)] for d in 'xyz']
        gm = [M['cross'][0] if M.get('crossed') else None for M in g]
        nm = [M['cross'][0] if M.get('crossed') else None for M in nn]
        g10 = [M['t10'] for M in g]
        n10 = [M['t10'] for M in nn]
        ratio = '-'
        both = [i for i in range(3) if g10[i] and n10[i]]
        if both:
            ratio = '%.3f' % (np.mean([g10[i] for i in both]) / np.mean([n10[i] for i in both]))
            if len(both) < 3:
                ratio += '*'
        w('| %g | %g | %s | %s | %s | %s | %s |' % (amp, d0, mean_rng(gm), mean_rng(nm), mean_rng(g10), mean_rng(n10), ratio))
w('')
w('Per-direction values (x, y, z) of a_min, in that order:')
w('')
for n, amp in [('delta2p5em3pm_splash', 0.0025), ('delta5em3pm_splash', 0.005), ('delta10em2pm_splash', 0.01), ('delta5em2pm_splash', 0.05)]:
    D = R['splash'][n]
    parts = []
    for model in ['GR', 'Newt']:
        for d0 in [0.03125, 0.0625, 0.125, 0.25]:
            vals = []
            for d in 'xyz':
                M = D['%s_%s_d0_%g' % (model, d, d0)]
                vals.append('%.2f' % M['cross'][0] if M.get('crossed') else '-')
            parts.append('%s L/%d: %s' % (model, int(round(1 / d0)), ', '.join(vals)))
    w('* dbar = %g: %s' % (amp, '; '.join(parts)))
w('')
w('Turning points after the first crossing (dbar = 0.01; a_p, d/L), from `delta10em2pm_splash/turning_points.csv`:')
w('')
D = R['splash']['delta10em2pm_splash']
w('| particle | GR: cross; next turning points | Newt: cross; next turning points |')
w('|---|---|---|')
for d0 in [0.03125, 0.0625, 0.125, 0.25]:
    for d in 'xyz':
        row = []
        for model in ['GR', 'Newt']:
            M = D['%s_%s_d0_%g' % (model, d, d0)]
            if not M.get('crossed'):
                row.append('-')
                continue
            s = 'min %.2f (%.4f)' % M['cross']
            for k, a, dd in M.get('turning', []):
                s += '; %s %.2f (%.4f)' % (k, a, dd)
            row.append(s)
        w('| %s, L/%d | %s | %s |' % (d, int(round(1 / d0)), row[0], row[1]))
w('')
w('Small-d0 Newtonian particles stay within d < 0.003 L after reaching the centre (no resolvable second apocentre), so '
  'their "first minimum" can be one or two snapshots after a_10; use a_10 or a_05 for them.')
w('')
w('Fig. 7 (resolution, dbar = 0.01): a_min mean over x, y, z [range]:')
w('')
w('| d0/L | GR low (N=128^3) | GR high (N=384^3) | Newt low (128^3) | Newt high (196^3) |')
w('|---|---|---|---|---|')
for d0 in [0.03125, 0.0625, 0.125, 0.25]:
    cells = []
    for n, tag in [('res_delta10em2pm_splash', 'GRlow'), ('res_delta10em2pm_splash', 'GRhigh'),
                   ('res_newt_delta10em2pm_splash', 'Newtlow'), ('res_newt_delta10em2pm_splash', 'Newthigh')]:
        Ds = R['splash'][n]
        cells.append(mean_rng([Ds['%s_%s_d0_%g' % (tag, d, d0)]['cross'][0] if Ds['%s_%s_d0_%g' % (tag, d, d0)].get('crossed') else None for d in 'xyz']))
    w('| %g | %s |' % (d0, ' | '.join(cells)))
w('')
w('First apocentre after the crossing, GR low vs high (dbar = 0.01, d0 = L/8): x 84.7 vs 77.5, y - vs 78.6, z 82.5 vs 76.2 '
  '(the resolution dependence grows after the first crossing, as the appendix says).')
w('')

# ---- Fig 3
w('## Fig. 3: |d_OD^Newt - d_OD^GR|/L against |v_infall|  [vector (gnuplot); +-0.06% in |v|, +-0.08% in the difference]')
w('')
w('* x: |v_infall|, the magnitude of the infall speed in the Newtonian run in units of c, log axis 3.15e-4 to 0.511 '
  '(ticks 0.001, 0.01, 0.1). y: |d_OD^Newt - d_OD^GR|/L, log axis 1e-5 to 0.1. Each curve stops at the first Newtonian '
  'halo crossing (caption); gnuplot clips at the axes box.')
w('* Curves (all x-direction particles, see check): ')
for c in st['rel_eff']['curves']:
    M = R['rel_eff'][c.id]
    w('  * %s (%s): |v| from %.3g to %.3g; |dd|/L = %.2g at the start, %.3g at the last point (|v| = %.3g); largest value '
      'away from the axes edges %.3g at |v| = %.3g.' % (c.meta['legend'], c.color.split(' (')[0], M['vmin'], M['vmax'],
                                                       M['y_start'][1], M['end'][1], M['end'][0], M['ymax'], M['v_at_ymax']))
w('* Upper envelope of the three curves (max |dd|/L in 0.25-dex bins of |v|): ' + ', '.join(
    '%.2g-%.2g: %s' % (lo, hi, fmt(mx, '%.2g')) for lo, hi, mx, md in R['rel_env'] if mx) + '.')
_ax = np.concatenate([c.x for c in st['rel_eff']['curves']])
_ay = np.concatenate([c.y for c in st['rel_eff']['curves']])
_ae = np.concatenate([np.concatenate([sg['edge'] for sg in c.segs]) for c in st['rel_eff']['curves']])
_thr = []
for T in [3e-4, 1e-3, 3e-3, 1e-2, 3e-2]:
    m = (_ay > T) & ~_ae
    _thr.append('< %g for |v| < %.3g' % (T, _ax[m].min()))
w('* In words (all three curves together): |dd|/L stays ' + ', '.join(_thr) + '; the curves pass through zero (deep dips) '
  'several times, so the envelope, not individual values, is the meaningful quantity.')
w('')

# ---- Figs 4, 5, 8


def dl_tables(amp, left, right):
    out = []
    Dl = R['dl'][left]
    Dr = R['dl'][right] if right else None
    out.append('| ray (a_em) | z range drawn [visible part] | GR: y at z=0.1, 0.5, 1, 2 | Newt: y at z=0.1, 0.5, 1, 2 | '
               + ('|dD/D| (right column) at z=0.1, 0.5, 1, 2 | max |dD/D| visible (z) |' if right else
                  'reconstructed GR-Newt s=(1+y_N)/(1+y_GR)-1: max |s| (z) |'))
    out.append('|---|---|---|---|---|' + ('---|' if right else ''))
    for c in st[left]['curves']:
        if not c.id.startswith('GR_'):
            continue
        g = Dl[c.id]
        nn = Dl['Newt_' + c.id[3:]]
        src, aem = c.id[3:].split('_aem')

        def zs(M):
            return ', '.join('/'.join('%.4g' % x for x in M['vals'][z]) if M['vals'][z] else '-' for z in A.ZS)
        zr = '%.3g-%.3g [%.3g-%.3g]' % (g['zmin'], g['zmax'], max(0.01, g['zmin']), g['zmax'])
        if g['nonmono']:
            zr += ', z turns back (ends at %.3g)' % g['z_last']
        if right:
            rid = '%s_aem%s' % (src, aem)
            M = Dr.get(rid)
            if M is None:
                cand = [k for k in Dr if k.startswith(src + '_aem') and abs(float(k.split('aem')[1]) - float(aem)) <= 1]
                M = Dr[cand[0]] if cand else None
            rv = zs(M) if M else '-'
            mx = '%.3g (z=%.3g)' % M['max_vis'] if M else '-'
            out.append('| %s->%s (%s) | %s | %s | %s | %s | %s |' % (src, 'UD' if src == 'OD' else 'OD', aem, zr, zs(g), zs(nn), rv, mx))
        else:
            s = SG.get((amp, c.id[3:]))
            out.append('| %s->%s (%s) | %s | %s | %s | %s |' % (src, 'UD' if src == 'OD' else 'OD', aem, zr, zs(g), zs(nn),
                                                             '%+.3g (z=%.3g)' % (s['max'][1], s['max'][0]) if s else '-'))
    return out


w('## Figs. 4, 5 and 8: luminosity distance along fiducial rays  [vector; z +-0.17%; left column +-2.7e-5 inside |y|<0.01 '
  'and +-0.7% of |y| outside; right column +-0.3%]')
w('')
w('* Left column (and Fig. 5): y = D_L/D_L^LFRW - 1, symlog axis from -30 to +30: linear for |y| < 1e-2 (linthresh 1e-2, '
  'linscale 1, i.e. the 0-1e-2 stretch is as long as 1.11 decades), log outside; x = z, log, 0.01-10. Right column: '
  '|D_L^Newt/D_L^GR - 1|, log 1e-4 to 1 (Fig. 8: 1e-4 to 2); x = z, log, 0.01-10.')
w('* Rays: emitted at the overdensity towards the underdensity (OD->UD) or the reverse, at emission times labelled '
  'a_em ~ 1, 28, 43, 52 (OD) and 1, 27, 44, 52 (UD) for dbar = 0.01; 1, 28, 58, 112 / 1, 28, 58, 111 for 0.005; '
  '1, 28, 59, 163 / 1, 28, 58, 162 for 0.0025; 1, 8 (OD) and 1, 9, 14 (UD) for 0.05. The a_em ~ 1 rays have their first '
  'drawn point at z = 0.089 (0.028-0.030 for dbar = 0.05); later rays start at z = 0.0022 (hidden below z = 0.01).')
w('* Values below: "a/b" means the ray passes that z twice (blueshift near the halo); "-" = z not reached.')
w('')
for amp, base in [(0.01, 'delta1em2'), (0.005, 'delta5em3'), (0.0025, 'delta2p5em3')]:
    w('### dbar = %g (Fig. 4 %s)' % (amp, {0.01: 'top row', 0.005: 'middle row', 0.0025: 'bottom row'}[amp]))
    w('')
    for line in dl_tables(amp, base + '_dl_comp_frw', base + '_dl_newt_gr'):
        w(line)
    w('')
w('### dbar = 0.05 (Fig. 5, left-column quantity only)')
w('')
for line in dl_tables(0.05, 'delta5em2_dl_comp_frw', None):
    w(line)
w('')
w('For Fig. 5 there is no right-column panel; the last column is the GR-Newtonian difference rebuilt from the two left-column '
  'curves (precision ~1% of 1+|y| where |y| > 0.01). For dbar <= 0.01 this reconstruction agrees with the plotted right '
  'column to a few 1e-4 absolute (e.g. dbar = 0.01, OD a_em 28, z = 0.1: 0.0280 rebuilt vs 0.0284 plotted; dbar = 0.0025, '
  'OD a_em 163: 0.0153 vs 0.0153).')
w('')
w('Largest GR-Newtonian differences (right column, inside the axes, z >= 0.01):')
w('')
for amp, base in [(0.01, 'delta1em2'), (0.005, 'delta5em3'), (0.0025, 'delta2p5em3')]:
    D = R['dl'][base + '_dl_newt_gr']
    items = sorted(D.items(), key=lambda kv: -kv[1]['max_vis'][0])
    w('* dbar = %g: ' % amp + '; '.join('%s %.3g at z = %.3g' % (k, M['max_vis'][0], M['max_vis'][1]) for k, M in items)
      + '. Fraction of drawn (visible) vertices below 1%: ' + ', '.join('%s %.0f%%' % (k, 100 * M['frac_below_1pc']) for k, M in D.items()) + '.')
w('* dbar = 0.05 (rebuilt from Fig. 5): OD a_em 8: s = +10 at z = 0.01 (Newtonian D_L 11x the GR one), +1.36 at z = 0.05, '
  '+0.41 at 0.1, -0.08 at 0.5, -0.13 at 1; UD a_em 9: -0.21 at z = 1.85 (end of ray), +0.002 to +0.008 for z <= 0.5; '
  'a_em ~ 1 rays: up to 1.9% (OD, z = 1.3) and 4.7% (UD, z = 4.6).')
w('')
w('Fig. 8 (dbar = 0.01, resolution): maximum |dD/D| inside the axes, high vs low resolution:')
w('')
w('| ray | high res: max (z) | low res: max (z) | at z = 0.1 high / low | at z = 0.5 high / low |')
w('|---|---|---|---|---|')
for nm in ['delta1em2_dl_newt_gr_res_ou', 'delta1em2_dl_newt_gr_res_uo']:
    D = R['dl'][nm]
    for k in D:
        if not k.endswith('highres'):
            continue
        h = D[k]
        lo = D[k.replace('highres', 'lowres')]

        def v(M, z):
            return '/'.join('%.3g' % x for x in M['vals'][z]) or '-'
        w('| %s | %.3g (%.3g) | %.3g (%.3g) | %s / %s | %s / %s |' % (k.replace('_highres', ''), *h['max_vis'], *lo['max_vis'],
                                                                     v(h, 0.1), v(lo, 0.1), v(h, 0.5), v(lo, 0.5)))
w('')

# ---- Fig 6
w('## Fig. 6: constraint convergence (dbar = 0.01)  [vector; <a> +-0.02, norm +-0.3%]')
w('')
w('x = <a>, volume-averaged scale factor, linear 0-140; y = <|C_a|>/L^2 as plotted, i.e. multiplied by 1, 2.25, 4 for '
  'L/dx = 64 (N_cell^(1/3) = 1, 64^3 particles), 96 (2, 192^3), 128 (4, 512^3); log axis 2e-6 to 1e-2. Curves start at '
  '<a> = 1.02-1.035; L/dx = 128 ends at <a> = 81.8.')
w('')
cn = R['cnst']
w('| <a> | 64: plotted (raw) | 96: plotted (raw) | 128: plotted (raw) |')
w('|---|---|---|---|')
for a in [1.5, 2, 3, 5, 10, 20, 30, 40, 60, 80, 100, 120, 140]:
    cells = []
    for k in ['Ldx64', 'Ldx96', 'Ldx128']:
        p = cn[k]['vals'][a]
        cells.append('%.3g (%.3g)' % (p, p / cn[k]['fac']) if p else '-')
    w('| %g | %s |' % (a, ' | '.join(cells)))
w('')
w('The rescaled curves overlap only for L/dx = 64 and 96 at <a> > ~95; earlier the raw norms imply convergence order '
  '3.7-5.6 (64->96) and 3.2-4.3 (96->128), i.e. faster than the second order used for the rescaling.')
w('')

# ---- checks
w('## Calibration checks against statements in the text')
w('')
w('1. Fig. 1 top/middle: every GR curve starts at |delta_obs|(a_p = 1) = 6.644 dbar (all four amplitudes, both points); '
  'linear theory for the longitudinal-gauge density of this mode gives 3 dbar (1 + 12/pi^2) = 6.648 dbar. Agreement 0.06%.')
w('2. Fig. 1 top caption ("Newtonian and GR ... essentially indistinguishable"): largest |Newt/GR - 1| is 2.0-2.3% for '
  'dbar <= 0.01 and 3.9% for 0.05 (at a_p = 1); about 1.5 pt on the page, below the 2 pt line width.')
w('3. Fig. 1 middle text ("collapse ... slightly earlier for the Newtonian case, and this difference increases" with dbar): '
  'GR/Newt a_p at |delta_obs| = 10 is 1.019, 1.058, 1.069, 1.310 for dbar = 0.0025, 0.005, 0.01, 0.05.')
w('4. "Saturation density significantly larger for the Newtonian case" and "with CIC ... much closer to the GR result": '
  'plateau medians 5e2-7.5e2 (GR, dbar = 0.005, 0.01), 1.2e5-2.9e6 (Newtonian), CIC 2.4e3 at a_p = 90 for dbar = 0.01.')
w('5. Fig. 1 bottom text ("finite resolution tends to lead [to] an underestimate of the density"; "collapse happens faster '
  'in the Newtonian case" even so): a_p at |delta_obs| = 100: GR 58.94 -> 57.21 (high res), GR fluid 55.85 -> 55.17, Newtonian '
  '52.71 -> 52.43; the best GR (55.2) is still later than the Newtonian (52.4).')
w('6. Fig. 2 caption (red/green/blue = x/y/z): with dbar_i = dbar (1, 0.9, 1.1) the z particles should fall in first and the '
  'y particles last. a_10 is ordered z < x < y in every panel and both models (e.g. dbar = 0.01, d0 = L/8: GR 63.2, 65.5, '
  '66.8; Newtonian 57.9, 59.4, 60.9), except GR dbar = 0.05 where y falls in before x (z 15.5, y 16.0, x 16.2 for d0 = L/32).')
w('7. Fig. 2 caption ("initial oscillations in the GR curves"): GR d rises above d0 by 8-12% (dbar = 0.05), 1.2-2.1% '
  '(0.01), 0.6-1.1% (0.005), 0.3-0.5% (0.0025) by a_p ~ 5-7; Newtonian curves decrease monotonically from the start.')
def _ratio(n, d0):
    g = [R['splash'][n]['GR_%s_d0_%g' % (d, d0)]['t10'] for d in 'xyz']
    nn = [R['splash'][n]['Newt_%s_d0_%g' % (d, d0)]['t10'] for d in 'xyz']
    if not all(g) or not all(nn):
        return None
    return np.mean(g) / np.mean(nn)


w('8. Fig. 2 text (discrepancy grows with dbar): GR/Newt ratio of the mean a_10 for d0 = L/16 is %s; for d0 = L/8 %s'
  '; for dbar = 0.05 the Newtonian x and z particles with d0 <= L/16 reach 0.1 d0 at a_p = 10.5-10.8, just before the run'
  ' stops, against 15.5-16.3 in GR (ratio ~1.5), and the other Newtonian particles never do.' % (
      ', '.join('%.3f (dbar=%g)' % (_ratio(n, 0.0625), amp) for n, amp in [('delta2p5em3pm_splash', 0.0025), ('delta5em3pm_splash', 0.005), ('delta10em2pm_splash', 0.01)]),
      ', '.join('%s (dbar=%g)' % (fmt(_ratio(n, 0.125), '%.3f'), amp) for n, amp in [('delta2p5em3pm_splash', 0.0025), ('delta5em3pm_splash', 0.005), ('delta10em2pm_splash', 0.01)])))
w('9. Fig. 3: initial speeds equal (H0 dbar/k) sin(k d0) for x particles to 1% (3.15e-4, 2.47e-3, 6.44e-3 read vs 3.11e-4, '
  '2.44e-3, 6.37e-3), confirming the legend, k = pi H0/2 and L = 4/H0; the end values match |d_N - d_GR| rebuilt from Fig. 2 '
  '(0.0133 vs 0.0132-0.0145; 0.0034 vs 0.0022-0.0036).')
w('10. Fig. 4 text (OD rays emitted late: GR D_L slightly smaller than Newtonian at small z, larger at larger z): from the left '
  'column, s = D_N/D_GR - 1 for dbar = 0.01 is +0.092/+0.028/-0.006 (a_em 28, z = 0.02/0.1/0.5) and +0.068/+0.003/-0.011 '
  '(a_em 43): positive at small z, negative beyond the dip, as stated; for a_em 52 s is positive only for z < ~0.03.')
w('11. Fig. 4 text (blueshift near the overdensity, top panel): z turns back along the UD->OD rays of dbar = 0.01 with a_em '
  '27, 44, 52 (z_max 0.735, 0.796, 0.771; ray ends at 0.695, 0.482, 0.408); no UD ray turns back for dbar = 0.005 or 0.0025.')
w('12. Fig. 4 text ("in most cases subpercent"; UD rays subpercent "until the overdensity is approached"): UD rays stay '
  'below 1% over 78-100% of their drawn vertices and exceed it only over the last part of the ray, towards the halo; the '
  'a_em ~ 1 rays stay below 0.2% everywhere; OD rays emitted after collapse reach 3-10% (dbar = 0.01: 9.7%, 10.3%, 3.2%; '
  '0.005: 5.4%, 3.5%; 0.0025: 5.5% for the last ray) at small z.')
w('13. Appendix (resolution changes the first crossing much less than GR vs Newtonian): dbar = 0.01, d0 = L/8, x: GR 70.08 '
  '(low) vs 68.13 (high), Newtonian 60.25 vs 60.19, GR - Newt 7.9. Subsequent oscillations differ more (first GR '
  'apocentre 84.7 vs 77.5).')
w('14. Fig. 6 caption factors: 2.25 = (96/64)^2 and 4.00 = (128/64)^2, as printed in the legend.')
w('15. Fig. 7 vs Fig. 2: the "High res." halves reproduce Fig. 2 (dbar = 0.01): Newtonian exactly, GR to <= 3.4e-4 in d/L.')
w('')

# ---- contradictions
w('## Figures versus text: contradictions and tensions')
w('')
w('1. **Fig. 8 caption** says "similar to the top left panel of Fig. 4", but the plotted quantity, |D_L^Newt/D_L^GR - 1|, is '
  'that of the top *right* panel.')
w('2. **GR particle numbers are inconsistent.** Text: default 96 points per wavelength with 4^3 particles per cell (384^3). '
  'Fig. 6 legend: L/dx = 64, 96, 128 with N_cell^(1/3) = 1, 2, 4, i.e. 64^3, 192^3, 512^3 particles (the 96-point run has 2^3 '
  'per cell). Fig. 7 caption: GR 128^3 and 384^3. Fig. 8 caption: GR 192^3 and 512^3. Fig. 2 equals the Fig. 7 "high" '
  'run (384^3 by that caption).')
w('3. **Fig. 1 bottom "GR OD" is not the default GR run of Fig. 1 middle**: the middle-panel GR dbar = 0.01 curve differs from '
  'both bottom-panel GR particle curves by up to 0.3-0.4 dex after collapse and lies between them in collapse time '
  '(|delta_obs| = 100 at a_p 58.0 vs 58.9 "GR OD" and 57.2 "High Res."). Their resolutions are not stated. Likewise "Newt. '
  'OD" in the bottom panel is the low-resolution (128^3) run and "Newt. OD High Res." the default 196^3 run, which the '
  'legend wording does not make clear.')
w('4. **"15-fold increase of scale factor"** for the Newtonian dbar = 0.05 run cannot be matched to the plotted a_p: the '
  'Newtonian curves end at a_p = 10.86 (halo density), 10.8-11.2 and 13.3-13.9 (particles) and 22.7 (void density). A '
  'void observer at a_p = 22.7 would need a proper time 1.86x the background time if the background scale factor were 15, '
  'far more than a potential |psi| < 1/2 allows; so either "15" refers to another clock or the void curve runs longer.')
w('5. **Initial-condition match at dbar = 0.05**: the text says the mass corrections "guarantee a high-accuracy match" of the '
  'Newtonian and GR initial conditions, but at a_p = 1 the Newtonian |delta_obs| is 0.347 (halo) and 0.319 (void) against '
  '0.332 for GR (+4.5%, -4.0%). For dbar = 0.01 the mismatch is +0.8% / -0.4%, smaller amplitudes less.')
w('6. **Eq. (1) vs the stated extremum positions** (text only): with delta_N = sum dbar_i sin(k x^i) the density contrast is '
  'zero at (0,0,0) and (pi/k, pi/k, pi/k), not maximal/minimal; the stated positions need cos(k x^i) (and then v^i proportional '
  'to sin(k x^i), not cos). The figures are consistent with |v| = (H0 dbar_i/k) sin(k d) at distance d from the peak.')
w('7. **Newtonian dbar = 0.005 particle offsets**: in Fig. 2 bottom left the Newtonian particles start 0.0013-0.0015 L farther '
  'out than the nominal L/32, L/16, L/8, L/4 used everywhere else (GR half of the same panel is nominal).')
w('8. **Fig. 6**: the rescaled curves do not coincide at <a> < ~80 (convergence faster than the assumed second order), which '
  'the caption does not mention; they coincide (64 vs 96) only at late times, where the caption says particle noise dominates.')
w('9. **Fig. 2, dbar = 0.05 GR**: y particles fall in before x particles although dbar_y = 0.9 dbar < dbar_x (all other '
  'panels and the Newtonian runs follow z, x, y).')
w('')

# ---- not extracted
w('## Not extracted or not recoverable')
w('')
w('* Parts of curves outside the page were never written to the EPS: Fig. 1 bottom above |delta_obs| = 2.35e4 (both '
  'Newtonian curves, the high-resolution fluid curve, the fluid peak region), Fig. 2 dbar = 0.05 GR d0 = L/4 curves above '
  'd/L = 0.28 (a_p ~ 4.2-7.5), Fig. 3 orange curve beyond |v| = 0.511, right-column D_L dips below 1.55e-5 (1.43e-5 in '
  'Fig. 8). Hidden-but-present parts (outside the axes, inside the page) are in the CSVs with visible = 0.')
w('* The underlying sample times: matplotlib dropped vertices on near-straight stretches, so the CSV vertices are not the '
  'simulation output times (except where the curve bends at every sample, e.g. the Newtonian particle curves).')
w('* Newtonian crossing times to better than about half a snapshot spacing (~0.7 in a_p for dbar = 0.01, ~3 for 0.0025).')
w('* The resolution of the Fig. 1 bottom GR curves and which GR particle number each figure used (inconsistent statements, '
  'see above).')
w('* Fig. 3: which simulation output each point corresponds to (only |v| is given), and the y and z particles (not plotted).')
w('* Fig. 5 has no GR-Newtonian panel; differences there are rebuilt from the left-column curves with ~1% precision.')
w('* Absolute D_L or z of the rays (only ratios to the LFRW solution and between models are plotted); the exact emission '
  'times beyond the rounded legend values (a_em ~ 1, 27, 28, ...).')
w('* The Newtonian potential psi and the GR metric (not plotted); the a_p <-> coordinate-time relation for each curve.')
w('')
open(os.path.join(OUT, 'SUMMARY.md'), 'w').write('\n'.join(S) + '\n')
print('wrote SUMMARY.md and READMEs')
