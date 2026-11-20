#!/usr/bin/env python3
"""Shared readers of package p1 (F-hills, wave 3): the P1 run directory, its chain logs,
Slurm accounting and the baseline trajectories written by baselines_tracks.py.

Uses nr_first/scripts/nrread.py unchanged (trackers joined across segments, horizon summaries
with failed searches removed, history, r psi4). Bodies: comp0 = m1, comp1 = m2, comp2 = M.
"""
import glob
import json
import os
import re
import struct
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(WT, "tracks", "F-hills", "nr_first", "scripts"))
import nrread as nr  # noqa: E402

RUN_ID = "F-20261119-150017-b45ec5f"
RUNDIR = f"/data/haiyangw/nrpic/scratch/F-hills/{RUN_ID}"
INPUT = os.path.join(WT, "tracks", "F-hills", "nr_first", "inputs", "p1_q4.athinput")
BASELINES_JSON = os.path.join(WT, "tracks", "F-hills", "nr_first", "results", "baselines_p1.json")
MASSES = np.array([0.125, 0.125, 1.0])     # bare masses of the input, comp0, comp1, comp2
A0 = 5.0                                   # nominal binary separation of the design
HRMS_MAX = 1e-3                            # horizon rows used for masses (HANDOFF, Traps)
T_FIRST = {0: 0.5, 1: 0.5, 2: 4.0}         # members from 0.5 M, heavy hole from about 4 M


def out_dir(argv):
    """--out=<dir> or $NRPIC_RUN_DIR; never the P1 run directory."""
    out = os.environ.get("NRPIC_RUN_DIR")
    for a in argv[1:]:
        if a.startswith("--out="):
            out = a.split("=", 1)[1]
    if not out:
        raise SystemExit("no output directory (--out= or NRPIC_RUN_DIR)")
    if os.path.abspath(out).startswith(RUNDIR):
        raise SystemExit("refusing to write into the P1 run directory")
    os.makedirs(out, exist_ok=True)
    return out


def rundir(argv):
    for a in argv[1:]:
        if a.startswith("--rundir="):
            return a.split("=", 1)[1]
    return RUNDIR


def energy_unit(m=MASSES, a0=A0):
    m1, m2, M = m
    return m1 * m2 / a0 * (M / (m1 + m2)) ** (1 / 3)


# ----------------------------------------------------------------------------------------
# simulation outputs
# ----------------------------------------------------------------------------------------
def trackers(rd):
    """{n: dict iter, t, x, v}, segments joined (nrread.read_trackers)."""
    return nr.read_trackers(rd)


def tracker_common(rd):
    """(t, X (N, 3, 3), V (N, 3, 3)) on the cycles all three trackers have."""
    return nr.common_times(trackers(rd), keys=[0, 1, 2])


def horizons_good(rd):
    """{n: dict of columns} of the searches that found a horizon, with hrms < HRMS_MAX and
    t >= T_FIRST[n]; plus the raw found/missed counts."""
    out = {}
    for n, (h, missed) in nr.read_horizons(rd).items():
        ok = (h["hrms"] < HRMS_MAX) & (h["t"] >= T_FIRST.get(n, 0.0))
        out[n] = dict({k: v[ok] for k, v in h.items()}, found=int(len(h["t"])), missed=missed,
                      good=int(ok.sum()))
    return out


def history(rd):
    f = glob.glob(os.path.join(rd, "*.z4c.user.hst"))
    return nr.read_hst(f[0]) if f else None


def restart_headers(rd):
    """[(file, time, ncycle, nmb_total, bytes, mtime)] from the binary header of each restart
    file (athenak/src/outputs/restart.cpp lines 218-235: the input text up to <par_end>, then
    int nmb_total, int root_level, RegionSize, 2 x RegionIndcs, Real time, Real dt, int ncycle).
    time is found as the double before dt = 3.90625e-3 (P1's fixed step)."""
    rows = []
    dtb = struct.pack("<d", 3.90625e-3)
    for f in sorted(glob.glob(os.path.join(rd, "rst", "*.rst*"))):
        with open(f, "rb") as fh:
            b = fh.read(400000)
        i = b.find(b"<par_end>")
        if i < 0:
            continue
        j = b.find(b"\n", i) + 1
        nmb = struct.unpack("<i", b[j:j + 4])[0]
        k = b.find(dtb, j)
        if k < 0:
            continue
        t = struct.unpack("<d", b[k - 8:k])[0]
        nc = struct.unpack("<i", b[k + 8:k + 12])[0]
        st = os.stat(f)
        rows.append(dict(file=os.path.basename(f), time=t, ncycle=nc, nmb=nmb,
                         bytes=st.st_size, mtime=st.st_mtime))
    return rows


_SEGRE = re.compile(r"seg(\d+)\.job(\d+)\.a(\d+)\.log$")


def segment_logs(rd):
    """Per chain segment log: job, attempt, MeshBlocks at the start and the end, first and
    last cycle and time, MeshBlock-cycles, cpu time, exit status, termination message, and the
    per-100-cycle wall times (elapsed=... lines)."""
    segs = []
    for f in sorted(glob.glob(os.path.join(rd, "chain", "seg*.log"))):
        m = _SEGRE.search(f)
        if not m:
            continue
        d = dict(seg=int(m.group(1)), job=int(m.group(2)), attempt=int(m.group(3)),
                 log=os.path.relpath(f, rd), nmb_start=None, nmb_end=None, mb_cycles=None,
                 cpu_time=None, exit=None, term=None, rows=[])
        for line in open(f, errors="replace"):
            s = line.strip()
            if s.startswith("Total number of MeshBlocks") and d["nmb_start"] is None:
                d["nmb_start"] = int(s.split("=")[1])
            elif s.startswith("Current number of MeshBlocks"):
                d["nmb_end"] = int(s.split("=")[1])
            elif s.startswith("MeshBlock-cycles"):
                d["mb_cycles"] = int(s.split("=")[1])
            elif s.startswith("cpu time used"):
                d["cpu_time"] = float(s.split("=")[1])
            elif s.startswith("Terminating on"):
                d["term"] = s
            elif s.startswith("# exit="):
                d["exit"] = int(s.split()[1].split("=")[1])
                d["end"] = s.split("end=")[1].split()[0]
            elif s.startswith("# host="):
                d["start"] = s.split("start=")[1].split()[0]
            elif s.startswith("elapsed="):
                kv = dict(t.split("=") for t in s.split())
                d["rows"].append((float(kv["elapsed"]), int(kv["cycle"]), float(kv["time"])))
            elif s.startswith("time=") and "cycle=" in s:
                kv = dict(t.split("=") for t in s.split())
                d["final"] = (int(kv["cycle"]), float(kv["time"]))
        r = np.array(d["rows"]) if d["rows"] else np.zeros((0, 3))
        d["rows"] = r.tolist()
        if len(r):
            d["cycle_first"], d["t_first"] = int(r[0, 1]), float(r[0, 2])
            d["cycle_last"], d["t_last"] = int(r[-1, 1]), float(r[-1, 2])
            if "final" in d:
                d["cycle_last"], d["t_last"] = d["final"]
            if len(r) > 2:
                # cycles per wall second from the elapsed= lines (setup excluded)
                d["cycles_per_s"] = float((r[-1, 1] - r[0, 1]) / (r[-1, 0] - r[0, 0]))
        if d["mb_cycles"] and d["cpu_time"]:
            d["mbc_per_s"] = d["mb_cycles"] / d["cpu_time"]
        segs.append(d)
    return segs


def sacct(jobs):
    """{job: dict state, exit, start, end, elapsed_s} from sacct (allocation lines only)."""
    if not jobs:
        return {}
    cmd = ["sacct", "-X", "-n", "-P", "-j", ",".join(str(j) for j in jobs),
           "--format=JobID,State,ExitCode,Start,End,ElapsedRaw"]
    try:
        txt = subprocess.run(cmd, capture_output=True, text=True, timeout=60).stdout
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)}
    out = {}
    for line in txt.splitlines():
        p = line.split("|")
        if len(p) < 6 or not p[0].isdigit():
            continue
        out[int(p[0])] = dict(state=p[1], exit=p[2], start=p[3], end=p[4],
                              elapsed_s=int(p[5]) if p[5].isdigit() else None)
    return out


# ----------------------------------------------------------------------------------------
# baselines
# ----------------------------------------------------------------------------------------
def baselines(path):
    """Arrays written by baselines_tracks.py (npz)."""
    z = np.load(path)
    return {k: z[k] for k in z.files}


def baselines_json():
    return json.load(open(BASELINES_JSON))


def baseline_path(argv, out):
    for a in argv[1:]:
        if a.startswith("--baselines-npz="):
            return a.split("=", 1)[1]
    return os.path.join(out, "baseline_tracks.npz")
