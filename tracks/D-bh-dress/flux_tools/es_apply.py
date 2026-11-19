#!/usr/bin/env python3
"""Journal entry 3: the flux tools applied to the wave-2 card runs ES-1 (black hole in a
vacuum bubble inside expanding dust) and V-1 (its vacuum control).

    es_apply.py --es <ES-1 run dir> --v1 <V-1 run dir> --data <data run dir> [--t0 100]
                [--floor 2.8e-5] [--out DIR]

(a) compare(): ES-1 finder mass against the excised rest mass of its history (release
    runs have no removal record), V-1 as the vacuum control, from t0;
(b) the energy the code assigns to a particle, E = alpha W - beta^i u_i (from traj.bin and
    trajmet.bin), against the exact Killing energy E_K = (1 + 2 E_LTB)^(1/2) of the tracer
    groups inside the bubble (exactly Schwarzschild of mass M by Birkhoff's theorem).
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import compare as cmp  # noqa: E402
import fluxio  # noqa: E402


def tracer_energies(run, base, groups, hst):
    tr = fluxio.read_traj(os.path.join(run, f"{base}.traj.bin"),
                          os.path.join(run, f"{base}.trajmet.bin"))
    t_end = float(hst["time"][-1])
    out = []
    for g in groups:
        lo, hi = g["tags"]
        EK = float(np.sqrt(1.0 + 2.0 * g["E"])) if g["R0"] < 36.0 else None
        rows = []
        for tag in range(lo, hi + 1):
            d = tr.get(tag)
            if d is None:
                continue
            excised = d["time"][-1] < t_end - 1.0
            rows.append(dict(tag=tag, t=d["time"], E=d["E"], alpha=d["alpha"],
                             excised=bool(excised), t_last=float(d["time"][-1]),
                             E_last=float(d["E"][-1]), E0=float(d["E"][0])))
        out.append(dict(group=g["index"], R0=g["R0"], E_LTB=g["E"], E_K=EK, rows=rows))
    return out


def summarise(groups):
    s = []
    for g in groups:
        if g["E_K"] is None:
            continue
        rows = g["rows"]
        ex = [r for r in rows if r["excised"]]
        ent = dict(group=g["group"], R0=g["R0"], E_K=g["E_K"], n=len(rows), n_excised=len(ex),
                   E0_over_EK=float(np.median([r["E0"] for r in rows]) / g["E_K"]))
        if ex:
            ent["t_excision_median"] = float(np.median([r["t_last"] for r in ex]))
            ratio = np.array([r["E_last"] for r in ex]) / g["E_K"]
            ent["E_at_excision_over_EK"] = [float(ratio.min()), float(np.median(ratio)), float(ratio.max())]
        # variation over the first 50 M of the median path
        r0 = rows[0]
        sel = r0["t"] <= 50.0
        if sel.sum() > 2:
            ent["E_variation_first_50M"] = float((r0["E"][sel].max() - r0["E"][sel].min()) / g["E_K"])
        s.append(ent)
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--es", required=True)
    ap.add_argument("--v1", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--t0", type=float, default=100.0)
    ap.add_argument("--floor", type=float, default=2.8e-5)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    meta = json.load(open(os.path.join(a.data, "es", "es.json")))
    groups = meta["tracers"]
    hor_es = fluxio.read_horizon(os.path.join(a.es, "es.horizon_summary_0.txt"))
    hor_v1 = fluxio.read_horizon(os.path.join(a.v1, "v1.horizon_summary_0.txt"))
    hst_es = fluxio.read_hst(os.path.join(a.es, "es.nrpic.hst"))
    hst_v1 = fluxio.read_hst(os.path.join(a.v1, "v1.nrpic.hst"))
    res = {}
    c = cmp.compare(hor_es, a.t0, hst=hst_es, ctrl=hor_v1, floor=a.floor)
    res["null_es1_vs_v1"] = c["summary"]
    cmp.plot(c, os.path.join(a.out, "es1_null_compare"),
             f"ES-1: finder mass against excised mass, V-1 control, t0 = {a.t0:g} M")
    cv = cmp.compare(hor_v1, a.t0, hst=hst_v1, floor=a.floor)
    res["v1_against_floor"] = cv["summary"]
    tes = tracer_energies(a.es, "es", groups, hst_es)
    tv1 = tracer_energies(a.v1, "v1", groups, hst_v1)
    res["tracers_es1"] = summarise(tes)
    res["tracers_v1"] = summarise(tv1)
    figure(a.out, tes, tv1, hst_es, hst_v1)
    with open(os.path.join(a.out, "es_apply.json"), "w") as f:
        json.dump(cmp.jsonable(res), f, indent=1)
    print(json.dumps(cmp.jsonable(res), indent=1))


def figure(out, tes, tv1, hst_es, hst_v1):
    sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "python", "nrpic"))
    import figstyle
    import matplotlib.pyplot as plt
    figstyle.use_style()
    fig, ax = plt.subplots(1, 3, figsize=(figstyle.FULL_WIDTH, 3.0))
    cols = figstyle.SERIES
    for k, (name, tr, hst) in enumerate((("ES-1", tes, hst_es), ("V-1", tv1, hst_v1))):
        a = ax[k]
        for gi, g in enumerate(tr):
            if g["E_K"] is None:
                continue
            for j, r in enumerate(g["rows"]):
                a.plot(r["t"], r["E"] / g["E_K"], color=cols[gi % len(cols)], lw=0.6, alpha=0.6,
                       label=f"group {g['group']}, $R_0={g['R0']:g}M$" if j == 0 else None)
                if r["excised"]:
                    a.plot(r["t_last"], r["E_last"] / g["E_K"], "x", color=cols[gi % len(cols)], ms=4)
        a.axhline(1.0, **figstyle.GUIDE)
        a.set_xlabel(r"$t\ [M]$")
        a.set_ylabel(r"$E_{\rm code}/E_{\rm K}$")
        a.set_title(name + " (x: last record before excision)", fontsize=8)
        a.legend(fontsize=6)
    a = ax[2]
    for name, hst, ls in (("ES-1", hst_es, "-"), ("V-1", hst_v1, "--")):
        for col, lab, c in (("alpha_probe2", "x = 4M", cols[0]), ("alpha_probe3", "x = 20M", cols[1]),
                            ("alpha_probe4", "x = 36M", cols[2])):
            a.plot(hst["time"], hst[col], ls=ls, color=c, lw=1, label=f"{name} {lab}")
    a.axhline(1.0, **figstyle.THIN)
    a.set_xlabel(r"$t\ [M]$")
    a.set_ylabel(r"lapse at probe")
    a.legend(fontsize=5, ncol=2)
    fig.tight_layout()
    figstyle.save(fig, os.path.join(out, "es_tracer_energy"))
    plt.close(fig)


if __name__ == "__main__":
    main()
