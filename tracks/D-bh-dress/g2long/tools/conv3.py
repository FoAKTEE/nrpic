#!/usr/bin/env python3
"""Three-way convergence of item C2 (stage/G2 CHECKLIST) in one reading (g2long entry 25).

(a) Particle number: horizon mass of N/4, N, 4N (same mesh M/8, same set-up ES-FLK) at the
    named times 100, 200, 300, 399.5 M; N3's ordering |M_4N - M_N| <= |M_N - M_N/4| at each.
(b) Mesh of the growth: Delta M_h(t) = M_AH,h(t) - M_AH,h(t0), t0 = 20 M (L3, entry 10), for
    the members given with --mesh; members flagged "out" are drawn and labelled outside the
    convergent regime (ruling 0039 item 4: M/4) and enter no in-regime statement.
    L3: |DM_16 - DM_8| < |DM_8 - DM_4| at 100, 200, 300 M. C2b: |DM_16 - DM_8| <= 3e-3.
(c) The same with each member's own-mesh vacuum control subtracted (as D2):
    DMc_h(t) = DM_h(t) - [M_ctrl,h(t) - M_ctrl,h(t0)]. Not predicted; read beside (b).
Also (not predicted) the rms of each difference over windows of +-25 M about the named times,
because the finder masses carry noise of ~1e-3 peak to peak (entry 19).

Horizon numbers here come from runs made WITHOUT `<fastflow> diagnostics` (decision 0041 item
4); failed searches are rechecked separately by hz_check.py. The finder summary is read with
fluxio.read_horizon (last record of a repeated time, finite rows).

Usage: conv3.py --out DIR --part NAME=RUNDIR:BASE (x3, coarse to fine: N/4, N, 4N)
                --mesh NAME=RUNDIR:BASE:CTRL_SUMMARY:H:in|out (coarse to fine)
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "flux_tools"))
import fluxio  # noqa: E402

PT = (100.0, 200.0, 300.0, 399.5)
MT = (100.0, 200.0, 300.0)
T0 = 20.0
TOL = 3e-3
WIN = 25.0


def hor(rd, base):
    h = fluxio.read_horizon(os.path.join(rd, base + ".horizon_summary_0.txt"))
    return h["time"], h["mass"]


def at(t, m, tq):
    return float(np.interp(tq, t, m))


def rms_win(tg, d, tq):
    s = np.abs(tg - tq) <= WIN
    return float(np.sqrt(np.mean(d[s] ** 2))) if s.any() else None


def main(argv=None, stem="conv3"):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    ap.add_argument("--part", action="append", required=True)
    ap.add_argument("--mesh", action="append", required=True)
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    out = dict(note="horizon masses from runs made without <fastflow> diagnostics (decision 0041 item 4)",
               t0=T0, particle={}, mesh={})

    # (a) particle number
    P = []
    for s in a.part:
        n, rest = s.split("=", 1)
        rd, base = rest.split(":")
        t, m = hor(rd, base)
        P.append(dict(name=n, run=rd, t=t, m=m))
    tend = min(p["t"][-1] for p in P)
    tg = np.arange(T0, tend + 1e-9, 0.5)
    q, n1, n4 = P
    d_lo = np.interp(tg, n1["t"], n1["m"]) - np.interp(tg, q["t"], q["m"])
    d_hi = np.interp(tg, n4["t"], n4["m"]) - np.interp(tg, n1["t"], n1["m"])
    rows = {}
    for tq in PT:
        if tq > tend + 1e-9:
            continue
        lo = at(n1["t"], n1["m"], tq) - at(q["t"], q["m"], tq)
        hi = at(n4["t"], n4["m"], tq) - at(n1["t"], n1["m"], tq)
        rows[str(tq)] = dict(M={p["name"]: at(p["t"], p["m"], tq) for p in P},
                             dM_N_minus_Nq=lo, dM_4N_minus_N=hi, ordered=bool(abs(hi) <= abs(lo)),
                             rms_win_N_minus_Nq=rms_win(tg, d_lo, tq), rms_win_4N_minus_N=rms_win(tg, d_hi, tq))
    out["particle"] = dict(members=[(p["name"], p["run"], float(p["t"][-1])) for p in P], at=rows,
                           n_ordered=int(sum(r["ordered"] for r in rows.values())), n_times=len(rows))

    # (b), (c) mesh of the growth
    M = []
    for s in a.mesh:
        n, rest = s.split("=", 1)
        rd, base, ctrl, h, reg = rest.split(":")
        t, m = hor(rd, base)
        c = fluxio.read_horizon(ctrl)
        M.append(dict(name=n, run=rd, t=t, m=m, ct=c["time"], cm=c["mass"], h=float(h), inreg=(reg == "in"),
                      ctrl=ctrl))
    tendm = min(x["t"][-1] for x in M + [dict(t=x["ct"]) for x in M])
    tgm = np.arange(T0, tendm + 1e-9, 0.5)
    for x in M:
        x["DM"] = np.interp(tgm, x["t"], x["m"]) - at(x["t"], x["m"], T0)
        x["DMc"] = x["DM"] - (np.interp(tgm, x["ct"], x["cm"]) - at(x["ct"], x["cm"], T0))
    mrows = {}
    for tq0 in MT:
        # a named time just past the common end of the mesh members (FL16 and its control end at
        # 299-299.75 M) is read at the common end and labelled so (added in batch 25 after the first
        # registered reading D-20261126-055207-0137c53 dropped 300 M: entry 27)
        tq = tq0 if tq0 <= tendm + 1e-9 else (tendm if tq0 - tendm <= 1.5 else None)
        if tq is None:
            continue
        r = dict(DM={x["name"]: float(np.interp(tq, tgm, x["DM"])) for x in M},
                 DMc={x["name"]: float(np.interp(tq, tgm, x["DMc"])) for x in M})
        for key in ("DM", "DMc"):
            v = [r[key][x["name"]] for x in M]
            r[key + "_diffs"] = {f"{M[i + 1]['name']}-{M[i]['name']}": v[i + 1] - v[i] for i in range(len(M) - 1)}
            r[key + "_rms_win"] = {f"{M[i + 1]['name']}-{M[i]['name']}":
                                   rms_win(tgm, M[i + 1][key] - M[i][key], tq) for i in range(len(M) - 1)}
        if len(M) == 3:
            dfine = abs(r["DM_diffs"][f"{M[2]['name']}-{M[1]['name']}"])
            dcoarse = abs(r["DM_diffs"][f"{M[1]['name']}-{M[0]['name']}"])
            r["L3_fine_lt_coarse"] = bool(dfine < dcoarse)
        fin = [x for x in M if x["inreg"]]
        if len(fin) >= 2:
            r["C2b_in_regime_absdiff"] = abs(r["DM"][fin[-1]["name"]] - r["DM"][fin[-2]["name"]])
            r["C2b_holds"] = bool(r["C2b_in_regime_absdiff"] <= TOL)
        r["t_named"], r["t_used"] = tq0, float(tq)
        mrows[str(tq0)] = r
    out["mesh"] = dict(members=[dict(name=x["name"], run=x["run"], h=x["h"], in_regime=x["inreg"], control=x["ctrl"],
                                     M_t0=at(x["t"], x["m"], T0), t_end=float(x["t"][-1])) for x in M],
                       t_end_common=float(tendm), at=mrows)
    with open(os.path.join(a.out, stem + ("_numbers" if stem != "conv3" else "") + ".json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))
    figure(a.out, tg, d_lo, d_hi, P, tgm, M, stem)
    return out


def figure(outdir, tg, d_lo, d_hi, P, tgm, M, stem="conv3"):
    import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 3.1))
    fig.subplots_adjust(left=0.075, right=0.985, bottom=0.16, top=0.86, wspace=0.42)
    x = ax[0]
    x.plot(tg, 1e3 * d_lo, color=fs.PAL["red"], lw=1.0, label=f"{P[1]['name']} $-$ {P[0]['name']}")
    x.plot(tg, 1e3 * d_hi, color=fs.PAL["blue"], lw=1.0, label=f"{P[2]['name']} $-$ {P[1]['name']}")
    for tq in PT:
        x.axvline(tq, color="0.6", lw=0.6, ls=":")
    x.axhline(0.0, color="k", lw=0.5)
    x.set_xlabel(r"$t/M$")
    x.set_ylabel(r"$\Delta M_{\rm AH}$ between members [$10^{-3}M$]")
    x.set_title("(a) particle number, M/8", loc="left", fontsize=8)
    x.legend(fontsize=6.5, frameon=False, loc="lower left")
    cols = ["0.5", fs.PAL["red"], fs.PAL["blue"]]
    for k, key, ttl in ((1, "DM", r"(b) mesh, $\Delta M$ from 20 M"), (2, "DMc", "(c) mesh, own vacuum control off")):
        x = ax[k]
        for i in range(len(M) - 1):
            lo, hi = M[i], M[i + 1]
            out_reg = not (lo["inreg"] and hi["inreg"])
            lab = f"{hi['name']} $-$ {lo['name']}" + (" (M/4 outside regime)" if out_reg else "")
            x.plot(tgm, 1e3 * (hi[key] - lo[key]), color=cols[i + 1] if not out_reg else "0.55",
                   ls="--" if out_reg else "-", lw=1.0, label=lab)
        x.axhspan(-1e3 * TOL, 1e3 * TOL, color="grey", alpha=0.13, lw=0)
        x.axhline(0.0, color="k", lw=0.5)
        for tq in MT:
            x.axvline(tq, color="0.6", lw=0.6, ls=":")
        x.set_xlabel(r"$t/M$")
        x.set_ylabel(r"difference of $\Delta M$ [$10^{-3}M$]")
        x.set_title(ttl, loc="left", fontsize=8)
        x.legend(fontsize=6.0, frameon=False, loc="best")
    fig.suptitle("Horizon masses from runs made without the finder diagnostics; band: 3e-3 (D2)", fontsize=7, y=0.985)
    fs.save(fig, os.path.join(outdir, stem))
    plt.close(fig)


if __name__ == "__main__":
    main()
