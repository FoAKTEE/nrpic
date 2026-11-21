"""A1: ledger rows of the second round (197, 200, 204, 205, 207-215) and of the spatial gauge
(116-123) from the M1 per-dump tables (own measurement), with figures.

Usage: python a1_rows.py <M1a run dir> <M1b run dir>
Definitions as in the ledger captions (note/tables/ledger.tex) and the note's text; where a
caption leaves a choice open (interpolation, window edge), the choice is stated in the output.
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vlib  # noqa: E402

OUT = os.environ.get("NRPIC_RUN_DIR", "/data/haiyangw/nrpic/scratch/B-emd-gw/tmp/a1")
os.makedirs(OUT, exist_ok=True)
MA, MB = sys.argv[1], sys.argv[2]


def load(name):
    for d in (MA, MB):
        p = os.path.join(d, f"m1_{name}.json")
        if os.path.exists(p):
            with open(p) as f:
                return json.load(f)["rows"]
    raise FileNotFoundError(name)


def series(name, kind="bin"):
    rr = [r for r in load(name) if r["kind"] == kind and "error" not in r]
    rr.sort(key=lambda r: r["time"])
    out, last = [], None
    for r in rr:                          # a dump written twice at the same time: keep one
        if last is None or r["time"] > last + 1e-9:
            out.append(r)
            last = r["time"]
    return out


def arr(rr, key, i=None):
    return np.array([r[key] if i is None else r[key][i] for r in rr], float)


def cplx(rr, key):
    return arr(rr, key, 0) + 1j * arr(rr, key, 1)


def tau(rr):
    return arr(rr, "time")


def dev(name, delta, eps, kind="bin", sign=1.0, key="K1_plus", minus=None):
    rr = series(name, kind)
    t = tau(rr)
    c = arr(rr, key, 0)
    if minus:
        c = c - arr(rr, minus, 0)
    m = t > 0
    return vlib.a_of_tau(t[m]), c[m] / (sign * vlib.s_static(delta, eps) * vlib.g_closed(t[m])) - 1.0


def mean_near(a, v, a0, frac):
    m = np.abs(a / a0 - 1.0) <= frac
    return float(np.mean(v[m])) if m.any() else float("nan")


def window(a, v, lim, a_lo=2.0):
    """largest a such that every dump from a_lo up to it has |v| <= lim"""
    m = a >= a_lo
    aa, vv = a[m], v[m]
    bad = np.flatnonzero(np.abs(vv) > lim)
    return float(aa[bad[0] - 1]) if bad.size else float(aa[-1])


res = {}
# ---------------------------------------------------------------- row 197: rerun floor
rep = series("e1_rep", "dbin")
orig = series("eps1", "rst")
to = {round(r["time"], 9): r for r in orig}
pairs = [(r, to[round(r["time"], 9)]) for r in rep if round(r["time"], 9) in to and r["time"] > 0]
a197 = vlib.a_of_tau(np.array([p[0]["time"] for p in pairs]))
rel = np.array([abs(p[0]["K1_plus"][0] / p[1]["K1_plus"][0] - 1) for p in pairs])
res["row197"] = {"n_pairs": len(pairs), "n_rep": len(rep), "n_orig": len(orig),
                 "maxrel_2_40": float(rel[(a197 >= 2) & (a197 <= 40)].max()),
                 "maxrel_80_140": float(rel[(a197 >= 80) & (a197 <= 140.5)].max()),
                 "a": a197.tolist(), "rel": rel.tolist()}
# the same numbers through the FFT route of the amplitude (the rounding of the diagnostic itself
# is of the size of the difference: T0b gives 4e-12 relative for the direct sum)
def amp_fft_file(path, kind):
    dd = vlib.read_rst(path) if kind == "rst" else vlib.read_bin(path)
    gg = vlib.Grid(dd)
    hh = vlib.traceless(vlib.tensor(dd, "g") - np.eye(3)[:, :, None, None, None])
    A = {"K1": gg.amp_from_fft(gg.fft_t(hh), (1, 1, 0)), "K2": gg.amp_from_fft(gg.fft_t(hh), (1, -1, 0))}
    return vlib.pol(A)["K1"][0].real


relf = np.array([abs(amp_fft_file(p[0]["file"], "dbin") / amp_fft_file(p[1]["file"], "rst") - 1) for p in pairs])
res["row197"]["fft_route_maxrel_2_40"] = float(relf[(a197 >= 2) & (a197 <= 40)].max())
res["row197"]["fft_route_maxrel_80_140"] = float(relf[(a197 >= 80) & (a197 <= 140.5)].max())
res["row197"]["fft_route_rel"] = relf.tolist()
# the same with the single-precision dumps (every 0.1), as a cross-check of the pairing
rb = series("e1_rep", "bin"); ob = series("eps1", "bin")
tb = {round(r["time"], 9): r for r in ob}
pb = [(r, tb[round(r["time"], 9)]) for r in rb if round(r["time"], 9) in tb and r["time"] > 0]
relb = np.array([abs(p[0]["K1_plus"][0] / p[1]["K1_plus"][0] - 1) for p in pb])
res["row197"]["single_bin_pairs"] = len(pb)
res["row197"]["single_bin_maxrel"] = float(relb.max()) if len(pb) else None

# ---------------------------------------------------------------- row 200: largest TT mode
res["row200"] = {}
for nm in ("jit0p3", "jit0p1", "eps0"):
    m = arr(series(nm), "max_TT_mode")
    res["row200"][nm] = [float(m[1:].min()), float(m[1:].max())]

# ---------------------------------------------------------------- rows 204, 205: null amplitudes
j3, j1, s1 = series("jit0p3"), series("jit0p1"), series("eps0p1")
t3, t1, ts = tau(j3), tau(j1), tau(s1)
c3, c1, cs = cplx(j3, "K1_plus"), cplx(j1, "K1_plus"), cplx(s1, "K1_plus")
res["time_offsets"] = {"jit0p3_vs_jit0p1_max": float(np.max(np.abs(t3[:min(len(t3), len(t1))] - t1[:min(len(t3), len(t1))]))),
                       "jit0p3_vs_eps0p1_max": float(np.max(np.abs(t3[:min(len(t3), len(ts))] - ts[:min(len(t3), len(ts))])))}
c1i = np.interp(t3, t1, c1.real) + 1j * np.interp(t3, t1, c1.imag)
a3 = vlib.a_of_tau(t3)
m = (a3 >= 1.5) & (a3 <= 20) & (t3 <= t1.max())
ratio = np.abs(c3[m] / c1i[m])
res["row204"] = {"min": float(ratio.min()), "median": float(np.median(ratio)), "max": float(ratio.max()),
                 "interp": "linear in tau (real, imaginary parts)"}
sig = np.interp(t3, ts, cs.real)
nz = np.abs(c3) / np.abs(sig)
res["row205"] = {}
for lo, hi in ((2, 20), (20, 80), (80, 140)):
    mm = (a3 >= lo) & (a3 <= hi) & (t3 <= ts.max())
    res["row205"][f"{lo}-{hi}"] = float(np.nanmax(nz[mm]))

# ---------------------------------------------------------------- rows 207, 208: spectra, energies
def pick(name, kind, fname_end):
    for r in series(name, kind):
        if r["file"].endswith(fname_end):
            return r
    raise KeyError(fname_end)


spec = {}
for lab, (nm, kind, fe) in {"j3_a2": ("jit0p3", "dbin", "cw.z4cd.00001.bin"), "j3_a12": ("jit0p3", "dbin", "cw.z4cd.00005.bin"),
                            "j3_a140": ("jit0p3", "dbin", "cw.z4cd.00022.bin"), "j1_a2": ("jit0p1", "dbin", "cw.z4cd.00001.bin"),
                            "j1_a12": ("jit0p1", "dbin", "cw.z4cd.00005.bin"), "s01_a12": ("eps0p1", "rst", "cw.00005.rst"),
                            "s01_a121": ("eps0p1", "rst", "cw.00020.rst")}.items():
    r = pick(nm, kind, fe)
    spec[lab] = {"a": float(vlib.a_of_tau(r["time"])), "round": r["frac_ge16_round"], "floor": r["frac_ge16_floor"],
                 "ge15p5": r["frac_ge15p5"]}
res["row207"] = spec
res["row208"] = {}
for nm in ("jit0p3", "jit0p1"):
    r = series(nm, "dbin")[-1]
    res["row208"][nm] = {"a": float(vlib.a_of_tau(r["time"])), "kin_over_grad": r["kin"] / r["grad"]}

# ---------------------------------------------------------------- rows 209-215: departures
D = {"d01_e1": dev("eps1", 0.01, 1.0), "d01_e0p3": dev("eps0p3", 0.01, 0.3),
     "d0025_e1": dev("d0025_e1", 0.0025, 1.0), "d0025_e0p3": dev("d0025_e0p3", 0.0025, 0.3)}
res["row209"] = {k: window(*v, 5e-3) for k, v in D.items()}
res["row210"] = {k: window(*v, 1e-2) for k, v in D.items()}
for e, row in (("e1", "row211"), ("e0p3", "row212")):
    (a1, v1), (a2, v2) = D[f"d01_{e}"], D[f"d0025_{e}"]
    res[row] = {f"a{a0}": mean_near(a1, v1, a0, 0.05) / mean_near(a2, v2, a0, 0.05) for a0 in (20, 30, 40, 60)}
    col = [mean_near(a2, v2, 4 * a0, 0.03) / mean_near(a1, v1, a0, 0.03) for a0 in (10, 15, 20, 25, 30, 35)]
    res.setdefault("row213", {})[e] = [min(col), max(col), col]
res["row214"] = {k: mean_near(*v, 140, 0.03) for k, v in D.items()}
r215 = {}
for nm, (d, e) in (("d0025_e1", (0.0025, 1.0)), ("d0025_e0p3", (0.0025, 0.3))):
    a, v = dev(nm, d, e, kind="dbin")
    mm = (a >= 2) & (a <= 10)
    r215[f"dbin_{nm}"] = float(np.max(np.abs(v[mm])))
for k, (a, v) in D.items():
    mm = (a >= 2) & (a <= 10)
    r215[f"bin_{k}"] = float(np.max(np.abs(v[mm])))
res["row215"] = r215

# ---------------------------------------------------------------- rows 116-123: spatial gauge
def interp_at(a, v, a0):
    return float(np.interp(a0, a, v))


def nearest_at(a, v, a0):
    return float(v[np.argmin(np.abs(a - a0))])


r116 = {}
for nm in ("eps0p1", "eps0p3", "eps1"):
    rr = series(nm)
    t = tau(rr); a = vlib.a_of_tau(t)
    c = arr(rr, "K1_plus", 0); G = arr(rr, "Gtot_K1_plus", 0)
    sel = (a >= 1.2) & (a <= 20)
    r116[nm] = {"max_le20": float(np.max(np.abs(G[sel] / c[sel]))),
                "a40_interp": abs(interp_at(a, G / c, 40)), "a40_nearest": abs(nearest_at(a, G / c, 40))}
res["row116_117"] = r116
s1 = vlib.s_static(0.01, 1.0)
g118 = {}
for lab, z, gd in (("64", "eps1", "eps1_gd"), ("32", "n32_eps1", "n32_eps1_gd")):
    rz, rg = series(z), series(gd)
    tg_ = np.array([r["time"] for r in rg])
    pr = []                                   # pair dumps whose times agree to 1e-5 (one step is ~1e-2)
    for r in rz:
        j = int(np.argmin(np.abs(tg_ - r["time"])))
        if abs(tg_[j] - r["time"]) < 1e-5 and r["time"] > 0:
            pr.append((r, rg[j]))
    a = vlib.a_of_tau(np.array([p[0]["time"] for p in pr]))
    cz = np.array([p[0]["K1_plus"][0] for p in pr]); cg = np.array([p[1]["K1_plus"][0] for p in pr])
    gz = np.array([p[0]["Gtot_K1_plus"][0] for p in pr]); gg = np.array([p[1]["Gtot_K1_plus"][0] for p in pr])
    qz = np.array([p[0]["Gq_K1_plus"][0] for p in pr]); qg = np.array([p[1]["Gq_K1_plus"][0] for p in pr])
    raw = (cz - cg) / s1; cor = ((cz - gz) - (cg - gg)) / s1; quad = ((cz - qz) - (cg - qg)) / s1
    big = np.abs(raw) > 1e-3
    g118[lab] = {"n_pairs": len(pr), "median_cor_over_raw": float(np.median(np.abs(cor[big] / raw[big]))),
                 "median_quad_over_raw": float(np.median(np.abs(quad[big] / raw[big]))),
                 "share_big": float(np.mean(big)),
                 "raw_at": {a0: abs(interp_at(a, raw, a0)) for a0 in (5, 10, 20, 40, 60)},
                 "cor_at": {a0: abs(interp_at(a, cor, a0)) for a0 in (5, 10, 20, 40, 60)}}
    if lab == "64":
        FIG_GAUGE = (a, raw, cor, quad)
res["row118_121"] = g118
a, d = dev("eps1", 0.01, 1.0)
ac, dc = dev("eps1", 0.01, 1.0, minus="Gtot_K1_plus")
res["row122"] = {f"a{a0}": [abs(interp_at(a, d, a0)), abs(interp_at(ac, dc, a0))] for a0 in (10, 20)}
rz, rg = series("eps1"), series("eps1_gd")
az, ag = vlib.a_of_tau(tau(rz)), vlib.a_of_tau(tau(rg))
nz_, ng_ = arr(rz, "rms_nonTT"), arr(rg, "rms_nonTT")
sel = az >= 10
rr_ = nz_[sel] / np.interp(az[sel], ag, ng_)
res["row123"] = [float(rr_.min()), float(rr_.max())]
# row 101 control (verifier3 recomputed it): kinetic over gradient of the TT part for a >= 12
r101 = {}
for nm in ("eps0p1", "eps1"):
    rr = series(nm); a_ = vlib.a_of_tau(tau(rr))
    gr = arr(rr, "grad")
    kg = np.where(gr > 0, arr(rr, "kin") / np.where(gr > 0, gr, 1.0), 0.0)
    ac = arr(rr, "a_chi")
    r101[nm] = {"a_tau_ge12": float(kg[a_ >= 12].max()), "a_chi_ge12": float(kg[ac >= 12].max()),
                "a_of_max": float(a_[a_ >= 12][np.argmax(kg[a_ >= 12])])}
res["row101_control"] = r101
# row 100 (box-mode share), wave-1-era quantity of the same runs, as an extra
r100 = {}
for nm in ("eps0p1", "eps1"):
    rr = series(nm); a_ = vlib.a_of_tau(tau(rr)); bs = arr(rr, "box_share")
    r100[nm] = {a0: interp_at(a_, bs, a0) for a0 in (10, 20)}
res["row100_extra"] = r100

with open(os.path.join(OUT, "a1_rows.json"), "w") as f:
    json.dump(res, f, indent=1, default=float)

# ---------------------------------------------------------------- figures
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import figstyle  # noqa: E402,F401

fig, ax = plt.subplots(2, 2, figsize=(9, 7))
for k, (a, v) in D.items():
    ax[0, 0].semilogy(a, np.abs(v), lw=1, label=k)
ax[0, 0].axhline(5e-3, color="k", ls=":", lw=0.8); ax[0, 0].axhline(1e-2, color="k", ls="--", lw=0.8)
for k in D:
    ax[0, 0].axvline(res["row209"][k], color="0.6", lw=0.5)
ax[0, 0].set_xscale("log"); ax[0, 0].set_xlabel("a"); ax[0, 0].set_ylabel("|c+/(s g) - 1|"); ax[0, 0].legend(fontsize=7)
ax[0, 0].set_title("rows 209-215: departure from second order", fontsize=9)
for e, col in (("e1", "C0"), ("e0p3", "C1")):
    (a1, v1), (a2, v2) = D[f"d01_{e}"], D[f"d0025_{e}"]
    ax[0, 1].loglog(a1 * 0.01 / 0.01, np.abs(v1), color=col, lw=1, label=f"delta=0.01 {e}")
    ax[0, 1].loglog(a2 * 0.0025 / 0.01, np.abs(v2), color=col, ls="--", lw=1, label=f"delta=0.0025 {e}")
ax[0, 1].set_xlabel("a delta/0.01"); ax[0, 1].set_ylabel("|departure|"); ax[0, 1].legend(fontsize=7)
ax[0, 1].set_title("rows 211-213: collapse in a delta", fontsize=9)
ax[1, 0].semilogy(a3, np.abs(c3), lw=1, label="jitter 0.3, |c(K1)|")
ax[1, 0].semilogy(vlib.a_of_tau(t1), np.abs(c1), lw=1, label="jitter 0.1")
ax[1, 0].semilogy(vlib.a_of_tau(ts), np.abs(cs.real), lw=1, color="k", label="eps=0.1 signal")
m0 = arr(series("eps0"), "max_TT_mode")
ax[1, 0].semilogy(vlib.a_of_tau(tau(series("eps0"))), m0 + 1e-30, lw=1, color="0.5", label="quiet lattice, max TT mode")
ax[1, 0].set_xscale("log"); ax[1, 0].set_xlabel("a"); ax[1, 0].legend(fontsize=7)
ax[1, 0].set_title("rows 200, 204, 205: box mode of the nulls", fontsize=9)
ga, graw, gcor, gquad = FIG_GAUGE
ax[1, 1].semilogy(ga, np.abs(graw), lw=1, label="gauge difference, as projected")
ax[1, 1].semilogy(ga, np.abs(gcor), lw=1, label="after G_tot")
ax[1, 1].semilogy(ga, np.abs(gquad), lw=1, label="after quadratic piece")
ax[1, 1].axhline(1e-3, color="k", ls=":", lw=0.8)
ax[1, 1].set_xscale("log"); ax[1, 1].set_xlabel("a"); ax[1, 1].set_ylabel("/|s|"); ax[1, 1].legend(fontsize=7)
ax[1, 1].set_title("rows 118-121: two spatial gauges, 64^3", fontsize=9)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "a1_rows.png"), dpi=130)

fig, ax = plt.subplots(1, 2, figsize=(9, 3.5))
ax[0].semilogy(res["row197"]["a"], np.array(res["row197"]["rel"]) + 1e-18, "o-", ms=3)
ax[0].set_xscale("log"); ax[0].set_xlabel("a"); ax[0].set_ylabel("|c_rep/c_first - 1|"); ax[0].set_title("row 197: rerun floor (double)", fontsize=9)
for nm in ("eps0p1", "eps0p3", "eps1"):
    rr = series(nm); a_ = vlib.a_of_tau(tau(rr))
    ax[1].semilogy(a_, np.abs(arr(rr, "Gtot_K1_plus", 0) / arr(rr, "K1_plus", 0)), lw=1, label=nm)
ax[1].axvline(20, color="0.6", lw=0.5); ax[1].axvline(40, color="0.6", lw=0.5)
ax[1].set_xscale("log"); ax[1].set_xlabel("a"); ax[1].set_ylabel("|G_tot/c+|"); ax[1].legend(fontsize=7)
ax[1].set_title("rows 116-117: gauge piece over strain", fontsize=9)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "a1_floor_gauge.png"), dpi=130)
print(json.dumps({k: v for k, v in res.items() if k != "row197"}, indent=1, default=float))
print("row197", {k: v for k, v in res["row197"].items() if k not in ("a", "rel")})
