#!/usr/bin/env python3
"""Analysis of the Newtonian-mode secondary-infall runs (AthenaK output only; decision 0010).

For each run (nm_run.py --kind infall): from the particle snapshots, by particle tag,
  - turnaround mass M_ta(t) = clump mass + dust that has had v_r < 0 at some snapshot <= t;
  - dress M_dr(t) = dust that has passed its pericentre: on the other side of the centre
    (x . x_0 < 0) at some snapshot, or moving outwards (v_r > 0) after having turned
    around at an earlier snapshot;
  - the spherically averaged dust density rho/rho_b(t) in logarithmic bins about the
    origin, rho_b = rho_i (t_i/(t_i + t))^2;
  - the clump: centre of mass, rms and 90 % radii; the conservation columns of
    <base>.newton.hst; the particle count of <base>.nrpic.hst.
Compares with the matched shell references (nm_shells.py) at the same times and with the
self-similar solution of test 2 (selfsimilar_profile.npz), r_ta from G M_ta t^2/r_ta^3 =
pi^2/8 with the measured M_ta. Writes nm_analysis.json, nm_growth.txt and figures to --out.

Wave 3 (late snapshots, a/a_i up to 30): the radial bins run to 2048 M (nm_late.LEDGES_LATE;
its first 27 bins are the wave-2 bins, so wave-2 numbers are unchanged), the growth table
includes a/a_i = 12, 16, 24, 30, and for every snapshot nearest to an a/a_i of --late_at
(within 2 %) the "late" block compares, in units of lambda = r/r_ta with r_ta from the run's
M_ta: the run's rho/rho_b with the self-similar solution binned in the same bins and with
each matched shell reference (binned the same way at its nearest snapshot), on
[lambda_min, 0.3] with lambda_min = max(4 dx/r_ta, 0.03), and the local logarithmic slopes
(nm_late.compare, the code nm_predict.py used for the predictions). Extra figures:
nm_late_profiles (profile, ratios, slopes per a/a_i) and nm_late_growth (dress/M_ta and
M_ta/(M a/a_i) against the shells and the self-similar values; run/shells - 1).

Usage: python3 nm_analyze.py --run LABEL:RUNDIR --ref LABEL:LAW:NPZ_JSON_PREFIX ...
                             --selfsim selfsimilar_profile.npz [--late_at 4 8 16 30]
  (--ref N128:kernel:/path/nm_shells_N128_kernel  attaches that reference to run N128;
   LAW is kernel, plummer, point or hybrid)
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..", "python")))

from common import load_figstyle, KAPPA, C_TA  # noqa: E402
from nrpic import newton as nw                 # noqa: E402
import nm_late as NL                           # noqa: E402

SS_DRESS_FRAC = 2.0255 ** (-2.0 / 3.0)   # self-similar dress/M_ta (JOURNAL.md wave 1, 3d')
# 0.1 dex bins for the profiles (factor 2^(1/3)); wave 2 used geomspace(0.5, 256, 28), which
# are the first 27 bins of these (identical to 1e-15)
LEDGES = NL.LEDGES_LATE
ROUND_A = (1.5, 2.0, 3.0, 4.0, 6.0, 8.0, 12.0, 16.0, 24.0, 30.0)


def snaps_of(rundir):
    return sorted(glob.glob(os.path.join(rundir, "infall.part.*.bin")))


VBIN = 10.0 ** 0.02          # fine radial bins (0.02 dex) of the M_ta(v) estimator


def r_ta_from_velocity(r, vr, nmin=20):
    """Wave 3: turnaround radius from the instantaneous velocity field, free of the flag
    history: the median radial velocity of the dust in 0.02-dex radial bins; r_ta is the
    outermost crossing from v_r < 0 (inside) to v_r > 0 (outside), interpolated linearly in
    ln r. Outside the outermost caustic (lambda_1 = 0.355) the flow is single-stream and the
    shells keep their order, so the mass inside this radius is the turnaround mass.
    Returns None if no bin has a negative median."""
    ok = np.isfinite(r) & np.isfinite(vr) & (r > 0)
    r, vr = r[ok], vr[ok]
    if r.size < nmin:
        return None
    lr = np.log(r)
    nb = int(np.ceil((lr.max() - np.log(0.5)) / np.log(VBIN))) + 1
    idx = np.clip(((lr - np.log(0.5)) / np.log(VBIN)).astype(int), 0, nb - 1)
    order = np.argsort(idx, kind="stable")
    cnt = np.bincount(idx, minlength=nb)
    starts = np.concatenate([[0], np.cumsum(cnt)[:-1]])
    vs = vr[order]
    med = np.full(nb, np.nan)
    for j in np.where(cnt >= nmin)[0]:
        med[j] = np.median(vs[starts[j]:starts[j] + cnt[j]])
    lc = np.log(0.5) + (np.arange(nb) + 0.5) * np.log(VBIN)
    good = np.where(np.isfinite(med))[0]
    neg = good[med[good] < 0]
    if neg.size == 0:
        return None
    j = neg[-1]
    nxt = good[good > j]
    if nxt.size == 0:
        return float(np.exp(lc[j]))
    k = nxt[0]
    f = med[j] / (med[j] - med[k])
    return float(np.exp(lc[j] + f * (lc[k] - lc[j])))


def analyse_run(rundir, stride=1):
    with open(os.path.join(rundir, "setup.json")) as f:
        p = json.load(f)
    with open(os.path.join(rundir, "nm_run.json")) as f:
        meta = json.load(f)
    n_tot, (c0, c1), (d0, d1) = p["n_total"], p["tag_clump"], p["tag_dust"]
    files = snaps_of(rundir)
    files = files[::stride] if (len(files) - 1) % stride == 0 else files[::stride] + files[-1:]
    shift = np.asarray(p.get("shift", [0.0, 0.0, 0.0]))
    t0, _, x, u, m, tag = nw.read_snapshot(files[0])
    x = x - shift
    X0 = np.zeros((n_tot, 3))
    X0[tag] = x
    M = np.zeros(n_tot)
    M[tag] = m
    md = M[d0:d1]
    turned = np.zeros(d1 - d0, bool)
    passed = np.zeros(d1 - d0, bool)
    crossed = np.zeros(d1 - d0, bool)     # wave 3: other side of the centre only
    t_turn = np.full(d1 - d0, np.nan)
    t_pass = np.full(d1 - d0, np.nan)
    rows, profiles, phase = [], [], {}
    for k, fn in enumerate(files):
        t, cyc, x, u, m, tag = nw.read_snapshot(fn)
        x = x - shift
        X = np.full((n_tot, 3), np.nan)
        U = np.full((n_tot, 3), np.nan)
        X[tag], U[tag] = x, u
        alive = ~np.isnan(X[:, 0])
        xc, uc = X[c0:c1], U[c0:c1]
        mc = M[c0:c1]
        ac = alive[c0:c1]
        com = (mc[ac, None] * xc[ac]).sum(0) / mc[ac].sum()
        rcl = np.sqrt(((xc[ac] - com) ** 2).sum(1))
        xd, ud = X[d0:d1], U[d0:d1]
        ad = alive[d0:d1]
        r = np.sqrt((xd ** 2).sum(1))
        with np.errstate(invalid="ignore", divide="ignore"):
            vr = (xd * ud).sum(1) / r
        side = (xd * X0[d0:d1]).sum(1) < 0
        new_pass = ad & ~passed & (side | (turned & (vr > 0)))
        passed |= new_pass
        t_pass[new_pass] = t
        new_turn = ad & ~turned & (vr < 0)
        turned |= new_turn
        t_turn[new_turn] = t
        a_ai = ((p["t_i"] + t) / p["t_i"]) ** (2.0 / 3.0)
        rho_b = p["rho_i"] * (p["t_i"] / (p["t_i"] + t)) ** 2
        mta = float(mc.sum() + md[turned].sum())
        crossed |= ad & side
        r_ta_v = r_ta_from_velocity(r[ad], vr[ad])
        mta_v = float(mc[ac].sum() + (md[ad & (r < r_ta_v)].sum() if r_ta_v else 0.0))
        rp_ = r[ad & passed]
        wq = md[ad & passed]
        if rp_.size:
            o = np.argsort(rp_)
            cw = np.cumsum(wq[o]) / wq.sum()
            rsp = {f"r_sp{int(q * 100)}": float(np.interp(q, cw, rp_[o])) for q in (0.5, 0.9, 0.99)}
        else:
            rsp = {}
        rows.append(dict(t=t, cycle=int(cyc), a=a_ai, mta=mta, dress=float(md[passed].sum()), **rsp,
                         mta_v=mta_v, r_ta_v=r_ta_v, dress_side=float(md[crossed].sum()),
                         n_alive=int(alive.sum()), com=com.tolist(),
                         clump_rms=float(np.sqrt(np.mean(rcl ** 2))),
                         clump_r90=float(np.percentile(rcl, 90)),
                         clump_rmax=float(rcl.max()),
                         dust_vr_mean_inner=float(np.mean(vr[ad & (r < 5 * meta["dx"])]))
                         if np.any(ad & (r < 5 * meta["dx"])) else None))
        h, _ = np.histogram(r[ad], bins=LEDGES, weights=md[ad])
        vol = 4.0 * np.pi / 3.0 * np.diff(LEDGES ** 3)
        hv, _ = np.histogram(r[ad], bins=LEDGES, weights=md[ad] * vr[ad])
        with np.errstate(invalid="ignore", divide="ignore"):
            vmean = hv / h
        profiles.append(dict(t=t, a=a_ai, rho=(h / vol / rho_b).tolist(), vr=vmean.tolist(),
                             mass_in=float(md[ad & (r < 2.0 * meta["dx"])].sum())))
        if k == len(files) - 1 or abs(a_ai - 2.0) < 0.02:
            sel = np.where(ad)[0][::25]
            phase[f"{a_ai:.3f}"] = dict(r=r[sel], vr=vr[sel], passed=passed[sel])
    hst = nw.read_newton_hst(glob.glob(os.path.join(rundir, "*.newton.hst"))[0])
    return dict(p=p, meta=meta, rows=rows, profiles=profiles, phase=phase, hst=hst,
                dx=meta["dx"], t_turn=t_turn, t_pass=t_pass, md=md)


def ref_profile(ref, k, rho_b):
    r = np.abs(ref["snap_r"][k])
    h, _ = np.histogram(r, bins=LEDGES, weights=ref["m0"])
    return h / (4.0 * np.pi / 3.0 * np.diff(LEDGES ** 3)) / rho_b


def load_ref(prefix):
    d = dict(np.load(prefix + ".npz"))
    with open(prefix + ".json") as f:
        d["info"] = json.load(f)
    g = d["info"]["growth"]
    d["g_t"] = np.array([x["t_code"] for x in g])
    d["g_mta"] = np.array([x["mta"] for x in g])
    d["g_dress"] = np.array([x["dress"] for x in g])
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", ""))
    ap.add_argument("--run", action="append", required=True)
    ap.add_argument("--ref", action="append", default=[])
    ap.add_argument("--selfsim", required=True)
    ap.add_argument("--stride", type=int, default=1,
                    help="use every stride-th snapshot (test of the sampling of the turnaround and "
                         "pericentre detection)")
    ap.add_argument("--late_at", type=float, nargs="+", default=[4.0, 8.0, 16.0, 30.0],
                    help="a/a_i of the late comparison with the self-similar solution")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    fs = load_figstyle()
    import matplotlib.pyplot as plt

    runs, order = {}, []
    for spec in a.run:
        lab, d = spec.split(":", 1)
        runs[lab] = analyse_run(d, a.stride)
        runs[lab]["dir"] = d
        runs[lab]["refs"] = {}
        order.append(lab)
    for spec in a.ref:
        lab, law, pre = spec.split(":", 2)
        runs[lab]["refs"][law] = load_ref(pre)
    ss = np.load(a.selfsim)

    summary = {}
    for lab in order:
        R = runs[lab]
        p, rows = R["p"], R["rows"]
        t = np.array([x["t"] for x in rows])
        av = np.array([x["a"] for x in rows])
        mta = np.array([x["mta"] for x in rows])
        dr = np.array([x["dress"] for x in rows])
        out = dict(run=R["dir"], dx=R["dx"], nsnap=len(rows), t_end=float(t[-1]), a_end=float(av[-1]),
                   n_alive_end=rows[-1]["n_alive"], n_total=p["n_total"])
        for law, ref in R["refs"].items():
            rm = np.interp(t, ref["g_t"], ref["g_mta"])
            rd = np.interp(t, ref["g_t"], ref["g_dress"])
            late = av >= 1.5
            out[f"vs_{law}"] = dict(
                mta_max_rel=float(np.max(np.abs(mta[late] / rm[late] - 1))),
                dress_rel_end=float(dr[-1] / rd[-1] - 1),
                dress_rel_at_a2=float(np.interp(2.0, av, dr / np.where(rd > 0, rd, np.nan) - 1)),
                ref_mta_end=float(rm[-1]), ref_dress_end=float(rd[-1]))
            R[f"rm_{law}"], R[f"rd_{law}"] = rm, rd
        # growth at the round values of a/a_i
        out["growth"] = []
        for aa in ROUND_A:
            if aa <= av[-1] * (1 + 2e-3):
                ae = float(min(aa, av[-1]))      # the last snapshot may lie just before a_end
                g_ = dict(a=aa, a_eval=ae, mta=float(np.interp(ae, av, mta)),
                          dress=float(np.interp(ae, av, dr)))
                g_.update(dress_over_mta=g_["dress"] / g_["mta"], mta_over_a=g_["mta"] / ae)
                # wave 3: estimators free of the flag history (H2)
                mv_ = np.array([x["mta_v"] for x in rows])
                ds_ = np.array([x["dress_side"] for x in rows])
                g_.update(mta_v=float(np.interp(ae, av, mv_)), dress_side=float(np.interp(ae, av, ds_)))
                g_.update(dress_side_over_mta_v=g_["dress_side"] / g_["mta_v"], mta_v_over_a=g_["mta_v"] / ae)
                for law, ref in R["refs"].items():
                    ag = ((p["t_i"] + ref["g_t"]) / p["t_i"]) ** (2.0 / 3.0)
                    if ae <= ag[-1] * (1 + 2e-3):
                        rm_ = float(np.interp(ae, ag, ref["g_mta"]))
                        rd_ = float(np.interp(ae, ag, ref["g_dress"]))
                        g_[f"{law}_mta"], g_[f"{law}_dress"] = rm_, rd_
                        g_[f"{law}_mta_rel"] = g_["mta"] / rm_ - 1
                        g_[f"{law}_dress_rel"] = g_["dress"] / rd_ - 1 if rd_ > 0 else None
                        g_[f"{law}_mta_v_rel"] = g_["mta_v"] / rm_ - 1
                        g_[f"{law}_dress_side_rel"] = g_["dress_side"] / rd_ - 1 if rd_ > 0 else None
                out["growth"].append(g_)
        # local growth exponent of the dress, d ln M_dr / d ln a, over factors of 1.25 in a
        k = dr > 0
        lg = np.gradient(np.log(dr[k]), np.log(av[k]))
        out["dlnMdress_dlna_end"] = float(np.mean(lg[-5:]))
        out["dress_over_mta_end"] = float(dr[-1] / mta[-1])
        out["mta_dust_over_a_end"] = float((mta[-1] - 1.0) / av[-1])
        out["mta_over_a_end"] = float(mta[-1] / av[-1])
        # clump and conservation
        com = np.array([x["com"] for x in rows])
        out["clump"] = dict(com_max=float(np.abs(com).max()), com_max_over_dx=float(np.abs(com).max() / R["dx"]),
                            rms_end=rows[-1]["clump_rms"], r90_max=float(max(x["clump_r90"] for x in rows)),
                            r90_max_over_dx=float(max(x["clump_r90"] for x in rows) / R["dx"]),
                            rmax_max=float(max(x["clump_rmax"] for x in rows)))
        h = R["hst"]
        Kc, Wc = h["K"], h["W"]
        E = Kc + Wc
        P = np.sqrt(h["P_x"] ** 2 + h["P_y"] ** 2 + h["P_z"] ** 2)
        Xc = np.sqrt(h["X_x"] ** 2 + h["X_y"] ** 2 + h["X_z"] ** 2)
        out["energy"] = dict(K0=float(Kc[0]), W0=float(Wc[0]),
                             dE_max_over_W0=float(np.max(np.abs(E - E[0])) / abs(Wc[0])),
                             dE_end_over_W0=float((E[-1] - E[0]) / abs(Wc[0])),
                             P_max=float(P.max()), com_all_max=float(Xc.max()),
                             steps=int(h["ncycle"][-1]), dt_min=float(h["dt"][1:].min()),
                             dt_median=float(np.median(h["dt"][1:])),
                             mg_cycles_mean=float(np.mean(h["mg_cycles"])),
                             mass_end_over_start=float(h["mass"][-1] / h["mass"][0]))
        R["E"], R["P"], R["ht"] = E, P, h["time"]
        # profiles against the references and the self-similar solution
        rc = np.sqrt(LEDGES[1:] * LEDGES[:-1])
        prof = []
        pa = np.array([x["a"] for x in R["profiles"]])
        want = {int(np.argmin(np.abs(pa - aa))) for aa in (2.0, 4.0, 8.0)
                if np.min(np.abs(pa / aa - 1)) < 0.05} | {len(pa) - 1}
        for kk, pr in enumerate(R["profiles"]):
            if kk not in want:
                continue
            rho_b = p["rho_i"] * (p["t_i"] / (p["t_i"] + pr["t"])) ** 2
            ent = dict(a=pr["a"], t=pr["t"], rho=pr["rho"])
            row = R["rows"][kk]
            ent.update({k_: row[k_] for k_ in ("r_sp50", "r_sp90", "r_sp99") if k_ in row})
            for law, ref in R["refs"].items():
                j = int(np.argmin(np.abs(ref["snap_t"] - pr["t"])))
                rp = ref_profile(ref, j, rho_b)
                pm = ref["snap_ncross"][j] > 0
                if pm.any():
                    rr_ = np.abs(ref["snap_r"][j][pm])
                    ww_ = ref["m0"][pm]
                    o = np.argsort(rr_)
                    cw = np.cumsum(ww_[o]) / ww_.sum()
                    for q in (0.5, 0.9, 0.99):
                        ent[f"ref_{law}_r_sp{int(q * 100)}"] = float(np.interp(q, cw, rr_[o]))
                ent[f"ref_{law}"] = rp.tolist()
                ent[f"ref_{law}_dt"] = float(ref["snap_t"][j] - pr["t"])
                mtak = np.interp(pr["t"], t, mta)
                r_ta = (mtak * (p["t_i"] + pr["t"]) ** 2 / KAPPA) ** (1.0 / 3.0)
                ok = (rc >= 4 * R["dx"]) & (rc <= r_ta) & (rp > 0) & (np.array(pr["rho"]) > 0)
                ratio = np.array(pr["rho"])[ok] / rp[ok]
                # the outermost caustic of the reference: the steepest fall between two bins
                # inside 1.5 r_ta; the bins on either side of it are excluded in max_dev_excl
                lr = np.log(np.where(rp > 0, rp, np.nan))
                jump = np.where((rc[1:] < 1.5 * r_ta), np.diff(lr), np.nan)
                jc = int(np.nanargmin(jump)) if np.isfinite(jump).any() else -10
                near = np.zeros(rc.size, bool)
                near[max(jc - 1, 0):jc + 3] = True
                keep = ~near[ok]
                ent[f"ratio_{law}_4dx_rta"] = dict(
                    r=rc[ok].tolist(), ratio=ratio.tolist(),
                    max_dev=float(np.max(np.abs(ratio - 1))) if ok.any() else None,
                    caustic_r=float(np.sqrt(rc[jc] * rc[jc + 1])) if jc >= 0 else None,
                    max_dev_excl_caustic=float(np.max(np.abs(ratio[keep] - 1))) if keep.any() else None,
                    rms_dev_excl_caustic=float(np.sqrt(np.mean((ratio[keep] - 1) ** 2))) if keep.any() else None)
            mtak = np.interp(pr["t"], t, mta)
            r_ta = (mtak * (p["t_i"] + pr["t"]) ** 2 / KAPPA) ** (1.0 / 3.0)
            vr = np.array(pr["vr"])
            okv = np.isfinite(vr)
            pos = np.where(okv & (vr > 0) & (rc > 2 * R["dx"]))[0]
            # measured turnaround radius: inner edge of the outermost run of outflowing bins
            r_ta_meas = None
            if pos.size:
                j = pos[-1]
                while j - 1 >= 0 and okv[j - 1] and vr[j - 1] > 0:
                    j -= 1
                if j > 0:
                    r_ta_meas = float(np.sqrt(rc[j] * rc[j - 1]))
            lam = rc / r_ta
            ssr = np.interp(np.log(lam), np.log(ss["rc"]), ss["rho"], left=np.nan, right=np.nan)
            okl = (lam >= 0.1) & (lam <= 0.35) & np.isfinite(ssr) & (np.array(pr["rho"]) > 0)
            ent.update(r_ta_selfsim_def=float(r_ta), r_ta_measured=r_ta_meas,
                       selfsim_ratio_0p1_0p35=(np.array(pr["rho"])[okl] / ssr[okl]).tolist(),
                       selfsim_lambda=lam[okl].tolist())
            prof.append(ent)
        out["profiles"] = prof
        R["prof"] = prof
        # ---------- late comparison (wave 3): self-similar solution and shells in units of r_ta
        late = []
        for aa in a.late_at:
            kk = int(np.argmin(np.abs(pa - aa)))
            if abs(pa[kk] / aa - 1) > 0.02:
                continue
            pr = R["profiles"][kk]
            tc = p["t_i"] + pr["t"]
            rho_b = p["rho_i"] * (p["t_i"] / tc) ** 2
            rho = np.array(pr["rho"])
            mtak = float(R["rows"][kk]["mta"])
            r_ta = NL.r_ta_of(mtak, tc)
            cmp_, ssr, sl, sl_ss = NL.compare(rc, LEDGES, rho, ss, r_ta, R["dx"])
            ent = dict(a_target=aa, a=float(pr["a"]), t=float(pr["t"]), M_ta=mtak,
                       dress=float(R["rows"][kk]["dress"]), r_ta=float(r_ta), vs_selfsim=cmp_,
                       rho=rho.tolist(), ssr=ssr.tolist(), slope=sl.tolist(), slope_ss=sl_ss.tolist())
            # the same with r_ta from the flag-free M_ta(v) (H2); r_ta_v_direct is the measured radius
            mtav = float(R["rows"][kk]["mta_v"])
            r_ta_v = NL.r_ta_of(mtav, tc)
            cmp_v, ssr_v, _, sl_ss_v = NL.compare(rc, LEDGES, rho, ss, r_ta_v, R["dx"])
            ent.update(M_ta_v=mtav, dress_side=float(R["rows"][kk]["dress_side"]), r_ta_v=float(r_ta_v),
                       r_ta_v_direct=R["rows"][kk]["r_ta_v"], vs_selfsim_v=cmp_v, ssr_v=ssr_v.tolist(),
                       slope_ss_v=sl_ss_v.tolist())
            for law, ref in R["refs"].items():
                j = int(np.argmin(np.abs(ref["snap_t"] - pr["t"])))
                rp = ref_profile(ref, j, rho_b)
                mref = float(np.interp(ref["snap_t"][j], ref["g_t"], ref["g_mta"]))
                r_ta_ref = NL.r_ta_of(mref, p["t_i"] + float(ref["snap_t"][j]))
                cref, ssr_ref, slr, _ = NL.compare(rc, LEDGES, rp, ss, r_ta_ref, R["dx"])
                ok = (rc >= 4 * R["dx"]) & (rc <= r_ta) & (rp > 0) & (rho > 0)
                ratio = np.where(ok, rho / np.where(rp > 0, rp, np.nan), np.nan)
                okl = ok & (rc / r_ta >= cmp_["lambda_min"]) & (rc / r_ta <= cmp_["lambda_max"])

                def _dev(m_):
                    if not m_.any():
                        return None, None
                    d_ = ratio[m_] - 1
                    return float(np.max(np.abs(d_))), float(np.sqrt(np.mean(d_ ** 2)))
                md4, rd4 = _dev(ok)
                mdl, rdl = _dev(okl)
                ent[f"ref_{law}"] = dict(
                    rho=rp.tolist(), ssr=ssr_ref.tolist(), dt=float(ref["snap_t"][j] - pr["t"]),
                    M_ta=mref, r_ta=float(r_ta_ref), slope=slr.tolist(), shells_vs_selfsim=cref,
                    run_over_ref_4dx_rta=dict(r=rc[ok].tolist(), ratio=ratio[ok].tolist(),
                                              max_dev=md4, rms_dev=rd4),
                    run_over_ref_lambda_range=dict(lam=(rc[okl] / r_ta).tolist(),
                                                   ratio=ratio[okl].tolist(), max_dev=mdl, rms_dev=rdl))
            late.append(ent)
        out["late"] = late
        R["late"] = late
        summary[lab] = out

    # ---------- tables
    with open(os.path.join(a.out, "nm_growth.txt"), "w") as f:
        for lab in order:
            R = runs[lab]
            f.write(f"# {lab}: {R['dir']}\n# t_code a/a_i M_ta M_dress" +
                    "".join(f" M_ta_{l} M_dress_{l}" for l in R["refs"]) + "\n")
            for i, x in enumerate(R["rows"]):
                f.write(f"{x['t']:.4f} {x['a']:.5f} {x['mta']:.6f} {x['dress']:.6f}" +
                        "".join(f" {R['rm_' + l][i]:.6f} {R['rd_' + l][i]:.6f}" for l in R["refs"]) + "\n")
    with open(os.path.join(a.out, "nm_analysis.json"), "w") as f:
        json.dump(summary, f, indent=1)

    series = [fs.PAL["red"], fs.PAL["yellow"], fs.PAL["green"], fs.PAL["orange"]]
    cols = {lab: series[i % len(series)] for i, lab in enumerate(order)}
    lsty = {"kernel": "-", "plummer": "--", "point": ":", "hybrid": "-.", "kernel_cc": (0, (5, 1)),
            "hybrid_cc": (0, (3, 1, 1, 1))}
    a_max = max(max(x["a"] for x in runs[lab]["rows"]) for lab in order)
    m_max = max(max(x["mta"] for x in runs[lab]["rows"]) for lab in order)
    a_ticks = [t_ for t_ in (1.5, 2, 3, 4, 6, 8, 12, 16, 24, 30) if t_ <= a_max * 1.05]

    # ---------- figure 1: growth
    fig, axs = plt.subplots(2, 1, figsize=(fs.COLUMN_WIDTH * 1.5, 6.4), sharex=True,
                            gridspec_kw=dict(height_ratios=[2.2, 1]))
    fig.subplots_adjust(left=0.13, right=0.97, bottom=0.08, top=0.98, hspace=0.04)
    for lab in order:
        R = runs[lab]
        av = np.array([x["a"] for x in R["rows"]])
        mta = np.array([x["mta"] for x in R["rows"]])
        dr = np.array([x["dress"] for x in R["rows"]])
        c = cols.get(lab, fs.PAL["orange"])
        axs[0].plot(av, mta, "o", ms=2.5, color=c, label=f"{lab} ($\\Delta x$ = {R['dx']:.3g}): $M_{{\\rm ta}}$")
        axs[0].plot(av, dr, "s", ms=2.5, mfc="none", color=c, label=f"{lab}: dress")
        ti = R["p"]["t_i"]
        for law, ref in R["refs"].items():
            kw = dict(color=fs.PAL["blue"], ls=lsty.get(law, "-"), lw=1.0)
            ag = ((ti + ref["g_t"]) / ti) ** (2.0 / 3.0)
            axs[0].plot(ag, ref["g_mta"], **kw)
            axs[0].plot(ag, ref["g_dress"], **kw)
            if law == "kernel":
                k = av >= 1.2
                axs[1].plot(av[k], mta[k] / R["rm_kernel"][k] - 1, "o", ms=2.5, color=c)
                kd = k & (R["rd_kernel"] > 0.02)
                axs[1].plot(av[kd], dr[kd] / R["rd_kernel"][kd] - 1, "s", ms=2.5, mfc="none", color=c)
    aa = np.linspace(1, max(8.0, a_max), 50)
    axs[0].plot(aa, 1 + C_TA * aa, **fs.GUIDE, label=r"self-similar: $1 + 0.565\,a/a_i$, $0.625\,M_{\rm ta}$")
    axs[0].plot(aa, SS_DRESS_FRAC * (1 + C_TA * aa), **fs.GUIDE)
    laws_used = sorted({law for lab in order for law in runs[lab]["refs"]})
    names = {"kernel": "mesh kernel", "plummer": "Plummer $s_{\\rm eff}$", "point": "$s$ = 0.05",
             "hybrid": "hybrid (kernel seed, dust unsoftened)",
             "kernel_cc": "cell-centre kernel", "hybrid_cc": "hybrid, cell-centre kernel"}
    for law in laws_used:
        axs[0].plot([], [], color=fs.PAL["blue"], lw=1.0, ls=lsty.get(law, "-"), label=f"shells, {names.get(law, law)}")
    axs[0].set_yscale("log")
    axs[0].set_ylim(0.02, max(8.0, 1.5 * m_max))
    axs[0].set_ylabel(r"mass [$M$]")
    axs[0].legend(loc="lower right", fontsize=7, ncol=2)
    axs[1].axhline(0, **fs.GUIDE)
    axs[1].axhspan(-0.02, 0.02, color="grey", alpha=0.15)
    axs[1].set_ylim(-0.15, 0.15)
    axs[1].set_xscale("log")
    axs[1].set_xlim(1.15, max(8.5, 1.06 * a_max))
    axs[1].set_xticks(a_ticks)
    axs[1].set_xticklabels([f"{t_:g}" for t_ in a_ticks])
    axs[1].set_xlabel(r"$a/a_i$", labelpad=-2)
    axs[1].set_ylabel("run / kernel shells $-$ 1")
    fs.save(fig, os.path.join(a.out, "nm_growth"))
    plt.close(fig)

    # ---------- figure 2: profiles
    rc = np.sqrt(LEDGES[1:] * LEDGES[:-1])
    n = len(order)
    fig, axs = plt.subplots(2, n, figsize=(fs.FULL_WIDTH, 5.2), sharex="col",
                            gridspec_kw=dict(height_ratios=[2, 1]))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.09, top=0.94, hspace=0.04, wspace=0.28)
    axs = np.atleast_2d(axs).reshape(2, n)
    pcols = [fs.PAL["red"], fs.PAL["yellow"], fs.PAL["green"], fs.PAL["orange"]]
    for i, lab in enumerate(order):
        R = runs[lab]
        ax, axr = axs[0, i], axs[1, i]
        for j, ent in enumerate(R["prof"]):
            c = pcols[j % len(pcols)]
            rho = np.array(ent["rho"])
            ok = rho > 0
            ax.plot(rc[ok], rho[ok], "o-", ms=2.5, lw=1.0, color=c, label=f"$a/a_i$ = {ent['a']:.2f}")
            for law in R["refs"]:
                rp = np.array(ent[f"ref_{law}"])
                okr = rp > 0
                ax.plot(rc[okr], rp[okr], color=c, ls=lsty.get(law, "-"), lw=0.8, alpha=0.8)
                if law == "kernel":
                    o2 = ok & okr
                    axr.plot(rc[o2], rho[o2] / rp[o2], "o-", ms=2.5, lw=1.0, color=c)
            ax.axvline(ent["r_ta_selfsim_def"], color=c, lw=0.8, ls="-.", alpha=0.6)
        for q in (2, 4):
            ax.axvline(q * R["dx"], **fs.MASK_LINE)
            axr.axvline(q * R["dx"], **fs.MASK_LINE)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_ylim(0.3, 3e4)
        ax.set_title(f"{lab}, $\\Delta x$ = {R['dx']:.3g} $M$", fontsize=10)
        ax.legend(loc="upper right", fontsize=7)
        axr.set_xscale("log")
        axr.axhline(1, **fs.GUIDE)
        axr.axhspan(0.7, 1.3, color="grey", alpha=0.15)
        axr.set_ylim(0.3, 1.7)
        axr.set_xlim(0.5, max(250.0, 1.6 * R["prof"][-1]["r_ta_selfsim_def"]))
        axr.set_xlabel(r"$r$ [$GM/c^2$]", labelpad=-2)
        if i == 0:
            ax.set_ylabel(r"$\rho/\rho_b(t)$ (dust)")
            axr.set_ylabel("run / kernel shells")
    fs.save(fig, os.path.join(a.out, "nm_profiles"))
    plt.close(fig)

    # ---------- figure 3: against the self-similar solution
    fig, ax = plt.subplots(figsize=(fs.COLUMN_WIDTH * 1.4, 4.0))
    fig.subplots_adjust(left=0.14, right=0.97, bottom=0.12, top=0.97)
    ax.plot(ss["rc"], ss["rho"], color=fs.PAL["blue"], lw=1.5, label="self-similar (test 2)")
    j = 0
    for lab in order:
        R = runs[lab]
        for ent in R["prof"]:
            if not any(abs(ent["a"] / x_ - 1) < 0.05 for x_ in (4.0, 8.0, 16.0, 30.0)):
                continue
            rho = np.array(ent["rho"])
            ok = rho > 0
            lam = rc / ent["r_ta_selfsim_def"]
            ax.plot(lam[ok], rho[ok], "o-", ms=2.5, lw=1.0, color=pcols[j % 4],
                    label=f"{lab}, $a/a_i$ = {ent['a']:.2f}")
            ax.axvline(2 * R["dx"] / ent["r_ta_selfsim_def"], color=pcols[j % 4], lw=0.8, ls=":")
            j += 1
    ll = np.geomspace(1e-3, 0.3, 20)
    ax.plot(ll, 3.0 * ll ** -2.25, **fs.GUIDE, label=r"$3\,\lambda^{-9/4}$")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(5e-3, 2)
    ax.set_ylim(0.5, 1e5)
    ax.set_xlabel(r"$\lambda = r/r_{\rm ta}(t)$")
    ax.set_ylabel(r"$\rho/\rho_b(t)$")
    ax.legend(loc="upper right", fontsize=8)
    fs.save(fig, os.path.join(a.out, "nm_selfsim"))
    plt.close(fig)

    # ---------- figure 4: clump and conservation
    fig, axs = plt.subplots(3, 1, figsize=(fs.COLUMN_WIDTH * 1.4, 6.4), sharex=True)
    fig.subplots_adjust(left=0.16, right=0.97, bottom=0.08, top=0.98, hspace=0.05)
    for lab in order:
        R = runs[lab]
        c = cols.get(lab, fs.PAL["orange"])
        av = np.array([x["a"] for x in R["rows"]])
        axs[0].plot(av, [x["clump_r90"] / R["dx"] for x in R["rows"]], "-", color=c, label=f"{lab}: $r_{{90}}$")
        axs[0].plot(av, [x["clump_rms"] / R["dx"] for x in R["rows"]], "--", color=c, label=f"{lab}: $r_{{\\rm rms}}$")
        axs[0].plot(av, [max(np.abs(x["com"])) / R["dx"] + 1e-18 for x in R["rows"]], ":", color=c,
                    label=f"{lab}: |centre of mass|")
        ah = ((R["p"]["t_i"] + R["ht"]) / R["p"]["t_i"]) ** (2 / 3)
        axs[1].plot(ah, (R["E"] - R["E"][0]) / abs(R["hst"]["W"][0]), color=c)
        axs[2].plot(ah, R["P"] + 1e-20, color=c)
    axs[0].set_yscale("log")
    axs[0].set_ylabel(r"clump radii / $\Delta x$")
    axs[0].legend(fontsize=6, ncol=3, loc="lower right")
    axs[1].set_ylabel(r"$\Delta(K+W)/|W_0|$")
    axs[2].set_yscale("log")
    axs[2].set_ylabel(r"$|\sum m\,\mathbf{v}|$ [$M c$]")
    axs[2].set_xlabel(r"$a/a_i$", labelpad=-2)
    fs.save(fig, os.path.join(a.out, "nm_clump"))
    plt.close(fig)

    # ---------- figure 5: phase space at the last snapshot against the kernel shells
    fig, axs = plt.subplots(1, n, figsize=(fs.FULL_WIDTH, 3.0), sharey=False)
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.15, top=0.92, wspace=0.25)
    axs = np.atleast_1d(axs)
    for i, lab in enumerate(order):
        R = runs[lab]
        key = sorted(R["phase"].keys(), key=float)[-1]
        ph = R["phase"][key]
        if "kernel" in R["refs"]:
            ref = R["refs"]["kernel"]
            axs[i].plot(np.abs(ref["snap_r"][-1]), np.sign(ref["snap_r"][-1]) * ref["snap_v"][-1], "-",
                        lw=2.0, color=fs.PAL["blue"], alpha=0.35, label="shells, mesh kernel")
        axs[i].plot(ph["r"], ph["vr"], ".", ms=0.6, color=fs.PAL["red"], alpha=0.6, label="run (1/25 of the dust)")
        if i == 0:
            axs[i].legend(loc="lower right", fontsize=7, markerscale=8)
        axs[i].set_xscale("log")
        axs[i].set_xlim(0.3, max(300.0, 1.6 * R["prof"][-1]["r_ta_selfsim_def"]))
        vlim = max(1.6, 1.1 * float(np.nanpercentile(np.abs(ph["vr"]), 99.9)))
        axs[i].set_ylim(-vlim, vlim)
        axs[i].set_title(f"{lab}, $a/a_i$ = {float(key):.2f}", fontsize=10)
        axs[i].set_xlabel(r"$r$ [$GM/c^2$]", labelpad=-2)
    axs[0].set_ylabel(r"$v_r$ [$c$]")
    fs.save(fig, os.path.join(a.out, "nm_phase"))
    plt.close(fig)

    # ---------- figure 6 (wave 3): late profiles in units of r_ta, one figure per run
    rcL = np.sqrt(LEDGES[1:] * LEDGES[:-1])
    for lab in order:
        R = runs[lab]
        L = R.get("late", [])
        if not L:
            continue
        nc = len(L)
        fig, axs = plt.subplots(3, nc, figsize=(max(fs.FULL_WIDTH * nc / 3.0, fs.COLUMN_WIDTH * 1.4), 6.8),
                                sharex="col", gridspec_kw=dict(height_ratios=[2, 1, 1]), squeeze=False)
        fig.subplots_adjust(left=0.09, right=0.98, bottom=0.08, top=0.95, hspace=0.05, wspace=0.28)
        for j, ent in enumerate(L):
            ax, axr, axl = axs[0, j], axs[1, j], axs[2, j]
            lam = rcL / ent["r_ta"]
            rho, ssr = np.array(ent["rho"]), np.array(ent["ssr"])
            sl, sls = np.array(ent["slope"]), np.array(ent["slope_ss"])
            ok, oks = rho > 0, np.isfinite(ssr) & (ssr > 0)
            ax.plot(lam[oks], ssr[oks], color=fs.PAL["blue"], lw=1.6, label="self-similar, same bins")
            axl.plot(lam, sls, color=fs.PAL["blue"], lw=1.6)
            for law in R["refs"]:
                rf = ent[f"ref_{law}"]
                lr = rcL / rf["r_ta"]
                rp, sr = np.array(rf["rho"]), np.array(rf["ssr"])
                okr = rp > 0
                ax.plot(lr[okr], rp[okr], color="k", ls=lsty.get(law, "-"), lw=0.9, label=f"shells, {law}")
                with np.errstate(invalid="ignore", divide="ignore"):
                    axr.plot(lr, np.where(okr, rp, np.nan) / sr, color="k", ls=lsty.get(law, "-"), lw=0.8)
                axl.plot(lr, np.array(rf["slope"]), color="k", ls=lsty.get(law, "-"), lw=0.8)
            ax.plot(lam[ok], rho[ok], "o", ms=3.0, color=fs.PAL["red"], label=f"{lab} (run)")
            with np.errstate(invalid="ignore", divide="ignore"):
                axr.plot(lam, np.where(ok, rho, np.nan) / ssr, "o-", ms=3.0, lw=1.0, color=fs.PAL["red"])
            axl.plot(lam, sl, "o-", ms=3.0, lw=1.0, color=fs.PAL["red"])
            lmin = ent["vs_selfsim"]["lambda_min"]
            for axx in (ax, axr, axl):
                axx.axvline(lmin, **fs.MASK_LINE)
                axx.axvline(0.3, color="grey", lw=0.8, ls=":")
                axx.axvline(2.0 * R["dx"] / ent["r_ta"], color="grey", lw=0.8, ls="-.")
            ax.set_xscale("log")
            ax.set_yscale("log")
            ax.set_xlim(3e-3, 2.0)
            ax.set_ylim(0.5, 1e5)
            vs = ent["vs_selfsim"]
            ax.set_title(f"$a/a_i$ = {ent['a']:.2f}" + (f", max dev {vs['max_dev']:.2f}" if vs["max_dev"] is not None else ""),
                         fontsize=9)
            axr.axhline(1, **fs.GUIDE)
            axr.axhspan(0.75, 1.25, color="grey", alpha=0.15)
            axr.set_ylim(0.2, 1.8)
            axl.axhline(-2.25, **fs.GUIDE)
            axl.set_ylim(-4.0, 0.0)
            axl.set_xlabel(r"$\lambda = r/r_{\rm ta}$", labelpad=-2)
            if j == 0:
                ax.set_ylabel(r"$\rho/\rho_b(t)$ (dust)")
                axr.set_ylabel("/ self-similar")
                axl.set_ylabel(r"$d\ln\rho/d\ln r$")
                ax.legend(loc="lower left", fontsize=6.5)
        fs.save(fig, os.path.join(a.out, f"nm_late_profiles_{lab}"))
        plt.close(fig)

    # ---------- figure 7 (wave 3): approach of the masses to the self-similar values
    fig, axs = plt.subplots(2, 1, figsize=(fs.COLUMN_WIDTH * 1.5, 6.0), sharex=True,
                            gridspec_kw=dict(height_ratios=[1.6, 1]))
    fig.subplots_adjust(left=0.14, right=0.97, bottom=0.08, top=0.98, hspace=0.05)
    lawcol = {"kernel": fs.PAL["blue"], "hybrid": fs.PAL["green"], "point": fs.PAL["orange"],
              "plummer": fs.PAL["yellow"], "kernel_cc": "#7a3fbf", "hybrid_cc": "#8c564b"}
    mk = ["o", "s", "^", "D"]
    for i, lab in enumerate(order):
        R = runs[lab]
        av = np.array([x["a"] for x in R["rows"]])
        mta = np.array([x["mta"] for x in R["rows"]])
        dr = np.array([x["dress"] for x in R["rows"]])
        st = max(1, len(av) // 60)
        axs[0].plot(av[::st], mta[::st] / av[::st], mk[i % 4], ms=2.5, color=fs.PAL["red"],
                    label=f"{lab}: $M_{{\\rm ta}}/(M a/a_i)$")
        k = dr > 0
        axs[0].plot(av[k][::st], (dr / mta)[k][::st], mk[i % 4], ms=2.5, mfc="none", color=fs.PAL["red"],
                    label=f"{lab}: dress/$M_{{\\rm ta}}$")
        ti = R["p"]["t_i"]
        for law, ref in R["refs"].items():
            ag = ((ti + ref["g_t"]) / ti) ** (2.0 / 3.0)
            c = lawcol.get(law, "k")
            if i == 0:
                axs[0].plot(ag, ref["g_mta"] / ag, color=c, ls=lsty.get(law, "-"), lw=1.0, label=f"shells, {law}")
                axs[0].plot(ag, ref["g_dress"] / ref["g_mta"], color=c, ls=lsty.get(law, "-"), lw=1.0)
            rm = np.interp(av, ag, ref["g_mta"])
            rd = np.interp(av, ag, ref["g_dress"])
            kk = av >= 1.2
            axs[1].plot(av[kk][::st], (mta / rm - 1)[kk][::st], mk[i % 4], ms=2.5, color=c,
                        label=f"{lab} / {law}: $M_{{\\rm ta}}$")
            kd = kk & (rd > 0.02)
            axs[1].plot(av[kd][::st], (dr / np.where(rd > 0, rd, np.nan) - 1)[kd][::st], mk[i % 4], ms=2.5,
                        mfc="none", color=c, label=f"{lab} / {law}: dress")
    axs[0].axhline(C_TA, **fs.GUIDE)
    axs[0].axhline(SS_DRESS_FRAC, **fs.GUIDE)
    axs[0].text(1.25, C_TA - 0.045, "0.565", fontsize=7)
    axs[0].text(1.25, SS_DRESS_FRAC + 0.015, "0.625", fontsize=7)
    axs[0].set_ylim(0.0, 1.0)
    axs[0].legend(fontsize=6, loc="lower right", ncol=2)
    axs[1].axhline(0, **fs.GUIDE)
    axs[1].axhspan(-0.01, 0.01, color="grey", alpha=0.15)
    axs[1].set_ylim(-0.06, 0.06)
    axs[1].set_xscale("log")
    axs[1].set_xlim(1.15, max(8.5, 1.06 * a_max))
    axs[1].set_xticks(a_ticks)
    axs[1].set_xticklabels([f"{t_:g}" for t_ in a_ticks])
    axs[1].set_xlabel(r"$a/a_i$", labelpad=-2)
    axs[1].set_ylabel("run / shells $-$ 1")
    axs[1].legend(fontsize=5.5, loc="lower right", ncol=2)
    fs.save(fig, os.path.join(a.out, "nm_late_growth"))
    plt.close(fig)

    # ---------- figure 8 (wave 3): flag-based against flag-free estimators, relative to each shell law
    fig, axs = plt.subplots(2, 1, figsize=(fs.COLUMN_WIDTH * 1.5, 6.0), sharex=True)
    fig.subplots_adjust(left=0.15, right=0.97, bottom=0.08, top=0.98, hspace=0.05)
    for i, lab in enumerate(order):
        R = runs[lab]
        av = np.array([x["a"] for x in R["rows"]])
        mta = np.array([x["mta"] for x in R["rows"]])
        mtv = np.array([x["mta_v"] for x in R["rows"]])
        dr = np.array([x["dress"] for x in R["rows"]])
        dsd = np.array([x["dress_side"] for x in R["rows"]])
        ti = R["p"]["t_i"]
        st = max(1, len(av) // 80)
        for law, ref in R["refs"].items():
            if law in ("plummer",):
                continue
            ag = ((ti + ref["g_t"]) / ti) ** (2.0 / 3.0)
            rm = np.interp(av, ag, ref["g_mta"])
            rd = np.interp(av, ag, ref["g_dress"])
            c = lawcol.get(law, "k")
            kk = av >= 1.2
            axs[0].plot(av[kk][::st], (mta / rm - 1)[kk][::st], mk[i % 4], ms=2.2, mfc="none", color=c,
                        label=f"{lab}/{law}: flags" if i == 0 else None)
            axs[0].plot(av[kk][::st], (mtv / rm - 1)[kk][::st], mk[i % 4], ms=2.2, color=c,
                        label=f"{lab}/{law}: $v_r$ crossing" if i == 0 else None)
            kd = kk & (rd > 0.02)
            axs[1].plot(av[kd][::st], (dr / np.where(rd > 0, rd, np.nan) - 1)[kd][::st], mk[i % 4], ms=2.2,
                        mfc="none", color=c, label=f"{lab}/{law}: flags" if i == 0 else None)
            axs[1].plot(av[kd][::st], (dsd / np.where(rd > 0, rd, np.nan) - 1)[kd][::st], mk[i % 4], ms=2.2,
                        color=c, label=f"{lab}/{law}: other side" if i == 0 else None)
    for axx, nm_ in zip(axs, ("$M_{\\rm ta}$", "dress")):
        axx.axhline(0, **fs.GUIDE)
        axx.axhspan(-0.01, 0.01, color="grey", alpha=0.15)
        axx.set_ylim(-0.15, 0.15)
        axx.set_ylabel(f"{nm_}: run / shells $-$ 1")
        axx.legend(fontsize=5.5, loc="lower right", ncol=2)
    axs[1].set_xscale("log")
    axs[1].set_xlim(1.15, max(8.5, 1.06 * a_max))
    axs[1].set_xticks(a_ticks)
    axs[1].set_xticklabels([f"{t_:g}" for t_ in a_ticks])
    axs[1].set_xlabel(r"$a/a_i$", labelpad=-2)
    fs.save(fig, os.path.join(a.out, "nm_estimators"))
    plt.close(fig)

    # ---------- table of the late comparison
    with open(os.path.join(a.out, "nm_late.txt"), "w") as f:
        f.write("# run a M_ta dress dress/M_ta M_ta/(M a/a_i) | vs self-similar on [lambda_min, 0.3]: "
                "lambda_min nbins max_dev rms_dev fit_slope (ss) mean_local_slope (ss) max|dslope| "
                "| per ref: M_ta_rel dress_rel run/shells max_dev rms_dev on the same range\n")
        for lab in order:
            for ent in runs[lab].get("late", []):
                vs = ent["vs_selfsim"]
                fmt = lambda x: "nan" if x is None else f"{x:.3f}"
                line = (f"{lab} {ent['a']:.3f} {ent['M_ta']:.4f} {ent['dress']:.4f} "
                        f"{ent['dress'] / ent['M_ta']:.4f} {ent['M_ta'] / ent['a']:.4f} | "
                        f"{vs['lambda_min']:.4f} {vs['n_bins']} {fmt(vs['max_dev'])} {fmt(vs['rms_dev'])} "
                        f"{fmt(vs.get('fit_slope'))} ({fmt(vs.get('fit_slope_ss'))}) {fmt(vs['slope_mean'])} "
                        f"({fmt(vs['slope_ss_mean'])}) {fmt(vs['slope_max_absdiff'])}")
                for law in runs[lab]["refs"]:
                    rf = ent[f"ref_{law}"]
                    mrel = ent["M_ta"] / rf["M_ta"] - 1
                    j = int(np.argmin(np.abs(runs[lab]["refs"][law]["snap_t"] - ent["t"])))
                    rd_ = float(np.interp(runs[lab]["refs"][law]["snap_t"][j], runs[lab]["refs"][law]["g_t"],
                                          runs[lab]["refs"][law]["g_dress"]))
                    lr_ = rf["run_over_ref_lambda_range"]
                    line += (f" | {law}: {mrel:+.4f} {ent['dress'] / rd_ - 1 if rd_ > 0 else float('nan'):+.4f} "
                             f"{fmt(lr_['max_dev'])} {fmt(lr_['rms_dev'])}")
                f.write(line + "\n")
                f.write("    ratios run/ss: " + " ".join(f"{l_:.3f}:{r_:.3f}" for l_, r_ in zip(vs["lam"], vs["ratio"]))
                        + "\n    slopes run/ss: " + " ".join(f"{l_:.3f}:{s_:.2f}/{t_:.2f}" for l_, s_, t_ in
                                                           zip(vs["slope_lam"], vs["slope"], vs["slope_ss"])) + "\n")
                # flag-free estimators (H2): M_ta(v), dress(side), and the profile with r_ta from M_ta(v)
                vv = ent["vs_selfsim_v"]
                line2 = (f"    flag-free: M_ta(v) {ent['M_ta_v']:.4f} (r_ta measured {fmt(ent['r_ta_v_direct'])}, "
                         f"from M_ta(v) {ent['r_ta_v']:.3f}) dress(side) {ent['dress_side']:.4f} "
                         f"dress(side)/M_ta(v) {ent['dress_side'] / ent['M_ta_v']:.4f} M_ta(v)/(M a/a_i) "
                         f"{ent['M_ta_v'] / ent['a']:.4f} | vs ss: {vv['lambda_min']:.4f} {vv['n_bins']} "
                         f"{fmt(vv['max_dev'])} {fmt(vv['rms_dev'])} {fmt(vv.get('fit_slope'))} "
                         f"({fmt(vv.get('fit_slope_ss'))}) {fmt(vv['slope_mean'])} ({fmt(vv['slope_ss_mean'])}) "
                         f"{fmt(vv['slope_max_absdiff'])}")
                for law in runs[lab]["refs"]:
                    rf = ent[f"ref_{law}"]
                    j = int(np.argmin(np.abs(runs[lab]["refs"][law]["snap_t"] - ent["t"])))
                    rd_ = float(np.interp(runs[lab]["refs"][law]["snap_t"][j], runs[lab]["refs"][law]["g_t"],
                                          runs[lab]["refs"][law]["g_dress"]))
                    line2 += (f" | {law}: {ent['M_ta_v'] / rf['M_ta'] - 1:+.4f} "
                              f"{ent['dress_side'] / rd_ - 1 if rd_ > 0 else float('nan'):+.4f}")
                f.write(line2 + "\n    ratios run/ss (r_ta from M_ta(v)): " +
                        " ".join(f"{l_:.3f}:{r_:.3f}" for l_, r_ in zip(vv["lam"], vv["ratio"])) +
                        "\n    slopes run/ss (r_ta from M_ta(v)): " +
                        " ".join(f"{l_:.3f}:{s_:.2f}/{t_:.2f}" for l_, s_, t_ in
                                 zip(vv["slope_lam"], vv["slope"], vv["slope_ss"])) + "\n")
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk not in ("profiles", "late")}
                      for k, v in summary.items()}, indent=1))


if __name__ == "__main__":
    main()
