#!/usr/bin/env python3
"""(c) Conservation of the deposited fields on the refined mesh.

Every cycle the particle history gives the proper-volume integrals of the deposited
sources before filtering, int E sqrt(gamma) dV and int S_i sqrt(gamma) dV (columns 9-12),
the same integrals after the nfilter binomial passes (columns 24-27, 27-column history),
and the particle sums sum m W and sum m u_i.  Their differences are shown versus time
(maximum over 5 M bins of 100 cycles) together with the events that could break them:
particles changing refinement level (counted between consecutive snapshots with the
static level map), particles leaving the mesh and particles excised.  The filtered
integrals are also recomputed from the 3D dumps (single precision, exact sqrt(gamma) at
the cell centres) as an independent check (markers).

Figure: figs/deposit_conservation.{pdf,png}
Numbers: results/deposit_conservation.json
"""
import json
import os

import numpy as np
import matplotlib.pyplot as plt

import ct_common as C
from nrpic import figstyle as fs

H = C.dc.H
RUNS = [("mesh_a{a}_n10000_mid", r"$N=10^4$ midpoint", fs.PAL["red"]),
        ("mesh_a{a}_n10000_boris", r"$N=10^4$ Boris", fs.PAL["green"]),
        ("mesh_a{a}_n1000_mid", r"$N=10^3$ midpoint", fs.PAL["yellow"]),
        ("mesh_a{a}_n100_mid", r"$N=10^2$ midpoint", fs.PAL["orange"]),
        ("plunge_a{a}_mid", r"plunging, $N=10^4$", fs.PAL["blue"])]
FLOOR = 1e-17


def post_filter(name, a, hist):
    """Integrals of the filtered fields from the 3D dumps: list of dicts per dump time."""
    out = []
    tcol = hist[:, H["time"]]
    for f in C.bin_files(name, "E3d"):
        fd = C.read_bin(f)
        x, y, z, vol, E = C.bin_cells(fd, "tmunu_E")
        sg = C.sqrt_gamma(x, y, z, a)
        k = int(np.argmin(np.abs(tcol - fd["time"])))
        rec = dict(t=fd["time"], t_hist=float(tcol[k]),
                   int_E=float(np.sum(E * sg * vol)), sum_mW=float(hist[k, H["sum_mw"]]))
        rec["dE"] = rec["int_E"] / rec["sum_mW"] - 1
        out.append(rec)
    for comp, col in (("Sx", "sum_mux"), ("Sy", "sum_muy"), ("Sz", "sum_muz")):
        for f in C.bin_files(name, f"tmunu_{comp}"):
            fd = C.read_bin(f)
            x, y, z, vol, S = C.bin_cells(fd, f"tmunu_{comp}")
            sg = C.sqrt_gamma(x, y, z, a)
            k = int(np.argmin(np.abs(tcol - fd["time"])))
            out.append(dict(t=fd["time"], comp=comp, int_S=float(np.sum(S * sg * vol)),
                            sum_mu=float(hist[k, H[col]]),
                            sum_mW=float(hist[k, H["sum_mw"]])))
    return out


def level_crossings(name):
    """Number of particles whose refinement level changed between consecutive snapshots,
    per unit time, and the snapshot mid-times."""
    h = C.invariant_history(name)
    x = h["x"].astype(float)
    lev = np.where(np.isfinite(x[..., 0]), C.level_of(np.nan_to_num(x)), -1)
    both = (lev[1:] >= 0) & (lev[:-1] >= 0)
    n = np.sum(both & (lev[1:] != lev[:-1]), axis=1)
    dt = np.diff(h["t"])
    return 0.5 * (h["t"][1:] + h["t"][:-1]), n / dt, int(n.sum())


def binned_max(t, v, width=5.0):
    """Maximum of |v| in bins of `width` in t (bin centres, maxima)."""
    edges = np.arange(0.0, t[-1] + width, width)
    k = np.clip(np.searchsorted(edges, t, side="right") - 1, 0, len(edges) - 2)
    out = np.zeros(len(edges) - 1)
    np.maximum.at(out, k, np.abs(v))
    cnt = np.bincount(k, minlength=len(edges) - 1)
    keep = cnt > 0
    return 0.5 * (edges[1:] + edges[:-1])[keep], out[keep]


def boundary_loss(name, a, hist, half=64.0):
    """At each snapshot, the fraction of sum m W that the cloud-in-cell weights put outside
    the domain (particles within half a cell of the outer boundary), and the history
    residual at that time.  Returns arrays (t, predicted, history)."""
    t = hist[:, H["time"]]
    dE = hist[:, H["int_e"]] / hist[:, H["sum_mw"]] - 1
    out = []
    for f in C.snapshots(name):
        ts, x, u, m, tag, sp = C.read_snap(f)
        dx = C.dx_of_level(C.level_of(x))
        near = np.max(np.abs(x), 1) > half - dx
        k = int(np.argmin(np.abs(t - ts)))
        pred = 0.0
        if near.any():
            fin = np.ones(near.sum())
            for d in range(3):
                fin *= np.clip((half - (np.abs(x[near, d]) - dx[near] / 2)) / dx[near], 0, 1)
            W = C.lorentz_W(x[near], u[near], a)
            pred = -np.sum(m[near] * W * (1 - fin)) / hist[k, H["sum_mw"]]
        out.append((ts, pred, dE[k]))
    return np.array(out).reshape(-1, 3)


SC = (("sx", "sum_mux"), ("sy", "sum_muy"), ("sz", "sum_muz"))
MAIN = ("mesh_a{a}_n10000_mid", "plunge_a{a}_mid")


def main():
    fs.use_style()
    res = {}
    fig, axes = plt.subplots(4, 2, figsize=(8.0, 9.0), sharex=True)
    fig.subplots_adjust(left=0.11, right=0.98, bottom=0.06, top=0.93, hspace=0.07,
                        wspace=0.26)
    for j, a in enumerate((0.0, 0.9)):
        for pat, lab, col in RUNS:
            name = pat.format(a=a)
            if not C.exists(name):
                continue
            h = C.history(name)
            t = h[:, H["time"]]
            mw = h[:, H["sum_mw"]]
            has_filt = h.shape[1] > H["int_e_filt"] and np.isfinite(h[:, H["int_e_filt"]]).all()
            dE = h[:, H["int_e"]] / mw - 1
            dS = np.stack([(h[:, H["int_" + c]] - h[:, H[s_]]) / mw for c, s_ in SC], 1)
            tb, vb = binned_max(t, dE)
            axes[0, j].semilogy(tb, np.maximum(vb, FLOOR), color=col, ls="-", label=lab,
                                lw=2.6 if pat == "mesh_a{a}_n10000_mid" else 1.2,
                                zorder=1 if pat == "mesh_a{a}_n10000_mid" else 2)
            rec = dict(max_abs_dE=float(np.max(np.abs(dE))),
                       rms_dE=float(np.sqrt(np.mean(dE ** 2))),
                       max_abs_dS_over_mW=np.max(np.abs(dS), 0).tolist(),
                       has_filtered_columns=bool(has_filt),
                       ncycle=int(h[-1, H["ncycle"]]), np_end=int(h[-1, H["np"]]),
                       n_escaped=int(h[-1, H["n_escaped"]]),
                       n_excised=int(h[-1, H["n_excised"]]),
                       m_escaped=float(h[-1, H["m_escaped"]]),
                       m_excised=float(h[-1, H["m_excised"]]),
                       push_maxit=int(h[:, H["push_maxit"]].max()),
                       push_unconverged_total=int(h[:, H["push_unconverged"]].sum()))
            bl = boundary_loss(name, a, h)
            nz = bl[:, 1] != 0
            rec["boundary_loss_snapshots"] = int(nz.sum())
            if nz.any():
                rec["boundary_loss_max"] = float(np.min(bl[:, 1]))
                rec["boundary_loss_minus_history_max"] = float(np.max(np.abs(bl[:, 1] - bl[:, 2])))
                axes[0, j].semilogy(bl[nz, 0], np.abs(bl[nz, 1]), "x", ms=4, color="k")
            # identity at snapshots with no particle near the outer boundary
            rec["max_abs_dE_snapshots_away_from_boundary"] = (
                float(np.max(np.abs(bl[~nz, 2]))) if (~nz).any() else None)
            bad = np.abs(dE) > 1e-12
            rec["n_cycles_dE_gt_1e-12"] = int(bad.sum())
            m0 = h[0, H["sum_m"]]
            rec["mass_bookkeeping"] = float(np.max(np.abs(
                (h[:, H["sum_m"]] + h[:, H["m_excised"]] + h[:, H["m_escaped"]]) / m0 - 1)))
            if has_filt:
                dEf = h[:, H["int_e_filt"]] / mw - 1
                dSf = np.stack([(h[:, H["int_" + c + "_filt"]] - h[:, H[s_]]) / mw
                                for c, s_ in SC], 1)
                if pat in MAIN:
                    tb, vb = binned_max(t, dEf)
                    axes[0, j].semilogy(tb, np.maximum(vb, FLOOR), color=col, ls="--", lw=1.2)
                rec.update(max_abs_dE_filt=float(np.max(np.abs(dEf))),
                           dE_filt_first=float(dEf[0]), dE_filt_last=float(dEf[-1]),
                           dE_filt_median=float(np.median(dEf)),
                           max_abs_dS_filt_over_mW=np.max(np.abs(dSf), 0).tolist())
            if pat in MAIN:
                for c, ls in zip(range(3), ("-", "--", ":")):
                    tb, vb = binned_max(t, dS[:, c])
                    axes[1, j].semilogy(tb, np.maximum(vb, FLOOR), color=col, ls=ls)
                    if has_filt:
                        tb, vb = binned_max(t, dSf[:, c])
                        axes[2, j].semilogy(tb, np.maximum(vb, FLOOR), color=col, ls=ls)
            # independent check of the filtered integrals from the 3D dumps
            pf = post_filter(name, a, h)
            pE = [p for p in pf if "dE" in p]
            pS = [p for p in pf if "comp" in p]
            if pE and pat in MAIN:
                axes[0, j].semilogy([p["t"] for p in pE],
                                    np.maximum(np.abs([p["dE"] for p in pE]), FLOOR),
                                    "o", ms=3.5, mfc="none", color=col)
            if pE:
                rec["dumps_dE_filt"] = [(p["t"], p["dE"]) for p in pE]
                if has_filt:
                    k = [int(np.argmin(np.abs(t - p["t"]))) for p in pE]
                    rec["dumps_minus_history_dE_filt_max"] = float(np.max(np.abs(
                        np.array([p["dE"] for p in pE]) - dEf[k])))
            if pS:
                rec["dumps_dS_filt_over_mW"] = [
                    (p["t"], p["comp"], (p["int_S"] - p["sum_mu"]) / p["sum_mW"]) for p in pS]
                if pat in MAIN:
                    for comp, mk in (("Sx", "o"), ("Sy", "s"), ("Sz", "^")):
                        q = [p for p in pS if p["comp"] == comp]
                        axes[2, j].semilogy(
                            [p["t"] for p in q],
                            np.maximum(np.abs([(p["int_S"] - p["sum_mu"]) / p["sum_mW"]
                                               for p in q]), FLOOR),
                            mk, ms=3.5, mfc="none", color=col)
            # events
            if pat in MAIN:
                tc, rate, ntot = level_crossings(name)
                axes[3, j].plot(tc, rate, color=col, lw=1.0, drawstyle="steps-mid")
                rec["level_crossings_total"] = ntot
                rem = h[:, H["n_excised"]] + h[:, H["n_escaped"]]
                tb = np.arange(0.0, t[-1] + 5.0, 5.0)
                i1 = np.clip(np.searchsorted(t, tb[1:], side="right") - 1, 0, len(t) - 1)
                i0 = np.clip(np.searchsorted(t, tb[:-1], side="right") - 1, 0, len(t) - 1)
                rr = (rem[i1] - rem[i0]) / 5.0
                if rr.max() > 0:
                    axes[3, j].plot(0.5 * (tb[1:] + tb[:-1]), rr, color=col, lw=1.0,
                                    ls="--", drawstyle="steps-mid")
            res[name] = rec
        axes[0, j].set_title(f"$a = {a}\\,M$")
        axes[3, j].set_xlabel("$t/M$")
        axes[3, j].set_yscale("symlog", linthresh=1.0)
        axes[3, j].set_ylim(0, None)
        axes[0, j].set_xlim(0, C.TLIM)
    axes[0, 0].set_ylabel(r"$|\int E\sqrt{\gamma}\,dV/\sum mW - 1|$")
    axes[1, 0].set_ylabel("$|\\int S_i\\sqrt{\\gamma}\\,dV - \\sum m u_i|$\n"
                          "$/ \\sum m W$, before filter")
    axes[2, 0].set_ylabel("same, after filter")
    axes[3, 0].set_ylabel(r"events per $M$")
    h0, l0 = [], []
    for ax in axes[0]:
        for hh, ll in zip(*ax.get_legend_handles_labels()):
            if ll not in l0:
                h0.append(hh); l0.append(ll)
    L = plt.Line2D
    axes[0, 1].legend([L([], [], color="k", ls="-"), L([], [], color="k", ls="--"),
                       L([], [], color="k", ls="", marker="o", mfc="none"),
                       L([], [], color="k", ls="", marker="x")],
                      ["before filter", "after filter", "after filter, 3D dumps",
                       "cloud weight outside the domain"],
                      loc="center right", fontsize=8)
    axes[1, 1].legend([L([], [], color="k", ls=s_) for s_ in ("-", "--", ":")],
                      ["$x$", "$y$", "$z$"], loc="center right", fontsize=8, ncol=3)
    axes[2, 1].legend([L([], [], color="k", ls="", marker=m, mfc="none") for m in "os^"],
                      ["$x$, 3D dumps", "$y$", "$z$"], loc="lower right", fontsize=8, ncol=3)
    axes[3, 1].legend([L([], [], color="k", ls="-"), L([], [], color="k", ls="--")],
                      ["refinement-level changes", "removals (excised, left mesh)"],
                      loc="upper right", fontsize=8)
    fig.legend(h0, l0, loc="upper center", ncol=5, fontsize=8, frameon=False,
               bbox_to_anchor=(0.54, 1.0))
    fs.save(fig, os.path.join(C.FIGS, "deposit_conservation"))
    plt.close(fig)
    os.makedirs(os.path.join(C.HERE, "results"), exist_ok=True)
    with open(os.path.join(C.HERE, "results", "deposit_conservation.json"), "w") as f:
        json.dump(res, f, indent=1)
    for k, v in res.items():
        print(k, {kk: vv for kk, vv in v.items() if not kk.startswith("dumps_dS")})


if __name__ == "__main__":
    main()
