#!/usr/bin/env python3
"""T0b of collide/TESTS.md: replay of one collision step from the code's dump.

    python3 t0b.py DESIGN_JSON [--exe PATH] [--tag cpu] [--set block/par=value ...]
                   [--ref RUN_DIR]

Wave 2b: --set adds input parameters to every run (particles/coll_energy=particle: the
dump is of version 2 and holds the metric at every particle, checked here to be flat);
--ref names the run directory of an earlier T0b run whose output files (every file but
athena.log and wall.json) must be byte-identical (the option-absent rerun with the
executable of core/collisions-2 against the release run of wave 2).

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
    # the dump of coll_dump_cycle = c is the step taken with pmesh->ncycle = c; coll.hst
    # labels a record with the number of completed steps, so that step is record c + 1
    sel = h["ncycle"] == d["cycle"] + 1
    rec = int(np.flatnonzero(sel)[0]) if sel.any() else None
    mesh = dict(xmin=[10.0] * 3, xmax=[11.0] * 3, n=[nx] * 3)
    out = dict(run=rd, dump=dpath[0], cycle=d["cycle"], n=d["n"], f=d["f"], triad=d["triad"],
               seed=d["seed"], version=d["version"], tries={})
    if d["version"] == 2:
        flat = np.zeros((d["n"], 6))
        flat[:, [0, 3, 5]] = 1.0
        out.update(energy_mode=d["energy"], pmetric_flag=d["pmetric_flag"],
                   pmetric_flat_exact=bool(np.all(d["alpha_p"] == 1.0) and
                                           np.all(d["beta_p"] == 0.0) and
                                           np.array_equal(d["ginv_p"], flat)))
        if "n_noroot" in h:
            out.update(hst_n_noroot=float(h["n_noroot"].sum()),
                       hst_n_balance=float(h["n_balance"].sum()),
                       hst_max_dlam=float(h["max_dlam"].max()))
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


def compare_bytes(rd, rref):
    """Every output file of rd (but athena.log, wall.json) against the file of the same
    name in rref; also files present in only one of them."""
    import filecmp
    skip = {"athena.log", "wall.json"}
    a = sorted(p for p in os.listdir(rd) if p not in skip)
    b = sorted(p for p in os.listdir(rref) if p not in skip)
    differ = [p for p in a if p in b and not filecmp.cmp(os.path.join(rd, p),
                                                         os.path.join(rref, p), shallow=False)]
    only = sorted(set(a) ^ set(b))
    return dict(ref=rref, compared=len(set(a) & set(b)), differ=differ, only_one=only,
                identical=not differ and not only)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("design")
    ap.add_argument("--exe", default=bl.EXE_CPU)
    ap.add_argument("--tag", default="cpu")
    ap.add_argument("--deck", default=bl.DECK,
                    help="input deck (inputs/box_c2.athinput has coll_energy, which a command "
                         "line may only override, not add)")
    ap.add_argument("--set", action="append", default=[],
                    help="extra input parameter block/par=value (repeatable)")
    ap.add_argument("--ref", default=None, help="earlier T0b run directory (byte comparison)")
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
                f"job/rng_seed={seed}"] + list(a.set)
            jobs.append((rd, ov, dict(exe=a.exe, deck=a.deck)))
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
        if a.ref:
            o["bytes"] = compare_bytes(rd, os.path.join(a.ref, name))
            o["pass"] = bool(o["pass"] and o["bytes"]["identical"])
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
    summ = dict(runs=res, set=list(a.set), ref=a.ref, deck=a.deck,
                pass_all=bool(res and all(v.get("pass") for v in res.values())))
    bl.save_json(os.path.join(out, f"t0b_{a.tag}.json"), summ)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    sys.exit(main())
