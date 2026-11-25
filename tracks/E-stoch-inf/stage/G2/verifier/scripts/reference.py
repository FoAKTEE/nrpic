"""V1: own reference (background, landmarks, continuum MS modes at every dump time).

python3 reference.py --out DIR
"""
import argparse
import json
import os
import sys
import time as _t

import numpy as np
from scipy.optimize import brentq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vlib  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    d = vlib.read_deck(vlib.DECK)
    tlim = float(d["time/tlim"])
    res = {"deck": vlib.DECK, "mode_file": vlib.MODEFILE, "tlim": tlim}
    t0 = _t.time()
    ref = vlib.Reference(vlib.DECK, vlib.MODEFILE, tlim, rtol=1e-12)
    res["wall_ref_s"] = _t.time() - t0
    res["nfev"] = int(ref.sol.nfev)
    res["H0"] = float(ref.hubble(ref.phi0, ref.pi0))
    # convergence of the reference itself: rtol 1e-10
    ref10 = vlib.Reference(vlib.DECK, vlib.MODEFILE, tlim, rtol=1e-10)
    R12, _ = ref.modes(tlim)
    R10, _ = ref10.modes(tlim)
    res["ref_self_err_Nf_max_rel"] = float(np.max(np.abs(R12 - R10) / np.abs(R12)))

    # background on a fine grid and landmarks
    tt = np.linspace(0.0, tlim, 200001)
    b = ref.background(tt)
    e2 = b["eps2"] - 3.0
    up = np.nonzero((e2[:-1] < 0) & (e2[1:] >= 0))[0]
    dn = np.nonzero((e2[:-1] > 0) & (e2[1:] <= 0))[0]
    f = lambda t: float(ref.background(t)["eps2"] - 3.0)
    t_on = brentq(f, tt[up[0]], tt[up[0] + 1], xtol=1e-14)
    t_off = brentq(f, tt[dn[0]], tt[dn[0] + 1], xtol=1e-14)
    i2 = int(np.argmax(b["eps2"]))
    i1 = int(np.argmin(b["eps1"]))
    lm = {"USR onset": t_on, "eps2 maximum": float(tt[i2]), "USR end": t_off,
          "eps1 minimum": float(tt[i1]), "N_f": tlim}
    res["landmarks"] = {}
    for k, t in lm.items():
        bb = ref.background(t)
        res["landmarks"][k] = {kk: float(v) for kk, v in bb.items()} | {"t": t}
    res["eps1_min"] = float(b["eps1"][i1])
    # comparison with the track's reference (usr/results/usr_reference.json), not used
    tr = json.load(open(os.path.join(vlib.TRACK, "usr", "results", "usr_reference.json")))
    res["track_ref_cmp"] = {
        "usr_cN_track": tr["usr_cN"], "usr_cN_mine": [res["landmarks"]["USR onset"]["N"],
                                                     res["landmarks"]["USR end"]["N"]],
        "eps1_min_track": tr["eps1_min"], "efolds_end_track": tr["T2_exact"]["efolds_at_t_end"],
        "efolds_end_mine": float(ref.background(tlim)["N"])}

    # lattice rms at N_f (ensemble lattice value)
    mult = vlib.full_multiplicity(4096)
    q2 = ref.q2
    W = ref.window(tlim, np.sqrt(q2.astype(float)))
    var = (mult[q2] * np.abs(W * R12) ** 2).sum() / vlib.L_BOX ** 3
    res["lattice_rms_Nf"] = float(np.sqrt(var))
    res["W_Nf_min"] = float(W.min())
    res["ensemble_lattice_rms_track"] = 0.89366

    # lockstep record of U256ap at N_f
    mp = os.path.join(vlib.run_dir("U256ap"), "usr.sf.00020.modes")
    hdr = open(mp).read().split("\n")[:3]
    rows = np.loadtxt(mp, comments="#")
    qq = rows[:, 0].astype(int)
    Rl = rows[:, 1] + 1j * rows[:, 2]
    idx = vlib.shell_lookup(q2, np.stack([np.sqrt(qq), 0 * qq, 0 * qq], 1).astype(int)) \
        if False else np.searchsorted(q2, qq)
    rel = np.abs(Rl - R12[idx]) / np.abs(R12[idx])
    res["lockstep_vs_ref_Nf"] = {"max_rel": float(rel.max()), "q2_at_max": int(qq[np.argmax(rel)]),
                                 "rel_q2_le_1024_max": float(rel[qq <= 1024].max()),
                                 "header": hdr}
    bN = ref.background(tlim)
    res["background_Nf"] = {k: float(v) for k, v in bN.items()}

    # reference at every dump time of every release run
    times = {}
    for lab in vlib.RUNS:
        times[lab] = [vlib.dump_header(vlib.dump_path(lab, k))["time"] for k in vlib.dumps_of(lab)]
    res["dump_times"] = times
    allt = np.unique(np.concatenate([np.array(v) for v in times.values()]))
    Rt = np.empty((len(allt), len(q2)), dtype=np.complex128)
    Wt = np.empty((len(allt), len(q2)))
    bg = {k: np.empty(len(allt)) for k in ("phi", "Pi", "N", "H", "K", "eps1", "eps2")}
    for i, t in enumerate(allt):
        Rt[i], _ = ref.modes(t)
        Wt[i] = ref.window(t, np.sqrt(q2.astype(float)))
        bb = ref.background(t)
        for k in bg:
            bg[k][i] = bb[k]
    np.savez(os.path.join(a.out, "reference_dumps.npz"), t=allt, q2=q2, R=Rt, W=Wt, **bg)
    np.savez(os.path.join(a.out, "background_fine.npz"), t=tt[::10],
             **{k: v[::10] for k, v in b.items()})
    json.dump(res, open(os.path.join(a.out, "reference.json"), "w"), indent=1)
    out = {k: v for k, v in res.items() if k != "dump_times"}
    print(json.dumps(out, indent=1))

    # figure
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import figstyle
    figstyle.use_style()
    fig, ax = plt.subplots(1, 3, figsize=(11, 3.3))
    cN = b["N"][::10]
    ax[0].semilogy(cN, b["eps1"][::10], label="eps1")
    ax[0].semilogy(cN, np.abs(b["eps2"][::10]), label="|eps2|")
    for k, v in res["landmarks"].items():
        ax[0].axvline(v["N"], lw=0.6, color="0.5")
    ax[0].set_xlabel("cN = N - N*")
    ax[0].legend(fontsize=7)
    ax[0].set_title("background (own), landmarks", fontsize=8)
    ax[1].loglog(np.sqrt(q2), np.abs(R12), lw=0.8)
    ax[1].set_xlabel("k / dk")
    ax[1].set_ylabel("|R_k(N_f)| (code units)")
    ax[1].set_title("own continuum MS at N_f", fontsize=8)
    ax[2].loglog(np.sqrt(qq), rel, ".", ms=1.5)
    ax[2].set_xlabel("k / dk")
    ax[2].set_ylabel("|R_lockstep - R_ref| / |R_ref|")
    ax[2].set_title("lockstep record U256ap vs own, N_f", fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(a.out, "fig_reference.png"), dpi=150)


if __name__ == "__main__":
    main()
