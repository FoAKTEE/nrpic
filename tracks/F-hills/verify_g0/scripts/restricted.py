"""verify_g0 K2: restricted parabolic three-body problem of SKR (arXiv:0911.1136), own code.

Equations prp.tex:224-259 (coplanar, z = 0), energy prp.tex:353-357, set-up prp.tex:595-618
(start at r0 = 10 r_t, effective phase phi, phi0 = S w t0 + phi). Units of the paper: lengths
(m/M)^(1/3) r_p, time sqrt(r_p^3/GM); the binary has scaled separation 1/D and angular
velocity D^(3/2). Outcome at r_m = 30 r_t outbound: bound pairs with apocentre beyond half
the Hill radius continue to 300 r_t; then disrupted = pair energy > 0.

Compares with the per-phase arrays of run F-hills-20261115-130237-cbfaf6b (coplanar.npz,
sha256 checked) at the same D.

Usage: python3 restricted.py --out DIR [--nphase 3000] [--rtol 1e-10]
"""
import argparse
import hashlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vint  # noqa: E402
import figstyle as fs  # noqa: E402

SCR = "/data/haiyangw/nrpic/scratch/F-hills"
TRACK_RUN = "F-hills-20261115-130237-cbfaf6b"
S2 = np.sqrt(2.0)


def t_of_f(f):
    u = np.tan(f / 2)
    return S2 / 3 * u * (3 + u * u)


def rhs(t, y, idx):
    x, yy, vx, vy, f = y.T
    c, s = np.cos(f), np.sin(f)
    k = (1 + c) ** 3 / 8
    proj = x * c + yy * s
    r3 = (x * x + yy * yy) ** 1.5
    ax = k * (-x + 3 * proj * c) - x / r3
    ay = k * (-yy + 3 * proj * s) - yy / r3
    fd = S2 * (1 + c) ** 2 / 4
    return np.stack([vx, vy, ax, ay, fd], axis=1)


def energy1(y, D):
    x, yy, vx, vy, f = y.T
    c, s = np.cos(f), np.sin(f)
    return -(1 / D) * ((1 + c) ** 2 / 4 * (x * c + yy * s) + (-s * vx + (1 + c) * vy) / S2)


def run_D(D, S, phases, rtol, k0=10.0, k1=30.0, k2=300.0):
    n = len(phases)
    f0 = -np.arccos(2 * D / k0 - 1)
    t0 = t_of_f(f0)
    rho, w = 1.0 / D, D ** 1.5
    ph0 = phases + S * w * t0
    y0 = np.zeros((n, 5))
    y0[:, 0], y0[:, 1] = rho * np.cos(ph0), rho * np.sin(ph0)
    y0[:, 2], y0[:, 3] = -S * rho * w * np.sin(ph0), S * rho * w * np.cos(ph0)
    y0[:, 4] = f0
    t1 = t_of_f(np.arccos(2 * D / k1 - 1))
    h0 = 1e-3 * min(1.0, 2 * np.pi / w)
    t, y, done, nacc = vint.integrate(rhs, y0, t0, t1, rtol=rtol, atol=rtol * 1e-2 * rho, h0=h0)
    # pair state
    r = np.hypot(y[:, 0], y[:, 1])
    v2 = y[:, 2] ** 2 + y[:, 3] ** 2
    eps = 0.5 * v2 - 1 / r
    hz = y[:, 0] * y[:, 3] - y[:, 1] * y[:, 2]
    a = np.where(eps < 0, -1 / (2 * np.minimum(eps, -1e-300)), np.inf)
    e = np.sqrt(np.maximum(0, 1 + 2 * eps * hz * hz))
    apo = a * (1 + e)
    rH = (k1 / D) * 3 ** (-1 / 3)
    wide = (eps < 0) & (apo > 0.5 * rH)
    nwide = int(wide.sum())
    if nwide:
        t2 = t_of_f(np.arccos(2 * D / k2 - 1))
        tw, yw, _, nw = vint.integrate(rhs, y[wide], t[wide], t2, rtol=rtol, atol=rtol * 1e-2 * rho, h0=h0)
        y[wide] = yw
        r = np.hypot(y[:, 0], y[:, 1])
        eps = 0.5 * (y[:, 2] ** 2 + y[:, 3] ** 2) - 1 / r
    dis = eps > 0
    E1 = energy1(y, D)
    return dict(dis=dis, E1=E1, nwide=nwide, nacc=nacc)


def sha(p):
    h = hashlib.sha256()
    h.update(open(p, "rb").read())
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--nphase", type=int, default=3000)
    ap.add_argument("--rtol", type=float, default=1e-10)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    tp = os.path.join(SCR, TRACK_RUN, "coplanar.npz")
    sums = dict((ln.split()[1].lstrip("*").removeprefix("./"), ln.split()[0])
                for ln in open(os.path.join(SCR, TRACK_RUN, "sha256sums.txt")) if ln.strip())
    sha_ok = sums.get("coplanar.npz") == sha(tp)
    z = np.load(tp)
    Dt = z["D"]
    phases = np.arange(a.nphase) * np.pi / a.nphase
    cases = [("pro", 1, d) for d in (0.01, 0.1, 0.16, 0.3, 1.0, 2.0, 2.05, 2.085, 2.09)] + \
            [("ret", -1, d) for d in (0.1, 0.3, 0.4, 0.405, 0.41)]
    rows = []
    for lab, S, D in cases:
        res = run_D(D, S, phases, a.rtol)
        i = int(np.argmin(abs(Dt - D)))
        Pt = float(z[f"disrupted_{lab}"][i].mean())
        Et = z[f"E2_{lab}"][i][z[f"disrupted_{lab}"][i]]
        Em = np.abs(res["E1"][res["dis"]])
        P = float(res["dis"].mean())
        sig = np.sqrt(max(P * (1 - P), 1.0 / a.nphase) / a.nphase)
        row = dict(sense=lab, D=D, D_track=float(Dt[i]), P_mine=P, P_track=Pt, dP=P - Pt,
                   binom_sigma=sig, Emax_mine=float(Em.max()) if len(Em) else 0.0,
                   Emax_track=float(np.abs(Et).max()) if len(Et) else 0.0,
                   Emean_mine=float(Em.mean()) if len(Em) else 0.0,
                   Emean_track=float(np.abs(Et).mean()) if len(Et) else 0.0,
                   n_wide_followed=res["nwide"], max_steps=int(res["nacc"].max()))
        rows.append(row)
        print(json.dumps(row), flush=True)
    out = dict(track_run=TRACK_RUN, track_file_sha256_ok=sha_ok, nphase=a.nphase, rtol=a.rtol, rows=rows)
    json.dump(out, open(os.path.join(a.out, "restricted.json"), "w"), indent=1)

    fs.use_style()
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(8, 3.4))
    ax = fig.add_axes([0.08, 0.15, 0.40, 0.78])
    ax2 = fig.add_axes([0.58, 0.15, 0.40, 0.78])
    for lab, ls in (("pro", "-"), ("ret", "--")):
        ax.plot(Dt, z[f"disrupted_{lab}"].mean(axis=1), color=fs.PAL["blue"], ls=ls,
                label=f"track scan, {lab}grade")
        rr = [r for r in rows if r["sense"] == lab]
        ax.plot([r["D"] for r in rr], [r["P_mine"] for r in rr], "o", mfc="none",
                color=fs.PAL["red"], label=f"this check, {lab}grade")
        E = np.where(z[f"disrupted_{lab}"], np.abs(z[f"E2_{lab}"]), np.nan)
        ax2.plot(Dt, np.nanmax(E, axis=1), color=fs.PAL["blue"], ls=ls, label=f"track, max, {lab}")
        ax2.plot([r["D"] for r in rr], [r["Emax_mine"] for r in rr], "o", mfc="none", color=fs.PAL["red"])
        ax2.plot(Dt, np.nanmean(E, axis=1), color=fs.PAL["green"], ls=ls, label=f"track, mean, {lab}")
        ax2.plot([r["D"] for r in rr], [r["Emean_mine"] for r in rr], "s", mfc="none", color=fs.PAL["red"])
    for v in (2.1, 0.44):
        ax.axvline(v, **fs.MASK_LINE)
    ax.axhline(0.8, **fs.GUIDE)
    ax.set_xscale("log")
    ax.set_xlim(5e-3, 3)
    ax.set_xlabel("$D=r_p/r_t$")
    ax.set_ylabel("$P_{dis}$")
    ax.legend(fontsize=7, loc="lower left")
    ax2.axhline(27.3, **fs.GUIDE)
    ax2.axhline(1.8, **fs.GUIDE)
    ax2.set_xscale("log")
    ax2.set_yscale("log")
    ax2.set_xlim(5e-3, 3)
    ax2.set_xlabel("$D$")
    ax2.set_ylabel(r"$|E|$ of the ejected member")
    ax2.legend(fontsize=7, loc="lower left")
    fs.save(fig, os.path.join(a.out, "fig_restricted"))


if __name__ == "__main__":
    main()
