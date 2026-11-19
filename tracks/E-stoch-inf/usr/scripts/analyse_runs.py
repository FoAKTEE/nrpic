#!/usr/bin/env python3
"""Analysis of the processor runs of the USR case (list ../inputs/proc.list) against the
reference of this package; acceptance quantities of JOURNAL entry 2 (U-A0 to U-A6).

    python3 analyse_runs.py --runs RUNDIR --ref ../results --out OUT

RUNDIR holds one directory per entry of the list (BGv03, ..., NC16).  Writes OUT/summary.json,
OUT/*.npz and the figures OUT/fig/*.png.
"""
import argparse
import csv
import json
import os

import numpy as np

import usr_lib as ul

PKG = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RUNS = {  # name: (nmax2, s, mode file)
    "M16p": (16, 1.0, "modes_usr_n16.txt"), "M16m": (16, -1.0, "modes_usr_n16.txt"),
    "M16l": (16, 1.0e-3, "modes_usr_n16.txt"),
    "M64p": (64, 1.0, "modes_usr_n64.txt"), "M64m": (64, -1.0, "modes_usr_n64.txt"),
}


def load_ref(refdir):
    r = json.load(open(os.path.join(refdir, "usr_reference.json")))
    ci = r["code_inputs"]
    lm = []
    with open(os.path.join(refdir, "landmarks.csv")) as fp:
        rows = [l for l in fp if not l.startswith("#")]
    for row in csv.DictReader(rows):
        lm.append(dict(label=row["label"], cN=float(row["cN"]), t=float(row["t"])))
    return r, ci, lm


# ------------------------------------------------------------------------ background
def analyse_bg(rundir, name, ci, lm):
    h = np.loadtxt(os.path.join(rundir, name, "bg.sf.hst"))
    t, phi, pi, kk, chi, th = h[:, 0], h[:, 2], h[:, 3], h[:, 4], h[:, 5], h[:, 15]
    tw = ul.twin_steps(ci["lambda"], ci["vev"], ci["phi0"], ci["pi0"], ci["K0"], np.diff(t))
    ktw = tw[:, 2] + 2.0 * tw[:, 3]
    ex = ul.exact_background(ci["lambda"], ci["vev"], ci["phi0"], ci["pi0"], ci["K0"], t)
    rel = lambda a, b: np.abs(a - b) / np.abs(b)
    out = dict(cycles=int(h[-1, 1]), t_end=float(t[-1]), dt=float(np.median(np.diff(t))),
               twin_rel_phi=float(rel(phi, tw[:, 0]).max()),
               twin_rel_Pi=float(rel(pi, tw[:, 1]).max()),
               twin_rel_K=float(rel(kk, ktw).max()),
               twin_rel_chi=float(rel(chi, tw[:, 4]).max()),
               exact_rel_phi_end=float(rel(phi, ex[0])[-1]),
               exact_rel_Pi_end=float(rel(pi, ex[1])[-1]),
               exact_rel_Pi_max=float(rel(pi, ex[1]).max()),
               exact_rel_K_max=float(rel(kk, ex[2]).max()),
               efolds_end=float(-0.5 * np.log(chi[-1])),
               efolds_exact_end=float(-0.5 * ex[3][-1]),
               rms_theta_max=float(th.max()))
    lnchi = np.log(chi)
    out["landmarks"] = []
    for m in lm:
        if m["t"] <= t[-1]:
            n_run = float(-0.5 * np.interp(m["t"], t, lnchi))
            # local cubic through the four nearest records
            i = int(np.clip(np.searchsorted(t, m["t"]) - 2, 0, t.size - 4))
            p = np.polyfit(t[i:i + 4] - m["t"], lnchi[i:i + 4], 3)
            n_run = float(-0.5 * p[-1])
            out["landmarks"].append(dict(label=m["label"], cN=m["cN"], N_run=n_run,
                                         dN=n_run - m["cN"]))
    curves = dict(t=t, rel_twin_phi=rel(phi, tw[:, 0]), rel_twin_Pi=rel(pi, tw[:, 1]),
                  rel_twin_K=rel(kk, ktw), rel_twin_chi=rel(chi, tw[:, 4]),
                  rel_ex_Pi=rel(pi, ex[1]), rel_ex_phi=rel(phi, ex[0]), rel_ex_K=rel(kk, ex[2]),
                  dN=-0.5 * (lnchi - ex[3]))
    return out, curves


# ------------------------------------------------------------------------ stochastic runs
def analyse_stoch(rundir, name, ci, out_dir):
    nmax2, s, mf = RUNS[name]
    d = os.path.join(rundir, name)
    dumps = ul.dump_list(d)
    h0 = ul.read_header(dumps[0])
    modes = ul.Modes(h0["nx"][0], nmax2)
    alpha = modes.alpha()
    times, cnr, means = [], [], []
    for p in dumps:
        h, f = ul.read_dump(p, ul.CURV_VARS)
        r, m = ul.curvature(modes, f)
        times.append(h["time"])
        cnr.append(r)
        means.append([m["phi"], m["Pi"], -3.0 * m["H"], m["chi"]])
    times = np.array(times)
    cnr = np.array(cnr)
    means = np.array(means)
    n2f, r0s, dr0s = ul.read_modefile(os.path.join(PKG, "inputs", mf))
    idx = np.searchsorted(n2f, modes.n2)
    assert np.array_equal(n2f[idx], modes.n2)
    r0, dr0 = r0s[idx], dr0s[idx]
    refs = {}
    for lab, k2 in (("cont", modes.k**2), ("stencil", modes.k2_stencil())):
        ref = ul.Reference(ci["lambda"], ci["vev"], ci["phi0"], ci["pi0"], k2, r0, dr0, times)
        cref = np.empty_like(cnr)
        bg = []
        for i in range(times.size):
            st = ref.at(i)
            w = ul.window(modes.k, st["a"], st["H"])
            cref[i] = ul.L_BOX**-1.5 * w * st["R"] * alpha
            bg.append([st["phi"], st["Pi"], st["K"], st["a"]])
        refs[lab] = (cref, np.array(bg))
    # lockstep record against the continuum reference per shell
    lock = []
    ref_sh = ul.Reference(ci["lambda"], ci["vev"], ci["phi0"], ci["pi0"],
                          n2f[n2f <= nmax2].astype(float), r0s[n2f <= nmax2],
                          dr0s[n2f <= nmax2], times)
    for i, p in enumerate(dumps):
        mp = p[:-5] + ".modes"
        if not os.path.exists(mp):
            continue
        hd, n2r, rr, drr = ul.read_modes_record(mp)
        st = ref_sh.at(i)
        rref = st["R"] * s
        lock.append(np.abs(rr - rref) / np.abs(rref))
    lock = np.array(lock)
    con = np.loadtxt(os.path.join(d, "usr.sf.con.hst"))
    np.savez_compressed(os.path.join(out_dir, f"{name}.npz"), t=times, cnr=cnr,
                        cref=refs["cont"][0], cref_st=refs["stencil"][0],
                        bg=refs["cont"][1], means=means, n=modes.n, n2=modes.n2,
                        alpha=alpha, lock=lock, con=con, s=s)
    return dict(times=times, cnr=cnr, cref=refs["cont"][0], cref_st=refs["stencil"][0],
                bg=refs["cont"][1], means=means, modes=modes, s=s, lock=lock, con=con,
                cN=-0.5 * np.log(means[:, 3]))


def mode_metrics(c, cref, s, kmask=None):
    """At the last dump: max and rms of abs(c/(s cref) - 1); over the run: max over modes
    of max_t abs(c - s cref)/max_t abs(s cref)."""
    rat = c[-1] / (s * cref[-1]) - 1.0
    norm = np.abs(s * cref).max(axis=0)
    dev_t = np.abs(c - s * cref) / norm[None, :]
    sel = np.ones(c.shape[1], bool) if kmask is None else kmask
    return dict(max_end=float(np.abs(rat[sel]).max()), rms_end=float(np.sqrt(np.mean(np.abs(rat[sel])**2))),
                max_run=float(dev_t[:, sel].max()), worst_mode=int(np.argmax(np.abs(rat))),
                per_mode_end=np.abs(rat), dev_t=dev_t)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(os.path.join(a.out, "fig"), exist_ok=True)
    r, ci, lm = load_ref(a.ref)
    S = dict(ref_run=r.get("run_id"), runs=a.runs)

    # ---------------- background
    bgc = {}
    for name in ("BGv03", "BGv03h", "BGs2"):
        if os.path.exists(os.path.join(a.runs, name, "bg.sf.hst")):
            S[name], bgc[name] = analyse_bg(a.runs, name, ci, lm)
    if "BGv03" in S and "BGv03h" in S:
        S["BG3_order_Pi"] = S["BGv03"]["exact_rel_Pi_end"] / S["BGv03h"]["exact_rel_Pi_end"]
        S["BG3_order_phi"] = S["BGv03"]["exact_rel_phi_end"] / S["BGv03h"]["exact_rel_phi_end"]
    if "BGv03" in S and "BGs2" in S:
        f1 = open(os.path.join(a.runs, "BGv03", "bg.sf.hst"), "rb").read()
        f2 = open(os.path.join(a.runs, "BGs2", "bg.sf.hst"), "rb").read()
        h1 = np.loadtxt(os.path.join(a.runs, "BGv03", "bg.sf.hst"))
        h2 = np.loadtxt(os.path.join(a.runs, "BGs2", "bg.sf.hst"))
        S["BG4_bytes_identical"] = f1 == f2
        S["BG4_max_abs_diff"] = float(np.abs(h1 - h2).max()) if h1.shape == h2.shape else None

    # ---------------- stochastic runs
    R = {}
    for name in RUNS:
        if os.path.isdir(os.path.join(a.runs, name)) and ul.dump_list(os.path.join(a.runs, name)):
            R[name] = analyse_stoch(a.runs, name, ci, a.out)
    for name, x in R.items():
        m = mode_metrics(x["cnr"], x["cref"], x["s"])
        mst = mode_metrics(x["cnr"], x["cref_st"], x["s"])
        k3 = x["modes"].n2 <= 9
        fr = np.abs(x["cnr"][-1])**2 / np.abs(x["s"] * x["cref"][-1])**2
        cnr_rms = np.sqrt(2.0 * (np.abs(x["cnr"])**2).sum(axis=1))
        ref_rms = np.sqrt(2.0 * (np.abs(x["s"] * x["cref"])**2).sum(axis=1))
        S[name] = dict(nmodes=int(x["modes"].M), ndumps=int(x["times"].size),
                       t_end=float(x["times"][-1]), cN_end=float(x["cN"][-1]),
                       U_A2_cont=dict((k, v) for k, v in m.items() if not isinstance(v, np.ndarray)),
                       U_A2_stencil=dict((k, v) for k, v in mst.items() if not isinstance(v, np.ndarray)),
                       U_A3_power_ratio_k_le_3=dict(min=float(fr[k3].min()), max=float(fr[k3].max())),
                       rms_R_end=float(cnr_rms[-1]), rms_R_ref_end=float(ref_rms[-1]),
                       lock_max_end=float(x["lock"][-1].max()) if x["lock"].size else None,
                       lock_max_run=float(x["lock"].max()) if x["lock"].size else None,
                       con_H_max=float(x["con"][:, 3].max()), con_M_max=float(x["con"][:, 6].max()),
                       con_H_end=float(x["con"][-1, 3]), con_M_end=float(x["con"][-1, 6]))
        x["metrics"] = (m, mst, fr, cnr_rms, ref_rms)
    pairs = {}
    for p, mname in (("M16p", "M16m"), ("M64p", "M64m")):
        if p in R and mname in R:
            xp, xm = R[p], R[mname]
            nt = min(xp["times"].size, xm["times"].size)
            odd = 0.5 * (xp["cnr"][:nt] - xm["cnr"][:nt])
            even = 0.5 * (xp["cnr"][:nt] + xm["cnr"][:nt])
            mo = mode_metrics(odd, xp["cref"][:nt], 1.0)
            mo_st = mode_metrics(odd, xp["cref_st"][:nt], 1.0)
            ratio_t = np.sqrt((np.abs(even)**2).sum(axis=1) / (np.abs(odd)**2).sum(axis=1))
            k3 = xp["modes"].n2 <= 9
            fr = np.abs(odd[-1])**2 / np.abs(xp["cref"][nt - 1])**2
            key = p[:-1] + "_odd"
            nc = min(xp["con"].shape[0], R[mname]["con"].shape[0])
            S[key] = dict(U_A2s_cont=dict((k, v) for k, v in mo.items() if not isinstance(v, np.ndarray)),
                          U_A2s_stencil=dict((k, v) for k, v in mo_st.items() if not isinstance(v, np.ndarray)),
                          U_A2n_even_over_odd_end=float(ratio_t[-1]),
                          U_A2n_even_over_odd_max=float(ratio_t.max()),
                          U_A2n_max_at_cN=float(xp["cN"][:nt][np.argmax(ratio_t)]),
                          U_A3_power_ratio_k_le_3=dict(min=float(fr[k3].min()), max=float(fr[k3].max())),
                          mean_Pi_rel_diff_vs_m=float(np.max(
                              np.abs(xp["con"][:nc, 17] - R[mname]["con"][:nc, 17])
                              / np.abs(xp["con"][:nc, 17]))))
            pairs[p[:-1]] = dict(odd=odd, even=even, ratio_t=ratio_t, cN=xp["cN"][:nt], mo=mo,
                                 cref=xp["cref"][:nt], modes=xp["modes"])
    # backreaction on the means: M16p and M64p against M16l (record every cycle)
    if "M16l" in R:
        cl = R["M16l"]["con"]
        for name in ("M16p", "M64p"):
            if name in R:
                c = R[name]["con"]
                n = min(c.shape[0], cl.shape[0])
                S[name]["M5_Pi_rel_vs_M16l_max"] = float(np.max(np.abs(c[:n, 17] - cl[:n, 17]) / np.abs(cl[:n, 17])))
                S[name]["M5_phi_rel_vs_M16l_max"] = float(np.max(np.abs(c[:n, 16] - cl[:n, 16]) / np.abs(cl[:n, 16])))
                S[name]["M5_K_rel_vs_M16l_max"] = float(np.max(np.abs(c[:n, 18] - cl[:n, 18]) / np.abs(cl[:n, 18])))
    # A1 for the stochastic runs: box means against the exact background
    for name, x in R.items():
        c = x["con"]
        ex = ul.exact_background(ci["lambda"], ci["vev"], ci["phi0"], ci["pi0"], ci["K0"], c[:, 0])
        S[name]["U_A1_Pi_rel_max"] = float(np.max(np.abs(c[:, 17] - ex[1]) / np.abs(ex[1])))
        S[name]["U_A1_phi_rel_max"] = float(np.max(np.abs(c[:, 16] - ex[0]) / np.abs(ex[0])))
        S[name]["U_A1_K_rel_max"] = float(np.max(np.abs(c[:, 18] - ex[2]) / np.abs(ex[2])))
        S[name]["efolds_end"] = float(c[-1, 2])
        x["exact"] = ex
    nc = os.path.join(a.runs, "NC16", "usr.sf.con.hst")
    if os.path.exists(nc):
        cnc = np.loadtxt(nc)
        S["NC16"] = dict(con_H_max=float(cnc[:, 3].max()), con_M_max=float(cnc[:, 6].max()),
                         t_end=float(cnc[-1, 0]))
        if "M16p" in R:
            cp = R["M16p"]["con"]
            n = min(cnc.shape[0], cp.shape[0])
            first = cnc[:n, 2] <= 1.0
            S["NC16"]["H_ratio_to_M16p_first_efold_min"] = float(np.min(cnc[:n, 3][first] / cp[:n, 3][first]))
            S["NC16"]["H_ratio_to_M16p_first_efold_median"] = float(np.median(cnc[:n, 3][first] / cp[:n, 3][first]))
    else:
        cnc = None
    with open(os.path.join(a.out, "summary.json"), "w") as fp:
        json.dump(S, fp, indent=1, default=float)
    print(json.dumps(S, indent=1, default=float)[:20000])
    figures(a.out, S, bgc, R, pairs, cnc, r, lm)


def figures(out, S, bgc, R, pairs, cnc, ref, lm):
    import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    fd = os.path.join(out, "fig")
    usr = ref["usr_cN"]
    # ---- background against twin and exact
    if "BGv03" in bgc:
        fig, ax = plt.subplots(2, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 5.4), sharex=True)
        fig.subplots_adjust(left=0.14, right=0.97, top=0.97, bottom=0.10, hspace=0.08)
        c = bgc["BGv03"]
        for key, ls, lab in (("rel_twin_phi", "-", r"$\phi$"), ("rel_twin_Pi", "--", r"$\Pi$"),
                             ("rel_twin_K", ":", r"$K$"), ("rel_twin_chi", "-.", r"$\chi$")):
            ax[0].semilogy(c["t"][1:], np.maximum(c[key][1:], 1e-17), color=fs.PAL["red"], ls=ls, label=lab)
        ax[0].axhline(1e-11, **fs.GUIDE, label="U-A1t (phi, K, chi)")
        ax[0].set_ylabel("|code - twin| / |twin|")
        ax[0].legend(loc="upper left", ncol=3, fontsize=8)
        for name, col in (("BGv03", fs.PAL["red"]), ("BGv03h", fs.PAL["blue"])):
            if name in bgc:
                cc = bgc[name]
                ax[1].semilogy(cc["t"][1:], cc["rel_ex_Pi"][1:], color=col, label=f"{name}: Pi")
                ax[1].semilogy(cc["t"][1:], cc["rel_ex_phi"][1:], color=col, ls="--", label=f"{name}: phi")
        if "BGv03h" in bgc:
            cc = bgc["BGv03h"]
            ax[1].semilogy(cc["t"][1:], 16 * cc["rel_ex_Pi"][1:], color=fs.PAL["blue"], ls=":", lw=1.0,
                           label="BGv03h Pi x 16")
        ax[1].axhline(1e-3, **fs.GUIDE, label="U-A1 (USR) 1e-3")
        for m in lm:
            if "USR" in m["label"]:
                for x in ax:
                    x.axvline(m["t"], **fs.MASK_LINE)
        ax[1].set_ylabel("|code - exact| / |exact|")
        ax[1].set_xlabel(r"$t$ (code units)")
        ax[1].legend(loc="lower right", ncol=2, fontsize=8)
        fs.save(fig, os.path.join(fd, "fig_run_background"))
        plt.close(fig)
    # ---- modes in time (run M16, odd part and linear limit)
    for tag, src in (("M16", "M16"), ("M64", "M64")):
        if src not in pairs:
            continue
        P = pairs[src]
        md = P["modes"]
        fig, ax = plt.subplots(2, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 6.0), sharex=True)
        fig.subplots_adjust(left=0.15, right=0.97, top=0.97, bottom=0.09, hspace=0.08)
        for x in ax:
            x.axvspan(usr[0], usr[1], color=fs.PAL["yellow"], alpha=0.15, lw=0)
        picks = [1, 2, 3, 4] + ([8] if md.nmax2 >= 64 else [])
        cols = fs.series_colors(len(picks))
        for col, p2 in zip(cols, picks):
            js = np.where(md.n2 == p2 * p2)[0]
            if js.size == 0:
                continue
            j = js[0]
            kfac = (p2**3) * (2 * np.pi)**3 / (2 * np.pi**2)
            ax[0].semilogy(P["cN"], kfac * np.abs(P["cref"][:, j])**2, color=col, lw=1.0, ls="--")
            ax[0].semilogy(P["cN"], kfac * np.abs(P["odd"][:, j])**2, color=col, marker="o", ms=3,
                           ls="none", label=f"n = {tuple(int(v) for v in md.n[j])}")
            if f"{src}l" in R:
                xl = R[f"{src}l"]
                ax[0].semilogy(xl["cN"], kfac * np.abs(xl["cnr"][:, j] / xl["s"])**2, color=col,
                               marker="x", ms=3, ls="none")
        ax[0].set_ylabel(r"$k^3 L^3 |c_n|^2/(2\pi^2)$ (o odd, x linear, -- MS)")
        ax[0].legend(loc="upper left", fontsize=8, ncol=2)
        dev = P["mo"]["dev_t"]
        ax[1].semilogy(P["cN"], np.maximum(dev.max(axis=1), 1e-16), color=fs.PAL["red"],
                       label="odd part: max over modes")
        if f"{src}l" in R:
            ml = R[f"{src}l"]["metrics"][0]
            ax[1].semilogy(R[f"{src}l"]["cN"], np.maximum(ml["dev_t"].max(axis=1), 1e-16),
                           color=fs.PAL["blue"], label="linear limit (s = 1e-3)")
        ax[1].semilogy(P["cN"], P["ratio_t"], color=fs.PAL["green"], label="even/odd (rms over modes)")
        ax[1].axhline(0.02, **fs.GUIDE, label="0.02")
        ax[1].set_ylabel(r"$|c-c_{\rm ref}|/\max_t|c_{\rm ref}|$")
        ax[1].set_xlabel(r"$N-N_*$ (from $\langle\chi\rangle$)")
        ax[1].legend(loc="lower right", fontsize=8)
        fs.save(fig, os.path.join(fd, f"fig_run_modes_{tag}"))
        plt.close(fig)
    # ---- per-mode errors at N_f
    fig, ax = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 3.4))
    fig.subplots_adjust(left=0.15, right=0.97, top=0.96, bottom=0.15)
    if "M16l" in R:
        x = R["M16l"]
        ax.semilogy(x["modes"].k, x["metrics"][0]["per_mode_end"], "o", ms=3, color=fs.PAL["blue"],
                    label="M16l (s = 1e-3), continuum k^2")
        ax.semilogy(x["modes"].k, x["metrics"][1]["per_mode_end"], "+", ms=4, color=fs.PAL["blue"],
                    label="M16l, stencil k^2")
    for src, col in (("M16", fs.PAL["red"]), ("M64", fs.PAL["orange"])):
        if src in pairs:
            P = pairs[src]
            ax.semilogy(P["modes"].k, P["mo"]["per_mode_end"], "s", ms=3, mfc="none", color=col,
                        label=f"{src} odd part")
            ev = np.abs(P["even"][-1]) / np.abs(P["odd"][-1])
            ax.semilogy(P["modes"].k, ev, ".", ms=3, color=col, alpha=0.5, label=f"{src} |even|/|odd|")
    ax.axhline(0.02, **fs.GUIDE, label="U-A2 0.02")
    ax.set_xlabel(r"$|n| = k/dk$")
    ax.set_ylabel(r"at $N_f$: $|c/c_{\rm ref}-1|$")
    ax.legend(loc="upper left", fontsize=7, ncol=2)
    fs.save(fig, os.path.join(fd, "fig_run_mode_errors"))
    plt.close(fig)
    # ---- constraints
    fig, ax = plt.subplots(2, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 5.4), sharex=True)
    fig.subplots_adjust(left=0.15, right=0.97, top=0.97, bottom=0.10, hspace=0.08)
    cols = dict(M16p=fs.PAL["red"], M16l=fs.PAL["blue"], M64p=fs.PAL["orange"], M16m=fs.PAL["green"])
    for x in ax:
        x.axvspan(usr[0], usr[1], color=fs.PAL["yellow"], alpha=0.15, lw=0)
    for name in ("M16p", "M16l", "M64p"):
        if name in R:
            c = R[name]["con"]
            ax[0].semilogy(c[:, 2], c[:, 3], color=cols[name], label=name)
            ax[1].semilogy(c[:, 2], c[:, 6], color=cols[name], label=name)
    if cnc is not None:
        ax[0].semilogy(cnc[:, 2], cnc[:, 3], color="k", ls=":", label="NC16 (sign flipped)")
        ax[1].semilogy(cnc[:, 2], cnc[:, 6], color="k", ls=":", label="NC16")
    ax[0].set_ylabel(r"$\langle|{\cal H}|/[{\cal H}]\rangle$")
    ax[1].set_ylabel(r"$\langle|{\cal M}|/[{\cal M}]\rangle$")
    ax[1].set_xlabel(r"$N-N_*$ (from $\langle\chi\rangle$)")
    ax[0].legend(loc="upper right", fontsize=8, ncol=2)
    fs.save(fig, os.path.join(fd, "fig_run_constraints"))
    plt.close(fig)
    # ---- box means against the exact background
    fig, ax = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 3.4))
    fig.subplots_adjust(left=0.15, right=0.97, top=0.96, bottom=0.15)
    ax.axvspan(usr[0], usr[1], color=fs.PAL["yellow"], alpha=0.15, lw=0)
    if "BGv03" in bgc:
        c = bgc["BGv03"]
        nb = -0.5 * np.log(np.loadtxt(os.path.join(S["runs"], "BGv03", "bg.sf.hst"))[:, 5])
        ax.semilogy(nb[1:], c["rel_ex_Pi"][1:], color="k", label="BGv03 (homogeneous)")
    for name in ("M16l", "M16p", "M64p"):
        if name in R:
            c = R[name]["con"]
            ex = R[name]["exact"]
            ax.semilogy(c[1:, 2], np.abs(c[1:, 17] - ex[1][1:]) / np.abs(ex[1][1:]), color=cols[name], label=name)
    ax.axhline(1e-3, **fs.GUIDE, label="U-A1 1e-3")
    ax.set_xlabel(r"$N-N_*$")
    ax.set_ylabel(r"$|\langle\Pi\rangle-\Pi_{\rm exact}|/\Pi_{\rm exact}$")
    ax.legend(loc="upper left", fontsize=8)
    fs.save(fig, os.path.join(fd, "fig_run_means"))
    plt.close(fig)
    # ---- shell spectrum of the realisation (M64 odd) against W^2 Delta
    if "M64" in pairs:
        P = pairs["M64"]
        md = P["modes"]
        fig, ax = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 3.6))
        fig.subplots_adjust(left=0.15, right=0.97, top=0.96, bottom=0.14)
        targets = [0.0, 2.0, 4.0, 5.0, 6.0, 10.0]
        colsT = fs.series_colors(len(targets))
        for col, tt in zip(colsT, targets):
            i = int(np.argmin(np.abs(P["cN"] - tt)))
            kfac = md.shell_n2**1.5 * (2 * np.pi)**3 / (2 * np.pi**2)
            pnr = np.array([np.mean(np.abs(P["odd"][i, md.shell_of == j])**2) for j in range(md.shell_n2.size)])
            pre = np.array([np.mean(np.abs(P["cref"][i, md.shell_of == j])**2) for j in range(md.shell_n2.size)])
            ks = np.sqrt(md.shell_n2)
            ax.loglog(ks, kfac * pre, color=col, lw=1.0)
            ax.loglog(ks, kfac * pnr, "o", ms=3, color=col, label=f"N-N* = {P['cN'][i]:.2f}")
        ax.set_xlabel(r"$k/dk$")
        ax.set_ylabel(r"shell mean $k^3|{\cal R}_k|^2/(2\pi^2)$ of the realisation")
        ax.legend(loc="lower right", fontsize=7, ncol=2)
        fs.save(fig, os.path.join(fd, "fig_run_spectrum_M64"))
        plt.close(fig)


if __name__ == "__main__":
    main()
