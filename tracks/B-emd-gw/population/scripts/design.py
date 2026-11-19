"""Semi-analytic design of the halo-population box of Track B (package population).

    python3 design.py            (output in $NRPIC_RUN_DIR, copies into ../results, ../figs)

Units G = c = 1, a = 1 and H = 1 at the start, lengths in initial Hubble radii, conformal
time t, a = (1 + t/2)^2, conformal Hubble rate Hc = a^(-1/2), comoving mean density
rho_c = 3/(8 pi). Field: scripts/make_ic.py (P_delta(k, a = 1) = 2 pi^2 (4/25) A_s k,
sharp cut at k_c = nc 2 pi/L, rms sigma1 at a = 1).

What it computes (every formula is stated where it is used; labels in DESIGN.md):
1. Scales against the box size L at fixed nc and sigma1: horizon entry of the cut mode,
   rms contrast there (the sigma of arXiv:2403.15126 and 2605.04487), linear potential,
   collapse epochs of peaks of height nu, virial potential and speed of the halos, virial
   radius in cells at 64, 128, 256 cells, halo dynamical and light-crossing wave numbers.
2. Expected number of maxima (BBKS, eq. 4.3 with f of eq. A15) against nc, and the
   Press-Schechter (sharp-k filter) number of halos against a.
3. The maxima of the realized field (seed 1, 64 cells), their deformation eigenvalues at
   a = 1, and the quadrupole-formula energy each radiates up to its first axis crossing
   from the wave-1 baseline (homogeneous ellipsoid, model A, tracks/B-emd-gw/baseline/
   scripts/ellipsoid.py), scaled to the patch: E = [E_lib/(M_lib c^2)] M R_L^7 c^2.
4. The quasi-static second-order TT strain of the same field, h = (20/3) [d_i Phi d_j
   Phi]^TT / k^2 (matter era, Phi constant), which for two crossed waves gives the
   (5/12) phi_x phi_y that the first source measured in the code to 0.2-0.4 per cent
   (stage/REVIEW-wave2.md), and its gradient energy against a.
5. Card cost of the relativistic run at 64, 128, 256 cells from the measured throughput.
"""
import json
import os
import shutil
import sys

import numpy as np
from scipy.integrate import quad
from scipy.special import erf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
PKG = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(ROOT, "cosmo", "ic"))
sys.path.insert(0, os.path.join(ROOT, "python"))
sys.path.insert(0, os.path.join(ROOT, "tracks", "B-emd-gw", "baseline", "scripts"))
sys.path.insert(0, HERE)
import random_field as rf            # noqa: E402
import cosmo_id as cid               # noqa: E402
import ellipsoid as el               # noqa: E402
from make_ic import pk_unit, mesh_sigma2_unit, RHO_M   # noqa: E402
from nrpic import figstyle as fs     # noqa: E402

DC = 1.686                     # spherical-collapse threshold [BACKGROUND]
DVIR = 18.0*np.pi**2           # virial overdensity in EdS [BACKGROUND]
NC, SIGMA1, SEED = 3.2, 0.0562, 1
LBOX = (2.0, 4.0, 8.0, 16.0)
NMESH = (64, 128, 256)

# measured card throughput, zone-cycles per second (one A100), with the source:
#   64^3, 1 ppc: runs/cosmo/east_d0.01_n64_pcs4b/athena.20261114-072656.log (5.770e6),
#   128^3, 1 ppc, quadratic cloud: runs/cosmo/east_d0.01_n128_tsc/athena.20261114-021442.log
#   (4.467e6); 128^3, 1 ppc, production configuration: runs/cosmo/dav_c256_n128_pcs4bt/
#   chain/seg00{1,2}*.log (5.7e6, 5.6e6); quoted in tracks/B-emd-gw/scope/SCOPE.md sec. 9.
#   Memory: 1685 MiB (64^3), 5083 MiB (128^3), linear in the cells between them.
RATE = {64: 5.77e6, 128: 4.47e6, 256: 4.47e6}   # 256: assumed equal to 128 [JUDGEMENT]
MEM_MIB = {64: 1685.0, 128: 5083.0}


def out_dir():
    d = os.environ.get("NRPIC_RUN_DIR")
    if not d:
        d = os.path.join(ROOT, "..", "..", "scratch", "B-emd-gw", "tmp", "design")
    os.makedirs(d, exist_ok=True)
    return d


# ---------------------------------------------------------------------------------------
# 1. scales
# ---------------------------------------------------------------------------------------
def scales(L, nc=NC, sigma1=SIGMA1):
    kc = nc*2.0*np.pi/L
    a_k = 1.0/kc**2                    # Hc(a_k) = a_k^(-1/2) = kc
    sig_H = sigma1*a_k                 # rms contrast of the cut band at its horizon entry
    s2u, _ = mesh_sigma2_unit(64, L, kc)
    As = sigma1**2/s2u
    # rms linear potential (3/2) delta_k/k^2 over the band (continuum, |k| < kc):
    # <Phi^2> = int dk k^2/(2 pi^2) (9/4) P(k)/k^4
    # (Delta^2_Phi is constant: the integral runs over the box modes, k_f <= |k| <= k_c;
    # evaluated as the sum over the modes of the 64-cell mesh)
    n = 64
    k1 = 2.0*np.pi*np.fft.fftfreq(n, d=L/n)
    kx, ky, kz = np.meshgrid(k1, k1, k1, indexing="ij")
    km = np.sqrt(kx*kx + ky*ky + kz*kz)
    ok = (km > 0) & (km <= kc*(1 + 1e-12))
    phi2 = float(((9.0/4.0)*As*pk_unit(km[ok])/km[ok]**4).sum()/L**3)
    RL = 1.5/kc                        # Lagrangian radius of a peak core [JUDGEMENT]
    M = 0.5*RL**3                      # rho_c (4 pi/3) R_L^3
    rows = []
    for nu in (1.0, 2.0, 3.0):
        a_c = DC/(nu*sigma1)
        phi_vir = 0.5*DVIR**(1.0/3.0)*RL**2/a_c       # G M / r_vir (physical)
        r_vir_c = RL/DVIR**(1.0/3.0)                  # comoving virial radius
        omega_dyn = np.sqrt(DVIR/2.0)/np.sqrt(a_c)     # sqrt(G rho_vir) in conformal time
        rows.append({"nu": nu, "a_c": a_c, "t_c": 2.0*(np.sqrt(a_c) - 1.0),
                     "Phi_lin": 1.5*DC/(kc**2*a_c), "Phi_vir": phi_vir,
                     "v_vir": float(np.sqrt(phi_vir)),
                     "r_vir_cells": {n: r_vir_c/(L/n) for n in NMESH},
                     "k_dyn": omega_dyn, "k_cross": 2.0*np.pi/(2.0*r_vir_c)})
    return {"L": L, "k_c": kc, "k_f": 2*np.pi/L, "a_k": a_k, "sigma_H": sig_H, "A_s": As,
            "Phi_rms_lin": float(np.sqrt(phi2)), "R_L": RL, "M_peak": M,
            "kc_over_Hc_at_a1": kc, "peaks": rows}


# ---------------------------------------------------------------------------------------
# 2. counts
# ---------------------------------------------------------------------------------------
def _f_bbks(x):
    a = (x**3 - 3*x)/2*(erf(np.sqrt(2.5)*x) + erf(np.sqrt(2.5)*x/2))
    b = np.sqrt(2/(5*np.pi))*((31*x**2/4 + 1.6)*np.exp(-5*x**2/8)
                              + (x**2/2 - 1.6)*np.exp(-2.5*x**2))
    return a + b


def bbks_counts(nc, L=4.0, nus=(0.0, 1.0, 2.0, 3.0)):
    """Maxima per box above each nu for the sharp-cut k^4 spectrum: gamma = sqrt(32)/6,
    R_* = 2/k_c (moments sigma_j^2 ~ k_c^(4+2j)/(4+2j))."""
    g = np.sqrt(32.0)/6.0
    Rs = 2.0/(nc*2*np.pi/L)

    def dn(nu):
        G = quad(lambda x: _f_bbks(x)*np.exp(-(x - g*nu)**2/(2*(1 - g*g)))
                 / np.sqrt(2*np.pi*(1 - g*g)), 0, 40)[0]
        return np.exp(-nu*nu/2)*G/((2*np.pi)**2*Rs**3)
    return {nu: quad(dn, nu, 9)[0]*L**3 for nu in nus}


def ps_counts(a, L=4.0, nc=NC, sigma1=SIGMA1):
    """Press-Schechter halo number in the box with the sharp-k filter (M = 6 pi^2 rho_c
    / k^3, as arXiv:2312.12499 main.tex:600). sigma(k_R, a) = sigma1 a (k_R/k_c)^2 for
    k_R <= k_c (sigma ~ M^(-2/3)); below the cut mass M_c the variance does not grow,
    so the collapsed fraction erfc(nu_c/sqrt 2) not in halos above M_c is counted in
    halos of mass M_c. Returns (number of halos, collapsed fraction, M_c)."""
    from scipy.special import erfc
    kc = nc*2*np.pi/L
    Mc = 6*np.pi**2*RHO_M/kc**3
    kR = np.logspace(np.log10(2*np.pi/L), np.log10(kc), 400)[::-1]   # M ascending
    M = 6*np.pi**2*RHO_M/kR**3
    nu = DC/(sigma1*a*(kR/kc)**2)
    dndlnM = np.sqrt(2/np.pi)*RHO_M/M*nu*(2.0/3.0)*np.exp(-nu*nu/2)
    lnM = np.log(M)
    N_above = float(np.trapz(dndlnM, lnM))*L**3
    f_above = float(np.trapz(M*dndlnM/RHO_M, lnM))
    f_tot = float(erfc(DC/(sigma1*a)/np.sqrt(2)))
    N_at_Mc = max(f_tot - f_above, 0.0)*RHO_M*L**3/Mc
    return N_above + N_at_Mc, f_tot, Mc


# ---------------------------------------------------------------------------------------
# 3. peaks of the realized field and their baseline energy
# ---------------------------------------------------------------------------------------
def realized_field(n=64, L=4.0, nc=NC, sigma1=SIGMA1, seed=SEED):
    kc = nc*2*np.pi/L
    s2u, _ = mesh_sigma2_unit(n, L, kc)
    As = sigma1**2/s2u
    return rf.gaussian_field(n, L, lambda k: As*pk_unit(k), seed, kcut=kc, cut="sharp",
                             zero_nyquist=True), As


def find_maxima(delta):
    n = delta.shape[0]
    is_max = np.ones_like(delta, dtype=bool)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dz in (-1, 0, 1):
                if dx == dy == dz == 0:
                    continue
                is_max &= delta > np.roll(delta, (dx, dy, dz), axis=(0, 1, 2))
    return np.argwhere(is_max & (delta > 0))


def deformation(delta, L):
    """d_ij = d_i d_j lap^-1 delta on the mesh (trace = delta), six arrays."""
    tor = cid.Torus(delta.shape[0], L)
    k2 = tor.k2.copy()
    k2[0, 0, 0] = 1.0
    G = -tor.fft(delta)/k2
    G[0, 0, 0] = 0.0
    kd = tor.kd
    return {(i, j): tor.ifft(-kd[i]*kd[j]*G) for i in range(3) for j in range(i, 3)}


def baseline_energy(lam):
    """Model-A energy (units of M c^2 of the library, horizon-sized patch) radiated from
    t_turn to the first axis crossing, and that crossing time in units of t_k."""
    r = el.integrate(np.asarray(lam), "A", 6.0*el.t_turn(lam[0]))
    if not r["crossings"]:
        return np.nan, np.nan
    tx = r["crossings"][0][0]
    s = el.sample(r, np.array([tx*(1 - 1e-9)]))
    return float(s["E"][0]/el.MASS), float(tx)


def peaks_and_energy(delta, L, sigma1):
    n = delta.shape[0]
    idx = find_maxima(delta)
    d = deformation(delta, L)
    out = []
    for (i, j, k) in idx:
        D = np.array([[d[min(p, q), max(p, q)][i, j, k] for q in range(3)] for p in range(3)])
        ev = np.sort(np.linalg.eigvalsh(D))[::-1]           # alpha >= beta >= gamma
        nu = delta[i, j, k]/delta.std()
        rec = {"cell": [int(i), int(j), int(k)], "delta": float(delta[i, j, k]),
               "nu": float(nu), "lam": [float(x) for x in ev]}
        if ev[0] > 0:
            E_lib, tx = baseline_energy(ev)
            # t_k of the library is the reference epoch a = 1 (cosmic time 2/3 in code
            # units); first crossing a_x = (t_x/t_k)^(2/3)
            rec.update({"E_over_Mc2_lib": E_lib, "a_x": float(tx**(2.0/3.0)),
                        "a_turn": float(1.0/(2.0*ev[0]))})
        out.append(rec)
    return out


# ---------------------------------------------------------------------------------------
# 4. quasi-static second-order TT strain
# ---------------------------------------------------------------------------------------
def quasi_static_tt(delta, L):
    """h_ij = (20/3) [d_i Phi d_j Phi]^TT / k^2 with Phi = -(3/2) lap^-1 delta (a = 1,
    linear, constant in time), on the rfft layout of cosmo_id.Torus; returns
    sum_k k^2 |h_ij|^2, sum_k |h_ij|^2 (summed over i, j and over the full mesh of
    modes, coefficients fftn/N) and the rms strain."""
    n = delta.shape[0]
    N = n**3
    tor = cid.Torus(n, L)
    k2 = tor.k2.copy()
    k2[0, 0, 0] = 1.0
    Phi_k = 1.5*tor.fft(delta)/k2
    Phi_k[0, 0, 0] = 0.0
    g = [tor.ifft(1j*kd*Phi_k) for kd in tor.kd]           # d_i Phi
    e = [kc/np.sqrt(k2) for kc in tor.k]
    S = {}
    for i in range(3):
        for j in range(i, 3):
            S[i, j] = np.fft.rfftn((20.0/3.0)*g[i]*g[j])/N

    def Sij(i, j):
        return S[min(i, j), max(i, j)]
    P = [[(1.0 if i == j else 0.0) - e[i]*e[j] for j in range(3)] for i in range(3)]
    w = np.full(n//2 + 1, 2.0)
    w[0] = 1.0
    if n % 2 == 0:
        w[-1] = 1.0
    w = np.broadcast_to(w[None, None, :], k2.shape)
    trP = sum(P[l][m]*Sij(l, m) for l in range(3) for m in range(3))
    tot_g, tot = 0.0, 0.0
    for i in range(3):
        for j in range(3):
            acc = 0.0
            for l in range(3):
                for m in range(3):
                    acc = acc + P[i][l]*P[j][m]*Sij(l, m)
            hij = (acc - 0.5*P[i][j]*trP)/k2
            hij[0, 0, 0] = 0.0
            tot_g += float((w*np.abs(hij)**2*tor.k2).sum())
            tot += float((w*np.abs(hij)**2).sum())
    return tot_g, tot, float(np.sqrt(tot))


# ---------------------------------------------------------------------------------------
# 5. card cost of the relativistic run
# ---------------------------------------------------------------------------------------
def gr_cost(n, L, a_end, ppc_factor=1.0, cfl=0.25, dtexp=0.01):
    """Steps with dt = min(cfl L/n, dtexp sqrt(a)) in conformal time, a = (1+t/2)^2:
    the expansion limit binds while sqrt(a) < cfl L/(n dtexp)."""
    dx = L/n
    t_end = 2.0*(np.sqrt(a_end) - 1.0)
    sa_sw = cfl*dx/dtexp                 # sqrt(a) where the two limits meet
    if sa_sw <= 1.0:
        steps = t_end/(cfl*dx)
    elif sa_sw >= np.sqrt(a_end):
        steps = (2.0/dtexp)*np.log(np.sqrt(a_end))
    else:
        t_sw = 2.0*(sa_sw - 1.0)
        steps = (2.0/dtexp)*np.log(sa_sw) + (t_end - t_sw)/(cfl*dx)
    cells = n**3
    sec = steps*cells/RATE[n]*ppc_factor
    c = (MEM_MIB[128] - MEM_MIB[64])/(128**3 - 64**3)
    mem = (MEM_MIB[64] + c*(cells - 64**3))/1024.0
    return {"n": n, "L": L, "a_end": a_end, "steps": int(np.ceil(steps)),
            "card_hours": sec/3600.0, "memory_GiB": mem}


# ---------------------------------------------------------------------------------------
def main():
    od = out_dir()
    res = {"nc": NC, "sigma1": SIGMA1, "seed": SEED}
    res["scales"] = [scales(L) for L in LBOX]
    res["bbks"] = {str(nc): bbks_counts(nc) for nc in (2.0, 3.2, 4.0, 6.4)}
    agrid = np.logspace(np.log10(5.0), np.log10(200.0), 60)
    ps = [ps_counts(a) for a in agrid]
    res["press_schechter"] = {"a": agrid.tolist(), "N_halos": [p[0] for p in ps],
                              "f_coll": [p[1] for p in ps], "M_c": ps[0][2]}
    # realized field
    delta, As = realized_field()
    pk = peaks_and_energy(delta, 4.0, SIGMA1)
    for rec in pk:
        if "E_over_Mc2_lib" in rec:
            sc = res["scales"][1]
            rec["E_code_L4"] = rec["E_over_Mc2_lib"]*sc["M_peak"]*sc["R_L"]**7
    res["peaks_seed1"] = pk
    # baseline radiative estimate against a (L = 4); E emitted at a_x redshifts as 1/a
    rho_c = RHO_M
    L = 4.0
    Ed = [(r["a_x"], r["E_code_L4"]) for r in pk if "E_code_L4" in r and np.isfinite(r["E_code_L4"])]
    Omega_rad = []
    for a in agrid:
        s = sum(E*ax for ax, E in Ed if ax <= a)
        Omega_rad.append(s/(a*L**3*rho_c))
    res["Omega_rad_baseline_L4"] = Omega_rad
    tot_g, tot, hrms = quasi_static_tt(delta, L)
    # gradient energy of the static field: rho = sum k^2 |h|^2/(32 pi a^2) (physical)
    # over rho_bar = rho_c/a^3: Omega_qs = a sum k^2 |h|^2/(32 pi rho_c)
    res["quasi_static"] = {"sum_k2_h2": tot_g, "h_rms": hrms,
                           "Omega_qs_over_a": tot_g/(32*np.pi*rho_c)}
    # check of the formula on the first source (two crossed waves, delta = 0.01, eps = 1):
    # (5/12) phi_x phi_y with phi = 1.82e-2 is 1.38e-4? -> see DESIGN.md; here only the
    # relation h(K) = (20/3) S/|K|^2 for one mode pair is evaluated numerically
    n = 32
    Lw = 4.0
    x = (np.arange(n) + 0.5)*Lw/n
    X, Y, Z = np.meshgrid(x, x, x, indexing="ij")
    kw = 2*np.pi/Lw
    phi_x, phi_y = 1.0e-2, 0.9e-2
    # delta that gives Phi = phi_x sin(k x) + phi_y sin(k y): delta = -(2/3) lap Phi
    dw = (2.0/3.0)*kw**2*(phi_x*np.sin(kw*X) + phi_y*np.sin(kw*Y))
    tg, t0, _ = quasi_static_tt(dw, Lw)
    # |h_+(K)|^2 summed over the four modes (+-k, +-k, 0) and the 2 x 2 components:
    # expected 4 modes x |h_+|^2 x (sum_ij e+_ij e+_ij = 2) / ... reported as rms per mode
    # h_ij = h_+ (u u - z z) with |h_+| = (5/12) phi_x phi_y at each of the four modes
    # (+-k, +-k, 0) (scope/SCOPE.md lines 106-112): sum_k sum_ij |h_ij|^2 = 4 x 2 |h_+|^2
    res["crossed_wave_check"] = {"sum_h2": t0, "expected_sum_h2":
                                 4*2*((5.0/12.0)*phi_x*phi_y)**2}
    res["gr_cost"] = [gr_cost(n, L, ae) for n in NMESH for L in (2.0, 4.0, 8.0)
                      for ae in (100.0, 200.0)]
    with open(os.path.join(od, "design.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)
    figures(res, od)
    os.makedirs(os.path.join(PKG, "results"), exist_ok=True)
    shutil.copy(os.path.join(od, "design.json"), os.path.join(PKG, "results", "design.json"))
    for fn in os.listdir(od):
        if fn.startswith("design_") and fn.endswith(".png"):
            shutil.copy(os.path.join(od, fn), os.path.join(PKG, "figs", fn))
    print(json.dumps({k: res[k] for k in ("bbks", "quasi_static", "crossed_wave_check")},
                     indent=1, default=float))


def figures(res, od):
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.17, top=0.9, wspace=0.38)
    # left: Phi_vir and v_vir against L for nu = 1, 2, 3
    ax = axs[0]
    cols = fs.series_colors(3)
    for j, nu in enumerate((1.0, 2.0, 3.0)):
        Ls = [s["L"] for s in res["scales"]]
        pv = [s["peaks"][j]["Phi_vir"] for s in res["scales"]]
        pl = [s["peaks"][j]["Phi_lin"] for s in res["scales"]]
        ax.loglog(Ls, pv, "-o", color=cols[j], ms=3, label=fr"$\nu={nu:.0f}$, virial")
        ax.loglog(Ls, pl, ":", color=cols[j])
    ax.axhline(0.25, color="k", ls="--", lw=1.0)
    ax.text(2.1, 0.3, r"$2GM/rc^2 \approx 0.5$", fontsize=8)
    ax.set_xlabel(r"box $L$ [initial Hubble radii]")
    ax.set_ylabel(r"$\Phi$ at collapse (dotted: linear)")
    ax.legend(fontsize=7, loc="lower right")
    # middle: halo counts
    ax = axs[1]
    ps = res["press_schechter"]
    ax.semilogx(ps["a"], ps["N_halos"], color=fs.PAL["blue"],
                label=r"Press-Schechter, $M\geq M_c$")
    for nc, c in zip(("3.2", "4.0"), (fs.PAL["red"], fs.PAL["orange"])):
        b = res["bbks"][nc]
        ax.axhline(b[0.0], color=c, ls="--", lw=1.0, label=f"BBKS maxima, nc = {nc}")
    ax.set_xlabel(r"$a$")
    ax.set_ylabel("halos in the box (L = 4)")
    ax.legend(fontsize=7, loc="upper left")
    # right: Omega estimates
    ax = axs[2]
    a = np.array(ps["a"])
    om = np.array(res["Omega_rad_baseline_L4"])
    ax.loglog(a, np.where(om > 0, om, np.nan), color=fs.PAL["red"],
              label="radiated, baseline model A")
    ax.loglog(a, res["quasi_static"]["Omega_qs_over_a"]*a, color=fs.PAL["blue"], ls="--",
              label="quasi-static TT (2nd order)")
    ax.set_xlabel(r"$a$")
    ax.set_ylabel(r"$\rho_{\rm GW}/\bar\rho$  (L = 4)")
    ax.legend(fontsize=7, loc="lower right")
    fs.save(fig, os.path.join(od, "design_scales"))
    plt.close(fig)


if __name__ == "__main__":
    main()
