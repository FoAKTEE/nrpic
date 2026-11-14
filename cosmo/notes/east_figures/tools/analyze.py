"""Derived numbers from the extracted curves (all interpolation is done in the
display (PostScript) coordinates, i.e. exactly along the drawn line)."""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
_REPO = _os.path.abspath(_os.path.join(_HERE, '..', '..', '..', '..'))

import os
import sys
import pickle
import numpy as np

sys.path.insert(0, _HERE + '/')
from extract_all import Curve  # noqa: F401,E402

WORK = _HERE + '/'
OUT = _REPO + '/cosmo/notes/east_figures'
st = pickle.load(open(os.path.join(WORK, 'curves.pkl'), 'rb'))
R = {}


def cur(name, cid):
    return [c for c in st[name]['curves'] if c.id == cid][0]


def disp_pts(c):
    """concatenated display coords and segment ids, dropping canvas-edge points."""
    xs, ys, sid = [], [], []
    for k, s in enumerate(c.segs):
        m = ~s['edge']
        xs.append(s['P'][m, 0])
        ys.append(s['P'][m, 1])
        sid.append(np.full(m.sum(), k))
    return np.concatenate(xs), np.concatenate(ys), np.concatenate(sid)


def at_x(name, c, x0):
    """All y values where the drawn curve passes x0 (drawing order), list of floats."""
    X, Y = st[name]['Xaxis'], st[name]['Yaxis']
    p0 = float(X.to_pos(x0))
    out = []
    for s in c.segs:
        P = s['P']
        ok = ~s['edge']
        for i in range(len(P) - 1):
            if not (ok[i] and ok[i + 1]):
                continue
            a, b = P[i, 0], P[i + 1, 0]
            if a == b:
                continue
            if (a - p0) * (b - p0) <= 0:
                f = (p0 - a) / (b - a)
                yp = P[i, 1] + f * (P[i + 1, 1] - P[i, 1])
                v = float(Y.to_data(yp))
                if out and abs(out[-1][1] - (i + 0.0)) <= 1 and abs(out[-1][0] - v) < 1e-12 + 1e-9 * abs(v):
                    continue
                out.append((v, i))
    return [v for v, i in out]


def first_up(name, c, level):
    """first x where the drawn curve reaches y=level from below (display interpolation)."""
    X, Y = st[name]['Xaxis'], st[name]['Yaxis']
    q = float(Y.to_pos(level))
    for s in c.segs:
        P = s['P']
        for i in range(len(P) - 1):
            if P[i, 1] < q <= P[i + 1, 1]:
                f = (q - P[i, 1]) / (P[i + 1, 1] - P[i, 1])
                return float(X.to_data(P[i, 0] + f * (P[i + 1, 0] - P[i, 0])))
    return None


def zigzag(y, h):
    out = []
    n = len(y)
    if n < 3:
        return out
    trend = 0
    ext = 0
    for i in range(1, n):
        if trend == 0:
            if y[i] - y[ext] > h:
                trend = 1
                ext = i
            elif y[ext] - y[i] > h:
                trend = -1
                ext = i
            continue
        if trend == 1:
            if y[i] > y[ext]:
                ext = i
            elif y[ext] - y[i] > h:
                out.append(('max', ext))
                trend = -1
                ext = i
        else:
            if y[i] < y[ext]:
                ext = i
            elif y[i] - y[ext] > h:
                out.append(('min', ext))
                trend = 1
                ext = i
    return out


# ============================================================ Fig. 1 top
APS = [1, 2, 5, 10, 20, 50, 100]
rows = []
for amp in [0.0025, 0.005, 0.01, 0.05]:
    g = cur('ud_comp', 'GR_dbar%g' % amp)
    n = cur('ud_comp', 'Newt_dbar%g' % amp)
    for a in APS:
        vg = at_x('ud_comp', g, a) if a > 1 else [g.y[0]]
        vn = at_x('ud_comp', n, a) if a > 1 else [n.y[0]]
        rows.append((amp, a, vg[0] if vg else None, vn[0] if vn else None))
    # max relative difference over the common range
    xs = np.exp(np.linspace(0, np.log(min(g.x.max(), n.x.max())), 400))
    dg = np.array([at_x('ud_comp', g, x)[0] if x > 1 else g.y[0] for x in xs[1:]])
    dn = np.array([at_x('ud_comp', n, x)[0] if x > 1 else n.y[0] for x in xs[1:]])
    rel = dn / dg - 1
    R.setdefault('ud_maxrel', {})[amp] = (float(np.max(np.abs(rel))), float(xs[1:][np.argmax(np.abs(rel))]),
                                          float(g.x.max()), float(n.x.max()), float(g.y[-1]), float(n.y[-1]))
R['ud_rows'] = rows
with open(os.path.join(OUT, 'ud_comp', 'values_at_ap.csv'), 'w') as f:
    f.write('# |delta_obs| at the minimum-density point read from the drawn curves (Fig. 1 top); empty = not plotted\n')
    f.write('dbar,a_p,abs_delta_obs_GR,abs_delta_obs_Newt,Newt_over_GR_minus_1\n')
    for amp, a, vg, vn in rows:
        f.write('%g,%g,%s,%s,%s\n' % (amp, a, '%.5g' % vg if vg else '', '%.5g' % vn if vn else '',
                                      '%.4f' % (vn / vg - 1) if (vg and vn) else ''))

# ============================================================ Fig. 1 middle / bottom
LEV = [1, 10, 100, 1000]


def od_metrics(name, c, h=0.05):
    x, y = c.x, c.y
    m = c.segs[0]['edge'] == 0
    cr = {L: first_up(name, c, L) for L in LEV}
    ly = np.log10(np.where(y > 0, y, np.nan))
    z = zigzag(ly, h)
    first_max = None
    for k, i in z:
        if k == 'max':
            first_max = (float(x[i]), float(y[i]))
            break
    plateau = None
    if first_max is not None:
        sel = (x >= first_max[0])
        yy = y[sel]
        plateau = (float(np.median(yy)), float(yy.min()), float(yy.max()), float(x[sel][-1]))
    return dict(cross=cr, first_max=first_max, plateau=plateau, end=(float(x[-1]), float(y[-1])),
                ymax=(float(x[np.argmax(y)]), float(y.max())), turning=[(k, float(x[i]), float(y[i])) for k, i in z])


R['od'] = {c.id: od_metrics('od_comp', c) for c in st['od_comp']['curves']}
R['od_all'] = {c.id: od_metrics('delta10m2_comp_all', c) for c in st['delta10m2_comp_all']['curves']}
for name, key in [('od_comp', 'od'), ('delta10m2_comp_all', 'od_all')]:
    with open(os.path.join(OUT, name, 'crossings.csv'), 'w') as f:
        f.write('# a_p where |delta_obs| first reaches 1, 10, 100, 1000 (interpolated along the drawn line); first maximum = first\n')
        f.write('# local maximum followed by a drop > 0.05 dex; plateau = median/min/max of |delta_obs| from the first maximum to the end\n')
        f.write('curve,a_p_at_1,a_p_at_10,a_p_at_100,a_p_at_1000,first_max_a_p,first_max_value,plateau_median,plateau_min,plateau_max,end_a_p,end_value,global_max_a_p,global_max_value\n')
        for c in st[name]['curves']:
            M = R[key][c.id]
            fm = M['first_max'] or (None, None)
            pl = M['plateau'] or (None, None, None, None)

            def F(v, fmt='%.4g'):
                return '' if v is None else fmt % v
            f.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (
                c.id, *[F(M['cross'][L], '%.3f') for L in LEV], F(fm[0], '%.2f'), F(fm[1]), F(pl[0]), F(pl[1]), F(pl[2]),
                F(M['end'][0], '%.2f'), F(M['end'][1]), F(M['ymax'][0], '%.2f'), F(M['ymax'][1])))

# identity tests between panels (log difference on a common grid)


def logdiff(n1, c1, n2, c2, lo, hi, logx=True):
    xs = np.exp(np.linspace(np.log(lo), np.log(hi), 300)) if logx else np.linspace(lo, hi, 300)
    d = []
    for x in xs:
        a = at_x(n1, c1, x)
        b = at_x(n2, c2, x)
        if a and b:
            d.append(np.log10(abs(a[0])) - np.log10(abs(b[0])))
    d = np.array(d)
    return float(np.max(np.abs(d))) if len(d) else None


R['identity_fig1'] = {
    'middle Newt 0.01 vs bottom "Newt. OD High Res."': logdiff('od_comp', cur('od_comp', 'Newt_dbar0.01'), 'delta10m2_comp_all', cur('delta10m2_comp_all', 'Newt_highres'), 1.01, 55),
    'middle Newt 0.01 vs bottom "Newt. OD"': logdiff('od_comp', cur('od_comp', 'Newt_dbar0.01'), 'delta10m2_comp_all', cur('delta10m2_comp_all', 'Newt'), 1.01, 55),
    'middle Newt CIC 0.01 vs bottom "Newt. OD CIC"': logdiff('od_comp', cur('od_comp', 'NewtCIC_dbar0.01'), 'delta10m2_comp_all', cur('delta10m2_comp_all', 'NewtCIC'), 1.01, 90),
    'middle GR 0.01 vs bottom "GR OD"': logdiff('od_comp', cur('od_comp', 'GR_dbar0.01'), 'delta10m2_comp_all', cur('delta10m2_comp_all', 'GR'), 1.01, 92),
    'middle GR 0.01 vs bottom "GR OD High Res."': logdiff('od_comp', cur('od_comp', 'GR_dbar0.01'), 'delta10m2_comp_all', cur('delta10m2_comp_all', 'GR_highres'), 1.01, 78),
    'top GR 0.01 (UD) vs middle GR 0.01 (OD) at a_p=1 (both 6.6*dbar)': None,
}

# ============================================================ Fig. 2 and Fig. 7


def splash_metrics(name, c):
    x = c.x
    d = np.abs(c.y)
    d0 = float(d[0])
    res = dict(d0=d0, end=(float(x[-1]), float(d[-1])), crossed=False)
    below = np.where(d < 0.15 * d0)[0]
    # a_p where d first falls below 0.1 d0 (linear interpolation)
    t10 = None
    for i in range(len(d) - 1):
        if d[i] >= 0.1 * d0 > d[i + 1]:
            t10 = float(x[i] + (0.1 * d0 - d[i]) / (d[i + 1] - d[i]) * (x[i + 1] - x[i]))
            break
    res['t10'] = t10
    t05 = None
    for i in range(len(d) - 1):
        if d[i] >= 0.05 * d0 > d[i + 1]:
            t05 = float(x[i] + (0.05 * d0 - d[i]) / (d[i + 1] - d[i]) * (x[i + 1] - x[i]))
            break
    res['t05'] = t05
    if len(below) == 0:
        return res
    i0 = below[0]
    # first local minimum at or after i0 (strict rise afterwards)
    imin = None
    for i in range(max(i0, 1), len(d) - 1):
        if d[i] <= d[i - 1] and d[i + 1] > d[i]:
            imin = i
            break
    if imin is None:
        res['near_end'] = True
        return res
    res['crossed'] = True
    res['cross'] = (float(x[imin]), float(d[imin]))
    # interval around the minimum where the drawn line stays within tol of d_min
    tol = max(5e-4, 0.02 * d0)
    lev = d[imin] + tol
    lo = x[imin]
    for i in range(imin, 0, -1):
        if d[i - 1] > lev:
            lo = x[i - 1] + (lev - d[i - 1]) / (d[i] - d[i - 1]) * (x[i] - x[i - 1])
            break
        lo = x[i - 1]
    hi = x[imin]
    for i in range(imin, len(d) - 1):
        if d[i + 1] > lev:
            hi = x[i] + (lev - d[i]) / (d[i + 1] - d[i]) * (x[i + 1] - x[i])
            break
        hi = x[i + 1]
    res['cross_bracket'] = (float(lo), float(hi))
    # subsequent turning points with hysteresis
    h = max(0.0005, 0.04 * d0)
    z = zigzag(d[imin:], h)
    tps = []
    for k, i in z:
        j = imin + i
        if j == imin:
            continue
        tps.append((k, float(x[j]), float(d[j])))
    res['turning'] = tps[:4]
    return res


SPL = ['delta5em2pm_splash', 'delta10em2pm_splash', 'delta5em3pm_splash', 'delta2p5em3pm_splash',
       'res_delta10em2pm_splash', 'res_newt_delta10em2pm_splash']
R['splash'] = {}
for name in SPL:
    R['splash'][name] = {}
    with open(os.path.join(OUT, name, 'turning_points.csv'), 'w') as f:
        f.write('# d = |plotted y| = distance/L from the point of maximum density. first_cross = first local minimum of d after\n')
        f.write('# d < 0.15 d0 (bracket = a_p interval around it where the drawn d stays within max(5e-4, 0.02 d0) of its minimum);\n')
        f.write('# a_p_d_lt_0.1d0 / a_p_d_lt_0.05d0 = first a_p with d < 0.1 d0 / 0.05 d0 (robust infall markers, linear interpolation);\n')
        f.write('# tp* = following turning points (hysteresis max(5e-4, 0.04 d0)); crossed=0: no minimum before the curve ends\n')
        f.write('curve,model,resolution,direction,d0_nominal,d0_plotted,a_p_d_lt_0.1d0,a_p_d_lt_0.05d0,crossed,first_cross_a_p,first_cross_d,bracket_lo,bracket_hi,'
                'tp1_kind,tp1_a_p,tp1_d,tp2_kind,tp2_a_p,tp2_d,tp3_kind,tp3_a_p,tp3_d,tp4_kind,tp4_a_p,tp4_d,end_a_p,end_d\n')
        for c in st[name]['curves']:
            M = splash_metrics(name, c)
            R['splash'][name][c.id] = M
            tp = M.get('turning', [])
            tps = []
            for k in range(4):
                if k < len(tp):
                    tps += [tp[k][0], '%.2f' % tp[k][1], '%.5f' % tp[k][2]]
                else:
                    tps += ['', '', '']
            cr = M.get('cross', (None, None))
            br = M.get('cross_bracket', (None, None))
            f.write('%s,%s,%s,%s,%g,%.5f,%s,%s,%d,%s,%s,%s,%s,%s,%.2f,%.5f\n' % (
                c.id, c.meta['model'], c.meta['resolution'].replace(',', ';'), c.meta['direction'], c.meta['d0_nominal'],
                M['d0'], '%.2f' % M['t10'] if M['t10'] else '', '%.2f' % M['t05'] if M['t05'] else '', int(M['crossed']),
                '%.2f' % cr[0] if cr[0] else '', '%.5f' % cr[1] if cr[1] is not None else '',
                '%.2f' % br[0] if br[0] else '', '%.2f' % br[1] if br[1] else '', ','.join(tps), M['end'][0], M['end'][1]))

# GR initial (gauge) oscillation amplitude
R['gauge'] = {}
for name in SPL[:4]:
    for c in st[name]['curves']:
        if c.meta['model'] == 'GR':
            d = np.abs(c.y)
            m = c.x < 10
            R['gauge'].setdefault(name, []).append(float(d[m].max() / d[0] - 1))

# identity: Fig.7 halves vs Fig.2 (0.01)


def pair_max_absdiff(n1, c1, n2, c2):
    xs = np.linspace(1.5, 89, 300)
    dd = []
    for x in xs:
        a = at_x(n1, c1, x)
        b = at_x(n2, c2, x)
        if a and b:
            dd.append(abs(abs(a[0]) - abs(b[0])))
    return float(np.max(dd))


idt = {}
for dirn in 'xyz':
    for d0 in [0.03125, 0.0625, 0.125, 0.25]:
        idt[('Newt', dirn, d0)] = pair_max_absdiff('res_newt_delta10em2pm_splash', cur('res_newt_delta10em2pm_splash', 'Newthigh_%s_d0_%g' % (dirn, d0)),
                                                   'delta10em2pm_splash', cur('delta10em2pm_splash', 'Newt_%s_d0_%g' % (dirn, d0)))
        idt[('GRhigh', dirn, d0)] = pair_max_absdiff('res_delta10em2pm_splash', cur('res_delta10em2pm_splash', 'GRhigh_%s_d0_%g' % (dirn, d0)),
                                                     'delta10em2pm_splash', cur('delta10em2pm_splash', 'GR_%s_d0_%g' % (dirn, d0)))
        idt[('GRlow', dirn, d0)] = pair_max_absdiff('res_delta10em2pm_splash', cur('res_delta10em2pm_splash', 'GRlow_%s_d0_%g' % (dirn, d0)),
                                                    'delta10em2pm_splash', cur('delta10em2pm_splash', 'GR_%s_d0_%g' % (dirn, d0)))
R['identity_fig7'] = idt

# ============================================================ Fig. 3 (rel_eff)
re = {}
for c in st['rel_eff']['curves']:
    x, y = c.x, c.y
    ok = np.concatenate([~s['edge'] for s in c.segs])
    re[c.id] = dict(vmin=float(x.min()), vmax=float(x.max()), end=(float(x[-1]), float(y[-1])),
                    ymax=float(y[ok].max()), v_at_ymax=float(x[ok][np.argmax(y[ok])]),
                    y_start=(float(x[0]), float(y[0])))
# envelope: max over curves of |dd| in log-v bins
edges = 10 ** np.arange(-3.5, -0.25, 0.25)
env = []
allx = np.concatenate([c.x for c in st['rel_eff']['curves']])
ally = np.concatenate([c.y for c in st['rel_eff']['curves']])
alle = np.concatenate([np.concatenate([s['edge'] for s in c.segs]) for c in st['rel_eff']['curves']])
for lo, hi in zip(edges[:-1], edges[1:]):
    m = (allx >= lo) & (allx < hi) & ~alle
    env.append((float(lo), float(hi), float(ally[m].max()) if m.any() else None,
                float(np.median(ally[m])) if m.any() else None))
R['rel_eff'] = re
R['rel_env'] = env
with open(os.path.join(OUT, 'rel_eff', 'envelope.csv'), 'w') as f:
    f.write('# upper envelope (max over the three curves) and median of |d_Newt - d_GR|/L in bins of |v_infall| (canvas-edge points excluded)\n')
    f.write('v_lo,v_hi,max_abs_dd_over_L,median_abs_dd_over_L\n')
    for lo, hi, mx, md in env:
        f.write('%.5g,%.5g,%s,%s\n' % (lo, hi, '%.4g' % mx if mx else '', '%.4g' % md if md else ''))

# cross-check: |d_N - d_GR| from Fig. 2 up to the first Newtonian crossing, with
# |v| ~ L H0 a_p^{1/2} |d(d_N)/da_p| (L H0 = 4; a ~ a_p), for comparison with Fig. 3
xc = {}
for name, amp in [('delta2p5em3pm_splash', 0.0025), ('delta10em2pm_splash', 0.01), ('delta5em2pm_splash', 0.05)]:
    for d0 in [0.03125, 0.0625, 0.25]:
        for dirn in 'xyz':
            cn = cur(name, 'Newt_%s_d0_%g' % (dirn, d0))
            cg = cur(name, 'GR_%s_d0_%g' % (dirn, d0))
            M = R['splash'][name][cn.id]
            aend = M['cross'][0] if M.get('crossed') else cn.x[-1]
            sel = (cn.x <= aend) & (cn.x > 1.0)
            xs = cn.x[sel]
            dn = np.abs(cn.y[sel])
            keep = np.concatenate([[True], np.diff(xs) > 1e-9])
            xs, dn = xs[keep], dn[keep]
            dg = np.array([abs(at_x(name, cg, a)[0]) if at_x(name, cg, a) else np.nan for a in xs])
            v = 4 * np.sqrt(xs) * np.abs(np.gradient(dn, xs))
            xc[(amp, d0, dirn)] = dict(a=xs, dd=np.abs(dn - dg), v=v, aend=float(aend), crossed=M.get('crossed'))
R['rel_xcheck'] = {k: dict(aend=v['aend'], crossed=v['crossed'], dd_end=float(v['dd'][-1]), dd_max=float(np.nanmax(v['dd'])),
                           v_end=float(v['v'][-1]), v_max=float(np.nanmax(v['v']))) for k, v in xc.items()}
pickle.dump(xc, open(os.path.join(WORK, 'rel_xcheck.pkl'), 'wb'))

# ============================================================ Figs. 4, 5, 8 (D_L)
ZS = [0.1, 0.5, 1.0, 2.0]
R['dl'] = {}
for name in st:
    if '_dl_' not in name:
        continue
    out = {}
    for c in st[name]['curves']:
        x, y = c.x, c.y
        edge = np.concatenate([s['edge'] for s in c.segs])
        vis = np.concatenate([s['vis'] for s in c.segs])
        ok = ~edge
        vals = {z: at_x(name, c, z) for z in ZS}
        info = dict(zmin=float(x[ok].min()), zmax=float(x[ok].max()), z_first=float(x[0]), z_last=float(x[-1]),
                    nonmono=bool(np.any(np.diff(x[ok]) < 0)), vals=vals)
        if 'newt_gr' in name:
            m = ok & vis
            info['max_vis'] = (float(y[m].max()), float(x[m][np.argmax(y[m])]))
            info['max_all'] = (float(y[ok].max()), float(x[ok][np.argmax(y[ok])]))
            # fraction of visible z-span with diff < 1e-2
            info['frac_below_1pc'] = float(np.mean(y[m] < 1e-2))
        else:
            m = ok & vis
            info['ymin'] = float(y[m].min())
            info['ymax'] = float(y[m].max())
            # where the curve turns around in z (blueshift): z maximum along ray
            if info['nonmono']:
                k = np.argmax(x[ok])
                info['zturn'] = (float(x[ok][k]), float(y[ok][k]))
        out[c.id] = info
    R['dl'][name] = out

# GR-Newt difference reconstructed from the left column vs right column
xcheck_dl = []
for amp, base in [(0.01, 'delta1em2'), (0.005, 'delta5em3'), (0.0025, 'delta2p5em3')]:
    left = base + '_dl_comp_frw'
    right = base + '_dl_newt_gr'
    for c in st[right]['curves']:
        src, aem = c.id.split('_aem')
        g = [k for k in st[left]['curves'] if k.id.startswith('GR_%s_aem' % src) and abs(float(k.id.split('aem')[1]) - float(aem)) < 0.5]
        n = [k for k in st[left]['curves'] if k.id.startswith('Newt_%s_aem' % src) and abs(float(k.id.split('aem')[1]) - float(aem)) < 0.5]
        if not g or not n:
            continue
        for z in ZS:
            yg = at_x(left, g[0], z)
            yn = at_x(left, n[0], z)
            yr = at_x(right, c, z)
            if yg and yn and yr:
                rec = abs((1 + yn[0]) / (1 + yg[0]) - 1)
                xcheck_dl.append((amp, c.id, z, rec, yr[0], len(yg), len(yn), len(yr)))
R['dl_xcheck'] = xcheck_dl

# Fig. 8 high-res vs Fig. 4 top right
f8 = {}
for nm, src in [('delta1em2_dl_newt_gr_res_ou', 'OD'), ('delta1em2_dl_newt_gr_res_uo', 'UD')]:
    for c in st[nm]['curves']:
        aem = c.id.split('_aem')[1].split('_')[0]
        ref = [k for k in st['delta1em2_dl_newt_gr']['curves'] if k.id == '%s_aem%s' % (src, aem)]
        if not ref:
            continue
        diffs = []
        for z in np.exp(np.linspace(np.log(0.012), np.log(5), 200)):
            a = at_x(nm, c, z)
            b = at_x('delta1em2_dl_newt_gr', ref[0], z)
            if a and b and a[0] > 1e-4 and b[0] > 1e-4:
                diffs.append(abs(np.log10(a[0] / b[0])))
        f8[c.id] = (float(np.median(diffs)), float(np.max(diffs))) if diffs else None
R['fig8_vs_fig4'] = f8

# ============================================================ constraint plot
AV = [1.5, 2, 3, 5, 10, 20, 30, 40, 60, 80, 100, 120, 140]
cn = {}
for c in st['10m2_cnst_conv']['curves']:
    fac = c.meta['plotted_scale_factor']
    cn[c.id] = dict(fac=fac, vals={a: (at_x('10m2_cnst_conv', c, a) or [None])[0] for a in AV},
                    xr=(float(c.x.min()), float(c.x.max())), peak=(float(c.x[np.argmax(c.y)]), float(c.y.max())))
R['cnst'] = cn
with open(os.path.join(OUT, '10m2_cnst_conv', 'values_at_a.csv'), 'w') as f:
    f.write('# plotted (rescaled) constraint norm and the raw norm (= plotted / factor) at selected <a>; empty = not plotted\n')
    f.write('a_avg,' + ','.join('%s_plotted,%s_raw' % (k, k) for k in cn) + '\n')
    for a in AV:
        row = []
        for k, v in cn.items():
            p = v['vals'][a]
            row += ['%.4g' % p if p else '', '%.4g' % (p / v['fac']) if p else '']
        f.write('%g,%s\n' % (a, ','.join(row)))

pickle.dump(R, open(os.path.join(WORK, 'results.pkl'), 'wb'))
print('done')
