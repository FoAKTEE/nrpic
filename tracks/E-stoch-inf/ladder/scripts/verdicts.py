#!/usr/bin/env python3
"""Verdicts on A1-A5 of the SR ladder from the outputs of analyse_all.py (one or several
result directories), against the thresholds of SCOPE 4 restated in ../JOURNAL.md entry 1.

    verdicts.py --res DIR [DIR ...] --out summary.json [--rundirs DIR ...]

--rundirs: output directories of the simulation runs, for the cost per step (athena.log).
Orders between resolutions use the odd parts interpolated to common times (log-linear in
time), because the dump times differ by up to one step between resolutions.
"""
import argparse
import glob
import json
import os
import re

import numpy as np


def load_json(dirs, name):
    for d in dirs:
        p = os.path.join(d, name)
        if os.path.isfile(p):
            with open(p) as fp:
                return json.load(fp)
    return None


def interp_log(t_src, y_src, t):
    y = np.asarray(y_src, float)
    ok = y > 0
    return np.exp(np.interp(t, np.asarray(t_src)[ok], np.log(y[ok]), left=np.nan,
                            right=np.nan))


def orders(rows_lo, rows_hi, key, tmin=0.4, tmax=3.6):
    t_lo = np.array([r["time"] for r in rows_lo])
    t_hi = np.array([r["time"] for r in rows_hi])
    y_lo = np.array([r[key] for r in rows_lo])
    y_hi = interp_log(t_hi, [r[key] for r in rows_hi], t_lo)
    sel = (t_lo >= tmin) & (t_lo <= tmax) & np.isfinite(y_hi)
    p = np.log2(y_lo[sel] / y_hi[sel])
    return dict(times=t_lo[sel].tolist(), order=p.tolist(),
                lo=y_lo[sel].tolist(), hi=y_hi[sel].tolist())


def cost(rundirs):
    out = {}
    for d in rundirs:
        for log in glob.glob(os.path.join(d, "*", "athena.log")):
            name = os.path.basename(os.path.dirname(log))
            txt = open(log, errors="replace").read()
            cyc = re.findall(r"^time=\S+ cycle=(\d+)", txt, re.M)
            cpu = re.findall(r"cpu time used\s*=\s*(\S+)", txt)
            zc = re.findall(r"zone-cycles/cpu_second\s*=\s*(\S+)", txt)
            if cyc and cpu:
                out[name] = dict(cycles=int(cyc[-1]), seconds=float(cpu[-1]),
                                 s_per_step=float(cpu[-1]) / max(int(cyc[-1]), 1),
                                 zone_cycles_per_s=float(zc[-1]) if zc else None)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--rundirs", nargs="*", default=[])
    a = ap.parse_args()
    R = a.res
    S = dict(thresholds=dict(A1=1e-4, A2=0.02, A3_ratio=0.01, A3_drift=2.5e-3,
                             A4="even part dominates during the entry; halving factor 4; "
                                "magnitude within 10x of 1e-10; sign flip first order",
                             A5="order of the convergent part between 4 and 6"))
    # A1
    a1 = {}
    for name in ("L32p", "L64p", "L128p", "L256p", "P256", "Q64p", "Q128p"):
        j = load_json(R, f"{name}.json")
        if j is not None:
            a1[name] = j["A1_max"]
    S["A1"] = dict(per_run=a1, pass_=all(max(v["phi"], v["Pi"], v["K"]) < 1e-4
                                         for v in a1.values()) if a1 else None)
    # A2, A3, spectrum
    for key in ("A2", "A3", "spectrum"):
        S[key] = {}
    for name in ("L32p", "L64p", "L128p", "L256p", "P256", "Q64p", "Q128p"):
        j = load_json(R, f"{name}_judge.json")
        if j is None:
            continue
        S["A2"][name] = dict(N_f=j["N_f"], **j["A2"])
        S["A3"][name] = j["A3"]
        S["spectrum"][name] = j["spectrum"]
    # pairs
    pairs = {}
    for f in sorted(set(sum([glob.glob(os.path.join(d, "pair_*.json")) for d in R], []))):
        with open(f) as fp:
            pairs[os.path.basename(f)[5:-5]] = json.load(fp)["rows"]
    # A5 on the L ladder
    a5 = {}
    for n in (32, 64, 128):
        lo, hi = pairs.get(f"L{n}p_L{n}m"), pairs.get(f"L{2*n}p_L{2*n}m")
        if lo is None or hi is None:
            continue
        oh, om = orders(lo, hi, "H_odd"), orders(lo, hi, "M_odd")
        ev = orders(lo, hi, "H_even")
        a5[f"{n}->{2*n}"] = dict(H_odd=oh, M_odd=om,
                                 H_even_ratio=[2.0**x for x in ev["order"]],
                                 H_order_range=[min(oh["order"]), max(oh["order"])]
                                 if oh["order"] else None,
                                 M_order_range=[min(om["order"]), max(om["order"])]
                                 if om["order"] else None)
    S["A5"] = a5
    # A4 at the paper set-up and on the ladder
    a4 = {}
    for tag, (p, h) in {"N32": ("L32p_L32m", "L32ph_L32mh"), "N64": ("Q64p_Q64m", "Q64ph_Q64mh"),
                        "N128": ("Q128p_Q128m", "Q128ph_Q128mh"), "N256": ("P256_P256m", None),
                        "L64": ("L64p_L64m", None), "L128": ("L128p_L128m", None),
                        "L256": ("L256p_L256m", None)}.items():
        rows = pairs.get(p)
        if rows is None:
            continue
        ent = [r for r in rows if 0.4 <= r["time"] <= 4.6]
        d = dict(max_odd_over_even_H=max(r["H_odd"] / r["H_even"] for r in ent),
                 max_odd_over_even_M=max(r["M_odd"] / r["M_even"] for r in ent),
                 max_record_H=max(max(r["ratio_H_p"], r["ratio_H_m"]) for r in rows),
                 max_record_M=max(max(r["ratio_M_p"], r["ratio_M_m"]) for r in rows),
                 first_efold_odd_exceeds_even_H=next((r["efolds"] for r in ent
                                                      if r["H_odd"] > r["H_even"]), None))
        if h is not None and pairs.get(h) is not None:
            rh = pairs[h]
            m = min(len(rows), len(rh))
            d["halving_even_H"] = [rows[i]["H_even"] / rh[i]["H_even"] for i in range(1, m)]
            d["halving_odd_H"] = [rows[i]["H_odd"] / rh[i]["H_odd"] for i in range(1, m)]
        a4[tag] = d
    S["A4"] = a4
    nc = {}
    for n, (p, c) in {32: ("L32p", "NC32p"), 64: ("Q64p", "NC64p"),
                      128: ("Q128p", "NC128p")}.items():
        rows_c = pairs.get(f"{c}_{c[:-1]}m")
        rows_p = pairs.get({32: "L32p_L32m", 64: "Q64p_Q64m", 128: "Q128p_Q128m"}[n])
        if rows_c is None or rows_p is None:
            continue
        m = min(len(rows_c), len(rows_p))
        nc[f"N{n}"] = dict(
            H_record_ratio_max=max(rows_c[i]["ratio_H_p"] / rows_p[i]["ratio_H_p"]
                                   for i in range(1, m)),
            M_record_max=max(r["ratio_M_p"] for r in rows_c),
            H_odd_over_even_min_first2=min(r["H_odd"] / r["H_even"] for r in rows_c
                                           if 0.4 <= r["time"] <= 2.1))
    S["negative_control"] = nc
    if a.rundirs:
        S["cost"] = cost(a.rundirs)
    with open(a.out, "w") as fp:
        json.dump(S, fp, indent=1)
    # short print
    print("A1", json.dumps(S["A1"]["per_run"]))
    for k, v in S["A2"].items():
        print(f"A2 {k}: N_f {v['N_f']:.2f} max D (|n|<=kmax/2) {v['max_D_half']:.2e} "
              f"all {v['max_D_all']:.2e} pass {v['pass_']}")
    for k, v in S["A3"].items():
        if v.get("n_modes"):
            print(f"A3 {k}: {v['n_modes']} modes, max|ratio-1| {v['max_abs_ratio_minus_1']:.2e},"
                  f" max|drift| {v['max_abs_drift_nr']:.2e} (MS {v['max_abs_drift_lin']:.2e})"
                  f" pass {v['pass_']}")
    for k, v in S["spectrum"].items():
        print(f"spectrum {k}: {v}")
    for k, v in S["A5"].items():
        print(f"A5 {k}: H order {v['H_order_range']}, M order {v['M_order_range']}, "
              f"even H ratio {np.round(v['H_even_ratio'], 3).tolist()}")
    for k, v in S["A4"].items():
        print(f"A4 {k}: " + ", ".join(f"{kk} {np.round(vv, 3).tolist() if isinstance(vv, list) else vv}"
                                      for kk, vv in v.items()))
    for k, v in S["negative_control"].items():
        print(f"NC {k}: {v}")
    if "cost" in S:
        for k, v in sorted(S["cost"].items()):
            print(f"cost {k}: {v}")


if __name__ == "__main__":
    main()
