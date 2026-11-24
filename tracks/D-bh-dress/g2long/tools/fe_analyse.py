#!/usr/bin/env python3
"""Judgement of test FE (g2long/JOURNAL.md entry 16): where the converged-finder null-test step happens.

Reads the probe tables of FP, FP-ext and FE (tools/probe_long.py, probes.json) and the runs' own horizon
summaries. With the tight finder (h1, variant A16) and S(t) = (M_ES(t) - M_V(t)) - (M_ES(100) - M_V(100)):
FE1 (M/8)  |S(50)| <= 2e-5 holds; refuted if >= 4e-5.
FE2 (M/16) S(150) in [2.0e-5, 5.1e-5] holds; refuted if >= 6.8e-5.
FE3 h0 within 3e-5 of the run's own mass at every FE dump; vacuum |M_h1(50) - M_h1(100)| <= 3e-5 at
    M/8 and M/16.

Usage: fe_analyse.py --probes P1.json [P2.json ...] --fe FE.json --out DIR NAME=RUNDIR:BASE ...
(names V-1L, ES-1L, V-1L16, ES-1L16).
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figstyle as fs  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402


def read_summary(path):
    a = np.loadtxt(path, comments="#")
    t = a[:, 1]
    _, idx = np.unique(t[::-1], return_index=True)      # last record of each time
    idx = np.sort(t.size - 1 - idx)
    return t[idx], a[idx, 2]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probes", required=True, nargs="+", help="probes.json of FP and FP-ext")
    ap.add_argument("--fe", required=True, help="probes.json of FE")
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    ap.add_argument("runs", nargs="+")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    fe = json.load(open(a.fe))
    P = [r for f in a.probes for r in json.load(open(f))] + fe
    R = {}
    for s in a.runs:
        name, rest = s.split("=", 1)
        rd, base = rest.rsplit(":", 1)
        t, m = read_summary(os.path.join(rd, base + ".horizon_summary_0.txt"))
        R[name] = dict(t=t, m=m, rid=os.path.basename(rd.rstrip("/")))
    rid2name = {v["rid"]: n for n, v in R.items()}
    # tight A16 masses: name -> {time: mass}; later probes of the same dump time replace earlier ones
    H1, H0 = {n: {} for n in R}, {n: {} for n in R}
    for p in P:
        n = rid2name.get(p["run"])
        if n is None or p.get("variant") != "A16" or not p.get("found"):
            continue
        tt = round(p["time_dump"], 6)
        if p["horizon"] == 1:
            H1[n][tt] = p["mass"]
        elif p["horizon"] == 0:
            H0[n][tt] = p["mass"]
    J = {"tight": {n: {str(k): v for k, v in sorted(d.items())} for n, d in H1.items()}}

    def S(es, vv):
        he, hv = H1[es], H1[vv]
        ts = sorted(t for t in set(he) & set(hv))
        ref = he[100.0] - hv[100.0]
        return {t: (he[t] - hv[t]) - ref for t in ts}

    S8, S16 = S("ES-1L", "V-1L"), S("ES-1L16", "V-1L16")
    J["S_M8"] = {str(k): v for k, v in S8.items()}
    J["S_M16"] = {str(k): v for k, v in S16.items()}
    s50 = S8.get(50.0)
    J["FE1"] = dict(S50=s50, holds=bool(s50 is not None and abs(s50) <= 2e-5),
                    refuted=bool(s50 is not None and abs(s50) >= 4e-5))
    s150 = S16.get(150.0)
    J["FE2"] = dict(S150=s150, S150_M8=S8.get(150.0),
                    holds=bool(s150 is not None and 2.0e-5 <= s150 <= 5.1e-5),
                    refuted=bool(s150 is not None and s150 >= 6.8e-5))
    fe_keys = {(rid2name.get(p["run"]), round(p["time_dump"], 6)) for p in fe}
    devs = []
    for n, tt in sorted(k for k in fe_keys if k[0] is not None):
        v = R[n]
        i = int(np.argmin(np.abs(v["t"] - tt)))
        if tt in H0[n]:
            devs.append(dict(run=n, t=tt, dev=H0[n][tt] - float(v["m"][i]), t_run=float(v["t"][i])))
    vac = {n: (H1[n][50.0] - H1[n][100.0]) if (50.0 in H1[n] and 100.0 in H1[n]) else None
           for n in ("V-1L", "V-1L16")}
    J["FE3"] = dict(h0_rows=devs, max_abs_dev=max(abs(d["dev"]) for d in devs) if devs else None,
                    vacuum_50_100=vac,
                    holds=bool(devs and max(abs(d["dev"]) for d in devs) <= 3e-5
                               and all(x is not None and abs(x) <= 3e-5 for x in vac.values())))
    J["fe_dump_times"] = sorted({f"{n} {t}" for n, t in fe_keys if n})
    with open(os.path.join(a.out, "fe_analyse.json"), "w") as f:
        json.dump(J, f, indent=1)
    print(json.dumps({k: v for k, v in J.items() if k != "tight"}, indent=1))
    figure(a.out, R, H1, S8, S16)


def figure(outdir, R, H1, S8, S16):
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.2), constrained_layout=True)
    x = ax[0]
    for es, vv, Sd, lab, c in (("ES-1L", "V-1L", S8, "M/8", fs.PAL["red"]),
                               ("ES-1L16", "V-1L16", S16, "M/16", fs.PAL["yellow"])):
        e, v = R[es], R[vv]
        ka = np.round(e["t"] * 8).astype(np.int64)
        kb = np.round(v["t"] * 8).astype(np.int64)
        k, ia, ib = np.intersect1d(ka, kb, return_indices=True)
        tc = k / 8.0
        i100a = int(np.argmin(np.abs(e["t"] - 100)))
        i100b = int(np.argmin(np.abs(v["t"] - 100)))
        dd = (e["m"][ia] - v["m"][ib]) - (e["m"][i100a] - v["m"][i100b])
        w = tc <= 320
        x.plot(tc[w], dd[w], color=c, lw=0.5, alpha=0.45, label=f"{lab}: run's own finder")
        ts = sorted(Sd)
        x.plot(ts, [Sd[t] for t in ts], "s-", color=c, ms=4.5, lw=1.0, mec="k", mew=0.4,
               label=f"{lab}: converged finder")
    x.axhline(0, **fs.GUIDE)
    x.set_xlim(0, 520)
    x.set_xlabel(r"$t/M$")
    x.set_ylabel(r"$S(t)$ (ES $-$ V, relative to 100 M)")
    x.legend(fontsize=6.5, frameon=False, loc="lower right")
    x.set_title("(a) bubble minus vacuum, horizon mass", loc="left", fontsize=9)
    x = ax[1]
    for n, c, m in (("V-1L", fs.PAL["blue"], "o"), ("ES-1L", fs.PAL["red"], "s"),
                    ("V-1L16", fs.PAL["green"], "o"), ("ES-1L16", fs.PAL["yellow"], "s")):
        d = H1[n]
        if 100.0 not in d:
            continue
        ts = sorted(d)
        x.plot(ts, [(d[t] - d[100.0]) * 1e5 for t in ts], m + "-", color=c, ms=4, lw=0.9,
               mfc="white" if n.startswith("V") else c, label=n)
    x.axhline(0, **fs.GUIDE)
    x.set_xlim(0, 520)
    x.set_xlabel(r"$t/M$")
    x.set_ylabel(r"$[M_{\rm AH}(t)-M_{\rm AH}(100)]/10^{-5}M$")
    x.legend(fontsize=6.5, frameon=False, ncol=2)
    x.set_title("(b) converged-finder masses", loc="left", fontsize=9)
    fs.save(fig, os.path.join(outdir, "fe_analyse"))
    plt.close(fig)


if __name__ == "__main__":
    main()
