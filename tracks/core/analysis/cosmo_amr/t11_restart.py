#!/usr/bin/env python3
"""T11 of the work package cosmo-amr: restarts on adaptive periodic meshes
(prediction: tracks/core/JOURNAL-cosmo-amr.md, entry 15:52).

    t11_restart.py --old OLD_EXE --new NEW_EXE --out DIR [--cores N] [--only a,b]

Every case runs uninterrupted ("straight") with restart files, and is restarted in other
directories; every record after the restart time of the histories (.nrpic.hst, .cstat.hst,
.region.hst), the tracker file and the files of the horizon finder is compared as text
with the uninterrupted run.  OLD is the executable of the tests T1 to T9 (counters of the
adaptive driver not restored), NEW the one with <file>.rst.amr.
  M    T5's moving tracker (M of t2_flrw.py), to cycle 90; regrids at cycles 4, 16, 76
       r14  from the restart file written inside the loop at cycle 14 (2 cycles before
            a regrid)
       r28  from the file of cycle 28 (a cycle of the check, no regrid there)
       f16  from the restart file written at the end of a run stopped at cycle 16 (after
            the regrid of that cycle)
       i16  from a file written inside the loop at cycle 16 (before the regrid of that
            cycle: the restarted run must do it first)
  P    T9's `ladder' on the peak data, to cycle 12; regrid at cycle 4
       r6   inside the loop at cycle 6;  f4  end of a run at cycle 4;  i4  inside the
            loop at cycle 4
  U    T2's U with the horizon finder and its status file (uniform mesh), to cycle 24;
       r8   inside the loop at cycle 8
Writes DIR/t11_summary.json and DIR/fig_t11_restart.{pdf,png}."""
import argparse
import glob
import json
import os
import subprocess
import sys
import time

import numpy as np

import amrlib as A
import t2_flrw as T2
import t9_peak as T9

FILES = {  # file suffix -> index of the time column
    "nrpic.hst": 0, "cstat.hst": 0, "region.hst": 0, "co_0.txt": 1,
    "horizon_status_0.txt": 1, "horizon_summary_0.txt": 1,
}


def rows(path, tcol):
    """records of a text output keyed by the text of their time field"""
    out = {}
    if not os.path.exists(path):
        return out
    with open(path) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            w = line.split()
            if len(w) > tcol:
                out[w[tcol]] = line.rstrip("\n")
    return out


def compare(dfull, drst, base, t_rst):
    res = {}
    for suf, tcol in FILES.items():
        a = rows(os.path.join(dfull, f"{base}.{suf}"), tcol)
        b = rows(os.path.join(drst, f"{base}.{suf}"), tcol)
        if not a and not b:
            continue
        keys = [k for k in a if float(k) > t_rst*(1.0 + 1e-14) + 1e-300]
        same = sum(1 for k in keys if k in b and b[k] == a[k])
        diff = sum(1 for k in keys if k in b and b[k] != a[k])
        miss = sum(1 for k in keys if k not in b)
        extra = sum(1 for k in b if k not in a)
        first = next((float(k) for k in keys if k not in b or b[k] != a[k]), None)
        res[suf] = dict(compared=len(keys), identical=same, differing=diff, missing=miss,
                        extra=extra, first_bad_time=first)
    return res


def run(exe, args, rundir, start_dir=None):
    os.makedirs(rundir, exist_ok=True)
    t0 = time.time()
    with open(os.path.join(rundir, "log.txt"), "w") as log:
        p = subprocess.run([exe] + args + ["-d", rundir], cwd=start_dir or rundir,
                           stdout=log, stderr=subprocess.STDOUT,
                           env=dict(os.environ, OMP_NUM_THREADS="1"))
    wall = time.time() - t0
    with open(os.path.join(rundir, "status.txt"), "w") as f:
        f.write(f"exit {p.returncode}\nwall {wall:.2f}\nexe {exe}\n")
    return p.returncode


def straight_jobs(out, lab, exe, ic1, ic8, icp):
    """(name, exe, deck, rundir) of the uninterrupted runs"""
    m = T2.cases(ic1, ic8)["M"]
    m.set("time", tlim=100.0, nlim=90)
    p = T9.base(icp)
    p.set("time", nlim=12)
    u = T2.cases(ic1, ic8)["U"]
    u.set("time", tlim=100.0, nlim=24)
    jobs = []

    def add(name, deck, nlim, dcycle):
        d = deck.copy().set("time", nlim=nlim)
        d.set("output9", file_type="rst", dcycle=dcycle)
        rd = os.path.join(out, lab, name)
        os.makedirs(rd, exist_ok=True)
        jobs.append((name, exe, d.write(os.path.join(rd, "deck.athinput")), rd))

    add("M_full", m, 90, 14)
    add("M_pre16", m, 16, 1000)
    add("M_in16", m, 17, 16)
    add("P_full", p, 12, 6)
    add("P_pre4", p, 4, 1000)
    add("P_in4", p, 5, 4)
    add("U_full", u, 24, 8)
    return jobs


# restart: (name, straight run, restart file number, restart cycle, case base name, full)
RESTARTS = [
    ("M_r14", "M_full", 1, 14, "flrw", "M_full"),
    ("M_r28", "M_full", 2, 28, "flrw", "M_full"),
    ("M_f16", "M_pre16", 1, 16, "flrw", "M_full"),
    ("M_i16", "M_in16", 1, 16, "flrw", "M_full"),
    ("P_r6", "P_full", 1, 6, "peak", "P_full"),
    ("P_f4", "P_pre4", 1, 4, "peak", "P_full"),
    ("P_i4", "P_in4", 1, 4, "peak", "P_full"),
    ("U_r8", "U_full", 1, 8, "flrw", "U_full"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--old", required=True)
    ap.add_argument("--new", required=True)
    ap.add_argument("--ic", default=T9.DEF_IC)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    ap.add_argument("--cores", type=int, default=8)
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    a.out, a.old, a.new = (os.path.abspath(v) for v in (a.out, a.old, a.new))
    os.makedirs(a.out, exist_ok=True)
    ic1, ic8 = os.path.join(a.out, "ic1"), os.path.join(a.out, "ic8")
    mk = os.path.join(A.ROOT, "cosmo/ic/make_lattice.py")
    for ic, ppc in ((ic1, 1), (ic8, 2)):
        if not os.path.exists(os.path.join(ic, "particles.nrp")):
            subprocess.run([sys.executable, mk, "--n", str(T2.N), "--ppc", str(ppc), "--L",
                            str(T2.L), "--xmin", str(-T2.L/2), "--out", ic], check=True,
                           stdout=subprocess.DEVNULL)
    import concurrent.futures as cf
    exes = (("old", a.old), ("new", a.new))
    only = a.only.split(",") if a.only else None
    jobs = []
    for lab, exe in exes:
        jobs += [(n, exe, deck, rd) for n, _, deck, rd in
                 [(j[0], j[1], j[2], j[3]) for j in straight_jobs(a.out, lab, exe, ic1,
                                                                    ic8, a.ic)]
                 if only is None or n.split("_")[0] in only]
    with cf.ThreadPoolExecutor(max_workers=a.cores) as ex:
        rc1 = list(ex.map(lambda j: run(j[1], ["-i", j[2]], j[3]), jobs))
    for j, rc in zip(jobs, rc1):
        print(f"{os.path.basename(os.path.dirname(j[3]))}/{j[0]:8s} exit {rc}", flush=True)

    rjobs = []
    for lab, exe in exes:
        for name, src, num, cyc, base, full in RESTARTS:
            if only is not None and name.split("_")[0] not in only:
                continue
            f = os.path.join(a.out, lab, src, "rst", f"{base}.{num:05d}.rst")
            rjobs.append((lab, name, exe, f, os.path.join(a.out, lab, name), cyc, base,
                          os.path.join(a.out, lab, full)))
    with cf.ThreadPoolExecutor(max_workers=a.cores) as ex:
        rc2 = list(ex.map(lambda j: run(j[2], ["-r", j[3]], j[4]), rjobs))

    res = {}
    for j, rc in zip(rjobs, rc2):
        lab, name, exe, f, rd, cyc, base, full = j
        h = A.read_hst(os.path.join(full, f"{base}.nrpic.hst"))
        t_rst = float(h["time"][np.argmin(np.abs(h["ncycle"] - cyc))])
        cmpres = compare(full, rd, base, t_rst)
        with open(os.path.join(rd, "log.txt"), errors="replace") as fh:
            notes = [x for x in fh.read().splitlines() if "refinement counters" in x
                     or "NRPIC: no" in x or "FATAL" in x]
        ok = rc == 0 and all(v["differing"] == 0 and v["missing"] == 0
                             for v in cmpres.values())
        res[f"{lab}/{name}"] = dict(exit=rc, restart_file=f, restart_cycle=cyc,
                                    restart_time=t_rst, amr_file=os.path.exists(f + ".amr"),
                                    files=cmpres, exact=ok, log=notes[:3])
        bad = {k: (v["differing"], v["missing"], v["first_bad_time"])
               for k, v in cmpres.items() if v["differing"] or v["missing"]}
        print(f"{lab}/{name:6s} exit {rc} exact {ok} "
              f"compared {sum(v['compared'] for v in cmpres.values())} bad {bad}", flush=True)
    with open(os.path.join(a.out, "t11_summary.json"), "w") as fh:
        json.dump(res, fh, indent=1)
        fh.write("\n")

    # ---- figure: MeshBlocks and the departure of alpha_max from the uninterrupted run
    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, ax = plt.subplots(1, 3, figsize=(8.0, 2.9))
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.17, top=0.93, wspace=0.40)
    cols = {"old": fs.PAL["red"], "new": fs.PAL["blue"]}
    for lab in ("old", "new"):
        full = os.path.join(a.out, lab, "M_full", "flrw.nrpic.hst")
        rst = os.path.join(a.out, lab, "M_r14", "flrw.nrpic.hst")
        if os.path.exists(full) and os.path.exists(rst):
            hf, hr = A.read_hst(full), A.read_hst(rst)
            if lab == "new":
                ax[0].plot(hf["ncycle"], hf["nmb"], color="k", lw=2.0, alpha=0.3,
                           label="uninterrupted")
            ax[0].plot(hr["ncycle"], hr["nmb"], "--" if lab == "old" else ":",
                       color=cols[lab], label=f"restart at 14 ({lab})")
            k = {c: i for i, c in enumerate(hf["ncycle"])}
            cyc = [c for c in hr["ncycle"] if c in k]
            d = [abs(hr["alpha_max"][list(hr["ncycle"]).index(c)]
                     / hf["alpha_max"][k[c]] - 1.0) for c in cyc]
            ax[1].semilogy(cyc, np.maximum(d, 1e-17), color=cols[lab], label=lab)
    ax[0].set_xlabel("cycle")
    ax[0].set_ylabel("MeshBlocks (case M)")
    ax[0].legend(frameon=False, fontsize=7)
    ax[1].set_xlabel("cycle")
    ax[1].set_ylabel(r"$|\alpha_{\max}^{\rm restart}/\alpha_{\max}-1|$ (M, r14)")
    ax[1].legend(frameon=False, fontsize=7)
    names = [r[0] for r in RESTARTS if f"new/{r[0]}" in res]
    for i, lab in enumerate(("old", "new")):
        nb = [sum(v["differing"] + v["missing"] for v in res[f"{lab}/{n}"]["files"].values())
              if f"{lab}/{n}" in res else np.nan for n in names]
        ax[2].bar(np.arange(len(names)) + (i - 0.5)*0.38, np.maximum(nb, 0.0) + 0.5,
                  width=0.38, color=cols[lab], label=lab, bottom=0.5)
    ax[2].set_yscale("log")
    ax[2].set_xticks(np.arange(len(names)))
    ax[2].set_xticklabels(names, rotation=60, fontsize=7)
    ax[2].set_ylabel("records that differ + 1")
    ax[2].legend(frameon=False, fontsize=7)
    fs.save(fig, os.path.join(a.out, "fig_t11_restart"))
    plt.close(fig)
    return 0


if __name__ == "__main__":
    sys.exit(main())
