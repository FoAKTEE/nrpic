#!/usr/bin/env python3
"""T10e of the work package cosmo-amr: where the jump of the Hamiltonian constraint after
the first regrid of the scouting run comes from (prediction:
tracks/core/JOURNAL-cosmo-amr.md, entries of T10e).

    t10e_jump.py --exe EXE --data DIR --out DIR [--tlim T] [--cores N] [--analyse-only]
                 [--cases u5,a5,...]

Track A's S1 data (DIR holds fields.bin and particles.nrp) with the example input
problems/cosmo_amr/peak_amr.athinput, finder off, constraint statistics every cycle:
  u5   no refinement (lapse_ratio_1 = 0.01: never asked for)
  a5   as the scouting run (lapse ladder, fine-shape deposit)
  a5c  as a5 with the uniform spreading (deposit_fine_shape = false)
  a5r  as a5 with every cloud on the root level (deposit_adaptive = false,
       deposit_max_level = 0)
Writes DIR/t10e_summary.json and DIR/fig_t10e_jump.{pdf,png}."""
import argparse
import glob
import json
import os
import sys

import numpy as np

import amrlib as A

CASES = {
    "u5": ["particles_amr/lapse_ratio_1=0.01"],
    "a5": [],
    "a5c": ["particles/deposit_fine_shape=false"],
    "a5r": ["particles/deposit_adaptive=false", "particles/deposit_max_level=0"],
}


def con_line(rd, q):
    p = os.path.join(rd, "tab", f"peak.con.{q:05d}.tab")
    if not os.path.exists(p):
        return None, None
    d, t = A.read_tab(p)
    o = np.argsort(d["x1v"])
    return {k: v[o] for k, v in d.items()}, t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    ap.add_argument("--tlim", type=float, default=3.5)
    ap.add_argument("--cores", type=int, default=4)
    ap.add_argument("--analyse-only", action="store_true")
    ap.add_argument("--cases", default="", help="comma-separated subset of the cases")
    a = ap.parse_args()
    sel = [n for n in CASES if not a.cases or n in a.cases.split(",")]
    a.out, a.exe, a.data = (os.path.abspath(a.out), os.path.abspath(a.exe),
                            os.path.abspath(a.data))
    os.makedirs(a.out, exist_ok=True)
    deck = A.Inp(os.path.join(A.ROOT, "problems/cosmo_amr/peak_amr.athinput"))
    common = [f"time/tlim={a.tlim}", f"problem/id_file={a.data}/fields.bin",
              f"particles/particle_file={a.data}/particles.nrp", "fastflow/start_time_0=100.0",
              "mesh_refinement/max_nmb_per_rank=300", "particles/cstat_dcycle=1",
              "particles/region_dcycle=4", "output3/dt=0.25", "output7/dt=100.0"]
    if not a.analyse_only:
        jobs = [(a.exe, deck, os.path.join(a.out, n), "peak", tuple(common + CASES[n]), None)
                for n in sel]
        rcs = A.run_many(jobs, a.cores)
        for n, rc in zip(sel, rcs):
            print(f"{n:4s} exit {rc[0]:3d} wall {rc[1]:8.1f} s", flush=True)
    res, keep = {}, {}
    for n in sel:
        rd = os.path.join(a.out, n)
        if not os.path.exists(os.path.join(rd, "peak.cstat.hst")):
            continue
        h = A.read_hst(os.path.join(rd, "peak.nrpic.hst"))
        s = A.read_hst(os.path.join(rd, "peak.cstat.hst"))
        g = A.read_hst(os.path.join(rd, "peak.region.hst"))
        nmb = h["nmb"].astype(int)
        ch = np.where(np.diff(nmb) != 0)[0] + 1
        r = {"exit": A.exit_status(rd) if os.path.exists(os.path.join(rd, "status.txt"))
             else None, "t_end": float(h["time"][-1]), "cycles": int(h["ncycle"][-1]),
             "nmb_changes": [[float(h["time"][i]), int(nmb[i-1]), int(nmb[i])] for i in ch],
             "Hr_max_max": float(np.max(s["Hr_max"])),
             "identity_max": float(np.max(np.abs(h["int_E"]/h["sum_mW"] - 1.0))),
             "E_min_smallest": float(np.min(h["E_min"]))}
        for tq in (0.0, 1.0, 2.0, 2.2, 2.5, 2.75, 3.0, 3.1, 3.25, 3.5, 4.0, 5.0):
            if tq <= s["time"][-1] + 1e-9:
                i = int(np.argmin(np.abs(s["time"] - tq)))
                j = int(np.argmin(np.abs(g["time"] - tq)))
                r[f"t{tq:g}"] = {"time": float(s["time"][i]), "Hr_max": float(s["Hr_max"][i]),
                                 "H_max": float(s["H_max"][i]), "Hr_mean": float(s["Hr_mean"][i]),
                                 "Mr_max": float(s["Mr_max"][i]),
                                 "H2_over_E2_in_s1": float(g["H2_in_s1"][j]/g["E2_in_s1"][j]),
                                 "H2_over_E2_in_s2": float(g["H2_in_s2"][j]/g["E2_in_s2"][j]),
                                 "nmb": int(nmb[int(np.argmin(np.abs(h["time"] - tq)))])}
        # first record with Hr_max above 0.05 (the jump)
        big = np.where(s["Hr_max"] > 0.05)[0]
        r["first_Hr_above_0.05"] = ({"time": float(s["time"][big[0]]),
                                     "Hr_max": float(s["Hr_max"][big[0]]),
                                     "Hr_max_before": float(s["Hr_max"][big[0]-1])}
                                    if len(big) else None)
        # largest ratio of Hr_max between consecutive records (a one-cycle jump)
        q = s["Hr_max"][2:]/s["Hr_max"][1:-1]
        iq = int(np.argmax(q))
        r["largest_step_ratio"] = {"ratio": float(q[iq]), "time": float(s["time"][iq+2])}
        if len(ch):
            w = s["time"][2:] > h["time"][ch[0]] + 1e-9
            if np.any(w):
                jq = int(np.argmax(np.where(w, q, 0.0)))
                r["largest_step_ratio_after_regrid"] = {"ratio": float(q[jq]),
                                                        "time": float(s["time"][jq+2])}
        # where on the x line |H| is largest, at the last table
        nt = len(glob.glob(os.path.join(rd, "tab", "peak.con.*.tab")))
        c, tc = con_line(rd, nt - 1)
        if c is not None:
            i = int(np.argmax(np.abs(c["con_H"])))
            r["x_line_last"] = {"time": float(tc), "x_of_max_absH": float(c["x1v"][i]),
                                "max_absH": float(abs(c["con_H"][i])),
                                "dx_min": float(np.min(np.diff(c["x1v"])))}
        res[n] = r
        keep[n] = (h, s, g, c, tc)
        print(n, json.dumps({k: v for k, v in r.items() if not k.startswith("t")
                             or k == "t_end"}), flush=True)
    with open(os.path.join(a.out, "t10e_summary.json"), "w") as f:
        json.dump(res, f, indent=1)
        f.write("\n")

    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(1, 3, figsize=(10.0, 3.2))
    fig.subplots_adjust(left=0.07, right=0.99, bottom=0.15, top=0.93, wspace=0.30)
    lab = {"u5": "no refinement", "a5": "ladder, fine shape", "a5c": "ladder, uniform spreading",
           "a5r": "ladder, clouds on the root"}
    sty = {"u5": "-", "a5": "-", "a5c": "--", "a5r": ":"}
    for i, n in enumerate(keep):
        h, s, g, c, tc = keep[n]
        ax[0].semilogy(s["time"], s["Hr_max"], sty[n], color=fs.SERIES[i], label=lab[n])
        ax[1].semilogy(g["time"], g["H2_in_s1"]/g["E2_in_s1"], sty[n], color=fs.SERIES[i],
                       label=lab[n])
        if c is not None:
            w = np.abs(c["x1v"]) < 6.0
            ax[2].semilogy(c["x1v"][w], np.maximum(np.abs(c["con_H"][w]), 1e-12), sty[n],
                           color=fs.SERIES[i], label=lab[n], lw=1.0)
    ax[0].set_ylabel(r"largest relative $|H|$")
    ax[1].set_ylabel(r"$\|H\|_2/\|16\pi E\|_2$ inside $r=2.45$")
    for q in ax[:2]:
        q.set_xlabel("conformal time")
    ax[0].legend(frameon=False, fontsize=7)
    ax[2].set_xlabel(r"$x$")
    ax[2].set_ylabel(r"$|H|$ on the $x$ line, last table")
    for xb in (-5.0, 5.0):
        ax[2].axvline(xb, color="grey", lw=0.5, ls=":")
    fs.save(fig, os.path.join(a.out, "fig_t10e_jump"))
    plt.close(fig)
    return 0


if __name__ == "__main__":
    sys.exit(main())
