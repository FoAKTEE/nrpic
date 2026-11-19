#!/usr/bin/env python3
"""Test T1 of tracks/core/JOURNAL-oblate.md: the oblate spheroid component of nrpic_cf
against the reference potential, on processors.

    cf_check.py --exe ATHENA [--out DIR] [--parts a,b,c]

P1a  psi^4 of the adm dump against (1 - Phi_N)^4 at every cell, for three shapes, to the
     rounding of the single-precision dump.  References: the function phi_N of
     tracks/core/verify/oblate/oblate_reference.py as it stands on branch core/nrpic
     (read with git show into the output directory; not written by this package), the
     defining integrals by quadrature at random points, the closed form of the sphere,
     and the Python twin nrpic.spheroid.OblateSpheroid.
P1b  without matter the Hamiltonian monitor is the Ricci scalar: 32 pi rho_N psi^-5
     inside, 0 outside, away from the surface; oblate case and prolate control.
P1c  with the sampled particles: sum m/psi(x_p) = M (Python), the mesh integral of
     E psi^5 and of H psi^5/(16 pi), the mean and rms of H in the core s < 0.8; oblate
     data and prolate control.
Writes cf_check.json and figs/cf_check_{psi,ham,id}.{png,pdf} of this directory.
"""
import argparse
import importlib.util
import json
import math
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "python"))
sys.path.insert(0, os.path.join(WT, "athenak", "vis", "python"))
import bin_convert  # noqa: E402
from nrpic import io as nio  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402
from nrpic.spheroid import OblateSpheroid, ProlateSpheroid  # noqa: E402

REF_BRANCH = "core/nrpic"
REF_PATH = "tracks/core/verify/oblate/oblate_reference.py"
Q = math.sqrt(1.0 - 0.81)      # b/a at e = 0.9


def run(exe, rundir, inp, args):
    os.makedirs(rundir, exist_ok=True)
    with open(os.path.join(rundir, "athena.log"), "w") as log:
        p = subprocess.run([exe, "-i", inp, "-d", rundir] + args, cwd=rundir,
                           stdout=log, stderr=subprocess.STDOUT)
    if p.returncode != 0:
        raise RuntimeError(f"{rundir}: exit status {p.returncode}")


def load(rundir, var):
    """Fields of the first dump of `var` as flat arrays over all MeshBlocks, with the
    cell centres and the cell volumes."""
    out = os.path.join(rundir, "bin")
    f = sorted(x for x in os.listdir(out) if f".{var}." in x)[0]
    d = bin_convert.read_binary(os.path.join(out, f))
    X, Y, Z, V = [], [], [], []
    for g in d["mb_geometry"]:
        nx, ny, nz = d["nx1_out_mb"], d["nx2_out_mb"], d["nx3_out_mb"]
        # the writer stores x1min, x1max, x2min, x2max, x3min, x3max of the block
        # (athenak/src/outputs/binary.cpp)
        dx, dy, dz = (g[1] - g[0]) / nx, (g[3] - g[2]) / ny, (g[5] - g[4]) / nz
        x = g[0] + (np.arange(nx) + 0.5) * dx
        y = g[2] + (np.arange(ny) + 0.5) * dy
        z = g[4] + (np.arange(nz) + 0.5) * dz
        zz, yy, xx = np.meshgrid(z, y, x, indexing="ij")
        X.append(xx.ravel())
        Y.append(yy.ravel())
        Z.append(zz.ravel())
        V.append(np.full(xx.size, dx * dy * dz))
    fields = {k: np.concatenate([np.asarray(b).ravel() for b in v])
              for k, v in d["mb_data"].items()}
    return (np.concatenate(X), np.concatenate(Y), np.concatenate(Z), np.concatenate(V),
            fields)


def reference_module(out):
    """oblate_reference.py of branch core/nrpic, written into the output directory."""
    blob = subprocess.run(["git", "-C", WT, "rev-parse", f"{REF_BRANCH}:{REF_PATH}"],
                          capture_output=True, text=True, check=True).stdout.strip()
    src = subprocess.run(["git", "-C", WT, "show", f"{REF_BRANCH}:{REF_PATH}"],
                         capture_output=True, text=True, check=True).stdout
    path = os.path.join(out, "oblate_reference_core_nrpic.py")
    with open(path, "w") as f:
        f.write(src)
    spec = importlib.util.spec_from_file_location("oblate_reference_core_nrpic", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, blob


def ulp32(v):
    return np.spacing(np.abs(v).astype(np.float32)).astype(np.float64)


def part_a(exe, out, ref, res):
    inp = os.path.join(WT, "problems", "tests", "oblate_cf.athinput")
    small = ["mesh/nx1=64", "mesh/nx2=64", "mesh/nx3=64", "mesh/x1min=-8", "mesh/x1max=8",
             "mesh/x2min=-8", "mesh/x2max=8", "mesh/x3min=-8", "mesh/x3max=8"]
    cases = {
        "e09": dict(a=10.0, b=10.0 * Q, args=[]),
        "e03": dict(a=2.0, b=2.0 * math.sqrt(1.0 - 0.09), args=small),
        "sphere": dict(a=3.0, b=3.0, args=small),
    }
    rng = np.random.default_rng(20261119)
    keep = {}
    for name, c in cases.items():
        a, b = c["a"], c["b"]
        rd = os.path.join(out, "P1a", name)
        run(exe, rd, inp, c["args"] + [f"problem/comp0_a={a!r}", f"problem/comp0_b={b!r}"])
        x, y, z, vol, fld = load(rd, "adm")
        p4 = fld["adm_psi4"]
        e = math.sqrt(max(0.0, 1.0 - (b / a) ** 2))
        twin = OblateSpheroid(e, a)
        psi_twin = twin.psibar(x, y, z)
        r = np.sqrt(x * x + y * y + z * z)
        if name == "sphere":
            psi_ref = 1.0 + np.where(r < a, 0.5 * (3.0 - r * r / (a * a)) / (2.0 * a),
                                     0.5 / r)
            refname = "closed form of the homogeneous sphere"
        else:
            psi_ref = 1.0 - ref.phi_N(x, y, z, a, b)[0]
            refname = f"phi_N of {REF_PATH} ({REF_BRANCH})"
        p4_ref = psi_ref ** 4
        d = np.abs(p4.astype(np.float64) - p4_ref)
        bound = 0.5 * ulp32(p4_ref) + 1e-12
        psi_dump = p4.astype(np.float64) ** 0.25
        # where the series of the component is used: q = c/w < 0.3
        lam = twin.lam(x, y, z)
        q = twin.c / np.sqrt(b * b + lam)
        s2 = twin.s2(x, y, z)
        # quadrature of the defining integrals at random cells
        idx = rng.choice(len(x), size=200, replace=False)
        dq = 0.0
        for k in idx:
            if a == b:
                continue
            I, Ja, Jb = ref.IJ_quad(float(lam[k]), a, b)
            psi_q = 1.0 + 0.375 * (I - (x[k] ** 2 + y[k] ** 2) * Ja - z[k] ** 2 * Jb)
            dq = max(dq, abs(float(psi_twin[k]) - psi_q) / (psi_q - 1.0))
        res["P1a"][name] = dict(
            a=a, b=b, e=e, cells=int(len(x)), reference=refname,
            cells_inside=int(np.sum(s2 <= 1.0)), cells_series=int(np.sum(q < 0.3)),
            cells_closed_form_outside=int(np.sum((q >= 0.3) & (s2 > 1.0))),
            max_abs_diff_psi4=float(d.max()),
            max_diff_over_ulp32=float((d / ulp32(p4_ref)).max()),
            cells_above_bound=int(np.sum(d > bound)),
            max_abs_diff_psi=float(np.abs(psi_dump - psi_ref).max()),
            max_rel_diff_u_twin_vs_reference=float(
                np.max(np.abs(psi_twin - psi_ref) / (psi_ref - 1.0))),
            max_rel_diff_u_twin_vs_quadrature_200pts=dq,
            u_min=float((psi_ref - 1.0).min()), u_max=float((psi_ref - 1.0).max()),
            passed=bool(np.sum(d > bound) == 0))
        print(f"P1a {name}: {res['P1a'][name]}", flush=True)
        keep[name] = (x, y, z, psi_dump, psi_ref, twin)
    # figure: psi along the two axes (cells nearest the axes) and the difference
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(2, 3, figsize=(fs.FULL_WIDTH, 4.6), sharex="col",
                           gridspec_kw=dict(height_ratios=[2, 1]))
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.11, top=0.93, wspace=0.30,
                        hspace=0.06)
    for j, name in enumerate(("e09", "e03", "sphere")):
        x, y, z, pd, pr, tw = keep[name]
        h = np.min(np.abs(x[np.abs(x) > 0]))
        for lab, sel, coord, col in (
                ("along $x$", (np.abs(y - h) < 1e-9) & (np.abs(z - h) < 1e-9), x,
                 fs.PAL["blue"]),
                ("along $z$", (np.abs(x - h) < 1e-9) & (np.abs(y - h) < 1e-9), z,
                 fs.PAL["red"])):
            o = np.argsort(coord[sel])
            cc = coord[sel][o]
            ax[0, j].plot(cc, pr[sel][o], color="k", lw=1.0, ls="--")
            ax[0, j].plot(cc, pd[sel][o], color=col, ls="none", marker="o", ms=2.0,
                          label=lab)
            ax[1, j].plot(cc, (pd[sel][o] - pr[sel][o]) * 1e8, color=col, lw=1.0)
        for v in (tw.a, tw.b):
            for axx in (ax[0, j], ax[1, j]):
                axx.axvline(v, **fs.MASK_LINE)
                axx.axvline(-v, **fs.MASK_LINE)
        ax[0, j].set_title({"e09": "$e=0.9$, $a=10M$", "e03": "$e=0.3$, $a=2M$",
                            "sphere": "sphere, $a=b=3M$"}[name], fontsize=10)
        ax[1, j].set_xlabel("coordinate along the axis [$M$]", labelpad=-1)
        ax[1, j].axhline(0.0, color="k", lw=0.6)
    ax[0, 0].set_ylabel(r"$\psi$ (points: code; dashed: reference)")
    ax[1, 0].set_ylabel(r"$10^8(\psi_{\rm code}-\psi_{\rm ref})$")
    ax[0, 0].legend(fontsize=8)
    fs.save(fig, os.path.join(HERE, "figs", "cf_check_psi"))
    plt.close(fig)


def clean_masks(x, y, z, a, b, dx):
    """Cells whose difference stencils (three cells each way, also diagonally) lie
    entirely inside, or entirely outside, the spheroid."""
    h = 3.0 * dx
    inside = np.ones(len(x), bool)
    for sx in (-h, h):
        for sy in (-h, h):
            for sz in (-h, h):
                inside &= ((x + sx) ** 2 + (y + sy) ** 2) / a ** 2 + (z + sz) ** 2 / b ** 2 < 1.0
    # outside: the confocal spheroid lam whose distance from the surface is at least
    # 5.5 cells everywhere (the distance is smallest at the end of the long axis)
    amax = max(a, b)
    lam_min = (amax + 5.5 * dx) ** 2 - amax ** 2
    R2, z2 = x * x + y * y, z * z
    B = a * a + b * b - R2 - z2
    C = a * a * b * b - R2 * b * b - z2 * a * a
    lam = 0.5 * (-B + np.sqrt(B * B - 4.0 * C))
    outside = (C < 0) & (lam > lam_min)
    return inside, outside


def part_b(exe, out, res):
    inp = os.path.join(WT, "problems", "tests", "oblate_cf.athinput")
    fine = ["mesh/nx1=128", "mesh/nx2=128", "mesh/nx3=128", "mesh/x1min=-16",
            "mesh/x1max=16", "mesh/x2min=-16", "mesh/x2max=16", "mesh/x3min=-16",
            "mesh/x3max=16"]
    cases = {"oblate": (10.0, 10.0 * Q, OblateSpheroid(0.9, 10.0)),
             "prolate": (10.0 * Q, 10.0, ProlateSpheroid(0.9, 10.0))}
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.1))
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.15, top=0.92, wspace=0.26)
    for j, (name, (a, b, sph)) in enumerate(cases.items()):
        rd = os.path.join(out, "P1b", name)
        run(exe, rd, inp, fine + [f"problem/comp0_a={a!r}", f"problem/comp0_b={b!r}"])
        x, y, z, vol, fld = load(rd, "con")
        H = fld["con_H"].astype(np.float64)
        dx = vol[0] ** (1.0 / 3.0)
        psi = sph.psibar(x, y, z)
        Hin = 32.0 * math.pi * sph.rhoN * psi ** -5
        inside, outside = clean_masks(x, y, z, a, b, dx)
        # leave out the cells whose stencils reach the ghost cells of the outer faces
        edge = (np.abs(x) > 16.0 - 4 * dx) | (np.abs(y) > 16.0 - 4 * dx) | \
               (np.abs(z) > 16.0 - 4 * dx)
        outside &= ~edge
        rel_in = np.abs(H[inside] / Hin[inside] - 1.0)
        Hc = float(32.0 * math.pi * sph.rhoN * sph.c0 ** -5)
        res["P1b"][name] = dict(
            a=a, b=b, dx=dx, cells_inside=int(inside.sum()), cells_outside=int(outside.sum()),
            H_centre_expected=Hc,
            max_rel_diff_inside=float(rel_in.max()),
            max_abs_H_outside_over_H_centre=float(np.abs(H[outside]).max() / Hc),
            max_abs_H_edge_over_H_centre=float(np.abs(H[edge]).max() / Hc),
            passed=bool(rel_in.max() < 1e-5 and np.abs(H[outside]).max() / Hc < 1e-5))
        print(f"P1b {name}: {res['P1b'][name]}", flush=True)
        h = np.min(np.abs(x[np.abs(x) > 0]))
        for lab, sel, coord, col in (
                ("along $x$", (np.abs(y - h) < 1e-9) & (np.abs(z - h) < 1e-9), x,
                 fs.PAL["blue"]),
                ("along $z$", (np.abs(x - h) < 1e-9) & (np.abs(y - h) < 1e-9), z,
                 fs.PAL["red"])):
            o = np.argsort(coord[sel])
            ax[j].plot(coord[sel][o], H[sel][o] / Hc, color=col, lw=1.0, marker="o",
                       ms=1.5, label=lab + " (code)")
            ref = np.where(sph.s2(x[sel][o], y[sel][o], z[sel][o]) <= 1.0, Hin[sel][o], 0.0)
            ax[j].plot(coord[sel][o], ref / Hc, color="k", lw=1.0, ls="--")
        ax[j].set_title(f"{name}, $dx=M/4$, no matter", fontsize=10)
        ax[j].set_xlabel("coordinate along the axis [$M$]", labelpad=-1)
        ax[j].set_xlim(-16, 16)
    ax[0].set_ylabel(r"$H/(32\pi\rho_N\psi_c^{-5})$")
    ax[0].legend(fontsize=8, loc="lower center")
    fs.save(fig, os.path.join(HERE, "figs", "cf_check_ham"))
    plt.close(fig)


def part_c(exe, out, res):
    inp = os.path.join(WT, "problems", "tests", "oblate_id.athinput")
    mk = os.path.join(WT, "problems", "ic", "make_ic.py")
    ic = os.path.join(out, "P1c", "ic")
    os.makedirs(ic, exist_ok=True)
    for model, opt in (("oblate", ["--a", "10"]), ("prolate", ["--b", "10"])):
        subprocess.run([sys.executable, mk, model, "--e", "0.9"] + opt +
                       ["--N", "10000", "--seed", "1", "--out", ic], check=True,
                       stdout=subprocess.DEVNULL)
    cases = {
        "oblate": (10.0, 10.0 * Q, OblateSpheroid(0.9, 10.0),
                   os.path.join(ic, "oblate_e0p9_a10_N10000_s1.nrp"), []),
        "prolate": (10.0 * Q, 10.0, ProlateSpheroid(0.9, 10.0),
                    os.path.join(ic, "prolate_e0p9_b10_N10000_s1.nrp"),
                    ["refined_region1/x1min=-5", "refined_region1/x1max=5",
                     "refined_region1/x2min=-5", "refined_region1/x2max=5",
                     "refined_region1/x3min=-11", "refined_region1/x3max=11"]),
    }
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.1))
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.15, top=0.92, wspace=0.26)
    for j, (name, (a, b, sph, nrp, extra)) in enumerate(cases.items()):
        xp, up, mp, spc = nio.read_nrp(nrp)
        psi_p = sph.psibar(xp[:, 0], xp[:, 1], xp[:, 2])
        S = float(np.sum(mp / psi_p))
        rd = os.path.join(out, "P1c", name)
        run(exe, rd, inp, extra + [f"problem/comp0_a={a!r}", f"problem/comp0_b={b!r}",
                                   f"particles/particle_file={nrp}"])
        x, y, z, vol, fa = load(rd, "adm")
        _, _, _, _, fc = load(rd, "con")
        _, _, _, _, ft = load(rd, "tmunu")
        psi = fa["adm_psi4"].astype(np.float64) ** 0.25
        H = fc["con_H"].astype(np.float64)
        E = ft["tmunu_E"].astype(np.float64)
        s = np.sqrt(sph.s2(x, y, z))
        dxf = vol.min() ** (1.0 / 3.0)
        fine = vol < 1.5 * vol.min()
        core = (s < 0.8) & fine
        int_E5 = float(np.sum(E * psi ** 5 * vol))
        int_E6 = float(np.sum(E * psi ** 6 * vol))
        int_H5 = float(np.sum(H * psi ** 5 * vol) / (16.0 * math.pi))
        mean_H = float(np.sum(H[core] * vol[core]) / np.sum(vol[core]))
        mean_E = float(np.sum(E[core] * vol[core]) / np.sum(vol[core]))
        rms_H = float(np.sqrt(np.mean(H[core] ** 2)))
        ncell = len(mp) * dxf ** 3 / sph.V       # particles per finest cell (uniform)
        n_core = int(np.sum(np.sqrt(sph.s2(xp[:, 0], xp[:, 1], xp[:, 2])) < 0.8))
        res["P1c"][name] = dict(
            a=a, b=b, particles=int(len(mp)), sum_m=float(mp.sum()),
            M_rest_continuum=sph.rest_mass(),
            sum_m_over_psi=S, sum_m_over_psi_minus_M=S - sph.M,
            mesh_int_E_psi5=int_E5, mesh_int_E_psi5_minus_sum=int_E5 - S,
            mesh_int_E_psi6=int_E6, mesh_int_E_psi6_minus_sum_m=int_E6 - float(mp.sum()),
            mesh_int_H_psi5_over_16pi=int_H5,
            dx_finest=dxf, core_cells=int(core.sum()), particles_in_core=n_core,
            core_mean_H_over_16piE=mean_H / (16.0 * math.pi * mean_E),
            core_mean_E=mean_E, core_E_continuum_centre=float(2.0 * sph.rhoN * sph.c0 ** -5),
            core_rms_H_over_16piE=rms_H / (16.0 * math.pi * mean_E),
            particles_per_finest_cell=ncell,
            core_rms_H_over_16piE_times_sqrt_ncell=rms_H / (16.0 * math.pi * mean_E)
            * math.sqrt(ncell))
        print(f"P1c {name}: {res['P1c'][name]}", flush=True)
        # profile of E and of the continuum density in shells of s (finest cells)
        edges = np.linspace(0.0, 1.4, 29)
        sc = 0.5 * (edges[1:] + edges[:-1])
        Eb = np.array([np.sum((E * vol)[fine & (s >= lo) & (s < hi)])
                       / max(np.sum(vol[fine & (s >= lo) & (s < hi)]), 1e-300)
                       for lo, hi in zip(edges[:-1], edges[1:])])
        Hb = np.array([np.sum((H * vol)[fine & (s >= lo) & (s < hi)])
                       / max(np.sum(vol[fine & (s >= lo) & (s < hi)]), 1e-300)
                       for lo, hi in zip(edges[:-1], edges[1:])])
        Ec = np.where(s <= 1.0, 2.0 * sph.rhoN * psi ** -5, 0.0)
        Ecb = np.array([np.sum((Ec * vol)[fine & (s >= lo) & (s < hi)])
                        / max(np.sum(vol[fine & (s >= lo) & (s < hi)]), 1e-300)
                        for lo, hi in zip(edges[:-1], edges[1:])])
        E0 = 2.0 * sph.rhoN * sph.c0 ** -5
        ax[j].plot(sc, Ecb / E0, color="k", lw=1.0, ls="--", label="continuum")
        ax[j].plot(sc, Eb / E0, color=fs.PAL["red"], marker="o", ms=2.5, lw=1.0,
                   label="deposited $E$")
        ax[j].plot(sc, -Hb / (16 * math.pi * E0), color=fs.PAL["blue"], marker="s",
                   ms=2.5, lw=1.0, label=r"$-H/16\pi$ (shell mean)")
        ax[j].axvline(0.8, **fs.MASK_LINE)
        ax[j].set_title(f"{name}, $10^4$ particles, $dx=M/4$", fontsize=10)
        ax[j].set_xlabel("spheroidal radius $s$", labelpad=-1)
    ax[0].set_ylabel(r"shell mean / $2\rho_N\psi_c^{-5}$")
    ax[0].legend(fontsize=8)
    fs.save(fig, os.path.join(HERE, "figs", "cf_check_id"))
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", os.getcwd()))
    ap.add_argument("--parts", default="a,b,c")
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    os.makedirs(os.path.join(HERE, "figs"), exist_ok=True)
    ref, blob = reference_module(out)
    res = {"exe": a.exe, "reference": dict(branch=REF_BRANCH, path=REF_PATH, blob=blob),
           "P1a": {}, "P1b": {}, "P1c": {}}
    parts = a.parts.split(",")
    if "a" in parts:
        part_a(a.exe, out, ref, res)
    if "b" in parts:
        part_b(a.exe, out, res)
    if "c" in parts:
        part_c(a.exe, out, res)
    with open(os.path.join(out, "cf_check.json"), "w") as f:
        json.dump(res, f, indent=1)
    print("wrote", os.path.join(out, "cf_check.json"))


if __name__ == "__main__":
    main()
