#!/usr/bin/env python3
"""Card check K of the initial-data solver, second pass (journal entry 5): the card runs
of a batch job against the processor runs of the same cases.

    nrpic-run submit ... -- python3 tracks/core/analysis/idsolve2/analyze_k.py
        --card <card run directory> --pair <case>=<processor case directory> [...]

Per case: outer iterations of the two records, the largest relative difference of psi
(and of W with the vector part), the far-field line, and for an evolution the region
means of |H| of the last field dump. Numbers: analyze_k_numbers.json; figure
figs/card_k.
"""
import argparse
import glob
import os
import sys

import numpy as np

import lib2
from lib2 import idlib
from nrpic import figstyle as fs  # noqa: E402

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def one(dc, dp):
    out = {}
    recs = glob.glob(os.path.join(dc, "*.idsolve.txt"))
    if not recs:
        return dict(missing="no record in the card run")
    base = os.path.basename(recs[0])[:-len(".idsolve.txt")]
    rc, tc = lib2.summary(os.path.join(dc, base + ".idsolve.txt"))
    rp, tp = lib2.summary(os.path.join(dp, base + ".idsolve.txt"))
    out.update(outer_card=int(rc[-1][0]), outer_proc=int(rp[-1][0]),
               lin_card=int(rc[:, 10].sum()), lin_proc=int(rp[:, 10].sum()),
               far_card=lib2.far_line(os.path.join(dc, base + ".idsolve.txt")),
               far_proc=lib2.far_line(os.path.join(dp, base + ".idsolve.txt")),
               summary_card=tc, summary_proc=tp)
    fc, fp = os.path.join(dc, base + ".idsolve.bin"), os.path.join(dp, base + ".idsolve.bin")
    if os.path.exists(fc) and os.path.exists(fp):
        a, b = idlib.read_idsolve_bin(fc), idlib.read_idsolve_bin(fp)
        out["dpsi_rel"] = float(np.abs(a["psi"] - b["psi"]).max()/np.abs(b["psi"]).max())
        out["H_after_card"] = float(np.abs(a["H"]).max())
        out["H_after_proc"] = float(np.abs(b["H"]).max())
    vc, vp = os.path.join(dc, base + ".idvector.bin"), os.path.join(dp, base + ".idvector.bin")
    if os.path.exists(vc) and os.path.exists(vp):
        a, b = lib2.read_idvector(vc), lib2.read_idvector(vp)
        wmax = max(np.abs(w).max() for w in b["W"])
        out["dW_rel"] = float(max(np.abs(x - y).max() for x, y in zip(a["W"], b["W"]))/wmax)
    dumps = sorted(glob.glob(os.path.join(dp, base + ".field.*.bin")))
    if dumps:
        last = os.path.basename(dumps[-1])
        if os.path.exists(os.path.join(dc, last)):
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            import test_b
            sc, _ = test_b.region_stats(os.path.join(dc, last), 8)
            sp, _ = test_b.region_stats(os.path.join(dp, last), 8)
            out["last_dump"] = last
            out["regions"] = {k: dict(card=sc[k]["H_mean"], proc=sp[k]["H_mean"],
                                      rel=abs(sc[k]["H_mean"] - sp[k]["H_mean"])
                                      / max(sp[k]["H_mean"], 1e-300))
                              for k in test_b.REGIONS}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--card", required=True)
    ap.add_argument("--pair", action="append", default=[])
    a = ap.parse_args()
    res = dict(run=lib2.run_id(), card=a.card, cases={})
    for p in a.pair:
        name, dp = p.split("=", 1)
        res["cases"][name] = one(os.path.join(a.card, name), dp)
        res["cases"][name]["proc_dir"] = dp
        print(name, {k: v for k, v in res["cases"][name].items()
                     if k in ("outer_card", "outer_proc", "dpsi_rel", "dW_rel")}, flush=True)
    root = lib2.run_root()
    out = os.path.join(root, "analyze_k_numbers.json")
    lib2.save_json(out, res)
    fs.use_style()
    fig, ax = plt.subplots(figsize=(fs.COLUMN_WIDTH, 2.4))
    names = list(res["cases"])
    for k, (key, lab, c) in enumerate((("dpsi_rel", r"$\psi$", fs.PAL["blue"]),
                                        ("dW_rel", r"$W$", fs.PAL["red"]))):
        v = [res["cases"][n].get(key, np.nan) for n in names]
        ax.bar(np.arange(len(names)) + 0.35*k, np.maximum(v, 1e-18), 0.35, color=c,
               label=lab + " card against processor")
    for n_i, n in enumerate(names):
        e = res["cases"][n]
        if "regions" in e:
            ax.plot(n_i + 0.7, max(e["regions"]["shell"]["rel"], 1e-18), "k^",
                    label=r"shell mean $|H|$ at $t=2$")
    ax.set_yscale("log")
    ax.set_xticks(np.arange(len(names)) + 0.17)
    ax.set_xticklabels(names, fontsize=6, rotation=20)
    ax.set_ylabel("largest relative difference")
    ax.legend(fontsize=5)
    fig.tight_layout()
    p = os.path.join(root, "card_k")
    fs.save(fig, p)
    plt.close(fig)
    lib2.publish([out, p + ".png", p + ".pdf"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
