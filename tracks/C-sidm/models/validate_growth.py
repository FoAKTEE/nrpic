#!/usr/bin/env python3
"""Validation of the growth-rate and collapse-time pipeline (growth.py) on synthetic signals
and on the first paper's cluster runs (JOURNAL.md, predictions G1-G6).

    python3 validate_growth.py [--out DIR] [--runs /data/haiyangw/nrpic/runs/st]

The runs are read-only outputs of the main checkout (runs/ is untracked there). Published
numbers: paper/sections/tables/tab_outcomes.tex (commit 250fd9b), rows quoted with line
numbers in PUBLISHED below. Writes DIR/growth_validation.json and DIR/growth_figdata.npz.
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

TAB = "paper/sections/tables/tab_outcomes.tex"
# (quantity, run, printed value, format, line of TAB)
PUBLISHED = [
    ("first apparent horizon t/M", "yc0605_v5", "191.0", "{:.1f}", 120),
    ("first apparent horizon t/M", "yc0500_v5", "104.3", "{:.1f}", 120),
    ("M_AH/M at the end", "yc0605_v5", "1.0000", "{:.4f}", 121),
    ("M_AH/M at the end", "yc0500_v5", "1.0001", "{:.4f}", 121),
    ("macroparticles left of 10^4", "yc0605_v5", "6", "{:d}", 121),
    ("macroparticles left of 10^4", "yc0500_v5", "3", "{:d}", 121),
    ("alpha_c at the end", "yc0605_v5", "0.051", "{:.3f}", 122),
    ("alpha_c at the end", "yc0500_v5", "0.016", "{:.3f}", 122),
    ("alpha_c(0), compressed by ten percent", "reconf_yc0756_hc", "0.749", "{:.3f}", 144),
    ("first apparent horizon t/M, compressed", "reconf_yc0756_hc", "147.2", "{:.1f}", 144),
    ("M_AH/M at the end, compressed", "reconf_yc0756_hc", "0.9970", "{:.4f}", 145),
    ("macroparticles left, compressed", "reconf_yc0756_hc", "0", "{:d}", 145),
    ("first upward crossing of alpha_c = 0.8, plain filter", "dir_yc0500_plain", "59", "{:.0f}", 138),
    ("first upward crossing of alpha_c = 0.8, compensated sample 1", "dir_yc0500_comp", "88", "{:.0f}", 138),
    ("first upward crossing of alpha_c = 0.8, compensated sample 2", "dir_yc0500_comp_s2", "86", "{:.0f}", 138),
    ("first upward crossing of alpha_c = 0.8, compensated sample 3", "dir_yc0500_comp_s3", "91", "{:.0f}", 138),
    ("half-swing growth per M, sample 1", "ctl/s1_nf4c", "1.3e-05", "{:.1e}", 110),
    ("half-swing growth per M, half the cell spacing", "osc/dx2b", "1.7e-05", "{:.1e}", 110),
]

UNPERT = ["dir_yc0500_comp", "dir_yc0500_comp_s2", "dir_yc0500_comp_s3", "dir_yc0500_plain"]
KICKED = ["yc0500_v5", "yc0605_v5", "reconf_yc0756_hc"]
DEFAULT = dict(width=10.0, lo=0.01, hi=0.1)          # unperturbed migration (alpha_c, r10)
COLLAPSE = dict(width=10.0, lo=0.02, hi=0.2)         # collapsing runs (alpha_c)
WIDTHS = (5.0, 10.0, 20.0)
WINDOWS = ((0.003, 0.03), (0.005, 0.05), (0.01, 0.1))


def strip(fit):
    return {k: v for k, v in fit.items() if k != "curve"}


# ---------------------------------------------------------------------------- G2 synthetic
def synthetic(nreal=50, seed=7):
    rng = np.random.default_rng(seed)
    out, fig = {}, {}
    for sig in (0.02, 0.05, 0.1):
        dt = 0.25
        t = np.arange(0.0, np.log(300.0) / sig + 20.0, dt)
        fits = []
        for k in range(nreal):
            sgn = 1.0 if k % 2 == 0 else -1.0
            phase = rng.uniform(0, 2 * np.pi)
            y = sgn * (1e-3 * np.exp(sig * t) + 2e-3 * np.sin(2 * np.pi * t / 25.0 + phase)
                       + 1e-3 * rng.standard_normal(len(t)))
            f = gr.growth_fit(t, 0.6 + y, **DEFAULT)
            if k == 0:
                fig[f"syn_{sig:g}_t"], fig[f"syn_{sig:g}_d"] = t, y
                fig[f"syn_{sig:g}_ts"], fig[f"syn_{sig:g}_ds"] = f["curve"]["ts"], f["curve"]["ds"]
                fig[f"syn_{sig:g}_win"] = np.array([f["t_start"], f["t_end"], f["sigma"], f["amp0"]])
            fits.append(strip(f))
        s = np.array([f["sigma"] for f in fits])
        se = np.array([f["se"] for f in fits])
        snl = np.array([f["sigma_nl"] for f in fits], float)
        rel = s / sig - 1
        out[f"{sig:g}"] = dict(
            sigma_true=sig, n=nreal, mean_rel_bias=float(rel.mean()),
            rms_rel_err=float(np.sqrt(np.mean(rel ** 2))), max_abs_rel_err=float(np.abs(rel).max()),
            coverage_3se=float(np.mean(np.abs(s - sig) < 3 * se)),
            coverage_1se=float(np.mean(np.abs(s - sig) < se)),
            mean_rel_bias_nl=float(np.nanmean(snl / sig - 1)), median_efolds=float(np.median([f["efolds"] for f in fits])),
            pass_bias=bool(abs(rel.mean()) < 0.03), pass_coverage=bool(np.mean(np.abs(s - sig) < 3 * se) >= 0.9))
        fig[f"syn_{sig:g}_fits"] = s
        fig[f"syn_{sig:g}_se"] = se
        print(f"G2 sigma = {sig}: mean bias {rel.mean():+.4f}, rms {np.sqrt(np.mean(rel**2)):.4f}, "
              f"3SE coverage {out[f'{sig:g}']['coverage_3se']:.2f}; curve_fit estimator: mean bias "
              f"{out[f'{sig:g}']['mean_rel_bias_nl']:+.4f}", flush=True)
    return out, fig


# ---------------------------------------------------------------------------- G1 published
def published(runs):
    cache, out = {}, []
    for qty, key, printed, fmt, line in PUBLISHED:
        d = os.path.join(runs, key)
        if key not in cache:
            cache[key] = gr.load_run(d)
        run = cache[key]
        cs = gr.collapse_summary(run)
        if qty.startswith("first apparent horizon"):
            v = cs["t_AH_first"]
        elif qty.startswith("M_AH/M at the end"):
            v = cs["M_AH_last"]
        elif qty.startswith("macroparticles left"):
            v = cs["np_end"]
        elif qty.startswith("alpha_c at the end"):
            v = cs["alpha_end"]
        elif qty.startswith("alpha_c(0)"):
            v = cs["alpha_0"]
        elif qty.startswith("first upward crossing"):
            v = gr.first_crossing(run["t"], run["alpha"], 0.8, +1)
        elif qty.startswith("half-swing"):
            v = gr.swing_growth(run["t"], run["alpha"])["slope"]
        else:
            raise ValueError(qty)
        mine = fmt.format(v)
        if fmt.endswith("e}"):
            mine = f"{float(mine):.1e}"
        ok = mine == printed
        out.append(dict(quantity=qty, run=f"runs/st/{key}", printed=printed, ours=mine,
                        value=v, match=ok, locator=f"{TAB}:{line}"))
        print(f"G1 {key:22s} {qty:60s} printed {printed:>8s} ours {mine:>8s} "
              f"{'MATCH' if ok else 'DIFFER'}", flush=True)
    return out, cache


# ---------------------------------------------------------------------------- G3-G6 runs
def growth_runs(runs, cache):
    out, fig = {}, {}
    for key in UNPERT + KICKED:
        d = os.path.join(runs, key)
        run = cache.get(key) or gr.load_run(d)
        T, Rq = gr.mass_radii(d)
        par = DEFAULT if key in UNPERT else COLLAPSE
        fa = gr.growth_fit(run["t"], run["alpha"], **par)
        live = np.isfinite(Rq[:, 0])
        fr = gr.growth_fit(T[live], Rq[live, 0], relative=True, **par)
        ent = dict(alpha=strip(fa), r10=strip(fr), collapse=gr.collapse_summary(run),
                   params=par, snapshots=int(len(T)))
        if key in UNPERT:
            sens = []
            for w in WIDTHS:
                for lo, hi in WINDOWS:
                    f = gr.growth_fit(run["t"], run["alpha"], width=w, lo=lo, hi=hi)
                    sens.append(dict(width=w, lo=lo, hi=hi, sigma=f.get("sigma"), se=f.get("se"),
                                     ok=f["ok"], t_start=f.get("t_start"), t_end=f.get("t_end")))
            ent["sensitivity"] = sens
        out[key] = ent
        fig[f"{key}_t"], fig[f"{key}_alpha"] = run["t"], run["alpha"]
        fig[f"{key}_T"], fig[f"{key}_r10"], fig[f"{key}_r50"] = T, Rq[:, 0], Rq[:, 1]
        for lab, f in (("a", fa), ("r", fr)):
            if f["ok"]:
                fig[f"{key}_{lab}_ts"], fig[f"{key}_{lab}_ds"] = f["curve"]["ts"], f["curve"]["ds"]
                fig[f"{key}_{lab}_fit"] = np.array([f["t_start"], f["t_end"], f["sigma"], f["amp0"], f["sign"]])
        fig[f"{key}_ah"] = np.array([run["ah_t"], run["ah_M"]]) if len(run["ah_t"]) else np.zeros((2, 0))
        sa = f"{fa['sigma']:.4f} +- {fa['se']:.4f} [{fa['t_start']:.0f}, {fa['t_end']:.0f}]" if fa["ok"] else fa["reason"]
        sr = f"{fr['sigma']:.4f} +- {fr['se']:.4f} [{fr['t_start']:.0f}, {fr['t_end']:.0f}]" if fr["ok"] else fr["reason"]
        print(f"growth {key:22s} alpha: {sa}; r10: {sr}", flush=True)
    return out, fig


def verdicts(G, syn):
    v = {}
    v["G2"] = all(s["pass_bias"] and s["pass_coverage"] for s in syn.values())
    comp = [G[k]["alpha"]["sigma"] for k in UNPERT[:3]]
    m = float(np.mean(comp))
    v["G3_seeds"] = dict(sigmas=comp, mean=m, max_rel_dev=float(max(abs(c / m - 1) for c in comp)),
                         pass_=bool(max(abs(c / m - 1) for c in comp) < 0.15))
    pl = G["dir_yc0500_plain"]["alpha"]
    amp_c = float(np.mean([G[k]["alpha"]["amp0"] for k in UNPERT[:3]]))
    if pl["ok"]:
        v["G3_plain"] = dict(sigma_plain=pl["sigma"], rel_to_comp=pl["sigma"] / m - 1,
                             amp0_plain=pl["amp0"], amp0_comp_mean=amp_c, amp_ratio=pl["amp0"] / amp_c,
                             pass_=bool(abs(pl["sigma"] / m - 1) < 0.25 and pl["amp0"] / amp_c > 2))
    else:
        v["G3_plain"] = dict(evaluable=False, reason=pl["reason"], pass_=None)
    rr = {k: G[k]["r10"]["sigma"] / G[k]["alpha"]["sigma"] - 1 for k in UNPERT
          if G[k]["r10"]["ok"] and G[k]["alpha"]["ok"]}
    v["G4"] = dict(rel_r10_vs_alpha=rr, pass_=bool(len(rr) == 4 and max(abs(x) for x in rr.values()) < 0.2))
    s605, s500 = G["yc0605_v5"]["alpha"].get("sigma"), G["yc0500_v5"]["alpha"].get("sigma")
    dts = {k: (G[k]["collapse"]["t_alpha"]["0.2"], G[k]["collapse"]["t_AH_first"]) for k in KICKED}
    lead = {k: b - a for k, (a, b) in dts.items() if a is not None and b is not None}
    v["G5"] = dict(sigma_0605=s605, sigma_0500_kicked=s500, sigma_0500_unpert_mean=m,
                   order_pass=bool(s605 is not None and s500 is not None and s605 < s500),
                   kicked_vs_unpert_rel=(s500 / m - 1) if s500 else None,
                   kicked_vs_unpert_pass=bool(s500 is not None and abs(s500 / m - 1) < 0.3),
                   t_AH_minus_t_alpha02=lead,
                   lead_pass=bool(len(lead) == 3 and all(0 <= x <= 6 for x in lead.values())))
    sens = {}
    for k in UNPERT[:3]:
        if not G[k]["alpha"]["ok"]:
            continue
        ss = [s["sigma"] for s in G[k]["sensitivity"] if s["ok"]]
        base = G[k]["alpha"]["sigma"]
        sens[k] = dict(min=min(ss), max=max(ss), max_rel_dev=float(max(abs(x / base - 1) for x in ss)),
                       n_ok=len(ss), n=len(G[k]["sensitivity"]))
    v["G6"] = dict(per_run=sens, pass_=bool(all(s["max_rel_dev"] < 0.2 and s["n_ok"] == s["n"]
                                                 for s in sens.values())))
    return v


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--runs", default="/data/haiyangw/nrpic/runs/st")
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    syn, fig1 = synthetic()
    pub, cache = published(a.runs)
    G, fig2 = growth_runs(a.runs, cache)
    V = verdicts(G, syn)
    res = dict(runs_dir=a.runs, published_table=TAB, G1=pub,
               G1_pass=bool(all(p["match"] for p in pub)), G2=syn, growth=G, verdicts=V,
               settings=dict(default=DEFAULT, collapse=COLLAPSE, widths=WIDTHS, windows=WINDOWS))
    print(json.dumps(V, indent=1, default=float))
    with open(os.path.join(a.out, "growth_validation.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)
    fig = dict(fig1)
    fig.update(fig2)
    np.savez_compressed(os.path.join(a.out, "growth_figdata.npz"), **fig)
    return 0


if __name__ == "__main__":
    sys.exit(main())
