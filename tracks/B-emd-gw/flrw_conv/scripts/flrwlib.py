"""Readers and reference solutions of flrw_conv (analysis of AthenaK output only).

Units of cosmo/: G = c = 1, initial Hubble rate 1 at a = 1, conformal time t,
a(t) = (1 + t/2)^2, alpha = a, chi = a^-2, K = -3 a^-3/2, E = rho_0 a^-3,
rho_0 = 3/(8 pi). Box L = 1.35085.
"""
import json
import os

import numpy as np

SCRATCH = "/data/haiyangw/nrpic/scratch/B-emd-gw"
L = 1.35085
RHO0 = 3.0/(8.0*np.pi)
K_WAVE = 2.0*np.pi/L
AMP = 1e-7


def a_of_t(t):
    return (1.0 + 0.5*np.asarray(t))**2


def load_hst(path):
    """Columns of an NRPIC history file by the names of its header ([i]=name)."""
    names = None
    with open(path) as f:
        for line in f:
            if line.startswith("#") and "[1]=" in line:
                names = [tok.split("=")[1] for tok in line[1:].split() if "=" in tok]
                break
    d = np.loadtxt(path)
    if d.ndim == 1:
        d = d[None, :]
    return {n: d[:, i] for i, n in enumerate(names) if i < d.shape[1]}


def rundir(spec):
    """'<run id>/<name>' or an absolute directory."""
    return spec if spec.startswith("/") else os.path.join(SCRATCH, spec)


def flrw_errors(d):
    """Relative scale-factor errors and constraints of a leg-F run directory."""
    h = load_hst(os.path.join(d, "flrw.nrpic.hst"))
    c = load_hst(os.path.join(d, "flrw.cstat.hst"))
    t = h["time"]
    a = a_of_t(t)
    out = {"t": t, "a": a,
           "e_alpha": np.maximum(np.abs(h["alpha_max"] - a), np.abs(h["alpha_min"] - a))/a,
           "e_alpha_signed_max": h["alpha_max"]/a - 1.0,
           "e_alpha_signed_min": h["alpha_min"]/a - 1.0,
           "e_V": (h["proper_volume"]/L**3)**(1.0/3.0)/a - 1.0,
           "e_K": (-h["mean_K"]/3.0)**(-2.0/3.0)/a - 1.0,
           "E_max": h["E_max"]*a**3/RHO0 - 1.0, "E_min": h["E_min"]*a**3/RHO0 - 1.0,
           "np": h["np"], "sum_m": h["sum_m"]}
    tc = c["time"]
    ac = a_of_t(tc)
    out.update({"tc": tc, "ac": ac,
                "e_chi": np.maximum(np.abs(c["chi_min"]**-0.5 - ac),
                                    np.abs(c["chi_max"]**-0.5 - ac))/ac,
                "Hr_max": c["Hr_max"], "Hr_mean": c["Hr_mean"], "Mr_max": c["Mr_max"],
                "H_max": c["H_max"], "M_max": c["M_max"], "Theta_max": c["Theta_max"]})
    out["finite"] = bool(all(np.isfinite(v).all() for v in out.values()
                             if isinstance(v, np.ndarray)))
    return out


def read_line(d, base="east"):
    """Line records: t, x and the arrays chi, alpha, K, E, S_x of shape (records, n)."""
    x = np.loadtxt(os.path.join(d, f"{base}.line.txt"), skiprows=2)
    n = len(x)
    r = np.fromfile(os.path.join(d, f"{base}.line.bin"))
    r = r[:(len(r)//(1 + 5*n))*(1 + 5*n)].reshape(-1, 1 + 5*n)
    out = {"t": r[:, 0], "x": x, "n": n}
    for i, k in enumerate(("chi", "alpha", "K", "E", "Sx")):
        out[k] = r[:, 1 + i*n:1 + (i + 1)*n]
    return out


def growth(d):
    """Amplitudes and growth rates of the plane wave of test B from the line records.

    D_delta: sin projection of delta = E a^3/rho_0 - 1 (the mean drops out);
    reference A (a + 3/k^2), f_ref = a/(a + 3/k^2) (arXiv:1904.07841 Main.tex:673 in the
    units of this code, H_c^2 = 1/a).
    D_star: D_delta - 3 H_c v_amp, v the potential of the coordinate velocity
    V = S_x/(E a) (cos projection over k); reference A a, f = 1 (Main.tex:629, 633).
    D_phi: a phi_amp, phi = (a^2 chi - 1)/2 (sin projection); reference
    a (3/2) A/k^2 (sign: phi_0 = -(3/2) A/k^2, so -a phi_amp), f = 1.
    """
    r = read_line(d)
    t, x = r["t"], r["x"]
    a = a_of_t(t)
    k = K_WAVE
    s, c = np.sin(k*x), np.cos(k*x)
    delta = r["E"]*a[:, None]**3/RHO0 - 1.0
    Dd = 2.0*(delta*s[None, :]).mean(axis=1)
    V = r["Sx"]/(r["E"]*a[:, None])
    vamp = 2.0*(V*c[None, :]).mean(axis=1)/k
    Hc = a**-0.5
    Ds = Dd - 3.0*Hc*vamp
    phi = 0.5*(a[:, None]**2*r["chi"] - 1.0)
    phiamp = 2.0*(phi*s[None, :]).mean(axis=1)
    Dp = -a*phiamp
    la = np.log(a)
    out = {"t": t, "a": a, "D_delta": Dd, "D_star": Ds, "D_phi": Dp, "phi_amp": phiamp,
           "v_amp": vamp, "n": r["n"],
           "Dref_delta": AMP*(a + 3.0/k**2), "Dref_star": AMP*a,
           "Dref_phi": AMP*1.5*a/k**2, "fref_delta": a/(a + 3.0/k**2),
           "fref_star": np.ones_like(a), "fref_phi": np.ones_like(a)}
    for key in ("delta", "star", "phi"):
        D = out[f"D_{key}"]
        e = D/out[f"Dref_{key}"] - 1.0
        out[f"e_{key}"] = e
        # growth rate f = d ln D / d ln a. The error f - f_ref equals d ln(D/D_ref)/d ln a
        # exactly; it is estimated (i) pointwise by centred differences of the records
        # ("_fd"), (ii) as the slope of a straight-line fit of ln(D/D_ref) against ln a in a
        # window of width WIN in ln a centred on each record (the default; it averages the
        # record-to-record jitter, whose difference quotient grows as the records come
        # closer in ln a late in the run). Differencing ln(D/D_ref) rather than ln D removes
        # the truncation error of the difference quotient of the reference itself.
        le = np.log1p(e)
        out[f"df_{key}_fd"] = np.gradient(le, la)
        out[f"df_{key}"] = window_slope(la, le, WIN)
        out[f"f_{key}"] = out[f"fref_{key}"] + out[f"df_{key}"]
    # residual of delta: the part of the line profile not in sin kx (mean removed)
    dl0 = delta - delta.mean(axis=1)[:, None]
    out["resid"] = np.abs(dl0 - Dd[:, None]*s[None, :]).max(axis=1)/np.abs(Dd)
    out["bg_delta"] = delta.mean(axis=1)
    return out


WIN = 0.1


def window_slope(x, y, w):
    """Least-squares slope of y(x) over the points with |x - x_i| <= w/2, per point i
    (at least three points; fewer at the ends of the record)."""
    out = np.empty_like(y)
    for i, xi in enumerate(x):
        m = np.abs(x - xi) <= 0.5*w
        if m.sum() < 3:
            j = np.argsort(np.abs(x - xi))[:3]
            m = np.zeros_like(m)
            m[j] = True
        xs, ys = x[m], y[m]
        xs0 = xs - xs.mean()
        out[i] = (xs0*(ys - ys.mean())).sum()/(xs0*xs0).sum()
    return out


def decaying_fit(g, amax=5.0):
    """Least-squares fit D_star = A_+ a + A_- a^-3/2 on a <= amax; eps = A_-/A_+."""
    m = g["a"] <= amax
    a = g["a"][m]
    M = np.stack([a, a**-1.5], axis=1)
    coef, *_ = np.linalg.lstsq(M, g["D_star"][m], rcond=None)
    return {"A_plus": float(coef[0]), "A_minus": float(coef[1]),
            "eps": float(coef[1]/coef[0]), "A_plus_over_A": float(coef[0]/AMP),
            "n_points": int(m.sum()), "amax": amax}


def save_json(obj, path):
    def conv(o):
        if isinstance(o, (np.floating, np.integer)):
            return o.item()
        if isinstance(o, np.ndarray):
            return o.tolist()
        raise TypeError(type(o))
    with open(path, "w") as f:
        json.dump(obj, f, indent=1, default=conv)
