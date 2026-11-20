#!/usr/bin/env python3
"""V3 of verifier3: measure tests F and X from the raw dumps with my own readers and
diagnostics (JOURNAL entry 5, predictions P3.1-P3.7).

Per dump: mode coefficients at K of the TT route (Lambda(gt - delta), Lambda(-2 alpha At)),
of the Weyl route with spectral and with sixth-order derivatives (F: Psi_4 along khat;
X: h, h' inverted from E_+, E_x, B_+, B_x), the background of X, non-TT and off-mode
fractions. Writes $NRPIC_RUN_DIR/v3_dumps.json (raw per-dump numbers); the summary and the
figures are made by v3_summary.py from that file.
Environment: V3_WORKERS (default 5), V3_CASES (default "F,X,X10").
"""
import glob
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import diag  # noqa: E402
import exact  # noqa: E402

OUT = os.environ.get("NRPIC_RUN_DIR", os.path.join(HERE, "..", "results", "tmp_v3"))
os.makedirs(OUT, exist_ok=True)
SCR = "/data/haiyangw/nrpic/scratch/B-emd-gw"
RUNS = {
    "F": [(16, "B-20261119-142016-ee73a03", "N16"), (32, "B-20261119-142016-ee73a03", "N32"),
          (48, "B-20261119-142233-70d5043", "N48"), (64, "B-20261119-142124-feb2daf", "flatN64")],
    "X": [(16, "B-20261119-142021-8f4c441", "N16"), (32, "B-20261119-142021-8f4c441", "N32"),
          (48, "B-20261119-142234-85da208", "N48"), (64, "B-20261119-142124-feb2daf", "expN64")],
    "X10": [(64, "B-20261119-155758-458cf17", "expN64x10")],
}
EPS = {"X": (2e-6, 1e-6), "X10": (2e-5, 1e-5)}
EYE = np.eye(3)[:, :, None, None, None]


def c2(z):
    return [float(np.real(z)), float(np.imag(z))]


def do_F(path):
    d = diag.read_bin(path)
    g, t = d["grid"], d["time"]
    gam, K, alp, chi, gt, At, trK = diag.z4c_to_adm(d)
    fw = exact.FlatWave()
    m = (1, 1, 1)
    hTT = diag.tt_project(gt - EYE, g)
    dTT = diag.tt_project(-2.0 * alp * At, g)
    out = {"t": t, "cycle": d["cycle"]}
    hp, hx = diag.pol_components(hTT, fw.K)
    dp, dx = diag.pol_components(dTT, fw.K)
    ch = [diag.mode_coeff(q, g, m) for q in (hp, hx)]
    cd = [diag.mode_coeff(q, g, m) for q in (dp, dx)]
    out["TT"] = [c2(2j * c) for c in ch]
    out["TTdot"] = [c2(2j * c) for c in cd]
    # forward/backward split: c_h = F + B, c_hd = -i w (F - B)
    out["backward_frac"] = [float(abs((c - 1j * cdd / fw.w) / 2) / abs((c + 1j * cdd / fw.w) / 2))
                            for c, cdd in zip(ch, cd)]
    full = gt - EYE
    out["nonTT_frac"] = float(np.sqrt(np.mean((full - hTT) ** 2) / np.mean(hTT ** 2)))
    # TT power outside the mode +-K
    mode = np.zeros_like(hTT)
    X = g.coords()
    ph = fw.K[0] * X[0] + fw.K[1] * X[1] + fw.K[2] * X[2]
    for a in range(3):
        for b in range(3):
            cab = diag.mode_coeff(hTT[a, b], g, m)
            mode[a, b] = 2 * np.real(cab * np.exp(1j * ph))
    out["offmode_frac"] = float(np.sqrt(np.mean((hTT - mode) ** 2) / np.mean(hTT ** 2)))
    for lab, der in (("Wsp", "spectral"), ("Wfd6", "fd6")):
        E, B = diag.weyl_EB(gam, K, g, deriv=der)
        p4 = diag.psi4(E, B, gam, fw.K)
        p4r = diag.psi4(E, B, gam, -fw.K)
        zp = 2j * diag.mode_coeff(-p4.real / fw.w ** 2, g, m)
        zx = 2j * diag.mode_coeff(p4.imag / fw.w ** 2, g, m)
        out[lab] = [c2(zp), c2(zx)]
        out[lab + "_rev_over_fwd"] = float(np.sqrt(np.mean(np.abs(p4r) ** 2) / np.mean(np.abs(p4) ** 2)))
    return out


def do_X(path, eps):
    d = diag.read_bin(path)
    g, t = d["grid"], d["time"]
    gam, K, alp, chi, gt, At, trK = diag.z4c_to_adm(d)
    xw = exact.ExpandingWave(eps_p=eps[0], eps_x=eps[1])
    m = (1, 1, 0)
    kn = xw.kn
    eph = np.exp(-1j * xw.phi_x)
    out = {"t": t, "cycle": d["cycle"]}
    out["bg"] = {"chi_mean": float(chi.mean()), "chi_rms_dev": float(chi.std()),
                 "alpha_mean": float(alp.mean()), "alpha_rms_dev": float(alp.std()),
                 "trK_mean": float(trK.mean()), "trK_rms_dev": float(trK.std()),
                 "Theta_max": float(np.max(np.abs(d["vars"]["z4c_Theta"])))}
    calH = -float(alp.mean()) * float(trK.mean()) / 3.0
    out["calH_num"] = calH
    hTT = diag.tt_project(gt - EYE, g)
    dTT = diag.tt_project(-2.0 * alp * At, g)
    hp, hx = diag.pol_components(hTT, xw.K)
    dp, dx = diag.pol_components(dTT, xw.K)
    H = [2 * diag.mode_coeff(hp, g, m), 2 * diag.mode_coeff(hx, g, m) * eph]
    Hd = [2 * diag.mode_coeff(dp, g, m), 2 * diag.mode_coeff(dx, g, m) * eph]
    out["TT_h"] = [c2(z) for z in H]
    out["TT_hd"] = [c2(z) for z in Hd]
    full = gt - EYE
    trace_part = np.einsum("aa...->...", full)
    out["nonTT_frac"] = float(np.sqrt(np.mean((full - hTT) ** 2) / np.mean(hTT ** 2)))
    out["trace_rms"] = float(np.sqrt(np.mean(trace_part ** 2)))
    mode = np.zeros_like(hTT)
    X = g.coords()
    ph = xw.K[0] * X[0] + xw.K[1] * X[1] + xw.K[2] * X[2]
    for a in range(3):
        for b in range(3):
            cab = diag.mode_coeff(hTT[a, b], g, m)
            mode[a, b] = 2 * np.real(cab * np.exp(1j * ph))
    out["offmode_frac"] = float(np.sqrt(np.mean((hTT - mode) ** 2) / np.mean(hTT ** 2)))
    for lab, der in (("Wsp", "spectral"), ("Wfd6", "fd6")):
        E, B = diag.weyl_EB(gam, K, g, deriv=der)
        Ep, Ex = diag.pol_components(E, xw.K)
        Bp, Bx = diag.pol_components(B, xw.K)
        cE = [2 * diag.mode_coeff(Ep, g, m), 2 * diag.mode_coeff(Ex, g, m)]
        cB = [2 * diag.mode_coeff(Bp, g, m), 2 * diag.mode_coeff(Bx, g, m)]
        hdp = cB[1] * (2j / kn)
        hdx = cB[0] * (-2j / kn)
        hpW = (2 * cE[0] - calH * hdp) / kn ** 2
        hxW = (2 * cE[1] - calH * hdx) / kn ** 2
        out[lab + "_h"] = [c2(hpW), c2(hxW * eph)]
        out[lab + "_hd"] = [c2(hdp), c2(hdx * eph)]
        out[lab + "_EB"] = [c2(z) for z in cE + cB]
        if lab == "Wsp":
            p4 = diag.psi4(E, B, gam, xw.K)
            out["psi4_coef"] = [c2(2 * diag.mode_coeff(p4.real, g, m)),
                                c2(2 * diag.mode_coeff(p4.imag, g, m))]
    return out


def work(item):
    case, N, path = item
    t0 = time.time()
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    r = do_F(path) if case == "F" else do_X(path, EPS[case])
    r.update({"case": case, "N": N, "file": os.path.relpath(path, SCR), "wall": time.time() - t0})
    return r


def main():
    cases = os.environ.get("V3_CASES", "F,X,X10").split(",")
    items = []
    for case in cases:
        for N, run, sub in RUNS[case]:
            files = sorted(glob.glob(f"{SCR}/{run}/{sub}/bin/*.z4c.*.bin"))
            items += [(case, N, f) for f in files]
    items.sort(key=lambda it: -it[1])          # big ones first
    nw = int(os.environ.get("V3_WORKERS", "5"))
    t0 = time.time()
    with Pool(nw) as pool:
        res = []
        for i, r in enumerate(pool.imap_unordered(work, items)):
            res.append(r)
            if i % 20 == 0:
                print(f"{i + 1}/{len(items)} {r['case']} N{r['N']} t={r['t']:.3f} "
                      f"({r['wall']:.1f} s; total {time.time() - t0:.0f} s)", flush=True)
    res.sort(key=lambda r: (r["case"], r["N"], r["t"]))
    with open(os.path.join(OUT, "v3_dumps.json"), "w") as f:
        json.dump({"runs": RUNS, "eps": EPS, "dumps": res, "wall_s": time.time() - t0}, f)
    print("done", len(res), "dumps", time.time() - t0, "s")


if __name__ == "__main__":
    main()
