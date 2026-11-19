"""G1 verifier, C18 part 2: the analytic-criteria package (criteria/), recomputed.

(1) the tallies of the check runs (wave 1 and wave 2) from their results.json;
(2) printed values of the papers at the cited locators (read in the sources);
(3) my own evaluation of the closed forms behind a subset of checks and of the prediction
    rows (R1, R2, R3, R4, R5, R7, R8, R9) at the scan's three ellipticities, against
    scan_summary.json and example_tables.txt;
(4) the amplitude measures of wave 2 (delta_c = 12 mu/5, deltabar = 12 mu/(5e), C_max).
Usage: python v_criteria.py [--out DIR]
"""
import argparse
import json
import math
import os
import re

import numpy as np
from scipy.integrate import quad, solve_ivp
from scipy.special import ellipe

import vcommon as vc
from vcommon import fs

ap = argparse.ArgumentParser()
ap.add_argument("--out", default=None)
a = ap.parse_args()
OUT = a.out or vc.outdir("criteria")
os.makedirs(OUT, exist_ok=True)
L = vc.Ledger("criteria")
EUL = math.e


def V(ok):
    return "CONFIRMED" if ok else "WRONG"


def src(arx, ver, f):
    return open(os.path.join(vc.KB, arx, ver, "src", f), errors="replace").read().split("\n")


# ------------------------------------------------------------------ (1) tallies
def tally(run):
    d = json.load(open(L.inp(run, "results.json", check=False)))
    c = d["checks"]
    boo = [x for x in c if isinstance(x["passed"], bool)]
    return c, boo, [x["id"] for x in boo if not x["passed"]], [x["id"] for x in c if x["passed"] is None]


for run, claim_n, claim_f in (("A-emd-pbh-20261115-115120-2eb3117", 37, ["T1.2b", "T2.2d", "T2.4a", "T2.4c"]),
                              ("A-emd-pbh-20261115-130256-a7374a4", 37, ["T1.2b", "T2.2d", "T2.4a", "T2.4c"])):
    c, boo, f, diag = tally(run)
    L.row(f"wave-1 tally {run}", f"{claim_n} checks, failing {claim_f}", f"{len(boo)} checks, failing {f}",
          V(len(boo) == claim_n and f == claim_f))
c1, b1, f1, d1 = tally("A-emd-pbh-20261115-161813-6c820fb")
L.row("wave-2 full run -161813-6c820fb", "40 checks, 3 failed (T2.6a-c); 4 diagnostics",
      f"{len(b1)} checks, failed {f1}; diagnostics {d1}", V(len(b1) == 40 and f1 == ["T2.6a", "T2.6b", "T2.6c"] and len(d1) == 4))
c2, b2, f2, d2 = tally("A-emd-pbh-20261115-163358-9b2d048")
L.row("wave-2 T2 rerun -163358-9b2d048", "17 checks, 0 failed", f"{len(b2)} checks, failed {f2}", V(len(b2) == 17 and not f2))
union = [x for x in b1 if not x["id"].startswith("T2")] + b2
nf = [x["id"] for x in union if not x["passed"]]
L.row("current state (T2 from the rerun, the rest from the full run)", "41 checks pass, 4 diagnostics",
      f"{len(union)} checks, {len(union) - len(nf)} pass; failing {nf}", V(len(union) == 41 and not nf),
      "the note (Sec. III E, ledger) still quotes the wave-1 state 33 of 37")

# ------------------------------------------------------------------ (2)+(3) papers and closed forms
s1609 = src("1609.01588", "v2", "apj_nonsphericalpbh.tex")
s1707 = src("1707.03595", "v4", "Spin_PBH.tex")
s2211 = src("2211.13950", "v3", "MD_threshold10.tex")
s2507 = src("2507.18312", "v3", "Main.tex")
s2508 = src("2508.10070", "v1", "main.tex")
L.row("printed values at the locators", "1609:764 0.05556; 771 0.01338, 0.1280; 1341 Ebar 1.182; 1707:1338-1346 1.921e-7, 0.1474, 3.244e-14, 0.004608",
      "; ".join([str("0.05556" in s1609[763]), str("0.01338" in s1609[770] and "0.1280" in s1609[770]),
                 str("1.182" in s1609[1340]), str("1.921" in s1707[1337] and "0.1474" in s1707[1338]),
                 str("3.244" in s1707[1344] and "0.004608" in s1707[1345])]),
      V("0.05556" in s1609[763] and "0.01338" in s1609[770] and "1.182" in s1609[1340]
        and "1.921" in s1707[1337] and "3.244" in s1707[1344]))

# Ebar (1609.01588:766-767) and c of beta0 = c sigma^5 (1332)
Ebm5 = 1.5 * quad(lambda u: (1 - 2 * u) * (1 + 2 * u) * ellipe(1 - (u + 0.5) ** 2) ** -5, -0.5, 0.5, epsabs=1e-14, epsrel=1e-13)[0]
Ebar = Ebm5 ** -0.2
c_beta = 7 * 5 ** 3 * math.pi ** 4.5 / (2 ** 9 * 3 ** 6 * math.sqrt(10)) * Ebm5
L.row("T1.2a/b: Ebar; c in beta0 = c sigma^5", "Ebar 1.1817 (paper 1.182); c 0.05555 (paper 0.05556)",
      f"{Ebar:.7f}; {c_beta:.10f}", V(abs(Ebar - 1.18166) < 2e-5 and abs(c_beta - 0.0555550) < 1e-6),
      "c rounds to 0.05556 only via 0.0555550; the code's 0.05555 is the correct 4-digit rounding")
K = 5 * math.sqrt(5) * math.pi ** 4 / 6 ** 9            # 1707.03595 semianalytic_anisotropy_threshold
pre2 = K * Ebm5 * 0.4 ** 6
pre1 = K * Ebm5 * (12 / 125) ** 9
pre1_1182 = K * 1.182 ** -5 * (12 / 125) ** 9
L.row("T2.2: prefactors of beta0(2), beta0(1); exponents", "1.921e-7, 3.244e-14 (paper); 0.1474, 0.004608",
      f"{pre2:.4e}, {pre1:.4e} (with Ebar = 1.182: {pre1_1182:.4e}); {0.5 * 0.4 ** (4 / 3):.4f}, {(12 / 125) ** 2 / 2:.6f}",
      V(abs(pre2 / 1.921e-7 - 1) < 3e-4 and abs(pre1_1182 / 3.244e-14 - 1) < 3e-4),
      "confirms the track's explanation of T2.2d: the paper used Ebar = 1.182 for the second prefactor only")
# T3.1 sigma_cr (2211.13950:496-498)
L.row("T3.1 sigma_cr(mu=1, ln kmin/k=1)", "e^-3", f"{math.exp(1 - 4):.6f}", "CONFIRMED", "closed form")


# T4.1 exact top hat with a pure growing mode: a_max delta and R_max/r_m (2507.18312:304-316)
def tophat(delta):
    """shell of comoving radius r_m = 1 in EdS with a(t) = (3t/2)^(2/3) (H0 r_m = 1 at a = 1);
    growing mode at a_i = 1e-4: R = a r (1 - delta_lin(a)/3), delta_lin = delta a."""
    ai = 1e-4
    ti = (2 / 3) * ai ** 1.5
    Hi = (2 / 3) / ti
    dl = delta * ai
    R0 = ai * (1 - dl / 3)
    v0 = Hi * ai * (1 - 2 * dl / 3)                                  # growing mode: d delta/dt = H delta
    GM = 0.5 * Hi ** 2 * ai ** 3                                     # GM = H^2 R^3/2 of the background = 1/2
    Eb = 0.5 * v0 ** 2 - GM / R0
    A = GM / (-2 * Eb); B = GM / (-2 * Eb) ** 1.5
    eta0 = math.acos(1 - R0 / A); tb = B * (eta0 - math.sin(eta0))
    t_ta = ti + B * math.pi - tb
    return 2 * A, (1.5 * t_ta) ** (2 / 3)


ok = True
outs = []
for d in (1e-3, 1e-2):
    Rmax, amax = tophat(d)
    outs.append(f"delta {d:g}: R_max delta = {Rmax * d:.5f} (3/5 = 0.6), a_max delta = {amax * d:.5f}")
    ok &= abs(Rmax * d / 0.6 - 1) < 2e-3 and abs(amax * d / (0.15 * (6 * math.pi) ** (2 / 3)) - 1) < 2e-3
L.row("T4.1 exact top hat: R_max = 3 r_m/(5 delta), a_max = 1.06/delta", "a_max delta 1.0624",
      "; ".join(outs) + f"; limit (3/20)(6 pi)^(2/3) = {0.15 * (6 * math.pi) ** (2 / 3):.5f}", V(ok),
      "my cycloid from growing-mode data at a_i = 1e-4")


# prediction rows at e = 0, 0.1, 0.2 against scan_summary.json
def R1(e, p=0.0):
    if e == 0:
        return 0.0
    return (36 / math.pi) * e * ellipe(1 - (e + p) ** 2 / (4 * e * e)) / (1 + 3 * e + p) ** 2


def R2(e, p=0.0):
    if e == 0:
        return 0.0
    al, be, ga = (1 + 3 * e + p) / 3, (1 - 2 * p) / 3, (1 - 3 * e + p) / 3
    m2 = 1 - ((al - be) / (al - ga)) ** 2 * ga / be
    return (2 / math.pi) * (al - ga) / al ** 2 * ellipe(m2) / (ga ** (1 / 3) / (al * be) ** (1 / 6))


ss = json.load(open(L.inp("A-emd-pbh-20261115-120425-80492f8", "scan_summary.json")))
th = ss["thresholds_sigmaH_0.01"]
r1 = [R1(e) for e in (0, 0.1, 0.2)]
r2 = [R2(e) for e in (0, 0.1, 0.2)]
d1_ = max(abs(x - y) for x, y in zip(r1, th["R1 hoop ball (1609.01588)"]))
d2_ = max(abs(x - y) for x, y in zip(r2, th["R2 hoop peak (2508.10070)"]))
L.row("R1, R2 at e = 0, 0.1, 0.2 (scan_summary.json)", "0, 0.821, 1.084; 0, 0.926, 1.452",
      f"{', '.join(f'{x:.4f}' for x in r1)}; {', '.join(f'{x:.4f}' for x in r2)}", V(d1_ < 1e-12 and d2_ < 1e-12),
      f"largest differences {d1_:.1e}, {d2_:.1e}")
grid_e = np.linspace(0, 0.25, 126)[1:]          # the e grid of the track's figure (126 points)
ratio = np.array([R2(e) / R1(e) for e in grid_e])
pr = ss["peak_over_ball_hoop_ratio_range"]
L.row("R2/R1 over e in (0, 0.25], p = 0", f"{pr[0]:.4f}-{pr[1]:.4f}", f"{ratio.min():.4f}-{ratio.max():.4f}",
      V(abs(ratio.min() - pr[0]) < 1e-9 and abs(ratio.max() - pr[1]) < 1e-9),
      "the lower end is the first grid point (the ratio tends to 1 as e -> 0)")
# R5 exact top hat: a at R = 2M (= r_m) for delta = 0.1 and 0.3 (example_tables.txt: 16.69, 5.276; a_max 10.62, 3.541)


def tophat_events(delta):
    ai = 1e-5
    ti = (2 / 3) * ai ** 1.5
    Hi = (2 / 3) / ti
    dl = delta * ai
    R0 = ai * (1 - dl / 3); v0 = Hi * ai * (1 - 2 * dl / 3)
    GM = 0.5 * Hi ** 2 * ai ** 3
    Eb = 0.5 * v0 ** 2 - GM / R0
    A = GM / (-2 * Eb); B = GM / (-2 * Eb) ** 1.5
    eta0 = math.acos(1 - R0 / A); tb = B * (eta0 - math.sin(eta0))
    eta_bh = 2 * math.pi - math.acos(1 - 2 * GM / A)      # R = 2 GM on the way in
    t_bh = ti + B * (eta_bh - math.sin(eta_bh)) - tb
    t_ta = ti + B * math.pi - tb
    return (1.5 * t_bh) ** (2 / 3), (1.5 * t_ta) ** (2 / 3), 2 * GM


ex = open(L.inp("A-emd-pbh-20261115-120425-80492f8", "example_tables.txt")).read()
got = []
for d, s_bh, s_ta in ((0.1, "16.69", "10.62"), (0.3, "5.276", "3.541"), (0.03, "56.13", "35.41")):
    abh, ata, rs = tophat_events(d)
    got.append((d, abh, ata, s_bh, s_ta))
okr5 = all(f"R = 2M at a/a_H = {s_bh}" in ex and abs(abh / float(s_bh) - 1) < 2e-3 and abs(ata / float(s_ta) - 1) < 2e-3
           for d, abh, ata, s_bh, s_ta in got)
L.row("R5 exact top hat: a/a_H at R = 2M and at turnaround, delta = 0.1, 0.3, 0.03", "16.69, 10.62; 5.276, 3.541; 56.13, 35.41",
      "; ".join(f"{abh:.3f}, {ata:.3f}" for d, abh, ata, _, _ in got), V(okr5),
      "R = 2GM = r_m with GM = R_H/2 at a = 1 (2507.18312:310-316); my cycloid")
# R3, R4, R8, R9 at sigma_H = 0.01
L.row("R3, R4, R8, R9 at sigma_H = 0.01 (a_end/a_H = 100 for R4)", "0.0252, 0.01, 0.0712, 0.229",
      f"{(0.004) ** (2 / 3):.4f}, {0.01:.2f}, {math.exp(-0.4) * (0.01 / EUL) ** 0.4:.4f}, {(0.025) ** 0.4:.4f}",
      V(abs(th["R3 Kerr bound (1707.03595)"][0] - 0.004 ** (2 / 3)) < 1e-12
        and abs(th["R8 dispersion (2211.13950)"][0] - math.exp(-0.4) * (0.01 / EUL) ** 0.4) < 1e-12
        and abs(th["R9 top hat (2507.18312)"][0] - 0.025 ** 0.4) < 1e-12))
# R6, R7 critical dispersions
L.row("R6, R7 critical sigma_v,H", "1.5; 0.548", f"1.5; {math.sqrt(0.3):.4f}",
      V(abs(ss["critical_sigv_H"]["2507.18312"] - math.sqrt(0.3)) < 1e-12 and ss["critical_sigv_H"]["2211.13950"] == 1.5))
# spin a*(2) at delta = 0.1, sigma_H = 0.01 (example table: 0.126) and R9 spin zeta^2/delta^(5/2) (0.198)
L.row("spins at delta = 0.1, sigma_H = 0.01: a*(2); zeta^2/delta^(5/2)", "0.126; 0.198",
      f"{0.4 * 0.01 * 0.1 ** -1.5:.4f}; {0.025 ** 2 / 0.1 ** 2.5:.4f}",
      V(abs(0.4 * 0.01 * 0.1 ** -1.5 - 0.126) < 6e-4 and abs(0.025 ** 2 / 0.1 ** 2.5 - 0.198) < 6e-4),
      "1707.03595:904-906; 2507.18312:630-631 as the README states them")

# ------------------------------------------------------------------ (4) amplitude measures (MDPBH.tex:839, 709-714)
mu = 0.1
k = 1.0
rm = math.sqrt(6) / k
zeta = lambda r: mu * math.exp(-k * k * r * r / 6)          # spherical part of zeta = 2 ln Psi
dzeta = lambda r: -mu * (k * k * r / 3) * math.exp(-k * k * r * r / 6)
lap0 = -mu * k * k                                         # lap of mu exp(-k^2 r^2/6) at 0 = 3 f''(0)
delta_c = -(2 / 5) * rm ** 2 * lap0


def dlin(r):                                              # -(2/5) r_m^2 lap zeta(r)
    f = math.exp(-k * k * r * r / 6)
    lap = mu * f * ((k * k * r / 3) ** 2 - k * k)
    return -(2 / 5) * rm ** 2 * lap


mean = 3 / rm ** 3 * quad(lambda r: dlin(r) * r * r, 0, rm, epsabs=1e-15)[0]
L.row("amplitude measures: delta_c/mu; deltabar/mu; ratio", "12/5; 12/(5e); e",
      f"{delta_c / mu:.12f}; {mean / mu:.12f}; {delta_c / mean:.12f}",
      V(abs(delta_c / mu - 2.4) < 1e-12 and abs(mean / mu - 12 / (5 * EUL)) < 1e-10),
      "volume mean of the linear contrast inside r_m by quadrature")
L.row("particle bracket and hoop line in the mean measure", "0.0397; 0.399",
      f"{12 * 0.045 / (5 * EUL):.4f}; {R1(0.2) / EUL:.4f}",
      V(abs(12 * 0.045 / (5 * EUL) - 0.0397) < 5e-5 and abs(R1(0.2) / EUL - 0.399) < 5e-4))
cm = lambda m_: (3 / 5) * (1 - (1 - 2 * m_ / EUL) ** 2)
L.row("C_max at mu = 0.32, 0.33, 0.5", "0.2493, 0.2560, 0.3603", f"{cm(0.32):.4f}, {cm(0.33):.4f}, {cm(0.5):.4f}",
      V(abs(cm(0.33) - 0.25599) < 1e-4 and abs(cm(0.5) - 0.36025) < 1e-4), "(3/5)[1 - (1 + r zeta')^2] at r_m, r_m zeta'(r_m) = -2 mu/e")
L.write(OUT)

# ------------------------------------------------------------------ figure: thresholds against e, my code and the track's
fs.use_style()
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.2))
fig.subplots_adjust(left=0.08, right=0.98, bottom=0.15, top=0.95, wspace=0.28)
ee = np.linspace(0.005, 0.3, 300)
ax[0].plot(ee, [R1(e) for e in ee], color=fs.PAL["blue"], label="R1 hoop, ball (mine)")
ax[0].plot(ee, [R2(e) for e in ee], color=fs.PAL["green"], label="R2 hoop, peak (mine)")
ax[0].plot([0, 0.1, 0.2], th["R1 hoop ball (1609.01588)"], "o", color=fs.PAL["red"], ms=4, label="track, scan_summary")
ax[0].plot([0, 0.1, 0.2], th["R2 hoop peak (2508.10070)"], "s", color=fs.PAL["red"], ms=4)
for y, lab in ((0.004 ** (2 / 3), "R3"), (math.exp(-0.4) * (0.01 / EUL) ** 0.4, "R8"), (0.025 ** 0.4, "R9"), (0.01, "R4")):
    ax[0].axhline(y, **fs.MASK_LINE); ax[0].text(0.285, y * 1.08, lab, fontsize=8, color="grey")
ax[0].plot([0.2], [0.108], "*", color="k", ms=8, label="2609.14218 particles")
ax[0].set_yscale("log"); ax[0].set_xlabel("ellipticity $e$"); ax[0].set_ylabel(r"threshold $\delta_c$")
ax[0].set_ylim(5e-3, 30); ax[0].legend(loc="upper left", fontsize=8, ncol=2)
uu = np.linspace(-0.5, 0.5, 400)
ax[1].plot(uu, [(1 - 2 * u) * (1 + 2 * u) * ellipe(1 - (u + 0.5) ** 2) ** -5 for u in uu], color=fs.PAL["blue"])
ax[1].set_xlabel("$u$"); ax[1].set_ylabel(r"integrand of $\bar E^{-5}$ (1609.01588:766)")
ax[1].text(-0.45, 0.05, rf"$\bar E$ = {Ebar:.6f}, c = {c_beta:.7f}", fontsize=9)
fs.save(fig, os.path.join(OUT, "fig_v_criteria"))
print("figure", os.path.join(OUT, "fig_v_criteria.png"))
