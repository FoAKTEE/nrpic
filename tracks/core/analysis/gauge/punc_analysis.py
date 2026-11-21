#!/usr/bin/env python3
"""Tests P, E1 and E2 of the work package "gauge" (tracks/core/JOURNAL-gauge.md): a
puncture with and without the lapse relaxation, and the shift damping that follows the
trackers, on one hole and on an unequal pair.

Reads the registered runs with tags <prefix>-p-*, <prefix>-e1-*, <prefix>-e2-* (prefix g:
processors, small mesh; gc: card): tracker files <base>.co_<n>.txt, horizon summaries
<base>.horizon_summary_<n>.txt, constraint norms <base>.z4c.user.hst.  Writes
punc_numbers_<prefix>.json and figs/punc_<prefix>_{p,e1,e2}.png|pdf.

    punc_analysis.py [--prefix g] [--batch RUN_ID ...]

With --batch the sub-directories p-*, e1-*, e2-* of card jobs registered by
harness/bin/nrpic-run (launcher batch: scratch/core/<run_id>/<name>/) are added.
"""
import argparse
import datetime
import filecmp
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "python"))
from nrpic import figstyle as fs               # noqa: E402
import matplotlib.pyplot as plt                # noqa: E402

RUNS = os.path.join(WT, "tracks/core/runs")
FIGS = os.path.join(HERE, "figs")


def manifests(prefix):
    """{tag: manifest}; of several runs with one tag the latest one that has output."""
    out = {}
    for f in sorted(glob.glob(os.path.join(RUNS, "*", "manifest.json"))):
        with open(f) as fh:
            m = json.load(fh)
        tag = m.get("tag", "")
        if tag.startswith(prefix) and "output_directory" in m:
            out[tag] = m
    return out


def batch_manifests(run_id):
    """{name: manifest-like dict} of the runs of one card job registered by nrpic-run
    (launcher batch): the keys the analysis needs, from the job's manifest, its list and
    the log of each run."""
    with open(os.path.join(WT, "tracks/core/runs", run_id, "manifest.json")) as f:
        m = json.load(f)
    root = os.path.join("/data/haiyangw/nrpic", m["outputs"]["dir"])
    out = {}
    with open(os.path.join(root, "batch.list")) as f:
        for line in f:
            w = line.split()
            if not w or w[0].startswith("#"):
                continue
            d = w[0]
            card_s, rc = None, None
            try:
                with open(os.path.join(d, "athena.log")) as fh:
                    txt = fh.read()
                fmt = "%Y-%m-%dT%H:%M:%S"
                t_a = datetime.datetime.strptime(txt.split("start=", 1)[1][:19], fmt)
                t_b = datetime.datetime.strptime(txt.rsplit("end=", 1)[1][:19], fmt)
                card_s = (t_b - t_a).total_seconds()
                rc = int(txt.rsplit("# exit=", 1)[1].split()[0])
            except (OSError, IndexError, ValueError):
                pass
            out[os.path.basename(d)] = dict(
                run_id=run_id + "/" + os.path.basename(d), command=w[1:],
                output_directory=d, exit_status=rc, wall_time_s=card_s,
                card_hours=round(card_s / 3600.0, 5) if card_s is not None else None,
                inputs=[dict(path=i["path"] if os.path.isabs(i["path"])
                             else os.path.join(WT, i["path"])) for i in m["inputs"]])
    return out


def table(path):
    rows = []
    with open(path) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            try:
                rows.append([float(v) for v in line.split()])
            except ValueError:
                continue
    n = min(len(r) for r in rows) if rows else 0
    return np.array([r[:n] for r in rows])


def load(man):
    d = man["output_directory"]
    base = None
    for f in glob.glob(os.path.join(d, "*.co_0.txt")):
        base = os.path.basename(f)[:-len(".co_0.txt")]
    if base is None:
        return None
    out = dict(dir=d, base=base, run_id=man["run_id"], exit=man.get("exit_status"),
               wall=man.get("wall_time_s"), card_hours=man.get("card_hours", 0.0),
               trackers=[], horizons=[])
    n = 0
    while os.path.exists(os.path.join(d, f"{base}.co_{n}.txt")):
        t = table(os.path.join(d, f"{base}.co_{n}.txt"))
        # one record per time (the tracker writes every cycle)
        out["trackers"].append(dict(t=t[:, 1], x=t[:, 2:5], v=t[:, 5:8]))
        h = os.path.join(d, f"{base}.horizon_summary_{n}.txt")
        hz = table(h) if os.path.exists(h) else np.zeros((0, 12))
        out["horizons"].append(dict(t=hz[:, 1], mass=hz[:, 2], spin=hz[:, 6],
                                    rmean=hz[:, 10]) if len(hz) else
                               dict(t=np.zeros(0), mass=np.zeros(0), spin=np.zeros(0),
                                    rmean=np.zeros(0)))
        n += 1
    hst = table(os.path.join(d, f"{base}.z4c.user.hst"))
    out["hst"] = dict(t=hst[:, 0], H=hst[:, 3], M=hst[:, 4], Theta=hst[:, 9])
    return out


def speed(tr, t0, width=0.5):
    """Mean coordinate speed of a tracker between t0 - width and t0 (positions)."""
    t, x = tr["t"], tr["x"]
    if t[-1] < t0 - 1e-9:
        return float("nan")
    xa = np.array([np.interp(t0 - width, t, x[:, i]) for i in range(3)])
    xb = np.array([np.interp(t0, t, x[:, i]) for i in range(3)])
    return float(np.linalg.norm(xb - xa) / width)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prefix", default="g")
    ap.add_argument("--batch", nargs="*", default=[],
                    help="run ids of card jobs registered by nrpic-run (launcher batch)")
    a = ap.parse_args()
    pre = a.prefix
    mans = manifests(pre + "-")
    for rid in a.batch:
        mans.update({pre + "-" + k: v for k, v in batch_manifests(rid).items()})
    runs = {}
    for tag, m in mans.items():
        name = tag[len(pre) + 1:]
        if name.split("-")[0] in ("p", "e1", "e2"):
            d = load(m)
            if d is not None:
                runs[name] = d
    numbers = {}
    os.makedirs(FIGS, exist_ok=True)
    fs.use_style()
    col = [fs.PAL["blue"], fs.PAL["red"], fs.PAL["green"], fs.PAL["yellow"], fs.PAL["orange"],
           "0.55", "k", "tab:purple"]

    # ---------------------------------------------------------------- P
    if "p-plain" in runs and "p-leak1" in runs:
        ra, rb = runs["p-plain"], runs["p-leak1"]
        same, differ = [], []
        for f in sorted(os.listdir(ra["dir"])):
            fa, fb = os.path.join(ra["dir"], f), os.path.join(rb["dir"], f)
            if not os.path.isfile(fa) or f.startswith(("run.log", "athena", "slurm")) \
                    or f.endswith(".athinput"):
                continue
            (same if os.path.exists(fb) and filecmp.cmp(fa, fb, shallow=False) else differ).append(f)
        ha, hb = ra["horizons"][0], rb["horizons"][0]
        n = min(len(ha["mass"]), len(hb["mass"]))
        dm = np.abs(ha["mass"][:n] - hb["mass"][:n])
        numbers["P"] = dict(runs=[ra["run_id"], rb["run_id"]], identical=same, differ=differ,
                            searches=int(n), t_end=float(ha["t"][n - 1]) if n else None,
                            mass_first=float(ha["mass"][0]) if n else None,
                            mass_last_plain=float(ha["mass"][n - 1]) if n else None,
                            mass_last_leak=float(hb["mass"][n - 1]) if n else None,
                            max_mass_diff=float(dm.max()) if n else None,
                            max_H_diff=float(np.abs(ra["hst"]["H"][:len(rb["hst"]["H"])]
                                                    - rb["hst"]["H"][:len(ra["hst"]["H"])]).max()))
        print("P:", json.dumps(numbers["P"], indent=1))
        fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.9))
        fig.subplots_adjust(left=0.10, right=0.98, bottom=0.17, top=0.95, wspace=0.30)
        ax[0].plot(ha["t"], ha["mass"] - 1.0, color=fs.PAL["blue"], label="plain 1+log")
        ax[0].plot(hb["t"], hb["mass"] - 1.0, color=fs.PAL["red"], ls="--",
                   label=r"with relaxation, $T=1\,m$")
        ax[0].set_xlabel(r"time $t/m$", labelpad=-2)
        ax[0].set_ylabel(r"horizon mass $M_{\rm AH}/m-1$")
        ax[0].legend(fontsize=8)
        ax[1].semilogy(ha["t"][:n], np.maximum(dm, 1e-17), color=fs.PAL["red"])
        ax[1].set_xlabel(r"time $t/m$", labelpad=-2)
        ax[1].set_ylabel("difference of the horizon masses")
        ax[1].set_ylim(1e-17, 1e-3)
        fs.save(fig, os.path.join(FIGS, f"punc_{pre}_p"))
        plt.close(fig)

    # ---------------------------------------------------------------- E1
    e1 = [("e1-eta2", r"$\eta=2$ (reference)"), ("e1-eta20", r"$\eta=20$"),
          ("e1-prof20", r"$\eta_0=20$, profile to 2"), ("e1-eta02", r"$\eta=0.2$"),
          ("e1-prof02", r"$\eta_0=0.2$, profile to 2"),
          ("e1-prof02-w4", r"$\eta_0=0.2$, profile, width 4"),
          ("e1-prof02-w8", r"$\eta_0=0.2$, profile, width 8"),
          ("e1-prof20-w8", r"$\eta_0=20$, profile, width 8")]
    e1 = [(k, lab) for k, lab in e1 if k in runs]
    if e1:
        numbers["E1"] = {}
        fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
        fig.subplots_adjust(left=0.08, right=0.985, bottom=0.17, top=0.95, wspace=0.52)
        for (k, lab), c in zip(e1, col):
            r = runs[k]
            tr, hz = r["trackers"][0], r["horizons"][0]
            v = np.linalg.norm(tr["v"], axis=1)
            ax[0].plot(tr["t"], v, color=c, label=lab)
            ax[1].plot(hz["t"], hz["mass"] - 1.0, color=c)
            ax[2].semilogy(r["hst"]["t"], r["hst"]["H"], color=c)
            numbers["E1"][k] = dict(
                run_id=r["run_id"], t_end=float(tr["t"][-1]),
                speed={f"{t0:g}": float(np.interp(t0, tr["t"], v)) for t0 in (1.6, 3.0, 4.9, 5.0)
                       if tr["t"][-1] >= t0 - 1e-9},
                x_end=float(tr["x"][-1, 0] - tr["x"][0, 0]),
                horizon_found=int(len(hz["mass"])),
                mass_end=float(hz["mass"][-1]) if len(hz["mass"]) else None,
                mass_min=float(hz["mass"].min()) if len(hz["mass"]) else None,
                mass_max=float(hz["mass"].max()) if len(hz["mass"]) else None,
                H_end=float(r["hst"]["H"][-1]), wall=r["wall"], card_hours=r["card_hours"])
        ax[0].set_xlabel(r"time $t/m$", labelpad=-2)
        ax[0].set_ylabel(r"tracker speed $|\beta|$ at the puncture")
        # the legend goes into the free corner of the middle panel (eight entries cover
        # the curves of the left one)
        hd, lb = ax[0].get_legend_handles_labels()
        ax[1].legend(hd, lb, fontsize=6, loc="lower right")
        ax[1].set_xlabel(r"time $t/m$", labelpad=-2)
        ax[1].set_ylabel(r"horizon mass $M_{\rm AH}/m - 1$")
        ax[2].set_xlabel(r"time $t/m$", labelpad=-2)
        ax[2].set_ylabel(r"norm of the Hamiltonian constraint")
        fs.save(fig, os.path.join(FIGS, f"punc_{pre}_e1"))
        plt.close(fig)
        ref = numbers["E1"].get("e1-eta2")
        print("E1: tracker speed at t = 1.6, 3, 4.9, 5 (ratio to eta = 2); horizon mass at the end")
        for k, lab in e1:
            n = numbers["E1"][k]
            row = "  %-10s" % k
            for t0, s in n["speed"].items():
                rr = s / ref["speed"][t0] if ref and t0 in ref["speed"] else float("nan")
                row += "  %s: %.5f (%.3f)" % (t0, s, rr)
            row += "   M_AH %s  H %.3e  searches %d" % (
                "%.5f" % n["mass_end"] if n["mass_end"] else "-", n["H_end"], n["horizon_found"])
            print(row)

    # ---------------------------------------------------------------- E2
    e2 = [("e2-eta2", r"$\eta=2$"), ("e2-eta8", r"$\eta=8$"), ("e2-profile", "profile, 2 and 8"),
          ("e2-profile-w4", "profile, width 4"), ("e2-profile-w8", "profile, width 8")]
    e2 = [(k, lab) for k, lab in e2 if k in runs]
    if e2:
        numbers["E2"] = {}
        fig, ax = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.2))
        fig.subplots_adjust(left=0.10, right=0.98, bottom=0.09, top=0.95, wspace=0.28,
                            hspace=0.26)
        t_end = min(runs[k]["trackers"][0]["t"][-1] for k, _ in e2)
        for (k, lab), c in zip(e2, col):
            r = runs[k]
            rec = dict(run_id=r["run_id"], t_end=float(r["trackers"][0]["t"][-1]),
                       H_end=float(r["hst"]["H"][-1]), H_max=float(r["hst"]["H"].max()),
                       M_end=float(r["hst"]["M"][-1]), wall=r["wall"],
                       card_hours=r["card_hours"], holes=[])
            for n, (name, a0, a1) in enumerate((("heavy hole, $m=1$", ax[0, 0], ax[1, 0]),
                                               ("light hole, $m=0.25$", ax[0, 1], ax[1, 1]))):
                tr, hz = r["trackers"][n], r["horizons"][n]
                v = np.linalg.norm(tr["v"], axis=1)
                a0.plot(tr["t"], v, color=c, label=lab)
                a0.set_title(name, fontsize=9)
                a1.plot(hz["t"], hz["mass"], color=c)
                nsearch = int(np.sum(hz["t"] <= t_end + 1e-9))
                rec["holes"].append(dict(
                    speed_end=float(np.interp(t_end, tr["t"], v)),
                    speed_half=float(np.interp(0.5 * t_end, tr["t"], v)),
                    displacement=float(np.linalg.norm(tr["x"][-1] - tr["x"][0])),
                    horizon_found=int(len(hz["mass"])),
                    mass_end=float(hz["mass"][-1]) if len(hz["mass"]) else None,
                    mass_first=float(hz["mass"][0]) if len(hz["mass"]) else None,
                    searches_to_common_end=nsearch))
            numbers["E2"][k] = rec
        for a0 in ax[0]:
            a0.set_xlabel(r"time $t/M$", labelpad=-2)
            a0.set_ylabel(r"tracker speed")
        for a1 in ax[1]:
            a1.set_xlabel(r"time $t/M$", labelpad=-2)
            a1.set_ylabel(r"horizon mass")
        ax[0, 0].legend(fontsize=8)
        fs.save(fig, os.path.join(FIGS, f"punc_{pre}_e2"))
        plt.close(fig)
        print("E2 (common end t = %.3f):" % t_end)
        for k, lab in e2:
            n = numbers["E2"][k]
            print("  %-11s heavy: v_end %.5f M_AH %s (%d)   light: v_end %.5f M_AH %s (%d)   "
                  "H_end %.3e H_max %.3e" % (
                      k, n["holes"][0]["speed_end"],
                      "%.5f" % n["holes"][0]["mass_end"] if n["holes"][0]["mass_end"] else "-",
                      n["holes"][0]["horizon_found"], n["holes"][1]["speed_end"],
                      "%.5f" % n["holes"][1]["mass_end"] if n["holes"][1]["mass_end"] else "-",
                      n["holes"][1]["horizon_found"], n["H_end"], n["H_max"]))

    with open(os.path.join(HERE, f"punc_numbers_{pre}.json"), "w") as f:
        json.dump(numbers, f, indent=1)
        f.write("\n")


if __name__ == "__main__":
    main()
