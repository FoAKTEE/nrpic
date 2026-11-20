#!/usr/bin/env python3
"""Analysis of the window scan (package tracks/E-stoch-inf/window, step 4) against the
linear reference of each window; predictions W1-W8 of ../JOURNAL.md entry 1.

    python3 analyse_window.py --runs RUNDIR --out OUT [--case usr sr]
                              [--nmax2 N --modefile F --tag T]   (development only)

RUNDIR holds one directory per entry of ../inputs/card_window.list (b_p, b_m, s25_p, ...,
sr_b_p, ...). Dumps are read one at a time, in order (NRSFDMP2, usr_lib.read_dump).
For every run: R^NR per mode (usr_lib.curvature) at every dump, box means, the constraint
record. Reference per window: L^-3/2 W R alpha with the continuum Mukhanov-Sasaki mode of
the run's mode file (usr_lib.Reference; window_lib.QuadReference for slow roll), at the
dump times of the run. Odd part O = (R(+1) - R(-1))/2, even part E = (R(+1) + R(-1))/2
where both runs exist; otherwise O = R(+1) (holds the even part as well).

Writes OUT/summary_<case>.json, OUT/table_<case>.md, OUT/<run>.npz (cache of R^NR) and
OUT/fig/*.png.
"""
import argparse
import json
import os

import numpy as np

import window_lib as wl
import usr_lib as ul

KMAX2_FRAC = 0.5          # U-A2 / A2: modes with k <= k_max/2
THR_A2 = 0.02


# ------------------------------------------------------------------------- reading
def read_run(rundir, name, case, modes, out):
    cache = os.path.join(out, f"{name}.npz")
    d = os.path.join(rundir, name)
    if os.path.exists(cache):
        z = np.load(cache)
        if int(z["nmodes"]) == modes.M:
            return dict(t=z["t"], cyc=z["cyc"], cnr=z["cnr"], means=z["means"], con=z["con"])
    base = wl.CASES[case]["base"]
    dumps = ul.dump_list(d, base=base)
    t, cyc, cnr, means = [], [], [], []
    for p in dumps:                      # one dump at a time, in order
        h, f = ul.read_dump(p, ul.CURV_VARS)
        r, m = ul.curvature(modes, f)
        del f
        t.append(h["time"])
        cyc.append(h["cycle"])
        cnr.append(r)
        means.append([m["phi"], m["Pi"], -3.0 * m["H"], m["chi"]])
    con = np.loadtxt(os.path.join(d, f"{base}.sf.con.hst"))
    res = dict(t=np.array(t), cyc=np.array(cyc), cnr=np.array(cnr), means=np.array(means),
               con=con)
    np.savez_compressed(cache, nmodes=modes.M, **res)
    return res


def athena_cost(rundir, name):
    """cpu time and zone-cycles/s from the run's AthenaK log, if present."""
    d = os.path.join(rundir, name)
    for f in sorted(os.listdir(d)):
        if f.startswith("athena") and f.endswith(".log"):
            cpu = zc = None
            for line in open(os.path.join(d, f), errors="replace"):
                if "cpu time used" in line:
                    cpu = float(line.split("=")[1])
                if "zone-cycles/cpu_second" in line:
                    zc = float(line.split("=")[1])
            if cpu is not None:
                return dict(cpu_s=cpu, zone_cycles_per_s=zc)
    return None


# ------------------------------------------------------------------------- analysis
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--case", nargs="+", default=["usr", "sr"])
    ap.add_argument("--nmax2", type=int, default=None, help="development only")
    ap.add_argument("--modefile", default=None, help="development only")
    a = ap.parse_args()
    os.makedirs(os.path.join(a.out, "fig"), exist_ok=True)
    for case in a.case:
        if a.nmax2:
            wl.CASES[case]["nmax2"] = a.nmax2
        if a.modefile:
            wl.CASES[case]["modefile"] = a.modefile
        S, D = analyse_case(a.runs, case, a.out)
        if S is None:
            continue
        with open(os.path.join(a.out, f"summary_{case}.json"), "w") as fp:
            json.dump(S, fp, indent=1, default=float)
        write_table(S, case, os.path.join(a.out, f"table_{case}.md"))
        figures(S, D, case, a.out)
        print(json.dumps(S["table"], indent=1, default=float))


def analyse_case(rundir, case, out):
    c = wl.CASES[case]
    pre = c["prefix"]
    present = [w for w in wl.WINDOWS
               if os.path.isdir(os.path.join(rundir, f"{pre}{w}_p"))]
    if "b" not in present:
        print(f"{case}: no baseline run in {rundir}")
        return None, None
    h0 = ul.read_header(ul.dump_list(os.path.join(rundir, f"{pre}b_p"), base=c["base"])[0])
    nmesh = int(round(h0["nmb"] ** (1.0 / 3.0))) * h0["nx"][0]   # cubic root mesh
    modes = wl.Modes(nmesh, c["nmax2"])
    alpha = modes.alpha()
    n2s, r0, dr0 = wl.shells(case)
    assert np.array_equal(modes.shell_n2, n2s), "mode file shells differ from the cut"
    kmode = modes.k
    kmax = np.sqrt(c["nmax2"])
    half = kmode <= KMAX2_FRAC * kmax
    runs = {}
    for w in present:
        for sgn in ("p", "m"):
            name = f"{pre}{w}_{sgn}"
            if os.path.isdir(os.path.join(rundir, name)):
                runs[name] = read_run(rundir, name, case, modes, out)
    # common dump times (the same step sequence for every run)
    nt = min(x["t"].size for x in runs.values())
    tb = runs[f"{pre}b_p"]["t"][:nt]
    tdiff = max(float(np.max(np.abs(x["t"][:nt] - tb))) for x in runs.values())
    ref = wl.reference(case, n2s.astype(float), r0, dr0, tb)
    st = [ref.at(i) for i in range(nt)]
    a_t = np.array([s["a"] for s in st])
    H_t = np.array([s["H"] for s in st])
    Rm = np.array([s["R"][modes.shell_of] for s in st])            # (nt, M)
    cN_ref = np.log(a_t)
    S = dict(case=case, rundir=rundir, nmesh=int(modes.N), nmax2=c["nmax2"], nmodes=int(modes.M),
             ndumps=int(nt), dump_times=tb.tolist(), max_dump_time_mismatch=tdiff,
             cN_last_dump=float(cN_ref[-1]), windows={}, runs_present=sorted(runs))
    D = dict(modes=modes, cN=cN_ref, t=tb, W={}, ref={}, O={}, E={}, P={})
    for w in present:
        s, sig = wl.WINDOWS[w]
        W = wl.window(kmode[None, :], a_t[:, None], H_t[:, None], s, sig)
        refw = wl.L_BOX**-1.5 * W * Rm * alpha[None, :]
        xp = runs[f"{pre}{w}_p"]
        xm = runs.get(f"{pre}{w}_m")
        if xm is not None:
            O = 0.5 * (xp["cnr"][:nt] - xm["cnr"][:nt])
            E = 0.5 * (xp["cnr"][:nt] + xm["cnr"][:nt])
        else:
            O, E = xp["cnr"][:nt], None
        D["W"][w], D["ref"][w], D["O"][w], D["E"][w] = W, refw, O, E
        D["P"][w] = xp["cnr"][:nt]
        rat = O[-1] / refw[-1] - 1.0
        norm = np.abs(refw).max(axis=0)
        dev_t = np.abs(O - refw) / norm[None, :]
        # shell powers at the last dump
        ns = modes.shell_n2.size
        cnt = np.bincount(modes.shell_of, minlength=ns)
        Pnr = np.bincount(modes.shell_of, weights=np.abs(O[-1])**2, minlength=ns) / cnt
        Pref = np.bincount(modes.shell_of, weights=np.abs(refw[-1])**2, minlength=ns) / cnt
        e_shell = Pnr / Pref - 1.0
        rms_nr = np.sqrt(2.0 * (np.abs(O)**2).sum(axis=1))
        rms_ref = np.sqrt(2.0 * (np.abs(refw)**2).sum(axis=1))
        ent = dict(s=s, sigma=sig, mirrored=xm is not None,
                   A2_max_end_half=float(np.abs(rat[half]).max()),
                   A2_rms_end_half=float(np.sqrt(np.mean(np.abs(rat[half])**2))),
                   A2_max_end_all=float(np.abs(rat).max()),
                   A2_k_of_max_all=float(kmode[np.argmax(np.abs(rat))]),
                   A2_max_run_half=float(dev_t[:, half].max()),
                   A2_max_run_all=float(dev_t.max()),
                   err_by_band=band_stats(kmode, np.abs(rat)),
                   shell_power_err_end=dict(max_half=float(np.abs(e_shell[np.sqrt(modes.shell_n2) <= KMAX2_FRAC * kmax]).max()),
                                            max_all=float(np.abs(e_shell).max())),
                   rms_WR_end_nr=float(rms_nr[-1]), rms_WR_end_ref=float(rms_ref[-1]),
                   rms_rel_err_end=float(rms_nr[-1] / rms_ref[-1] - 1.0),
                   rms_rel_err_max=float(np.max(np.abs(rms_nr[1:] / rms_ref[1:] - 1.0))),
                   cost=athena_cost(rundir, f"{pre}{w}_p"))
        D[f"e_shell_{w}"] = e_shell
        D[f"rat_{w}"] = rat
        D[f"dev_t_{w}"] = dev_t
        D[f"rms_{w}"] = (rms_nr, rms_ref)
        if E is not None:
            ratio_t = np.sqrt((np.abs(E)**2).sum(axis=1) / (np.abs(O)**2).sum(axis=1))
            ent.update(EO_rms_end=float(ratio_t[-1]), EO_rms_max=float(ratio_t[1:].max()),
                       EO_cN_of_max=float(cN_ref[1:][np.argmax(ratio_t[1:])]),
                       E_over_ref_end_max=float((np.abs(E[-1]) / np.abs(refw[-1])).max()),
                       E_over_ref_end_k_of_max=float(kmode[np.argmax(np.abs(E[-1]) / np.abs(refw[-1]))]))
            D[f"EO_t_{w}"] = ratio_t
        S["windows"][w] = ent
    # ---------------- shifts against the baseline
    Ob, refb = D["O"]["b"], D["ref"]["b"]
    shells_k = np.sqrt(modes.shell_n2.astype(float))
    ns = shells_k.size
    cnt = np.bincount(modes.shell_of, minlength=ns)
    shellP = lambda X: np.bincount(modes.shell_of, weights=np.abs(X)**2, minlength=ns) / cnt
    for w in present:
        if w == "b":
            continue
        Ow, refw = D["O"][w], D["ref"][w]
        dnr = shellP(Ow[-1]) / shellP(Ob[-1]) - 1.0
        dlin = shellP(refw[-1]) / shellP(refb[-1]) - 1.0
        err = np.abs(D[f"e_shell_{w}"]) + np.abs(D["e_shell_b"])
        # +1 runs only (contain the even parts)
        dnr_p = shellP(D["P"][w][-1]) / shellP(D["P"]["b"][-1]) - 1.0
        permode = np.abs(Ow[-1] / Ob[-1] - 1.0)
        # passage: per mode, NR shift against the linear shift, k <= k_max/2
        normw = np.abs(refw).max(axis=0)
        res_t = np.abs((Ow - Ob) - (refw - refb)) / normw[None, :]
        lin_t = np.abs(refw - refb) / normw[None, :]
        pas = (cN_ref > 0.01) & (cN_ref < 4.5)
        # shells that crossed before the USR onset in both windows
        s_w, g_w = wl.WINDOWS[w]
        kb = 11.874342087037917 * min(g_w, 1.0)     # reference entry 2 (k < 11.87 sigma)
        pre_usr = kmode < kb
        ent = S["windows"][w]
        ent.update(
            shift_end_shell_nr=dict(by_band=band_stats(shells_k, np.abs(dnr)),
                                    max_half=float(np.abs(dnr[shells_k <= KMAX2_FRAC * kmax]).max()),
                                    max_all=float(np.abs(dnr).max())),
            shift_end_shell_lin_max=float(np.abs(dlin).max()),
            shift_end_shell_err=dict(by_band=band_stats(shells_k, err),
                                     max_half=float(err[shells_k <= KMAX2_FRAC * kmax].max())),
            shift_end_shell_nr_plus_runs=dict(by_band=band_stats(shells_k, np.abs(dnr_p)),
                                              max_half=float(np.abs(dnr_p[shells_k <= KMAX2_FRAC * kmax]).max())),
            shift_end_mode_max_half=float(permode[half].max()),
            passage_residual_max_half=float(res_t[pas][:, half].max()) if pas.any() else None,
            passage_linear_shift_max_half=float(lin_t[pas][:, half].max()) if pas.any() else None,
            passage_residual_max_all=float(res_t[pas].max()) if pas.any() else None,
            pre_usr_k_bound=kb,
            pre_usr_nmodes=int(pre_usr.sum()),
            pre_usr_mode_shift_max=float(permode[pre_usr].max()),
            pre_usr_mode_shift_median=float(np.median(permode[pre_usr])))
        if D["E"][w] is not None and D["E"]["b"] is not None:
            dE = D["E"][w][-1] - D["E"]["b"][-1]
            ent["even_shift_rms_over_odd_rms_end"] = float(
                np.sqrt((np.abs(dE)**2).sum() / (np.abs(Ob[-1])**2).sum()))
            ent["even_shift_rms_over_even_rms_end"] = float(
                np.sqrt((np.abs(dE)**2).sum() / (np.abs(D["E"]["b"][-1])**2).sum()))
        D[f"dnr_{w}"], D[f"dlin_{w}"], D[f"err_{w}"] = dnr, dlin, err
        D[f"res_t_{w}"], D[f"lin_t_{w}"] = res_t, lin_t
    # ---------------- sensitivity per parameter (slopes in ln s and ln sigma)
    S["sensitivity"] = {}
    for par, members in (("s", ("s25", "b", "s10")), ("sigma", ("g05", "b", "g2"))):
        if not all(m in present for m in members):
            continue
        x = np.log([wl.WINDOWS[m][0 if par == "s" else 1] for m in members])
        lnP = np.array([np.log(shellP(D["O"][m][-1])) for m in members])
        lnPl = np.array([np.log(shellP(D["ref"][m][-1])) for m in members])
        xc = x - x.mean()
        slope = (xc[:, None] * (lnP - lnP.mean(axis=0))).sum(axis=0) / (xc**2).sum()
        slope_l = (xc[:, None] * (lnPl - lnPl.mean(axis=0))).sum(axis=0) / (xc**2).sum()
        e = np.array([np.abs(D[f"e_shell_{m}"]) for m in members])
        slope_err = np.sqrt(((xc[:, None] * e)**2).sum(axis=0)) / (xc**2).sum()
        S["sensitivity"][par] = dict(
            by_band=band_stats(shells_k, np.abs(slope)), by_band_err=band_stats(shells_k, slope_err),
            linear_max=float(np.abs(slope_l).max()))
        D[f"slope_{par}"] = (slope, slope_err, slope_l)
    # ---------------- constraints and means (records every cycle)
    cb = runs[f"{pre}b_p"]["con"]
    for w in present:
        cw = runs[f"{pre}{w}_p"]["con"]
        n = min(cw.shape[0], cb.shape[0])
        same_t = bool(np.allclose(cw[:n, 0], cb[:n, 0], rtol=0, atol=1e-12))
        late = cb[:n, 2] > 5.0
        rel = lambda col: float(np.max(np.abs(cw[:n, col] - cb[:n, col]) / np.abs(cb[:n, col])))
        S["windows"][w].update(
            con_same_steps=same_t, con_cycles=int(cw[-1, 1]),
            H_record_late_ratio=[float(np.min(cw[:n, 3][late] / cb[:n, 3][late])),
                                 float(np.max(cw[:n, 3][late] / cb[:n, 3][late]))] if late.any() else None,
            M_record_late_ratio=[float(np.min(cw[:n, 6][late] / cb[:n, 6][late])),
                                 float(np.max(cw[:n, 6][late] / cb[:n, 6][late]))] if late.any() else None,
            H_record_max=float(cw[:, 3].max()), M_record_max=float(cw[:, 6].max()),
            means_rel_diff_vs_b=dict(phi=rel(16), Pi=rel(17), K=rel(18)))
        D[f"con_{w}"] = cw
    S["table"] = table_rows(S, present)
    return S, D


def band_stats(k, v):
    bands = (("k<6", k < 6), ("6<=k<12", (k >= 6) & (k < 12)), ("12<=k<=16", (k >= 12) & (k <= 16)),
             ("16<k<=32", (k > 16) & (k <= 32)), ("8<k<=16", (k > 8) & (k <= 16)))
    out = {}
    for lab, sel in bands:
        if sel.any():
            out[lab] = float(np.max(v[sel]))
    return out


def table_rows(S, present):
    rows = []
    for w in present:
        e = S["windows"][w]
        rows.append(dict(
            window=w, s=e["s"], sigma=e["sigma"],
            A2_half=e["A2_max_end_half"], A2_all=e["A2_max_end_all"],
            shift_half=e.get("shift_end_shell_nr", {}).get("max_half"),
            shift_err_half=e.get("shift_end_shell_err", {}).get("max_half"),
            shift_all=e.get("shift_end_shell_nr", {}).get("max_all"),
            shift_lin=e.get("shift_end_shell_lin_max"),
            pre_usr=e.get("pre_usr_mode_shift_max"),
            passage_res=e.get("passage_residual_max_half"),
            passage_lin=e.get("passage_linear_shift_max_half"),
            EO=e.get("EO_rms_end"), rms_rel=e["rms_rel_err_end"],
            M_late=e.get("M_record_late_ratio"), means=max(e["means_rel_diff_vs_b"].values())))
    return rows


def fmt(x, f="{:.2e}"):
    if x is None:
        return "-"
    if isinstance(x, (list, tuple)):
        return "-".join(fmt(v, "{:.3g}") for v in x)
    return f.format(x)


def write_table(S, case, path):
    kmax = np.sqrt(S["nmax2"])
    with open(path, "w") as fp:
        fp.write(f"# Sensitivity of the {case.upper()} spectrum to s and sigma "
                 f"({S['nmesh']}^3, nmax2 = {S['nmax2']}, last dump cN = {S['cN_last_dump']:.3f})\n\n")
        fp.write("| window | s | sigma | U-A2 k<=k_max/2 | U-A2 all | shell shift k<=k_max/2 "
                 "(error) | shell shift all | linear shift | modes crossed before USR: max shift "
                 "| passage residual (linear shift) | E/O rms | one-point rms NR/ref-1 | "
                 "late M record / baseline | means vs baseline |\n")
        fp.write("|" + "---|" * 14 + "\n")
        for r in S["table"]:
            fp.write(f"| {r['window']} | {r['s']:g} | {r['sigma']:g} | {fmt(r['A2_half'])} | "
                     f"{fmt(r['A2_all'])} | {fmt(r['shift_half'])} ({fmt(r['shift_err_half'])}) | "
                     f"{fmt(r['shift_all'])} | {fmt(r['shift_lin'])} | {fmt(r['pre_usr'])} | "
                     f"{fmt(r['passage_res'])} ({fmt(r['passage_lin'])}) | {fmt(r['EO'])} | "
                     f"{fmt(r['rms_rel'])} | {fmt(r['M_late'])} | {fmt(r['means'])} |\n")
        fp.write(f"\nk_max = {kmax:g} dk. Shifts are shell powers at the last dump against the "
                 "baseline (odd parts where mirrored); error = |e_w| + |e_b|, the NR-vs-reference "
                 "power error of the two runs. Passage residual: max over modes k <= k_max/2 "
                 "and dumps 0 < cN < 4.5 of |(O_w - O_b) - (ref_w - ref_b)|/max_t|ref_w|.\n")
        if S.get("sensitivity"):
            fp.write("\nSensitivity d ln P/d ln(par) at the last dump, max per band "
                     "(error from the NR-vs-reference power errors):\n\n")
            for par, v in S["sensitivity"].items():
                fp.write(f"- {par}: " + ", ".join(
                    f"{b}: {v['by_band'][b]:.2e} ({v['by_band_err'][b]:.2e})" for b in v["by_band"])
                    + f"; linear {v['linear_max']:.1e}\n")


# ------------------------------------------------------------------------- figures
def figures(S, D, case, out):
    import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    cols = dict(zip(wl.WINDOWS, [fs.PAL["blue"], fs.PAL["red"], fs.PAL["orange"],
                                 fs.PAL["green"], "purple"]))
    present = list(S["windows"])
    modes = D["modes"]
    k = modes.k
    kmax = np.sqrt(S["nmax2"])
    cN = D["cN"]
    usr = case == "usr"
    fd = os.path.join(out, "fig")
    tag = case
    # ---- 1. per-mode errors at the last dump
    fig, ax = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 3.6))
    fig.subplots_adjust(left=0.14, right=0.97, top=0.96, bottom=0.14)
    for w in present:
        ax.semilogy(k, np.maximum(np.abs(D[f"rat_{w}"]), 1e-12), ".", ms=1.5, color=cols[w],
                    alpha=0.5, rasterized=True)
        ks = np.sqrt(modes.shell_n2)
        mx = np.array([np.abs(D[f"rat_{w}"])[modes.shell_of == j].max() for j in range(ks.size)])
        ax.semilogy(ks, mx, color=cols[w], lw=1.0, label=wl.LABEL[w] + (" (odd)" if S["windows"][w]["mirrored"] else " (+1 run)"))
    ax.axhline(THR_A2, **fs.GUIDE, label="U-A2 0.02")
    ax.axvline(KMAX2_FRAC * kmax, **fs.MASK_LINE)
    ax.set_xlabel(r"$k/dk$")
    ax.set_ylabel(r"$|{\cal R}^{\rm NR}/(W{\cal R}\alpha L^{-3/2})-1|$ at $N_f$")
    ax.legend(loc="lower right", fontsize=7)
    fs.save(fig, os.path.join(fd, f"fig_{tag}_mode_errors"))
    plt.close(fig)
    # ---- 2. shell power shift at the last dump against the baseline
    ks = np.sqrt(modes.shell_n2)
    fig, ax = plt.subplots(2, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 5.6), sharex=True)
    fig.subplots_adjust(left=0.15, right=0.97, top=0.97, bottom=0.10, hspace=0.08)
    for w in present:
        if w == "b":
            continue
        ax[0].plot(ks, D[f"dnr_{w}"], ".", ms=2.5, color=cols[w], label=wl.LABEL[w])
        ax[0].plot(ks, D[f"dlin_{w}"], color=cols[w], lw=0.8)
        ax[1].semilogy(ks, np.maximum(np.abs(D[f"dnr_{w}"]), 1e-12), ".", ms=2.5, color=cols[w])
        ax[1].semilogy(ks, D[f"err_{w}"], color=cols[w], lw=0.8)
    ax[0].axhline(0.0, **fs.THIN)
    ax[0].set_ylabel(r"$P_w/P_b-1$ (dots NR, lines linear)")
    ax[0].legend(loc="upper left", fontsize=8, ncol=2)
    ax[1].axhline(2e-3, **fs.GUIDE, label="W3a 2e-3 (k <= k_max/2)")
    ax[1].axvline(KMAX2_FRAC * kmax, **fs.MASK_LINE)
    ax[1].set_ylabel(r"$|P_w/P_b-1|$ (dots); $|e_w|+|e_b|$ (lines)")
    ax[1].set_xlabel(r"$k/dk$ (shell)")
    ax[1].legend(loc="upper left", fontsize=8)
    fs.save(fig, os.path.join(fd, f"fig_{tag}_shift_Nf"))
    plt.close(fig)
    # ---- 3. passage: shell power in time for four shells, NR vs each window's reference
    picks = [2, 6, 12, 24] if kmax >= 24 else [1, 2, 4, 8]
    fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 6.0), sharex=True)
    fig.subplots_adjust(left=0.09, right=0.98, top=0.96, bottom=0.09, hspace=0.12, wspace=0.22)
    for axx, kk in zip(axs.ravel(), picks):
        j = int(np.argmin(np.abs(ks - kk)))
        sel = modes.shell_of == j
        kfac = ks[j]**3 * wl.L_BOX**3 / (2 * np.pi**2)
        if usr:
            axx.axvspan(wl.USR_ON, wl.USR_OFF, color=fs.PAL["yellow"], alpha=0.15, lw=0)
        for w in present:
            pr = kfac * (np.abs(D["ref"][w][:, sel])**2).mean(axis=1)
            pn = kfac * (np.abs(D["O"][w][:, sel])**2).mean(axis=1)
            axx.semilogy(cN, np.maximum(pr, 1e-30), color=cols[w], lw=1.0)
            axx.semilogy(cN, np.maximum(pn, 1e-30), "o", ms=3, mfc="none", color=cols[w],
                         label=wl.LABEL[w])
        axx.set_title(f"shell |n|^2 = {modes.shell_n2[j]} (k = {ks[j]:.2f} dk, {sel.sum()} modes)",
                      fontsize=9)
    axs[0, 0].legend(loc="lower right", fontsize=7)
    for axx in axs[1]:
        axx.set_xlabel(r"$N-N_*$")
    for axx in axs[:, 0]:
        axx.set_ylabel(r"$k^3L^3\langle|c_n|^2\rangle/(2\pi^2)$")
    fs.save(fig, os.path.join(fd, f"fig_{tag}_passage"))
    plt.close(fig)
    # ---- 4. passage residual and linear shift in time
    fig, ax = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 3.6))
    fig.subplots_adjust(left=0.14, right=0.97, top=0.96, bottom=0.14)
    half = k <= KMAX2_FRAC * kmax
    if usr:
        ax.axvspan(wl.USR_ON, wl.USR_OFF, color=fs.PAL["yellow"], alpha=0.15, lw=0)
    for w in present:
        if w == "b":
            continue
        ax.semilogy(cN, np.maximum(D[f"res_t_{w}"][:, half].max(axis=1), 1e-16), "o-", ms=3,
                    color=cols[w], label=wl.LABEL[w] + ": NR shift - linear shift")
        ax.semilogy(cN, np.maximum(D[f"lin_t_{w}"][:, half].max(axis=1), 1e-16), color=cols[w],
                    ls="--", lw=1.0)
    ax.axhline(THR_A2, **fs.GUIDE)
    ax.set_xlabel(r"$N-N_*$")
    ax.set_ylabel(r"max$_{k\leq k_{max}/2}$ / max$_t|{\rm ref}_w|$ (dashed: linear shift)")
    ax.legend(loc="lower right", fontsize=7)
    fs.save(fig, os.path.join(fd, f"fig_{tag}_passage_residual"))
    plt.close(fig)
    # ---- 5. one-point rms of W R in time
    fig, ax = plt.subplots(2, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 5.6), sharex=True)
    fig.subplots_adjust(left=0.15, right=0.97, top=0.97, bottom=0.10, hspace=0.08)
    for x in ax:
        if usr:
            x.axvspan(wl.USR_ON, wl.USR_OFF, color=fs.PAL["yellow"], alpha=0.15, lw=0)
    for w in present:
        rn, rr = D[f"rms_{w}"]
        ax[0].semilogy(cN, rr, color=cols[w], lw=1.0)
        ax[0].semilogy(cN, rn, "o", ms=3, mfc="none", color=cols[w], label=wl.LABEL[w])
        ax[1].plot(cN[1:], rn[1:] / rr[1:] - 1.0, "o-", ms=3, color=cols[w])
    ax[0].set_ylabel(r"one-point rms of $W{\cal R}$ (o NR, - linear)")
    ax[0].legend(loc="lower right", fontsize=8)
    ax[1].axhline(0.0, **fs.THIN)
    ax[1].set_ylabel("NR / linear - 1")
    ax[1].set_xlabel(r"$N-N_*$")
    fs.save(fig, os.path.join(fd, f"fig_{tag}_onepoint"))
    plt.close(fig)
    # ---- 6. even part
    if any(f"EO_t_{w}" in D for w in present):
        fig, ax = plt.subplots(2, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 5.6))
        fig.subplots_adjust(left=0.15, right=0.97, top=0.97, bottom=0.10, hspace=0.30)
        if usr:
            ax[0].axvspan(wl.USR_ON, wl.USR_OFF, color=fs.PAL["yellow"], alpha=0.15, lw=0)
        for w in present:
            if f"EO_t_{w}" in D:
                ax[0].semilogy(cN[1:], D[f"EO_t_{w}"][1:], "o-", ms=3, color=cols[w], label=wl.LABEL[w])
                ev = np.abs(D["E"][w][-1]) / np.abs(D["ref"][w][-1])
                ax[1].semilogy(k, np.maximum(ev, 1e-16), ".", ms=1.5, color=cols[w], alpha=0.5,
                               rasterized=True)
        ax[0].set_ylabel("rms |E| / rms |O| (over modes)")
        ax[0].set_xlabel(r"$N-N_*$")
        ax[0].legend(loc="upper left", fontsize=8)
        ax[1].set_ylabel(r"$|E|/|{\rm ref}|$ per mode at $N_f$")
        ax[1].set_xlabel(r"$k/dk$")
        fs.save(fig, os.path.join(fd, f"fig_{tag}_even"))
        plt.close(fig)
    # ---- 7. constraint records
    fig, ax = plt.subplots(2, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 5.6), sharex=True)
    fig.subplots_adjust(left=0.15, right=0.97, top=0.97, bottom=0.10, hspace=0.08)
    for x in ax:
        if usr:
            x.axvspan(wl.USR_ON, wl.USR_OFF, color=fs.PAL["yellow"], alpha=0.15, lw=0)
    for w in present:
        cw = D[f"con_{w}"]
        ax[0].semilogy(cw[:, 2], cw[:, 3], color=cols[w], lw=1.0, label=wl.LABEL[w])
        ax[1].semilogy(cw[:, 2], cw[:, 6], color=cols[w], lw=1.0)
    ax[0].set_ylabel(r"$\langle|{\cal H}|/[{\cal H}]\rangle$ (+1 runs)")
    ax[1].set_ylabel(r"$\langle|{\cal M}|/[{\cal M}]\rangle$")
    ax[1].set_xlabel(r"$N-N_*$ (from $\langle\chi\rangle$)")
    ax[0].legend(loc="upper right", fontsize=8)
    fs.save(fig, os.path.join(fd, f"fig_{tag}_constraints"))
    plt.close(fig)


if __name__ == "__main__":
    main()
