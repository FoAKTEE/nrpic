"""A2-5's mesh clause from the chain's segment logs of A2 (F-20261124-210400-902c650):
MeshBlock counts printed at the start ("Total number of MeshBlocks") and end ("Current number of
MeshBlocks") of every segment, the card-memory peak each segment's wrapper wrote
("gpu_mem_peak_MiB"), exit codes, and lines with error words.

Run: python vlogs.py --out <dir>
"""
import argparse
import glob
import json
import os
import re

CHAIN = "/data/haiyangw/nrpic/scratch/F-hills/F-20261124-210400-902c650/chain"
ERR = re.compile(r"out of memory|bad_alloc|CUDA error|Segmentation|FATAL|ERROR", re.I)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    segs = []
    for p in sorted(glob.glob(os.path.join(CHAIN, "seg*.log"))):
        txt = open(p, errors="replace").read()
        tot = [int(x) for x in re.findall(r"Total number of MeshBlocks = (\d+)", txt)]
        cur = [int(x) for x in re.findall(r"Current number of MeshBlocks = (\d+)", txt)]
        peak = [int(x) for x in re.findall(r"gpu_mem_peak_MiB=(\d+)", txt)]
        mtot = [int(x) for x in re.findall(r"memory\.total \[MiB\].*\n.*?,\s*(\d+)\s*MiB", txt)]
        ex = re.findall(r"# exit=(\d+)", txt)
        times = re.findall(r"time=([0-9.eE+-]+)\s+cycle=", txt)
        errs = [ln.strip()[:160] for ln in txt.splitlines() if ERR.search(ln)]
        segs.append({"log": os.path.basename(p), "total_at_start": tot, "current_at_end": cur,
                     "gpu_mem_peak_MiB": peak, "exit": ex, "t_last_cycle_line": float(times[-1]) if times else None,
                     "error_lines": errs[:5]})
    allmb = [x for s in segs for x in s["total_at_start"] + s["current_at_end"]]
    peaks = [x for s in segs for x in s["gpu_mem_peak_MiB"]]
    res = {"n_segments": len(segs), "max_meshblocks": max(allmb) if allmb else None,
           "min_meshblocks": min(allmb) if allmb else None, "max_gpu_mem_peak_MiB": max(peaks) if peaks else None,
           "exits": sorted(set(e for s in segs for e in s["exit"])),
           "segments_with_error_lines": [s["log"] for s in segs if s["error_lines"]],
           "segments": segs}
    with open(os.path.join(a.out, "vlogs.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "segments"}))


if __name__ == "__main__":
    main()
