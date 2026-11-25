#!/usr/bin/env python3
"""Review test R8 (journal entry 10): what level 1 on the mesh differs from level 0 on
the mesh when nothing is perturbed.

    level01_dt.py --exe ATHENA --out DIR [--workers 5]

Homogeneous slice (<problem> id = flrw), kicks off, slow-roll input at 32^3 (nmax2 = 64),
t = 0 .. 1.0, the per-mode record at the cycles nearest to t = 0.5 and 1.0, with the
Courant numbers 0.25, 0.125 and 0.0625:
  l1_<c>   level 1 on the mesh: coefficients from the box means of the evolved mesh
  l0_<c>   level 0 on the mesh: coefficients from the Friedmann equations of the lockstep
The mesh is homogeneous to the last bit, so the two differ only by how the same
background is integrated in time.  Writes DIR/summary.json and DIR/fig_level01.png."""
import argparse
import concurrent.futures as cf
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cpu_tests as ct                      # noqa: E402
import nl2                                  # noqa: E402
import numpy as np                          # noqa: E402

CFL = (0.25, 0.125, 0.0625)


def cases():
    c = {}
    for cfl in CFL:
        # dumps at fixed cycles: 10, 20 at Courant 0.25 (t = 0.49, 0.98), doubled below
        nd = int(round(10*0.25/cfl))
        base = {**ct.BASE, **ct.HOM, **ct.OFF, "time/cfl_number": cfl, "time/tlim": 1.0,
                "scalar_field/dump_dt": -1.0, "scalar_field/dump_dcycle": nd,
                "time/nlim": 2*nd}
        c[f"l1_{cfl}"] = {**base, **ct.L1M}
        c[f"l0_{cfl}"] = {**base, **ct.L0M}
    return c


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
    res = dict(exe=os.path.abspath(a.exe), exit=rcs, wall_s=walls, rows=[])
    for cfl in CFL:
        for k in (1, 2):
            h1, n, n2, r1, d1 = ct.modes_at(os.path.join(out, f"l1_{cfl}"), k)
            h0, _, _, r0, d0 = ct.modes_at(os.path.join(out, f"l0_{cfl}"), k)
            _, rs, _ = ct.shells_at(os.path.join(out, f"l0_{cfl}"), k, n2)
            d = ct.rel(r1, r0)
            res["rows"].append(dict(
                cfl=cfl, dump=k, time_l1=h1["time"], time_l0=h0["time"],
                rms=float(np.sqrt(np.mean(d*d))), max=float(d.max()),
                rms_cut=float(np.sqrt(np.mean(d[n2 > 48]**2))),
                rms_low=float(np.sqrt(np.mean(d[n2 <= 16]**2))),
                # the time error of the mode equation itself, for scale: level 0 on the
                # mesh against its own shells carries the stencil, not shown here
                l0_vs_shell_low=float(ct.rel(r0, rs)[n2 <= 4].max())))
    by = {(r["cfl"], r["dump"]): r for r in res["rows"]}
    res["ratio_per_halving"] = {
        f"dump{k}": [by[(CFL[i], k)]["rms"]/by[(CFL[i+1], k)]["rms"] for i in range(2)]
        for k in (1, 2)}
    nl2.dump_json(res, os.path.join(out, "summary.json"))
    print(json.dumps(dict(exit=rcs, rows=res["rows"], ratio=res["ratio_per_halving"]),
                     indent=1))

    fs = ct.nl2_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 1, figsize=(fs.FULL_WIDTH*0.5, 2.8))
    fig.subplots_adjust(left=0.2, right=0.97, bottom=0.17, top=0.9)
    for k, cl, mk in ((1, fs.PAL["blue"], "o"), (2, fs.PAL["orange"], "s")):
        y = [by[(c, k)]["rms"] for c in CFL]
        ax.loglog(CFL, y, mk + "-", ms=4, color=cl,
                  label=f"$t = {by[(CFL[0], k)]['time_l1']:.2f}$")
    ax.loglog(CFL, [by[(CFL[0], 2)]["rms"]*(c/CFL[0])**4 for c in CFL], "--", color="0.4",
              lw=0.8, label=r"$\propto\Delta t^4$")
    ax.set_xlabel("Courant number")
    ax.set_ylabel(r"rms$_n$ $|c_R^{L1}/c_R^{L0}-1|$")
    ax.set_title("homogeneous slice, kicks off", fontsize=8)
    ax.legend(fontsize=6, loc="upper left")
    fig.savefig(os.path.join(out, "fig_level01.png"), dpi=200)
    sys.exit(0 if all(v == 0 for v in rcs.values()) else 1)


if __name__ == "__main__":
    main()
