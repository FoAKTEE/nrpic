#!/usr/bin/env python3
"""Analysis of wave 3, round 1 (JOURNAL.md 2026-11-20 22:30): both diagnostics on every dump,
errors against the exact solutions and against the predictions.

    analyze_r1.py --mode f120 --runs 16=<dir>,32=<dir>,48=<dir>,64=<dir>
        test F2, k = 2 pi (1,2,0): TT and Weyl (order 6, spectral) amplitudes, phase and
        polarization errors; mode coefficients at +k of Gamma^i, Theta, Khat and of the
        non-TT part of h, against the whole-Z4c symbol model (wlib/z4c_symbol.py).
    analyze_r1.py --mode xdt --runs 16=<dir>,... --dt-expansion 0.001 [--ref <final_results.json>]
        test X with a smaller expansion step: errors against the exact mode and against the
        2S prediction at that step; comparison with the reference runs (dt_expansion 0.01).

<dir> is relative to scratch/B-emd-gw (the run directory and the sub-directory of one
resolution). Writes into $NRPIC_RUN_DIR: <tag>results.json, <tag>dumps_N<n>.json, figures
(PNG, PDF); copies the JSON and the PNGs into ../results and ../figs.
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
from wlib import PKG  # noqa: E402
from wlib import refs, measure, predict as pr, z4c_symbol as zs  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

SCR = "/data/haiyangw/nrpic/scratch/B-emd-gw"
F120 = dict(kvec=2 * np.pi * np.array([1.0, 2.0, 0.0]), L=(1.0, 1.0, 1.0),
            tlim=4.0 / np.sqrt(5.0), dt_out=1.0 / (8 * np.sqrt(5.0)),
            amp=1e-6, amp_x=5e-7, ph_x=1.0, kappa1=0.02)
EXP = dict(kvec=2 * np.pi / 4.0 * np.array([1.0, 1.0, 0.0]), L=(4.0, 4.0, 4.0),
           tlim=10.0, dt_out=0.25, eps_p=2e-6, eps_x=1e-6, ph_x=1.0)
DIAGS = ("tt", "weyl6", "weylS")
CFG = {"mode": "f120"}


def exact(mode, t):
    if mode == "f120":
        c = F120
        return refs.flat_amplitudes(t, np.linalg.norm(c["kvec"]), c["amp"], c["amp_x"], c["ph_x"])
    c = EXP
    return refs.flrw_amplitudes(t, np.linalg.norm(c["kvec"]), c["eps_p"], c["eps_x"], 0.0, c["ph_x"])


def one_dump(args):
    mode, path = args
    cfg = F120 if mode == "f120" else EXP
    kv = cfg["kvec"]
    kn = float(np.linalg.norm(kv))
    d = measure.read_bin(path)
    m = measure.measure(d, kv)
    t = m["time"]
    ex = refs.wave_measures(*exact(mode, t), kn)
    rec = {k: m[k] for k in ("time", "cycle", "a", "alpha", "calH", "max_beta", "nonTT_rel",
                             "tt_offmode_rel", "psi4_field_rel", "nonTT_env", "env_rms")}
    amps = {"tt": m["tt"], "weyl6": m["weyl"]["6"], "weylS": m["weyl"]["spectral"]}
    mt = refs.wave_measures(*amps["tt"], kn)
    for key, a4 in amps.items():
        ms = refs.wave_measures(*a4, kn)
        err = refs.compare(ms, ex)
        rec[key] = {k: float(v) for k, v in err.items()}
        rec[key]["Wf_p"] = [float(ms["Wf_p"].real), float(ms["Wf_p"].imag)]
        rec[key]["Wf_x"] = [float(ms["Wf_x"].real), float(ms["Wf_x"].imag)]
        if key != "tt":
            rec[key]["vs_tt"] = float(max(abs(ms["Wf_p"] - mt["Wf_p"]) / abs(mt["Wf_p"]),
                                          abs(ms["Wf_x"] - mt["Wf_x"]) / abs(mt["Wf_x"])))
    rec["tt"]["P"] = [complex(v).real for v in amps["tt"]] + [complex(v).imag for v in amps["tt"]]
    # the sector the discrete divergence drives: mode coefficients at +k
    g = d["grid"]
    gam = np.array([refs.mode_coeff(d[n], g, kv) for n in ("Gamx", "Gamy", "Gamz")])
    rec["Gamma_k"] = [[float(v.real), float(v.imag)] for v in gam]
    rec["Theta_k"] = abs(complex(refs.mode_coeff(d["Theta"], g, kv)))
    rec["Khat_k"] = abs(complex(refs.mode_coeff(d["Khat"], g, kv)))
    names = {(0, 0): "gxx", (0, 1): "gxy", (0, 2): "gxz", (1, 1): "gyy", (1, 2): "gyz", (2, 2): "gzz"}
    C = np.empty((3, 3), complex)
    for (a, b), n in names.items():
        C[a, b] = C[b, a] = refs.mode_coeff(d[n], g, kv)
    Lam = zs.lambda_projector(kv / kn)
    CT = (Lam @ C.ravel()).reshape(3, 3)
    rec["nonTT_mode"] = float(np.linalg.norm(C - CT) / np.linalg.norm(CT))
    rec["exact_Wf_p"] = [float(ex["Wf_p"].real), float(ex["Wf_p"].imag)]
    return rec


def orders(vals, ns):
    return [float(np.log(abs(vals[i] / vals[i + 1])) / np.log(ns[i + 1] / ns[i]))
            if vals[i + 1] != 0 else None for i in range(len(vals) - 1)]


def summarize(recs, key):
    last = recs[-1][key]
    out = {}
    for q in ("amp_p", "phase_p", "amp_x", "phase_x", "pol_amp", "pol_phase", "back_p", "back_x"):
        out[q + "_end"] = last[q]
        out[q + "_max"] = float(max(abs(r[key][q]) for r in recs))
    if key != "tt":
        out["vs_tt_max"] = float(max(r[key]["vs_tt"] for r in recs[1:]))
        out["vs_tt_end"] = last["vs_tt"]
    return out


def model_f120(n):
    c = F120
    z = zs.evolve_linear_wave(c["kvec"], c["L"], (n, n, n), c["tlim"], c["dt_out"], c["amp"],
                              c["amp_x"], c["ph_x"], kappa1=c["kappa1"])
    kn = float(np.linalg.norm(c["kvec"]))
    ex = refs.wave_measures(*refs.flat_amplitudes(z["t"], kn, c["amp"], c["amp_x"], c["ph_x"]), kn)
    cm = refs.compare(refs.wave_measures(z["P"], z["X"], z["Pd"], z["Xd"], kn), ex)
    return z, cm


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("f120", "xdt"), required=True)
    ap.add_argument("--runs", required=True)
    ap.add_argument("--dt-expansion", type=float, default=0.001)
    ap.add_argument("--ref", default=None, help="results JSON of the reference X analysis")
    ap.add_argument("--ref-dumps", default=None, help="directory with <prefix>dumps_exp_N<n>.json of the reference")
    ap.add_argument("--ref-prefix", default="final_")
    ap.add_argument("--nwork", type=int, default=int(os.environ.get("NWORK", "6")))
    ap.add_argument("--tag", default=None)
    a = ap.parse_args()
    mode = a.mode
    tag = a.tag if a.tag is not None else ("f120_" if mode == "f120" else "xdt_")
    out = os.environ["NRPIC_RUN_DIR"]
    dirs = {int(kv.split("=")[0]): kv.split("=")[1] for kv in a.runs.split(",")}
    ns = sorted(dirs)
    jobs, keys = [], []
    for n in ns:
        files = sorted(glob.glob(os.path.join(SCR, dirs[n], "*.z4c.*.bin"))
                       + glob.glob(os.path.join(SCR, dirs[n], "bin", "*.z4c.*.bin")))
        jobs += [(mode, f) for f in files]
        keys += [n] * len(files)
    with Pool(a.nwork) as pool:
        recs = pool.map(one_dump, jobs, chunksize=1)
    data = {}
    for n, r in zip(keys, recs):
        data.setdefault(n, []).append(r)
    res = {"mode": mode, "runs": dirs, "ns": ns}
    cfg = F120 if mode == "f120" else EXP
    for n in ns:
        rr = sorted(data[n], key=lambda r: r["time"])
        data[n] = rr
        with open(os.path.join(out, f"{tag}dumps_N{n}.json"), "w") as f:
            json.dump(rr, f, indent=1)
        s = {k: summarize(rr, k) for k in DIAGS}
        s["t_end"], s["n_dumps"] = rr[-1]["time"], len(rr)
        s["t0"] = {k: {q: rr[0][k][q] for q in ("amp_p", "phase_p", "amp_x", "phase_x")} for k in DIAGS}
        s["nonTT_rel_max"] = float(max(r["nonTT_rel"] for r in rr[1:]))
        s["nonTT_mode_max"] = float(max(r["nonTT_mode"] for r in rr[1:]))
        s["nonTT_mode_end"] = float(rr[-1]["nonTT_mode"])
        s["Gamma_abs_max"] = float(max(np.linalg.norm(np.array(r["Gamma_k"])) for r in rr))
        s["Theta_k_max"] = float(max(r["Theta_k"] for r in rr))
        s["Khat_k_max"] = float(max(r["Khat_k"] for r in rr))
        s["max_beta"] = float(max(r["max_beta"] for r in rr))
        if mode == "f120":
            z, cm = model_f120(n)
            s["model"] = {"amp_p_end": float(cm["amp_p"][-1]), "phase_p_end": float(cm["phase_p"][-1]),
                          "amp_x_end": float(cm["amp_x"][-1]), "phase_x_end": float(cm["phase_x"][-1]),
                          "back_p_max": float(np.max(cm["back_p"])),
                          "nonTT_mode_max": float(np.max(z["nonTT_mode"][1:])),
                          "nonTT_mode_end": float(z["nonTT_mode"][-1]),
                          "Gamma_abs_max": float(np.max(np.linalg.norm(z["Gamma"], axis=1))),
                          "n_out": int(len(z["t"])), "t_end": float(z["t"][-1])}
            # dump-by-dump ratios measured / model where the model is above 1e-15
            tm = z["t"]
            rg, rn = [], []
            for r in rr[1:]:
                i = int(np.argmin(np.abs(tm - r["time"])))
                gm = float(np.linalg.norm(z["Gamma"][i]))
                gd = float(np.linalg.norm(np.array(r["Gamma_k"])))
                if gm > 1e-15:
                    rg.append(gd / gm)
                rn.append(r["nonTT_mode"] / z["nonTT_mode"][i])
            s["Gamma_ratio_meas_over_model"] = {"median": float(np.median(rg)) if rg else None,
                                                "min": float(np.min(rg)) if rg else None,
                                                "max": float(np.max(rg)) if rg else None, "n": len(rg)}
            s["nonTT_mode_ratio_meas_over_model"] = {"median": float(np.median(rn)), "min": float(np.min(rn)),
                                                     "max": float(np.max(rn))}
        else:
            p = pr.predict_flrw_coupled(cfg["kvec"], cfg["L"], (n, n, n), cfg["tlim"], cfg["dt_out"],
                                        dt_expansion=a.dt_expansion, scheme="2s")
            s["pred_amp_end"] = float(np.abs(p["ratio"][-1]) - 1)
            s["pred_phase_end"] = float(np.angle(p["ratio"][-1]))
            s["pred_nsteps"] = int(p["nsteps"])
            t = np.array([r["time"] for r in rr])
            ae, He, _ = refs.background(t)
            s["a_rel_err_max"] = float(np.max(np.abs(np.array([r["a"] for r in rr]) / ae - 1)))
            s["calH_rel_err_max"] = float(np.max(np.abs(np.array([r["calH"] for r in rr]) / He - 1)))
            s["alpha_over_a_max"] = float(np.max(np.abs(np.array([r["alpha"] for r in rr]) / ae - 1)))
            s["cycle_end"] = int(rr[-1]["cycle"])
        res[str(n)] = s
    res["orders"] = {}
    for k in DIAGS:
        res["orders"][k] = {q: orders([res[str(n)][k][q] for n in ns], ns)
                            for q in ("amp_p_end", "phase_p_end", "amp_x_end", "phase_x_end")}
    for k in ("weyl6",):
        res["orders"][k]["vs_tt_max"] = orders([res[str(n)][k]["vs_tt_max"] for n in ns], ns)
    if mode == "f120":
        res["orders"]["nonTT_mode_max"] = orders([res[str(n)]["nonTT_mode_max"] for n in ns], ns)
        res["orders"]["Gamma_abs_max"] = orders([res[str(n)]["Gamma_abs_max"] for n in ns], ns)
    ref = None
    if mode == "xdt" and a.ref:
        ref = json.load(open(a.ref))
        res["reference"] = {"file": a.ref}
        for n in ns:
            if str(n) in ref.get("exp", {}):
                rs = ref["exp"][str(n)]
                res["reference"][str(n)] = {
                    "tt": {q: rs["tt"][q] for q in ("amp_p_end", "phase_p_end", "amp_x_end", "phase_x_end",
                                                   "pol_amp_end", "pol_phase_end")},
                    "weylS_vs_tt_max": rs["weylS"]["vs_tt_max"],
                    "a_rel_err_max": rs.get("a_rel_err_max"), "alpha_over_a_max": rs.get("alpha_over_a_max")}
    with open(os.path.join(out, f"{tag}results.json"), "w") as f:
        json.dump(res, f, indent=1)
    if mode == "f120":
        fig_f120(data, res, ns, out, tag)
    else:
        refd = {}
        if a.ref_dumps:
            for n in ns:
                p = os.path.join(a.ref_dumps, f"{a.ref_prefix}dumps_exp_N{n}.json")
                if os.path.exists(p):
                    refd[n] = sorted(json.load(open(p)), key=lambda r: r["time"])
        fig_xdt(data, res, ns, out, tag, refd, a.dt_expansion)
    shutil.copy(os.path.join(out, f"{tag}results.json"), os.path.join(PKG, "results", f"{tag}results.json"))
    for png in glob.glob(os.path.join(out, f"{tag}*.png")):
        shutil.copy(png, os.path.join(PKG, "figs", os.path.basename(png)))
    brief = {str(n): {k: res[str(n)][k] for k in res[str(n)] if k not in ("t0",)} for n in ns}
    print(json.dumps({"summary": brief, "orders": res["orders"]}, indent=1)[:20000])


COLS = None


def cols():
    return {16: fs.PAL["yellow"], 32: fs.PAL["red"], 48: fs.PAL["orange"], 64: fs.PAL["green"]}


def fig_f120(data, res, ns, out, tag):
    fs.use_style()
    cc = cols()
    fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 6.2))
    fig.subplots_adjust(left=0.1, right=0.98, bottom=0.08, top=0.95, wspace=0.3, hspace=0.33)
    kn = float(np.linalg.norm(F120["kvec"]))
    for n in ns:
        rr = data[n]
        t = np.array([r["time"] for r in rr])
        z, cm = model_f120(n)
        c = cc.get(n, "k")
        for ax, q in ((axs[0, 0], "amp_p"), (axs[0, 1], "phase_p")):
            ax.semilogy(t[1:], [abs(r["tt"][q]) for r in rr[1:]], color=c, label=f"TT, N = {n}")
            ax.semilogy(t[1:], [abs(r["weyl6"][q]) for r in rr[1:]], color=c, ls="--",
                        label="Weyl FD6" if n == ns[0] else None)
            ax.semilogy(z["t"][1:], np.abs(cm[q][1:]), color="k", ls=":", lw=1.0,
                        label="Z4c symbol" if n == ns[0] else None)
        axs[1, 0].semilogy(t[1:], [r["nonTT_mode"] for r in rr[1:]], color=c, label=f"N = {n}")
        axs[1, 0].semilogy(z["t"][1:], z["nonTT_mode"][1:], color="k", ls=":", lw=1.0,
                           label="Z4c symbol" if n == ns[0] else None)
        axs[1, 1].semilogy(t, [np.linalg.norm(np.array(r["Gamma_k"])) / (F120["amp"] * kn) + 1e-30 for r in rr],
                           color=c, label=f"N = {n}")
        axs[1, 1].semilogy(z["t"], np.linalg.norm(z["Gamma"], axis=1) / (F120["amp"] * kn) + 1e-30,
                           color="k", ls=":", lw=1.0, label="Z4c symbol" if n == ns[0] else None)
    axs[0, 0].set_ylabel("|amplitude error|, + pol.")
    axs[0, 1].set_ylabel("|phase error| (rad), + pol.")
    axs[1, 0].set_ylabel("non-TT part of h at +k")
    axs[1, 1].set_ylabel("|Γ at +k| / (A |k|)")
    axs[0, 0].set_title("F2: k = 2π(1,2,0)", fontsize=10)
    for ax in axs.ravel():
        ax.set_xlabel("t", labelpad=-2)
        lo, hi = ax.get_ylim()
        ax.set_ylim(lo, hi * (hi / lo) ** 0.4)
        ax.legend(loc="upper center", ncol=3, fontsize=6.5)
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(out, f"{tag}errors.{ext}"))
    plt.close(fig)
    # convergence
    fig, ax = plt.subplots(figsize=(fs.FULL_WIDTH / 2 + 0.6, 4.2))
    fig.subplots_adjust(left=0.16, right=0.97, bottom=0.12, top=0.93)
    nn = np.array(ns, float)
    for q, mk, lab in (("amp_p_end", "o", "amplitude"), ("phase_p_end", "s", "phase")):
        ax.loglog(nn, [abs(res[str(n)]["tt"][q]) for n in ns], marker=mk, color=fs.PAL["red"], label="TT " + lab)
        ax.loglog(nn, [abs(res[str(n)]["weyl6"][q]) for n in ns], marker=mk, mfc="none", ls="--",
                  color=fs.PAL["orange"], label="Weyl FD6 " + lab)
        ax.loglog(nn, [abs(res[str(n)]["model"][q]) for n in ns], "x" if q[0] == "a" else "+", color="k", ms=8,
                  label="Z4c symbol " + lab)
    ax.loglog(nn, [res[str(n)]["nonTT_mode_max"] for n in ns], marker="D", color=fs.PAL["green"],
              label="non-TT at +k (max)")
    ax.loglog(nn, [res[str(n)]["model"]["nonTT_mode_max"] for n in ns], "1", color="k", ms=9,
              label="symbol non-TT")
    ax.loglog(nn, [res[str(n)]["weyl6"]["vs_tt_max"] for n in ns], marker="v", color=fs.PAL["blue"],
              label="Weyl FD6 vs TT (max)")
    ax.loglog(nn, [res[str(n)]["weylS"]["vs_tt_max"] for n in ns], marker="^", mfc="none", color=fs.PAL["blue"],
              label="Weyl spectral vs TT")
    ax.set_xticks(ns)
    ax.set_xticklabels([str(n) for n in ns])
    ax.minorticks_off()
    ax.set_xlabel("N (cells per side)")
    ax.set_ylabel("error at the last dump")
    lo, hi = ax.get_ylim()
    ax.set_ylim(lo, hi * (hi / lo) ** 0.55)
    ax.legend(loc="upper right", ncol=2, fontsize=6)
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(out, f"{tag}convergence.{ext}"))
    plt.close(fig)


def fig_xdt(data, res, ns, out, tag, refd, dte):
    fs.use_style()
    cc = cols()
    fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 6.2))
    fig.subplots_adjust(left=0.1, right=0.98, bottom=0.08, top=0.95, wspace=0.3, hspace=0.33)
    for n in ns:
        rr = data[n]
        t = np.array([r["time"] for r in rr])
        c = cc.get(n, "k")
        p = pr.predict_flrw_coupled(EXP["kvec"], EXP["L"], (n, n, n), EXP["tlim"], EXP["dt_out"],
                                    dt_expansion=dte, scheme="2s")
        for ax, q, pv in ((axs[0, 0], "amp_x", np.abs(p["ratio"]) - 1), (axs[0, 1], "phase_x", np.angle(p["ratio"]))):
            ax.semilogy(t[1:], [abs(r["tt"][q]) + 1e-18 for r in rr[1:]], color=c, label=f"N = {n}, dt_exp {dte:g}")
            if n in refd:
                ax.semilogy([r["time"] for r in refd[n][1:]], [abs(r["tt"][q]) + 1e-18 for r in refd[n][1:]],
                            color=c, ls="--", lw=1.0, label="reference 0.01" if n == ns[0] else None)
            ax.semilogy(p["t"][1:], np.abs(pv[1:]) + 1e-18, color="k", ls=":", lw=1.0,
                        label="2S prediction" if n == ns[0] else None)
        axs[1, 0].semilogy(t[1:], [abs(r["tt"]["pol_phase"]) + 1e-18 for r in rr[1:]], color=c, label=f"N = {n}")
        axs[1, 1].semilogy(t[1:], [r["weylS"]["vs_tt"] + 1e-18 for r in rr[1:]], color=c, label=f"N = {n}")
        if n in refd:
            axs[1, 0].semilogy([r["time"] for r in refd[n][1:]], [abs(r["tt"]["pol_phase"]) + 1e-18 for r in refd[n][1:]],
                               color=c, ls="--", lw=1.0, label="reference 0.01" if n == ns[0] else None)
            axs[1, 1].semilogy([r["time"] for r in refd[n][1:]], [r["weylS"]["vs_tt"] + 1e-18 for r in refd[n][1:]],
                               color=c, ls="--", lw=1.0, label="reference 0.01" if n == ns[0] else None)
    axs[0, 0].set_ylabel("|amplitude error|, cross pol.")
    axs[0, 1].set_ylabel("|phase error| (rad), cross pol.")
    axs[1, 0].set_ylabel("|arg R error| (rounding of +)")
    axs[1, 1].set_ylabel("Weyl spectral vs TT")
    for ax in axs.ravel():
        ax.set_xlabel("t (conformal)", labelpad=-2)
        lo, hi = ax.get_ylim()
        ax.set_ylim(lo, hi * (hi / lo) ** 0.45)
        ax.legend(loc="upper center", ncol=2, fontsize=6.5)
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(out, f"{tag}errors.{ext}"))
    plt.close(fig)


if __name__ == "__main__":
    main()
