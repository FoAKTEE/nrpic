#!/usr/bin/env python3
"""The zeta reader of G3 (SCOPE 4d.1 (ii), 4d.9 A3) and its tests on the 32^3 mirrored pairs.

    zeta_reader.py OUT --run <dir of E-20261125-153148-cfad424> --deck <usr_base.athinput>
                   [--ref8 <ref_inflection_n8.json>] [--msteps 4000]

zeta(x) = -1/2 ln(chi/<chi>) + DN(phi(x), v(x)) - <DN>, v = dphi/dN = Pi / H_cell, H_cell = -K/3 (alpha = 1 on the
geodesic slice: checked), DN(phi, v) the e-folds of a homogeneous Friedmann-Klein-Gordon universe (G = 1, the
deck's potential, H^2 = 8 pi V / (3 - 4 pi v^2)) from (phi, v) to phi_e, phi_e the background field at
N_e = N* + 15 (own integration from the deck's phi0, pi0 at N*, t = 0, a = 1).
Reader map: classical RK4 in phi as the independent variable, y = (N, v), dN/dphi = 1/v,
dv/dphi = -(3 - 4 pi v^2)(v + V'/(8 pi V)) / v, a fixed number of steps per cell from phi to phi_e, all cells at once.
Independent map (Z1): scipy DOP853 in cosmic time t for (phi, Pi, ln a), H from Friedmann, an event at phi_e.

Tests (SCOPE 4d.9 A3; predictions zeta/JOURNAL.md entry 4, g3/JOURNAL.md entry 4):
Z0  rms(O_zeta + O_R)/rms(O_R) at s = 1/4 (O = [X(+) - X(-)]/2, R = R^NR of read_seed.r_nr), bar 1e-3.
Z1  five-point first and second coefficients of the reader's map against DOP853 at the background state of N_f
    along phi, along Pi and along the box's (d phi, d Pi) relation, eps = box rms; bar 1 per cent.
Z2  a = slope of E - <E> on O^2 - <O^2> for zeta at s = 1/4 and 1/2 (within 2 per cent); (iii) a_zeta against the
    independent map's a_map = (1/2) N'' / N'^2 along the box relation (2 per cent, as written); (iii') against
    a_map - a_R, a_R of R^NR on the same pairs (0.5 per cent; entry 4).
LM  the TO VERIFY of 4d.3: deck parameters and background landmarks against sdn/models.HiggsInflection and
    sdn/linear.ClassicalBackground (phi0 = -1.2, N* - N0 = 3) mapped to code units.
A4p the box's d phi at N_f against the 8-band reference (variance, intrinsic skewness of the pair).
Writes OUT/zeta_tests.json, OUT/fig_zeta_tests.png (and .pdf).
"""
import argparse
import glob
import json
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

HERE = os.path.dirname(os.path.abspath(__file__))
TRK = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(TRK, "g3"))
sys.path.insert(0, os.path.join(TRK, "ladder", "scripts"))
sys.path.insert(0, os.path.join(TRK, "langevin"))
sys.path.insert(0, os.path.abspath(os.path.join(TRK, "..", "..", "python")))
import ladder_lib as LL  # noqa: E402
from read_seed import r_nr, sigma_lin_of  # noqa: E402
from power import amplitude_grid  # noqa: E402
from nrpic import figstyle  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("out")
ap.add_argument("--run", required=True)
ap.add_argument("--deck", required=True)
ap.add_argument("--ref8", default=None)
ap.add_argument("--msteps", type=int, default=4000)
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
PI4, PI8 = 4.0 * np.pi, 8.0 * np.pi
SQ2 = np.sqrt(2.0)


def deck_value(path, block, key):
    blk = None
    for line in open(path):
        s = line.split("#")[0].strip()
        if s.startswith("<"):
            blk = s.strip("<>")
        elif "=" in s and blk == block and s.split("=")[0].strip() == key:
            return float(s.split("=")[1])
    raise KeyError(key)


LAM = deck_value(a.deck, "scalar_field", "lambda")
VEV = deck_value(a.deck, "scalar_field", "vev")
PHI0 = deck_value(a.deck, "problem", "phi0")
PI0 = deck_value(a.deck, "problem", "pi0")
TLIM = deck_value(a.deck, "time", "tlim")


def V(p):   # the code's inflection form (athenak/src/scalar_field/scalar_field.hpp lines 57-58)
    return LAM * VEV**4 * p**2 * (3 * p**2 + 2 * SQ2 * p * VEV + 6 * VEV**2) / (3.0 * (3 * p**2 + 2 * VEV**2)**2)


def dV(p):  # derivative of V, written out (checked against a central difference below)
    P = 3 * p**2 + 2 * SQ2 * p * VEV + 6 * VEV**2
    Q = 3 * p**2 + 2 * VEV**2
    dP = 6 * p + 2 * SQ2 * VEV
    dQ = 6 * p
    num = 2 * p * P + p**2 * dP
    return LAM * VEV**4 * (num * Q - 2 * p**2 * P * dQ) / (3.0 * Q**3)


# ------------------------------------------------------------ background in code units (own, t-integration)
def bg_rhs(t, y):
    p, pi, lna = y
    H = np.sqrt(PI8 / 3.0 * (0.5 * pi**2 + V(p)))
    return [pi, -3 * H * pi - dV(p), H]


BG = solve_ivp(bg_rhs, (0.0, 80.0), [PHI0, PI0, 0.0], method="DOP853", rtol=1e-13, atol=1e-16,
               dense_output=True)


def t_of_N(Nc):
    return brentq(lambda t: BG.sol(t)[2] - Nc, 0.0, 80.0, xtol=1e-14)


def bg_at_N(Nc):
    t = t_of_N(Nc)
    p, pi, _ = BG.sol(t)
    return t, p, pi, np.sqrt(PI8 / 3.0 * (0.5 * pi**2 + V(p)))


NSTAR, NF_C, NE_C = 3.0, 10.0, 15.0           # code N counts from N* (a* = 1)
PHI_E = bg_at_N(NE_C)[1]


# ------------------------------------------------------------ the reader's map: RK4 in phi
def map_rk4(phi, v, m=a.msteps):
    phi = np.asarray(phi, float)
    v = np.asarray(v, float).copy()
    h = (PHI_E - phi) / m
    N = np.zeros_like(phi)
    p = phi.copy()

    def f(p, v):
        return 1.0 / v, -(3.0 - PI4 * v * v) * (v + dV(p) / (PI8 * V(p))) / v
    for _ in range(m):
        k1n, k1v = f(p, v)
        k2n, k2v = f(p + 0.5 * h, v + 0.5 * h * k1v)
        k3n, k3v = f(p + 0.5 * h, v + 0.5 * h * k2v)
        k4n, k4v = f(p + h, v + h * k3v)
        N += h / 6 * (k1n + 2 * k2n + 2 * k3n + k4n)
        v += h / 6 * (k1v + 2 * k2v + 2 * k3v + k4v)
        p += h
    return N


# ------------------------------------------------------------ the independent map: DOP853 in t with an event
def map_dop(phi, pi):
    ev = lambda t, y: y[0] - PHI_E  # noqa: E731
    ev.terminal = True
    r = solve_ivp(bg_rhs, (0.0, 1e4), [phi, pi, 0.0], method="DOP853", rtol=1e-13, atol=1e-18, events=ev)
    return float(r.y_events[0][0][2])


# second independent map (batch 20, zeta/JOURNAL.md entry 6): DOP853 in N on (x = phi - phi_e, v) with an event at
# x = 0; the first one (in t, N = ln a at the event) has a floor near 1e-10 in N that the second coefficient
# along Pi alone (1.3e-9 in N at eps = box rms) does not clear.
def map_dopN(phi, pi):
    H = np.sqrt(PI8 / 3.0 * (0.5 * pi**2 + V(phi)))

    def rhs(N, y):
        x, v = y
        p = x + PHI_E
        return [v, -(3.0 - PI4 * v * v) * (v + dV(p) / (PI8 * V(p)))]
    ev = lambda N, y: y[0]  # noqa: E731
    ev.terminal = True
    r = solve_ivp(rhs, (0.0, 1e3), [phi - PHI_E, pi / H], method="DOP853", rtol=3e-14, atol=1e-24, events=ev)
    return float(r.t_events[0][0])


# map_dopN at rtol 3e-14 took over ten minutes for 25 states (run E-20261125-161757-fb0eb95, stopped); at 1e-13 one
# call needs 3.4e6 evaluations (40 s). Off by default; the *_N fields then repeat the first map's.
USE_DOPN = os.environ.get("ZETA_USE_DOPN", "0") == "1"


# ------------------------------------------------------------ dumps
VARS = ["phi", "Pi", "chi", "K", "alpha"]


def last(member):
    f = sorted(glob.glob(os.path.join(a.run, member, "*.sf.*.dump")))[-1]
    h, d = LL.read_dump(f, VARS)
    return f, h, d


def zeta_of(d):
    H = -d["K"] / 3.0
    v = d["Pi"] / H
    assert np.all(v > 0), "a cell rolls backwards: the map in phi does not apply"
    dn = map_rk4(d["phi"].ravel(), v.ravel()).reshape(d["phi"].shape)
    z = -0.5 * np.log(d["chi"] / d["chi"].mean()) + dn
    return z - z.mean(), v


def slope(E, O):
    q = O**2 - np.mean(O**2)
    E = E - E.mean()
    return float(np.sum(E * q) / np.sum(q * q))


def skew(x):
    c = x - x.mean()
    return float(np.mean(c**3) / np.mean(c**2)**1.5)


res = dict(deck=dict(lam=LAM, vev=VEV, phi0=PHI0, pi0=PI0, tlim=TLIM), phi_e=PHI_E, msteps=a.msteps)
# dV check
pp = np.linspace(-0.2, -0.03, 7)
res["dV_check_max_rel"] = float(np.max(np.abs((V(pp + 1e-7) - V(pp - 1e-7)) / 2e-7 / dV(pp) - 1)))
# the deck's tlim is N_f
res["N_at_tlim"] = float(BG.sol(TLIM)[2])

pairs = {}
for tag, s, plus, minus in (("q", 0.25, "zp4", "zm4"), ("h", 0.5, "zp2", "zm2")):
    fp, hp, dp = last(plus)
    fm, hm, dm = last(minus)
    zp, vp = zeta_of(dp)
    zm, vm = zeta_of(dm)
    Rp = r_nr(fp, 2)[0]
    Rm = r_nr(fm, 2)[0]
    Oz, Ez = 0.5 * (zp - zm), 0.5 * (zp + zm)
    OR, ER = 0.5 * (Rp - Rm), 0.5 * (Rp + Rm)
    Op = 0.5 * (dp["phi"] - dm["phi"])
    Ep = 0.5 * (dp["phi"] + dm["phi"])
    OP = 0.5 * (dp["Pi"] - dm["Pi"])
    alpha_dev = max(float(np.max(np.abs(dp["alpha"] - 1))), float(np.max(np.abs(dm["alpha"] - 1))))
    rec = dict(s=s, time=hp["time"], files=[fp, fm], alpha_max_dev=alpha_dev,
               Z0=float(np.sqrt(np.mean((Oz + OR)**2)) / np.sqrt(np.mean(OR**2))),
               sigma_Oz=float(Oz.std()), sigma_OR=float(OR.std()), sigma_Ophi=float(Op.std()), sigma_OPi=float(OP.std()),
               a_zeta=slope(Ez, Oz), a_R=slope(ER, OR),
               slope_dPi_on_dphi=float(np.sum(Op * OP) / np.sum(Op * Op)),
               corr_dphi_dPi=float(np.corrcoef(Op.ravel(), OP.ravel())[0, 1]),
               skew_Ophi=skew(Op), intrinsic_skew_phi_s1=float(3 * np.mean(Op**2 * (Ep - Ep.mean())) / Op.std()**3 / s),
               intrinsic_skew_zeta_s1=float(3 * np.mean(Oz**2 * (Ez - Ez.mean())) / Oz.std()**3 / s),
               var_dphi_plus=float(dp["phi"].var()), var_dphi_minus=float(dm["phi"].var()),
               mean_phi=float(0.5 * (dp["phi"].mean() + dm["phi"].mean())), mean_Pi=float(0.5 * (dp["Pi"].mean() + dm["Pi"].mean())),
               mean_H=float(-0.5 * (dp["K"].mean() + dm["K"].mean()) / 3.0),
               v_min=float(min(vp.min(), vm.min())))
    pairs[tag] = rec
    pairs[tag + "_arrays"] = (Oz, Ez, OR, ER)
    print(tag, {k: v for k, v in rec.items() if k != "files"}, flush=True)
res["pairs"] = {k: v for k, v in pairs.items() if not k.endswith("_arrays")}

# ------------------------------------------------------------ Z1 at the background state of N_f
tf, pf, pif, Hf = bg_at_N(NF_C)
res["bg_Nf"] = dict(t=tf, phi=pf, Pi=pif, H=Hf, v=pif / Hf, x_from_inflection=pf + SQ2 * VEV)
q = pairs["q"]
sl = q["slope_dPi_on_dphi"]
eps_p = q["sigma_Ophi"] / 0.25          # box rms at s = 1 (the run's amplitude)
eps_P = q["sigma_OPi"] / 0.25
z1 = {}
# Pi_x10, Pi_x100: diagnostics (not judged): the second coefficient along Pi alone is 1e-9 in N at eps = box rms,
# near the precision of the two integrators; a larger step shows whether a disagreement is that floor.
for lab, (ep, eP) in {"phi": (eps_p, 0.0), "Pi": (0.0, eps_P), "box": (eps_p, eps_p * sl),
                      "Pi_x10": (0.0, 10 * eps_P), "Pi_x100": (0.0, 100 * eps_P)}.items():
    js = np.array([-2, -1, 0, 1, 2], float)
    ph = pf + js * ep
    pi = pif + js * eP
    Hs = np.sqrt(PI8 / 3.0 * (0.5 * pi**2 + V(ph)))   # a homogeneous state: Friedmann H
    nr = map_rk4(ph, pi / Hs)
    nd = np.array([map_dop(x, y) for x, y in zip(ph, pi)])
    nN = nd if not USE_DOPN else np.array([map_dopN(x, y) for x, y in zip(ph, pi)])
    c1 = lambda n: (-n[4] + 8 * n[3] - 8 * n[1] + n[0]) / 12.0  # noqa: E731  (per unit step)
    c2 = lambda n: (-n[4] + 16 * n[3] - 30 * n[2] + 16 * n[1] - n[0]) / 12.0  # noqa: E731
    z1[lab] = dict(eps_phi=ep, eps_Pi=eP, N0_reader=float(nr[2]), N0_dop=float(nd[2]),
                   c1_reader=float(c1(nr)), c1_dop=float(c1(nd)), c2_reader=float(c2(nr)), c2_dop=float(c2(nd)),
                   rel_c1=float(c1(nr) / c1(nd) - 1), rel_c2=float(c2(nr) / c2(nd) - 1),
                   a_map_dop=float(0.5 * c2(nd) / c1(nd)**2), a_map_reader=float(0.5 * c2(nr) / c1(nr)**2),
                   c1_dopN=float(c1(nN)), c2_dopN=float(c2(nN)), rel_c1_N=float(c1(nr) / c1(nN) - 1),
                   rel_c2_N=float(c2(nr) / c2(nN) - 1), N0_dopN=float(nN[2]))
    print("Z1", lab, z1[lab], flush=True)
res["Z1"] = z1
res["Z1_pass"] = bool(all(abs(z1[k]["rel_c1"]) < 0.01 and abs(z1[k]["rel_c2"]) < 0.01 for k in ("phi", "Pi", "box")))
res["Z1_pass_dopN"] = bool(all(abs(z1[k]["rel_c1_N"]) < 0.01 and abs(z1[k]["rel_c2_N"]) < 0.01 for k in ("phi", "Pi", "box")))
res["Z1_pass_phi_box"] = bool(all(abs(z1[k]["rel_c1"]) < 0.01 and abs(z1[k]["rel_c2"]) < 0.01 for k in ("phi", "box")))
res["Z0_pass"] = bool(pairs["q"]["Z0"] < 1e-3)
a_map = z1["box"]["a_map_dop"]
aq, ah = pairs["q"]["a_zeta"], pairs["h"]["a_zeta"]
aRq = pairs["q"]["a_R"]
res["Z2"] = dict(a_q=aq, a_h=ah, ratio=ah / aq, a_map=a_map, iii=aq / a_map - 1,
                 iii_prime=(aq - (a_map - aRq)) / a_map, a_R=aRq,
                 pass_i=bool(abs(ah / aq - 1) < 0.02), pass_iii=bool(abs(aq / a_map - 1) < 0.02),
                 pass_iii_prime=bool(abs((aq - (a_map - aRq)) / a_map) < 0.005))

# ------------------------------------------------------------ LM: the TO VERIFY of 4d.3
from sdn import models, linear  # noqa: E402
mdl = models.HiggsInflection()
dpdN, H0 = models.h0_fixing(mdl, -1.2)
rbg = linear.ClassicalBackground(mdl, -1.2, dpdN, N0=0.0, Nstar=3.0, N_extra=250.0)
phs, ws = rbg.state(3.0)
Hs_ref = rbg.H(3.0)
S8 = np.sqrt(PI8)
lm = dict(H_star_ref=Hs_ref, vev_pred=0.198 / S8, vev_rel=VEV / (0.198 / S8) - 1,
          lam_pred=PI8 * 1.86e-6 / Hs_ref**2, lam_rel=LAM / (PI8 * 1.86e-6 / Hs_ref**2) - 1,
          phi0_pred=phs / S8, phi0_rel=PHI0 / (phs / S8) - 1,
          pi0_pred=ws / Hs_ref / S8, pi0_rel=PI0 / (ws / Hs_ref / S8) - 1)


def lnd_eps1_code(Nc, h=1e-4):
    def e1(n):
        _, p, pi, H = bg_at_N(n)
        return PI4 * pi**2 / H**2
    return (np.log(e1(Nc + h)) - np.log(e1(Nc - h))) / (2 * h)


def lnd_eps1_ref(N, h=1e-4):
    return (np.log(rbg.eps1(N + h)) - np.log(rbg.eps1(N - h))) / (2 * h)


marks = {}
for lab, val, lo, hi in (("eps2=0 up", 0.0, 0.5, 3.0), ("eps2=3 up (USR onset)", -3.0, 1.8, 3.5),
                         ("eps2=3 down (USR end)", -3.0, 5.0, 7.5), ("eps2=0 down", 0.0, 7.0, 9.5)):
    nc = brentq(lambda n: lnd_eps1_code(n) - val, lo, hi, xtol=1e-10)
    nr_ = brentq(lambda n: lnd_eps1_ref(n) - val, lo + 3.0, hi + 3.0, xtol=1e-10)
    marks[lab] = dict(N_code_plus_3=nc + 3.0, N_ref=nr_, diff=nr_ - (nc + 3.0))
nc = brentq(lambda n: bg_at_N(n)[1] + SQ2 * VEV, 3.0, 6.0, xtol=1e-12)
nr_ = brentq(lambda n: rbg.state(n)[0] + SQ2 * 0.198, 6.0, 9.0, xtol=1e-12)
marks["inflection point"] = dict(N_code_plus_3=nc + 3.0, N_ref=nr_, diff=nr_ - (nc + 3.0))
lm["landmarks"] = marks
lm["max_abs_diff_N"] = float(max(abs(m["diff"]) for m in marks.values()))
lm["pass"] = bool(lm["max_abs_diff_N"] < 1e-4 and max(abs(lm[k]) for k in ("vev_rel", "lam_rel", "phi0_rel", "pi0_rel")) < 1e-6)
res["LM"] = lm
print("LM", lm, flush=True)

# ------------------------------------------------------------ A4 preview against the 8-band reference
# sigma_lin of the 32^3 run from its own record (the record carries s: R32) and the Gaussian sample scatter of
# one box's variance, rel = sqrt(2 sum m^2) / sum m over the full grid (m = |W R|^2 L^-3 per mode)
fq = pairs["q"]["files"][0]
sl_q, md_q = sigma_lin_of(fq[:-len(".dump")] + ".modes", 32)
amp_q, _ = amplitude_grid(md_q, 32)
wq = np.full(amp_q.shape, 2.0)
wq[:, :, 0] = 1.0
wq[:, :, -1] = 1.0
mq = amp_q**2
res["box32"] = dict(sigma_lin_record_q=sl_q, sigma_lin_s1=sl_q / 0.25, sigma_OR_over_sigma_lin=pairs["q"]["sigma_OR"] / sl_q,
                    rel_scatter_box_variance=float(np.sqrt(2 * np.sum(wq * mq**2)) / np.sum(wq * mq)))
print("box32", res["box32"], flush=True)
if a.ref8:
    r8 = json.load(open(a.ref8))
    st = r8["s0.01_lattice"]["state_Nf"]
    var_ref_code = st["var_phi"] / PI8
    box_var = 0.5 * (pairs["q"]["var_dphi_plus"] + pairs["q"]["var_dphi_minus"]) / 0.25**2
    res["A4p"] = dict(var_box_s1=box_var, var_ref_code=var_ref_code, ratio=box_var / var_ref_code,
                      skew_ref_phi=st["skew_phi"], se_skew_ref_phi=st["moments_phi"]["se_skew"],
                      intrinsic_skew_box_phi=pairs["q"]["intrinsic_skew_phi_s1"],
                      skew_ref_dN=r8["s0.01_lattice"]["Ne"]["skew"], se_skew_ref_dN=r8["s0.01_lattice"]["Ne"]["se_skew"],
                      intrinsic_skew_box_zeta=pairs["q"]["intrinsic_skew_zeta_s1"],
                      var_ref_dN=r8["s0.01_lattice"]["Ne"]["var"], var_box_zeta_s1=pairs["q"]["sigma_Oz"]**2 / 0.25**2)
    print("A4p", res["A4p"], flush=True)

json.dump(res, open(os.path.join(a.out, "zeta_tests.json"), "w"), indent=1)

# ------------------------------------------------------------ figure
figstyle.use_style()
fig = plt.figure(figsize=(figstyle.FULL_WIDTH, 2.8))
a1 = figstyle.inch_axes(fig, 0.65, 0.5, 2.1, 2.1)
a2 = figstyle.inch_axes(fig, 3.35, 0.5, 2.1, 2.1)
a3 = figstyle.inch_axes(fig, 6.05, 0.5, 1.9, 2.1)
Oz, Ez, OR, ER = pairs["q_arrays"]
sel = np.random.default_rng(0).choice(Oz.size, 4000, replace=False)
a1.plot(-OR.ravel()[sel], Oz.ravel()[sel], ".", ms=1.0, color=figstyle.PAL["red"])
lim = np.max(np.abs(OR))
a1.plot([-lim, lim], [-lim, lim], **figstyle.GUIDE)
a1.set_xlabel(r"$-O_{\mathcal{R}}$ ($s=1/4$)")
a1.set_ylabel(r"$O_\zeta$")
a1.text(0.05, 0.9, f"Z0 = {pairs['q']['Z0']:.1e}", transform=a1.transAxes, fontsize=7)
for tag, col in (("q", figstyle.PAL["red"]), ("h", figstyle.PAL["yellow"])):
    Oz_, Ez_, _, _ = pairs[tag + "_arrays"]
    qq = (Oz_**2 - np.mean(Oz_**2)).ravel()
    ee = (Ez_ - Ez_.mean()).ravel()
    sc = (pairs[tag]["s"] / 0.25)**2
    a2.plot(qq[sel] / sc, ee[sel] / sc, ".", ms=1.0, color=col, label=f"$s={pairs[tag]['s']}$")
xx = np.linspace(*a2.get_xlim(), 3)
a2.plot(xx, a_map * xx, color=figstyle.PAL["blue"], lw=1.0, label=r"$a_\mathrm{map}$ (DOP853)")
a2.plot(xx, (a_map - aRq) * xx, color=figstyle.PAL["blue"], lw=1.0, ls="--", label=r"$a_\mathrm{map}-a_\mathcal{R}$")
a2.set_xlabel(r"$(O_\zeta^2-\langle O_\zeta^2\rangle)/(4s)^2$")
a2.set_ylabel(r"$E_\zeta/(4s)^2$")
a2.legend(loc="upper left", fontsize=6.5)
labs = list(z1.keys())
a3.semilogy(range(len(labs)), [max(abs(z1[k]["rel_c1"]), 1e-16) for k in labs], "o", color=figstyle.PAL["red"], label="first")
a3.semilogy(np.arange(len(labs)) + 0.15, [max(abs(z1[k]["rel_c2"]), 1e-16) for k in labs], "s", color=figstyle.PAL["yellow"], label="second")
a3.axhline(0.01, **figstyle.MASK_LINE)
a3.set_xticks(range(len(labs)))
a3.set_xticklabels([l.replace("_", "\n") for l in labs], fontsize=6)
a3.minorticks_off()
a3.set_ylabel("Z1: |reader/DOP853 - 1|")
a3.legend(loc="lower right", fontsize=6.5)
figstyle.save(fig, os.path.join(a.out, "fig_zeta_tests"))
fig.savefig(os.path.join(a.out, "fig_zeta_tests.png"), dpi=150)
print("Z0", res["Z0_pass"], "Z1", res["Z1_pass"], "Z2", res["Z2"], flush=True)
