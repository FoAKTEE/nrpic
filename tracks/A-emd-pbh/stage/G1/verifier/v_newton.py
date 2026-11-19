"""G1 verifier, C18 part 3: the Newtonian-mode results of newton/ (wave 2), recomputed from
the AthenaK histories (newton.newton.hst) with my own estimators and my own references.

References written here: the cycloid of a uniform sphere through (R0, V0), and the cold
homogeneous ellipsoid, A_i'' = -G M A_i R_D(A_j^2, A_k^2, A_i^2) (G = 1), both started
from the Zel'dovich data of each case's ball.json (a0, H0, abg, r_vol). Code time + t0 =
cosmic time. Semi-axes from the centred second moments, A_i = sqrt(5 I_ii/M).
Usage: python v_newton.py [--out DIR]
"""
import argparse
import glob
import json
import math
import os

import numpy as np
from scipy.integrate import solve_ivp
from scipy.special import ellipe, elliprd

import vcommon as vc
from vcommon import fs

ap = argparse.ArgumentParser()
ap.add_argument("--out", default=None)
a = ap.parse_args()
OUT = a.out or vc.outdir("newton")
os.makedirs(OUT, exist_ok=True)
L = vc.Ledger("newton")
TH = "A-emd-pbh-20261115-153409-dc27b98"
SC = "A-emd-pbh-20261115-153415-dc27b98"
CA = "A-emd-pbh-20261115-153437-dc27b98"
PR = "A-emd-pbh-20261115-153424-dc27b98"      # particle files and ball.json of the card cases


def load(run, case):
    b = json.load(open(L.inp(PR if run == CA else run, f"{case}/ball.json")))
    h = np.loadtxt(L.inp(run, f"{case}/newton.newton.hst"))
    t = h[:, 0] + b["t0"]
    M = h[0, 3]
    X = h[:, 15:18]
    I = h[:, [18, 21, 23]] - M * X ** 2          # centred diagonal second moments (xx, yy, zz)
    Ioff = h[:, [19, 20, 22]] - M * np.stack([X[:, 0] * X[:, 1], X[:, 0] * X[:, 2], X[:, 1] * X[:, 2]], 1)
    Etot = h[:, 4] + h[:, 5]
    Emesh = h[:, 4] + h[:, 6]
    return b, dict(t=t, M=M, I=I, Ioff=Ioff, A=np.sqrt(5 * np.maximum(I, 0) / M), E=Etot, Em=Emesh, W0=h[0, 5])


def vertex(t, y, i, k=4, kind="max"):
    """vertex of a parabola through y[i-k..i+k] (t, y)."""
    s = slice(max(i - k, 0), i + k + 1)
    c = np.polyfit(t[s] - t[i], y[s], 2)
    tv = -c[1] / (2 * c[0])
    return t[i] + tv, np.polyval(c, tv)


# ------------------------------------------------------------------ references
def cycloid(R0, V0, M, t0):
    E = 0.5 * V0 ** 2 - M / R0
    A = M / (-2 * E); B = M / (-2 * E) ** 1.5
    e0 = math.acos(1 - R0 / A); tb = t0 - B * (e0 - math.sin(e0))
    t_of = lambda eta: tb + B * (eta - math.sin(eta))
    eta_q = 2 * math.pi - math.acos(1 - 0.25 * 2)       # R = 0.25 R_max = 0.5 A on the way in
    return dict(t_ta=t_of(math.pi), R_max=2 * A, t_q=t_of(eta_q), t_c=t_of(2 * math.pi))


def ellipsoid(b, t_end):
    a0, H0, M = b["a0"], b["H0"], b["mass"]
    lam = np.array(b["abg"]); r = b["r_vol"]
    A0 = a0 * (1 - a0 * lam) * r
    V0 = H0 * a0 * (1 - 2 * a0 * lam) * r

    def rhs(t, y):
        A = y[:3]; A2 = A * A
        acc = np.array([-M * A[0] * elliprd(A2[1], A2[2], A2[0]),
                        -M * A[1] * elliprd(A2[0], A2[2], A2[1]),
                        -M * A[2] * elliprd(A2[0], A2[1], A2[2])])
        return np.concatenate([y[3:], acc])

    evs = []
    for i in range(3):
        f = (lambda i: (lambda t, y: y[i]))(i)
        f.terminal = True; f.direction = -1
        evs.append(f)
    t, y = b["t0"], np.concatenate([A0, V0])
    out, ts, ys = [], [], []
    while t < t_end and len(out) < 3:
        sol = solve_ivp(rhs, (t, t_end), y, rtol=1e-12, atol=1e-14, events=evs, dense_output=True, method="DOP853")
        tt = np.linspace(t, sol.t[-1], 400)
        ts.append(tt); ys.append(np.abs(sol.sol(tt)[:3].T))
        if sol.status == -1:                       # spindle (two axes at once): the solver stops at the line singularity
            Ae = np.abs(sol.y[:3, -1])
            if Ae.min() < 1e-4 * Ae.max():
                for k in np.argsort(Ae)[:2]:
                    if Ae[k] < 1e-4 * Ae.max():
                        out.append(dict(t=sol.t[-1], axis=int(k), A=Ae.copy(), singular=True))
            break
        if sol.status != 1:
            break
        i = [k for k in range(3) if len(sol.t_events[k])][0]
        te, ye = sol.t_events[i][0], sol.y_events[i][0].copy()
        out.append(dict(t=te, axis=i, A=np.abs(ye[:3]).copy()))
        # pass through: the dynamics depends on A_i^2 only, so reflect (A_i -> +0, V_i -> -V_i)
        ye[i] = 1e-13; ye[3 + i] = -ye[3 + i]
        t, y = te, ye
    return out, np.concatenate(ts), np.concatenate(ys)


def hoop(Aj, Ak, M):
    a_, b_ = max(Aj, Ak), min(Aj, Ak)
    return 4 * a_ * ellipe(1 - (b_ / a_) ** 2) / (4 * math.pi * M)


# ------------------------------------------------------------------ top hat
th_cases = sorted(os.path.basename(p) for p in glob.glob(os.path.join(vc.SCR, TH, "th_*")))
card_th = sorted(os.path.basename(p) for p in glob.glob(os.path.join(vc.SCR, CA, "th_*")))
res_th = {}
for run, cases in ((TH, th_cases), (CA, card_th)):
    for c in cases:
        b, d = load(run, c)
        lam = b["abg"][0]
        R0 = b["a0"] * (1 - b["a0"] * lam) * b["r_vol"]; V0 = b["H0"] * b["a0"] * (1 - 2 * b["a0"] * lam) * b["r_vol"]
        ref = cycloid(R0, V0, b["mass"], b["t0"])
        R = np.sqrt(np.sum(d["A"] ** 2, 1) / 3)          # sqrt(5 tr I / (3 M))
        i = int(np.argmax(R)); t_ta, Rm = vertex(d["t"], R, i)
        j = i + int(np.argmax(R[i:] < 0.25 * Rm))
        t_q = np.interp(0.25 * Rm, R[j:j - 2:-1] if False else [R[j], R[j - 1]], [d["t"][j], d["t"][j - 1]])
        k = i + int(np.argmin(R[i:])); t_min, Rmin = vertex(d["t"], R, k, kind="min") if 3 < k < len(R) - 4 else (d["t"][k], R[k])
        e = dict(t_ta=t_ta / ref["t_ta"] - 1, R_max=Rm / ref["R_max"] - 1, t_q=t_q / ref["t_q"] - 1,
                 t_c=t_min / ref["t_c"] - 1, n=b["n"], nx=b["case"]["nx"], Rmin=Rmin,
                 dE=float(np.max(np.abs(d["E"] / d["E"][0] - 1))), run=run,
                 refcheck=abs(ref["t_c"] / b["reference"]["ellipsoid_isolated"]["collapses"][0]["t"] - 1))
        res_th[f"{run[-7:]}:{c}"] = e
print("top hat (signed relative errors):")
for k_, e in res_th.items():
    print(f"  {k_:28s} n={e['n']:8d} nx={e['nx']:4d} t_ta {e['t_ta']:+.2e} R_max {e['R_max']:+.2e} t_q {e['t_q']:+.2e} "
          f"t_c {e['t_c']:+.2e} dE {e['dE']:.1e}  (my cycloid t_c vs ball.json {e['refcheck']:.1e})")
e128 = res_th[f"{TH[-7:]}:th_n128_h025"]
claim = dict(t_ta=7.16e-4, R_max=4.31e-4, t_q=8.39e-4, t_c=2.59e-4)
ok = all(abs(e128[q] - claim[q]) <= 1.5e-4 for q in claim)
L.row("top hat 128^3, 2.7e5 particles: t_ta; R_max; t(R=0.25 R_max); softened collapse",
      "+7.16e-4; +4.31e-4; +8.39e-4; +2.59e-4",
      f"{e128['t_ta']:+.2e}; {e128['R_max']:+.2e}; {e128['t_q']:+.2e}; {e128['t_c']:+.2e}", "CONFIRMED" if ok else "WRONG",
      "my estimators (parabola vertex of the moment radius; linear interpolation); my cycloid")
fac = []
for q in ("t_ta", "R_max", "t_q", "t_c"):
    e32, e64, e128_ = (res_th[f"{TH[-7:]}:th_n{n:03d}_h025"][q] for n in (32, 64, 128))
    fac.append((q, e32 / e64, e64 / e128_))
ok = all(3.5 < f2 < 6.5 for _, _, f2 in fac)
L.row("top hat: mesh convergence factors 32->64->128 (2.7e5 particles)", "4.0-6.1 per doubling (second order)",
      "; ".join(f"{q} {f1:.1f}, {f2:.1f}" for q, f1, f2 in fac), "CONFIRMED" if ok else "WRONG")
c128 = res_th.get(f"{CA[-7:]}:th_n128_h0125")
if c128:
    dd = max(abs(c128[q] - e128[q]) for q in claim)
    L.row("top hat 128^3 with 2.1e6 particles (card) against 2.7e5", "agree to 1e-5",
          f"largest difference {dd:.1e} (t_ta {c128['t_ta']:+.2e})", "CONFIRMED" if dd < 2e-5 else "WRONG")
_, d128 = load(TH, "th_n128_h025")
_b = json.load(open(L.inp(TH, "th_n128_h025/ball.json")))
lam_ = _b["abg"][0]
_ref = cycloid(_b["a0"] * (1 - _b["a0"] * lam_) * _b["r_vol"], _b["H0"] * _b["a0"] * (1 - 2 * _b["a0"] * lam_) * _b["r_vol"], _b["mass"], _b["t0"])
dE_q = float(np.max(np.abs(d128["E"][d128["t"] <= _ref["t_q"]] - d128["E"][0])) / abs(d128["W0"]))
dE_q2 = float(np.max(np.abs(d128["E"][d128["t"] <= _ref["t_q"]] / d128["E"][0] - 1)))
L.row("top hat energy, 128^3: max |K+W-E_0|/|W_0| up to t(R = 0.25 R_max)", "9.5e-5",
      f"{dE_q:.2e} (relative to |E_0|: {dE_q2:.1e}; over the whole run, past the softened collapse: {e128['dE']:.1e})",
      "CONFIRMED" if abs(dE_q / 9.5e-5 - 1) < 0.1 else "WRONG", "interval and normalisation as in the track's docstring")

# ------------------------------------------------------------------ scan against the ellipsoid
sc_cases = sorted(os.path.basename(p) for p in glob.glob(os.path.join(vc.SCR, SC, "e0p*")))
card_sc = sorted(os.path.basename(p) for p in glob.glob(os.path.join(vc.SCR, CA, "e0p*")))
res = {}
series = {}
for run, cases in ((SC, sc_cases), (CA, card_sc)):
    for c in cases:
        b, d = load(run, c)
        t_end = d["t"][-1]
        cols, tr, Ar = ellipsoid(b, t_end * 1.02)
        series[f"{run[-7:]}:{c}"] = (d, tr, Ar)
        ax_pred = int(np.argmax(b["abg"])) if abs(b["abg"][0] - b["abg"][1]) > 1e-12 else 0
        c1 = cols[0]
        # measured first collapse: global minimum of the centred moment of each axis before 1.2 t_1
        sel = d["t"] < c1["t"] + 0.2 * (c1["t"] - b["t0"])
        tmin = []
        for ax_ in range(3):
            i = int(np.argmin(d["I"][sel, ax_]))
            tmin.append(vertex(d["t"], d["I"][:, ax_], i, k=3, kind="min")[0] if 3 < i < sel.sum() - 4 else np.inf)
        ax_meas = int(np.argmin(tmin))
        t1 = tmin[ax_meas]
        i1 = int(np.argmin(np.abs(d["t"] - t1)))
        others = [x for x in range(3) if x != c1["axis"]]
        A_t1 = [float(np.interp(t1, d["t"], d["A"][:, x])) for x in others]
        h_run = hoop(A_t1[0], A_t1[1], d["M"]); h_ref = hoop(c1["A"][others[0]], c1["A"][others[1]], b["mass"])
        # like-for-like with newton/analyze_newton.py's docstring: axes at the REFERENCE t_1; t_1 from a
        # parabola through c_i where A_i < 0.2 A_i(0); energy |K+W-E_0|/|W_0|
        A_r = [float(np.interp(c1["t"], d["t"], d["A"][:, x])) for x in others]
        h_r = hoop(A_r[0], A_r[1], d["M"])
        cax = c1["axis"]; Aax = d["A"][:, cax]
        ib = int(np.argmin(np.where(sel, d["I"][:, cax], np.inf)))
        lo = ib; hi = ib
        while lo > 0 and Aax[lo - 1] < 0.2 * Aax[0]:
            lo -= 1
        while hi < len(Aax) - 1 and Aax[hi + 1] < 0.2 * Aax[0] and d["I"][hi + 1, cax] >= d["I"][hi, cax]:
            hi += 1
        cc = np.polyfit(d["t"][lo:hi + 1] - d["t"][ib], d["I"][lo:hi + 1, cax], 2)
        t1_w = d["t"][ib] - cc[1] / (2 * cc[0])
        W0 = abs(d["W0"])
        ref_ball = b["reference"]["ellipsoid_isolated"]["collapses"][0]["t"]
        r = dict(e=b["e"], p=b["p"], dL=b["deltaL"], n=b["n"], nx=b["case"]["nx"], axis_ref=c1["axis"], axis_meas=ax_meas,
                 t1_ref=c1["t"], t1=t1 / c1["t"] - 1, t1_elapsed=(t1 - c1["t"]) / (c1["t"] - b["t0"]),
                 refdiff=c1["t"] / ref_ball - 1,
                 A2=A_t1[0] / max(c1["A"][others[0]], 1e-300) - 1 if c1["A"][others[0]] > 1e-6 else A_t1[0],
                 A3=A_t1[1] / c1["A"][others[1]] - 1, h=h_run / h_ref - 1, hdL=h_run * b["deltaL"], hdL_ref=h_ref * b["deltaL"],
                 dE09=float(np.max(np.abs(d["E"][d["t"] <= b["t0"] + 0.9 * (c1["t"] - b["t0"])] / d["E"][0] - 1))),
                 dE1=float(np.abs(d["E"][i1] / d["E"][0] - 1)),
                 t1_w=t1_w / c1["t"] - 1,
                 A2_r=(A_r[0] / c1["A"][others[0]] - 1) if c1["A"][others[0]] > 1e-6 else A_r[0],
                 A3_r=A_r[1] / c1["A"][others[1]] - 1, h_r=h_r / h_ref - 1, hdL_r=h_r * b["deltaL"],
                 dEW09=float(np.max(np.abs(d["E"][d["t"] <= b["t0"] + 0.9 * (c1["t"] - b["t0"])] - d["E"][0])) / W0),
                 dEW1=float(np.max(np.abs(d["E"][d["t"] <= c1["t"]] - d["E"][0])) / W0))
        if len(cols) > 1 and cols[1]["t"] < d["t"][-1] and cols[1]["t"] - c1["t"] > 1e-6 * c1["t"]:
            ax2 = cols[1]["axis"]
            selb = (d["t"] > t1 + 0.02 * (cols[1]["t"] - t1)) & (d["t"] < cols[1]["t"] + 0.1 * (cols[1]["t"] - b["t0"]))
            idx = np.where(selb)[0]
            i2 = idx[int(np.argmin(d["I"][selb, ax2]))]
            r["t2"] = vertex(d["t"], d["I"][:, ax2], i2, k=3, kind="min")[0] / cols[1]["t"] - 1
        res[f"{run[-7:]}:{c}"] = r
print("scan (relative errors at the first collapse):")
for k_, r in res.items():
    print(f"  {k_:20s} e={r['e']:.2f} p={r['p']:+.2f} dL={r['dL']:.2f} n={r['n']:7d} nx={r['nx']:3d} axis {r['axis_meas']}/{r['axis_ref']} "
          f"t1 {r['t1']:+.2e} (elapsed {r['t1_elapsed']:+.2e}) A2 {r['A2']:+.2e} A3 {r['A3']:+.2e} h {r['h']:+.2e} "
          f"h*dL {r['hdL']:.4f}/{r['hdL_ref']:.4f} | A2 {r['A2_r']:+.2e} A3 {r['A3_r']:+.2e} h {r['h_r']:+.2e} hdL {r['hdL_r']:.4f} dE/W0 {r['dEW09']:.1e}/{r['dEW1']:.1e} | t2 {r.get('t2', float('nan')):+.2e} dE(0.9t1) {r['dE09']:.1e} dE(t1) {r['dE1']:.1e} ref-vs-ball {r['refdiff']:.1e}")

main = [k for k, r in res.items() if r["nx"] == 128 and r["n"] == 268096 and "rot" not in k and abs(r["dL"] - 0.2) < 1e-9]
L.row("first collapse along the predicted axis", "all 14 runs", f"{sum(r['axis_meas'] == r['axis_ref'] for r in res.values())} of {len(res)}",
      "CONFIRMED" if all(r["axis_meas"] == r["axis_ref"] for r in res.values()) and len(res) == 14 else "WRONG",
      "spindle p = -e: two axes collapse together; the measured one is either")
reg = [res[k] for k in main if abs(res[k]["p"]) < 1e-9]
t1s = [r["t1"] for r in reg]
L.row("t_1 for e = 0.05-0.3 (p = 0, 128^3, 2.7e5)", "+2.2e-4 to +6.3e-4",
      f"{min(t1s):+.2e} to {max(t1s):+.2e} (" + ", ".join(f"e={r['e']:.2f}: {r['t1']:+.1e}" for r in reg) + ")",
      "CONFIRMED" if min(t1s) > 1.0e-4 and max(t1s) < 7.0e-4 else "WRONG",
      "relative to the cosmic time of the reference collapse; my vertex uses +-3 records around the minimum of the moment, "
      "the track's a wider window: the two differ by up to 1.3e-4 (e = 0.05)")
spin = [res[k] for k in main if res[k]["p"] < -1e-9][0]
L.row("t_1 of the spindle p = -e", "+1.5e-3", f"{spin['t1']:+.2e}", "CONFIRMED" if abs(spin["t1"] - 1.5e-3) < 3e-4 else "WRONG")
oth = [max(abs(res[k]["A3"]), abs(res[k]["A2"]) if res[k]["p"] >= -1e-9 else 0) for k in main]
hh = [abs(res[k]["h"]) for k in main]
oth_r = [max(abs(res[k]["A3_r"]), abs(res[k]["A2_r"]) if res[k]["p"] >= -1e-9 else 0) for k in main]
hh_r = [abs(res[k]["h_r"]) for k in main]
L.row("like-for-like (axes at the reference t_1): other semi-axes; hoop ratio", "within 1.2e-3; within 6.1e-4",
      f"largest {max(oth_r):.1e}; {max(hh_r):.1e}", "CONFIRMED" if max(oth_r) < 1.3e-3 and max(hh_r) < 6.6e-4 else "WRONG",
      f"the track's estimator; with the axes at the MEASURED t_1 (my first estimator) the largest errors are {max(oth):.1e} and "
      f"{max(hh):.1e}, of opposite sign: the axis error is dominated by the 1e-4 shift of t_1")
order = {(0.05, 0.0): 0.3597, (0.1, 0.0): 0.5925, (0.2, 0.0): 0.8547, (0.3, 0.0): 0.9685, (0.2, 0.2): 0.9194, (0.2, -0.2): 0.8636}
got = {(round(res[k]["e"], 2), round(res[k]["p"], 2) + 0.0): res[k]["hdL_r"] for k in main}
okh = all(abs(got[k] - v) < 6e-4 for k, v in order.items() if k in got)
L.row("Newtonian hoop amplitudes h_1 delta_L (run; axes at the reference t_1)", "0.3597, 0.5925, 0.8547, 0.9685, 0.9194, 0.8636",
      ", ".join(f"{got.get(k, float('nan')):.4f}" for k in order), "CONFIRMED" if okh and len(got) == 6 else "WRONG")
okref = all(abs(r["refdiff"]) < 1e-6 for r in res.values())
L.row("my ellipsoid reference against the track's (ball.json) t_1", "same reference", f"largest {max(abs(r['refdiff']) for r in res.values()):.1e}",
      "CONFIRMED" if okref else "WRONG")
amp = [res[k]["t1"] for k in res if "dL" in k] + [res[f"{SC[-7:]}:e0p1"]["t1"]]
L.row("three amplitudes (delta_L = 0.05, 0.2, 0.6, e = 0.1) agree", "to 5e-7", f"spread {max(amp) - min(amp):.1e}",
      "CONFIRMED" if max(amp) - min(amp) < 2e-6 else "WRONG")
for tag, claim_v in (("e0p1_n064", 8.8e-4), ("e0p2_n064", 1.5e-3), ("e0p2_rot", 3.7e-4)):
    k = f"{SC[-7:]}:{tag}"
    if k in res:
        L.row(f"control {tag}: t_1", f"{claim_v:+.1e}", f"{res[k]['t1']:+.2e}",
              "CONFIRMED" if abs(res[k]["t1"] - claim_v) < 0.15 * claim_v + 5e-5 else "WRONG")
kc = f"{CA[-7:]}:e0p2_h0125"
if kc in res:
    L.row("control e = 0.2 with 2.1e6 particles (card): t_1", "+3.7e-4 (9e-6 from 2.7e5)",
          f"{res[kc]['t1']:+.2e} ({res[kc]['t1'] - res[SC[-7:] + ':e0p2']['t1']:+.1e} from 2.7e5)",
          "CONFIRMED" if abs(res[kc]["t1"] - res[SC[-7:] + ":e0p2"]["t1"]) < 3e-5 else "WRONG")
t2s = [(k, res[k]["t2"]) for k in main if "t2" in res[k]]
L.row("second collapse t_2 (where inside the run)", "+3.1e-4, +4.0e-4, +5.6e-4 (e = 0.05, 0.1, 0.2)",
      ", ".join(f"{k.split(':')[1]} {v:+.1e}" for k, v in t2s), "CONFIRMED" if t2s and max(abs(v) for _, v in t2s) < 7e-4 else "WRONG")
e09 = [res[k]["dEW09"] for k in main]; e1 = [res[k]["dEW1"] for k in main if res[k]["p"] >= -1e-9]
L.row("energy |K+W-E_0|/|W_0|: up to 0.9 t_1; up to t_1 (p >= 0); spindle up to t_1", "<= 1.9e-4; 1.1e-3 to 9.3e-3; 3.0e-2",
      f"{max(e09):.1e}; {min(e1):.1e} to {max(e1):.1e}; {spin['dEW1']:.1e}",
      "CONFIRMED" if max(e09) < 2.0e-4 and abs(min(e1) / 1.1e-3 - 1) < 0.15 and abs(max(e1) / 9.3e-3 - 1) < 0.15 and abs(spin["dEW1"] / 3.0e-2 - 1) < 0.15 else "WRONG",
      "normalised by |W_0| as the track's docstring says")
L.write(OUT)
with open(os.path.join(OUT, "newton_recomputed.json"), "w") as f:
    json.dump({"tophat": res_th, "scan": res}, f, indent=1, default=float)

# ------------------------------------------------------------------ figures
fs.use_style()
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.3))
fig.subplots_adjust(left=0.09, right=0.98, bottom=0.15, top=0.95, wspace=0.3)
for n, col in ((32, fs.PAL["yellow"]), (64, fs.PAL["green"]), (128, fs.PAL["red"])):
    e_ = res_th[f"{TH[-7:]}:th_n{n:03d}_h025"]
    ax[0].plot([1, 2, 3, 4], [abs(e_[q]) for q in ("t_ta", "R_max", "t_q", "t_c")], "o-", color=col, label=f"{n}$^3$, 2.7e5")
if c128:
    ax[0].plot([1, 2, 3, 4], [abs(c128[q]) for q in ("t_ta", "R_max", "t_q", "t_c")], "s--", color="k", ms=4, label="128$^3$, 2.1e6 (card)")
ax[0].set_xticks([1, 2, 3, 4]); ax[0].set_xticklabels([r"$t_{\rm ta}$", r"$R_{\max}$", r"$t_{1/4}$", r"$t_{\min R}$"])
ax[0].set_yscale("log"); ax[0].set_ylabel("|relative error| vs my cycloid"); ax[0].set_ylim(1e-4, 1e-1)
ax[0].legend(loc="upper right", fontsize=8, ncol=2)
d, tr, Ar = series[f"{SC[-7:]}:e0p2"]
for i_, col in enumerate((fs.PAL["red"], fs.PAL["green"], fs.PAL["orange"])):
    ax[1].plot(d["t"], d["A"][:, i_], color=col, label=f"$A_{i_ + 1}$ run")
    ax[1].plot(tr, np.abs(Ar[:, i_]), color=fs.PAL["blue"], ls="--", lw=1.0)
ax[1].plot([], [], color=fs.PAL["blue"], ls="--", lw=1.0, label="my ellipsoid")
ax[1].set_xlabel("cosmic time $t$"); ax[1].set_ylabel("semi-axes, $e=0.2$, $p=0$"); ax[1].legend(loc="upper left", fontsize=8)
fs.save(fig, os.path.join(OUT, "fig_v_newton"))
fig, ax = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH, 3.0))
fig.subplots_adjust(left=0.2, right=0.96, bottom=0.16, top=0.95)
for k_ in main:
    r = res[k_]
    ax.plot(r["e"] + 0.004 * r["p"] / 0.2, abs(r["t1"]), "o", color=fs.PAL["red"] if abs(r["p"]) < 1e-9 else fs.PAL["orange"], ms=4)
    ax.plot(r["e"] + 0.004 * r["p"] / 0.2, abs(r["h_r"]), "s", color=fs.PAL["blue"], ms=4)
ax.plot([], [], "o", color=fs.PAL["red"], label=r"$|\Delta t_1/t_1|$")
ax.plot([], [], "s", color=fs.PAL["blue"], label=r"$|\Delta h_1/h_1|$")
ax.set_yscale("log"); ax.set_xlabel("ellipticity $e$"); ax.legend(loc="upper left", fontsize=8)
fs.save(fig, os.path.join(OUT, "fig_v_newton_scan"))
print("figures", OUT)
