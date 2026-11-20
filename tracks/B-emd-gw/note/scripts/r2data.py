"""Data of the second round of the first source (note v2): jittered null, delta = 0.0025, floor.

Reads the per-dump diagnostics of the second-round runs (one JSON per case, rows of
single-precision `bin` and double-precision `dbin` dumps) and the prediction of the jittered
null written from its initial data before the card run, every file through common.run_file
(checksum against the run's sha256sums.txt). The second-order reference s g(tau) is g1data's
(own junk solution, own s), with the amplitude delta of the case:

    s = -(5/6) phi_x phi_y,  phi_i = -(3/2)(H/k)^2 delta r_i,  r = (1, eps, 0).

The departure from second order is dev = c_+/(s g) - 1 at K1 = (k, k, 0), c_+ the cosine part
of the + amplitude (column h_K1_plus[0]). Values at a given scale factor are means over the
dumps within 5 per cent of it (single-precision dumps carry a rounding noise of a few 1e-4 in
dev at delta = 0.0025, first_source/JOURNAL.md P14(a)); windows are the largest a such that
every dump from a = 2 up to it has |dev| <= 0.5 per cent.
Null: complex amplitude h[0] + i h[1] at K1 and K2 against the predicted response
cross * g_cross + nn * g_nn (prediction run, cubic spline in tau to the dump times).
"""
import json

import numpy as np
from scipy.interpolate import CubicSpline

import common
import g1data

CASES = {  # name -> (run key, file, delta, eps)
    "d01_e1": ("scan64_b", "cw_eps1.json", 0.01, 1.0),
    "d01_e0p3": ("scan64_a", "cw_eps0p3.json", 0.01, 0.3),
    "d0025_e1": ("r2_jit1_d1", "d0025_e1.json", 0.0025, 1.0),
    "d0025_e0p3": ("r2_d3", "d0025_e0p3.json", 0.0025, 0.3),
    "jit0p3": ("r2_jit3", "jit0p3.json", 0.01, 0.0),
    "jit0p1": ("r2_jit1_d1", "jit0p1.json", 0.01, 0.0),
    "null0": ("scan64_a", "cw_eps0.json", 0.01, 0.0),
    "s01": ("scan64_a", "cw_eps0p1.json", 0.01, 0.1),
}
_CACHE = {}


def rows(name, kind="bin"):
    key = (name, kind)
    if key not in _CACHE:
        run, fn, _, _ = CASES[name]
        with open(common.run_file(run, fn)) as f:
            c = json.load(f)
        rr = [r for r in c["rows"] if r.get("kind") == kind and "error" not in r]
        rr.sort(key=lambda r: r["time"])
        out, last = [], None
        for r in rr:                       # drop a dump written twice at the last step
            if last is None or r["time"] > last + 1e-9:
                out.append(r)
                last = r["time"]
        _CACHE[key] = out
    return _CACHE[key]


def tau_a(rr):
    t = np.array([r["time"] for r in rr])
    return t, g1data.a_of_tau(t)


def s_static(delta, eps):
    kb = g1data.KBOX
    px = -1.5 * (g1data.H / kb) ** 2 * delta
    return -(5.0 / 6.0) * px * (px * eps)


def departure(name, kind="bin"):
    """(tau, a, dev) over the dumps after the first (g = 0 at tau = 0)."""
    _, _, delta, eps = CASES[name]
    rr = rows(name, kind)
    t, a = tau_a(rr)
    c = np.array([r["h_K1_plus"][0] for r in rr])
    sel = t > 0
    dev = c[sel] / (s_static(delta, eps) * g1data.g_ref(t[sel])) - 1.0
    return t[sel], a[sel], dev


def mean_near(a, v, a0, frac=0.05):
    m = np.abs(a / a0 - 1.0) <= frac
    return float(np.mean(v[m])) if m.any() else float("nan")


def window(a, v, lim=5e-3, a_lo=2.0):
    bad = np.flatnonzero((a >= a_lo) & (np.abs(v) > lim))
    return float(a[bad[0] - 1]) if bad.size else float(a[-1])


def complex_amp(name, K="K1", kind="bin"):
    rr = rows(name, kind)
    t, a = tau_a(rr)
    v = np.array([r[f"h_{K}_plus"] for r in rr], float)
    return t, a, v[:, 0] + 1j * v[:, 1]


def null_prediction(name, K, t):
    """Predicted complex box-mode amplitude of a jittered null at the times t."""
    p = common.load_json("r2_null_pred", "null_prediction.json")
    pc = p["cases"][name]
    pt = np.array(p["tau"])
    pr = (complex(*pc[f"cross_{K}_plus"]) * np.array(p["g_cross"])
          + complex(*pc[f"nn_{K}_plus"]) * np.array(p["g_nn"]))
    out = CubicSpline(pt, pr.real)(t) + 1j * CubicSpline(pt, pr.imag)(t)
    out[(t < pt[0]) | (t > pt[-1])] = np.nan
    return out


def null_numbers():
    out = {}
    for name in ("jit0p3", "jit0p1"):
        for K in ("K1", "K2"):
            t, a, c = complex_amp(name, K)
            p = null_prediction(name, K, t)
            m = (a >= 3.0) & (a <= 20.0)
            r = np.abs(c[m]) / np.abs(p[m])
            ph = np.angle(c[m] / p[m])
            out[f"{name}_{K}_ratio"] = [float(r.min()), float(np.median(r)), float(r.max())]
            out[f"{name}_{K}_phase"] = [float(ph.min()), float(ph.max())]
            out[f"{name}_{K}_maxabsphase"] = float(np.max(np.abs(ph)))
    # the two jitter amplitudes at K1
    t3, a3, c3 = complex_amp("jit0p3")
    t1, _, c1 = complex_amp("jit0p1")
    c1i = CubicSpline(t1, c1.real)(t3) + 1j * CubicSpline(t1, c1.imag)(t3)
    m = (a3 >= 1.5) & (a3 <= 20.0) & (t3 <= t1.max())
    rr = c3[m] / c1i[m]
    out["amp_ratio_K1"] = [float(np.min(np.abs(rr))), float(np.median(np.abs(rr))), float(np.max(np.abs(rr)))]
    # null (jitter 0.3) over the eps = 0.1 signal at K1, |cosine part| of the signal
    ts, _, cs = complex_amp("s01")
    sig = CubicSpline(ts, cs.real)(t3)
    with np.errstate(invalid="ignore", divide="ignore"):
        nz = np.abs(c3) / np.abs(sig)
    for lo, hi in ((2.0, 20.0), (20.0, 80.0), (80.0, 140.0)):
        mm = (a3 >= lo) & (a3 <= hi) & (t3 <= ts.max())
        out[f"null_over_signal_{lo:g}_{hi:g}"] = float(np.nanmax(nz[mm]))
    # largest TT amplitude after the first dump: jittered and plane-symmetric nulls
    for name in ("jit0p3", "jit0p1", "null0"):
        rr_ = rows(name)
        m_ = np.array([r["max_TT_mode"] for r in rr_])
        out[f"maxTT_min_{name}"] = float(np.min(m_[1:]))
        out[f"maxTT_max_{name}"] = float(np.max(m_[1:]))
    # last double-precision dump of the jittered nulls: rms TT, kinetic over gradient energy
    for name in ("jit0p3", "jit0p1"):
        r = rows(name, "dbin")[-1]
        out[f"last_{name}"] = dict(a=r["a"], rms_TT=r["rms_TT"], kin_over_grad=r["rho_kin"] / r["rho_grad"])
    # rms TT of all modes against the second-order estimate (prediction run, late value)
    p = common.load_json("r2_null_pred", "null_prediction.json")
    _, a, _ = complex_amp("jit0p3")
    rms = np.array([r["rms_TT"] for r in rows("jit0p3")])
    m = (a >= 3.0) & (a <= 20.0)
    out["rms_over_estimate_jit0p3"] = [float(np.min(rms[m]) / p["cases"]["jit0p3"]["rms_late"]),
                                       float(np.max(rms[m]) / p["cases"]["jit0p3"]["rms_late"])]
    # shell spectra: share of the TT power at |k|L/2pi >= 16 (read from the spectra run)
    sp = common.load_json("r2_spec", "null_spectrum.json")
    out["frac_ge16"] = [float(sp[k]["h"]["frac_TT_ge16"]) for k in ("j3_a2", "j3_a12", "j3_a140", "j1_a2", "j1_a12")]
    out["frac_ge16_signal"] = [float(sp[k]["h"]["frac_TT_ge16"]) for k in ("s01_a12", "s01_a121")]
    out["spec_a"] = [float(sp[k]["a"]) for k in ("j3_a2", "j3_a12", "j3_a140")]
    return out


def delta_numbers():
    out = {}
    dev = {n: departure(n) for n in ("d01_e1", "d01_e0p3", "d0025_e1", "d0025_e0p3")}
    for n, (t, a, v) in dev.items():
        out[f"window_{n}"] = window(a, v)
        out[f"window1_{n}"] = window(a, v, lim=1e-2)
        for a0 in (20, 40, 60, 140):
            out[f"dev_{n}_a{a0}"] = mean_near(a, v, a0, 0.03)
    for e in ("e1", "e0p3"):
        _, a1, v1 = dev[f"d01_{e}"]
        _, a2, v2 = dev[f"d0025_{e}"]
        out[f"R_{e}"] = [mean_near(a1, v1, a0) / mean_near(a2, v2, a0) for a0 in (20, 30, 40, 60)]
        col = [mean_near(a2, v2, 4 * a0, 0.03) / mean_near(a1, v1, a0, 0.03) for a0 in (10, 15, 20, 25, 30, 35)]
        out[f"collapse_{e}"] = [min(col), max(col)]
    # double-precision dumps, 2 <= a <= 10
    for n in ("d0025_e1", "d0025_e0p3"):
        _, a, v = departure(n, "dbin")
        m = (a >= 2.0) & (a <= 10.0)
        out[f"dbin_{n}"] = float(np.max(np.abs(v[m])))
        out[f"dbin_a_{n}"] = [float(x) for x in a[m]]
        _, a, v = departure(n, "bin")
        m = (a >= 2.0) & (a <= 10.0)
        out[f"bin_{n}"] = float(np.max(np.abs(v[m])))
    for n in ("d01_e1", "d01_e0p3"):
        _, a, v = departure(n, "bin")
        m = (a >= 2.0) & (a <= 10.0)
        out[f"bin_{n}"] = float(np.max(np.abs(v[m])))
    return out


def floor_numbers():
    """Run-to-run floor and initial-data parity (read from the helper's comparison files)."""
    cmp_ = common.load_json("r2_rerun_cmp", "conv_summary.json")["P12_P13"]["e1_rep_d_vs_e1_p8_d"]
    par = common.load_json("r2_parity", "parity.json")
    fmax = max(par["fields_maxabs_diff"].values())
    return {"rep_2_40": cmp_["maxrel_a2.0_40.0"], "rep_80_140": cmp_["maxrel_a80.0_140.0"],
            "parity": max(par["max_dx"], par["max_du"], par["max_dm_rel"], fmax),
            "parity_n": par["N"][0]}


def helper_numbers():
    """The helper's own summaries of the same runs (second reading; never printed as the value)."""
    nc = common.load_json("r2_null_cmp", "conv_summary.json")["P11"]
    dc = common.load_json("r2_delta_cmp", "conv_summary.json")["P14"]
    return nc, dc
