#!/usr/bin/env python3
"""Restarts under threads (journal entry 19, prediction P16): for the cosmology box with
Z4c (east) and the Newtonian mode (newton), an uninterrupted run of 2n steps against a
run continued from the restart file written after n steps, with the threaded executable
at one thread, at four threads with private deposit copies, and at four threads with
atomic additions.

    restart_threads.py [--exe O3] [--out DIR] [--threads 4]

DIR/<case>/<config>/full and .../cont; DIR/restart_threads.json;
DIR/figs/restart_threads.{png,pdf}. Compared: every restart file the continued run wrote
(mesh data, particle restart file, Newtonian state), every particle snapshot it wrote,
and the history records of its cycles. Measure: omplib.number_diff (rel_max: largest
difference over the largest number of the file). Exit status 1 if a run fails, a file
of the continued run has no partner or another shape, or a difference exceeds --tol.
"""
import argparse
import filecmp
import glob
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "python"))
import omplib as L  # noqa: E402

# case: deck, linked files, arguments of the uninterrupted run, text appended to the deck,
# number of the restart file written half way
RCASES = {
    "east": dict(inp="problems/cosmo/east.athinput",
                 files=[L.IC + "/east16/particles.nrp", L.IC + "/east16/fields.bin"],
                 args=["mesh/nx1=16", "mesh/nx2=16", "mesh/nx3=16", "meshblock/nx1=8",
                       "meshblock/nx2=8", "meshblock/nx3=8", "time/nlim=20",
                       "particles/snap_dt=0.2", "particles/traj_ntrack=46"],
                 append=L.RST % 10, half=1),
    "newton": dict(inp="problems/newton/periodic.athinput", files=[L.IC2 + "/wave32.nrp"],
                   args=["time/tlim=0.2", "particles/snap_dt=0.05",
                         "particles/particle_file=wave32.nrp", "output1/dt=0.1"],
                   half=1),
}


def history_diff(fa, fb):
    """Records of the continued run's history fb against the same cycles of fa."""
    def recs(path):
        out = {}
        for ln in open(path):
            if ln.startswith("#") or not ln.strip():
                continue
            w = ln.split()
            out[int(w[1])] = (ln.rstrip("\n"), np.array([float(x) for x in w]))
        return out
    ra, rb = recs(fa), recs(fb)
    miss = [c for c in rb if c not in ra]
    cyc = [c for c in sorted(rb) if c in ra]
    if not cyc:
        return {"kind": "history", "records": 0, "missing": len(miss), "rel_max": 0.0}
    a = np.array([ra[c][1] for c in cyc])
    b = np.array([rb[c][1] for c in cyc])
    full = np.array([v[1] for v in ra.values()])
    isint = np.all(full == np.round(full), axis=0)
    scale = float(np.abs(full[:, ~isint]).max()) if (~isint).any() else 1.0
    d = np.abs(a - b)
    return {"kind": "history", "records": len(cyc), "missing": len(miss),
            "cycles": [cyc[0], cyc[-1]],
            "text_identical": all(ra[c][0] == rb[c][0] for c in cyc),
            "int_columns_differ": int((d[:, isint] > 0).any(axis=0).sum()),
            "abs": float(d.max()), "rel_max": float(d[:, ~isint].max()/scale)}


def compare(full, cont):
    out, hard = {}, False
    names = []
    for pat in ("rst/*.rst", "rst/*.rst.prt", "rst/*.rst.prt.nwt", "*.part.*.bin"):
        names += sorted(os.path.relpath(p, cont) for p in glob.glob(os.path.join(cont, pat)))
    for n in names:
        fa, fb = os.path.join(full, n), os.path.join(cont, n)
        if not os.path.exists(fa):
            out[n] = {"kind": "missing"}
            hard = True
        elif filecmp.cmp(fa, fb, shallow=False):
            out[n] = {"kind": "identical", "rel_max": 0.0}
        else:
            out[n] = L.number_diff(fa, fb)
            hard |= out[n]["kind"] in ("size", "text-shape") or bool(out[n].get("nonfinite"))
    for fb in sorted(glob.glob(os.path.join(cont, "*.hst"))):
        n = os.path.basename(fb)
        fa = os.path.join(full, n)
        if os.path.exists(fa):
            out[n] = history_diff(fa, fb)
            hard |= bool(out[n]["missing"]) or bool(out[n]["int_columns_differ"])
    worst = max([v.get("rel_max", 0.0) for v in out.values()] + [0.0])
    return {"files": out, "worst_rel_max": worst, "structural_difference": hard,
            "all_identical": all(v["kind"] == "identical" or v.get("text_identical")
                                 for v in out.values()) and not hard}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", default="O3")
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--tol", type=float, default=1.0e-10)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", ""))
    a = ap.parse_args()
    exe = L.EXES.get(a.exe, a.exe)
    configs = [("t1", 1, ""), ("t%dp" % a.threads, a.threads, "priv"),
               ("t%d" % a.threads, a.threads, "")]
    res = {"exe": exe, "exe_sha256": L.sha256(exe), "tol": a.tol, "cases": {}}
    bad = 0
    for case, c in RCASES.items():
        res["cases"][case] = {}
        for label, nt, mode in configs:
            base = os.path.join(os.path.abspath(a.out), case, label)
            full, cont = os.path.join(base, "full"), os.path.join(base, "cont")
            r1 = L.run_case(exe, case, full, nt, spec=c, mode=mode)
            rsts = sorted(glob.glob(os.path.join(full, "rst", "*.rst")))
            rec = {"threads": nt, "mode": mode or "atomic", "full_exit": r1["exit"],
                   "restart_files": [os.path.basename(x) for x in rsts]}
            if r1["exit"] != 0 or len(rsts) <= c["half"]:
                rec["error"] = "uninterrupted run failed or wrote no restart file half way"
                bad += 1
                res["cases"][case][label] = rec
                continue
            os.makedirs(cont, exist_ok=True)
            for path in c["files"]:
                link = os.path.join(cont, os.path.basename(path))
                if not os.path.lexists(link):
                    os.symlink(path, link)
            cmd = [exe, "-r", rsts[c["half"]]]
            with open(os.path.join(cont, "run.log"), "w") as log:
                rc = subprocess.run(cmd, cwd=cont, stdout=log, stderr=subprocess.STDOUT,
                                    env=L.thread_env(nt), timeout=3600).returncode
            rec.update(cont_exit=rc, restart_from=os.path.basename(rsts[c["half"]]),
                       cont_cmd=cmd)
            if rc != 0:
                rec["error"] = "continued run failed"
                bad += 1
            else:
                rec.update(compare(full, cont))
                flag = rec["structural_difference"] or rec["worst_rel_max"] > a.tol
                bad += int(flag)
                print("%-7s %-4s %-7s restart from %s: %2d files compared, %2d identical, "
                      "worst rel_max %.2e%s" % (
                          case, label, rec["mode"], rec["restart_from"], len(rec["files"]),
                          sum(v["kind"] == "identical" or bool(v.get("text_identical"))
                              for v in rec["files"].values()),
                          rec["worst_rel_max"], "  FAIL" if flag else ""))
                for n, v in rec["files"].items():
                    if not (v["kind"] == "identical" or v.get("text_identical")):
                        print("            %-28s %-10s rel_max %.2e" % (
                            n, v["kind"], v.get("rel_max", float("nan"))))
            res["cases"][case][label] = rec
            L.dump(res, os.path.join(a.out, "restart_threads.json"))
    res["failures"] = bad
    L.dump(res, os.path.join(a.out, "restart_threads.json"))
    figure(res, os.path.join(a.out, "figs", "restart_threads"))
    print("failures: %d" % bad)
    return 1 if bad else 0


def figure(res, out):
    """Per case and configuration, every compared file of the continued run: largest
    difference from the uninterrupted run over the largest number of the file; marks at
    the left edge are byte-identical files (histories: identical text records)."""
    from nrpic import figstyle as fs
    import matplotlib.pyplot as plt
    os.makedirs(os.path.dirname(out), exist_ok=True)
    fs.use_style()
    floor = 1.0e-19
    fig, ax = plt.subplots(figsize=(fs.COLUMN_WIDTH*1.5, 3.0))
    fig.subplots_adjust(left=0.30, right=0.97, bottom=0.17, top=0.96)
    kinds = [("restart files", lambda n: n.startswith("rst/"), "o"),
             ("particle snapshots", lambda n: ".part." in n, "s"),
             ("histories", lambda n: n.endswith(".hst"), "D")]
    rows, y = [], 0
    for case, cc in res["cases"].items():
        for label, rec in cc.items():
            rows.append("%s, %d thread%s%s" % (case, rec["threads"],
                                             "" if rec["threads"] == 1 else "s",
                                             ", private" if rec["mode"] == "priv" else ""))
            for k, (name, sel, mk) in enumerate(kinds):
                v = [max(f.get("rel_max", 0.0), floor)
                     for n, f in rec.get("files", {}).items() if sel(n)]
                ax.plot(v, [y + (k - 1)*0.22]*len(v), mk, color=fs.SERIES[k], ms=5,
                        mfc="none", label=name if y == 0 else None)
            y += 1
    ax.axvline(res["tol"], **fs.GUIDE)
    ax.axvline(floor, **fs.MASK_LINE)
    ax.text(floor*2.0, -0.75, "identical", fontsize=8, color="0.4")
    ax.set_xscale("log")
    ax.set_xlim(floor/5, 1.0e-7)
    ax.set_xticks([1e-18, 1e-15, 1e-12, 1e-9])
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels(rows, fontsize=8)
    ax.tick_params(axis="y", which="minor", left=False, right=False)
    ax.set_ylim(len(rows) - 0.5, -1.1)
    ax.set_xlabel("continued against uninterrupted run:\nlargest difference / largest number")
    ax.legend(loc="lower right", fontsize=7)
    fs.save(fig, out)
    print("wrote", out + ".png")


if __name__ == "__main__":
    sys.exit(main())
