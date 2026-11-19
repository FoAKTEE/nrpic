#!/usr/bin/env python3
"""T8: analysis of the two card batches of the card test T8 (predictions P10 of
tracks/core/JOURNAL-bfix.md), on processors.

Stages:
  regress  P10a: the Z4c benchmark of the release and the new card executable, every
           output file byte by byte
  amp      P10b: oblique wave k = (1,1,1), one period, N = 64 and 128, A = 1e-7 and 1e-5
           (this batch) with A = 1e-6 (T4): non-TT part, pointwise error, Psi_4 along k
           and -k, amplitude and phase against the Fourier symbol, second-order fields
  zgrow    P10c: the 256 x 256 x 16 thin box to t = 4, z departure per dump
  circ     P10d: the circular wave on the card against the processor run of T1

    python3 t8_analysis.py --base DIR --new DIR --t4 DIR --t1 DIR [--out DIR]
"""
import argparse
import filecmp
import glob
import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import bfix_common as bc  # noqa: E402
from bfix_common import athena_bin, fs  # noqa: E402
import t1_linear_wave as t1  # noqa: E402
import t3_thin_jitter as t3  # noqa: E402
from t4b_zdep import zstats  # noqa: E402

K = (1, 1, 1)
AMPS_NEW = ("1e-07", "1e-05")
# directory names of the batch list t8_new.list (lw64_a1e-7, ...)
AMP_DIR = {"1e-07": "1e-7", "1e-05": "1e-5"}


def is_log(name):
    b = os.path.basename(name)
    return b.startswith("athena") and (b.endswith(".log") or b.endswith(".csv"))


def stage_regress(res, base, new):
    da, db = os.path.join(base, "bench"), os.path.join(new, "bench")
    names = sorted(set(os.path.relpath(p, d) for d in (da, db)
                       for p in glob.glob(os.path.join(d, "**", "*"), recursive=True)
                       if os.path.isfile(p) and not is_log(p)))
    only = [n for n in names if not (os.path.exists(os.path.join(da, n))
                                     and os.path.exists(os.path.join(db, n)))]
    differ = [n for n in names if n not in only
              and not filecmp.cmp(os.path.join(da, n), os.path.join(db, n), shallow=False)]
    r = {"files": names, "n_files": len(names), "only_in_one": only, "differing": differ,
         "bytes": int(sum(os.path.getsize(os.path.join(da, n)) for n in names
                          if os.path.exists(os.path.join(da, n))))}
    res["regress"] = r
    print("regress:", {k: v for k, v in r.items() if k != "files"}, r["files"])


def second_order_fields(path):
    d = bc.z4c_from_bin(athena_bin.read_bin(path))
    return {"max_abs_alpha_minus_1": float(np.abs(d["alpha"] - 1).max()),
            "max_abs_chi_minus_1": float(np.abs(d["chi"] - 1).max()),
            "max_abs_Khat": float(np.abs(d["Khat"]).max()),
            "max_abs_Theta": float(np.abs(d["Theta"]).max()),
            "max_abs_Gam": float(max(np.abs(d[f"Gam{c}"]).max() for c in "xyz"))}


def stage_amp(res, B, new, t4):
    with open(os.path.join(t4, "results_t4.json")) as f:
        r4 = json.load(f)["evol"]
    r = {}
    for n in (64, 128):
        rows = {}
        # A = 1e-6 from T4
        last6 = dict(r4[str(n)]["last"])
        last6.update(second_order_fields(sorted(glob.glob(
            os.path.join(t4, "evol", f"N{n}", "bin", "*.z4c.*.bin")))[-1]))
        rows["1e-06"] = {"last": last6, "pred_gain_abs_minus_1": r4[str(n)]["pred_gain_abs_minus_1"],
                         "pred_gain_phase": r4[str(n)]["pred_gain_phase"],
                         "errs_dat_rms_L1": r4[str(n)]["errs_dat_rms_L1"], "source": "T4"}
        for a in AMPS_NEW:
            rd = os.path.join(new, f"lw{n}_a{AMP_DIR[a]}")
            files = sorted(glob.glob(os.path.join(rd, "bin", "*.z4c.*.bin")))
            last, _ = t1.analyse_dump(B, files[-1], K, float(a), 0.0, 0.0)
            last.update(second_order_fields(files[-1]))
            pa, pp = t1.predict3d(B, K, n, last["t"], last["cycle"])
            with open(os.path.join(rd, "lwo-errs.dat")) as f:
                errs = f.read().split("\n")[1].split()
            rows[a] = {"last": last, "pred_gain_abs_minus_1": pa, "pred_gain_phase": pp,
                       "errs_dat_rms_L1": float(errs[4]), "source": "T8"}
        for a, v in rows.items():
            l = v["last"]
            v["gain_minus_pred"] = l["gain_abs_minus_1"] - v["pred_gain_abs_minus_1"]
            v["phase_minus_pred"] = l["gain_phase"] - v["pred_gain_phase"]
            print(f"amp N={n} A={a}: nonTT/A {l['nonTT_over_A']:.3e}, gt err/A "
                  f"{l['max_err_gt_over_A']:.3e}, psi4 err {l['psi4_err_rel']:.3e}, psi4 rev "
                  f"{l['psi4_reverse_over_max']:.3e}, gain-1 {l['gain_abs_minus_1']:+.3e} (pred "
                  f"{v['pred_gain_abs_minus_1']:+.3e}), phase {l['gain_phase']:+.3e} (pred "
                  f"{v['pred_gain_phase']:+.3e}), |alpha-1| {l['max_abs_alpha_minus_1']:.3e}, "
                  f"|Khat| {l['max_abs_Khat']:.3e}, |Gam| {l['max_abs_Gam']:.3e}")
        r[str(n)] = rows
    # ratios between amplitudes
    ratios = {}
    for n in ("64", "128"):
        rr = {}
        for q in ("nonTT_over_A", "max_err_gt_over_A", "psi4_err_rel", "psi4_reverse_over_max",
                  "max_abs_alpha_minus_1", "max_abs_Khat", "max_abs_Gam"):
            v = {a: r[n][a]["last"][q] for a in r[n]}
            rr[q] = {"1e-05/1e-06": v["1e-05"]/v["1e-06"], "1e-07/1e-06": v["1e-07"]/v["1e-06"]}
        ratios[n] = rr
        print("ratios N", n, json.dumps(rr))
    res["amp"] = r
    res["amp_ratios"] = ratios


def stage_zgrow(res, rd, key="zgrow"):
    """z departure per z4c dump of the thin-box run in rd (stored as res[key])."""
    files = sorted(glob.glob(os.path.join(rd, "bin", "east.z4c.0*.bin")))
    groups = {"At": ["Axx", "Axy", "Ayy", "Azz"], "Axz": ["Axz"], "gt": ["gxx", "gxy", "gyy", "gzz"],
              "gxz": ["gxz"], "chi": ["chi"], "alpha": ["alpha"], "Khat": ["Khat"],
              "Theta": ["Theta"], "Gam": ["Gamx", "Gamy"], "Gamz": ["Gamz"]}
    ser = {g: [] for g in groups}
    rel = {g: [] for g in groups}
    ts, cyc = [], []
    for p in files:
        d = athena_bin.read_bin(p)
        ts.append(float(d["time"]))
        cyc.append(int(d["cycle"]))
        for g, vs in groups.items():
            st = [zstats(np.asarray(d["z4c_" + v], float)) for v in vs]
            ser[g].append(max(s["absdev"] for s in st))
            rel[g].append(max((s["rel_xyvar"] if np.isfinite(s["rel_xyvar"]) else 0.0) for s in st))
    e = []
    for p in sorted(glob.glob(os.path.join(rd, "bin", "east.tmunu.0*.bin"))):
        d = athena_bin.read_bin(p)
        s = zstats(np.asarray(d["tmunu_E"], float))
        e.append({"t": float(d["time"]), **s})
    snaps = sorted(glob.glob(os.path.join(rd, "east.part.*.bin")))
    _, ds, _ = t3.read_snapshot(snaps[-1])
    with open(os.path.join(rd, "athena.log")) as f:
        log = f.read()

    def last(key):
        v = [ln for ln in log.splitlines() if key in ln]
        return float(v[-1].split("=")[1]) if v else None

    gfac = {g: (np.array(ser[g][-8:])/np.maximum(np.array(ser[g][-9:-1]), 1e-300)).tolist()
            for g in groups}
    i1 = int(np.argmin(np.abs(np.array(ts) - 1.0)))
    r = {"t": ts, "cycle": cyc, "absdev": ser, "rel_xyvar": rel, "E": e,
         "growth_per_dump_last8": gfac,
         "growth_t1_to_end": {g: ser[g][-1]/max(ser[g][i1], 1e-300) for g in groups},
         "particles_end": int(len(ds)), "a_end": None,
         "zone_cycles_per_cpu_second": last("zone-cycles/cpu_second"),
         "cpu_s": last("cpu time used"),
         "terminated": [ln for ln in log.splitlines() if "Terminating" in ln][-1:]}
    dl = bc.z4c_from_bin(athena_bin.read_bin(files[-1]))
    r["a_end"] = float(1.0/np.sqrt(dl["chi"].mean()))
    res[key] = r
    print(f"{key}: t", [round(t, 3) for t in ts])
    for g in groups:
        print(f"  {g:6s} absdev", " ".join(f"{v:.2e}" for v in ser[g]))
    print("  growth t=1 to end", {g: f"{v:.3g}" for g, v in r["growth_t1_to_end"].items()})
    print("  particles", r["particles_end"], "a_end", r["a_end"], r["terminated"],
          "zone-cycles/s", r["zone_cycles_per_cpu_second"])


def stage_circ(res, new, t1dir):
    rc = os.path.join(new, "circ16")
    rp = os.path.join(t1dir, "pol", "circular")
    out = {}
    for tag, idx in (("first", 0), ("last", -1)):
        fc = sorted(glob.glob(os.path.join(rc, "bin", "*.z4c.*.bin")))[idx]
        fp = sorted(glob.glob(os.path.join(rp, "bin", "*.z4c.*.bin")))[idx]
        dc, dp = bc.z4c_from_bin(athena_bin.read_bin(fc)), bc.z4c_from_bin(athena_bin.read_bin(fp))
        A = 1e-6
        o = {"t": [dc["time"], dp["time"]], "cycle": [dc["cycle"], dp["cycle"]],
             "gt_over_A": float(np.abs(bc.tensor(dc, "g") - bc.tensor(dp, "g")).max()/A),
             "At_over_A": float(np.abs(bc.tensor(dc, "A") - bc.tensor(dp, "A")).max()/A)}
        o["all_fields_max_abs"] = float(max(np.abs(dc[v] - dp[v]).max() for v in dc
                                            if isinstance(dc[v], np.ndarray) and dc[v].ndim == 3))
        # per field: largest |card - processor| and largest |value| (processor)
        o["per_field"] = {v: {"max_abs_diff": float(np.abs(dc[v] - dp[v]).max()),
                              "max_abs": float(np.abs(dp[v]).max())}
                          for v in sorted(dc) if isinstance(dc[v], np.ndarray) and dc[v].ndim == 3}
        out[tag] = o
    errs = {}
    for tag, d in (("card", rc), ("processor", rp)):
        with open(os.path.join(d, "lwo-errs.dat")) as f:
            errs[tag] = float(f.read().split("\n")[1].split()[4])
    out["errs_rms_L1"] = errs
    out["errs_rel_diff"] = abs(errs["card"] - errs["processor"])/errs["processor"]
    res["circ"] = out
    print("circ:", json.dumps(out))


def figures(res, out):
    fs.use_style()
    paths = []
    if "amp" in res:
        fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.4))
        fig.subplots_adjust(left=0.09, right=0.98, bottom=0.15, top=0.93, wspace=0.3)
        A = np.array([1e-7, 1e-6, 1e-5])
        keys = ["1e-07", "1e-06", "1e-05"]
        ax = axs[0]
        for n, mk in (("64", "o"), ("128", "s")):
            r = res["amp"][n]
            ax.loglog(A, [r[k]["last"]["nonTT_over_A"] for k in keys], mk + "-",
                      color=fs.PAL["red"], label=f"non-TT part / A, N = {n}")
            ax.loglog(A, [r[k]["last"]["max_err_gt_over_A"] for k in keys], mk + "--",
                      mfc="none", color=fs.PAL["blue"], label=f"max |gt - exact| / A, N = {n}")
            ax.loglog(A, [r[k]["last"]["max_abs_alpha_minus_1"]/k2 for k, k2 in zip(keys, A)],
                      mk + ":", color=fs.PAL["green"], label=f"max |alpha - 1| / A, N = {n}")
        ax.loglog(A, 3.4e-6*A/1e-6, color="k", lw=0.7, label=r"$\propto A$")
        ax.set_xlabel("amplitude A")
        ax.set_ylabel("after one period")
        ax.legend(fontsize=6, loc="upper left")
        ax = axs[1]
        for n, mk in (("64", "o"), ("128", "s")):
            r = res["amp"][n]
            ax.loglog(A, [r[k]["last"]["psi4_reverse_over_max"] for k in keys], mk + "-",
                      color=fs.PAL["red"], label=f"Psi_4 along -k / max, N = {n}")
            ax.loglog(A, [r[k]["last"]["psi4_err_rel"] for k in keys], mk + "--", mfc="none",
                      color=fs.PAL["yellow"], label=f"Psi_4 error, N = {n}")
            ax.loglog(A, [abs(r[k]["gain_minus_pred"]) for k in keys], mk + ":",
                      color=fs.PAL["blue"], label=f"|amplitude error - symbol|, N = {n}")
        ax.loglog(A, 7.8e-7*1e-6/A, color="k", lw=0.7, label=r"$\propto 1/A$")
        ax.set_xlabel("amplitude A")
        ax.legend(fontsize=6, loc="lower left")
        paths += fs.save(fig, os.path.join(out, "t8_amplitude"))
    if "zgrow" in res:
        z = res["zgrow"]
        fig, ax = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH + 1.0, 3.4))
        fig.subplots_adjust(left=0.15, right=0.97, bottom=0.14, top=0.95)
        cols = {"At": fs.PAL["red"], "Axz": fs.PAL["red"], "gt": fs.PAL["blue"],
                "gxz": fs.PAL["blue"], "Gam": fs.PAL["green"], "Gamz": fs.PAL["green"],
                "Khat": fs.PAL["yellow"], "Theta": fs.PAL["orange"], "chi": "k"}
        for g, c in cols.items():
            ls = "--" if g in ("Axz", "gxz", "Gamz") else "-"
            ax.semilogy(z["t"], np.maximum(z["absdev"][g], 1e-22), ls, color=c, marker=".",
                        label=g)
        ax.axhline(1e-9, color="k", lw=0.7, ls=":")
        ax.set_xlabel("conformal time")
        ax.set_ylabel("largest |f(z) - f(z_0)|")
        ax.set_ylim(1e-20, 1e-6)
        ax.legend(fontsize=6, ncol=3, loc="lower right")
        paths += fs.save(fig, os.path.join(out, "t8_zgrow"))
    if "circ" in res and "per_field" in res["circ"]["last"]:
        pf = res["circ"]["last"]["per_field"]
        names = list(pf)
        x = np.arange(len(names))
        dif = np.array([pf[v]["max_abs_diff"] for v in names])
        mx = np.array([pf[v]["max_abs"] for v in names])
        eps = np.finfo(float).eps
        fig, ax = plt.subplots(1, 1, figsize=(fs.FULL_WIDTH, 3.0))
        fig.subplots_adjust(left=0.09, right=0.98, bottom=0.2, top=0.93)
        ax.semilogy(x, np.maximum(dif, 1e-22), "o", color=fs.PAL["red"],
                    label="max |card - processor| at t = 0.577 (cycle 37)")
        ax.semilogy(x, np.maximum(eps*mx, 1e-22), "_", ms=12, color="k",
                    label="eps x max |field|")
        ax.axhline(1e-9*1e-6, color=fs.PAL["blue"], lw=0.7, ls=":",
                   label="bound of P10d (1e-9 A)")
        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=60, fontsize=6)
        ax.set_ylabel("absolute")
        ax.set_ylim(1e-22, 1e-12)
        ax.legend(fontsize=6, loc="lower right")
        paths += fs.save(fig, os.path.join(out, "t8_circ"))
    return paths


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--new", required=True)
    ap.add_argument("--t4", required=True)
    ap.add_argument("--t1", required=True)
    ap.add_argument("--bdir", default=bc.B_DEFAULT)
    ap.add_argument("--stages", default="regress,amp,zgrow,circ")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = bc.out_dir(a.out)
    B = bc.track_b(a.bdir)
    res = {"meta": {"base": a.base, "new": a.new, "t4": a.t4, "t1": a.t1,
                    "commit": bc.git_rev()}}
    st = a.stages.split(",")
    resfile = os.path.join(out, "results_t8.json")
    if "regress" in st:
        stage_regress(res, a.base, a.new)
        bc.save_json(res, resfile)
    if "circ" in st:
        stage_circ(res, a.new, a.t1)
        bc.save_json(res, resfile)
    if "amp" in st:
        stage_amp(res, B, a.new, a.t4)
        bc.save_json(res, resfile)
    if "zgrow" in st:
        stage_zgrow(res, os.path.join(a.new, "big4"))
        bc.save_json(res, resfile)
    print("figures:", figures(res, out))


if __name__ == "__main__":
    main()
