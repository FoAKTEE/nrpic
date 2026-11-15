"""Lead's independent recomputation of the first_source scan (wave 2 review, R1-R6 of
../JOURNAL.md).

Reads the single-precision z4c dumps of the registered card and processor runs with
its own reader (athbin.py), computes the + amplitude of the conformal-metric perturbation
at K1 = (k, k, 0) and K2 = (k, -k, 0) by direct summation (no FFT, no gw_diag code),
the second-order reference s g(tau) from its own integration of
g'' + 2 Hc g' + |K|^2 (g - 1) = 0, and, for the null runs, the largest TT amplitude at
any nonzero wave vector with its own TT projector. The only numbers taken from the
helper's outputs are G_tot at K1 (to form the gauge-corrected difference), read from the
registered analysis JSON of runs B-20261115-180834-c77a132 and B-20261115-184650-2d155b6.

Usage: rv_first_source.py OUTDIR   (the run directories are fixed below)
"""
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
from scipy.integrate import solve_ivp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import athbin  # noqa: E402

S = "/data/haiyangw/nrpic/scratch/B-emd-gw"
C64A = f"{S}/B-20261115-164059-d802e82"   # eps = 0, 0.3, 0.1 (cards)
C64B = f"{S}/B-20261115-165353-b592d43"   # eps = 1 zero shift, Gamma driver (cards)
C32 = f"{S}/B-20261115-165525-f7c2004"    # all five at 32^3 (processors)
AN64 = f"{S}/B-20261115-180834-c77a132"   # helper analysis, eps = 1 pair, 64^3
AN32 = f"{S}/B-20261115-184650-2d155b6"   # helper analysis, 32^3
CASES = {
    "64/eps0": f"{C64A}/cw_eps0", "64/eps0p1": f"{C64A}/cw_eps0p1",
    "64/eps0p3": f"{C64A}/cw_eps0p3", "64/eps1": f"{C64B}/cw_eps1",
    "64/eps1_gd": f"{C64B}/cw_eps1_gd",
    "32/eps0": f"{C32}/cw_eps0", "32/eps0p1": f"{C32}/cw_eps0p1",
    "32/eps0p3": f"{C32}/cw_eps0p3", "32/eps1": f"{C32}/cw_eps1",
    "32/eps1_gd": f"{C32}/cw_eps1_gd",
}
EPS = {"eps0": 0.0, "eps0p1": 0.1, "eps0p3": 0.3, "eps1": 1.0, "eps1_gd": 1.0}
DELTA, L = 0.01, 4.0
k = 2 * np.pi / L
KK = np.sqrt(2.0) * k
GT = ["z4c_gxx", "z4c_gxy", "z4c_gxz", "z4c_gyy", "z4c_gyz", "z4c_gzz"]
IJ = [(0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)]


def s_static(eps):
    """s = -(5/6) phi_x phi_y, phi_i = -(3/2) (H/k)^2 delta r_i, H = 1 at tau = 0."""
    phi = -1.5 * (1.0 / k) ** 2 * DELTA
    return -(5.0 / 6.0) * phi * (eps * phi)


def g_of_tau(tau):
    def rhs(t, y):
        hc = 1.0 / (1.0 + t / 2.0)
        return [y[1], -2.0 * hc * y[1] - KK ** 2 * (y[0] - 1.0)]
    sol = solve_ivp(rhs, (0.0, float(np.max(tau)) + 1e-9), [0.0, 0.0], method="DOP853",
                    rtol=1e-12, atol=1e-14, dense_output=True)
    return sol.sol(tau)[0]


def tensor(d):
    h = np.zeros((3, 3) + d[GT[0]].shape)
    for name, (i, j) in zip(GT, IJ):
        v = d[name] - (1.0 if i == j else 0.0)
        h[i, j] = v
        h[j, i] = v
    return h


def max_tt(h, Lbox):
    """Largest TT + amplitude over nonzero wave vectors, own projector."""
    n = h.shape[2:]
    H = np.fft.rfftn(h, axes=(2, 3, 4))
    kz = np.fft.fftfreq(n[0]) * n[0]
    ky = np.fft.fftfreq(n[1]) * n[1]
    kx = np.fft.rfftfreq(n[2]) * n[2]
    KZ, KY, KX = np.meshgrid(kz, ky, kx, indexing="ij")
    kv = np.stack([KX, KY, KZ])
    kn = np.sqrt((kv ** 2).sum(0))
    kn[0, 0, 0] = 1.0
    kh = kv / kn
    P = np.eye(3)[:, :, None, None, None] - kh[:, None] * kh[None, :]
    PHP = np.einsum("ia...,ab...,bj...->ij...", P, H, P)
    tr = np.einsum("ab...,ba...->...", P, H)
    LH = PHP - 0.5 * P * tr
    amp = np.sqrt(2.0) * np.sqrt((np.abs(LH) ** 2).sum((0, 1))) / np.prod(n)
    amp[0, 0, 0] = 0.0
    # Nyquist planes carry no well-defined TT part; drop them
    for ax, m in enumerate(n):
        if m % 2 == 0:
            sl = [slice(None)] * 3
            sl[ax] = m // 2
            amp[tuple(sl)] = 0.0
    return float(amp.max())


def one(args):
    path, null = args
    d = athbin.read(path, want=GT + ["z4c_chi"])
    n1, n2, n3 = d["n"]
    dx = d["L"][0] / n1
    x = d["xmin"][0] + (np.arange(n1) + 0.5) * dx
    y = d["xmin"][1] + (np.arange(n2) + 0.5) * dx
    z = d["xmin"][2] + (np.arange(n3) + 0.5) * dx
    Z, Y, X = np.meshgrid(z, y, x, indexing="ij")
    h = tensor(d)
    out = {"time": d["time"], "cycle": d["cycle"], "file": os.path.basename(path),
           "a_chi": float(np.mean(d["z4c_chi"]) ** -0.5), "vsize": d["vsize"]}
    for lab, K, u in (("K1", (k, k, 0.0), (1, -1, 0)), ("K2", (k, -k, 0.0), (1, 1, 0))):
        u = np.array(u, float) / np.sqrt(2.0)
        ep = np.outer(u, u) - np.outer([0, 0, 1.0], [0, 0, 1.0])
        q = np.einsum("ij,ij...->...", ep, h)
        ph = K[0] * X + K[1] * Y + K[2] * Z
        N3 = q.size
        out[lab] = [float((q * np.cos(ph)).sum() / N3), float((q * np.sin(ph)).sum() / N3)]
    if null:
        out["max_tt"] = max_tt(h, d["L"])
        out["zdep"] = float(max(np.abs(h[i, j] - h[i, j].mean(0, keepdims=True)).max()
                                for i, j in IJ))
    return out


def series(case, path, stride_null=10):
    files = sorted(f for f in os.listdir(f"{path}/bin") if f.endswith(".bin") and ".z4c." in f)
    null = case.endswith("eps0")
    jobs = [(f"{path}/bin/{f}", null and (i % stride_null == 0 or i == len(files) - 1))
            for i, f in enumerate(files)]
    with ProcessPoolExecutor(int(os.environ.get("NWORK", "8"))) as ex:
        rows = list(ex.map(one, jobs, chunksize=4))
    return rows


def at_a(a, v, targets):
    out = {}
    for t in targets:
        i = int(np.argmin(np.abs(a - t)))
        out[str(t)] = float(v[i])
    return out


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else os.environ["NRPIC_RUN_DIR"]
    os.makedirs(outdir, exist_ok=True)
    data = {}
    for case, path in CASES.items():
        rows = series(case, path)
        data[case] = rows
        print(case, len(rows), "dumps", flush=True)
    res = {"s_eps1": s_static(1.0), "cases": {}}
    tgt = [2, 5, 10, 20, 40, 60, 80, 100, 140]
    for case, rows in data.items():
        tau = np.array([r["time"] for r in rows])
        a = (1 + tau / 2) ** 2
        g = g_of_tau(tau)
        eps = EPS[case.split("/")[1]]
        c1 = np.array([r["K1"][0] for r in rows])
        c2 = np.array([r["K2"][0] for r in rows])
        sin1 = np.array([r["K1"][1] for r in rows])
        ent = {"n_dumps": len(rows), "tau_end": float(tau[-1]), "a_end": float(a[-1]),
               "max_a_vs_a_chi": float(np.max(np.abs(a / np.array([r["a_chi"] for r in rows]) - 1))),
               "max_abs_sin_K1": float(np.max(np.abs(sin1)))}
        if eps > 0:
            s = s_static(eps)
            ref = s * g
            win = (a >= 2) & (a <= 10)
            ent["s"] = s
            ent["P2_K1_maxdev_a2_10"] = float(np.max(np.abs(c1[win] / ref[win] - 1)))
            ent["P2_K2_maxdev_a2_10"] = float(np.max(np.abs(-c2[win] / ref[win] - 1)))
            ent["dev_K1_at_a"] = at_a(a, c1 / ref - 1, tgt)
            ent["c_over_s_at_a"] = at_a(a, c1 / s, tgt)
            ent["max_c_over_s"] = float(np.max(c1 / s))
            ent["a_of_max_c_over_s"] = float(a[int(np.argmax(c1 / s))])
            # quasi-static check of the K1 mode: (dc/dtau)^2 / (|K|^2 c^2)
            dc = np.gradient(c1, tau)
            qs = dc ** 2 / (KK ** 2 * c1 ** 2 + 1e-300)
            ent["kin_over_grad_K1_at_a"] = at_a(a, qs, [4, 12, 40, 100, 140])
            ent["kin_over_grad_K1_max_a12_140"] = float(np.max(qs[a >= 12]))
        else:
            mt = [r["max_tt"] for r in rows if "max_tt" in r]
            zd = [r["zdep"] for r in rows if "zdep" in r]
            ent["null_max_tt"] = float(np.max(mt))
            ent["null_max_tt_last"] = float(mt[-1])
            ent["null_max_zdep"] = float(np.max(zd))
            ent["null_max_abs_c_K1"] = float(np.max(np.abs(c1)))
        res["cases"][case] = ent
    # linearity (P3)
    for N in ("64", "32"):
        tau = np.array([r["time"] for r in data[f"{N}/eps0p1"]])
        a = (1 + tau / 2) ** 2
        c01 = np.array([r["K1"][0] for r in data[f"{N}/eps0p1"]]) / 0.1
        c03 = np.array([r["K1"][0] for r in data[f"{N}/eps0p3"]]) / 0.3
        c10 = np.array([r["K1"][0] for r in data[f"{N}/eps1"]]) / 1.0
        win = (a >= 2) & (a <= 10)
        res[f"P3_{N}"] = {"max_rel_0p3_vs_0p1_a2_10": float(np.max(np.abs(c03[win] / c01[win] - 1))),
                          "max_rel_1_vs_0p1_a2_10": float(np.max(np.abs(c10[win] / c01[win] - 1)))}
    # second gauge (P6c), raw from this script, corrected with the helper's G_tot(K1)
    s1 = s_static(1.0)
    for N, an in (("64", AN64), ("32", AN32)):
        zs, gd = data[f"{N}/eps1"], data[f"{N}/eps1_gd"]
        assert [r["file"] for r in zs] == [r["file"] for r in gd]
        tau = np.array([r["time"] for r in zs])
        tau_gd = np.array([r["time"] for r in gd])
        a = (1 + tau / 2) ** 2
        raw = np.array([r["K1"][0] for r in zs]) - np.array([r["K1"][0] for r in gd])
        hj = {}
        for cs in ("cw_eps1", "cw_eps1_gd"):
            rows = json.load(open(f"{an}/{cs}.json"))["rows"]
            hj[cs] = {r["file"]: r for r in rows if r.get("kind") == "bin"}
        G_zs = np.array([hj["cw_eps1"][r["file"]]["Gtot_K1_plus"][0] for r in zs])
        G_gd = np.array([hj["cw_eps1_gd"][r["file"]]["Gtot_K1_plus"][0] for r in gd])
        their_c = np.array([hj["cw_eps1"][r["file"]]["h_K1_plus"][0] for r in zs])
        mine_c = np.array([r["K1"][0] for r in zs])
        corr = (mine_c - G_zs) - (np.array([r["K1"][0] for r in gd]) - G_gd)
        sel = (np.abs(raw) > 1e-3 * abs(s1)) & (a <= 140)
        res[f"P6_{N}"] = {
            "max_dtau_between_gauges": float(np.max(np.abs(tau - tau_gd))),
            "raw_pct_of_s_at_a": {kk: 100 * v for kk, v in at_a(a, np.abs(raw) / abs(s1), [5, 10, 20, 40, 60]).items()},
            "corrected_pct_of_s_at_a": {kk: 100 * v for kk, v in at_a(a, np.abs(corr) / abs(s1), [5, 10, 20, 40, 60]).items()},
            "median_corr_over_raw": float(np.median(np.abs(corr[sel]) / np.abs(raw[sel]))),
            "frac_dumps_used": float(sel.mean()),
            "max_rel_mine_vs_helper_c_K1": float(np.max(np.abs(mine_c - their_c)) / abs(s1)),
        }
        res[f"P6_{N}_series"] = {"a": a.tolist(), "raw": raw.tolist(), "corr": corr.tolist()}
    # resolution (P8)
    res["P8"] = {}
    for cs in ("eps0p1", "eps0p3", "eps1", "eps1_gd"):
        r64, r32 = data[f"64/{cs}"], data[f"32/{cs}"]
        t64 = np.array([r["time"] for r in r64]); t32 = np.array([r["time"] for r in r32])
        c64 = np.array([r["K1"][0] for r in r64])
        c32 = np.interp(t64, t32, np.array([r["K1"][0] for r in r32]))
        a = (1 + t64 / 2) ** 2
        rel = np.abs(c32 / c64 - 1)
        res["P8"][cs] = {"rel_at_a": at_a(a, rel, [5, 10, 20, 40, 60, 80, 100]),
                         "max_rel_a5_40": float(np.max(rel[(a >= 5) & (a <= 40)])),
                         "max_rel_a40_80": float(np.max(rel[(a > 40) & (a <= 80)])),
                         "max_dtau_grid": float(np.max(np.abs(np.interp(t64, t32, t32) - t64)))}
    with open(f"{outdir}/rv_first_source.json", "w") as f:
        json.dump({"summary": res, "series": {c: rows for c, rows in data.items()}}, f)
    print(json.dumps(res, indent=1, default=str)[:20000])


if __name__ == "__main__":
    main()
