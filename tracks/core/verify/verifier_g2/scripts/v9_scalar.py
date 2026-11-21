#!/usr/bin/env python3
"""V9: Klein-Gordon plane wave of the scalar field (test 1a): frequency and spatial order.

Own reader of <basename>.sf.NNNNN.dump (layout at the top of
athenak/src/scalar_field/scalar_field_io.cpp: "NRSFDMP1"; int64 nmb, nx1, nx2, nx3,
nvar, cycle, nnoise; double time; per MeshBlock int64 level, lx1, lx2, lx3; double
x1min..x3max; nvar arrays of nx3*nx2*nx1 doubles, first index fastest; phi first).
Analytic case for the reader: the dump at t = 0 must hold cos(k.x) sampled at the cell
centres (checked, number reported).
Frequency: Fourier coefficient c(t) of phi at k = 2 pi (1, 1, 0) (box 1) fitted by two
travelling waves A exp(-i W t) + B exp(i W t) (the initial momentum need not be that of
the discrete frequency); the plain phase slope is reported too. Exact omega = sqrt(m^2 + |k|^2), m = 5. Own stencil
frequencies omega_h from the symbols of the centred second derivative of orders 2, 4, 6
(nghost 2, 3, 4).

usage: v9_scalar.py RUNDIR OUTDIR
"""
import glob
import json
import os
import struct
import sys

import numpy as np

M_KG = 5.0
KVEC = 2 * np.pi * np.array([1.0, 1.0, 0.0])


def read_dump(path):
    with open(path, "rb") as fh:
        b = fh.read()
    assert b[:8] == b"NRSFDMP1", path
    nmb, nx1, nx2, nx3, nvar, cycle, nnoise = struct.unpack_from("<7q", b, 8)
    (time,) = struct.unpack_from("<d", b, 64)
    off = 72
    blocks = []
    n = nx1 * nx2 * nx3
    for _ in range(nmb):
        lev, l1, l2, l3 = struct.unpack_from("<4q", b, off)
        off += 32
        ext = struct.unpack_from("<6d", b, off)
        off += 48
        arr = np.frombuffer(b, dtype="<f8", count=nvar * n, offset=off).reshape(nvar, nx3, nx2, nx1)
        off += 8 * nvar * n
        blocks.append((ext, arr))
    assert off == len(b), (off, len(b))
    return time, cycle, (nx1, nx2, nx3), blocks


def coeff(blocks, nx):
    """Fourier coefficient of phi at KVEC and the max deviation from cos(k.x) (t=0 check)."""
    s, cnt = 0j, 0
    for ext, arr in blocks:
        x = ext[0] + (np.arange(nx[0]) + 0.5) * (ext[1] - ext[0]) / nx[0]
        y = ext[2] + (np.arange(nx[1]) + 0.5) * (ext[3] - ext[2]) / nx[1]
        z = ext[4] + (np.arange(nx[2]) + 0.5) * (ext[5] - ext[4]) / nx[2]
        Z, Y, X = np.meshgrid(z, y, x, indexing="ij")
        ph = KVEC[0] * X + KVEC[1] * Y + KVEC[2] * Z
        s += np.sum(arr[0] * np.exp(-1j * ph))
        cnt += arr[0].size
    return s / cnt


def cosdev(blocks, nx):
    dev = 0.0
    for ext, arr in blocks:
        x = ext[0] + (np.arange(nx[0]) + 0.5) * (ext[1] - ext[0]) / nx[0]
        y = ext[2] + (np.arange(nx[1]) + 0.5) * (ext[3] - ext[2]) / nx[1]
        z = ext[4] + (np.arange(nx[2]) + 0.5) * (ext[5] - ext[4]) / nx[2]
        Z, Y, X = np.meshgrid(z, y, x, indexing="ij")
        dev = max(dev, float(np.max(np.abs(arr[0] - np.cos(KVEC[0] * X + KVEC[1] * Y)))))
    return dev


def kh2(k, dx, order):
    th = k * dx
    if order == 2:
        sym = (2 * np.cos(th) - 2) / dx ** 2
    elif order == 4:
        sym = (-2 * np.cos(2 * th) + 32 * np.cos(th) - 30) / (12 * dx ** 2)
    else:
        sym = (4 * np.cos(3 * th) - 54 * np.cos(2 * th) + 540 * np.cos(th) - 490) / (180 * dx ** 2)
    return -sym


def main():
    rd, outdir = sys.argv[1:3]
    os.makedirs(outdir, exist_ok=True)
    omega = np.sqrt(M_KG ** 2 + KVEC @ KVEC)
    res = {"omega_exact": float(omega), "cases": {}}
    for ng in (2, 3, 4):
        for n in (8, 12, 16, 24):
            case = f"a_ng{ng}_n{n}"
            files = sorted(glob.glob(os.path.join(rd, case, "*.sf.*.dump")))
            ts, cs = [], []
            for i, f in enumerate(files):
                t, cyc, nx, blocks = read_dump(f)
                if i == 0:
                    dev0 = cosdev(blocks, nx)
                    ntot = len(blocks) * nx[0] * nx[1] * nx[2]
                ts.append(t)
                cs.append(coeff(blocks, nx))
            ts, cs = np.array(ts), np.array(cs)
            phase = np.unwrap(np.angle(cs))
            p = np.polyfit(ts, phase, 1)
            om_phase = abs(p[0])
            # two travelling waves: c(t) = A exp(-i W t) + B exp(+i W t); linear LSQ in A, B
            # for given W, W found by minimising the residual near the phase-fit value
            def resid(W):
                G = np.stack([np.exp(-1j * W * ts), np.exp(1j * W * ts)], axis=1)
                sol, *_ = np.linalg.lstsq(G, cs, rcond=None)
                return float(np.sum(np.abs(G @ sol - cs) ** 2)), sol
            from scipy.optimize import minimize_scalar
            r = minimize_scalar(lambda W: resid(W)[0], bracket=(om_phase * (1 - 1e-3), om_phase, om_phase * (1 + 1e-3)),
                                tol=1e-14)
            om = float(r.x)
            rr, AB = resid(om)
            dx = 1.0 / round(ntot ** (1 / 3)) if False else 1.0 / n
            om_h = np.sqrt(M_KG ** 2 + 2 * kh2(2 * np.pi, dx, 2 * (ng - 1)))
            res["cases"][case] = {"n": n, "ng": ng, "ndumps": len(files), "t_last": float(ts[-1]),
                                  "t0_reader_check_max_dev_from_cos": dev0, "ncells": int(ntot),
                                  "omega_meas": float(om), "omega_phase_only": float(om_phase), "omega_h_own": float(om_h),
                                  "two_wave_resid": rr, "B_over_A": float(abs(AB[1] / AB[0])),
                                  "rel_meas_minus_h": float(om / om_h - 1),
                                  "err_vs_exact": float(abs(om - omega)),
                                  "phase_fit_resid_max": float(np.max(np.abs(np.polyval(p, ts) - phase)))}
    orders = {}
    for ng in (2, 3, 4):
        ns = np.array([8, 12, 16, 24])
        e = np.array([res["cases"][f"a_ng{ng}_n{n}"]["err_vs_exact"] for n in ns])
        pair = [float(np.log(e[i] / e[i + 1]) / np.log(ns[i + 1] / ns[i])) for i in range(3)]
        slope = float(-np.polyfit(np.log(ns), np.log(e), 1)[0])
        orders[ng] = {"pairwise": pair, "lsq_all": slope, "errors": [float(x) for x in e]}
    res["orders"] = orders
    with open(os.path.join(outdir, "v9_scalar.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps(orders, indent=1))
    for k, v in res["cases"].items():
        print(k, f"{v['omega_meas']:.12f} {v['omega_h_own']:.12f} {v['rel_meas_minus_h']:.3e} dev0={v['t0_reader_check_max_dev_from_cos']:.1e}")

    import matplotlib
    matplotlib.use("Agg")
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
    ns = np.array([8, 12, 16, 24])
    for i, ng in enumerate((2, 3, 4)):
        e = np.array(orders[ng]["errors"])
        axs[0].loglog(ns, e, "o-", color=fs.SERIES[i], lw=1, ms=3, label=f"nghost {ng}: {orders[ng]['lsq_all']:.3f}")
        axs[0].loglog(ns, e[0] * (ns / ns[0]) ** (-2 * (ng - 1)), color=fs.SERIES[i], lw=0.8, ls="--")
        r = [res["cases"][f"a_ng{ng}_n{n}"]["rel_meas_minus_h"] for n in ns]
        axs[1].plot(ns, r, "o-", color=fs.SERIES[i], lw=1, ms=3, label=f"nghost {ng}")
    axs[0].set_xlabel("cells per box length")
    axs[0].set_ylabel(r"$|\omega_{\rm meas}-\omega|$")
    axs[0].legend(fontsize=7, title="order (fit)", title_fontsize=7)
    axs[1].set_xlabel("cells per box length")
    axs[1].set_ylabel(r"$\omega_{\rm meas}/\omega_h - 1$ (own symbols)")
    axs[1].legend(fontsize=7)
    fig.suptitle("V9: Klein-Gordon plane wave, run core-20261115-150004-3629622 (dashed: orders 2, 4, 6)", fontsize=8)
    fig.tight_layout()
    fs.save(fig, os.path.join(outdir, "fig_v9_scalar"))


if __name__ == "__main__":
    main()
