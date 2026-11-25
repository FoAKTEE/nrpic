#!/usr/bin/env python3
"""Rerun script of the G2 package of D-bh-dress (checklist C6).

Every run id cited in the G2 stage files (CHECKLIST.md, EVIDENCE.md, LADDER.md, OPEN.md, STAGE_REPORT.md;
not VERIFY_RESULTS.md, the stage tool's list of every registered run) is looked up in tracks/D-bh-dress/runs/<id>/manifest.json and sorted:

  analysis   launcher local: the registered command is rerun as a NEW registered run through
             `harness/bin/nrpic-run submit --kind scouting --gate G2 --cores 1 -- <command>`; it
             reads the registered outputs of the card runs under scratch/D-bh-dress/ and writes
             into its own run directory. The command is the manifest's, run on the current tree;
             the manifest keeps the commit of the original reading (`git.commit`).
  card       launcher batch or chain: listed with input deck, executable and card-hours; such a run
             is repeated only through the shared queue (`harness/bin/nrpic-queue add ... -- <the
             nrpic-run submit arguments>`), never by this script.
  missing    cited but without a manifest in this worktree (reported, never guessed).

Usage (from the worktree root):
  python3 tracks/D-bh-dress/stage/G2/rerun_g2.py               # list what would run (default)
  python3 tracks/D-bh-dress/stage/G2/rerun_g2.py --run [--only ID ...]   # rerun the analyses
  python3 tracks/D-bh-dress/stage/G2/rerun_g2.py --json FILE    # write the plan as JSON
No card job is ever submitted. Analyses run one after another on one core each.
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TRACK = os.path.dirname(os.path.dirname(HERE))          # tracks/D-bh-dress
ROOT = os.path.dirname(os.path.dirname(TRACK))          # worktree root
RID = re.compile(r"\bD-(?:bh-dress-)?20\d{6}-\d{6}-[0-9a-f]{7}\b")


def cited_ids():
    ids = {}
    for f in sorted(glob.glob(os.path.join(HERE, "*.md"))):
        if os.path.basename(f).startswith("VERIFY_RESULTS"):   # the stage tool's list of every run
            continue
        for line_no, line in enumerate(open(f), 1):
            for m in RID.findall(line):
                ids.setdefault(m, []).append(f"{os.path.basename(f)}:{line_no}")
    return ids


SCRATCH = "/data/haiyangw/nrpic/scratch/D-bh-dress"


def safe_command(rid, cmd):
    """The command with the original run directory replaced by '$NRPIC_RUN_DIR' (nrpic-run substitutes
    it), so that a rerun never writes into the registered output of the original; None if the command
    names no output directory of its own (it would write elsewhere: listed, not rerun)."""
    own = os.path.join(SCRATCH, rid)
    cmd = [c.replace(own, "$NRPIC_RUN_DIR") for c in cmd]
    return cmd if any("$NRPIC_RUN_DIR" in c or "NRPIC_RUN_DIR" in c for c in cmd) else None


def classify(rid):
    p = os.path.join(TRACK, "runs", rid, "manifest.json")
    if not os.path.exists(p):
        return dict(kind="missing")
    m = json.load(open(p))
    launcher = m.get("launcher") or "local"
    res = m.get("resources") or {}
    cmd = m.get("command")
    cmd = cmd if isinstance(cmd, list) else ["bash", "-c", str(cmd)]
    out = dict(status=m.get("status"), purpose=(m.get("purpose") or "")[:160], launcher=launcher,
               commit=(m.get("git") or {}).get("commit") if isinstance(m.get("git"), dict) else None)
    if launcher in ("batch", "chain") or (res.get("gpus") or 0) > 0:
        out.update(kind="card", input=m.get("input"),
                   inputs=[i.get("path") for i in (m.get("inputs") or []) if isinstance(i, dict)],
                   gpu_hours=res.get("gpu_hours"), command=cmd)
    else:
        sim = any("athena" in os.path.basename(c.split()[0]) for c in cmd if c.strip()) or \
            any("athena_cpu" in c or "/athena " in c or c.endswith("/athena") for c in cmd)
        out.update(kind="processor_sim" if sim else "analysis", command=cmd,
                   rerun_command=safe_command(rid, cmd))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true", help="rerun the analyses (registered)")
    ap.add_argument("--only", nargs="*", default=None, help="restrict to these run ids")
    ap.add_argument("--json", default=None)
    ap.add_argument("--include-sims", action="store_true",
                    help="also rerun processor simulations (AthenaK on processors; can take hours)")
    a = ap.parse_args()
    ids = cited_ids()
    plan = {rid: dict(cited=ids[rid], **classify(rid)) for rid in sorted(ids)}
    if a.only:
        plan = {k: v for k, v in plan.items() if k in a.only}
    kinds = ("analysis", "processor_sim", "card", "missing")
    n = {k: sum(1 for v in plan.values() if v["kind"] == k) for k in kinds}
    print(f"G2 package of D-bh-dress: {len(plan)} cited run ids: {n['analysis']} analyses, {n['processor_sim']} "
          f"processor simulations, {n['card']} card runs, {n['missing']} without a manifest here; "
          f"{sum(1 for v in plan.values() if v.get('kind') in ('analysis', 'processor_sim') and v.get('rerun_command') is None)}"
          f" without an output directory of their own (listed, not rerun)")
    for rid, v in plan.items():
        if v["kind"] in ("analysis", "processor_sim"):
            tag = "analysis" if v["kind"] == "analysis" else "proc-sim"
            rc = v["rerun_command"]
            print(f"[{tag}] {rid}  ({v['cited'][0]}){'' if rc else '  NOT RERUN: no own output directory'}"
                  f"\n    {' '.join(rc or v['command'])[:400]}")
        elif v["kind"] == "card":
            print(f"[card]     {rid}  {v['launcher']}, input {v['input']}, gpu_hours {v['gpu_hours']}  "
                  f"(repeat through nrpic-queue only)")
        else:
            print(f"[missing]  {rid}  cited at {', '.join(v['cited'][:3])}")
    if a.json:
        with open(a.json, "w") as f:
            json.dump(plan, f, indent=1)
    if not a.run:
        return 0
    fails = []
    for rid, v in plan.items():
        if v["kind"] == "card" or v["kind"] == "missing" or v.get("rerun_command") is None:
            continue
        if v["kind"] == "processor_sim" and not a.include_sims:
            continue
        cmd = v["rerun_command"]
        sub = [os.path.join(ROOT, "harness", "bin", "nrpic-run"), "submit", "--kind", "scouting", "--gate", "G2",
               "--cores", "1", "--purpose", f"G2 rerun (stage/G2/rerun_g2.py) of {rid}", "--"] + cmd
        print("running", rid, flush=True)
        r = subprocess.run(sub, cwd=ROOT, env=dict(os.environ, OMP_NUM_THREADS="1"))
        if r.returncode != 0:
            fails.append(rid)
    print("failed reruns:", fails or "none")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
