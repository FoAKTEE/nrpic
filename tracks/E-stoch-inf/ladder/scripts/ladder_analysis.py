#!/usr/bin/env python3
"""Analysis of the SR ladder runs (package tracks/E-stoch-inf/ladder).

    ladder_analysis.py extract RUNDIR --nmesh N --nmax2 M --modefile F --scale S --out NPZ
        per dump: R^NR_n (when the dump has the metric), the linear reference
        s L^-3/2 W R alpha_n, constraint statistics of the dump (rms and mean of H, rms |M|);
        A1 from the record: box means of phi, Pi, K against the reference background
    ladder_analysis.py pair RUN_P RUN_M --scale S --out JSON
        odd and even parts under s -> -s of H and M_i at common dumps
    ladder_analysis.py judge NPZ --out JSON
        A2 at the last dump, A3 freezing, shell spectrum, against the thresholds of
        SCOPE 4 (restated in ../JOURNAL.md, entry 1)

Definitions: ../JOURNAL.md entry 1 and ladder_lib.py.
"""
import argparse
import json
import os

import numpy as np

import ladder_lib as LL


def jdump(obj, path):
    def conv(o):
        if isinstance(o, (np.floating, np.integer)):
            return o.item()
        if isinstance(o, np.ndarray):
            return o.tolist()
        raise TypeError(type(o))
    with open(path, "w") as fp:
        json.dump(obj, fp, indent=1, default=conv)


# ---------------------------------------------------------------------------- extract
def extract(a):
    dumps = LL.dump_list(a.run)
    if not dumps:
        raise SystemExit(f"no dumps in {a.run}")
    names = LL.read_header(dumps[0])["names"]
    has_metric = "gxx" in names
    has_con = "H" in names
    modes = LL.Modes(a.nmesh, a.nmax2)
    t_dumps = [LL.read_header(f)["time"] for f in dumps]
    con = LL.read_con(a.run)
    t_end = max(max(t_dumps), con[-1, 0]) + 0.05
    ref = LL.reference_for(modes, a.modefile, t_end, t_eval=t_dumps)
    alpha = modes.alpha()
    kshell = np.sqrt(modes.shell_n2.astype(float))
    # the reference with the stencil's k^2 (SCOPE 4, A2) for the modes of A2
    sub = np.nonzero(modes.n2 <= a.nmax2 / 4.0)[0]
    ref_st = LL.reference_modes_stencil(modes, a.modefile, t_end, t_dumps, sub)
    lin_st_all = []
    out = dict(times=[], cycles=[], efolds_dump=[], efolds_ref=[], rmsH=[], meanH=[],
               rmsM=[], aniso_rms_rel=[])
    rnr_all, lin_all, w_all = [], [], []
    for f in dumps:
        h = LL.read_header(f)
        want = (LL.CURV_VARS if has_metric else ["chi"]) + \
            (["H", "Mx", "My", "Mz"] if has_con else [])
        _, flds = LL.read_dump(f, want)
        t = h["time"]
        out["times"].append(t)
        out["cycles"].append(h["cycle"])
        out["efolds_dump"].append(-0.5 * np.log(flds["chi"].mean()))
        out["efolds_ref"].append(float(ref.background(t)["lna"]))
        if has_con:
            out["rmsH"].append(float(np.sqrt(np.mean(flds["H"]**2))))
            out["meanH"].append(float(flds["H"].mean()))
            out["rmsM"].append(float(np.sqrt(np.mean(flds["Mx"]**2 + flds["My"]**2 +
                                                      flds["Mz"]**2))))
        rk, _ = ref.modes(t)
        w = ref.window(t, kshell)
        lin = a.scale * LL.L_BOX**-1.5 * (w * rk)[modes.shell_of] * alpha
        lin_all.append(lin)
        w_all.append(w[modes.shell_of])
        rs, _ = ref_st.modes(t)
        lin_st_all.append(a.scale * LL.L_BOX**-1.5 * ref_st.window(t, modes.k[sub]) * rs
                          * alpha[sub])
        if has_metric:
            rnr, aniso, _ = LL.curvature(modes, flds)
            rnr_all.append(rnr)
            out["aniso_rms_rel"].append(float(np.sqrt(np.mean(np.abs(aniso)**2) /
                                                      np.mean(np.abs(rnr)**2))))
        del flds
    _, nk_shell, hk_shell, e1k_shell = ref.crossing(kshell, t_end)
    # A1 from the record
    bg = ref.background(con[:, 0])
    a1 = dict(phi=np.abs(con[:, 16] / bg["phi"] - 1.0), Pi=np.abs(con[:, 17] / bg["Pi"] - 1.0),
              K=np.abs(con[:, 18] / bg["K"] - 1.0),
              efolds=np.abs(con[:, 2] - bg["lna"]))
    out["A1_max"] = {k: float(v.max()) for k, v in a1.items()}
    out["con_time"] = con[:, 0]
    out["con_efolds_ref"] = bg["lna"]
    np.savez(a.out, n=modes.n, n2=modes.n2, shell_n2=modes.shell_n2,
             shell_of=modes.shell_of, alpha=alpha,
             rnr=np.array(rnr_all) if has_metric else np.zeros((0, modes.M)),
             lin=np.array(lin_all), w=np.array(w_all),
             sub_stencil=sub, lin_stencil=np.array(lin_st_all),
             kshell=kshell, Nk=nk_shell, Hk=hk_shell, eps1k=e1k_shell,
             con=con, a1_phi=a1["phi"], a1_Pi=a1["Pi"], a1_K=a1["K"],
             **{k: np.array(v) for k, v in out.items() if k not in ("A1_max",)})
    summ = {k: v for k, v in out.items() if k not in ("con_time", "con_efolds_ref")}
    summ.update(run=a.run, nmesh=a.nmesh, nmax2=a.nmax2, scale=a.scale, modes=modes.M,
                shells=int(modes.shell_n2.size), has_metric=has_metric, has_con=has_con,
                con_max_H_ratio=float(con[:, 3].max()), con_max_M_ratio=float(con[:, 6].max()))
    jdump(summ, os.path.splitext(a.out)[0] + ".json")
    print(json.dumps({k: summ[k] for k in ("run", "modes", "A1_max", "con_max_H_ratio",
                                            "con_max_M_ratio")}, indent=1, default=float))


# ------------------------------------------------------------------------------- pair
def pair(a):
    dp, dm = LL.dump_list(a.run_p), LL.dump_list(a.run_m)
    n = min(len(dp), len(dm))
    cp, cm = LL.read_con(a.run_p), LL.read_con(a.run_m)
    rows = []
    for i in range(n):
        hp, fp = LL.read_dump(dp[i], ["H", "Mx", "My", "Mz"])
        hm, fm = LL.read_dump(dm[i], ["H", "Mx", "My", "Mz"])
        if hp["cycle"] != hm["cycle"]:
            raise SystemExit(f"cycle mismatch at dump {i}: {hp['cycle']} {hm['cycle']}")
        cyc = hp["cycle"]
        rowp = cp[np.nonzero(cp[:, 1] == cyc)[0][0]]
        rowm = cm[np.nonzero(cm[:, 1] == cyc)[0][0]]
        hmag, mmag = 0.5 * (rowp[9] + rowm[9]), 0.5 * (rowp[10] + rowm[10])
        ho = 0.5 * (fp["H"] - fm["H"])
        he = 0.5 * (fp["H"] + fm["H"])
        mo = [0.5 * (fp[c] - fm[c]) for c in ("Mx", "My", "Mz")]
        me = [0.5 * (fp[c] + fm[c]) for c in ("Mx", "My", "Mz")]
        rows.append(dict(
            dump=i, cycle=cyc, time=hp["time"], efolds=float(rowp[2]),
            Hmag=hmag, Mmag=mmag,
            H_odd=float(np.sqrt(np.mean(ho**2)) / hmag),
            H_even=float(np.sqrt(np.mean((he - he.mean())**2)) / hmag),
            H_even_mean=float(he.mean() / hmag),
            M_odd=float(np.sqrt(np.mean(sum(x**2 for x in mo))) / mmag),
            M_even=float(np.sqrt(np.mean(sum((x - x.mean())**2 for x in me))) / mmag),
            ratio_H_p=float(rowp[3]), ratio_H_m=float(rowm[3]),
            ratio_M_p=float(rowp[6]), ratio_M_m=float(rowm[6])))
        del fp, fm, ho, he, mo, me
    res = dict(run_p=a.run_p, run_m=a.run_m, scale=a.scale, rows=rows)
    jdump(res, a.out)
    for r in rows:
        print(f"{r['time']:6.2f} N={r['efolds']:5.2f}  H odd {r['H_odd']:.3e} even "
              f"{r['H_even']:.3e} mean {r['H_even_mean']:+.2e}   M odd {r['M_odd']:.3e} "
              f"even {r['M_even']:.3e}")


# ------------------------------------------------------------------------------ judge
def judge(a):
    z = np.load(a.npz)
    rnr, lin, w = z["rnr"], z["lin"], z["w"]
    if rnr.shape[0] == 0:
        raise SystemExit("no metric in the dumps: nothing to judge")
    t, nd = z["times"], z["efolds_ref"]
    n2, shell_of, kshell, nk = z["n2"], z["shell_of"], z["kshell"], z["Nk"]
    nmax2 = int(n2.max())
    k = np.sqrt(n2.astype(float))
    nk_mode = nk[shell_of]
    last = -1
    nf = float(nd[last])
    d = np.abs(rnr / lin - 1.0)
    q = np.abs(rnr)**2 / np.abs(lin)**2
    res = dict(npz=a.npz, N_f=nf, t_f=float(t[last]), modes=int(n2.size))
    # A2
    sel_half = n2 <= nmax2 / 4.0
    res["A2"] = dict(threshold=0.02, max_D_half=float(d[last, sel_half].max()),
                     median_D_half=float(np.median(d[last, sel_half])),
                     n_half=int(sel_half.sum()), max_D_all=float(d[last].max()),
                     worst_n2_half=int(n2[sel_half][np.argmax(d[last, sel_half])]),
                     pass_=bool(d[last, sel_half].max() < 0.02))
    sub = z["sub_stencil"]
    d_st = np.abs(rnr[:, sub] / z["lin_stencil"] - 1.0)
    res["A2"].update(stencil_reference=dict(
        max_D_half=float(d_st[last].max()), median_D_half=float(np.median(d_st[last])),
        n=int(sub.size), pass_=bool(d_st[last].max() < 0.02),
        max_rel_diff_references=float(np.abs(z["lin_stencil"][last] / lin[last, sub] - 1).max())))
    # A2 history (modes with W > 1/2)
    hist = []
    for i in range(len(t)):
        s_in = w[i] > 0.5
        hist.append(dict(time=float(t[i]), efolds=float(nd[i]), n_in=int(s_in.sum()),
                         max_D_in=float(d[i, s_in].max()) if s_in.any() else None,
                         max_D_in_half=float(d[i, s_in & sel_half].max())
                         if (s_in & sel_half).any() else None))
    res["A2_history"] = hist
    # A3
    sel3 = (nf - nk_mode) >= 6.0
    a3 = dict(threshold=0.01, drift_threshold=2.5e-3, n_modes=int(sel3.sum()))
    if sel3.any():
        idx = np.nonzero(sel3)[0]
        ratio = np.empty(idx.size)
        drift_nr = np.empty(idx.size)
        drift_lin = np.empty(idx.size)
        for j, m in enumerate(idx):
            n4 = nk_mode[m] + 4.0
            qi = np.interp(n4, nd, q[:, m])
            ratio[j] = q[last, m] / qi - 1.0
            use = nd >= n4 - 1e-9
            if use.sum() >= 3:
                drift_nr[j] = np.polyfit(nd[use], np.log(np.abs(rnr[use, m])**2), 1)[0]
                drift_lin[j] = np.polyfit(nd[use], np.log(np.abs(lin[use, m])**2), 1)[0]
            else:
                drift_nr[j] = drift_lin[j] = np.nan
        a3.update(max_abs_ratio_minus_1=float(np.abs(ratio).max()),
                  max_abs_drift_nr=float(np.nanmax(np.abs(drift_nr))),
                  max_abs_drift_lin=float(np.nanmax(np.abs(drift_lin))),
                  max_abs_drift_difference=float(np.nanmax(np.abs(drift_nr - drift_lin))),
                  n2_max=int(n2[idx].max()),
                  pass_=bool(np.abs(ratio).max() < 0.01 and
                             np.nanmax(np.abs(drift_nr)) < 2.5e-3))
        np.savez(os.path.splitext(a.out)[0] + "_a3.npz", idx=idx, ratio=ratio,
                 drift_nr=drift_nr, drift_lin=drift_lin, n2=n2[idx], nk=nk_mode[idx])
    res["A3"] = a3
    # spectrum by shell at N_f
    ns = kshell.size
    cnt = np.bincount(shell_of, minlength=ns)
    p_nr = np.bincount(shell_of, weights=np.abs(rnr[last])**2, minlength=ns) / cnt
    p_lin = np.bincount(shell_of, weights=np.abs(lin[last])**2, minlength=ns) / cnt
    p_lin_ens = np.bincount(shell_of, weights=np.abs(lin[last] / z["alpha"])**2,
                            minlength=ns) / cnt
    fac = kshell**3 * LL.L_BOX**3 / (2.0 * np.pi**2)
    dl_nr, dl_lin, dl_ens = fac * p_nr, fac * p_lin, fac * p_lin_ens
    # slow-roll formula at crossing: H_k^2/(8 pi^2 eps1_k Mpl^2), H in units of H*
    d_sr = LL.H_STAR_PLANCK**2 * z["Hk"]**2 / (8.0 * np.pi**2 * z["eps1k"])
    low = kshell <= 7.0
    res["spectrum"] = dict(
        shell_ratio_alpha_corrected_max_dev=float(np.abs(p_nr[kshell <= np.sqrt(nmax2) / 2]
                                                         / p_lin[kshell <= np.sqrt(nmax2) / 2]
                                                         - 1).max()),
        frac_shells_beyond_3sigma=float(np.mean(np.abs(dl_nr / dl_ens - 1) >
                                                3.0 / np.sqrt(cnt))),
        lin_over_sr_k_le_7=[float((dl_ens / d_sr)[low].min()), float((dl_ens / d_sr)[low].max())])
    np.savez(os.path.splitext(a.out)[0] + "_spec.npz", k=kshell, cnt=cnt, d_nr=dl_nr,
             d_lin=dl_lin, d_ens=dl_ens, d_sr=d_sr, nk=nk)
    jdump(res, a.out)
    print(json.dumps({k: v for k, v in res.items() if k != "A2_history"}, indent=1,
                     default=float))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("extract")
    e.add_argument("run")
    e.add_argument("--nmesh", type=int, required=True)
    e.add_argument("--nmax2", type=int, required=True)
    e.add_argument("--modefile", required=True)
    e.add_argument("--scale", type=float, default=1.0)
    e.add_argument("--out", required=True)
    p = sub.add_parser("pair")
    p.add_argument("run_p")
    p.add_argument("run_m")
    p.add_argument("--scale", type=float, default=1.0)
    p.add_argument("--out", required=True)
    j = sub.add_parser("judge")
    j.add_argument("npz")
    j.add_argument("--out", required=True)
    a = ap.parse_args()
    {"extract": extract, "pair": pair, "judge": judge}[a.cmd](a)


if __name__ == "__main__":
    main()
