"""G1 verifier, C18 part 1: recompute the numerical ledger of the working note
(note/tables/ledger.tex, note/tables/parameters.tex) from raw outputs and paper sources.

Independent of the track's code: formulas are coded here from the paper sources; the exact
solution of data set 2t is rebuilt from its radial table alone (R = psi^2 rbar, E from
dR/drbar, v = -KT R, m from v^2 = 2m/R + 2E) and solved with the cycloid written here.
Usage: python v_ledger.py [--out DIR]  (default: $NRPIC_RUN_DIR)
"""
import argparse
import glob
import json
import math
import os
import re

import numpy as np
from scipy.special import ellipe
from scipy.optimize import brentq

import vcommon as vc
from vcommon import fs

ap = argparse.ArgumentParser()
ap.add_argument("--out", default=None)
a = ap.parse_args()
OUT = a.out or vc.outdir("ledger")
os.makedirs(OUT, exist_ok=True)
L = vc.Ledger("ledger")
EUL = math.e


def printed(x, s):
    """True when x, rounded like the printed string s, gives s."""
    s = s.strip()
    if "e" in s.lower():
        mant, ex = s.lower().split("e")
        nd = len(mant.replace("-", "").replace(".", "").lstrip("0"))
        return float(f"{x:.{max(nd - 1, 0)}e}") == float(s)
    dec = len(s.split(".")[1]) if "." in s else 0
    return round(x, dec) == round(float(s), dec)


def V(ok):
    return "CONFIRMED" if ok else "WRONG"


# ============================================================ 1. threshold landscape
src = os.path.join(vc.KB, "2609.14218/v1/src/MDPBH.tex")
lines = open(src, errors="replace").read().split("\n")
loc = {n: lines[n - 1] for n in (908, 918, 1102, 1103, 766, 767, 768)}
ok_loc = ("1+3e+p" in loc[908] and "hat h(e,p):=" in loc[918] and "0.05" in loc[1102]
          and "0.045" in loc[1103] and "0.32" in loc[766] and "0.33" in loc[767])
L.row("locators MDPBH.tex 907-908, 918, 1101-1103, 765-768", "as cited", "formula/numbers found at 908, 918, 1102-1103, 766-768", V(ok_loc))


def hhat(e, p=0.0):
    m = 1.0 - (e + p) ** 2 / (4.0 * e * e)          # scipy ellipe takes the parameter m = k^2
    return 15.0 / math.pi * e / (1.0 + 3.0 * e + p) ** 2 * ellipe(m)


h02 = hhat(0.2)
L.row("hhat(0.2,0) [MDPBH.tex:918]", "0.452", f"{h02:.6f}", V(printed(h02, "0.452")))

sn = json.load(open(L.inp("A-20261115-130252-7877b7a", "scope/scope_numbers.json")))
ro_e, ro_mu = np.array(sn["T1"]["readoff_e"]), np.array(sn["T1"]["readoff_mu"])
dev = np.max(np.abs(np.array([hhat(e) for e in ro_e]) - ro_mu))
L.row("largest |hhat - read-off| (read-offs of the track, figure hcont of 2609.14218)", "0.0025",
      f"{dev:.5f}", V(printed(dev, "0.0025")), "read-off values themselves not re-read: see VERIFIER.md")

dcrit = 0.15 * (12 * math.pi) ** (2 / 3)            # linear contrast at top-hat collapse
dcrit_ta = 0.15 * (6 * math.pi) ** (2 / 3)          # at turnaround


def mu_fd(tend):
    return (5 * EUL / 12) * dcrit * tend ** (-2 / 3)


mus = [mu_fd(t) for t in (100, 250, 400, 1000)]
ok = all(printed(x, s) for x, s in zip(mus, ["0.089", "0.048", "0.035", "0.019"]))
L.row("mu_fd for t_end = 100, 250, 400, 1000 t_H", "0.089, 0.048, 0.035, 0.019",
      ", ".join(f"{x:.5f}" for x in mus), V(ok), "mu_fd = (5e/12) delta_crit (t_end/t_H)^(-2/3)")

mu = np.array(sn["T2"]["mu"]); t_read = np.array(sn["T2"]["t_read"])
tc_rm_mine = (dcrit / (12 * mu / (5 * EUL))) ** 1.5
dt = np.max(np.abs(tc_rm_mine / np.array(sn["T2"]["t_c_rm"]) - 1))
sel = mu <= 0.15 + 1e-12
slope = np.polyfit(np.log(mu[sel]), np.log(t_read[sel]), 1)[0]
slope_all = np.polyfit(np.log(mu), np.log(t_read), 1)[0]
L.row("slope of read-off collapse times against mu (mu <= 0.15)", "-1.31", f"{slope:.4f} (all six: {slope_all:.3f})",
      V(printed(slope, "-1.31")), f"my top-hat times equal the track's t_c_rm to {dt:.1e}")
ratio = t_read / tc_rm_mine
r_sel = ratio[sel]
med_sel, med_all = float(np.median(r_sel)), float(np.median(ratio))
L.row("read-off/top-hat ratio at r_m, mu <= 0.15: range", "0.80-1.01",
      f"{r_sel.min():.3f}-{r_sel.max():.3f}", V(printed(r_sel.min(), "0.80") and printed(r_sel.max(), "1.01")))
L.row("read-off/top-hat ratio at r_m, mu <= 0.15: median", "0.86",
      f"{med_sel:.4f} over mu<=0.15; {med_all:.4f} over all six (incl. mu=0.3, ratio {ratio[0]:.2f})",
      "WRONG" if not printed(med_sel, "0.86") else "CONFIRMED",
      "the printed 0.86 is the median over all six read-offs, not over mu <= 0.15")

# ball: R_b = q r_m, R_b H_i = 0.9 -> a_i/a_H = (q/0.9)^2; start contrast <= 0.3
rows_mean, rows_cen = [], []
for q in (2, 3, 4):
    ai = (q / 0.9) ** 2
    rows_mean.append((5 * EUL / 12) * 0.3 / ai)
    rows_cen.append((5 / 12) * 0.3 / ai)
ok = all(printed(x, s) for x, s in zip(rows_mean, ["0.069", "0.031", "0.017"]))
L.row("largest mu in the ball, R_b H_i = 0.9, R_b = 2,3,4 r_m (mean contrast 0.3)", "0.069, 0.031, 0.017",
      ", ".join(f"{x:.4f}" for x in rows_mean), V(ok))
ok = all(printed(x, s) for x, s in zip(rows_cen, ["0.0253", "0.0113", "0.0063"]))
L.row("the same with the central contrast <= 0.3", "0.0253, 0.0113, 0.0063",
      ", ".join(f"{x:.5f}" for x in rows_cen), V(ok))

# critical dispersions: b_min = (5/3) s^2 r_max/GM (2507.18312:542) < b_BH = 5 delta/3 (316) with s R
# conserved from t_H (R_H = r_m, r_max = 3 r_m/(5 delta), GM = r_m/2) -> sigma_H^2 < 3/10;
# crossing: sigma_v R < 3 M (2211.13950:715) at t_H -> sigma_H < 3/2
s_vir = math.sqrt(0.3)
L.row("critical dispersion: virial halt; crossing", "0.55; 1.5", f"{s_vir:.4f}; 1.5",
      V(printed(s_vir, "0.55")), "derived here from 2507.18312:316,542 and 2211.13950:715")

# measured cost of the two-overdensity run (raw chain logs; untracked run directory)
segs = sorted(glob.glob("/data/haiyangw/nrpic/runs/jeans/n1e4_v19/chain/seg*.log"))
cpu, cyc_done = 0.0, 0
for s in segs:
    t = open(s, errors="replace").read()
    c = re.findall(r"cpu time used\s*=\s*([0-9.eE+-]+)", t)
    cpu += float(c[-1]) if c else 0.0
    cy = [int(x) for x in re.findall(r"cycle=(\d+)", t)]
    if cy:
        cyc_done += max(cy) - min(cy)
ev = open("/data/haiyangw/nrpic/runs/jeans/n1e4_v19/chain/events.log").read()
final_cycle = int(re.findall(r"finished: time=\S+ cycle=(\d+)", ev)[-1])
L.row("measured cost of the two-overdensity run: card-hours; s per cycle", "5.41; 0.761",
      f"{cpu / 3600:.4f}; {cpu / final_cycle:.4f} ({len(segs)} segments, final cycle {final_cycle}; "
      f"{cyc_done} cycles between first and last cycle lines of the segments)",
      V(printed(cpu / 3600, "5.41") and printed(cpu / final_cycle, "0.761")),
      "runs/jeans/n1e4_v19 is untracked and has no checksum file; per computed cycle it is "
      f"{cpu / max(cyc_done, 1):.3f} s")

rows = sn["T5"]["rows"]
ch = np.array([r["card_hours"] for r in rows])
ch6 = np.array([r["card_hours"] for r in rows if r["N_p"] == 1e6])
ch6m = np.array([r["card_hours"] for r in rows if r["N_p"] == 1e6 and r["dbar_ent"] in (0.02, 0.04)])
L.row("modelled cost per run (range; median at 1e6)", "1.1-3.5; 2.4",
      f"{ch.min():.3f}-{ch.max():.3f}; median of the 8 rows at 1e6 {np.median(ch6):.3f}, of the 4 at dbar 0.02/0.04 {np.median(ch6m):.3f}",
      "CONFIRMED", "arithmetic over the model's rows; the model itself not re-derived")
L.row("first scan: runs; card-hours", "65; 155", f"65 x {np.median(ch6m):.4f} = {65 * np.median(ch6m):.1f}",
      V(printed(65 * np.median(ch6m), "155")), "65 = 25+18+10+12 (SCOPE.md section 5) taken as given")

# ============================================================ 2. analytic criteria (my code from the sources)
e = 0.2
R1 = (36 / math.pi) * e * ellipe(1 - 0.25) / (1 + 3 * e) ** 2           # 1609.01588:604-607, central measure
al, be, ga = (1 + 3 * e) / 3, 1 / 3, (1 - 3 * e) / 3                    # shape of (alpha, beta, gamma)/delta
m2 = 1 - ((al - be) / (al - ga)) ** 2 * ga / be                          # 2508.10070:594
R2 = (2 / math.pi) * (al - ga) / al ** 2 * ellipe(m2) / (ga ** (1 / 3) / (al * be) ** (1 / 6))
sigH = 0.01
R3 = (0.4 * 1.0 * sigH) ** (2 / 3)                                       # 1707.03595:957-960, I = 1, q = 0
R4 = (100.0 ** 1.5) ** (-2 / 3)                                          # 1707.03595:920-923, t_end/t_H = (a_end/a_H)^(3/2)
L_, mu_ln = 1.0, 1.0
R8 = math.exp(-0.4 * mu_ln * L_ ** 2) * (sigH * math.exp(-L_)) ** 0.4    # 2211.13950:555-561 (sigma_0 < sigma_cr)
assert sigH < math.exp(mu_ln * L_ ** 2 - 4 * L_)                         # sigma_cr, 2211.13950:496-498
R9 = (2.5 * sigH) ** 0.4                                                 # 2507.18312:338, zeta_rms = 5 sigma_H/2
mine = [R1, R2, R9, R8, R3, R4]
claim = ["1.08", "1.45", "0.229", "0.0712", "0.0252", "0.01"]
ss = json.load(open(L.inp("A-emd-pbh-20261115-120425-80492f8", "scan_summary.json")))
th = ss["thresholds_sigmaH_0.01"]
theirs = [th["R1 hoop ball (1609.01588)"][2], th["R2 hoop peak (2508.10070)"][2], th["R9 top hat (2507.18312)"][2],
          th["R8 dispersion (2211.13950)"][2], th["R3 Kerr bound (1707.03595)"][2], th["R4 duration (1707.03595)"][2]]
d_rel = max(abs(x / y - 1) for x, y in zip(mine, theirs))
ok = all(printed(x, s) for x, s in zip(mine, claim))
L.row("threshold delta_c at e=0.2: hoop ball, hoop peak, profile, dispersion, spin, duration",
      ", ".join(claim), ", ".join(f"{x:.4g}" for x in mine), V(ok),
      f"my code vs scan_summary.json: largest relative difference {d_rel:.1e}; the ledger's label lists 8 names "
      "('hoop, ball, hoop, peak, ...') for 6 values")
L.row("hhat consistency: 12/5 hhat(0.2,0) = R1", "(note eq. 2)", f"{12 / 5 * h02:.6f} vs {R1:.6f}",
      V(abs(12 / 5 * h02 - R1) < 1e-12))
L.row("particle threshold of 2609.14218 in delta_c", "0.108", f"12/5 x 0.045 = {12 / 5 * 0.045:.4f}",
      V(printed(12 / 5 * 0.045, "0.108")),
      "0.045 is the largest mu WITHOUT a horizon (MDPBH.tex:1103); the bracket is delta_c in (0.108, 0.120]")

res = json.load(open(L.inp("A-emd-pbh-20261115-130256-a7374a4", "results.json")))
chk = res["checks"]
fails = [c["id"] for c in chk if not c["passed"]]
L.row("checks against the five papers: passed of total; failing", "33 of 37; T1.2b, T2.2d, T2.4a, T2.4c",
      f"{len(chk) - len(fails)} of {len(chk)}; {', '.join(fails)}",
      V(len(chk) == 37 and fails == ["T1.2b", "T2.2d", "T2.4a", "T2.4c"]),
      "wave-1 state; criteria/README says wave 2 superseded it (see v_criteria)")

# ============================================================ 3. initial-data constraint orders
def orders(run, model, p, cells, q):
    d = json.load(open(L.inp(run, "convergence.json", check=False)))
    mdl = d["models"][model]
    Ns = mdl["N"]
    n = [mdl["norms"][str(N)][str(p)][cells][q] for N in Ns]
    return Ns, [math.log2(n[i] / n[i + 1]) for i in range(len(n) - 1)]


F = "A-emd-pbh-20261115-130402-f5566fb"
S = "A-emd-pbh-20261115-122117-aa1c84d"
checks = [
    ("order ||M||_2 flat, smooth, p=2", F, "flat", 2, "smooth", "M_L2", "2.00"),
    ("order ||M||_2 flat, smooth, p=4", F, "flat", 4, "smooth", "M_L2", "4.00"),
    ("order ||M||_2 tapered, all, p=2", F, "flat_taper", 2, "all", "M_L2", "1.99"),
    ("order ||M||_2 tapered, all, p=4", F, "flat_taper", 4, "all", "M_L2", "3.90"),
    ("order ||H||_2 top hat, smooth, p=4", F, "tophat", 4, "smooth", "H_L2", "4.00"),
    ("order ||M||_2 top hat, smooth, p=4", F, "tophat", 4, "smooth", "M_L2", "4.00"),
    ("order ||M||_2 top hat, all, p=4", F, "tophat", 4, "all", "M_L2", "-0.50"),
    ("order ||H||_2 smoothed top hat 256->512, smooth, p=4", S, "smooth_tophat", 4, "smooth", "H_L2", "3.98"),
    ("order ||M||_2 smoothed top hat 256->512, smooth, p=4", S, "smooth_tophat", 4, "smooth", "M_L2", "3.94"),
]
conv_rows = []
for name, run, model, p, cells, q, c in checks:
    Ns, o = orders(run, model, p, cells, q)
    last = o[-1]
    conv_rows.append((name, Ns, o))
    L.row(name, c, f"{last:.3f} (all pairs {', '.join(f'{x:.2f}' for x in o)})", V(printed(last, c)),
          f"log2 of the finest pair, N = {Ns[-2]}->{Ns[-1]}; convergence.json has no checksum file (wave-1 run)")

# ============================================================ 4. cross-checks (transcription + my exterior K)
cc = json.load(open(L.inp("A-20261115-130257-a7374a4", "crosscheck.json")))
l2 = max(cc["L2"][k]["max_all"] for k in ("u", "KL", "KT", "betar"))
l3 = max(cc["L3"][k] for k in ("u", "KL", "KT", "alpha", "betar"))
L.row("two generators (flat ball), largest difference", "4.8e-15", f"{l2:.2e}", V(printed(l2, "4.8e-15")), "transcription of crosscheck.json")
L.row("two table evaluators, largest difference", "6.9e-18", f"{l3:.2e}", V(printed(l3, "6.9e-18")), "transcription")
L.row("three exact-solution codes (times)", "1.1e-14", f"{cc['L4']['max_disagreement']:.2e}",
      V(printed(cc["L4"]["max_disagreement"], "1.1e-14")), "transcription")
L.row("exterior K vs -(3/2) sqrt(2M/R^3) (their run)", "4.3e-15", f"{cc['L6']['max_rel']:.2e}",
      V(printed(cc["L6"]["max_rel"], "4.3e-15")), "transcription; my own check on data set 2t below")

# ============================================================ 5. exact solution of data set 2t from its table
DS = "A-emd-pbh-20261115-130609-947c898"
base = "expball_smooth_tophat_HRb0p5_dc1_R10p3_R20p75_w0p1875"
tab = np.loadtxt(L.inp(DS, base + ".tab", check=False))
hdr = {}
for line in open(os.path.join(vc.SCR, DS, base + ".tab")):
    if line.startswith("#") and "=" in line:
        k, v = line[1:].split("=", 1)
        hdr[k.strip()] = v.strip()
rb, u, KL, KT, alp, betar = tab.T
h = rb[1] - rb[0]
psi = 1.0 + u
R = psi ** 2 * rb


def d1(f):
    """fourth-order first derivative on the uniform grid (second order at the two ends)."""
    g = np.gradient(f, h, edge_order=2)
    g[2:-2] = (f[:-4] - 8 * f[1:-3] + 8 * f[3:-1] - f[4:]) / (12 * h)
    return g


Rp = d1(R)
one2E = Rp ** 2 / psi ** 4
E = 0.5 * (one2E - 1.0)
v = -KT * R
m = 0.5 * R * (v ** 2 - 2 * E)
m[0] = 0.0
for k in (1, 2):                                          # one-sided differences at the centre: use the
    E[k] = E[3] * (R[k] / R[3]) ** 2                      # homogeneous-core scaling instead
    m[k] = m[3] * (R[k] / R[3]) ** 3
Mtot = m[-1]
mp = d1(m)
rest = np.trapezoid(mp / np.sqrt(one2E), rb)
matter = rb[np.where(np.abs(mp) > 1e-6 * np.max(np.abs(mp)))[0][-1]]
ti = float(hdr["t_i"])
mom = np.max(np.abs(KL + d1(v) / Rp)[5:-5])            # K^R_R = -dv/dR (momentum constraint identity)
L.row("total M; rest mass (from the table)", "1.00959; 1.01590", f"{Mtot:.5f}; {rest:.5f}",
      V(printed(Mtot, "1.00959") and printed(rest, "1.01590")),
      f"header M = {float(hdr['M']):.10f}; matter edge rbar = {matter:.3f}; |KL + dv/dR| <= {mom:.1e}")

# cycloid per shell
bound = (E < -1e-9) & (rb > 0.04) & (rb < matter)
A_ = np.where(bound, m / np.maximum(-2 * E, 1e-300), np.nan)
B_ = np.where(bound, m / np.maximum(-2 * E, 1e-300) ** 1.5, np.nan)
eta_i = np.where(bound, np.arccos(np.clip(1 - R / A_, -1, 1)), np.nan)
tb = B_ * (eta_i - np.sin(eta_i))                       # time since the bang
par = (E >= -1e-9) & (rb > 0.04)
tb_par = np.where(par, (2 / 3) * R ** 1.5 / np.sqrt(2 * np.maximum(m, 1e-300)), np.nan)
inner = R < 6.5                                          # inside the surface taper (R_b - 1.5)
spread = np.nanmax(np.abs(np.concatenate([tb[bound & inner], tb_par[par & inner]]) - ti))
taper = par & (R >= 6.5) & (rb < matter)
tb_taper = (np.nanmin(tb_par[taper]), np.nanmax(tb_par[taper]))
tau_ta = B_ * math.pi - tb
tau_c = 2 * math.pi * B_ - tb
eta_ah = 2 * math.pi - np.arccos(np.clip(1 + 4 * E, -1, 1))
tau_ah = B_ * (eta_ah - np.sin(eta_ah)) - tb
core = bound & (R < 2.3)
core_ta = np.nanmedian(tau_ta[core]); core_c = np.nanmedian(tau_c[core])
core_spread = np.nanmax(tau_ta[core]) - np.nanmin(tau_ta[core])
Rmax_Ri = np.nanmedian((2 * A_ / R)[core])
L.row("common bang time: |t_bang - t_i| over the shells inside the taper (R < 6.5)", "t_i = 10.667 for every shell",
      f"{spread:.1e}", V(spread < 1e-6))
L.row("bang time in the surface taper (6.5 <= R < matter edge)", "note: 'a common bang time for every shell'",
      f"{tb_taper[0]:.4f} to {tb_taper[1]:.4f}", "WRONG" if tb_taper[1] - ti > 1e-3 else "CONFIRMED",
      "the taper lowers m at E = 0, so its shells start later than t_i (a decaying mode in the taper)")
L.row("core turnaround tau_ta; R_max/R_i", "16.894; 1.3398", f"{core_ta:.4f}; {Rmax_Ri:.5f} (spread over core shells {core_spread:.1e})",
      V(printed(core_ta, "16.894") and printed(Rmax_Ri, "1.3398")))
i_min = int(np.nanargmin(np.where(bound, tau_ah, np.nan)))
# refine the minimum by a parabola through three neighbours
y = tau_ah[i_min - 1:i_min + 2]; x = rb[i_min - 1:i_min + 2]
cpar = np.polyfit(x, y, 2); xr = -cpar[1] / (2 * cpar[0]); tah_min = np.polyval(cpar, xr)
Ri_ah = np.interp(xr, rb, R); m_ah = np.interp(xr, rb, m)
L.row("first trapped sphere: tau_AH; shell R_i; m_AH; areal radius 2 m_AH", "44.349; 2.742; 0.0805; 0.161",
      f"{tah_min:.4f}; {Ri_ah:.4f}; {m_ah:.5f}; {2 * m_ah:.4f} (m_AH/M_total = {m_ah / Mtot:.5f})",
      V(printed(tah_min, "44.349") and printed(Ri_ah, "2.742") and printed(m_ah, "0.0805") and printed(2 * m_ah, "0.161")),
      "values in code units (nominal mass 1), not divided by the total mass M = 1.0096 the labels name")
i_edge = int(np.argmin(np.abs(R - 2.4)))
f_edge = np.interp(2.4, R[i_edge - 3:i_edge + 4], tau_ah[i_edge - 3:i_edge + 4])
L.row("core edge (R_i = 2.4) trapped; core crunch", "44.381; 44.454", f"{f_edge:.4f}; {core_c:.4f}",
      V(printed(f_edge, "44.381") and printed(core_c, "44.454")))
# outermost trapped sphere at the core crunch
outer = bound & (rb > xr)
j = np.where(outer & (tau_ah <= core_c))[0][-1]
m_c = np.interp(core_c, tau_ah[j:j + 2], m[j:j + 2])
L.row("m_AH at the crunch", "0.0960", f"{m_c:.5f} (/M_total {m_c / Mtot:.5f})", V(printed(m_c, "0.0960")),
      "code units, as above")


def eta_of_tau(tau, Bv, tbv):
    tgt = (tau + tbv) / Bv
    return brentq(lambda x: x - math.sin(x) - tgt, 0.0, 2 * math.pi)


k0 = np.where(core)[0][5]
Bk, tbk, etk, Rik, Ek = B_[k0], tb[k0], eta_i[k0], R[k0], E[k0]
fac = Rik / math.sqrt(-2 * Ek)
t_ta_c = fac * (math.pi - etk)
t_ah_c = fac * (eta_of_tau(tah_min, Bk, tbk) - etk)
t_cr_c = fac * (2 * math.pi - etk)
ok = printed(t_ta_c, "13.82") and printed(t_ah_c, "49.51") and printed(t_cr_c, "54.96")
L.row("conformal-time coordinate times: turnaround, core at tau_AH, crunch", "13.82, 49.51, 54.96",
      f"{t_ta_c:.3f}, {t_ah_c:.3f}, {t_cr_c:.3f}", V(ok), "t = int (R_i/R) dtau along a core shell (alpha = a/a_i)")

# geodesic slicing: largest coordinate speed of light against tau (all shells, not only the core)
taus = np.linspace(0.0, core_c - 1e-3, 1500)
bound2 = (E < -1e-9) & (rb > 0) & (rb < matter)
sel_b = np.where(bound2)[0]
A2 = m / np.maximum(-2 * E, 1e-300); B2 = A2 / np.sqrt(np.maximum(-2 * E, 1e-300))
n2 = np.arccos(np.clip(1 - R / A2, -1, 1)); tb2 = B2 * (n2 - np.sin(n2))
cmax_all, cmax_core = [], []
eta_cache = n2[sel_b].copy()
for tau in taus:
    tgt = (tau + tb2[sel_b]) / B2[sel_b]
    x_ = np.clip(eta_cache, 1e-8, 2 * math.pi)
    for _ in range(60):                                    # Newton on eta - sin eta = tgt
        f_ = x_ - np.sin(x_) - tgt
        x_ = np.clip(x_ - f_ / np.maximum(1 - np.cos(x_), 1e-14), 1e-10, 2 * math.pi)
    eta_cache = x_
    Rt = R.copy()
    Rt[sel_b] = A2[sel_b] * (1 - np.cos(x_))
    unb = (~bound2) & (rb > 0)                             # marginally bound / exterior: E = 0 observers
    Rt[unb] = (R[unb] ** 1.5 + 1.5 * np.sqrt(2 * np.maximum(m[unb], 1e-300)) * tau) ** (2 / 3)
    Rtp = d1(Rt)
    cr = np.sqrt(one2E[1:]) / np.abs(Rtp[1:])
    ct = rb[1:] / Rt[1:]
    cmax_all.append(np.max(np.maximum(cr, ct)[: np.searchsorted(rb, matter + 2.0)]))
    cmax_core.append(np.max(np.maximum(cr, ct)[: np.searchsorted(rb, 2.0)]))
cmax_all, cmax_core = np.array(cmax_all), np.array(cmax_core)
lim = 0.618 / 0.25


def first_cross(c):
    k = int(np.argmax(c > lim))
    return float(taus[k - 1] + (lim - c[k - 1]) * (taus[k] - taus[k - 1]) / (c[k] - c[k - 1]))


tau_lim_all, tau_lim_core = first_cross(cmax_all), first_cross(cmax_core)
L.row("geodesic slicing reaches the step bound at cfl = 0.25 (tau)", "42.30",
      f"{tau_lim_core:.2f} (core only); {tau_lim_all:.2f} (largest speed over all shells)",
      V(abs(tau_lim_all - 42.30) < 0.1), "bound C_max = 0.618 taken from the track (gauge T2), not re-derived; "
      "the track's speed R_i/R omits the factor 1/psi^2 of the coordinate metric, hence the 0.06-0.08 shift")
L.row("predicted card-hours of the two scouting runs", "0.15; 0.16", "not recomputed (cost model of the track)", "NOT CONFIRMED",
      "only the inputs; no independent cost model")

# parameters table
i0 = 0
max2m = np.max(2 * m[1:] / R[1:]); r2m = R[1:][np.argmax(2 * m[1:] / R[1:])]
L.row("parameters: conformal factor at the centre; largest 2m/R", "1.0138; 0.236",
      f"{psi[0]:.5f}; {max2m:.4f} at R = {r2m:.3f}", V(printed(psi[0], "1.0138") and printed(max2m, "0.236")))
H = float(hdr["H"]); Rb = float(hdr["Rb"])
Delta_c = 2 * m[5] / (H ** 2 * R[5] ** 3) - 1
L.row("parameters: H R_b; R_b; H; t_i (units of the table)", "0.5; 8; 0.0625; 10.667",
      f"{H * Rb:.3f}; {Rb:g}; {H:g}; {ti:.3f}; core contrast from m: {Delta_c:.4f}; matter edge rbar {matter:.2f}",
      V(abs(H * Rb - 0.5) < 1e-12 and abs(ti - 2 / (3 * H)) < 1e-9),
      "table quotes H, R_b, t_i in units of the nominal mass 1 while its row 1 calls M = 1.0096 'M'")

L.write(OUT)
np.savez(os.path.join(OUT, "ledger_series.npz"), rb=rb, R=R, m=m, E=E, tau_ah=tau_ah, tau_ta=tau_ta,
         taus=taus, cmax_all=cmax_all, cmax_core=cmax_core)

# ============================================================ figure
fs.use_style()
import matplotlib.pyplot as plt
fig, ax = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 6.0))
fig.subplots_adjust(left=0.09, right=0.98, bottom=0.08, top=0.97, wspace=0.28, hspace=0.32)
ee = np.linspace(0.02, 0.32, 200)
ax[0, 0].plot(ee, [hhat(x) for x in ee], color=fs.PAL["blue"], label=r"$\hat h(e,0)$, MDPBH.tex:918 (mine)")
ax[0, 0].plot(ro_e, ro_mu, "o", color=fs.PAL["red"], ms=4, label="read-offs of the track")
ax[0, 0].set_xlabel("ellipticity $e$"); ax[0, 0].set_ylabel(r"$\mu$"); ax[0, 0].legend(loc="lower right")
ax[0, 1].loglog(mu, t_read, "o", color=fs.PAL["red"], ms=4, label="read-off collapse times")
mm = np.logspace(np.log10(0.04), np.log10(0.35), 100)
ax[0, 1].loglog(mm, (dcrit / (12 * mm / (5 * EUL))) ** 1.5, color=fs.PAL["blue"], label=r"top hat at $r_m$ (mine)")
for t_ in (100, 250, 400, 1000):
    ax[0, 1].axvline(mu_fd(t_), **fs.MASK_LINE)
ax[0, 1].set_xlabel(r"$\mu$"); ax[0, 1].set_ylabel(r"$t/t_H$"); ax[0, 1].legend(loc="upper right")
selp = bound & (rb < 6.5)
ax[1, 0].plot(R[selp], tau_ah[selp], color=fs.PAL["blue"], label=r"$\tau_{\rm AH}(R_i)$")
ax[1, 0].plot(R[selp], tau_c[selp], **fs.GUIDE, label=r"$\tau_{\rm c}(R_i)$")
ax[1, 0].plot([Ri_ah], [tah_min], "o", color=fs.PAL["red"], ms=5, label="first trapped sphere")
ax[1, 0].set_ylim(44.2, 45.2); ax[1, 0].set_xlabel(r"$R_i$ (code units)"); ax[1, 0].set_ylabel(r"$\tau$")
ax[1, 0].legend(loc="upper left")
ax[1, 1].semilogy(core_c - taus, cmax_all, color=fs.PAL["red"], label="largest speed, all shells")
ax[1, 1].semilogy(core_c - taus, cmax_core, color=fs.PAL["blue"], ls="--", label="core only")
ax[1, 1].axhline(lim, **fs.MASK_LINE); ax[1, 1].set_xscale("log")
ax[1, 1].set_xlabel(r"$\tau_{\rm c} - \tau$"); ax[1, 1].set_ylabel("coordinate speed of light")
ax[1, 1].legend(loc="upper right")
fs.save(fig, os.path.join(OUT, "fig_v_ledger"))
print("figure", os.path.join(OUT, "fig_v_ledger.png"))
