"""Data of the G1 sections of the note: the crossed-wave scan in full relativity.

Reads the per-dump diagnostics that the first-source analysis runs wrote (one JSON per case,
rows of single-precision `bin` and double-precision `rst` dumps; columns described in
tracks/B-emd-gw/first_source/README.md and JOURNAL.md set-up), every file through
common.run_file (checksum against the run's sha256sums.txt). The second-order reference is
computed here, independently of the helper's fslib/reference.py:

    Phi = sum_i phi_i sin(k x_i),  phi_i = -(3/2)(H/k)^2 delta r_i,  r = (1, eps, 0),
    s = -(5/6) phi_x phi_y           (static + amplitude at K1 = (k, k, 0)),
    g'' + 2 Hc g' + |K1|^2 (g - 1) = 0,  g(0) = g'(0) = 0,  Hc = 1/(1 + tau/2),
    a = (1 + tau/2)^2,  H = 1,  L = 4,  delta = 0.01   (scope/SCOPE.md section 3;
    cosmo/ic/make_east.py lines 5-9; the id.json of the initial-data runs).
c_+ is the cosine part of the + amplitude at K1 (column h_K1_plus[0]); at K2 = (k, -k, 0) the
reference has the opposite sign in its own basis.
"""
import json

import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import CubicSpline

import common

DELTA, L, H = 0.01, 4.0, 1.0
KBOX = 2 * np.pi / L
EPS = {"cw_eps0": 0.0, "cw_eps0p1": 0.1, "cw_eps0p3": 0.3, "cw_eps1": 1.0, "cw_eps1_gd": 1.0}
RUN64 = {"cw_eps0": "scan64_a", "cw_eps0p1": "scan64_a", "cw_eps0p3": "scan64_a",
         "cw_eps1": "scan64_b", "cw_eps1_gd": "scan64_b"}
_CACHE = {}


def case(name, n=64):
    key = (name, n)
    if key not in _CACHE:
        run = RUN64[name] if n == 64 else "scan32"
        with open(common.run_file(run, name + ".json")) as f:
            _CACHE[key] = json.load(f)
    return _CACHE[key]


def series(name, key, part=0, kind="bin", n=64):
    """(tau, a, values) of one column over the dumps of one kind, in time order."""
    rows = [r for r in case(name, n)["rows"] if r.get("kind") == kind and "error" not in r]
    rows.sort(key=lambda r: r["time"])
    t = np.array([r["time"] for r in rows])
    v = []
    for r in rows:
        x = r.get(key)
        if isinstance(x, list):
            x = x[part]
        v.append(np.nan if x is None else x)
    return t, a_of_tau(t), np.array(v, float)


def a_of_tau(tau):
    return (1.0 + 0.5 * np.asarray(tau, float)) ** 2


def phis(eps):
    return [-1.5 * (H / KBOX) ** 2 * DELTA * r for r in (1.0, eps, 0.0)]


def s_static(eps):
    p = phis(eps)
    return -(5.0 / 6.0) * p[0] * p[1]


def g_ref(tau):
    """Junk solution g(tau) of the (k, k, 0) mode from conformally flat data."""
    tau = np.asarray(tau, float)
    kk = 2.0 * KBOX * KBOX

    def rhs(t, y):
        return [y[1], -2.0 * y[1] / (1.0 + 0.5 * t) - kk * (y[0] - 1.0)]
    sol = solve_ivp(rhs, (0.0, float(tau.max()) + 1e-9), [0.0, 0.0], method="DOP853",
                    rtol=1e-11, atol=1e-14, dense_output=True)
    return sol.sol(tau)[0]


def common_dumps(t1, t2, tol=1e-6):
    """Indices (i1, i2) of the dumps at the same time in two series (the two spatial gauges
    share their step sequence; other pairs are compared by interpolation in tau)."""
    i1, i2 = [], []
    j = 0
    for i, t in enumerate(t1):
        while j < len(t2) and t2[j] < t - tol:
            j += 1
        if j < len(t2) and abs(t2[j] - t) <= tol:
            i1.append(i)
            i2.append(j)
    return np.array(i1, int), np.array(i2, int)


def amplitude(name, n=64, K="K1", kind="bin", corrected=False):
    """(tau, a, c_+) at K; corrected: minus the spatial-gauge piece G_tot of the same dump."""
    t, a, c = series(name, f"h_{K}_plus", 0, kind, n)
    if corrected:
        _, _, g = series(name, f"Gtot_{K}_plus", 0, kind, n)
        c = c - g
    return t, a, c


def departure(name, n=64, K="K1", corrected=False):
    """(a, c_+ / (sign s g) - 1) over the bin dumps after the first (g = 0 at tau = 0)."""
    t, a, c = amplitude(name, n, K, corrected=corrected)
    sign = 1.0 if K == "K1" else -1.0
    sel = t > 0
    ref = sign * s_static(EPS[name]) * g_ref(t[sel])
    return a[sel], c[sel] / ref - 1.0


def maxabs_window(a, v, lo, hi):
    sel = (a >= lo) & (a <= hi)
    return float(np.nanmax(np.abs(v[sel])))


def at(a, v, a0):
    return float(np.interp(a0, a, v))


def scan_numbers():
    """Every number of the first-source subsection, from the per-dump files."""
    out = {"s_eps1": s_static(1.0), "a_cross_zeldovich": 1.0 + 1.0 / DELTA}
    for n in (64, 32):
        for name in ("cw_eps0p1", "cw_eps0p3", "cw_eps1"):
            for K in ("K1", "K2"):
                a, d = departure(name, n, K)
                out[f"dev_{n}_{name}_{K}_2_10"] = maxabs_window(a, d, 2, 10)
            a, d = departure(name, n, "K1")
            for a0 in (20, 40, 60):
                out[f"dev_{n}_{name}_a{a0}"] = at(a, d, a0)
            # logarithmic slope of the departure between a = 10 and a = 60
            out[f"dev_slope_{n}_{name}"] = float(np.log(at(a, d, 60) / at(a, d, 10)) / np.log(6.0))
    # dependence of the departure on eps: departure/(1 + eps^2) relative to that of eps = 0.1
    # (the pattern of relative corrections in phi_x^2 + phi_y^2, i.e. of next order in the potential)
    for a0 in (20, 40, 60):
        base = out[f"dev_64_cw_eps0p1_a{a0}"] / (1.0 + 0.1 ** 2)
        for name in ("cw_eps0p3", "cw_eps1"):
            e = EPS[name]
            out[f"dev_scaled_{name}_a{a0}"] = out[f"dev_64_{name}_a{a0}"] / (1.0 + e * e) / base
    # linearity in eps (64^3): c/eps of 0.3 and of 1 against 0.1 at the same dumps
    t1, a1, c1 = amplitude("cw_eps0p1")
    for other, e in (("cw_eps0p3", 0.3), ("cw_eps1", 1.0)):
        t2, _, c2 = amplitude(other)
        i1 = np.nonzero((t1 >= t2.min()) & (t1 <= t2.max()))[0]
        sel = (a1[i1] >= 2) & (a1[i1] <= 10)
        r = (CubicSpline(t2, c2)(t1[i1]) / e) / (c1[i1] / 0.1) - 1.0
        out[f"lin_{other}_2_10"] = float(np.max(np.abs(r[sel])))
        for a0 in (20, 60):
            out[f"lin_{other}_a{a0}"] = at(a1[i1], r, a0)
    # largest strain after crossing (eps = 1, zero shift)
    t, a, c = amplitude("cw_eps1")
    ratio = c / s_static(1.0)
    i = int(np.nanargmax(ratio))
    out["max_c_over_s_eps1"], out["a_of_max_eps1"] = float(ratio[i]), float(a[i])
    for name in ("cw_eps0p1", "cw_eps0p3"):
        t, a, c = amplitude(name)
        out[f"max_c_over_s_{name}"] = float(np.nanmax(c / s_static(EPS[name])))
    # the null (eps = 0): largest TT amplitude at any nonzero wave vector, both dump kinds
    for kind in ("bin", "rst"):
        _, a, m = series("cw_eps0", "max_TT_mode", kind=kind)
        _, _, mA = series("cw_eps0", "max_TT_mode_A", kind=kind)
        _, _, zd = series("cw_eps0", "z_dependence", kind=kind)
        out[f"null_h_{kind}"] = float(np.nanmax(m))
        out[f"null_A_{kind}"] = float(np.nanmax(mA))
        out[f"null_zdep_{kind}"] = float(np.nanmax(zd))
        out[f"null_ndumps_{kind}"] = int(len(a))
        out[f"null_amax_{kind}"] = float(a.max())
    # two meshes: c_+(32^3)/c_+(64^3) - 1 at the common dumps
    for name in ("cw_eps0p1", "cw_eps0p3", "cw_eps1", "cw_eps1_gd"):
        t6, a6, c6 = amplitude(name, 64)
        t3, _, c3 = amplitude(name, 32)
        # 32^3 interpolated (cubic spline in tau) to the 64^3 dump times: the dumps of the
        # two meshes are written up to one coarse step apart
        i6 = np.nonzero((t6 >= t3.min()) & (t6 <= t3.max()))[0]
        r = CubicSpline(t3, c3)(t6[i6]) / c6[i6] - 1.0
        aa = a6[i6]
        out[f"res_{name}_5_40"] = maxabs_window(aa, r, 5, 40)
        out[f"res_{name}_40_80"] = maxabs_window(aa, r, 40, 80)
        out[f"res_{name}_a100"] = at(aa, r, 100)
        out[f"res_{name}_ncommon"] = int(len(i6))
    # mode content and energy of the TT field (64^3, double-precision dumps)
    for name in ("cw_eps0p1", "cw_eps1"):
        _, a, bf = series(name, "box_mode_fraction")
        out[f"box_share_{name}_a20"] = at(a, bf, 20)
        out[f"box_share_{name}_a10"] = at(a, bf, 10)
        _, a, rk = series(name, "rho_kin", kind="rst")
        _, _, rg = series(name, "rho_grad", kind="rst")
        _, _, rb = series(name, "rho_bar", kind="rst")
        sel = a >= 12
        out[f"kin_over_grad_{name}_a12"] = float(np.max(rk[sel] / rg[sel]))
        out[f"rhoGW_over_rhobar_{name}"] = float(np.max((rk + rg) / rb))
    # initial data residuals (the solve of the constraints on the torus)
    res = []
    for run, sub in (("scan_ic64", "eps0"), ("scan_ic64", "eps0p1"), ("scan_ic64", "eps0p3"),
                     ("scan_ic64_eps1", "eps1")):
        with open(common.run_file(run, sub + "/id.json")) as f:
            j = json.load(f)
        res.append((j["max_hamiltonian_residual"], j["max_momentum_residual"], j["N"], j["n"], j["ppc"]))
    out["ic_ham_max"] = max(r[0] for r in res)
    out["ic_mom_max"] = max(r[1] for r in res)
    out["ic_particles"] = res[0][2]
    return out


def gauge_numbers():
    """Every number of the spatial-gauge subsection (eps = 1, two spatial gauges)."""
    out = {}
    s1 = s_static(1.0)
    for n in (64, 32):
        tz, a, cz = amplitude("cw_eps1", n)
        tg, _, cg = amplitude("cw_eps1_gd", n)
        _, _, gz = series("cw_eps1", "Gtot_K1_plus", 0, n=n)
        _, _, gg = series("cw_eps1_gd", "Gtot_K1_plus", 0, n=n)
        _, _, qz = series("cw_eps1", "G_K1_plus", 0, n=n)
        _, _, qg = series("cw_eps1_gd", "G_K1_plus", 0, n=n)
        iz, ig = common_dumps(tz, tg)
        aa = a[iz]
        raw = (cz[iz] - cg[ig]) / s1
        cor = ((cz[iz] - gz[iz]) - (cg[ig] - gg[ig])) / s1
        quad = ((cz[iz] - qz[iz]) - (cg[ig] - qg[ig])) / s1
        big = np.abs(raw) > 1e-3
        out[f"median_cor_over_raw_{n}"] = float(np.median(np.abs(cor[big] / raw[big])))
        out[f"median_quad_over_raw_{n}"] = float(np.median(np.abs(quad[big] / raw[big])))
        out[f"share_big_{n}"] = float(np.mean(big))
        if n == 64:
            for a0 in (5, 10, 20, 40, 60):
                out[f"raw_a{a0}"] = abs(at(aa, raw, a0))
                out[f"cor_a{a0}"] = abs(at(aa, cor, a0))
    # size of the gauge piece in the zero-shift runs, a <= 20
    for name in ("cw_eps0p1", "cw_eps0p3", "cw_eps1"):
        _, a, c = amplitude(name)
        _, _, g = series(name, "Gtot_K1_plus", 0)
        sel = (a >= 1.2) & (a <= 20)
        out[f"Gtot_over_c_{name}_le20"] = float(np.max(np.abs(g[sel] / c[sel])))
        out[f"Gtot_over_c_{name}_a40"] = abs(at(a, g / c, 40))
    # the corrected strain against the second-order value (eps = 1)
    a, d = departure("cw_eps1")
    ac, dc = departure("cw_eps1", corrected=True)
    for a0 in (10, 20):
        out[f"dev_raw_a{a0}"] = abs(at(a, d, a0))
        out[f"dev_cor_a{a0}"] = abs(at(ac, dc, a0))
    # the non-TT part: Gamma driver against zero shift for a >= 10
    _, a, nz = series("cw_eps1", "rms_nonTT")
    _, ag, ng = series("cw_eps1_gd", "rms_nonTT")
    sel = a >= 10
    r = nz[sel] / np.interp(a[sel], ag, ng)
    out["nonTT_ratio_min"], out["nonTT_ratio_max"] = float(r.min()), float(r.max())
    # magnetic Weyl part (x amplitude at K1, sine part) and Lambda h, double-precision dumps
    tb, ab, bz = series("cw_eps1", "B_K1_cross", 1, kind="rst")
    tb2, _, bg = series("cw_eps1_gd", "B_K1_cross", 1, kind="rst")
    _, _, hz = series("cw_eps1", "h_K1_plus", 0, kind="rst")
    _, _, hg = series("cw_eps1_gd", "h_K1_plus", 0, kind="rst")
    i1, i2 = common_dumps(tb, tb2)
    ab = ab[i1]
    dB = np.abs(bz[i1] - bg[i2]) / np.maximum(np.abs(bz[i1]), np.abs(bg[i2]))
    dh = np.abs(hz[i1] - hg[i2]) / np.maximum(np.abs(hz[i1]), np.abs(hg[i2]))
    out["weyl_a"], out["weyl_dB"], out["weyl_dh"] = ab.tolist(), dB.tolist(), dh.tolist()
    sel = (ab > 1.5) & (ab <= 64)
    out["weyl_dB_median_le64"] = float(np.median(dB[sel]))
    out["weyl_dh_median_le64"] = float(np.median(dh[sel]))
    # T0: exact pure-gauge data
    with open(common.run_file("t0_gauge", "t0_gauge.json")) as f:
        t0 = json.load(f)
    sl = {k: v["slopes"] for k, v in t0["cases"].items()}
    out["t0_slopes"] = sl
    return out
