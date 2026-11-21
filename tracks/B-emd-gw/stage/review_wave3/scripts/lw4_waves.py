#!/usr/bin/env python3
"""Lead review, batch 4a (B-emd-gw), checks L4 and L5 of ../JOURNAL.md: waves round 1.

L4: test F2 (k = 2 pi (1,2,0)) at N = 16, 32, 48, 64. Forward combination W = c_h + i c_h'/|k|
    of the TT mode at +k (h = gt - 1, h' = -2 alpha At, zero shift), referred to the first
    dump: amplitude |W_tot(t)|/|W_tot(0)| - 1 with |W_tot|^2 = |W_+|^2 + |W_x|^2 (independent
    of the polarization basis), phase arg(W_+(t)/W_+(0)) + |k| t, at the last dump.
L5: test X step test (dt_expansion = 0.001, card run B-20261120-222841-acfe21d): cross
    polarization errors at the last dump against verifier3's exact EdS mode; time part with
    verifier3's own e(0.01) at N = 64.

Independent of the waves package: reader, TT projector, polarization basis, mode coefficient
and exact solutions are verifier3's (stage/G1/verifier3/scripts/diag.py, exact.py,
v3_measure.do_X). The waves numbers are read only to be compared.

    python3 lw4_waves.py   (through nrpic-run; writes $NRPIC_RUN_DIR/lw4_waves.{json,png,pdf})
"""
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TRACK = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
REPO = os.path.abspath(os.path.join(TRACK, "..", ".."))
V3 = os.path.join(TRACK, "stage", "G1", "verifier3", "scripts")
SCR = "/data/haiyangw/nrpic/scratch/B-emd-gw"
sys.path.insert(0, V3)
sys.path.insert(0, os.path.join(REPO, "python"))
import diag  # noqa: E402
import exact  # noqa: E402
import v3_measure  # noqa: E402

OUT = os.environ.get("NRPIC_RUN_DIR", os.path.join(SCR, "tmp", "lw4"))
os.makedirs(OUT, exist_ok=True)
EYE = np.eye(3)[:, :, None, None, None]

F2 = {16: "B-20261120-222849-3b921b7/N16", 32: "B-20261120-222849-3b921b7/N32",
      48: "B-20261120-222849-3b921b7/N48", 64: "B-20261120-222841-acfe21d/f120N64"}
XS = {n: f"B-20261120-222841-acfe21d/xdt3N{n}" for n in (16, 32, 48, 64)}


def f2_forward(path, K):
    d = diag.read_bin(path)
    g = d["grid"]
    gam, Kij, alp, chi, gt, At, trK = diag.z4c_to_adm(d)
    m = tuple(int(round(v)) for v in K / (2 * np.pi) * g.L)
    kn = np.linalg.norm(K)
    hTT = diag.tt_project(gt - EYE, g)
    dTT = diag.tt_project(-2.0 * alp * At, g)
    W = []
    for T, D in zip(diag.pol_components(hTT, K), diag.pol_components(dTT, K)):
        ch, cd = diag.mode_coeff(T, g, m), diag.mode_coeff(D, g, m)
        W.append(complex(ch + 1j * cd / kn))
    return d["time"], W


def main():
    res = {"F2": {}, "XS": {}}
    wav = json.load(open(os.path.join(TRACK, "waves", "results", "f120_results.json")))
    K = 2 * np.pi * np.array([1.0, 2.0, 0.0])
    kn = np.linalg.norm(K)
    for n, sub in F2.items():
        files = sorted(glob.glob(f"{SCR}/{sub}/bin/*.z4c.*.bin"))
        t0, W0 = f2_forward(files[0], K)
        t1, W1 = f2_forward(files[-1], K)
        amp = np.sqrt(abs(W1[0]) ** 2 + abs(W1[1]) ** 2) / np.sqrt(abs(W0[0]) ** 2 + abs(W0[1]) ** 2) - 1
        ph = float(np.angle(W1[0] / W0[0] * np.exp(1j * kn * (t1 - t0))))
        ph_x = float(np.angle(W1[1] / W0[1] * np.exp(1j * kn * (t1 - t0))))
        w = wav[str(n)]["tt"]
        res["F2"][n] = {"t_end": t1, "amp": float(amp), "phase_p": ph, "phase_x": ph_x,
                        "waves_amp_p": w["amp_p_end"], "waves_amp_x": w["amp_x_end"],
                        "waves_phase_p": w["phase_p_end"], "waves_phase_x": w["phase_x_end"],
                        "rel_amp": float(amp / w["amp_p_end"] - 1),
                        "rel_phase": float(ph / w["phase_p_end"] - 1)}
        print("F2", n, res["F2"][n], flush=True)
    ns = sorted(res["F2"])
    for q in ("amp", "phase_p"):
        res["F2"]["orders_" + q] = [float(np.log(abs(res["F2"][a][q] / res["F2"][b][q])) / np.log(b / a))
                                    for a, b in zip(ns[:-1], ns[1:])]
    # L5
    xdt = json.load(open(os.path.join(TRACK, "waves", "results", "xdt_card_results.json")))
    v3s = json.load(open(os.path.join(TRACK, "stage", "G1", "verifier3", "results", "v3_summary.json")))
    eps = (2e-6, 1e-6)
    xw = exact.ExpandingWave(eps_p=eps[0], eps_x=eps[1])
    for n, sub in XS.items():
        f = sorted(glob.glob(f"{SCR}/{sub}/bin/*.z4c.*.bin"))[-1]
        r = v3_measure.do_X(f, eps)
        t = r["t"]
        T, dT = xw.mode.T(t), xw.mode.dT(t)
        p = 1
        H, Hd = complex(*r["TT_h"][p]), complex(*r["TT_hd"][p])
        Z = H.real + 1j * Hd.real / xw.kn
        Zex = eps[p] * (T + 1j * dT / xw.kn)
        amp, ph = float(abs(Z) / abs(Zex) - 1), float(np.angle(Z / Zex))
        w = xdt[str(n)]["tt"]
        e01 = v3s["X"][str(n)]["TT x"]
        res["XS"][n] = {"t_end": t, "amp_x": amp, "phase_x": ph,
                        "waves_amp_x": w["amp_x_end"], "waves_phase_x": w["phase_x_end"],
                        "v3_e001_amp_x": e01["amp_err_final"], "v3_e001_phase_x": e01["phase_err_final"],
                        "time_amp": e01["amp_err_final"] - amp, "time_phase": e01["phase_err_final"] - ph,
                        "rel_amp": float(amp / w["amp_x_end"] - 1), "rel_phase": float(ph / w["phase_x_end"] - 1)}
        print("XS", n, res["XS"][n], flush=True)
    with open(os.path.join(OUT, "lw4_waves.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    figure(res)


def figure(res):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.9))
    ns = [n for n in res["F2"] if isinstance(n, int)]
    ax = axs[0]
    for q, wq, col, lab in (("amp", "waves_amp_p", fs.PAL["blue"], "amplitude"),
                            ("phase_p", "waves_phase_p", fs.PAL["red"], "phase")):
        ax.loglog(ns, [abs(res["F2"][n][q]) for n in ns], "o", mfc="none", color=col, label=lab + " (lead)")
        ax.loglog(ns, [abs(res["F2"][n][wq]) for n in ns], "x", color=col, label=lab + " (waves)")
    ax.set_xlabel("N")
    ax.set_ylabel("|error| at last dump")
    ax.set_title("(a) F2, k = 2pi(1,2,0), TT")
    ax.legend(fontsize=6)
    ax = axs[1]
    xs = sorted(res["XS"])
    for q, wq, col, lab in (("amp_x", "waves_amp_x", fs.PAL["blue"], "amplitude"),
                            ("phase_x", "waves_phase_x", fs.PAL["red"], "phase")):
        ax.loglog(xs, [abs(res["XS"][n][q]) for n in xs], "o", mfc="none", color=col, label=lab + " dt 0.001 (lead)")
        ax.loglog(xs, [abs(res["XS"][n][wq]) for n in xs], "x", color=col, label=lab + " dt 0.001 (waves)")
    ax.loglog(xs, [abs(res["XS"][n]["v3_e001_amp_x"]) for n in xs], "s", mfc="none", color=fs.PAL["yellow"],
              label="amplitude dt 0.01 (verifier3)")
    ax.set_xlabel("N")
    ax.set_title("(b) X cross, step test")
    ax.legend(fontsize=6)
    fs.save(fig, os.path.join(OUT, "lw4_waves"))


if __name__ == "__main__":
    main()
