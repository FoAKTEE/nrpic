#!/usr/bin/env python3
"""Journal entry 5: esf_analyse.py on a synthetic ES-F run built from the exact LTB
solution (a test of the analysis logic before the card run exists).

    t_esf_synth.py --data <ES-F data run dir> [--out DIR]

Synthetic run (written into DIR/synth): code time t = tau / 1.4 (a stand-in gauge map);
finder M_AH(t) = M + sum of m E_K over the lattice particles with tau_H <= 1.4 t (the
discrete accretion; case continuum_truth: the continuum m(R0) at tau_H = 1.4 t, entry 5)
plus Gaussian noise of 1e-5; every dust
particle with tau_H < 1.4 * 200 M is removed (reason 3) at the proper time
tau_H + 0.3 (tau_0 - tau_H), with the code energy E = 1.35 E_K (the gauge factor of
entry 3); a flux sphere at areal radius 5 M crossed by each shell on its collapsing
branch, summed with the same contaminated E. Then esf_analyse.py runs on it twice: with
the exact history and with the growth scaled by 0.97.
"""
import argparse
import json
import math
import os
import struct
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fluxio  # noqa: E402

GAUGE = 1.4
TEND = 200.0
EFAC = 1.35


def write_run(d, data, scale, truth="discrete", seed=1):
    os.makedirs(d, exist_ok=True)
    lab = np.load(os.path.join(data, "esf_labels.npz"))
    g = np.loadtxt(os.path.join(data, "esf_growth.csv"), delimiter=",", skiprows=1)
    rng = np.random.default_rng(seed)
    t = np.arange(0.0, TEND + 1e-9, 0.5)
    if truth == "continuum":
        dMt = np.interp(GAUGE * t, g[:, 2], g[:, 1]) - 1.0
    else:   # the discrete accreted energy of the lattice particles inside the horizon
        dd = lab["rest"] > 1e-20
        o = np.argsort(lab["tauH"][dd])
        tt = lab["tauH"][dd][o]
        cs = np.concatenate([[0.0], np.cumsum((lab["rest"] * lab["E_K"])[dd][o])])
        dMt = cs[np.searchsorted(tt, GAUGE * t, side="right")]
    M = 1.0 + scale * dMt + rng.normal(0, 1e-5, t.size)
    with open(os.path.join(d, "esf.horizon_summary_0.txt"), "w") as f:
        f.write("# 1:iter 2:time 3:mass 4:Sx 5:Sy 6:Sz 7:S 8:area 9:hrms 10:hmean 11:meanradius 12:minradius\n")
        for ti, mi in zip(t, M):
            f.write(f"4 {ti:g} {mi:.15e} 0 0 0 0 {16*math.pi*mi*mi:.15e} 0 0 2 2\n")
    R0, EK, rest = lab["R0"], lab["E_K"], lab["rest"]
    dust = rest > 1e-20
    tauH, tau0 = lab["tauH"], lab["tau0"]
    sel = np.where(dust & (tauH < GAUGE * TEND))[0]
    tau_rem = tauH[sel] + 0.3 * (tau0[sel] - tauH[sel])
    t_rem = tau_rem / GAUGE
    keep = t_rem <= TEND
    sel, tau_rem, t_rem = sel[keep], tau_rem[keep], t_rem[keep]
    rec = np.zeros((sel.size, 20))
    rec[:, 0], rec[:, 1], rec[:, 3] = t_rem, sel, 3
    rec[:, 10], rec[:, 11], rec[:, 17] = rest[sel], tau_rem, EFAC * EK[sel]
    with open(os.path.join(d, "esf.removed.bin"), "wb") as f:
        f.write(b"NRPREM01" + struct.pack("<q", 20) + rec.astype("<f8").tobytes())
    # sphere at isotropic radius 5 M at t = 0, i.e. areal R_s = 5 (1 + 1/10)^2 = 6.05 M,
    # crossed by each shell outside it on its collapsing branch (cycloid of each shell)
    Rs = 5.0 * 1.1 ** 2
    m = lab["m_label"]
    A = m * R0 / 2.0
    T = m / (2.0 / R0) ** 1.5
    eta0 = np.arccos(np.clip(1.0 - 2.0 / m, -1, 1))
    ok = dust & (Rs / A <= 2.0) & (R0 > Rs)
    eta5 = 2 * math.pi - np.arccos(np.clip(1.0 - Rs / A, -1, 1))
    tau5 = T * ((eta5 - np.sin(eta5)) - (eta0 - np.sin(eta0)))
    t5 = np.where(ok, tau5 / GAUGE, np.inf)
    th = np.arange(0.0, TEND + 1e-9, 0.25)
    o = np.argsort(t5)
    cs_mE = np.concatenate([[0.0], np.cumsum((rest * EFAC * EK)[o])])
    cs_m = np.concatenate([[0.0], np.cumsum(rest[o])])
    k = np.searchsorted(t5[o], th, side="right")
    with open(os.path.join(d, "esf.acc.hst"), "w") as f:
        f.write("# [1]=time [2]=radius1 [3]=n_in1 [4]=m_in1 [5]=mE_in1 [6]=n_out1 [7]=m_out1 [8]=mE_out1 [9]=m_inside1\n")
        m_in0 = float(rest[dust & (R0 < Rs)].sum())
        for ti, ki in zip(th, k):
            f.write(f"{ti:.15e} 5.0 {ki} {cs_m[ki]:.15e} {cs_mE[ki]:.15e} 0 0 0 {m_in0:.15e}\n")
    with open(os.path.join(d, "esf.nrpic.hst"), "w") as f:
        f.write("# [1]=time [2]=np\n")
        for ti in th:
            f.write(f"{ti:.15e} {int(dust.sum() - np.sum(t_rem <= ti))}\n")
    return dict(n_removed=int(sel.size), n_sphere=int(np.isfinite(t5).sum()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    a = ap.parse_args()
    res = {}
    for name, scale, truth in (("exact", 1.0, "discrete"), ("growth_x0.97", 0.97, "discrete"),
                               ("continuum_truth", 1.0, "continuum")):
        d = os.path.join(a.out, "synth_" + name)
        info = write_run(d, a.data, scale, truth)
        p = subprocess.run([sys.executable, os.path.join(HERE, "esf_analyse.py"), "--run", d,
                            "--data", a.data, "--floor", "0", "--out", d],
                           capture_output=True, text=True, check=True)
        res[name] = dict(info, analysis=json.loads(p.stdout))
    with open(os.path.join(a.out, "t_esf_synth.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
