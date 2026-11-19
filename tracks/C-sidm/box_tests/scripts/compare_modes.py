#!/usr/bin/env python3
"""The collision step of coll_energy = particle against that of the operator of core-v0.3
in the flat box, from the dumps of two T0b runs (same particle files, seeds, cases).

    python3 compare_modes.py RUN_DIR_A RUN_DIR_B [--tag c2]

For each case T0b_<var>_s<seed> present in both: the "before" records identical
(positions, momenta, cells, n_sub), the same particles updated, and the "after" momenta
of the collided particles: share bit-identical, largest difference over max(1, |u|).
Writes compare_modes_<tag>.json and compare_modes_<tag>.png into $NRPIC_RUN_DIR.
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

import boxlib as bl

sys.path.insert(0, os.path.join(bl.REPO, "python"))
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402


def dump(rd):
    p = glob.glob(os.path.join(rd, "box.coll_dump.*.bin"))
    assert len(p) == 1, p
    return bl.read_dump(p[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--tag", default="c2")
    a = ap.parse_args()
    out = bl.outdir()
    res = {}
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH / 2, 3.0))
    ax = fig.add_axes([0.17, 0.16, 0.78, 0.78])
    names = sorted(os.path.basename(p) for p in glob.glob(os.path.join(a.a, "T0b_*")))
    for k, name in enumerate(names):
        ra, rb = os.path.join(a.a, name), os.path.join(a.b, name)
        if not os.path.isdir(rb):
            continue
        da, db = dump(ra), dump(rb)
        before = bool(np.array_equal(da["x"], db["x"]) and np.array_equal(da["u0"], db["u0"])
                      and np.array_equal(da["I"], db["I"]) and np.array_equal(da["nsub"], db["nsub"]))
        upd = bool(np.array_equal(da["nupd"], db["nupd"]))
        coll = da["nupd"] > 0
        scale = np.maximum(1.0, np.sqrt(np.sum(da["u1"] ** 2, 1)))
        du = np.max(np.abs(da["u1"] - db["u1"]), 1) / scale
        res[name] = dict(a=ra, b=rb, version_a=da["version"], version_b=db["version"],
                         before_identical=before, updates_identical=upd,
                         collided=int(coll.sum()),
                         collided_bit_identical=int(np.sum(du[coll] == 0)),
                         max_du_collided=float(du[coll].max()) if coll.any() else 0.0,
                         untouched_identical=bool(np.array_equal(da["u1"][~coll], db["u1"][~coll])))
        x = np.sort(np.maximum(du[coll], 1e-18))
        ax.step(x, np.arange(1, x.size + 1) / x.size, color=fs.SERIES[k % len(fs.SERIES)],
                label=f"{name[4:]} ({x.size})")
    ax.set_xscale("log")
    ax.set_xlim(1e-18, 1e-13)
    ax.set_xlabel(r"$|u'_{\rm particle}-u'_{\rm absent}|/\max(1,|u|)$ (collided)")
    ax.set_ylabel("cumulative fraction")
    ax.legend(loc="upper left", fontsize=6)
    fs.save(fig, os.path.join(out, f"compare_modes_{a.tag}"))
    plt.close(fig)
    summ = dict(runs=res, all_before_identical=all(v["before_identical"] for v in res.values()),
                all_updates_identical=all(v["updates_identical"] for v in res.values()),
                max_du=max(v["max_du_collided"] for v in res.values()))
    bl.save_json(os.path.join(out, f"compare_modes_{a.tag}.json"), summ)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    sys.exit(main())
