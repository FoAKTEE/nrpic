"""Late-time comparison of a secondary-infall density profile with the self-similar
solution (wave 3; analysis only, decision 0010). Shared by nm_predict.py (shell
references) and nm_analyze.py (AthenaK runs), so that runs, shells and the self-similar
solution are binned and differentiated the same way.

- bins: LEDGES of nm_analyze.py (0.1 dex in r, 0.5 to 256 M) or any edges in r;
- the self-similar solution (test 2, selfsimilar_profile.npz: ln m on a ln lambda grid) is
  binned in EXACTLY the bins of the run, rho/rho_b = (9 pi^2/16) [m(l_hi) - m(l_lo)]/(l_hi^3 - l_lo^3)
  with l = r/r_ta, so caustics fall into the same bins in both;
- r_ta from G M_ta t^2/r_ta^3 = pi^2/8 with the measured M_ta (nm_analyze.py's definition);
- local logarithmic slope d ln rho/d ln r centred over two bins (0.2 dex);
- the comparison range [lambda_min, lambda_max] with lambda_min = max(4 dx/r_ta, 0.03).
"""
import numpy as np

PI = np.pi
KAPPA = PI ** 2 / 8.0
LEDGES = np.geomspace(0.5, 256.0, 28)    # nm_analyze.py
LEDGES_LATE = np.geomspace(0.5, 2048.0, 37)   # same 0.1-dex spacing, out to 2 r_ta at a/a_i = 30


def r_ta_of(mta, t_cosmic):
    return (mta * t_cosmic ** 2 / KAPPA) ** (1.0 / 3.0)


def binned_density(r, m, edges, rho_b):
    h, _ = np.histogram(r, bins=edges, weights=m)
    return h / (4.0 * PI / 3.0 * np.diff(edges ** 3)) / rho_b


def selfsim_binned(ss, edges_lambda):
    """Self-similar rho/rho_b in the given lambda bins (nan outside the tabulated range)."""
    lg, lnm = np.asarray(ss["lngrid"]), np.asarray(ss["lnm"])
    e = np.asarray(edges_lambda, float)
    m = np.exp(np.interp(np.log(np.clip(e, np.exp(lg[0]), 1.0)), lg, lnm))
    m = np.where(e >= 1.0, 1.0, m)       # m = 1 at and beyond r_ta (no shell outside r_ta has turned)
    rho = (9.0 * PI ** 2 / 16.0) * np.diff(m) / np.diff(e ** 3)
    rho[(e[1:] > 1.0)] = np.nan          # beyond r_ta the solution has the unturned infall, not tabulated
    return rho


def local_slope(rc, rho):
    """d ln rho/d ln r centred over two bins; nan where a neighbour is empty."""
    lr = np.log(rc)
    with np.errstate(divide="ignore", invalid="ignore"):
        lp = np.where(rho > 0, np.log(rho), np.nan)
    s = np.full(rc.size, np.nan)
    s[1:-1] = (lp[2:] - lp[:-2]) / (lr[2:] - lr[:-2])
    return s


def compare(rc, edges, rho, ss, r_ta, dx, lam_lo_floor=0.03, lam_hi=0.3):
    """Profile and slope of one snapshot against the self-similar solution on
    [max(4 dx/r_ta, lam_lo_floor), lam_hi]; bins whose centres lie in the range."""
    lam = rc / r_ta
    ssr = selfsim_binned(ss, edges / r_ta)
    lam_min = max(4.0 * dx / r_ta, lam_lo_floor)
    ok = (lam >= lam_min) & (lam <= lam_hi) & np.isfinite(ssr) & (rho > 0)
    ratio = np.where(ok, rho / np.where(ssr > 0, ssr, np.nan), np.nan)
    sl, sl_ss = local_slope(rc, rho), local_slope(rc, ssr)
    oks = ok & np.isfinite(sl) & np.isfinite(sl_ss)
    out = dict(lambda_min=float(lam_min), lambda_max=lam_hi, n_bins=int(ok.sum()),
               lam=lam[ok].tolist(), ratio=ratio[ok].tolist(),
               max_dev=float(np.nanmax(np.abs(ratio[ok] - 1))) if ok.any() else None,
               rms_dev=float(np.sqrt(np.nanmean((ratio[ok] - 1) ** 2))) if ok.any() else None,
               slope=sl[oks].tolist(), slope_ss=sl_ss[oks].tolist(), slope_lam=lam[oks].tolist(),
               slope_max_absdiff=float(np.nanmax(np.abs(sl[oks] - sl_ss[oks]))) if oks.any() else None,
               slope_mean=float(np.nanmean(sl[oks])) if oks.any() else None,
               slope_ss_mean=float(np.nanmean(sl_ss[oks])) if oks.any() else None)
    # least-squares slope of ln rho over the whole range (run and self-similar alike)
    if ok.sum() >= 3:
        out["fit_slope"] = float(np.polyfit(np.log(rc[ok]), np.log(rho[ok]), 1)[0])
        out["fit_slope_ss"] = float(np.polyfit(np.log(rc[ok]), np.log(ssr[ok]), 1)[0])
    return out, ssr, sl, sl_ss
