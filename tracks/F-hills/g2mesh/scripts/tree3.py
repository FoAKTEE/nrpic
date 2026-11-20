#!/usr/bin/env python3
"""MeshBlock tree of AthenaK's Z4c tracker refinement for several punctures (g2mesh).

The rules of tracks/F-hills/nr_first/scripts/tree_check.py (E11 of nr_first: exact against
the restart trees of one puncture), extended to every puncture of a `puncture_setup` input
and written level by level with sets of block indices:

  trackers  one per puncture component n, in the order of the components
            (athenak/src/pgen/nrpic/nrpic_puncture_setup.hpp lines 113-132):
            radius r_n = comp<c>_radius or puncture_radius * mass (the tracker gets 0.999 r_n,
            the refined region all of it), level L_n = comp<c>_level or
            (num_levels - 1) - round(log2(mass / lightest mass)), at least 0.
  start     (cycle 0) the refined regions <refined_region_punc<n>>: cube of half-width r_n
            about the puncture at level L_n. A block of level l < L_n is refined when it
            overlaps the open cube (mesh/build_tree.cpp lines 134-183: the level-L_n blocks
            whose right edge > xmin and left edge < xmax, rounded out to sibling pairs).
            The radius criterion acts only at regrids, so it is left out.
  regrid    (cycle > 0) z4c/z4c_amr.cpp: RefineTracker (lines 80-132): refine while
            level < L_n if the nearest point of the block is closer than 0.999 r_n to the
            tracker or the block contains it; RefineRadii (lines 329-372): refine while
            level < reflevel if a corner of the block is closer to the origin than the
            radius.
  2:1 rule  between all 26 neighbours (E11: what reproduces the restart trees).
Blocks are only added, never removed (the minimal tree; derefinement that lags behind a
moving puncture is not modelled).

The tree is held as R[l] = set of refined blocks of level l (l = 0 .. lmax-1). A block of
level l exists if l = 0 or its parent is in R[l-1]. Fixed point of:
  top-down   flag the existing unrefined blocks of each level, add them to R[l];
  bottom-up  for every block of R[l] its 26 neighbours of level l must exist:
             their parents (and its own parent) go into R[l-1].
Leaves of level l: |existing blocks of level l| - |R[l]|.

Command line (tests): tree3.py test <out.json>
  compares with tree_check.Model for the single-puncture input of nr_first at several
  tracker positions (both must agree level by level).
"""
import json
import math
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))

D27 = np.array([(a, b, c) for a in (-1, 0, 1) for b in (-1, 0, 1) for c in (-1, 0, 1)],
               dtype=np.int64)
C8 = np.array([(a, b, c) for a in (0, 1) for b in (0, 1) for c in (0, 1)], dtype=np.int64)


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


def punctures(inp, nlev):
    """[(mass, radius, level, (x, y, z))] of the puncture components, as puncture_setup."""
    prob = inp["problem"]
    ncomp = int(prob.get("ncomp", 1))
    comps = [c for c in range(ncomp) if prob.get(f"comp{c}_type", "") == "puncture"]
    mass = [float(prob[f"comp{c}_mass"]) for c in comps]
    mmin = min(mass)
    rfac = float(prob.get("puncture_radius", 2.0))
    lfine = int(prob.get("puncture_level", nlev - 1))
    out = []
    for c, m in zip(comps, mass):
        r = float(prob[f"comp{c}_radius"]) if f"comp{c}_radius" in prob else rfac * m
        lev = int(prob[f"comp{c}_level"]) if f"comp{c}_level" in prob else \
            lfine - int(round(math.log2(m / mmin)))   # std::lround: halves away from 0
        x = tuple(float(prob.get(f"comp{c}_x{a}", 0.0)) for a in (1, 2, 3))
        out.append((m, r, max(lev, 0), x))
    return out


class Tree:
    """Tree model of one mesh set-up. Overrides: nx (root cells per side), num_levels,
    block (MeshBlock cells per side), radii [(radius, reflevel)] of the wave zone."""

    def __init__(self, inp, nx=None, num_levels=None, block=None, radii=None):
        msh = inp["mesh"]
        self.xmin = float(msh["x1min"])
        self.L = float(msh["x1max"]) - self.xmin
        self.nx = int(nx or msh["nx1"])
        self.block = int(block or inp["meshblock"]["nx1"])
        if self.nx % self.block:
            raise ValueError(f"root {self.nx} is not a multiple of the block {self.block}")
        self.nroot = self.nx // self.block
        self.bs0 = self.L / self.nroot                  # root block width
        self.nlev = int(num_levels or inp["mesh_refinement"]["num_levels"])
        self.lmax = self.nlev - 1
        if radii is None:
            amr = inp.get("z4c_amr", {})
            radii = []
            for n in range(16):
                if f"radius_{n}_rad" not in amr:
                    break
                radii.append((float(amr[f"radius_{n}_rad"]),
                              int(amr.get(f"radius_{n}_reflevel", -1))))
        self.radii = radii
        self.punc = punctures(inp, self.nlev)
        self.h_root = self.L / self.nx

    def h(self, level):
        return self.h_root / 2 ** level

    # ---------------------------------------------------------------- criteria
    def flags(self, l, idx, pos, start):
        """idx (n, 3) blocks of level l; pos (np, 3) puncture positions -> bool (n,)."""
        s = self.bs0 / 2 ** l
        lo = self.xmin + idx * s
        hi = lo + s
        f = np.zeros(len(idx), dtype=bool)
        for (m, r, lev, _), p in zip(self.punc, pos):
            if l >= lev:
                continue
            p = np.asarray(p, dtype=float)
            if start:
                f |= np.all((hi > p - r) & (lo < p + r), axis=1)
            else:
                c = np.clip(p, lo, hi)
                d2 = np.sum((p - c) ** 2, axis=1)
                inside = np.all((p >= lo) & (p <= hi), axis=1)
                rt = 0.999 * r
                f |= (d2 < rt * rt) | inside
        if not start and self.radii:
            rmin2 = np.sum(np.minimum(lo * lo, hi * hi), axis=1)
            for R, lev in self.radii:
                if l < lev:
                    f |= rmin2 < R * R
        return f

    # ---------------------------------------------------------------- build
    def build(self, pos, start=False):
        """-> {level: leaves} of the tree for puncture positions pos (np, 3)."""
        nr = self.nroot
        lmax = self.lmax
        R = [set() for _ in range(lmax)]
        roots = {(i, j, k) for i in range(nr) for j in range(nr) for k in range(nr)}
        changed = True
        while changed:
            changed = False
            exist = roots
            for l in range(lmax):
                cand = exist - R[l]
                if cand:
                    arr = np.array(sorted(cand), dtype=np.int64)
                    fl = self.flags(l, arr, pos, start)
                    if fl.any():
                        R[l].update(map(tuple, arr[fl].tolist()))
                        changed = True
                exist = self._children(R[l])
            for l in range(lmax - 1, 0, -1):
                if not R[l]:
                    continue
                n = nr << l
                arr = np.array(list(R[l]), dtype=np.int64)
                nb = (arr[:, None, :] + D27[None, :, :]).reshape(-1, 3)
                ok = np.all((nb >= 0) & (nb < n), axis=1)
                par = np.unique(nb[ok] >> 1, axis=0)
                new = set(map(tuple, par.tolist())) - R[l - 1]
                if new:
                    R[l - 1] |= new
                    changed = True
        counts = {}
        nexist = nr ** 3
        for l in range(lmax):
            leaves = nexist - len(R[l])
            if leaves:
                counts[l] = leaves
            nexist = 8 * len(R[l])
        if nexist:
            counts[lmax] = nexist
        return counts

    @staticmethod
    def _children(Rl):
        if not Rl:
            return set()
        arr = np.array(list(Rl), dtype=np.int64)
        ch = (2 * arr[:, None, :] + C8[None, :, :]).reshape(-1, 3)
        return set(map(tuple, ch.tolist()))

    def cells(self, counts):
        return sum(counts.values()) * self.block ** 3


def total(counts):
    return int(sum(counts.values()))


# -------------------------------------------------------------------- test against E11
def test(out):
    sys.path.insert(0, os.path.join(WT, "tracks/F-hills/nr_first/scripts"))
    import tree_check as tc                                     # read only
    path = os.path.join(WT, "tracks/F-hills/nr_first/inputs/single_P025.athinput")
    inp = tc.read_athinput(path)
    rows, ok = [], True
    for x in (0.0, 0.79, 1.45, 1.96, 2.25, 3.1, 4.0, 7.3):
        for start in (True, False):
            ref = tc.model_tree(inp, [x, 0.0, 0.0], radii=not start)
            t = Tree(inp)
            # tree_check's start tree uses the tracker sphere; compare that variant
            # here (sphere rule with the radii removed), and the cube rule separately
            if start:
                t.radii = []
                mine = t.build(np.array([[x, 0.0, 0.0]]), start=False)
                cube = t.build(np.array([[x, 0.0, 0.0]]), start=True)
            else:
                mine = t.build(np.array([[x, 0.0, 0.0]]), start=False)
                cube = None
            same = {int(k): int(v) for k, v in ref.items()} == mine
            ok &= same
            rows.append(dict(x=x, rule="start(sphere)" if start else "regrid",
                             tree_check=ref, tree3=mine, equal=same, cube=cube))
            print(x, rows[-1]["rule"], total(ref), total(mine), "equal" if same else "DIFF",
                  "cube", None if cube is None else total(cube))
    json.dump(dict(input=path, rows=rows, all_equal=ok), open(out, "w"), indent=1,
              default=str)
    print("all equal:", ok)
    return ok


if __name__ == "__main__":
    if sys.argv[1] == "test":
        sys.exit(0 if test(sys.argv[2]) else 1)
