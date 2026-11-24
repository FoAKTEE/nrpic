#!/usr/bin/env python3
"""Where the five cut runs of the reproduction stopped, and whether the restart file each
continuation starts from is intact (package repro/continue, Track E, batch R2).

For every label of runs.json (written beside this script):
  * the chain's history: segments, outcome, last progress line of the newest segment log;
  * the last record of <base>.sf.con.hst (time, cycle) against tlim (from the parameter
    text stored in the restart file itself, i.e. with the command-line overrides);
  * the newest restart file by the chain's own rule (newest modification time, ties by
    the higher number): its header (AthenaK outputs/restart.cpp: parameter text up to
    <par_end>, nmb, root level, RegionSize, 2 x RegionIndcs, time, dt, ncycle, logical
    locations, costs, the z4c output time, data_size) and its size, which must equal
    header + nmb * data_size; data_size must be (nx1+2ng)(nx2+2ng)(nx3+2ng) * nz4c * 8;
    no holes (allocated blocks cover the file); the last MiB holds finite doubles;
  * its scalar-field sidecar <rst>.sf (scalar_field_io.cpp WriteRestart: "NRSFRST1",
    5 int64 extents, u0, int64 dump number, double next dump time, int64 ny, y0): size
    equal to the one its own counts give; dump number and next dump time;
  * with --sha: sha256 of both files against the original run's sha256sums.txt (written
    by `nrpic-run finish` of the original run).
Writes restart_check.json and fig_progress.{pdf,png} into the output directory.

    python3 check_restart.py --out DIR [--sha]
"""
import argparse
import hashlib
import json
import os
import re
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
SCRATCH = "/data/haiyangw/nrpic/scratch/E-stoch-inf"


def newest_restart(rundir):
    d = os.path.join(rundir, "rst")
    cands = [os.path.join(d, f) for f in os.listdir(d) if f.endswith(".rst")]
    cands.sort(key=lambda p: (os.path.getmtime(p), p), reverse=True)
    return cands[0] if cands else None


def parse_rst(path):
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        head = f.read(1 << 20)
        k = head.find(b"<par_end>")
        if k < 0:
            return {"ok": False, "why": "no <par_end> in the first MiB"}
        k = head.index(b"\n", k) + 1
        par = head[:k].decode("ascii", "replace")
        off = k
        nmb, root_level = struct.unpack_from("<ii", head, off); off += 8
        msize = struct.unpack_from("<9d", head, off); off += 72
        mind = struct.unpack_from("<19i", head, off); off += 76
        bind = struct.unpack_from("<19i", head, off); off += 76
        time, dt = struct.unpack_from("<dd", head, off); off += 16
        (ncycle,) = struct.unpack_from("<i", head, off); off += 4
        off += nmb * (16 + 4)               # logical locations, costs
        (z4c_last,) = struct.unpack_from("<d", head, off); off += 8
        # puncture trackers: none in these decks (nco = 0); checked by the size identity
        (data_size,) = struct.unpack_from("<Q", head, off); off += 8
        header = off
        f.seek(max(0, size - (1 << 20)))
        tail = np.frombuffer(f.read(1 << 20), dtype="<f8")
        ng, nx1, nx2, nx3 = bind[0], bind[1], bind[2], bind[3]
        n1, n2, n3 = nx1 + 2 * ng, nx2 + 2 * ng, nx3 + 2 * ng
        ncell = n1 * n2 * n3
        # central k-plane of the last MeshBlock for chi (z4c variable 0) and alpha (18):
        # the tail is ghost cells of the shift, zero in these decks, so it proves little
        samples = {}
        for name, v in (("chi", 0), ("alpha", 18)):
            o = header + (nmb - 1) * data_size + (v * ncell + (n3 // 2) * n1 * n2) * 8
            f.seek(o)
            pl = np.frombuffer(f.read(n1 * n2 * 8), dtype="<f8").reshape(n2, n1)
            act = pl[ng:ng + nx2, ng:ng + nx1]
            samples[name] = {"min": float(act.min()), "max": float(act.max()),
                             "finite": bool(np.all(np.isfinite(act)))}
    nz4c = data_size / (ncell * 8.0)
    expected = header + nmb * data_size
    st = os.stat(path)
    allocated = st.st_blocks * 512
    out = {
        "path": path, "bytes": size, "header_bytes": header, "nmb": nmb,
        "root_level": root_level, "mesh_nx": mind[1:4], "mb_nx": [nx1, nx2, nx3], "ng": ng,
        "time": time, "dt": dt, "ncycle": ncycle, "z4c_last_output_time": z4c_last,
        "data_size": data_size, "nz4c": nz4c, "expected_bytes": expected,
        "size_ok": size == expected, "nz4c_integer": abs(nz4c - round(nz4c)) < 1e-12,
        "allocated_bytes": allocated, "no_holes": allocated >= size - 4096,
        "tail_finite": bool(np.all(np.isfinite(tail))),
        "tail_nonzero_fraction": float(np.mean(tail != 0.0)),
        "mid_plane": samples,
        "mtime": st.st_mtime,
    }
    m = re.search(r"^\s*tlim\s*=\s*([-+0-9.eE]+)", par, re.M)
    out["tlim"] = float(m.group(1)) if m else None
    out["par_tail"] = par[-200:]
    out["ok"] = bool(out["size_ok"] and out["nz4c_integer"] and out["no_holes"]
                     and out["tail_finite"] and samples["chi"]["finite"]
                     and samples["chi"]["min"] > 0.0 and samples["alpha"]["finite"]
                     and samples["alpha"]["min"] > 0.0)
    return out


def parse_sf(path):
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        magic = f.read(8)
        dims = struct.unpack("<5q", f.read(40))
        n = int(np.prod(dims))
        f.seek(48 + 8 * n)
        dn, dnext, ny = struct.unpack("<qdq", f.read(24))
        f.seek(max(0, 48 + 8 * n - (1 << 20)))
        tail = np.frombuffer(f.read(min(1 << 20, 8 * n)), dtype="<f8")
    expected = 48 + 8 * n + 24 + 8 * ny
    st = os.stat(path)
    out = {"path": path, "bytes": size, "magic": magic.decode("ascii", "replace"),
           "dims": dims, "dump_number": dn, "dump_next_time": dnext, "ny": ny,
           "expected_bytes": expected, "size_ok": size == expected,
           "no_holes": st.st_blocks * 512 >= size - 4096,
           "tail_finite": bool(np.all(np.isfinite(tail)))}
    out["ok"] = bool(out["magic"] == "NRSFRST1" and out["size_ok"] and out["no_holes"]
                     and out["tail_finite"])
    return out


def sha256(path, bufsize=1 << 24):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(bufsize)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def recorded_sha(rundir, rel):
    p = os.path.join(rundir, "sha256sums.txt")
    if not os.path.exists(p):
        return None
    for line in open(p):
        parts = line.split()
        if len(parts) == 2 and parts[1] == rel:
            return parts[0]
    return None


def last_record(path):
    """last data line and per-segment cycles of a record file"""
    rows = []
    for line in open(path):
        if line.startswith("#") or not line.strip():
            continue
        s = line.split()
        rows.append((float(s[0]), int(s[1])))
    restarts = [i for i in range(1, len(rows)) if rows[i][1] <= rows[i - 1][1]]
    return {"lines": len(rows), "last_time": rows[-1][0], "last_cycle": rows[-1][1],
            "max_cycle": max(c for _, c in rows), "rewinds_at_line": restarts,
            "rewind_to_cycle": [rows[i][1] for i in restarts]}


def chain_summary(rundir):
    c = os.path.join(rundir, "chain")
    ev = open(os.path.join(c, "events.log")).read().splitlines()
    status = open(os.path.join(c, "STATUS")).read().strip()
    segs = sorted(f for f in os.listdir(c) if re.match(r"seg\d+\.job\d+\.a\d+\.log$", f))
    prog = {}
    for s in segs:
        last = None
        for line in open(os.path.join(c, s), errors="replace"):
            if line.startswith("elapsed=") or line.startswith("time="):
                last = line.strip()
        prog[s] = last
    kills = [e for e in ev if "SIGTERM" in e or "outside" in e or "wall-clock" in e]
    return {"status": status, "events_tail": ev[-3:], "segment_logs": prog, "stops": kills}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--sha", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    runs = json.load(open(os.path.join(HERE, "runs.json")))
    res = {}
    for lab, r in runs.items():
        rd = os.path.join(SCRATCH, r["orig"])
        rst = newest_restart(rd)
        e = {"orig": r["orig"], "chain": chain_summary(rd)}
        e["record"] = last_record(os.path.join(rd, r["base"] + ".sf.con.hst"))
        e["rst"] = parse_rst(rst)
        e["sf"] = parse_sf(rst + ".sf")
        e["expected_rst"] = r.get("rst")
        e["newest_is_expected"] = os.path.basename(rst) == r.get("rst")
        if a.sha:
            for key, p in (("rst", rst), ("sf", rst + ".sf")):
                rel = os.path.relpath(p, rd)
                e[key]["sha256"] = sha256(p)
                e[key]["sha256_recorded"] = recorded_sha(rd, rel)
                e[key]["sha256_match"] = e[key]["sha256"] == e[key]["sha256_recorded"]
        e["intact"] = bool(e["rst"]["ok"] and e["sf"]["ok"]
                           and (not a.sha or (e["rst"]["sha256_match"] and e["sf"]["sha256_match"])))
        tl = e["rst"]["tlim"]
        e["fraction_done_record"] = e["record"]["max_cycle"] * e["rst"]["dt"] / tl if tl else None
        e["remaining_cycles"] = int(np.ceil((tl - e["rst"]["time"]) / e["rst"]["dt"] - 1e-9)) if tl else None
        res[lab] = e
        print(f"{lab:7s} {r['orig']}: rst {os.path.basename(rst)} t={e['rst']['time']:.6f} "
              f"cycle={e['rst']['ncycle']} dt={e['rst']['dt']:.9e} tlim={tl} "
              f"remaining={e['remaining_cycles']} cycles; record to cycle "
              f"{e['record']['max_cycle']} (t={e['record']['last_time']:.4f}); "
              f"size_ok={e['rst']['size_ok']} sf_ok={e['sf']['ok']} dump#={e['sf']['dump_number']} "
              f"next={e['sf']['dump_next_time']:.6f} intact={e['intact']}"
              + (f" sha={e['rst']['sha256_match']},{e['sf']['sha256_match']}" if a.sha else ""))
    json.dump(res, open(os.path.join(a.out, "restart_check.json"), "w"), indent=1, default=str)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use_style()
    labs = list(res)
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 2.8))
    ax = fig.add_axes([0.11, 0.17, 0.86, 0.78])
    for i, lab in enumerate(labs):
        e = res[lab]
        tl = e["rst"]["tlim"]
        tmax = e["record"]["max_cycle"] * e["rst"]["dt"] / tl
        ax.barh(i, 1.0, color=fs.PAL["blue"], alpha=0.15, height=0.6)
        ax.barh(i, tmax, color=fs.PAL["blue"], alpha=0.6, height=0.6,
                label="reached (records)" if i == 0 else None)
        ax.plot([e["rst"]["time"] / tl] * 2, [i - 0.35, i + 0.35], color=fs.PAL["red"], lw=2.0,
                label="newest restart file" if i == 0 else None)
        ax.text(1.01, i, f"tlim {tl:.3f}", va="center", fontsize=8)
    ax.set_yticks(range(len(labs)))
    ax.set_yticklabels(labs)
    ax.minorticks_off()
    ax.set_xlim(0, 1.12)
    ax.set_xlabel("simulated time / tlim of the run")
    ax.legend(loc="lower right", ncol=2)
    fs.save(fig, os.path.join(a.out, "fig_progress"))
    print("wrote", os.path.join(a.out, "restart_check.json"))


if __name__ == "__main__":
    main()
