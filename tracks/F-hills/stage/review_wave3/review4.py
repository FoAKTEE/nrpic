#!/usr/bin/env python3
"""Lead's independent checks of wave 3, batch 4a (F-hills JOURNAL.md, lead session of
2026-11-21T15:55Z, predictions L4-L5).

Written by the lead without the packages' readers (binary_conv/scripts/analyze.py, refs.py,
junk_gauge/scripts/junk_lib.py, nr_first/scripts/nrread.py, eih/eih.py): it parses AthenaK's raw
files and integrates its own equations.

  review4.py bc <out> <R8 dir> <R16n dir> <P1 dir> <bin_m16.athinput>
      L4: tracker separations, own ADM 1PN two-body Hamiltonian (Schaefer-Jaranowski form,
      momenta canonical, bare masses), Newton, horizons, history H-norm2.
  review4.py pn <out> <bin_m16.athinput>
      L4f: 1PN variants of the isolated binary (ADM Hamiltonian; harmonic EIH started with v
      from the truncated or the exact inversion of the momenta), input and centre-of-mass frame.
  review4.py junk <out> <P1 dir>
      L5: fixed-frequency integration (Reisswig and Pollney 2011) of r psi4 modes l = 2..8 at
      70 and 90 M (and 40, 48 M), energy in the retarded-time window [-35, 6] M.

Writes <out>/review4_<mode>.json and <out>/fig_review4_<mode>.{png,pdf}.
"""
import glob
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "python"))


def _fig():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    return plt, fs


# ------------------------------------------------------------------------------ readers
def read_tracker_series(rundir, n):
    files = sorted(glob.glob(os.path.join(rundir, "trk_keep", "*", f"hills.co_{n}.txt")))
    files.append(os.path.join(rundir, f"hills.co_{n}.txt"))
    rows = {}
    for f in files:                          # later file wins on equal time keys
        if not os.path.exists(f):
            continue
        a = np.loadtxt(f, comments="#", ndmin=2)
        for r in a:
            rows[round(float(r[1]), 9)] = r[2:5]
    t = np.array(sorted(rows))
    x = np.array([rows[k] for k in t])
    return t, x


def separation(rundir):
    t0, x0 = read_tracker_series(rundir, 0)
    t1, x1 = read_tracker_series(rundir, 1)
    tc = np.intersect1d(t0, t1)
    d = np.linalg.norm(x0[np.searchsorted(t0, tc)] - x1[np.searchsorted(t1, tc)], axis=1)
    return tc, d


def read_horizon(path):
    a = np.loadtxt(path, comments="#", ndmin=2)
    t, m, hrms = a[:, 1], a[:, 2], a[:, 8]
    good = np.isfinite(m) & np.isfinite(hrms) & (hrms < 1e-3)
    rep = np.zeros(len(a), bool)
    rep[1:] = np.all(a[1:, 2:12] == a[:-1, 2:12], axis=1)
    return t, m, good & ~rep, rep


def read_hst(path):
    a = np.loadtxt(path, comments="#", ndmin=2)
    return a[:, 0], a[:, 3]                 # time, H-norm2


def read_punctures(path):
    vals = {}
    sec = None
    for line in open(path):
        s = line.split("#")[0].strip()
        if s.startswith("<"):
            sec = s.strip("<>")
            continue
        if sec == "problem" and "=" in s:
            k, v = [w.strip() for w in s.split("=", 1)]
            vals[k] = v
    n = int(vals["ncomp"])
    m = np.array([float(vals[f"comp{c}_mass"]) for c in range(n)])
    x = np.array([[float(vals[f"comp{c}_x{i}"]) for i in (1, 2, 3)] for c in range(n)])
    p = np.array([[float(vals[f"comp{c}_p{i}"]) for i in (1, 2, 3)] for c in range(n)])
    return m, x, p


# ------------------------------------------------------------------------- 1PN two-body
def ham(q, p, m1, m2, pn=True):
    """ADM two-body Hamiltonian to 1PN, G = c = 1 (complex-safe)."""
    x1, x2, p1, p2 = q[:3], q[3:], p[:3], p[3:]
    rv = x1 - x2
    r = np.sqrt(np.sum(rv * rv))
    n = rv / r
    p1s, p2s = np.sum(p1 * p1), np.sum(p2 * p2)
    h = p1s / (2 * m1) + p2s / (2 * m2) - m1 * m2 / r
    if pn:
        h += -(p1s ** 2 / (8 * m1 ** 3) + p2s ** 2 / (8 * m2 ** 3))
        h += -(m1 * m2 / (2 * r)) * (3 * p1s / m1 ** 2 + 3 * p2s / m2 ** 2
                                     - 7 * np.sum(p1 * p2) / (m1 * m2)
                                     - np.sum(n * p1) * np.sum(n * p2) / (m1 * m2))
        h += m1 * m2 * (m1 + m2) / (2 * r * r)
    return h


def grad_cs(f, z, eps=1e-30):
    g = np.empty(len(z))
    for i in range(len(z)):
        zz = z.astype(complex)
        zz[i] += 1j * eps
        g[i] = f(zz).imag / eps
    return g


def integrate(m, x, p, tend, pn, ts):
    from scipy.integrate import solve_ivp
    m1, m2 = m

    def rhs(t, y):
        q, pp = y[:6], y[6:]
        dq = grad_cs(lambda z: ham(q, z, m1, m2, pn), pp)
        dp = -grad_cs(lambda z: ham(z, pp, m1, m2, pn), q)
        return np.concatenate([dq, dp])

    y0 = np.concatenate([x.ravel(), p.ravel()])
    sol = solve_ivp(rhs, (0, tend), y0, method="DOP853", rtol=1e-12, atol=1e-13,
                    t_eval=ts)
    Y = sol.y.T
    s = np.linalg.norm(Y[:, :3] - Y[:, 3:6], axis=1)
    h0 = ham(y0[:6], y0[6:], m1, m2, pn)
    h1 = ham(Y[-1, :6], Y[-1, 6:], m1, m2, pn)
    return s, float(h0), float(abs(h1 - h0) / abs(h0))


def mode_bc(out, r8, r16, p1, inp):
    res = {}
    S = {k: separation(d) for k, d in (("P1", p1), ("R8", r8), ("R16n", r16))}
    times = [2.5, 5.0, 7.5, 10.0, 15.0, 20.0]
    for k, (t, d) in S.items():
        res[f"{k}_t_range"] = [float(t[0]), float(t[-1])]
        res[f"{k}_sep"] = {f"{tt}": (float(np.interp(tt, t, d)) if tt <= t[-1] else None)
                           for tt in times}
    tp, dp = S["P1"]
    t8, d8 = S["R8"]
    diff = np.abs(d8 - np.interp(t8, tp, dp))
    i = int(np.argmax(diff))
    res["max_abs_R8_minus_P1"] = [float(t8[i]), float(diff[i])]
    for tt in (7.5, 15.0, 20.0):
        ds8 = d8[0] - np.interp(tt, t8, d8)
        dsp = dp[0] - np.interp(tt, tp, dp)
        res[f"Delta_s_ratio_R8_P1_{tt}"] = float(ds8 / dsp)

    m, x, p = read_punctures(inp)
    ts = np.linspace(0, 25.0, 2501)
    s1, h1, dh1 = integrate(m, x, p, 25.0, True, ts)
    s0, h0, dh0 = integrate(m, x, p, 25.0, False, ts)
    res["adm1pn_H0"], res["adm1pn_rel_drift_H"] = h1, dh1
    res["newton_H0"], res["newton_rel_drift_H"] = h0, dh0
    res["adm1pn_sep"] = {f"{tt}": float(np.interp(tt, ts, s1)) for tt in times}
    res["newton_sep"] = {f"{tt}": float(np.interp(tt, ts, s0)) for tt in times}
    t16, d16 = S["R16n"]
    dev16 = d16 - np.interp(t16, ts, s1)
    res["R16n_minus_adm1pn_range"] = [float(dev16.min()), float(dev16.max())]
    res["R8_minus_adm1pn_at_7.5"] = float(np.interp(7.5, t8, d8) - np.interp(7.5, ts, s1))
    res["R16n_minus_adm1pn_at_7.5"] = float(np.interp(7.5, t16, d16) - np.interp(7.5, ts, s1))

    hz = {}
    for k, d in (("R8", r8), ("R16n", r16)):
        for n in (0, 1):
            t, mm, g, rep = read_horizon(os.path.join(d, f"hills.horizon_summary_{n}.txt"))
            late = t > 0.5
            w = g & (t >= 3.0)
            w5 = g & (t >= 5.0)
            fit = np.polyfit(t[w5], mm[w5], 1) if w5.sum() > 3 else [float("nan")] * 2
            hz[(k, n)] = (t, mm, g)
            res[f"{k}_finder{n}"] = dict(rows=int(len(t)), bad_after_0_5=int((late & ~g).sum()),
                                         repeats=int(rep.sum()),
                                         m_range_after_3=[float(mm[w].min()), float(mm[w].max())],
                                         first_good=[float(t[g][0]), float(mm[g][0])],
                                         last_good=[float(t[g][-1]), float(mm[g][-1])],
                                         drift_per_M_after_5=float(fit[0]))
    for k, d in (("R8", r8), ("P1", p1), ("R16n", r16)):
        th, hn = read_hst(os.path.join(d, "hills.z4c.user.hst"))
        res[f"{k}_Hnorm2"] = {f"{tt}": float(hn[np.argmin(np.abs(th - tt))]) for tt in (0.0, 0.5, 1.0)}
        res[f"{k}_Hnorm2"]["times_found"] = [float(th[np.argmin(np.abs(th - tt))]) for tt in (0.0, 0.5, 1.0)]
        res[f"{k}_Hnorm2_after_2_median"] = float(np.median(hn[th > 2.0]))
    json.dump(res, open(os.path.join(out, "review4_bc.json"), "w"), indent=1)

    plt, fs = _fig()
    fig, ax = plt.subplots(3, 1, figsize=(fs.COLUMN_WIDTH * 1.5, 7.0), sharex=True)
    ax[0].plot(tp[tp <= 25], dp[tp <= 25], color="k", label="P1 (three holes, m/8)")
    ax[0].plot(t8, d8, color=fs.PAL["red"], label="binary alone, m/8")
    ax[0].plot(t16, d16, color=fs.PAL["blue"], lw=1.6, label="binary alone, m/16")
    ax[0].plot(ts, s1, color=fs.PAL["orange"], ls="--", label="own ADM 1PN")
    ax[0].plot(ts, s0, color=fs.PAL["green"], ls=":", label="own Newton")
    ax[0].set_ylabel("separation [M]")
    ax[0].legend(loc="lower left", fontsize=7)
    ax[1].plot(t8, d8 - np.interp(t8, ts, s1), color=fs.PAL["red"], label="m/8 - 1PN")
    ax[1].plot(t16, dev16, color=fs.PAL["blue"], lw=1.6, label="m/16 - 1PN")
    ax[1].plot(ts, s0 - s1, color=fs.PAL["green"], ls=":", label="Newton - 1PN")
    ax[1].axhline(0, color="0.6", lw=0.5)
    ax[1].set_yscale("symlog", linthresh=1e-3)
    ax[1].set_ylabel("deviation from 1PN [M]")
    ax[1].legend(loc="lower left", fontsize=7)
    for (k, n), (t, mm, g) in hz.items():
        c = fs.PAL["red"] if k == "R8" else fs.PAL["blue"]
        ax[2].plot(t[g], mm[g], ".", ms=1.5, color=c, alpha=0.8 if n == 0 else 0.4,
                   label=f"{k} finder {n}")
    ax[2].set_ylabel("member horizon mass [M]")
    ax[2].set_xlabel("t [M]")
    ax[2].legend(loc="upper left", fontsize=7, markerscale=5)
    fig.subplots_adjust(left=0.15, right=0.97, top=0.98, bottom=0.07, hspace=0.07)
    fs.save(fig, os.path.join(out, "fig_review4_bc"))
    print(json.dumps(res, indent=1))


# ------------------------------------------------------------------------------- junk
def tortoise(R, M):
    return R + 2 * M * math.log(R / (2 * M) - 1)


def cos_taper(t, w):
    f = np.ones_like(t)
    a, b = t[0], t[-1]
    lo, hi = t < a + w, t > b - w
    f[lo] = 0.5 * (1 - np.cos(np.pi * (t[lo] - a) / w))
    f[hi] = 0.5 * (1 - np.cos(np.pi * (b - t[hi]) / w))
    return f


def ffi_once(t, z, w0, taper_w=4.0):
    """int z dt with the frequency floor w0 (numpy FFT: d/dt <-> i w)."""
    dt = t[1] - t[0]
    n = len(t)
    N = 4 * n
    zz = np.zeros(N, complex)
    zz[:n] = z * cos_taper(t, taper_w)
    w = 2 * np.pi * np.fft.fftfreq(N, dt)
    wf = np.where(np.abs(w) > w0, w, w0 * np.where(w >= 0, 1.0, -1.0))
    return np.fft.ifft(np.fft.fft(zz) / (1j * wf))[:n]


def mode_junk(out, p1):
    Mtot = 1.25
    res = {}
    plt, fs = _fig()
    fig, ax = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH * 1.5, 3.2))
    for R, c in ((40, fs.PAL["red"]), (48, fs.PAL["orange"]), (70, fs.PAL["green"]), (90, fs.PAL["blue"])):
        fr = os.path.join(p1, "waveforms", f"rpsi4_real_{R:04d}.txt")
        fi = os.path.join(p1, "waveforms", f"rpsi4_imag_{R:04d}.txt")
        hdr = open(fr).readline().split()[1:]
        names = [h.split(":")[1] for h in hdr]
        ar, ai = np.loadtxt(fr, comments="#"), np.loadtxt(fi, comments="#")
        t = ar[:, 0]
        # keep the first occurrence of each time (restart overlaps), sorted
        _, idx = np.unique(t, return_index=True)
        ar, ai, t = ar[idx], ai[idx], t[idx]
        u = t - tortoise(R, Mtot)
        cut = u <= 14.0
        uu = u[cut]
        dE = np.zeros(cut.sum())
        El = {}
        for j, nm in enumerate(names[1:], start=1):
            l = int(nm[0])
            z = ar[cut, j] + 1j * ai[cut, j]
            news = ffi_once(uu, z, 0.2)
            rate = np.abs(news) ** 2 / (16 * np.pi)
            dE += rate
            win = (uu >= -35) & (uu <= 6)
            El[l] = El.get(l, 0.0) + float(np.trapz(rate[win], uu[win]))
        win = (uu >= -35) & (uu <= 6)
        E = float(np.trapz(dE[win], uu[win]))
        res[f"R{R}"] = dict(E_window=E, l_ge4_share=float(sum(v for k, v in El.items() if k >= 4) / E),
                            E_l={str(k): v for k, v in sorted(El.items())},
                            u_range=[float(uu[0]), float(uu[-1])], dt=float(uu[1] - uu[0]))
        cum = np.concatenate([[0], np.cumsum(0.5 * (dE[1:] + dE[:-1]) * np.diff(uu))])
        res[f"R{R}"]["E_early_m35_m28"] = float(np.interp(-28, uu, cum) - np.interp(-35, uu, cum))
        res[f"R{R}"]["rate_m20_6"] = float((np.interp(6, uu, cum) - np.interp(-20, uu, cum)) / 26.0)
        res[f"R{R}"]["E_m28_6"] = float(np.interp(6, uu, cum) - np.interp(-28, uu, cum))
        sel = (uu >= -40) & (uu <= 14)
        ax.plot(uu[sel], cum[sel] - np.interp(-35, uu, cum), color=c, label=f"R = {R} M")
    ax.axvspan(-35, 6, color="0.9", zorder=0)
    ax.set_xlabel("u = t - R* [M]")
    ax.set_ylabel("E(u) - E(-35) [M]")
    ax.legend(loc="upper left", fontsize=7)
    fig.subplots_adjust(left=0.16, right=0.97, top=0.97, bottom=0.16)
    fs.save(fig, os.path.join(out, "fig_review4_junk"))
    json.dump(res, open(os.path.join(out, "review4_junk.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))


# ------------------------------------------------------------- L4f: 1PN ambiguity
def eih_acc(x1, x2, v1, v2, m1, m2):
    """Harmonic 1PN two-body accelerations (Blanchet, Living Rev. Rel. 17, 2 (2014), Eq. 203
    to 1PN)."""
    def a(xa, xb, va, vb, ma, mb):
        X = xa - xb
        r = np.linalg.norm(X)
        n = X / r
        br = (5 * ma / r + 4 * mb / r + 1.5 * np.dot(n, vb) ** 2 - np.dot(va, va)
              + 4 * np.dot(va, vb) - 2 * np.dot(vb, vb))
        return (-mb * n / r ** 2 + (mb / r ** 2) * br * n
                + (mb / r ** 2) * (4 * np.dot(n, va) - 3 * np.dot(n, vb)) * (va - vb))
    return a(x1, x2, v1, v2, m1, m2), a(x2, x1, v2, v1, m2, m1)


def eih_momenta(x, v, m):
    """p_a = dL/dv_a of the 1PN (EIH) Lagrangian, two bodies (own form)."""
    out = np.zeros_like(v)
    for a, b in ((0, 1), (1, 0)):
        X = x[a] - x[b]
        r = np.linalg.norm(X)
        n = X / r
        out[a] = (m[a] * v[a] * (1 + 0.5 * np.dot(v[a], v[a]) + 3 * m[b] / r)
                  - 0.5 * m[a] * m[b] / r * (7 * v[b] + n * np.dot(n, v[b])))
    return out


def v_exact(x, p, m):
    from scipy.optimize import fsolve
    v0 = p / m[:, None]
    sol = fsolve(lambda vv: (eih_momenta(x, vv.reshape(2, 3), m) - p).ravel(), v0.ravel(),
                 xtol=1e-15)
    return sol.reshape(2, 3)


def run_eih(x, v, m, ts):
    from scipy.integrate import solve_ivp

    def rhs(t, y):
        a1, a2 = eih_acc(y[0:3], y[3:6], y[6:9], y[9:12], m[0], m[1])
        return np.concatenate([y[6:12], a1, a2])
    s = solve_ivp(rhs, (0, ts[-1]), np.concatenate([x.ravel(), v.ravel()]), method="DOP853",
                  rtol=1e-12, atol=1e-13, t_eval=ts)
    return np.linalg.norm(s.y[0:3].T - s.y[3:6].T, axis=1)


def mode_pn(out, inp):
    m, x, p = read_punctures(inp)
    ts = np.array([0, 2.5, 5, 7.5, 10, 15, 20])
    tf = np.linspace(0, 20, 801)
    res = {"times": ts.tolist()}
    curves = {}
    for frame in ("input", "cm"):
        pp = p.copy()
        if frame == "cm":
            pp = p - np.outer(m / m.sum(), p.sum(0))
        q = x.ravel()
        v_tr = grad_cs(lambda z: ham(q, z, m[0], m[1], True), pp.ravel()).reshape(2, 3)
        v_ex = v_exact(x, pp, m)
        var = {"adm_hamiltonian": integrate(m, x, pp, 20.0, True, tf)[0],
               "eih_v_truncated": run_eih(x, v_tr, m, tf),
               "eih_v_exact": run_eih(x, v_ex, m, tf),
               "newton": integrate(m, x, pp, 20.0, False, tf)[0]}
        res[frame] = {k: np.interp(ts, tf, s).round(6).tolist() for k, s in var.items()}
        pn = np.array([var[k] for k in ("adm_hamiltonian", "eih_v_truncated", "eih_v_exact")])
        spread = pn.max(0) - pn.min(0)
        res[frame]["spread_1pn"] = np.interp(ts, tf, spread).round(6).tolist()
        res[frame]["v_exact_minus_truncated_max"] = float(np.abs(v_ex - v_tr).max())
        curves[frame] = var
    pkg = [4.9519, 4.9503, 4.9490, 4.9478, 4.9464, 4.9412, 4.9302]   # BC-3 table, EIH canonical
    res["eih_v_exact_minus_package"] = (np.array(res["input"]["eih_v_exact"]) - pkg).round(6).tolist()
    json.dump(res, open(os.path.join(out, "review4_pn.json"), "w"), indent=1)
    plt, fs = _fig()
    fig, ax = plt.subplots(1, 2, figsize=(fs.COLUMN_WIDTH * 2, 3.0), sharey=True)
    sty = {"adm_hamiltonian": (fs.PAL["orange"], "-"), "eih_v_truncated": (fs.PAL["red"], "--"),
           "eih_v_exact": (fs.PAL["blue"], "-."), "newton": (fs.PAL["green"], ":")}
    for a_, frame in zip(ax, ("input", "cm")):
        for k, s in curves[frame].items():
            a_.plot(tf, s, color=sty[k][0], ls=sty[k][1], label=k.replace("_", " "))
        a_.set_title(f"{frame} frame", fontsize=8)
        a_.set_xlabel("t [M]")
    ax[0].plot(ts, pkg, "ko", ms=3, label="package EIH canonical")
    ax[0].set_ylabel("separation [M]")
    ax[0].legend(loc="lower left", fontsize=6)
    fig.subplots_adjust(left=0.09, right=0.98, top=0.9, bottom=0.17, wspace=0.05)
    fs.save(fig, os.path.join(out, "fig_review4_pn"))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    mode, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    if mode == "bc":
        mode_bc(out, *sys.argv[3:7])
    elif mode == "pn":
        mode_pn(out, sys.argv[3])
    elif mode == "junk":
        mode_junk(out, sys.argv[3])
    else:
        raise SystemExit(__doc__)
