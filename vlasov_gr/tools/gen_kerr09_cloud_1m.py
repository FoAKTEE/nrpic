#!/usr/bin/env python3
"""Generate a 1,000,000-particle inclined grazing cloud (NRPIC001) around a chi=0.90 spinning BH."""
import argparse
import json
import math
from pathlib import Path
import numpy as np
from scipy.stats import qmc


def sample_ball_poly(u_r, u_cos, u_phi, R_cl):
    """Sample smooth compact rho(r) proportional to (1 - (r/R_cl)^2)^2 inside sphere of radius R_cl."""
    # CDF F(s) = (105/16) * (s^3/3 - 2*s^5/5 + s^7/7), s in [0, 1]
    lo = np.zeros_like(u_r)
    hi = np.ones_like(u_r)
    for _ in range(32):
        mid = 0.5 * (lo + hi)
        m2 = mid * mid
        cdf = (105.0 / 16.0) * (mid**3 / 3.0 - 0.4 * (mid**5) + (mid**7) / 7.0)
        lo = np.where(cdf < u_r, mid, lo)
        hi = np.where(cdf >= u_r, mid, hi)
    r = 0.5 * (lo + hi) * R_cl
    cos_t = 2.0 * u_cos - 1.0
    sin_t = np.sqrt(np.maximum(0.0, 1.0 - cos_t * cos_t))
    phi = 2.0 * np.pi * u_phi
    x = r * sin_t * np.cos(phi)
    y = r * sin_t * np.sin(phi)
    z = r * cos_t
    return np.stack([x, y, z], axis=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="Output NRPIC001 .nrp file path")
    ap.add_argument("--meta", required=True, help="Output metadata .json path")
    ap.add_argument("--n", type=int, default=1_000_000, help="Particle count")
    ap.add_argument("--mass", type=float, default=0.05, help="Total cloud rest mass in M_BH")
    ap.add_argument("--radius", type=float, default=1.4, help="Cloud outer radius R_cl [M]")
    ap.add_argument("--r0", type=float, default=7.0, help="Initial radial distance [M]")
    ap.add_argument("--inc-deg", type=float, default=20.0, help="Orbital inclination above spin plane [deg]")
    ap.add_argument("--L-orb", type=float, default=2.62, help="Specific orbital angular momentum [M]")
    ap.add_argument("--ur-in", type=float, default=-0.04, help="Initial inward radial covariant u_r")
    ap.add_argument("--sig-u", type=float, default=0.04, help="Isotropic thermal velocity dispersion")
    ap.add_argument("--seed", type=int, default=20261125)
    args = ap.parse_args()

    N = int(args.n)
    # Use 2^20 Sobol points and slice first N for ultra-low discrepancy (or exact Sobol up to N)
    m_pow = int(math.ceil(math.log2(N)))
    sob = qmc.Sobol(d=6, scramble=True, seed=args.seed)
    U = sob.random_base2(m=m_pow)[:N]

    # Spatial positions relative to center
    dx = sample_ball_poly(U[:, 0], U[:, 1], U[:, 2], args.radius)
    inc = math.radians(args.inc_deg)
    xc = np.array([args.r0 * math.cos(inc), 0.0, args.r0 * math.sin(inc)], dtype=np.float64)
    x = dx + xc[None, :]

    # Smooth differential Keplerian-like prograde orbital velocity tilted by inclination inc
    # Orbital plane normal n_orb = (-sin(inc), 0, cos(inc)), tangent at phi=0 along +y
    # For each particle at cylindrical radius rho_p in orbital plane:
    # e_phi = (n_orb x r_hat), v_orb = (L_orb / r) -> covariant u_phi ~ psi^4 * v_orb
    # Approximate isotropic conformal factor psi(r) = 1 + 0.5 / r_p near r ~ 8 M
    r_p = np.sqrt(np.sum(x * x, axis=1))
    psi = 1.0 + 0.5 / np.maximum(r_p, 1.0)
    gamma_iso = psi**4

    n_orb = np.array([-math.sin(inc), 0.0, math.cos(inc)], dtype=np.float64)
    r_hat = x / r_p[:, None]
    e_phi = np.cross(n_orb[None, :], r_hat)
    e_phi_norm = np.linalg.norm(e_phi, axis=1, keepdims=True)
    e_phi = e_phi / np.maximum(e_phi_norm, 1e-12)

    # Covariant angular momentum u_phi_hat ~ L_orb / r_p * (local isotropic scale ~ 1)
    # Give inner half slightly tighter orbit, outer half follows smooth rigid/Keplerian shear
    u_tan = args.L_orb / r_p
    u_orb = u_tan[:, None] * e_phi + args.ur_in * r_hat * gamma_iso[:, None]

    # Inverse-normal transform for 3D thermal dispersion via Sobol U[:, 3:6]
    from scipy.special import ndtri
    U_clip = np.clip(U[:, 3:6], 1e-9, 1.0 - 1e-9)
    du = args.sig_u * ndtri(U_clip)
    # Zero mean du so total cloud momentum is exact
    du -= np.mean(du, axis=0, keepdims=True)
    # Multiply by sqrt(gamma_iso) ~ psi^2 so proper-frame dispersion = sig_u
    u = u_orb + (psi**2)[:, None] * du

    mp = float(args.mass) / float(N)
    m = np.full(N, mp, dtype=np.float64)
    species = np.zeros(N, dtype=np.int32)

    # Total linear momentum & angular momentum
    P_tot = np.sum(m[:, None] * u, axis=0)
    J_tot = np.sum(m[:, None] * np.cross(x, u), axis=0)
    x_cm = np.sum(m[:, None] * x, axis=0) / np.sum(m)

    out_p = Path(args.out)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    # NRPIC001 format: 8-byte magic, int64 N, N*7 float64 (x,y,z,ux,uy,uz,m), N int32 species
    rec = np.column_stack([x, u, m]).astype(np.float64, copy=False)
    with open(out_p, "wb") as fp:
        fp.write(b"NRPIC001")
        np.array([N], dtype=np.int64).tofile(fp)
        rec.tofile(fp)
        species.tofile(fp)

    meta = {
        "nparticles": N,
        "mass_total": float(np.sum(m)),
        "particle_mass": mp,
        "center_M": xc.tolist(),
        "x_cm_M": x_cm.tolist(),
        "R_cl_M": args.radius,
        "inc_deg": args.inc_deg,
        "L_orb_M": args.L_orb,
        "ur_in": args.ur_in,
        "sig_u": args.sig_u,
        "P_cloud": P_tot.tolist(),
        "P_BH_comp": (-P_tot).tolist(),
        "J_cloud": J_tot.tolist(),
        "nrp_bytes": int(out_p.stat().st_size),
    }
    with open(args.meta, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"Wrote {out_p} ({meta['nrp_bytes']/1e6:.2f} MB) | N={N}")
    print(f"P_cloud = {P_tot.tolist()} -> P_BH_comp = {(-P_tot).tolist()}")
    print(f"J_cloud = {J_tot.tolist()}")


if __name__ == "__main__":
    main()
