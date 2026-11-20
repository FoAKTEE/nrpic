"""V1c: temperature step at lambda/L = 0.01 (TESTS.md T6(b)), own analysis.

Run C-20261119-144535-2c7b6a4, two seeds. Data: reduced.npz (slab sums and 200-bin profiles
of every snapshot, written by the driver), checked against my own sums of the first and
the last snapshot. Two fits of the slab rest mass M_s(t) (mass in the hot half [0, L/2)):
 (1) the definition of T6(b): the linear square-wave form
     M_s(t) = M/2 + (M_s(0) - M/2) (8/pi^2) sum_{j odd} exp(-chi (j k_1)^2 t)/j^2,
     chi free, over t in [20 t_coll, 2/(chi_1 k_1^2)]; ratio chi/chi_1 with
     chi_1 = kappa_1(theta_f)/(n c_p(theta_f)) at the final uniform state;
 (2) the nonlinear isobaric reference (heat_ref.py), kappa = f kappa_1(T), M_s(f t).
"""
import argparse
import glob
import json
import os
import sys

import numpy as np
from scipy.optimize import least_squares

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, "/data/haiyangw/nrpic/wt/C-sidm/python")
import lib  # noqa: E402
import heat_ref  # noqa: E402

K1C = heat_ref.K1C
THTAB = np.geomspace(1e-4, 1.0, 4001)
WTAB = np.array([lib.mean_w(x) for x in THTAB])          # increasing in theta
CVCP = np.array([lib.c_v(x)/(lib.c_v(x) + 1) for x in THTAB])
RUN ="C-20261119-144535-2c7b6a4"
SCR = "/data/haiyangw/nrpic/scratch/C-sidm"


def linear_form(t, chi, k1, Ms0, Mh, jmax=401):
    j = np.arange(1, jmax + 1, 2)
    s = (8/np.pi**2)*np.sum(np.exp(-chi*np.outer(t, (j*k1)**2))/j**2, axis=1)
    return Mh + (Ms0 - Mh)*s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = a.out or lib.run_dir(SCR + "/tmp/verify_g1/v1_step")
    os.makedirs(out, exist_ok=True)
    cases = sorted(glob.glob(f"{SCR}/{RUN}/step_b_*"))
    rows = []
    store = {}
    refs = {}
    for cdir in cases:
        cs = json.load(open(os.path.join(cdir, "case.json")))
        d = np.load(os.path.join(cdir, "reduced.npz"))
        L = cs["box"][0]
        A = cs["box"][1]*cs["box"][2]
        sig = cs["sigma"]
        lam = 1.0/sig
        th1, th2 = cs["theta1"], cs["theta2"]
        x0 = 10.0
        # own sums of the first and the last snapshot
        chk = []
        snaps = sorted(glob.glob(cdir + "/heat.part.*.bin"))
        init = None
        for idx, fn in [(0, snaps[0]), (-1, snaps[-1])]:
            sn = lib.read_snap(fn)
            xr = np.mod(sn["x"][:, 0] - x0, L)       # snapshot positions are not wrapped
            inslab = xr < L/2
            Ms = sn["m"][inslab].sum()
            chk.append(abs(Ms - d["slab_M"][idx])/d["slab_M"][idx])
            if idx == 0:
                u = sn["u"]
                W = np.sqrt(1 + np.einsum("ij,ij->i", u, u))
                th_l = lib_theta(W[inslab].mean())
                th_r = lib_theta(W[~inslab].mean())
                init = dict(M_slab0=Ms, M_tot=sn["m"].sum(), theta_left=th_l,
                            theta_right=th_r, n_left=int(inslab.sum()),
                            n_right=int((~inslab).sum()))
        Mtot = init["M_tot"]
        rho1 = init["M_slab0"]/(A*L/2)
        rho2 = (Mtot - init["M_slab0"])/(A*L/2)
        # final state: energy conservation sum M <W> (exact MJ inversion)
        wbar = (init["M_slab0"]*lib.mean_w(th1) + (Mtot - init["M_slab0"])*lib.mean_w(th2))/Mtot
        thf = lib_theta(wbar)
        cpf = lib.c_v(thf) + 1
        nf = Mtot/(A*L)
        chi1 = K1C*np.sqrt(thf)*lam*nf/(nf*cpf)/nf   # kappa_1/(n c_p), kappa_1 ~ sqrt(T)/sigma
        k1 = 2*np.pi/L
        t = d["time"]
        Ms = d["slab_M"]/A                           # mass per unit area
        Mh = 0.5*Mtot/A
        tcoll_hot = 1.0/(rho1*sig*lib.vmol_mean(th1))
        tcoll_cold = 1.0/(rho2*sig*lib.vmol_mean(th2))
        t0, t1 = 20*max(tcoll_hot, tcoll_cold), 2.0/(chi1*k1**2)
        w = (t >= t0) & (t <= t1)
        # (1) linear form, chi free
        r1 = least_squares(lambda p: linear_form(t[w], p[0]*chi1, k1, Ms[0], Mh) - Ms[w],
                           [1.0])
        # (2) nonlinear isobaric reference, constant c_p at three temperatures
        fits = {}
        for lab, cpv in [("cp_f", cpf), ("cp_hot", lib.c_v(th1) + 1),
                         ("cp_cold", lib.c_v(th2) + 1)]:
            key = (lab, rho1, rho2)
            if key not in refs:
                T, dm, P, Mt, M1 = heat_ref.step_initial(th1, th2, rho1, rho2, L, 4000)
                tr = np.linspace(0, 1.5*t[-1], 1501)
                Tt = heat_ref.evolve(T, dm, P, lam, cpv, tr, rtol=1e-7, atol=1e-12)
                refs[key] = (tr, heat_ref.slab_mass(Tt, dm, P, M1, L), Tt, dm, P, M1)
            tr, msr = refs[key][:2]
            r2 = least_squares(lambda p: np.interp(p[0]*t[w], tr, msr) - Ms[w], [1.0])
            J = r2.jac
            s2 = np.sum(r2.fun**2)/max(1, w.sum() - 1)
            fits[lab] = dict(f=float(r2.x[0]), f_err=float(np.sqrt(s2/(J.T @ J)[0, 0])),
                             rms=float(np.sqrt(np.mean(r2.fun**2))/abs(Ms[0] - Mh)))
        # (3) sound removed: entropy part of the slab mass, from the 200-bin profiles.
        # Local MJ temperature from e_K/n per bin, p = n theta; an adiabatic sound wave has
        # dn = (c_v/c_p) (n/p) dp, so M_ent = M_s - sum_slab (c_v/c_p) n (p - <p>)/p dV.
        nb = d["prof_M"].shape[1]
        Vb = A*L/nb
        nbin = d["prof_M"]/Vb
        wb = 1 + d["prof_MK"]/np.maximum(d["prof_M"], 1e-300)
        thb = np.interp(wb, WTAB, THTAB)
        pb = nbin*thb
        pbar = pb.mean(axis=1, keepdims=True)
        gam = np.interp(thb, THTAB, CVCP)
        xb = (np.arange(nb) + 0.5)/nb*L
        slab = xb < L/2
        corr = np.sum((gam*nbin*(pb - pbar)/pb*Vb)[:, slab], axis=1)/A
        Me = Ms - corr
        tr, msr = refs[("cp_f", rho1, rho2)][:2]
        r3 = least_squares(lambda p: np.interp(p[0]*t[w], tr, msr) - Me[w], [1.0])
        J = r3.jac
        s2 = np.sum(r3.fun**2)/max(1, w.sum() - 1)
        fits["cp_f_sound_removed"] = dict(
            f=float(r3.x[0]), f_err=float(np.sqrt(s2/(J.T @ J)[0, 0])),
            rms=float(np.sqrt(np.mean(r3.fun**2))/abs(Ms[0] - Mh)),
            pbar_rel_drift=float(np.ptp(pbar)/pbar.mean()))
        row = dict(case=os.path.basename(cdir), seed=cs["seed"], lam_over_L=cs["lam_over_L"],
                   init=init, rho1=rho1, rho2=rho2, theta_f=thf, c_p_f=cpf, chi1=chi1,
                   window=[t0, t1], n_fit=int(w.sum()), slab_check_max_rel=max(chk),
                   chi_ratio_linear=float(r1.x[0]),
                   rms_linear=float(np.sqrt(np.mean(r1.fun**2))/abs(Ms[0] - Mh)),
                   nonlinear=fits)
        rows.append(row)
        store[row["case"]] = dict(t=t, Ms=Ms, Mh=Mh, w=w, r1=r1.x[0], chi1=chi1, k1=k1,
                                  ref=refs[("cp_f", rho1, rho2)], f=fits["cp_f"]["f"],
                                  prof=d["prof_M"], L=L, A=A, Me=Me,
                                  fe=fits["cp_f_sound_removed"]["f"])
        print(json.dumps(row, default=float))
    fl = np.array([r["nonlinear"]["cp_f"]["f"] for r in rows])
    cl = np.array([r["chi_ratio_linear"] for r in rows])
    summ = dict(f_mean=fl.mean(), f_half_diff=abs(fl[0] - fl[-1])/2,
                linear_mean=cl.mean(), linear_half_diff=abs(cl[0] - cl[-1])/2,
                f_cp_hot=np.mean([r["nonlinear"]["cp_hot"]["f"] for r in rows]),
                f_cp_cold=np.mean([r["nonlinear"]["cp_cold"]["f"] for r in rows]),
                f_sound_removed=np.mean([r["nonlinear"]["cp_f_sound_removed"]["f"]
                                         for r in rows]),
                f_sound_removed_half_diff=abs(rows[0]["nonlinear"]["cp_f_sound_removed"]["f"]
                                              - rows[-1]["nonlinear"]["cp_f_sound_removed"]["f"])/2)
    print(json.dumps(summ, default=float))
    lib.save_json(os.path.join(out, "v1_step.json"), dict(rows=rows, summary=summ))
    figures(out, rows, store)


def lib_theta(wbar):
    """theta from <W> of a Maxwell-Juttner gas (bisection on lib.mean_w)."""
    lo, hi = 1e-6, 10.0
    for _ in range(200):
        mid = np.sqrt(lo*hi)
        if lib.mean_w(mid) < wbar:
            lo = mid
        else:
            hi = mid
    return np.sqrt(lo*hi)


def figures(out, rows, store):
    from nrpic import figstyle
    import matplotlib.pyplot as plt
    figstyle.use_style()
    P = figstyle.PAL
    fig, ax = plt.subplots(2, 2, figsize=(8, 5.4))
    fig.subplots_adjust(left=0.1, right=0.98, bottom=0.09, top=0.95, wspace=0.28,
                        hspace=0.32)
    cols = [P["red"], P["green"]]
    for i, r in enumerate(rows):
        s = store[r["case"]]
        t = s["t"]
        y = (s["Ms"] - s["Mh"])/(s["Ms"][0] - s["Mh"])
        ax[0, 0].plot(t, y, ".", ms=2, color=cols[i], label="seed %d" % r["seed"])
        tr, msr = s["ref"][:2]
        yr = (np.interp(s["f"]*t, tr, msr) - s["Mh"])/(s["Ms"][0] - s["Mh"])
        yl = (linear_form(t, s["r1"]*s["chi1"], s["k1"], s["Ms"][0], s["Mh"]) -
              s["Mh"])/(s["Ms"][0] - s["Mh"])
        if i == 0:
            ax[0, 0].plot(t, yr, "k-", lw=1, label="nonlinear isobaric ref., fitted f")
            ax[0, 0].plot(t, yl, "k--", lw=1, label=r"linear form, fitted $\chi$")
            ax[0, 0].axvspan(r["window"][0], r["window"][1], color="grey", alpha=0.1)
        ax[0, 1].plot(t, y - yr, ".", ms=2, color=cols[i], label="seed %d: data - nonlinear" % r["seed"])
        ye = (s["Me"] - s["Mh"])/(s["Ms"][0] - s["Mh"])
        yre = (np.interp(s["fe"]*t, tr, msr) - s["Mh"])/(s["Ms"][0] - s["Mh"])
        ax[0, 1].plot(t, ye - yre - 0.06, "-", lw=0.8, color=cols[i],
                      label="seed %d: sound removed - nonlinear (offset -0.06)" % r["seed"])
        ax[0, 1].plot(t, y - yl, "-", lw=0.8, color=cols[i], alpha=0.6,
                      label="seed %d: data - linear" % r["seed"])
    ax[0, 0].set_yscale("log")
    ax[0, 0].set_xlabel("t")
    ax[0, 0].set_ylabel(r"$(M_s - M/2)/(M_s(0) - M/2)$")
    ax[0, 0].legend(fontsize=7, loc="lower left")
    ax[0, 1].axhline(0, color="k", lw=0.8)
    ax[0, 1].set_xlabel("t")
    ax[0, 1].set_ylabel("residual (normalised)")
    ax[0, 1].legend(fontsize=6, loc="upper right", ncol=1)
    # profiles of seed 1 against the reference at three times
    s = store[rows[0]["case"]]
    tr, msr, Tt, dm, Pp, M1 = s["ref"]
    nb = s["prof"].shape[1]
    xb = (np.arange(nb) + 0.5)/nb*s["L"]
    for j, ti in enumerate([1.0, 5.0, 20.0]):
        it = np.argmin(abs(s["t"] - ti))
        dens = s["prof"][it]/(s["A"]*s["L"]/nb)
        ax[1, 0].plot(xb, dens, ".", ms=2, color=[P["red"], P["blue"], P["green"]][j],
                      label="t = %.1f" % s["t"][it])
        k = np.argmin(abs(tr - s["f"]*s["t"][it]))
        T = Tt[k]
        v = np.cumsum(T)*dm/Pp - 0.5*T*dm/Pp
        xc = np.interp(M1/2, (np.arange(len(T)) + 0.5)*dm, v)
        xx = np.mod(v - xc + s["L"]/4, s["L"])
        o = np.argsort(xx)
        ax[1, 0].plot(xx[o], (Pp/T)[o], "k-", lw=0.8)
    ax[1, 0].set_xlabel("x - x0")
    ax[1, 0].set_ylabel(r"rest-mass density")
    ax[1, 0].legend(fontsize=7)
    ax[1, 1].bar([0, 1], [r["nonlinear"]["cp_f"]["f"] for r in rows], width=0.35,
                 color=P["blue"], label="nonlinear ref. f")
    ax[1, 1].bar([0.4, 1.4], [r["chi_ratio_linear"] for r in rows], width=0.35,
                 color=P["red"], label=r"linear $\chi/\chi_1$")
    ax[1, 1].axhspan(0.95, 1.10, color="grey", alpha=0.15, label="T6(b) interval")
    ax[1, 1].set_ylim(0.85, 1.15)
    ax[1, 1].set_xticks([0.2, 1.2])
    ax[1, 1].set_xticklabels(["seed %d" % r["seed"] for r in rows])
    ax[1, 1].legend(fontsize=7, loc="lower right")
    fig.savefig(os.path.join(out, "v1c_step.png"))
    plt.close(fig)


if __name__ == "__main__":
    main()
