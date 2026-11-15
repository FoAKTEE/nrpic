#!/usr/bin/env python3
"""Test 0 of the work package "id": the format-2 reader of nrpic_cf against the Python
evaluator `nrpic.io.Table2`, on the curved slice of the bound ball.

    test0_reader.py run      generate the data and start the registered runs (processors)
    test0_reader.py          compare; writes test0_numbers.json and figs/t0_reader
"""
import json
import math
import os
import subprocess
import sys

import numpy as np

import idlib
from nrpic import expanding_ball as eb
from nrpic import io as nio

IC = "/data/haiyangw/nrpic/scratch/core/id/ic_ball"
HALF = 16.0
BALL = dict(M=1.0, Rb=5.0, e0=0.16, RE=10.0)


def run():
    os.makedirs(IC, exist_ok=True)
    for n in (64, 128):
        h = 2.0 * HALF / n
        stem = os.path.join(IC, f"t0_bound_n{n:03d}")
        subprocess.run([sys.executable, os.path.join(idlib.WT, "problems/ic/make_ball.py"),
                        "--Rb", "5", "--e0", "0.16", "--RE", "10", "--h", repr(h), "--out", IC,
                        "--prefix", os.path.basename(stem)], check=True, capture_output=True)
        with open(stem + ".json") as f:
            meta = json.load(f)
        cases = [(f"t0-bound-n{n:03d}", stem + ".tab")]
        if n == 64:
            # the same table with the exterior set to zero
            with open(stem + ".tab") as f:
                txt = f.read().replace("# exterior = pg", "# exterior = zero")
            with open(stem + "_zero.tab", "w") as f:
                f.write(txt)
            cases.append((f"t0-bound-zero-n{n:03d}", stem + "_zero.tab"))
        for tag, tab in cases:
            cmd = [sys.executable, os.path.join(idlib.HERE, "nrun.py"),
                   "--purpose", f"test 0, format-2 reader against the Python evaluator: {tag}",
                   "--tag", tag, "--inputs", stem + ".nrp", tab, stem + ".json",
                   "--athinput", os.path.join(idlib.WT, "problems/ball/ball.athinput"),
                   f"mesh/nx1={n}", f"mesh/nx2={n}", f"mesh/nx3={n}",
                   f"mesh/x1min={-HALF}", f"mesh/x1max={HALF}", f"mesh/x2min={-HALF}",
                   f"mesh/x2max={HALF}", f"mesh/x3min={-HALF}", f"mesh/x3max={HALF}",
                   "time/nlim=0", "particles/field_time1=1.0e9", "particles/traj_dcycle=1",
                   f"particles/traj_ntrack={meta['traj_ntrack']}", "particles/snap_dt=-1.0",
                   f"particles/particle_file={stem}.nrp", f"problem/comp0_file={tab}",
                   "problem/shift=table"]
            r = subprocess.run(cmd, capture_output=True, text=True)
            print(tag, r.returncode, r.stdout.strip().splitlines()[-1])


def compare():
    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    mans = idlib.manifests("t0-")
    ball = eb.Ball(**BALL)
    res = {}
    prof = {}
    for tag, man in sorted(mans.items()):
        tab = nio.read_tab2([i["path"] for i in man["inputs"] if i["path"].endswith(".tab")][0])
        out = man["output_directory"]
        fld = idlib.read_field(os.path.join(out, "ball.field.00000.bin"))
        n = fld["n"][0]
        dx = 2.0 * HALF / n
        r = idlib.cell_radius(fld["n"], HALF)
        u, kl, kt, alp, br = tab(r)
        trk = fld["Khat"] + 2.0 * fld["Theta"]
        tr = idlib.read_traj(out)
        x = tr["x"][0]
        rp = np.sqrt(np.sum(x * x, axis=1))
        bex = tab(rp)[4][:, None] * x / rp[:, None]
        mabs = np.sqrt(fld["chi"] * (fld["Mx"] ** 2 + fld["My"] ** 2 + fld["Mz"] ** 2))
        vac = (r > 6.7) & (r < 9.0)
        away = np.abs(rp - ball.rbar_b) > 3.0 * dx          # the particle metric is a cubic
        d = dict(run_id=man["run_id"], cells=n, dx=dx, exterior=tab.exterior,
                 K_err=float(np.abs(trk - (kl + 2.0 * kt)).max()),
                 alpha_err=float(np.abs(fld["alpha"] - alp).max()),
                 chi_err=float(np.abs(fld["chi"] - (1.0 + u) ** -4).max()),
                 beta_err=float(np.abs(tr["beta"][0] - bex)[away].max()),
                 beta_scale=float(np.abs(bex).max()),
                 H_vac_max=float(np.abs(fld["H"][vac]).max()), M_vac_max=float(mabs[vac].max()),
                 K_beyond_table_max=float(np.abs(trk[r > tab.rlast]).max()),
                 rlast=tab.rlast)
        res[tag[3:]] = d
        edges = np.arange(0.0, HALF - 3.0 * dx, dx)
        idx = np.digitize(r.ravel(), edges) - 1
        ok = (idx >= 0) & (idx < len(edges) - 1)
        cnt = np.maximum(np.bincount(idx[ok], minlength=len(edges) - 1), 1)
        prof[tag[3:]] = (0.5 * (edges[1:] + edges[:-1]),
                         np.sqrt(np.bincount(idx[ok], weights=fld["H"].ravel()[ok] ** 2, minlength=len(edges) - 1) / cnt),
                         np.sqrt(np.bincount(idx[ok], weights=mabs.ravel()[ok] ** 2, minlength=len(edges) - 1) / cnt))
        print(tag, {k: (f"{v:.3e}" if isinstance(v, float) else v) for k, v in d.items()})
    if "bound-n064" in res and "bound-n128" in res:
        a, b = res["bound-n064"], res["bound-n128"]
        res["order"] = dict(H=math.log2(a["H_vac_max"] / b["H_vac_max"]),
                            M=math.log2(a["M_vac_max"] / b["M_vac_max"]))
        print("order in the curved vacuum, 6.7 < r < 9 M:", res["order"])
    with open(os.path.join(idlib.HERE, "test0_numbers.json"), "w") as f:
        json.dump(res, f, indent=1)
        f.write("\n")
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.2))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.15, top=0.95, wspace=0.26)
    for k, c in zip(("bound-n064", "bound-n128"), (fs.PAL["blue"], fs.PAL["red"])):
        if k in prof:
            rr, hh, mm = prof[k]
            ax[0].semilogy(rr, np.maximum(hh, 1e-20), color=c, label=r"$\Delta x=%g\,M$" % res[k]["dx"])
            ax[1].semilogy(rr, np.maximum(mm, 1e-20), color=c, label=r"$\Delta x=%g\,M$" % res[k]["dx"])
    for a, yl in zip(ax, (r"rms of $|H|$ in shells", r"rms of $|M_i|$ in shells")):
        for rb in (ball.rbar_b, float(ball.isotropic(ball.RE))):
            a.axvline(rb, **fs.MASK_LINE)
        a.axvspan(6.7, 9.0, color=fs.PAL["blue"], alpha=0.1)
        a.set_xlabel(r"isotropic radius $\bar r/M$", labelpad=-2)
        a.set_ylabel(yl)
        a.set_ylim(1e-14, 1.0)
        a.legend()
    os.makedirs(idlib.FIGS, exist_ok=True)
    fs.save(fig, os.path.join(idlib.FIGS, "t0_reader"))


if __name__ == "__main__":
    run() if sys.argv[1:] == ["run"] else compare()
