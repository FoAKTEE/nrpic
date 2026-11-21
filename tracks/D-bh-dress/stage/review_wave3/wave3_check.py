#!/usr/bin/env python3
"""Lead's wave-3 re-check (batch 2a) of D-bh-dress: predictions Z1-Z5 of JOURNAL.md,
session lead-wave3-batch2a (2026-11-21T06:35Z).

Written without the helpers' analysis code (es_runs/analyse.py, tools/es1g_judge.py,
tools/es_extra.py, flux_tools/check_esf_construction.py, drift_controls/tools/*,
verifier_g1/*). Readers are those of the previous lead's
stage/review_wave2/es_finish_check.py. Reads only registered outputs:
  ES-1G  D-20261119-142633-6f72922  (es.*)    lapse_leak run
  ES-1   D-20261115-172726-60ba4c2  (es.*)    1+log run, for the figure only
  V-1    D-20261115-172730-c6d151b  (v1.*)    vacuum control
  V-1B   D-20261120-222625-63abd72  (v1b.*)   V-1 with the faces at +-384 M
  ES-F data D-20261119-145022-2208a19 (esf.nrp, esf.json, energy_by_tag.npy)
  secondary_infall/nm_growth_cellcentre.txt (table of the wave-2 analysis
  D-20261115-190541-e27453d, committed)
File layouts: header of the finder summaries; traj.bin 8 doubles and trajmet.bin 17
doubles (athenak/src/particles/nrpic_io.cpp:803-814; proper time index 12);
docs/FORMATS.md (.nrp).

Writes wave3_check.json and wave3_check.png/.pdf into --out (default $NRPIC_RUN_DIR).
"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TRACK = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.normpath(os.path.join(TRACK, "..", "..", "python")))
from nrpic import figstyle as fs  # noqa: E402

SCR = "/data/haiyangw/nrpic/scratch/D-bh-dress"
RUNS = {"ES-1G": (os.path.join(SCR, "D-20261119-142633-6f72922"), "es"),
        "ES-1": (os.path.join(SCR, "D-20261115-172726-60ba4c2"), "es"),
        "V-1": (os.path.join(SCR, "D-20261115-172730-c6d151b"), "v1"),
        "V-1B": (os.path.join(SCR, "D-20261120-222625-63abd72"), "v1b")}
ESF = os.path.join(SCR, "D-20261119-145022-2208a19")
PRED = os.path.join(TRACK, "es_runs", "results", "predictions.json")
GROWTH = os.path.join(TRACK, "secondary_infall", "nm_growth_cellcentre.txt")
NGROUP = 14


def wall_exact(tau):
    return (36.0 ** 1.5 + 1.5 * math.sqrt(2.0) * np.asarray(tau)) ** (2.0 / 3.0)


def read_summary(path):
    a = np.loadtxt(path, comments="#")
    t = a[:, 1]
    _, idx = np.unique(t, return_index=True)   # t = 0 is written twice
    a = a[idx]
    return {"t": a[:, 1], "m": a[:, 2], "meanr": a[:, 10], "minr": a[:, 11]}


def read_traj(d, base):
    tr = np.fromfile(os.path.join(d, base + ".traj.bin"), dtype="<f8").reshape(-1, 8)
    tm = np.fromfile(os.path.join(d, base + ".trajmet.bin"), dtype="<f8").reshape(-1, 17)
    assert tr.shape[0] == tm.shape[0]
    assert np.array_equal(tr[:, 0], tm[:, 0]) and np.array_equal(tr[:, 1], tm[:, 1])
    x = tr[:, 2:5]
    r = np.linalg.norm(x, axis=1)
    n = x / r[:, None]
    g = tm[:, 6:12]
    G = np.empty((len(g), 3, 3))
    G[:, 0, 0], G[:, 0, 1], G[:, 0, 2] = g[:, 0], g[:, 1], g[:, 2]
    G[:, 1, 0], G[:, 1, 1], G[:, 1, 2] = g[:, 1], g[:, 3], g[:, 4]
    G[:, 2, 0], G[:, 2, 1], G[:, 2, 2] = g[:, 2], g[:, 4], g[:, 5]
    B = 0.5 * (np.trace(G, axis1=1, axis2=2) - np.einsum("ni,nij,nj->n", n, G, n))
    return {"t": tr[:, 0], "tag": tr[:, 1].astype(int), "R": r * np.sqrt(B),
            "tau": tm[:, 12], "alpha": tm[:, 2]}


def crossing(T, tag):
    s = T["tag"] == tag
    R, tau = T["R"][s], T["tau"][s]
    k = np.nonzero(R < 2.0)[0]
    if len(k) == 0 or k[0] == 0:
        return None
    k = k[0]
    w = (R[k - 1] - 2.0) / (R[k - 1] - R[k])
    return float(tau[k - 1] + w * (tau[k] - tau[k - 1]))


def drift(S, t0=100.0):
    i0 = int(np.argmin(np.abs(S["t"] - t0)))
    return S["t"], S["m"] / S["m"][i0] - 1.0, i0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    pred = json.load(open(PRED))
    out = {"inputs": {k: v[0] for k, v in RUNS.items()}}

    S = {k: read_summary(os.path.join(d, b + ".horizon_summary_0.txt"))
         for k, (d, b) in RUNS.items()}

    # ---- Z1 ES-1G horizon
    t, D, i0 = drift(S["ES-1G"])
    w = (t >= 100.0) & (t <= 199.5)
    i25 = int(np.argmin(np.abs(t - 25.0)))
    out["Z1"] = {"t0": float(t[i0]), "M100_minus_1": float(S["ES-1G"]["m"][i0] - 1.0),
                 "drift_max_100_199.5": float(D[w].max()),
                 "t_of_max": float(t[w][np.argmax(D[w])]),
                 "drift_min_100_199.5": float(D[w].min()),
                 "t_of_min": float(t[w][np.argmin(D[w])]),
                 "drift_range_100_165": [float(D[w & (t <= 165)].min()),
                                         float(D[w & (t <= 165)].max())],
                 "meanr_25": float(S["ES-1G"]["meanr"][i25]),
                 "meanr_last": float(S["ES-1G"]["meanr"][-1]), "t_last": float(t[-1])}

    # ---- Z2 ES-1G tracers
    T = read_traj(*RUNS["ES-1G"])
    errs = []
    for g in range(56, 70):
        s = T["tag"] == g
        errs.append(np.max(np.abs(T["R"][s] / wall_exact(T["tau"][s]) - 1.0)))
    tau_wall_end = float(np.max(T["tau"][(T["tag"] >= 56) & (T["tag"] < 70)]))
    cr6 = [crossing(T, g) for g in range(0, 14)]
    cr6 = [c for c in cr6 if c is not None]
    cr10 = [crossing(T, g) for g in range(14, 28)]
    cr10 = [c for c in cr10 if c is not None]
    ex6 = pred["tau_reach_2M_es"]["group0_R0=6"]
    ex10 = pred["tau_reach_2M_es"]["group1_R0=10"]
    tl = T["t"].max()
    s48 = (T["tag"] >= 84) & (T["tag"] < 98) & (T["t"] == tl)
    out["Z2"] = {"wall_max_rel_err_whole_run": float(max(errs)), "wall_tau_end": tau_wall_end,
                 "R0_6_n_crossed": len(cr6), "R0_6_tau_mean": float(np.mean(cr6)),
                 "R0_6_err_mean": float(np.mean(cr6) - ex6),
                 "R0_6_err_range": [float(min(cr6) - ex6), float(max(cr6) - ex6)],
                 "R0_10_n_crossed": len(cr10),
                 "R0_10_err_range": [float(min(cr10) - ex10), float(max(cr10) - ex10)],
                 "t_last_record": float(tl),
                 "R0_48_tau_at_t_last": [float(T["tau"][s48].min()), float(T["tau"][s48].max())],
                 "n_R0_48_at_t_last": int(s48.sum())}

    # ---- Z3 V-1B against V-1
    tV, DV, _ = drift(S["V-1"])
    tB, DB, _ = drift(S["V-1B"])

    def at(tt, DD, x):
        return float(DD[int(np.argmin(np.abs(tt - x)))])
    wB = (tB >= 100) & (tB <= 199.5)
    ct = np.intersect1d(S["V-1"]["t"], S["V-1B"]["t"])
    dm = (np.interp(ct, S["V-1B"]["t"], S["V-1B"]["m"])
          - np.interp(ct, S["V-1"]["t"], S["V-1"]["m"]))
    sep = ct[np.abs(dm) > 1e-6]
    sep9 = ct[np.abs(dm) > 1e-9]
    out["Z3"] = {"V1_D199.5": at(tV, DV, 199.5), "V1B_D199.5": at(tB, DB, 199.5),
                 "V1B_range_100_199.5": [float(DB[wB].min()), float(DB[wB].max())],
                 "V1B_range_100_165": [float(DB[wB & (tB <= 165)].min()),
                                       float(DB[wB & (tB <= 165)].max())],
                 "V1B_M100_minus_1": float(S["V-1B"]["m"][np.argmin(np.abs(tB - 100))] - 1),
                 "V1_M100_minus_1": float(S["V-1"]["m"][np.argmin(np.abs(tV - 100))] - 1),
                 "first_t_sep_1e-6": float(sep[0]) if len(sep) else None,
                 "first_t_sep_1e-9": float(sep9[0]) if len(sep9) else None,
                 "t_last_V1B": float(tB[-1]),
                 "Pb1_holds": bool(at(tB, DB, 199.5) > -5e-5 and
                                   np.all(np.abs(DB[wB]) <= 5e-5)),
                 "Pb1_refuted": bool(at(tB, DB, 199.5) < -1.0e-4)}

    # ---- Z4 dress at a/a_i = 2, 4, 8 against the kernel shells
    hdr = [l for l in open(GROWTH) if l.startswith("#")]
    blocks, cur, name = {}, [], None
    for line in open(GROWTH):
        if line.startswith("#"):
            if ":" in line and "/data" in line:
                if name and cur:
                    blocks[name] = np.array(cur)
                name, cur = line[1:].split(":")[0].strip(), []
            continue
        if line.strip():
            cur.append([float(v) for v in line.split()])
    if name and cur:
        blocks[name] = np.array(cur)
    z4 = {"header": hdr[1].strip() if len(hdr) > 1 else None}
    for nm, a in blocks.items():
        r = {}
        for A in (2.0, 4.0, 8.0):
            if a[:, 1].max() < A - 1e-9:
                continue
            Mt = np.interp(A, a[:, 1], a[:, 2])
            Md = np.interp(A, a[:, 1], a[:, 3])
            Mtk = np.interp(A, a[:, 1], a[:, 4])
            Mdk = np.interp(A, a[:, 1], a[:, 5])
            r[f"a={A:g}"] = {"Mta": Mt, "Mta_kernel": Mtk, "dMta_pct": 100 * (Mt / Mtk - 1),
                             "dress": Md, "dress_kernel": Mdk,
                             "ddress_pct": 100 * (Md / Mdk - 1)}
        s = a[:, 1] >= 3.0
        r["max_abs_ddress_pct_a_ge_3"] = float(np.max(np.abs(100 * (a[s, 3] / a[s, 5] - 1))))
        z4[nm] = r
    out["Z4"] = z4

    # ---- Z5 ES-F particle file
    with open(os.path.join(ESF, "esf.nrp"), "rb") as f:
        magic = f.read(8)
        n = int(np.frombuffer(f.read(8), "<i8")[0])
        rec = np.frombuffer(f.read(56 * n), "<f8").reshape(n, 7)
        _sp = np.frombuffer(f.read(4 * n), "<i4")
    js = json.load(open(os.path.join(ESF, "esf.json")))
    ebt = np.load(os.path.join(ESF, "energy_by_tag.npy"))
    m = rec[:, 6]
    trc = m == 1e-30
    dust = ~trc
    sum_m = float(np.sum(m[dust]))
    sum_me = float(np.sum(m[dust] * ebt[dust])) if len(ebt) == n else None
    out["Z5"] = {"magic": magic.decode(), "n": n, "n_tracers": int(trc.sum()),
                 "max_abs_u": float(np.max(np.abs(rec[:, 3:6]))),
                 "sum_dust_m": sum_m, "json_lattice_rest_mass": js["lattice_rest_mass"],
                 "rel_diff_rest": sum_m / js["lattice_rest_mass"] - 1.0,
                 "len_energy_by_tag": int(len(ebt)),
                 "sum_m_times_e": sum_me, "json_lattice_ms": js["lattice_misner_sharp"],
                 "rel_diff_ms": (sum_me / js["lattice_misner_sharp"] - 1.0) if sum_me else None,
                 "rest_vs_continuum": sum_m / js["continuum_rest_mass"] - 1.0,
                 "ms_vs_Dtot": (sum_me / js["Dtot"] - 1.0) if sum_me else None}

    with open(os.path.join(args.out, "wave3_check.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    print(json.dumps(out, indent=1, default=float))

    # ---- figure
    fs.use_style()
    fig, ax = plt_subplots(fs)
    a0, a1, a2, a3 = ax.ravel()
    for k, c in (("ES-1", "C0"), ("V-1", "C1"), ("V-1B", "C2"), ("ES-1G", "C3")):
        tt, DD, _ = drift(S[k])
        s = tt >= 100
        a0.plot(tt[s], DD[s], color=c, lw=1.2, label=k)
    a0.axhline(5e-5, color="0.5", lw=0.6, ls=":")
    a0.axhline(-5e-5, color="0.5", lw=0.6, ls=":")
    a0.set_ylim(-4e-4, 1.2e-3)
    a0.set_xlabel(r"$t/M$")
    a0.set_ylabel(r"$M_{\rm AH}(t)/M_{\rm AH}(100M)-1$")
    a0.set_title("(a) horizon-mass drift from 100 M", loc="left")
    a0.legend(frameon=False, fontsize=8, loc="upper left")
    a1.semilogy(ct, np.abs(dm) + 1e-16, color="C2", lw=1.0)
    a1.axhline(1e-6, color="0.5", lw=0.6, ls=":")
    a1.set_xlabel(r"$t/M$")
    a1.set_ylabel(r"$|M_{\rm V\!-\!1B}-M_{\rm V\!-\!1}|/M$")
    a1.set_title("(b) V-1B against V-1", loc="left")
    for g in range(56, 70):
        s = T["tag"] == g
        a2.plot(T["tau"][s], T["R"][s] / wall_exact(T["tau"][s]) - 1.0, lw=0.7)
    a2.set_xlabel(r"$\tau/M$")
    a2.set_ylabel(r"$R/R_{\rm w}(\tau)-1$")
    a2.set_title("(c) ES-1G wall tracers", loc="left")
    for nm, c in zip(blocks, ("C0", "C1", "C2")):
        a = blocks[nm]
        s = a[:, 1] >= 1.5
        a3.plot(a[s, 1], 100 * (a[s, 3] / a[s, 5] - 1), color=c, lw=1.2, label=nm)
    a3.axhspan(-0.5, 0.5, color="0.85", lw=0)
    a3.set_xscale("log")
    a3.set_xticks([1.5, 2, 3, 4, 6, 8])
    a3.set_xticklabels(["1.5", "2", "3", "4", "6", "8"])
    a3.minorticks_off()
    a3.set_xlabel(r"$a/a_i$")
    a3.set_ylabel("dress / kernel shells - 1 (%)")
    a3.set_title("(d) Newtonian-mode dress (wave 2)", loc="left")
    a3.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fs.save(fig, os.path.join(args.out, "wave3_check"))


def plt_subplots(fsmod):
    import matplotlib.pyplot as plt
    return plt.subplots(2, 2, figsize=(9.0, 6.4))


if __name__ == "__main__":
    main()
