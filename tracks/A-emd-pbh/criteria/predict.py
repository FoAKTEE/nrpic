#!/usr/bin/env python3
"""Table of predictions of every analytic criterion for one set of initial-data parameters.

    python3 predict.py --delta 0.1 --e 0.1 --p 0 --sigv 0 --aend 100 --sigmaH 0.01

Parameters (definitions in emd_criteria's docstring): amplitude delta = linear density
contrast of the region at its horizon entry; ellipticity e and prolateness p of the
deformation tensor; velocity dispersion sigma_v (3D rms, units of c) at horizon entry
(--sigv) or at an initial slice where the region has H R = --HR-ini (--sigv-ini), carried
by the adiabatic invariant sigma_v R = const (2211.13950:330-334); duration of the matter
era a_end/a_H (--aend) or its e-folds after horizon entry (--efolds). The statistical
criteria also need the rms density contrast sigma_H at horizon entry on the PBH scale
(--sigmaH); zeta_rms defaults to (5/2) sigma_H (1609.01588:1165-1167).
"""
import argparse
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import emd_criteria as C  # noqa: E402

# ---------------------------------------------------------------------------------------
# Amplitude measures (scope/SCOPE.md 10.1). All are linear growing-mode contrasts at the
# horizon entry of the compaction radius, a H r_m = 1 (MDPBH.tex:707-714), except C_max.
#   delta_c   central contrast, -(2/5) r_m^2 lap(zeta)(0) = alpha+beta+gamma of
#             MDPBH.tex:907-908 at k^2/(aH)^2 = 6: 12 mu/5 for the profile of 839.
#   deltabar  mean contrast inside the sphere r_m, -(6/5) r_m zeta'(r_m); equal to the
#             linear compaction function at r_m, i.e. delta_m of 2507.18312:194-205
#             (C = (3/5) K r^2 for dust); 12 mu/(5e) for the profile of 839. The anisotropic
#             part of 839 is a traceless quadratic times a radial function: it averages to
#             zero over every sphere, so deltabar (and delta_c) do not depend on e, p.
#   C_max     nonlinear compaction at r_m, (3/5)[1 - (1 + r zeta')^2] (MDPBH.tex:695 with
#             2507.18312:198-205), spherical part: deltabar (1 - mu/e) for 839.
#   mu        peak curvature zeta(0) = 2 ln Psi(0) of MDPBH.tex:839 (gauss2609 only).
# Profiles: "gauss2609" (ratio delta_c/deltabar = e, Euler's number) and "tophat"
# (homogeneous region: all linear measures equal; mu undefined).
# ---------------------------------------------------------------------------------------
EULER = math.e
AMP_PROFILES = ("gauss2609", "tophat")
AMP_MEASURES = ("mu", "central", "mean")


def amplitude_measures(value, measure="central", profile="gauss2609"):
    """All amplitude measures from one of them. measure: 'mu', 'central' (delta_c) or
    'mean' (deltabar). Returns dict(mu, delta_c, deltabar, C_max, ratio_c_over_mean)."""
    v = float(value)
    if profile == "gauss2609":
        if measure == "mu":
            mu = v
        elif measure == "central":
            mu = 5.0 * v / 12.0
        elif measure == "mean":
            mu = 5.0 * EULER * v / 12.0
        else:
            raise ValueError(f"unknown measure {measure!r}")
        dc = 12.0 * mu / 5.0
        db = dc / EULER
        return dict(profile=profile, mu=mu, delta_c=dc, deltabar=db,
                    C_max=db * (1.0 - mu / EULER), ratio_c_over_mean=EULER)
    if profile == "tophat":
        if measure == "mu":
            raise ValueError("mu is defined for the profile of 2609.14218 only")
        if measure not in ("central", "mean"):
            raise ValueError(f"unknown measure {measure!r}")
        return dict(profile=profile, mu=None, delta_c=v, deltabar=v, C_max=None,
                    ratio_c_over_mean=1.0)
    raise ValueError(f"unknown profile {profile!r}")


def convert_amplitude(value, frm, to, profile="gauss2609"):
    """One amplitude measure into another ('mu', 'central', 'mean')."""
    m = amplitude_measures(value, frm, profile)
    return m[{"mu": "mu", "central": "delta_c", "mean": "deltabar"}[to]]


def measures_from_zeta(dzeta, lap_zeta0, r_hi, r_lo=None):
    """Numerical route for any spherical zeta(r) (linear theory, tests the closed forms):
    dzeta(r) = zeta'(r), lap_zeta0 = lap(zeta) at the centre. r_m maximises -r zeta'(r)
    (MDPBH.tex:709 written as d(r zeta')/dr = 0) on (r_lo, r_hi); at a H r_m = 1:
    delta_c = -(2/5) r_m^2 lap_zeta0, deltabar = -(6/5) r_m zeta'(r_m)."""
    from scipy import optimize
    r_lo = 1e-6 * r_hi if r_lo is None else r_lo
    res = optimize.minimize_scalar(lambda r: r * dzeta(r), bounds=(r_lo, r_hi),
                                   method="bounded", options=dict(xatol=1e-12 * r_hi))
    rm = float(res.x)
    return dict(r_m=rm, delta_c=-0.4 * rm * rm * lap_zeta0, deltabar=-1.2 * rm * dzeta(rm))


def predict(delta, e=0.0, p=0.0, sigv=0.0, aend=math.inf, sigmaH=None, zeta_rms=None,
            I=1.0, region="ball", mu=1.0, lnkmin=1.0, profile="tophat", A2=None,
            npart=None, HR_ini=None, noise="poisson"):
    """List of rows, one per criterion: dict(id, criterion, source, collapse, delta_th,
    a_form, spin, note). collapse is True/False, or None when an input is missing."""
    rows = []
    a, b, c = C.eigen_from_dep(delta, e, p)
    if zeta_rms is None and sigmaH is not None:
        zeta_rms = 2.5 * sigmaH

    # R1 hoop, Lagrangian ball with uniform deformation
    h = float(C.hoop_h(a, b, c))
    ac = C.zeldovich_collapse_a(a) if a > 0 else math.inf
    ok = (a > 0) and h <= 1
    rows.append(dict(id="R1", criterion="hoop + Zel'dovich, Lagrangian ball",
                     source="1609.01588:596-607 (t_c: 537)",
                     collapse=bool(ok and ac <= aend), delta_th=float(C.hoop_threshold_delta(e, p)),
                     a_form=ac, spin=None,
                     note=f"h = {h:.3g}" + ("" if ac <= aend or not ok else
                                           f"; pancake at a/a_H = {ac:.3g} > a_end")))

    # R2 hoop, ellipsoidal peak region of a monochromatic spectrum (shape = tide)
    if c > 0:
        H = float(C.hoop_peak_ratio(a, b, c))
        ok = H <= 1
        rows.append(dict(id="R2", criterion="hoop + Zel'dovich, peak ellipsoid (monochromatic)",
                         source="2508.10070:593-598 (322-325)",
                         collapse=bool(ok and ac <= aend),
                         delta_th=float(C.hoop_peak_threshold_delta(e, p)), a_form=ac,
                         spin=0.0, note=f"H = {H:.3g}; spin 0: no tidal torque when shape = "
                                        "tide (584); delta = peak height"))
    else:
        rows.append(dict(id="R2", criterion="hoop + Zel'dovich, peak ellipsoid (monochromatic)",
                         source="2508.10070:593-598", collapse=None, delta_th=None,
                         a_form=None, spin=None,
                         note="not a density peak (gamma <= 0, needs e < (1+p)/3)"))

    # R3 Kerr bound on the angular momentum frozen at maximum expansion
    if region == "ball":
        q = 0.0
    else:
        lam = np.array([a, b, c])
        A = lam ** -0.5 if c > 0 else np.array([np.nan] * 3)
        q = float(C.quadrupole_q(*A)) if c > 0 else math.nan
    tend_tH = aend ** 1.5
    a1 = float(C.spin_a1(q, delta))
    if sigmaH is not None:
        dth, d1, d2, dfd = C.spin_threshold(q, I, sigmaH, tend_tH)
        a2 = float(C.spin_a2(I, sigmaH, delta))
        astar = max(a1, a2)
        rows.append(dict(id="R3", criterion="Kerr bound a* <= 1 (tidal torque, 1st+2nd order)",
                         source="1707.03595:900-960, 925",
                         collapse=bool(delta >= dth), delta_th=dth, a_form=1.0 / delta,
                         spin=astar,
                         note=f"q = {q:.3g}, I = {I:g}; a*(1) = {a1:.3g}, a*(2) = {a2:.3g}; "
                              f"delta_th(1,2,fd) = {d1:.3g}, {d2:.3g}, {dfd:.3g}"))
    else:
        rows.append(dict(id="R3", criterion="Kerr bound a* <= 1 (tidal torque, 1st+2nd order)",
                         source="1707.03595:900-960", collapse=None if a1 <= 1 else False,
                         delta_th=12 / 125 * q * q, a_form=1.0 / delta, spin=a1 if q > 0 else None,
                         note="needs --sigmaH for a*(2); a*(1) alone" if q > 0 else
                              "needs --sigmaH (a*(1) = 0 for a ball)"))

    # R4 finite duration of the matter era: delta(t_end) >= 1
    dfd = 1.0 / aend if math.isfinite(aend) else 0.0
    rows.append(dict(id="R4", criterion="finite duration, t_m = t_H delta^-3/2 < t_end",
                     source="1707.03595:919-927", collapse=bool(delta >= dfd), delta_th=dfd,
                     a_form=1.0 / delta, spin=None, note=f"a_end/a_H = {aend:.4g}"))

    # R5 exact spherical top hat (LTB), no perturbation: always forms, at a_BH
    aBH = C.tophat_aBH(delta) if delta < 0.6 else math.nan
    rows.append(dict(id="R5", criterion="exact spherical top hat (LTB), unperturbed",
                     source="2507.18312:211-214, 310, 316",
                     collapse=bool(np.isfinite(aBH) and aBH <= aend), delta_th=0.0, a_form=aBH,
                     spin=0.0, note=f"R = 2M at a/a_H = {aBH:.4g}; a_max/a_H = "
                                    f"{C.tophat_amax(delta):.4g}"))

    # R6, R7 a velocity dispersion present from the start, adiabatic sigma_v R = const
    sR_over_M = 2.0 * sigv                       # R_H = 2M
    rows.append(dict(id="R6", criterion="velocity dispersion, crossing vs free fall",
                     source="2211.13950:330-359, 715",
                     collapse=bool(C.vd_collapse_adiabatic(sR_over_M)), delta_th=None,
                     a_form=None, spin=None,
                     note=f"sigma_v R/M = {sR_over_M:.3g} (forms if < 3, i.e. sigma_v,H < 1.5)"))
    s_max = sigv * (5 * delta / 3)                # sigma_v at R_max = 3 r_m/(5 delta)
    bmin = C.virial_bmin(s_max, 5 * delta / 6) if delta > 0 else math.inf
    rows.append(dict(id="R7", criterion="velocity dispersion, virial halt radius",
                     source="2507.18312:517-520, 542 (b_BH 316)",
                     collapse=bool(bmin < C.tophat_bBH(delta)), delta_th=None, a_form=None,
                     spin=None, note=f"b_min = {bmin:.3g} vs b_BH = {C.tophat_bBH(delta):.3g} "
                                     "(forms if sigma_v,H < 0.548)"))

    # R8 velocity dispersion generated by small-scale power, log-normal spectrum
    if sigmaH is not None:
        dth = float(C.vd_delta_th(sigmaH, mu, lnkmin))
        rows.append(dict(id="R8", criterion="dispersion from small-scale power (log-normal)",
                         source="2211.13950:551-563", collapse=bool(delta > dth), delta_th=dth,
                         a_form=None, spin=None,
                         note=f"sigma0 = {sigmaH:g}, mu = {mu:g}, ln(kmin/k) = {lnkmin:g}; "
                              f"sigma_cr = {C.vd_sigma_cr(mu, lnkmin):.3g}"))
    else:
        rows.append(dict(id="R8", criterion="dispersion from small-scale power (log-normal)",
                         source="2211.13950:551-563", collapse=None, delta_th=None,
                         a_form=None, spin=None, note="needs --sigmaH"))

    # R9 profile shape + typical perturbations zeta_rms
    if zeta_rms is not None:
        dth = C.profile_threshold(zeta_rms, A2=A2 if profile != "tophat" else None)
        arms = float(C.profile_spin_rms(zeta_rms, delta))
        rows.append(dict(id="R9", criterion="profile flatness + zeta_rms perturbations",
                         source="2507.18312:336-339, 401-412; spin 630-631",
                         collapse=bool(delta > dth), delta_th=dth, a_form=None, spin=arms,
                         note=f"zeta_rms = {zeta_rms:.3g}, profile = "
                              f"{'top hat' if profile == 'tophat' else f'A2 = {A2:g}, A4 = 1'}; "
                              "O(1) factors set to 1"))
    else:
        rows.append(dict(id="R9", criterion="profile flatness + zeta_rms perturbations",
                         source="2507.18312:336-339, 401-412", collapse=None, delta_th=None,
                         a_form=None, spin=None, note="needs --sigmaH or --zeta-rms"))

    # R10 particle shot noise of a simulation (extension, [JUDGEMENT])
    if npart is not None:
        if HR_ini is None:
            raise SystemExit("--npart needs --HR-ini")
        n0 = npart ** -0.5 if noise == "poisson" else npart ** (-2 / 3)
        a_ini = HR_ini ** -2                       # a_ini/a_H = (H R)_ini^-2
        dmax = n0 * C.tophat_amax(delta) / a_ini   # growth ~ a until turnaround
        bmin = 1.2 * dmax ** (2 / 3)               # b_min = 1.2 N^-1/3 for n0 = N^-1/2 at rest
        rows.append(dict(id="R10", criterion=f"particle shot noise ({noise}), halt at b_min",
                         source="2507.18312:483-489, 513 [JUDGEMENT extension]",
                         collapse=bool(bmin < C.tophat_bBH(delta)), delta_th=None, a_form=None,
                         spin=None, note=f"N = {npart:.3g}, noise at t_max = {dmax:.3g}, "
                                         f"b_min = {bmin:.3g} vs b_BH = {C.tophat_bBH(delta):.3g}"))
    return rows


def fmt(x, w=9):
    if x is None:
        return "-".rjust(w)
    if isinstance(x, bool):
        return ("yes" if x else "no").rjust(w)
    if isinstance(x, float) and not math.isfinite(x):
        return "inf".rjust(w) if x > 0 else "nan".rjust(w)
    return f"{x:.3g}".rjust(w)


def amplitude_line(amp, feed):
    """One header line naming every amplitude measure and the one fed to the rows."""
    if amp is None:
        return None
    parts = []
    if amp.get("mu") is not None:
        parts.append(f"mu = {amp['mu']:.4g}")
    parts.append(f"delta_c (central) = {amp['delta_c']:.4g}")
    parts.append(f"deltabar (mean in r_m) = {amp['deltabar']:.4g}")
    if amp.get("C_max") is not None:
        parts.append(f"C_max (nonlinear compaction) = {amp['C_max']:.4g}")
    return (f"# amplitude ({amp['profile']}): " + ", ".join(parts)
            + f"; rows use the {feed} measure")


def print_table(rows, params, out=sys.stdout, amp=None, feed="central"):
    pr = ", ".join(f"{k} = {v}" for k, v in params.items() if v is not None)
    print(f"# inputs: {pr}", file=out)
    al = amplitude_line(amp, feed)
    if al:
        print(al, file=out)
    print(f"{'id':4s} {'criterion':50s} {'collapse':>9s} {'delta_th':>9s} {'a_f/a_H':>9s} "
          f"{'spin':>9s}  source; note", file=out)
    for r in rows:
        col = r["collapse"]
        print(f"{r['id']:4s} {r['criterion'][:50]:50s} "
              f"{('n/a' if col is None else ('yes' if col else 'no')):>9s} "
              f"{fmt(r['delta_th'])} {fmt(r['a_form'])} {fmt(r['spin'])}  "
              f"{r['source']}; {r['note']}", file=out)
    det = [r for r in rows if r["collapse"] is not None]
    yes = [r["id"] for r in det if r["collapse"]]
    no = [r["id"] for r in det if not r["collapse"]]
    print(f"# collapse predicted by {', '.join(yes) or 'none'}; "
          f"no collapse by {', '.join(no) or 'none'}", file=out)
    sp = [(r["id"], r["spin"]) for r in rows if r["spin"] is not None and r["collapse"]]
    if sp:
        print("# spin where given (for criteria that predict collapse): "
              + ", ".join(f"{i} {s:.3g}" for i, s in sp), file=out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    am = ap.add_mutually_exclusive_group(required=True)
    am.add_argument("--delta", type=float,
                    help="linear density contrast of the region at horizon entry, in the "
                         "measure named by --measure")
    am.add_argument("--mu", type=float,
                    help="peak curvature mu of arXiv:2609.14218 (MDPBH.tex:839); implies "
                         "--amp-profile gauss2609")
    ap.add_argument("--measure", choices=["central", "mean"], default="central",
                    help="what --delta is: central contrast delta_c or mean inside r_m "
                         "(deltabar); SCOPE.md 10.1")
    ap.add_argument("--amp-profile", choices=list(AMP_PROFILES), default=None,
                    help="profile for the conversion between measures (default: gauss2609 "
                         "with --mu, tophat with --delta)")
    ap.add_argument("--feed", choices=["central", "mean"], default="central",
                    help="measure handed to the rows (wave 1: central)")
    ap.add_argument("--e", type=float, default=0.0, help="ellipticity")
    ap.add_argument("--p", type=float, default=0.0, help="prolateness, -e <= p <= e")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--sigv", type=float, default=None,
                   help="3D velocity dispersion at horizon entry (units of c)")
    g.add_argument("--sigv-ini", type=float, default=None,
                   help="3D velocity dispersion on the initial slice (needs --HR-ini)")
    ap.add_argument("--HR-ini", type=float, default=None,
                    help="H R of the region on the initial slice (areal radius/Hubble radius)")
    d = ap.add_mutually_exclusive_group()
    d.add_argument("--aend", type=float, default=math.inf, help="a_end / a_H")
    d.add_argument("--efolds", type=float, default=None, help="ln(a_end/a_H)")
    ap.add_argument("--sigmaH", type=float, default=None,
                    help="rms density contrast at horizon entry on the PBH scale")
    ap.add_argument("--zeta-rms", type=float, default=None)
    ap.add_argument("--I", type=float, default=1.0, help="second-order torque factor (1707)")
    ap.add_argument("--region", choices=["ball", "peak"], default="ball",
                    help="Lagrangian ball (expanding-ball data) or peak ellipsoid")
    ap.add_argument("--mu-ln", type=float, default=1.0,
                    help="log-normal width mu of 2211.13950 (was --mu in wave 1; --mu is now "
                         "the amplitude of 2609.14218)")
    ap.add_argument("--lnkmin", type=float, default=1.0, help="ln(k_min/k_PBH) (2211)")
    ap.add_argument("--A2", type=float, default=None,
                    help="profile curvature A2 (2507); default: top hat")
    ap.add_argument("--npart", type=float, default=None, help="particle number (shot noise)")
    ap.add_argument("--noise", choices=["poisson", "lattice"], default="poisson")
    ap.add_argument("--json", action="store_true", help="print JSON instead of the table")
    a = ap.parse_args(argv)
    if a.p < -a.e - 1e-12 or a.p > a.e + 1e-12:
        print("warning: p outside [-e, e] breaks alpha >= beta >= gamma", file=sys.stderr)
    sigv = a.sigv if a.sigv is not None else 0.0
    if a.sigv_ini is not None:
        if a.HR_ini is None:
            ap.error("--sigv-ini needs --HR-ini")
        sigv = a.sigv_ini / a.HR_ini ** 2        # sigma_v R conserved, R_ini/R_H = (HR)^-2
    aend = math.exp(a.efolds) if a.efolds is not None else a.aend
    prof = a.amp_profile or ("gauss2609" if a.mu is not None else "tophat")
    if a.mu is not None:
        amp = amplitude_measures(a.mu, "mu", prof)
    else:
        amp = amplitude_measures(a.delta, a.measure, prof)
    delta = amp["delta_c"] if a.feed == "central" else amp["deltabar"]
    params = dict(delta=delta, e=a.e, p=a.p, sigv_H=sigv, aend=aend, sigmaH=a.sigmaH,
                  zeta_rms=a.zeta_rms, I=a.I, region=a.region, mu_lognormal=a.mu_ln,
                  lnkmin=a.lnkmin, A2=a.A2, npart=a.npart, HR_ini=a.HR_ini)
    rows = predict(delta, a.e, a.p, sigv, aend, a.sigmaH, a.zeta_rms, a.I, a.region, a.mu_ln,
                   a.lnkmin, "tophat" if a.A2 is None else "A2", a.A2, a.npart, a.HR_ini,
                   a.noise)
    if a.json:
        print(json.dumps(dict(inputs=params, amplitude=amp, feed=a.feed, rows=rows),
                         indent=1, default=str))
    else:
        print_table(rows, params, amp=amp, feed=a.feed)


if __name__ == "__main__":
    main()
