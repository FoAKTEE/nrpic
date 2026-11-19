"""G1 verifier, C18 part 4: the expanding-ball comparison of wave 2 (runs_ball/), recomputed
from the AthenaK trajectories with my own reader and my own exact solution.

Inputs per run: <seg>/ball.traj.bin (records of 8: t, tag, x^i, u_i) and ball.trajmet.bin
(records of 17: t, tag, alpha, beta^i, gamma_ij, tau, E, S_i; coord/INTERFACES/diagnostics.md
section 6). Areal radius of a particle R = r sqrt(gamma_perp), gamma_perp = (tr gamma -
n.gamma.n)/2 (spherical symmetry); proper time tau = int alpha/W dt, W^2 = 1 + gamma^ij u_i u_j
(compared with the code's own tau column). Exact solution: the cycloid of each particle's
shell, m and E rebuilt from the data-set table as in v_ledger.py.
Usage: python v_ball.py [--out DIR]
"""
import argparse
import json
import math
import os

import numpy as np

import vcommon as vc
from vcommon import fs

ap = argparse.ArgumentParser()
ap.add_argument("--out", default=None)
a = ap.parse_args()
OUT = a.out or vc.outdir("ball")
os.makedirs(OUT, exist_ok=True)
L = vc.Ledger("ball")
TAU_TA = 16.894

RUNS = {  # label: (run id, segment, gauge, dx)
    "sr1_M": ("A-emd-pbh-20261115-155056-ec1b816", "sr1_n128", "sr1", 1.0),
    "sr2_M": ("A-emd-pbh-20261115-155056-ec1b816", "sr2_n128", "sr2", 1.0),
    "sr1_M2": ("A-emd-pbh-20261115-153843-7172b66", "sr1", "sr1", 0.5),
    "sr2_M2": ("A-emd-pbh-20261115-153845-7172b66", "sr2", "sr2", 0.5),
    "sr1_M4": ("A-emd-pbh-20261115-164539-0b18e84", "sr1_n256_L32", "sr1", 0.25),
    "sr2_M4": ("A-emd-pbh-20261115-164541-0b18e84", "sr2_n256_L32", "sr2", 0.25),
}

# ------------------------------------------------------------------ exact shells from the table
DS = "A-emd-pbh-20261115-130609-947c898"
tab = np.loadtxt(L.inp(DS, "expball_smooth_tophat_HRb0p5_dc1_R10p3_R20p75_w0p1875.tab", check=False))
rb, u_, KL, KT, _, _ = tab.T
h = rb[1] - rb[0]
psi = 1 + u_
Rtab = psi ** 2 * rb


def d1(f):
    g = np.gradient(f, h, edge_order=2)
    g[2:-2] = (f[:-4] - 8 * f[1:-3] + 8 * f[3:-1] - f[4:]) / (12 * h)
    return g


Etab = 0.5 * (d1(Rtab) ** 2 / psi ** 4 - 1)
vtab = -KT * Rtab
mtab = 0.5 * Rtab * (vtab ** 2 - 2 * Etab)
for k in (1, 2):
    Etab[k] = Etab[3] * (Rtab[k] / Rtab[3]) ** 2
    mtab[k] = mtab[3] * (Rtab[k] / Rtab[3]) ** 3
mtab[0] = 0.0
TI = 32.0 / 3.0


def shell(r0):
    m = np.interp(r0, rb, mtab); E = np.interp(r0, rb, Etab); Ri = np.interp(r0, rb, Rtab)
    A = m / (-2 * E); B = m / (-2 * E) ** 1.5
    eta0 = np.arccos(np.clip(1 - Ri / A, -1, 1))
    tb = B * (eta0 - np.sin(eta0))
    return dict(m=m, E=E, Ri=Ri, A=A, B=B, eta0=eta0, tb=tb, tau_ta=B * np.pi - tb, Rmax=2 * A)


def R_exact(sh, tau):
    tgt = (tau + sh["tb"]) / sh["B"]
    x = np.array(np.broadcast_to(sh["eta0"], np.shape(tgt)), dtype=float)
    for _ in range(80):
        f = x - np.sin(x) - tgt
        x = np.clip(x - f / np.maximum(1 - np.cos(x), 1e-14), 1e-12, 2 * np.pi)
    return sh["A"] * (1 - np.cos(x))


# ------------------------------------------------------------------ reader
def read(run, seg):
    p1 = L.inp(run, f"{seg}/ball.traj.bin")
    p2 = L.inp(run, f"{seg}/ball.trajmet.bin")
    tr = np.fromfile(p1).reshape(-1, 8)
    tm = np.fromfile(p2).reshape(-1, 17)
    assert np.array_equal(tr[:, :2], tm[:, :2]), "traj and trajmet records differ"
    ts = np.unique(tr[:, 0])
    ntag = int(tr[:, 1].max()) + 1
    # keep only times with a complete set of records (a run may be cut mid-output)
    keep = []
    rows = {}
    order = np.lexsort((tr[:, 1], tr[:, 0]))
    tr, tm = tr[order], tm[order]
    starts = np.searchsorted(tr[:, 0], ts)
    ends = np.searchsorted(tr[:, 0], ts, side="right")
    good = [(s, e) for s, e in zip(starts, ends) if e - s == ntag]
    idx = np.concatenate([np.arange(s, e) for s, e in good])
    tr, tm = tr[idx].reshape(len(good), ntag, 8), tm[idx].reshape(len(good), ntag, 17)
    return tr, tm


def analyse(label, run, seg, gauge, dx):
    tr, tm = read(run, seg)
    t = tr[:, 0, 0]
    x = tr[:, :, 2:5]; uu = tr[:, :, 5:8]
    al = tm[:, :, 2]; g = tm[:, :, 6:12]; tau_code = tm[:, :, 12]
    fin = np.all(np.isfinite(tr.reshape(len(t), -1)), 1) & np.all(np.isfinite(tm.reshape(len(t), -1)), 1)
    nf = int(np.argmin(fin)) if not fin.all() else len(t)
    t_last = float(t[nf - 1])
    # also flag the first time a tracked areal radius jumps (field blow-up): |R| > 1e3 or not finite
    r = np.linalg.norm(x, axis=2)
    n = x / np.maximum(r, 1e-300)[..., None]
    gxx, gxy, gxz, gyy, gyz, gzz = (g[..., k] for k in range(6))
    tr_g = gxx + gyy + gzz
    ngn = (n[..., 0] ** 2 * gxx + n[..., 1] ** 2 * gyy + n[..., 2] ** 2 * gzz
           + 2 * (n[..., 0] * n[..., 1] * gxy + n[..., 0] * n[..., 2] * gxz + n[..., 1] * n[..., 2] * gyz))
    R = r * np.sqrt(np.maximum(0.5 * (tr_g - ngn), 0))
    # proper time: int alpha/W dt
    det = gxx * (gyy * gzz - gyz ** 2) - gxy * (gxy * gzz - gyz * gxz) + gxz * (gxy * gyz - gyy * gxz)
    ixx = (gyy * gzz - gyz ** 2) / det; iyy = (gxx * gzz - gxz ** 2) / det; izz = (gxx * gyy - gxy ** 2) / det
    ixy = (gxz * gyz - gxy * gzz) / det; ixz = (gxy * gyz - gxz * gyy) / det; iyz = (gxy * gxz - gxx * gyz) / det
    uu2 = (ixx * uu[..., 0] ** 2 + iyy * uu[..., 1] ** 2 + izz * uu[..., 2] ** 2
           + 2 * (ixy * uu[..., 0] * uu[..., 1] + ixz * uu[..., 0] * uu[..., 2] + iyz * uu[..., 1] * uu[..., 2]))
    rate = al / np.sqrt(1 + uu2)
    tau = np.zeros_like(rate)
    tau[1:] = np.cumsum(0.5 * (rate[1:] + rate[:-1]) * np.diff(t)[:, None], axis=0)
    dtau = float(np.nanmax(np.abs(tau[:nf] - tau_code[:nf])))
    r0 = r[0]
    sel = r0 > 1e-6
    sh = shell(r0)
    Ri0_run = R[0]
    dRi = float(np.nanmax(np.abs(Ri0_run[sel] / sh["Ri"][sel] - 1)))
    core = sel & (sh["Ri"] < 2.4)
    inner = sel & (sh["Ri"] < 2.0)
    # errors along the run up to the last finite time
    tt = tau[:nf]
    Rex = np.stack([R_exact(sh, tt[k]) for k in range(nf)])
    eps = R[:nf] / Rex - 1
    # at tau = 16.894 (interpolated per particle)
    e_ta = []
    for j in np.where(core)[0]:
        if tt[-1, j] >= TAU_TA:
            e_ta.append(np.interp(TAU_TA, tt[:, j], eps[:, j]))
    e_ta = np.array(e_ta)
    # turnaround per core particle: vertex of R(tau) through the maximum and its neighbours
    dta, dRm, dta_code = [], [], []
    tc_ = tau_code[:nf]
    win = {}
    for half in (1, 2, 3, 5):                    # sensitivity of the turnaround to the fit window (code tau)
        dd = []
        for j in np.where(core)[0]:
            k = int(np.nanargmax(R[:nf, j]))
            if half <= k <= nf - 1 - half:
                sl = slice(k - half, k + half + 1)
                c = np.polyfit(tc_[sl, j] - tc_[k, j], R[sl, j], 2)
                dd.append(tc_[k, j] - c[1] / (2 * c[0]) - sh["tau_ta"][j])
        win[half] = (float(np.mean(dd)), float(np.median(dd)))
    for j in np.where(core)[0]:
        k = int(np.nanargmax(R[:nf, j]))
        if 2 <= k <= nf - 3:
            s = slice(k - 2, k + 3)
            c = np.polyfit(tt[s, j] - tt[k, j], R[s, j], 2)
            tv = -c[1] / (2 * c[0])
            dta.append(tt[k, j] + tv - sh["tau_ta"][j])
            dRm.append(np.polyval(c, tv) / sh["Rmax"][j] - 1)
            c2 = np.polyfit(tc_[s, j] - tc_[k, j], R[s, j], 2)
            dta_code.append(tc_[k, j] - c2[1] / (2 * c2[0]) - sh["tau_ta"][j])
    # history and log: first non-positive metric determinant, first H-norm2 above 1e10
    t_det, t_blow = None, None
    try:
        for line in open(os.path.join(vc.SCR, run, seg, "athena.log"), errors="replace"):
            if "non-positive or non-finite metric determinant at time" in line:
                t_det = float(line.split("at time")[1].split()[0]); break
        for line in open(L.inp(run, f"{seg}/ball.z4c.user.hst")):
            if line.startswith("#"):
                continue
            v = line.split()
            hn = float(v[3])
            if not np.isfinite(hn) or hn > 1e10:
                t_blow = float(v[0]); break
    except FileNotFoundError:
        pass
    # central lapse at the core turnaround (innermost tracked particle)
    j0 = int(np.argmin(np.where(sel, r0, np.inf)))
    k_ta = int(np.argmin(np.abs(tt[:, j0] - TAU_TA))) if tt[-1, j0] >= TAU_TA else None
    res = dict(label=label, run=run, gauge=gauge, dx=dx, n_track=int(sel.sum()), n_core=int(core.sum()),
               t_last_finite=t_last, t_end=float(t[-1]), n_times=len(t), tau_vs_code=dtau, Ri_vs_table=dRi,
               max_eps_core_tauta=float(np.max(np.abs(e_ta))) if len(e_ta) else None,
               max_eps_inner_tauta=float(np.max(np.abs([np.interp(TAU_TA, tt[:, j], eps[:, j]) for j in np.where(inner)[0] if tt[-1, j] >= TAU_TA]))) if inner.any() else None,
               mean_dtau_ta=float(np.mean(dta)) if dta else None,
               mean_dtau_ta_code=float(np.mean(dta_code)) if dta_code else None, t_det=t_det, t_blow=t_blow,
               dtau_ta_window={str(k): v for k, v in win.items()}, mean_dRmax=float(np.mean(dRm)) if dRm else None,
               alpha_centre_at_ta=float(al[k_ta, j0]) if k_ta is not None else None, r_centre=float(r0[j0]))
    return res, dict(t=t, tau=tau, R=R, eps=eps, core=core, nf=nf, sh=sh, al=al, j0=j0)


results, series = {}, {}
for lab, (run, seg, gauge, dx) in RUNS.items():
    try:
        res, ser = analyse(lab, run, seg, gauge, dx)
    except FileNotFoundError as ex:
        print("missing", lab, ex)
        continue
    results[lab] = res; series[lab] = ser
    print(json.dumps(res, default=float))


def V(ok):
    return "CONFIRMED" if ok else "WRONG"


def near(x, c, rel):
    return x is not None and abs(x - c) <= rel * abs(c)


r = results
L.row("my proper time int alpha/W dt against the code's tau column", "(consistency)",
      ", ".join(f"{k}: {v['tau_vs_code']:.1e}" for k, v in r.items()), V(all(v["tau_vs_code"] < 5e-3 for v in r.values())),
      "largest difference over the run; mine is a trapezoid over the output records only, the code's integrates every step")
L.row("initial areal radius of the tracked particles (trajmet) against the table", "(consistency)",
      ", ".join(f"{k}: {v['Ri_vs_table']:.1e}" for k, v in r.items()), V(all(v["Ri_vs_table"] < 1e-2 for v in r.values())),
      "metric reconstructed at the particles at t = 0 vs psi^2 rbar")
L.row("SR-1 breakdown: dx = M/2; dx = M", "t = 33.0; 30.3 (non-finite)",
      f"first non-positive metric determinant {r['sr1_M2']['t_det']}; {r['sr1_M']['t_det']}; ||H||_2 > 1e10 at {r['sr1_M2']['t_blow']}; {r['sr1_M']['t_blow']}; "
      f"trajectory records end at {r['sr1_M2']['t_end']:.2f}; {r['sr1_M']['t_end']:.2f}",
      V(abs(r["sr1_M2"]["t_det"] - 33.0) < 0.3 and abs(r["sr1_M"]["t_det"] - 30.3) < 0.3),
      "athena.log and ball.z4c.user.hst; the trajectories stop at the last finite record")
def wtxt(lab):
    w = r[lab]["dtau_ta_window"]
    return "mean over windows of +-1, 2, 3, 5 records: " + ", ".join(f"{w[k][0]:+.4f}" for k in ("1", "2", "3", "5")) + \
        "; medians " + ", ".join(f"{w[k][1]:+.4f}" for k in ("1", "2", "3", "5"))


L.row("SR-1 dx = M/2: mean turnaround error of core shells; mean R_max error", "-0.022 M; +0.07 %",
      f"{r['sr1_M2']['mean_dtau_ta']:+.4f}; {100 * r['sr1_M2']['mean_dRmax']:+.3f} %",
      V(near(r["sr1_M2"]["mean_dtau_ta"], -0.022, 0.2) and near(r["sr1_M2"]["mean_dRmax"], 7e-4, 0.3)))
L.row("SR-2 dx = M/2: mean turnaround error of core shells; mean R_max error", "+0.043 M; +0.10 %",
      f"{r['sr2_M2']['dtau_ta_window']['1'][0]:+.4f} (three-point vertex, code tau); {100 * r['sr2_M2']['mean_dRmax']:+.3f} %",
      V(near(r["sr2_M2"]["dtau_ta_window"]["1"][0], 0.043, 0.05) and near(r["sr2_M2"]["mean_dRmax"], 1.0e-3, 0.3)),
      "estimator-dependent: " + wtxt("sr2_M2"))
L.row("core shells max |R/R_ex - 1| at tau = 16.9: SR-1 dx = M; M/2", "5.6e-2; 6.2e-3",
      f"{r['sr1_M']['max_eps_core_tauta']:.2e}; {r['sr1_M2']['max_eps_core_tauta']:.2e}",
      V(near(r["sr1_M"]["max_eps_core_tauta"], 5.6e-2, 0.2) and near(r["sr1_M2"]["max_eps_core_tauta"], 6.2e-3, 0.2)),
      "core = R_i < 2.4")
L.row("core shells max |R/R_ex - 1| at tau = 16.9: SR-2 dx = M; M/2", "2.1e-2; 7.5e-3",
      f"{r['sr2_M']['max_eps_core_tauta']:.2e}; {r['sr2_M2']['max_eps_core_tauta']:.2e}",
      V(near(r["sr2_M"]["max_eps_core_tauta"], 2.1e-2, 0.2) and near(r["sr2_M2"]["max_eps_core_tauta"], 7.5e-3, 0.2)))
if "sr1_M4" in r:
    L.row("SR-1 dx = M/4: mean turnaround error; core max |eps| at tau = 16.894", "-0.0125 M; 7.6e-4",
          f"{r['sr1_M4']['mean_dtau_ta']:+.4f}; {r['sr1_M4']['max_eps_core_tauta']:.2e}",
          V(near(r["sr1_M4"]["mean_dtau_ta"], -0.0125, 0.2) and near(r["sr1_M4"]["max_eps_core_tauta"], 7.6e-4, 0.2)))
if "sr2_M4" in r:
    L.row("SR-2 dx = M/4: mean turnaround error", "+0.031 M (fails R2's bound)",
          f"{r['sr2_M4']['dtau_ta_window']['1'][0]:+.4f} (three-point vertex, code tau)",
          V(near(r["sr2_M4"]["dtau_ta_window"]["1"][0], 0.031, 0.05)),
          "reproduced only with the three-point vertex; " + wtxt("sr2_M4") + "; the SR-1 values do not depend on the window (" + wtxt("sr1_M4") + ")")
    o1 = math.log2(r["sr1_M2"]["max_eps_core_tauta"] / r["sr1_M4"]["max_eps_core_tauta"])
    o2 = math.log2(r["sr2_M2"]["max_eps_core_tauta"] / r["sr2_M4"]["max_eps_core_tauta"])
    o1i = math.log2(r["sr1_M2"]["max_eps_inner_tauta"] / r["sr1_M4"]["max_eps_inner_tauta"])
    o2i = math.log2(r["sr2_M2"]["max_eps_inner_tauta"] / r["sr2_M4"]["max_eps_inner_tauta"])
    L.row("apparent order of the core-shell error between M/2 and M/4", "3.0-4.3",
          f"SR-1 {o1:.2f}, SR-2 {o2:.2f} (R_i < 2: {o1i:.2f}, {o2i:.2f})", V(2.7 < min(o1, o2) and max(o1, o2) < 4.6),
          "M/2 runs on [-64,64]^3, M/4 runs on [-32,32]^3: domain size changes with the cell size")
    if r["sr1_M4"]["mean_dtau_ta"] and r["sr1_M2"]["mean_dtau_ta"]:
        L.row("turnaround error ratio M/2 -> M/4 (SR-1; SR-2)", "(not claimed)",
              f"{r['sr1_M2']['mean_dtau_ta'] / r['sr1_M4']['mean_dtau_ta']:.2f}; {r['sr2_M2']['mean_dtau_ta'] / r['sr2_M4']['mean_dtau_ta']:.2f}",
              "CONFIRMED", "informational: the turnaround converges at first order or slower, unlike the radii")
L.row("SR-2 central lapse at the core turnaround", "1.85 (instead of 1.34)",
      f"dx = M/2: {r['sr2_M2']['alpha_centre_at_ta']:.3f}; dx = M: {r['sr2_M']['alpha_centre_at_ta']:.3f} (innermost tracked particle, r = {r['sr2_M2']['r_centre']:.2f})",
      V(near(r["sr2_M2"]["alpha_centre_at_ta"], 1.85, 0.05)), "exact conformal-time lapse at turnaround: R_max/R_i = 1.340")
L.write(OUT)
with open(os.path.join(OUT, "ball_recomputed.json"), "w") as f:
    json.dump(results, f, indent=1, default=float)

# ------------------------------------------------------------------ figure
fs.use_style()
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
fig.subplots_adjust(left=0.085, right=0.99, bottom=0.17, top=0.95, wspace=0.42)
cols = {1.0: fs.PAL["yellow"], 0.5: fs.PAL["red"], 0.25: fs.PAL["green"]}
for lab, s in series.items():
    gauge, dx = RUNS[lab][2], RUNS[lab][3]
    axk = ax[0] if gauge == "sr1" else ax[1]
    core = np.where(s["core"])[0]
    e = np.nanmax(np.abs(s["eps"][:, core]), axis=1)
    tmed = np.nanmedian(s["tau"][: s["nf"], core], axis=1)
    axk.semilogy(tmed, e, color=cols[dx], label=f"dx = M/{int(round(1 / dx))}" if dx < 1 else "dx = M")
for k_, (axk, title) in enumerate(((ax[0], "SR-1 geodesic"), (ax[1], "SR-2 conformal time"))):
    axk.axvline(TAU_TA, **fs.MASK_LINE); axk.set_xlabel(r"proper time $\tau$")
    axk.set_ylabel(r"max $|R/R_{\rm ex}-1|$, core", labelpad=1); axk.legend(loc="lower right", fontsize=8); axk.set_ylim(1e-5, 1)
    axk.text(0.03, 0.92, title, transform=axk.transAxes, fontsize=9)
s = series["sr1_M2"]; j = np.where(s["core"])[0][::40]
for jj in j:
    ax[2].plot(s["tau"][: s["nf"], jj], s["R"][: s["nf"], jj] / s["sh"]["Ri"][jj], color=fs.PAL["red"], lw=1.0)
    tt_ = np.linspace(0, 44.4, 300)
    sh1 = {k: (v[jj] if isinstance(v, np.ndarray) else v) for k, v in s["sh"].items()}
    ax[2].plot(tt_, R_exact(sh1, tt_) / sh1["Ri"], color=fs.PAL["blue"], ls="--", lw=1.0)
ax[2].set_xlabel(r"proper time $\tau$"); ax[2].set_ylabel(r"$R/R_i$, core, SR-1, M/2", labelpad=1)
ax[2].plot([], [], color=fs.PAL["red"], label="run"); ax[2].plot([], [], color=fs.PAL["blue"], ls="--", label="my cycloid")
ax[2].legend(loc="lower left", fontsize=8)
fs.save(fig, os.path.join(OUT, "fig_v_ball"))
print("figure", os.path.join(OUT, "fig_v_ball.png"))
