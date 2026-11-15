"""Readers and Maxwell-Juttner functions of the lead's wave-2 review (C-sidm).

Written for the review, independent of the helpers' code: the file layouts are those of
docs/FORMATS.md (snapshots NRPSNAP1, particle files NRPIC001, radial tables) and the
headers of the history files; the Maxwell-Juttner moments are closed forms in scaled
Bessel functions (theta = T/m, z = 1/theta).
"""
import json
import math
import os
import re

import numpy as np
from scipy.optimize import brentq
from scipy.special import kve

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SCR = "/data/haiyangw/nrpic/scratch/C-sidm"


def outdir():
    d = os.environ.get("NRPIC_RUN_DIR") or os.path.join(SCR, "tmp", "review_wave2")
    os.makedirs(d, exist_ok=True)
    return d


# ---------------------------------------------------------------- files
def read_snap(path):
    """NRPSNAP1: magic, float64 time, int64 N, int64 cycle, N x 7 float64, N int32 tags,
    N int32 species."""
    with open(path, "rb") as f:
        b = f.read()
    assert b[:8] == b"NRPSNAP1", path
    t = np.frombuffer(b, "<f8", 1, 8)[0]
    n = int(np.frombuffer(b, "<i8", 1, 16)[0])
    cyc = int(np.frombuffer(b, "<i8", 1, 24)[0])
    off = 32
    rec = np.frombuffer(b, "<f8", 7 * n, off).reshape(n, 7)
    off += 56 * n
    tag = np.frombuffer(b, "<i4", n, off)
    off += 4 * n
    sp = np.frombuffer(b, "<i4", n, off)
    off += 4 * n
    tau = None
    if len(b) == off + 8 * n:
        # N float64 of proper time follow (nrpic_io.cpp:943-944, NrpicWriteSnapshot); the
        # table of docs/FORMATS.md line 123 does not list them
        tau = np.frombuffer(b, "<f8", n, off)
        off += 8 * n
    assert off == len(b), (path, off, len(b))
    return dict(t=t, n=n, cycle=cyc, x=rec[:, :3], u=rec[:, 3:6], m=rec[:, 6], tag=tag,
                species=sp, tau=tau, raw_records=b[32:32 + 56 * n + 4 * n])


def read_nrp(path):
    with open(path, "rb") as f:
        b = f.read()
    assert b[:8] == b"NRPIC001", path
    n = int(np.frombuffer(b, "<i8", 1, 8)[0])
    rec = np.frombuffer(b, "<f8", 7 * n, 16).reshape(n, 7)
    sp = np.frombuffer(b, "<i4", n, 16 + 56 * n)
    assert 16 + 60 * n == len(b)
    return dict(n=n, x=rec[:, :3], u=rec[:, 3:6], m=rec[:, 6], species=sp)


def read_hist(path):
    """Text history with a header line '# [1]=name [2]=name ...'; returns dict of arrays."""
    names, rows = None, []
    with open(path) as f:
        for line in f:
            if line.startswith("#"):
                found = re.findall(r"\[(\d+)\]=(\S+)", line)
                if found:
                    names = [nm for _, nm in found]
                continue
            if line.strip():
                rows.append([float(v) for v in line.split()])
    a = np.array(rows)
    assert names is not None and a.shape[1] == len(names), path
    return {nm: a[:, i] for i, nm in enumerate(names)}


def read_table(path):
    """Radial table: rows r, u = psi - 1, alpha on a uniform grid from r = 0."""
    a = np.loadtxt(path, comments="#")
    return a[:, 0], a[:, 1], a[:, 2]


def interp4(rg, f, r):
    """Four-point Lagrange interpolation on a uniform grid starting at 0."""
    dr = rg[1] - rg[0]
    s = r / dr
    k = np.clip(np.floor(s).astype(int) - 1, 0, len(rg) - 4)
    t = s - k
    y0, y1, y2, y3 = f[k], f[k + 1], f[k + 2], f[k + 3]
    return (-y0 * (t - 1) * (t - 2) * (t - 3) / 6 + y1 * t * (t - 2) * (t - 3) / 2
            - y2 * t * (t - 1) * (t - 3) / 2 + y3 * t * (t - 1) * (t - 2) / 6)


def wall_dt(rundir):
    w = json.load(open(os.path.join(rundir, "wall.json")))
    for c in w["cmd"]:
        if c.startswith("particles/dt="):
            return w, float(c.split("=", 1)[1])
    return w, None


def snaps(rundir, stem="box"):
    fs = sorted(p for p in os.listdir(rundir) if p.startswith(stem + ".part.") and p.endswith(".bin"))
    return [os.path.join(rundir, p) for p in fs]


# ---------------------------------------------------------------- Maxwell-Juttner
def mean_W(theta):
    z = 1.0 / theta
    return kve(1, z) / kve(2, z) + 3.0 * theta


def theta_from_W(wbar):
    return math.exp(brentq(lambda lt: mean_W(math.exp(lt)) - wbar, math.log(1e-8), math.log(1e6),
                           xtol=1e-15, rtol=1e-15))


def theta_from_W_vec(wbar, iters=60):
    """Vectorised inverse of mean_W by Newton steps in log(theta), checked to 1e-13."""
    wbar = np.asarray(wbar, float)
    th = np.where(wbar - 1 < 1, (2.0 / 3.0) * (wbar - 1), wbar / 3.0)
    th = np.maximum(th, 1e-12)
    for _ in range(iters):
        f = mean_W(th) - wbar
        th = th * np.exp(-np.clip(f / (c_v(th) * th), -1, 1))
    assert np.all(np.abs(mean_W(th) / wbar - 1) < 1e-13)
    return th


def c_v(theta, h=1e-4):
    """d<W>/dtheta by a fourth-order central difference in theta."""
    d = h * theta
    return (-mean_W(theta + 2 * d) + 8 * mean_W(theta + d) - 8 * mean_W(theta - d)
            + mean_W(theta - 2 * d)) / (12 * d)


def vmol(theta):
    """<v_Mol> of a Maxwell-Juttner gas = 4 K3(2z) / (z K2(z)^2), z = 1/theta."""
    z = 1.0 / theta
    return 4.0 * kve(3, 2 * z) / (z * kve(2, z) ** 2)


def mj_speed_cdf(theta, umax=None, n=200001):
    """CDF of |u| for MJ(theta): pdf ~ u^2 exp(-(W - 1)/theta)."""
    if umax is None:
        umax = max(40 * theta, 40 * math.sqrt(theta)) + 1.0
    u = np.linspace(0.0, umax, n)
    W = np.sqrt(1 + u * u)
    pdf = u * u * np.exp(-(W - 1) / theta)
    c = np.concatenate([[0], np.cumsum(0.5 * (pdf[1:] + pdf[:-1]) * np.diff(u))])
    c /= c[-1]
    return lambda x: np.interp(x, u, c)


def theta_and_se(W, wts=None):
    """theta from <W> (weights = masses), standard error by the delta method."""
    if wts is None:
        wts = np.ones_like(W)
    wn = wts / wts.sum()
    wb = float(np.sum(wn * W))
    th = theta_from_W(wb)
    neff = wts.sum() ** 2 / np.sum(wts * wts)
    var = float(np.sum(wn * (W - wb) ** 2))
    return th, math.sqrt(var / neff) / c_v(th)


def fsum_mW(s):
    W = np.sqrt(1.0 + np.sum(s["u"] ** 2, 1))
    return math.fsum((s["m"] * W).tolist())
