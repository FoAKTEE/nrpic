#!/usr/bin/env python3
"""Lead's integration checks of the problem generator nrpic_cf (wave 1, core lead).

    cf_checks.py --base ATHENA_BASE --new ATHENA_NEW

Run in an empty directory (runreg.py gives it one). Two parts:

P2  byte regression of existing nrpic_cf set-ups, baseline executable against the
    merged one: problems/tests/regress_cf.athinput (table, Gaussian, spheroid, puncture;
    the table from tracks/core/analysis/mp/make_regress_table.py) and
    problems/tests/cf_table_regress.athinput (Oppenheimer-Snyder table of format 1,
    10^4 lattice particles, one refined level). Compared with
    tracks/core/analysis/id/regress_format1.py (36 never-set bytes of mesh restart
    headers left out).

P5  curvature of combined initial data, merged executable only: a table of format 2
    (expanding ball, problems/ic/make_ball.py) together with a puncture carrying momentum
    and spin.  Three runs that differ only in the curvature terms:
      comb  format-2 table with its KL, KT   + puncture with p, s
      A     format-2 table with its KL, KT   + puncture without p, s
      B     format-2 table with KL = KT = 0  + puncture with p, s
    The conformal factor is the same in all three (same rows u, same code path), so
    K_ij(comb) = K_ij(A) + K_ij(B) must hold to rounding if the two kinds of curvature
    add (commit 0f11630); before that commit K(comb) = K(A).
Writes summary.json and fig_cf_combined.png in the working directory.
"""
import argparse
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "python"))
sys.path.insert(0, os.path.join(WT, "athenak", "vis", "python"))


def run(exe, rundir, inp, args):
    os.makedirs(rundir, exist_ok=True)
    with open(os.path.join(rundir, "athena.log"), "w") as log:
        p = subprocess.run([exe, "-i", inp, "-d", rundir] + args, cwd=rundir,
                           stdout=log, stderr=subprocess.STDOUT)
    if p.returncode != 0:
        raise RuntimeError(f"{rundir}: exit status {p.returncode}")


def compare(a, b):
    p = subprocess.run([sys.executable, os.path.join(WT, "tracks", "core", "analysis", "id",
                                                     "regress_format1.py"), a, b],
                       capture_output=True, text=True)
    return p.returncode, p.stdout


def read_bin(path):
    import bin_convert  # athenak/vis/python
    return bin_convert.read_binary(path)


def kfield(rundir, comp):
    """K_ij component of the first adm snapshot, as one array over all MeshBlocks."""
    out = os.path.join(rundir, "bin")
    f = sorted(x for x in os.listdir(out) if ".adm." in x)[0]
    d = read_bin(os.path.join(out, f))
    return np.concatenate([np.asarray(b).ravel() for b in d["mb_data"]["adm_" + comp]])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--new", required=True)
    a = ap.parse_args()
    top = os.getcwd()
    summary = {"base": a.base, "new": a.new}
    ic = os.path.join(top, "ic")
    os.makedirs(ic, exist_ok=True)

    # ---- P2: byte regression of existing set-ups
    subprocess.run([sys.executable, os.path.join(WT, "tracks", "core", "analysis", "mp",
                                                 "make_regress_table.py"),
                    os.path.join(ic, "regress.tab")], check=True)
    subprocess.run([sys.executable, os.path.join(WT, "problems", "ic", "make_ic.py"), "os",
                    "--N", "10000", "--sampler", "lattice", "--out", ic],
                   check=True, stdout=subprocess.DEVNULL)
    osnrp = sorted(x for x in os.listdir(ic) if x.endswith(".nrp"))[0]
    ostab = osnrp[:-4] + ".tab"
    cases = {
        "regress_cf": (os.path.join(WT, "problems", "tests", "regress_cf.athinput"),
                       [f"problem/comp0_file={ic}/regress.tab"]),
        "cf_table_regress": (os.path.join(WT, "problems", "tests",
                                          "cf_table_regress.athinput"),
                             [f"particles/particle_file={ic}/{osnrp}",
                              f"problem/comp0_file={ic}/{ostab}"]),
    }
    summary["P2"] = {}
    for name, (inp, args) in cases.items():
        for lab, exe in (("base", a.base), ("new", a.new)):
            run(exe, os.path.join(top, name, lab), inp, args)
        rc, txt = compare(os.path.join(top, name, "base"), os.path.join(top, name, "new"))
        summary["P2"][name] = {"identical": rc == 0, "report": txt.splitlines()[-1]}
        print(f"P2 {name}: {txt.splitlines()[-1]}", flush=True)

    # ---- P5: combined curvature
    ball = os.path.join(ic, "ball")
    os.makedirs(ball, exist_ok=True)
    subprocess.run([sys.executable, os.path.join(WT, "problems", "ic", "make_ball.py"),
                    "--Rb", "5", "--h", "0.5", "--out", ball], check=True,
                   stdout=subprocess.DEVNULL)
    tab = os.path.join(ball, sorted(x for x in os.listdir(ball) if x.endswith(".tab"))[0])
    tab0 = os.path.join(ball, "ball_zeroK.tab")
    with open(tab) as fi, open(tab0, "w") as fo:
        for line in fi:
            if line.startswith("#") or not line.strip():
                fo.write(line)
                continue
            v = line.split()
            fo.write(" ".join([v[0], v[1], "0.0", "0.0", v[4], "0.0"]) + "\n")
    inp = os.path.join(WT, "problems", "tests", "regress_cf.athinput")
    common = ["problem/ncomp=2", "problem/comp0_type=table", "problem/comp0_x1=0.0",
              "problem/comp1_type=gaussian",   # placeholder, replaced below
              "problem/lapse=one", "time/nlim=0", "output5/dcycle=-1",
              "mesh/x1min=-12", "mesh/x1max=12", "mesh/x2min=-12", "mesh/x2max=12",
              "mesh/x3min=-12", "mesh/x3max=12"]
    common = [c for c in common if not c.startswith("problem/comp1_type")]
    punc = ["problem/comp1_type=puncture", "problem/comp1_mass=0.5",
            "problem/comp1_x1=2.6", "problem/comp1_x2=-1.1", "problem/comp1_x3=0.7"]
    mom = ["problem/comp1_p1=0.05", "problem/comp1_p2=0.3", "problem/comp1_s3=0.2"]
    runs = {"comb": [f"problem/comp0_file={tab}"] + punc + mom,
            "A": [f"problem/comp0_file={tab}"] + punc,
            "B": [f"problem/comp0_file={tab0}"] + punc + mom}
    for lab, extra in runs.items():
        run(a.new, os.path.join(top, "P5", lab), inp, common + extra)
    comps = ["Kxx", "Kxy", "Kxz", "Kyy", "Kyz", "Kzz"]
    res = {}
    for c in comps:
        kc = kfield(os.path.join(top, "P5", "comb"), c)
        ka = kfield(os.path.join(top, "P5", "A"), c)
        kb = kfield(os.path.join(top, "P5", "B"), c)
        scale = max(np.max(np.abs(kc)), 1e-300)
        res[c] = {"max|K_comb|": float(scale),
                  "max|K_comb-(K_A+K_B)|": float(np.max(np.abs(kc - (ka + kb)))),
                  "max|K_comb-K_A|": float(np.max(np.abs(kc - ka))),
                  "max|K_B|": float(np.max(np.abs(kb)))}
        print(f"P5 {c}: {res[c]}", flush=True)
    worst = max(v["max|K_comb-(K_A+K_B)|"] / v["max|K_comb|"] for v in res.values())
    summary["P5"] = {"components": res, "worst_relative": worst, "pass": worst < 1e-13}
    print(f"P5 worst relative difference {worst:.3e}: "
          f"{'PASS' if worst < 1e-13 else 'FAIL'}", flush=True)

    # figure: K_yy along the x axis through the puncture height
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle
    figstyle.use_style()
    import bin_convert
    def line(lab, comp):
        out = os.path.join(top, "P5", lab, "bin")
        f = sorted(x for x in os.listdir(out) if ".adm." in x)[0]
        d = bin_convert.read_binary(os.path.join(out, f))
        xs, vs = [], []
        for m, blk in enumerate(d["mb_data"]["adm_" + comp]):
            blk = np.asarray(blk)
            g = d["mb_geometry"][m]
            nz, ny, nx = blk.shape
            x = g[0] + (np.arange(nx) + 0.5) * (g[1] - g[0]) / nx
            y = g[2] + (np.arange(ny) + 0.5) * (g[3] - g[2]) / ny
            z = g[4] + (np.arange(nz) + 0.5) * (g[5] - g[4]) / nz
            jy, kz = np.argmin(np.abs(y + 1.1)), np.argmin(np.abs(z - 0.7))
            if abs(y[jy] + 1.1) <= 0.5 * (g[3] - g[2]) / ny + 1e-12 and \
               abs(z[kz] - 0.7) <= 0.5 * (g[5] - g[4]) / nz + 1e-12:
                xs.append(x)
                vs.append(blk[kz, jy, :])
        x = np.concatenate(xs)
        v = np.concatenate(vs)
        o = np.argsort(x)
        return x[o], v[o]
    fig, ax = plt.subplots(2, 1, figsize=(6.4, 6.0), sharex=True)
    for lab, st in (("comb", "-"), ("A", "--"), ("B", ":")):
        x, v = line(lab, "Kxy")
        ax[0].plot(x, v, st, label={"comb": "table + moving puncture",
                                     "A": "table + puncture at rest",
                                     "B": "zero-curvature table + moving puncture"}[lab])
    xc, vc = line("comb", "Kxy")
    xa, va = line("A", "Kxy")
    xb, vb = line("B", "Kxy")
    ax[1].semilogy(xc, np.abs(vc - (va + vb)) + 1e-300, "-", label="|comb - (A + B)|")
    ax[1].semilogy(xc, np.abs(vc - va) + 1e-300, "--", label="|comb - A|")
    ax[0].set_ylabel(r"$K_{xy}$")
    ax[1].set_ylabel(r"difference")
    ax[1].set_xlabel(r"$x$ (line $y=-1.1$, $z=0.7$ through the puncture)")
    ax[0].legend(frameon=False, fontsize=8)
    ax[1].legend(frameon=False, fontsize=8)
    ax[1].set_ylim(1e-20, 10)
    fig.tight_layout()
    fig.savefig(os.path.join(top, "fig_cf_combined.png"), dpi=150)
    with open(os.path.join(top, "summary.json"), "w") as fp:
        json.dump(summary, fp, indent=1)
    ok = all(v["identical"] for v in summary["P2"].values()) and summary["P5"]["pass"]
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
