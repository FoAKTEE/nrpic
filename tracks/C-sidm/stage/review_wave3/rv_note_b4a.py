"""Lead's batch-4a check L25 of note v1 (C-sidm): six ledger rows against the JSON of their
runs, and the paper-writing checker with --compile on a copy of the note (the worktree copy
is not touched).

    python3 rv_note_b4a.py --out DIR
"""
import argparse
import glob
import json
import os
import shutil
import statistics
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
NOTE = os.path.abspath(os.path.join(HERE, "..", "..", "note"))
SCR = "/data/haiyangw/nrpic/scratch/C-sidm"
FORBID = ("nrpic_cf|nrpic_geodesic|tmb\\.py|evstatic|make_box|an_step|nrpic-run|athinput|F21|G26|"
          "core-v0|C-pre|anta|A100")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    ledger = open(os.path.join(NOTE, "tables", "ledger.tex")).read()
    s = json.load(open(f"{SCR}/C-20261121-075202-1a37fb9/summary.json"))
    t8 = json.load(open(f"{SCR}/C-20261120-223321-3d088d4/t8.json"))
    cm = json.load(open(f"{SCR}/C-20261121-075359-26e3b31/compare_cc2_M8.json"))
    gv = json.load(open(f"{SCR}/C-20261120-222716-9d86ebc/growth_validation_v2.json"))
    tc = s["groups"]["cc1_kn10_cell"]["t_c_interp"]
    card = [x for x in t8["sets"] if x["n"] == 4000000][0]["params"]
    r = cm["cc2_M8/cc2_M4"]
    rows = {
        "decisive t_c CC1 Kn=10 cell": ", ".join(f"{v:.2f}" for v in tc),
        "decisive sd": f"{statistics.stdev(tc):.2f}",
        "card T8 finest changes": ", ".join(f"{card[p]['finest_change']:.4f}" for p in ("dt_frac", "pmax", "dx_frac")),
        "drift ratios": "; ".join(f"{r[k]:.2f}" for k in ("A_cos", "A_sin_trend", "max_20M_mean")),
        "growth bias sigma 0.1": f"+{gv['G2']['0.1']['v2']['mean_rel_bias'] * 1e4:.1f}e-04",
        "growth bias sigma 0.05": f"{gv['G2']['0.05']['v2']['mean_rel_bias'] * 1e4:.1f}e-04",
    }
    res = {"rows": {k: dict(value=v, in_ledger=(v.replace("e-04", "e-04") in ledger)) for k, v in rows.items()}}
    # the checker on a copy
    work = os.path.join(a.out, "note_copy")
    shutil.copytree(NOTE, work, ignore=shutil.ignore_patterns("scripts", "__pycache__"))
    chk = sorted(glob.glob(os.path.expanduser("~/.claude/skills/synced/*/paper-writing/scripts/check_manuscript.py")))[0]
    p = subprocess.run([sys.executable, chk, "--main", "main.tex", "--compile", "--forbid", FORBID],
                       cwd=work, capture_output=True, text=True)
    open(os.path.join(a.out, "checker.txt"), "w").write(p.stdout + "\n--- stderr ---\n" + p.stderr)
    res["checker_exit"] = p.returncode
    res["checker_tail"] = p.stdout.strip().splitlines()[-25:]
    pdf = os.path.join(work, "main.pdf")
    if os.path.exists(pdf):
        q = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True)
        res["pages"] = [ln for ln in q.stdout.splitlines() if ln.startswith("Pages")]
    json.dump(res, open(os.path.join(a.out, "rv_note_b4a.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
