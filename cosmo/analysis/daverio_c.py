"""Random field from a power spectrum over a thousandfold expansion (cosmo/PLAN.md, C5;
test C of Daverio, Dirian & Mitsou, arXiv:1904.07841, Figs. 9 to 15).

    python3 daverio_c.py [--runs runs/cosmo] [--box 704] [--cases dav_c704_n32,...]

From the constraint statistics: cell means of the relative and absolute constraints
against redshift (z = 1001 / a - 1 with a = 1 at the start of the run), and the ratio
between successive resolutions. From the field dumps at z = 1000, 100, 10, 1, 0: the
power spectrum of E / <E> - 1 in shells of the fundamental wave number against linear
theory, P(t, k) = [(3 + k^2/H_c^2(t)) / (3 + k^2/H_c^2(0))]^2 P(0, k), with the
measured initial spectrum of the same run (the factor is squared; the formula printed in
the source paper is not, its figure is). Wave numbers in h/Mpc: k_code x 0.333716.
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
sys.path.insert(0, os.path.join(REPO, "python"))
sys.path.insert(0, os.path.join(REPO, "cosmo", "ic"))
from nrpic import figstyle as fs  # noqa: E402
import random_field as rf  # noqa: E402

HC0 = 0.0105535          # conformal Hubble rate at the start, h/Mpc
LUNIT = (1.0/1001.0)/0.0105535


def read_field(path):
    with open(path, "rb") as f:
        magic = f.read(8)
        assert magic in (b"NRFIELD1", b"NRFIELD2")
        t = np.fromfile(f, dtype=np.float64, count=1)[0]
        n = np.fromfile(f, dtype=np.int64, count=3)
        nc = int(n[0]*n[1]*n[2])
        e = np.fromfile(f, dtype=np.float32, count=nc).astype(np.float64)
        chi = np.fromfile(f, dtype=np.float32, count=nc).astype(np.float64)
    # stored with the first index fastest: [k, j, i] in C order
    e = e.reshape(int(n[2]), int(n[1]), int(n[0])).transpose(2, 1, 0)
    chi = chi.reshape(int(n[2]), int(n[1]), int(n[0])).transpose(2, 1, 0)
    return t, e, chi


def load(rundir, box):
    f = os.path.join(rundir, "east.cstat.hst")
    if not os.path.exists(f):
        return None
    c = np.loadtxt(f)
    a = (1.0 + 0.5*c[:, 0])**2
    out = {"z": 1001.0/a - 1.0, "a": a, "Hr": c[:, 11], "Mr": c[:, 15],
           "H": 0.5*c[:, 9]/LUNIT**2, "M": c[:, 13]/LUNIT**2, "finite": bool(np.isfinite(c).all())}
    spec = []
    for i in range(6):
        p = os.path.join(rundir, f"east.field.{i:05d}.bin")
        if not os.path.exists(p):
            continue
        t, e, chi = read_field(p)
        n = e.shape[0]
        delta = e/e.mean() - 1.0
        k, pk, nm = rf.measure_power(delta, box, nbins=None)
        spec.append({"t": float(t), "a": float((1.0 + 0.5*t)**2), "k": k, "P": pk, "nm": nm,
                     "rms": float(delta.std()), "delta": delta})
    out["spec"] = spec
    return out


def linear_field(delta0, box, a):
    """The initial contrast evolved by linear theory to the scale factor a (1 at the
    start): every Fourier mode multiplied by (3 + k^2/H_c^2(t)) / (3 + k^2/H_c^2(0)),
    H_c(t) = H_c(0)/sqrt(a). Mode by mode, because the factor varies strongly across a
    shell of wave numbers."""
    n = delta0.shape[0]
    k1 = 2.0*np.pi*np.fft.fftfreq(n, d=box/n)
    kr = 2.0*np.pi*np.fft.rfftfreq(n, d=box/n)
    KX, KY, KZ = np.meshgrid(k1, k1, kr, indexing="ij")
    x = (KX**2 + KY**2 + KZ**2)/HC0**2
    return np.fft.irfftn(np.fft.rfftn(delta0)*(3.0 + x*a)/(3.0 + x), s=(n,)*3, axes=(0, 1, 2))


VARIANT = {"": "", "k": "", "cic": "linear cloud", "pcs": "cubic cloud",
           "k2": "damping rate 2", "cfl": "step 0.05 of the cell",
           "comp": "compensated after the division", "dcomp": "compensated"}


def label(case):
    """Legend entry from the name of a run, dav_<box>_n<cells>[_<variant>]."""
    parts = case.split("_")
    n = next(p for p in parts if p.startswith("n") and p[1:].isdigit())
    var = "_".join(parts[parts.index(n) + 1:])
    text = VARIANT.get(var, var)
    return rf"$N_g = {n[1:]}$" + (f", {text}" if text else "")


def main():
    args = sys.argv[1:]
    opt = {args[i][2:]: args[i+1] for i in range(0, len(args) - 1, 2)}
    runs = opt.get("runs", os.path.join(REPO, "runs", "cosmo"))
    box = float(opt.get("box", "704"))
    cut = float(opt.get("cut", "220"))
    tag = opt.get("tag", f"c{box:g}")
    cases = opt.get("cases", ",".join(f"dav_{tag}_n{n}" for n in (32, 64, 128, 256))).split(",")
    data = {c: load(os.path.join(runs, c), box) for c in cases}
    data = {c: d for c, d in data.items() if d is not None}
    if not data:
        sys.exit("no run found")
    fs.use_style()
    cols = [fs.PAL[c] for c in ("blue", "green", "red", "orange", "yellow")] + ["0.4", "k"]
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.085, right=0.985, bottom=0.17, top=0.95, wspace=0.36)
    summ = {}
    kcut = 2.0*np.pi/cut
    for col, (c, d) in zip(cols, data.items()):
        lab = label(c)
        zz = np.maximum(d["z"], 1e-3)
        axs[0].loglog(zz[1:], d["Hr"][1:], color=col, label=lab)
        axs[1].loglog(zz[1:], d["Mr"][1:], color=col)
        s = {"finite": d["finite"], "z_end": float(d["z"][-1])}
        for zref in (100.0, 10.0, 1.0, 0.02):
            i = int(np.argmin(np.abs(d["z"] - zref)))
            s[f"z{zref:g}"] = {"Hr": float(d["Hr"][i]), "Mr": float(d["Mr"][i]),
                               "H": float(d["H"][i]), "M": float(d["M"][i])}
        sp = d["spec"]
        if len(sp) > 1:
            k0 = sp[0]["k"]
            for q in sp[1:]:
                zq = 1001.0/q["a"] - 1.0
                _, pan, _ = rf.measure_power(linear_field(sp[0]["delta"], box, q["a"]), box,
                                             nbins=None)
                dev = np.abs(q["P"] - pan)/pan
                # amplitude and phase: the field against its linear prediction
                lin = linear_field(sp[0]["delta"], box, q["a"])
                q["corr"] = float((q["delta"]*lin).sum()/np.sqrt((q["delta"]**2).sum()
                                                               * (lin**2).sum()))
                keep = k0 <= kcut*1.0001
                half = k0 <= 0.5*kcut
                s[f"spec_z{zq:.3g}"] = {"rms": q["rms"], "corr": q["corr"],
                                        "max_dev_below_half_cut": float(dev[half].max()),
                                        "max_dev_below_cut": float(dev[keep].max()),
                                        "dev": [float(v) for v in dev[keep]],
                                        "k": [float(v) for v in k0[keep]]}
                if abs(zq - 10.0) < 1.0:
                    axs[2].semilogy(k0[keep], dev[keep], color=col, marker="o", ms=2.5, lw=0.8)
        summ[c] = s
    axs[0].set_xlabel(r"redshift $z$")
    axs[0].set_ylabel(r"mean of $H_r$")
    axs[0].invert_xaxis()
    axs[0].legend(frameon=False, loc="upper left")
    axs[1].set_xlabel(r"redshift $z$")
    axs[1].set_ylabel(r"mean of $M_r$")
    axs[1].invert_xaxis()
    axs[2].set_xlabel(r"$k$ ($h$/Mpc)")
    axs[2].set_ylabel(r"$|P/P_{\rm lin} - 1|$ at $z = 10$")
    figdir = os.path.join(HERE, "figs")
    fs.save(fig, os.path.join(figdir, f"daverio_{tag}"))
    with open(os.path.join(HERE, f"daverio_{tag}.json"), "w") as fp:
        json.dump(summ, fp, indent=1)
    names = list(summ)
    for c, s in summ.items():
        print(f"== {c}: finite {s['finite']}, ends at z = {s['z_end']:.3f}")
        for zref in ("100", "10", "1", "0.02"):
            v = s[f"z{zref}"]
            print(f"   z = {zref:>4}: mean H_r {v['Hr']:.2e}  M_r {v['Mr']:.2e}  H {v['H']:.2e}  "
                  f"|M| {v['M']:.2e}")
        for key, v in s.items():
            if key.startswith("spec_"):
                print(f"   {key}: rms of the contrast {v['rms']:.3e}; correlation with the "
                      f"linear field {v['corr']:.5f}; largest |P/P_lin - 1| below "
                      f"half the cut {v['max_dev_below_half_cut']:.2e}, below the cut "
                      f"{v['max_dev_below_cut']:.2e}")
    for a, b in zip(names[:-1], names[1:]):
        r = {z: (summ[a][f"z{z}"]["Hr"]/summ[b][f"z{z}"]["Hr"],
                 summ[a][f"z{z}"]["Mr"]/summ[b][f"z{z}"]["Mr"]) for z in ("100", "10", "1")}
        print(f"ratio {a} / {b} (H_r, M_r) at z = 100, 10, 1: "
              + "  ".join(f"{v[0]:.1f}, {v[1]:.1f}" for v in r.values()))
    print(os.path.join(figdir, f"daverio_{tag}.png"))


if __name__ == "__main__":
    main()
