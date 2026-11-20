"""V1: independent recomputation of the ES-1 / V-1 claims (verifier_g1, JOURNAL entry 1).

Reads: the data set (table, particle file, puncture mass from the run's input), the
trajectory files, the snapshots and the horizon summary of ES-1 and V-1, with the readers
of vreaders.py. Writes v1_results.json and figures into $NRPIC_RUN_DIR (or --out).
"""
import argparse
import glob
import json
import os
import re

import numpy as np

import vreaders as V
import figstyle as fs

S = "/data/haiyangw/nrpic/scratch/D-bh-dress"
RUNS = {"ES-1": (S + "/D-20261115-172726-60ba4c2", "es"),
        "V-1": (S + "/D-20261115-172730-c6d151b", "v1")}
DATA = S + "/D-20261115-170213-d2c2131"
NTR = 140
WALL = list(range(56, 70))


def input_value(path, key):
    with open(path) as f:
        for l in f:
            m = re.match(r"\s*%s\s*=\s*(\S+)" % key, l)
            if m:
                return m.group(1)
    raise KeyError(key)


def areal_radius(x, g):
    """x: (n,3) coordinate positions; g: (n,6) gamma xx xy xz yy yz zz."""
    r = np.linalg.norm(x, axis=1)
    n = x / r[:, None]
    G = np.empty((len(x), 3, 3))
    G[:, 0, 0], G[:, 0, 1], G[:, 0, 2] = g[:, 0], g[:, 1], g[:, 2]
    G[:, 1, 0], G[:, 1, 1], G[:, 1, 2] = g[:, 1], g[:, 3], g[:, 4]
    G[:, 2, 0], G[:, 2, 1], G[:, 2, 2] = g[:, 2], g[:, 4], g[:, 5]
    tr = G[:, 0, 0] + G[:, 1, 1] + G[:, 2, 2]
    A = np.einsum("ni,nij,nj->n", n, G, n)
    B = 0.5 * (tr - A)
    det = np.linalg.det(G)
    B2 = np.sqrt(det / A)          # second definition, equal to B in spherical symmetry
    return r * np.sqrt(B), r * np.sqrt(B2), r


def exact_orbit(R0, m, Et2, KT0):
    """Radial geodesic in Schwarzschild of mass m from R0 with dR/dtau = -R0 KT0 and
    Etilde^2 = Et2. Returns R(tau) callable and the proper time to R = 2m (or None)."""
    if abs(1 - Et2) < 1e-8:
        c = 1.5 * np.sqrt(2 * m)
        return (lambda tau: (R0 ** 1.5 + c * tau) ** (2.0 / 3.0)), None
    assert Et2 < 1
    Rmax = 2 * m / (1 - Et2)
    A = np.sqrt(Rmax ** 3 / (8 * m))
    eta0 = -np.arccos(np.clip(2 * R0 / Rmax - 1, -1, 1)) * (1 if -KT0 >= 0 else -1)
    eta1 = np.arccos(2 * 2 * m / Rmax - 1)
    tau_of = lambda eta: A * ((eta + np.sin(eta)) - (eta0 + np.sin(eta0)))
    eg = np.linspace(eta0, np.pi * 0.999999, 200001)
    tg = tau_of(eg)
    Rg = 0.5 * Rmax * (1 + np.cos(eg))

    def R_of(tau):
        return np.interp(tau, tg, Rg)
    return R_of, tau_of(eta1)


def crossing(tau, R, Rc=2.0):
    """Proper time where R first falls below Rc (cubic through four samples)."""
    i = np.where(R < Rc)[0]
    if len(i) == 0:
        return None
    k = i[0]
    lo = max(k - 2, 0)
    hi = min(lo + 4, len(R))
    lo = hi - 4
    p = np.polyfit(R[lo:hi] - Rc, tau[lo:hi], 3)
    return float(np.polyval(p, 0.0)), float(np.interp(Rc, R[k - 1:k + 1][::-1], tau[k - 1:k + 1][::-1]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    ap.add_argument("--snap_every", type=int, default=1)
    args = ap.parse_args()
    out = args.out
    fs.use_style()
    import matplotlib.pyplot as plt
    res = {"inputs": {}}

    # ---------------- exact references from the data set ----------------
    ref = {}
    for name, (rdir, base) in RUNS.items():
        sub = "es" if base == "es" else "v1"
        m_p = float(input_value("/data/haiyangw/nrpic/wt/D-bh-dress/tracks/D-bh-dress/es_runs/inputs/%s_dx8.athinput" % ("es1" if base == "es" else "v1"), "comp1_mass"))
        tab = V.Table2(DATA + "/%s/%s.tab" % (sub, sub))
        pf = V.read_particle_file(DATA + "/%s/%s.nrp" % (sub, sub))
        x0 = pf["x"][:NTR]
        rb0 = np.linalg.norm(x0, axis=1)
        sph = V.sphere_of_table(tab, m_p, rb0)
        Et2 = 1 - 2 * sph["m"] / sph["R"] + sph["R"] ** 2 * sph["KT"] ** 2
        orbits = []
        for p in range(NTR):
            Rf, tc = exact_orbit(sph["R"][p], sph["m"][p], Et2[p], sph["KT"][p])
            orbits.append((Rf, tc))
        ref[name] = dict(R0=sph["R"], m=sph["m"], Et2=Et2, KT=sph["KT"], orbits=orbits,
                         u0=pf["u"][:NTR], m_p=m_p)
        groups = {}
        for g in range(10):
            tags = range(14 * g, 14 * g + 14)
            groups[g] = dict(R0=[float(sph["R"][p]) for p in tags][:1],
                             R0_spread=float(np.ptp(sph["R"][list(tags)])),
                             m=float(np.mean(sph["m"][list(tags)])),
                             Etilde2=float(np.mean(Et2[list(tags)])),
                             tau_2M_exact=(None if orbits[14 * g][1] is None else float(orbits[14 * g][1])))
        res.setdefault("exact", {})[name] = groups
        res["exact"][name]["m_p"] = m_p
        res["exact"][name]["max_|u_i|_tracers_t0"] = float(np.abs(pf["u"][:NTR]).max())

    # ---------------- tracers ----------------
    figT, axT = plt.subplots(2, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 5.2), sharex=True)
    figT.subplots_adjust(left=0.14, right=0.97, bottom=0.1, top=0.97, hspace=0.08)
    figC, axC = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 3.4))
    figC.subplots_adjust(left=0.13, right=0.97, bottom=0.14, top=0.96)
    for ir, (name, (rdir, base)) in enumerate(RUNS.items()):
        tm = V.read_trajmet(rdir + "/%s.trajmet.bin" % base)
        tr = V.read_traj(rdir + "/%s.traj.bin" % base)
        assert len(tm) == len(tr) and np.all(tm[:, :2] == tr[:, :2])
        R, R2, rc = areal_radius(tr[:, 2:5], tm[:, 6:12])
        tau = tm[:, 12]
        tags = tm[:, 1].astype(int)
        t = tm[:, 0]
        o = ref[name]["orbits"]
        rr = {"wall": {}, "groups": {}}
        worst = 0.0
        worst_def2 = 0.0
        for p in WALL:
            s = tags == p
            tt, ta, Rp, R2p = t[s], tau[s], R[s], R2[s]
            keep = ta <= 200.0
            err = Rp[keep] / o[p][0](ta[keep]) - 1
            err2 = R2p[keep] / o[p][0](ta[keep]) - 1
            errall = Rp / o[p][0](ta) - 1
            rr["wall"][p] = dict(max_abs=float(np.abs(err).max()), tau_max=float(ta.max()),
                                 max_abs_whole_run=float(np.abs(errall).max()),
                                 err_at_end=float(errall[-1]),
                                 t_at_tau200=float(np.interp(200.0, ta, tt)) if ta.max() >= 200 else None,
                                 max_abs_def2=float(np.abs(err2).max()),
                                 dir=[float(v) for v in np.round(tr[tags == p][0, 2:5] / np.linalg.norm(tr[tags == p][0, 2:5]), 3)])
            worst = max(worst, np.abs(err).max())
            worst_def2 = max(worst_def2, np.abs(err2).max())
            axT[ir].plot(ta, Rp / o[p][0](ta) - 1, lw=0.8,
                         color=fs.PAL["red"] if abs(rr["wall"][p]["dir"][0]) in (0.0, 1.0) and max(abs(np.array(rr["wall"][p]["dir"]))) > 0.99 else fs.PAL["orange"])
        rr["wall_max_abs_tau_le_200"] = float(worst)
        rr["wall_max_abs_tau_le_200_def2"] = float(worst_def2)
        axT[ir].axhline(0, **fs.GUIDE)
        axT[ir].axvline(200, **fs.MASK_LINE)
        axT[ir].set_ylabel(r"$R/R_w(\tau)-1$, %s" % name)
        axT[ir].text(0.02, 0.9, "%s: max |err| (tau<=200) = %.3g" % (name, worst),
                     transform=axT[ir].transAxes)
        # inner groups
        for g, col in ((0, fs.PAL["red"]), (1, fs.PAL["orange"]), (2, fs.PAL["green"])):
            cr = []
            crl = []
            dev = 0.0
            for p in range(14 * g, 14 * g + 14):
                s = tags == p
                ta, Rp = tau[s], R[s]
                c = crossing(ta, Rp)
                if c is not None:
                    cr.append(c[0])
                    crl.append(c[1])
                kk = Rp > 2.0
                dev = max(dev, np.abs(Rp[kk] - o[p][0](ta[kk])).max())
                if ir == 0:
                    axC.plot(ta, Rp, color=col, lw=0.8)
            tauex = o[14 * g][1]
            rr["groups"][g] = dict(R0=float(ref[name]["R0"][14 * g]),
                                   tau_2M_exact=float(tauex),
                                   n_crossed=len(cr),
                                   tau_2M_run_mean=(float(np.mean(cr)) if cr else None),
                                   tau_2M_run_min=(float(np.min(cr)) if cr else None),
                                   tau_2M_run_max=(float(np.max(cr)) if cr else None),
                                   tau_2M_run_mean_linear=(float(np.mean(crl)) if crl else None),
                                   t_last_record=float(t[tags == 14 * g].max()),
                                   max_abs_dR_before_2M=float(dev))
            if ir == 0:
                tg = np.linspace(0, tauex if tauex else 250, 400)
                axC.plot(tg, o[14 * g][0](tg), **fs.GUIDE)
        res.setdefault("tracers", {})[name] = rr
    axT[1].set_xlabel(r"proper time $\tau$ of the tracer ($M$)")
    axC.axhline(2.0, **fs.MASK_LINE)
    axC.set_xlabel(r"proper time $\tau$ ($M$)")
    axC.set_ylabel(r"areal radius $R$ ($M$), ES-1")
    axC.set_xlim(0, 260)
    axC.text(0.5, 0.9, "red/orange/green: R0 = 6, 10, 20 M tracers (run)\nblack dashed: closed-form geodesic",
             transform=axC.transAxes, ha="center", va="top")
    fs.save(figT, out + "/v1_wall")
    fs.save(figC, out + "/v1_inner")

    # ---------------- horizon mass ----------------
    figH, axH = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 3.4))
    figH.subplots_adjust(left=0.16, right=0.97, bottom=0.14, top=0.96)
    for name, (rdir, base), col in zip(RUNS, RUNS.values(), (fs.PAL["red"], fs.PAL["blue"])):
        h = V.read_horizon_summary(rdir + "/%s.horizon_summary_0.txt" % base)
        t, Mh = h["time"], h["mass"]
        ok = Mh > 0
        t, Mh = t[ok], Mh[ok]
        # duplicate times (restarts) keep the last
        _, idx = np.unique(t[::-1], return_index=True)
        idx = len(t) - 1 - idx
        t, Mh = t[idx], Mh[idx]
        i100 = np.argmin(np.abs(t - 100.0))
        M100 = Mh[i100]
        d = Mh / M100 - 1
        w1 = (t >= 100) & (t <= 200)
        w2 = (t >= 100) & (t <= 165)
        # alternative reference: mean over 95-105 M
        M100b = Mh[(t >= 95) & (t <= 105)].mean()
        db = Mh / M100b - 1
        res.setdefault("horizon", {})[name] = dict(
            t100_sample=float(t[i100]), M_AH_100=float(M100), M_AH_100_minus_M=float(M100 - 1),
            max_abs_100_200=float(np.abs(d[w1]).max()), t_of_max_100_200=float(t[w1][np.argmax(np.abs(d[w1]))]),
            min_100_200=float(d[w1].min()), max_100_200=float(d[w1].max()),
            max_abs_100_165=float(np.abs(d[w2]).max()), min_100_165=float(d[w2].min()), max_100_165=float(d[w2].max()),
            max_abs_100_200_ref_mean95_105=float(np.abs(db[w1]).max()),
            max_abs_100_165_ref_mean95_105=float(np.abs(db[w2]).max()),
            t_last=float(t.max()), n_samples=int(len(t)), dt_median=float(np.median(np.diff(t))))
        axH.plot(t, d, color=col, label=name)
    axH.axvspan(100, 165, color=fs.PAL["blue"], alpha=0.08)
    axH.axhline(0, **fs.GUIDE)
    axH.set_xlim(90, 201)
    axH.set_ylim(-5e-4, 3e-4)
    axH.set_xlabel(r"$t$ ($M$)")
    axH.set_ylabel(r"$M_{\rm AH}(t)/M_{\rm AH}(100M)-1$")
    axH.legend(loc="lower left")
    fs.save(figH, out + "/v1_horizon")

    # ---------------- dust against the wall ----------------
    rdir, base = RUNS["ES-1"]
    snaps = sorted(glob.glob(rdir + "/%s.part.*.bin" % base))[::args.snap_every]
    p0 = V.read_particle_file(DATA + "/es/es.nrp")
    dust0 = set(range(NTR, p0["n"]))
    x0d_by_tag = p0["x"][NTR:]
    rows = []
    for sp in snaps:
        s = V.read_snapshot(sp)
        tg = s["tag"]
        isd = tg >= NTR
        xw = np.array([s["x"][tg == p][0] for p in WALL if np.any(tg == p)])
        rw = np.linalg.norm(xw, axis=1)
        nw = xw / rw[:, None]
        xd = s["x"][isd]
        rd = np.linalg.norm(xd, axis=1)
        nd = xd / rd[:, None]
        cosang = nd @ nw.T
        near = np.argmax(cosang, axis=1)
        marg_dir = rd - rw[near]
        # cones around each wall tracer direction
        cones = {}
        for deg in (3.0, 6.0, 10.0):
            c = np.cos(np.radians(deg))
            mm = []
            for j in range(len(rw)):
                sel = cosang[:, j] >= c
                if sel.any():
                    mm.append(float((rd[sel] - rw[j]).min()))
            cones["%g" % deg] = dict(min=min(mm) if mm else None, n_dirs=len(mm))
        # wall radius in any direction from the lowest cubic harmonic,
        # r_w(n) = a + b (nx^4 + ny^4 + nz^4), least-squares fit to the 14 wall tracers
        q = (nw ** 4).sum(axis=1)
        Afit = np.vstack([np.ones_like(q), q]).T
        coef, *_ = np.linalg.lstsq(Afit, rw, rcond=None)
        fit_res = float(np.abs(Afit @ coef - rw).max())
        rw_model = coef[0] + coef[1] * (nd ** 4).sum(axis=1)
        marg_model = rd - rw_model
        kmin = int(np.argmin(marg_model))
        # test of the interpolation: the innermost dust layer as a probe of the angular
        # shape, r = a + b (r0 - 36.4) + c q4 + d q6; shape(n) from (c, d), scaled so that
        # it is 0 on the axes and 1 on the diagonals, then the wall r_w(n) =
        # r_axis + (r_diag - r_axis) shape(n)
        r0d = np.linalg.norm(x0d_by_tag[s["tag"][isd] - NTR], axis=1)
        lay = r0d < 36.7
        q4 = (nd[lay] ** 4).sum(axis=1)
        q6 = (nd[lay] ** 6).sum(axis=1)
        X = np.vstack([np.ones_like(q4), r0d[lay] - 36.4, q4, q6]).T
        cf, *_ = np.linalg.lstsq(X, rd[lay], rcond=None)
        resid = rd[lay] - X @ cf
        X2 = X[:, :3]
        cf2, *_ = np.linalg.lstsq(X2, rd[lay], rcond=None)
        resid2 = rd[lay] - X2 @ cf2
        shp = lambda nn: cf[2] * (nn ** 4).sum(axis=1) + cf[3] * (nn ** 6).sum(axis=1)
        e_ax = shp(np.array([[1.0, 0, 0]]))[0]
        e_dg = shp(np.array([[1.0, 1.0, 1.0]]) / np.sqrt(3))[0]
        ax_sel = np.abs(nw).max(axis=1) > 0.99
        r_ax, r_dg = rw[ax_sel].mean(), rw[~ax_sel].mean()
        if abs(e_dg - e_ax) > 1e-12:
            rw_dust_shape = r_ax + (r_dg - r_ax) * (shp(nd) - e_ax) / (e_dg - e_ax)
        else:
            rw_dust_shape = np.full_like(rd, r_ax)
        marg_shape = rd - rw_dust_shape
        layer = dict(n=int(lay.sum()), coef=[float(c) for c in cf], resid_max=float(np.abs(resid).max()),
                     resid_rms=float(np.sqrt((resid ** 2).mean())), resid_max_q4only=float(np.abs(resid2).max()),
                     margin_wall_from_dust_shape=float(marg_shape.min()),
                     n_inside_dust_shape=int((marg_shape < 0).sum()))
        missing_dust = len(dust0) - int(isd.sum())
        missing_tr = sorted(set(range(NTR)) - set(tg[~isd].tolist()))
        rows.append(dict(t=float(s["t"]), n=int(s["n"]), n_dust=int(isd.sum()), missing_dust=missing_dust,
                         missing_tracers=missing_tr, r_wall_min=float(rw.min()), r_wall_max=float(rw.max()),
                         r_dust_min=float(rd.min()), margin_all=float(rd.min() - rw.max()),
                         margin_nearest_dir=float(marg_dir.min()),
                         margin_cones=cones, margin_cubic_model=float(marg_model.min()),
                         cubic_fit_max_residual=fit_res, cubic_coef=[float(c) for c in coef],
                         dir_of_min_model=[float(v) for v in np.round(nd[kmin], 3)],
                         n_dust_inside_model=int((marg_model < 0).sum()),
                         inner_layer=layer,
                         tau_dust_median=float(np.median(s["tau"][isd]))))
        print("snapshot", sp, rows[-1])
    res["dust_vs_wall"] = rows
    figD, axD = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 3.4))
    figD.subplots_adjust(left=0.14, right=0.97, bottom=0.14, top=0.96)
    tt = [r["t"] for r in rows]
    axD.plot(tt, [r["margin_nearest_dir"] for r in rows], "o-", color=fs.PAL["red"], label="nearest wall tracer direction")
    axD.plot(tt, [r["margin_all"] for r in rows], "s--", color=fs.PAL["orange"], label="against the outermost wall tracer")
    axD.plot(tt, [r["margin_cubic_model"] for r in rows], "^-", color=fs.PAL["blue"], label="cubic-harmonic wall model")
    axD.plot(tt, [r["margin_cones"]["3"]["min"] for r in rows], "v-", color=fs.PAL["green"], label="3 deg cones of the wall tracers")
    axD.axhline(0, **fs.GUIDE)
    axD.set_xlabel(r"$t$ ($M$)")
    axD.set_ylabel(r"min $r_{\rm dust} - r_{\rm wall}$ ($M$, coordinate)")
    axD.legend(loc="upper left")
    fs.save(figD, out + "/v1_dust_wall")

    with open(out + "/v1_results.json", "w") as f:
        json.dump(res, f, indent=1, default=lambda o: o if not isinstance(o, np.generic) else o.item())
    print(json.dumps({k: res[k] for k in ("exact", "tracers", "horizon")}, indent=1, default=str)[:6000])


if __name__ == "__main__":
    main()
