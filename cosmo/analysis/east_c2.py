"""Comparison of the relativistic and Newtonian runs of the single-wavelength problem
(cosmo/PLAN.md, C2; East, Wojtak & Pretorius, arXiv:1908.05683, Figs. 1 to 3).

    python3 east_c2.py [--runs runs/cosmo] [--n 64] [--deltas 0.0025,0.005,0.01,0.05]

For each amplitude with both runs present:
  observer density contrast at the underdensity and the overdensity against the
  proper-time scale factor of the observer there;
  coordinate distance of the fiducial observers from the point of maximum density
  against their own proper-time scale factor, and the scale factor at which each first
  crosses the overdensity (gauge independent);
  difference of the coordinate distances between the two gravities against the
  Newtonian infall speed.
Writes figures to cosmo/analysis/figs and the numbers to cosmo/analysis/east_c2.json.
"""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "cosmo", "ic"))
sys.path.insert(0, os.path.join(REPO, "python"))
sys.path.insert(0, HERE)
from nrpic import figstyle as fs  # noqa: E402
from delta_obs import gr_probes  # noqa: E402

L, H0 = 4.0, 1.0
XPK = 0.25*L
SHOWN = (1.0/32.0, 1.0/16.0, 1.0/8.0, 1.0/4.0)   # initial distances over L, as the source


def a_of_tau(tau):
    return (1.0 + 1.5*H0*tau)**(2.0/3.0)


def gr_fiducial(rundir, base="east"):
    """Tracks of the fiducial observers of a relativistic run: dict with t (nt), x
    (nt, nfid, 3), tau (nt, nfid), and the initial lattice coordinate and axis."""
    fid = np.load(os.path.join(rundir, "fiducial.npz"))
    nfid = len(fid["axis"])
    tr = np.fromfile(os.path.join(rundir, base + ".traj.bin")).reshape(-1, 8)
    tm = np.fromfile(os.path.join(rundir, base + ".trajmet.bin")).reshape(-1, 17)
    n = min(len(tr), len(tm))
    tr, tm = tr[:n], tm[:n]
    tag = tr[:, 1].astype(int)
    keep = tag < nfid
    tr, tm, tag = tr[keep], tm[keep], tag[keep]
    # records of one output share the time; restarts may repeat times: keep the last
    times, inv = np.unique(tr[:, 0], return_inverse=True)
    nt = len(times)
    x = np.full((nt, nfid, 3), np.nan)
    tau = np.full((nt, nfid), np.nan)
    x[inv, tag] = tr[:, 2:5]
    tau[inv, tag] = tm[:, 12]
    return {"t": times, "x": x, "tau": tau, "q": fid["q"], "axis": fid["axis"]}


def distances(x, q, axis):
    """Signed coordinate distance from the peak along the line of each observer,
    unwrapped in time, positive on the side where the observer starts."""
    nt, nf, _ = x.shape
    d = np.empty((nt, nf))
    for j in range(nf):
        ax = axis[j]
        s = x[:, j, ax] - XPK
        s0 = q[j, ax] - XPK
        # unwrap: start from the lattice coordinate, follow increments modulo L
        inc = np.diff(np.concatenate([[q[j, ax]], x[:, j, ax]]))
        inc -= L*np.round(inc/L)
        s = s0 + np.cumsum(inc)
        d[:, j] = s*np.sign(s0) if s0 != 0.0 else s
    return d


def first_crossing(a_p, d):
    """Scale factor of the first passage through zero distance (linear interpolation);
    nan if none."""
    ok = np.isfinite(d) & np.isfinite(a_p)
    a_p, d = a_p[ok], d[ok]
    i = np.flatnonzero((d[:-1] > 0.0) & (d[1:] <= 0.0))
    if len(i) == 0:
        return np.nan
    i = i[0]
    return float(a_p[i] + (a_p[i+1] - a_p[i])*d[i]/(d[i] - d[i+1]))


def rise(a_p, dobs, level):
    """Scale factor at which delta_obs first reaches the level."""
    ok = np.isfinite(dobs)
    a_p, dobs = a_p[ok], dobs[ok]
    i = np.flatnonzero((dobs[:-1] < level) & (dobs[1:] >= level))
    if len(i) == 0:
        return np.nan
    i = i[0]
    f = (np.log(1.0 + level) - np.log(1.0 + dobs[i]))/(np.log(1.0 + dobs[i+1])
                                                      - np.log(1.0 + dobs[i]))
    return float(a_p[i]*(a_p[i+1]/a_p[i])**f)


def below(a_p, d, level):
    """Scale factor at which the distance first falls below the level."""
    ok = np.isfinite(d) & np.isfinite(a_p)
    a_p, d = a_p[ok], d[ok]
    i = np.flatnonzero((d[:-1] > level) & (d[1:] <= level))
    if len(i) == 0:
        return np.nan
    i = i[0]
    return float(a_p[i] + (a_p[i+1] - a_p[i])*(d[i] - level)/(d[i] - d[i+1]))


def load(runs, delta, n, gsuf="", nsuf=""):
    tagd = f"{delta:g}"
    gdir = os.path.join(runs, f"east_d{tagd}_n{n}{gsuf}")
    nfile = os.path.join(runs, f"newton_d{tagd}_n{n}{nsuf}", "newton.npz")
    if not (os.path.exists(os.path.join(gdir, "east.nrpic.hst")) and os.path.exists(nfile)):
        return None
    g, h = gr_probes(gdir)
    f = gr_fiducial(gdir)
    # a run that stops (collapse of the lapse at the overdensity) is cut where the
    # first particle is lost or a probe value stops being finite
    bad = (h["np"] < h["np"][0]) | ~np.isfinite(h["alpha_probe"]) \
        | ~np.isfinite(h["E_probe"]) | (h["alpha_min"] <= 0.0)
    if bad.any():
        t_end = h["time"][np.argmax(bad)] - 1e-9
        keep = g["t"] < t_end
        g = {k: v[keep] for k, v in g.items()}
        kf = f["t"] < t_end
        for k in ("t", "x", "tau"):
            f[k] = f[k][kf]
        g["t_stop"] = t_end
    nw = dict(np.load(nfile))
    # the Newtonian dictionary ends where 1 + 2 psi_N turns negative: cut all Newtonian
    # histories at the last time with a finite observer density at the overdensity
    okn = np.isfinite(nw["delta_obs_0"]) & np.isfinite(nw["t_p_0"])
    if not okn.all():
        m = int(np.argmin(okn))
        nt = len(nw["tau"])
        nw = {k: (v[:m] if isinstance(v, np.ndarray) and v.ndim >= 1 and len(v) == nt
                  else v) for k, v in nw.items()}
        nw["stopped"] = True
    return {"g": g, "f": f, "nw": nw, "gdir": gdir}


def main():
    args = sys.argv[1:]
    opt = {args[i][2:]: args[i+1] for i in range(0, len(args) - 1, 2)}
    runs = opt.get("runs", os.path.join(REPO, "runs", "cosmo"))
    n = int(opt.get("n", "64"))
    deltas = [float(s) for s in opt.get("deltas", "0.0025,0.005,0.01,0.05").split(",")]
    suffix = opt.get("suffix", "")
    gsuf, nsuf = opt.get("gr-suffix", ""), opt.get("newton-suffix", "")
    # wavelength of the perturbation (box size), default four initial Hubble radii
    global L, XPK
    L = float(opt.get("L", L))
    XPK = 0.25*L
    data = {d: load(runs, d, n, gsuf, nsuf) for d in deltas}
    data = {d: v for d, v in data.items() if v is not None}
    if not data:
        sys.exit("no pair of runs found")
    fs.use_style()
    figdir = os.path.join(HERE, "figs")
    os.makedirs(figdir, exist_ok=True)
    cols = [fs.PAL["blue"], fs.PAL["green"], fs.PAL["orange"], fs.PAL["red"]]
    summary = {}

    # ---- observer density contrast at the two probes
    fig, axs = plt.subplots(2, 1, figsize=(fs.COLUMN_WIDTH, 5.4))
    fig.subplots_adjust(left=0.17, right=0.97, bottom=0.09, top=0.98, hspace=0.24)
    for c, (d, v) in zip(cols, data.items()):
        g, nw = v["g"], v["nw"]
        s = summary.setdefault(f"{d:g}", {})
        for ax, i, sign in ((axs[0], 1, -1.0), (axs[1], 0, 1.0)):
            ax.plot(g[f"a_p_{i}"], sign*g[f"delta_obs_{i}"], color=c,
                    label=rf"$\bar\delta = {d:g}$")
            ok = np.isfinite(nw[f"delta_obs_{i}"])
            ax.plot(nw[f"a_p_{i}"][ok], sign*nw[f"delta_obs_{i}"][ok], color=c, ls="--",
                    lw=0.9)
        # numbers
        ok = np.isfinite(nw["delta_obs_1"])
        apn = nw["a_p_1"][ok]
        gi = np.interp(apn, g["a_p_1"], g["delta_obs_1"])
        sel = apn <= g["a_p_1"][-1]
        dif = (gi[sel] - nw["delta_obs_1"][ok][sel])/(1.0 + nw["delta_obs_1"][ok][sel])
        s["underdensity_max_rel_diff_of_density"] = float(np.abs(dif).max())
        s["underdensity_delta_obs_end_gr"] = float(g["delta_obs_1"][-1])
        s["a_p_end_gr_underdensity"] = float(g["a_p_1"][-1])
        s["a_p_end_gr_overdensity"] = float(g["a_p_0"][-1])
        for lev in (1.0, 10.0, 100.0):
            ag = rise(g["a_p_0"], g["delta_obs_0"], lev)
            an = rise(nw["a_p_0"], nw["delta_obs_0"], lev)
            s[f"overdensity_a_p_at_{lev:g}"] = {"gr": ag, "newton": an,
                                               "gr_over_newton": ag/an}
        s["overdensity_max_gr"] = float(np.nanmax(g["delta_obs_0"]))
        s["overdensity_max_newton"] = float(np.nanmax(nw["delta_obs_0"]))
        s["newton_valid_to_a"] = float(nw["a"][np.isfinite(nw["delta_obs_0"])][-1])
    axs[0].set_xscale("log")
    axs[0].set_ylabel(r"$-\delta_{\rm obs}$, underdensity")
    axs[0].set_ylim(0.0, 1.0)
    axs[1].set_xscale("log")
    axs[1].set_yscale("log")
    axs[1].set_ylim(1e-2, 3e4)
    axs[1].set_ylabel(r"$\delta_{\rm obs}$, overdensity")
    axs[1].set_xlabel(r"$a_p$")
    axs[0].legend(frameon=False, loc="upper left")
    axs[1].plot([], [], color="0.3", label="general relativity")
    axs[1].plot([], [], color="0.3", ls="--", lw=0.9, label="Newtonian")
    h, lab = axs[1].get_legend_handles_labels()
    axs[1].legend(h[-2:], lab[-2:], frameon=False, loc="lower right")
    fs.save(fig, os.path.join(figdir, "east_delta_obs" + suffix))
    plt.close(fig)

    # ---- fiducial observers
    nd = len(data)
    fig, axs = plt.subplots(2, nd, figsize=(fs.FULL_WIDTH, 4.4), sharex="col",
                            squeeze=False)
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.11, top=0.93, hspace=0.0,
                        wspace=0.24)
    axcol = [fs.PAL["red"], fs.PAL["green"], fs.PAL["blue"]]
    fig3, ax3 = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH, 2.8))
    fig3.subplots_adjust(left=0.17, right=0.97, bottom=0.17, top=0.96)
    for k, (c, (d, v)) in enumerate(zip(cols, data.items())):
        f, nw = v["f"], v["nw"]
        s = summary[f"{d:g}"]
        dg = distances(f["x"], f["q"], f["axis"])
        apg = a_of_tau(f["tau"])
        dn = distances(np.mod(nw["x"], L), nw["q_fid"], nw["axis_fid"])
        apn = a_of_tau(nw["t_p"])
        q0 = np.abs(np.array([f["q"][j, f["axis"][j]] - XPK for j in range(len(f["axis"]))]))
        h = L/n
        # observers shown: initial lattice distances of 4, 8, 12, 16 cells on the + side
        show = []
        cross = []
        for j in range(len(f["axis"])):
            s0 = f["q"][j, f["axis"][j]] - XPK
            if s0 <= 0.0 or s0 > 0.25*L + 1e-9:
                continue
            ag, an = first_crossing(apg[:, j], dg[:, j]), first_crossing(apn[:, j], dn[:, j])
            cross.append({"axis": int(f["axis"][j]), "q0": float(s0), "gr": ag,
                          "newton": an,
                          "gr_10": below(apg[:, j], dg[:, j], 0.1*dg[0, j]),
                          "newton_10": below(apn[:, j], dn[:, j], 0.1*dn[0, j])})
            if any(abs(s0 - fr*L) < 1e-9 for fr in SHOWN):
                show.append(j)
        s["crossings"] = cross
        for j in show:
            cc = axcol[f["axis"][j]]
            axs[0, k].plot(apg[:, j], dg[:, j], color=cc, lw=0.8)
            ok = np.isfinite(apn[:, j])
            axs[1, k].plot(apn[ok, j], dn[ok, j], color=cc, lw=0.8)
        a_first = np.nanmin([c_["newton"] for c_ in cross] + [c_["gr"] for c_ in cross])
        a_last = min(np.nanmax(apg), 2.2*a_first) if np.isfinite(a_first) else np.nanmax(apg)
        for ax in axs[:, k]:
            ax.axhline(0.0, **fs.THIN)
            ax.set_xlim(1.0, a_last)
            ax.set_ylim(-0.3, 1.1)
        axs[0, k].set_title(rf"$\bar\delta = {d:g}$", fontsize=8)
        axs[1, k].set_xlabel(r"$a_p$")
        # difference of distance against Newtonian infall speed, up to the first
        # Newtonian crossing, for the x line
        for j in show:
            if f["axis"][j] != 0:
                continue
            an_c = first_crossing(apn[:, j], dn[:, j])
            ok = np.isfinite(apn[:, j])
            if np.isfinite(an_c):
                ok &= apn[:, j] <= an_c
            vinf = np.abs(nw["v"][:, j, 0])
            dgi = np.interp(apn[ok, j], apg[:, j], dg[:, j], right=np.nan)
            ax3.plot(vinf[ok], np.abs(dgi - dn[ok, j])/L, color=c, lw=0.8,
                     ls=("-", ":", "--", "-.")[show.index(j) % 4])
    axs[0, 0].set_ylabel("distance, general relativity")
    axs[1, 0].set_ylabel("distance, Newtonian")
    fs.save(fig, os.path.join(figdir, "east_splash" + suffix))
    plt.close(fig)
    ax3.set_xscale("log")
    ax3.set_yscale("log")
    ax3.set_ylim(1e-6, 0.3)
    ax3.set_xlabel("Newtonian infall speed")
    ax3.set_ylabel(r"$|d_{\rm GR} - d_{\rm N}|/L$")
    for c, d in zip(cols, data):
        ax3.plot([], [], color=c, label=rf"$\bar\delta = {d:g}$")
    ax3.legend(frameon=False, loc="upper left")
    fs.save(fig3, os.path.join(figdir, "east_rel_eff" + suffix))
    plt.close(fig3)

    with open(os.path.join(HERE, "east_c2" + suffix + ".json"), "w") as fp:
        json.dump(summary, fp, indent=1)

    # ---- printed summary
    for d, s in summary.items():
        print(f"== delta = {d}: relativistic run ends at a_p = {s['a_p_end_gr_underdensity']:.2f} "
              f"(underdensity), {s['a_p_end_gr_overdensity']:.2f} (overdensity); Newtonian "
              f"dictionary valid to a = {s['newton_valid_to_a']:.2f}")
        print(f"   underdensity: largest |rho_GR - rho_N| / rho_N = "
              f"{s['underdensity_max_rel_diff_of_density']:.3e}; delta_obs at the end "
              f"{s['underdensity_delta_obs_end_gr']:.4f}")
        for lev in ("1", "10", "100"):
            r = s[f"overdensity_a_p_at_{lev}"]
            print(f"   overdensity reaches {lev:>3}: a_p = {r['gr']:.3f} (GR) {r['newton']:.3f} "
                  f"(N), ratio {r['gr_over_newton']:.4f}")
        print(f"   overdensity maximum: {s['overdensity_max_gr']:.1f} (GR) "
              f"{s['overdensity_max_newton']:.1f} (N)")
        cr = [c for c in s["crossings"] if np.isfinite(c["gr"]) and np.isfinite(c["newton"])]
        for ax in range(3):
            line = "  ".join(f"{c['q0']:.3f}:{c['gr']:.2f}/{c['newton']:.2f}"
                             f"({c['gr']/c['newton'] - 1.0:+.3f})"
                             for c in cr if c["axis"] == ax
                             and any(abs(c["q0"] - fr*L) < 1e-9 for fr in SHOWN))
            print(f"   first crossing, axis {ax} (q0: GR/N (rel. diff.)): {line}")
        for fr in SHOWN:
            sel = [c for c in s["crossings"] if abs(c["q0"] - fr*L) < 1e-9
                   and np.isfinite(c["gr_10"]) and np.isfinite(c["newton_10"])]
            if sel:
                g10 = np.mean([c["gr_10"] for c in sel])
                n10 = np.mean([c["newton_10"] for c in sel])
                print(f"   distance below a tenth, d0 = L/{1.0/fr:.0f} (mean of {len(sel)} "
                      f"directions): a_p = {g10:.2f} (GR) {n10:.2f} (N), ratio {g10/n10:.4f}")
    print(os.path.join(figdir, "east_delta_obs" + suffix + ".png"))
    print(os.path.join(figdir, "east_splash" + suffix + ".png"))
    print(os.path.join(figdir, "east_rel_eff" + suffix + ".png"))


if __name__ == "__main__":
    main()
