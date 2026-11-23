#!/usr/bin/env python3
"""Ladder row 1: the Kerr passage of regression G (merged processor build).

Left: relative errors of E, L_z and Q along the passage for the two pushers with the
analytic metric and with the Hermite lattice. Right: final position error against the
step for the three pushers with the analytic metric, with a dt^2 guide.

    fig_geodesic.py OUTDIR    (writes OUTDIR/figures/fig_geodesic.*, OUTDIR/numbers_geodesic.json)
"""
import json
import sys
from pathlib import Path

import numpy as np

import common as C

import geo_common as gc  # noqa: E402  (analysis/geodesic, path set in common)

A = 0.9


def main():
    out = Path(sys.argv[1])
    (out / "figures").mkdir(parents=True, exist_ok=True)
    fs = C.style()
    import matplotlib.pyplot as plt
    run = C.SCRATCH / C.RUN["G"]
    fin = np.array(gc.kerr_ref()["orbits"]["ks_passage"]["final_state"]["ks"]["x"])
    nums = {}
    series = {}
    names = ["mid_ks_dt0.01", "bsym_ks_dt0.01", "mid_lat_dt0.01", "bchol_lat_dt0.01",
             "mid_ks_dt0.005", "mid_ks_dt0.02", "bsym_ks_dt0.005", "bsym_ks_dt0.02",
             "bchol_ks_dt0.005", "bchol_ks_dt0.01", "bchol_ks_dt0.02"]
    for n in names:
        d = run / n
        meta = json.loads(C.checked(d / "run.json").read_text())["meta"]
        C.checked(d / "geo.traj.bin")
        tr = gc.read_traj(d)
        inv = gc.invariant_errors(meta["system"], tr["x"], tr["u"], A)
        efin, _ = gc.final_position_error(meta["system"], tr, fin, A)
        series[n] = (tr["t"], inv)
        r = gc.radius(meta["system"], tr["x"], A)
        tp, rp = gc.local_extrema(tr["t"], r, "min")
        k = int(np.argmin(rp))
        for q in ("E", "Lz", "Q"):
            C.put(nums, f"geo.{n}.max_d{q}", float(inv["max_d" + q]), C.RUN["G"],
                  "V1" if n.endswith("dt0.01") and not n.startswith("bchol_ks") else "")
        C.put(nums, f"geo.{n}.final_pos_err", efin, C.RUN["G"])
        if n == "mid_ks_dt0.01":
            C.put(nums, "geo.r_peri", float(rp[k]), C.RUN["G"], "V1")
            C.put(nums, "geo.t_peri", float(tp[k]), C.RUN["G"], "V1")
            C.put(nums, "geo.E0", float(inv["ref"][0]), C.RUN["G"], "V1")
            C.put(nums, "geo.Lz0", float(inv["ref"][1]), C.RUN["G"], "V1")
            C.put(nums, "geo.Q0", float(inv["ref"][2]), C.RUN["G"], "V1")
    for p in ("mid", "bsym", "bchol"):
        dts = np.array([0.005, 0.01, 0.02])
        err = np.array([nums[f"geo.{p}_ks_dt{dt}.final_pos_err"]["value"]
                        for dt in ("0.005", "0.01", "0.02")])
        o = gc.pairwise_orders(dts, err)
        C.put(nums, f"geo.{p}.order_pair1", float(o[0]), C.RUN["G"], "V1")
        C.put(nums, f"geo.{p}.order_pair2", float(o[1]), C.RUN["G"], "V1")

    fig = plt.figure(figsize=(8.0, 3.3))
    ax = fig.add_axes([0.085, 0.16, 0.50, 0.78])
    bx = fig.add_axes([0.68, 0.16, 0.28, 0.78])
    cols = {"mid_ks_dt0.01": fs.PAL["blue"], "bsym_ks_dt0.01": fs.PAL["red"],
            "mid_lat_dt0.01": fs.PAL["green"], "bchol_lat_dt0.01": fs.PAL["yellow"]}
    labs = {"mid_ks_dt0.01": "midpoint, analytic", "bsym_ks_dt0.01": "Boris, analytic",
            "mid_lat_dt0.01": "midpoint, lattice", "bchol_lat_dt0.01": "Boris, lattice"}
    for n, c in cols.items():
        t, inv = series[n]
        ax.semilogy(t, np.maximum.accumulate(np.abs(inv["dE"])) + 1e-18, color=c, lw=1.5,
                    ls="-", label=labs[n])
        ax.semilogy(t, np.maximum.accumulate(np.abs(inv["dQ"])) + 1e-18, color=c, lw=1.5, ls=":")
    ax.set_xlabel(r"$t/M$")
    ax.set_ylabel(r"largest $|\Delta E/E|$ (solid), $|\Delta Q/Q|$ (dotted)")
    ax.set_ylim(1e-11, 1e-3)
    ax.set_xlim(0, 230)
    ax.legend(frameon=False, ncol=2, fontsize=8, loc="upper left")
    mk = {"mid": ("o", fs.PAL["blue"], "midpoint"), "bsym": ("s", fs.PAL["red"], "Boris symmetric"),
          "bchol": ("^", fs.PAL["green"], "Boris Cholesky")}
    dts = np.array([0.005, 0.01, 0.02])
    for p, (m, c, lab) in mk.items():
        err = [nums[f"geo.{p}_ks_dt{dt}.final_pos_err"]["value"] for dt in ("0.005", "0.01", "0.02")]
        bx.loglog(dts, err, marker=m, color=c, lw=1.2, label=lab)
    e0 = nums["geo.mid_ks_dt0.01.final_pos_err"]["value"]
    bx.loglog(dts, e0 * (dts / 0.01) ** 2 * 0.5, **fs.GUIDE, label=r"$\propto \Delta t^2$")
    bx.set_xticks(dts)
    bx.set_xticklabels(["0.005", "0.01", "0.02"])
    bx.minorticks_off()
    bx.set_xlabel(r"$\Delta t/M$")
    bx.set_ylabel("final position error")
    bx.legend(frameon=False, fontsize=8, loc="upper left")
    fs.save(fig, str(out / "figures" / "fig_geodesic"))
    (out / "numbers_geodesic.json").write_text(json.dumps(nums, indent=1))
    for k in ("mid_ks_dt0.01", "bsym_ks_dt0.01", "mid_lat_dt0.01", "bchol_lat_dt0.01"):
        print(k, " ".join(f"{nums[f'geo.{k}.max_d{q}']['value']:.4g}" for q in ("E", "Lz", "Q")))


if __name__ == "__main__":
    main()
