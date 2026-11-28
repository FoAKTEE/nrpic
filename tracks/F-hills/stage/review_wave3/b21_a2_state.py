#!/usr/bin/env python3
"""State of the vacuum passage A2 (lead, batch 21; batch 35: the label and the figure title are read
from the chain's STATUS and the last record, no longer fixed to PARTIAL): what the complete and cut segments
of the chain F-20261124-210400-902c650 hold, whether the tracker trajectory survives the
truncation of the tracker file at each restart, and predictions S1-S6 of JOURNAL.md (batch 21).

Inputs (read only): the run directories of A (F-20261121-203144-b2cf16b, 0 to 61.8 M) and A2
(F-20261124-210400-902c650, from A's restart 23 at 61.80 M) under scratch/F-hills/:
  trk_keep/<UTC stamp>/hills.co_<n>.txt  tracker copies made by athena_resume_bc.sh before each
                                         start (each holds one segment: restart time to cut)
  hills.co_<n>.txt                       live tracker file (the newest segment)
  hills.horizon_summary_<n>.txt, hills.z4c.user.hst, waveforms/rpsi4_*  (appended files)
  chain/events.log                       attempts, restart file used, cut or wall-clock stop
Readers: nr_first/scripts/nrread.py (join of copies, later segment wins from its first time;
failed horizon searches removed by the failure signature, made without <fastflow> diagnostics).

Output (--out): b21_a2_state.json; fig_b21_a2_state.png/.pdf (copies' time spans, overlap
differences, separation of the pair, distances to M).

Batch 35 (verifier part 2, stage/G1/VERIFIER.md sections 16-17; GATE_REVIEW.md section 5):
  - S6 drift fits use only accepted searches with hrms <= 1e-2 (finding F5: "found" is not
    converged); the counts dropped are reported; the heavy hole is quoted on its converged upper
    branch (hrms < 1e-6) over 86.6-131 M;
  - MeshBlocks are reported per run (A and A2 separately; "Total" at a segment's start and
    "Current" at its end), so the source of each extreme is named;
  - S7: the end state at the last common tracker time (m2's distance and speeds against M; the
    last summary rows of finders 1 and 2 with hrms and mean expansion; status rows after 186 M).
"""
import argparse
import glob
import json
import os
import re
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "tracks/F-hills/nr_first/scripts"))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(WT, "python"))
import nrread as nr  # noqa: E402
import b11_cards as bc  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

S = "/data/haiyangw/nrpic/scratch/F-hills"
RUN_A = f"{S}/F-20261121-203144-b2cf16b"
RUN_A2 = f"{S}/F-20261124-210400-902c650"
DT = 1.953125e-3          # time step of the P1b m/16 deck (hst column dt)
WAVE_R = (40, 48, 70, 90)


def copies(rundir, n):
    """Tracker files of tracker n in write order with their rows (iter, t, x)."""
    out = []
    for p in nr.tracker_files(rundir, n):
        a = nr.read_table(p)
        if a.size == 0:
            continue
        out.append({"path": os.path.relpath(p, rundir), "iter": a[:, 0].astype(int), "t": a[:, 1],
                    "x": a[:, 2:5]})
    return out


def overlaps(cs):
    """For every earlier copy i and later copy j: max |x_i - x_j| at the cycles both hold."""
    res = []
    for j in range(1, len(cs)):
        for i in range(j):
            common, ia, ja = np.intersect1d(cs[i]["iter"], cs[j]["iter"], return_indices=True)
            if len(common) == 0:
                continue
            d = np.linalg.norm(cs[i]["x"][ia] - cs[j]["x"][ja], axis=1)
            res.append({"earlier": cs[i]["path"], "later": cs[j]["path"], "n_cycles": int(len(common)),
                        "t_from": float(cs[j]["t"][ja].min()), "t_to": float(cs[j]["t"][ja].max()),
                        "max_dx": float(d.max()), "dx_first_cycle": float(d[0])})
    return res


def coverage(t):
    t = np.unique(t)
    g = np.diff(t)
    k = int(np.argmax(g)) if len(g) else 0
    return {"t_first": float(t[0]), "t_last": float(t[-1]), "n_times": int(len(t)),
            "max_gap": float(g.max()) if len(g) else None, "t_at_max_gap": float(t[k]) if len(g) else None}


def all_rows_time(path, col):
    a = nr.read_table(path)
    return a[:, col] if a.size else np.zeros(0)


def chain_state(rundir):
    try:
        return open(os.path.join(rundir, "chain", "STATUS")).read().strip()
    except OSError:
        return "NONE"


def seg_mesh(rundir):
    """MeshBlocks at the start ("Total") and end ("Current") of each segment log, with the log."""
    tot, cur, peak = [], [], []
    for log in sorted(glob.glob(os.path.join(rundir, "chain", "seg*.log"))):
        txt = open(log, errors="replace").read()
        b = os.path.basename(log)
        tot += [(int(x), b) for x in re.findall(r"Total number of MeshBlocks = (\d+)", txt)]
        cur += [(int(x), b) for x in re.findall(r"Current number of MeshBlocks = (\d+)", txt)]
        peak += [int(x) for x in re.findall(r"gpu_mem_peak_MiB=(\d+)", txt)]
    both = tot + cur
    mx = max(both) if both else (None, None)
    mn = min(both) if both else (None, None)
    return {"mb_max": mx[0], "mb_max_log": mx[1], "mb_min": mn[0], "mb_min_log": mn[1],
            "total_max": max(tot)[0] if tot else None, "current_max": max(cur)[0] if cur else None,
            "gpu_peak_MiB": max(peak) if peak else None, "n_logs": len(glob.glob(os.path.join(rundir, "chain", "seg*.log")))}


def status_rows(path, t_after):
    """Status file rows after t_after: (found flags, area masses); rows end with '# <words>'."""
    fl, am = [], []
    if not os.path.exists(path):
        return np.zeros(0), np.zeros(0)
    for line in open(path):
        if line.startswith("#"):
            continue
        v = line.split("#")[0].split()
        if len(v) < 7:
            continue
        if float(v[1]) > t_after:
            fl.append(int(v[2]))
            am.append(float(v[6]))
    return np.array(fl), np.array(am)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    o = ap.parse_args()
    os.makedirs(o.out, exist_ok=True)
    st = chain_state(RUN_A2)
    res = {"runs": {"A": RUN_A, "A2": RUN_A2}, "chain_status_A2": st}

    # --- S1, S2: tracker copies, coverage, overlaps -------------------------------------
    trk = {}
    cs_all = {}
    for name, rd in (("A", RUN_A), ("A2", RUN_A2)):
        trk[name] = {}
        for n in (0, 1, 2):
            cs = copies(rd, n)
            cs_all[(name, n)] = cs
            merged = nr.read_tracker_merged([os.path.join(rd, c["path"]) for c in cs])
            ov = overlaps(cs)
            trk[name][n] = {
                "n_files": len(cs),
                "spans": [[c["path"], float(c["t"][0]), float(c["t"][-1]), int(len(c["t"]))] for c in cs],
                "merged": coverage(merged["t"]),
                "overlaps": ov,
                "max_overlap_dx": max([v["max_dx"] for v in ov], default=None),
            }
    joined = bc.trackers("A")          # A + A2 (b11_cards.RUNS["A2"] is the requeued run)
    res["joined_coverage"] = {str(n): coverage(joined[n]["t"]) for n in joined}
    res["trackers"] = {k: {str(n): v for n, v in d.items()} for k, d in trk.items()}
    gaps = [trk[k][n]["merged"]["max_gap"] for k in trk for n in trk[k]] + \
        [res["joined_coverage"][n]["max_gap"] for n in res["joined_coverage"]]
    ovs = [trk[k][n]["max_overlap_dx"] for k in trk for n in trk[k] if trk[k][n]["max_overlap_dx"] is not None]
    res["S1"] = {"max_gap_all": float(max(gaps)), "bound": 2 * DT,
                 "verdict": "MET" if max(gaps) <= 2 * DT * 1.001 else "REFUTED"}
    res["S2"] = {"max_overlap_dx_all": float(max(ovs)) if ovs else None, "bound": 1e-5, "refute_above": 1e-3,
                 "verdict": ("MET" if ovs and max(ovs) <= 1e-5 else
                             "REFUTED" if ovs and max(ovs) > 1e-3 else "NOT MET (between bound and refutation)")}

    # --- S3: appended outputs -------------------------------------------------------------
    s3 = {}
    for n in (0, 1, 2):
        p = os.path.join(RUN_A2, f"hills.horizon_summary_{n}.txt")
        t = all_rows_time(p, 1)
        s3[f"horizon_summary_{n}"] = dict(coverage(t), n_rows=int(len(t)))
    th = all_rows_time(os.path.join(RUN_A2, "hills.z4c.user.hst"), 0)
    s3["hst"] = dict(coverage(th), n_rows=int(len(th)))
    wave_ok = True
    for r in WAVE_R:
        tw, _ = nr.read_rpsi4(RUN_A2, r)
        raw = all_rows_time(os.path.join(RUN_A2, "waveforms", f"rpsi4_real_{r:04d}.txt"), 0)
        grid = np.arange(62.0, 96.0 + 1e-9, 0.25)
        missing = [float(g) for g in grid if not np.any(np.abs(tw - g) < 1e-6)]
        wave_ok &= not missing
        s3[f"rpsi4_{r}"] = dict(coverage(tw), n_rows_raw=int(len(raw)), n_grid=int(len(grid)),
                                missing_on_grid=missing[:10], n_missing=len(missing))
    hs_ok = all(s3[f"horizon_summary_{n}"]["t_first"] < 62.0 and s3[f"horizon_summary_{n}"]["t_last"] > 96.0
                for n in (0, 1, 2))
    s3["verdict"] = "MET" if (wave_ok and hs_ok and s3["hst"]["t_first"] <= 62.0 and s3["hst"]["t_last"] >= 96.0) else "REFUTED"
    res["S3"] = s3

    # --- chain attempts (events.log) -------------------------------------------------------
    ev = open(os.path.join(RUN_A2, "chain", "events.log")).read().splitlines()
    att = []
    for line in ev:
        m = re.search(r"seg=(\d+) job=(\d+) attempt \d+: athena -r \S+/rst/(hills\.\d+\.rst)", line)
        if m:
            att.append({"seg": int(m.group(1)), "job": int(m.group(2)), "restart": m.group(3)})
        m = re.search(r"seg=(\d+) job=(\d+) (received SIGTERM|wall-clock limit reached at 'time=(\S+))", line)
        if m and att and att[-1]["job"] == int(m.group(2)):
            att[-1]["end"] = "SIGTERM" if "SIGTERM" in m.group(3) else f"wall-clock at t = {float(m.group(4)):.3f}"
    res["attempts"] = att

    # --- S4, S5: the passage so far ----------------------------------------------------------
    t, s, _, _ = bc.pair(joined, 0, 1)
    k = (t >= 61.8)
    i_min = int(np.argmin(s[k]))
    tA2 = t[k]
    smin, tmin = float(s[k][i_min]), float(tA2[i_min])
    mins, maxs = bc.local_extrema(t, s)
    res["S4"] = {"s_min_after_61.8": smin, "t_at_s_min": tmin, "s_min_all": float(s.min()),
                 "t_s_min_all": float(t[np.argmin(s)]), "local_minima": [m for m in mins if m[0] > 40],
                 "local_maxima": [m for m in maxs if m[0] > 40], "s_end": float(s[-1]), "t_end": float(t[-1]),
                 "band": "2.0-2.7 M at 63-75 M; s > 1 M throughout",
                 "verdict": "MET" if (2.0 <= smin <= 2.7 and 63 <= tmin <= 75 and s.min() > 1.0) else "REFUTED"}
    tc, X, V = nr.common_times(joined, keys=[0, 1, 2], dt=0.25)
    com = 0.5 * (X[:, 0] + X[:, 1])
    dcm = np.linalg.norm(com - X[:, 2], axis=1)
    d0 = np.linalg.norm(X[:, 0] - X[:, 2], axis=1)
    d1 = np.linalg.norm(X[:, 1] - X[:, 2], axis=1)
    kk = tc >= tc[-1] - 5
    slope = float(np.polyfit(tc[kk], dcm[kk], 1)[0])
    res["S5"] = {"d_cm_at_end": float(dcm[-1]), "t_end": float(tc[-1]), "d_cm_slope_last5M": slope,
                 "d_cm_min": float(dcm.min()), "t_d_cm_min": float(tc[np.argmin(dcm)]),
                 "d_m1_end": float(d0[-1]), "d_m2_end": float(d1[-1]),
                 "verdict": ("MET (A2-2 open)" if (9 <= dcm[-1] <= 16 and slope < 0) else "REFUTED")}

    # --- S6: A2-5 to the last record (accepted searches only; no diagnostics) ----------------
    hz = nr.read_horizons(RUN_A2)
    s6 = {}
    HRMS_MAX = 1e-2       # batch 35: accepted searches above this are unconverged (finding F5)
    for n in (0, 1, 2):
        d, nfail = hz[n]
        good = d["hrms"] <= HRMS_MAX
        s6[f"finder{n}"] = {"drift_per_M_65_95": bc.drift_per_M(d["t"][good], d["mass"][good], 65, 95),
                            "drift_per_M_65_95_all_accepted": bc.drift_per_M(d["t"], d["mass"], 65, 95),
                            "mass_min": float(d["mass"][good].min()), "mass_max": float(d["mass"][good].max()),
                            "mass_median": float(np.median(d["mass"][good])), "n_accepted": int(len(d["t"])),
                            "n_hrms_above_1e-2": int((~good).sum()), "n_failed_signature": nfail}
    d2 = hz[2][0]
    up = (d2["hrms"] < 1e-6) & (d2["t"] >= 86.6) & (d2["t"] <= 131.0)
    s6["heavy_upper_branch_86.6_131"] = {"n": int(up.sum()), "median": float(np.median(d2["mass"][up])) if up.any() else None,
                                         "change": float(np.ptp(d2["mass"][up])) if up.any() else None,
                                         "hrms_max": float(d2["hrms"][up].max()) if up.any() else None}
    conv = (d2["hrms"] < 1e-6) & (d2["t"] <= 131.0)
    s6["heavy_hole_change"] = float(np.ptp(d2["mass"][conv]))
    s6["heavy_hole_change_note"] = ("converged searches (hrms < 1e-6) of A2 up to 131 M, before m1's approach; "
                                    "the lower branches and the 62-86.6 M decline have hrms 1e-4 to 6.5e-4 (unconverged)")
    s6["heavy_hole_change_hrms_le_1e-2_before_133"] = float(np.ptp(d2["mass"][(d2["t"] < 133.0) & (d2["hrms"] <= HRMS_MAX)]))
    appr = (d2["t"] > 131.0) & (d2["t"] < 137.4)
    s6["heavy_approach_131_137.4"] = {"mass_at_133": float(d2["mass"][np.argmin(np.abs(d2["t"] - 133.0))]),
                                      "mass_at_135": float(d2["mass"][np.argmin(np.abs(d2["t"] - 135.0))]),
                                      "mass_max": float(d2["mass"][appr].max()), "hrms_max": float(d2["hrms"][appr].max())}
    h = nr.read_hst(os.path.join(RUN_A2, "hills.z4c.user.hst"))
    s6["rms_H_max"] = float(np.sqrt(h["H2"]).max())
    s6["rms_H_t_max"] = float(h["time"][int(np.argmax(h["H2"]))]) if "time" in h else None
    s6["rms_H_end"] = float(np.sqrt(h["H2"][-1]))
    s6["mb_and_memory"] = {"A": seg_mesh(RUN_A), "A2": seg_mesh(RUN_A2)}
    ok = all(abs(s6[f"finder{n}"]["drift_per_M_65_95"] or 1) < 1e-4 for n in (0, 1)) and \
        s6["heavy_hole_change"] < 1e-3 and s6["rms_H_max"] < 1e-4
    s6["verdict"] = "MET (to the last record)" if ok else "REFUTED (to the last record)"
    s6["note"] = ("failed searches found by the failure signature; drifts on accepted searches with hrms <= 1e-2; "
                  "the capture at 137.5 M changes the heavy hole by about 0.11 (not in heavy_hole_change)")
    res["S6"] = s6

    # --- S7: end state at the last common tracker time (batch 35) ---------------------------
    tN, XN, VN = nr.common_times(joined, keys=[0, 1, 2])
    s7 = {}
    for tq in (186.0, 200.0, float(tN[-1])):
        k = int(np.argmin(np.abs(tN - tq)))
        if abs(tN[k] - tq) > 0.01:
            continue
        r = XN[k, 1] - XN[k, 2]
        v = VN[k, 1] - VN[k, 2]
        dist = float(np.linalg.norm(r))
        s7[f"t={tN[k]:.4f}"] = {"d_m2_M": dist, "v_rel": float(np.linalg.norm(v)),
                                "v_rel_radial": float(np.dot(r, v) / dist), "v_m2": float(np.linalg.norm(VN[k, 1])),
                                "v_M": float(np.linalg.norm(VN[k, 2])), "d_m1_M": float(np.linalg.norm(XN[k, 0] - XN[k, 2]))}
    k186 = tN >= 186.0
    if k186.sum() > 2:
        dd = np.linalg.norm(XN[k186, 1] - XN[k186, 2], axis=1)
        s7["d_m2_M_monotonic_after_186"] = bool(np.all(np.diff(dd) > -1e-9))
    for n in (1, 2):
        d, _ = hz[n]
        j = int(np.argmax(d["t"]))
        s7[f"finder{n}_last"] = {"t": float(d["t"][j]), "mass": float(d["mass"][j]), "S": float(d["S"][j]),
                                 "chi": float(d["S"][j] / d["mass"][j] ** 2), "hrms": float(d["hrms"][j]),
                                 "hmean": float(d["hmean"][j])}
        aft = d["t"] > 186.001
        if aft.any():
            s7[f"finder{n}_after_186"] = {"n": int(aft.sum()), "mass_min": float(d["mass"][aft].min()),
                                          "mass_max": float(d["mass"][aft].max()),
                                          "chi_min": float((d["S"][aft] / d["mass"][aft] ** 2).min()),
                                          "chi_max": float((d["S"][aft] / d["mass"][aft] ** 2).max()),
                                          "hrms_min": float(d["hrms"][aft].min()), "hrms_max": float(d["hrms"][aft].max())}
    for n in (0, 1, 2):
        fl, am = status_rows(os.path.join(RUN_A2, f"hills.horizon_status_{n}.txt"), 186.001)
        s7[f"status{n}_after_186"] = {"rows": int(len(fl)), "found": int(fl.sum()) if len(fl) else 0,
                                      "area_mass_min": float(am[fl == 1].min()) if (fl == 1).any() else None,
                                      "area_mass_max": float(am[fl == 1].max()) if (fl == 1).any() else None}
    kh = h["time"] > 186.001 if "time" in h else np.zeros(0, bool)
    s7["rms_H_max_after_186"] = float(np.sqrt(h["H2"][kh]).max()) if kh.any() else None
    s7["n_hst_after_186"] = int(kh.sum())
    res["S7"] = s7
    t_last = float(joined[0]["t"][-1])
    res["t_last_record"] = t_last
    res["label"] = (f"COMPLETE: A + A2 to tlim, last record {t_last:.3f} M (chain STATUS DONE)" if st == "DONE" else
                    f"ENDED at {t_last:.3f} M (chain STATUS {st}; tlim 200 M not reached)" if st in ("FAILED", "STOPPED") else
                    f"IN PROGRESS: last record {t_last:.3f} M (chain STATUS {st})")

    with open(os.path.join(o.out, "b21_a2_state.json"), "w") as f:
        json.dump(res, f, indent=1)

    # --- figure ------------------------------------------------------------------------------
    fs.use_style()
    fig, axs = plt.subplots(4, 1, figsize=(6.6, 9.6))
    ax = axs[0]
    for n, col in zip((0, 1, 2), (fs.PAL["red"], fs.PAL["orange"], fs.PAL["blue"])):
        for j, sp in enumerate(trk["A2"][n]["spans"]):
            ax.plot([sp[1], sp[2]], [j + 0.25 * n] * 2, color=col, lw=2.2,
                    label=f"tracker {n}" if j == 0 else None)
    ax.set_ylabel("tracker copy (write order)")
    ax.set_title(f"A2 {res['label'].split(':')[0].split(' (')[0]} ({res['t_last_record']:.1f} M, chain {st}): "
                 "time span of each kept tracker copy and the live file", fontsize=8)
    ax.legend(fontsize=6, loc="upper left")
    ax = axs[1]
    for n, col in zip((0, 1, 2), (fs.PAL["red"], fs.PAL["orange"], fs.PAL["blue"])):
        for name, mk in (("A", "s"), ("A2", "o")):
            ov = trk[name][n]["overlaps"]
            if ov:
                ax.semilogy([v["t_from"] for v in ov], [max(v["max_dx"], 1e-17) for v in ov], mk, color=col, ms=4,
                            label=f"{name}, tracker {n}")
    ax.axhline(1e-5, color="0.5", lw=0.8, ls="--")
    ax.axhline(1e-3, color="k", lw=0.8, ls=":")
    ax.set_ylabel(r"max $|\Delta x|$ at common cycles [$M$]")
    ax.set_xlabel(r"start of the recomputed stretch [$M$]")
    ax.legend(fontsize=6, ncol=3)
    t_end_plot = float(max(t[-1], tc[-1]))  # batch 25: axes to the last record, not a fixed 120 M
    ax = axs[2]
    ax.plot(t, s, color=fs.PAL["red"], lw=1.0, label="NR m/16, A + A2 joined")
    ax.add_patch(plt.Rectangle((63, 2.0), 12, 0.7, color=fs.PAL["blue"], alpha=0.15, label="A2-1 band"))
    ax.axvline(61.8, color="0.5", lw=0.6, ls=":")
    ax.plot([tmin], [smin], "v", color="k", ms=5)
    ax.set_ylabel(r"separation $s$ [$M$]")
    ax.legend(fontsize=7)
    ax = axs[3]
    ax.plot(tc, dcm, color=fs.PAL["red"], lw=1.3, label="centre of mass of the pair to M")
    ax.plot(tc, d0, color=fs.PAL["orange"], lw=0.8, label="m1 to M")
    ax.plot(tc, d1, color=fs.PAL["yellow"], lw=0.8, label="m2 to M")
    ax.axhspan(8, 11, color=fs.PAL["blue"], alpha=0.12, label="A2-2: closest approach 8-11 M at 95-115 M")
    ax.axvspan(95, 115, color=fs.PAL["blue"], alpha=0.06)
    ax.axvline(61.8, color="0.5", lw=0.6, ls=":")
    ax.set_ylabel(r"distance to $M$ [$M$]")
    ax.set_xlabel(r"$t$ [$M$]")
    ax.set_xlim(0, max(120.0, float(np.ceil(t_end_plot))))
    ax.legend(fontsize=6)
    for a in axs[2:]:
        a.set_xlim(0, max(120.0, float(np.ceil(t_end_plot))))
    fig.tight_layout()
    fs.save(fig, os.path.join(o.out, "fig_b21_a2_state"))
    short = {k: res[k] for k in ("label", "S1", "S2", "S4", "S5", "S7")}
    short["S3"] = {k: v for k, v in res["S3"].items() if k in ("verdict", "hst", "rpsi4_40")}
    short["S6"] = res["S6"]
    print(json.dumps(short, indent=1)[:6000])


if __name__ == "__main__":
    main()
