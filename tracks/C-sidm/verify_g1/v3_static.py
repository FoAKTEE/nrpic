"""V3: collisions in the static homogeneous curved metric (T12), own analysis.

Run C-20261119-143049-0cf699a (collisions-2 CPU executable; deck
box_tests/inputs/box_static.athinput: alpha0 = 0.8, psi0 = 1.1, gamma_ij = psi0^4 delta_ij,
zero shift; flat twins with box side psi0^2 and dt alpha0 dt). Own expectation (JOURNAL
entry 7): collisions per coordinate step
    (1/2) N rho_p sigma_m <v_Mol>(theta_s) alpha0 dt,   rho_p = sum M / (psi0^6 V_c),
i.e. alpha0 psi0^6 times the flat rate per unit time and volume at equal proper density.
"""
import argparse
import glob
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib  # noqa: E402
from lib import COLL  # noqa: E402
from v2_box import vmol_quad, theta_from_w, parse_args_log, batch_se  # noqa: E402

SCR = "/data/haiyangw/nrpic/scratch/C-sidm"
RUN = "C-20261119-143049-0cf699a"
DECK = "/data/haiyangw/nrpic/wt/C-sidm/tracks/C-sidm/box_tests/inputs/box_static.athinput"


def read_deck(path):
    out, blk = {}, None
    for line in open(path):
        line = line.split("#")[0].strip()
        if not line:
            continue
        if line.startswith("<"):
            blk = line.strip("<>")
            continue
        if "=" in line:
            k, v = [s.strip() for s in line.split("=", 1)]
            out[f"{blk}/{k}"] = v
    return out


def cell_counts(x, lo, side, ncell):
    """Occupation of the ncell^3 coordinate cells of the box [lo, lo + side)^3."""
    idx = np.floor((x - lo)/side*ncell).astype(np.int64)
    idx = np.clip(idx, 0, ncell - 1)
    flat = (idx[:, 0]*ncell + idx[:, 1])*ncell + idx[:, 2]
    return np.bincount(flat, minlength=ncell**3)


def analyse(cdir, curved, alpha0, psi0):
    kv = parse_args_log(os.path.join(cdir, "athena.log"))
    dt = float(kv["particles/dt"])
    sig = float(kv["particles/coll_sigma"])
    side = float(kv.get("mesh/x1max", "11.0")) - 10.0
    ncell = int(kv["mesh/nx1"])
    snaps = sorted(glob.glob(cdir + "/box.part.*.bin"))
    s0 = lib.read_snap(snaps[0])
    s1 = lib.read_snap(snaps[-1])
    p4 = psi0**4 if curved else 1.0
    lap = alpha0 if curved else 1.0
    vprop_factor = psi0**6 if curved else 1.0
    u0 = s0["u"]
    W0 = np.sqrt(1 + np.einsum("ij,ij->i", u0, u0)/p4)
    M = s0["m"]
    N = s0["n"]
    Vc = side**3
    rho_p = math.fsum(M)/(vprop_factor*Vc)
    th = theta_from_w(math.fsum(M*W0)/math.fsum(M))
    vm = vmol_quad(th)
    expct = 0.5*N*rho_p*sig*vm*lap*dt
    h = lib.read_hist(os.path.join(cdir, "box.coll.hst"))
    ncoll = h[:, COLL["n_coll"]]
    sumP = h[:, COLL["sum_P"]]
    sumW = h[:, COLL["sum_W"]]
    nst = len(ncoll)
    out = dict(case=os.path.basename(cdir), curved=curved, energy=kv.get("particles/coll_energy"),
               dt=dt, sigma=sig, side=side, N=N, rho_p=rho_p, theta_s=th, vmol=vm,
               expected_per_step=expct, steps=nst, ncoll_total=float(ncoll.sum()),
               sumP_total=float(sumP.sum()))
    out["z_ncoll_vs_expected"] = (ncoll.sum() - nst*expct)/math.sqrt(nst*expct)
    out["rel_ncoll_vs_expected"] = ncoll.sum()/(nst*expct) - 1
    out["rel_sumP_vs_expected"] = sumP.mean()/expct - 1
    out["z_sumP_batch"] = (sumP.mean() - expct)/batch_se(sumP)
    out["z_ncoll_vs_sumP"] = (ncoll.sum() - sumP.sum())/math.sqrt(sumP.sum())
    # per coordinate time and coordinate volume
    out["rate_coord"] = ncoll.sum()/(nst*dt*Vc)
    out["rate_coord_expected"] = expct/(dt*Vc)
    # pair counting at cycle 1: one straight push from the initial snapshot
    vel = lap*u0/(p4*W0[:, None])
    x1 = s0["x"] + vel*h[0, COLL["time"]]
    x1 = 10.0 + np.mod(x1 - 10.0, side)
    cnt = cell_counts(x1, 10.0, side, ncell).astype(float)
    dVp = vprop_factor*(side/ncell)**3
    Mp = M[0]
    sumW_own = math.fsum(cnt*(cnt - 1))*sig*Mp*lap*dt/(2*dVp)
    out["sumW_cycle1_code"] = float(sumW[0])
    out["sumW_cycle1_own"] = sumW_own
    out["sumW_cycle1_rel"] = sumW[0]/sumW_own - 1
    out["mass_equal"] = bool(np.all(M == Mp))
    # conservation per step
    smw = h[:, COLL["sum_MW"]]
    dE = np.abs(h[:, COLL["dE"]])/smw
    dP = np.max(np.abs(h[:, COLL["dP1"]:COLL["dP3"] + 1]), axis=1)/smw
    bound = 1e-14*np.sqrt(ncoll + 1)
    out["T1_max_dE_over_bound"] = float(np.max(dE/bound))
    out["T1_max_dP_over_bound"] = float(np.max(dP/bound))
    mu = h[:, COLL["sum_Mu1"]:COLL["sum_Mu3"] + 1]
    out["hist_sumMu_maxstep_rel"] = float(np.max(np.abs(np.diff(mu, axis=0)))/smw.mean())
    out["hist_sumMW_maxstep_rel"] = float(np.max(np.abs(np.diff(smw)))/smw.mean())
    if h.shape[1] >= 36:
        out["n_noroot"] = int(h[:, COLL["n_noroot"]].sum())
        out["n_balance"] = int(h[:, COLL["n_balance"]].sum())
        out["max_dlam"] = float(h[:, COLL["max_dlam"]].max())
        out["max_abs_dH_particles_rel"] = float(np.max(np.abs(h[:, COLL["dH_particles"]]))/smw.mean())
    out["n_trunc"] = int(h[:, COLL["n_trunc"]].sum())
    # snapshot sums (covariant momenta, energies with the metric)
    W1 = np.sqrt(1 + np.einsum("ij,ij->i", s1["u"], s1["u"])/p4)
    E0 = math.fsum(M*W0)
    out["snap_cycles"] = [int(s0["cycle"]), int(s1["cycle"])]
    out["snap_dE_rel"] = (math.fsum(s1["m"]*W1) - E0)/E0
    out["snap_dPcov_rel"] = [(math.fsum(s1["m"]*s1["u"][:, i]) - math.fsum(M*u0[:, i]))/E0
                             for i in range(3)]
    series = dict(ncoll=ncoll, sumP=sumP, sumW=sumW, ntested=h[:, COLL["n_tested"]], expct=expct,
                  dE=dE, dP=dP, bound=bound, s0=s0, s1=s1)
    return out, series


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = a.out or lib.run_dir(SCR + "/tmp/verify_g1/v3")
    os.makedirs(out, exist_ok=True)
    deck = read_deck(DECK)
    alpha0 = float(deck["problem/alpha0"])
    psi0 = float(deck["problem/psi0"])
    for k in ["alpha_amp", "psi_amp", "shift_amp"]:
        assert float(deck["problem/" + k]) == 0.0
    res = dict(alpha0=alpha0, psi0=psi0, factor=alpha0*psi0**6, cases=[], twins=[])
    ser = {}
    for cdir in sorted(glob.glob(f"{SCR}/{RUN}/T12_*")):
        name = os.path.basename(cdir)
        curved = ("curved" in name) or ("cell" in name)
        r, s = analyse(cdir, curved, alpha0, psi0)
        res["cases"].append(r)
        ser[name] = s
        print(json.dumps(r, default=float))
    # twins
    for th in ["0.1", "1.0"]:
        for sd in ["1", "2"]:
            c = ser.get(f"T12_th{th}_curved_s{sd}")
            f = ser.get(f"T12_th{th}_flat_s{sd}")
            if c is None or f is None:
                continue
            tw = dict(theta=th, seed=sd, steps=len(c["ncoll"]),
                      same_ntested=int(np.sum(c["ntested"] == f["ntested"])),
                      same_ncoll=int(np.sum(c["ncoll"] == f["ncoll"])),
                      sumP_maxrel=float(np.max(np.abs(c["sumP"]/f["sumP"] - 1))))
            for key, s in [("start", "s0"), ("end", "s1")]:
                cs, fs = c[s], f[s]
                oc, of = np.argsort(cs["tag"]), np.argsort(fs["tag"])
                tw[f"{key}_tags_equal"] = bool(np.array_equal(cs["tag"][oc], fs["tag"][of]))
                tw[f"{key}_max_du"] = float(np.max(np.abs(cs["u"][oc]/psi0**2 - fs["u"][of])))
                dx = psi0**2*(cs["x"][oc] - 10.0) - (fs["x"][of] - 10.0)
                L = psi0**2
                dx = dx - L*np.round(dx/L)
                tw[f"{key}_max_dx"] = float(np.max(np.abs(dx)))
            res["twins"].append(tw)
            print(json.dumps(tw))
    cc = ser.get("T12_th0.1_cell_s1")
    cp = ser.get("T12_th0.1_curved_s1")
    if cc is not None and cp is not None:
        oc, op = np.argsort(cc["s1"]["tag"]), np.argsort(cp["s1"]["tag"])
        res["cell_vs_particle"] = dict(
            same_ntested=int(np.sum(cc["ntested"] == cp["ntested"])),
            same_ncoll=int(np.sum(cc["ncoll"] == cp["ncoll"])), steps=len(cc["ncoll"]),
            end_max_du=float(np.max(np.abs(cc["s1"]["u"][oc] - cp["s1"]["u"][op]))))
        print(json.dumps(res["cell_vs_particle"]))
    lib.save_json(os.path.join(out, "v3_static.json"), res)
    figures(out, res, ser)


def figures(out, res, ser):
    from nrpic import figstyle
    import matplotlib.pyplot as plt
    figstyle.use_style()
    P = figstyle.PAL
    fig, ax = plt.subplots(2, 2, figsize=(8, 6))
    fig.subplots_adjust(left=0.1, right=0.98, bottom=0.09, top=0.94, wspace=0.32, hspace=0.38)
    for name, col in [("T12_th0.1_curved_s1", P["red"]), ("T12_th0.1_flat_s1", P["blue"]),
                      ("T12_th1.0_curved_s1", P["orange"]), ("T12_th1.0_flat_s1", P["green"])]:
        s = ser.get(name)
        if s is None:
            continue
        ls = "-" if "curved" in name else ":"
        ax[0, 0].plot(s["ncoll"]/s["expct"] - 1, ls, color=col, lw=0.8, label=name[4:])
        ax[0, 1].plot(np.cumsum(s["ncoll"] - s["expct"])/np.sqrt(np.cumsum(np.full(len(s["ncoll"]), s["expct"]))),
                      ls, color=col, lw=1.0, label=name[4:])
        ax[1, 1].plot(s["dE"]/s["bound"], ls, color=col, lw=0.8, label=name[4:])
    ax[0, 0].axhline(0, color="k", lw=0.8)
    ax[0, 0].set_ylabel("n_coll per step / own expectation - 1")
    ax[0, 0].set_xlabel("step")
    ax[0, 0].legend(fontsize=6)
    ax[0, 1].axhspan(-4, 4, color="grey", alpha=0.15)
    ax[0, 1].set_ylabel(r"cumulative z of $\Sigma$ n_coll")
    ax[0, 1].set_xlabel("step")
    ax[1, 1].set_yscale("log")
    ax[1, 1].axhline(1, color="k", ls="--", lw=1)
    ax[1, 1].set_ylabel(r"|dE| / $10^{-14}\sqrt{n_{coll}+1}$ sum_MW")
    ax[1, 1].set_xlabel("step")
    rows = [r for r in res["cases"]]
    x = np.arange(len(rows))
    ax[1, 0].errorbar(x, [r["z_ncoll_vs_expected"] for r in rows], fmt="o", ms=4, color=P["red"],
                      label="n_coll vs own expectation")
    ax[1, 0].plot(x, [r["z_ncoll_vs_sumP"] for r in rows], "s", ms=4, mfc="none", color=P["blue"],
                  label="n_coll vs sum_P")
    ax[1, 0].axhspan(-4, 4, color="grey", alpha=0.15)
    ax[1, 0].set_xticks(x)
    ax[1, 0].set_xticklabels([r["case"][4:] for r in rows], rotation=90, fontsize=6)
    ax[1, 0].set_ylabel("z (Poisson)")
    ax[1, 0].legend(fontsize=6)
    fig.suptitle(r"T12: static metric $\alpha_0$ = %.2f, $\psi_0$ = %.2f; factor $\alpha_0\psi_0^6$ = %.4f"
                 % (res["alpha0"], res["psi0"], res["factor"]), fontsize=9)
    fig.savefig(os.path.join(out, "v3_static.png"))
    plt.close(fig)


if __name__ == "__main__":
    main()
