#!/usr/bin/env python3
"""Judge the card check of branch core/faces-finder (card.list; prediction K of
tracks/core/JOURNAL-faces-finder.md, entry 5).  Nothing is run here.

    card_check.py --card CARD_RUN_DIR --dep DEP_COMPARE_RUN --cons COMP_CONS_RUN \
                  --s1l S1L_SHEAR_RUN --out DIR

K1  dl_cic, dl_cic_fs, dl_pcs_comp: E on the line within 1e-12 of the processor run of
    this branch in every cell; cic_fs equals cic within 1e-13; line sum of pcs_comp 32
    within 1e-10
K2  cons_pcs_c2, cons_pcs_c2_lim, cons_cic_plain: integral of E against the sum of m W
    within 1e-12 at every record
K3  s1l_shear: every member found on processors is found, area mass within 1e-6
    relative, column 16 within 1e-4, scan start within 1e-6
K4  rst_add: status 0, a status file with a record, the log line of the added parameter
Writes DIR/card_check.json and DIR/fig_card_check.{pdf,png}; exit 0 if all hold.
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))


def line(d):
    f = sorted(glob.glob(os.path.join(d, "**", "*tmunu_E*.tab"), recursive=True))[-1]
    rows = []
    for ln in open(f):
        if ln.startswith("#") or not ln.strip():
            continue
        p = ln.split()
        rows.append((float(p[2]), float(p[-1])))
    rows.sort()
    return np.array(rows)


def status_rows(d):
    out = {}
    for f in glob.glob(os.path.join(d, "**", "*horizon_status_*.txt"), recursive=True):
        n = int(f.rsplit("_", 1)[1].split(".")[0])
        rows = [ln.split("#")[0].split() for ln in open(f) if not ln.startswith("#")]
        if rows:
            out[n] = [float(v) for v in rows[-1]]
    return out


def main():
    ap = argparse.ArgumentParser()
    for k in ("card", "dep", "cons", "s1l", "out"):
        ap.add_argument("--" + k, required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res, chk = {}, {}
    st = glob.glob(os.path.join(a.card, "*.status"))
    res["status_lines"] = open(st[0]).read().split("\n") if st else []
    chk["status"] = bool(st) and all("rc=0" in ln for ln in res["status_lines"] if ln.strip())

    # K1
    k1, dev = True, {}
    for c in ("cic", "cic_fs", "pcs_comp"):
        card = line(os.path.join(a.card, "dl_" + c))
        cpu = line(os.path.join(a.dep, "new", c))
        d = float(np.max(np.abs(card[:, 1] - cpu[:, 1])))
        dev[c] = d
        k1 &= d < 1e-12
    cc, cf = line(os.path.join(a.card, "dl_cic")), line(os.path.join(a.card, "dl_cic_fs"))
    dev["cic_fs_minus_cic"] = float(np.max(np.abs(cc[:, 1] - cf[:, 1])))
    pc = line(os.path.join(a.card, "dl_pcs_comp"))
    dev["line_sum_pcs_comp"] = float(np.sum(pc[:, 1] * np.where(np.abs(pc[:, 0]) < 8.0, 0.5, 1.0)))
    k1 &= dev["cic_fs_minus_cic"] < 1e-13 and abs(dev["line_sum_pcs_comp"] - 32.0) < 1e-10
    res["K1"], chk["K1"] = dev, bool(k1)

    # K2
    k2, errs = True, {}
    for c in ("pcs_c2", "pcs_c2_lim", "cic_plain"):
        h = np.loadtxt(glob.glob(os.path.join(a.card, "cons_" + c, "*.nrpic.hst"))[0],
                       comments="#", ndmin=2)
        e = np.abs(h[:, 8] - h[:, 4]) / np.abs(h[:, 4])
        hc = np.loadtxt(os.path.join(a.cons, c, "new", "dep.nrpic.hst"), comments="#",
                        ndmin=2)
        errs[c] = {"records": int(len(e)), "max_rel_err_E": float(e.max()),
                   "processor_records": int(len(hc)), "series": e.tolist()}
        k2 &= e.max() < 1e-12 and len(e) == len(hc)
    res["K2"], chk["K2"] = errs, bool(k2)

    # K3
    sc, sp = status_rows(os.path.join(a.card, "s1l_shear")), status_rows(a.s1l)
    k3, rows = len(sp) > 0, {}
    for n, p in sp.items():
        c = sc.get(n)
        r = {"processor": p[:8] + p[15:], "card": (c[:8] + c[15:]) if c else None}
        ok = c is not None and int(c[2]) == int(p[2])
        if ok and int(p[2]) == 1:
            ok &= abs(c[6] - p[6]) / p[6] < 1e-6
            if len(p) > 15 and len(c) > 15:
                ok &= abs(c[15] - p[15]) < 1e-4 and abs(c[16] - p[16]) < 1e-6
        r["ok"] = bool(ok)
        rows[n] = r
        k3 &= ok
    res["K3"], chk["K3"] = rows, bool(k3)

    # K4
    d = os.path.join(a.card, "rst_add")
    logs = glob.glob(os.path.join(d, "*.log")) + glob.glob(os.path.join(d, "*.out"))
    txt = "".join(open(f, errors="replace").read() for f in logs)
    txt += "".join(open(f, errors="replace").read()
                   for f in glob.glob(os.path.join(a.card, "*.out")))
    srow = status_rows(d)
    res["K4"] = {"status_records": len(srow),
                 "log_line": "added on restart from the command line: <fastflow> diagnostics"
                             in txt}
    chk["K4"] = len(srow) >= 1 and res["K4"]["log_line"]
    res["checks"] = chk
    res["verdict"] = "PASS" if all(chk.values()) else "FAIL"
    json.dump(res, open(os.path.join(a.out, "card_check.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "K2"}, indent=1))
    for c, v in errs.items():
        print(c, v["records"], v["max_rel_err_E"])

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle
    figstyle.use_style()
    cols = figstyle.series_colors(3)
    fig, axs = plt.subplots(1, 3, figsize=(12.0, 3.3))
    for col, c in zip(cols, ("cic", "cic_fs", "pcs_comp")):
        card = line(os.path.join(a.card, "dl_" + c))
        cpu = line(os.path.join(a.dep, "new", c))
        axs[0].plot(card[:, 0], card[:, 1] - cpu[:, 1], "o-", ms=2.5, lw=0.8, color=col,
                    label=c)
    axs[0].set_xlabel(r"$x^1$")
    axs[0].set_ylabel("E on the line, card minus processors")
    axs[0].legend(fontsize=7)
    axs[0].set_title("(a) uniform lattice across a level face", fontsize=9)
    for col, (c, v) in zip(cols, errs.items()):
        axs[1].semilogy(np.maximum(v["series"], 1e-18), "o-", ms=2.5, lw=0.8, color=col,
                        label=c)
    axs[1].axhline(1e-12, color="0.6", lw=0.6, ls="--")
    axs[1].set_xlabel("record")
    axs[1].set_ylabel(r"$|\int E\,dV - \sum mW|/\sum mW$ on the card")
    axs[1].legend(fontsize=7)
    axs[1].set_title("(b) compensated deposit, refined mesh", fontsize=9)
    ns = sorted(rows)
    dm = [abs(rows[n]["card"][6] - rows[n]["processor"][6]) / rows[n]["processor"][6]
          if rows[n]["card"] else np.nan for n in ns]
    axs[2].semilogy(ns, np.maximum(dm, 1e-18), "o", color=cols[0])
    axs[2].axhline(1e-6, color="0.6", lw=0.6, ls="--")
    axs[2].set_xlabel("horizon of the S1L probe (weighted flow)")
    axs[2].set_ylabel("area mass, |card - processors| / mass")
    axs[2].set_title("(c) finder on Track A's file", fontsize=9)
    fig.tight_layout()
    figstyle.save(fig, os.path.join(a.out, "fig_card_check"))
    print("CARD CHECK", res["verdict"])
    return 0 if res["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
