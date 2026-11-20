#!/usr/bin/env python3
"""Linear reference of the window scan (package tracks/E-stoch-inf/window, step 1).

For each window (s, sigma) of window_lib.WINDOWS and each case (USR 128^3 with
nmax2 = 1024; slow roll 64^3 with nmax2 = 256), from the background and the
Mukhanov-Sasaki mode of every shell of the cut (code time, from the mode file at N*,
usr_lib.Reference; ODEs and lattice sums only, decision 0010):

  - W_k(N*) and W_k'(N*): what the initial slice of the code holds per shell (the slice
    places W(N*) R and W' R + W R', scalar_field_slice.cpp:128-143 at a58e95b);
  - crossing e-folds of every shell: W = 0.05, 0.5, 0.95; class against the USR phase
    (crossed before the onset, during USR, after);
  - linear prediction of the coarse-grained R at N_f per shell, ensemble power
    Delta = k^3 W^2 |R|^2/(2 pi^2) and its shift against the baseline;
  - the one-point variance of W R on the lattice in time, ensemble
    (sum over modes of 2 L^-3 |W R|^2) and the realisation of the runs
    (2 L^-3 |W R alpha|^2 with the amplitudes of seed 20261115);
  - the linear shift between windows during the passage.

    python3 window_reference.py --out DIR [--case usr sr]
Writes DIR/reference_<case>.json, DIR/shells_<case>.csv, DIR/fig/*.png.
"""
import argparse
import csv
import json
import os
import time

import numpy as np

import window_lib as wl


def crossing_cN(cN, lnaH, k, s, sigma, w):
    """e-folds where W = w: s ln(sigma a H/k) = artanh(2 w - 1)."""
    target = np.log(k / sigma) + np.arctanh(2.0 * w - 1.0) / s
    if target < lnaH[0] - 1e-12:
        return float("-inf")          # in before N* (in the slice)
    if target <= lnaH[0]:
        return float(cN[0])
    if target >= lnaH[-1]:
        return float("inf")
    return float(np.interp(target, lnaH, cN))


def run_case(case, out):
    c = wl.CASES[case]
    n2s, r0, dr0 = wl.shells(case)
    ks = np.sqrt(n2s.astype(float))
    modes = wl.Modes(c["nmesh"], c["nmax2"])
    mult = np.bincount(modes.shell_of, minlength=modes.shell_n2.size)
    assert np.array_equal(modes.shell_n2, n2s)
    alpha = modes.alpha()
    t = np.unique(np.concatenate([np.linspace(0.0, c["tlim"], 1001), [c["tlim"]]]))
    t0 = time.time()
    ref = wl.reference(case, ks**2, r0, dr0, t)
    wall = time.time() - t0
    nt = t.size
    lna = np.array([ref.at(i)["lna"] for i in range(nt)])
    hub = np.array([ref.at(i)["H"] for i in range(nt)])
    cN = lna
    lnaH = lna + np.log(hub)
    R = np.array([ref.at(i)["R"] for i in range(nt)])          # (nt, nshell)
    L3 = wl.L_BOX**-3
    res = dict(case=case, nmesh=c["nmesh"], nmax2=c["nmax2"], nshell=int(n2s.size),
               nmodes=int(modes.M), tlim=c["tlim"], ode_wall_s=wall,
               modefile=os.path.relpath(c["modefile"], wl.TRACK), windows={})
    shell_rows = {"n2": n2s, "k": ks, "mult": mult,
                  "Delta_MS_Nf": ks**3 * np.abs(R[-1])**2 / (2 * np.pi**2)}
    var_t = {}
    for name, (s, sig) in wl.WINDOWS.items():
        W = wl.window(ks[None, :], np.exp(lna)[:, None], hub[:, None], s, sig)
        w0 = W[0]
        st0 = ref.at(0)
        ch = np.cosh(s * np.log(sig * st0["a"] * st0["H"] / ks))
        w1 = 0.5 * s * st0["H"] * (1.0 - st0["eps1"]) / ch**2
        var_ens = 2.0 * L3 * (mult[None, :] * W**2 * np.abs(R)**2).sum(axis=1)
        WRm = W[:, modes.shell_of] * R[:, modes.shell_of] * alpha[None, :]
        var_real = 2.0 * L3 * (np.abs(WRm)**2).sum(axis=1)
        var_t[name] = (var_ens, var_real)
        cr = {w: np.array([crossing_cN(cN, lnaH, k, s, sig, w) for k in ks])
              for w in (0.05, 0.5, 0.95)}
        cls = np.where(cr[0.5] < wl.USR_ON, "before", np.where(cr[0.5] < wl.USR_OFF, "during",
                                                               "after"))
        shell_rows[f"W0_{name}"] = w0
        shell_rows[f"Wdot0_{name}"] = w1
        shell_rows[f"cN05_{name}"] = cr[0.05]
        shell_rows[f"cN50_{name}"] = cr[0.5]
        shell_rows[f"cN95_{name}"] = cr[0.95]
        shell_rows[f"class_{name}"] = cls
        shell_rows[f"WNf_{name}"] = W[-1]
        # slice at N*: variance it holds and how many shells are in
        var_slice = 2.0 * L3 * (mult * w0**2 * np.abs(r0)**2).sum()
        res["windows"][name] = dict(
            s=s, sigma=sig,
            one_minus_W_Nf_max=float(np.max(1.0 - W[-1])),
            rms_WR_Nf_ensemble=float(np.sqrt(var_ens[-1])),
            rms_WR_Nf_realisation=float(np.sqrt(var_real[-1])),
            rms_WR_Nstar_ensemble=float(np.sqrt(var_ens[0])),
            rms_slice_Nstar_ensemble=float(np.sqrt(var_slice)),
            shells_W0_above_1e_3=int(np.sum(w0 > 1e-3)),
            shells_W0_above_0p5=int(np.sum(w0 > 0.5)),
            W0_first_shells=[float(x) for x in w0[:4]],
            last_crossing_cN=float(cr[0.5][-1]), last_in95_cN=float(cr[0.95][-1]),
            first_crossing_cN=float(cr[0.5][0]),
            shells_cross_before_usr=int(np.sum(cls == "before")),
            kmax_cross_before_usr=float(ks[cls == "before"].max()) if np.any(cls == "before") else 0.0,
            shells_cross_during_usr=int(np.sum(cls == "during")),
            shells_cross_after_usr=int(np.sum(cls == "after")))
    # shifts against the baseline: at N_f and the largest during the passage
    Wb = wl.window(ks[None, :], np.exp(lna)[:, None], hub[:, None], *wl.WINDOWS["b"])
    for name, (s, sig) in wl.WINDOWS.items():
        W = wl.window(ks[None, :], np.exp(lna)[:, None], hub[:, None], s, sig)
        shift_Nf = (W[-1] / Wb[-1])**2 - 1.0
        shell_rows[f"shift_Nf_{name}"] = shift_Nf
        dW = np.abs(W - Wb)       # |ref_w - ref_b| / |R| per shell in time
        imax = np.argmax(dW, axis=0)
        res["windows"][name].update(
            linear_power_shift_Nf_max=float(np.max(np.abs(shift_Nf))),
            max_dW_passage=float(dW.max()),
            cN_of_max_dW_median=float(np.median(cN[imax])),
            var_ratio_to_baseline_at=dict(
                (f"{x:.1f}", float(var_t[name][0][np.argmin(np.abs(cN - x))]
                                   / var_t["b"][0][np.argmin(np.abs(cN - x))]))
                for x in (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, cN[-1])))
    res["cN_end"] = float(cN[-1])
    res["H_end"] = float(hub[-1])
    res["var_time"] = dict(cN=cN[::10].tolist(), **{
        f"{n}_ens": v[0][::10].tolist() for n, v in var_t.items()}, **{
        f"{n}_real": v[1][::10].tolist() for n, v in var_t.items()})
    with open(os.path.join(out, f"reference_{case}.json"), "w") as fp:
        json.dump(res, fp, indent=1)
    keys = list(shell_rows)
    with open(os.path.join(out, f"shells_{case}.csv"), "w", newline="") as fp:
        fp.write(f"# linear reference of the window scan, case {case} "
                 f"({c['nmesh']}^3, nmax2 = {c['nmax2']}); cN = N - N*; "
                 f"W0 = W(N*), class = crossing (W = 1/2) before/during/after USR\n")
        wr = csv.writer(fp)
        wr.writerow(keys)
        for i in range(n2s.size):
            wr.writerow([shell_rows[k][i] if isinstance(shell_rows[k][i], str)
                         else f"{float(shell_rows[k][i]):.10e}" for k in keys])
    return res, dict(cN=cN, lna=lna, hub=hub, R=R, ks=ks, mult=mult, var_t=var_t,
                     shell_rows=shell_rows)


def figures(case, res, d, out):
    import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    cols = dict(zip(wl.WINDOWS, [fs.PAL["blue"], fs.PAL["red"], fs.PAL["orange"],
                                 fs.PAL["green"], "purple"]))
    cN, ks = d["cN"], d["ks"]
    usr = case == "usr"
    # ---- W(cN) for three shells, each window
    fig, ax = plt.subplots(2, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 6.0), sharex=True)
    fig.subplots_adjust(left=0.14, right=0.97, top=0.97, bottom=0.09, hspace=0.08)
    picks = [2.0, 8.0, np.sqrt(float(d["shell_rows"]["n2"][-1]))]
    for x in ax:
        if usr:
            x.axvspan(wl.USR_ON, wl.USR_OFF, color=fs.PAL["yellow"], alpha=0.15, lw=0)
    for name, (s, sig) in wl.WINDOWS.items():
        for ls, kk in zip(("-", "--", ":"), picks):
            j = int(np.argmin(np.abs(ks - kk)))
            W = wl.window(ks[j], np.exp(d["lna"]), d["hub"], s, sig)
            ax[0].plot(cN, W, color=cols[name], ls=ls,
                       label=f"{wl.LABEL[name]}" if ls == "-" else None)
        ve, vr = d["var_t"][name]
        ax[1].semilogy(cN, np.sqrt(ve), color=cols[name], label=wl.LABEL[name])
        ax[1].semilogy(cN, np.sqrt(vr), color=cols[name], ls="--", lw=1.0)
    ax[0].set_ylabel(r"$W_k$")
    ax[0].text(0.02, 0.97, "solid k = 2 dk, dashed 8 dk, dotted %g dk" % picks[2],
               transform=ax[0].transAxes, va="top", fontsize=8)
    ax[0].legend(loc="lower right", fontsize=8)
    ax[1].set_ylabel(r"rms of $W{\cal R}$ (one point)")
    ax[1].text(0.02, 0.97, "solid: ensemble lattice sum; dashed: the realisation of the runs",
               transform=ax[1].transAxes, va="top", fontsize=8)
    ax[1].set_xlabel(r"$N-N_*$")
    ax[1].legend(loc="lower right", fontsize=8)
    fs.save(fig, os.path.join(out, "fig", f"fig_ref_{case}_windows"))
    plt.close(fig)
    # ---- crossings per shell and the slice at N*
    fig, ax = plt.subplots(2, 1, figsize=(fs.COLUMN_WIDTH * 1.6, 6.0), sharex=True)
    fig.subplots_adjust(left=0.14, right=0.97, top=0.97, bottom=0.09, hspace=0.08)
    sr = d["shell_rows"]
    if usr:
        ax[0].axhspan(wl.USR_ON, wl.USR_OFF, color=fs.PAL["yellow"], alpha=0.15, lw=0,
                      label="USR")
    for name in wl.WINDOWS:
        ax[0].plot(ks, np.maximum(sr[f"cN50_{name}"], -1), color=cols[name], label=wl.LABEL[name])
        ax[0].fill_between(ks, np.maximum(sr[f"cN05_{name}"], -1), sr[f"cN95_{name}"],
                           color=cols[name], alpha=0.12, lw=0)
        ax[1].semilogy(ks, np.maximum(sr[f"W0_{name}"], 1e-30), ".", ms=3, color=cols[name],
                       label=wl.LABEL[name])
    ax[0].set_ylabel(r"$N-N_*$ at $W$ = 0.5 (band 0.05-0.95)")
    ax[0].text(0.02, 0.97, "s = 2.5, 5, 10 share the W = 1/2 curve (sigma = 1);\n"
               "shells in at N* are drawn at -1", transform=ax[0].transAxes, va="top",
               fontsize=8)
    ax[0].legend(loc="lower right", fontsize=8)
    ax[1].set_ylabel(r"$W_k(N_*)$ in the initial slice")
    ax[1].set_ylim(1e-20, 2)
    ax[1].set_xlabel(r"$k/dk$")
    ax[1].legend(loc="lower left", fontsize=8)
    fs.save(fig, os.path.join(out, "fig", f"fig_ref_{case}_crossing"))
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--case", nargs="+", default=["usr", "sr"])
    a = ap.parse_args()
    os.makedirs(os.path.join(a.out, "fig"), exist_ok=True)
    summary = {}
    for case in a.case:
        res, d = run_case(case, a.out)
        figures(case, res, d, a.out)
        summary[case] = res["windows"]
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
