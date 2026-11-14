"""Extract every curve of the East, Wojtak & Pretorius (arXiv:1908.05683) figures.

Writes one long-format CSV per figure plus a curve index under
cosmo/notes/east_figures/<figure>/ and a pickle with all curves for analysis.
The EPS files are read as text only.
"""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
_REPO = _os.path.abspath(_os.path.join(_HERE, '..', '..', '..', '..'))

import os
import sys
import pickle
import numpy as np

sys.path.insert(0, _HERE + '/')
import calib as C          # noqa: E402
import psparse as P        # noqa: E402

OUT = _REPO + '/cosmo/notes/east_figures'
WORK = _HERE + '/'

COLOR_NAME = {
    (0.0, 0.0, 0.0): 'black', (1.0, 0.0, 0.0): 'red', (0.0, 0.5, 0.0): 'green (mpl "g")',
    (0.0, 0.0, 1.0): 'blue', (0.0, 0.75, 0.75): 'cyan (mpl "c")', (0.75, 0.0, 0.75): 'magenta (mpl "m")',
    (0.502, 0.0, 0.0): 'maroon', (0.498, 1.0, 0.0): 'chartreuse', (0.133, 0.545, 0.133): 'forestgreen',
    (0.824, 0.412, 0.118): 'chocolate', (0.125, 0.698, 0.667): 'lightseagreen',
    (1.0, 0.549, 0.0): 'darkorange', (0.0, 1.0, 1.0): 'aqua/cyan',
    (0.58, 0.0, 0.83): 'purple (gnuplot 0.58,0,0.83)', (0.0, 0.62, 0.45): 'teal green (gnuplot 0,0.62,0.45)',
    (0.9, 0.62, 0.0): 'orange (gnuplot 0.9,0.62,0)'}
DASH_NAME = {(): 'solid', (6.0, 6.0): 'dashed [6 6]', (1.0, 3.0): 'dotted [1 3]',
             (3.0, 5.0, 1.0, 5.0): 'dash-dot [3 5 1 5]'}
D0 = [0.03125, 0.0625, 0.125, 0.25]
DIRN = {(1.0, 0.0, 0.0): 'x', (0.0, 0.5, 0.0): 'y', (0.0, 0.0, 1.0): 'z'}


def cname(c):
    c = tuple(round(v, 3) for v in c)
    return COLOR_NAME.get(c, 'rgb(%.3f,%.3f,%.3f)' % c)


def dname(d):
    return DASH_NAME.get(tuple(d), str(d))


class Curve:
    def __init__(self, cid, meta, color, dash, segs):
        self.id = cid
        self.meta = meta
        self.color = cname(color)
        self.dash = dname(dash)
        self.rgb = tuple(float(c) for c in color)
        self.dash_t = tuple(dash)
        self.segs = segs          # list of dict(x, y, vis, edge)

    @property
    def x(self):
        return np.concatenate([s['x'] for s in self.segs])

    @property
    def y(self):
        return np.concatenate([s['y'] for s in self.segs])


def flag_points(s, box, canvas):
    """visible: inside axes box; edge: on the page canvas boundary (clip artefact)."""
    Pp = s['P']
    tol = 1e-3
    vis = ((Pp[:, 0] >= box['x0'] - tol) & (Pp[:, 0] <= box['x1'] + tol) &
           (Pp[:, 1] >= box['y0'] - tol) & (Pp[:, 1] <= box['y1'] + tol))
    W, H = canvas
    edge = ((np.abs(Pp[:, 0]) < tol) | (np.abs(Pp[:, 0] - W) < tol) |
            (np.abs(Pp[:, 1]) < tol) | (np.abs(Pp[:, 1] - H) < tol))
    return dict(x=s['x'], y=s['y'], vis=vis, edge=edge, P=Pp)


def canvas_of(F):
    for s in F['d']['strokes']:
        c = s['clip']
        if c and c[2] == 0 and c[3] == 0:
            return (c[0], c[1])
    return (576.0, 432.0)


def legend(F):
    """(colour, dash) -> label text, from legend sample lines and their labels."""
    d = F['d']
    canvas = canvas_of(F)
    samples = [s for s in d['strokes'] if s['clip'] and s['clip'][2] == 0 and len(s['pts']) == 2
               and abs(s['pts'][0][1] - s['pts'][1][1]) < 1e-6 and 15 < abs(s['pts'][1][0] - s['pts'][0][0]) < 40]
    texts = sorted(d['texts'], key=lambda t: t['line'])
    out = []
    for s in samples:
        nxt = [t for t in texts if t['line'] > s['line']]
        if nxt:
            out.append((tuple(round(c, 3) for c in s['color']), tuple(s['dash']), P.text_string(nxt[0])))
    return out


def group(strokes, key):
    """Merge consecutive strokes with the same key into one curve (list of segments)."""
    groups = []
    for s in strokes:
        k = key(s)
        if groups and groups[-1][0] == k:
            groups[-1][1].append(s)
        else:
            groups.append((k, [s]))
    return groups


def write_fig(name, curves, xcol, ycol, F, extra_note=''):
    od = os.path.join(OUT, name)
    os.makedirs(od, exist_ok=True)
    with open(os.path.join(od, name + '.csv'), 'w') as f:
        f.write('# %s: curves extracted from the vector paths of %s.eps (arXiv:1908.05683)\n' % (name, name))
        f.write('# columns: curve id (see curves.csv), segment index (a new segment starts where the drawn path was\n')
        f.write('#   broken by clipping at the page edge), %s, %s,\n' % (xcol, ycol))
        f.write('#   visible = 1 if the point lies inside the plotted axes box (0: drawn outside the axes, hidden in the paper),\n')
        f.write('#   canvas_edge = 1 if the point is an artificial intersection with the page boundary (value there is the\n')
        f.write('#   clip limit, not data). Points are in drawing order (order along the curve), not sorted.\n')
        if extra_note:
            f.write('# ' + extra_note + '\n')
        f.write('curve,segment,%s,%s,visible,canvas_edge\n' % (xcol, ycol))
        for c in curves:
            for k, s in enumerate(c.segs):
                for x, y, v, e in zip(s['x'], s['y'], s['vis'], s['edge']):
                    f.write('%s,%d,%.7g,%.7g,%d,%d\n' % (c.id, k, x, y, int(v), int(e)))
    keys = []
    for c in curves:
        for k in c.meta:
            if k not in keys:
                keys.append(k)
    with open(os.path.join(od, 'curves.csv'), 'w') as f:
        f.write('curve,color,linestyle,n_points,n_segments,%s_min,%s_max,%s\n' % (xcol, xcol, ','.join(keys)))
        for c in curves:
            x = c.x
            f.write('%s,%s,%s,%d,%d,%.6g,%.6g,%s\n' % (
                c.id, c.color.replace(',', ';'), c.dash, len(x), len(c.segs), np.nanmin(x), np.nanmax(x),
                ','.join(str(c.meta.get(k, '')).replace(',', ';') for k in keys)))


def nearest(v, opts, log=True):
    if log:
        return min(opts, key=lambda o: abs(np.log(abs(v)) - np.log(o)))
    return min(opts, key=lambda o: abs(abs(v) - o))


AMPS = [0.0025, 0.005, 0.01, 0.05]
# delta_obs(a_p=1) ~ 3*dbar*(1 + 3 H^2/k^2) = 3*dbar*(1 + 12/pi^2) for the
# longitudinal-gauge density of the k = pi H0/2 mode (checked below, used only to label)
D1FAC = 3 * (1 + 12 / np.pi ** 2)


def fig_ud_od(name):
    F = C.load_mpl(name, 'log', 'log')
    canvas = canvas_of(F)
    curves = []
    for s in F['strokes']:
        col = tuple(round(c, 3) for c in s['color'])
        model = {(0.0, 0.0, 0.0): 'GR', (1.0, 0.0, 0.0): 'Newtonian',
                 (0.75, 0.0, 0.75): 'Newtonian CIC'}[col]
        amp = nearest(s['y'][0] / D1FAC, AMPS)
        tag = {'GR': 'GR', 'Newtonian': 'Newt', 'Newtonian CIC': 'NewtCIC'}[model]
        seg = flag_points(s, F['box'], canvas)
        curves.append(Curve('%s_dbar%g' % (tag, amp),
                            dict(model=model, dbar=amp,
                                 point='underdensity (minimum density)' if name == 'ud_comp' else 'overdensity (maximum density)',
                                 resolution='default (GR: 96 points per wavelength; Newtonian: N=196^3)',
                                 density_estimator=('CIC' if 'CIC' in model else ('tetrahedral (phase-space) cells' if model != 'GR' else 'GR particle deposit on grid'))),
                            s['color'], s['dash'], [seg]))
    curves.sort(key=lambda c: (c.meta['dbar'], c.meta['model']))
    write_fig(name, curves, 'a_p', 'abs_delta_obs', F)
    return F, curves


def fig_comp_all():
    name = 'delta10m2_comp_all'
    F = C.load_mpl(name, 'lin', 'log')
    canvas = canvas_of(F)
    lab = {((0.0, 0.0, 1.0), ()): ('GR', 'GR OD', 'particles', 'default (96 points per wavelength)'),
           ((0.0, 0.5, 0.0), ()): ('GR_highres', 'GR OD High Res.', 'particles', 'high (presumably 128 points per wavelength, 4/3 x default)'),
           ((1.0, 0.0, 0.0), ()): ('GR_fluid', 'GR OD Fluid', 'pressureless fluid', 'default (96 points per wavelength)'),
           ((0.0, 0.75, 0.75), ()): ('GR_fluid_highres', 'GR OD Fluid High Res.', 'pressureless fluid', 'high (presumably 128 points per wavelength)'),
           ((1.0, 0.0, 0.0), (6.0, 6.0)): ('Newt', 'Newt. OD', 'particles (tetrahedral density)', 'see README: identical to Fig.1 middle Newtonian dbar=0.01 (N=196^3 default)'),
           ((0.0, 0.0, 0.0), (6.0, 6.0)): ('Newt_highres', 'Newt. OD High Res.', 'particles (tetrahedral density)', 'labelled High Res.; N not stated'),
           ((0.0, 0.0, 1.0), (6.0, 6.0)): ('NewtCIC', 'Newt. OD CIC', 'particles (CIC density)', 'default N=196^3')}
    groups = group(F['strokes'], lambda s: (tuple(round(c, 3) for c in s['color']), tuple(s['dash'])))
    curves = []
    for k, ss in groups:
        cid, label, matter, res = lab[k]
        curves.append(Curve(cid, dict(legend=label, model='GR' if cid.startswith('GR') else 'Newtonian',
                                      matter=matter, dbar=0.01, point='overdensity', resolution=res),
                            ss[0]['color'], ss[0]['dash'], [flag_points(s, F['box'], canvas) for s in ss]))
    write_fig(name, curves, 'a_p', 'abs_delta_obs', F)
    return F, curves


def fig_splash(name, top_label, bot_label, amp):
    F = C.load_mpl(name, 'lin', 'lin')
    canvas = canvas_of(F)
    groups = group(F['strokes'], lambda s: (tuple(round(c, 3) for c in s['color']), tuple(s['dash']),
                                            1 if s['y'][0] > 0 else -1))
    curves = []
    for (col, dash, sgn), ss in groups:
        segs = [flag_points(s, F['box'], canvas) for s in ss]
        y0 = abs(ss[0]['y'][0])
        d0 = nearest(y0, D0)
        half = top_label if sgn > 0 else bot_label
        dirn = DIRN[col]
        cid = '%s_%s_d0_%g' % (half[0], dirn, d0)
        curves.append(Curve(cid, dict(half='top (plotted +d/L)' if sgn > 0 else 'bottom (plotted -d/L)',
                                      model=half[1], resolution=half[2], dbar=amp, direction=dirn,
                                      d0_nominal=d0, d0_plotted=round(y0, 5)),
                            col, dash, segs))
    curves.sort(key=lambda c: (c.meta['half'][0] != 't', c.meta['direction'], c.meta['d0_nominal']))
    write_fig(name, curves, 'a_p', 'plotted_y', F,
              extra_note='plotted_y = +d/L for the top-half curves and -d/L for the bottom-half curves (d >= 0 is the '
                         'coordinate distance from the point of maximum density, L the domain length = one wavelength = 4/H0)')
    return F, curves


def fig_dl_left(name, amp):
    F = C.load_mpl(name, 'log', 'symlog')
    canvas = canvas_of(F)
    leg = legend(F)
    lab = {}
    for c, d, t in leg:
        lab.setdefault((c, d), t)
    st = F['strokes']
    curves = []
    last_ray = None
    for s in st:
        col = tuple(round(c, 3) for c in s['color'])
        dash = tuple(s['dash'])
        seg = flag_points(s, F['box'], canvas)
        if col != (0.0, 0.0, 0.0):
            t = lab.get((col, ()), '?')
            src = 'OD' if 'OD' in t else 'UD'
            aem = t.split('~')[-1]
            last_ray = (src, aem, t)
            curves.append(Curve('GR_%s_aem%s' % (src, aem),
                                dict(model='GR', ray='emitted at %s towards %s' % (src, 'UD' if src == 'OD' else 'OD'),
                                     a_em_label=aem, legend=t, dbar=amp), s['color'], s['dash'], [seg]))
        else:
            src, aem, t = last_ray
            kind = 'OD->UD' if dash == (6.0, 6.0) else 'UD->OD'
            assert (kind == 'OD->UD') == (src == 'OD'), (name, kind, src)
            prev = curves[-1]
            assert abs(prev.x[0] - seg['x'][0]) / prev.x[0] < 1e-3 and abs(prev.x[-1] - seg['x'][-1]) / prev.x[-1] < 1e-3
            curves.append(Curve('Newt_%s_aem%s' % (src, aem),
                                dict(model='Newtonian', ray='emitted at %s towards %s' % (src, 'UD' if src == 'OD' else 'OD'),
                                     a_em_label=aem, legend='(black, paired with %s)' % t, dbar=amp),
                                s['color'], s['dash'], [seg]))
    write_fig(name, curves, 'z', 'DL_over_DL_LFRW_minus_1', F)
    return F, curves


def fig_dl_right(name, amp, res=False):
    F = C.load_mpl(name, 'log', 'log')
    canvas = canvas_of(F)
    leg = legend(F)
    groups = group(F['strokes'], lambda s: (tuple(round(c, 3) for c in s['color']), tuple(s['dash'])))
    curves = []
    for (col, dash), ss in groups:
        segs = [flag_points(s, F['box'], canvas) for s in ss]
        if not res:
            t = [l for c, d, l in leg if c == col and d == dash][0]
            src = 'OD' if 'OD' in t else 'UD'
            aem = t.split('~')[-1]
            cid = '%s_aem%s' % (src, aem)
            meta = dict(ray='emitted at %s towards %s' % (src, 'UD' if src == 'OD' else 'OD'), a_em_label=aem,
                        legend=t, dbar=amp, quantity='|D_L^Newt/D_L^GR - 1|')
        else:
            src = 'OD' if name.endswith('_ou') else 'UD'
            # legend: black solid = High Res, black dotted = Low Res; colours give a_em
            tcol = [l for c, d, l in leg if c == col]
            aem = tcol[0].split('~')[-1].split()[0]
            hi = dash == ()
            cid = '%s_aem%s_%s' % (src, aem, 'highres' if hi else 'lowres')
            meta = dict(ray='emitted at %s towards %s' % (src, 'UD' if src == 'OD' else 'OD'), a_em_label=aem,
                        resolution=('high: GR N=512^3 vs Newtonian N=196^3' if hi else 'low: GR N=192^3 vs Newtonian N=128^3'),
                        dbar=amp, quantity='|D_L^Newt/D_L^GR - 1|')
        curves.append(Curve(cid, meta, col, dash, segs))
    write_fig(name, curves, 'z', 'abs_DL_Newt_over_DL_GR_minus_1', F)
    return F, curves


def fig_cnst():
    name = '10m2_cnst_conv'
    F = C.load_mpl(name, 'lin', 'log')
    canvas = canvas_of(F)
    info = {(0.0, 0.0, 0.0): (64, 1, 1.00), (0.0, 0.0, 1.0): (96, 2, 2.25), (0.0, 0.5, 0.0): (128, 4, 4.00)}
    curves = []
    for s in F['strokes']:
        col = tuple(round(c, 3) for c in s['color'])
        n, nc, fac = info[col]
        seg = flag_points(s, F['box'], canvas)
        curves.append(Curve('Ldx%d' % n, dict(L_over_dx=n, Ncell_cuberoot=nc, N_particles='%d^3' % (n * nc),
                                             plotted_scale_factor=fac, dbar=0.01,
                                             note='plotted value = (L2 norm of C_a)/L^2 x factor'),
                            s['color'], s['dash'], [seg]))
    write_fig(name, curves, 'a_avg', 'scaled_constraint_norm', F,
              extra_note='scaled_constraint_norm = <|C_a|>/L^2 multiplied by (L/dx/64)^2 = 1, 2.25, 4 as plotted; divide by the curve factor for the raw norm')
    return F, curves


def fig_rel_eff():
    name = 'rel_eff'
    paths, labels = C.load_gnuplot(name)
    # calibration from the tick labels (gnuplot units of 0.05 pt)
    xt = [(l[0], float(l[2][0][3])) for l in labels if l[3] == 'MCshow' and l[1] == 1024]
    yt = [(l[1], 10.0 ** int(l[2][1][3])) for l in labels if l[3] == 'MRshow' and l[0] == 1184]
    X = C.Axis(xt, 'log')
    Y = C.Axis(yt, 'log')
    box = dict(x0=1376, x1=8062, y0=1344, y1=7239)
    curves = []
    meta = {1: dict(dbar=0.0025, d0_label=0.031, legend='dbar=0.0025, d_OD(a_p=1)/L=0.031'),
            2: dict(dbar=0.01, d0_label=0.063, legend='dbar=0.01, d_OD(a_p=1)/L=0.063'),
            3: dict(dbar=0.01, d0_label=0.25, legend='dbar=0.01, d_OD(a_p=1)/L=0.25 (as labelled)')}
    by = {}
    for blk, col, pts in paths:
        if blk is None:
            continue
        p = np.array(pts, float)
        if len(p) == 2 and p[0][0] == 5177:      # legend sample
            continue
        by.setdefault(blk, (col, []))[1].append(p)
    for blk, (col, ps) in sorted(by.items()):
        segs = []
        for p in ps:
            x = X.to_data(p[:, 0])
            y = Y.to_data(p[:, 1])
            vis = np.ones(len(p), bool)
            edge = (np.abs(p[:, 1] - box['y0']) < 0.5) | (np.abs(p[:, 0] - box['x1']) < 0.5)
            segs.append(dict(x=x, y=y, vis=vis, edge=edge, P=p))
        m = meta[blk]
        cid = 'dbar%g_d0_%g' % (m['dbar'], m['d0_label'])
        m = dict(m, plot_block=blk, quantity='|d_OD^Newt - d_OD^GR|/L vs |v_infall| (Newtonian), up to first Newtonian halo crossing')
        curves.append(Curve(cid, m, col, (), segs))
    F = dict(X=X, Y=Y, box=dict(box, xlim=(float(X.to_data(1376)), float(X.to_data(8062))),
                                ylim=(float(Y.to_data(1344)), float(Y.to_data(7239)))))
    write_fig(name, curves, 'abs_v_infall', 'abs_dNewt_minus_dGR_over_L', F,
              extra_note='gnuplot clips at the axes box: canvas_edge = 1 marks points on the bottom (1e-5) or right axis edge')
    return F, curves


def main():
    allf = {}
    for n in ['ud_comp', 'od_comp']:
        allf[n] = fig_ud_od(n)
    allf['delta10m2_comp_all'] = fig_comp_all()
    gr = ('GR', 'GR', 'default (96 points per wavelength; caption of Fig. 7 implies N=384^3 particles)')
    nw = ('Newt', 'Newtonian', 'default (N=196^3)')
    for n, a in [('delta5em2pm_splash', 0.05), ('delta10em2pm_splash', 0.01),
                 ('delta5em3pm_splash', 0.005), ('delta2p5em3pm_splash', 0.0025)]:
        allf[n] = fig_splash(n, gr, nw, a)
    allf['res_delta10em2pm_splash'] = fig_splash(
        'res_delta10em2pm_splash', ('GRlow', 'GR', 'low (caption: N=128^3)'),
        ('GRhigh', 'GR', 'high (caption: N=384^3)'), 0.01)
    allf['res_newt_delta10em2pm_splash'] = fig_splash(
        'res_newt_delta10em2pm_splash', ('Newtlow', 'Newtonian', 'low (caption: N=128^3)'),
        ('Newthigh', 'Newtonian', 'high (caption: N=196^3)'), 0.01)
    allf['rel_eff'] = fig_rel_eff()
    for n, a in [('delta1em2', 0.01), ('delta5em3', 0.005), ('delta2p5em3', 0.0025), ('delta5em2', 0.05)]:
        allf[n + '_dl_comp_frw'] = fig_dl_left(n + '_dl_comp_frw', a)
        if n != 'delta5em2':
            allf[n + '_dl_newt_gr'] = fig_dl_right(n + '_dl_newt_gr', a)
    for n in ['delta1em2_dl_newt_gr_res_ou', 'delta1em2_dl_newt_gr_res_uo']:
        allf[n] = fig_dl_right(n, 0.01, res=True)
    allf['10m2_cnst_conv'] = fig_cnst()
    store = {}
    for n, (F, curves) in allf.items():
        store[n] = dict(curves=curves, box=F['box'],
                        X=F['X'].describe(), Y=F['Y'].describe(),
                        Xaxis=F['X'], Yaxis=F['Y'])
    with open(os.path.join(WORK, 'curves.pkl'), 'wb') as f:
        pickle.dump(store, f)
    for n, v in store.items():
        print(n, len(v['curves']), 'curves;', ', '.join(c.id for c in v['curves']))


if __name__ == '__main__':
    main()
