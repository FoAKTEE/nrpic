#!/usr/bin/env python3
"""Inventory of the pre-program run directories that carry ladder rows 2, 3 and 4.

The directories under /data/haiyangw/nrpic/runs/ were made before the program's run
registry existed (executables older than core-v0.1, 2026-11-13). This script names each
one, the ladder row it carries, and records its provenance as it stands today: the
input file, the timestamped copy of the executable that ran, logs, histories, horizon
summaries and particle files with their sha256; the bulk outputs (particle snapshots,
restart files, mesh dumps) by count and size only. It reads, never writes, the run
directories.

Usage: inventory.py OUTDIR
Writes OUTDIR/inventory.json, OUTDIR/INVENTORY.md, OUTDIR/fig_inventory.{png,pdf}.
"""
import hashlib
import json
import os
import re
import sys
from pathlib import Path

RUNS = Path("/data/haiyangw/nrpic/runs")

# directory, ladder row, what the ladder reads from it (verify/LADDER.md)
DIRS = [
    ("os/nocap_sc", "row 2", "Oppenheimer-Snyder reference to 60 M: first horizon, M_AH/M, removal"),
    ("os/nocap_v4", "row 2", "Oppenheimer-Snyder with the published lattice mass rule"),
    ("prolate/e09_v8", "row 3", "prolate collapse at M/16: horizon time and mass, Kretschmann"),
    ("st/yc0900_v4", "row 4", "y_c = 0.900 kicked: central lapse range, particles kept"),
    ("st/yc0819_v4", "row 4", "y_c = 0.819 kicked: central lapse range, particles kept"),
    ("st/yc0605_v5", "row 4", "y_c = 0.605 kicked: first horizon, M_AH/M"),
    ("st/yc0500_v5", "row 4", "y_c = 0.500 kicked: first horizon, M_AH/M"),
    ("st/yc0283_v5", "row 4", "y_c = 0.283 kicked: central lapse at the end"),
    ("st/migration_yc0500_v4", "row 4", "y_c = 0.5 unperturbed: late mean central lapse"),
    ("st/yc0756_unpert", "row 4", "y_c = 0.756 unperturbed to 800 M: lapse range"),
]

BULK = [re.compile(p) for p in (r"\.part\.\d+\.bin$", r"\.rst$", r"\.bin$", r"\.vtk$",
                                r"\.athdf$", r"\.xdmf$")]

CLASSES = [
    ("input", lambda n: n.endswith(".athinput")),
    ("executable", lambda n: n.endswith(".exe") or n == "athena"),
    ("log", lambda n: n.endswith(".log") or (n.startswith("slurm-") and n.endswith(".out"))),
    ("nrpic history", lambda n: n.endswith(".nrpic.hst")),
    ("z4c history", lambda n: n.endswith(".z4c.user.hst")),
    ("horizon summary", lambda n: "horizon_summary" in n),
    ("particle file", lambda n: n.endswith(".nrp")),
    ("table", lambda n: n.endswith(".tab")),
]


def sha256(path, bufsize=1 << 22):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(bufsize)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def classify(name):
    for cls, test in CLASSES:
        if test(name):
            return cls
    return None


def inventory(rel):
    d = RUNS / rel
    out = {"dir": str(d), "exists": d.is_dir(), "hashed": [], "bulk": {"count": 0, "bytes": 0},
           "classes": {c: [] for c, _ in CLASSES}}
    if not d.is_dir():
        return out
    for root, _, files in os.walk(d):
        for n in sorted(files):
            p = Path(root) / n
            r = str(p.relative_to(d))
            try:
                st = p.stat()
            except OSError:
                continue
            if any(b.search(n) for b in BULK) or "/rst/" in "/" + r:
                out["bulk"]["count"] += 1
                out["bulk"]["bytes"] += st.st_size
                continue
            rec = {"path": r, "bytes": st.st_size, "mtime": int(st.st_mtime), "sha256": sha256(p)}
            out["hashed"].append(rec)
            c = classify(n)
            if c:
                out["classes"][c].append(r)
    return out


def main():
    outdir = Path(sys.argv[1])
    outdir.mkdir(parents=True, exist_ok=True)
    res = []
    for rel, row, what in DIRS:
        inv = inventory(rel)
        inv.update({"rel": rel, "row": row, "what": what})
        res.append(inv)
        print(f"{rel}: {len(inv['hashed'])} files hashed, bulk {inv['bulk']['count']} files "
              f"{inv['bulk']['bytes'] / 1e9:.2f} GB", flush=True)
    (outdir / "inventory.json").write_text(json.dumps(res, indent=1))

    cls_names = [c for c, _ in CLASSES]
    lines = ["# Inventory of the pre-program run directories (ladder rows 2 to 4)", "",
             "Written by `tracks/core/verify/preprogram/inventory.py`; sha256 of every file except",
             "the bulk outputs (snapshots, restart files, mesh dumps: count and size only).", "",
             "| Directory | Row | " + " | ".join(cls_names) + " | bulk files (GB) |",
             "|---|---|" + "---|" * len(cls_names) + "---|"]
    for inv in res:
        cells = [str(len(inv["classes"][c])) for c in cls_names]
        lines.append(f"| `runs/{inv['rel']}` | {inv['row']} | " + " | ".join(cells)
                     + f" | {inv['bulk']['count']} ({inv['bulk']['bytes'] / 1e9:.1f}) |")
    lines += ["", "Executables and inputs (sha256, first 16 hex digits):", ""]
    for inv in res:
        recs = {h["path"]: h for h in inv["hashed"]}
        for c in ("input", "executable"):
            for r in inv["classes"][c]:
                lines.append(f"- `runs/{inv['rel']}/{r}`: {recs[r]['sha256'][:16]}, "
                             f"{recs[r]['bytes']} bytes")
    (outdir / "INVENTORY.md").write_text("\n".join(lines) + "\n")

    # figure: presence matrix (number of files of each class per directory)
    sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "python"))
    from nrpic import figstyle
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    figstyle.use_style()
    mat = np.array([[len(inv["classes"][c]) for c in cls_names] for inv in res], float)
    fig = plt.figure(figsize=(8.0, 4.0))
    ax = fig.add_axes([0.30, 0.30, 0.62, 0.62])
    cmap = figstyle.truncate_cmap("magma", 0.2, 1.0)
    ax.imshow(np.minimum(mat, 3), cmap=cmap, vmin=0, vmax=3, aspect="auto")
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            v = int(mat[i, j])
            ax.text(j, i, str(v), ha="center", va="center", fontsize=8,
                    color="white" if v < 2 else "black")
    ax.set_xticks(range(len(cls_names)))
    ax.set_xticklabels(cls_names, rotation=40, ha="right")
    ax.set_yticks(range(len(res)))
    ax.set_yticklabels([f"{inv['rel']} ({inv['row']})" for inv in res])
    ax.minorticks_off()
    ax.set_title("files per class in each pre-program run directory (0 = missing)", fontsize=9)
    figstyle.save(fig, str(outdir / "fig_inventory"))


if __name__ == "__main__":
    main()
