"""A2: first_source round 3 (batch-2b report) from own per-dump tables (M1 runs).

Usage: python a2_round3.py <M1 run dir> [<M1 run dir> ...]
P12: c_+(K1) of eps = 1 at 64^3 with 1, 8 and 27 particles per cell (8: the wave-2 run).
P13: 128^3 (1 per cell) against 64^3 (1 and 8 per cell); rms of c(128,1)/c(64,8) - 1 and of
     c(64,8)/c(32,8) - 1 after shell crossing.
Times differ between runs by up to a step: the series of the reference run is carried to the
times of the other by a cubic spline in tau (dumps every 0.1).
(1 + eps^2) test: R(a) = dev(0.01)/dev(0.0025), Q(a) = [dev(eps=1)/2]/[dev(eps=0.3)/1.09],
dev = c_+/(s g) - 1, cubic spline through the double-precision dumps, a = 20, 30, 40, 50, 60.
P16': D = TT power at |m| >= 16 without the wave over that with it, at tau = 0.1, a = 2.3, 12.
"""
import json
import os
import sys

import numpy as np
from scipy.interpolate import CubicSpline

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vlib  # noqa: E402

OUT = os.environ.get("NRPIC_RUN_DIR", "/data/haiyangw/nrpic/scratch/B-emd-gw/tmp/a2")
os.makedirs(OUT, exist_ok=True)
DIRS = sys.argv[1:]


def load(name):
    for d in DIRS:
        p = os.path.join(d, f"m1_{name}.json")
        if os.path.exists(p):
            with open(p) as f:
                return json.load(f)["rows"]
    raise FileNotFoundError(name)


def series(name, kind="bin"):
    rr = sorted([r for r in load(name) if r["kind"] == kind and "error" not in r], key=lambda r: r["time"])
    out, last = [], None
    for r in rr:
        if last is None or r["time"] > last + 1e-9:
            out.append(r); last = r["time"]
    t = np.array([r["time"] for r in out]); c = np.array([r["K1_plus"][0] for r in out])
    return t, c, out


def compare(num, ref, kind="bin"):
    """relative difference c_num/c_ref - 1 at the times of num (ref by cubic spline)."""
    tn, cn, _ = series(num, kind); tr, cr, _ = series(ref, kind)
    m = (tn > 0) & (tn >= tr[1]) & (tn <= tr[-1])
    cri = CubicSpline(tr, cr)(tn[m])
    return vlib.a_of_tau(tn[m]), cn[m] / cri - 1.0, float(np.max(np.abs(tn[m][:, None] - tr[None, :]).min(axis=1)))


res = {}
cmp_ = {}
for lab, (n, r) in {"p1_vs_p27": ("e1_p1_n64", "e1_p27_n64"), "p8_vs_p27": ("eps1", "e1_p27_n64"),
                    "n128p1_vs_n64p8": ("e1_p1_n128", "eps1"), "n128p1_vs_n64p1": ("e1_p1_n128", "e1_p1_n64"),
                    "n64p8_vs_n32p8": ("eps1", "n32_eps1"), "rep_vs_first_bin": ("e1_rep", "eps1")}.items():
    try:
        a, d, toff = compare(n, r)
    except FileNotFoundError as e:
        res[lab] = {"missing": str(e)}
        continue
    cmp_[lab] = (a, d)
    out = {"max_time_offset_to_nearest_ref_dump": toff}
    for lo, hi in ((2, 40), (80, 140.5), (101, 140.5), (40, 80)):
        mm = (a >= lo) & (a <= hi)
        if mm.any():
            out[f"maxabs_{lo}_{hi}"] = float(np.max(np.abs(d[mm])))
            out[f"rms_{lo}_{hi}"] = float(np.sqrt(np.mean(d[mm] ** 2)))
    res[lab] = out

# (1 + eps^2) test on double-precision dumps
def dev_spline(name, kind, delta, eps):
    t, c, _ = series(name, kind)
    m = t > 0
    dv = c[m] / (vlib.s_static(delta, eps) * vlib.g_closed(t[m])) - 1.0
    return CubicSpline(t[m], dv)


def tau_of_a(a):
    return 2.0 * (np.sqrt(a) - 1.0)


A_T = (20, 30, 40, 50, 60)
eq = {}
for mesh, cases in {"n64": {"d01_e1": ("eps1", "rst"), "d01_e0p3": ("eps0p3", "rst"),
                            "d0025_e1": ("d0025_e1", "dbin"), "d0025_e0p3": ("d0025_e0p3", "dbin")},
                    "n32": {"d01_e1": ("n32_eps1", "rst"), "d01_e0p3": ("n32_eps0p3", "rst"),
                            "d0025_e1": ("n32_d0025_e1", "dbin"), "d0025_e0p3": ("n32_d0025_e0p3", "dbin")}}.items():
    try:
        sp = {k: dev_spline(nm, kind, 0.01 if k.startswith("d01") else 0.0025, 1.0 if k.endswith("e1") else 0.3)
              for k, (nm, kind) in cases.items()}
    except FileNotFoundError as e:
        eq[mesh] = {"missing": str(e)}
        continue
    dv = {k: {a0: float(s(tau_of_a(a0))) for a0 in A_T} for k, s in sp.items()}
    eq[mesh] = {"dev": dv,
                "R_e1": {a0: dv["d01_e1"][a0] / dv["d0025_e1"][a0] for a0 in A_T},
                "R_e0p3": {a0: dv["d01_e0p3"][a0] / dv["d0025_e0p3"][a0] for a0 in A_T},
                "Q_d0025": {a0: (dv["d0025_e1"][a0] / 2) / (dv["d0025_e0p3"][a0] / 1.09) for a0 in A_T},
                "Q_d01": {a0: (dv["d01_e1"][a0] / 2) / (dv["d01_e0p3"][a0] / 1.09) for a0 in A_T}}
res["eps2_test"] = eq

# P16': grid-scale TT power without the wave over that with it
def pick(name, kind, fe):
    for r in load(name):
        if r["kind"] == kind and r["file"].endswith(fe):
            return r
    raise KeyError(fe)


p16 = {}
for lab, (kind, fe) in {"tau0.1": ("bin", "cw.z4c.00001.bin"), "a2": ("dbin", "cw.z4cd.00001.bin"),
                        "a12": ("dbin", "cw.z4cd.00005.bin")}.items():
    try:
        nw, j3 = pick("nw64", kind, fe), pick("jit0p3", kind, fe)
    except (FileNotFoundError, KeyError) as e:
        p16[lab] = {"missing": str(e)}
        continue
    out = {"a": float(vlib.a_of_tau(nw["time"])), "t_nw": nw["time"], "t_j3": j3["time"]}
    for key in ("frac_ge16_round", "frac_ge16_floor"):
        out[f"D_{key}"] = (nw[key] * nw["rms_TT"] ** 2) / (j3[key] * j3["rms_TT"] ** 2)
    p16[lab] = out
res["p16"] = p16

with open(os.path.join(OUT, "a2_round3.json"), "w") as f:
    json.dump(res, f, indent=1, default=float)

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import figstyle  # noqa: E402,F401

fig, ax = plt.subplots(1, 2, figsize=(9, 3.6))
for lab, (a, d) in cmp_.items():
    ax[0].semilogy(a, np.abs(d) + 1e-16, lw=0.9, label=lab)
ax[0].axvline(101, color="0.6", lw=0.6, ls=":")
ax[0].set_xscale("log"); ax[0].set_xlabel("a"); ax[0].set_ylabel("|c/c_ref - 1| at K1"); ax[0].legend(fontsize=6)
ax[0].set_title("P12, P13: particle number and mesh, eps = 1", fontsize=9)
for mesh, mk in (("n64", "o"), ("n32", "s")):
    if "Q_d0025" in eq.get(mesh, {}):
        ax[1].plot(A_T, [eq[mesh]["Q_d0025"][a0] for a0 in A_T], mk + "-", label=f"Q, delta=0.0025, {mesh}")
        ax[1].plot(A_T, [eq[mesh]["R_e1"][a0] / 16 for a0 in A_T], mk + "--", label=f"R(eps=1)/16, {mesh}")
ax[1].axhspan(0.95, 1.05, color="0.9")
ax[1].set_xlabel("a"); ax[1].legend(fontsize=6); ax[1].set_title("(1 + eps^2) test", fontsize=9)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "a2_round3.png"), dpi=130)
print(json.dumps(res, indent=1, default=float))
