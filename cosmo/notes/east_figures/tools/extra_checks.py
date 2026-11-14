import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
_REPO = _os.path.abspath(_os.path.join(_HERE, '..', '..', '..', '..'))
import sys, pickle, numpy as np
sys.path.insert(0, _HERE + '/')
from extract_all import Curve  # noqa
import analyze as A   # re-runs analysis (cheap) and gives at_x
st = A.st
R = A.R
E = {}
# signed GR-Newt difference from the left column, s = (1+y_N)/(1+y_GR) - 1  (>0: D_N > D_GR)
sg = {}
for base, amp in [('delta1em2', 0.01), ('delta5em3', 0.005), ('delta2p5em3', 0.0025), ('delta5em2', 0.05)]:
    left = base + '_dl_comp_frw'
    cs = {c.id: c for c in st[left]['curves']}
    for cid, g in cs.items():
        if not cid.startswith('GR_'):
            continue
        n = cs['Newt_' + cid[3:]]
        zlo = max(0.01, g.x.min(), n.x.min())
        zhi = min(np.max(g.x), np.max(n.x))
        zs = np.exp(np.linspace(np.log(zlo), np.log(zhi), 200))
        out = []
        for z in zs:
            a = A.at_x(left, g, z)
            b = A.at_x(left, n, z)
            if a and b:
                out.append((z, (1 + b[0]) / (1 + a[0]) - 1))
        out = np.array(out)
        k = np.argmax(np.abs(out[:, 1]))
        sg[(amp, cid[3:])] = dict(z=out[:, 0], s=out[:, 1], max=(float(out[k, 0]), float(out[k, 1])))
E['signed'] = {k: v['max'] for k, v in sg.items()}
for k, v in sg.items():
    z, s = v['z'], v['s']
    sel = [0.01, 0.02, 0.05, 0.1, 0.2, 0.3, 0.5, 1, 2]
    vals = [(zz, float(np.interp(np.log(zz), np.log(z), s))) for zz in sel if z.min() <= zz <= z.max()]
    print(k, 'max |s| = %.4g at z=%.4g' % (abs(v['max'][1]), v['max'][0]), ' '.join('%g:%+.4f' % t for t in vals))
pickle.dump(sg, open(_HERE + '/signed.pkl', 'wb'))
# convergence order implied by Fig. 6 raw norms
cn = R['cnst']
for a in [1.5, 2, 3, 5, 10, 20, 30, 40, 60, 80, 100, 120, 140]:
    r64 = cn['Ldx64']['vals'][a]
    r96 = cn['Ldx96']['vals'][a] / 2.25 if cn['Ldx96']['vals'][a] else None
    r128 = cn['Ldx128']['vals'][a] / 4 if cn['Ldx128']['vals'][a] else None
    p1 = np.log(r64 / r96) / np.log(1.5) if r96 else None
    p2 = np.log(r96 / r128) / np.log(4 / 3) if (r96 and r128) else None
    print('a=%g  p(64->96)=%s  p(96->128)=%s' % (a, '%.2f' % p1 if p1 else '-', '%.2f' % p2 if p2 else '-'))
# direction ordering of first crossings (z first, then x, then y expected from dbar_i = (1, 0.9, 1.1))
for name in ['delta10em2pm_splash', 'delta5em3pm_splash', 'delta2p5em3pm_splash', 'delta5em2pm_splash']:
    D = R['splash'][name]
    for model in ['GR', 'Newt']:
        for d0 in [0.03125, 0.0625, 0.125, 0.25]:
            t = {d: D['%s_%s_d0_%g' % (model, d, d0)]['t10'] for d in 'xyz'}
            if all(t.values()):
                print(name, model, d0, 'a10 z,x,y = %.2f %.2f %.2f' % (t['z'], t['x'], t['y']), 'order ok' if t['z'] < t['x'] < t['y'] else 'ORDER DIFFERENT')
