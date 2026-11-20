#!/usr/bin/env python3
"""T10 of the work package cosmo-amr: analysis of the scouting run of Track A's
above-threshold case S1 (mu = 0.3) with adaptive refinement toward the peak, against the
track's own run with four static levels (prediction: tracks/core/JOURNAL-cosmo-amr.md,
entries of T10 and T10b).  Nothing is run here.

    t10_scout.py --run CASEDIR --s1 S1_CASEDIR --out DIR [--more CASEDIR ...]

CASEDIR holds peak.nrpic.hst, peak.cstat.hst, peak.region.hst, the finder status file(s),
athena.log, tab/ and, after a guard stop, peak.guard.txt.  --more: continuations of the
run (restarts) whose records are appended for the figure and summarised separately.
Writes DIR/t10_summary.json, DIR/fig_t10_scout.{pdf,png}, DIR/fig_t10_lines.{pdf,png}."""
import argparse
import glob
import json
import os
import re
import sys

import numpy as np

import amrlib as A

DX_ROOT = 20.0/64.0


def read_status(path):
    """finder status file: rows of 15 numbers, the reason in words after '#'"""
    rows = []
    if not os.path.exists(path):
        return np.zeros((0, 15))
    with open(path) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            rows.append([float(x) for x in line.split("#")[0].split()])
    return np.array(rows) if rows else np.zeros((0, 15))


def read_log(path):
    out = {"refine": [], "elapsed": []}
    with open(path) as f:
        for line in f:
            if line.startswith("NRPIC refine:"):
                w = line.split()
                # cycle, time, blocks, flagged up, flagged down, max ppc, lapse, chi ratio
                out["refine"].append([float(w[3]), float(w[5]), float(w[7]),
                                      float(w[9]), float(w[10]), float(w[15]),
                                      float(w[19]), float(w[23])])
            elif line.startswith("elapsed="):
                m = re.findall(r"=([0-9.eE+-]+)", line)
                out["elapsed"].append([float(x) for x in m[:4]])
            elif line.startswith("# exit="):
                out["exit"] = int(line.split("exit=")[1].split()[0])
                m = re.search(r"gpu_mem_peak_MiB=(\d+)", line)
                out["gpu_mem_peak_MiB"] = int(m.group(1)) if m else None
            elif "MeshBlocks created" in line:
                out["amr_line"] = line.strip()
            elif line.startswith("Terminating"):
                out["terminating"] = line.strip()
            elif line.startswith("time=") and "cycle=" in line:
                out["end"] = line.strip()
    out["refine"] = np.array(out["refine"]) if out["refine"] else np.zeros((0, 8))
    out["elapsed"] = np.array(out["elapsed"]) if out["elapsed"] else np.zeros((0, 4))
    return out


def line(rd, name, n):
    p = os.path.join(rd, "tab", f"peak.{name}.{n:05d}.tab")
    if not os.path.exists(p):
        return None, None
    d, t = A.read_tab(p)
    o = np.argsort(d["x1v"] if "x1v" in d else d[[k for k in d if k.endswith("v")][0]])
    return {k: v[o] for k, v in d.items()}, t


def ntab(rd, name="z4c"):
    return len(glob.glob(os.path.join(rd, "tab", f"peak.{name}.*.tab")))


def summarise(rd):
    h = A.read_hst(os.path.join(rd, "peak.nrpic.hst"))
    s = A.read_hst(os.path.join(rd, "peak.cstat.hst"))
    lg = read_log(os.path.join(rd, "athena.log"))
    r = {"records": int(len(h["time"])), "t_end": float(h["time"][-1]),
         "cycle_end": int(h["ncycle"][-1]), "exit": lg.get("exit"),
         "terminating": lg.get("terminating"), "end": lg.get("end"),
         "amr": lg.get("amr_line"), "gpu_mem_peak_MiB": lg.get("gpu_mem_peak_MiB")}
    if len(lg["elapsed"]):
        r["wall_s_last_report"] = float(lg["elapsed"][-1, 0])
        r["cycle_last_report"] = int(lg["elapsed"][-1, 1])
    fin = np.isfinite(h["alpha_min"]) & np.isfinite(h["E_max"])
    r["last_finite_time"] = float(h["time"][fin][-1])
    r["np_first_last"] = [int(h["np"][0]), int(h["np"][-1])]
    r["sum_m_change_while_all_particles"] = float(np.max(np.abs(
        h["sum_m"][h["np"] == h["np"][0]]/h["sum_m"][0] - 1.0)))
    ok = fin & (h["np"] == h["np"][0])
    r["identity_max_while_all_particles"] = float(np.max(np.abs(
        h["int_E"][ok]/h["sum_mW"][ok] - 1.0)))
    # MeshBlock counts: times at which the count changes
    nmb = h["nmb"].astype(int)
    ch = np.where(np.diff(nmb) != 0)[0] + 1
    r["nmb_changes"] = [[float(h["time"][i]), int(h["ncycle"][i]), int(nmb[i-1]),
                         int(nmb[i])] for i in ch]
    r["nmb_max"] = int(nmb.max())
    r["Hr_max_t0"] = float(s["Hr_max"][0])
    r["H_max_t0"] = float(s["H_max"][0])
    for tq in (2.0, 5.0, 7.0, 9.0, 10.0, 10.5, 11.0, 11.5):
        if tq <= h["time"][fin][-1]:
            i = int(np.argmin(np.abs(h["time"] - tq)))
            j = int(np.argmin(np.abs(s["time"] - tq)))
            r[f"t{tq:g}"] = {"alpha_min_over_max": float(h["alpha_min"][i]/h["alpha_max"][i]),
                             "E_max_over_min": float(h["E_max"][i]/h["E_min"][i])
                             if h["E_min"][i] > 0 else None,
                             "E_min": float(h["E_min"][i]),
                             "Hr_max": float(s["Hr_max"][j]),
                             "chi_min_over_max": float(s["chi_min"][j]/s["chi_max"][j]),
                             "nmb": int(nmb[i]), "wall_s": None}
            if len(lg["elapsed"]):
                k = int(np.argmin(np.abs(lg["elapsed"][:, 2] - tq)))
                r[f"t{tq:g}"]["wall_s"] = float(lg["elapsed"][k, 0])
    sf = np.isfinite(s["chi_min"])
    r["last_cstat"] = {"time": float(s["time"][sf][-1]), "chi_min": float(s["chi_min"][sf][-1]),
                       "chi_max": float(s["chi_max"][sf][-1]),
                       "K_max": float(s["K_max"][sf][-1]), "E_max": float(s["E_max"][sf][-1]),
                       "Hr_max": float(s["Hr_max"][sf][-1]),
                       "Theta_max": float(s["Theta_max"][sf][-1])}
    r["E_min_smallest"] = float(np.nanmin(h["E_min"][fin]))
    i = int(np.where(fin)[0][-1])
    r["last_finite"] = {"time": float(h["time"][i]), "dt_prev": float(h["time"][i] - h["time"][i-1]),
                        "alpha_min": float(h["alpha_min"][i]),
                        "alpha_max": float(h["alpha_max"][i]),
                        "E_max": float(h["E_max"][i]), "E_min": float(h["E_min"][i])}
    gp = os.path.join(rd, "peak.guard.txt")
    if os.path.exists(gp):
        with open(gp) as f:
            r["guard"] = [x for x in f.read().splitlines() if x.strip()][:40]
    # finder
    fnd = {}
    for p in sorted(glob.glob(os.path.join(rd, "peak.horizon_status_*.txt"))):
        st = read_status(p)
        k = os.path.basename(p).split("_")[-1].split(".")[0]
        f = {"searches": int(len(st))}
        if len(st):
            f["reasons"] = {str(int(q)): int(np.sum(st[:, 3] == q)) for q in np.unique(st[:, 3])}
            f["found"] = int(np.sum(st[:, 2] > 0))
            f["flow_iterations_min_max"] = [int(st[:, 4].min()), int(st[:, 4].max())]
            f["first_time"], f["last_time"] = float(st[0, 1]), float(st[-1, 1])
            f["mean_expansion_integral_first_last"] = [float(st[0, 9]), float(st[-1, 9])]
            f["area_first_last"] = [float(st[0, 5]), float(st[-1, 5])]
            f["mean_radius_last"] = float(st[-1, 7])
            f["points_outside_mesh_max"] = int(st[:, 11].max())
            if f["found"]:
                g = st[st[:, 2] > 0]
                f["first_found"] = {"cycle": int(g[0, 0]), "time": float(g[0, 1]),
                                    "area_mass": float(g[0, 6]), "mean_radius": float(g[0, 7]),
                                    "min_radius": float(g[0, 8])}
                f["last_found"] = {"cycle": int(g[-1, 0]), "time": float(g[-1, 1]),
                                   "area_mass": float(g[-1, 6]), "mean_radius": float(g[-1, 7]),
                                   "min_radius": float(g[-1, 8])}
        fnd[k] = f
    r["finder"] = fnd
    # finest cell on the x line of the last table: level reached
    n = ntab(rd)
    lv = []
    for q in range(n):
        d, t = line(rd, "z4c", q)
        if d is None:
            continue
        dx = np.min(np.diff(d["x1v"]))
        lv.append([float(t), int(round(np.log2(DX_ROOT/dx)))])
    r["finest_level_on_x_line"] = lv
    return r, h, s, lg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--s1", required=True)
    ap.add_argument("--more", nargs="*", default=[])
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    a = ap.parse_args()
    a.out = os.path.abspath(a.out)
    os.makedirs(a.out, exist_ok=True)
    res = {}
    r, h, s, lg = summarise(a.run)
    res["run"] = r
    r1, h1, s1, lg1 = summarise(a.s1)
    res["s1_static"] = r1
    more = []
    for i, rd in enumerate(a.more):
        rm, hm, sm, lgm = summarise(rd)
        res[f"more{i}"] = dict(rm, dir=rd)
        more.append((rd, hm, sm, lgm))
    g = A.read_hst(os.path.join(a.run, "peak.region.hst"))
    # relative constraint norms inside and outside the two spheres
    reg = {}
    for k in ("s1", "s2"):
        with np.errstate(divide="ignore", invalid="ignore"):
            reg[k] = (g["time"], g[f"H2_in_{k}"]/g[f"E2_in_{k}"],
                      g[f"H2_out_{k}"]/g[f"E2_out_{k}"])
        for tq in (0.0, 5.0, 9.0, 10.0, 11.0):
            if tq <= g["time"][-1]:
                i = int(np.argmin(np.abs(g["time"] - tq)))
                res["run"].setdefault("region", {})[f"{k}_t{tq:g}"] = {
                    "radius": float(g[f"radius_{k}"][i]),
                    "H2_over_E2_in": float(reg[k][1][i]),
                    "H2_over_E2_out": float(reg[k][2][i])}
    with open(os.path.join(a.out, "t10_summary.json"), "w") as f:
        json.dump(res, f, indent=1)
        f.write("\n")
    for k in ("t_end", "cycle_end", "exit", "terminating", "nmb_max", "Hr_max_t0",
              "last_finite", "gpu_mem_peak_MiB", "wall_s_last_report"):
        print(k, r.get(k))
    print("nmb changes", r["nmb_changes"])
    print("finder", json.dumps(r["finder"]))
    for q in r.get("guard", [])[:8]:
        print("guard:", q[:200])

    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    cb, cr, cg = fs.PAL["blue"], fs.PAL["red"], fs.PAL["green"]
    fig, ax = plt.subplots(2, 3, figsize=(10.0, 6.0))
    fig.subplots_adjust(left=0.07, right=0.94, bottom=0.09, top=0.95, wspace=0.36,
                        hspace=0.30)
    runs = [("adaptive (this run)", h, s, cb, "-"), ("four static levels (S1)", h1, s1, cr, "--")]
    for i, (rd, hm, sm, lgm) in enumerate(more):
        runs.append((f"continuation {i+1}", hm, sm, cg, ":"))
    for lab, hh, ss, c, st in runs:
        fin = np.isfinite(hh["alpha_min"]) & (hh["alpha_max"] > 0)
        ax[0, 0].semilogy(hh["time"][fin], hh["alpha_min"][fin]/hh["alpha_max"][fin], st,
                          color=c, label=lab)
        ok = fin & (hh["E_min"] > 0)
        ax[0, 1].semilogy(hh["time"][ok], hh["E_max"][ok]/hh["E_min"][ok], st, color=c,
                          label=lab)
        sf = np.isfinite(ss["Hr_max"]) & (ss["Hr_max"] > 0)
        ax[0, 2].semilogy(ss["time"][sf], ss["Hr_max"][sf], st, color=c, label=lab)
    for thr in (0.9, 0.7, 0.55, 0.4):
        ax[0, 0].axhline(thr, color="grey", lw=0.5, ls=":")
    ax[0, 0].set_ylabel(r"$\alpha_{\min}/\alpha_{\max}$")
    ax[0, 0].legend(frameon=False, fontsize=8, loc="lower left")
    ax[0, 1].set_ylabel(r"$E_{\max}/E_{\min}$")
    ax[0, 2].set_ylabel(r"largest relative $|H|$")
    for k, c in (("s1", cb), ("s2", cg)):
        t, rin, rout = reg[k]
        ok = np.isfinite(rin) & (rin > 0)
        ax[1, 0].semilogy(t[ok], rin[ok], "-", color=c,
                          label=f"inside r = {g['radius_'+k][0]:.2f}")
        ok = np.isfinite(rout) & (rout > 0)
        ax[1, 0].semilogy(t[ok], rout[ok], "--", color=c, label="outside")
    ax[1, 0].set_ylabel(r"$\|H\|_2/\|16\pi E\|_2$ (region norms)")
    ax[1, 0].legend(frameon=False, fontsize=7, ncol=2)
    ax[1, 1].plot(h["time"], h["nmb"], "-", color=cb, label="adaptive")
    ax[1, 1].plot(h1["time"], h1["nmb"], "--", color=cr, label="static (S1)")
    for i, (rd, hm, sm, lgm) in enumerate(more):
        ax[1, 1].plot(hm["time"], hm["nmb"], ":", color=cg)
    ax[1, 1].set_ylabel("MeshBlocks")
    ax[1, 1].legend(frameon=False, fontsize=8, loc="upper left")
    dt = np.diff(h["time"])
    ok = dt > 0
    ax[1, 2].semilogy(h["time"][1:][ok], dt[ok], "-", color=cb, label="adaptive")
    dt1 = np.diff(h1["time"])
    ok = (dt1 > 0) & np.isfinite(dt1)
    ax[1, 2].semilogy(h1["time"][1:][ok], dt1[ok], "--", color=cr, label="static (S1)")
    ax[1, 2].set_ylim(1e-4, 0.2)
    ax[1, 2].set_ylabel("step")
    ax[1, 2].legend(frameon=False, fontsize=8)
    tmax = max(h["time"][np.isfinite(h["alpha_min"])][-1], 12.0)
    for q in ax.flat:
        q.set_xlabel("conformal time")
        q.set_xlim(0, tmax*1.02)
    fs.save(fig, os.path.join(a.out, "fig_t10_scout"))
    plt.close(fig)

    # ---- lines through the peak at the last tables before the end
    n = ntab(a.run)
    sel = [q for q in (n-7, n-5, n-3, n-2, n-1) if q >= 0]
    fig, ax = plt.subplots(2, 3, figsize=(10.0, 6.0))
    fig.subplots_adjust(left=0.07, right=0.98, bottom=0.09, top=0.95, wspace=0.32,
                        hspace=0.30)
    cols = fs.series_colors(len(sel))
    for c, q in zip(cols, sel):
        z, t = line(a.run, "z4c", q)
        e, _ = line(a.run, "tmunu_E", q)
        cn, _ = line(a.run, "con", q)
        if z is None:
            continue
        fin = np.isfinite(z["z4c_alpha"])
        lab = f"t = {t:.2f}"
        for col in (0, 1):
            w = (np.abs(z["x1v"]) < (10.0 if col == 0 else 1.25)) & fin
            ax[0, col].semilogy(z["x1v"][w], np.abs(z["z4c_alpha"][w]), "-", color=c,
                                label=lab, marker="." if col else None, ms=2)
            if e is not None:
                we = (np.abs(e["x1v"]) < (10.0 if col == 0 else 1.25)) & (e["tmunu_E"] > 0)
                ax[1, col].semilogy(e["x1v"][we], e["tmunu_E"][we], "-", color=c, label=lab,
                                    marker="." if col else None, ms=2)
        w = (np.abs(z["x1v"]) < 1.25) & fin
        ax[0, 2].plot(z["x1v"][w], z["z4c_chi"][w]/np.nanmax(z["z4c_chi"][fin]), "-",
                      color=c, label=lab, marker=".", ms=2)
        if cn is not None:
            wc = (np.abs(cn["x1v"]) < 1.25) & np.isfinite(cn["con_H"]) & (cn["con_H"] != 0)
            ax[1, 2].semilogy(cn["x1v"][wc], np.abs(cn["con_H"][wc]), "-", color=c, label=lab,
                              marker=".", ms=2)
    ax[0, 0].set_ylabel(r"$\alpha$ on the $x$ line")
    ax[0, 1].set_ylabel(r"$\alpha$, centre")
    ax[0, 2].set_ylabel(r"$\chi/\chi_{\max}$, centre")
    ax[0, 2].axhline(0.0, color="grey", lw=0.5)
    ax[1, 0].set_ylabel(r"$E$ on the $x$ line")
    ax[1, 1].set_ylabel(r"$E$, centre")
    ax[1, 2].set_ylabel(r"$|H|$, centre")
    ax[0, 0].legend(frameon=False, fontsize=7)
    for q in ax.flat:
        q.set_xlabel(r"$x$")
    fs.save(fig, os.path.join(a.out, "fig_t10_lines"))
    plt.close(fig)
    return 0


if __name__ == "__main__":
    sys.exit(main())
