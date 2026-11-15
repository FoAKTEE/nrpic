#!/usr/bin/env python3
"""T0b of collide/TESTS.md: replay of one collision step from the code's dump.

    python3 t0b.py [--exe PATH] [--tag cpu]

The T2 box at theta = 0.1 (design run: sigma = 0.2025, dt = 0.03185), 1e4 particles,
4^3 cells, dump of cycle 20, triad = cholesky (lead's choice; in the flat box the triad
is the identity). Variants, each with seeds (1, 1) and (2, 2):
  plain  sigma of the design (n_sub = 1 expected),
  sub    sigma x 25 (sub-cycling active),
  f2     sigma x 25 on an 8^3 mesh with coll_cell_factor = 2 (4^3 collision cells).
Pass (TESTS.md): identical set of tested pairs and of accepted pairs, every
post-collision u within 1e-13 of max(1, |u|) of the "after" dump, untouched particles
bit-identical. Checked here through: cell index and n_sub of every particle; number of
momentum updates of every particle; n_tested, n_coll (and sum_P to 1e-12 relative) of the
record of that cycle in coll.hst; momenta. The random-number key uses the step number;
the replay tries the dump's cycle and its neighbours and reports which one reproduces
the code.
"""
import argparse
import json
import os
import sys

import numpy as np

import boxlib as bl
import replay as rp

sys.path.insert(0, os.path.join(bl.REPO, "python"))
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402


def check(rd, nx, f):
    dpath = [p for p in os.listdir(rd) if p.startswith("box.coll_dump.")]
    assert len(dpath) == 1, dpath
    d = bl.read_dump(os.path.join(rd, dpath[0]))
    h = bl.coll_history(rd)
    rec = int(np.flatnonzero(h["ncycle"] == d["cycle"])[0]) if (h["ncycle"] == d["cycle"]).any() else None
    mesh = dict(xmin=[10.0] * 3, xmax=[11.0] * 3, n=[nx] * 3)
    out = dict(run=rd, dump=dpath[0], cycle=d["cycle"], n=d["n"], f=d["f"], triad=d["triad"],
               seed=d["seed"], tries={})
    best = None
    for kc in (d["cycle"], d["cycle"] - 1, d["cycle"] + 1):
        r = rp.replay(d, mesh, kc)
        coll = r["nupd"] > 0
        scale = np.maximum(1.0, np.sqrt(np.sum(d["u1"] ** 2, 1)))
        du = np.max(np.abs(r["u"] - d["u1"]), 1) / scale
        t = dict(key_cycle=kc,
                 cells_identical=bool(np.array_equal(r["idx"][:, 0] // f, d["I"]) and
                                      np.array_equal(r["idx"][:, 1] // f, d["J"]) and
                                      np.array_equal(r["idx"][:, 2] // f, d["K"])),
                 nsub_identical=bool(np.array_equal(r["nsub"], d["nsub"])),
                 nupd_identical=bool(np.array_equal(r["nupd"], d["nupd"])),
                 n_tested=r["tot"]["n_tested"], n_coll=r["tot"]["n_coll"],
                 sum_P=r["tot"]["sum_P"], sum_W=r["tot"]["sum_W"], max_P=r["tot"]["max_P"],
                 n_trunc=r["tot"]["n_trunc"], cells_odd_substeps=r["tot"]["cells_odd"],
                 n_collided=int(coll.sum()),
                 max_du_collided=float(du[coll].max()) if coll.any() else 0.0,
                 untouched_bit_identical=bool(np.array_equal(r["u"][~coll], d["u1"][~coll])),
                 code_untouched_unchanged=bool(np.array_equal(d["u0"][d["nupd"] == 0],
                                                              d["u1"][d["nupd"] == 0])))
        if rec is not None:
            t.update(hst_n_tested=float(h["n_tested"][rec]), hst_n_coll=float(h["n_coll"][rec]),
                     hst_sum_P=float(h["sum_P"][rec]), hst_sum_W=float(h["sum_W"][rec]),
                     hst_max_P=float(h["max_P"][rec]),
                     sumP_rel=float(abs(r["tot"]["sum_P"] / h["sum_P"][rec] - 1)),
                     sumW_rel=float(abs(r["tot"]["sum_W"] / h["sum_W"][rec] - 1)))
        t["pass"] = bool(t["cells_identical"] and t["nsub_identical"] and t["nupd_identical"]
                         and t["max_du_collided"] < 1e-13 and t["untouched_bit_identical"]
                         and rec is not None and t["n_tested"] == t["hst_n_tested"]
                         and t["n_coll"] == t["hst_n_coll"] and t["sumP_rel"] < 1e-12)
        out["tries"][str(kc)] = t
        if best is None or t["pass"]:
            best = (t, du, coll, d, r)
            if t["pass"]:
                break
    out["pass"] = any(t["pass"] for t in out["tries"].values())
    return out, best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("design")
    ap.add_argument("--exe", default=bl.EXE_CPU)
    ap.add_argument("--tag", default="cpu")
    a = ap.parse_args()
    des = json.load(open(a.design))["T2"]["0.1"]
    out = bl.outdir()
    jobs, runs = [], []
    for var, fac, nx, f in (("plain", 1, 4, 1), ("sub", 25, 4, 1), ("f2", 25, 8, 2)):
        for seed in (1, 2):
            name = f"T0b_{var}_s{seed}"
            rd = os.path.join(out, name)
            sig = des["sigma"] * fac
            bl.make_box(rd, "mj", n=10000, theta=0.1, sigma=sig, seed=seed)
            ov = bl.mesh_overrides(nx) + [
                f"particles/dt={des['dt']!r}", "time/nlim=25", f"particles/coll_sigma={sig!r}",
                "particles/coll_dump_cycle=20", f"particles/coll_cell_factor={f}",
                f"job/rng_seed={seed}"]
            jobs.append((rd, ov, dict(exe=a.exe)))
            runs.append((name, rd, nx, f))
    rr = bl.run_many(jobs, 6)
    res = {}
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.2))
    ax1 = fig.add_axes([0.08, 0.15, 0.40, 0.78])
    ax2 = fig.add_axes([0.58, 0.15, 0.40, 0.78])
    cols = dict(plain=fs.PAL["blue"], sub=fs.PAL["red"], f2=fs.PAL["yellow"])
    for (name, rd, nx, f), r0 in zip(runs, rr):
        if r0["rc"] != 0:
            res[name] = dict(rc=r0["rc"], failed=True)
            continue
        o, best = check(rd, nx, f)
        res[name] = o
        t, du, coll, d, r = best
        var = name.split("_")[1]
        seed = int(name[-1])
        if coll.any():
            x = np.sort(np.maximum(du[coll], 1e-18))
            ax1.step(x, np.arange(1, x.size + 1) / x.size, color=cols[var],
                     ls="-" if seed == 1 else "--", label=f"{var} s{seed} ({x.size})")
        ax2.plot(d["nsub"], r["nsub"], "o", ms=3, color=cols[var], mfc="none" if seed == 2 else cols[var])
    ax1.set_xscale("log")
    ax1.axvline(1e-13, **fs.GUIDE)
    ax1.set_xlabel(r"$|u_{\rm replay}-u_{\rm code}|/\max(1,|u|)$ (collided)")
    ax1.set_ylabel("cumulative fraction")
    ax1.legend(loc="upper left", fontsize=7)
    ax1.set_xlim(1e-18, 1e-12)
    ax2.plot([0, 40], [0, 40], **fs.GUIDE)
    ax2.set_xlabel(r"$n_{\rm sub}$ of the code (dump)")
    ax2.set_ylabel(r"$n_{\rm sub}$ of the replay")
    fs.save(fig, os.path.join(out, f"t0b_replay_{a.tag}"))
    plt.close(fig)
    summ = dict(runs=res, pass_all=bool(res and all(v.get("pass") for v in res.values())))
    bl.save_json(os.path.join(out, f"t0b_{a.tag}.json"), summ)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    sys.exit(main())
