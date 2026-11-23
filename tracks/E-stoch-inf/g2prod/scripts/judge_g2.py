#!/usr/bin/env python3
"""SCOPE 4c (G2 criteria of the USR case) judged on the g2prod analyses, as written, nothing
excluded; and the predictions of g2prod/JOURNAL.md entry 1 for the USR runs.

    python3 judge_g2.py --a G2A_DIR --b SEEDB_DIR --r U320_DIR --scout SCOUT_DIR \
        --runs label=rundir ... --out OUT [--no-control]

G2A_DIR, SEEDB_DIR, U320_DIR: outputs of analyse_g2.py (summary.json, coeffs_N*.npz);
SCOUT_DIR: the scouting pair analysis E-20261121-101756-6bffd0c (coeffs_N256.npz, summary.json);
--runs: every g2prod chain (records, U-A4'(c)) and nc/ap/am for the control (U-A4'(d)).
Writes OUT/judge_g2.json and OUT/fig/fig_g2_*.png.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "usr", "scripts"))
import card_lib as cl  # noqa: E402
import figstyle as fs  # noqa: E402
import usr_lib as ul  # noqa: E402

ENTRY_CN = float(np.log(32.0))
USR = (2.5235, 6.5503)


def load(d):
    return json.load(open(os.path.join(d, "summary.json")))


def floor_halving(c1, ch, lab):
    o1, oh = np.array(c1[lab + "_odd_abs"]), np.array(ch[lab + "_odd_abs"])
    e1, eh = np.array(c1[lab + "_even_abs"]), np.array(ch[lab + "_even_abs"])
    f2 = np.maximum(0.0, (4.0 * oh**2 - o1**2) / 3.0)
    f = np.sqrt(f2)
    corr = np.sqrt(np.maximum(e1**2 - f2, 0.0)) / np.sqrt(np.maximum(eh**2 - f2, 1e-300))
    return dict(o1=o1, oh=oh, e1=e1, eh=eh, f=f, corr=corr, f_over_oh=f / np.maximum(oh, 1e-300),
                sel_a=eh > 3.0 * f, sel_b=oh > 3.0 * f)


def control(runs):
    """Odd part of H of the sign-flip control U256nc against that of the proper pair (ap, am)."""
    dn, da, dm = (cl.dump_list(runs[k]) for k in ("U256nc", "U256ap", "U256am"))
    rows = []
    for p in dn:
        h = ul.read_header(p)
        t = h["time"]
        ia = [i for i, q in enumerate(da) if abs(ul.read_header(q)["time"] - t) <= 1e-9]
        if not ia:
            rows.append(dict(t=t, cycle=h["cycle"], matched=False))
            continue
        i = ia[0]
        _, fn = cl.read_fields(p, ["H"])
        _, fa = cl.read_fields(da[i], ["H"])
        _, fm = cl.read_fields(dm[i], ["H"])
        hn = fn["H"] - fn["H"].mean()
        ho = 0.5 * (fa["H"] - fm["H"])
        ho = ho - ho.mean()
        hx = 0.5 * (fn["H"] - fm["H"])
        hx = hx - hx.mean()
        rows.append(dict(t=t, cycle=h["cycle"], matched=True,
                         proper_odd=float(np.sqrt(np.mean(ho * ho))),
                         nc_single=float(np.sqrt(np.mean(hn * hn))),
                         nc_cross=float(np.sqrt(np.mean(hx * hx)))))
        del fn, fa, fm, hn, ho, hx
    con = cl.read_con(os.path.join(runs["U256nc"], "usr.sf.con.hst"))
    cmap = {int(r[cl.C["cycle"]]): float(r[cl.C["efolds"]]) for r in con}
    for r in rows:
        r["cN"] = cmap.get(int(r["cycle"]))
    m = [r for r in rows if r["matched"] and r["cN"] is not None and 0 < r["cN"] <= ENTRY_CN + 1e-12]
    out = dict(rows=rows, entry_cN=ENTRY_CN, n_judged=len(m))
    if m:
        po = max(r["proper_odd"] for r in m)
        out["ratio_max_single"] = max(r["nc_single"] for r in m) / po
        out["ratio_max_cross"] = max(r["nc_cross"] for r in m) / po
        out["ratio_decides"] = min(out["ratio_max_single"], out["ratio_max_cross"])
        out["pointwise_single"] = [r["nc_single"] / r["proper_odd"] for r in m]
        out["pointwise_cross"] = [r["nc_cross"] / r["proper_odd"] for r in m]
        out["pass"] = bool(out["ratio_decides"] >= 1e3)
    return out


def shell_power(c, shell_of):
    return np.bincount(shell_of, weights=np.abs(c)**2) / np.bincount(shell_of)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--r", required=True)
    ap.add_argument("--scout", required=True)
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--no-control", action="store_true")
    a = ap.parse_args()
    os.makedirs(os.path.join(a.out, "fig"), exist_ok=True)
    runs = dict(x.split("=", 1) for x in a.runs)
    SA, SB, SR, SS = load(a.a), load(a.b), load(a.r), load(a.scout)
    V = {}
    # ------------------------------------------------ U-A0, U-A1, U-A3 per run, U-A2' per pair
    per_run = {}
    for tag, S, names in (("A", SA, ("U256", "U256m", "U256h", "U256hm")), ("B", SB, ("U256", "U256m")),
                          ("R320", SR, ("U256", "U256m"))):
        for n in names:
            s = S[n]
            dN = max(abs(x["dN"]) for x in s["U_A0_landmarks"])
            a1 = max(s["U_A1_phi_rel_max"], s["U_A1_Pi_rel_max"], s["U_A1_K_rel_max"])
            a3 = s["U_A3_power_ratio_k_le_3"]
            per_run[f"{tag}:{n}"] = dict(s=s["s"], U_A0_max_dN=dN, U_A0_pass=bool(dN < 1e-5), U_A1_max=a1,
                                         U_A1_pass=bool(a1 < 1e-3), U_A3=a3,
                                         U_A3_pass=bool(abs(a3["min"] - 1) <= 0.1 and abs(a3["max"] - 1) <= 0.1),
                                         U_A2_single_max_end=s["U_A2"]["max_end"],
                                         rms_R_end=s["rms_R_end"], lock_max_end=s["lock_max_end"],
                                         onepoint_end=(s["onepoint"][-1]["full"] if "onepoint" in s else None))
    V["per_run"] = per_run
    pairs = {}
    for tag, S, key in (("A", SA, "U256_U256m"), ("A_half", SA, "U256h_U256hm"), ("B", SB, "U256_U256m"),
                        ("R320", SR, "U256_U256m"), ("scout", SS, "U256_U256m")):
        P = S[key]
        pairs[tag] = dict(UA2p_max=P["U_A2s"]["max_end"], UA2p_pass=bool(P["U_A2s"]["max_end"] < 0.02),
                          max_all_modes=P["U_A2s"]["max_all_modes_end"],
                          even_over_odd_kmask=P["U_A2s"]["even_over_odd_rms_end_kmask"],
                          UA2n_end=P["U_A2n_even_over_odd_end"], UA2n_max=P["U_A2n_even_over_odd_max"],
                          UA2n_pass=bool(P["U_A2n_even_over_odd_max"] < 0.3),
                          UA3_odd=P["U_A3_odd_power_ratio_k_le_3"],
                          shell_max={int(k): v for k, v in P["U_A2s_shell_max_end"].items()})
    V["pairs"] = pairs
    # ------------------------------------------------ release vs scouting, per mode (seed A, s = +-1)
    za = np.load(os.path.join(a.a, "coeffs_N256.npz"))
    zs = np.load(os.path.join(a.scout, "coeffs_N256.npz"))
    rv = dict(times_equal=bool(za["t"].shape == zs["t"].shape and np.abs(za["t"] - zs["t"]).max() <= 1e-9))
    if rv["times_equal"]:
        for n in ("U256", "U256m"):
            cn, cs = za[f"c_{n}"], zs[f"c_{n}"]
            rms = np.sqrt(np.mean(np.abs(cs[-1])**2))
            rv[n] = dict(max_abs_diff_over_rms_end=float(np.max(np.abs(cn[-1] - cs[-1])) / rms),
                         max_abs_diff_over_rms_all=float(np.max(np.abs(cn - cs) / np.sqrt(np.mean(np.abs(cs)**2, axis=1))[:, None])))
    V["release_vs_scouting"] = rv
    # ------------------------------------------------ U-A4'(a), (b): floor and even halving (seed A)
    c1, ch = SA["U256_U256m"]["constraints"], SA["U256h_U256hm"]["constraints"]
    cN = np.array(c1["cN"])
    hal = dict(cN=cN.tolist())
    for lab in ("H", "M"):
        r = floor_halving(c1, ch, lab)
        selA = r["sel_a"].copy()             # every dump, the initial one included (clause on the maxima)
        selAB = selA & r["sel_b"]
        d = dict(f=r["f"].tolist(), f_over_oh=r["f_over_oh"].tolist(), corr=r["corr"].tolist(),
                 raw_even=(r["e1"] / r["eh"]).tolist(), raw_odd=(r["o1"] / r["oh"]).tolist(),
                 sel_a=selA.tolist(), sel_ab=selAB.tolist())
        for nm, sel in (("a_text", selA), ("a_and_b", selAB)):
            x = r["corr"][sel]
            d[nm] = dict(n=int(sel.sum()), min=float(x.min()) if x.size else None, max=float(x.max()) if x.size else None,
                         outside=[float(v) for v in x[np.abs(x - 4.0) > 0.05]],
                         outside_cN=[float(v) for v in cN[sel][np.abs(x - 4.0) > 0.05]],
                         pass_=bool(x.size and np.all(np.abs(x - 4.0) <= 0.05)))
        hal[lab] = d
    V["UA4a_b"] = hal
    hk = SA.get("halving_U256_over_U256h", {})
    V["R_halving"] = dict(R_odd_end=hk.get("R_odd", [None])[-1], R_even_end=hk.get("R_even", [None])[-1])
    # ------------------------------------------------ U-A4'(c): records of every run
    rec = {}
    for lab, d in runs.items():
        con = cl.read_con(os.path.join(d, "usr.sf.con.hst"))
        rec[lab] = dict(Hp_max=float(con[1:, cl.C["Hp_ratio"]].max()), M_max=float(con[1:, cl.C["M_ratio"]].max()),
                        H_abs_max=float(con[1:, cl.C["H_ratio"]].max()), rows=int(con.shape[0]),
                        t_end=float(con[-1, 0]), efolds_end=float(con[-1, cl.C["efolds"]]))
        rec[lab]["pass"] = bool(rec[lab]["Hp_max"] < 1e-9 and rec[lab]["M_max"] < 1e-1)
    V["UA4c_records"] = rec
    # ------------------------------------------------ U-R
    zr = np.load(os.path.join(a.r, "coeffs_N320.npz"))
    same_modes = bool(np.array_equal(zr["n"], za["n"]))
    UR = dict(same_modes=same_modes, t_end_256=float(za["t"][-1]), t_end_320=float(zr["t"][-1]))
    UR["i_factor"] = pairs["A"]["UA2p_max"] / pairs["R320"]["UA2p_max"]
    UR["i_pass"] = bool(2.0 <= UR["i_factor"] <= 4.5)
    if same_modes and abs(UR["t_end_256"] - UR["t_end_320"]) <= 1e-9:
        n2 = (za["n"]**2).sum(axis=1)
        sh_n2, shell_of = np.unique(n2, return_inverse=True)
        p256 = shell_power(za["c_U256"][-1], shell_of)
        p320 = shell_power(zr["c_U256"][-1], shell_of)
        rat = p320 / p256 - 1.0
        k = np.sqrt(sh_n2)
        lo = k <= 32.0 + 1e-9
        UR["ii_max_k_le_32"] = float(np.abs(rat[lo]).max())
        UR["ii_max_to_64"] = float(np.abs(rat).max())
        UR["ii_pass"] = bool(UR["ii_max_k_le_32"] <= 1e-3 and UR["ii_max_to_64"] <= 1e-2)
        UR["_rat"] = rat.tolist()
        UR["_k"] = k.tolist()
        # per shell odd-part D maxima at N_f, 256 and 320
    # an observation, not a criterion: the part of the odd-part error at N_f common to all modes
    for tag, z in (("256", za), ("320", zr)):
        q = 0.5 * (z["c_U256"][-1] - z["c_U256m"][-1]) / z["cref"][-1] - 1.0
        lo = (z["n"]**2).sum(axis=1) <= 256
        UR[f"common_mode_{tag}"] = dict(k_le=16, mean_re=float(np.mean(q.real[lo])), mean_im=float(np.mean(q.imag[lo])),
                                        std_re=float(np.std(q.real[lo])), std_im=float(np.std(q.imag[lo])),
                                        median_abs=float(np.median(np.abs(q[lo]))))
    q_t = 0.5 * (za["c_U256"] - za["c_U256m"]) / za["cref"] - 1.0
    lo = (za["n"]**2).sum(axis=1) <= 256
    UR["common_mode_t_256"] = dict(cN=za["cN"].tolist(), mean_re=q_t.real[:, lo].mean(axis=1).tolist(),
                                   std_re=q_t.real[:, lo].std(axis=1).tolist(),
                                   median_abs=np.median(np.abs(q_t[:, lo]), axis=1).tolist())
    e256, e320 = pairs["A"]["UA2n_end"], pairs["R320"]["UA2n_end"]
    UR["iii_even_odd_256"], UR["iii_even_odd_320"] = e256, e320
    UR["iii_rel"] = abs(e320 / e256 - 1.0)
    UR["iii_kmask_256"], UR["iii_kmask_320"] = pairs["A"]["even_over_odd_kmask"], pairs["R320"]["even_over_odd_kmask"]
    UR["iii_kmask_rel"] = abs(UR["iii_kmask_320"] / UR["iii_kmask_256"] - 1.0)
    UR["iii_pass"] = bool(UR["iii_rel"] <= 0.05 and UR["iii_kmask_rel"] <= 0.05)
    V["U_R"] = UR
    # ------------------------------------------------ U-S
    ob = per_run["B:U256"]["onepoint_end"]
    obm = per_run["B:U256m"]["onepoint_end"]
    US = dict(UA2p=pairs["B"]["UA2p_max"], UA2p_pass=pairs["B"]["UA2p_pass"],
              UA3_pass=per_run["B:U256"]["U_A3_pass"] and per_run["B:U256m"]["U_A3_pass"],
              rms_bp=ob["rms"] if ob else None, rms_bm=obm["rms"] if obm else None,
              skew_bp=ob["skew"] if ob else None, skew_bm=obm["skew"] if obm else None, lattice_ref=0.89366)
    if ob:
        US["rms_pass"] = bool(abs(ob["rms"] - 0.89366) <= 5e-3 and abs(obm["rms"] - 0.89366) <= 5e-3)
    V["U_S"] = US
    # ------------------------------------------------ U-A4'(d)
    if not a.no_control and all(k in runs for k in ("U256nc", "U256ap", "U256am")):
        V["UA4d_control"] = control(runs)
    with open(os.path.join(a.out, "judge_g2.json"), "w") as fp:
        json.dump(V, fp, indent=1, default=float)
    short = {k: v for k, v in V.items()}
    short["U_R"] = {k: v for k, v in UR.items() if not k.startswith("_")}
    print(json.dumps(short, indent=1, default=float)[:12000])

    # ================================================= figures
    fs.use_style()
    import matplotlib.pyplot as plt
    cols = fs.series_colors(6)
    # U-A2' per shell
    fig, ax = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 3.4))
    fig.subplots_adjust(left=0.14, right=0.97, top=0.96, bottom=0.14)
    for (tag, lab), col in zip((("scout", "scouting pair 256 (core_scalar-3)"), ("A", "seed A 256, release"),
                                ("B", "seed B 256, release"), ("A_half", "seed A 256, s=1/2"),
                                ("R320", "seed A 320, release")), cols):
        sm = pairs[tag]["shell_max"]
        k2 = np.array(sorted(sm))
        ax.semilogy(np.sqrt(k2), [sm[x] for x in k2], lw=0.8, color=col, label=lab)
    ax.axhline(0.02, **fs.GUIDE, label="U-A2' bar 0.02")
    ax.axvline(32.0, **fs.MASK_LINE)
    ax.set_xlabel(r"$|n| = k/dk$ of the shell")
    ax.set_ylabel(r"odd part: shell max $D_n$ at $N_f$")
    ax.legend(loc="upper left", fontsize=6, ncol=2)
    fs.save(fig, os.path.join(a.out, "fig", "fig_g2_ua2"))
    plt.close(fig)
    # U-A4'(a),(b)
    fig, ax = plt.subplots(2, 2, figsize=(fs.COLUMN_WIDTH * 2.0, 5.2), sharex=True)
    fig.subplots_adjust(left=0.09, right=0.98, top=0.95, bottom=0.1, hspace=0.12, wspace=0.28)
    for j, lab in enumerate(("H", "M")):
        d = hal[lab]
        x = ax[0, j]
        x.axvspan(USR[0], USR[1], color=fs.PAL["yellow"], alpha=0.15, lw=0)
        x.axhspan(3.95, 4.05, color="0.85", lw=0)
        corr = np.array(d["corr"])
        sa, sab = np.array(d["sel_a"]), np.array(d["sel_ab"])
        x.plot(cN[1:], np.array(d["raw_even"])[1:], "s", mfc="none", ms=3, color=cols[1], label="even, raw")
        x.plot(cN[1:], corr[1:], "o", ms=2, color="0.5", label="even, floor removed (all)")
        x.plot(cN[sa], corr[sa], "o", ms=4, color=cols[0], label=r"judged: $e_{1/2}>3f$")
        x.plot(cN[sab], corr[sab], "x", ms=5, color=cols[3], label=r"and $o_{1/2}>3f$")
        x.set_ylim(0, 6)
        x.set_title(f"{lab}: s=1 over s=1/2", fontsize=8)
        x.legend(loc="lower left", fontsize=5.5)
        y = ax[1, j]
        y.axvspan(USR[0], USR[1], color=fs.PAL["yellow"], alpha=0.15, lw=0)
        y.semilogy(cN[1:], np.maximum(np.array(d["f_over_oh"])[1:], 1e-6), "o-", ms=2.5, color=cols[2], label=r"$f/o_{1/2}$")
        y.semilogy(cN[1:], np.maximum((np.array(d["f"]) / np.maximum(np.array(ch[lab + "_even_abs"]), 1e-300))[1:], 1e-6),
                   "s--", ms=2.5, color=cols[4], label=r"$f/e_{1/2}$")
        y.axhline(1.0 / 3.0, **fs.GUIDE)
        y.set_xlabel(r"$N-N_*$")
        y.legend(loc="upper left", fontsize=6)
    ax[0, 0].set_ylabel("halving factor")
    ax[1, 0].set_ylabel("floor fraction")
    fs.save(fig, os.path.join(a.out, "fig", "fig_g2_halving"))
    plt.close(fig)
    # U-R
    fig, ax = plt.subplots(2, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 5.2))
    fig.subplots_adjust(left=0.15, right=0.97, top=0.97, bottom=0.09, hspace=0.32)
    if "_rat" in UR:
        ax[0].semilogy(UR["_k"], np.maximum(np.abs(UR["_rat"]), 1e-12), ".", ms=2, color=cols[0])
        ax[0].plot([0, 32], [1e-3, 1e-3], **fs.GUIDE)
        ax[0].plot([32, 64], [1e-2, 1e-2], **fs.GUIDE)
        ax[0].set_xlabel(r"$|n|$ of the shell")
        ax[0].set_ylabel(r"|shell power 320/256 - 1| at $N_f$")
    sa, sr = pairs["A"]["shell_max"], pairs["R320"]["shell_max"]
    k2 = np.array(sorted(sa))
    rat = np.array([sa[x] / sr[x] for x in k2])
    ax[1].plot(np.sqrt(k2), rat, ".", ms=2.5, color=cols[2], label="shell max D: 256 / 320")
    ax[1].axhspan(2.0, 4.5, color="0.88", lw=0)
    ax[1].axhline((320 / 256)**4, color=cols[4], lw=0.8, ls="--", label="(320/256)^4")
    ax[1].axhline((320 / 256)**6, color=cols[5], lw=0.8, ls=":", label="(320/256)^6")
    ax[1].axvline(32.0, **fs.MASK_LINE)
    ax[1].set_xlabel(r"$|n|$ of the shell")
    ax[1].set_ylabel("factor")
    ax[1].legend(loc="upper right", fontsize=6)
    fs.save(fig, os.path.join(a.out, "fig", "fig_g2_resolution"))
    plt.close(fig)
    # observation: common-mode part of the odd-part error (k <= 16 dk) in time, seed A at 256^3
    ct = UR["common_mode_t_256"]
    fig, ax = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 3.2))
    fig.subplots_adjust(left=0.15, right=0.97, top=0.96, bottom=0.15)
    ax.axvspan(USR[0], USR[1], color=fs.PAL["yellow"], alpha=0.15, lw=0)
    c_ = np.array(ct["cN"])
    ax.semilogy(c_[1:], np.abs(np.array(ct["mean_re"]))[1:], "o-", ms=3, color=cols[0], label="|mean Re(O/c_ref - 1)|, k<=16")
    ax.semilogy(c_[1:], np.array(ct["std_re"])[1:], "s--", ms=3, color=cols[2], label="scatter (std) over the modes")
    ax.semilogy(c_[1:], np.array(ct["median_abs"])[1:], "x:", ms=4, color=cols[4], label="median |O/c_ref - 1|")
    for tag, mk, col in (("256", "D", cols[1]), ("320", "^", cols[3])):
        cm = UR[f"common_mode_{tag}"]
        ax.semilogy([c_[-1] + (0.1 if tag == "320" else 0.0)], [abs(cm["mean_re"])], mk, ms=5, color=col, label=f"N_f, {tag}^3")
    ax.set_xlabel(r"$N-N_*$")
    ax.set_ylabel("odd-part error, seed A")
    ax.legend(loc="lower right", fontsize=6)
    fs.save(fig, os.path.join(a.out, "fig", "fig_g2_common_mode"))
    plt.close(fig)
    # U-A4'(c) records
    fig, ax = plt.subplots(2, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 5.6), sharex=True)
    fig.subplots_adjust(left=0.15, right=0.97, top=0.97, bottom=0.09, hspace=0.08)
    rc = fs.series_colors(len(runs))
    for (lab, d), col in zip(sorted(runs.items()), rc):
        con = cl.read_con(os.path.join(d, "usr.sf.con.hst"))
        e = con[1:, cl.C["efolds"]]
        ax[0].semilogy(e, con[1:, cl.C["Hp_ratio"]], lw=0.7, color=col, label=lab)
        ax[1].semilogy(e, con[1:, cl.C["M_ratio"]], lw=0.7, color=col)
    ax[0].axhline(1e-9, **fs.GUIDE)
    ax[1].axhline(1e-1, **fs.GUIDE)
    for x in ax:
        x.axvspan(USR[0], USR[1], color=fs.PAL["yellow"], alpha=0.15, lw=0)
    ax[0].set_ylabel(r"$\langle|H'|/[H]\rangle$ (record)")
    ax[1].set_ylabel(r"$\langle|M|/[M]\rangle$ (record)")
    ax[1].set_xlabel(r"$N-N_*$")
    ax[0].legend(loc="lower right", fontsize=5.5, ncol=3)
    fs.save(fig, os.path.join(a.out, "fig", "fig_g2_records"))
    plt.close(fig)
    # U-A4'(d)
    if "UA4d_control" in V:
        rows = [r for r in V["UA4d_control"]["rows"] if r["matched"] and r["cN"] is not None]
        fig, ax = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 3.2))
        fig.subplots_adjust(left=0.14, right=0.97, top=0.96, bottom=0.15)
        c = np.array([r["cN"] for r in rows])
        for key, lab, col, mk in (("proper_odd", "proper pair: odd part of H", cols[0], "o"),
                                  ("nc_single", "control: H - <H>", cols[3], "s"),
                                  ("nc_cross", "control: (H_nc - H_am)/2", cols[4], "x")):
            ax.semilogy(c[1:], np.array([r[key] for r in rows])[1:], marker=mk, ms=4, lw=0.8, color=col, label=lab)
        ax.axvline(ENTRY_CN, **fs.MASK_LINE)
        ax.set_xlabel(r"$N-N_*$")
        ax.set_ylabel("rms of H (code units)")
        ax.legend(loc="lower right", fontsize=6)
        fs.save(fig, os.path.join(a.out, "fig", "fig_g2_control"))
        plt.close(fig)


if __name__ == "__main__":
    main()
