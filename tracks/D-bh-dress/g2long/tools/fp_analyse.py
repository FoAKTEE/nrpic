#!/usr/bin/env python3
"""Judgement of test FP (g2long/JOURNAL.md entry 10): finder re-search of the long runs' dumps.

Reads <probe dir>/fp/probes.json (tools/probe_long.py) and the runs' own horizon summaries.
FP1 h0 within 3e-5 of the run's own mass at the dump time; h1 and h2 found at every dump.
FP2 V-1L, tight h1 (A16): |M_h1(t) - M_h1(100)| <= 3e-5 at 150-450 M; C1 refuted if
    M_h1(250) - M_h1(200) >= 8e-5.
FP3 the same for V-1L16 at 200, 250, 300 M.
FP4 tight A32 offsets e = M - 1 at 200 M over M/4, M/8, M/16 monotone with q = (e4-e8)/(e8-e16) > 1
    and order log2(q) in [1.5, 4.5]; refuted if q < 1 or a sign change.
FP5 null test with the tight finder: |(M_ES(t) - M_ES(100)) - (M_V(t) - M_V(100))| <= 1e-4 at 200,
    250, 300 M for M/8 (ES-1L, V-1L) and M/16 (ES-1L16, V-1L16).

Usage: fp_analyse.py --probes DIR/fp/probes.json --out DIR NAME=RUNDIR:BASE ... (names V-1L,
V-1L16, V-1L4, ES-1L, ES-1L16; the run directory's basename keys the probes).
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
    ap.add_argument("--probes", required=True, nargs="+")
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    ap.add_argument("runs", nargs="+")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    P = [r for f in a.probes for r in json.load(open(f))]
    R = {}
    for s in a.runs:
        name, rest = s.split("=", 1)
        rd, base = rest.rsplit(":", 1)
        t, m = read_summary(os.path.join(rd, base + ".horizon_summary_0.txt"))
        R[name] = dict(t=t, m=m, rid=os.path.basename(rd.rstrip("/")))
    # probe table: name -> variant -> horizon -> {time: mass}
    T = {}
    for name, v in R.items():
        T[name] = {}
        for p in P:
            if p["run"] != v["rid"]:
                continue
            T[name].setdefault(p["variant"], {}).setdefault(p["horizon"], {})[round(p["time_dump"], 6)] = \
                (p.get("mass") if p.get("found") else None)
    J = {"table": {n: {var: {str(h): {str(k): vv for k, vv in sorted(d.items())} for h, d in hs.items()}
                       for var, hs in T[n].items()} for n in T}}
    # FP1
    devs, missing = [], []
    for n, v in R.items():
        for tt, mm in T[n].get("A16", {}).get(0, {}).items():
            i = int(np.argmin(np.abs(v["t"] - tt)))
            if mm is not None:
                devs.append(dict(run=n, t=tt, run_mass=float(v["m"][i]), t_run=float(v["t"][i]),
                                 h0=mm, dev=mm - float(v["m"][i])))
        for h in (1, 2):
            for tt, mm in T[n].get("A16", {}).get(h, {}).items():
                if mm is None:
                    missing.append((n, h, tt))
    J["FP1"] = dict(max_abs_dev=max(abs(d["dev"]) for d in devs) if devs else None, rows=devs,
                    not_found=missing,
                    holds=bool(devs and max(abs(d["dev"]) for d in devs) <= 3e-5 and not missing))

    def tight(n, var="A16"):
        return T.get(n, {}).get(var, {}).get(1, {})

    for key, n, times in (("FP2", "V-1L", (150.0, 200.0, 250.0, 300.0, 450.0)),
                          ("FP3", "V-1L16", (200.0, 250.0, 300.0))):
        h1 = tight(n)
        if 100.0 in h1 and h1[100.0] is not None:
            d = {str(t): (h1[t] - h1[100.0]) if h1.get(t) is not None else None for t in times}
            vals = [abs(x) for x in d.values() if x is not None]
            jump = (h1[250.0] - h1[200.0]) if (h1.get(250.0) is not None and h1.get(200.0) is not None) else None
            # the run's own drift at the same times, for comparison
            v = R[n]
            own = {}
            i100 = int(np.argmin(np.abs(v["t"] - 100.0)))
            for t in times:
                i = int(np.argmin(np.abs(v["t"] - t)))
                own[str(t)] = float(v["m"][i] - v["m"][i100])
            J[key] = dict(D_tight=d, D_run=own, jump_250_200=jump,
                          holds=bool(vals and max(vals) <= 3e-5),
                          refuted=bool(jump is not None and jump >= 8e-5))
    # FP4
    e = {}
    for n in ("V-1L4", "V-1L", "V-1L16"):
        mm = tight(n, "A32").get(200.0)
        e[n] = (mm - 1.0) if mm is not None else None
    if all(v is not None for v in e.values()):
        q = (e["V-1L4"] - e["V-1L"]) / (e["V-1L"] - e["V-1L16"])
        J["FP4"] = dict(e=e, q=q, p=float(np.log2(q)) if q > 0 else None,
                        e_A16_tight={n: (tight(n).get(200.0) - 1.0) if tight(n).get(200.0) is not None else None
                                     for n in e},
                        holds=bool(q > 1 and 1.5 <= np.log2(q) <= 4.5),
                        refuted=bool(q < 1 or (e["V-1L4"] * e["V-1L"] < 0) or (e["V-1L"] * e["V-1L16"] < 0)))
    # FP5
    fp5 = {}
    for tag, es, vv in (("M8", "ES-1L", "V-1L"), ("M16", "ES-1L16", "V-1L16")):
        he, hv = tight(es), tight(vv)
        if he.get(100.0) is None or hv.get(100.0) is None:
            continue
        rows = {}
        for t in (200.0, 250.0, 300.0):
            if he.get(t) is not None and hv.get(t) is not None:
                rows[str(t)] = (he[t] - he[100.0]) - (hv[t] - hv[100.0])
        fp5[tag] = rows
    if fp5:
        allv = [abs(x) for r in fp5.values() for x in r.values()]
        J["FP5"] = dict(diff=fp5, max_abs=max(allv), holds=bool(max(allv) <= 1e-4))
    # FP-ext (entry 11): every common dump of V-1L and ES-1L, tight finder
    he, hv = tight("ES-1L"), tight("V-1L")
    if he.get(100.0) is not None and hv.get(100.0) is not None:
        ts = sorted(t for t in set(he) & set(hv) if he[t] is not None and hv[t] is not None and t >= 100.0)
        ser = {str(t): (he[t] - he[100.0]) - (hv[t] - hv[100.0]) for t in ts}
        dv = {str(t): hv[t] - hv[100.0] for t in sorted(hv) if hv[t] is not None and t >= 100.0}
        mx = max(abs(x) for x in ser.values())
        J["FPX"] = dict(null_tight=ser, D_V_tight=dv, max_abs_null=mx,
                        i_holds=bool(all(abs(dv[str(t)]) <= 3e-5 for t in (350.0, 400.0, 500.0) if str(t) in dv)),
                        ii_holds=bool(mx <= 5e-5), ii_refuted=bool(mx > 1e-4))
    with open(os.path.join(a.out, "fp_analyse.json"), "w") as f:
        json.dump(J, f, indent=1)
    print(json.dumps({k: v for k, v in J.items() if k != "table"}, indent=1))
    figure(a.out, R, T, J)


def figure(outdir, R, T, J):
    fs.use_style()
    fig, ax = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 6.4), constrained_layout=True)
    mk = {0: ("o", "h0 production, from the dump's radius"), 1: ("s", "h1 tight (1e-9), from 1 M"),
          2: ("^", "h2 production, from 2 M")}
    for x, n, c in ((ax[0, 0], "V-1L", fs.PAL["blue"]), (ax[0, 1], "V-1L16", fs.PAL["green"])):
        if n not in R:
            continue
        v = R[n]
        w = v["t"] >= 90
        x.plot(v["t"][w], v["m"][w] - 1.0, color=c, lw=0.8, label=f"{n} run (production finder)")
        for h, (m, lab) in mk.items():
            d = T[n].get("A16", {}).get(h, {})
            tt = [k for k, vv in d.items() if vv is not None]
            x.plot(tt, [d[k] - 1.0 for k in tt], m, color="k" if h == 1 else c, mfc="white" if h != 1 else "k",
                   ms=5, ls="none", label=lab)
        x.set_xlabel(r"$t/M$")
        x.set_ylabel(r"$M_{\rm AH}/M-1$")
        x.legend(fontsize=6.5, frameon=False, loc="best")
        x.set_title(f"({'a' if n == 'V-1L' else 'b'}) {n}: finder re-search of the dumps", loc="left", fontsize=9)
    x = ax[1, 0]
    for tag, c in (("M8", fs.PAL["red"]), ("M16", fs.PAL["yellow"])):
        if tag == "M8" and "FPX" in J:
            r = J["FPX"]["null_tight"]
            x.plot([float(k) for k in r], list(r.values()), "s-", color=c, ms=5, lw=1.0,
                   label=f"{tag}: tight finder, ES - V (all dumps)")
        elif "FP5" in J and tag in J["FP5"]["diff"]:
            r = J["FP5"]["diff"][tag]
            x.plot([float(k) for k in r], list(r.values()), "s-", color=c, ms=5, lw=1.0,
                   label=f"{tag}: tight finder, ES - V")
    for es, vv, tag, c in (("ES-1L", "V-1L", "M8", fs.PAL["red"]), ("ES-1L16", "V-1L16", "M16", fs.PAL["yellow"])):
        if es in R and vv in R:
            e, v = R[es], R[vv]
            ka = np.round(e["t"] * 8).astype(np.int64)
            kb = np.round(v["t"] * 8).astype(np.int64)
            k, ia, ib = np.intersect1d(ka, kb, return_indices=True)
            tc = k / 8.0
            i100a = int(np.argmin(np.abs(e["t"] - 100)))
            i100b = int(np.argmin(np.abs(v["t"] - 100)))
            dd = (e["m"][ia] - e["m"][i100a]) - (v["m"][ib] - v["m"][i100b])
            w = (tc >= 100) & (tc <= 300)
            x.plot(tc[w], dd[w], color=c, lw=0.6, alpha=0.6, label=f"{tag}: run's own finder")
    for s in (1, -1):
        x.axhline(s * 1e-4, **fs.GUIDE)
    x.set_xlabel(r"$t/M$")
    x.set_ylabel(r"$D_{\rm ES}-D_{\rm V}$")
    x.legend(fontsize=6.5, frameon=False)
    x.set_title("(c) null test with the tight finder (dashed: FP5 bound)", loc="left", fontsize=9)
    x = ax[1, 1]
    hs = {"V-1L4": 0.25, "V-1L": 0.125, "V-1L16": 0.0625}
    for var, h, m, lab, c in (("A16", 0, "o", "production (A16, h0)", fs.PAL["blue"]),
                              ("A16", 1, "s", "tight, A16", fs.PAL["red"]),
                              ("A32", 1, "D", "tight, A32", "k")):
        xs, ys = [], []
        for n, hh in hs.items():
            mm = T.get(n, {}).get(var, {}).get(h, {}).get(200.0)
            if mm is not None:
                xs.append(hh)
                ys.append(mm - 1.0)
        if xs:
            ys = np.array(ys)
            x.plot(xs, np.abs(ys), "-", color=c, lw=0.8)
            for xx, yy in zip(xs, ys):
                x.plot(xx, abs(yy), m, color=c, mfc=c if yy > 0 else "white", ms=6)
            x.plot([], [], m, color=c, label=lab)
    x.set_xscale("log")
    x.set_yscale("log")
    x.set_xlabel(r"$h/M$ (finest level)")
    x.set_ylabel(r"$|M_{\rm AH}/M-1|$ at 200 M (filled $>0$, open $<0$)")
    x.legend(fontsize=6.5, frameon=False)
    x.set_title("(d) offset against mesh spacing, finder converged", loc="left", fontsize=9)
    fs.save(fig, os.path.join(outdir, "fp_analyse"))
    plt.close(fig)


if __name__ == "__main__":
    main()
