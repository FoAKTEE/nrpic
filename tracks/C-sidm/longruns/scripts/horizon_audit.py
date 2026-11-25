#!/usr/bin/env python3
"""Recheck of the collapse and horizon times of C-sidm's G2 package against the horizon finder's
status files (decision 0040 item 3; orch outbox 20261125T151500Z).

For every run id named in the given stage files (and any run ids given on the command line):
  - analysis runs (no AthenaK executable in the manifest) are listed and skipped;
  - simulation runs: the deck (chain/input.athinput, else the manifest's input file) is read for a
    <fastflow> block and `diagnostics = true`; the output directory is searched (top level and
    one level down, restart directories excluded) for `*horizon_summary_*` and
    `horizon_status_*` files; where both exist, each summary line is matched to the nearest
    status line in time and the searches that did not find a horizon are counted;
  - the collapse time read from the lapse, t_c = first linear crossing of alpha_min = 0.3 in
    `*.nrpic.hst` (later segments of a restarted run replace earlier rows), is recomputed with
    the reader of blockA_delta.py, so the package's numbers are checked from the histories.
Writes OUT/horizon_audit.json and OUT/fig_horizon_audit.png.

    python3 horizon_audit.py --out DIR --stage-files F [F ...] [--runs RUN ...]
"""
import argparse
import glob
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from blockA_delta import crossing, read_hist  # noqa: E402

WT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
SCR = "/data/haiyangw/nrpic/scratch/C-sidm"
RID = re.compile(r"C-20\d{6}-\d{6}-[0-9a-f]{7}")


def deck_text(run, man):
    for p in (os.path.join(SCR, run, "chain", "input.athinput"),):
        if os.path.exists(p):
            return p, open(p).read()
    f = (man.get("input") or {}).get("file")
    if f:
        p = f if os.path.isabs(f) else os.path.join(WT, f)
        if os.path.exists(p):
            return p, open(p).read()
    decks = sorted(glob.glob(os.path.join(SCR, run, "*.athinput")))
    if decks:
        return decks[0], open(decks[0]).read()
    return None, ""


def live(text):
    return "\n".join(ln.split("#", 1)[0] for ln in text.splitlines())


def horizon_files(run):
    out = {"summary": [], "status": []}
    for depth in ("*", "*/*"):
        for p in glob.glob(os.path.join(SCR, run, depth)):
            if "/rst/" in p or not os.path.isfile(p):
                continue
            b = os.path.basename(p)
            if "horizon_summary" in b:
                out["summary"].append(p)
            elif b.startswith("horizon_status"):
                out["status"].append(p)
    return out


def table(path):
    rows = []
    for ln in open(path):
        if ln.startswith("#") or not ln.strip():
            continue
        rows.append(ln.split())
    return rows


def match_status(summary, status):
    """Each summary line to the nearest status line by time (column 2 of the summary, column 1 of
    the status file: decision 0040 item 3); counts of searches found / not found."""
    s = table(summary)
    st = table(status)
    if not s or not st:
        return {"summary_lines": len(s), "status_lines": len(st)}
    ts = np.array([float(r[0]) for r in st])
    found = [r[1] for r in st]
    n_ok = n_fail = 0
    for r in s:
        t = float(r[1])
        k = int(np.argmin(abs(ts - t)))
        if found[k].lower() in ("1", "true", "found", "ok"):
            n_ok += 1
        else:
            n_fail += 1
    return {"summary_lines": len(s), "status_lines": len(st), "matched_found": n_ok,
            "matched_not_found": n_fail}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--stage-files", nargs="*", default=[])
    ap.add_argument("--runs", nargs="*", default=[])
    a = ap.parse_args()
    runs = []
    for f in a.stage_files:
        for r in RID.findall(open(f).read()):
            if r not in runs:
                runs.append(r)
    for r in a.runs:
        if r not in runs:
            runs.append(r)
    res = []
    for r in runs:
        mp = os.path.join(WT, "tracks", "C-sidm", "runs", r, "manifest.json")
        if not os.path.exists(mp):
            res.append({"run": r, "kind": "no manifest"})
            continue
        man = json.load(open(mp))
        exe = ((man.get("code") or {}).get("exe") or "")
        cmd = " ".join(man.get("command") or [])
        sim = "athena" in os.path.basename(exe) or "submit_chain" in cmd or "gpu_batch" in cmd
        row = {"run": r, "purpose": (man.get("purpose") or "")[:90], "status": man.get("status")}
        if not sim:
            row["kind"] = "analysis"
            res.append(row)
            continue
        row["kind"] = "simulation"
        dp, txt = deck_text(r, man)
        lt = live(txt)
        row["deck"] = dp
        row["finder_in_deck"] = "<fastflow>" in lt
        row["diagnostics_true"] = bool(re.search(r"(?m)^\s*diagnostics\s*=\s*true", lt))
        hf = horizon_files(r)
        row["horizon_summary_files"] = len(hf["summary"])
        row["horizon_status_files"] = len(hf["status"])
        if hf["summary"] and hf["status"]:
            row["status_match"] = [match_status(s, st) for s, st in zip(sorted(hf["summary"]), sorted(hf["status"]))]
        hs = sorted(glob.glob(os.path.join(SCR, r, "*.nrpic.hst")))
        if hs:
            H = read_hist(hs[0])
            row["hist"] = os.path.basename(hs[0])
            row["t_end"] = float(H["time"][-1])
            tc = crossing(H["time"], H["alpha_min"]) if "alpha_min" in H else None
            row["t_c_alpha_min_0p3"] = None if tc is None else float(tc)
            row["alpha_min_last"] = float(H["alpha_min"][-1]) if "alpha_min" in H else None
        else:
            row["hist"] = None
        res.append(row)
    sims = [x for x in res if x.get("kind") == "simulation"]
    summ = {"runs": len(res), "simulations": len(sims),
            "analyses": sum(1 for x in res if x.get("kind") == "analysis"),
            "with_finder_in_deck": sum(1 for x in sims if x.get("finder_in_deck")),
            "with_diagnostics": sum(1 for x in sims if x.get("diagnostics_true")),
            "with_horizon_files": sum(1 for x in sims if x.get("horizon_summary_files") or x.get("horizon_status_files")),
            "collapsed_by_lapse": sum(1 for x in sims if x.get("t_c_alpha_min_0p3") is not None)}
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "horizon_audit.json"), "w") as f:
        json.dump({"summary": summ, "runs": res}, f, indent=1)
    print(json.dumps(summ))
    for x in sims:
        print(f"{x['run']} finder={x.get('finder_in_deck')} diag={x.get('diagnostics_true')} "
              f"hfiles={x.get('horizon_summary_files')}/{x.get('horizon_status_files')} "
              f"t_end={x.get('t_end')} t_c(alpha_min=0.3)={x.get('t_c_alpha_min_0p3')} | {x['purpose'][:60]}")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, os.path.join(WT, "python"))
    try:
        from nrpic import figstyle
        figstyle.apply()
    except Exception:
        pass
    fig, ax = plt.subplots(figsize=(7.0, 0.32 * max(len(sims), 4) + 1.2))
    for i, x in enumerate(sims):
        te = x.get("t_end") or 0.0
        ax.plot([0, te], [i, i], color="0.75", lw=2)
        tc = x.get("t_c_alpha_min_0p3")
        if tc is not None:
            ax.plot(tc, i, "o", color="C3", ms=5)
        mk = "s" if x.get("horizon_status_files") else "x"
        ax.plot(te + 12, i, mk, color="k" if mk == "s" else "C0", ms=4)
    ax.set_yticks(range(len(sims)))
    ax.set_yticklabels([x["run"][2:17] + " " + (x["purpose"].split(":")[1][:22] if ":" in x["purpose"] else "")
                        for x in sims], fontsize=6)
    ax.set_xlabel("t / M")
    ax.set_title("G2 runs: record (grey), t_c from alpha_min = 0.3 (red), finder status file: x none", fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(a.out, "fig_horizon_audit.png"), dpi=140)
    print("wrote", os.path.join(a.out, "fig_horizon_audit.png"))


if __name__ == "__main__":
    main()
