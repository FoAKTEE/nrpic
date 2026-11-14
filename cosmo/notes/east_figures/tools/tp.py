import numpy as np


def zigzag(x, y, h):
    """Turning points of polyline (x, y) with hysteresis h (in y units).
    Returns list of (kind, index) with kind 'max'/'min'; only confirmed reversals."""
    out = []
    if len(y) < 3:
        return out
    trend = 0
    ext_i = 0
    for i in range(1, len(y)):
        if trend >= 0:
            if y[i] > y[ext_i]:
                ext_i = i
                if trend == 0 and y[i] - y[0] > h:
                    trend = 1
            elif y[ext_i] - y[i] > h:
                if trend == 1:
                    out.append(('max', ext_i))
                elif trend == 0:
                    out.append(('max', ext_i)) if ext_i > 0 else None
                trend = -1
                ext_i = i
        if trend == -1 and i > ext_i:
            if y[i] < y[ext_i]:
                ext_i = i
            elif y[i] - y[ext_i] > h:
                out.append(('min', ext_i))
                trend = 1
                ext_i = i
        elif trend == -1 and i == ext_i:
            pass
    return out


def first_cross(x, y, level, log=True):
    """first a where the polyline y(x) reaches `level` going up; interpolate in log-log."""
    for i in range(len(y) - 1):
        if y[i] < level <= y[i + 1]:
            if log:
                f = (np.log(level) - np.log(y[i])) / (np.log(y[i + 1]) - np.log(y[i]))
                return float(np.exp(np.log(x[i]) + f * (np.log(x[i + 1]) - np.log(x[i]))))
            f = (level - y[i]) / (y[i + 1] - y[i])
            return float(x[i] + f * (x[i + 1] - x[i]))
    return None


def at_x(x, y, x0, logx=True, logy=True):
    """all values of y where the polyline passes x0 (in drawing order)."""
    vals = []
    for i in range(len(x) - 1):
        a, b = x[i], x[i + 1]
        if (a - x0) * (b - x0) <= 0 and a != b:
            if logx:
                f = (np.log(x0) - np.log(a)) / (np.log(b) - np.log(a))
            else:
                f = (x0 - a) / (b - a)
            if logy and y[i] > 0 and y[i + 1] > 0:
                v = np.exp(np.log(y[i]) + f * (np.log(y[i + 1]) - np.log(y[i])))
            else:
                v = y[i] + f * (y[i + 1] - y[i])
            if not vals or abs(i - vals[-1][1]) > 1 or True:
                vals.append((float(v), i))
    # remove duplicates from vertices exactly at x0
    out = []
    for v, i in vals:
        if not out or abs(i - out[-1][1]) > 1:
            out.append((v, i))
    return [v for v, i in out]
