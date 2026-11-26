#!/usr/bin/env python3
"""Fresh verifier of gate G2 (Track A), item V5: every row of Table V of the note (note/tables/ledger_g2.tex):
the run id has a manifest under tracks/A-emd-pbh/runs/ with a finished status, and each printed value occurs in the
run's registered output (any number in its text, JSON, log or markdown files that rounds to the printed value at
the printed number of significant digits). Plus the spot check of the conv_ball member C: the raw horizon summary
of the card run against the numbers of the analysis.

    python -I table5_check.py --table note/tables/ledger_g2.tex --runs tracks/A-emd-pbh/runs --scratch DIR --out DIR

test_match() checks the matcher on known strings first.
"""
import argparse
import glob
import json
import math
import os
import re

NUM = re.compile(r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?")


def sig_digits(s):
    s = s.strip().lstrip("-+")
    if "e" in s.lower():
        s = s.lower().split("e")[0]
    s = s.replace(".", "").lstrip("0")
    return max(1, len(s))


def matches(printed, value):
    p = float(printed)
    d = sig_digits(printed)
    if value == 0 or p == 0:
        return abs(value - p) < 10 ** (-d)
    if math.copysign(1, p) != math.copysign(1, value):
        return False
    e = math.floor(math.log10(abs(p)))
    q = 10 ** (e - d + 1)
    return abs(value - p) <= 0.5 * q * (1 + 1e-9) or abs(round(value / q) * q - p) < 1e-12 * abs(p)


def test_match():
    cases = [("0.193", 0.19312, True), ("0.193", 0.1936, False), ("-0.0925", -0.092468, True), ("4.35", 4.346046, True),
             ("0.000277", 0.00027716, True), ("2.64", 2.6449, True), ("2", 1.98, True), ("1.5", 1.52, True),
             ("13.8", 13.847, True), ("14.4", 14.3576, True), ("0.045", 0.04428, False)]
    out = [dict(printed=p, value=v, expect=e, got=matches(p, v)) for p, v, e in cases]
    return dict(cases=out, passed=all(c["expect"] == c["got"] for c in out))


def numbers_in(d):
    vals = []
    for f in glob.glob(os.path.join(d, "**", "*"), recursive=True):
        if not os.path.isfile(f) or os.path.getsize(f) > 50e6:
            continue
        if not f.endswith((".json", ".log", ".md", ".txt", ".tex", ".csv")):
            continue
        with open(f, errors="replace") as fh:
            for m in NUM.finditer(fh.read()):
                try:
                    x = float(m.group(0))
                    if math.isfinite(x):
                        vals.append(x)
                except ValueError:
                    pass
    return vals


def parse_table(path):
    rows = []
    with open(path) as f:
        for ln in f:
            if "\\texttt{" not in ln or "&" not in ln:
                continue
            q, v, r = [c.strip() for c in ln.split("&")[:3]]
            run = re.search(r"\\texttt\{([^}]*)\}", r).group(1)
            vals = [x for x in NUM.findall(v.replace("--", " "))]
            # brackets (a, b]: both numbers
            rows.append(dict(quantity=q, printed=vals, run=run))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--table", required=True)
    ap.add_argument("--runs", required=True)
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res = dict(test=test_match(), rows=[])
    print("matcher test", res["test"]["passed"])
    cache = {}
    for row in parse_table(a.table):
        run = row["run"]
        man = os.path.join(a.runs, run, "manifest.json")
        st = None
        if os.path.isfile(man):
            with open(man) as f:
                m = json.load(f)
            st = m.get("status")
        if run not in cache:
            cache[run] = numbers_in(os.path.join(a.scratch, run))
        vals = cache[run]
        found = {p: any(matches(p, v) for v in vals) for p in row["printed"]}
        # orders printed as 1.5, 2: an order of the run's output or the log2 of its error ratios (not searched)
        row.update(manifest=os.path.isfile(man), status=st, n_numbers=len(vals), found=found,
                   all_found=all(found.values()))
        res["rows"].append(row)
        print(f"{run} {st} {row['quantity'][:60]:60s} {row['printed']} -> {found}")
    # spot check: conv_ball member C, raw horizon summary of the card chain against the analysis numbers
    sc = {}
    raw = os.path.join(a.scratch, "A-20261121-083336-6a82131", "ball.horizon_summary_0.txt")
    first = None
    with open(raw) as f:
        for ln in f:
            if ln.startswith("#") or not ln.strip():
                continue
            v = ln.split()
            if v[2] != "nan":
                first = dict(t=float(v[1]), mass=float(v[2]))
                break
    with open(os.path.join(a.scratch, "A-20261121-120257-a2eb839", "C_numbers.json")) as f:
        cn = json.load(f)
    fi = cn["finder"]["first"]
    sc["raw_first_found"] = first
    sc["analysis_first"] = dict(t=fi["t"], mass=fi["mass"], tau_at_horizon=fi["tau_at_horizon"],
                                tau_ah_exact_shell_at_r=fi["tau_ah_exact_shell_at_r"])
    sc["dt_det_C_recomputed"] = fi["tau_at_horizon"] - fi["tau_ah_exact_shell_at_r"]
    sc["raw_equals_analysis"] = bool(first and abs(first["t"] - fi["t"]) < 1e-3 and abs(first["mass"] / fi["mass"] - 1) < 1e-6)
    res["spot_check_C"] = sc
    print("spot check C", json.dumps(sc))
    with open(os.path.join(a.out, "table5_check.json"), "w") as f:
        json.dump(res, f, indent=1)


if __name__ == "__main__":
    main()
