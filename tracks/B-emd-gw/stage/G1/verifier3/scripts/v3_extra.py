#!/usr/bin/env python3
"""V3 supplement of verifier3 (JOURNAL entry 7): where the TT and Weyl diagnostics differ.

1. Test F: |Z_TT - Z_Psi4(spectral)| / |Z_ex| against time, with the prediction
   delta_disp |sin(w t)|, delta_disp = w_semi-discrete / w - 1 from the symbol of AthenaK's
   sixth-order second derivative (coefficients 1/90, -3/20, 3/2, -49/18, ...): the initial data
   are the continuum wave, so they excite a backward discrete mode of relative amplitude
   delta/2; TT sees forward + backward, Psi_4 along +n only the forward part.
2. Test X: |Z_TT - Z_Weyl(spectral)| / |Z_ex| against time, next to the background error
   |a_num/a_ex - 1| (the Weyl inversion uses calH = -alpha K/3 of the numerical background).
3. Test F, last dump of N = 16 and 64: where the non-TT part of gt - delta lives
   (k = 0, the wave vector +-K, everything else), to read the 'nonTT_frac' column of V3.
Inputs: V3_DUMPS (v3_dumps.json of run B-20261121-025826-80973e3) and the raw F dumps.
Writes $NRPIC_RUN_DIR/v3_extra.json and v3_F_diag_diff.png/pdf, v3_X_diag_diff.png/pdf.
"""
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import diag  # noqa: E402
import exact  # noqa: E402
import figstyle as fs  # noqa: E402

OUT = os.environ.get("NRPIC_RUN_DIR", os.path.join(HERE, "..", "results", "tmp_v3x"))
os.makedirs(OUT, exist_ok=True)
D = json.load(open(os.environ["V3_DUMPS"]))
dumps = D["dumps"]
SCR = "/data/haiyangw/nrpic/scratch/B-emd-gw"


def cx(p):
    return complex(p[0], p[1])


def sym6(theta):
    """-h^2 times the symbol of the sixth-order centred second derivative."""
    return (49.0 / 18.0 - 3.0 * np.cos(theta) + 0.3 * np.cos(2 * theta)
            - (2.0 / 90.0) * np.cos(3 * theta))


res = {"F": {}, "X": {}, "F_nonTT": {}}
fw = exact.FlatWave()
TSF = {}
for N in (16, 32, 48, 64):
    S = [d for d in dumps if d["case"] == "F" and d["N"] == N]
    t = np.array([d["t"] for d in S])
    h = 1.0 / N
    th = fw.K * h
    w_sd = np.sqrt(np.sum(sym6(th))) / h           # sym6 = h^2 k_eff^2 per direction (~theta^2)
    delta = w_sd / fw.w - 1.0
    rows = {}
    for p in (0, 1):
        Zex = np.array([fw.complex_amp(tt)[p] for tt in t])
        dW = np.array([abs(cx(d["TT"][p]) - cx(d["Wsp"][p])) for d in S]) / np.abs(Zex)
        rows[p] = dW
    pred = np.abs(delta * np.sin(fw.w * t))
    res["F"][N] = {"delta_disp": float(delta), "theta^6/1120": float(th[0] ** 6 / 1120),
                   "max_t |TT-Wsp| +": float(rows[0].max()), "max_t |TT-Wsp| x": float(rows[1].max()),
                   "max_t |(|TT-Wsp| +) - pred|": float(np.max(np.abs(rows[0] - pred))),
                   "ratio max/|delta|": float(rows[0].max() / abs(delta))}
    TSF[N] = (t, rows, pred)

TSX = {}
for N in (16, 32, 48, 64):
    S = [d for d in dumps if d["case"] == "X" and d["N"] == N]
    t = np.array([d["t"] for d in S])
    eps = D["eps"]["X"]
    xw = exact.ExpandingWave(eps_p=eps[0], eps_x=eps[1])
    T, dT = xw.mode.T(t), xw.mode.dT(t)
    rows = {}
    for p in (0, 1):
        Zex = eps[p] * (T + 1j * dT / xw.kn)
        zt = np.array([cx(d["TT_h"][p]).real + 1j * cx(d["TT_hd"][p]).real / xw.kn for d in S])
        zw = np.array([cx(d["Wsp_h"][p]).real + 1j * cx(d["Wsp_hd"][p]).real / xw.kn for d in S])
        rows[p] = np.abs(zt - zw) / np.abs(Zex)
    a_num = np.array([d["bg"]["chi_mean"] for d in S]) ** -0.5
    bg = np.abs(a_num / exact.eds_a(t) - 1)
    calH_err = np.abs(np.array([d["calH_num"] for d in S]) / exact.eds_calH(t) - 1)
    res["X"][N] = {"max_t |TT-Wsp| +": float(rows[0].max()), "max_t |TT-Wsp| x": float(rows[1].max()),
                   "max_t |a/a_ex-1|": float(bg.max()), "max_t |calH/calH_ex-1|": float(calH_err.max())}
    TSX[N] = (t, rows, bg, calH_err)

# where the non-TT part of gt - delta lives (F, last dump)
runs = {16: ("B-20261119-142016-ee73a03", "N16"), 64: ("B-20261119-142124-feb2daf", "flatN64")}
EYE = np.eye(3)[:, :, None, None, None]
for N, (run, sub) in runs.items():
    f = sorted(glob.glob(f"{SCR}/{run}/{sub}/bin/*.z4c.*.bin"))[-1]
    d = diag.read_bin(f)
    g = d["grid"]
    gt = diag.sym_from(d["vars"], "z4c_g")
    full = gt - EYE
    hTT = diag.tt_project(full, g)
    rest = full - hTT
    F = np.fft.fftn(rest, axes=(-3, -2, -1)) / np.prod(g.n)
    P = np.sum(np.abs(F) ** 2, axis=(0, 1))
    tot = P.sum()
    m = [(1, 1, 1), (-1, -1, -1)]
    Pk = sum(P[tuple(v % n for v, n in zip(mm, g.n))] for mm in m)
    m2 = [(2, 2, 2), (-2, -2, -2)]
    P2k = sum(P[tuple(v % n for v, n in zip(mm, g.n))] for mm in m2)
    F0 = F[:, :, 0, 0, 0].real
    res["F_nonTT"][N] = {"file": os.path.relpath(f, SCR), "t": d["time"],
                         "rms(gt-delta-hTT)": float(np.sqrt(np.mean(rest ** 2))),
                         "rms(hTT)": float(np.sqrt(np.mean(hTT ** 2))),
                         "power fraction k=0": float(P[0, 0, 0] / tot),
                         "power fraction +-K": float(Pk / tot), "power fraction +-2K": float(P2k / tot),
                         "k=0 mean of gt-delta (3x3)": F0.tolist(),
                         "k=0 trace": float(np.trace(F0))}

with open(os.path.join(OUT, "v3_extra.json"), "w") as fh:
    json.dump(res, fh, indent=1)
print(json.dumps(res, indent=1))

fs.use_style()
import matplotlib.pyplot as plt  # noqa: E402

NCOL = {16: fs.PAL["blue"], 32: fs.PAL["red"], 48: fs.PAL["yellow"], 64: fs.PAL["green"]}
fig, ax = plt.subplots(figsize=(fs.COLUMN_WIDTH * 1.6, 3.4))
fig.subplots_adjust(left=0.14, right=0.97, bottom=0.15, top=0.96)
for N, (t, rows, pred) in TSF.items():
    per = t * np.sqrt(3.0)
    ax.semilogy(per, rows[0], "o", ms=3, color=NCOL[N], label=f"N={N}, $+$")
    ax.semilogy(per, rows[1], "x", ms=4, color=NCOL[N], label=f"N={N}, $\\times$")
    tt = np.linspace(0, t[-1], 600)
    ax.semilogy(tt * np.sqrt(3.0), np.abs(res["F"][N]["delta_disp"] * np.sin(fw.w * tt)) + 1e-16,
                color=NCOL[N], lw=0.8)
ax.set_ylim(1e-11, 1e-5)
ax.set_xlabel("t [periods]", labelpad=-2)
ax.set_ylabel(r"$|Z_{\rm TT}-Z_{\Psi_4}|/|Z_{\rm ex}|$")
ax.legend(loc="lower right", ncol=4, fontsize=6)
ax.text(0.02, 0.95, r"lines: $|\delta_{\rm disp}\,\sin\omega t|$ (symbol of the FD6 $\partial^2$)",
        transform=ax.transAxes, fontsize=7, va="top")
fs.save(fig, os.path.join(OUT, "v3_F_diag_diff"))

fig, ax = plt.subplots(figsize=(fs.COLUMN_WIDTH * 1.6, 3.4))
fig.subplots_adjust(left=0.14, right=0.97, bottom=0.15, top=0.96)
for N, (t, rows, bg, cerr) in TSX.items():
    ax.semilogy(t[1:], rows[0][1:], "-", color=NCOL[N], label=f"TT$-$Weyl, N={N}")
    ax.semilogy(t[1:], rows[1][1:], "--", color=NCOL[N])
    ax.semilogy(t[1:], cerr[1:], ":", color=NCOL[N], lw=1.0)
ax.set_xlabel("conformal time t", labelpad=-2)
ax.set_ylabel("relative difference")
ax.legend(loc="lower right", fontsize=6, ncol=2)
ax.text(0.02, 0.95, r"solid $+$, dashed $\times$; dotted: $|\mathcal{H}_{\rm num}/\mathcal{H}-1|$",
        transform=ax.transAxes, fontsize=7, va="top")
fs.save(fig, os.path.join(OUT, "v3_X_diag_diff"))
