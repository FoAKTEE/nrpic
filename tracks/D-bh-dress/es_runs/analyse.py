#!/usr/bin/env python3
"""Analysis of ES-1 and its vacuum control V-1 (AthenaK output), against the exact
Einstein-Straus references.

    analyse.py --es <ES-1 run dir> --v1 <V-1 run dir> --data <make_data run dir> [--out DIR]
               [--t0 100] [--tag NAME]

DIR defaults to $NRPIC_RUN_DIR. A run directory holds <base>.horizon_summary_0.txt,
<base>.nrpic.hst, <base>.traj.bin, <base>.trajmet.bin, bin/<base>.z4c.*.bin (base = es, v1);
partial runs are read as far as they go.

Measures (JOURNAL.md entry 2):
1. Apparent-horizon mass M_AH(t) of both runs, drift M_AH(t)/M_AH(t0) - 1 and the
   difference ES-1 minus V-1; floor statistics over [t0, t_end].
2. Every tracer: areal radius R = r sqrt(gamma_T) from the metric at the particle
   (gamma_T = (tr gamma - n.gamma.n)/2, the tangential component; exact for a spherically
   symmetric metric in Cartesian coordinates) against its proper time
   tau = int alpha/W dt, W = sqrt(1 + gamma^ij u_i u_j); compared with the exact LTB curve
   R(R0, tau) (es_model.ltb_radius with the group's m and E).
3. Times at which the inner groups reach R = 2M (interpolated), against the exact ones.
4. Lapse at the probes and its minimum on the mesh against coordinate time; lapse, chi
   and Khat along the x axis from the z = 0 slices.
Writes DIR/es_analysis.json and figures DIR/figs/*.png,pdf.
"""
import argparse
import glob
import json
import math
import os
import sys

sys.dont_write_bytecode = True
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "tracks", "D-bh-dress", "einstein_straus"))
sys.path.insert(0, os.path.join(WT, "python"))
sys.path.insert(0, os.path.join(WT, "athenak", "vis", "python"))
sys.path.insert(0, HERE)
import es_model as em  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402
from make_data import GEOM, VacuumBubble, plateau_lapse_model  # noqa: E402

NTR = 140
NDIR = 14
HZ_COLS = ["iter", "time", "mass", "Sx", "Sy", "Sz", "S", "area", "hrms", "hmean", "meanradius", "minradius"]
PROBE_X = {"probe0": 46.0, "probe1": 1.0, "probe2": 4.0, "probe3": 20.0, "probe4": 36.0, "probe5": 56.0,
           "probe6": 80.0, "probe7": 152.0}


# ------------------------------------------------------------------ readers
def read_horizon(path):
    if not os.path.exists(path):
        return None
    a = np.loadtxt(path, comments="#", ndmin=2)
    if a.size == 0:
        return None
    d = {k: a[:, i] for i, k in enumerate(HZ_COLS)}
    # one row per search time; a restart repeats the search of its cycle: keep the last
    t = d["time"]
    _, idx = np.unique(t[::-1], return_index=True)
    idx = len(t) - 1 - idx
    idx.sort()
    return {k: v[idx] for k, v in d.items()}


def read_named_hst(path):
    if not os.path.exists(path):
        return None
    names = None
    with open(path) as f:
        for line in f:
            if "[1]=" in line:
                names = [s.split("=", 1)[1] for s in line.split() if "=" in s and s.startswith("[")]
                break
    a = np.loadtxt(path, comments="#", ndmin=2)
    t = a[:, 0]
    _, idx = np.unique(t[::-1], return_index=True)     # restarts append: keep the last record
    idx = np.sort(len(t) - 1 - idx)
    return {n: a[idx, i] for i, n in enumerate(names[:a.shape[1]])}


def read_records(path, n):
    if not os.path.exists(path):
        return None
    a = np.fromfile(path, dtype=np.float64)
    a = a[: (len(a) // n) * n].reshape(-1, n)
    return a


def tracer_tracks(run, base):
    """{tag: dict(t, x[3], u[3], alpha, beta[3], g[6])}, records joined on (time, tag),
    duplicates from restarts removed (last kept)."""
    tr = read_records(os.path.join(run, f"{base}.traj.bin"), 8)
    # 17 doubles per record (nrpic_io.cpp:811-814; docs/FORMATS.md still says 12): time, tag,
    # alpha, beta^i, gamma_ij (xx xy xz yy yz zz), proper time of the particle, E, S_i
    tm = read_records(os.path.join(run, f"{base}.trajmet.bin"), 17)
    if tr is None or tm is None:
        return {}
    out = {}
    for tag in range(NTR):
        a = tr[tr[:, 1] == tag]
        b = tm[tm[:, 1] == tag]
        if len(a) == 0 or len(b) == 0:
            continue
        ta, ia = np.unique(a[::-1, 0], return_index=True)
        a = a[::-1][ia]
        tb, ib = np.unique(b[::-1, 0], return_index=True)
        b = b[::-1][ib]
        common, ja, jb = np.intersect1d(a[:, 0], b[:, 0], return_indices=True)
        a, b = a[ja], b[jb]
        out[tag] = dict(t=a[:, 0], x=a[:, 2:5], u=a[:, 5:8], alpha=b[:, 2], beta=b[:, 3:6], g=b[:, 6:12],
                        tau_code=b[:, 12], E=b[:, 13])
    return out


def areal_and_tau(d):
    gxx, gxy, gxz, gyy, gyz, gzz = d["g"].T
    x = d["x"]
    r = np.linalg.norm(x, axis=1)
    n = x / r[:, None]
    G = np.empty((len(r), 3, 3))
    G[:, 0, 0], G[:, 0, 1], G[:, 0, 2] = gxx, gxy, gxz
    G[:, 1, 0], G[:, 1, 1], G[:, 1, 2] = gxy, gyy, gyz
    G[:, 2, 0], G[:, 2, 1], G[:, 2, 2] = gxz, gyz, gzz
    tr = gxx + gyy + gzz
    gnn = np.einsum("ni,nij,nj->n", n, G, n)
    gT = 0.5 * (tr - gnn)
    R = r * np.sqrt(gT)
    Ginv = np.linalg.inv(G)
    uu = np.einsum("ni,nij,nj->n", d["u"], Ginv, d["u"])
    W = np.sqrt(1.0 + uu)
    rate = d["alpha"] / W
    tau_int = np.concatenate([[0.0], np.cumsum(0.5 * (rate[1:] + rate[:-1]) * np.diff(d["t"]))])
    if d["t"][0] > 0:
        tau_int += rate[0] * d["t"][0]
    # the particle's own proper time (accumulated by the pusher) is used; the trapezoid
    # integral of alpha/W over the records is the cross-check
    return R, d["tau_code"], gnn, gT, tau_int


def axis_profiles(run, base, var_list=("z4c_alpha", "z4c_chi", "z4c_Khat", "z4c_betax")):
    """Values along the positive x axis (cells next to y = 0 in the z = 0 slice), per output."""
    import bin_convert
    files = sorted(glob.glob(os.path.join(run, "bin", f"{base}.z4c.[0-9]*.bin")))
    out = []
    for p in files:
        try:
            fd = bin_convert.read_binary(p)
        except Exception as e:  # noqa: BLE001
            print("cannot read", p, e)
            continue
        rows = []
        nmb = (fd["nx1_mb"], fd["nx2_mb"], fd["nx3_mb"])
        for b in range(fd["n_mbs"]):
            g = fd["mb_geometry"][b]
            ix = fd["mb_index"][b]
            dxs = [(g[2 * k + 1] - g[2 * k]) / nmb[k] for k in range(3)]
            if not (g[2] < 0.0 + 1e-9 < g[3] + dxs[1] or g[2] <= -dxs[1] / 2 <= g[3]):
                pass
            q0 = np.asarray(fd["mb_data"][var_list[0]][b], dtype=float)
            n3, n2, n1 = q0.shape
            xc = g[0] + (ix[0] + np.arange(n1) + 0.5) * dxs[0]
            yc = g[2] + (ix[2] + np.arange(n2) + 0.5) * dxs[1]
            jsel = np.where(np.abs(np.abs(yc) - 0.5 * dxs[1]) < 1e-9 * max(1.0, dxs[1]))[0]
            if len(jsel) == 0:
                continue
            isel = np.where(xc > 0)[0]
            for j in jsel:
                vals = [np.asarray(fd["mb_data"][v][b], dtype=float)[0, j, isel] for v in var_list]
                for k, i in enumerate(isel):
                    rows.append([xc[i], dxs[0]] + [vv[k] for vv in vals])
        if not rows:
            continue
        a = np.array(rows)
        # finest cell at each x; average the two cells at y = +-dx/2
        a = a[np.lexsort((a[:, 0], a[:, 1]))]
        keep = {}
        for row in a:
            key = round(row[0], 9)
            if key not in keep or row[1] < keep[key][0][1] - 1e-12:
                keep[key] = [row]
            elif abs(row[1] - keep[key][0][1]) < 1e-12:
                keep[key].append(row)
        xs = np.array(sorted(keep))
        vals = np.array([np.mean(keep[k], axis=0) for k in sorted(keep)])
        # drop coarse cells whose x is covered by finer cells
        out.append(dict(time=float(fd["time"]), x=vals[:, 0], dx=vals[:, 1],
                        **{v: vals[:, 2 + i] for i, v in enumerate(var_list)}))
    return out


# ------------------------------------------------------------------ analysis
def exact_groups(model, info_tracers):
    groups = []
    for g in info_tracers:
        m, E = model.shell_energy(np.array([g["R0"]]))
        groups.append(dict(index=g["index"], R0=g["R0"], m=float(m[0]), E=float(E[0]), tags=list(range(g["tags"][0], g["tags"][1] + 1))))
    return groups


def crossing(tau, R, level=2.0):
    i = np.where(R <= level)[0]
    if len(i) == 0 or i[0] == 0:
        return None
    k = i[0]
    return float(tau[k - 1] + (level - R[k - 1]) * (tau[k] - tau[k - 1]) / (R[k] - R[k - 1]))


def analyse_tracers(run, base, model, groups):
    tracks = tracer_tracks(run, base)
    res = {"groups": []}
    per = {}
    for g in groups:
        rec = dict(index=g["index"], R0=g["R0"], m=g["m"], E=g["E"], n_tracks=0)
        rel_all, cross, tcross, tau_end, R0meas = [], [], [], [], []
        for tag in g["tags"]:
            if tag not in tracks:
                continue
            d = tracks[tag]
            R, tau, gnn, gT, tau_int = areal_and_tau(d)
            Rex = em.ltb_radius(np.full_like(tau, g["R0"]), tau, g["m"], g["E"])
            rel = R / Rex - 1.0
            per[tag] = dict(t=d["t"], tau=tau, R=R, Rex=Rex, rel=rel, alpha=d["alpha"], x=d["x"],
                            tau_int_diff=float(np.max(np.abs(tau_int - tau))) if len(tau) else 0.0)
            rec["n_tracks"] += 1
            ok = np.isfinite(rel) & (R > 2.2)
            rel_all.append(rel[ok])
            cross.append(crossing(tau, R))
            tcross.append(crossing(d["t"], R))
            tau_end.append(float(tau[-1]))
            R0meas.append(float(R[0]))
        if rec["n_tracks"]:
            rr = np.concatenate(rel_all) if rel_all else np.array([])
            rec["max_abs_rel"] = float(np.max(np.abs(rr))) if rr.size else None
            # windows in proper time
            for T in (200.0, 400.0, 800.0, 1e9):
                vals = []
                for tag in g["tags"]:
                    if tag in per:
                        p = per[tag]
                        s = (p["tau"] <= T) & np.isfinite(p["rel"]) & (p["R"] > 2.2)
                        if s.any():
                            vals.append(np.max(np.abs(p["rel"][s])))
                rec[f"max_abs_rel_tau<={T:g}"] = float(max(vals)) if vals else None
            rec["R_at_t0"] = [min(R0meas), max(R0meas)]
            rec["tau_cross_2M"] = cross
            rec["t_cross_2M"] = tcross
            cr = [c for c in cross if c is not None]
            rec["tau_cross_2M_mean"] = float(np.mean(cr)) if cr else None
            rec["tau_cross_2M_spread"] = float(np.ptp(cr)) if cr else None
            rec["tau_end_range"] = [min(tau_end), max(tau_end)]
            rec["tau_code_minus_integral_max"] = float(max(per[t]["tau_int_diff"] for t in g["tags"] if t in per))
            tex = np.linspace(0, 400, 40001)
            rec["tau_cross_2M_exact"] = crossing(tex, em.ltb_radius(np.full_like(tex, g["R0"]), tex, g["m"], g["E"]))
        res["groups"].append(rec)
    return res, per


def horizon_drift(S, t0):
    if S is None:
        return None
    t, M = S["time"], S["mass"]
    out = dict(t_first=float(t[0]), t_last=float(t[-1]), n=int(len(t)))
    if t[-1] < t0:
        out["note"] = f"run has not reached t0 = {t0}"
        return out
    M0 = float(np.interp(t0, t, M))
    s = t >= t0
    d = M[s] / M0 - 1.0
    out.update(M_t0=M0, offset_from_M=M0 - 1.0, max_abs_drift=float(np.max(np.abs(d))),
               end_drift=float(d[-1]), rms_drift=float(np.sqrt(np.mean(d * d))),
               slope_per_M=float(np.polyfit(t[s], d, 1)[0]) if s.sum() > 2 else None,
               chi_max=float(np.max(np.abs(S["S"][s] / M[s] ** 2))))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--es", required=True)
    ap.add_argument("--v1", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--t0", type=float, default=100.0)
    ap.add_argument("--no_profiles", action="store_true")
    a = ap.parse_args()
    os.makedirs(os.path.join(a.out, "figs"), exist_ok=True)
    es_info = json.load(open(os.path.join(a.data, "es", "es.json")))
    esm = em.EinsteinStrausBH(**GEOM)
    vm = VacuumBubble(**GEOM)
    runs = {"ES-1": (a.es, "es", esm), "V-1": (a.v1, "v1", vm)}
    res = {"t0": a.t0, "runs": {}}
    data = {}
    for name, (d, base, model) in runs.items():
        S = read_horizon(os.path.join(d, f"{base}.horizon_summary_0.txt"))
        H = read_named_hst(os.path.join(d, f"{base}.nrpic.hst"))
        groups = exact_groups(model, es_info["tracers"])
        tr, per = analyse_tracers(d, base, model, groups)
        prof = [] if a.no_profiles else axis_profiles(d, base)
        data[name] = dict(S=S, H=H, per=per, prof=prof, groups=groups)
        r = dict(dir=d, horizon=horizon_drift(S, a.t0), tracers=tr)
        if H is not None:
            r["hst"] = dict(t_last=float(H["time"][-1]), np_first=int(H["np"][0]), np_last=int(H["np"][-1]),
                            n_excised_last=int(H["n_excised"][-1]), n_escaped_last=int(H["n_escaped"][-1]),
                            sum_m_first=float(H["sum_m"][0]), sum_m_last=float(H["sum_m"][-1]),
                            alpha_min_range=[float(np.min(H["alpha_min"])), float(np.max(H["alpha_min"]))],
                            alpha_max_last=float(H["alpha_max"][-1]),
                            push_unconverged_max=int(np.max(H["push_unconverged"])),
                            finite=bool(np.all(np.isfinite(H["sum_mW"]))))
            probes = {}
            for k in ("alpha_probe",) + tuple(f"alpha_probe{i}" for i in range(1, 8)):
                if k in H:
                    key = "probe0" if k == "alpha_probe" else "probe" + k[-1]
                    probes[key] = {f"t={T:g}": float(np.interp(T, H["time"], H[k])) for T in (0, 10, 25, 50, 100, 150, 200)
                                   if T <= H["time"][-1]}
            r["lapse_probes"] = probes
        res["runs"][name] = r
    # difference of the horizon masses on common times
    Se, Sv = data["ES-1"]["S"], data["V-1"]["S"]
    if Se is not None and Sv is not None:
        tc = np.intersect1d(np.round(Se["time"], 9), np.round(Sv["time"], 9))
        if len(tc):
            Me = np.interp(tc, Se["time"], Se["mass"])
            Mv = np.interp(tc, Sv["time"], Sv["mass"])
            res["horizon_difference"] = dict(t_last=float(tc[-1]), at_t=[{"t": float(T), "ES-1 - V-1": float(np.interp(T, tc, Me - Mv))}
                                                                          for T in (10, 50, 100, 150, 200) if T <= tc[-1]])
            s = tc >= a.t0
            if s.sum() > 2:
                de = Me[s] / np.interp(a.t0, tc, Me) - 1.0
                dv = Mv[s] / np.interp(a.t0, tc, Mv) - 1.0
                res["horizon_difference"]["drift_difference_max_abs"] = float(np.max(np.abs(de - dv)))
                res["horizon_difference"]["drift_ES_max_abs"] = float(np.max(np.abs(de)))
                res["horizon_difference"]["drift_V1_max_abs"] = float(np.max(np.abs(dv)))
    t, tau_p, a_p, alp = plateau_lapse_model(esm.H, t_end=200.0, n=20001)
    res["plateau_model"] = {f"t={T:g}": float(np.interp(T, t, alp)) for T in (10, 25, 50, 100, 150, 200)}
    with open(os.path.join(a.out, "es_analysis.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)
    print(json.dumps(res, indent=1, default=float)[:12000])
    figures(a, data, res, (t, alp), esm, vm)


# ------------------------------------------------------------------ figures
def figures(a, data, res, plateau, esm, vm):
    fs.use_style()
    import matplotlib.pyplot as plt
    col = {"ES-1": fs.PAL["red"], "V-1": fs.PAL["blue"]}
    figs = os.path.join(a.out, "figs")

    # 1. horizon mass
    fig, axs = plt.subplots(3, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 7.2), sharex=True)
    fig.subplots_adjust(left=0.17, right=0.97, bottom=0.07, top=0.98, hspace=0.06)
    for name, d in data.items():
        S = d["S"]
        if S is None:
            continue
        axs[0].plot(S["time"], S["mass"] - 1.0, color=col[name], label=name)
        if S["time"][-1] >= a.t0:
            M0 = np.interp(a.t0, S["time"], S["mass"])
            s = S["time"] >= a.t0 - 50
            axs[1].plot(S["time"][s], S["mass"][s] / M0 - 1.0, color=col[name], label=name)
    Se, Sv = data["ES-1"]["S"], data["V-1"]["S"]
    if Se is not None and Sv is not None:
        tc = np.intersect1d(np.round(Se["time"], 9), np.round(Sv["time"], 9))
        if len(tc):
            axs[2].plot(tc, np.interp(tc, Se["time"], Se["mass"]) - np.interp(tc, Sv["time"], Sv["mass"]),
                        color=fs.PAL["yellow"])
    axs[0].set_ylabel(r"$M_{\rm AH}/M - 1$")
    axs[0].set_ylim(-0.01, 0.01)
    axs[0].legend(loc="lower right", ncol=2)
    axs[1].set_ylabel(r"$M_{\rm AH}(t)/M_{\rm AH}(%g\,M) - 1$" % a.t0)
    for y in (-3e-5, 3e-5):
        axs[1].axhline(y, **fs.GUIDE)
    axs[1].axvline(a.t0, **fs.MASK_LINE)
    axs[1].set_ylim(-3e-4, 3e-4)
    axs[1].text(0.02, 0.9, r"dashed: $\pm3\times10^{-5}$ (prediction 1)", transform=axs[1].transAxes, fontsize=8)
    axs[2].set_ylabel(r"$M_{\rm AH}^{\rm ES\text{-}1} - M_{\rm AH}^{\rm V\text{-}1}$")
    axs[2].set_xlabel(r"coordinate time $t/M$")
    fs.save(fig, os.path.join(figs, "horizon_mass"))
    plt.close(fig)

    # 2. wall and all tracer groups: R(tau) against exact; relative error
    fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 6.2), sharex="col",
                            gridspec_kw=dict(height_ratios=[2.2, 1]))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.08, top=0.97, hspace=0.05, wspace=0.27)
    for j, name in enumerate(("ES-1", "V-1")):
        d = data[name]
        ax, axr = axs[0, j], axs[1, j]
        cc = fs.series_colors(len(d["groups"]))
        for g, c in zip(d["groups"], cc):
            first = True
            for tag in g["tags"]:
                p = d["per"].get(tag)
                if p is None:
                    continue
                ax.plot(p["tau"], p["R"], color=c, lw=0.8, label=(f"$R_0={g['R0']:g}M$" if first else None))
                s = np.isfinite(p["rel"]) & (p["R"] > 2.2)
                axr.plot(p["tau"][s], p["rel"][s], color=c, lw=0.6)
                first = False
            tmax = max([d["per"][t]["tau"][-1] for t in g["tags"] if t in d["per"]] or [1.0])
            te = np.linspace(0, tmax, 600)
            ax.plot(te, em.ltb_radius(np.full_like(te, g["R0"]), te, g["m"], g["E"]), color="k", lw=0.8, ls="--")
        ax.axhline(2.0, **fs.MASK_LINE)
        ax.set_yscale("log")
        ax.set_ylabel(r"areal radius $R/M$")
        ax.text(0.03, 0.93, f"{name}; dashed: exact", transform=ax.transAxes)
        if j == 0:
            ax.legend(loc="lower right", ncol=2, fontsize=7)
        axr.axhline(0.01, **fs.GUIDE)
        axr.axhline(-0.01, **fs.GUIDE)
        axr.set_ylim(-0.03, 0.03)
        axr.set_xlabel(r"proper time of the tracer $\tau/M$")
        axr.set_ylabel(r"$R/R_{\rm exact} - 1$")
    fs.save(fig, os.path.join(figs, "tracers_all"))
    plt.close(fig)

    # 3. the wall (group 4, R0 = 36) zoomed: relative error against tau, both runs
    fig, ax = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 3.4))
    fig.subplots_adjust(left=0.16, right=0.97, bottom=0.14, top=0.97)
    for name in ("ES-1", "V-1"):
        d = data[name]
        g = [g for g in d["groups"] if abs(g["R0"] - 36.0) < 1e-9][0]
        first = True
        for tag in g["tags"]:
            p = d["per"].get(tag)
            if p is None:
                continue
            axis = np.count_nonzero(np.abs(p["x"][0]) > 1e-6) == 1
            ax.plot(p["tau"], p["rel"], color=col[name], lw=1.0 if axis else 0.6, ls="-" if axis else ":",
                    label=(name if first else None))
            first = False
    ax.axhline(3e-3, **fs.GUIDE)
    ax.axhline(-3e-3, **fs.GUIDE)
    ax.axvline(200.0, **fs.MASK_LINE)
    ax.set_xlabel(r"proper time of the wall tracer $\tau/M$")
    ax.set_ylabel(r"$R_{\rm wall}/R_{\rm exact} - 1$")
    ax.text(0.02, 0.04, r"solid: on axes, dotted: diagonals; dashed: $\pm3\times10^{-3}$", transform=ax.transAxes, fontsize=8)
    ax.legend(loc="upper left", ncol=2)
    fs.save(fig, os.path.join(figs, "wall"))
    plt.close(fig)

    # 4. lapse at the probes
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.6), sharey=True)
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.14, top=0.97, wspace=0.05)
    t, alp = plateau
    for j, name in enumerate(("ES-1", "V-1")):
        H = data[name]["H"]
        ax = axs[j]
        if H is None:
            continue
        keys = [("alpha_probe", "probe0")] + [(f"alpha_probe{i}", f"probe{i}") for i in range(1, 8)]
        cc = fs.series_colors(len(keys))
        for (k, pk), c in zip(keys, cc):
            if k in H:
                ax.plot(H["time"], H[k], color=c, label=f"$x={PROBE_X[pk]:g}M$")
        ax.plot(H["time"], H["alpha_min"], color="k", lw=1.0, label=r"min on mesh")
        if name == "ES-1":
            ax.plot(t, alp, **dict(fs.GUIDE, label=r"$1+6\ln a$ (plateau)"))
        ax.set_yscale("log")
        ax.set_xlabel(r"coordinate time $t/M$")
        ax.text(0.03, 0.93, name, transform=ax.transAxes)
        if j == 0:
            ax.set_ylabel(r"lapse $\alpha$")
            ax.legend(loc="lower right", ncol=2, fontsize=7)
    fs.save(fig, os.path.join(figs, "lapse_probes"))
    plt.close(fig)

    # 5. profiles along x
    if all(data[n]["prof"] for n in data):
        fig, axs = plt.subplots(3, 2, figsize=(fs.FULL_WIDTH, 7.6), sharex=True, sharey="row")
        fig.subplots_adjust(left=0.09, right=0.98, bottom=0.07, top=0.98, hspace=0.06, wspace=0.05)
        for j, name in enumerate(("ES-1", "V-1")):
            prof = data[name]["prof"]
            sel = [p for p in prof if any(abs(p["time"] - T) < 1e-6 for T in (0, 20, 50, 100, 150, 200))]
            cc = fs.series_colors(len(sel))
            for p, c in zip(sel, cc):
                axs[0, j].plot(p["x"], p["z4c_alpha"], color=c, label=f"t={p['time']:g}M")
                axs[1, j].plot(p["x"], p["z4c_chi"], color=c)
                axs[2, j].plot(p["x"], p["z4c_Khat"], color=c)
            axs[0, j].set_yscale("log")
            axs[1, j].set_yscale("log")
            axs[2, j].set_xscale("log")
            axs[2, j].set_xlabel(r"$x/M$ (along the x axis)")
            axs[0, j].text(0.03, 0.9, name, transform=axs[0, j].transAxes)
            for ax in axs[:, j]:
                for xx in (36.0, 60.0):
                    ax.axvline(xx, **fs.MASK_LINE)
        axs[0, 0].set_ylabel(r"$\alpha$")
        axs[1, 0].set_ylabel(r"$\chi$")
        axs[2, 0].set_ylabel(r"$\hat K$ ($M^{-1}$)")
        axs[0, 0].legend(loc="lower right", ncol=2, fontsize=7)
        fs.save(fig, os.path.join(figs, "axis_profiles"))
        plt.close(fig)


if __name__ == "__main__":
    main()
