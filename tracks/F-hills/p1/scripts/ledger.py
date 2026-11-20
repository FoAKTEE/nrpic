#!/usr/bin/env python3
"""Card ledger of P1, segment by segment: Slurm job, sacct state and elapsed time,
card-hours (1 card per job), t and cycle at the start and the end (segment logs), MeshBlocks
at the start and the end, MeshBlock-cycles per second, and how the segment ended.
Writes <out>/ledger.json and prints a Markdown table (for README.md).
Usage: ledger.py [--out=<dir>] [--rundir=<dir>]
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import p1lib  # noqa: E402


def main():
    out = p1lib.out_dir(sys.argv)
    rd = p1lib.rundir(sys.argv)
    segs = p1lib.segment_logs(rd)
    acct = p1lib.sacct([s["job"] for s in segs])
    rst = {r["file"]: r for r in p1lib.restart_headers(rd)}
    rows = []
    for s in segs:
        a = acct.get(s["job"], {})
        el = a.get("elapsed_s")
        # the segment starts at the time of the restart file it read (t = 0 for the first)
        rf = s.get("restart_file")
        r0 = rst.get(rf) or rst.get(f"{rf}.bad") if rf else None
        if rf is None:
            s["t_first"], s["cycle_first"] = 0.0, 0
        elif r0:
            s["t_first"], s["cycle_first"] = r0["time"], r0["ncycle"]
        rows.append(dict(seg=s["seg"], job=s["job"], attempt=s["attempt"],
                         state=a.get("state"), exit_slurm=a.get("exit"),
                         start=a.get("start"), end=a.get("end"), elapsed_s=el,
                         card_hours=round(el / 3600.0, 4) if el is not None else None,
                         t_start=s.get("t_first"), t_end=s.get("t_last"),
                         cycle_start=s.get("cycle_first"), cycle_end=s.get("cycle_last"),
                         advance_M=(s["t_last"] - s["t_first"])
                         if s.get("t_first") is not None and s.get("t_last") is not None else None,
                         nmb_start=s["nmb_start"], nmb_end=s["nmb_end"],
                         mbc_per_s=s.get("mbc_per_s"), cycles_per_s=s.get("cycles_per_s"),
                         restart_file=rf, athena_exit=s["exit"], termination=s["term"],
                         log=s["log"]))
    tot = sum(r["card_hours"] or 0.0 for r in rows)
    res = dict(run_id=p1lib.RUN_ID, rundir=rd, segments=rows, card_hours_total=round(tot, 4),
               note="card_hours = sacct ElapsedRaw / 3600 (one card per job); t_end of a "
                    "killed segment is its last elapsed= line, the restart point of the next "
                    "segment can be earlier")
    json.dump(res, open(os.path.join(out, "ledger.json"), "w"), indent=1)
    print("| seg | job | sacct | elapsed | card-h | t start-end [M] | advance | cycles | "
          "MeshBlocks start/end | MB-cycles/s | ended |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        el = r["elapsed_s"]
        if r["t_start"] is None or r["t_end"] is None:
            print(f"| {r['seg']} | {r['job']} | {r['state']} | - | {r['card_hours']} | "
                  f"(no step yet) | - | - | {r['nmb_start']}/- | - | running or no data |")
            continue
        els = f"{el // 3600}:{el % 3600 // 60:02d}:{el % 60:02d}" if el is not None else "-"
        mbc = f"{r['mbc_per_s']:.0f}" if r["mbc_per_s"] else "-"
        end = r["termination"] or f"exit {r['athena_exit']}"
        print(f"| {r['seg']} | {r['job']} | {r['state']} | {els} | {r['card_hours']} | "
              f"{r['t_start']:.2f}-{r['t_end']:.2f} | {r['advance_M']:.2f} | "
              f"{r['cycle_start']}-{r['cycle_end']} | {r['nmb_start']}/{r['nmb_end'] or '-'} | "
              f"{mbc} | {end} |")
    print(f"total card-hours: {tot:.3f}")


if __name__ == "__main__":
    main()
