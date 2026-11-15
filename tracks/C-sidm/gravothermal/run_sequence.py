"""Equilibrium sequences, criteria and the comparison with F21 (arXiv:2108.11967).

    python3 -E run_sequence.py <f21_tables.json> <outdir>

<f21_tables.json> is written by `python3 -I paper_tables.py <main.tex> <json>`.
Writes into <outdir>:
  table1_compare.csv   every row of F21 Table 1 (main.tex:490-583) beside this solver
  table2_compare.csv   every row of F21 Table 2 (main.tex:605-618): root <gamma> = gamma_cr
  criteria.json        per b: maxima of E^, B^, eps; root <gamma> = gamma_cr; root
                       gamma_cr = 5/3; exact fluid onset omega_0^2 = 0 for gamma = 1 + p/u and
                       for gamma = 5/3 (Rayleigh-Ritz, finite elements)
  sequences.json       dense sequences in w0 (all columns and omega_0^2) for the figures
  eos.json             v/c and gamma versus b w for b = 0.5 ... 0.001 (F21 Fig. 2)
  profiles.json        radial profiles of the marginal configurations at b = 0.1 (F21 Fig. 4)
  summary.md           the numbers, for the README
"""
import csv
import json
import math
import os
import sys
import time

import numpy as np
from scipy.optimize import brentq

import tmb

COLS = ["E", "Erest", "B", "eps", "R", "C", "Z0", "ec0", "rho0", "p0", "v0", "gavg", "gcr"]
BS = (0.1, 0.2, 0.3, 0.5)
NFEM = 600


def omega2(b, w0, gamma_mode="F21"):
    return float(tmb.pulsation(b, w0, N=NFEM, gamma_mode=gamma_mode)["omega2"][0])


def strip(e):
    return {k: v for k, v in e.items() if not k.startswith("_")}


def main(tables_path, outdir):
    t_start = time.time()
    os.makedirs(outdir, exist_ok=True)
    tab = json.load(open(tables_path))

    # ------------------------------------------------------------- Table 1, row by row
    rows = []
    for r in tab["table1"]:
        e = tmb.solve(r["b"], r["w0"])
        row = dict(line=r["line"], b=r["b"], w0=r["w0"], underlined=" ".join(r["underlined"]))
        for k in COLS:
            row[f"{k}_paper"] = r[k]
            row[f"{k}_here"] = e[k]
            row[f"{k}_rel"] = e[k] / r[k] - 1.0
        row["C_from_paper_R"] = e["E"] / r["R"]
        rows.append(row)
    with open(os.path.join(outdir, "table1_compare.csv"), "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        wr.writeheader()
        wr.writerows(rows)

    # ------------------------------------------------------------- Table 2: the roots
    rows2 = []
    for r in tab["table2"]:
        b = r["b"]
        lo, hi = 0.97 * r["w0"], 1.03 * r["w0"]
        e = tmb.gamma_root(b, lo, hi)
        row = dict(line=r["line"], b=b)
        for k in ("w0", "E", "R", "C", "Z0", "ec0", "rho0", "p0", "v0", "gavg"):
            row[f"{k}_paper"] = r[k]
            row[f"{k}_here"] = e[k]
            row[f"{k}_rel"] = e[k] / r[k] - 1.0
        row["gcr_here"] = e["gcr"]
        rows2.append(row)
    with open(os.path.join(outdir, "table2_compare.csv"), "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows2[0].keys()))
        wr.writeheader()
        wr.writerows(rows2)

    # ------------------------------------------------------------- criteria per b
    crit = {}
    seqs = {}
    for b in BS:
        wmax = 0.95 / b if b * 10.0 > 0.95 else 10.0
        grid = np.linspace(0.02 / b * 0.1, min(wmax, 0.95 / b), 90)
        grid = grid[grid * b < 0.95]
        seq = [strip(tmb.solve(b, w)) for w in grid]
        c = {}
        for key in ("E", "B", "eps"):
            lo, hi = tmb.bracket_max(b, key, list(grid))
            c[f"max_{key}"] = strip(tmb.maximum(b, key, lo, hi))
        lo, hi = tmb.bracket_root(lambda w: (lambda e: e["gavg"] - e["gcr"])(tmb.solve(b, w)),
                                  list(grid))
        c["gavg_eq_gcr"] = strip(tmb.gamma_root(b, lo, hi))
        try:
            lo, hi = tmb.bracket_root(lambda w: tmb.solve(b, w)["gcr"] - 5.0 / 3.0, list(grid))
            c["gcr_eq_5_3"] = strip(tmb.gamma_root(b, lo, hi, target=5.0 / 3.0))
        except RuntimeError:
            c["gcr_eq_5_3"] = None
        # exact fluid onset (lowest radial mode), gamma = 1 + p/u and gamma = 5/3
        for mode, tag in (("F21", "omega2_zero_F21gamma"), (5.0 / 3.0, "omega2_zero_gamma53")):
            vals = [omega2(b, w, mode) for w in grid]
            for e, v in zip(seq, vals):
                e[f"omega2_{'F21' if mode == 'F21' else '53'}"] = v
            idx = [i for i in range(len(grid) - 1) if vals[i] > 0 >= vals[i + 1]]
            if idx:
                i = idx[0]
                w_on = brentq(lambda w: omega2(b, w, mode), grid[i], grid[i + 1], xtol=1e-7)
                e_on = strip(tmb.solve(b, w_on))
                e_on["omega2_check"] = omega2(b, w_on, mode)
                c[tag] = e_on
            else:
                c[tag] = None
        crit[str(b)] = c
        seqs[str(b)] = seq
        print(f"b={b}: done ({time.time() - t_start:.0f} s)", flush=True)
    json.dump(crit, open(os.path.join(outdir, "criteria.json"), "w"), indent=1)
    json.dump(seqs, open(os.path.join(outdir, "sequences.json"), "w"))

    # ------------------------------------------------------------- equation of state (F21 Fig. 2)
    eos = {}
    for b in (0.5, 0.1, 0.03, 0.01, 0.001):
        bw = np.linspace(1e-3, 0.995, 200)
        w = bw / b
        eos[str(b)] = dict(bw=bw.tolist(), v=[tmb.v_over_c(b, x) for x in w],
                           gamma=[tmb.gamma_local(b, x) for x in w])
    json.dump(eos, open(os.path.join(outdir, "eos.json"), "w"))

    # ------------------------------------------------------------- profiles at b = 0.1 (F21 Fig. 4)
    prof = {}
    c = crit["0.1"]
    for tag in ("max_E", "max_B", "max_eps", "gavg_eq_gcr", "omega2_zero_F21gamma"):
        if c.get(tag) is None:
            continue
        p = tmb.profiles(0.1, c[tag]["w0"], n=600)
        prof[tag] = {k: (v.tolist() if isinstance(v, np.ndarray) else None)
                     for k, v in p.items() if k != "eq"}
        prof[tag]["w0"] = c[tag]["w0"]
        prof[tag]["R"] = p["eq"]["R"]
    json.dump(prof, open(os.path.join(outdir, "profiles.json"), "w"))

    # ------------------------------------------------------------- summary
    L = ["# Summary of run_sequence.py", ""]
    L.append("## Table 1 of F21, row by row (56 rows): relative difference this solver / paper")
    L.append("")
    L.append("| column | median abs | max abs | row of max (line, b, w0) |")
    L.append("|---|---|---|---|")
    for k in COLS:
        d = np.array([abs(r[f"{k}_rel"]) for r in rows])
        i = int(np.argmax(d))
        L.append(f"| {k} | {np.median(d):.2e} | {d[i]:.2e} | main.tex:{rows[i]['line']}, "
                 f"b={rows[i]['b']}, w0={rows[i]['w0']} |")
    dC = np.array([abs(r["C_from_paper_R"] / r["C_paper"] - 1) for r in rows])
    L.append(f"| C = M^(here)/R^(paper) | {np.median(dC):.2e} | {dC.max():.2e} | |")
    L.append("")
    L.append("## Table 2 of F21 (root <gamma> = gamma_cr): relative difference")
    L.append("")
    L.append("| column | median abs | max abs | row of max |")
    L.append("|---|---|---|---|")
    for k in ("w0", "E", "R", "C", "Z0", "ec0", "rho0", "p0", "v0", "gavg"):
        d = np.array([abs(r[f"{k}_rel"]) for r in rows2])
        i = int(np.argmax(d))
        L.append(f"| {k} | {np.median(d):.2e} | {d[i]:.2e} | main.tex:{rows2[i]['line']}, "
                 f"b={rows2[i]['b']} |")
    L.append("")
    L.append("## Criteria along the sequences (this solver)")
    L.append("")
    L.append("| b | criterion | w0 | E^ | B^ | eps | R^ | C | Z(0) | v(0)/c | <gamma> | gamma_cr |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for b in BS:
        for tag, e in crit[str(b)].items():
            if e is None:
                L.append(f"| {b} | {tag} | none on the sequence | | | | | | | | | |")
                continue
            L.append(f"| {b} | {tag} | {e['w0']:.6g} | {e['E']:.6g} | {e['B']:.6g} | "
                     f"{e['eps']:.6g} | {e['R']:.6g} | {e['C']:.6g} | {e['Z0']:.6g} | "
                     f"{e['v0']:.6g} | {e['gavg']:.6g} | {e['gcr']:.6g} |")
    L.append("")
    L.append(f"wall time {time.time() - t_start:.0f} s")
    open(os.path.join(outdir, "summary.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
