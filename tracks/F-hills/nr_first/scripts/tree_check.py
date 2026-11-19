#!/usr/bin/env python3
"""E11 of nr_first/JOURNAL.md: the MeshBlock tree of the single-puncture runs.

Two parts:
  model   the tree that AthenaK's refinement rules give for one puncture tracker at a given
          position: z4c_amr.cpp RefineTracker (a block whose nearest point is closer than the
          tracker radius, or that contains the tracker, is refined while its level is below
          the tracker's level; lines 80-137), RefineRadii (a block with a corner closer to the
          origin than radius_<n>_rad is refined while its level is below radius_<n>_reflevel;
          lines 329-374), and the 2:1 rule between all 26 neighbours (the t = 0 tree of S3,
          56 blocks per level, is what that rule gives). Blocks are only added (a tree built
          from the root, as at the start of a run), never removed.
  rst     the tree stored in an AthenaK restart file (outputs/restart.cpp lines 216-245:
          parameter text up to "<par_end>\\n", then nmb_total, root_level, RegionSize,
          2 RegionIndcs of 19 int, time, dt, ncycle, LogicalLocation[nmb_total] = 4 int32 each;
          mesh/mesh.hpp lines 26-65).
Usage:
  tree_check.py model <athinput> <x> [<y> <z>]        prints the model tree
  tree_check.py <out | -> <athinput> <rundir> [...]   reads <rundir>/rst/*.rst and the
          tracker file, builds the model at each restart's tracker position, writes
          tree_check.json and fig_tree_check.{png,pdf}
"""
import glob
import json
import math
import os
import re
import struct
import sys
from collections import Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(WT, "python"))

DIRS = [(a, b, c) for a in (-1, 0, 1) for b in (-1, 0, 1) for c in (-1, 0, 1)
        if (a, b, c) != (0, 0, 0)]


def read_athinput(path):
    """-> {block: {key: value string}} (comments removed)."""
    out, blk = {}, None
    with open(path) as f:
        for line in f:
            line = line.split("#")[0].strip()
            if not line:
                continue
            m = re.match(r"<(\w+)>", line)
            if m:
                blk = m.group(1)
                out.setdefault(blk, {})
            elif "=" in line and blk:
                k, v = line.split("=", 1)
                out[blk][k.strip()] = v.strip()
    return out


class Model:
    """Leaves of the block tree, keyed (level, i, j, k); level 0 = the root grid."""

    def __init__(self, inp):
        msh, mb = inp["mesh"], inp["meshblock"]
        self.xmin = float(msh["x1min"])
        self.L = float(msh["x1max"]) - self.xmin
        self.nroot = int(msh["nx1"]) // int(mb["nx1"])
        self.bs0 = self.L / self.nroot
        amr = inp.get("z4c_amr", {})
        self.radii = []
        for n in range(16):
            if f"radius_{n}_rad" in amr:
                self.radii.append((float(amr[f"radius_{n}_rad"]),
                                   int(amr.get(f"radius_{n}_reflevel", -1))))
        prob = inp["problem"]
        nlev = int(inp["mesh_refinement"]["num_levels"])
        self.trk_level = nlev - 1
        self.trk_radius = 0.999 * float(prob.get("puncture_radius", 2.0)) * \
            float(prob["comp0_mass"])
        self.leaves = {(0, i, j, k) for i in range(self.nroot) for j in range(self.nroot)
                       for k in range(self.nroot)}

    def box(self, key):
        l, i, j, k = key
        s = self.bs0 / 2 ** l
        lo = np.array([self.xmin + i * s, self.xmin + j * s, self.xmin + k * s])
        return lo, lo + s

    def flag(self, key, trk):
        l = key[0]
        lo, hi = self.box(key)
        c = np.clip(trk, lo, hi)
        d2 = float(np.sum((trk - c) ** 2))
        inside = bool(np.all(trk >= lo) and np.all(trk <= hi))
        if (d2 < self.trk_radius ** 2 or inside) and l < self.trk_level:
            return True
        corners = [(a, b, cc) for a in (lo[0], hi[0]) for b in (lo[1], hi[1])
                   for cc in (lo[2], hi[2])]
        rmin2 = min(a * a + b * b + cc * cc for a, b, cc in corners)
        for R, lev in self.radii:
            if rmin2 < R * R and l < lev:
                return True
        return False

    def refine(self, key):
        l, i, j, k = key
        self.leaves.discard(key)
        for a in (0, 1):
            for b in (0, 1):
                for c in (0, 1):
                    self.leaves.add((l + 1, 2 * i + a, 2 * j + b, 2 * k + c))

    def leaf_containing(self, l, i, j, k):
        for lp in range(l, -1, -1):
            sh = l - lp
            key = (lp, i >> sh, j >> sh, k >> sh)
            if key in self.leaves:
                return key
        return None

    def balance(self):
        changed = True
        while changed:
            changed = False
            for key in sorted(self.leaves, reverse=True):
                if key not in self.leaves:
                    continue
                l, i, j, k = key
                n = self.nroot * 2 ** l
                for a, b, c in DIRS:
                    ii, jj, kk = i + a, j + b, k + c
                    if not (0 <= ii < n and 0 <= jj < n and 0 <= kk < n):
                        continue
                    nb = self.leaf_containing(l, ii, jj, kk)
                    if nb is not None and nb[0] < l - 1:
                        self.refine(nb)
                        changed = True

    def build(self, trk):
        trk = np.asarray(trk, dtype=float)
        while True:
            fl = [key for key in self.leaves if self.flag(key, trk)]
            if not fl:
                break
            for key in fl:
                self.refine(key)
            self.balance()
        self.balance()
        return self

    def counts(self):
        return dict(sorted(Counter(k[0] for k in self.leaves).items()))


def model_tree(inp, trk, radii=True):
    """radii=False: the tree of the start, before the first regrid (AthenaK builds it from
    the refined regions of puncture_setup; the radius criteria act only at the regrids)."""
    m = Model(inp)
    if not radii:
        m.radii = []
    return m.build(trk).counts()


def read_rst_tree(path):
    with open(path, "rb") as f:
        head = f.read(1 << 20)
        p = head.find(b"<par_end>")
        if p < 0:
            raise ValueError(f"{path}: no <par_end>")
        off = head.index(b"\n", p) + 1
        f.seek(off)
        nmb, root = struct.unpack("<2i", f.read(8))
        f.read(9 * 8 + 2 * 19 * 4)                  # RegionSize (9 Real), 2 RegionIndcs (19 int)
        time, dt = struct.unpack("<2d", f.read(16))
        ncycle, = struct.unpack("<i", f.read(4))
        ll = np.frombuffer(f.read(16 * nmb), dtype="<i4").reshape(nmb, 4)
    lev = ll[:, 3] - root
    return dict(nmb=int(nmb), root_level=int(root), time=float(time), ncycle=int(ncycle),
                counts={int(k): int(v) for k, v in sorted(Counter(lev.tolist()).items())},
                lloc=ll)


def tracker_at(rundir, t):
    p = glob.glob(os.path.join(rundir, "*.co_0.txt"))
    if not p:
        return np.zeros(3)
    a = np.loadtxt(p[0], comments="#")
    k = int(np.argmin(np.abs(a[:, 1] - t)))
    return a[k, 2:5]


def main():
    if sys.argv[1] == "model":
        inp = read_athinput(sys.argv[2])
        trk = [float(v) for v in sys.argv[3:6]] + [0.0] * (3 - len(sys.argv[3:6]))
        c = model_tree(inp, trk)
        print(json.dumps(dict(tracker=trk, counts=c, total=sum(c.values()))))
        return
    out = sys.argv[1] if sys.argv[1] != "-" else os.environ["NRPIC_RUN_DIR"]
    inp = read_athinput(sys.argv[2])
    os.makedirs(out, exist_ok=True)
    res = {"input": sys.argv[2], "runs": {}}
    for rd in sys.argv[3:]:
        name = os.path.basename(rd.rstrip("/"))
        rows = []
        for p in sorted(glob.glob(os.path.join(rd, "rst", "*.rst"))):
            tr = read_rst_tree(p)
            trk = tracker_at(rd, tr["time"])
            mc = model_tree(inp, trk, radii=tr["ncycle"] > 0)
            rows.append(dict(file=os.path.basename(p), time=tr["time"], ncycle=tr["ncycle"],
                             nmb=tr["nmb"], counts=tr["counts"], tracker=trk.tolist(),
                             model_counts=mc, model_total=sum(mc.values())))
            print(name, rows[-1]["file"], "t", tr["time"], "nmb", tr["nmb"], tr["counts"],
                  "model", sum(mc.values()), mc)
        res["runs"][name] = rows
    # the model along the tracker path of the longest run: how the tree changes as it moves
    xs = np.linspace(0.0, 4.0, 33)
    path = []
    for x in xs:
        mc = model_tree(inp, [x, 0.0, 0.0])
        path.append(dict(x=float(x), total=sum(mc.values()), counts=mc))
    res["model_along_x"] = path
    with open(os.path.join(out, "tree_check.json"), "w") as f:
        json.dump(res, f, indent=1)

    from nrpic import figstyle as fs
    fs.apply() if hasattr(fs, "apply") else None
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.8))
    cols = [fs.PAL["blue"], fs.PAL["red"], fs.PAL["yellow"], fs.PAL["green"]]
    for n, (name, rows) in enumerate(res["runs"].items()):
        for r in rows:
            lv = sorted(set(r["counts"]) | set(r["model_counts"]))
            ax[0].plot(lv, [r["counts"].get(l, 0) for l in lv], "o-", color=cols[n % 4],
                       ms=3, lw=1, label=f"{name} rst t = {r['time']:.0f}: {r['nmb']}")
            ax[0].plot(lv, [r["model_counts"].get(l, 0) for l in lv], "x--",
                       color=cols[n % 4], ms=4, lw=0.8)
    ax[0].set_xlabel("refinement level (0 = root)")
    ax[0].set_ylabel("MeshBlocks")
    ax[0].set_title("circles: restart files; crosses: rule model", fontsize=8)
    ax[0].legend(fontsize=6)
    ax[1].plot([p["x"] for p in path], [p["total"] for p in path], "-", color="k", lw=1)
    ax[1].axhline(1600, color=fs.PAL["red"], lw=0.8, ls=":")
    ax[1].set_xlabel(r"tracker $x\,[m]$")
    ax[1].set_ylabel("MeshBlocks (model)")
    ax[1].set_title("dotted: max_nmb_per_rank of S3, S2", fontsize=8)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(out, f"fig_tree_check.{ext}"), dpi=200)
        print("figure:", os.path.join(out, f"fig_tree_check.{ext}"))


if __name__ == "__main__":
    main()
