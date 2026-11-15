#!/usr/bin/env python3
"""Bring the helpers' hand-written run manifests into the fields that harness/bin/nrpic-run reads.

The helpers of wave 1 wrote manifests by hand (tracks/A-emd-pbh/runs/<run_id>/manifest.json)
with their own spellings of the state ("done", "ok", "aborted", none) and without the
`outputs.dir` and `gate` fields of harness/templates/run_manifest.json. nrpic-run then stops
with KeyError 'outputs' (is_live) for every command that reads the owner's manifests.

This script adds the missing fields and maps the state; every field the helper wrote is kept,
and the changed ones are recorded under "lead_corrections" with the original value. It never
removes a field. Run from the worktree root:  python3 tracks/A-emd-pbh/analysis/normalize_manifests.py
"""

import datetime as dt
import glob
import json
import os

STATE = {"done": "completed", "ok": "completed", "completed": "completed",
         "aborted": "stopped", "failed": "failed", "stopped": "stopped"}

GATE_OF_HELPER = {"scope": "G0"}


def main():
    root = os.getcwd()
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    changed = 0
    for path in sorted(glob.glob(os.path.join(root, "tracks/A-emd-pbh/runs/*/manifest.json"))):
        with open(path) as f:
            m = json.load(f)
        rid = m["run_id"]
        corr = m.get("lead_corrections", [])
        before = json.dumps(m, sort_keys=True)

        st = m.get("status")
        ex = m.get("exit", m.get("exit_status", m.get("exit_code")))
        prev = [c for c in corr if c.get("field") == "status"]
        if prev and prev[0]["was"] is None:
            st = None                      # the lead set it before: re-derive from the exit field
        if st is None:
            new = "completed" if ex in (0, "0", "ok", None) else "failed"
        else:
            new = STATE.get(str(st).lower(), st)
        if prev:
            prev[0]["now"] = new
            m["status"] = new
        elif new != st:
            corr.append({"field": "status", "was": st, "now": new, "why": "harness state names"})
            m["status"] = new

        kind = m.get("kind")
        if kind == "production":
            corr.append({"field": "kind", "was": kind, "now": "scouting",
                         "why": "offline analysis before G0 passed; production needs a preregistered plan and the G0 tag"})
            m["kind"] = "scouting"

        if "gate" not in m:
            m["gate"] = GATE_OF_HELPER.get(m.get("helper"), "G1")
            corr.append({"field": "gate", "was": None, "now": m["gate"], "why": "field of the template"})

        out = m.get("outputs")
        od = m.get("output_directory") or m.get("output_dir") or f"/data/haiyangw/nrpic/scratch/A-emd-pbh/{rid}"
        rel = os.path.relpath(od, "/data/haiyangw/nrpic") if os.path.isabs(od) else od
        if not isinstance(out, dict) or "dir" not in out:
            if out is not None:
                m["outputs_as_written"] = out
            m["outputs"] = {"dir": rel}
            corr.append({"field": "outputs", "was": "missing or not a mapping", "now": {"dir": rel},
                         "why": "nrpic-run reads outputs.dir"})

        if "launcher" not in m:
            m["launcher"] = "local"
        if "track" not in m:
            m["track"] = "A-emd-pbh"

        if json.dumps(m, sort_keys=True) != before:
            for c in corr:
                c.setdefault("by", "A-emd-pbh lead")
                c.setdefault("at", stamp)
            m["lead_corrections"] = corr
            with open(path, "w") as f:
                json.dump(m, f, indent=1)
                f.write("\n")
            changed += 1
    print(f"normalized {changed} manifests")


if __name__ == "__main__":
    main()
