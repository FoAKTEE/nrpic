"""Axis calibration and data conversion for the East+ (arXiv:1908.05683) figures."""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
_REPO = _os.path.abspath(_os.path.join(_HERE, '..', '..', '..', '..'))

import re
import numpy as np
from collections import Counter
import psparse as P

SRC = _REPO + '/refs/arxiv_1908.05683/src'

LT = 1e-2          # symlog linthresh of the Fig. 4 left column (from the ticks)


def g_symlog(v, lt=LT, c=None):
    """matplotlib-1.5 symlog transform in units of lt-decades, with linscale_adj c."""
    v = np.asarray(v, float)
    out = np.where(np.abs(v) <= lt, v / lt * c,
                   np.sign(v) * (c + np.log10(np.maximum(np.abs(v), 1e-300) / lt)))
    return out


def g_symlog_inv(u, lt=LT, c=None):
    u = np.asarray(u, float)
    return np.where(np.abs(u) <= c, u / c * lt, np.sign(u) * lt * 10 ** (np.abs(u) - c))


class Axis:
    """pos = A + B * f(value) with f = id, log10 or symlog."""

    def __init__(self, ticks, kind):
        self.kind = kind
        pos = np.array([t[0] for t in ticks])
        val = np.array([t[1] for t in ticks])
        self.ticks = list(zip(pos, val))
        if kind == 'lin':
            f = val
        elif kind == 'log':
            f = np.log10(val)
        elif kind == 'symlog':
            # solve for linscale_adj c from the 0 and +-lt ticks
            p0 = pos[val == 0][0]
            plt_ = pos[np.isclose(val, LT)][0]
            p10 = pos[np.isclose(val, 10 * LT)][0]
            B = p10 - plt_
            self.c = (plt_ - p0) / B
            f = g_symlog(val, c=self.c)
        M = np.vstack([np.ones_like(f), f]).T
        (self.A, self.B), *_ = np.linalg.lstsq(M, pos, rcond=None)
        self.resid = pos - (self.A + self.B * f)

    def to_data(self, p):
        u = (np.asarray(p, float) - self.A) / self.B
        if self.kind == 'lin':
            return u
        if self.kind == 'log':
            return 10 ** u
        return g_symlog_inv(u, c=self.c)

    def to_pos(self, v):
        v = np.asarray(v, float)
        if self.kind == 'lin':
            f = v
        elif self.kind == 'log':
            f = np.log10(v)
        else:
            f = g_symlog(v, c=self.c)
        return self.A + self.B * f

    def describe(self):
        s = '%s axis: pos = %.6f + %.6f * f(v)' % (self.kind, self.A, self.B)
        if self.kind == 'symlog':
            s += ' (linthresh=%g, linscale_adj=%.5f)' % (LT, self.c)
        s += '; ticks used: ' + ', '.join('%g@%.3f' % (v, p) for p, v in self.ticks)
        s += '; max |residual| = %.4f pt' % np.max(np.abs(self.resid))
        return s


def load_mpl(name, xkind, ykind):
    d = P.parse('%s/%s.eps' % (SRC, name))
    clips = Counter(s['clip'] for s in d['strokes'])
    ax = max((c for c in clips if c and not (c[2] == 0 and c[3] == 0)), key=lambda c: clips[c])
    t = P.axis_ticks(d, ax)
    X = Axis([(p, v) for p, v, _ in t['x']], xkind)
    Y = Axis([(p, v) for p, v, _ in t['y']], ykind)
    w, h, x0, y0 = ax
    strokes = [s for s in d['strokes'] if s['clip'] == ax]
    for s in strokes:
        pts = np.array(s['pts'])
        s['P'] = pts
        s['x'] = X.to_data(pts[:, 0])
        s['y'] = Y.to_data(pts[:, 1])
    box = dict(x0=x0, x1=x0 + w, y0=y0, y1=y0 + h,
               xlim=(float(X.to_data(x0)), float(X.to_data(x0 + w))),
               ylim=(float(Y.to_data(y0)), float(Y.to_data(y0 + h))))
    # visible limits as far as the page canvas lets a path extend (matplotlib PS
    # backend clips paths to the 576x432 pt canvas, not to the axes)
    return dict(d=d, X=X, Y=Y, strokes=strokes, box=box, clip=ax)


# ------------------------------------------------------------------ gnuplot
def load_gnuplot(name):
    """Parse the gnuplot-5.2 EPS (rel_eff.eps).  Units are 0.05 pt."""
    txt = open('%s/%s.eps' % (SRC, name), errors='replace').read()
    body = txt.split('%%Page: 1 1', 1)[1]
    lines = body.split('\n')
    cur = None
    cp = (0, 0)
    color = (0, 0, 0)
    block = None
    paths = []      # (block, color, [pts])
    labels = []     # (x, y, text, op)
    pending_label = None
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        i += 1
        mb = re.match(r'^% Begin plot #(\d+)', s)
        if mb:
            block = int(mb.group(1))
            continue
        if re.match(r'^% End plot', s):
            if cur and len(cur) > 1:
                paths.append((block, color, cur))
            cur = None
            block = None
            continue
        if s.startswith('['):
            # text array; collect until ...show
            parts = []
            j = i - 1
            while True:
                t = lines[j].strip()
                for m in re.finditer(r'\[\(([^)]*)\)\s+(\S+)\s+(\S+)\s+\S+\s+\S+\s+\S+\s+\(((?:[^()\\]|\\.)*)\)\]', t):
                    parts.append((m.group(1), float(m.group(2)), float(m.group(3)), m.group(4)))
                if re.search(r'M[RLC]show', t):
                    op = re.search(r'(M[RLC]show)', t).group(1)
                    break
                j += 1
            labels.append((cp[0], cp[1], parts, op))
            i = j + 1
            continue
        toks = s.split()
        if not toks:
            continue
        # colour statement like "0.58 0.00 0.83 C ..." possibly followed by M
        k = 0
        while k < len(toks):
            tk = toks[k]
            def isnum(x):
                return re.match(r'^-?\d+(\.\d*)?$', x) is not None
            if tk == 'C' and k >= 3 and all(isnum(x) for x in toks[k - 3:k]):
                color = tuple(float(x) for x in toks[k - 3:k])
            elif tk in ('M', 'N', 'V', 'R') and k >= 2 and not (isnum(toks[k - 2]) and isnum(toks[k - 1])):
                pass
            elif tk in ('M', 'N') and k >= 2:
                if cur and len(cur) > 1:
                    paths.append((block, color, cur))
                cp = (int(toks[k - 2]), int(toks[k - 1]))
                cur = [cp]
            elif tk == 'V' and k >= 2:
                cp = (cp[0] + int(toks[k - 2]), cp[1] + int(toks[k - 1]))
                if cur is None:
                    cur = [cp]
                else:
                    cur.append(cp)
            elif tk == 'R' and k >= 2:
                if cur and len(cur) > 1:
                    paths.append((block, color, cur))
                cp = (cp[0] + int(toks[k - 2]), cp[1] + int(toks[k - 1]))
                cur = [cp]
            elif tk == 'stroke':
                if cur and len(cur) > 1:
                    paths.append((block, color, cur))
                cur = None
            k += 1
    return paths, labels
