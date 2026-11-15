#!/usr/bin/env python3
"""Test T1 of tracks/core/JOURNAL-scalar2.md: the initial slice of the stochastic-
inflation runs at t = 0 (pgen scalar_field, id = stochastic).

    python3 t1_slice.py --exe EXE --out DIR [--workers 12]

Runs problems/scalar/sr_stochastic.athinput for zero steps with the mode functions
scaled by s = +-1, +-1/2, +-1/4 (corrected and printed delta Pi), with the continuum k^2
at N = 16 and 32, and without the window; then compares the dumped slice with the Python
twin (nrpic.sf_inflation.slice_transfer), the constraint ratios with their order in s,
and the odd part of the constraint fields with the linear predictions.
Writes DIR/summary.json and DIR/fig_slice.png."""
import argparse
import os

import common
from common import inf, np
from nrpic import scalar_field as sf

INP = os.path.join(common.PROB, "sr_stochastic.athinput")
SEED = 20261115
NMAX2 = 64


def load(rundir):
    d = sf.read_dump(os.path.join(rundir, "sr.sf.00000.dump"))
    h = sf.read_con_history(os.path.join(rundir, "sr.sf.con.hst"))
    return d["fields"], {k: v[0] for k, v in h.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=12)
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    case = common.sr_case(NMAX2)
    base = common.write_case(case, out) + ["time/nlim=0", "scalar_field/dump_dt=1.0",
                                           "scalar_field/dump_noise=false"]
    v, dv, phi0, pi0 = inf.code_background(case)
    length = case["length"]

    def tag(s):
        return ("p" if s > 0 else "m") + f"{abs(s):g}".replace(".", "")

    runs = {}
    cases = []

    def add(name, n, nmax2, s, extra):
        runs[name] = dict(n=n, nmax2=nmax2, s=s)
        cases.append((os.path.join(out, name), INP,
                      base + common.mesh_args(n) + [f"scalar_field/noise_nmax2={nmax2}",
                                                    f"scalar_field/noise_mode_scale={s}"]
                      + extra))

    scales = [1.0, -1.0, 0.5, -0.5, 0.25, -0.25]
    for s in scales:
        add("cor_" + tag(s), 32, NMAX2, s, [])
        add("prt_" + tag(s), 32, NMAX2, s, ["problem/slice_delta_pi=printed"])
    for s in (1.0, -1.0):
        add("con16_" + tag(s), 16, 16, s, ["problem/slice_k2=continuum"])
        add("ste16_" + tag(s), 16, 16, s, [])
        add("con32_" + tag(s), 32, NMAX2, s, ["problem/slice_k2=continuum"])
    for s in (1.0, 0.5):
        add("now_" + tag(s), 32, NMAX2, s, ["problem/slice_window=false"])
    walls = common.run_many(a.exe, cases, a.workers)
    data = {name: load(os.path.join(out, name)) for name in runs}
    summ = dict(exe=os.path.abspath(a.exe), case={k: case[k] for k in (
        "phi0", "pi0", "mass", "h_star_planck", "eps1", "eps2", "length")},
        wall_s=sum(walls), runs=len(walls))

    # ---- P1a: the slice against the twin
    n, n2 = sf.mode_set(NMAX2)
    al = sf.mode_alpha(SEED, 0, 0, n)
    kb = -np.sqrt(24.0*np.pi*(0.5*pi0*pi0 + v(phi0)))
    twin = {}
    for name, windowed in (("cor_p1", True), ("now_p1", False)):
        f = data[name][0]
        tr = inf.slice_transfer(n, case["n2"], case["R"], case["dR"], length, 32, v, dv,
                                phi0, pi0, windowed=windowed)
        res = {}
        for key, fld in (("phi", f["phi"] - phi0), ("Pi", f["Pi"] - pi0),
                         ("chi", f["chi"] - 1.0), ("K", f["K"] - kb)):
            c, fh = sf.analyse(fld, n)
            ref = tr[key]*al
            rms = np.sqrt((np.abs(ref)**2).mean())
            mask = np.ones(fh.shape, dtype=bool)
            mask[n[:, 0] % 32, n[:, 1] % 32, n[:, 2] % 32] = False
            mask[(-n[:, 0]) % 32, (-n[:, 1]) % 32, (-n[:, 2]) % 32] = False
            res[key] = dict(max_dev_over_rms=np.abs(c - ref).max()/rms, rms_coeff=rms,
                            outside_over_rms=np.abs(fh[mask]).max()/rms,
                            rms_field=fld.std())
            if name == "cor_p1":
                twin[key] = (np.sqrt(n2.astype(float)), np.abs(c), np.abs(ref),
                             np.abs(c - ref))
        g = [f[k] for k in ("gxx", "gyy", "gzz")]
        go = [f[k] for k in ("gxy", "gxz", "gyz")]
        aa = [f[k] for k in ("Axx", "Axy", "Axz", "Ayy", "Ayz", "Azz")]
        res["gt_minus_delta_max"] = max(max(np.abs(x - 1.0).max() for x in g),
                                        max(np.abs(x).max() for x in go))
        res["At_max"] = max(np.abs(x).max() for x in aa)
        res["alpha_minus_1_max"] = np.abs(f["alpha"] - 1.0).max()
        summ["P1a_" + name] = res

    # ---- P1b, P1d: order of the constraint ratios in s
    order = {}
    for fam in ("cor", "prt"):
        hr = [data[f"{fam}_{tag(s)}"][1]["H_ratio"] for s in (1.0, 0.5, 0.25)]
        mr = [data[f"{fam}_{tag(s)}"][1]["M_ratio"] for s in (1.0, 0.5, 0.25)]
        ml = [data[f"{fam}_{tag(s)}"][1]["M_l1"] for s in (1.0, 0.5, 0.25)]
        order[fam] = dict(H_ratio=hr, M_ratio=mr, M_l1=ml,
                          H_ratio_per_halving=[hr[0]/hr[1], hr[1]/hr[2]],
                          M_ratio_per_halving=[mr[0]/mr[1], mr[1]/mr[2]],
                          M_l1_per_halving=[ml[0]/ml[1], ml[1]/ml[2]])
    hr = [data[f"now_{tag(s)}"][1]["H_ratio"] for s in (1.0, 0.5)]
    mr = [data[f"now_{tag(s)}"][1]["M_ratio"] for s in (1.0, 0.5)]
    order["now"] = dict(H_ratio=hr, M_ratio=mr, H_ratio_per_halving=[hr[0]/hr[1]],
                        M_ratio_per_halving=[mr[0]/mr[1]])
    summ["P1b_order"] = order
    summ["mag"] = {k: data["cor_p1"][1][k] for k in ("H_mag", "M_mag", "H_l1", "M_l1",
                                                    "H_rms", "M_rms", "M_bssn_adm")}

    # ---- P1c, P1d, P1e: odd and even parts of the constraint fields
    def parts(fam, s, key):
        p, m = data[f"{fam}_{tag(s)}"][0][key], data[f"{fam}_{tag(-s)}"][0][key]
        return 0.5*(p - m), 0.5*(p + m), p

    odd = {}
    for fam in ("cor", "prt", "con16", "ste16", "con32"):
        res = {}
        for key in ("H", "Mx", "My", "Mz"):
            o, e, p = parts(fam, 1.0, key)
            res[key] = dict(rms_odd=np.sqrt((o*o).mean()), rms_even=np.sqrt((e*e).mean()),
                            rms=np.sqrt((p*p).mean()),
                            even_minus_field_over_rms=np.sqrt(((e - p)**2).mean())
                            / np.sqrt((p*p).mean()))
        odd[fam] = res
    summ["P1c_odd_even"] = odd
    tr = inf.slice_transfer(n, case["n2"], case["R"], case["dR"], length, 32, v, dv, phi0,
                            pi0)
    summ["largest_linear_term_rms"] = float(np.sqrt(2.0*(np.abs(4.0*tr["ksq"]*tr["Psi"]
                                                                * al)**2).sum()))
    # printed delta Pi: coefficients of the odd part of H against -4 eps1 H^2 Psi alpha
    o, e, p = parts("prt", 1.0, "H")
    c, fh = sf.analyse(o, n)
    ref = tr["H_printed"]*al
    rms = np.sqrt((np.abs(ref)**2).mean())
    summ["P1d_printed"] = dict(max_dev_over_rms=np.abs(c - ref).max()/rms, rms_coeff=rms,
                               rms_odd_H=np.sqrt((o*o).mean()),
                               rms_even_H=np.sqrt((e*e).mean()))
    prt = (np.sqrt(n2.astype(float)), np.abs(c), np.abs(ref), np.abs(c - ref))
    # continuum k^2: coefficients of the odd part of H against -4 (k2_stencil - k2) Psi
    con = {}
    for fam, nn, nm2 in (("con16", 16, 16), ("con32", 32, NMAX2)):
        nq, nq2 = sf.mode_set(nm2)
        alq = sf.mode_alpha(SEED, 0, 0, nq)
        trc = inf.slice_transfer(nq, case["n2"], case["R"], case["dR"], length, nn, v, dv,
                                 phi0, pi0, k2="continuum")
        trs = inf.slice_transfer(nq, case["n2"], case["R"], case["dR"], length, nn, v, dv,
                                 phi0, pi0, k2="stencil")
        o, e, p = parts(fam, 1.0, "H")
        c, fh = sf.analyse(o, nq)
        ref = -4.0*(trs["ksq"] - trc["ksq"])*trc["Psi"]*alq
        first = nq2 == 1
        con[fam] = dict(
            first_shell_max_rel_dev=(np.abs(c - ref)[first]/np.abs(ref)[first]).max(),
            first_shell_ref_abs=np.abs(ref)[first].tolist(),
            first_shell_code_abs=np.abs(c)[first].tolist(),
            rel_size_of_k2_error=(1.0 - trs["ksq"][first]/trc["ksq"][first]).tolist(),
            rms_odd_H=np.sqrt((o*o).mean()))
        con[fam + "_curve"] = (np.sqrt(nq2.astype(float)), np.abs(c), np.abs(ref))
    summ["P1e_continuum"] = {k: v_ for k, v_ in con.items() if not k.endswith("_curve")}
    common.dump_json(summ, os.path.join(out, "summary.json"))

    # ---- figure
    fs = common.style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 6.4))
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.075, top=0.97, wspace=0.26,
                        hspace=0.24)
    col = dict(phi=fs.PAL["blue"], Pi=fs.PAL["red"], chi=fs.PAL["green"],
               K=fs.PAL["orange"])
    lab = dict(phi=r"$\delta\phi$", Pi=r"$\delta\Pi$", chi=r"$\chi-1$", K=r"$\delta K$")
    p = ax[0, 0]
    for key in ("phi", "Pi", "chi", "K"):
        q, cc, rr, dd = twin[key]
        p.plot(q, cc, ".", ms=2.5, color=col[key], label=lab[key])
        p.plot(q, dd, "x", ms=2.5, color=col[key], alpha=0.5)
    p.set_yscale("log")
    p.set_xlabel(r"$|n|$", labelpad=-2)
    p.set_ylabel("coefficient of the slice (dots), code minus twin (crosses)")
    p.legend(ncol=2, loc="lower left")
    p = ax[0, 1]
    ss = np.array([1.0, 0.5, 0.25])
    p.plot(ss, order["cor"]["H_ratio"], "o-", color=fs.PAL["blue"],
           label=r"$\langle|H|/[H]\rangle$, corrected")
    p.plot(ss, order["prt"]["H_ratio"], "s-", color=fs.PAL["red"],
           label=r"$\langle|H|/[H]\rangle$, printed $\delta\Pi$")
    p.plot(ss, order["cor"]["M_ratio"], "o--", color=fs.PAL["green"],
           label=r"$\langle|M|/[M]\rangle$, corrected")
    p.plot(ss, order["cor"]["H_ratio"][0]*ss**2, **fs.GUIDE)
    p.plot(ss, order["prt"]["H_ratio"][0]*ss, **fs.GUIDE)
    p.plot(ss, order["cor"]["M_ratio"][0]*ss, **fs.GUIDE)
    p.set_xscale("log")
    p.set_yscale("log")
    p.set_xlabel("factor $s$ on the mode functions", labelpad=-2)
    p.set_ylabel("constraint ratio at $t=0$")
    p.legend(loc="center left", fontsize=8)
    p = ax[1, 0]
    q, cc, rr, dd = prt
    p.plot(q, rr, "o", ms=4, mfc="none", color=fs.PAL["blue"],
           label=r"$4\varepsilon_1H^2|\Psi_n\alpha_n|$")
    p.plot(q, cc, ".", ms=3, color=fs.PAL["red"], label="odd part of $H$, printed")
    p.plot(q, dd, "x", ms=2.5, color="grey", label="difference")
    o, e, pp_ = parts("cor", 1.0, "H")
    c0, fh0 = sf.analyse(o, n)
    p.plot(q, np.abs(c0), "+", ms=3, color=fs.PAL["green"],
           label="odd part of $H$, corrected")
    p.set_yscale("log")
    p.set_xlabel(r"$|n|$", labelpad=-2)
    p.set_ylabel("coefficient of the odd part of $H$")
    p.legend(loc="upper right", fontsize=8)
    p = ax[1, 1]
    for fam, mk, cl in (("con16", "o", fs.PAL["red"]), ("con32", "s", fs.PAL["orange"])):
        q, cc, rr = con[fam + "_curve"]
        p.plot(q, rr, mk, ms=4, mfc="none", color=fs.PAL["blue"])
        p.plot(q, cc, ".", ms=3, color=cl, label=f"continuum $k^2$, $N={fam[3:]}$")
    o, e, pp_ = parts("ste16", 1.0, "H")
    nq, nq2 = sf.mode_set(16)
    c1, fh1 = sf.analyse(o, nq)
    p.plot(np.sqrt(nq2.astype(float)), np.abs(c1), "+", ms=3, color=fs.PAL["green"],
           label="stencil $k^2$, $N=16$")
    p.set_yscale("log")
    p.set_xlabel(r"$|n|$", labelpad=-2)
    p.set_ylabel("coefficient of the odd part of $H$")
    p.legend(loc="upper right", fontsize=8)
    fig.savefig(os.path.join(out, "fig_slice.png"), dpi=200)
    print("T1 done:", os.path.join(out, "summary.json"))


if __name__ == "__main__":
    main()
