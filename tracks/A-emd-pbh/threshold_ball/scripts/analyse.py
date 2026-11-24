#!/usr/bin/env python3
"""Analysis of the threshold scan of the expanding ball (package threshold_ball, Track A):
predictions T1-T6 of JOURNAL.md entry 1, from the card runs of queue.txt lines 3-13.

    analyse.py --out DIR [--member NAME ...] [--jobs 4]

For every member (table MEMBERS: run directory, mesh, data set) whose run directory holds
ball.nrpic.hst: compare_tb.py (copy of conv_ball's compare.py, gauge leak, rate 8, nested
geometry 32:<1/h_f>, every line kept), then from its numbers and the run's own files:
  - searches of the finder (ball.horizon_status_0.txt: one row per search, found or not);
    BH = found in at least three consecutive searches spanning at least 5 m_AH and in every
    later search (entry 1); isolated detections before that are counted;
  - ddet = proper time of the tracked particles at the finder's mean radius at first
    detection minus the exact tau_AH of the shell there (compare.py finder.first);
    tau_det = that proper time; for the threshold the exact core tau_AH is the reference;
  - dmmed = median over detections of m_irr / m_exact(slice) - 1; dm1 at first detection;
  - slice or finder: the outermost marginally trapped sphere on the mesh line (Misner-Sharp
    mass from the adm line output, compare.py line_horizon) at the line time nearest the
    first detection, its mass against the finder's m_irr and the exact shell mass there;
  - T6: Slurm/chain end state, guard stop (segment logs), cost per cycle (cpu time used over
    cycles of each segment), and the ratio ||H||_2 / ||16 pi E||_2 over the mesh line outside
    the finder's mean radius (r^2 dr weights, positive x), largest over the line outputs.
Writes threshold.json, threshold.md and figures fig_threshold_*.png.
"""
import argparse
import concurrent.futures as cf
import glob
import json
import math
import os
import re
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
S = "/data/haiyangw/nrpic/scratch/A-emd-pbh"
DATA = S + "/A-20261121-202812-cae4436"
T_END = 45.0

# name: (run dir, nest OUTER:HF_INV, data set key of prep_summary.json, lattice, tlim, data dir)
MEMBERS = {
    "B-d0.42": (S + "/A-20261121-204149-c48bd33", "32:32", "dc0p42", "nestB", 51.0),
    "B-d0.40": (S + "/A-20261121-204250-0bf45c7", "32:32", "dc0p4", "nestB", 54.0),
    "A-d0.42": (S + "/A-20261121-235851-d2200d7/A-d0.42", "32:16", "dc0p42", "nestA", 51.0),
    "A-d0.40": (S + "/A-20261121-235851-d2200d7/A-d0.40", "32:16", "dc0p4", "nestA", 54.0),
    "B-d0.45": (S + "/A-20261122-003952-552f805", "32:32", "dc0p45", "nestB", 47.0),
    "B-d0.50": (S + "/A-20261122-051554-7662f22", "32:32", "dc0p5", "nestB", 42.0),
    "B-d1.00": (S + "/A-20261122-054155-4b3d92e", "32:32", "dc1p0", "nestB", 23.0),
    "B-d0.70": (S + "/A-20261122-100756-829dcf9", "32:32", "dc0p7", "nestB", 31.0),
    "B-d0.35": (S + "/A-20261122-101357-9a73701", "32:32", "dc0p35", "nestB", 62.0),
    "B-d0.20": (S + "/A-20261122-132959-dfba903", "32:32", "dc0p2", "nestB", 70.0),
    "C-R1.25": (S + "/A-20261122-141100-f00cfc2", "16:64", "R1p25", "nestC", 16.0),
    "C-d0.42": (S + "/A-20261122-173202-f98c79f", "32:64", "dc0p42", "nestC", 51.0),
}
DC = {"dc1p0": 1.0, "dc0p7": 0.7, "dc0p5": 0.5, "dc0p45": 0.45, "dc0p42": 0.42, "dc0p4": 0.40,
      "dc0p35": 0.35, "dc0p2": 0.20, "R1p25": 1.5}


def run_compare(name, out):
    rd, nest, key, lat, tlim = MEMBERS[name]
    prep = os.path.join(DATA, key, lat)
    o_, hf_ = nest.split(":")
    cmd = [sys.executable, os.path.join(HERE, "compare_tb.py"), "--prep", prep, "--seg", rd,
           "--gauge", "leak", "--leak", "8", "--dx", f"{float(o_) / float(hf_):g}", "--nest", nest,
           "--label", name, "--out", out, "--figdir", os.path.join(out, "figs"), "--keep-all-lines"]
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MPLBACKEND="Agg")
    with open(os.path.join(out, f"{name}_compare.log"), "w") as f:
        f.write("# " + " ".join(cmd) + "\n")
        f.flush()
        rc = subprocess.call(cmd, stdout=f, stderr=subprocess.STDOUT, env=env)
    return name, rc


def searches(rd):
    p = os.path.join(rd, "ball.horizon_status_0.txt")
    if not os.path.isfile(p):
        return np.zeros((0, 3))
    rows = []
    for ln in open(p):
        if ln.startswith("#") or not ln.strip():
            continue
        v = ln.split("#")[0].split()
        rows.append((float(v[1]), int(v[2]), float(v[5]) if len(v) > 5 else np.nan))   # time, found, area
    a = np.array(rows) if rows else np.zeros((0, 3))
    # repeated times after a restart: the rows written last win
    keep, tn = [], np.inf
    for i in range(len(a) - 1, -1, -1):
        if a[i, 0] < tn:
            keep.append(i)
            tn = a[i, 0]
    return a[keep[::-1]]


def persistence(srch, m_ah):
    """First index from which every search finds the horizon, if that run has at least three
    searches spanning at least 5 m_AH; isolated finds before it."""
    if len(srch) == 0:
        return None, 0
    found = srch[:, 1] > 0
    first = None
    for i in range(len(found)):
        if found[i:].all():
            first = i
            break
    if first is None:
        return None, int(found.sum())
    n = len(found) - first
    span = srch[-1, 0] - srch[first, 0]
    iso = int(found[:first].sum())
    if n >= 3 and span >= 5 * m_ah:
        return first, iso
    return None, iso


def seg_info(rd):
    logs = sorted(glob.glob(os.path.join(rd, "chain", "seg*.log"))) + \
        sorted(glob.glob(os.path.join(rd, "athena.*.log")))
    out = []
    for lg in logs:
        if os.path.islink(lg):
            continue
        txt = open(lg, errors="replace").read()
        cyc = [int(c) for c in re.findall(r"cycle=(\d+) time=", txt)]
        cpu = re.findall(r"cpu time used\s*=\s*([0-9.e+-]+)", txt)
        rec = dict(log=os.path.basename(lg), terminated_tlim="Terminating on time limit" in txt,
                   guard=bool(re.search(r"guard|non-finite|not finite", txt, re.I)),
                   exit=(re.findall(r"# exit=(\d+)", txt) or [None])[-1])
        if cpu and len(cyc) > 1 and cyc[-1] > cyc[0]:
            rec["s_per_cycle"] = float(cpu[-1]) / (cyc[-1] - cyc[0])
        rec["cycles"] = (cyc[0], cyc[-1]) if cyc else None
        out.append(rec)
    st = os.path.join(rd, "chain", "STATUS")
    status = open(st).read().strip() if os.path.isfile(st) else None
    if status is None:          # batch member: status file of the batch
        bs = os.path.join(os.path.dirname(rd), "batch.list.status")
        if os.path.isfile(bs):
            for ln in open(bs):
                if ln.strip().endswith(os.path.basename(rd)):
                    status = ln.split()[1]
    return out, status


def read_tab(path):
    with open(path) as f:
        first = f.readline()
        names = f.readline().strip("# \n").split()
    t = float(first.split("time=")[1].split()[0])
    d = np.loadtxt(path, comments="#", ndmin=2)
    return t, {n: d[:, i] for i, n in enumerate(names)}


def constraint_ratio(rd, finder_rows, step=4):
    """max over line outputs (every `step`-th) of ||H||/||16 pi E|| outside the finder radius."""
    con = sorted(glob.glob(os.path.join(rd, "tab", "ball.con.*.tab")))
    ft = np.array([r["t"] for r in finder_rows]) if finder_rows else np.zeros(0)
    fr = np.array([r["r_mean"] for r in finder_rows]) if finder_rows else np.zeros(0)
    ser = []
    for f in con[::step]:
        g = f.replace(".con.", ".tmunu.")
        if not os.path.isfile(g):
            continue
        t, c = read_tab(f)
        _, m = read_tab(g)
        x = c["x1v"]
        o = np.argsort(x)
        x, H, E = x[o], c["con_H"][o], m["tmunu_E"][o]
        pos = x > 0
        x, H, E = x[pos], H[pos], E[pos]
        dx = np.gradient(x)
        rh = 0.0
        if len(ft):
            j = int(np.argmin(np.abs(ft - t)))
            if abs(ft[j] - t) < 0.2:
                rh = fr[j]
        s = x > rh
        w = x[s] ** 2 * dx[s]
        num = math.sqrt(np.nansum(w * H[s] ** 2))
        den = math.sqrt(np.nansum(w * (16 * math.pi * E[s]) ** 2))
        ser.append((t, num / den if den > 0 else np.nan, rh))
    return ser


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--member", action="append", default=None)
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()
    os.makedirs(os.path.join(a.out, "figs"), exist_ok=True)
    summ = json.load(open(os.path.join(DATA, "prep_summary.json")))
    names = a.member or list(MEMBERS)
    todo = [n for n in names if os.path.isfile(os.path.join(MEMBERS[n][0], "ball.nrpic.hst"))]
    print("members with output:", todo)
    with cf.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        rcs = dict(ex.map(lambda n: run_compare(n, a.out), todo))
    print("compare_tb exit codes:", rcs)
    res = {}
    for n in todo:
        rd, nest, key, lat, tlim = MEMBERS[n]
        ex_ = summ.get(key, {})
        tau_ah, m_ah = ex_.get("tau_AH"), ex_.get("m_AH")
        r = dict(name=n, run=rd, nest=nest, delta_c=DC[key], tlim=tlim, compare_rc=rcs.get(n),
                 exact=dict(tau_ta=ex_.get("tau_ta"), tau_AH=tau_ah, tau_c=ex_.get("tau_c"), m_AH=m_ah,
                            outcome_45=("BH" if (tau_ah is not None and tau_ah <= T_END) else "late")))
        segs, status = seg_info(rd)
        r["segments"] = segs
        r["status"] = status
        cps = [s["s_per_cycle"] for s in segs if "s_per_cycle" in s]
        r["s_per_cycle"] = float(np.median(cps)) if cps else None
        r["guard"] = any(s["guard"] for s in segs)
        srch = searches(rd)
        r["n_searches"] = int(len(srch))
        r["n_found"] = int(srch[:, 1].sum()) if len(srch) else 0
        fi, iso = persistence(srch, m_ah or 0.4)
        r["persistent_from_t"] = float(srch[fi, 0]) if fi is not None else None
        r["isolated_finds_before"] = iso
        r["first_found_t"] = float(srch[srch[:, 1] > 0][0, 0]) if r["n_found"] else None
        r["last_search_t"] = float(srch[-1, 0]) if len(srch) else None
        nj = os.path.join(a.out, f"{n}_numbers.json")
        if os.path.isfile(nj):
            num = json.load(open(nj))
            fd = num.get("finder", {})
            ff = fd.get("first", {})
            rows = fd.get("rows", [])
            if ff:
                r["tau_det"] = ff.get("tau_at_horizon")
                r["ddet"] = (ff["tau_at_horizon"] - ff["tau_ah_exact_shell_at_r"]
                             if ff.get("tau_ah_exact_shell_at_r") is not None else None)
                r["ddet_core"] = ff["tau_at_horizon"] - tau_ah if tau_ah else None
                r["m_irr_first"] = ff.get("m_irr")
                r["r_mean_first"] = ff.get("r_mean")
                r["m_exact_shell_first"] = ff.get("m_exact_shell_at_r")
                r["dm1"] = (ff["m_irr"] / ff["m_exact_shell_at_r"] - 1.0
                            if ff.get("m_exact_shell_at_r") else None)
            e = fd.get("m_irr_rel_err_vs_m_exact_slice", {})
            r["dmmed"] = e.get("median")
            r["dm_maxabs"] = e.get("maxabs")
            r["dm_n"] = e.get("n")
            # detections with particle proper time below t_end
            r["n_det_tau_below_45"] = int(sum(1 for q in rows if q.get("tau_at_horizon") is not None
                                              and q["tau_at_horizon"] < T_END))
            r["min_tau_det"] = min([q["tau_at_horizon"] for q in rows if q.get("tau_at_horizon") is not None],
                                   default=None)
            ev = num.get("events", {})
            r["core_turnaround_n"] = ev.get("core", {}).get("turnaround", {}).get("n")
            r["core_turnaround_dtau_mean"] = ev.get("core", {}).get("turnaround", {}).get("dtau_mean")
            r["core_trapping_n"] = ev.get("core", {}).get("trapping", {}).get("n")
            r["first_trapped_tracked"] = ev.get("first_trapped_tracked")
            r["traj_t_last"] = num.get("traj", {}).get("t_last")
            r["history"] = {k: v for k, v in num.get("history", {}).items() if k != "series"}
            lh = num.get("line_horizon", {})
            r["line_horizon_first_t"] = lh.get("first_t")
            ent = lh.get("entries", [])
            if ff and ent:
                lt = np.array([q["t"] for q in ent])
                j = int(np.argmin(np.abs(lt - ff["t"])))
                r["slice_or_finder"] = dict(t_finder=ff["t"], t_line=float(lt[j]), m_line=ent[j]["m"],
                                            r_line=ent[j]["r"], m_exact_shell_line=ent[j]["m_exact_shell"],
                                            m_finder=ff["m_irr"], r_finder=ff["r_mean"],
                                            m_exact_shell_finder=ff.get("m_exact_shell_at_r"))
                # the same at the median detection: line minus finder over all matched times
                pairs = []
                for q in rows:
                    k = int(np.argmin(np.abs(lt - q["t"])))
                    if abs(lt[k] - q["t"]) <= 0.07:
                        pairs.append((q["t"], q["m_irr"], ent[k]["m"], ent[k]["m_exact_shell"],
                                      q.get("m_exact_shell_at_r") or np.nan))
                r["line_vs_finder_pairs"] = pairs
            r["line_first_t_maxH_gt_1"] = num.get("line_first_t_maxH_gt_1")
            r["misner_sharp_maxabs_t0"] = num.get("misner_sharp", {}).get("maxabs_t0")
            r["cr_series"] = constraint_ratio(rd, rows)
            crs = [c[1] for c in r["cr_series"] if np.isfinite(c[1])]
            r["cr_max"] = max(crs) if crs else None
        res[n] = r
    # ---- verdicts
    V = {}
    bhB = ["B-d1.00", "B-d0.70", "B-d0.50", "B-d0.45", "B-d0.42"]
    t1 = []
    for n in bhB:
        if n not in res:
            continue
        r = res[n]
        lim_d = 0.2 if r["delta_c"] >= 0.7 else 0.5
        lim_m = 5e-3 if r["delta_c"] >= 0.7 else 1e-2
        ok = (r["persistent_from_t"] is not None and r.get("ddet") is not None and abs(r["ddet"]) <= lim_d
              and r.get("dmmed") is not None and abs(r["dmmed"]) <= lim_m)
        t1.append(dict(member=n, persistent=r["persistent_from_t"] is not None, ddet=r.get("ddet"),
                       bound_ddet=lim_d, dmmed=r.get("dmmed"), bound_dm=lim_m, holds=bool(ok)))
    V["T1"] = t1
    t2 = []
    for n, must in (("B-d0.40", True), ("B-d0.35", True), ("B-d0.20", False)):
        if n not in res:
            continue
        r = res[n]
        early = r.get("n_det_tau_below_45", 0)
        formed = r["persistent_from_t"] is not None
        ok = (early == 0) and (formed == must)
        t2.append(dict(member=n, detections_tau_below_45=early, min_tau_det=r.get("min_tau_det"),
                       persistent=formed, expected_horizon=must, holds=bool(ok),
                       core_turnaround_n=r.get("core_turnaround_n")))
    V["T2"] = t2
    if "B-d0.42" in res and "B-d0.40" in res:
        a42, a40 = res["B-d0.42"].get("tau_det"), res["B-d0.40"].get("tau_det")
        V["T3"] = dict(tau_det_042=a42, tau_det_040=a40, exact_042=43.656, exact_040=46.415,
                       holds=bool(a42 is not None and a40 is not None and a42 <= T_END < a40
                                  and abs(a42 - 43.656) <= 0.5 and abs(a40 - 46.415) <= 0.5))
    t4 = {}
    for n in ("A-d0.42", "A-d0.40"):
        if n in res:
            t4[n] = dict(persistent=res[n]["persistent_from_t"] is not None, status=res[n]["status"],
                         guard=res[n]["guard"], traj_t_last=res[n].get("traj_t_last"))
    if "C-d0.42" in res and "B-d0.42" in res:
        c, b = res["C-d0.42"], res["B-d0.42"]
        t4["C_vs_B"] = dict(ddet_C=c.get("ddet"), ddet_B=b.get("ddet"), dmmed_C=c.get("dmmed"),
                            dmmed_B=b.get("dmmed"))
    V["T4"] = t4
    if "C-R1.25" in res:
        c = res["C-R1.25"]
        V["T5"] = dict(ddet=c.get("ddet"), dmmed=c.get("dmmed"), ref_ddet=0.0166, ref_dmmed=-2.09e-4,
                       holds=bool(c.get("ddet") is not None and abs(c["ddet"] - 0.0166) <= 0.02
                                  and c.get("dmmed") is not None and abs(c["dmmed"] + 2.09e-4) <= 1e-3))
    t6 = []
    for n, r in res.items():
        t6.append(dict(member=n, status=r["status"], guard=r["guard"], s_per_cycle=r["s_per_cycle"],
                       cr_max=r.get("cr_max")))
    V["T6"] = t6
    out = dict(members={k: {kk: vv for kk, vv in v.items() if kk not in ("cr_series", "line_vs_finder_pairs")}
                        for k, v in res.items()}, verdicts=V)
    json.dump(out, open(os.path.join(a.out, "threshold.json"), "w"), indent=1, default=float)
    json.dump({k: dict(cr=v.get("cr_series"), pairs=v.get("line_vs_finder_pairs")) for k, v in res.items()},
              open(os.path.join(a.out, "threshold_series.json"), "w"), default=float)
    # ---- table
    L = ["| member | delta_c | exact tau_AH | status | guard | s/cycle | searches | found | persistent from t | "
         "tau_det | ddet | dm1 | dmmed | cr_max |", "|" + "---|" * 14]

    def f(x, fmt):
        return "-" if x is None else (fmt % x)
    for n, r in sorted(res.items(), key=lambda q: (q[0][0], -q[1]["delta_c"])):
        L.append("| %s | %.2f | %s | %s | %s | %s | %d | %d | %s | %s | %s | %s | %s | %s |" % (
            n, r["delta_c"], f(r["exact"]["tau_AH"], "%.3f"), r["status"], r["guard"],
            f(r["s_per_cycle"], "%.3f"), r["n_searches"], r["n_found"], f(r["persistent_from_t"], "%.3f"),
            f(r.get("tau_det"), "%.3f"), f(r.get("ddet"), "%+.4f"), f(r.get("dm1"), "%+.2e"),
            f(r.get("dmmed"), "%+.2e"), f(r.get("cr_max"), "%.3f")))
    L.append("")
    for n, r in res.items():
        if "slice_or_finder" in r:
            q = r["slice_or_finder"]
            L.append("%s first detection t=%.3f: finder m_irr %.5f (r %.3f), line MOTS m %.5f at t=%.3f (r %.3f); "
                     "exact shell mass at finder r %.5f, at line r %.5f" % (
                         n, q["t_finder"], q["m_finder"], q["r_finder"], q["m_line"], q["t_line"], q["r_line"],
                         q["m_exact_shell_finder"] or np.nan, q["m_exact_shell_line"]))
    open(os.path.join(a.out, "threshold.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))
    print(json.dumps(V, indent=1, default=float))
    figures(res, a.out)


def figures(res, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, os.path.join(PKG, "..", "conv_ball", "scripts"))
    try:
        from nrpic import figstyle as fs
    except ImportError:
        sys.path.insert(0, os.path.join(PKG, "..", "periodic_threshold", "scripts"))
        import figstyle as fs
    fs.use_style()
    col = {"A": fs.PAL["blue"], "B": fs.PAL["red"], "C": fs.PAL["green"] if "green" in fs.PAL else "k"}
    # (1) outcome: tau_det against exact tau_AH, the t_end line
    fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 6.4))
    fig.subplots_adjust(left=0.1, right=0.98, bottom=0.08, top=0.95, wspace=0.32, hspace=0.38)
    ax = axs[0, 0]
    dcs = np.linspace(0.2, 1.0, 50)
    ex = sorted([(r["delta_c"], r["exact"]["tau_AH"]) for r in res.values() if r["exact"]["tau_AH"]
                 and r["name"] != "C-R1.25"])
    if ex:
        ax.plot([e[0] for e in ex], [e[1] for e in ex], "k--", lw=1.0, label=r"exact $\tau_{AH}$ (core edge)")
    for n, r in res.items():
        if r.get("tau_det") is not None and n != "C-R1.25":
            ax.plot(r["delta_c"], r["tau_det"], "o", color=col[n[0]], ms=5)
        elif n != "C-R1.25":
            ax.plot(r["delta_c"], r["tlim"], "v", color=col[n[0]], ms=6, mfc="none")
    ax.axhline(T_END, **fs.MASK_LINE)
    ax.text(0.62, T_END + 1.5, r"$t_{\rm end}=45$", fontsize=8)
    ax.set_xlabel(r"core contrast $\delta_c$")
    ax.set_ylabel(r"proper time at first detection")
    ax.set_title("(a) horizon time; open triangles: none by tlim", fontsize=9)
    ax.set_yscale("log")
    ax.legend(loc="upper right", fontsize=7)
    ax = axs[0, 1]
    for n, r in res.items():
        if r.get("ddet") is not None:
            ax.plot(r["delta_c"], abs(r["ddet"]), "o", color=col[n[0]], ms=5)
            ax.annotate(n.split("-")[0], (r["delta_c"], abs(r["ddet"])), fontsize=6, xytext=(3, 2),
                        textcoords="offset points")
    ax.plot([0.42, 0.5], [0.5, 0.5], "k:", lw=1)
    ax.plot([0.7, 1.0], [0.2, 0.2], "k:", lw=1)
    ax.set_yscale("log")
    ax.set_xlabel(r"$\delta_c$")
    ax.set_ylabel(r"$|\Delta\tau_{\rm det}|$ (M)")
    ax.set_title("(b) T1 bounds dotted", fontsize=9)
    ax = axs[1, 0]
    for n, r in res.items():
        if r.get("dmmed") is not None:
            ax.plot(r["delta_c"], abs(r["dmmed"]), "o", color=col[n[0]], ms=5)
            if r.get("dm1") is not None:
                ax.plot(r["delta_c"], abs(r["dm1"]), "x", color=col[n[0]], ms=5)
    ax.plot([0.42, 0.5], [1e-2, 1e-2], "k:", lw=1)
    ax.plot([0.7, 1.0], [5e-3, 5e-3], "k:", lw=1)
    ax.set_yscale("log")
    ax.set_xlabel(r"$\delta_c$")
    ax.set_ylabel(r"$|m_{\rm irr}/m_{\rm exact}-1|$")
    ax.set_title("(c) o median over detections, x first detection", fontsize=9)
    ax = axs[1, 1]
    for n, r in res.items():
        if r.get("cr_series"):
            c = np.array([[q[0], q[1]] for q in r["cr_series"]])
            ax.semilogy(c[:, 0], c[:, 1], color=col[n[0]], lw=0.8, alpha=0.8)
    ax.axhline(0.1, **fs.GUIDE)
    ax.set_xlabel("t")
    ax.set_ylabel(r"$\|H\|/\|16\pi E\|$ on the line, $r>r_{AH}$")
    ax.set_title("(d) T6 constraint ratio (B red, A blue, C green)", fontsize=9)
    fig.savefig(os.path.join(out, "fig_threshold_outcome.png"), dpi=150)
    # (2) slice or finder: finder m_irr and line MOTS mass against exact, per member
    mem = [n for n, r in res.items() if r.get("line_vs_finder_pairs")]
    if mem:
        nc = 3
        nr = int(math.ceil(len(mem) / nc))
        fig, axs = plt.subplots(nr, nc, figsize=(fs.FULL_WIDTH, 2.4 * nr), squeeze=False)
        fig.subplots_adjust(left=0.09, right=0.98, bottom=0.08, top=0.95, wspace=0.35, hspace=0.5)
        for k, n in enumerate(mem):
            ax = axs[k // nc, k % nc]
            p = np.array(res[n]["line_vs_finder_pairs"], dtype=float)
            ax.plot(p[:, 0], p[:, 1] / p[:, 4] - 1, ".", ms=3, color=fs.PAL["red"], label="finder")
            ax.plot(p[:, 0], p[:, 2] / p[:, 3] - 1, ".", ms=3, color=fs.PAL["blue"], label="line MOTS")
            ax.axhline(0, color="k", lw=0.6)
            ax.set_title(n, fontsize=8)
            ax.set_xlabel("t", fontsize=8)
            ax.set_ylabel(r"$m/m_{\rm shell}-1$", fontsize=8)
            ax.set_ylim(-0.1, 0.1)
            if k == 0:
                ax.legend(fontsize=7)
        for k in range(len(mem), nr * nc):
            axs[k // nc, k % nc].axis("off")
        fig.savefig(os.path.join(out, "fig_threshold_slice_or_finder.png"), dpi=150)


if __name__ == "__main__":
    main()
