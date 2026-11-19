#!/usr/bin/env python3
"""Analysis of test U of tracks/core/JOURNAL-scalar3.md (runs of u1_usr.py or of a card
list with the same run names): the inflection (ultra-slow-roll) case against the
ordinary differential equations.

    python3 u2_usr_analysis.py --data DIR [DIR ...] [--out DIR] [--nmax2 64]
                               [--pairs p1:m1:1,p01:m01:0.1] [--prefix ""]

Every DIR holds run directories (p1, m1, p01, m01, z0, c0125, z0c0125, ctl; missing ones
are skipped).  With --prefix X the directories are X + name.
  background  box means of <basename>.sf.hst against nrpic.scalar_field.ms_reference
              (SciPy); lockstep background; Courant 0.25 against 0.125
  modes       lockstep mode functions of the .modes records against the reference
  constraints records <basename>.sf.con.hst; odd and even parts in the mode scale s of
              the constraint fields of the dumps
  rnr         R^NR per mode against L^(-3/2) W R alpha of the lockstep record
Writes OUT/summary.json and OUT/fig_usr_background.png, fig_usr_constraints.png,
fig_usr_rnr.png."""
import argparse
import os

import s3
from s3 import common, inf, np, sf

BASE = "usr"


def find(dirs, name, prefix=""):
    for d in dirs:
        p = os.path.join(d, prefix + name)
        if os.path.isdir(p) and os.path.exists(os.path.join(p, BASE + ".sf.hst")):
            return p
    return None


def at(x, y, x0):
    """Value of y at the first x >= x0 (None beyond the record)."""
    i = int(np.searchsorted(x, x0))
    return float(y[i]) if i < len(x) else None


def classes(q, ent, qtop):
    return (("n_le_2", ent & (q <= 2.0 + 1e-9)), ("n_le_4", ent & (q <= 4.0 + 1e-9)),
            ("top_shell", ent & (q >= qtop - 1e-9)), ("all_in", ent))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", nargs="+", required=True)
    ap.add_argument("--out")
    ap.add_argument("--nmax2", type=int, default=64)
    ap.add_argument("--pairs", default="p1:m1:1,p01:m01:0.1")
    ap.add_argument("--prefix", default="")
    ap.add_argument("--modefile", help="mode file of the runs (default: the reference "
                    "integrated from the Bunch-Davies time, as u1_usr.py)")
    a = ap.parse_args()
    out = s3.run_dir(a.out)
    dirs = [os.path.abspath(d) for d in a.data]
    case = s3.case("usr", 1)
    v, dv, phi0, pi0 = inf.code_background(case)
    if a.modefile:
        sh_n2, sh_r, sh_dr = inf.read_mode_file(a.modefile)
    else:
        cm = s3.case("usr", a.nmax2)
        sh_n2, sh_r, sh_dr = cm["n2"], cm["R"], cm["dR"]
    keep = sh_n2 <= a.nmax2
    sh_n2, sh_r, sh_dr = sh_n2[keep], sh_r[keep], sh_dr[keep]
    names = ["p1", "m1", "p01", "m01", "p001", "m001", "z0", "c0125", "z0c0125", "ctl"]
    rd = {k: find(dirs, k, a.prefix) for k in names}
    rd = {k: p for k, p in rd.items() if p}
    summ = dict(data=dirs, runs=rd, nmax2=a.nmax2,
                case={k: case[k] for k in ("phi0", "pi0", "lambda", "vev", "eps1",
                                           "eps2", "h_star_planck")})
    hist = {k: sf.read_history(os.path.join(p, BASE + ".sf.hst")) for k, p in rd.items()}
    con = {k: sf.read_con_history(os.path.join(p, BASE + ".sf.con.hst"))
           for k, p in rd.items() if os.path.exists(os.path.join(p, BASE + ".sf.con.hst"))}

    # ------------------------------------------------------------------ background
    bgs = {}
    for k, h in hist.items():
        t = h["time"]
        ref = sf.ms_reference(v, dv, phi0, pi0, [1], [0j], [0j], s3.LENGTH, t)
        e = dict(time=t, efolds=ref["ln_a"],
                 phi=np.abs(h["phi"]/ref["phi"] - 1.0),
                 Pi=np.abs(h["Pi"]/ref["Pi"] - 1.0),
                 K=np.abs(h["K"]/(-3.0*ref["H"]) - 1.0),
                 efold=np.abs(-0.5*np.log(h["chi"]) - ref["ln_a"]),
                 lock_Pi=np.abs(h["Pi"]/h["Pi_b"] - 1.0),
                 lock_phi=np.abs(h["phi"]/h["phi_b"] - 1.0),
                 lockref_Pi=np.abs(h["Pi_b"]/ref["Pi"] - 1.0),
                 eps1_mesh=4.0*np.pi*h["Pi"]**2/(h["K"]/3.0)**2,
                 eps1=ref["eps1"], eps2=ref["eps2"], H=ref["H"])
        bgs[k] = e
        s = dict(t_end=float(t[-1]), efolds_end=float(ref["ln_a"][-1]),
                 steps=int(t.size - 1))
        for q in ("phi", "Pi", "K", "efold", "lock_Pi", "lock_phi", "lockref_Pi"):
            s["max_" + q] = float(e[q].max())
            for ne in (3.0, 5.0, 8.0):
                s[f"{q}_at_{ne:g}"] = at(ref["ln_a"], e[q], ne)
            s[q + "_end"] = float(e[q][-1])
        s["eps1_min_ref"] = float(ref["eps1"].min())
        s["eps2_max_ref"] = float(ref["eps2"].max())
        usr = ref["ln_a"][ref["eps2"] > 3.0]
        s["usr_from_to"] = [float(usr.min()), float(usr.max())] if usr.size else None
        s["H_end"] = float(ref["H"][-1])
        summ.setdefault("background", {})[k] = s
    # Courant 0.25 against 0.125 at equal times (every second record of the fine run)
    for co, fi in (("z0", "z0c0125"), ("p1", "c0125")):
        if co in bgs and fi in bgs:
            nco = bgs[co]["time"].size - 2      # the last step may be cut at tlim
            r = {}
            for q in ("phi", "Pi", "K", "efold"):
                ec, ef = bgs[co][q][1:nco], bgs[fi][q][2:2*nco:2]
                ok = ef > 1e-13
                r[q + "_ratio_median"] = float(np.median(ec[ok]/ef[ok])) if ok.any() \
                    else None
                r[q + "_ratio_end"] = float(ec[-1]/ef[-1]) if ef[-1] > 0 else None
            summ.setdefault("courant_ratio", {})[co + "/" + fi] = r

    # ------------------------------------------------------------------ mode functions
    n, n2 = sf.mode_set(a.nmax2)
    al = sf.mode_alpha(s3.SEED, 0, 0, n)
    q = np.sqrt(n2.astype(float))
    qtop = np.sqrt(float(sh_n2.max()))
    modes = {}
    for k in ("p1", "c0125", "p01", "p001"):
        if k not in rd:
            continue
        dd = s3.dumps(rd[k], BASE)
        cyc = sorted(dd)
        times = np.array([dd[c]["time"] for c in cyc])
        scale = dict(p1=1.0, c0125=1.0, p01=0.1, p001=0.01)[k]
        ref = sf.ms_reference(v, dv, phi0, pi0, sh_n2, sh_r, sh_dr, s3.LENGTH,
                              times[1:])
        rows = []
        for it, c in enumerate(cyc[1:]):
            head, tab = sf.read_modes(dd[c]["file"].replace(".dump", ".modes"))
            rl = (tab[:, 1] + 1j*tab[:, 2])/scale
            sh = tab[:, 0].astype(int)
            rr = ref["R"][it][np.searchsorted(sh_n2, sh)]
            dev = np.abs(rl/rr - 1.0)
            qs = np.sqrt(sh.astype(float))
            rows.append(dict(time=float(times[it+1]), efolds=float(ref["ln_a"][it]),
                             dev_n_le_2=float(dev[qs <= 2.0 + 1e-9].max()),
                             dev_top=float(dev[qs >= qtop - 1e-9].max()),
                             dev_max=float(dev.max()),
                             absR_first=float(np.abs(rr[0])),
                             absR_top=float(np.abs(rr[-1])),
                             dev_all=dev, absR=np.abs(rr), absR_lock=np.abs(rl), q=qs))
        modes[k] = rows
        summ.setdefault("modes", {})[k] = [
            {kk: vv for kk, vv in r.items() if not isinstance(vv, np.ndarray)}
            for r in rows]
    if "p1" in modes and "c0125" in modes:
        # dumps of the two runs are at the first step at or after each multiple of the
        # dump interval: close in time, not equal
        rat = []
        for r1, r2 in zip(modes["p1"], modes["c0125"]):
            rat.append(dict(efolds=r1["efolds"], time_coarse=r1["time"],
                            time_fine=r2["time"],
                            ratio_n_le_2=r1["dev_n_le_2"]/r2["dev_n_le_2"],
                            ratio_top=r1["dev_top"]/r2["dev_top"]))
        summ["modes_courant_ratio"] = rat

    # ------------------------------------------------------------------ constraints
    cs = {}
    for k, c in con.items():
        ne = c["efolds"]
        i_h, i_m = int(np.argmax(c["H_ratio"])), int(np.argmax(c["M_ratio"]))
        s = dict(H_ratio_max=float(c["H_ratio"][i_h]), H_ratio_max_efolds=float(ne[i_h]),
                 M_ratio_max=float(c["M_ratio"][i_m]), M_ratio_max_efolds=float(ne[i_m]),
                 H_ratio_t0=float(c["H_ratio"][0]), M_ratio_t0=float(c["M_ratio"][0]))
        early = ne <= 3.0
        s["M_ratio_max_to_3"] = float(c["M_ratio"][early].max())
        s["H_ratio_max_to_3"] = float(c["H_ratio"][early].max())
        late = ne >= 4.0
        if late.any():
            s["H_ratio_max_from_4"] = float(c["H_ratio"][late].max())
            s["M_ratio_max_from_4"] = float(c["M_ratio"][late].max())
            s["M_ratio_min_from_4"] = float(c["M_ratio"][late].min())
        for x in (0.5, 1.0, 2.0, 3.0, 4.0, 6.0, 8.0, 10.0):
            s[f"H_ratio_at_{x:g}"] = at(ne, c["H_ratio"], x)
            s[f"M_ratio_at_{x:g}"] = at(ne, c["M_ratio"], x)
            s[f"H_mag_at_{x:g}"] = at(ne, c["H_mag"], x)
            s[f"M_mag_at_{x:g}"] = at(ne, c["M_mag"], x)
        cs[k] = s
    summ["constraints"] = cs
    if "z0" in con and "z0c0125" in con:
        c1, c2 = con["z0"], con["z0c0125"]
        nco = c1["time"].size - 2
        r = c1["H_ratio"][1:nco]/np.maximum(c2["H_ratio"][2:2*nco:2], 1e-300)
        sel = (c1["efolds"][1:nco] > 0.5) & (c1["efolds"][1:nco] < 3.0)
        summ["z0_courant_ratio_H_median_0p5_to_3"] = float(np.median(r[sel]))

    # odd and even parts of the constraint fields
    pairs = []
    for spec in a.pairs.split(","):
        kp, km, sc = spec.split(":")
        if kp in rd and km in rd:
            pairs.append((kp, km, float(sc)))
    dz = s3.dumps(rd["z0"], BASE) if "z0" in rd else {}
    parts = {}
    rnr_rows = {}
    for kp, km, sc in pairs:
        dp, dm = s3.dumps(rd[kp], BASE), s3.dumps(rd[km], BASE)
        rows, rrows = [], []
        for c in sorted(set(dp) & set(dm)):
            fp, fm = dp[c]["fields"], dm[c]["fields"]
            row = dict(cycle=c, time=float(dp[c]["time"]), scale=sc)
            if "H" in fp:
                h0 = dz[c]["fields"]["H"] if c in dz else 0.0
                oh = 0.5*(fp["H"] - fm["H"])
                eh = 0.5*(fp["H"] + fm["H"]) - h0
                om = [0.5*(fp[x] - fm[x]) for x in ("Mx", "My", "Mz")]
                em = [0.5*(fp[x] + fm[x]) for x in ("Mx", "My", "Mz")]
                row.update(H_odd=s3.rms(oh), H_even=s3.rms(eh),
                           H0=float(np.mean(h0)) if c in dz else None,
                           H0_std=float(np.std(h0)) if c in dz else None,
                           M_odd=float(np.sqrt(sum((x*x).mean() for x in om))),
                           M_even=float(np.sqrt(sum((x*x).mean() for x in em))))
            if "gxx" in fp and "gxx" in fm:
                rp, mp = s3.rnr_of_dump(dp[c], n, n2)
                rm, _ = s3.rnr_of_dump(dm[c], n, n2)
                ref, w, head, _ = s3.lock_reference(dp[c]["file"], n2)
                ref = ref*al
                ent = w > 0.5
                odd = 0.5*(rp - rm)
                rr = dict(cycle=c, time=float(dp[c]["time"]),
                          efolds=float(np.log(head["a"])), scale=sc,
                          modes_in=int(ent.sum()), eps1=float(head["eps1"]),
                          eps2=float(head["eps2"]),
                          rms_rnr=float(np.sqrt(2.0*(np.abs(rp)**2).sum())),
                          rms_ref=float(np.sqrt(2.0*(np.abs(ref)**2).sum())))
                for lab, sel in classes(q, ent, qtop):
                    if sel.any():
                        rr["single_" + lab] = float(np.abs(rp/ref - 1.0)[sel].max())
                        rr["odd_" + lab] = float(np.abs(odd/ref - 1.0)[sel].max())
                        rr["even_" + lab] = float(np.abs(0.5*(rp + rm)/ref)[sel].max())
                sel = w > 1e-3
                rr["single_w_gt_1e-3"] = float(np.abs(rp/ref - 1.0)[sel].max())
                rr["dev_odd"] = np.abs(odd/ref - 1.0)
                rr["dev_single"] = np.abs(rp/ref - 1.0)
                rr["w"] = w
                rr["means"] = mp
                rrows.append(rr)
            rows.append(row)
        parts[kp] = rows
        rnr_rows[kp] = rrows
        summ.setdefault("parts", {})[kp + "/" + km] = rows
        summ.setdefault("rnr", {})[kp + "/" + km] = [
            {kk: vv for kk, vv in r.items() if not isinstance(vv, np.ndarray)}
            for r in rrows]
    # ratios between the two amplitudes at equal cycles
    if len(pairs) == 2:
        (ka, _, sa), (kb, _, sb) = pairs
        ra = {r["cycle"]: r for r in parts[ka]}
        rat = []
        for r in parts[kb]:
            if r["cycle"] in ra and "H_odd" in r:
                x = ra[r["cycle"]]
                rat.append(dict(cycle=r["cycle"], time=r["time"],
                                H_odd=x["H_odd"]/r["H_odd"], M_odd=x["M_odd"]/r["M_odd"],
                                H_even=x["H_even"]/r["H_even"],
                                M_even=x["M_even"]/r["M_even"],
                                H_odd_small=r["H_odd"], M_odd_small=r["M_odd"]))
        summ["part_ratios"] = dict(amplitude_ratio=sa/sb, rows=rat)
    # negative control
    if "ctl" in rd:
        dc = s3.dumps(rd["ctl"], BASE)
        rows = []
        for c in sorted(dc):
            if "gxx" not in dc[c]["fields"]:
                break
            rp, _ = s3.rnr_of_dump(dc[c], n, n2)
            ref, w, head, _ = s3.lock_reference(dc[c]["file"], n2)
            ent = w > 0.5
            if ent.any():
                rows.append(dict(time=float(dc[c]["time"]),
                                 efolds=float(np.log(head["a"])),
                                 dev_min=float(np.abs(rp/(ref*al) - 1.0)[ent].min()),
                                 dev_max=float(np.abs(rp/(ref*al) - 1.0)[ent].max())))
        summ["control_rnr"] = rows
    common.dump_json(summ, os.path.join(out, "summary.json"))

    # ------------------------------------------------------------------ figures
    fs = common.style()
    import matplotlib.pyplot as plt
    from matplotlib import cm
    B, R_, G, O, Y = (fs.PAL[x] for x in ("blue", "red", "green", "orange", "yellow"))

    # background and mode functions
    fig, ax = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.6))
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.09, top=0.97, wspace=0.27,
                        hspace=0.27)
    kb = "z0" if "z0" in bgs else next(iter(bgs))
    e = bgs[kb]
    ax[0, 0].plot(e["efolds"], e["eps1"], color=B, label=r"$\varepsilon_1$, reference")
    ax[0, 0].plot(e["efolds"][::8], e["eps1_mesh"][::8], ".", ms=3, color=R_,
                  label=r"$\varepsilon_1$, box means")
    ax[0, 0].plot(e["efolds"], np.abs(e["eps2"]), color=G,
                  label=r"$|\varepsilon_2|$, reference")
    ax[0, 0].axhline(3.0, **fs.MASK_LINE)
    ax[0, 0].set_yscale("log")
    ax[0, 0].set_xlabel("e-folds after $N_*$")
    ax[0, 0].set_ylabel("slow-roll parameters")
    ax[0, 0].legend(loc="lower left", fontsize=7)
    for k, ls in (("z0", "-"), ("z0c0125", "--")):
        if k not in bgs:
            continue
        e = bgs[k]
        lab = "Courant 0.25" if k == "z0" else "Courant 0.125"
        ax[0, 1].plot(e["efolds"][1:], np.maximum(e["Pi"][1:], 1e-16), ls, color=R_,
                      label=r"$\langle\Pi\rangle$, " + lab)
        ax[0, 1].plot(e["efolds"][1:], np.maximum(e["phi"][1:], 1e-16), ls, color=B,
                      label=r"$\langle\phi\rangle$" if k == "z0" else None)
        ax[0, 1].plot(e["efolds"][1:], np.maximum(e["K"][1:], 1e-16), ls, color=G,
                      label=r"$\langle K\rangle$" if k == "z0" else None)
        ax[0, 1].plot(e["efolds"][1:], np.maximum(e["efold"][1:], 1e-16), ls, color=O,
                      label=r"e-folds (abs.)" if k == "z0" else None)
    ax[0, 1].axhline(1e-4, **fs.MASK_LINE)
    ax[0, 1].set_yscale("log")
    ax[0, 1].set_xlabel("e-folds after $N_*$")
    ax[0, 1].set_ylabel("box mean against the reference")
    ax[0, 1].legend(loc="lower right", fontsize=6.5, ncol=2)
    if "p1" in modes:
        rows = modes["p1"]
        ne = np.array([r["efolds"] for r in rows])
        qs = rows[0]["q"]
        pick = [0, int(np.argmin(np.abs(qs - 2.0))), int(np.argmin(np.abs(qs - 4.0))),
                qs.size - 1]
        for i, cl in zip(pick, (B, G, O, R_)):
            ax[1, 0].plot(ne, [r["absR"][i] for r in rows], color=cl,
                          label=f"$|n|={qs[i]:.0f}$")
            ax[1, 0].plot(ne, [r["absR_lock"][i] for r in rows], "o", ms=3, mfc="none",
                          color=cl)
        ax[1, 0].set_yscale("log")
        ax[1, 0].set_xlabel("e-folds after $N_*$")
        ax[1, 0].set_ylabel(r"$|R_k|$: reference (lines), code (circles)")
        ax[1, 0].legend(loc="upper left", fontsize=7)
        for k, ls in (("p1", "-"), ("c0125", "--")):
            if k not in modes:
                continue
            rows = modes[k]
            ne = np.array([r["efolds"] for r in rows])
            lab = "Courant 0.25" if k == "p1" else "Courant 0.125"
            ax[1, 1].plot(ne, [r["dev_n_le_2"] for r in rows], ls, color=B,
                          label=r"$|n|\leq2$, " + lab)
            ax[1, 1].plot(ne, [r["dev_top"] for r in rows], ls, color=R_,
                          label="top shell, " + lab)
        ax[1, 1].set_yscale("log")
        ax[1, 1].set_xlabel("e-folds after $N_*$")
        ax[1, 1].set_ylabel(r"$|R_k^{\rm code}/R_k^{\rm ref}-1|$")
        ax[1, 1].legend(loc="lower right", fontsize=6.5)
    fig.savefig(os.path.join(out, "fig_usr_background.png"), dpi=200)
    plt.close(fig)

    # constraints
    fig, ax = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.6))
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.09, top=0.97, wspace=0.27,
                        hspace=0.27)
    sty = dict(p1=(B, "-", "$s=1$"), p01=(G, "-", "$s=0.1$"), p001=(G, ":", "$s=0.01$"),
               z0=(O, "-", "$s=0$"), c0125=(B, "--", "$s=1$, Courant 0.125"),
               z0c0125=(O, "--", "$s=0$, Courant 0.125"), ctl=(R_, "-", "control"))
    for k, (cl, ls, lab) in sty.items():
        if k not in con:
            continue
        c = con[k]
        ax[0, 0].plot(c["efolds"][1:], np.maximum(c["H_ratio"][1:], 1e-18), ls,
                      color=cl, label=lab)
        if k not in ("z0", "z0c0125"):
            ax[0, 1].plot(c["efolds"][1:], np.maximum(c["M_ratio"][1:], 1e-18), ls,
                          color=cl, label=lab)
    ax[0, 0].set_yscale("log")
    ax[0, 0].set_xlabel("e-folds after $N_*$")
    ax[0, 0].set_ylabel(r"$\langle|\mathcal{H}|/[\mathcal{H}]\rangle$")
    ax[0, 0].legend(loc="upper right", fontsize=6.5, ncol=2)
    ax[0, 1].set_yscale("log")
    ax[0, 1].set_xlabel("e-folds after $N_*$")
    ax[0, 1].set_ylabel(r"$\langle|\mathcal{M}|/[\mathcal{M}]\rangle$")
    ax[0, 1].legend(loc="lower right", fontsize=6.5)
    for (kp, km, sc), ls in zip(pairs, ("-", "--")):
        rows = [r for r in parts[kp] if "H_odd" in r]
        if not rows:
            continue
        hk = hist[kp]
        ne = np.interp([r["time"] for r in rows], hk["time"], hk["ln_a"])
        ax[1, 0].plot(ne, [r["H_odd"]/sc for r in rows], ls, color=B,
                      label=f"odd$/s$, $s={sc:g}$")
        ax[1, 0].plot(ne, [r["H_even"]/sc**2 for r in rows], ls, color=R_,
                      label=f"(even$-H_0)/s^2$, $s={sc:g}$")
        if ls == "-" and rows[0]["H0"] is not None:
            ax[1, 0].plot(ne[1:], [abs(r["H0"]) for r in rows[1:]], "-", color=O,
                          label=r"$|H_0|$ ($s=0$)")
        ax[1, 1].plot(ne, [r["M_odd"]/sc for r in rows], ls, color=B,
                      label=f"odd$/s$, $s={sc:g}$")
        ax[1, 1].plot(ne, [r["M_even"]/sc**2 for r in rows], ls, color=R_,
                      label=f"even$/s^2$, $s={sc:g}$")
    for j, lab in ((0, r"rms parts of $\mathcal{H}$"), (1, r"rms parts of $|\mathcal{M}|$")):
        ax[1, j].set_yscale("log")
        ax[1, j].set_xlabel("e-folds after $N_*$")
        ax[1, j].set_ylabel(lab)
        ax[1, j].legend(loc="upper right", fontsize=6.5)
    fig.savefig(os.path.join(out, "fig_usr_constraints.png"), dpi=200)
    plt.close(fig)

    # curvature perturbation
    fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.075, right=0.99, bottom=0.15, top=0.95, wspace=0.3)
    small = pairs[-1][0] if pairs else None
    if small and rnr_rows.get(small):
        rows = rnr_rows[small]
        cols = cm.viridis(np.linspace(0.0, 0.92, len(rows)))
        for r, cl in zip(rows[::2], cols[::2]):
            sel = r["w"] > 0.5
            ax[0].plot(q[sel], r["dev_odd"][sel], ".", ms=2, color=cl,
                       label=f"$N={r['efolds']:.1f}$")
        ax[0].set_yscale("log")
        ax[0].set_xlabel(r"$|n|$")
        ax[0].set_ylabel(r"odd part of $R^{\rm NR}_n$ against $W R\,\alpha_n$, "
                         f"$s=\\pm{pairs[-1][2]:g}$")
        ax[0].legend(loc="lower right", fontsize=5.5, ncol=3)
    for j, (kp, km, sc) in enumerate(pairs[:2]):
        rows = rnr_rows[kp]
        if not rows:
            continue
        ne = [r["efolds"] for r in rows]
        for lab, cl, lbl in (("n_le_2", B, r"$|n|\leq2$"), ("n_le_4", G, r"$|n|\leq4$"),
                             ("top_shell", R_, "top shell")):
            ax[1 + j].plot(ne, [r.get("odd_" + lab, np.nan) for r in rows], "-",
                           color=cl, label=lbl + ", odd part")
            ax[1 + j].plot(ne, [r.get("single_" + lab, np.nan) for r in rows], "--",
                           color=cl, label=lbl + f", run $s={sc:g}$")
        ax[1 + j].axhline(2e-2, **fs.MASK_LINE)
        ax[1 + j].set_yscale("log")
        ax[1 + j].set_xlabel("e-folds after $N_*$")
        ax[1 + j].set_ylabel(f"largest deviation, $s=\\pm{sc:g}$")
        ax[1 + j].legend(loc="lower right", fontsize=5.5)
    fig.savefig(os.path.join(out, "fig_usr_rnr.png"), dpi=200)
    plt.close(fig)
    print("U analysis done:", os.path.join(out, "summary.json"))


if __name__ == "__main__":
    main()
