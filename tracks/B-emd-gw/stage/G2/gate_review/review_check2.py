#!/usr/bin/env python3
"""Second gate review of B G2 (C2 only, decision 0050): the band strain of the four 128^3
members of the halo box from their Z4c dumps, so that condition (b) (eight against one
particle per cell in the Gamma-driver gauge) and the gauge ratio at both samplings are read.

Readers: the fresh verifier's mesh reader and flat TT projector (stage/G2/verifier/scripts/
vlib.py); of the lead's code only the gauge piece that defines the "corrected" strain
(gw_diag/gwdiag/gauge.py, tt_strain_from_conformal). Band: |k| <= 8 k_f, in the exact
per-mode form (shells nk = rint(|n|), Nyquist planes out) and in the files' form
sum_n S_n / n^2 with S_n the shell sums of p k^2 (compare_legs.py band_rms2).
Predictions RE0-RE4: stage/G2/GATE_REVIEW.md part 2, section P1 (commit 5e8dc1977).

    python3 review_check2.py OUTDIR [--np 3]
"""
import argparse
import glob
import json
import os
import sys
from multiprocessing import Pool

import numpy as np

ROOT = "/data/haiyangw/nrpic"
WT = os.path.join(ROOT, "wt/B-emd-gw")
S = os.path.join(ROOT, "scratch/B-emd-gw")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "verifier", "scripts"))
sys.path.insert(0, os.path.join(WT, "tracks/B-emd-gw/gw_diag"))
sys.path.insert(0, os.path.join(ROOT, "python"))
import vlib  # noqa: E402
from gwdiag import gauge  # noqa: E402
from gwdiag.grid import Grid  # noqa: E402

L = 8.0
NB = 8
G6 = ["z4c_gxx", "z4c_gxy", "z4c_gxz", "z4c_gyy", "z4c_gyz", "z4c_gzz"]
KEYS = [(0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)]
MEMBERS = {
    "zs1": [f"{S}/B-20261123-014847-f295ab4/bin"],
    "gd1": [f"{S}/B-20261124-210431-6bf48af/bin"],
    "zs8": [f"{S}/B-20261124-223926-33194d9/bin", f"{S}/B-20261125-221742-5100a22/p8_cont/bin"],
    "gd8": [f"{S}/B-20261128-034731-640f4f4/bin"],
}
TIMES = (8.0, 10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 21.0)
COR_TIMES = (21.0, 18.0, 14.0, 12.0)          # corrected strain here (a = 132, 100, 64, 49)
PART1 = f"{S}/B-20261128-032405-7c4aa64/review_check.json"


def find_dump(member, t, tol=0.02):
    """The dump of a member whose header time is nearest to t (first directory wins)."""
    best = None
    for d in MEMBERS[member]:
        for fn in sorted(glob.glob(os.path.join(d, "pop.z4cd.*.bin"))):
            i = int(os.path.basename(fn).split(".")[2])
            if abs(i/4.0 - t) > 0.6:          # header read only near the epoch (dumps every 0.25)
                continue
            th = vlib.read_mesh_header(fn)["time"]
            if abs(th - t) <= tol and (best is None or abs(th - t) < abs(best[1] - t)):
                best = (fn, th)
        if best is not None:
            return best
    raise RuntimeError(f"no dump of {member} near t = {t}")


def bands(fields, a):
    """Band power |k| <= 8 k_f of a dict (i, j) -> h_ij: exact per-mode and files' form."""
    p, KX, KY, KZ, nyq = vlib.tt_power(fields, L)
    nn = np.sqrt(KX**2 + KY**2 + KZ**2)
    nk = np.rint(nn).astype(int)
    ok = (~nyq) & (nn > 0)
    exact = float(p[ok & (nk >= 1) & (nk <= NB)].sum())
    k2 = (2*np.pi/L)**2*nn**2
    rho_c = 3.0/(8.0*np.pi)
    spec = np.bincount(nk[ok], weights=(p*k2)[ok]*a/(32*np.pi*rho_c), minlength=nk.max() + 1)
    n = np.arange(len(spec))
    m = (n >= 1) & (n <= NB)
    form = float((spec[m]/n[m]**2).sum())
    return exact, form, float(p[ok].sum())


def measure_arrays(g, a, corrected=True):
    """g: dict name -> array of the conformal metric. Raw and (if asked) corrected bands."""
    raw = {k: g[nm] - (1.0 if k[0] == k[1] else 0.0) for nm, k in zip(G6, KEYS)}
    out = {}
    out["raw_exact"], out["raw_form"], out["raw_all"] = bands(raw, a)
    if not corrected:
        return out
    nz, ny, nx = raw[0, 0].shape
    gt = np.empty((3, 3, nz, ny, nx))
    for (i, j), v in raw.items():
        gt[i, j] = v + (1.0 if i == j else 0.0)
        gt[j, i] = gt[i, j]
    del raw
    grid = Grid((nx, ny, nz), (L, L, L), (0.0, 0.0, 0.0))
    s = gauge.tt_strain_from_conformal(gt, grid)
    cor = {k: s["corrected"][k[0], k[1]] for k in KEYS}
    out["cor_exact"], out["cor_form"], out["cor_all"] = bands(cor, a)
    return out


def job(args):
    member, t, corrected = args
    fn, th = find_dump(member, t)
    d, h = vlib.read_mesh(fn, G6)
    a = float(vlib.scale(h["time"]))
    row = {"member": member, "t_req": t, "file": fn, "t": h["time"], "a": a, "cycle": h["cycle"]}
    row.update(measure_arrays(d, a, corrected))
    print(f"{member} t={h['time']:.4f} a={a:.2f} cor_form={row.get('cor_form', float('nan')):.6e} "
          f"raw_form={row['raw_form']:.6e}", flush=True)
    return row


def analytic_check():
    """RE0: plane TT wave h_xx = -h_yy = A cos(2 pi 2 z / L) on 32^3; band = A^2."""
    n, A = 32, 1e-3
    z = (np.arange(n) + 0.5)*L/n
    Z = np.broadcast_to(z[:, None, None], (n, n, n))
    w = A*np.cos(2*np.pi*2*Z/L)
    g = {nm: np.zeros((n, n, n)) for nm in G6}
    g["z4c_gxx"] = 1.0 + w
    g["z4c_gyy"] = 1.0 - w
    g["z4c_gzz"] = np.ones((n, n, n))
    r = measure_arrays(g, 1.0)
    res = {"A2": A*A, "raw_exact_rel": r["raw_exact"]/(A*A) - 1, "cor_over_raw": r["cor_exact"]/r["raw_exact"] - 1}
    ok = abs(res["raw_exact_rel"]) < 1e-10 and abs(res["cor_over_raw"]) < 1e-6
    res["holds"] = bool(ok)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--np", type=int, default=3)
    ap.add_argument("--from-json", default=None,
                    help="review_check2.json of an earlier run: only the table and the figure")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    if args.from_json:
        res = json.load(open(args.from_json))
        res["from_json"] = args.from_json
        report(res, args.out)
        return
    res = {"RE0": analytic_check()}
    print("RE0", res["RE0"], flush=True)
    if not res["RE0"]["holds"]:
        json.dump(res, open(os.path.join(args.out, "review_check2.json"), "w"), indent=1)
        sys.exit("RE0 refuted: reader not trusted")
    # The gauge piece costs 6-12 min per dump (first run B-20261128-083507-772ea1c, stopped):
    # corrected only at the epochs the predictions judge, those first; raw at every epoch.
    cor_t = set(COR_TIMES)
    order = list(COR_TIMES) + [t for t in TIMES if t not in cor_t]
    jobs = [(m, t, t in cor_t) for t in order for m in ("gd8", "gd1", "zs8", "zs1")]
    with Pool(args.np) as pool:
        rows = []
        for r in pool.imap(job, jobs, chunksize=1):
            rows.append(r)
            with open(os.path.join(args.out, "rows.jsonl"), "a") as f:   # rows as they come
                f.write(json.dumps(r) + "\n")
    res["rows"] = rows
    R = {(r["member"], r["t_req"]): r for r in rows}
    ratios = []
    for t in TIMES:
        e = {"t": t, "a": R["gd1", t]["a"]}
        for kind in ("cor_form", "cor_exact", "raw_form", "raw_exact"):
            if kind not in R["gd1", t]:
                continue
            b = {m: R[m, t][kind] for m in ("gd8", "gd1", "zs8", "zs1")}
            e[f"P_gd_{kind}"] = float(np.sqrt(b["gd8"]/b["gd1"]))
            e[f"P_zs_{kind}"] = float(np.sqrt(b["zs8"]/b["zs1"]))
            e[f"R1_{kind}"] = float(np.sqrt(b["gd1"]/b["zs1"]))
            e[f"R8_{kind}"] = float(np.sqrt(b["gd8"]/b["zs8"]))
        e["dt_max"] = max(abs(R[m, t]["t"] - R["gd1", t]["t"]) for m in ("gd8", "zs8", "zs1"))
        ratios.append(e)
    res["ratios"] = ratios
    if os.path.exists(PART1):
        p1 = json.load(open(PART1))["gauge_leg"]
        cmp_ = []
        for e in [x for x in ratios if "R1_cor_form" in x]:
            j = int(np.argmin([abs(x["a"] - e["a"]) for x in p1]))
            if abs(p1[j]["a"] - e["a"]) < 0.01*e["a"]:
                cmp_.append({"a": e["a"], "a_part1": p1[j]["a"], "R1_mine": e["R1_cor_form"],
                             "R1_part1": p1[j]["rms_cor_ratio"], "diff": e["R1_cor_form"] - p1[j]["rms_cor_ratio"],
                             "R1_raw_mine": e["R1_raw_form"], "R1_raw_part1": p1[j]["rms_raw_ratio"]})
        res["RE3_cmp"] = cmp_
    json.dump(res, open(os.path.join(args.out, "review_check2.json"), "w"), indent=1)
    report(res, args.out)


def report(res, out):
    """Table, the judgements RE1-RE4 as worded in GATE_REVIEW.md part 2, and the figure."""
    nan = float("nan")
    ratios = res["ratios"]
    for e in ratios:
        g = lambda k: e.get(k, nan)  # noqa: E731
        print(f"a={e['a']:7.2f} P_gd cor {g('P_gd_cor_form'):.5f} raw {g('P_gd_raw_form'):.5f} | "
              f"P_zs cor {g('P_zs_cor_form'):.5f} raw {g('P_zs_raw_form'):.5f} | "
              f"R1 cor {g('R1_cor_form'):.5f} R8 cor {g('R8_cor_form'):.5f} | "
              f"R1 raw {g('R1_raw_form'):.5f} R8 raw {g('R8_raw_form'):.5f} | dt {e['dt_max']:.1e}")
    cor = [e for e in ratios if "P_gd_cor_form" in e]
    late = {round(e["a"]): e for e in cor}
    j = {}
    j["RE1_maxdev_P_gd_cor_a_le_64"] = max(abs(e["P_gd_cor_form"] - 1) for e in cor if e["a"] < 65)
    j["RE1_maxdev_P_gd_cor_all"] = max(abs(e["P_gd_cor_form"] - 1) for e in cor)
    j["RE1_maxdev_P_gd_raw_all"] = max(abs(e["P_gd_raw_form"] - 1) for e in ratios)
    j["RE1_holds"] = j["RE1_maxdev_P_gd_cor_a_le_64"] <= 5e-3 and j["RE1_maxdev_P_gd_cor_all"] <= 1e-2
    j["condition_b_refuted"] = any(not 0.95 <= late[a]["P_gd_cor_form"] <= 1.05 for a in (64, 100, 132))
    j["RE2_R8_minus_R1"] = {a: late[a]["R8_cor_form"] - late[a]["R1_cor_form"] for a in (64, 100, 132)}
    j["RE2_fall"] = {a: abs(late[a]["R8_cor_form"] - 1)/abs(late[a]["R1_cor_form"] - 1) for a in (64, 100, 132)}
    j["RE2_holds"] = all(abs(v) <= 0.02 for v in j["RE2_R8_minus_R1"].values())
    j["RE2_refuted"] = all(j["RE2_fall"][a] <= 0.5 for a in (100, 132))
    if "RE3_cmp" in res:
        j["RE3_maxdiff"] = max(abs(c["diff"]) for c in res["RE3_cmp"])
        j["RE3_holds"] = j["RE3_maxdiff"] <= 2e-3
    j["RE4_maxdiff_raw_cor"] = max(abs(e["P_gd_raw_form"] - e["P_gd_cor_form"]) for e in cor)
    j["RE4_holds"] = j["RE4_maxdiff_raw_cor"] <= 3e-3
    res["judgement"] = j
    print(json.dumps(j, indent=1))
    json.dump(res, open(os.path.join(out, "review_check2_report.json"), "w"), indent=1)
    figure(res, out)


def figure(res, out):
    from nrpic import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    rr = res["ratios"]
    nan = float("nan")
    rr = [dict({k: nan for k in ("P_gd_cor_form", "P_zs_cor_form", "R1_cor_form", "R8_cor_form")}, **e) for e in rr]
    a = np.array([e["a"] for e in rr])
    fig, axs = plt.subplots(1, 2, figsize=(8.4, 3.4))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.15, top=0.9, wspace=0.28)
    ax = axs[0]
    ax.axhspan(0.95, 1.05, color="0.92", lw=0)
    ax.axhspan(0.99, 1.01, color="0.82", lw=0)
    ax.axhline(1.0, color="k", lw=0.8)
    ax.plot(a, [e["P_gd_cor_form"] for e in rr], "o", color=fs.PAL["red"], ms=7, label="Gamma driver, corrected")
    ax.plot(a, [e["P_gd_raw_form"] for e in rr], "s--", color=fs.PAL["red"], mfc="none", label="Gamma driver, raw")
    ax.plot(a, [e["P_zs_cor_form"] for e in rr], "^", color=fs.PAL["blue"], label="zero shift, corrected")
    ax.plot(a, [e["P_zs_raw_form"] for e in rr], "v:", color=fs.PAL["blue"], mfc="none", label="zero shift, raw")
    ax.set_xscale("log")
    ax.set_ylim(0.985, 1.005)
    ax.set_xlabel(r"$a$")
    ax.set_ylabel(r"band rms $|k|\leq 8k_f$: 8 / 1 per cell")
    ax.set_title(r"(a) particle number, $128^3$ (shaded: 1 per cent)", fontsize=9)
    ax.legend(frameon=False, fontsize=7, loc="lower left")
    ax = axs[1]
    ax.axhline(1.0, color="k", lw=0.8)
    ax.plot(a, [e["R1_cor_form"] for e in rr], "o", color=fs.PAL["blue"], ms=7, label="1 per cell, corrected")
    ax.plot(a, [e["R8_cor_form"] for e in rr], "s", color=fs.PAL["red"], mfc="none", ms=7, label="8 per cell, corrected")
    ax.plot(a, [e["R1_raw_form"] for e in rr], "-", color=fs.PAL["blue"], lw=1, label="1 per cell, raw")
    ax.plot(a, [e["R8_raw_form"] for e in rr], "--", color=fs.PAL["red"], lw=1, label="8 per cell, raw")
    if "RE3_cmp" in res:
        c = res["RE3_cmp"]
        ax.plot([x["a_part1"] for x in c], [x["R1_part1"] for x in c], "x", color="k", ms=7,
                label="part 1 (lead's files), 1 per cell")
    ax.set_xscale("log")
    ax.set_xlabel(r"$a$")
    ax.set_ylabel(r"band rms: Gamma driver / zero shift")
    ax.set_title("(b) gauge ratio at both samplings", fontsize=9)
    ax.legend(frameon=False, fontsize=7, loc="lower left")
    fs.save(fig, os.path.join(out, "review_check2"))


if __name__ == "__main__":
    main()
