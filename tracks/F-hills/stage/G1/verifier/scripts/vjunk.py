"""Criterion (iii) of G1: t = 0 Hamiltonian residual of the three-puncture data (K1) and the junk
energy of P1's data at its four spheres (J0 analytic test, J1), with readers of this package.

Run: python tracks/F-hills/stage/G1/verifier/scripts/vjunk.py --out <dir>
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vread  # noqa: E402
import figstyle  # noqa: E402

SCR = "/data/haiyangw/nrpic/scratch/F-hills"
E2 = os.path.join(SCR, "F-20261115-173547-a02af7d")
SMOKE = os.path.join(SCR, "F-20261115-174602-c6879fe", "P1smoke")
P1 = os.path.join(SCR, "F-20261119-150017-b45ec5f")
M_ADM = 1.25


def ffi_news(t, psi, omega0):
    """dh/dt from psi4 = d2h/dt2 by fixed-frequency integration (the mean removed first)."""
    n = len(t)
    dt = t[1] - t[0]
    x = psi - psi.mean()
    f = np.fft.fft(x)
    w = 2 * np.pi * np.fft.fftfreq(n, dt)
    weff = np.where(np.abs(w) < omega0, np.sign(w) * omega0, w)
    weff[weff == 0] = omega0
    return np.fft.ifft(f / (-1j * weff))


def read_modes(rundir, r):
    tag = f"{r:04d}"
    pr = os.path.join(rundir, "waveforms", f"rpsi4_real_{tag}.txt")
    pi = os.path.join(rundir, "waveforms", f"rpsi4_imag_{tag}.txt")
    with open(pr) as f:
        head = f.readline().split()[1:]
    labels = [h.split(":")[1] for h in head]
    ra, _ = vread.read_numeric(pr)
    ia, _ = vread.read_numeric(pi)
    lr = {round(row[0], 6): row for row in ra}
    li = {round(row[0], 6): row for row in ia}
    ts = sorted(set(lr) & set(li))
    R = np.array([lr[k] for k in ts])
    I = np.array([li[k] for k in ts])
    modes = {}
    for c, lab in enumerate(labels[1:], start=1):
        l = int(lab[0])
        m = int(lab[1:])
        modes[(l, m)] = R[:, c] + 1j * I[:, c]
    return np.array(ts), modes


def rstar(r, M):
    return r + 2 * M * np.log(r / (2 * M) - 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    out = ap.parse_args().out
    os.makedirs(out, exist_ok=True)
    res = {}

    # ---------------- K1: t = 0 Hamiltonian residual ----------------
    k1 = {}
    for case in ("approx_L9", "approx_L10", "approx_L11", "none_L9", "none_L10", "none_L11", "plain_L10"):
        h, _ = vread.read_hst(os.path.join(E2, case, [f for f in os.listdir(os.path.join(E2, case)) if f.endswith(".hst")][0]))
        k = int(np.argmin(np.abs(h["time"])))
        k1[case] = {"t": float(h["time"][k]), "rmsH": float(np.sqrt(h["H-norm2"][k] / h["Volume"][k])),
                    "H-norm2": float(h["H-norm2"][k])}
    sm = [f for f in os.listdir(SMOKE) if f.endswith(".hst")]
    if sm:
        h, _ = vread.read_hst(os.path.join(SMOKE, sm[0]))
        k1["card_smoke_P1"] = {"t": float(h["time"][0]), "rmsH": float(np.sqrt(h["H-norm2"][0] / h["Volume"][0]))}
    for c in ("approx", "none"):
        a, b, d = (k1[f"{c}_L{L}"]["rmsH"] for L in (9, 10, 11))
        k1[f"order_{c}_L9_L10"] = float(np.log2(a / b))
        k1[f"order_{c}_L10_L11"] = float(np.log2(b / d))
    k1["none_over_approx_L11"] = k1["none_L11"]["rmsH"] / k1["approx_L11"]["rmsH"]
    k1["none_over_approx_L10"] = k1["none_L10"]["rmsH"] / k1["approx_L10"]["rmsH"]
    k1["plain_over_approx_L10"] = k1["plain_L10"]["rmsH"] / k1["approx_L10"]["rmsH"]
    res["K1"] = k1

    # ---------------- J0: analytic test of the energy pipeline ----------------
    dt = 0.25
    t = np.arange(0, 200, dt)
    A, t0, s, w = 1e-3, 100.0, 12.0, 0.5
    tf = np.arange(0, 200, 0.001)
    def h_of(tt):
        return A * np.exp(-((tt - t0) / s) ** 2) * np.exp(-1j * w * tt)
    hf = h_of(tf)
    hdot = np.gradient(hf, tf)
    E_exact = float(np.trapezoid(np.abs(hdot) ** 2, tf) / (16 * np.pi))
    # psi4 sampled analytically
    g = lambda tt: np.exp(-((tt - t0) / s) ** 2)
    def psi_of(tt):
        a = -2 * (tt - t0) / s ** 2
        gp = a * g(tt)
        gpp = (a * a - 2 / s ** 2) * g(tt)
        e = np.exp(-1j * w * tt)
        return A * (gpp - 2j * w * gp - w * w * g(tt)) * e
    news = ffi_news(t, psi_of(t), 0.2)
    E_ffi = float(np.trapezoid(np.abs(news) ** 2, t) / (16 * np.pi))
    res["J0"] = {"E_exact": E_exact, "E_ffi": E_ffi, "rel": E_ffi / E_exact - 1,
                 "pass": bool(abs(E_ffi / E_exact - 1) < 0.01)}

    # ---------------- J1: junk of P1's data at the four spheres ----------------
    j1 = {}
    curves = {}
    for r in (40, 48, 70, 90):
        ts, modes = read_modes(P1, r)
        u = ts - rstar(r, M_ADM)
        rec = u <= 14.0
        dEdu = np.zeros(rec.sum())
        El = {}
        for (l, m), psi in modes.items():
            nw = ffi_news(ts[rec], psi[rec], 0.2)
            p = np.abs(nw) ** 2 / (16 * np.pi)
            dEdu += p
            win = (u[rec] >= -35) & (u[rec] <= 6)
            El[l] = El.get(l, 0.0) + float(np.trapezoid(p[win], u[rec][win]))
        win = (u[rec] >= -35) & (u[rec] <= 6)
        E = float(np.trapezoid(dEdu[win], u[rec][win]))
        # alternatives: u = t - r, and omega_0 = 0.1, 0.3
        alt = {}
        for name, uu, om in (("u=t-r", ts - r, 0.2), ("omega0=0.1", u, 0.1), ("omega0=0.3", u, 0.3)):
            rc = uu <= 14.0
            de = np.zeros(rc.sum())
            for (l, m), psi in modes.items():
                de += np.abs(ffi_news(ts[rc], psi[rc], om)) ** 2 / (16 * np.pi)
            wn = (uu[rc] >= -35) & (uu[rc] <= 6)
            alt[name] = float(np.trapezoid(de[wn], uu[rc][wn]))
        j1[str(r)] = {"E_window": E, "share_l_ge_4": sum(v for l, v in El.items() if l >= 4) / E,
                      "E_by_l": El, "alternatives": alt, "n_samples_record": int(rec.sum()),
                      "u_first": float(u[0])}
        curves[r] = (u[rec], dEdu)
    vals = [j1[str(r)]["E_window"] for r in (40, 48, 70, 90)]
    j1["max_over_min"] = max(vals) / min(vals)
    res["J1"] = j1

    figstyle.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(8, 3.2))
    fig.subplots_adjust(left=0.1, right=0.98, bottom=0.16, top=0.95, wspace=0.3)
    cols = figstyle.SERIES
    for c, r in zip(cols, (40, 48, 70, 90)):
        uu, de = curves[r]
        ax[0].semilogy(uu, de + 1e-14, color=c, lw=1.0, label=f"r = {r} M")
    ax[0].axvspan(-35, 6, color="grey", alpha=0.1)
    ax[0].set_xlabel("u = t - r* [M]"); ax[0].set_ylabel("dE/du (all l <= 8)"); ax[0].legend(fontsize=8)
    ax[0].set_ylim(1e-11, None)
    for c, r in zip(cols, (40, 48, 70, 90)):
        El = j1[str(r)]["E_by_l"]
        ls_ = sorted(El)
        ax[1].semilogy(ls_, [El[l] for l in ls_], "o-", color=c, lw=1.0, ms=3, label=f"r = {r} M")
    ax[1].set_xlabel("l"); ax[1].set_ylabel("E in window [-35, 6] M"); ax[1].legend(fontsize=8)
    figstyle.save(fig, os.path.join(out, "fig_v_junk"))
    with open(os.path.join(out, "vjunk.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)
    print(json.dumps(res, default=float)[:2500])


if __name__ == "__main__":
    main()
