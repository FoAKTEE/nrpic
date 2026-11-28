#!/usr/bin/env python3
"""Reader of EG8 (excguard JOURNAL entry 1, predictions E1-E8), written after the run ended and
before any of its outputs was read beyond the chain status and the segment logs (entry 3).

Steps:
  1. a view directory with the finder summary FILTERED by the status file (searches not found
     dropped, decision 0040 item 3, trap 8) and links to the other outputs;
  2. g2runs/tools/esf_criteria.py on that view (criterion (iii), D2, D3 against V-1L) -> E2, E5;
  3. g2long/tools/d4_timing.py on EG8 and FK -> E6;
  4. here: E1 (smallest horizon radius, removal reasons after 219.5 M, resumptions), E3 (EG8 - FK
     at common finder times 20-219 M), E4 (status file), E7 (card time from the segment logs),
     E8 (chain status, exit codes, guard file); one figure eg8_read.png.

Usage: eg8_read.py --eg8 RUNDIR --fk RUNDIR --esfl RUNDIR --data DATADIR --control V1L_SUMMARY
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TRACK = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(TRACK, "flux_tools"))
sys.path.insert(0, os.path.join(TRACK, "g2long", "tools"))
import fluxio  # noqa: E402
import figstyle  # noqa: E402  (g2long copy of python/nrpic/figstyle.py)

GUARD_OLD = 3.2   # 4 x 0.8 M
GUARD_NEW = 6.4   # 8 x 0.8 M


def read_status(path):
    rows = []
    for line in open(path):
        if line.startswith("#") or not line.strip():
            continue
        p = line.split("#")[0].split()
        rows.append([float(x) for x in p[:12]])
    a = np.array(rows)
    cols = dict(cycle=a[:, 0], time=a[:, 1], found=a[:, 2].astype(int), reason=a[:, 3].astype(int),
                flow=a[:, 4].astype(int), area_mass=a[:, 6], minradius=a[:, 8])
    return fluxio.dedupe(cols)


def filtered_view(run, base, out):
    """Copy of the summary without the searches the status file marks as not found."""
    os.makedirs(out, exist_ok=True)
    st = read_status(os.path.join(run, base + ".horizon_status_0.txt"))
    bad = set(np.round(st["time"][st["found"] == 0], 6))
    src = os.path.join(run, base + ".horizon_summary_0.txt")
    n_drop = 0
    with open(src) as f, open(os.path.join(out, base + ".horizon_summary_0.txt"), "w") as g:
        for line in f:
            if not line.startswith("#") and line.strip():
                t = float(line.split()[1])
                if round(t, 6) in bad:
                    n_drop += 1
                    continue
            g.write(line)
    for name in (base + ".removed.bin", base + ".acc.hst", base + ".nrpic.hst", "rst"):
        dst = os.path.join(out, name)
        if not os.path.lexists(dst):
            os.symlink(os.path.join(run, name), dst)
    return st, n_drop


def segment_times(chain):
    """(start, end, t0, t1, exit) per segment log, wall seconds from the start/end stamps."""
    from datetime import datetime
    segs = []
    for f in sorted(glob.glob(os.path.join(chain, "seg*.log"))):
        txt = open(f).read()
        s = re.search(r"start=(\S+)", txt)
        e = re.search(r"# exit=(\d+) end=(\S+)", txt)
        times = re.findall(r"time=([0-9.eE+-]+) cycle=(\d+)", txt)
        cpu = re.search(r"cpu time used\s*=\s*([0-9.eE+-]+)", txt)
        if not (s and e):
            continue
        ws = (datetime.fromisoformat(e.group(2)) - datetime.fromisoformat(s.group(1))).total_seconds()
        segs.append(dict(log=os.path.basename(f), wall_s=ws, exit=int(e.group(1)),
                         t_last=float(times[-1][0]) if times else None,
                         cpu_s=float(cpu.group(1)) if cpu else None))
    return segs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eg8", required=True)
    ap.add_argument("--fk", required=True)
    ap.add_argument("--esfl", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--control", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    J = {}

    # 1. filtered view
    view = os.path.join(a.out, "view")
    st, n_drop = filtered_view(a.eg8, "esflg8", view)
    J["summary_rows_dropped_not_found"] = n_drop

    # 2. criteria (iii), D2, D3 on the filtered view
    crit = os.path.join(a.out, "criteria")
    subprocess.run([sys.executable, os.path.join(TRACK, "g2runs", "tools", "esf_criteria.py"),
                    "--run", view, "--base", "esflg8", "--data", a.data, "--control", a.control,
                    "--tau_max", "650", "--out", crit], check=True)
    C = json.load(open(os.path.join(crit, "esf_criteria.json")))
    # 3. D4 for EG8 and FK
    d4 = os.path.join(a.out, "d4")
    subprocess.run([sys.executable, os.path.join(TRACK, "g2long", "tools", "d4_timing.py"),
                    "--out", d4, "--split", "219",
                    f"EG8={view}:esflg8:{a.data}", f"FK={a.fk}:esflk:{a.data}"], check=True)
    D4 = json.load(open(glob.glob(os.path.join(d4, "*.json"))[0]))

    # E1: horizon radius and removal reasons
    hor = fluxio.read_horizon(os.path.join(view, "esflg8.horizon_summary_0.txt"))
    th, rmin, Mh = hor["time"], hor["minradius"], hor["mass"]
    above = np.nonzero(rmin > GUARD_OLD)[0]
    t_cross = float(th[above[0]]) if above.size else None
    rem = fluxio.read_removed(os.path.join(a.eg8, "esflg8.removed.bin"))
    rst_t = fluxio.restart_times(os.path.join(a.eg8, "rst"))
    info = []
    if np.any(np.diff(rem["time"]) < 0):
        rem, info = fluxio.drop_overlaps(rem, rst_t)
    dust = rem["tag"] >= 140
    late = dust & (rem["time"] > 219.5)
    resumes = sorted(set(t for t, _ in info))
    # also every segment start (chain resumptions from restart files)
    near_resume = np.zeros(rem["time"].size, bool)
    for tr in rst_t:
        near_resume |= (rem["time"] >= tr) & (rem["time"] <= tr + 2.0)
    r2_late = late & (rem["reason"] == 2)
    J["E1"] = dict(t_minradius_above_3p2=t_cross, minradius_max=float(rmin.max()),
                   t_finder_end=float(th[-1]),
                   dust_removals_total=int(dust.sum()),
                   dust_by_reason_all={str(r): int(np.sum(dust & (rem["reason"] == r))) for r in (1, 2, 3, 4)},
                   dust_after_219p5_by_reason={str(r): int(np.sum(late & (rem["reason"] == r))) for r in (1, 2, 3, 4)},
                   reason2_after_219p5_within_2M_of_a_restart=int(np.sum(r2_late & near_resume)),
                   reason2_after_219p5_elsewhere=int(np.sum(r2_late & ~near_resume)),
                   last_reason3_time=float(rem["time"][dust & (rem["reason"] == 3)].max()),
                   overlaps_dropped=info, restart_times=[float(x) for x in rst_t])
    J["E1"]["holds"] = bool(t_cross is not None and abs(t_cross - 219.5) <= 3.0
                            and rmin.max() < GUARD_NEW and J["E1"]["reason2_after_219p5_elsewhere"] == 0
                            and J["E1"]["last_reason3_time"] > 255.0)

    # E2 (iii) bins
    bins = [b for b in C["iii"]["dust"]["bins"] if b["counted"]]
    med = np.array([b["median"] for b in bins])
    J["E2"] = dict(n_bins=len(bins), min=float(med.min()), max=float(med.max()),
                   bins=[(b["lo"], b["hi"], b["n"], b["median"]) for b in bins])
    J["E2"]["holds"] = bool(med.min() >= 0.0010 and med.max() <= 0.0032)
    J["E2"]["refuted"] = bool(med.max() > 0.0045 or med.min() < 0.0)

    # E3 EG8 - FK at common finder times on 20-219 M
    fk = fluxio.read_horizon(os.path.join(a.fk, "esflk.horizon_summary_0.txt"))
    t8 = np.round(th, 6)
    tk = np.round(fk["time"], 6)
    com, i8, ik = np.intersect1d(t8, tk, return_indices=True)
    w = (com >= 20) & (com <= 219)
    dMk = Mh[i8][w] - fk["mass"][ik][w]
    J["E3"] = dict(n=int(w.sum()), median=float(np.median(dMk)), p05=float(np.percentile(dMk, 5)),
                   p95=float(np.percentile(dMk, 95)))
    J["E3"]["holds"] = bool(2e-5 <= J["E3"]["median"] <= 1.2e-4)
    J["E3"]["refuted"] = bool(J["E3"]["median"] < 0 or J["E3"]["median"] > 3e-4)

    # E4 status
    s2 = st["time"] > 2.0
    fnd = s2 & (st["found"] == 1)
    J["E4"] = dict(n_after_2M=int(s2.sum()), found=int(fnd.sum()),
                   frac_not_found=float(1 - fnd.sum() / s2.sum()),
                   not_found_times=[float(x) for x in st["time"][s2 & (st["found"] == 0)]],
                   not_found_reasons=[int(x) for x in st["reason"][s2 & (st["found"] == 0)]],
                   flow_min=int(st["flow"][fnd].min()), flow_median=float(np.median(st["flow"][fnd])),
                   flow_max=int(st["flow"][fnd].max()),
                   frac_flow_in_100_200=float(np.mean((st["flow"][fnd] >= 100) & (st["flow"][fnd] <= 200))))
    J["E4"]["holds"] = bool(J["E4"]["frac_not_found"] <= 0.01)

    # E5 D2, D3
    J["E5"] = dict(D2=C["D2"], D3=C["D3"])
    J["E5"]["holds"] = bool(C["D2"]["n_below"] == 0 and C["D2"]["n_above"] == 0
                            and C["D3"]["n_violations"] == 0)
    # E6 D4
    J["E6"] = D4

    # E7 card time, E8 status
    segs = segment_times(os.path.join(a.eg8, "chain"))
    J["E7"] = dict(segments=segs, wall_h=sum(s["wall_s"] for s in segs) / 3600.0)
    J["E7"]["holds"] = bool(1.2 <= J["E7"]["wall_h"] <= 1.7)
    J["E7"]["refuted"] = bool(J["E7"]["wall_h"] > 2.0)
    status = open(os.path.join(a.eg8, "chain", "STATUS")).read().strip()
    guard = glob.glob(os.path.join(a.eg8, "*.guard.txt"))
    J["E8"] = dict(chain_status=status, last_exit=segs[-1]["exit"], t_last=segs[-1]["t_last"],
                   guard_files=guard)
    J["E8"]["holds"] = bool(status.startswith("DONE") and segs[-1]["exit"] == 0 and not guard
                            and abs(segs[-1]["t_last"] - 260.0) < 1e-6)
    # G-8 rate for the timing comparison (g3/amend entry 3): seconds per M of the long segments

    # ES-FL for the figure
    esfl = fluxio.read_horizon(os.path.join(a.esfl, "esfl.horizon_summary_0.txt"))
    with open(os.path.join(a.out, "eg8_read.json"), "w") as f:
        json.dump(J, f, indent=1, default=float)

    # figure
    import matplotlib
    matplotlib.use("Agg")
    figstyle.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(2, 2, figsize=(10, 7.2))
    A = ax[0, 0]
    A.plot(esfl["time"], esfl["minradius"], color="0.6", lw=1, label="ES-FL (guard 3.2 M)")
    A.plot(fk["time"], fk["minradius"], color="C0", lw=1, label="FK (start 1.6 M, guard 6.4 M)")
    A.plot(th, rmin, color="C3", lw=1.2, label="EG8 (start 0.8 M, factor 8: 6.4 M)")
    A.axhline(GUARD_OLD, ls=":", color="k", lw=0.8)
    A.axhline(GUARD_NEW, ls="--", color="k", lw=0.8)
    A.axvline(219.5, ls=":", color="0.5", lw=0.8)
    A.set_xlim(0, 262)
    A.set_ylim(0, 7)
    A.set_xlabel("t [M]")
    A.set_ylabel("smallest horizon radius [M]")
    A.legend(fontsize=7, loc="upper left")
    A.set_title("(a) E1: guard radius", fontsize=9)
    B = ax[0, 1]
    tb = np.arange(0, 262, 5.0)
    for r, c, lab in ((3, "C3", "reason 3 (horizon)"), (2, "C1", "reason 2 (lapse)")):
        s = dust & (rem["reason"] == r)
        B.hist(rem["time"][s], bins=tb, histtype="step", color=c, label=f"EG8 {lab}: {int(s.sum())}")
    B.axvline(219.5, ls=":", color="0.5", lw=0.8)
    for tr in rst_t:
        B.axvline(tr, color="0.85", lw=0.6, zorder=0)
    B.set_yscale("log")
    B.set_xlabel("t_rem [M]")
    B.set_ylabel("dust removals per 5 M")
    B.legend(fontsize=7)
    B.set_title("(b) E1: removal reasons (grey: restart times)", fontsize=9)
    Cc = ax[1, 0]
    lo = np.array([b[0] for b in J["E2"]["bins"]])
    Cc.step(lo + 5, 100 * med, where="mid", color="C3", label="EG8")
    Cc.axhspan(0.10, 0.32, color="C2", alpha=0.15, label="E2 band [0.10, 0.32] %")
    Cc.axhline(0.45, ls="--", color="k", lw=0.8, label="refutation 0.45 %")
    Cc.axhline(0.0, color="k", lw=0.5)
    Cc.set_xlabel("tau_rem [M]")
    Cc.set_ylabel("median M_AH/M_LTB - 1 [%]")
    Cc.legend(fontsize=7)
    Cc.set_title("(c) E2: criterion (iii), 10 M bins with >= 20", fontsize=9)
    D = ax[1, 1]
    D.plot(com[w], 1e5 * dMk, color="C3", lw=0.8, label="M_EG8 - M_FK")
    D.axhspan(2, 12, color="C2", alpha=0.15, label="E3 band [2e-5, 1.2e-4]")
    D.axhline(1e5 * J["E3"]["median"], color="k", lw=0.8, ls="--", label=f"median {J['E3']['median']:.2e}")
    D.set_xlabel("t [M]")
    D.set_ylabel("mass difference [1e-5 M]")
    D.legend(fontsize=7)
    D.set_title("(d) E3: polished minus unpolished finder", fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(a.out, "eg8_read.png"), dpi=130)
    print(json.dumps({k: (v.get("holds") if isinstance(v, dict) else None) for k, v in J.items()}, indent=1))


if __name__ == "__main__":
    main()
