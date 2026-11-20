"""V2: collision rate (T2) and conservation per step (T1) in the flat box, own analysis.

Runs C-20261115-165500-c67e036 (release core-v0.3 CPU executable) and
C-20261119-141806-af19c1c (core/collisions-2 CPU executable, coll_energy = particle).
Own Moller-rate reference (JOURNAL entry 6):
  <v_Mol>(theta) = E_{MJ x MJ}[ (F(eta1 + eta2) - F(|eta1 - eta2|)) / (2 u1 u2 W1 W2) ],
  F(eta) = (sinh eta cosh eta - eta)/2,  eta = asinh u,
by tensor Gauss-Laguerre quadrature (weight y^(1/2) e^-y, y = (W - 1)/theta).
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
sys.path.insert(0, "/data/haiyangw/nrpic/wt/C-sidm/python")
import lib  # noqa: E402
from lib import COLL  # noqa: E402

SCR = "/data/haiyangw/nrpic/scratch/C-sidm"
RUNS = {"release": "C-20261115-165500-c67e036", "c2particle": "C-20261119-141806-af19c1c"}


def Fr(eta):
    eta = np.asarray(eta, dtype=float)
    out = 0.5*(np.sinh(eta)*np.cosh(eta) - eta)
    small = eta < 1e-2
    e = eta[small]
    out[small] = (e**3/3 + e**5/15 + 2*e**7/315)        # series of (sinh 2e/2 - e)/2
    return out


def vmol_quad(theta, n=1000):
    y, w = special.roots_genlaguerre(n, 0.5)
    W = 1 + theta*y
    u = np.sqrt(theta*y*(2 + theta*y))
    q = np.sqrt(theta*(2 + theta*y))*W                    # u W / sqrt(y)
    eta = np.arcsinh(u)
    E1, E2 = np.meshgrid(eta, eta, indexing="ij")
    U1, U2 = np.meshgrid(u, u, indexing="ij")
    W1, W2 = np.meshgrid(W, W, indexing="ij")
    V = (Fr(E1 + E2) - Fr(np.abs(E1 - E2)))/(2*U1*U2*W1*W2)
    wq = w*q
    return float(wq @ V @ wq/(wq.sum())**2)


def theta_from_w(wbar):
    lo, hi = 1e-6, 100.0
    for _ in range(200):
        mid = np.sqrt(lo*hi)
        if lib.mean_w(mid) < wbar:
            lo = mid
        else:
            hi = mid
    return float(np.sqrt(lo*hi))


def mj_cdf_u(theta):
    s = lib.MJSampler(theta)
    return lambda x: np.interp(x, s.u, s.cdf)


def parse_args_log(path):
    first = open(path).readline().split()
    kv = {}
    for a in first:
        if "=" in a:
            k, v = a.split("=", 1)
            kv[k] = v
    return kv


def batch_se(x, nb=10):
    b = np.array_split(x, nb)
    m = np.array([bb.mean() for bb in b])
    return m.std(ddof=1)/np.sqrt(nb)


def analyse_case(cdir, rng):
    box = json.load(open(os.path.join(cdir, "box.json")))
    kv = parse_args_log(os.path.join(cdir, "athena.log"))
    dt = float(kv["particles/dt"])
    sig = float(kv["particles/coll_sigma"])
    snaps = sorted(glob.glob(cdir + "/box.part.*.bin"))
    s0 = lib.read_snap(snaps[0])
    s1 = lib.read_snap(snaps[-1])
    V = box["box"][0]*box["box"][1]*box["box"][2]
    N = s0["n"]
    W0 = np.sqrt(1 + np.einsum("ij,ij->i", s0["u"], s0["u"]))
    W1 = np.sqrt(1 + np.einsum("ij,ij->i", s1["u"], s1["u"]))
    M0 = s0["m"]
    rho0 = math.fsum(M0)/V
    th_s = theta_from_w(math.fsum(M0*W0)/math.fsum(M0))
    out = dict(case=os.path.basename(cdir), theta_nominal=box["theta"], theta_sample=th_s,
               N=N, dt=dt, sigma=sig, rho0=rho0, steps=int(s1["cycle"]))
    # snapshot conservation (exactly rounded sums), tags aligned
    o0 = np.argsort(s0["tag"])
    o1 = np.argsort(s1["tag"])
    E0 = math.fsum(M0*W0)
    E1 = math.fsum(s1["m"]*W1)
    out["snap_dE_rel"] = (E1 - E0)/E0
    out["snap_dP_rel"] = [(math.fsum(s1["m"]*s1["u"][:, i]) - math.fsum(M0*s0["u"][:, i]))/E0
                          for i in range(3)]
    out["u_identical_fraction"] = float(np.mean(np.all(s0["u"][o0] == s1["u"][o1], axis=1)))
    out["mass_identical"] = bool(np.array_equal(s0["m"][o0], s1["m"][o1]))
    hpath = os.path.join(cdir, "box.coll.hst")
    if not os.path.exists(hpath) or os.path.getsize(hpath) == 0:
        out["collisions"] = False
        return out, None
    h = lib.read_hist(hpath)
    out["collisions"] = True
    out["ncol_hist"] = h.shape[1]
    nsteps = h.shape[0]
    sumP = h[:, COLL["sum_P"]]
    ncoll = h[:, COLL["n_coll"]]
    sumW = h[:, COLL["sum_W"]]
    vm = vmol_quad(th_s)
    vm_closed = lib.vmol_mean(th_s)
    expct = 0.5*N*rho0*sig*vm*dt
    # T2(a)
    out["T2a_z"] = float((ncoll.sum() - sumP.sum())/np.sqrt(sumP.sum()))
    # T2(b)
    m = sumP.mean()
    se_naive = sumP.std(ddof=1)/np.sqrt(nsteps)
    se_batch = batch_se(sumP)
    out.update(vmol_quad=vm, vmol_closed=vm_closed, vmol_rel_diff=vm/vm_closed - 1,
               expected_per_step=expct, sumP_mean=m, T2b_rel=m/expct - 1,
               T2b_z_naive=(m - expct)/se_naive, T2b_z_batch=(m - expct)/se_batch,
               T2b_se_rel=se_batch/expct)
    # decomposition
    wexp = 0.5*N*rho0*sig*dt
    out["sumW_rel"] = sumW.mean()/wexp - 1
    out["sumW_z"] = (sumW.mean() - wexp)/batch_se(sumW)
    vt = sumP/sumW
    out["vtested_rel"] = vt.mean()/vm - 1
    out["vtested_z"] = (vt.mean() - vm)/batch_se(vt)
    # sample's own all-pairs Moller mean (random pairs of the initial snapshot)
    npair = 20_000_000
    acc = []
    for _ in range(20):
        i = rng.integers(0, N, npair//20)
        j = rng.integers(0, N, npair//20)
        keep = i != j
        ua, ub = s0["u"][i[keep]], s0["u"][j[keep]]
        wa, wb = W0[i[keep]], W0[j[keep]]
        g = wa*wb - np.einsum("ij,ij->i", ua, ub)
        acc.append(np.mean(np.sqrt(np.maximum(g*g - 1, 0))/(wa*wb)))
    acc = np.array(acc)
    vs = acc.mean()
    out["vsample"] = vs
    out["vsample_se"] = acc.std(ddof=1)/np.sqrt(len(acc))
    out["vsample_vs_ensemble_rel"] = vs/vm - 1
    out["vtested_vs_sample_z"] = (vt.mean() - vs)/np.hypot(batch_se(vt), out["vsample_se"])
    # T2(c)
    out["T2c_dW_rel"] = (math.fsum(s1["m"]*W1)/math.fsum(s1["m"]) -
                         math.fsum(M0*W0)/math.fsum(M0))/(np.std(W0)/np.sqrt(N))
    cdf = mj_cdf_u(th_s)
    um1 = np.sqrt(np.einsum("ij,ij->i", s1["u"], s1["u"]))
    um0 = np.sqrt(np.einsum("ij,ij->i", s0["u"], s0["u"]))
    out["KS_p_end"] = float(stats.kstest(um1, cdf).pvalue)
    out["KS_p_start"] = float(stats.kstest(um0, cdf).pvalue)
    # T1 per step
    smw = h[:, COLL["sum_MW"]]
    dE = np.abs(h[:, COLL["dE"]])/smw
    dP = np.max(np.abs(h[:, COLL["dP1"]:COLL["dP3"] + 1]), axis=1)/smw
    bound = 1e-14*np.sqrt(ncoll + 1)
    out["T1_max_dE_over_bound"] = float(np.max(dE/bound))
    out["T1_max_dP_over_bound"] = float(np.max(dP/bound))
    out["T1_abs_dE_max_rel"] = float(np.max(h[:, COLL["abs_dE"]]/smw))
    seq = np.diff(smw)/smw[1:]
    out["T1_seq_sumMW_max_rel"] = float(np.max(np.abs(seq))) if len(seq) else 0.0
    out["T1_seq_sumMW_over_bound"] = float(np.max(np.abs(seq)/bound[1:])) if len(seq) else 0.0
    mu = h[:, COLL["sum_Mu1"]:COLL["sum_Mu3"] + 1]
    out["T1_seq_sumMu_max_rel"] = float(np.max(np.abs(np.diff(mu, axis=0)))/smw.mean())
    out["n_trunc_total"] = int(h[:, COLL["n_trunc"]].sum())
    out["max_P"] = float(h[:, COLL["max_P"]].max())
    out["mean_nsub"] = float(h[:, COLL["mean_nsub"]].mean())
    out["max_nsub"] = float(h[:, COLL["max_nsub"]].max())
    if h.shape[1] >= 36:
        out["n_noroot"] = int(h[:, COLL["n_noroot"]].sum())
        out["n_balance"] = int(h[:, COLL["n_balance"]].sum())
        out["max_dlam"] = float(h[:, COLL["max_dlam"]].max())
    series = dict(sumP=sumP, ncoll=ncoll, sumW=sumW, expct=expct, wexp=wexp, vt=vt, vm=vm,
                  vs=vs, dE=dE, dP=dP, bound=bound, ntested=h[:, COLL["n_tested"]])
    return out, series


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = a.out or lib.run_dir(SCR + "/tmp/verify_g1/v2")
    os.makedirs(out, exist_ok=True)
    rng = np.random.default_rng(7)
    # reference check of the quadrature
    refchk = []
    for th in [1e-3, 0.01, 0.1, 1.0, 10.0]:
        q1 = vmol_quad(th)
        q2 = vmol_quad(th, n=700)
        refchk.append(dict(theta=th, quad=q1, quad_n700=q2, closed=lib.vmol_mean(th),
                           rel=q1/lib.vmol_mean(th) - 1, nr_limit=np.sqrt(16*th/np.pi)))
        print("vmol", refchk[-1])
    res = dict(reference=refchk, runs={})
    allseries = {}
    for lab, run in RUNS.items():
        rows = []
        for cdir in sorted(glob.glob(f"{SCR}/{run}/T2_*")):
            r, s = analyse_case(cdir, rng)
            rows.append(r)
            allseries[(lab, r["case"])] = s
            print(lab, json.dumps(r, default=float))
        res["runs"][lab] = rows
    # same pairs in both executables
    same = []
    for r in res["runs"]["release"]:
        s1 = allseries[("release", r["case"])]
        s2 = allseries.get(("c2particle", r["case"]))
        if s1 is None or s2 is None:
            continue
        same.append(dict(case=r["case"],
                         steps_same_ntested=int(np.sum(s1["ntested"] == s2["ntested"])),
                         steps_same_ncoll=int(np.sum(s1["ncoll"] == s2["ncoll"])),
                         steps=len(s1["ncoll"]),
                         sumP_maxrel=float(np.max(np.abs(s1["sumP"]/s2["sumP"] - 1)))))
    res["paired"] = same
    print(json.dumps(same))
    lib.save_json(os.path.join(out, "v2_box.json"), res)
    figures(out, res, allseries)


def figures(out, res, allseries):
    from nrpic import figstyle
    import matplotlib.pyplot as plt
    figstyle.use_style()
    P = figstyle.PAL
    fig, ax = plt.subplots(2, 2, figsize=(8, 6))
    fig.subplots_adjust(left=0.1, right=0.98, bottom=0.08, top=0.95, wspace=0.3, hspace=0.35)
    cols = {"release": P["red"], "c2particle": P["blue"]}
    for lab, rows in res["runs"].items():
        rr = [r for r in rows if r["collisions"]]
        x = np.arange(len(rr)) + (0.15 if lab == "c2particle" else -0.15)
        ax[0, 0].errorbar(x, [100*r["T2b_rel"] for r in rr],
                          yerr=[100*r["T2b_se_rel"] for r in rr], fmt="o", ms=3,
                          color=cols[lab], label=lab)
        ax[0, 1].plot(x, [r["T2a_z"] for r in rr], "o", ms=3, color=cols[lab], label=lab)
        ax[1, 0].plot(x, [r["vtested_vs_sample_z"] for r in rr], "o", ms=3, color=cols[lab],
                      label=lab + ": tested vs sample pairs")
        ax[1, 0].plot(x, [r["vtested_z"] for r in rr], "x", ms=4, color=cols[lab],
                      label=lab + ": tested vs ensemble")
        ax[1, 1].plot(x, [r["T1_max_dE_over_bound"] for r in rr], "o", ms=3, color=cols[lab],
                      label=lab + ": max |dE| / bound")
        ax[1, 1].plot(x, [r["T1_max_dP_over_bound"] for r in rr], "s", ms=3, mfc="none",
                      color=cols[lab], label=lab + ": max |dP| / bound")
    names = [r["case"].replace("T2_th", "") for r in res["runs"]["release"] if r["collisions"]]
    for a in ax.ravel():
        a.set_xticks(range(len(names)))
        a.set_xticklabels(names, rotation=90, fontsize=6)
    ax[0, 0].axhspan(-0.5, 0.5, color="grey", alpha=0.15)
    ax[0, 0].axhline(0, color="k", lw=0.8)
    ax[0, 0].set_ylabel(r"sum_P / expected $-$ 1 [%]")
    ax[0, 0].legend(fontsize=7)
    ax[0, 1].axhspan(-4, 4, color="grey", alpha=0.15)
    ax[0, 1].set_ylabel(r"T2(a): z of $\Sigma n_{coll}$ vs $\Sigma$ sum_P")
    ax[1, 0].axhspan(-4, 4, color="grey", alpha=0.15)
    ax[1, 0].set_ylabel(r"z of $\langle v_{Mol}\rangle$ of tested pairs")
    ax[1, 0].legend(fontsize=6)
    ax[1, 1].set_yscale("log")
    ax[1, 1].axhline(1, color="k", ls="--", lw=1)
    ax[1, 1].set_ylabel(r"T1: per-step defect / $10^{-14}\sqrt{n_{coll}+1}$")
    ax[1, 1].legend(fontsize=6)
    fig.savefig(os.path.join(out, "v2_box.png"))
    plt.close(fig)
    # time series of one case
    fig, ax = plt.subplots(1, 2, figsize=(8, 3))
    fig.subplots_adjust(left=0.1, right=0.98, bottom=0.17, top=0.9, wspace=0.3)
    for k, name in enumerate(["T2_th0.1_plain_s1", "T2_th10.0_sub_s1"]):
        s = allseries.get(("release", name))
        if s is None:
            continue
        ax[k].plot(s["sumP"]/s["expct"] - 1, color=P["red"], lw=0.8, label="sum_P/expected - 1")
        ax[k].plot(s["sumW"]/s["wexp"] - 1, color=P["green"], lw=0.8,
                   label="sum_W/expected - 1")
        ax[k].plot(s["vt"]/s["vm"] - 1, color=P["blue"], lw=0.8,
                   label=r"tested $\langle v\rangle$/MJ - 1")
        ax[k].axhline(0, color="k", lw=0.8)
        ax[k].set_title(name + " (release)", fontsize=9)
        ax[k].set_xlabel("step")
    ax[0].legend(fontsize=7)
    fig.savefig(os.path.join(out, "v2_series.png"))
    plt.close(fig)


if __name__ == "__main__":
    main()
