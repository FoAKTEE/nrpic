"""Figure: the first full-relativity evolution of the black hole in a vacuum bubble, against
its vacuum control (same table without dust, same mesh, slicing and length).

Reads the raw outputs of the two card runs es1 and v1 (horizon summaries, particle
histories with the lapse at the probes, tracer trajectories with the metric at the
particle; each file checked against the run's sha256sums.txt), the data run es2_data
(es/es.json: tracer groups), and the K-at-the-tracer series of the analysis run es_extra
(es_extra.json). The tracer reading (areal radius from the tangential metric at the
particle, the particle's own proper time) and the exact Lemaitre-Tolman-Bondi curves are
those of es_runs/analyse.py and einstein_straus/es_model.py, imported read-only; the
homogeneous 1+log model of the plateau lapse is es_runs/make_data.py:plateau_lapse_model.
Panels: (a) apparent-horizon mass minus M; (b) its drift from t0 = 100 M and the
difference of the two runs; (c) wall tracers, areal radius over the wall law minus one,
on the axes and the diagonals; (d) areal radius of the infalling tracer groups against
proper time with the exact curves; (e) lapse at the probe in the dust plateau against the
homogeneous 1+log model; (f) trace of the extrinsic curvature at the plateau tracer over
-3H. Numbers to fig_esrun_numbers.json.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common as C  # noqa: E402
import czstyle as cz  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

STEM = "fig_esrun"
T0 = 100.0          # reference time of the drift (es_runs JOURNAL entry 2, after the step near 30 M)
TLATE = 165.0       # start of the common late drift (entry 4)
WALL_R0 = 36.0
COL = {"bubble": cz.PAL["red"], "control": cz.PAL["blue"]}


def load_es_tools():
    sys.path.insert(0, os.path.join(C.TRACK, "es_runs"))
    import analyse as A  # noqa: E402
    import es_model as em  # noqa: E402
    from make_data import GEOM, VacuumBubble, plateau_lapse_model  # noqa: E402
    return A, em, GEOM, VacuumBubble, plateau_lapse_model


def drift_stats(S, t0):
    t, M = S["time"], S["mass"]
    M0 = float(np.interp(t0, t, M))
    s = t >= t0
    d = M[s] / M0 - 1.0
    w = (t[s] <= TLATE)
    return dict(M_t0=M0, level=M0 - 1.0, max_abs=float(np.max(np.abs(d))), end=float(d[-1]),
                t_end=float(t[-1]), window_100_165=[float(d[w].min()), float(d[w].max())],
                slope_per_M=float(np.polyfit(t[s], d, 1)[0])), (t[s], d)


def main():
    out = C.out_dir("figures")
    A, em, GEOM, VacuumBubble, plateau_lapse_model = load_es_tools()
    es_info = C.load_json("es2_data", "es/es.json")
    extra = C.load_json("es_extra", "es_extra.json")
    models = {"bubble": em.EinsteinStrausBH(**GEOM), "control": VacuumBubble(**GEOM)}
    runs = {"bubble": ("es1", "es"), "control": ("v1", "v1")}
    D = {}
    for name, (key, base) in runs.items():
        for f in ("horizon_summary_0.txt", "nrpic.hst", "traj.bin", "trajmet.bin"):
            C.run_file(key, f"{base}.{f}")          # sha256 against the run's record
        d = C.run_dir(key)
        S = A.read_horizon(os.path.join(d, f"{base}.horizon_summary_0.txt"))
        H = A.read_named_hst(os.path.join(d, f"{base}.nrpic.hst"))
        groups = A.exact_groups(models[name], es_info["tracers"])
        tr, per = A.analyse_tracers(d, base, models[name], groups)
        D[name] = dict(S=S, H=H, groups=groups, tr=tr, per=per)

    nums = {"t0": T0, "t_late": TLATE, "runs": {}}
    cz.use_style()
    fig, axs = plt.subplots(2, 3, figsize=(7.0, 4.7))
    fig.subplots_adjust(left=0.085, right=0.98, bottom=0.095, top=0.975, wspace=0.48, hspace=0.36)
    (a, b, c), (d_, e, f) = axs

    # (a) level, (b) drift
    series = {}
    for name in ("bubble", "control"):
        S = D[name]["S"]
        st, (ts, ds) = drift_stats(S, T0)
        series[name] = (ts, ds)
        nums["runs"][name] = dict(horizon=st)
        a.plot(S["time"], 1e3 * (S["mass"] - 1.0), color=COL[name], lw=0.9, label=name)
        b.plot(ts, 1e4 * ds, color=COL[name], lw=0.9)
    a.axhspan(1.2, 1.8, color="grey", alpha=0.18, lw=0)
    a.text(105, 1.62, "predicted level", fontsize=6.5, color="0.3")
    a.set_xlim(0, 200)
    a.set_ylim(0.7, 1.9)
    a.set_xlabel(r"$t/M$")
    a.set_ylabel(r"$(M_{\rm AH}-M)/M\ [10^{-3}]$")
    a.legend(frameon=False, loc="upper left", fontsize=6.5, handlelength=1.4, bbox_to_anchor=(0.0, 0.86))
    a.text(0.05, 0.88, "(a)", transform=a.transAxes)
    tb, tv = series["bubble"][0], series["control"][0]
    tc = np.intersect1d(np.round(tb, 9), np.round(tv, 9))
    diff = np.interp(tc, tb, series["bubble"][1]) - np.interp(tc, tv, series["control"][1])
    b.plot(tc, 1e4 * diff, color="k", lw=0.8, ls=":", label="difference")
    b.axhspan(-0.3, 0.3, color="grey", alpha=0.18, lw=0)
    b.axvspan(TLATE, 200, color=cz.PAL["yellow"], alpha=0.12, lw=0)
    b.text(168, -3.7, "late\ndrift", fontsize=6.5, color="0.3")
    b.set_xlim(T0, 200)
    b.set_ylim(-4, 1.6)
    b.set_xlabel(r"$t/M$")
    b.set_ylabel(r"$M_{\rm AH}(t)/M_{\rm AH}(t_0)-1\ [10^{-4}]$")
    b.legend(frameon=False, loc="lower left", fontsize=6.5, handlelength=1.4, bbox_to_anchor=(0.0, 0.1))
    b.text(0.05, 0.05, "(b)", transform=b.transAxes)
    nums["difference"] = dict(max_abs=float(np.max(np.abs(diff))),
                              over_control_floor=float(np.max(np.abs(diff)) / nums["runs"]["control"]["horizon"]["max_abs"]),
                              window_100_165=[float(diff[tc <= TLATE].min()), float(diff[tc <= TLATE].max())])
    # the two horizon masses before the dust can reach the black hole
    Sb, Sv = D["bubble"]["S"], D["control"]["S"]
    tcm = np.intersect1d(np.round(Sb["time"], 9), np.round(Sv["time"], 9))
    dm = np.interp(tcm, Sb["time"], Sb["mass"]) - np.interp(tcm, Sv["time"], Sv["mass"])
    early = tcm <= 20.0
    nums["difference"]["mass_bubble_minus_control_max_abs_t_le_20"] = float(np.max(np.abs(dm[early])))
    split = np.where(np.abs(dm) > 1e-9)[0]
    nums["difference"]["t_first_split_1e-9"] = float(tcm[split[0]]) if split.size else None
    w2 = (tcm >= 25.0) & (tcm <= 50.0)
    nums["difference"]["mass_bubble_minus_control_25_50"] = [float(dm[w2].min()), float(dm[w2].max())]

    # (c) wall tracers by direction class, (d) infalling groups
    for name, ls in (("bubble", "-"), ("control", "--")):
        g = [x for x in D[name]["groups"] if abs(x["R0"] - WALL_R0) < 1e-9][0]
        per = D[name]["per"]
        cls_max = {"axis": 0.0, "diagonal": 0.0}
        for tag in g["tags"]:
            p = per.get(tag)
            if p is None:
                continue
            n0 = np.abs(p["x"][0]) / np.linalg.norm(p["x"][0])
            cls = "axis" if np.max(n0) > 0.99 else "diagonal"
            s = p["tau"] <= 200.0
            cls_max[cls] = max(cls_max[cls], float(np.max(np.abs(p["rel"][s]))))
            c.plot(p["tau"], 1e3 * p["rel"], color=COL[name] if cls == "axis" else
                   (cz.PAL["orange"] if name == "bubble" else cz.PAL["green"]), lw=0.6, ls=ls)
        rec = [x for x in D[name]["tr"]["groups"] if abs(x["R0"] - WALL_R0) < 1e-9][0]
        nums["runs"][name]["wall"] = dict(max_abs_rel_tau_le_200=rec["max_abs_rel_tau<=200"],
                                          by_class_tau_le_200=cls_max, tau_end=rec["tau_end_range"])
        nums["runs"][name]["groups"] = [{k: x[k] for k in ("R0", "E", "max_abs_rel_tau<=200",
                                                            "tau_cross_2M_mean", "tau_cross_2M_spread",
                                                            "tau_cross_2M_exact", "tau_end_range")}
                                        | {"tau_cross_2M_range": [min(v for v in x["tau_cross_2M"] if v is not None),
                                                                  max(v for v in x["tau_cross_2M"] if v is not None)]
                                           if any(v is not None for v in x["tau_cross_2M"]) else None,
                                           "t_cross_2M_mean": float(np.mean([v for v in x["t_cross_2M"] if v is not None]))
                                           if any(v is not None for v in x["t_cross_2M"]) else None}
                                        for x in D[name]["tr"]["groups"]]
    c.axhspan(-3, 3, color="grey", alpha=0.15, lw=0)
    c.axvline(200, color="grey", lw=0.8, ls=":")
    for lab, col, ls in (("bubble, axes", COL["bubble"], "-"), ("bubble, diagonals", cz.PAL["orange"], "-"),
                         ("control, axes", COL["control"], "--"), ("control, diagonals", cz.PAL["green"], "--")):
        c.plot([], [], color=col, ls=ls, lw=0.9, label=lab)
    c.set_xlim(0, 290)
    c.set_ylim(-8, 20)
    c.set_xlabel(r"proper time $\tau/M$")
    c.set_ylabel(r"$R/R_w(\tau)-1\ [10^{-3}]$")
    c.legend(frameon=False, loc="upper left", fontsize=6.0, handlelength=1.6, bbox_to_anchor=(0.0, 0.9))
    c.text(0.05, 0.88, "(c)", transform=c.transAxes)

    per = D["bubble"]["per"]
    tex = np.linspace(0, 290, 2901)
    gcols = {6.0: cz.PAL["red"], 10.0: cz.PAL["yellow"], 20.0: cz.PAL["blue"]}
    for g in D["bubble"]["groups"]:
        if g["R0"] not in gcols:
            continue
        col = gcols[g["R0"]]
        for tag in g["tags"]:
            p = per.get(tag)
            if p is not None:
                d_.plot(p["tau"], p["R"], color=col, lw=0.6, alpha=0.7)
        Rex = em.ltb_radius(np.full_like(tex, g["R0"]), tex, g["m"], g["E"])
        ok = Rex >= 2.0
        d_.plot(tex[ok], Rex[ok], color="k", lw=0.9, ls="--")
        rec = [x for x in D["bubble"]["tr"]["groups"] if x["R0"] == g["R0"]][0]
        if rec["tau_cross_2M_exact"] is not None:
            d_.plot(rec["tau_cross_2M_exact"], 2.0, "o", ms=3.5, mfc="none", mec="k", mew=0.8)
        d_.text(rec["tau_cross_2M_exact"] + 4 if g["R0"] != 20.0 else 222, g["R0"] + 1.2 if g["R0"] != 20.0 else 18.0,
                rf"$R_0={g['R0']:g}M$", fontsize=6.5, color=col)
    d_.axhline(2.0, color="grey", lw=0.8, ls=":")
    d_.plot([], [], color="k", lw=0.9, ls="--", label="exact")
    d_.set_xlim(0, 290)
    d_.set_ylim(0, 30)
    d_.set_xlabel(r"proper time $\tau/M$")
    d_.set_ylabel(r"areal radius $R/M$")
    d_.legend(frameon=False, loc="center", fontsize=6.5, handlelength=1.6, bbox_to_anchor=(0.45, 0.35))
    d_.text(0.05, 0.88, "(d)", transform=d_.transAxes)

    # (e) lapse at the plateau probe (x = 46 M) and the homogeneous 1+log model
    tm, taum, am, alm = plateau_lapse_model(models["bubble"].H, t_end=200.0, n=20001)
    e.plot(tm, alm, **cz.GUIDE, label=r"$1+6\ln a$")
    lap = {}
    for name in ("bubble", "control"):
        H = D[name]["H"]
        e.plot(H["time"], H["alpha_probe"], color=COL[name], lw=0.9, label=name)
        lap[name] = {f"t={T:g}": float(np.interp(T, H["time"], H["alpha_probe"])) for T in (10, 25, 50, 100, 150, 200)}
        lap[name]["alpha_min_mesh_range"] = [float(np.min(H["alpha_min"])), float(np.max(H["alpha_min"]))]
        lap[name]["alpha_max_after_10"] = float(np.max(H["alpha_max"][H["time"] >= 10.0]))
        lap[name]["n_excised_last"] = int(H["n_excised"][-1])
        lap[name]["sum_m_first_last"] = [float(H["sum_m"][0]), float(H["sum_m"][-1])]
    nums["lapse_probe_46M"] = lap
    nums["plateau_model"] = {f"t={T:g}": float(np.interp(T, tm, alm)) for T in (10, 25, 50, 100, 150, 200)}
    nums["plateau_model_tau_at_200"] = float(np.interp(200.0, tm, taum))
    e.set_xlim(0, 200)
    e.set_ylim(0.8, 5.0)
    e.set_xlabel(r"$t/M$")
    e.set_ylabel(r"lapse $\alpha$ in the dust")
    e.legend(frameon=False, loc="center right", fontsize=6.5, handlelength=1.6)
    e.text(0.05, 0.88, "(e)", transform=e.transAxes)

    # (f) K at the plateau tracer over -3H
    ks = extra["runs"]["ES-1"]["K_at_plateau_tracer"]["R0=48"]
    tk = np.array([x["t"] for x in ks])
    kr = np.array([x["K_over_minus3H"] for x in ks])
    f.plot(tk, kr, "o-", ms=2.8, color=COL["bubble"], lw=0.9)
    f.axhline(1.0, **cz.GUIDE)
    f.axhline(0.0, color="grey", lw=0.8, ls=":")
    f.text(60, 1.07, "comoving slicing", fontsize=6.5, color="0.3")
    f.set_xlim(0, 200)
    f.set_ylim(-0.6, 1.25)
    f.set_xlabel(r"$t/M$")
    f.set_ylabel(r"$K/(-3H)$ at a plateau tracer")
    f.text(0.05, 0.88, "(f)", transform=f.transAxes)
    nums["K_over_minus3H_R0_48"] = {f"t={x['t']:g}": x["K_over_minus3H"] for x in ks}
    nums["dust_proper_time_R0_48_at_end"] = [x["tau_end_range"] for x in nums["runs"]["bubble"]["groups"] if x["R0"] == 48.0][0]
    cz.save(fig, os.path.join(out, STEM))
    with open(os.path.join(out, STEM + "_numbers.json"), "w") as fo:
        json.dump(nums, fo, indent=1, default=float)
    for name in ("bubble", "control"):
        h = nums["runs"][name]["horizon"]
        w = nums["runs"][name]["wall"]
        print(f"{STEM}: {name}: level {h['level']:.3e}, max|drift| {h['max_abs']:.3e}, 100-165 M "
              f"[{h['window_100_165'][0]:.2e}, {h['window_100_165'][1]:.2e}], wall {w['max_abs_rel_tau_le_200']:.3e}")
        for x in nums["runs"][name]["groups"][:3]:
            print(f"   R0 {x['R0']}: tau_cross {x['tau_cross_2M_range']} exact {x['tau_cross_2M_exact']}")
    print(f"{STEM}: difference max {nums['difference']['max_abs']:.3e} = "
          f"{nums['difference']['over_control_floor']:.2f} x control; lapse {lap['bubble']}; model {nums['plateau_model']}")
    C.report_checks(STEM)


if __name__ == "__main__":
    main()
