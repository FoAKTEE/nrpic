"""Verifier of B-emd-gw, claim C7: the Fourier-TT diagnostic and Psi_4 of package gw_diag
agree on linear waves. Uses the package's functions as the object under test; the fields
and the expected values are built here.

    python3 v5_gwdiag.py [OUTDIR or - for $NRPIC_RUN_DIR] [V4_RUNDIR]

(a) plane waves h = A_+ e_+ sin(phi) + A_x e_x sin(phi + d), phi = k.x - w t, on a flat
    background, for lattice directions (1,0,0), (1,2,0), (1,1,1), (0,1,2) and three
    polarization states; K_ij = -(1/2) d_t gamma_ij (unit lapse). Expected: h_+, h_x read
    back exactly (TT projection of an exact TT field) and Psi_4 = d_t^2 h_+ - i d_t^2 h_x
    (the convention documented in gwdiag/weyl.py), the backward partner zero.
(b) the same wave in rescaled coordinates, gamma = a^2 (delta + h), a = 3, w = |k|/a:
    Psi_4 = d_t^2 h_+ - i d_t^2 h_x with the proper frequency.
(c) gauge modes of flat space: gamma_ij = d_i X^a d_j X^a with X = x + xi(x) (exactly
    flat), K = 0, amplitudes eps = 1e-4 and 1e-3: TT part must scale as eps^2, E and B
    vanish to the derivative error (spectral derivatives); and a slicing mode
    K_ij = -d_i d_j f on flat gamma: TT of K at first order zero, B zero.
(d) the AthenaK x-wave at 64 cells after 10 crossings (run of v4_lw_runs.sh, if given):
    h_+ from the TT projection and Psi_4 from E, B against the exact wave.

Writes OUTDIR/v5_gwdiag.json and OUTDIR/v5_gwdiag.png.
"""
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..", "..", "..", "..", "..")
sys.path.insert(0, os.path.join(ROOT, "tracks", "B-emd-gw", "gw_diag"))
sys.path.insert(0, os.path.join(ROOT, "python"))
from gwdiag import Grid, tt, weyl  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

A0 = 1.0e-6


def wave(grid, m, Ap, Ax, d, a=1.0, t=0.0):
    X, Y, Z = grid.mesh()
    k = 2*np.pi*np.array(m, float)/np.array(grid.L)
    kk = np.linalg.norm(k)
    w = kk/a
    kh = (k/kk).reshape(3, 1, 1, 1)
    ep, ex, _, _ = tt.pol_basis(kh)
    ph = k[0]*X + k[1]*Y + k[2]*Z - w*t
    hp, hx = Ap*np.sin(ph), Ax*np.sin(ph + d)
    hpd, hxd = -w*Ap*np.cos(ph), -w*Ax*np.cos(ph + d)
    hpdd, hxdd = -w*w*hp, -w*w*hx
    h = ep*hp + ex*hx
    hd = ep*hpd + ex*hxd
    I3 = np.eye(3)[:, :, None, None, None]
    gamma = a*a*(I3 + h)
    K = -0.5*a*a*hd
    return gamma, K, hp, hx, hpdd - 1j*hxdd, k/kk


def rms(x):
    return float(np.sqrt(np.mean(np.abs(x)**2)))


def plane_tests():
    out = []
    grid = Grid((24, 24, 24), (1.0, 1.0, 1.0), (0.0, 0.0, 0.0))
    for a in (1.0, 3.0):
        for m in ((1, 0, 0), (1, 2, 0), (1, 1, 1), (0, 1, 2)):
            for (Ap, Ax, d) in ((A0, 0.0, 0.0), (0.0, A0, 0.0), (0.6*A0, 0.8*A0, 1.0)):
                gamma, K, hp, hx, p4, nh = wave(grid, m, Ap, Ax, d, a=a)
                hTT, hdTT, chib = tt.tt_from_adm(gamma, K, grid)
                hp_n, hx_n = tt.polarization_along(hTT, nh)
                row = {"a": a, "m": m, "Ap": Ap, "Ax": Ax,
                       "tt_err_over_A": (rms(hp_n - hp) + rms(hx_n - hx))/A0}
                scale = rms(p4)
                for order in (6, "spectral"):
                    E, B = weyl.electric_magnetic(gamma, K, grid, order=order)
                    P4 = weyl.psi4(E, B, gamma, grid, direction=nh)
                    P0 = weyl.psi0_like(E, B, gamma, grid, nh)
                    row[f"psi4_err_{order}"] = rms(P4 - p4)/scale
                    row[f"psi4_backward_{order}"] = rms(P0)/scale
                out.append(row)
    return out


def gauge_tests():
    grid = Grid((32, 32, 32), (1.0, 1.0, 1.0), (0.0, 0.0, 0.0))
    X, Y, Z = grid.mesh()
    rng = np.random.default_rng(7)
    modes = [(rng.integers(-2, 3, 3), rng.normal(size=3), rng.uniform(0, 2*np.pi))
             for _ in range(4)]
    res = {}
    D = weyl.Deriv(grid, "spectral")
    for eps in (1e-4, 1e-3):
        xi = np.zeros((3,) + X.shape)
        for m, amp, p in modes:
            if not np.any(m):
                continue
            k = 2*np.pi*m
            xi += eps*amp[:, None, None, None]*np.sin(k[0]*X + k[1]*Y + k[2]*Z + p)[None]
        J = np.empty((3, 3) + X.shape)               # J[a, i] = d_i X^a
        for a_ in range(3):
            for i in range(3):
                J[a_, i] = (1.0 if a_ == i else 0.0) + D.d1(xi[a_], i)
        gamma = np.einsum("ai...,aj...->ij...", J, J)
        K = np.zeros_like(gamma)
        hTT, _, _ = tt.tt_from_adm(gamma, K, grid)
        E, B = weyl.electric_magnetic(gamma, K, grid, order="spectral")
        h = gamma - np.eye(3)[:, :, None, None, None]
        res[f"spatial_eps{eps:g}"] = {"rms_h": rms(h), "rms_hTT": rms(hTT),
                                      "rms_E": rms(E), "rms_B": rms(B)}
        # slicing mode: K_ij = -d_i d_j f, flat gamma
        f = sum(eps*amp[0]*np.sin(2*np.pi*(m[0]*X + m[1]*Y + m[2]*Z) + p)
                for m, amp, p in modes if np.any(m))
        I3 = np.eye(3)[:, :, None, None, None]
        Ks = np.empty((3, 3) + X.shape)
        for i in range(3):
            for j in range(3):
                Ks[i, j] = -D.d2(f, i, j)
        hTT2, hdTT2, _ = tt.tt_from_adm(I3 + 0*Ks, Ks, grid)
        E2, B2 = weyl.electric_magnetic(I3 + 0*Ks, Ks, grid, order="spectral")
        res[f"slicing_eps{eps:g}"] = {"rms_K": rms(Ks), "rms_KTT": rms(hdTT2)/2,
                                      "rms_E": rms(E2), "rms_B": rms(B2)}
    for kind in ("spatial", "slicing"):
        a1, a2 = res[f"{kind}_eps0.0001"], res[f"{kind}_eps0.001"]
        key = "rms_hTT" if kind == "spatial" else "rms_KTT"
        res[f"{kind}_TT_ratio_eps10x"] = a2[key]/a1[key] if a1[key] > 0 else None
    return res


def read_tab(path):
    with open(path) as fh:
        head = fh.readline()
        cols = fh.readline().lstrip("#").split()
    t = float(re.search(r"time=([0-9.eE+-]+)", head).group(1))
    d = np.loadtxt(path)
    return t, {c: d[:, i] for i, c in enumerate(cols)}


def athenak_test(rundir):
    import glob
    f = sorted(glob.glob(os.path.join(rundir, "x_N64", "tab", "*.tab")))[-1]
    t, d = read_tab(f)
    n = d["x1v"].size
    nyz = 4
    grid = Grid((n, nyz, nyz), (1.0, 4.0/n, 4.0/n), (0.0, 0.0, 0.0))
    names = [["gxx", "gxy", "gxz"], ["gxy", "gyy", "gyz"], ["gxz", "gyz", "gzz"]]

    def field(c):
        return np.broadcast_to(d["z4c_" + c][None, None, :], grid.shape).copy()
    gt = np.array([[field(names[i][j]) for j in range(3)] for i in range(3)])
    At = np.array([[field(names[i][j].replace("g", "A")) for j in range(3)] for i in range(3)])
    chi = field("chi")
    Kh = field("Khat")
    gamma = gt/chi
    K = At/chi + gamma*Kh/3.0
    hTT, hdTT = tt.tt_from_conformal(gt, At, grid)
    hp, hx = tt.polarization_along(hTT, (1, 0, 0))
    E, B = weyl.electric_magnetic(gamma, K, grid, order=6)
    P4 = weyl.psi4(E, B, gamma, grid, direction=(1, 0, 0))
    X, _, _ = grid.mesh()
    ph = 2*np.pi*(X - t)
    # pol_basis((1,0,0)): u = theta-hat = (0,0,-1), v = (0,1,0): e_+ = zz - yy
    hp_ex = A0*np.sin(ph)
    p4_ex = -(2*np.pi)**2*hp_ex
    return {"t": t, "file": f, "hplus_rms_err_over_A": rms(hp - hp_ex)/A0,
            "hcross_rms_over_A": rms(hx)/A0,
            "psi4_rms_err_over_scale": rms(P4 - p4_ex)/rms(p4_ex),
            "psi4_over_minus_k2_hplus_TT_rms_dev": rms(P4.real/(-(2*np.pi)**2) - hp)/A0,
            "x": X[0, 0].tolist(), "hp": hp[0, 0].tolist(), "hp_ex": hp_ex[0, 0].tolist(),
            "p4": P4.real[0, 0].tolist(), "p4_ex": p4_ex[0, 0].tolist()}


def main():
    out = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] != "-" else os.environ["NRPIC_RUN_DIR"]
    v4 = sys.argv[2] if len(sys.argv) > 2 else None
    os.makedirs(out, exist_ok=True)
    res = {"plane": plane_tests(), "gauge": gauge_tests()}
    pl = res["plane"]
    res["plane_max_tt_err"] = max(r["tt_err_over_A"] for r in pl)
    for o in ("6", "spectral"):
        res[f"plane_max_psi4_err_{o}"] = max(r[f"psi4_err_{o}"] for r in pl)
        res[f"plane_max_psi4_backward_{o}"] = max(r[f"psi4_backward_{o}"] for r in pl)
    if v4:
        res["athenak"] = athenak_test(v4)
    with open(os.path.join(out, "v5_gwdiag.json"), "w") as fh:
        json.dump(res, fh, indent=1, default=lambda o: list(o) if isinstance(o, tuple) else
                  (o.tolist() if hasattr(o, "tolist") else str(o)))
    short = {k: v for k, v in res.items() if k not in ("plane", "athenak")}
    print(json.dumps(short, indent=1, default=str))
    if v4:
        print({k: v for k, v in res["athenak"].items() if not isinstance(v, list)})

    fs.use_style()
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.2))
    ax = fig.add_axes([0.08, 0.15, 0.38, 0.78])
    lab = [f"{r['m']}" + ("" if r["a"] == 1 else ", a=3") for r in pl]
    xs = np.arange(len(pl))
    ax.semilogy(xs, [max(r["tt_err_over_A"], 1e-17) for r in pl], "o",
                color=fs.PAL["blue"], ms=3.5, label="TT read-back / $A$")
    ax.semilogy(xs, [r["psi4_err_6"] for r in pl], "s", color=fs.PAL["red"], ms=3.5,
                label=r"$\Psi_4$, 6th-order FD")
    ax.semilogy(xs, [r["psi4_err_spectral"] for r in pl], "^", color=fs.PAL["yellow"],
                ms=3.5, label=r"$\Psi_4$, spectral")
    ax.semilogy(xs, [max(r["psi4_backward_spectral"], 1e-17) for r in pl], "x",
                color="k", ms=3.5, label=r"backward partner, spectral")
    ax.set_xticks(xs[::3])
    ax.set_xticklabels(lab[::3], rotation=30, fontsize=7)
    ax.set_ylabel("relative rms error")
    ax.set_ylim(1e-17, 1)
    ax.legend(loc="center left", fontsize=7)
    ax2 = fig.add_axes([0.58, 0.15, 0.40, 0.78])
    if v4:
        r = res["athenak"]
        x = np.array(r["x"])
        ax2.plot(x, np.array(r["hp_ex"])/A0, **fs.GUIDE, label=r"exact $h_+/A$")
        ax2.plot(x, np.array(r["hp"])/A0, "o", color=fs.PAL["blue"], ms=3,
                 label=r"TT projection, AthenaK $N=64$")
        ax2.plot(x, np.array(r["p4"])/(-(2*np.pi)**2*A0), "s", color=fs.PAL["red"], ms=2,
                 label=r"$-\Psi_4/(k^2 A)$, AthenaK")
        ax2.set_xlabel("$x$")
        ax2.set_ylabel(f"$t = {r['t']:.2f}$")
        ax2.legend(loc="lower left", fontsize=7)
    fs.save(fig, os.path.join(out, "v5_gwdiag"))


if __name__ == "__main__":
    main()
