#!/usr/bin/env python3
"""Review test R11 (journal entry 12): <scalar_field> noise_background_eq = evolved, the
lockstep background of level 0 in the variables and with the equations of the mesh.

    level0_evolved.py --exe ATHENA --out DIR [--workers 5]

Slow-roll input at 32^3 (nmax2 = 64), t = 0 .. 3.2, dumps every 0.4 with the per-mode
record:
  (a) homogeneous slice, kicks off: h1 level 1 on the mesh, h0e level 0 on the mesh with
      the evolved background, h0c the same with the constraint form (as before)
  (b) perturbed slice, kicks on, amplitude 1 and 0.1 (noise_mode_scale): s1, s0e and
      s1_b, s0e_b; and s0c at amplitude 1
  (c) restart: r0e, 20 cycles with a restart file at cycle 10, and r0er restarted from it
Writes DIR/summary.json and DIR/fig_level0_evolved.png; exit status 1 if a run fails or
the restart differs."""
import argparse
import concurrent.futures as cf
import filecmp
import glob
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cpu_tests as ct                      # noqa: E402
import nl2                                  # noqa: E402
import numpy as np                          # noqa: E402
from nrpic import scalar_field as sf        # noqa: E402

EV = {"scalar_field/noise_background_eq": "evolved"}
AMP = {"scalar_field/noise_mode_scale": 0.1}


def cases():
    c = {
        "h1": {**ct.HOM, **ct.OFF, **ct.L1M},
        "h0e": {**ct.HOM, **ct.OFF, **ct.L0M, **EV},
        "h0c": {**ct.HOM, **ct.OFF, **ct.L0M},
        "s1": {**ct.L1M}, "s0e": {**ct.L0M, **EV}, "s0c": {**ct.L0M},
        "s1_b": {**ct.L1M, **AMP}, "s0e_b": {**ct.L0M, **EV, **AMP},
        "r0e": {**ct.L0M, **EV, "time/nlim": 20, "scalar_field/dump_dt": -1.0,
                "scalar_field/dump_dcycle": 10, "output9/file_type": "rst",
                "output9/dcycle": 10},
    }
    return {k: {**ct.BASE, **v} for k, v in c.items()}


def pair(out, a, b):
    rows = []
    for k in range(min(ct.ndumps(os.path.join(out, a)), ct.ndumps(os.path.join(out, b)))):
        ha, _, n2, ra, da = ct.modes_at(os.path.join(out, a), k)
        _, _, _, rb, db = ct.modes_at(os.path.join(out, b), k)
        d = ct.rel(ra, rb)
        rows.append(dict(time=ha["time"], rms=float(np.sqrt(np.mean(d*d))),
                         max=float(d.max()),
                         rms_dR=float(np.sqrt(np.mean(ct.rel(da, db)**2)))))
    return rows


def background(out, lab):
    """lockstep chi_b, K_b of the .modes headers against the box means of the dumps."""
    rows = []
    for f in sorted(glob.glob(os.path.join(out, lab, "sr.sf.?????.modes"))):
        head, _ = sf.read_modes(f)
        d = sf.read_dump(f.replace(".modes", ".dump"))["fields"]
        rows.append(dict(time=head["time"],
                         chi=float(head["chi_b"]/d["chi"].mean() - 1.0),
                         K=float(head["K_b"]/d["K"].mean() - 1.0),
                         Pi=float(head["Pi_b"]/d["Pi"].mean() - 1.0)))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=5)
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    rcs, walls = {}, {}

    def one(name, par):
        inp = nl2.write_input(ct.INP, os.path.join(out, name + ".athinput"), par)
        t0 = time.time()
        return name, nl2.run(a.exe, os.path.join(out, name), inp), round(time.time() - t0, 2)
    with cf.ThreadPoolExecutor(max_workers=a.workers) as pool:
        for f in [pool.submit(one, k, v) for k, v in cases().items()]:
            k, rc, w = f.result()
            rcs[k], walls[k] = rc, w
    rst = sorted(glob.glob(os.path.join(out, "r0e", "rst", "*.00001.rst")))
    rcs["r0er"] = nl2.run(a.exe, os.path.join(out, "r0er"), rst[0], ["time/nlim=20"]) \
        if rst else -1
    same, differ = [], []
    for f in sorted(os.listdir(os.path.join(out, "r0er"))):
        if f.startswith("sr.sf.00002"):
            x, y = os.path.join(out, "r0e", f), os.path.join(out, "r0er", f)
            (same if os.path.exists(x) and filecmp.cmp(x, y, shallow=False)
             else differ).append(f)
    res = dict(exe=os.path.abspath(a.exe), exit=rcs, wall_s=walls,
               restart=dict(identical=same, differ=differ),
               hom=dict(evolved_vs_l1=pair(out, "h0e", "h1"),
                        constraint_vs_l1=pair(out, "h0c", "h1"),
                        background=background(out, "h0e")),
               pert=dict(evolved_vs_l1=pair(out, "s0e", "s1"),
                         constraint_vs_l1=pair(out, "s0c", "s1"),
                         evolved_vs_l1_amp01=pair(out, "s0e_b", "s1_b"),
                         background=background(out, "s0e")))
    p = res["pert"]
    res["pert"]["ratio_amp01_over_amp1"] = [
        q["rms"]/max(r["rms"], 1e-300)
        for r, q in zip(p["evolved_vs_l1"][1:], p["evolved_vs_l1_amp01"][1:])]
    nl2.dump_json(res, os.path.join(out, "summary.json"))
    last = lambda rows: {k: rows[-1][k] for k in ("rms", "max", "rms_dR")}   # noqa: E731
    print(json.dumps(dict(
        exit=rcs, restart=res["restart"],
        hom_evolved=last(res["hom"]["evolved_vs_l1"]),
        hom_constraint=last(res["hom"]["constraint_vs_l1"]),
        hom_background=res["hom"]["background"][-1],
        pert_evolved=last(p["evolved_vs_l1"]), pert_constraint=last(p["constraint_vs_l1"]),
        pert_evolved_amp01=last(p["evolved_vs_l1_amp01"]),
        ratio=res["pert"]["ratio_amp01_over_amp1"],
        pert_background=res["pert"]["background"][-1]), indent=1))

    fs = ct.nl2_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.09, right=0.99, bottom=0.17, top=0.9, wspace=0.28)
    for a_, key, ttl in ((ax[0], "hom", "(a) homogeneous slice, kicks off"),
                         (ax[1], "pert", "(b) perturbed slice, kicks on")):
        for lab, cl, mk, nm in (("constraint_vs_l1", "0.4", "x", "constraint form"),
                                ("evolved_vs_l1", fs.PAL["orange"], "o", "evolved form")):
            rows = res[key][lab][1:]
            a_.semilogy([r["time"] for r in rows], [max(r["rms"], 1e-18) for r in rows],
                        mk + "-", ms=3, color=cl, label=nm)
        if key == "pert":
            rows = res[key]["evolved_vs_l1_amp01"][1:]
            a_.semilogy([r["time"] for r in rows], [max(r["rms"], 1e-18) for r in rows],
                        "s--", ms=3, color=fs.PAL["blue"], label="evolved form, amplitude 0.1")
        a_.set_xlabel("$t$ (1/H$_*$)")
        a_.set_ylabel(r"rms$_n$ $|c_R^{L0}/c_R^{L1}-1|$")
        a_.set_title(ttl, fontsize=8)
        a_.set_ylim(1e-15, 1e-2)
        a_.legend(fontsize=6, loc="upper right", ncol=2)
    fig.savefig(os.path.join(out, "fig_level0_evolved.png"), dpi=200)
    ok = all(v == 0 for v in rcs.values()) and not differ and same
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
