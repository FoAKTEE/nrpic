#!/usr/bin/env python3
"""Re-measure, from the run files of the earlier campaign (runs/, untracked, read-only),
the numbers that LADDER.md quotes for the self-gravitating rows of the ladder, and draw
one overview figure. Nothing is simulated; the output is an analysis run.

    python3 ladder_measure.py [--run-id ID]   # registers the run, writes
        scratch/core/<ID>/ladder_numbers.json and figs/ladder_overview_<ID>.{pdf,png}
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "regress"))
import lib  # noqa: E402

sys.path.insert(0, str(lib.WT / "cosmo" / "ic"))
sys.path.insert(0, str(lib.WT / "python"))
from nrp_io import read_history  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

R = lib.OLD_RUNS
SOURCES = {
    "os_nocap_sc": (R / "os" / "nocap_sc", "os"),
    "os_published_rule_nocap_v4": (R / "os" / "nocap_v4", "os"),
    "prolate_e09_v8": (R / "prolate" / "e09_v8", "prol"),
    "st_yc0900_v4": (R / "st" / "yc0900_v4", "st"),
    "st_yc0819_v4": (R / "st" / "yc0819_v4", "st"),
    "st_yc0605_v5": (R / "st" / "yc0605_v5", "st"),
    "st_yc0500_v5": (R / "st" / "yc0500_v5", "st"),
    "st_yc0283_v5": (R / "st" / "yc0283_v5", "st"),
    "st_migration_yc0500_v4": (R / "st" / "migration_yc0500_v4", "st"),
    "st_yc0756_unpert": (R / "st" / "yc0756_unpert", "st"),
}


def horizon(d, base):
    f = d / f"{base}.horizon_summary_0.txt"
    if not f.exists():
        return None, None
    a = np.loadtxt(f, comments="#", ndmin=2)
    t, m = a[:, 1], a[:, 2]
    _, idx = np.unique(t[::-1], return_index=True)
    idx = len(t) - 1 - idx
    t, m = t[idx], m[idx]
    ok = np.isfinite(m)
    return t[ok], m[ok]


def measure_one(d, base):
    h = read_history(d / f"{base}.nrpic.hst")
    t = h["time"]
    out = dict(t_end=float(t[-1]), n_start=int(h["np"][0]), n_end=int(h["np"][-1]),
               alpha_c_start=float(h["alpha_probe"][0]),
               alpha_c_min=float(h["alpha_probe"].min()),
               alpha_c_max=float(h["alpha_probe"].max()),
               alpha_c_end=float(h["alpha_probe"][-1]),
               n_escaped_end=int(h["n_escaped"][-1]) if "n_escaped" in h else None)
    th, mh = horizon(d, base)
    if th is not None and len(th):
        out.update(t_first_ah=float(th[0]), m_first_ah=float(mh[0]),
                   m_ah_max=float(mh.max()), t_m_ah_max=float(th[np.argmax(mh)]),
                   m_ah_last=float(mh[-1]), t_ah_last=float(th[-1]),
                   max_abs_m_minus_1_after_first=float(np.max(np.abs(mh - 1.0))))
    else:
        out.update(t_first_ah=None)
    return out, h, (th, mh)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id")
    a = ap.parse_args()
    run_id = a.run_id or lib.new_run_id()
    out = lib.run_dir(run_id)
    lib.write_manifest(run_id, kind="scouting", test="ladder re-measurement",
                       purpose="Re-read the numbers of the self-gravitating ladder rows from the "
                               "earlier run files for LADDER.md",
                       command=[f"python3 {Path(__file__).resolve()} --run-id {run_id}"],
                       cwd=str(HERE),
                       inputs=[lib.file_record(Path(__file__).resolve())] +
                              [dict(path=str(d), note="earlier run directory (read only)")
                               for d, _ in SOURCES.values()],
                       resources=dict(device="processor", cores=1, card_hours=0.0),
                       status="running")
    t0 = time.time()
    res, hists = {}, {}
    for k, (d, base) in SOURCES.items():
        if not (d / f"{base}.nrpic.hst").exists():
            res[k] = dict(missing=str(d))
            continue
        res[k], h, ah = measure_one(d, base)
        hists[k] = (h, ah)
    # derived quantities quoted in LADDER.md
    mg = hists["st_migration_yc0500_v4"][0]
    sel = (mg["time"] >= 1500.0) & (mg["time"] <= 2500.0)
    res["st_migration_yc0500_v4"]["alpha_c_mean_1500_2500"] = float(np.mean(mg["alpha_probe"][sel]))
    osn = hists["os_nocap_sc"][1]
    near = lambda tq: float(osn[1][np.argmin(np.abs(osn[0] - tq))])
    res["os_nocap_sc"]["m_ah_at"] = {f"{tq:g}": near(tq) for tq in (20.0, 40.0, 59.5)}
    (out / "ladder_numbers.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))
    figure(run_id, hists)
    lib.write_manifest(run_id, status="finished", wall_time_s=round(time.time() - t0, 2),
                       outputs=[str(out / "ladder_numbers.json")])


def figure(run_id, hists):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.6))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.09, top=0.97, hspace=0.30, wspace=0.27)
    ax = axs[0, 0]
    for k, c, lab in (("os_nocap_sc", fs.PAL["red"], "corrected lattice masses"),
                      ("os_published_rule_nocap_v4", fs.PAL["blue"], "published lattice rule")):
        th, mh = hists[k][1]
        ax.plot(th, mh, color=c, label=lab)
    ax.axhspan(1 - 1e-3, 1 + 1e-3, color="grey", alpha=0.15, lw=0)
    ax.axhline(1.0, **fs.GUIDE)
    ax.set_ylim(0.995, 1.015)
    ax.set_xlabel(r"$t/M$")
    ax.set_ylabel(r"dust collapse $M_{\rm AH}/M$")
    ax.legend(loc="upper right")
    ax = axs[0, 1]
    th, mh = hists["prolate_e09_v8"][1]
    ax.plot(th, mh, color=fs.PAL["red"])
    ax.axhline(1.0, **fs.GUIDE)
    ax.axvline(32.0, **fs.MASK_LINE)
    ax.set_xlabel(r"$t/M$")
    ax.set_ylabel(r"prolate collapse $M_{\rm AH}/M$")
    ax = axs[1, 0]
    for i, k in enumerate(("st_yc0900_v4", "st_yc0819_v4", "st_yc0605_v5", "st_yc0500_v5",
                           "st_yc0283_v5")):
        h = hists[k][0]
        ax.plot(h["time"], h["alpha_probe"], color=fs.SERIES[i], lw=1.0,
                label=r"$y_c=$" + k.split("yc")[1][:4].replace("0", "0.", 1))
    for tq, c in ((109.0, fs.SERIES[2]), (73.0, fs.SERIES[3])):
        ax.axvline(tq, color=c, lw=1.0, ls="--")
    ax.set_xlabel(r"$t/M$")
    ax.set_ylabel(r"central lapse $\alpha_c$")
    ax.set_ylim(0, 1.05)
    ax.legend(loc="lower left", ncol=2, fontsize=8)
    ax = axs[1, 1]
    h = hists["st_migration_yc0500_v4"][0]
    ax.plot(h["time"], h["alpha_probe"], color=fs.PAL["red"], lw=1.0)
    ax.axhline(0.833530, **fs.GUIDE)
    ax.set_xlabel(r"$t/M$")
    ax.set_ylabel(r"migration $y_c=0.5$: $\alpha_c$")
    fs.save(fig, str(lib.FIGS / f"ladder_overview_{run_id}"))


if __name__ == "__main__":
    main()
