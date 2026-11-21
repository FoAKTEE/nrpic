"""V2: independent recomputation of D-pre-3 in AthenaK's Newtonian mode (verifier_g1,
JOURNAL entry 2). Definitions are in the journal. Writes v2_results.json and figures
into $NRPIC_RUN_DIR (or --out)."""
import argparse
import glob
import json
import os

import numpy as np

import vreaders as V
import v2_selfsim as SS
import figstyle as fs

S = "/data/haiyangw/nrpic/scratch/D-bh-dress"
TRK = "/data/haiyangw/nrpic/wt/D-bh-dress/tracks/D-bh-dress/secondary_infall"
RUNS = {"N128c": (S + "/D-20261115-171503-4262f03", TRK + "/kernel_nx128.txt"),
        "N64c": (S + "/D-20261115-171505-62940f4", TRK + "/kernel_nx64.txt"),
        "N128Lc": (S + "/D-20261115-171507-d1058a9", TRK + "/kernel_nx128.txt")}
CLAIM = {"N128c": {"Mta": {2: 1.5063, 4: 2.5966}, "dress": {2: 0.1744, 4: 0.7975}},
         "N64c": {"Mta": {2: 1.5064, 4: 2.5966}, "dress": {2: 0.1736, 4: 0.7966}},
         "N128Lc": {"Mta": {2: 1.5077, 4: 2.5962, 8: 4.8159}, "dress": {2: 0.1751, 4: 0.7977, 8: 2.1537}}}
CLAIM_REF = {"N128c": {"Mta": {2: 1.5065, 4: 2.5956}, "dress": {2: 0.1735, 4: 0.7976}},
             "N64c": {"Mta": {2: 1.5058, 4: 2.5934}, "dress": {2: 0.1712, 4: 0.7954}},
             "N128Lc": {"Mta": {2: 1.5059, 4: 2.5937, 8: 4.8019}, "dress": {2: 0.1694, 4: 0.7940, 8: 2.1515}}}


# ------------------------------------------------------------------ snapshots
def by_tag(s):
    o = np.argsort(s["tag"])
    return {k: (v[o] if isinstance(v, np.ndarray) and v.shape[:1] == o.shape else v) for k, v in s.items()}


def front_outermost(rb, frac, level):
    """outermost r where frac (bin values at centres rb) crosses `level` coming from
    outside (frac < level outside)."""
    ok = np.isfinite(frac)
    rb, frac = rb[ok], frac[ok]
    above = frac >= level
    if not above.any():
        return np.nan
    k = np.where(above)[0].max()
    if k == len(rb) - 1:
        return rb[-1]
    f0, f1 = frac[k], frac[k + 1]
    return rb[k] + (level - f0) / (f1 - f0) * (rb[k + 1] - rb[k])


def analyse_run(name, rdir, nbins=300):
    setup = json.load(open(rdir + "/setup.json"))
    snaps = sorted(glob.glob(rdir + "/infall.part.*.bin"))
    c0s, c1s = setup["tag_clump"]
    d0, d1 = setup["tag_dust"]
    s0 = by_tag(V.read_snapshot(snaps[0]))
    assert np.array_equal(s0["tag"], np.arange(len(s0["tag"])))
    mc = s0["m"][c0s:c1s]
    Mcl = float(mc.sum())
    cen0 = (s0["x"][c0s:c1s] * mc[:, None]).sum(0) / Mcl
    xd0 = s0["x"][d0:d1] - cen0
    ri = np.linalg.norm(xd0, axis=1)
    n0 = xd0 / ri[:, None]
    md = s0["m"][d0:d1]
    order = np.argsort(ri)
    ri_s = ri[order]
    Mcum = np.cumsum(md[order])

    def Md_below(r):
        return np.interp(r, ri_s, Mcum, left=0.0)
    vr0 = np.einsum("ij,ij->i", s0["u"][d0:d1], n0)
    hub = float(np.median(vr0 / ri))
    edges = np.linspace(ri.min(), ri.max(), nbins + 1)
    rb = 0.5 * (edges[1:] + edges[:-1])
    ib = np.clip(np.digitize(ri, edges) - 1, 0, nbins - 1)
    cnt = np.bincount(ib, minlength=nbins)
    rows = []
    t_i = setup["t_i"]
    for sp in snaps:
        s = by_tag(V.read_snapshot(sp))
        mcl = s["m"][c0s:c1s]
        cen = (s["x"][c0s:c1s] * mcl[:, None]).sum(0) / mcl.sum()
        vcen = (s["u"][c0s:c1s] * mcl[:, None]).sum(0) / mcl.sum()
        xd = s["x"][d0:d1] - cen
        r = np.linalg.norm(xd, axis=1)
        nn = xd / np.maximum(r, 1e-30)[:, None]
        vr = np.einsum("ij,ij->i", s["u"][d0:d1] - vcen, nn)
        passed = np.einsum("ij,ij->i", xd, n0) < 0
        fpass = np.bincount(ib, weights=passed.astype(float), minlength=nbins) / np.maximum(cnt, 1)
        rc = front_outermost(rb, fpass, 0.5)
        dress = float(Md_below(rc)) if np.isfinite(rc) else 0.0
        # turnaround: median v_r per r_i bin among not-passed particles outside the front
        med = np.full(nbins, np.nan)
        rnow = np.full(nbins, np.nan)
        sel = ~passed
        # vectorised median by sorting within bins
        ks = ib[sel]
        o = np.lexsort((vr[sel], ks))
        ks_o = ks[o]
        vr_o = vr[sel][o]
        r_o = r[sel][o]
        starts = np.searchsorted(ks_o, np.arange(nbins))
        ends = np.searchsorted(ks_o, np.arange(nbins), side="right")
        for k in range(nbins):
            if ends[k] - starts[k] >= 5:
                med[k] = vr_o[(starts[k] + ends[k]) // 2]
                rnow[k] = np.median(r_o[starts[k]:ends[k]])
        neg = (med <= 0) & np.isfinite(med)
        if np.isfinite(rc):
            neg &= rb > rc
        if neg.any():
            k = np.where(neg)[0].max()
            if k + 1 < nbins and np.isfinite(med[k + 1]) and med[k + 1] > 0:
                w = (0 - med[k]) / (med[k + 1] - med[k])
                rta_i = rb[k] + w * (rb[k + 1] - rb[k])
                rta_now = rnow[k] + w * (rnow[k + 1] - rnow[k])
            else:
                rta_i, rta_now = rb[k], rnow[k]
            Mta = Mcl + float(Md_below(rta_i))
        else:
            rta_i = rta_now = np.nan
            Mta = Mcl
        a = ((s["t"] + t_i) / t_i) ** (2.0 / 3.0)
        rows.append(dict(t=float(s["t"]), a=float(a), Mta=Mta, dress=dress, r_c_i=float(rc),
                         r_ta_i=float(rta_i), r_ta=float(rta_now), clump_offset=float(np.linalg.norm(cen - cen0)),
                         n_passed=int(passed.sum())))
    last = s
    return dict(setup=setup, Mcl=Mcl, rows=rows, hub=hub, ri_s=ri_s, Mcum=Mcum, md=md, ri=ri,
                vr0=vr0, last=dict(x=xd, r=r, vr=vr, m=s["m"][d0:d1], t=float(s["t"]), cen=cen,
                                   rclump=np.linalg.norm(s["x"][c0s:c1s] - cen, axis=1), mclump=mcl))


def at_a(rows, key, a):
    aa = np.array([r["a"] for r in rows])
    vv = np.array([r[key] for r in rows])
    return float(np.interp(a, aa, vv))


# ------------------------------------------------------------------ references
def kepler_Mta(res, tq):
    """point mass, no shell crossing before turnaround: M_ta(t) from the closed form."""
    eps = res["setup"]["eps"]
    r = np.linspace(res["ri_s"][0], res["ri_s"][-1], 20000)
    Menc = res["Mcl"] + np.interp(r, res["ri_s"], res["Mcum"])
    v = eps * r
    E = 0.5 * v ** 2 - Menc / r
    ok = E < 0
    rmax = Menc[ok] / (-E[ok])
    th = np.arccos(1 - 2 * r[ok] / rmax)
    dt = np.sqrt(rmax ** 3 / (8 * Menc[ok])) * (np.pi - (th - np.sin(th)))
    tc = np.sqrt(rmax ** 3 / (8 * Menc[ok])) * (2 * np.pi - (th - np.sin(th)))
    Mta = np.interp(tq, dt, Menc[ok])
    Mc = np.interp(tq, tc, Menc[ok])  # first arrival at the centre, no crossing
    return Mta, Mc


def load_kernel(path):
    k = np.loadtxt(path)
    return k[:, 0], k[:, 1]


def shells(res, kernel, law, dx, t_out, Ns=3000, dt=0.01, soft=0.25):
    """Spherical shells from the lattice; returns M_ta and dress at t_out."""
    ri, md = res["ri"], res["md"]
    o = np.argsort(ri)
    grp = np.array_split(o, Ns)
    r = np.array([ri[g].mean() for g in grp])
    m = np.array([md[g].sum() for g in grp])
    v = np.array([res["vr0"][g].mean() for g in grp])
    Mcl = res["Mcl"]
    q_k, K_k = kernel

    def Kf(rr):
        q = rr / dx
        K = np.interp(np.log(np.maximum(q, 1e-12)), np.log(q_k), K_k, left=np.nan, right=1.0)
        lo = q < q_k[0]
        K[lo] = K_k[0] * (q[lo] / q_k[0]) ** 3
        far = q > q_k[-1]
        K[far] = 1.0
        return K

    def acc(r):
        oo = np.argsort(r)
        cm = np.cumsum(m[oo]) - 0.5 * m[oo]
        Min = np.empty_like(r)
        Min[oo] = cm
        if law == "point":
            return -(Mcl + Min) * r / (r ** 2 + soft ** 2) ** 1.5
        K = Kf(r)
        if law == "kernel_seed":
            return -(Mcl * K + Min) / np.maximum(r, 1e-8) ** 2 * np.where(r < 1e-8, 0, 1)
        return -(Mcl + Min) * K / np.maximum(r, 1e-8) ** 2

    turned = np.zeros(Ns, bool)
    bounced = np.zeros(Ns, bool)
    t = 0.0
    out = []
    t_out = sorted(t_out)
    j = 0
    a_ = acc(r)
    while j < len(t_out):
        h = min(dt, t_out[j] - t) if t_out[j] - t > 1e-12 else 0.0
        if h > 0:
            v += 0.5 * h * a_
            r += h * v
            neg = r < 0
            r[neg] = -r[neg]
            v[neg] = -v[neg]
            bounced |= neg
            a_ = acc(r)
            v += 0.5 * h * a_
            t += h
            turned |= v <= 0
        if abs(t - t_out[j]) < 1e-9:
            out.append(dict(t=t, Mta=float(Mcl + m[turned].sum()), dress=float(m[bounced].sum())))
            j += 1
    return out


# ------------------------------------------------------------------ self-similar
# own solver in v2_selfsim.py (pure-Python adaptive leapfrog; the first solve_ivp version
# was too slow and was dropped before any registered run, JOURNAL entry 2)


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    ap.add_argument("--runs", default="N128c,N64c,N128Lc")
    args = ap.parse_args()
    out = args.out
    fs.use_style()
    import matplotlib.pyplot as plt
    R = {}
    res_json = {"runs": {}}
    for name in args.runs.split(","):
        rdir, kfile = RUNS[name]
        print("analysing", name, flush=True)
        res = analyse_run(name, rdir)
        R[name] = res
        res150 = analyse_run(name, rdir, nbins=150)
        st = res["setup"]
        dx = 2 * st["L"] / {"N128c": 128, "N64c": 64, "N128Lc": 128}[name]
        rows = res["rows"]
        tq = np.array([r["t"] for r in rows])
        kM, kC = kepler_Mta(res, tq)
        kern = load_kernel(kfile)
        sh = {}
        for law in ("kernel_seed", "kernel_all", "point"):
            print("  shells", law, flush=True)
            sh[law] = shells(res, kern, law, dx, list(tq), dt=(0.005 if law == "point" else 0.01))
        aa = [r["a"] for r in rows]
        summ = {"dx": dx, "M_clump": res["Mcl"], "hubble_fit_vr_over_r_t0": res["hub"], "at": {}}
        for A in (2, 4, 8):
            if A > max(aa) + 1e-6:
                continue
            d = {"run_Mta": at_a(rows, "Mta", A), "run_dress": at_a(rows, "dress", A),
                 "run_r_ta": at_a(rows, "r_ta", A),
                 "kepler_point_Mta": float(np.interp(A, aa, kM)),
                 "kepler_point_first_arrival_mass": float(np.interp(A, aa, kC))}
            d["run_Mta_nbins150"] = at_a(res150["rows"], "Mta", A)
            d["run_dress_nbins150"] = at_a(res150["rows"], "dress", A)
            for law in sh:
                d["shell_%s_Mta" % law] = float(np.interp(A, aa, [x["Mta"] for x in sh[law]]))
                d["shell_%s_dress" % law] = float(np.interp(A, aa, [x["dress"] for x in sh[law]]))
            if A in CLAIM[name]["Mta"]:
                d["claim_run_Mta"] = CLAIM[name]["Mta"][A]
                d["claim_run_dress"] = CLAIM[name]["dress"][A]
                d["claim_ref_Mta"] = CLAIM_REF[name]["Mta"][A]
                d["claim_ref_dress"] = CLAIM_REF[name]["dress"][A]
            summ["at"][str(A)] = d
        mask = np.array(aa) >= 1.5
        summ["max_rel_dev_Mta_vs_kernel_seed_after_1.5"] = float(np.max(np.abs(np.array([r["Mta"] for r in rows])[mask] /
                                                                              np.array([x["Mta"] for x in sh["kernel_seed"]])[mask] - 1)))
        summ["rows"] = rows
        summ["shells"] = sh
        summ["kepler_Mta"] = list(map(float, kM))
        res_json["runs"][name] = summ
        print(json.dumps(summ["at"], indent=1), flush=True)

    # growth figure
    fig, axs = plt.subplots(2, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 5.6), sharex=True)
    fig.subplots_adjust(left=0.14, right=0.97, bottom=0.09, top=0.97, hspace=0.06)
    cols = {"N128c": fs.PAL["red"], "N64c": fs.PAL["orange"], "N128Lc": fs.PAL["green"]}
    for name, summ in res_json["runs"].items():
        aa = np.array([r["a"] for r in summ["rows"]])
        for key, ax in (("Mta", axs[0]), ("dress", axs[1])):
            run = np.array([r[key] for r in summ["rows"]])
            ref = np.array([x[key] for x in summ["shells"]["kernel_seed"]])
            ax.plot(aa, run, color=cols[name], label=name + " (run)")
            ax.plot(aa, ref, color=fs.PAL["blue"], ls="--", lw=1.0)
    axs[0].plot([], [], color=fs.PAL["blue"], ls="--", lw=1.0, label="my shells, kernel on clump")
    axs[0].set_ylabel(r"$M_{\rm ta}$ ($M$)")
    axs[1].set_ylabel(r"dress ($M$)")
    axs[1].set_xlabel(r"$a/a_i$")
    axs[0].legend(loc="upper left")
    fs.save(fig, out + "/v2_growth")

    fig, ax = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 3.4))
    fig.subplots_adjust(left=0.15, right=0.97, bottom=0.14, top=0.96)
    for name, summ in res_json["runs"].items():
        aa = np.array([r["a"] for r in summ["rows"]])
        m = aa >= 1.2
        for key, ls in (("Mta", "-"), ("dress", "--")):
            run = np.array([r[key] for r in summ["rows"]])
            ref = np.array([x[key] for x in summ["shells"]["kernel_seed"]])
            ax.plot(aa[m], run[m] / ref[m] - 1, color=cols[name], ls=ls, label="%s %s" % (name, key))
    ax.axhline(0, **fs.GUIDE)
    ax.set_ylim(-0.05, 0.05)
    ax.set_xlabel(r"$a/a_i$")
    ax.set_ylabel("run / my kernel shells - 1")
    ax.legend(loc="lower right", ncol=2, fontsize=8)
    fs.save(fig, out + "/v2_growth_ratio")

    # self-similar: main solution and two numerical checks
    print("self-similar", flush=True)
    sols = {}
    for key, (tm, eta) in {"main": (500.0, 0.01), "tau200_eta0.005": (200.0, 0.005),
                           "tau200_eta0.01": (200.0, 0.01)}.items():
        r_ = SS.solve(tau_max=tm, eta=eta)
        sols[key] = r_
        print(key, "iterations", len(r_["hist"]), "caustic", r_["lam_caustic1"], flush=True)
    sol = sols["main"]
    lam_g, m_g = sol["lam"], sol["m"]
    small = (lam_g > 2e-3) & (lam_g < 2e-2)
    slope_small = float(np.polyfit(np.log(lam_g[small]), np.log(m_g[small] - m_g[0]), 1)[0])
    e01 = np.logspace(-1, np.log10(0.3), 9)
    ss = {}
    for key, r_ in sols.items():
        ss[key] = dict(iterations=len(r_["hist"]), last_change=r_["hist"][-1],
                       lambda_caustic1=r_["lam_caustic1"], tau_caustic1=r_["tau_caustic1"],
                       tau_first_passage=r_["tau_first_passage"],
                       m_at={str(l): float(np.interp(l, r_["lam"], r_["m"])) for l in (0.01, 0.1, 0.2, 0.3, 0.5)},
                       rho_bins_01_03=SS.binned_rho(r_["lam"], r_["m"], e01).tolist())
    ss["slope_dlnm_dlnlam_2e-3_2e-2_main"] = slope_small
    res_json["selfsimilar"] = ss
    print(json.dumps(ss, indent=1), flush=True)

    # profile comparison at the last snapshot of each run
    figP, axP = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 3.6))
    figP.subplots_adjust(left=0.15, right=0.97, bottom=0.14, top=0.96)
    figR, axR = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 3.2))
    figR.subplots_adjust(left=0.15, right=0.97, bottom=0.15, top=0.96)
    lb_ss = np.logspace(-2.5, 0, 60)
    mm = np.interp(lb_ss, lam_g, m_g)
    rr_ss = (9 * np.pi ** 2 / 16) * np.diff(mm) / np.diff(lb_ss ** 3)
    axP.loglog(np.sqrt(lb_ss[1:] * lb_ss[:-1]), rr_ss, **fs.GUIDE, label="my self-similar solution")
    for name, res in R.items():
        summ = res_json["runs"][name]
        last = res["last"]
        rta = summ["rows"][-1]["r_ta"]
        a_end = summ["rows"][-1]["a"]
        rho_b = res["setup"]["rho_i"] * a_end ** -3
        edges = np.logspace(np.log10(0.1), np.log10(0.3), 9)
        mass = np.histogram(last["r"] / rta, bins=edges, weights=last["m"])[0]
        vol = 4 * np.pi / 3 * (rta * edges) ** 3
        rho = mass / np.diff(vol)
        mm_b = np.interp(edges, lam_g, m_g)
        ss_b = (9 * np.pi ** 2 / 16) * np.diff(mm_b) / np.diff(edges ** 3)
        ratio = rho / rho_b / ss_b
        brk = {}
        for fac in (0.97, 1.03):
            m_f = np.histogram(last["r"] / (fac * rta), bins=edges, weights=last["m"])[0]
            r_f = m_f / np.diff(4 * np.pi / 3 * (fac * rta * edges) ** 3) / rho_b / ss_b
            brk["r_ta_x%.2f" % fac] = float(np.max(np.abs(r_f - 1)))
        for key in sols:
            if key == "main":
                continue
            ssk = SS.binned_rho(sols[key]["lam"], sols[key]["m"], edges)
            brk["ss_" + key] = float(np.max(np.abs(rho / rho_b / ssk - 1)))
        axR.semilogx(np.sqrt(edges[1:] * edges[:-1]), ratio - 1, "o-", ms=3, color=cols[name],
                     label="%s, a/a_i = %.2f" % (name, a_end))
        # a finer comparison over a wider range, for the figure
        e2 = np.logspace(np.log10(2 * summ["dx"] / rta), 0.1, 40)
        mass2 = np.histogram(last["r"] / rta, bins=e2, weights=last["m"])[0]
        mass2 += np.histogram(last["rclump"] / rta, bins=e2, weights=last["mclump"])[0]
        rho2 = mass2 / np.diff(4 * np.pi / 3 * (rta * e2) ** 3)
        axP.loglog(np.sqrt(e2[1:] * e2[:-1]), rho2 / rho_b, "o-", ms=3, color=cols[name],
                   label="%s, a/a_i = %.2f" % (name, a_end))
        summ["profile_0.1_0.3"] = dict(a=a_end, r_ta=rta, rho_b=rho_b, edges=edges.tolist(),
                                       ratio_run_over_ss=ratio.tolist(),
                                       max_abs_dev=float(np.max(np.abs(ratio - 1))),
                                       break_attempts_max_abs_dev=brk)
        print(name, "profile ratio", np.round(ratio, 3), flush=True)
    axP.axvspan(0.1, 0.3, color=fs.PAL["blue"], alpha=0.08)
    axP.set_xlabel(r"$\lambda = r/r_{\rm ta}$")
    axP.set_ylabel(r"$\rho/\rho_b$")
    axP.legend(loc="lower left", fontsize=8)
    axP.set_xlim(3e-3, 1.5)
    fs.save(figP, out + "/v2_profile")
    axR.axhline(0, **fs.GUIDE)
    for y in (-0.25, 0.25):
        axR.axhline(y, color=fs.PAL["grey"] if "grey" in fs.PAL else "0.5", ls=":", lw=0.8)
    axR.set_xlabel(r"$\lambda = r/r_{\rm ta}$ (8 bins on [0.1, 0.3])")
    axR.set_ylabel("run / my self-similar - 1")
    axR.legend(loc="best", fontsize=8)
    fs.save(figR, out + "/v2_profile_ratio")

    with open(out + "/v2_results.json", "w") as f:
        json.dump(res_json, f, indent=1)
    np.savez(out + "/v2_selfsimilar.npz", lam=lam_g, m=m_g)


if __name__ == "__main__":
    main()
