#!/usr/bin/env python3
"""PARTIAL reading of the particle-number sequence FK (N), FN4 (4N), FNQ (N/4) while FN4 and FNQ
are still running as chains (g2long/JOURNAL.md entry 10: N1-N3, Q1-Q2; judged in full only when
the runs end and are closed).

"As far as complete segments reach": each run is cut at t_cut = the second-newest restart time
in its rst/ (the newest may still be written, and what follows the newest restart of a chain
that is preempted is written again by its successor). Finder records with t <= t_cut (last
record of a time), removal records with t <= t_cut (whole records only; records of preempted
segments dropped as in esf_criteria.py).

Numbers (each run with its own data: energy_by_tag.npy, esf_labels.npz, esf_growth.csv):
- removed dust sum m E_K at t = 50, 100, 150, 200, 250, 300, 350 M (those <= t_cut), ratio to FK
  (N2: FN4 within 1 per cent, refuted above 3 per cent; Q2: FNQ within 3 per cent);
- M_AH(t) - M_AH,FK(t) at the same times (N3: FN4 within 2e-3 of FK at 100-400 M, and
  |M_4N - M_N| <= |M_N - M_N/4| at three of four times);
- criterion G's (iii) bins (10 M of tau_rem, >= 20 removals, |median| <= 1 per cent; FNQ 2 per
  cent) on the removals before t_cut (N1, Q1 partial).

Usage: np_partial.py --out DIR NAME=RUNDIR:BASE:DATADIR ...  (first run = the reference, FK)
"""
import argparse
import glob
import json
import os
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TRACK = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(TRACK, "flux_tools"))
sys.path.insert(0, os.path.join(TRACK, "g2runs", "tools"))
import fluxio  # noqa: E402
from esf_criteria import binned_median, first_sample  # noqa: E402

TIMES = (50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 399.5)


def read_removed_whole(path):
    with open(path, "rb") as f:
        raw = f.read()
    if raw[:8] != b"NRPREM01":
        raise ValueError(path)
    nrec = struct.unpack("<q", raw[8:16])[0]
    body = raw[16:]
    nfull = len(body) // (8 * nrec)
    a = np.frombuffer(body[: nfull * 8 * nrec], dtype="<f8").reshape(-1, nrec)
    out = {k: a[:, i].copy() for i, k in enumerate(fluxio.REMOVED_FIELDS)}
    for k in ("tag", "species", "reason", "peri"):
        out[k] = np.rint(out[k]).astype(np.int64)
    out["n"] = a.shape[0]
    return out, len(body) - nfull * 8 * nrec


def load(spec):
    run, base, data = spec.split(":")
    rts = sorted(fluxio.restart_times(os.path.join(run, "rst")))
    stf = os.path.join(run, "chain", "STATUS")
    done = os.path.isfile(stf) and open(stf).read().strip() == "DONE"
    # a chain that ended (DONE) is read whole; a running one up to its second-newest restart
    t_cut = float("inf") if done else (float(rts[-2]) if len(rts) >= 2 else float(rts[-1]))
    hor = fluxio.read_horizon(os.path.join(run, base + ".horizon_summary_0.txt"))
    keep = hor["time"] <= t_cut + 1e-9
    hor = {k: v[keep] for k, v in hor.items()}
    rem, partial_bytes = read_removed_whole(os.path.join(run, base + ".removed.bin"))
    info = []
    if np.any(np.diff(rem["time"]) < 0.0):
        rem, info = fluxio.drop_overlaps(rem, rts)
    k = rem["time"] <= t_cut + 1e-9
    rem = {kk: (v[k] if isinstance(v, np.ndarray) and v.shape[:1] == k.shape else v) for kk, v in rem.items()}
    EK = np.load(os.path.join(data, "energy_by_tag.npy"))
    grow = np.loadtxt(os.path.join(data, "esf_growth.csv"), delimiter=",", skiprows=1)
    g_tau, g_m = grow[:, 2], grow[:, 1]
    o = np.argsort(g_tau)
    hz = np.isin(rem["reason"], (2, 3)) & (rem["tag"] >= 140)
    trem, tag, tau, m = rem["time"][hz], rem["tag"][hz], rem["tau"][hz], rem["m"][hz]
    order = np.argsort(trem, kind="stable")
    trem, tag, tau, m = trem[order], tag[order], tau[order], m[order]
    cum_mEK = np.cumsum(m * EK[tag])
    th, Mh = hor["time"], hor["mass"]
    kk, ok = first_sample(th, trem)
    ratio = Mh[kk] / np.interp(tau, g_tau[o], g_m[o], left=1.0) - 1.0
    bins = binned_median(tau[ok], ratio[ok], tau_max=650.0)
    if done:
        t_cut = float(th[-1])
    return dict(run=run, base=base, data=data, t_cut=t_cut, chain_done=done, t_finder_end=float(th[-1]), n_rst=len(rts),
                partial_tail_bytes=int(partial_bytes), overlaps=info, th=th, Mh=Mh, trem=trem,
                cum_mEK=cum_mEK, bins=bins, n_dust_removed=int(trem.size),
                dust_mass_total=float(np.sum(np.load(os.path.join(data, "esf_labels.npz"))["rest"])))


def removed_at(r, t):
    k = np.searchsorted(r["trem"], t, side="right")
    return float(r["cum_mEK"][k - 1]) if k > 0 else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    ap.add_argument("runs", nargs="+")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    R = {}
    for spec in a.runs:
        name, rest = spec.split("=", 1)
        R[name] = load(rest)
    names = list(R)
    ref = R[names[0]]
    out = dict(label="PARTIAL: runs cut at the second-newest restart time", runs={})
    for n, r in R.items():
        cnt = [b for b in r["bins"] if b["counted"]]
        row = dict(run=r["run"], data=r["data"], t_cut=r["t_cut"], chain_done=r["chain_done"], t_finder_end=r["t_finder_end"],
                   n_dust_removed=r["n_dust_removed"], dust_mass_total=r["dust_mass_total"],
                   partial_tail_bytes=r["partial_tail_bytes"], overlaps=r["overlaps"],
                   iii_n_counted=len(cnt), iii_tau_reached=float(cnt[-1]["hi"]) if cnt else None,
                   iii_max_abs_median=float(max(abs(b["median"]) for b in cnt)) if cnt else None,
                   iii_bins=[dict(lo=b["lo"], n=b["n"], median=b["median"]) for b in cnt],
                   at={})
        for t in TIMES:
            if t > min(r["t_cut"], ref["t_cut"]) + 1e-9:
                continue
            Mr = float(np.interp(t, r["th"], r["Mh"]))
            M0 = float(np.interp(t, ref["th"], ref["Mh"]))
            Fr, F0 = removed_at(r, t), removed_at(ref, t)
            row["at"][str(t)] = dict(M_AH=Mr, dM_vs_ref=Mr - M0, removed_mEK=Fr,
                                     removed_ratio_to_ref=(Fr / F0 if F0 > 0 else None))
        out["runs"][n] = row
    with open(os.path.join(a.out, "np_partial.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    for n, row in out["runs"].items():
        print(n, "t_cut", row["t_cut"], "iii counted", row["iii_n_counted"], "max|med|", row["iii_max_abs_median"],
              "tau reached", row["iii_tau_reached"])
        for t, v in row["at"].items():
            print("   ", t, json.dumps(v))
    figure(a.out, R, names)


def figure(outdir, R, names):
    import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    cols = [fs.PAL["blue"], fs.PAL["red"], fs.PAL["green"], fs.PAL["yellow"]]
    ref = R[names[0]]
    fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.16, top=0.88, wspace=0.42)
    x = ax[0]
    for c, n in zip(cols, names):
        r = R[n]
        tt = r["th"][r["th"] <= min(r["t_cut"], ref["t_cut"])]
        x.plot(tt, 1e3 * (np.interp(tt, r["th"], r["Mh"]) - np.interp(tt, ref["th"], ref["Mh"])), color=c, lw=1.3, label=n)
    x.axhspan(-2, 2, color="grey", alpha=0.15, lw=0)
    x.set_xlabel(r"$t/M$", labelpad=-2)
    x.set_ylabel(r"$M_{\rm AH}-M_{\rm AH,FK}$ [$10^{-3}M$]")
    x.set_title("Left: horizon mass (band N3)", loc="left", fontsize=8)
    x.legend(fontsize=7, frameon=False)
    x = ax[1]
    tg = np.arange(20.0, 400.0, 5.0)
    for c, n in zip(cols, names):
        r = R[n]
        tt = tg[tg <= min(r["t_cut"], ref["t_cut"])]
        x.plot(tt, [100 * (removed_at(r, t) / removed_at(ref, t) - 1) for t in tt], color=c, lw=1.3)
    x.axhspan(-1, 1, color="grey", alpha=0.15, lw=0)
    x.axhline(3, **fs.GUIDE)
    x.axhline(-3, **fs.GUIDE)
    x.set_xlabel(r"$t/M$", labelpad=-2)
    x.set_ylabel(r"removed $\sum mE_K$ / FK $-1$ [per cent]")
    x.set_title("Middle: relaxation control (N2, Q2)", loc="left", fontsize=8)
    x = ax[2]
    for c, n in zip(cols, names):
        b = [q for q in R[n]["bins"] if q["counted"]]
        if b:
            x.step([q["lo"] for q in b] + [b[-1]["hi"]], [100 * q["median"] for q in b] + [100 * b[-1]["median"]],
                   where="post", color=c, lw=1.3)
    x.axhspan(-1, 1, color="grey", alpha=0.15, lw=0)
    x.set_xlabel(r"$\tau_{\rm rem}/M$", labelpad=-2)
    x.set_ylabel(r"(iii) bin median [per cent]")
    x.set_title("Right: criterion G, partial", loc="left", fontsize=8)
    fs.save(fig, os.path.join(outdir, "np_partial"))
    plt.close(fig)


if __name__ == "__main__":
    main()
