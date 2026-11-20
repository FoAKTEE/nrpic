"""Leg F of flrw_conv: scale-factor error of the homogeneous particle FLRW run against
a = (1 + t/2)^2, for meshes 16, 32, 64 and 1, 8, 27 particles per cell, with and without
position noise; constraint histories.

    python3 analyze_f.py <runs.json> [<outdir>]     (default outdir $NRPIC_RUN_DIR)

runs.json maps case names (f_n<N>_p<ppc per direction>_a<0|1|2>) to '<run id>/<name>'.
Writes <outdir>/flrw_f.json and figures fig_f_lattice, fig_f_noise, fig_f_scaling,
fig_f_constraints (PDF and PNG).
"""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import figstyle as fs  # noqa: E402
import flrwlib as fl  # noqa: E402

AREF = (1.5, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0)
MEAS = ("e_alpha", "e_chi", "e_V", "e_K")
LAB = {"e_alpha": r"$|\alpha - a|/a$ (extrema)", "e_chi": r"$|\chi^{-1/2} - a|/a$ (extrema)",
       "e_V": r"$|(V/L^3)^{1/3}/a - 1|$ (volume)", "e_K": r"$|(-\langle K\rangle/3)^{-2/3}/a - 1|$"}


def parse(name):
    _, n, p, a = name.split("_")
    return int(n[1:]), int(p[1:])**3, int(a[1:])


def at(d, key, a0, akey="a"):
    a = d[akey]
    if a0 > a[-1]*1.001 or a0 < a[0]:
        return float("nan")
    return float(np.interp(np.log(a0), np.log(a), np.abs(d[key])))


def noise_part(d, ref, key, akey="a"):
    """|e - e_lattice| on the records of d (lattice interpolated in ln a)."""
    e0 = np.interp(np.log(d[akey]), np.log(ref[akey]), ref[key])
    return np.abs(d[key] - e0)


def main():
    runs = json.load(open(sys.argv[1]))
    out = sys.argv[2] if len(sys.argv) > 2 else os.environ["NRPIC_RUN_DIR"]
    os.makedirs(out, exist_ok=True)
    data = {}
    for name, spec in sorted(runs.items()):
        if not name.startswith("f_"):
            continue
        d = fl.rundir(spec)
        if not os.path.exists(os.path.join(d, "flrw.nrpic.hst")):
            print(f"missing {name}: {d}")
            continue
        data[name] = fl.flrw_errors(d)
    fs.use_style()
    summ = {}
    for name, d in data.items():
        n, nc, ia = parse(name)
        s = {"n": n, "ppc": nc, "noise": ia, "a_end": float(d["a"][-1]),
             "finite": d["finite"], "np_start": float(d["np"][0]), "np_end": float(d["np"][-1]),
             "mass_change": float(d["sum_m"][-1]/d["sum_m"][0] - 1.0)}
        for key in MEAS:
            ak = "ac" if key == "e_chi" else "a"
            s[f"{key}_max"] = float(np.nanmax(np.abs(d[key])))
            s[f"{key}_at"] = {f"{a0:g}": at(d, key, a0, ak) for a0 in AREF}
        for key in ("Hr_max", "Mr_max", "Theta_max", "H_max"):
            s[f"{key}_start"] = float(d[key][0])
            s[f"{key}_max_after_a2"] = float(np.nanmax(d[key][d["ac"] > 2.0]))
            s[f"{key}_end"] = float(d[key][-1])
        s["delta_E_max_at"] = {f"{a0:g}": at(d, "E_max", a0) for a0 in AREF}
        s["delta_E_min_at"] = {f"{a0:g}": at(d, "E_min", a0) for a0 in AREF}
        ref = data.get(f"f_n{n}_p1_a0")
        if ia > 0 and ref is not None:
            for key in MEAS:
                ak = "ac" if key == "e_chi" else "a"
                npart = noise_part(d, ref, key, ak)
                s[f"{key}_noise_at"] = {f"{a0:g}": float(np.interp(np.log(a0), np.log(d[ak]), npart))
                                        if d[ak][0] <= a0 <= d[ak][-1]*1.001 else float("nan")
                                        for a0 in AREF}
                lin = d[ak] <= 30.0
                s[f"{key}_noise_max_a_le_30"] = float(np.nanmax(npart[lin]))
                s[f"{key}_noise_max"] = float(np.nanmax(npart))
        summ[name] = s
    fl.save_json(summ, os.path.join(out, "flrw_f.json"))

    # ---- figure 1: lattices -------------------------------------------------------
    lat = [k for k in data if k.endswith("_a0")]
    cols = dict(zip(sorted(lat, key=lambda k: parse(k)[:2]), fs.series_colors(len(lat))))
    fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.2), sharex=True)
    fig.subplots_adjust(left=0.09, right=0.99, bottom=0.09, top=0.97, wspace=0.28, hspace=0.1)
    for ax, key in zip(axs.flat, MEAS):
        ak = "ac" if key == "e_chi" else "a"
        for name in sorted(lat, key=lambda k: parse(k)[:2]):
            d = data[name]
            n, nc, _ = parse(name)
            ax.loglog(d[ak][1:], np.maximum(np.abs(d[key][1:]), 1e-17), color=cols[name],
                      lw=1.0, ls="-" if nc == 1 else ("--" if nc == 8 else ":"),
                      label=rf"$N={n}$, {nc}/cell")
        ax.axhline(1e-2, **fs.MASK_LINE)
        ax.set_ylabel(LAB[key])
        ax.set_ylim(1e-16, 3e-2)
    for ax in axs[1]:
        ax.set_xlabel(r"$a$")
    axs[0, 0].legend(fontsize=7, loc="lower right", ncol=2)
    axs[0, 0].text(0.03, 0.9, "lattices at rest; grey: $10^{-2}$", transform=axs[0, 0].transAxes,
                   fontsize=7)
    fs.save(fig, os.path.join(out, "fig_f_lattice"))
    plt.close(fig)

    # ---- figure 2: noise runs -----------------------------------------------------
    noisy = sorted([k for k in data if not k.endswith("_a0")], key=lambda k: parse(k))
    colsn = dict(zip(noisy, fs.series_colors(max(len(noisy), 1), "viridis")))
    fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.2), sharex=True)
    fig.subplots_adjust(left=0.09, right=0.99, bottom=0.09, top=0.97, wspace=0.28, hspace=0.1)
    for name in noisy:
        d = data[name]
        n, nc, ia = parse(name)
        lab = rf"$N={n}$, {nc}/cell, A{ia}"
        axs[0, 0].loglog(d["a"][1:], np.abs(d["e_alpha"][1:]), color=colsn[name], lw=1.0, label=lab)
        axs[0, 1].loglog(d["a"][1:], np.abs(d["e_V"][1:]), color=colsn[name], lw=1.0)
        axs[1, 0].loglog(d["a"][1:], np.maximum(np.abs(d["E_max"][1:]), np.abs(d["E_min"][1:])),
                         color=colsn[name], lw=1.0)
        axs[1, 1].loglog(d["ac"], d["Hr_max"], color=colsn[name], lw=1.0)
    for name in lat:
        d = data[name]
        if parse(name)[1] != 1:
            continue
        axs[0, 0].loglog(d["a"][1:], np.abs(d["e_alpha"][1:]), color="grey", lw=0.6, ls="--")
        axs[0, 1].loglog(d["a"][1:], np.abs(d["e_V"][1:]), color="grey", lw=0.6, ls="--")
    for ax in axs.flat:
        ax.axhline(1e-2, **fs.MASK_LINE)
    axs[0, 0].set_ylabel(LAB["e_alpha"])
    axs[0, 1].set_ylabel(LAB["e_V"])
    axs[1, 0].set_ylabel(r"largest $|E a^3/\rho_0 - 1|$")
    axs[1, 1].set_ylabel(r"largest $H_r$")
    for ax in axs[1]:
        ax.set_xlabel(r"$a$")
    axs[0, 0].legend(fontsize=6.5, loc="lower right", ncol=2)
    axs[0, 1].text(0.03, 0.9, "dashed grey: lattices, 1/cell", transform=axs[0, 1].transAxes,
                   fontsize=7)
    fs.save(fig, os.path.join(out, "fig_f_noise"))
    plt.close(fig)

    # ---- figure 3: scaling of the noise-induced part --------------------------------
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.09, right=0.99, bottom=0.16, top=0.95, wspace=0.3)
    mk = {"e_alpha": "o", "e_chi": "s", "e_V": "^", "e_K": "v"}
    a0s = ("3", "30")
    for key in MEAS:
        for j, a0 in enumerate(a0s):
            pts = [(summ[k]["ppc"], summ[k].get(f"{key}_noise_at", {}).get(a0, np.nan))
                   for k in summ if summ[k]["n"] == 32 and summ[k]["noise"] == 2]
            pts = sorted(pts)
            if pts:
                x, y = np.array(pts).T
                axs[0].loglog(x, y, marker=mk[key], ls="-" if j == 0 else ":", lw=0.8,
                              color=fs.SERIES[MEAS.index(key)],
                              label=f"{key[2:]}, a={a0}" if True else None)
            pts = [(summ[k]["n"], summ[k].get(f"{key}_noise_at", {}).get(a0, np.nan))
                   for k in summ if summ[k]["ppc"] == 1 and summ[k]["noise"] == 2]
            pts = sorted(pts)
            if pts:
                x, y = np.array(pts).T
                axs[1].loglog(x, y, marker=mk[key], ls="-" if j == 0 else ":", lw=0.8,
                              color=fs.SERIES[MEAS.index(key)])
    xs = np.array([1.0, 27.0])
    for ax, xs, slopes, lab in ((axs[0], np.array([1.0, 27.0]), (-0.5, -1.0), r"$N_c$"),
                                (axs[1], np.array([16.0, 64.0]), (-1.0, 0.0), r"$N$")):
        y0 = ax.get_ylim()
        for sl in slopes:
            yy = np.sqrt(y0[0]*y0[1])*(xs/xs[0])**sl
            ax.loglog(xs, yy, color="k", lw=0.8, ls="--")
            ax.text(xs[-1], yy[-1], f" slope {sl:g}", fontsize=7, va="center")
        ax.set_xlabel(lab)
    axs[0].set_ylabel("noise part (A2, 32 cells)")
    axs[1].set_ylabel("noise part (A2, 1 per cell)")
    axs[0].legend(fontsize=6, ncol=2, loc="lower left")
    fs.save(fig, os.path.join(out, "fig_f_scaling"))
    plt.close(fig)

    # ---- figure 4: constraints ----------------------------------------------------
    allc = sorted(data, key=lambda k: parse(k))
    colsa = dict(zip(allc, fs.series_colors(len(allc), "viridis")))
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.8))
    fig.subplots_adjust(left=0.07, right=0.99, bottom=0.17, top=0.95, wspace=0.35)
    for name in allc:
        d = data[name]
        n, nc, ia = parse(name)
        for ax, key in zip(axs, ("Hr_max", "Mr_max", "Theta_max")):
            ax.loglog(d["ac"], np.maximum(d[key], 1e-20), color=colsa[name], lw=0.9,
                      ls="-" if ia else "--", label=rf"$N={n}$, {nc}/cell, A{ia}")
    for ax, lab in zip(axs, (r"largest $H_r$", r"largest $M_r$", r"largest $|\Theta|$")):
        ax.set_xlabel(r"$a$")
        ax.set_ylabel(lab)
    axs[2].legend(fontsize=5.5, ncol=2, loc="lower left")
    fs.save(fig, os.path.join(out, "fig_f_constraints"))
    plt.close(fig)

    for name, s in summ.items():
        line = " ".join(f"{k[2:]}={s[f'{k}_max']:.2e}" for k in MEAS)
        print(f"{name}: a_end={s['a_end']:.1f} max {line}; Hr start {s['Hr_max_start']:.1e} "
              f"after a=2 {s['Hr_max_max_after_a2']:.1e} end {s['Hr_max_end']:.1e}")
        if "e_alpha_noise_at" in s:
            print("   noise part alpha:", {k: f"{v:.2e}" for k, v in s["e_alpha_noise_at"].items()})
            print("   noise part V:    ", {k: f"{v:.2e}" for k, v in s["e_V_noise_at"].items()})


if __name__ == "__main__":
    main()
