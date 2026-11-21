#!/usr/bin/env python3
"""Lockstep record per shell against the code-time MS reference at N_f, for the card runs of
the USR case (JOURNAL entry 14.1, predictions L1-L3): the RK4 phase-error reading
k^5 dt^4 / 600 of the lockstep integration of the mode functions from N*.

    python3 lockstep_shells.py --g1 G1RUNDIR --u256 U256RUNDIR --coeffs COEFFS_N256.npz \
        --ref ../results --out OUT
"""
import argparse
import json
import os

import numpy as np

import analyse_cards as ac
import card_lib as cl
import usr_lib as ul


def lock_per_shell(rundir, ci, s=1.0):
    dumps = cl.dump_list(rundir)
    h = ul.read_header(dumps[-1])
    hd, n2r, rr, drr = ul.read_modes_record(dumps[-1][:-5] + ".modes")
    nmax2 = int(n2r.max())
    mf = os.path.join(ac.PKG, "inputs", ac.MODEFILE[64 if nmax2 <= 64 else 4096])
    sref = cl.ShellReference(ci, mf, nmax2, np.array([h["time"]]))
    st = sref.state(0)
    idx = np.searchsorted(sref.n2, n2r)
    R = s * st["R"][idx]
    rel = np.abs(rr - R) / np.abs(R)
    con = cl.read_con(os.path.join(rundir, "usr.sf.con.hst"))
    dt = float(np.median(np.diff(con[:, cl.C["t"]])))
    return dict(n2=n2r, k=np.sqrt(n2r.astype(float)), rel=rel, dt=dt, t=h["time"], nmax2=nmax2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--g1", required=True)
    ap.add_argument("--u256", required=True)
    ap.add_argument("--coeffs", required=True)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(os.path.join(a.out, "fig"), exist_ok=True)
    r, ci, lm = ac.load_ref(a.ref)
    runs = {"U64p": os.path.join(a.g1, "U64p"), "U128p": os.path.join(a.g1, "U128p"),
            "U256": os.path.join(a.u256, "U256")}
    L = {n: lock_per_shell(d, ci) for n, d in runs.items()}
    out = dict(runs=runs)
    for n, x in L.items():
        pred = x["k"]**5 * x["dt"]**4 / 600.0
        out[n] = dict(dt=x["dt"], t=x["t"], nshells=int(x["n2"].size), lock_max=float(x["rel"].max()),
                      lock_lowest=float(x["rel"][0]), lock_top=float(x["rel"][-1]),
                      top_minus_lowest=float(x["rel"][-1] - x["rel"][0]),
                      pred_top=float(pred[-1]))
        print(n, {k: v for k, v in out[n].items()}, flush=True)
    stats = lambda v: dict(n=int(v.size), ratio_min=float(v.min()), ratio_max=float(v.max()),
                           ratio_median=float(np.median(v)),
                           within_05_2=int(np.sum((v >= 0.5) & (v <= 2.0)))) if v.size else dict(n=0)
    # L1: 256^3, shells k >= 24 (within_05_2 = within a factor 2)
    x = L["U256"]
    pred = x["k"]**5 * x["dt"]**4 / 600.0
    sel = x["k"] >= 24.0 - 1e-9
    ratio = x["rel"][sel] / pred[sel]
    out["L1"] = stats(ratio)
    print("L1", out["L1"], flush=True)
    # L2: 64^3 and 128^3 top minus lowest shell
    out["L2"] = {n: dict(top_minus_lowest=out[n]["top_minus_lowest"], pred=out[n]["pred_top"]) for n in ("U64p", "U128p")}
    print("L2", out["L2"], flush=True)
    # L3: per-mode R^NR error at N_f, shell median, against the lockstep error of the shell
    z = np.load(a.coeffs)
    nn = z["n"]
    n2m = (nn * nn).sum(axis=1)
    c = z["c_U256"][-1]
    cr = z["cref"][-1]
    rel_m = np.abs(c / cr - 1.0)
    sh, inv = np.unique(n2m, return_inverse=True)
    med = np.array([np.median(rel_m[inv == j]) for j in range(sh.size)])
    assert np.array_equal(sh, x["n2"])
    ks = np.sqrt(sh.astype(float))
    s3 = ks >= 40.0 - 1e-9
    q = med[s3] / x["rel"][s3]
    out["L3"] = stats(q)
    print("L3", out["L3"], flush=True)
    med_odd = None
    if "c_U256m" in z.files:
        # entry 14.3: the odd part of the pair U256/U256m against the same reference
        odd = 0.5 * (z["c_U256"][-1] - z["c_U256m"][-1])
        even = 0.5 * (z["c_U256"][-1] + z["c_U256m"][-1])
        rel_o = np.abs(odd / cr - 1.0)
        med_odd = np.array([np.median(rel_o[inv == j]) for j in range(sh.size)])
        k_m = np.sqrt(n2m.astype(float))
        km32 = k_m <= 32.0 + 1e-9
        qo = med_odd[s3] / x["rel"][s3]
        out["P14_3"] = dict(
            odd_median_k_le_32=float(np.median(rel_o[km32])), odd_max_k_le_32=float(rel_o[km32].max()),
            even_over_odd_rms_k_le_32=float(np.sqrt(np.sum(np.abs(even[km32])**2) / np.sum(np.abs(odd[km32])**2))),
            single_run_failures_odd=[float(v) for v in rel_o[km32][rel_m[km32] > 0.02]],
            odd_shell_median_over_lock_k_ge_40=stats(qo))
        print("P14_3", out["P14_3"], flush=True)
    with open(os.path.join(a.out, "lockstep_shells.json"), "w") as fp:
        json.dump(out, fp, indent=1)

    import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    cols = fs.series_colors(3)
    fig, ax = plt.subplots(2, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 6.0))
    fig.subplots_adjust(left=0.15, right=0.97, top=0.97, bottom=0.09, hspace=0.3)
    for (n, xx), col in zip(L.items(), cols):
        p = xx["k"]**5 * xx["dt"]**4 / 600.0
        ax[0].loglog(xx["k"], xx["rel"], ".", ms=2.0, color=col, label=f"{n}: lockstep record (dt = {xx['dt']:.3g})")
        kk = np.linspace(1.0, xx["k"].max(), 200)
        ax[0].loglog(kk, kk**5 * xx["dt"]**4 / 600.0 + (xx["rel"][0] if n != "U256" else 0.0), color=col, lw=0.8,
                     ls="--", label=r"$k^5 dt^4/600$" + (" + lowest shell" if n != "U256" else ""))
    ax[0].set_xlabel(r"$|n| = k/dk$ of the shell")
    ax[0].set_ylabel(r"$|R_{\rm lock}-R_{\rm ref}|/|R_{\rm ref}|$ at $N_f$")
    ax[0].legend(loc="upper left", fontsize=6)
    ax[1].semilogy(ks, med, color=cols[2], lw=0.8, label=r"U256: shell median of $|c/c_{\rm ref}-1|$ ($R^{\rm NR}$)")
    if med_odd is not None:
        ax[1].semilogy(ks, med_odd, color=cols[1], lw=0.8, label=r"U256/U256m odd part: shell median")
    ax[1].semilogy(x["k"], x["rel"], color=cols[0], lw=0.8, label="U256: lockstep record of the shell")
    ax[1].axvline(40.0, **fs.MASK_LINE)
    ax[1].set_xlabel(r"$|n| = k/dk$")
    ax[1].set_ylabel(r"at $N_f$")
    ax[1].legend(loc="upper left", fontsize=7)
    fs.save(fig, os.path.join(a.out, "fig", "fig_card_lockstep"))
    plt.close(fig)
    print("done", flush=True)


if __name__ == "__main__":
    main()
