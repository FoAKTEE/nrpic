"""P2: own second-order prediction of the box-mode strain of the jittered nulls (ledger rows
201-203, 206) from the initial data, and its comparison with the measured strain (M1a).

Derivation (note Eqs. (3)-(4), checked here on the crossed waves): the quasi-static solution
of (1/2) h'' + Hc h' - (1/2) lap h = (10/3) TT[d Phi d Phi] is
    h(K) = (20 / (3 K^2)) TT[d Phi d Phi](K)
for growing-mode potentials Phi, times the junk response g(tau) of conformally flat data.
Phi on the initial slice from the conformal factor: psi^4 = 1 - 2 Phi. The wave's potential
is that of the unjittered data (jit0: the same wave, same tool); the noise potential is the
difference. The noise has no peculiar velocity, so its growing part is 3/5 of it (the rest
decays as a^(-5/2)); this script keeps the growing part only (response g for both the cross
term and the noise-noise term), which differs from the track's prediction by the decaying
parts (the track's g_cross, g_nn): a difference of order (2/5) a^(-5/2) <~ 0.06 at a >= 3.
Checks: the crossed-wave coefficient -(5/6) phi_x phi_y is recovered by the same code on an
analytic potential.
Usage: python p2_null_pred.py <M1a run dir>
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vlib  # noqa: E402

SC = "/data/haiyangw/nrpic/scratch/B-emd-gw"
IC = f"{SC}/B-20261119-141216-9c98929"
OUT = os.environ.get("NRPIC_RUN_DIR", f"{SC}/tmp/p2")
os.makedirs(OUT, exist_ok=True)
M1A = sys.argv[1]
N, L = 64, 4.0


def read_psi(p):
    raw = np.fromfile(p, np.uint8)
    assert raw[:8].tobytes() == b"NRCOSMO1"
    n = raw[8:32].view(np.int64)
    nc = int(np.prod(n))
    arr = raw[32:32 + 72 * nc].view(np.float64).reshape(9, int(n[2]), int(n[1]), int(n[0]))
    return arr[0]


d = {"n": (N, N, N), "L": np.array([L, L, L]), "xmin": np.zeros(3), "dx": L / N}
g = vlib.Grid(d)


def grad(f):
    F = np.fft.fftn(f)
    return np.array([np.fft.ifftn(1j * g.k[a] * F).real for a in range(3)])


def static_strain(phi_a, phi_b):
    """(20/(3K^2)) TT[sym(d phi_a d phi_b)] as full-FFT coefficients."""
    ga, gb = grad(phi_a), grad(phi_b)
    S = 0.5 * (ga[:, None] * gb[None, :] + gb[:, None] * ga[None, :])
    T = g.tt(g.fft_t(S))
    with np.errstate(divide="ignore", invalid="ignore"):
        fac = np.where(g.k2 > 0, 20.0 / (3.0 * g.k2), 0.0)
    return T * fac


def box_amps(T):
    A = {nm: g.amp_from_fft(T, m) for nm, (m, _, _) in vlib.BASIS.items()}
    return {nm: v[0] for nm, v in vlib.pol(A).items()}       # complex + amplitude (c - i s)


res = {}
# check on the analytic crossed waves
x = (np.arange(N) + 0.5) * L / N
Z, Y, X = np.meshgrid(x, x, x, indexing="ij")
k = 2 * np.pi / L
px = -1.5 * (1.0 / k) ** 2 * 0.01
phi = px * np.sin(k * X) + 0.3 * px * np.sin(k * Y)
hp = box_amps(static_strain(phi, phi))
res["check_crossed"] = {"K1": [hp["K1"].real, hp["K1"].imag], "expected_K1": vlib.s_static(0.01, 0.3),
                        "K2": [hp["K2"].real, hp["K2"].imag], "expected_K2": -vlib.s_static(0.01, 0.3)}

phi0 = (1.0 - read_psi(f"{IC}/jit0/fields.bin") ** 4) / 2.0
res["phi_wave_check"] = {"max_abs_phi_jit0": float(np.abs(phi0).max()), "phi_x_expected": abs(px)}
pred = {}
for case in ("jit0p3", "jit0p1"):
    phin = (1.0 - read_psi(f"{IC}/{case}/fields.bin") ** 4) / 2.0 - phi0
    cross = static_strain(phi0, 0.6 * phin) * 2.0          # 2 sym(d Phi_w d (3/5 Phi_n))
    nn = static_strain(0.6 * phin, 0.6 * phin)
    tot = cross + nn
    pred[case] = {"cross": box_amps(cross), "nn": box_amps(nn), "tot": box_amps(tot),
                  "rms_static_all": float(np.sqrt(g.power(tot).sum())),
                  "rms_static_cross": float(np.sqrt(g.power(cross).sum())),
                  "rms_phin": float(np.sqrt(np.mean(phin ** 2)))}
    rows = json.load(open(os.path.join(M1A, f"m1_{case}.json")))["rows"]
    rr = sorted([r for r in rows if r["kind"] == "bin" and "error" not in r], key=lambda r: r["time"])
    t = np.array([r["time"] for r in rr]); a = vlib.a_of_tau(t)
    gg = vlib.g_closed(t)
    out = {"rms_static_all": pred[case]["rms_static_all"], "rms_phin": pred[case]["rms_phin"]}
    for K in ("K1", "K2"):
        c = np.array([r[f"{K}_plus"][0] + 1j * r[f"{K}_plus"][1] for r in rr])
        p = pred[case]["tot"][K] * gg
        m = (a >= 3) & (a <= 20)
        ratio = np.abs(c[m]) / np.abs(p[m])
        ph = np.angle(c[m] / p[m])
        out[K] = {"ratio_min_med_max": [float(ratio.min()), float(np.median(ratio)), float(ratio.max())],
                  "maxabs_phase": float(np.abs(ph).max()),
                  "pred_static": [pred[case]["tot"][K].real, pred[case]["tot"][K].imag],
                  "cross_static": [pred[case]["cross"][K].real, pred[case]["cross"][K].imag],
                  "nn_static": [pred[case]["nn"][K].real, pred[case]["nn"][K].imag]}
        out[K]["series"] = {"a": a.tolist(), "meas": [abs(v) for v in c], "pred": [abs(v) for v in pred[case]["tot"][K] * gg]}
    rms = np.array([r["rms_TT"] for r in rr])
    m = (a >= 3) & (a <= 20)
    out["rms_TT_over_static_estimate_3_20"] = [float(rms[m].min() / pred[case]["rms_static_all"]),
                                               float(rms[m].max() / pred[case]["rms_static_all"])]
    res[case] = out
r3 = np.array(res["jit0p3"]["K1"]["series"]["pred"]); r1 = np.array(res["jit0p1"]["K1"]["series"]["pred"])
res["pred_ratio_K1_jit3_over_jit1"] = float(np.median(r3[1:] / r1[1:]))
with open(os.path.join(OUT, "p2_null_pred.json"), "w") as f:
    json.dump(res, f, indent=1, default=lambda v: [v.real, v.imag] if isinstance(v, complex) else float(v))

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import figstyle  # noqa: E402,F401

fig, ax = plt.subplots(1, 2, figsize=(9, 3.6))
for i, K in enumerate(("K1", "K2")):
    for case, col in (("jit0p3", "C0"), ("jit0p1", "C1")):
        s = res[case][K]["series"]
        ax[i].semilogy(s["a"], s["meas"], color=col, lw=1, label=f"{case} measured")
        ax[i].semilogy(s["a"], s["pred"], color=col, lw=1, ls="--", label=f"{case} own prediction (growing part)")
    ax[i].axvspan(3, 20, color="0.93")
    ax[i].set_xscale("log"); ax[i].set_xlabel("a"); ax[i].set_ylabel(f"|h_+({K})|"); ax[i].legend(fontsize=6)
    ax[i].set_title(f"rows 201-203: jittered null at {K}", fontsize=9)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "p2_null_pred.png"), dpi=130)
print(json.dumps({k: (v if k not in ("jit0p3", "jit0p1") else {kk: (vv if kk not in ("K1", "K2") else {x: y for x, y in vv.items() if x != "series"}) for kk, vv in v.items()}) for k, v in res.items()}, indent=1, default=lambda v: [v.real, v.imag] if isinstance(v, complex) else float(v)))
