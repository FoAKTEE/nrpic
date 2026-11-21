#!/usr/bin/env python3
"""T15 of the work package cosmo-amr: the options that no other test exercised
(prediction: tracks/core/JOURNAL-cosmo-amr.md).

    t15_options.py --new NEW_EXE --out DIR [--cores N]

  Gdt   T2's U (homogeneous universe, step 0.03125) with <z4c_guard> stop_dt_below = 0.05
  Gnp   T2's G (Courant number 1.5) with stop_nonfinite = false, stop_no_particles = true
  Gdc   T2's G with check_dcycle = 4
  Rh    T4's unit puncture (case a) with a sparse lattice of light particles, two cycles,
        finder every cycle, region_dcycle = 1 with region_radius1 = 1.0 and
        region_horizon = 0 (the sphere of the horizon once it is found)
Writes DIR/t15_summary.json and DIR/fig_t15_options.{pdf,png}."""
import argparse
import json
import os
import subprocess
import sys

import numpy as np

import amrlib as A
import t2_flrw as T2

PER = {f"ix{d}_bc": "periodic" for d in (1, 2, 3)}
PER.update({f"ox{d}_bc": "periodic" for d in (1, 2, 3)})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--new", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    ap.add_argument("--cores", type=int, default=4)
    ap.add_argument("--t4", default="/data/haiyangw/nrpic/scratch/core/"
                    "core-20261119-152106-9332260", help="run directory of T4")
    a = ap.parse_args()
    a.out, a.new = os.path.abspath(a.out), os.path.abspath(a.new)
    os.makedirs(a.out, exist_ok=True)
    ic1, ic8 = os.path.join(a.out, "ic1"), os.path.join(a.out, "ic8")
    if not os.path.exists(os.path.join(ic1, "particles.nrp")):
        subprocess.run([sys.executable, os.path.join(A.ROOT, "cosmo/ic/make_lattice.py"),
                        "--n", str(T2.N), "--ppc", "1", "--L", str(T2.L), "--xmin",
                        str(-T2.L/2), "--out", ic1], check=True, stdout=subprocess.DEVNULL)
    c = T2.cases(ic1, ic8)
    cs = {}
    cs["Gdt"] = c["U"].copy().set("z4c_guard", stop_dt_below=0.05).drop("fastflow")
    cs["Gnp"] = c["G"].copy().set("z4c_guard", stop_nonfinite=False, stop_no_particles=True)
    cs["Gdc"] = c["G"].copy().set("z4c_guard", check_dcycle=4)
    # a unit puncture of T4 (lattice of punctures through nrpic_cosmo, box [-4, 4)^3,
    # 64^3) with a sparse lattice of light particles (8^3, H0 = 1e-3: density 1e-6 of
    # the critical one), so that the region diagnostic of the particle module runs
    r = A.Inp(os.path.join(a.t4, "a", "punc.athinput"))
    icr = os.path.join(a.out, "ic_light")
    if not os.path.exists(os.path.join(icr, "particles.nrp")):
        subprocess.run([sys.executable, os.path.join(A.ROOT, "cosmo/ic/make_lattice.py"),
                        "--n", "8", "--ppc", "1", "--L", "8", "--xmin", "-4", "--H0",
                        "1e-3", "--out", icr], check=True, stdout=subprocess.DEVNULL)
    pb = A.Inp(os.path.join(A.ROOT, "problems/cosmo/flrw.athinput")).blocks["particles"]
    r.blocks["particles"] = pb.copy()
    r.set("particles", particle_file=os.path.join(icr, "particles.nrp"), region_dcycle=1,
          region_radius1=1.0, region_horizon=0, snap_dt=-1.0)
    r.set("time", nlim=2)
    r.set("fastflow", find_every=1)
    cs["Rh"] = r
    names = list(cs)
    base = {n: ("punc" if n == "Rh" else "flrw") for n in names}
    rcs = A.run_many([(a.new, cs[n], os.path.join(a.out, n), base[n], (), None)
                      for n in names], a.cores)
    res = {}
    for n, rc in zip(names, rcs):
        d = os.path.join(a.out, n)
        r = dict(exit=rc[0])
        g = os.path.join(d, f"{base[n]}.guard.txt")
        if os.path.exists(g):
            with open(g) as f:
                r["guard"] = f.read().splitlines()[1:4]
        hp = os.path.join(d, f"{base[n]}.nrpic.hst")
        if os.path.exists(hp):
            h = A.read_hst(hp)
            r.update(last_cycle=int(h["ncycle"][-1]), last_np=int(h["np"][-1]),
                     first_np0_cycle=(int(h["ncycle"][np.argmax(h["np"] == 0)])
                                      if np.any(h["np"] == 0) else None))
        rp = os.path.join(d, f"{base[n]}.region.hst")
        if os.path.exists(rp):
            g = A.read_hst(rp)
            r["region_columns"] = list(g.keys())
            r["region_rows"] = [[float(g[k][i]) for k in g] for i in range(len(g["time"]))]
        sp = os.path.join(d, f"{base[n]}.horizon_summary_0.txt")
        if os.path.exists(sp):
            with open(sp) as f:
                r["horizon_summary"] = [x.split()[:12] for x in f if not x.startswith("#")]
        res[n] = r
        print(n, {k: v for k, v in r.items() if k not in ("region_rows", "region_columns")},
              flush=True)
    with open(os.path.join(a.out, "t15_summary.json"), "w") as f:
        json.dump(res, f, indent=1)
        f.write("\n")

    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(8.0, 3.0))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.16, top=0.93, wspace=0.30)
    for i, n in enumerate(("Gnp", "Gdc")):
        hp = os.path.join(a.out, n, "flrw.nrpic.hst")
        if os.path.exists(hp):
            h = A.read_hst(hp)
            ax[0].plot(h["ncycle"], h["np"], "o-", ms=3, color=fs.SERIES[i], label=n)
    ax[0].set_xlabel("cycle")
    ax[0].set_ylabel("particles left")
    ax[0].legend(frameon=False)
    if "region_rows" in res.get("Rh", {}):
        cols = res["Rh"]["region_columns"]
        rows = np.array(res["Rh"]["region_rows"])
        t = rows[:, 0]
        for k, lab in (("V_in_s1", "V inside r = 1"), ("V_in_s2", "V inside the horizon"),
                       ("radius_s2", "radius of the horizon sphere")):
            if k in cols:
                ax[1].plot(t, rows[:, cols.index(k)], "o-", ms=3, label=lab)
    ax[1].set_xlabel("time")
    ax[1].set_ylabel("region diagnostic (puncture)")
    ax[1].legend(frameon=False, fontsize=8)
    fs.save(fig, os.path.join(a.out, "fig_t15_options"))
    plt.close(fig)
    return 0


if __name__ == "__main__":
    sys.exit(main())
