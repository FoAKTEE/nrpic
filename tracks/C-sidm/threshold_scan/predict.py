#!/usr/bin/env python3
"""Predictions for the collisional cluster runs CC1/CC2, computed before the runs from the
particle files and the static metric of the equilibria (no AthenaK output is read).

For every collision cell of the first step (the leaf mesh cell of the static mesh of
inputs/*.athinput; cell factor 1) and every pair (i, j) in it, the operator of
coord/INTERFACES/collisions.md collides the pair with the expected number per step

    w_ij = sigma_m M alpha_c dt v_Mol(i, j) / (psi_c^6 dx^3)                  (eq. 1 there)

(each particle is tested against one partner drawn from the other N - 1 with probability
(N - 1) times this per test), so the expectation of the history column sum_P of one step is
sum_ij w_ij, whatever the pairing. The momenta are the triad components p = u/psi_c^2 of
the cell-centre metric (conformally flat data: both triad gauges give S = psi^2 I). For
each pair the isotropic scattering in its centre-of-momentum frame is sampled in K
directions; from it follow, per collision:

  - the change of sum M W with W at each particle's own metric, W = (1 + u^2/psi(r_i)^4)^(1/2)
    (history column dE_particles with coll_budget = true): the energy defect of the
    operator in a potential (core's interface, section 9);
  - the change of the Killing energy sum M alpha(r_i) W_i (zero shift);
  - the number of particles moved above the King cut-off E0 and above E = 1 (unbound).

The spread of sum_P of one step over random pairings is sampled by drawing the pairing of
the operator (random permutation, pairs (0,1), (2,3), ..., a triple for odd N).

    python3 predict.py [--out DIR] [--K 16] [--pairings 200]

Writes predictions.json and the figures fig_pred_*.png into --out (default
$NRPIC_RUN_DIR).
"""
import argparse
import json
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

import numpy as np  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

T_RUN = 300.0


def cells_of(x):
    """Leaf cell of each particle: cell size and integer cell index on its level."""
    dx = C.leaf_dx(x)
    idx = np.floor((x - C.X_MIN) / dx[:, None]).astype(np.int64)
    lev = np.round(np.log2(C.DX_ROOT / dx)).astype(np.int64)
    key = ((lev * 8192 + idx[:, 0]) * 8192 + idx[:, 1]) * 8192 + idx[:, 2]
    centre = C.X_MIN + (idx + 0.5) * dx[:, None]
    return key, dx, centre


def scatter(pa, pb, n):
    """Isotropic elastic scattering in the centre-of-momentum frame (unit masses; pa, pb
    triad momenta [P,3]; n unit vectors [P,3] in the CM frame reached by the boost
    without rotation). Returns pa', pb'."""
    Wa = np.sqrt(1.0 + np.sum(pa * pa, axis=1))
    Wb = np.sqrt(1.0 + np.sum(pb * pb, axis=1))
    P = pa + pb
    E = Wa + Wb
    s = E * E - np.sum(P * P, axis=1)
    rs = np.sqrt(s)
    pstar = np.sqrt(np.maximum(s / 4.0 - 1.0, 0.0))
    nP = np.sum(n * P, axis=1)
    pa2 = pstar[:, None] * n + P * (pstar * nP / (rs * (E + rs)) + 0.5)[:, None]
    return pa2, P - pa2


def vmol(pa, pb):
    Wa = np.sqrt(1.0 + np.sum(pa * pa, axis=1))
    Wb = np.sqrt(1.0 + np.sum(pb * pb, axis=1))
    g = Wa * Wb - np.sum(pa * pb, axis=1)
    return np.sqrt(np.maximum(g * g - 1.0, 0.0)) / (Wa * Wb)


def predict_model(key, K, npair, rng):
    spec = C.MODELS[key]
    md = C.load_model(spec["tag"])
    meta = md["meta"]
    x, u, m = md["x"], md["u"], md["m"]
    N = len(m)
    M = float(m[0])
    E0 = meta["E0"]
    Kc, Hc, v1 = C.kn_constant(meta)
    r = np.linalg.norm(x, axis=1)
    psi_p, alp_p = C.psi_alpha(md, r)
    W_p = np.sqrt(1.0 + np.sum(u * u, axis=1) / psi_p ** 4)
    EK = alp_p * W_p
    ckey, dx, centre = cells_of(x)
    order = np.argsort(ckey, kind="stable")
    sk = ckey[order]
    starts = np.flatnonzero(np.r_[True, sk[1:] != sk[:-1]])
    ends = np.r_[starts[1:], len(sk)]
    occ = ends - starts
    # all pairs of every cell with at least two particles
    ia, ib, cell_of_pair = [], [], []
    for c, (s0, s1) in enumerate(zip(starts, ends)):
        n = s1 - s0
        if n < 2:
            continue
        mem = order[s0:s1]
        a, b = np.triu_indices(n, 1)
        ia.append(mem[a])
        ib.append(mem[b])
        cell_of_pair.append(np.full(len(a), c))
    ia, ib, cell_of_pair = np.concatenate(ia), np.concatenate(ib), np.concatenate(cell_of_pair)
    # cell-centre metric
    first = order[starts]
    rc = np.linalg.norm(centre[first], axis=1)
    psi_c, alp_c = C.psi_alpha(md, rc)
    dx_c = dx[first]
    dt = C.CFL * C.DX_ROOT / 2 ** 6           # global step: Courant number times finest dx
    V_c = psi_c ** 6 * dx_c ** 3
    fac_c = M * alp_c * dt / V_c              # times sigma_m and v_Mol: expected collisions
    cp = cell_of_pair
    pa = u[ia] / psi_c[cp, None] ** 2
    pb = u[ib] / psi_c[cp, None] ** 2
    v = vmol(pa, pb)
    w1 = fac_c[cp] * v                        # per unit sigma_m
    # isotropic outcomes, K directions per pair
    dWp = np.zeros(len(ia))
    dEK = np.zeros(len(ia))
    dtail = np.zeros(len(ia))
    dunb = np.zeros(len(ia))
    pre_tail = (EK[ia] > E0).astype(float) + (EK[ib] > E0)
    pre_unb = (EK[ia] > 1.0).astype(float) + (EK[ib] > 1.0)
    for _ in range(K):
        nvec = rng.normal(size=(len(ia), 3))
        nvec /= np.linalg.norm(nvec, axis=1)[:, None]
        qa, qb = scatter(pa, pb, nvec)
        ua = qa * psi_c[cp, None] ** 2
        ub = qb * psi_c[cp, None] ** 2
        Wa = np.sqrt(1.0 + np.sum(ua * ua, axis=1) / psi_p[ia] ** 4)
        Wb = np.sqrt(1.0 + np.sum(ub * ub, axis=1) / psi_p[ib] ** 4)
        dWp += M * (Wa + Wb - W_p[ia] - W_p[ib])
        Ea, Eb = alp_p[ia] * Wa, alp_p[ib] * Wb
        dEK += M * (Ea + Eb - EK[ia] - EK[ib])
        dtail += (Ea > E0).astype(float) + (Eb > E0) - pre_tail
        dunb += (Ea > 1.0).astype(float) + (Eb > 1.0) - pre_unb
    dWp /= K
    dEK /= K
    dtail /= K
    dunb /= K
    # check of the kernel: the cell-frame pair energy is conserved
    qa, qb = scatter(pa[:2000], pb[:2000], np.tile([0.0, 0.0, 1.0], (min(2000, len(pa)), 1)))
    e_err = float(np.max(np.abs(np.sqrt(1 + np.sum(qa * qa, 1)) + np.sqrt(1 + np.sum(qb * qb, 1))
                                - np.sqrt(1 + np.sum(pa[:2000] ** 2, 1))
                                - np.sqrt(1 + np.sum(pb[:2000] ** 2, 1)))))
    sumw1 = float(w1.sum())
    per = lambda q: float(np.sum(w1 * q) / sumw1)   # mean over collisions  # noqa: E731
    # spread of sum_P of one step over random pairings (operator's pairing rule)
    pair_sums = []
    vcell = {}
    for c, (s0, s1) in enumerate(zip(starts, ends)):
        if s1 - s0 >= 2:
            vcell[c] = order[s0:s1]
    cells = list(vcell)
    for _ in range(npair):
        tot = 0.0
        for c in cells:
            mem = rng.permutation(vcell[c])
            n = len(mem)
            sc = psi_c[c] ** -2
            f = fac_c[c] * (n - 1)
            if n % 2:
                tri = mem[:3]
                for a, b in ((0, 1), (1, 2), (2, 0)):
                    tot += 0.5 * f * vmol(u[tri[a]][None] * sc, u[tri[b]][None] * sc)[0]
                rest = mem[3:]
            else:
                rest = mem
            if len(rest):
                tot += f * float(np.sum(vmol(u[rest[0::2]] * sc, u[rest[1::2]] * sc)))
        pair_sums.append(tot)
    pair_sums = np.array(pair_sums)
    # Knudsen-number bookkeeping from the equilibria package (run C-sidm-20261115-122915-cdc395c)
    kj = [d for d in json.load(open(C.KNUDSEN_JSON))["models"] if d["tag"] == spec["tag"]][0]
    out = dict(model=key, tag=spec["tag"], N=N, M_particle=M, E0=E0, alpha_c=meta["alpha_c"],
               psi_c=meta["psi_c"], K_sigma=Kc, H_c=Hc, v1_c=v1, dt=dt,
               cells_occupied=int(len(starts)), cells_ge2=int(np.sum(occ >= 2)),
               occupancy_max=int(occ.max()), occupancy_mean=float(occ.mean()),
               frac_in_level6=float(np.mean(dx == 0.25)), pairs=int(len(ia)),
               kernel_pair_energy_err=e_err,
               frac_EK_above_E0_initial=float(np.mean(EK > E0)),
               frac_EK_within={f"{d:g}": float(np.mean(EK > E0 * (1 - d))) for d in (1e-3, 1e-2, 3e-2)},
               runs={})
    for kn in C.KN_LIST:
        if kn is None:
            continue
        sig = C.sigma_of(meta, kn)
        nstep = sig * sumw1
        nsteps = int(round(T_RUN / dt))
        kn_l = kj["Kn_times_sigma_tilde"] / sig
        nu_bar = kj["nu_bar_times_Kn"] / kn_l
        n_conv = 0.5 * N * nu_bar / kj["t_d_coord"] * T_RUN
        ncoll = nstep * nsteps
        e_sum = float(np.sum(M * W_p))
        out["runs"][C.run_name(key, kn)] = dict(
            Kn=kn, sigma=sig,
            sumP_step1_expected=nstep,
            sumP_step1_pairing_mean=float(sig * pair_sums.mean()),
            sumP_step1_pairing_sd=float(sig * pair_sums.std(ddof=1)),
            collisions_300M_constant_rate=ncoll,
            collisions_300M_conversion_md=n_conv,
            collisions_per_particle_300M=2.0 * ncoll / N,
            dE_particles_per_collision=per(dWp),
            dE_particles_per_collision_rel=per(dWp) / e_sum,
            dE_particles_300M_rel=per(dWp) * ncoll / e_sum,
            dEK_per_collision=per(dEK),
            dEK_300M=per(dEK) * ncoll,
            tail_E0_per_collision=per(dtail),
            unbound_per_collision=per(dunb),
            tail_E0_300M_linear=per(dtail) * ncoll,
            unbound_300M_linear=per(dunb) * ncoll,
            sum_MW_initial=e_sum)
    figdata = dict(r=r, EK=EK, occ=occ, rc=rc, pair_sums=pair_sums, w1=w1, dWp=dWp,
                   rpair=np.linalg.norm(centre[order[starts]][cp], axis=1), E0=E0)
    return out, figdata


def figures(outdir, res, figs):
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    # 1: occupation of the collision cells against the radius of the cell centre
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.07, right=0.985, bottom=0.16, top=0.95, wspace=0.42)
    cols = {"cc1": fs.PAL["red"], "cc2": fs.PAL["blue"]}
    for key, fd in figs.items():
        axs[0].plot(fd["rc"], fd["occ"], ".", ms=1.5, color=cols[key], alpha=0.4,
                    label=C.MODELS[key]["label"])
        ps = fd["pair_sums"]
        axs[1].hist((ps - ps.mean()) / ps.mean(), bins=30, histtype="step", color=cols[key],
                    lw=1.5, label=key.upper())
        # energy defect per collision, binned by radius of the cell
        rb = np.linspace(0, 12, 25)
        k = np.digitize(fd["rpair"], rb)
        num = np.bincount(k, weights=fd["w1"] * fd["dWp"], minlength=len(rb) + 1)
        den = np.bincount(k, weights=fd["w1"], minlength=len(rb) + 1)
        ok = den[1:len(rb)] > 0
        rm = 0.5 * (rb[1:] + rb[:-1])
        axs[2].plot(rm[ok], num[1:len(rb)][ok] / den[1:len(rb)][ok] / res[key]["M_particle"],
                    color=cols[key], label=key.upper())
    axs[0].axvline(8.0, **fs.MASK_LINE)
    axs[0].set_xlabel(r"cell centre $r/M$")
    axs[0].set_ylabel("particles per collision cell")
    axs[0].legend(fontsize=8, loc="upper right", markerscale=6)
    axs[1].ticklabel_format(axis="x", style="sci", scilimits=(-2, 2))
    axs[1].set_xlabel(r"sum$_P$(step 1)/mean $-$ 1")
    axs[1].set_ylabel("pairings")
    axs[1].legend(fontsize=8)
    axs[2].axhline(0.0, **fs.GUIDE)
    axs[2].set_xlabel(r"cell centre $r/M$")
    axs[2].set_ylabel(r"$\langle\Delta(W_a+W_b)\rangle$ per collision")
    axs[2].legend(fontsize=8)
    fig.savefig(os.path.join(outdir, "fig_pred_cells.png"), dpi=200)
    plt.close(fig)
    # 2: Killing energies of the initial particles near the cut-off
    fig, ax = plt.subplots(figsize=(fs.COLUMN_WIDTH, 3.0))
    fig.subplots_adjust(left=0.17, right=0.97, bottom=0.15, top=0.95)
    for key, fd in figs.items():
        ax.hist(fd["EK"] / fd["E0"], bins=200, histtype="step", color=cols[key], lw=1.2,
                label=key.upper(), density=True)
    ax.axvline(1.0, **fs.GUIDE)
    ax.set_xlabel(r"Killing energy $E/E_0$ of the initial particles")
    ax.set_ylabel("density")
    ax.legend(fontsize=8, loc="upper left")
    fig.savefig(os.path.join(outdir, "fig_pred_energies.png"), dpi=200)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--K", type=int, default=16)
    ap.add_argument("--pairings", type=int, default=200)
    ap.add_argument("--seed", type=int, default=20261115)
    a = ap.parse_args()
    if not a.out:
        sys.exit("give --out or run through nrpic-run")
    os.makedirs(a.out, exist_ok=True)
    rng = np.random.default_rng(a.seed)
    res, figs = {}, {}
    for key in C.MODELS:
        res[key], figs[key] = predict_model(key, a.K, a.pairings, rng)
        print(json.dumps(res[key], indent=1), flush=True)
    res["inputs"] = dict(ic_run=C.IC_RUN, knudsen_json=os.path.relpath(C.KNUDSEN_JSON, C.WT),
                         K=a.K, pairings=a.pairings, seed=a.seed, T_run=T_RUN)
    with open(os.path.join(a.out, "predictions.json"), "w") as f:
        json.dump(res, f, indent=1)
    figures(a.out, res, figs)
    return 0


if __name__ == "__main__":
    sys.exit(main())
