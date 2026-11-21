"""Figure: the first passage's input for 400 cycles on one card (smoke test E7).

Reads the raw outputs of the smoke run (common.RUNS["e7"], directory P1smoke/; each file
checked against the run's sha256sums.txt): the AthenaK log (wall time every 50 cycles; the
MeshBlock counts at start and end; MeshBlock-cycles and the timed seconds of the summary),
the card-memory samples written beside it, the three tracker files and the three horizon
summaries (readers: common.nrread(), failed searches counted as missed), and the input file
(puncture positions and momenta). The horizon medians and missed counts are checked against
p1_analysis.json of the passage analysis rerun (common.RUNS["e7an"]). Cost of the full passage
[arithmetic]: tlim / dt cycles times a mean tree of N MeshBlocks divided by the measured rate,
with N = the tree at cycle 400 and N = the largest tree of the wave-1 trees along the Newtonian
track at q = 4 (mesh_count_b.json of common.RUNS["mesh4"], case D256q4_m8_r1.8).
Writes fig_smoke.{pdf,png} and fig_smoke_numbers.json.
"""
import os
import re
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402
import czstyle as cz  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

STEM = "fig_smoke"
LOG = "P1smoke/athena.20261115-122314.log"
MEM = "P1smoke/athena.20261115-122314.gpumem.csv"
INP = "P1smoke/p1_q4.athinput"
HRMS_GOOD = 1e-3
NAMES = {0: r"$m_1$", 1: r"$m_2$", 2: r"$M$"}


def read_log(path):
    el, cyc, tt = [], [], []
    d = {}
    for line in open(path):
        m = re.match(r"elapsed=(\S+) cycle=(\d+) time=(\S+) dt=(\S+)", line)
        if m:
            el.append(float(m.group(1)))
            cyc.append(int(m.group(2)))
            tt.append(float(m.group(3)))
            d["dt"] = float(m.group(4))
        for key, pat in (("nmb_start", r"Total number of MeshBlocks = (\d+)"),
                         ("nmb_end", r"Current number of MeshBlocks = (\d+)"),
                         ("mb_cycles", r"MeshBlock-cycles = (\d+)"),
                         ("cpu_s", r"cpu time used\s*=\s*(\S+)"),
                         ("tlim", r"tlim=(\S+) nlim"),
                         ("created", r"(\d+) MeshBlocks created"),
                         ("deleted", r"created, (\d+) deleted")):
            m = re.search(pat, line)
            if m:
                d[key] = float(m.group(1))
    d.update(elapsed=np.array(el), cycle=np.array(cyc), time=np.array(tt))
    return d


def read_problem(path):
    vals = {}
    blk = None
    for line in open(path):
        s = line.split("#")[0].strip()
        if s.startswith("<"):
            blk = s.strip("<>")
        elif "=" in s and blk == "problem":
            k, v = [x.strip() for x in s.split("=", 1)]
            vals[k] = v
    return vals


def main():
    out = C.out_dir("figures")
    nr = C.nrread()
    rdir = os.path.join(C.SCRATCH, C.RUNS["e7"], "P1smoke")
    for rel in (LOG, MEM, INP) + tuple(f"P1smoke/hills.co_{n}.txt" for n in range(3)) + \
            tuple(f"P1smoke/hills.horizon_summary_{n}.txt" for n in range(3)):
        C.run_file("e7", rel)
    an = C.load_json("e7an", "p1_analysis.json")
    m4 = C.load_json("mesh4", "mesh_count_b.json")["tracks"]["D256q4_m8_r1.8"]
    lg = read_log(os.path.join(rdir, os.path.basename(LOG)))
    mem = np.genfromtxt(os.path.join(rdir, os.path.basename(MEM)), delimiter=",",
                        skip_header=1, usecols=(1, 2))
    prob = read_problem(os.path.join(rdir, os.path.basename(INP)))
    trk = nr.read_trackers(rdir)
    hz = nr.read_horizons(rdir)

    rate = lg["mb_cycles"] / lg["cpu_s"]
    spc = np.diff(lg["elapsed"]) / np.diff(lg["cycle"])
    cycles = int(round(lg["tlim"] / lg["dt"]))
    n_big = int(m4["n_max"])
    cost = {str(n): cycles * n / rate / 3600.0 for n in (int(lg["nmb_end"]), n_big)}
    nums = {"runs": [C.RUNS["e7"], C.RUNS["e7an"], C.RUNS["mesh4"]],
            "nmb_start": int(lg["nmb_start"]), "nmb_end": int(lg["nmb_end"]),
            "created": int(lg["created"]), "deleted": int(lg["deleted"]),
            "mb_cycles": int(lg["mb_cycles"]), "timed_s": lg["cpu_s"], "rate": rate,
            "s_per_cycle_windows": spc.tolist(), "s_per_cycle_mean": float(np.mean(spc)),
            "mem_peak_MiB": float(mem[:, 0].max()), "dt": lg["dt"], "tlim": lg["tlim"],
            "cycles_passage": cycles, "n_largest_wave1_tree": n_big, "card_hours": cost}
    # trackers: offset from the input at t = 0, speed against the momentum per bare mass
    off, fr = {}, {}
    for n in range(3):
        x0 = np.array([float(prob[f"comp{n}_x{i}"]) for i in (1, 2, 3)])
        p = np.array([float(prob[f"comp{n}_p{i}"]) for i in (1, 2, 3)])
        mass = float(prob[f"comp{n}_mass"])
        tr = trk[n]
        off[n] = float(np.linalg.norm(tr["x"][0] - x0))
        fr[n] = (tr["t"], np.linalg.norm(tr["v"], axis=1) / (np.linalg.norm(p) / mass))
    nums["tracker_offset_t0"] = {NAMES[n]: off[n] for n in off}
    nums["tracker_speed_ratio_end"] = {NAMES[n]: float(fr[n][1][-1]) for n in fr}
    nums["horizons"] = {}
    for n in range(3):
        h, miss = hz[n]
        med = float(np.median(h["mass"]))
        C.close(med, an["horizon_median"][str(n)], 1e-12, f"horizon median {n}")
        assert miss == an["horizon_missed"][str(n)], f"missed searches {n}"
        good = h["hrms"] < HRMS_GOOD
        nums["horizons"][NAMES[n]] = dict(median=med, found=int(len(h["mass"])), missed=int(miss),
                                         good=int(good.sum()),
                                         first_good_t=float(h["t"][good][0]) if good.any() else None,
                                         good_range=[float(h["mass"][good].min()),
                                                     float(h["mass"][good].max())] if good.any() else None)
    C.close(nums["mb_cycles"], 689088, 0, "MeshBlock-cycles")

    cz.use_style()
    col = {0: cz.PAL["blue"], 1: cz.PAL["red"], 2: "k"}
    fig, axs = plt.subplots(2, 2, figsize=(7.0, 4.1))
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.105, top=0.975, wspace=0.27, hspace=0.36)
    a = axs[0, 0]
    a.hlines(spc, lg["time"][:-1], lg["time"][1:], color="k", lw=1.5)
    a.axhline(lg["cpu_s"] / lg["cycle"][-1], color=cz.PAL["blue"], lw=1.0, ls="--")
    a.text(0.04, 0.9, f"{int(lg['nmb_start'])} to {int(lg['nmb_end'])} MeshBlocks",
           transform=a.transAxes, fontsize=7)
    a.text(0.96, 0.1, "dashed: mean of the timed run", transform=a.transAxes, fontsize=7,
           ha="right", color=cz.PAL["blue"])
    a.set_xlabel(r"$t\;[M]$")
    a.set_ylabel("seconds per cycle")
    a.set_ylim(0, 1.2)
    b = axs[0, 1]
    tw = np.arange(len(mem)) * 0.5 / 60.0
    b.plot(tw, mem[:, 0] / 1024.0, color="k", lw=1.3)
    b.set_xlabel("wall time [min]")
    b.set_ylabel("card memory [GiB]")
    b.set_ylim(0, 80)
    b.text(0.96, 0.1, "slots for 2700 MeshBlocks", transform=b.transAxes, fontsize=7, ha="right")
    c = axs[1, 0]
    for n in range(3):
        c.plot(fr[n][0], fr[n][1], color=col[n], lw=1.2, label=NAMES[n])
    c.set_xlabel(r"$t\;[M]$")
    c.set_ylabel(r"$|v_{\rm tracker}|\,/\,(|P|/m)$")
    c.set_ylim(-0.05, 1.0)
    c.legend(frameon=False, fontsize=7.5, loc="upper left")
    d = axs[1, 1]
    for n in range(3):
        h, _ = hz[n]
        good = h["hrms"] < HRMS_GOOD
        med = nums["horizons"][NAMES[n]]["median"]
        d.plot(h["t"][good], 1e3 * (h["mass"][good] / med - 1), "o-", color=col[n], ms=2.5,
               lw=0.9, label=NAMES[n])
        d.plot(h["t"][~good], 1e3 * (h["mass"][~good] / med - 1), "o", color=col[n], ms=3,
               mfc="none", mew=0.8)
    d.set_xlabel(r"$t\;[M]$")
    d.set_ylabel(r"$10^3\,(M_{\rm AH}/{\rm median}-1)$")
    d.set_ylim(-15, 25)
    d.legend(frameon=False, fontsize=7.5, loc="lower right", ncol=3)
    d.text(0.04, 0.9, "open: residual above $10^{-3}$", transform=d.transAxes, fontsize=7)
    for ax in (a, c, d):
        ax.set_xlim(0, 1.6)
    cz.save(fig, os.path.join(out, STEM))
    C.write_numbers(out, STEM, nums)
    C.report_checks(STEM)


if __name__ == "__main__":
    main()
