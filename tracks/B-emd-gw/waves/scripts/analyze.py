#!/usr/bin/env python3
"""Both diagnostics on every dump of tests F and X, errors against the exact solutions,
orders of convergence, figures.

    python3 analyze.py --flat 16=<run id>/N16,32=<run id>/N32,64=<run id>/flatN64 \
                       --exp 16=<run id>/N16,... [--nwork 8]

Reads scratch/B-emd-gw/<dir>/*.z4c.*.bin (double precision) for every N=<dir>; writes into
$NRPIC_RUN_DIR: results.json, per-dump tables (dumps_<test>_N<n>.json), figures (PNG, PDF);
copies results.json and the PNGs into ../results and ../figs.
"""
import argparse
import glob
import json
import os
import shutil
import sys
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from wlib import WT, PKG  # noqa: E402
from wlib import refs, measure, predict as pr  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

SCR = "/data/haiyangw/nrpic/scratch/B-emd-gw"
FLAT = dict(kvec=2 * np.pi * np.array([1.0, 1.0, 1.0]), L=(1.0, 1.0, 1.0),
            tlim=4.0 / np.sqrt(3.0), dt_out=1.0 / (8 * np.sqrt(3.0)),
            amp=1e-6, amp_x=5e-7, ph_x=1.0)
EXP = dict(kvec=2 * np.pi / 4.0 * np.array([1.0, 1.0, 0.0]), L=(4.0, 4.0, 4.0),
           tlim=10.0, dt_out=0.25, eps_p=2e-6, eps_x=1e-6, ph_x=1.0)
DIAGS = ("tt", "weyl6", "weylS")
LABEL = {"tt": "TT projection", "weyl6": "Weyl, FD order 6", "weylS": "Weyl, spectral"}


def exact_amplitudes(test, t):
    if test == "flat":
        c = FLAT
        return refs.flat_amplitudes(t, np.linalg.norm(c["kvec"]), c["amp"], c["amp_x"], c["ph_x"])
    c = EXP
    return refs.flrw_amplitudes(t, np.linalg.norm(c["kvec"]), c["eps_p"], c["eps_x"], 0.0, c["ph_x"])


def one_dump(args):
    test, path = args
    cfg = FLAT if test == "flat" else EXP
    d = measure.read_bin(path)
    m = measure.measure(d, cfg["kvec"])
    kn = np.linalg.norm(cfg["kvec"])
    t = m["time"]
    ex = refs.wave_measures(*exact_amplitudes(test, t), kn)
    rec = {"time": t, "cycle": m["cycle"], "a": m["a"], "alpha": m["alpha"], "calH": m["calH"],
           "max_beta": m["max_beta"], "nonTT_rel": m["nonTT_rel"],
           "tt_offmode_rel": m["tt_offmode_rel"], "psi4_field_rel": m["psi4_field_rel"],
           "nonTT_env": m["nonTT_env"], "tt_offmode_env": m["tt_offmode_env"], "env_rms": m["env_rms"],
           "psi4_rms": m["psi4_rms"], "vsize": d["vsize"]}
    amps = {"tt": m["tt"], "weyl6": m["weyl"]["6"], "weylS": m["weyl"]["spectral"]}
    for key, a4 in amps.items():
        ms = refs.wave_measures(*a4, kn)
        err = refs.compare(ms, ex)
        rec[key] = {k: float(v) for k, v in err.items()}
        rec[key]["Wf_p"] = [float(ms["Wf_p"].real), float(ms["Wf_p"].imag)]
        rec[key]["Wf_x"] = [float(ms["Wf_x"].real), float(ms["Wf_x"].imag)]
    for key in ("weyl6", "weylS"):
        mw = refs.wave_measures(*amps[key], kn)
        mt = refs.wave_measures(*amps["tt"], kn)
        rec[key]["vs_tt"] = float(max(abs(mw["Wf_p"] - mt["Wf_p"]) / abs(mt["Wf_p"]),
                                      abs(mw["Wf_x"] - mt["Wf_x"]) / abs(mt["Wf_x"])))
    rec["exact_Wf_p"] = [float(ex["Wf_p"].real), float(ex["Wf_p"].imag)]
    rec["exact_Wf_x"] = [float(ex["Wf_x"].real), float(ex["Wf_x"].imag)]
    return rec


def read_hst(rundir):
    fs_ = [f for f in glob.glob(os.path.join(rundir, "*.hst")) if ".z4c." in os.path.basename(f)]
    if not fs_:
        return None
    a = np.loadtxt(fs_[0], ndmin=2)
    with open(fs_[0]) as f:
        for line in f:
            if line.startswith("#") and "[1]" in line:
                names = [w.split("=")[1] for w in line[1:].split()]
                break
    return {n: a[:, i] for i, n in enumerate(names)}


def summarize(recs, key):
    """errors at the last dump and maxima over time for one diagnostic."""
    last = recs[-1][key]
    out = {}
    for q in ("amp_p", "phase_p", "amp_x", "phase_x", "pol_amp", "pol_phase", "back_p", "back_x"):
        out[q + "_end"] = last[q]
        out[q + "_max"] = float(max(abs(r[key][q]) for r in recs))
    if key != "tt":
        out["vs_tt_max"] = float(max(r[key]["vs_tt"] for r in recs))
        out["vs_tt_end"] = last["vs_tt"]
    return out


def orders(vals):
    return [float(np.log2(abs(vals[i] / vals[i + 1]))) if vals[i + 1] != 0 else None
            for i in range(len(vals) - 1)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--flat", required=True)
    ap.add_argument("--exp", required=True)
    ap.add_argument("--nwork", type=int, default=int(os.environ.get("NWORK", "8")))
    ap.add_argument("--tag", default="", help="prefix of the output names (e.g. ascan_)")
    ap.add_argument("--scale-flat", type=float, default=1.0, help="amplitude factor of test F")
    ap.add_argument("--scale-exp", type=float, default=1.0, help="amplitude factor of test X")
    ap.add_argument("--no-figures", action="store_true")
    a = ap.parse_args()
    for key in ("amp", "amp_x"):
        FLAT[key] *= a.scale_flat
    for key in ("eps_p", "eps_x"):
        EXP[key] *= a.scale_exp
    tag = a.tag
    out = os.environ.get("NRPIC_RUN_DIR", os.path.join(SCR, "tmp", "analyze"))
    os.makedirs(out, exist_ok=True)
    dirs = {}
    for test, spec in (("flat", a.flat), ("exp", a.exp)):
        dirs[test] = {int(kv.split("=")[0]): kv.split("=")[1] for kv in spec.split(",")}
    ns = sorted(dirs["flat"])
    assert ns == sorted(dirs["exp"])
    runs = dirs
    jobs, keys = [], []
    for test in ("flat", "exp"):
        for n in ns:
            files = sorted(glob.glob(os.path.join(SCR, dirs[test][n], "*.z4c.*.bin"))
                           + glob.glob(os.path.join(SCR, dirs[test][n], "bin", "*.z4c.*.bin")))
            jobs += [(test, f) for f in files]
            keys += [(test, n)] * len(files)
    with Pool(a.nwork) as pool:
        recs = pool.map(one_dump, jobs, chunksize=1)
    data = {}
    for (test, n), r in zip(keys, recs):
        data.setdefault(test, {}).setdefault(n, []).append(r)
    res = {"runs": runs, "ns": ns, "flat": {}, "exp": {}}
    for test in ("flat", "exp"):
        cfg = FLAT if test == "flat" else EXP
        fun = pr.predict_flat if test == "flat" else pr.predict_flrw
        for n in ns:
            recs_n = sorted(data[test][n], key=lambda r: r["time"])
            data[test][n] = recs_n
            with open(os.path.join(out, f"{tag}dumps_{test}_N{n}.json"), "w") as f:
                json.dump(recs_n, f, indent=1)
            p = fun(cfg["kvec"], cfg["L"], (n, n, n), cfg["tlim"], cfg["dt_out"])
            s = {k: summarize(recs_n, k) for k in DIAGS}
            s["pred_amp_end"] = float(np.abs(p["ratio"][-1]) - 1)
            s["pred_phase_end"] = float(np.angle(p["ratio"][-1]))
            s["t_end"] = recs_n[-1]["time"]
            s["n_dumps"] = len(recs_n)
            s["vsize"] = recs_n[0]["vsize"]
            s["t0"] = {k: {q: recs_n[0][k][q] for q in ("amp_p", "phase_p", "amp_x", "phase_x")}
                       for k in DIAGS}
            s["nonTT_rel_max"] = float(max(r["nonTT_rel"] for r in recs_n[1:]))
            s["tt_offmode_rel_max"] = float(max(r["tt_offmode_rel"] for r in recs_n[1:]))
            s["nonTT_env_max"] = float(max(r["nonTT_env"] for r in recs_n[1:]))
            s["nonTT_env_end"] = float(recs_n[-1]["nonTT_env"])
            s["tt_offmode_env_max"] = float(max(r["tt_offmode_env"] for r in recs_n[1:]))
            s["psi4_field_rel_max"] = float(max(r["psi4_field_rel"] for r in recs_n[1:]))
            s["max_beta"] = float(max(r["max_beta"] for r in recs_n))
            if test == "exp":
                t = np.array([r["time"] for r in recs_n])
                ae, He, _ = refs.background(t)
                s["a_rel_err_max"] = float(np.max(np.abs(np.array([r["a"] for r in recs_n]) / ae - 1)))
                s["calH_rel_err_max"] = float(np.max(np.abs(np.array([r["calH"] for r in recs_n]) / He - 1)))
                s["alpha_over_a_max"] = float(np.max(np.abs(np.array([r["alpha"] for r in recs_n]) / ae - 1)))
            h = read_hst(os.path.join(SCR, dirs[test][n]))
            if h is not None:
                s["H_norm2_max"] = float(np.max(h["H-norm2"]))
                s["M_norm2_max"] = float(np.max(h["M-norm2"]))
            res[test][str(n)] = s
        for k in DIAGS:
            for q in ("amp_p_end", "phase_p_end", "amp_x_end", "phase_x_end", "pol_amp_end", "pol_phase_end"):
                res[test].setdefault("orders", {}).setdefault(k, {})[q] = orders(
                    [res[test][str(n)][k][q] for n in ns])
        for k in ("weyl6", "weylS"):
            res[test]["orders"][k]["vs_tt_max"] = orders([res[test][str(n)][k]["vs_tt_max"] for n in ns])
    res["scale"] = {"flat": a.scale_flat, "exp": a.scale_exp}
    with open(os.path.join(out, f"{tag}results.json"), "w") as f:
        json.dump(res, f, indent=1)
    if not a.no_figures:
        figures(data, res, ns, out, tag)
    shutil.copy(os.path.join(out, f"{tag}results.json"), os.path.join(PKG, "results", f"{tag}results.json"))
    for png in glob.glob(os.path.join(out, "*.png")):
        shutil.copy(png, os.path.join(PKG, "figs", os.path.basename(png)))
    print(json.dumps({t: {n: {k: res[t][n][k] for k in ("tt", "weyl6")} for n in map(str, ns)}
                      for t in ("flat", "exp")}, indent=1)[:6000])


def figures(data, res, ns, out, tag=""):
    fs.use_style()
    cols = {16: fs.PAL["yellow"], 32: fs.PAL["red"], 64: fs.PAL["green"]}
    for test in ("flat", "exp"):
        cfg = FLAT if test == "flat" else EXP
        fun = pr.predict_flat if test == "flat" else pr.predict_flrw
        kn = np.linalg.norm(cfg["kvec"])
        fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 6.0))
        fig.subplots_adjust(left=0.1, right=0.98, bottom=0.08, top=0.95, wspace=0.3, hspace=0.3)
        # top left: the signal, N = 32
        n0 = 32 if 32 in ns else ns[-1]
        recs = data[test][n0]
        t = np.array([r["time"] for r in recs])
        tf = np.linspace(0, t[-1], 600)
        exf = refs.wave_measures(*exact_amplitudes(test, tf), kn)
        ax = axs[0, 0]
        if test == "flat":
            sc = cfg["amp"]
            ax.plot(tf, exf["Wf_p"].real / sc, color=fs.PAL["blue"], label="exact, Re W+")
            ax.plot(tf, exf["Wf_x"].real / sc, color=fs.PAL["blue"], ls="--", label="exact, Re Wx")
            ax.set_ylabel("W / amp")
        else:
            sc = cfg["eps_p"] / 2
            ax.plot(tf, exf["Wf_p"].real / sc, color=fs.PAL["blue"], label="exact T, + pol.")
            ax.plot(tf, exf["Wf_p"].imag / sc / 1, color=fs.PAL["blue"], ls="--", label="exact T'/|k|")
            ax.set_ylabel("W+ / (eps+/2)")
        ax.plot(t, [r["tt"]["Wf_p"][0] / sc for r in recs], "o", ms=3, color=fs.PAL["red"], label=f"TT, N = {n0}")
        ax.plot(t, [r["weyl6"]["Wf_p"][0] / sc for r in recs], "x", ms=4, color=fs.PAL["orange"], label="Weyl (FD 6)")
        if test == "flat":
            ax.plot(t, [r["tt"]["Wf_x"][0] / sc for r in recs], "o", ms=3, mfc="none", color=fs.PAL["red"])
        else:
            ax.plot(t, [r["tt"]["Wf_p"][1] / sc for r in recs], "o", ms=3, mfc="none", color=fs.PAL["red"])
        ax.set_xlabel("t", labelpad=-2)
        lo, hi = ax.get_ylim()
        ax.set_ylim(lo, hi + 0.45 * (hi - lo))
        ax.legend(loc="upper right", ncol=2, fontsize=7)
        # errors
        for n in ns:
            recs = data[test][n]
            t = np.array([r["time"] for r in recs])
            p = fun(cfg["kvec"], cfg["L"], (n, n, n), cfg["tlim"], cfg["dt_out"])
            c = cols.get(n, "k")
            for ax, q in ((axs[0, 1], "amp_p"), (axs[1, 0], "phase_p")):
                ax.semilogy(t[1:], [abs(r["tt"][q]) for r in recs[1:]], color=c, label=f"TT, N = {n}")
                ax.semilogy(t[1:], [abs(r["weyl6"][q]) for r in recs[1:]], color=c, ls="--",
                            label="Weyl FD6" if n == ns[0] else None)
                pv = np.abs(p["ratio"]) - 1 if q == "amp_p" else np.angle(p["ratio"])
                ax.semilogy(p["t"][1:], np.abs(pv[1:]), color="k", ls=":", lw=1.0,
                            label="symbol prediction" if n == ns[0] else None)
            ax = axs[1, 1]
            ax.semilogy(t[1:], [abs(r["tt"]["pol_amp"]) + 1e-18 for r in recs[1:]], color=c, label=f"|R| error, N = {n}")
            ax.semilogy(t[1:], [abs(r["tt"]["pol_phase"]) + 1e-18 for r in recs[1:]], color=c, ls="-.",
                        label="arg R error" if n == ns[0] else None)
            ax.semilogy(t[1:], [r["weyl6"]["vs_tt"] for r in recs[1:]], color=c, ls="--",
                        label="Weyl FD6 vs TT" if n == ns[0] else None)
            ax.semilogy(t[1:], [r["weylS"]["vs_tt"] for r in recs[1:]], color=c, ls=":",
                        label="Weyl spectral vs TT" if n == ns[0] else None)
        axs[0, 1].set_ylabel("|amplitude error|, + pol.")
        axs[1, 0].set_ylabel("|phase error| (rad), + pol.")
        axs[1, 1].set_ylabel("polarization ratio; Weyl vs TT")
        for ax in (axs[0, 1], axs[1, 0], axs[1, 1]):
            ax.set_xlabel("t", labelpad=-2)
            lo, hi = ax.get_ylim()
            ax.set_ylim(lo, hi * (hi / lo) ** 0.45)
            ax.legend(loc="upper center", ncol=2, fontsize=6.5)
        fig.savefig(os.path.join(out, f"{tag}{test}_errors.png"))
        fig.savefig(os.path.join(out, f"{tag}{test}_errors.pdf"))
        plt.close(fig)
    # convergence
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 4.0))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.14, top=0.9, wspace=0.28)
    nn = np.array(ns, float)
    for ax, test in zip(axs, ("flat", "exp")):
        r = res[test]
        for q, mk, lab in (("amp_p_end", "o", "amplitude"), ("phase_p_end", "s", "phase")):
            ax.loglog(nn, [abs(r[str(n)]["tt"][q]) for n in ns], marker=mk, color=fs.PAL["red"], label="TT " + lab)
            ax.loglog(nn, [abs(r[str(n)]["weyl6"][q]) for n in ns], marker=mk, mfc="none", ls="--",
                      color=fs.PAL["orange"], label="Weyl FD6 " + lab)
        ax.loglog(nn, [max(r[str(n)]["tt"]["pol_amp_max"], r[str(n)]["tt"]["pol_phase_max"]) for n in ns],
                  marker="D", color=fs.PAL["green"], label="TT polarization ratio (max)")
        ax.loglog(nn, [abs(r[str(n)]["pred_amp_end"]) for n in ns], "x", color="k", ms=7, label="prediction amp.")
        ax.loglog(nn, [abs(r[str(n)]["pred_phase_end"]) for n in ns], "+", color="k", ms=8, label="prediction phase")
        ax.loglog(nn, [r[str(n)]["weyl6"]["vs_tt_end"] for n in ns], marker="v", color=fs.PAL["blue"],
                  label="Weyl FD6 vs TT")
        y0 = abs(r[str(ns[0])]["tt"]["phase_p_end"])
        ax.loglog(nn, y0 * (nn / nn[0]) ** -4, **dict(fs.GUIDE, lw=1.0), label="N^-4")
        ax.loglog(nn, y0 * (nn / nn[0]) ** -6, color="k", ls="-.", lw=1.0, label="N^-6")
        ax.set_xlabel("N (cells per side)")
        ax.set_xticks(ns)
        ax.set_xticklabels([str(n) for n in ns])
        ax.minorticks_off()
        ax.set_title("flat, oblique" if test == "flat" else "expanding box")
        lo, hi = ax.get_ylim()
        ax.set_ylim(lo, hi * (hi / lo) ** 0.6)
        ax.legend(loc="upper right", ncol=2, fontsize=6)
    axs[0].set_ylabel("error at the last dump")
    fig.savefig(os.path.join(out, f"{tag}convergence.png"))
    fig.savefig(os.path.join(out, f"{tag}convergence.pdf"))
    plt.close(fig)


if __name__ == "__main__":
    main()
