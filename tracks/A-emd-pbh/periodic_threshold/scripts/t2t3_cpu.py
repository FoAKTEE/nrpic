"""T2 (mesh refinement in the periodic cosmological box) and T3 (horizon finder in a
periodic mesh): short runs of the processor executable (JOURNAL.md, T2/T3 entry).

    python3 t2t3_cpu.py --out DIR [--jobs 3] [--only-analysis]

Cases and predictions: JOURNAL.md. Executable: the release processor build
/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena (serial).
"""
import argparse
import glob
import json
import os
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
REPO = "/data/haiyangw/nrpic/wt/A-emd-pbh"
EXE = "/data/haiyangw/nrpic/.work/build_cpu_v03/src/athena"
sys.path.insert(0, HERE)
import figstyle as fs  # noqa: E402

SMR = os.path.join(PKG, "inputs", "peak_smr.athinput")
AMR = os.path.join(PKG, "inputs", "peak_amr.athinput")
PUNC = os.path.join(PKG, "inputs", "punc_box16.athinput")
PER = ["mesh/ix1_bc=periodic", "mesh/ox1_bc=periodic", "mesh/ix2_bc=periodic",
       "mesh/ox2_bc=periodic", "mesh/ix3_bc=periodic", "mesh/ox3_bc=periodic"]

CASES = {
    # T2a + T3d: homogeneous universe
    "T2a_uniform": dict(inp=SMR, ic="flrw", args=["problem/id=flrw", "time/tlim=0.3",
                                                    "mesh_refinement/refinement=none",
                                                    "fastflow/find_every=4"]),
    "T2a_smr_adaptive": dict(inp=SMR, ic="flrw", args=["problem/id=flrw", "time/tlim=0.3",
                                                         "fastflow/find_every=4"]),
    "T2a_smr_finest": dict(inp=SMR, ic="flrw", args=["problem/id=flrw", "time/tlim=0.3",
                                                       "fastflow/find_every=4",
                                                       "particles/deposit_adaptive=false"]),
    # T2b: the peak data at t = 0
    "T2b_uniform_mu0.5": dict(inp=SMR, ic="peak0.5", args=["time/nlim=1",
                                                           "mesh_refinement/refinement=none",
                                                           "fastflow/find_every=1000"]),
    "T2b_smr_mu0.5": dict(inp=SMR, ic="peak0.5", args=["time/nlim=1",
                                                       "fastflow/find_every=1000"]),
    "T2b_uniform_mu0.03": dict(inp=SMR, ic="peak0.03", args=["time/nlim=1",
                                                             "mesh_refinement/refinement=none",
                                                             "fastflow/find_every=1000"]),
    "T2b_smr_mu0.03": dict(inp=SMR, ic="peak0.03", args=["time/nlim=1",
                                                         "fastflow/find_every=1000"]),
    # T2c: adaptive refinement at the start
    "T2c_amr_flrw": dict(inp=AMR, ic="flrw", args=["problem/id=flrw", "time/nlim=8",
                                                   "mesh/nx1=32", "mesh/nx2=32",
                                                   "mesh/nx3=32", "meshblock/nx1=8",
                                                   "meshblock/nx2=8", "meshblock/nx3=8",
                                                   "fastflow/find_every=1000"]),
    "T2c_amr_mu0.5": dict(inp=AMR, ic="peak0.5", args=["time/nlim=8", "mesh/nx1=32",
                                                       "mesh/nx2=32", "mesh/nx3=32",
                                                       "meshblock/nx1=8", "meshblock/nx2=8",
                                                       "meshblock/nx3=8",
                                                       "fastflow/find_every=1000"]),
    # T3: vacuum puncture
    "T3a_outflow": dict(inp=PUNC, ic=None, args=["time/nlim=1", "fastflow/find_every=1"]),
    "T3b_periodic": dict(inp=PUNC, ic=None, args=["time/nlim=1", "fastflow/find_every=1"]
                         + PER),
    "T3c_periodic_shift": dict(inp=PUNC, ic=None, args=["time/nlim=1",
                                                        "fastflow/find_every=1",
                                                        "fastflow/center_x_0=32.0"] + PER),
}


def make_ic(out):
    """Initial data shared by the cases (32^3, box 20, peak at the origin)."""
    py = os.path.join(REPO, ".venv", "bin", "python")
    d = os.path.join(out, "ic_flrw")
    if not os.path.exists(os.path.join(d, "particles.nrp")):
        os.makedirs(d, exist_ok=True)
        subprocess.run([py, os.path.join(REPO, "cosmo", "ic", "make_lattice.py"), "--n", "32",
                        "--ppc", "1", "--L", "20", "--xmin", "-10", "--out", d], check=True,
                       stdout=open(d + ".log", "w"), stderr=subprocess.STDOUT)
    for mu in ("0.5", "0.03"):
        d = os.path.join(out, f"ic_peak{mu}")
        if not os.path.exists(os.path.join(d, "particles.nrp")):
            subprocess.run([py, "-I", os.path.join(HERE, "make_peak_ic.py"), "--mu", mu,
                            "--e", "0.2", "--eps-i", "1", "--n", "32", "--nfilter", "2",
                            "--compensate", "--out", d], check=True,
                           stdout=open(d + ".log", "w"), stderr=subprocess.STDOUT)


def launch(out, name, c):
    d = os.path.join(out, name)
    os.makedirs(d, exist_ok=True)
    args = [EXE, "-i", c["inp"], "-d", d] + c["args"]
    if c["ic"] is not None:
        icd = os.path.join(out, "ic_" + c["ic"])
        args += [f"particles/particle_file={icd}/particles.nrp"]
        if c["ic"] != "flrw":
            args += [f"problem/id_file={icd}/fields.bin"]
    env = dict(os.environ, OMP_NUM_THREADS="1")
    return subprocess.Popen(args, cwd=d, stdout=open(os.path.join(d, "athena.log"), "w"),
                            stderr=subprocess.STDOUT, env=env)


def read_cols(path):
    names = None
    with open(path) as f:
        for line in f:
            if line.startswith("# [1]="):
                names = [w.split("=")[1] for w in line[1:].split()]
                break
    a = np.loadtxt(path, ndmin=2)
    return {n: a[:, i] for i, n in enumerate(names)}


def read_tab(path):
    with open(path) as f:
        lines = f.readlines()
    hdr = [ln for ln in lines if ln.startswith("# gid")][0][1:].split()
    rows = [ln.split() for ln in lines if not ln.startswith("#") and ln.strip()]
    return {h: np.array([float(r[i]) for r in rows]) for i, h in enumerate(hdr)}


def horizon(path):
    a = np.loadtxt(path, ndmin=2) if os.path.getsize(path) > 0 else None
    if a is None or a.size == 0:
        return []
    return [dict(iter=int(r[0]), time=float(r[1]), mass=float(r[2]), area=float(r[7]),
                 hrms=float(r[8]), meanradius=float(r[10])) for r in a]


def analyse(out):
    res = {}
    for name in CASES:
        d = os.path.join(out, name)
        if not os.path.isdir(d):
            continue
        r = {"log_tail": open(os.path.join(d, "athena.log")).read().splitlines()[-4:]}
        cst = glob.glob(os.path.join(d, "*.cstat.hst"))
        if cst:
            c = read_cols(cst[0])
            r["cstat"] = {k: v.tolist() for k, v in c.items()}
        hz = glob.glob(os.path.join(d, "*horizon_summary_0.txt"))
        if hz:
            r["horizon"] = horizon(hz[0])
        nh = glob.glob(os.path.join(d, "*.nrpic.hst"))
        if nh:
            c = read_cols(nh[0])
            r["nmb"] = c.get("nmb", np.array([])).tolist()
            r["time_nrpic"] = c["time"].tolist()
        t0 = sorted(glob.glob(os.path.join(d, "tab", "*.con.00000.tab")))
        e0 = sorted(glob.glob(os.path.join(d, "tab", "*.tmunu_E.00000.tab")))
        if t0 and e0:
            con = read_tab(t0[0])
            ee = read_tab(e0[0])
            x = con["x1v"]
            order = np.argsort(x)
            Ebar = 3.0/(8.0*np.pi)
            dE = 16*np.pi*np.abs(ee["tmunu_E"] - Ebar).max()
            r["line_t0"] = {"x": x[order].tolist(), "H": con["con_H"][order].tolist(),
                            "E": ee["tmunu_E"][order].tolist(),
                            "dx": np.diff(np.sort(x)).tolist()}
            r["H_over_16piDE"] = float(np.abs(con["con_H"]).max()/dE)
            fine = np.abs(x) < 5.0
            coarse = ~fine
            r["H_over_16piDE_inner"] = float(np.abs(con["con_H"][fine]).max()/dE)
            r["H_over_16piDE_outer"] = float(np.abs(con["con_H"][coarse]).max()/dE)
        res[name] = r
    with open(os.path.join(out, "t2t3_results.json"), "w") as f:
        json.dump(res, f, indent=1)
    # summary
    for name, r in res.items():
        line = f"{name:22s}"
        if "cstat" in r:
            c = r["cstat"]
            chi = (np.array(c["chi_max"])/np.array(c["chi_min"]) - 1.0)
            line += (f" t_end={c['time'][-1]:.3f} Hmax0={c['H_max'][0]:.2e}"
                     f" Hrmax0={c['Hr_max'][0]:.2e} Hrmax_end={c['Hr_max'][-1]:.2e}"
                     f" Hmax/Hmean_end={c['H_max'][-1]/max(abs(c['H_mean'][-1]), 1e-300):.3g}"
                     f" chi_spread_end={chi[-1]:.2e}")
        if "H_over_16piDE" in r:
            line += (f" |H|/16pi|dE| all={r['H_over_16piDE']:.3e}"
                     f" inner={r['H_over_16piDE_inner']:.3e}"
                     f" outer={r['H_over_16piDE_outer']:.3e}")
        if "horizon" in r:
            ms = [h["mass"] for h in r["horizon"]]
            line += f" AH masses={ms}"
        if r.get("nmb"):
            line += f" nmb first/last={r['nmb'][0]:.0f}/{r['nmb'][-1]:.0f}"
        print(line)
        print("     log:", r["log_tail"][-1] if r["log_tail"] else "")
    figures(out, res)


def figures(out, res):
    fs.use_style()
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(8, 5.6))
    fig.subplots_adjust(left=0.1, right=0.98, bottom=0.09, top=0.97, wspace=0.3,
                        hspace=0.35)
    # top left: T2a relative Hamiltonian constraint against time
    ax = fig.add_subplot(2, 2, 1)
    for name, col in (("T2a_uniform", fs.PAL["blue"]), ("T2a_smr_adaptive", fs.PAL["red"]),
                      ("T2a_smr_finest", fs.PAL["yellow"])):
        c = res.get(name, {}).get("cstat")
        if c:
            ax.semilogy(c["time"], np.maximum(c["Hr_max"], 1e-17), "o-", color=col,
                        label=name[4:])
            ax.semilogy(c["time"], np.maximum(c["Hr_mean"], 1e-17), "--", color=col)
    ax.set_xlabel(r"$t$ (conformal)")
    ax.set_ylabel(r"$H_r$ max (solid), mean (dashed)")
    ax.legend(frameon=False, fontsize=8)
    # top right: T2a spread of chi across the mesh
    ax = fig.add_subplot(2, 2, 2)
    for name, col in (("T2a_uniform", fs.PAL["blue"]), ("T2a_smr_adaptive", fs.PAL["red"]),
                      ("T2a_smr_finest", fs.PAL["yellow"])):
        c = res.get(name, {}).get("cstat")
        if c:
            sp = np.array(c["chi_max"])/np.array(c["chi_min"]) - 1.0
            ax.semilogy(c["time"], np.maximum(sp, 1e-17), "o-", color=col, label=name[4:])
    ax.set_xlabel(r"$t$ (conformal)")
    ax.set_ylabel(r"$\chi_{\max}/\chi_{\min} - 1$")
    # bottom: T2b Hamiltonian constraint along x at t = 0, normalised
    for j, mu in enumerate(("0.5", "0.03")):
        ax = fig.add_subplot(2, 2, 3 + j)
        for name, col in ((f"T2b_uniform_mu{mu}", fs.PAL["blue"]),
                          (f"T2b_smr_mu{mu}", fs.PAL["red"])):
            ln = res.get(name, {}).get("line_t0")
            if ln:
                E = np.array(ln["E"])
                dE = 16*np.pi*np.abs(E - 3/(8*np.pi)).max()
                ax.plot(ln["x"], np.array(ln["H"])/dE, ".-", color=col, ms=3,
                        label=name.split("_")[1])
        ax.axvspan(-5, 5, color="0.5", alpha=0.1)
        ax.axvspan(-2.5, 2.5, color="0.5", alpha=0.1)
        ax.set_xlabel(r"$x$ (line through the peak), $t = 0$")
        ax.set_ylabel(r"$H / (16\pi\,\max|E-\bar E|)$")
        ax.text(0.03, 0.9, rf"$\mu = {mu}$", transform=ax.transAxes)
        ax.legend(frameon=False, fontsize=8, loc="lower right")
    fs.save(fig, os.path.join(out, "fig_t2_mesh"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--only-analysis", action="store_true")
    ap.add_argument("--cases", default="", help="comma-separated prefixes of case names")
    a = ap.parse_args()
    if not a.only_analysis:
        make_ic(a.out)
        pre = [c for c in a.cases.split(",") if c]
        queue = [(n, c) for n, c in CASES.items()
                 if not pre or any(n.startswith(p_) for p_ in pre)]
        running = []
        t0 = time.time()
        while queue or running:
            while queue and len(running) < a.jobs:
                name, c = queue.pop(0)
                running.append((name, launch(a.out, name, c), time.time()))
            time.sleep(2)
            still = []
            for name, p, ts in running:
                if p.poll() is None:
                    still.append((name, p, ts))
                else:
                    print(f"{name}: exit {p.returncode}, {time.time() - ts:.0f} s", flush=True)
            running = still
        print(f"all done in {time.time() - t0:.0f} s")
    analyse(a.out)


if __name__ == "__main__":
    main()
