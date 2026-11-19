#!/usr/bin/env python3
"""Lead's independent check of the slow-roll ladder (E-stoch-inf, review of wave 2b).

Predictions LR3-LR5 of the owner JOURNAL (entry 2026-11-19T14:58Z). Written by the lead
without the ladder package's code: own reader of the NRSFDMP2 dump (layout of
tracks/core/interfaces/scalar_field_2.md section 4 on core/scalar-2), complex FFT,
amplitudes from core's twin python/nrpic/scalar_field.mode_alpha (the ladder used the
track's noise/ref/philox_ref.py), own Friedmann and Mukhanov-Sasaki integration with LSODA
(the ladder used DOP853), parameters read from the input deck copied into each run
directory.

    lead_check.py --l32 DIR_L32 --l64 DIR_L64 --l128 DIR_L128 --modefile FILE --out OUT

DIR_L32 holds L32p, L32m, L32ph, L32mh (run E-20261115-172636-ce98836); DIR_L64 and DIR_L128
hold L64p/L64m and L128p (run E-20261115-172625-416fec0).
"""
import argparse
import json
import os
import struct
import sys

import numpy as np
from scipy.integrate import solve_ivp

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "python"))
from nrpic.scalar_field import mode_alpha  # noqa: E402  (core's twin of the keys)

sys.path.insert(0, HERE)
import figstyle as fs  # noqa: E402

LBOX = 2.0 * np.pi


# ----------------------------------------------------------------------------- input
def deck(rundir):
    """Values of the input deck copied into the run directory (last occurrence wins)."""
    files = [f for f in os.listdir(rundir) if f.endswith(".athinput")]
    vals = {}
    with open(os.path.join(rundir, files[0])) as fp:
        for line in fp:
            line = line.split("#")[0].strip()
            if "=" in line:
                k, v = (s.strip() for s in line.split("=", 1))
                vals[k] = v
    return vals


def dumps(rundir):
    return sorted(os.path.join(rundir, f) for f in os.listdir(rundir)
                  if f.endswith(".dump") and ".sf." in f)


def read_dump(path, names):
    """Own reader: header, then per MeshBlock (level, lx1, lx2, lx3), six doubles of
    bounds, nvar arrays nx3 x nx2 x nx1 with the first index fastest."""
    with open(path, "rb") as f:
        if f.read(8) != b"NRSFDMP2":
            raise ValueError(path)
        nmb, nx1, nx2, nx3, nvar, cycle, _ = struct.unpack("<7q", f.read(56))
        (t,) = struct.unpack("<d", f.read(8))
        vn = [f.read(16).split(b"\0")[0].decode() for _ in range(nvar)]
        idx = [vn.index(n) for n in names]
        cells = nx1 * nx2 * nx3
        blocks = []
        for _ in range(nmb):
            lev, l1, l2, l3 = struct.unpack("<4q", f.read(32))
            f.read(48)
            start = f.tell()
            arrs = []
            for i in idx:
                f.seek(start + 8 * i * cells)
                arrs.append(np.fromfile(f, dtype="<f8", count=cells).reshape(nx3, nx2, nx1))
            f.seek(start + 8 * nvar * cells)
            blocks.append((l1, l2, l3, arrs))
    n1 = (max(b[0] for b in blocks) + 1) * nx1
    n2 = (max(b[1] for b in blocks) + 1) * nx2
    n3 = (max(b[2] for b in blocks) + 1) * nx3
    out = {n: np.empty((n3, n2, n1)) for n in names}
    for l1, l2, l3, arrs in blocks:
        for n, a in zip(names, arrs):
            out[n][l3 * nx3:(l3 + 1) * nx3, l2 * nx2:(l2 + 1) * nx2, l1 * nx1:(l1 + 1) * nx1] = a
    return t, cycle, out


def record(rundir):
    files = [f for f in os.listdir(rundir) if f.endswith(".sf.con.hst")]
    return np.loadtxt(os.path.join(rundir, files[0]))


# ----------------------------------------------------------------------------- modes
def hemisphere(nmax2):
    m = int(np.sqrt(nmax2)) + 1
    out = []
    for nx in range(0, m + 1):
        for ny in range(-m, m + 1):
            for nz in range(-m, m + 1):
                n2 = nx * nx + ny * ny + nz * nz
                if not (1 <= n2 <= nmax2):
                    continue
                if nx > 0 or (nx == 0 and ny > 0) or (nx == 0 and ny == 0 and nz > 0):
                    out.append((nx, ny, nz))
    return np.array(out, dtype=np.int64)


def coefficients(f, n):
    """c_n = N^-3 sum_x f(x) exp(-i n.x), x = (j + 1/2) h, with numpy's complex FFT of an
    array [z, y, x]."""
    N = f.shape[0]
    F = np.fft.fftn(f)
    c = F[n[:, 2] % N, n[:, 1] % N, n[:, 0] % N]
    return c * np.exp(-1j * np.pi * n.sum(axis=1) / N) / N**3


def curvature(fl, n):
    """R^NR_n of SPEC 7.1 P-c with the factors of SPEC 9 E6 (re-written from SPEC.md)."""
    k = np.sqrt((n * n).sum(axis=1))
    nh = n / k[:, None]
    phi_n = coefficients(fl["chi"], n) / (2.0 * fl["chi"].mean())
    comp = {"gxx": (0, 0, 1), "gyy": (1, 1, 1), "gzz": (2, 2, 1),
            "gxy": (0, 1, 2), "gxz": (0, 2, 2), "gyz": (1, 2, 2)}
    for name, (i, j, w) in comp.items():
        phi_n = phi_n + 0.25 * w * nh[:, i] * nh[:, j] * coefficients(fl[name], n)
    hb = -fl["K"].mean() / (3.0 * fl["alpha"].mean())
    return phi_n + hb / fl["Pi"].mean() * coefficients(fl["phi"], n)


# ------------------------------------------------------------------------ reference
class Reference:
    """Background and Mukhanov-Sasaki modes R'' + (3 H + d ln eps1/dt) R' + (k/a)^2 R = 0
    in code time (G = 1), LSODA, one shell at a time, scaled to unit initial modulus."""

    def __init__(self, mass, phi0, pi0, k, r0, dr0, t_end):
        self.m2 = mass * mass
        self.bg = solve_ivp(self._bg, (0.0, t_end), [phi0, pi0, 0.0], method="LSODA",
                            rtol=1e-12, atol=1e-14, dense_output=True)
        self.sols = []
        for kk, a0, b0 in zip(k, r0, dr0):
            s = abs(a0)
            y0 = [a0.real / s, a0.imag / s, b0.real / s, b0.imag / s]
            sol = solve_ivp(lambda t, y, kk=kk: self._ms(t, y, kk), (0.0, t_end), y0,
                            method="LSODA", rtol=1e-11, atol=1e-13, dense_output=True)
            self.sols.append((s, sol))

    def _hub(self, phi, pi):
        return np.sqrt(8.0 * np.pi / 3.0 * (0.5 * pi * pi + 0.5 * self.m2 * phi * phi))

    def _bg(self, t, y):
        phi, pi, _ = y
        h = self._hub(phi, pi)
        return [pi, -3.0 * h * pi - self.m2 * phi, h]

    def _ms(self, t, y, k):
        phi, pi, lna = self.bg.sol(t)
        h = self._hub(phi, pi)
        pidot = -3.0 * h * pi - self.m2 * phi
        hdot = -4.0 * np.pi * pi * pi
        dleps = 2.0 * pidot / pi - 2.0 * hdot / h
        fr = 3.0 * h + dleps
        w2 = (k / np.exp(lna))**2
        return [y[2], y[3], -fr * y[2] - w2 * y[0], -fr * y[3] - w2 * y[1]]

    def lna(self, t):
        return self.bg.sol(t)[2]

    def hub(self, t):
        phi, pi, _ = self.bg.sol(t)
        return self._hub(phi, pi)

    def mode(self, i, t):
        s, sol = self.sols[i]
        y = sol.sol(t)
        return s * (y[0] + 1j * y[1])

    def window(self, t, k, sharp, sigma):
        return 0.5 * (1.0 + np.tanh(sharp * np.log(sigma * np.exp(self.lna(t)) * self.hub(t) / k)))

    def crossing(self, k, t_end):
        from scipy.optimize import brentq
        f = lambda t: self.lna(t) + np.log(self.hub(t)) - np.log(k)  # noqa: E731
        return 0.0 if f(0.0) >= 0.0 else brentq(f, 0.0, t_end, xtol=1e-12)


def read_modefile(path):
    d = np.loadtxt(path)
    return d[:, 0].astype(int), d[:, 1] + 1j * d[:, 2], d[:, 3] + 1j * d[:, 4]


# -------------------------------------------------------------------------- checks
def a2_a3(rundir, modefile):
    p = deck(rundir)
    nmax2 = int(p["noise_nmax2"])
    seed = int(p["rng_seed"])
    scale = float(p["noise_mode_scale"])
    n = hemisphere(nmax2)
    n2 = (n * n).sum(axis=1)
    k = np.sqrt(n2.astype(float))
    alpha = mode_alpha(seed, 0, 0, n)
    files = dumps(rundir)
    t_end = read_dump(files[-1], ["phi"])[0] + 1e-9
    n2f, r0, dr0 = read_modefile(modefile)
    shells = np.unique(n2)
    pos = {s: i for i, s in enumerate(n2f)}
    sel = [pos[s] for s in shells]
    ref = Reference(float(p["mass"]), float(p["phi0"]), float(p["pi0"]),
                    np.sqrt(shells.astype(float)), r0[sel], dr0[sel], t_end)
    shell_of = np.searchsorted(shells, n2)
    names = ["chi", "phi", "K", "alpha", "Pi", "gxx", "gxy", "gxz", "gyy", "gyz", "gzz"]
    T, NN, RNR, RLIN = [], [], [], []
    for f in files:
        t, _, fl = read_dump(f, names)
        rnr = curvature(fl, n)
        rk = np.array([ref.mode(i, t) for i in range(shells.size)])[shell_of]
        w = ref.window(t, k, float(p["noise_sharpness"]), float(p["noise_sigma"]))
        rlin = scale * LBOX**-1.5 * w * rk * alpha
        T.append(t)
        NN.append(ref.lna(t))
        RNR.append(rnr)
        RLIN.append(rlin)
    T, NN, RNR, RLIN = map(np.array, (T, NN, RNR, RLIN))
    D = np.abs(RNR[-1] / RLIN[-1] - 1.0)
    low = k <= np.sqrt(nmax2) / 2.0
    # A3: modes with N_f - N_k >= 6; ratio Q between N_f and the first dump at N >= N_k + 4
    Nk = np.array([ref.lna(ref.crossing(kk, t_end))
                   for kk in np.sqrt(shells.astype(float))])[shell_of]
    Nf = NN[-1]
    a3 = np.where(Nf - Nk >= 6.0)[0]
    Q = np.abs(RNR)**2 / np.abs(RLIN)**2
    qrat, dr_nr, dr_lin = [], [], []
    for j in a3:
        i0 = int(np.argmax(NN >= Nk[j] + 4.0))
        qrat.append(Q[-1, j] / Q[i0, j] - 1.0)
        x = NN[i0:]
        dr_nr.append(np.polyfit(x, np.log(np.abs(RNR[i0:, j])**2), 1)[0])
        dr_lin.append(np.polyfit(x, np.log(np.abs(RLIN[i0:, j])**2), 1)[0])
    qrat, dr_nr, dr_lin = map(np.array, (qrat, dr_nr, dr_lin))
    res = dict(run=rundir, modes=int(n.shape[0]), t_last=float(T[-1]), N_last=float(Nf),
               A2_max_low=float(D[low].max()), A2_max_all=float(D.max()),
               A2_n2_of_max_all=int(n2[np.argmax(D)]),
               A2_pass=bool(D[low].max() < 0.02),
               A3_modes=int(a3.size), A3_max_abs_Qratio=float(np.abs(qrat).max()),
               A3_max_abs_drift_nr=float(np.abs(dr_nr).max()),
               A3_max_abs_drift_minus_ref=float(np.abs(dr_nr - dr_lin).max()),
               A3_pass=bool(np.abs(qrat).max() < 0.01 and np.abs(dr_nr).max() < 2.5e-3))
    return res, dict(k=k, D=D, low=low, NN=NN, Nk=Nk, a3=a3, qrat=qrat, dr_nr=dr_nr,
                     dr_lin=dr_lin, T=T, Dt=np.abs(RNR / np.where(RLIN == 0, np.nan, RLIN) - 1.0))


def h_parts(dir_p, dir_m, tmax):
    """rms of the odd part and of the even part (box mean removed) of H relative to <[H]>
    at each common dump with t <= tmax; also the box mean of the even part."""
    fp, fm = dumps(dir_p), dumps(dir_m)
    rec = record(dir_p)
    out = []
    for a, b in zip(fp, fm):
        ta, ca, xa = read_dump(a, ["H"])
        tb, cb, xb = read_dump(b, ["H"])
        if abs(ta - tb) > 1e-9 or ta > tmax + 1e-9:
            continue
        row = rec[np.argmin(np.abs(rec[:, 1] - ca))]
        hn = row[9]
        odd = 0.5 * (xa["H"] - xb["H"])
        even = 0.5 * (xa["H"] + xb["H"])
        out.append(dict(t=ta, efold=row[2], odd=float(np.sqrt((odd**2).mean()) / hn),
                        even=float(np.sqrt(((even - even.mean())**2).mean()) / hn),
                        even_mean=float(even.mean() / hn)))
    return out


def a1_record(rundir, t_end):
    p = deck(rundir)
    rec = record(rundir)
    ref = Reference(float(p["mass"]), float(p["phi0"]), float(p["pi0"]), [], [], [], t_end)
    t = rec[:, 0]
    y = ref.bg.sol(t)
    phi, pi = y[0], y[1]
    hub = ref._hub(phi, pi)
    dphi = np.abs(rec[:, 16] / phi - 1.0).max()
    dpi = np.abs(rec[:, 17] / pi - 1.0).max()
    dk = np.abs(rec[:, 18] / (-3.0 * hub) - 1.0).max()
    defold = np.abs(rec[:, 2] - y[2]).max()
    return dict(run=rundir, rows=int(rec.shape[0]), A1_phi=float(dphi), A1_Pi=float(dpi),
                A1_K=float(dk), efold_minus_lna=float(defold),
                H_record_last=float(rec[-1, 3]), M_record_last=float(rec[-1, 6]),
                t_last=float(rec[-1, 0]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--l32", required=True)
    ap.add_argument("--l64", required=True)
    ap.add_argument("--l128", required=True)
    ap.add_argument("--modefile", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    R = {}
    # LR3
    r3, d3 = a2_a3(os.path.join(a.l32, "L32p"), a.modefile)
    R["LR3_L32p"] = r3
    # LR4
    R["LR4"] = {name: a1_record(os.path.join(d, name), 8.6)
                for d, name in ((a.l32, "L32p"), (a.l64, "L64p"), (a.l128, "L128p"))}
    hl = [R["LR4"][x]["H_record_last"] for x in ("L32p", "L64p", "L128p")]
    R["LR4"]["H0_factors"] = [hl[0] / hl[1], hl[1] / hl[2]]
    # LR5
    full = h_parts(os.path.join(a.l32, "L32p"), os.path.join(a.l32, "L32m"), 4.0)
    half = h_parts(os.path.join(a.l32, "L32ph"), os.path.join(a.l32, "L32mh"), 4.0)
    p64 = h_parts(os.path.join(a.l64, "L64p"), os.path.join(a.l64, "L64m"), 8.5)
    rows = []
    t64 = np.array([x["t"] for x in p64])
    o64 = np.array([x["odd"] for x in p64])
    for f, h in zip(full, half):
        r = dict(t=f["t"], efold=f["efold"], odd_s1=f["odd"], even_s1=f["even"],
                 odd_half_factor=f["odd"] / h["odd"], even_half_factor=f["even"] / h["even"],
                 odd_over_even=f["odd"] / f["even"], even_mean_s1=f["even_mean"],
                 even_mean_half=h["even_mean"])
        if t64[0] <= f["t"] <= t64[-1]:
            o = np.exp(np.interp(f["t"], t64, np.log(o64)))
            r["odd_64_interp"] = float(o)
            r["order_32_64"] = float(np.log2(f["odd"] / o))
        rows.append(r)
    R["LR5_L32"] = rows
    R["LR5_L64"] = p64
    with open(os.path.join(a.out, "lead_check.json"), "w") as fp:
        json.dump(R, fp, indent=1, default=float)

    # figure
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH * 1.25, fs.FULL_WIDTH * 0.95))
    ax = np.asarray(ax)
    k, D, low = d3["k"], d3["D"], d3["low"]
    ax[0, 0].semilogy(k[~low], D[~low], ".", ms=3, label=r"$|n| > k_{\max}/2$")
    ax[0, 0].semilogy(k[low], D[low], ".", ms=4, label=r"$|n| \leq k_{\max}/2$ (A2)")
    ax[0, 0].axhline(0.02, ls="--", color="k", lw=1, label="threshold 0.02")
    ax[0, 0].set_xlabel(r"$|n|$")
    ax[0, 0].set_ylabel(r"$D_n$ at $N_f$")
    ax[0, 0].set_title("A2, L32p (own extraction)")
    ax[0, 0].legend(fontsize=8)
    ax[0, 1].semilogy(k[d3["a3"]], np.abs(d3["dr_nr"]), ".", ms=4,
                      label=r"$|d\ln|R^{NR}|^2/dN|$")
    ax[0, 1].semilogy(k[d3["a3"]], np.maximum(np.abs(d3["dr_nr"] - d3["dr_lin"]), 1e-12), ".",
                      ms=4, label="NR minus linear")
    ax[0, 1].semilogy(k[d3["a3"]], np.maximum(np.abs(d3["qrat"]), 1e-12), ".", ms=4,
                      label=r"$|Q(N_f)/Q(N_k+4)-1|$")
    ax[0, 1].axhline(2.5e-3, ls="--", color="k", lw=1, label="drift threshold")
    ax[0, 1].set_xlabel(r"$|n|$")
    ax[0, 1].set_title("A3 freezing, L32p")
    ax[0, 1].legend(fontsize=8)
    t = np.array([r["t"] for r in rows])
    ax[1, 0].semilogy(t, [r["odd_s1"] for r in rows], "o-", label="odd, s = 1")
    ax[1, 0].semilogy(t, [r["even_s1"] for r in rows], "s-", label="even (mean removed), s = 1")
    ax[1, 0].semilogy(t, [r["odd_s1"] / r["odd_half_factor"] for r in rows], "o--",
                      label="odd, s = 1/2")
    ax[1, 0].semilogy(t, [r["even_s1"] / r["even_half_factor"] for r in rows], "s--",
                      label="even, s = 1/2")
    ax[1, 0].semilogy(t64, o64, "^-", label="odd, s = 1, N = 64")
    ax[1, 0].set_xlabel("t (code units)")
    ax[1, 0].set_ylabel(r"rms part of $H$ / $\langle[H]\rangle$")
    ax[1, 0].set_title("A4/A5 parts of H")
    ax[1, 0].legend(fontsize=7)
    ax[1, 1].plot(t, [r["odd_half_factor"] for r in rows], "o-", label="odd halving factor")
    ax[1, 1].plot(t, [r["even_half_factor"] for r in rows], "s-", label="even halving factor")
    tt = [r["t"] for r in rows if "order_32_64" in r]
    ax[1, 1].plot(tt, [r["order_32_64"] for r in rows if "order_32_64" in r], "^-",
                  label="order of odd part, 32 to 64")
    for y in (2, 4, 6):
        ax[1, 1].axhline(y, color="0.6", lw=0.8, ls=":")
    ax[1, 1].set_xlabel("t (code units)")
    ax[1, 1].set_title("halving factors and order")
    ax[1, 1].legend(fontsize=8)
    fig.tight_layout()
    fs.save(fig, os.path.join(a.out, "fig_lead_check"))
    print(json.dumps({"LR3": R["LR3_L32p"], "LR4": R["LR4"]}, indent=1, default=float))


if __name__ == "__main__":
    main()
