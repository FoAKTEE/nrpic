"""First execution of the Szekeres test in AthenaK (DESIGN.md sections 3-5, JOURNAL entry 3).

For each N: the field file and the particle file of the reference model (eps = 0.1) on the
periodic box [-8, 8]^3 (szekeres/codeid.py), then the processor executable of release
core-v0.3 with inputs/szekeres_geodesic.athinput (geodesic slicing, cloud-in-cell, one
particle per cell), then the comparison of the field dumps (tau = 0, 10, 20, 30, 40) with
the exact solution at the same cells: trace K = Khat + 2 Theta_Z4c against -Theta, the
energy density E against rho, chi against psi^-4 (rho(t)/rho(t_i))^(2/3), and the
constraint monitor, by region of the shell label (core r < 2.4, shell, outside r > 6).
Writes code_geodesic.json and fig_code_geodesic.

    python3 scripts/run_code_geodesic.py [--N 32 64] [--tlim 40]
"""

import argparse
import math
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

import numpy as np  # noqa: E402

from szekeres.confmap import ConformalMap  # noqa: E402
from szekeres import codeid  # noqa: E402

EXE = "/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena"
DECK = os.path.join(common.PKG, "inputs", "szekeres_geodesic.athinput")
LH = 8.0


def read_field(path):
    with open(path, "rb") as f:
        magic = f.read(8)
        t = np.frombuffer(f.read(8), "<f8")[0]
        n1, n2, n3 = np.frombuffer(f.read(24), "<i8")
        nc = int(n1 * n2 * n3)
        E = np.frombuffer(f.read(4 * nc), "<f4").astype(float)
        chi = np.frombuffer(f.read(4 * nc), "<f4").astype(float)
        out = dict(t=float(t), E=E, chi=chi)
        if magic == b"NRFIELD2":
            for k in ("H", "Mx", "My", "Mz", "Khat", "Theta", "alpha"):
                out[k] = np.frombuffer(f.read(8 * nc), "<f8").copy()
    shp = (int(n3), int(n2), int(n1))
    # file order: x fastest -> array [k, j, i]; return [i, j, k]
    return {k: (v.reshape(shp).transpose(2, 1, 0) if isinstance(v, np.ndarray) else v) for k, v in out.items()}


def launch(N, rdir, szk, cm, tlim):
    d = os.path.join(rdir, f"N{N}")
    os.makedirs(d, exist_ok=True)
    f = codeid.slice_on_mesh(cm, N, LH)
    codeid.write_nrcosmo(os.path.join(d, "fields.bin"), f)
    npart = codeid.write_particles(os.path.join(d, "particles.nrp"), f)
    np.savez_compressed(os.path.join(d, "slice_t0.npz"), **{k: v for k, v in f.items()})
    cmd = [EXE, "-i", DECK, "-d", d, f"mesh/nx1={N}", f"mesh/nx2={N}", f"mesh/nx3={N}",
           f"problem/id_file={os.path.join(d, 'fields.bin')}",
           f"particles/particle_file={os.path.join(d, 'particles.nrp')}", f"time/tlim={tlim}"]
    log = open(os.path.join(d, "athena.log"), "w")
    p = subprocess.Popen(cmd, cwd=d, stdout=log, stderr=subprocess.STDOUT,
                         env=dict(os.environ, OMP_NUM_THREADS="1"))
    return dict(N=N, dir=d, proc=p, slice=f, npart=npart, cmd=cmd, t0=time.time())


def compare(job, szk):
    d, f = job["dir"], job["slice"]
    files = sorted(fn for fn in os.listdir(d) if fn.startswith("szk.field.") and fn.endswith(".bin"))
    regions = {"core": f["r"] < 2.4, "shell": (f["r"] >= 2.4) & (f["r"] <= 6.0), "outside": f["r"] > 6.0}
    rho0 = f["rho"]
    rows = []
    for fn in files:
        F = read_field(os.path.join(d, fn))
        tau = F["t"]
        ex = szk.fields(szk.t_i + tau, f["r"], f["bn"])
        K_code = F["Khat"] + 2 * F["Theta"]
        K_ex = -ex["Theta"]
        chi_ex = f["psi"] ** -4 * (ex["rho"] / rho0) ** (2.0 / 3.0)
        a = (1 + tau / szk.t_i) ** (2.0 / 3.0)
        H_t = szk.H / a ** 1.5
        rho_b = szk.rho_b / a ** 3
        row = dict(file=fn, tau=tau)
        for name, m in regions.items():
            row[name] = dict(
                K_rel_max=float(np.max(np.abs(K_code - K_ex)[m] / np.abs(K_ex[m]))),
                K_err_rms_over_H=float(np.sqrt(np.mean(((K_code - K_ex)[m] / H_t) ** 2))),
                E_rel_max=float(np.max(np.abs(F["E"] - ex["rho"])[m] / ex["rho"][m])),
                E_rel_rms=float(np.sqrt(np.mean(((F["E"] - ex["rho"]) / ex["rho"])[m] ** 2))),
                chi_rel_max=float(np.max(np.abs(F["chi"] - chi_ex)[m] / chi_ex[m])),
                H_over_16pirho_rms=float(np.sqrt(np.mean((F["H"][m] / (16 * math.pi * rho_b)) ** 2))),
                M_over_16pirho_rms=float(np.sqrt(np.mean(((F["Mx"] ** 2 + F["My"] ** 2 + F["Mz"] ** 2)[m])) / (16 * math.pi * rho_b))),
                alpha_dev_max=float(np.max(np.abs(F["alpha"][m] - 1.0))))
        rows.append(row)
        row["_arrays"] = dict(K_code=K_code, K_ex=K_ex, E=F["E"], rho=ex["rho"], chi=F["chi"], chi_ex=chi_ex)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--N", type=int, nargs="+", default=[32, 64])
    ap.add_argument("--tlim", type=float, default=40.0)
    a = ap.parse_args()
    rdir = common.run_dir("code_geodesic")
    _, szk = common.models()
    cm = ConformalMap(szk)
    jobs = [launch(N, rdir, szk, cm, a.tlim) for N in a.N]
    for j in jobs:
        j["exit"] = j["proc"].wait()
        j["wall"] = time.time() - j["t0"]
        print(f"N = {j['N']}: exit {j['exit']}, {j['wall']:.0f} s", flush=True)
    out = dict(run_id=common.run_id(), commit=common.git_commit(), exe=EXE, deck=DECK, LH=LH, model=szk.summary(),
               runs={})
    allrows = {}
    for j in jobs:
        rows = compare(j, szk) if j["exit"] == 0 or any(fn.startswith("szk.field.") for fn in os.listdir(j["dir"])) else []
        allrows[j["N"]] = rows
        out["runs"][j["N"]] = dict(exit=j["exit"], wall_s=j["wall"], particles=j["npart"], cmd=" ".join(j["cmd"]),
                                   dumps=[{k: v for k, v in r.items() if k != "_arrays"} for r in rows])
        for r in rows:
            print(j["N"], f"tau = {r['tau']:.3f}", {k: r[k] for k in ("core", "shell", "outside")}, flush=True)
    common.dump(os.path.join(rdir, "code_geodesic.json"), out)

    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use_style()
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.08, right=0.985, bottom=0.16, top=0.9, wspace=0.36)
    cols = {N: c for N, c in zip(sorted(allrows), fs.SERIES)}
    for N, rows in allrows.items():
        if not rows:
            continue
        tau = [r["tau"] for r in rows]
        for region, ls in (("core", ":"), ("shell", "-"), ("outside", "--")):
            axs[0].semilogy(tau, [max(r[region]["K_rel_max"], 1e-16) for r in rows], ls=ls, marker="o", ms=3,
                            color=cols[N], label=f"N = {N}, {region}")
            axs[1].semilogy(tau, [max(r[region]["E_rel_max"], 1e-16) for r in rows], ls=ls, marker="o", ms=3,
                            color=cols[N])
            axs[2].semilogy(tau, [max(r[region]["H_over_16pirho_rms"], 1e-16) for r in rows], ls=ls, marker="o",
                            ms=3, color=cols[N])
    axs[0].set_ylabel(r"$\max |K - K_{\rm exact}|/|K_{\rm exact}|$")
    axs[1].set_ylabel(r"$\max |E - \rho_{\rm exact}|/\rho_{\rm exact}$")
    axs[2].set_ylabel(r"rms $H/(16\pi\bar\rho)$")
    for ax in axs:
        ax.set_xlabel(r"proper time $\tau$")
    axs[0].legend(fontsize=6.5, ncol=1, loc="lower right")
    common.save_fig(fig, "fig_code_geodesic", rdir)
    # profile along the x axis at the last dump of the largest N
    Nmax = max(N for N in allrows if allrows[N])
    rows = allrows[Nmax]
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.16, top=0.9, wspace=0.3)
    j = [jb for jb in jobs if jb["N"] == Nmax][0]
    xc = j["slice"]["x"]
    mid = Nmax // 2
    for r, c in zip(rows, fs.series_colors(len(rows))):
        A = r["_arrays"]
        axs[0].plot(xc, A["K_ex"][:, mid, mid], color=c, lw=2.5, alpha=0.35)
        axs[0].plot(xc, A["K_code"][:, mid, mid], color=c, lw=1.0, ls="--", label=f"$\\tau = {r['tau']:.1f}$")
        axs[1].plot(xc, A["rho"][:, mid, mid], color=c, lw=2.5, alpha=0.35)
        axs[1].plot(xc, A["E"][:, mid, mid], color=c, lw=1.0, ls="--")
    axs[0].set_xlabel("x (code coordinate, y and z at the cell next to 0)")
    axs[0].set_ylabel(r"$K$ (thick: exact, dashed: AthenaK)")
    axs[0].legend(fontsize=7)
    axs[1].set_yscale("log")
    axs[1].set_xlabel("x")
    axs[1].set_ylabel(r"$E$ and $\rho$")
    common.save_fig(fig, "fig_code_geodesic_profiles", rdir)
    print("written", rdir)


if __name__ == "__main__":
    main()
