#!/usr/bin/env python3
"""V2 and V3: TT strain of the population box.

(1) From the lead's analysis files (their spectra, my own band sums): 256^3 over 128^3 in the
    Gamma-driver gauge, raw and corrected, at every dump the files share (matched by the
    nearest time, which is what a pairing by a can do), and the gauge-piece share.
(2) From the raw dumps with my own reader and flat TT projector (Nyquist planes excluded):
    the band rms |k| <= 8 k_f (exact per-mode sum, shells nk = rint(|n|)) and the files'
    form sum_n spec[n]/n^2, and the TT measure above 16 k_f, Omega>16 =
    a/(32 pi rho_c) sum_{nk > 16} p k^2 (k = 2 pi n/L), at chosen dumps; for the 128^3 run
    the two dumps around each 256^3 time, interpolated in log to that time.

    python3 v2_strain.py OUTDIR SCRATCH
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vlib  # noqa: E402
import figstyle as fs  # noqa: E402

out, S = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
L = 8.0
RHO_C = 3.0/(8.0*np.pi)
G6 = ["z4c_gxx", "z4c_gxy", "z4c_gxz", "z4c_gyy", "z4c_gyz", "z4c_gzz"]
KEYS = [(0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)]
F = {"gd128": "B-20261125-115558-2ab4161/analysis_gr_gd.json",
     "gd256": "B-20261126-221911-a0531db/analysis_gr_m256gd.json",
     "zs128": "B-20261124-131918-e71996f/analysis_gr.json"}
res = {}


def load(fn):
    d = json.load(open(os.path.join(S, fn)))
    return d[0] if isinstance(d, list) else d


def band_files(spec, nmax=8):
    s = np.asarray(spec, float)
    n = np.arange(len(s))
    m = (n >= 1) & (n <= nmax)
    return float((s[m]/n[m]**2).sum())


def above(spec, n0):
    s = np.asarray(spec, float)
    return float(s[np.arange(len(s)) > n0].sum())


# (1) the analysis files ------------------------------------------------------------------
A = {k: load(v) for k, v in F.items()}
zs = A["zs128"]
if "dumps" not in zs:   # analysis_gr.json may hold several runs
    zs = next(r for r in json.load(open(os.path.join(S, F["zs128"]))) if r.get("name") in ("s014", "base"))
A["zs128"] = zs
for k in A:
    res[k + "_name"] = A[k].get("name")
fine = [d for d in A["gd256"]["dumps"] if "spec_cor" in d]
base = A["gd128"]["dumps"]
pairs = []
for d in fine:
    j = int(np.argmin([abs(b["t"] - d["t"]) for b in base]))
    b = base[j]
    row = {"t256": d["t"], "t128": b["t"], "a256": float(vlib.scale(d["t"])), "a128": float(vlib.scale(b["t"])),
           "raw_ratio": np.sqrt(band_files(d["spec_raw"])/band_files(b["spec_raw"]))}
    if "spec_cor" in b:
        row["cor_ratio"] = np.sqrt(band_files(d["spec_cor"])/band_files(b["spec_cor"]))
        row["G_share_256"] = d["rms_G"]/d["rms_cor"]
        row["G_share_128"] = b["rms_G"]/b["rms_cor"]
        row["Om_all_ratio_cor"] = d["Omega_cor"]/b["Omega_cor"]
        row["Om_gt16_ratio_cor"] = above(d["spec_cor"], 16)/above(b["spec_cor"], 16)
    # time-interpolated 128^3 raw band (log-linear between the two dumps around t256)
    tt = np.array([x["t"] for x in base])
    i1 = int(np.searchsorted(tt, d["t"]))
    if 0 < i1 < len(tt):
        b0, b1 = base[i1-1], base[i1]
        y0, y1 = np.log(band_files(b0["spec_raw"])), np.log(band_files(b1["spec_raw"]))
        yi = y0 + (y1 - y0)*(d["t"] - b0["t"])/(b1["t"] - b0["t"])
        row["raw_ratio_tinterp"] = np.sqrt(band_files(d["spec_raw"])/np.exp(yi))
    pairs.append(row)
res["files_pairs"] = pairs
for lim in (64.5, 133):
    sel = [p for p in pairs if p["a256"] <= lim and "cor_ratio" in p]
    res[f"files_max_dev_cor_a_le_{lim}"] = max(abs(p["cor_ratio"] - 1) for p in sel) if sel else None
    sel2 = [p for p in pairs if p["a256"] <= lim]
    res[f"files_max_dev_raw_a_le_{lim}"] = max(abs(p["raw_ratio"] - 1) for p in sel2)
    sel3 = [p for p in pairs if p["a256"] <= lim and "raw_ratio_tinterp" in p]
    res[f"files_max_dev_raw_tinterp_a_le_{lim}"] = max(abs(p["raw_ratio_tinterp"] - 1) for p in sel3) if sel3 else None
print(json.dumps({k: v for k, v in res.items() if k.startswith("files_max")}, indent=1))

# high-k ratio zero shift over Gamma driver at a ~ 121 from the files
zsd = {round(d["a"], 1): d for d in A["zs128"]["dumps"] if "spec_cor" in d}
gdd = {round(d["a"], 1): d for d in base if "spec_cor" in d}
hk = []
for a_ in sorted(set(zsd) & set(gdd)):
    hk.append({"a": a_, "gt16_cor": above(zsd[a_]["spec_cor"], 16)/above(gdd[a_]["spec_cor"], 16),
               "gt16_raw": above(zsd[a_]["spec_raw"], 16)/above(gdd[a_]["spec_raw"], 16),
               "band8_cor": np.sqrt(band_files(gdd[a_]["spec_cor"])/band_files(zsd[a_]["spec_cor"]))})
res["files_highk_zs_over_gd"] = hk


# (2) raw recomputation from the dumps ----------------------------------------------------
def measure(fn):
    d, h = vlib.read_mesh(fn, G6)
    t = h["time"]
    a = float(vlib.scale(t))
    fields = {k: d[nm] - (1.0 if k[0] == k[1] else 0.0) for nm, k in zip(G6, KEYS)}
    del d
    p, KX, KY, KZ, nyq = vlib.tt_power(fields, L)
    del fields
    nn = np.sqrt(KX**2 + KY**2 + KZ**2)
    nk = np.rint(nn).astype(int)
    ok = (~nyq) & (nn > 0)
    k2 = (2*np.pi/L)**2*nn**2
    band_exact = float(p[ok & (nk >= 1) & (nk <= 8)].sum())
    spec = np.bincount(nk[ok], weights=(p*k2)[ok]*a/(32*np.pi*RHO_C), minlength=nk.max() + 1)
    return {"file": os.path.basename(fn), "t": t, "a": a, "rms_all": float(np.sqrt(p[ok].sum())),
            "band8_exact": band_exact, "band8_filesform": band_files(spec),
            "Om_gt16": above(spec, 16), "Om_all": float(spec.sum())}


R128 = os.path.join(S, "B-20261124-210431-6bf48af", "bin")
R256 = os.path.join(S, "B-20261126-105021-6343c13", "bin")
Z128 = os.path.join(S, "B-20261123-014847-f295ab4", "bin")
sel256 = [int(x) for x in os.environ.get("V2_256", "4,9,16,25").split(",")]
raw = {"gd256": [], "gd128": [], "zs128": []}
for i in sel256:
    m = measure(os.path.join(R256, f"pop.z4cd.{i:05d}.bin"))
    raw["gd256"].append(m)
    t = m["t"]
    i128 = int(round(4*t))          # 128^3 dumps at t = 0.00817 + i/4 for i >= 5
    for j in (i128 - 1, i128):
        raw["gd128"].append(measure(os.path.join(R128, f"pop.z4cd.{j:05d}.bin")))
    print("raw", m)
# the high-k pair at t ~ 20 (a ~ 121)
for j in (80,):
    raw["zs128"].append(measure(os.path.join(Z128, f"pop.z4cd.{j:05d}.bin")))
    raw["gd128"].append(measure(os.path.join(R128, f"pop.z4cd.{j:05d}.bin")))
res["raw"] = raw
json.dump(res, open(os.path.join(out, "v2_strain.json"), "w"), indent=1, default=float)   # before the comparisons


def fdump(run, t):
    lst = A[run]["dumps"]
    j = int(np.argmin([abs(x["t"] - t) for x in lst]))
    return lst[j]


cmp_ = []
for run in ("gd256", "gd128", "zs128"):
    for m in raw[run]:
        f = fdump(run, m["t"])
        cmp_.append({"run": run, "t": m["t"], "t_file": f["t"], "rms_raw_mine": m["rms_all"], "rms_raw_file": f["rms_raw"],
                     "band8_filesform_mine": m["band8_filesform"], "band8_file": band_files(f["spec_raw"]),
                     "rel_rms": m["rms_all"]/f["rms_raw"] - 1,
                     "rel_band": m["band8_filesform"]/band_files(f["spec_raw"]) - 1,
                     "exact_over_filesform": m["band8_exact"]/m["band8_filesform"]})
res["raw_vs_files"] = cmp_
mine = []
for m in raw["gd256"]:
    t = m["t"]
    c = [x for x in raw["gd128"] if abs(x["t"] - t) < 0.3]
    c = sorted(c, key=lambda x: x["t"])[:2]
    t0, t1 = c[0]["t"], c[1]["t"]
    for key in ("band8_exact", "band8_filesform"):
        y = np.log(c[0][key]) + (np.log(c[1][key]) - np.log(c[0][key]))*(t - t0)/(t1 - t0)
        nearest = c[1][key] if abs(t1 - t) < abs(t0 - t) else c[0][key]
        mine.append({"t": t, "a": m["a"], "measure": key, "ratio_tinterp": float(np.sqrt(m[key]/np.exp(y))),
                     "ratio_nearest": float(np.sqrt(m[key]/nearest))})
res["raw_ratios_mine"] = mine
# the two runs write their dumps at times that differ by ~6e-9 (different step histories)
zz, gg = raw["zs128"][-1], [x for x in raw["gd128"] if abs(x["t"] - raw["zs128"][-1]["t"]) < 1e-3][0]
res["raw_highk_zs_over_gd_mine"] = {"t": zz["t"], "a": zz["a"], "Om_gt16_ratio": zz["Om_gt16"]/gg["Om_gt16"],
                                   "band8_gd_over_zs": float(np.sqrt(gg["band8_exact"]/zz["band8_exact"]))}
json.dump(res, open(os.path.join(out, "v2_strain.json"), "w"), indent=1, default=float)
print(json.dumps(res["raw_vs_files"], indent=1, default=float))
print(json.dumps(res["raw_ratios_mine"], indent=1, default=float))
print(res["raw_highk_zs_over_gd_mine"], res["files_highk_zs_over_gd"][-3:])

# figure
fs.use_style()
import matplotlib.pyplot as plt  # noqa: E402
fig, axs = plt.subplots(1, 2, figsize=(8, 3.2))
fig.subplots_adjust(left=0.09, right=0.98, bottom=0.15, top=0.9, wspace=0.3)
ax = axs[0]
ax.plot([p["a256"] for p in pairs], [p["raw_ratio"] for p in pairs], "o-", color=fs.PAL["blue"], label="files, raw, nearest dump")
ax.plot([p["a256"] for p in pairs if "cor_ratio" in p], [p["cor_ratio"] for p in pairs if "cor_ratio" in p], "s--",
        color=fs.PAL["blue"], mfc="none", label="files, corrected, nearest dump")
ax.plot([p["a256"] for p in pairs if "raw_ratio_tinterp" in p], [p["raw_ratio_tinterp"] for p in pairs if "raw_ratio_tinterp" in p],
        "^:", color=fs.PAL["yellow"], label="files, raw, time-interpolated")
mm = [x for x in mine if x["measure"] == "band8_exact"]
ax.plot([x["a"] for x in mm], [x["ratio_tinterp"] for x in mm], "D", color=fs.PAL["red"], ms=7, mfc="none",
        label="my dumps, raw, exact band, interp.")
for y in (0.989, 1.011, 0.972, 1.028):
    ax.axhline(y, **fs.MASK_LINE)
ax.axhline(1.0, color="k", lw=1.0)
ax.set_xscale("log")
ax.set_xlabel(r"$a$")
ax.set_ylabel(r"band rms $|k|\leq 8k_f$: $256^3/128^3$")
ax.set_title("Gamma driver, mesh pair", fontsize=10)
ax.legend(frameon=False, fontsize=7, loc="lower left")
ax = axs[1]
ax.plot([x["a"] for x in hk], [x["gt16_cor"] for x in hk], "o-", color=fs.PAL["blue"], label="files, corrected")
ax.plot([x["a"] for x in hk], [x["gt16_raw"] for x in hk], "s--", color=fs.PAL["blue"], mfc="none", label="files, raw")
r_ = res["raw_highk_zs_over_gd_mine"]
ax.plot([r_["a"]], [r_["Om_gt16_ratio"]], "D", color=fs.PAL["red"], ms=8, mfc="none", label="my dumps, raw")
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel(r"$a$")
ax.set_ylabel(r"$\Omega_{>16k_f}$: zero shift / Gamma driver")
ax.set_title(r"$128^3$, high wave numbers", fontsize=10)
ax.legend(frameon=False, fontsize=8, loc="upper left")
fs.save(fig, os.path.join(out, "v2_strain"))
