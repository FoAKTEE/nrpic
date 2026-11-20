#!/usr/bin/env python3
"""Validation of the fixed growth estimator growth.growth_fit_v2 beside the old growth_fit
(JOURNAL.md entry 9: predictions R1, G1'-G6').

    python3 validate_growth_v2.py [--out DIR] [--runs /data/haiyangw/nrpic/runs/st]

Old estimator: validate_growth.synthetic/published/growth_runs/verdicts, unchanged, compared
with results/growth_validation.json of run C-20261115-170346-298a1ba (regression).
New estimator (v2): the same synthetic signals (seed 7, same draw order); the first
paper's runs (read-only, runs/ of the main checkout) with the probe reference of each run.
Writes DIR/growth_validation_v2.json and DIR/growth_v2_figdata.npz.
"""

import argparse
import json
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

import growth as gr  # noqa: E402
import validate_growth as vg  # noqa: E402

OLD_JSON = os.path.join(HERE, "results", "growth_validation.json")
K_LO = 3.0
HI_UNPERT, HI_COLLAPSE, HI_R10 = 0.1, 0.2, 0.3
G6_HIS = (0.07, 0.1, 0.14)
TRUTH_REF = 0.6          # equilibrium value of the synthetic signals (validate_growth.synthetic)
P_TRUE = 25.0


def strip(f):
    return {k: v for k, v in f.items() if k != "curve"}


# ---------------------------------------------------------------------------- G2' synthetic
def synthetic_v2(nreal=50, seed=7):
    """The signals of validate_growth.synthetic, drawn in the same order."""
    rng = np.random.default_rng(seed)
    out, fig = {}, {}
    for sig in (0.02, 0.05, 0.1):
        dt = 0.25
        t = np.arange(0.0, np.log(300.0) / sig + 20.0, dt)
        rows = {"v2": [], "v2_first": []}
        for k in range(nreal):
            sgn = 1.0 if k % 2 == 0 else -1.0
            phase = rng.uniform(0, 2 * np.pi)
            y = sgn * (1e-3 * np.exp(sig * t) + 2e-3 * np.sin(2 * np.pi * t / 25.0 + phase)
                       + 1e-3 * rng.standard_normal(len(t)))
            f = gr.growth_fit_v2(t, TRUTH_REF + y, TRUTH_REF, k_lo=K_LO, hi=HI_UNPERT)
            g = gr.growth_fit_v2(t, TRUTH_REF + y, "first", k_lo=K_LO, hi=HI_UNPERT)
            rows["v2"].append(f)
            rows["v2_first"].append(g)
            if k == 0:
                fig[f"syn_{sig:g}_t"], fig[f"syn_{sig:g}_d"] = t, y
                if f["ok"]:
                    fig[f"syn_{sig:g}_v2_ts"], fig[f"syn_{sig:g}_v2_ds"] = f["curve"]["ts"], f["curve"]["ds"]
                    fig[f"syn_{sig:g}_v2_win"] = np.array([f["t_start"], f["t_end"], f["sigma"], f["amp0"],
                                                           f["period"], f["lo"]])
        out[f"{sig:g}"] = {}
        for name, fits in rows.items():
            ok = np.array([f["ok"] for f in fits])
            s = np.array([f["sigma"] if f["ok"] else np.nan for f in fits])
            se = np.array([f["se"] if f["ok"] else np.nan for f in fits])
            P = np.array([f.get("period", np.nan) for f in fits], float)
            rel = s[ok] / sig - 1
            cov3 = float(np.mean(np.abs(s[ok] - sig) < 3 * se[ok])) if ok.any() else None
            cov1 = float(np.mean(np.abs(s[ok] - sig) < se[ok])) if ok.any() else None
            ent = dict(sigma_true=sig, n=nreal, n_ok=int(ok.sum()),
                       mean_rel_bias=float(rel.mean()) if ok.any() else None,
                       sem_rel_bias=float(rel.std(ddof=1) / np.sqrt(len(rel))) if ok.sum() > 1 else None,
                       rms_rel_err=float(np.sqrt(np.mean(rel ** 2))) if ok.any() else None,
                       coverage_3se=cov3, coverage_1se=cov1,
                       median_period=float(np.nanmedian(P)), period_min=float(np.nanmin(P)),
                       period_max=float(np.nanmax(P)),
                       median_se_over_rms=float(np.median(se[ok] / sig) / np.sqrt(np.mean(rel ** 2))) if ok.any() else None,
                       median_A_init=float(np.median([f["A_init"] for f in fits if "A_init" in f])),
                       median_efolds=float(np.median([f["efolds"] for f in fits if f["ok"]])) if ok.any() else None)
            out[f"{sig:g}"][name] = ent
            fig[f"syn_{sig:g}_{name}_fits"] = s
            fig[f"syn_{sig:g}_{name}_se"] = se
            fig[f"syn_{sig:g}_{name}_P"] = P
            print(f"G2' sigma = {sig:<5g} {name:9s}: ok {ent['n_ok']}/{nreal}, mean bias "
                  f"{ent['mean_rel_bias']:+.4f} +- {ent['sem_rel_bias']:.4f}, rms {ent['rms_rel_err']:.4f}, "
                  f"3SE {cov3:.2f}, 1SE {cov1:.2f}, median P {ent['median_period']:.2f} "
                  f"[{ent['period_min']:.2f}, {ent['period_max']:.2f}]", flush=True)
        e = out[f"{sig:g}"]["v2"]
        e["pass"] = dict(bias=bool(abs(e["mean_rel_bias"]) <= 0.01), rms=bool(e["rms_rel_err"] < 0.02),
                         cov3=bool(e["coverage_3se"] >= 0.9), cov1=bool(0.5 <= e["coverage_1se"] <= 0.97),
                         period=bool(abs(e["median_period"] / P_TRUE - 1) < (0.05 if sig < 0.1 else 0.15)),
                         all_ok=bool(e["n_ok"] == nreal))
        e1 = out[f"{sig:g}"]["v2_first"]
        e1["pass_first"] = bool(e1["mean_rel_bias"] is not None and 0.01 <= e1["mean_rel_bias"] <= 0.06)
    return out, fig


# ---------------------------------------------------------------------------- R1, G3'-G6'
def runs_v2(runs, cache):
    out, fig = {}, {}
    for key in vg.UNPERT + vg.KICKED:
        d = os.path.join(runs, key)
        run = cache.get(key) or gr.load_run(d)
        t, a = run["t"], run["alpha"]
        pr = gr.run_probe_reference(d, alpha0=float(a[0]))
        ref = pr["alpha_ref"]
        hi = HI_UNPERT if key in vg.UNPERT else HI_COLLAPSE
        fa = gr.growth_fit_v2(t, a, ref, k_lo=K_LO, hi=hi)
        ff = gr.growth_fit_v2(t, a, "first", k_lo=K_LO, hi=hi)
        ent = dict(probe_reference=pr, alpha=strip(fa), alpha_first=strip(ff), hi=hi, k_lo=K_LO)
        print(f"R1 {key:22s} alpha_probe(0) {a[0]:.7f} table(r_p) {ref:.7f} (level {pr['level']}, "
              f"r_p {pr['r_p']:.4f}) diff {pr['probe_minus_ref']:+.2e}; alpha_c {pr['alpha_c']}", flush=True)
        if fa["ok"]:
            print(f"   v2 alpha: sigma {fa['sigma']:.4f} +- {fa['se']:.4f} (noise {fa['se_noise']:.4f}, fit "
                  f"{fa['se_fit']:.4f}) [{fa['t_start']:.1f}, {fa['t_end']:.1f}] P {fa['period']:.2f} "
                  f"({fa['period_fit']['trend']}, zc {fa['period_fit']['period_zero_crossings']}) "
                  f"A_init {fa['A_init']:.4g} lo {fa['lo']:.4g} efolds {fa['efolds']:.2f}", flush=True)
        else:
            print(f"   v2 alpha: no window: {fa['reason']}; P {fa.get('period')}", flush=True)
        fig[f"{key}_t"], fig[f"{key}_alpha"] = t, a
        fig[f"{key}_ref"] = np.array([ref, pr["alpha_c"] or np.nan])
        if fa["ok"]:
            fig[f"{key}_v2a_ts"], fig[f"{key}_v2a_ds"] = fa["curve"]["ts"], fa["curve"]["ds"]
            fig[f"{key}_v2a_fit"] = np.array([fa["t_start"], fa["t_end"], fa["sigma"], fa["amp0"], fa["sign"],
                                              fa["period"], fa["lo"], fa["hi"]])
        if key in vg.UNPERT:
            T, Rq = gr.mass_radii(d)
            live = np.isfinite(Rq[:, 0])
            T, r10 = T[live], Rq[live, 0]
            fig[f"{key}_T"], fig[f"{key}_r10"] = T, r10
            if fa.get("period"):
                fr = gr.growth_fit_v2(T, r10, "first", period=fa["period"], k_lo=K_LO, hi=HI_R10,
                                      relative=True)
                ent["r10_own"] = strip(fr)
                if fr["ok"]:
                    fig[f"{key}_v2r_ts"], fig[f"{key}_v2r_ds"] = fr["curve"]["ts"], fr["curve"]["ds"]
                    fig[f"{key}_v2r_fit"] = np.array([fr["t_start"], fr["t_end"], fr["sigma"], fr["amp0"],
                                                      fr["sign"]])
                if fa["ok"]:
                    fb = gr.slope_over(T, r10, "first", fa["period"], fa["t_start"], fa["t_end"], relative=True)
                    ent["r10_alpha_window"] = {kk: vv for kk, vv in fb.items() if not kk.startswith("curve")}
                    if fb["ok"]:
                        fig[f"{key}_v2rb_fit"] = np.array([fb["t_start"], fb["t_end"], fb["sigma"], fb["amp0"],
                                                           fb["sign"]])
                    if not fr["ok"] and "curve_ts" in fb:
                        fig[f"{key}_v2r_ts"], fig[f"{key}_v2r_ds"] = fb["curve_ts"], fb["curve_ds"]
                sr = (f"{fr['sigma']:.4f} +- {fr['se']:.4f} [{fr['t_start']:.1f}, {fr['t_end']:.1f}]"
                      if fr["ok"] else fr["reason"])
                rb = ent.get("r10_alpha_window", {})
                sb = (f"{rb['sigma']:.4f} +- {rb['se']:.4f}" if rb.get("ok") else rb.get("reason", "n/a"))
                print(f"   v2 r10 own window: {sr}; over the alpha window: {sb}", flush=True)
            if fa["ok"]:
                ent["G6"] = gr.window_grid(t, a, ref, fa["period"], G6_HIS, HI_UNPERT)
                fig[f"{key}_G6"] = np.array([[r["width_factor"], r["k_lo"], r["hi"],
                                              r["sigma"] if r["ok"] else np.nan] for r in ent["G6"]["rows"]])
                print(f"   G6': {ent['G6']['n_ok']}/{ent['G6']['n']} settings, range "
                      f"[{ent['G6'].get('min', np.nan):.4f}, {ent['G6'].get('max', np.nan):.4f}], "
                      f"max rel dev {ent['G6'].get('max_rel_dev', np.nan):.3f}", flush=True)
        out[key] = ent
    return out, fig


def verdicts_v2(syn, R, old_cmp, pub):
    v = {}
    v["G1"] = dict(n_match=int(sum(p["match"] for p in pub)), n=len(pub),
                   pass_=bool(all(p["match"] for p in pub)))
    v["old_regression"] = old_cmp
    v["G2"] = {s: e["v2"]["pass"] for s, e in syn.items()}
    v["G2"]["pass_"] = bool(all(all(p.values()) for p in v["G2"].values() if isinstance(p, dict)))
    v["G2_first"] = {s: e["v2_first"]["pass_first"] for s, e in syn.items()}
    stat = [k for k in vg.UNPERT if R[k]["probe_reference"]["refinement"] != "adaptive"]
    v["R1"] = dict(diffs={k: R[k]["probe_reference"]["probe_minus_ref"] for k in R},
                   levels={k: R[k]["probe_reference"]["level"] for k in R},
                   pass_static=bool(all(abs(R[k]["probe_reference"]["probe_minus_ref"]) < 1e-5 for k in stat)),
                   pass_adaptive=bool(all(abs(R[k]["probe_reference"]["probe_minus_ref"]) < 1e-5
                                          for k in ("yc0500_v5", "yc0605_v5"))))
    comp = vg.UNPERT[:3]
    old = {"dir_yc0500_comp": 0.0655, "dir_yc0500_comp_s2": 0.0606, "dir_yc0500_comp_s3": 0.0602}
    ok3 = all(R[k]["alpha"]["ok"] for k in comp)
    if ok3:
        s = {k: R[k]["alpha"]["sigma"] for k in comp}
        m = float(np.mean(list(s.values())))
        Ps = [R[k]["alpha"]["period"] for k in comp]
        v["G3"] = dict(sigmas=s, mean=m, max_rel_dev=float(max(abs(x / m - 1) for x in s.values())),
                       rel_to_old={k: s[k] / old[k] - 1 for k in comp}, periods=Ps,
                       pass_spread=bool(max(abs(x / m - 1) for x in s.values()) < 0.15),
                       pass_old=bool(all(abs(s[k] / old[k] - 1) < 0.15 for k in comp)),
                       pass_range=bool(all(0.050 <= x <= 0.075 for x in s.values())),
                       pass_period=bool(all(15 <= p <= 40 for p in Ps) and max(Ps) / min(Ps) - 1 < 0.2))
    else:
        v["G3"] = dict(evaluable=False, reasons={k: R[k]["alpha"].get("reason") for k in comp})
    g4a, g4b = {}, {}
    for k in comp:
        if not R[k]["alpha"]["ok"]:
            continue
        sa = R[k]["alpha"]["sigma"]
        if R[k].get("r10_own", {}).get("ok"):
            g4a[k] = R[k]["r10_own"]["sigma"] / sa - 1
        if R[k].get("r10_alpha_window", {}).get("ok"):
            g4b[k] = R[k]["r10_alpha_window"]["sigma"] / sa - 1
    v["G4"] = dict(own_window=g4a, alpha_window=g4b,
                   own_n_within_20=int(sum(abs(x) < 0.2 for x in g4a.values())), own_n=len(g4a),
                   alpha_window_n_within_20=int(sum(abs(x) < 0.2 for x in g4b.values())),
                   pred_a_holds=bool(len(g4a) < 3 or any(abs(x) >= 0.2 for x in g4a.values())),
                   pred_b_holds=bool(sum(abs(x) < 0.2 for x in g4b.values()) >= 2))
    s605, s500 = R["yc0605_v5"]["alpha"].get("sigma"), R["yc0500_v5"]["alpha"].get("sigma")
    se605, se500 = R["yc0605_v5"]["alpha"].get("se"), R["yc0500_v5"]["alpha"].get("se")
    m = v["G3"].get("mean")
    v["G5"] = dict(sigma_0605=s605, se_0605=se605, sigma_0500_kicked=s500, se_0500_kicked=se500,
                   sigma_0756_compressed=R["reconf_yc0756_hc"]["alpha"].get("sigma"),
                   order_pass=bool(s605 is not None and s500 is not None and s605 < s500),
                   order_beyond_errors=bool(s605 is not None and s500 is not None and se605 and se500
                                            and s500 - s605 > np.hypot(se605, se500)),
                   kicked_vs_unpert_rel=(s500 / m - 1) if (s500 and m) else None,
                   kicked_vs_unpert_pass=bool(s500 is not None and m is not None and abs(s500 / m - 1) < 0.3))
    g6 = {}
    for k in comp:
        G = R[k].get("G6")
        if G and "max_rel_dev" in G:
            g6[k] = dict(n_ok=G["n_ok"], n=G["n"], min=G["min"], max=G["max"], max_rel_dev=G["max_rel_dev"],
                         half_range=G["half_range"])
    v["G6"] = dict(per_run=g6, pass_dev=bool(len(g6) == 3 and all(x["max_rel_dev"] < 0.2 for x in g6.values())),
                   pass_count=bool(len(g6) == 3 and all(x["n_ok"] >= 24 for x in g6.values())))
    return v


def old_regression(syn_old, pub_old, G_old):
    """The old estimator against the stored result of run C-20261115-170346-298a1ba."""
    ref = json.load(open(OLD_JSON))
    diffs = {}
    for s, e in syn_old.items():
        r = ref["G2"][s]
        diffs[f"G2_{s}"] = dict(bias=e["mean_rel_bias"] - r["mean_rel_bias"],
                                cov3=e["coverage_3se"] - r["coverage_3se"])
    for k, e in G_old.items():
        r = ref["growth"][k]["alpha"]
        if e["alpha"]["ok"] and r["ok"]:
            diffs[f"alpha_{k}"] = e["alpha"]["sigma"] - r["sigma"]
    worst = max(abs(x) if not isinstance(x, dict) else max(abs(y) for y in x.values()) for x in diffs.values())
    same_pub = [p["ours"] for p in pub_old] == [p["ours"] for p in ref["G1"]]
    return dict(diffs=diffs, worst_abs=float(worst), identical=bool(worst == 0.0 and same_pub),
                G1_identical=bool(same_pub))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--runs", default="/data/haiyangw/nrpic/runs/st")
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    print("=== old estimator (growth_fit), unchanged", flush=True)
    syn_old, fig_old = vg.synthetic()
    pub, cache = vg.published(a.runs)
    G_old, fig_old2 = vg.growth_runs(a.runs, cache)
    V_old = vg.verdicts(G_old, syn_old)
    cmp_ = old_regression(syn_old, pub, G_old)
    print(f"old estimator against run C-20261115-170346-298a1ba: worst difference {cmp_['worst_abs']:.3g}, "
          f"identical {cmp_['identical']}", flush=True)
    print("=== new estimator (growth_fit_v2)", flush=True)
    syn, fig1 = synthetic_v2()
    R, fig2 = runs_v2(a.runs, cache)
    V = verdicts_v2(syn, R, cmp_, pub)
    res = dict(runs_dir=a.runs, settings=dict(k_lo=K_LO, hi_unpert=HI_UNPERT, hi_collapse=HI_COLLAPSE,
                                              hi_r10=HI_R10, g6_his=G6_HIS, g6_widths=gr.GRID_WIDTHS,
                                              g6_klo=gr.GRID_KLO),
               old=dict(G2=syn_old, growth={k: {kk: vv for kk, vv in e.items()} for k, e in G_old.items()},
                        verdicts=V_old),
               G1=pub, G2=syn, runs=R, verdicts=V)
    print(json.dumps(V, indent=1, default=float))
    with open(os.path.join(a.out, "growth_validation_v2.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)
    fig = {f"old_{k}": v for k, v in fig_old.items()}
    fig.update({f"old_{k}": v for k, v in fig_old2.items()})
    fig.update(fig1)
    fig.update(fig2)
    np.savez_compressed(os.path.join(a.out, "growth_v2_figdata.npz"), **fig)
    return 0


if __name__ == "__main__":
    sys.exit(main())
