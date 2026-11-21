"""V5: reproducibility (T10), long conservation (T1, 1e4 steps), relaxation to Maxwell-Juttner
(T3), two-temperature initial rate (T4) and unequal masses (T9), own analysis (JOURNAL entry 14).
"""
import argparse
import glob
import json
import math
import os
import sys

import numpy as np
from scipy import special, stats

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "python"))
import lib  # noqa: E402
from lib import COLL  # noqa: E402
from v2_box import Fr, _dens, theta_from_w  # noqa: E402

SCR = "/data/haiyangw/nrpic/scratch/C-sidm"
R_T10 = "C-20261119-143041-f94e350"
R_T1L = "C-20261115-170741-248af65"
R_T345 = "C-20261115-170539-28432c3"
R_T9 = "C-20261115-170814-8a54b43"


def snaps(d):
    return sorted(glob.glob(d + "/box.part.*.bin"))


def by_tag(s):
    o = np.argsort(s["tag"], kind="stable")
    return {k: s[k][o] for k in ["x", "u", "m", "tag"]}


def wof(u):
    return np.sqrt(1 + np.einsum("ij,ij->i", u, u))


# ---------------------------------------------------------------- exact initial rate (T4)
def X_quad(th1, th2, n=300, m=120, smax=11.0):
    """X = <v_Mol (W_b - W_a)/2>, a ~ MJ(th1), b ~ MJ(th2); angular average of v_Mol in closed
    form (as in V2), Gauss-Legendre in s = sqrt((W - 1)/theta) split at the kink."""
    x, w = special.roots_legendre(n)
    s1 = 0.5*smax*(x + 1)
    w1 = 0.5*smax*w
    xm, wm = special.roots_legendre(m)
    p1, u1, W1 = _dens(s1, th1)
    e1 = np.arcsinh(u1)
    Z1 = np.sum(w1*p1)
    # normalisation of the second density
    s2f = 0.5*smax*(x + 1)
    Z2 = np.sum(w1*_dens(s2f, th2)[0])
    tot = 0.0
    for k in range(n):
        # kink where eta_2 = eta_1, i.e. s_2 with u_2 = u_1
        Wk = W1[k]
        s_k = math.sqrt(max(Wk - 1, 0.0)/th2)
        cuts = [0.0] + ([s_k] if 0 < s_k < smax else []) + [smax]
        for a, b in zip(cuts[:-1], cuts[1:]):
            s2 = a + 0.5*(b - a)*(xm + 1)
            w2 = 0.5*(b - a)*wm
            p2, u2, W2 = _dens(s2, th2)
            e2 = np.arcsinh(u2)
            V = (Fr(e1[k] + e2) - Fr(np.abs(e1[k] - e2)))/(2*u1[k]*u2*W1[k]*W2)
            tot += w1[k]*p1[k]*np.sum(w2*p2*V*(W2 - W1[k])/2)
    return float(tot/(Z1*Z2))


def X_mc(th1, th2, npair, rng):
    ua = lib.MJSampler(th1).sample(npair, rng)
    ub = lib.MJSampler(th2).sample(npair, rng)
    wa, wb = wof(ua), wof(ub)
    g = wa*wb - np.einsum("ij,ij->i", ua, ub)
    v = np.sqrt(np.maximum(g*g - 1, 0))/(wa*wb)
    q = v*(wb - wa)/2
    vr = np.linalg.norm(ua/wa[:, None] - ub/wb[:, None], axis=1)
    return float(q.mean()), float(q.std(ddof=1)/np.sqrt(npair)), float((vr*(wb - wa)/2).mean())


def rate_exact(th1, th2, sigma, n1, n2, X):
    return sigma*X*(n2/lib.c_v(th1) + n1/lib.c_v(th2))


# ---------------------------------------------------------------- T10
def t10():
    base = f"{SCR}/{R_T10}"
    ref = by_tag(lib.read_snap(f"{base}/mb8/box.part.00001.bin"))
    out = dict(ref="mb8", cases={})
    for c in ["mb1", "mb64", "rst0", "rst1", "rst2", "seed8"]:
        p = f"{base}/{c}/box.part.00001.bin"
        if not os.path.exists(p):
            out["cases"][c] = "no snapshot"
            continue
        s = lib.read_snap(p)
        t = by_tag(s)
        same = {k: bool(np.array_equal(t[k], ref[k])) for k in ["x", "u", "m", "tag"]}
        bytes_same = open(p, "rb").read() == open(f"{base}/mb8/box.part.00001.bin", "rb").read()
        out["cases"][c] = dict(time=s["time"], cycle=s["cycle"], identical=same, file_bytes_identical=bytes_same,
                               frac_u_identical=float(np.mean(np.all(t["u"] == ref["u"], axis=1))),
                               max_du=float(np.max(np.abs(t["u"] - ref["u"]))))
    h8 = lib.read_hist(f"{base}/mb8/box.coll.hst")
    for c in ["mb1", "mb64", "rst0", "rst1", "rst2", "seed8"]:
        hp = f"{base}/{c}/box.coll.hst"
        if not os.path.exists(hp):
            continue
        h = lib.read_hist(hp)
        cyc = h[:, 1].astype(int)
        m8 = {int(r[1]): r for r in h8}
        eq = [bool(np.array_equal(r, m8[int(r[1])])) for r in h if int(r[1]) in m8]
        out["cases"][c]["hist_records"] = len(eq)
        out["cases"][c]["hist_records_identical"] = int(sum(eq))
        out["cases"][c]["hist_cycles"] = [int(cyc.min()), int(cyc.max())]
    # A/B overlap in T345: B's snapshot at 0.25 tau_rel against A's last
    ab = {}
    for case in sorted(glob.glob(f"{SCR}/{R_T345}/T345_*_A")):
        sa = lib.read_snap(snaps(case)[-1])
        bdir = case[:-2] + "_B"
        sb = None
        for p in snaps(bdir)[:4]:
            s = lib.read_snap(p)
            if s["cycle"] == sa["cycle"]:
                sb = s
                break
        if sb is None:
            ab[os.path.basename(case)] = "no matching cycle"
            continue
        ta, tb = by_tag(sa), by_tag(sb)
        ab[os.path.basename(case)] = dict(cycle=int(sa["cycle"]), time_a=sa["time"], time_b=sb["time"],
                                          identical=all(np.array_equal(ta[k], tb[k]) for k in ["x", "u", "m", "tag"]))
    out["T345_A_vs_B"] = ab
    print("T10", json.dumps(out, default=float))
    return out


# ---------------------------------------------------------------- T1 long
def t1long():
    res = {}
    for d in sorted(glob.glob(f"{SCR}/{R_T1L}/T1long_s*")):
        ss = snaps(d)
        E, P, t = [], [], []
        for p in ss:
            s = lib.read_snap(p)
            W = wof(s["u"])
            E.append(math.fsum(s["m"]*W))
            P.append([math.fsum(s["m"]*s["u"][:, i]) for i in range(3)])
            t.append(s["cycle"])
        E = np.array(E)
        h = lib.read_hist(f"{d}/box.coll.hst")
        smw = h[:, COLL["sum_MW"]]
        nc = h[:, COLL["n_coll"]]
        bound = 1e-14*np.sqrt(nc + 1)
        res[os.path.basename(d)] = dict(
            snap_cycles=t, drift_rel=((E - E[0])/E[0]).tolist(),
            max_abs_drift_rel=float(np.max(np.abs(E - E[0]))/E[0]),
            P_drift_rel=float(np.max(np.abs(np.array(P) - np.array(P[0])))/E[0]),
            hist_records=int(h.shape[0]), hist_first_last_cycle=[int(h[0, 1]), int(h[-1, 1])],
            hist_sumMW_drift_rel=float((smw[-1] - smw[0])/smw[0]),
            max_dE_over_bound=float(np.max(np.abs(h[:, COLL["dE"]])/smw/bound)),
            max_dP_over_bound=float(np.max(np.max(np.abs(h[:, COLL["dP1"]:COLL["dP3"] + 1]), axis=1)/smw/bound)),
            n_trunc=int(h[:, COLL["n_trunc"]].sum()), n_coll_total=float(nc.sum()))
        print("T1long", os.path.basename(d), json.dumps({k: v for k, v in res[os.path.basename(d)].items() if k != "drift_rel"}, default=float))
    return res


# ---------------------------------------------------------------- T3, T4
def pop_theta(s, npop1):
    W = wof(s["u"])
    m1 = s["tag"] < npop1
    out = []
    for msk in [m1, ~m1]:
        wm = W[msk].mean()
        th = theta_from_w(wm)
        se = W[msk].std(ddof=1)/np.sqrt(msk.sum())/lib.c_v(th)
        out.append((th, se))
    return out


def t34(rng):
    res = {}
    for ic in sorted(glob.glob(f"{SCR}/{R_T345}/T345_*_ic")):
        name = os.path.basename(ic)[:-3]
        box = json.load(open(ic + "/box.json"))
        n1 = box["n_pop1"]
        th1n, th2n, sig = box["theta1"], box["theta2"], box["sigma"]
        A = snaps(ic[:-3] + "_A")
        B = snaps(ic[:-3] + "_B")
        # T4: first 16 snapshots of A
        ts, d, se_d, th1s, th2s = [], [], [], [], []
        for p in A[:16]:
            s = lib.read_snap(p)
            (a, sa), (b, sb) = pop_theta(s, n1)
            ts.append(s["time"])
            d.append(a - b)
            se_d.append(math.hypot(sa, sb))
            th1s.append(a)
            th2s.append(b)
        ts, d = np.array(ts), np.array(d)
        X = X_quad(th1s[0], th2s[0])
        Xm, Xse, Xvr = X_mc(th1s[0], th2s[0], 4_000_000, rng)
        exact = rate_exact(th1s[0], th2s[0], sig, 0.5, 0.5, X)
        c, cov = np.polyfit(ts, d, 2, cov=True)
        slope, se = float(c[1]), float(np.sqrt(cov[1, 1]))
        c1 = np.polyfit(ts[ts <= ts[10] + 1e-12], d[ts <= ts[10] + 1e-12], 1)
        tau_own = (th1s[0] - th2s[0])/abs(exact)
        r4 = dict(theta1_0=th1s[0], theta2_0=th2s[0], X_quad=X, X_mc=Xm, X_mc_se=Xse, X_quad_vs_mc_z=(X - Xm)/Xse,
                  vrel_over_vmol_rate=Xvr/Xm, exact_rate=exact, fit_slope=slope, fit_se=se,
                  rel=slope/exact - 1, pass_4se=bool(abs(slope - exact) <= 4*se + 0.01*abs(exact)),
                  pass_5pc=bool(abs(slope - exact) <= 0.05*abs(exact)), line_slope_0to0p1=float(c1[0]),
                  tau_rel_own=tau_own, snap_spacing=float(ts[1] - ts[0]), spacing_over_tau=float((ts[1] - ts[0])/tau_own),
                  t=ts.tolist(), d=d.tolist(), se_d=se_d)
        # T3: last snapshot of B
        s0 = lib.read_snap(A[0])
        sE = lib.read_snap(B[-1])
        W0 = wof(s0["u"])
        th_eq = theta_from_w(math.fsum(s0["m"]*W0)/math.fsum(s0["m"]))
        WE = wof(sE["u"])
        um = np.sqrt(np.einsum("ij,ij->i", sE["u"], sE["u"]))
        smp = lib.MJSampler(th_eq)
        ks = stats.kstest(um, lambda x: np.interp(x, smp.u, smp.cdf))
        q = np.einsum("ij,ij->i", sE["u"], sE["u"])/WE
        (a, sa), (b, sb) = pop_theta(sE, n1)
        r3 = dict(t_end=sE["time"], tau_end=sE["time"]/tau_own, theta_eq=th_eq, KS_p=float(ks.pvalue), KS_D=float(ks.statistic),
                  u2W_z=float((q.mean() - 3*th_eq)/(q.std(ddof=1)/np.sqrt(len(q)))),
                  pop1_z=float((a - th_eq)/sa), pop2_z=float((b - th_eq)/sb), pop_diff_z=float((a - b)/math.hypot(sa, sb)),
                  energy_rel_change=float((math.fsum(sE["m"]*WE) - math.fsum(s0["m"]*W0))/math.fsum(s0["m"]*W0)))
        res[name] = dict(T4=r4, T3=r3)
        print("T34", name, json.dumps({k: v for k, v in r4.items() if k not in ("t", "d", "se_d")}, default=float), json.dumps(r3, default=float))
    return res


# ---------------------------------------------------------------- T9
def t9():
    res = {}
    dE, dP = [], []
    for d in sorted(glob.glob(f"{SCR}/{R_T9}/T9_s*")):
        ss = snaps(d)
        s0, s1 = lib.read_snap(ss[0]), lib.read_snap(ss[-1])
        W0, W1 = wof(s0["u"]), wof(s1["u"])
        E0 = math.fsum(s0["m"]*W0)
        th_eq = theta_from_w(E0/math.fsum(s0["m"]))
        mmin = s1["m"].min()
        out = dict(t_end=s1["time"], theta_eq=th_eq)
        smp = lib.MJSampler(th_eq)
        ths = []
        for lab, msk in [("light", s1["m"] < 1.5*mmin), ("heavy", s1["m"] >= 1.5*mmin)]:
            w = W1[msk]
            th = theta_from_w(w.mean())
            se = w.std(ddof=1)/np.sqrt(msk.sum())/lib.c_v(th)
            um = np.sqrt(np.einsum("ij,ij->i", s1["u"][msk], s1["u"][msk]))
            out[lab] = dict(n=int(msk.sum()), theta=th, se=se, z_vs_eq=(th - th_eq)/se,
                            KS_p=float(stats.kstest(um, lambda x: np.interp(x, smp.u, smp.cdf)).pvalue))
            ths.append((th, se))
        out["class_diff_z"] = (ths[0][0] - ths[1][0])/math.hypot(ths[0][1], ths[1][1])
        e_rel = (math.fsum(s1["m"]*W1) - E0)/E0
        p_rel = [(math.fsum(s1["m"]*s1["u"][:, i]) - math.fsum(s0["m"]*s0["u"][:, i]))/E0 for i in range(3)]
        out.update(dE_rel=e_rel, dP_rel=p_rel)
        dE.append(e_rel)
        dP.append(p_rel)
        res[os.path.basename(d)] = out
        print("T9", os.path.basename(d), json.dumps(out, default=float))
    dE, dP = np.array(dE), np.array(dP)
    res["drift_mean_z"] = dict(E=float(dE.mean()/(dE.std(ddof=1)/np.sqrt(len(dE)))),
                               P=[float(dP[:, i].mean()/(dP[:, i].std(ddof=1)/np.sqrt(len(dE)))) for i in range(3)],
                               E_mean=float(dE.mean()), E_std=float(dE.std(ddof=1)))
    log = open(f"{SCR}/{R_T9}/T9_equal_refused/athena.log").read()
    res["equal_refused"] = dict(fatal="FATAL ERROR" in log, names_unequal="unequal rest masses" in log)
    print("T9 summary", json.dumps({k: res[k] for k in ["drift_mean_z", "equal_refused"]}, default=float))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = a.out or lib.run_dir(SCR + "/tmp/verify_g1/v5")
    os.makedirs(out, exist_ok=True)
    rng = np.random.default_rng(11)
    # quadrature check: NR limit and MC
    chk = []
    for th1, th2 in [(3e-3, 1e-3), (3.0, 1.0), (0.3, 0.1)]:
        Xq = X_quad(th1, th2)
        Xm, se, _ = X_mc(th1, th2, 4_000_000, rng)
        chk.append(dict(th1=th1, th2=th2, X_quad=Xq, X_mc=Xm, z=(Xq - Xm)/se))
        print("Xcheck", chk[-1])
    res = dict(Xcheck=chk)
    res["T10"] = t10()
    res["T1long"] = t1long()
    res["T34"] = t34(rng)
    res["T9"] = t9()
    lib.save_json(os.path.join(out, "v5_box.json"), res)
    figures(out, res)


def figures(out, res):
    from nrpic import figstyle
    import matplotlib.pyplot as plt
    figstyle.use_style()
    P = figstyle.PAL
    fig, ax = plt.subplots(2, 2, figsize=(8, 6.2))
    fig.subplots_adjust(left=0.11, right=0.97, bottom=0.09, top=0.95, wspace=0.33, hspace=0.38)
    for (name, r), col in zip(res["T34"].items(), figstyle.SERIES):
        r4 = r["T4"]
        t = np.array(r4["t"])/r4["tau_rel_own"]
        d0 = r4["d"][0]
        ax[0, 0].errorbar(t, np.array(r4["d"])/d0, yerr=np.array(r4["se_d"])/d0, fmt="o", ms=2, color=col,
                          label=name.replace("T345_", ""))
        ax[0, 0].plot(t, 1 + r4["exact_rate"]*np.array(r4["t"])/d0, color=col, lw=1)
    ax[0, 0].set_xlabel(r"$t/\tau_{rel}$ (own $\tau_{rel}$)")
    ax[0, 0].set_ylabel(r"$(\theta_1 - \theta_2)/(\theta_1 - \theta_2)_0$")
    ax[0, 0].set_title("T4: lines = own exact initial rate", fontsize=8)
    ax[0, 0].legend(fontsize=6)
    names = list(res["T34"].keys())
    x = np.arange(len(names))
    ax[0, 1].errorbar(x, [100*res["T34"][n]["T4"]["rel"] for n in names],
                      yerr=[100*res["T34"][n]["T4"]["fit_se"]/abs(res["T34"][n]["T4"]["exact_rate"]) for n in names],
                      fmt="o", color=P["blue"], label="T4 slope / exact - 1")
    ax[0, 1].axhspan(-5, 5, color="grey", alpha=0.15)
    ax[0, 1].axhline(0, color="k", lw=0.8)
    ax[0, 1].set_xticks(x)
    ax[0, 1].set_xticklabels([n.replace("T345_", "") for n in names], fontsize=6, rotation=30)
    ax[0, 1].set_ylabel("percent")
    ax[0, 1].legend(fontsize=6)
    zs = []
    labs = []
    for n in names:
        r3 = res["T34"][n]["T3"]
        zs.append([r3["u2W_z"], r3["pop1_z"], r3["pop2_z"]])
        labs.append(n.replace("T345_", ""))
    zs = np.array(zs)
    for j, (lab, mk) in enumerate([(r"$\langle u^2/W\rangle$ - 3$\theta_{eq}$", "o"), ("pop 1", "s"), ("pop 2", "^")]):
        ax[1, 0].plot(x + 0.1*(j - 1), zs[:, j], mk, ms=4, label=lab)
    for n_, xx in zip(names, x):
        ax[1, 0].annotate("KS p=%.2f" % res["T34"][n_]["T3"]["KS_p"], (xx, -3.6), fontsize=6, ha="center")
    ax[1, 0].axhspan(-4, 4, color="grey", alpha=0.15)
    ax[1, 0].set_xticks(x)
    ax[1, 0].set_xticklabels(labs, fontsize=6, rotation=30)
    ax[1, 0].set_ylabel("z at the end (T3)")
    ax[1, 0].legend(fontsize=6)
    for (k, r), col in zip(res["T1long"].items(), [P["red"], P["blue"]]):
        ax[1, 1].plot(r["snap_cycles"], np.abs(r["drift_rel"]) + 1e-18, "o-", ms=3, color=col, label=k)
    ax[1, 1].axhline(1e-11, **figstyle.GUIDE)
    ax[1, 1].set_yscale("log")
    ax[1, 1].set_xlabel("cycle")
    ax[1, 1].set_ylabel(r"|$\Sigma MW(t)/\Sigma MW(0) - 1$| (+1e-18)")
    ax[1, 1].set_title("T1 long: criterion 1e-11 (dashed)", fontsize=8)
    ax[1, 1].legend(fontsize=6)
    fig.savefig(os.path.join(out, "v5_box.png"))
    plt.close(fig)


if __name__ == "__main__":
    main()
