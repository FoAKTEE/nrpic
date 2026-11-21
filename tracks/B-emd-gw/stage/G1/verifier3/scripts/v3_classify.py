#!/usr/bin/env python3
"""Numbers for the classification of the waves/README claims (JOURNAL entry 10), from my
own per-dump measurements (v3_dumps.json of run B-20261121-025826-80973e3).

1. Test F, the forward combination of the TT route, Z_F = (Z_h + i Z_h'/w)/2 (removes the
   backward discrete wave; the README measures W = P + i P'/|k|): amplitude and phase
   errors at the last dump, Z_F against spectral and FD6 Psi_4 (final and max over t), the
   polarization ratio Z_x/Z_+ against 0.5 e^{i} (max over t of modulus and argument), the
   error at t = 0, local orders.
2. Test F, my own symbol-plus-integrator prediction of the forward error: eigenvalue
   lambda = -i w_sd - sigma, w_sd from the sixth-order second-derivative symbol, Kreiss-Oliger
   rate sigma = diss sum_a sin^8(theta_a / 2) / h (diss = 0.5, nghost 4), amplification
   R(z) = 1 + z + z^2/2 + z^3/6 + z^4/24 (every 4-stage 4th-order RK on a linear autonomous
   system), steps dt = cfl h with a shortened last step (cycle count of the last dump).
3. Test X: polarization ratio, plus/cross; the late-time power law of the F non-TT norm.
Writes $NRPIC_RUN_DIR/v3_classify.json.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import exact  # noqa: E402

OUT = os.environ.get("NRPIC_RUN_DIR", os.path.join(HERE, "..", "results", "tmp_v3c"))
os.makedirs(OUT, exist_ok=True)
D = json.load(open(os.environ["V3_DUMPS"]))
dumps = D["dumps"]


def cx(p):
    return complex(p[0], p[1])


def sym6(theta):
    return (49.0 / 18.0 - 3.0 * np.cos(theta) + 0.3 * np.cos(2 * theta)
            - (2.0 / 90.0) * np.cos(3 * theta))


def order(e1, e2, n1, n2):
    return float(np.log(abs(e1) / abs(e2)) / np.log(n2 / n1))


fw = exact.FlatWave()
res = {"F": {}, "X": {}}
Ns = (16, 32, 48, 64)
fin = {}
for N in Ns:
    S = [d for d in dumps if d["case"] == "F" and d["N"] == N]
    t = np.array([d["t"] for d in S])
    rec = {}
    ZF, ZW, ZW6 = {}, {}, {}
    for p, nm in ((0, "+"), (1, "x")):
        Zex = np.array([fw.complex_amp(tt)[p] for tt in t])
        Zh = np.array([cx(d["TT"][p]) for d in S])
        Zd = np.array([cx(d["TTdot"][p]) for d in S])
        ZF[p] = (Zh + 1j * Zd / fw.w) / 2
        ZW[p] = np.array([cx(d["Wsp"][p]) for d in S])
        ZW6[p] = np.array([cx(d["Wfd6"][p]) for d in S])
        r = ZF[p] / Zex
        rec[f"TTfwd {nm}"] = {"amp_err_final": float(abs(r[-1]) - 1), "phase_err_final": float(np.angle(r[-1])),
                              "t0 |Z/Zex - 1|": float(abs(r[0] - 1))}
        dsp = np.abs(ZF[p] - ZW[p]) / np.abs(Zex)
        d6 = np.abs(ZF[p] - ZW6[p]) / np.abs(Zex)
        rec[f"TTfwd-Wsp {nm}"] = {"final": float(dsp[-1]), "max": float(dsp.max())}
        rec[f"TTfwd-Wfd6 {nm}"] = {"final": float(d6[-1]), "max": float(d6.max())}
        r6 = ZW6[p] / Zex
        rec[f"Wfd6 {nm}"] = {"amp_err_final": float(abs(r6[-1]) - 1), "phase_err_final": float(np.angle(r6[-1]))}
    ratio = ZF[1] / ZF[0] / (0.5 * np.exp(1j))
    rec["ratio x/+ vs 0.5e^i"] = {"max |mod-1|": float(np.max(np.abs(np.abs(ratio) - 1))),
                                  "max |arg|": float(np.max(np.abs(np.angle(ratio))))}
    ratio_h = np.array([cx(d["TT"][1]) for d in S]) / np.array([cx(d["TT"][0]) for d in S]) / (0.5 * np.exp(1j))
    rec["ratio x/+ (h only) vs 0.5e^i"] = {"max |mod-1|": float(np.max(np.abs(np.abs(ratio_h) - 1))),
                                           "max |arg|": float(np.max(np.abs(np.angle(ratio_h))))}
    # my predictor
    h = 1.0 / N
    th = fw.K * h
    w_sd = np.sqrt(np.sum(sym6(th))) / h
    sigma = 0.5 * np.sum(np.sin(th / 2) ** 8) / h
    lam = -1j * w_sd - sigma
    ncyc = S[-1]["cycle"]
    dt = 0.25 * h
    dt_last = t[-1] - (ncyc - 1) * dt

    def R(z):
        return 1 + z + z ** 2 / 2 + z ** 3 / 6 + z ** 4 / 24

    G = R(lam * dt) ** (ncyc - 1) * R(lam * dt_last)
    Gex = np.exp(-1j * fw.w * t[-1])
    rec["prediction"] = {"cycles": ncyc, "dt": dt, "dt_last": float(dt_last), "w_sd/w - 1": float(w_sd / fw.w - 1),
                         "sigma": float(sigma), "amp_err": float(abs(G) - 1),
                         "phase_err": float(np.angle(G / Gex)),
                         "KO only amp": float(np.exp(-sigma * t[-1]) - 1),
                         "semi-discrete phase only": float((fw.w - w_sd) * t[-1])}
    pr = rec["prediction"]
    m = rec["TTfwd +"]
    rec["measured/predicted"] = {"amp": m["amp_err_final"] / pr["amp_err"], "phase": m["phase_err_final"] / pr["phase_err"]}
    # non-TT late-time exponent
    nt = np.array([d["nonTT_frac"] for d in S])
    sel = t > 0.5 * t[-1]
    rec["nonTT exponent (t > t_end/2)"] = float(np.polyfit(np.log(t[sel]), np.log(nt[sel]), 1)[0])
    rec["nonTT exponent (all t > 0)"] = float(np.polyfit(np.log(t[1:]), np.log(nt[1:]), 1)[0])
    res["F"][N] = rec
    fin[N] = rec
orders = {}
for key in ("amp_err_final", "phase_err_final"):
    v = [fin[N]["TTfwd +"][key] for N in Ns]
    orders[f"TTfwd + {key}"] = [order(v[i], v[i + 1], Ns[i], Ns[i + 1]) for i in range(3)]
    v = [fin[N]["Wfd6 +"][key] for N in Ns]
    orders[f"Wfd6 + {key}"] = [order(v[i], v[i + 1], Ns[i], Ns[i + 1]) for i in range(3)]
v = [fin[N]["TTfwd-Wfd6 +"]["final"] for N in Ns]
orders["TTfwd-Wfd6 + final"] = [order(v[i], v[i + 1], Ns[i], Ns[i + 1]) for i in range(3)]
res["F"]["orders"] = orders

for case in ("X", "X10"):
    for N in (16, 32, 48, 64):
        S = [d for d in dumps if d["case"] == case and d["N"] == N]
        if not S:
            continue
        eps = D["eps"][case]
        xw = exact.ExpandingWave(eps_p=eps[0], eps_x=eps[1])
        kn = xw.kn
        Z = {}
        for p in (0, 1):
            H = np.array([cx(d["TT_h"][p]) for d in S])
            Hd = np.array([cx(d["TT_hd"][p]) for d in S])
            Z[p] = (H.real + 1j * Hd.real / kn) / eps[p]
        ratio = Z[1] / Z[0]
        res["X"][f"{case} N{N}"] = {"max_t>0 |arg(Zx/Z+)|": float(np.max(np.abs(np.angle(ratio[1:])))),
                                    "max_t>0 ||Zx/Z+|-1|": float(np.max(np.abs(np.abs(ratio[1:]) - 1))),
                                    "final arg": float(np.angle(ratio[-1])),
                                    "final |.|-1": float(abs(ratio[-1]) - 1)}

with open(os.path.join(OUT, "v3_classify.json"), "w") as fh:
    json.dump(res, fh, indent=1)
print(json.dumps(res, indent=1))
