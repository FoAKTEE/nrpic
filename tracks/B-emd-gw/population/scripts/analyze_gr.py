#!/usr/bin/env python3
"""Analysis of the full-relativity population runs (pop_s014_gr, pop_s028_gr) against the
Newtonian population (fidL8) and the design's signal estimate (DESIGN.md sections 5, 6).

    python3 analyze_gr.py --run s014:DIR:0.014 [--run s028:DIR:0.028] \
        --newton ../results/analysis_fidL8.json --newton-dir NEWTON_CASE_DIR [--workers 4]

Writes into $NRPIC_RUN_DIR analysis_gr.json and the figures pop_gr_*.png (PDF beside).
Predictions A1-A3, H1-H2, Z: JOURNAL.md, entry of 2026-11-24 05:15.

Units as in analyze.py: G = c = 1, comoving x, conformal time t, a = (1 + t/2)^2, box L = 8.

1. Constraints and gauge: pop.cstat.hst, pop.nrpic.hst (rows of a preempted segment that
   the restart repeated are dropped: the last row of each time is kept).
2. Halos: friends-of-friends of analyze.py (b = 0.2 of the mean spacing) on the particle
   snapshots pop.part.NNNNN.bin, counted above a common mass limit (100 particles of the
   Newtonian fidL8 run, 800 of these runs); compared with the fidL8 catalogues at the same
   stage a_N = a sigma1/0.0562 (the Newtonian problem depends on sigma1 a only, P4).
3. TT strain of the metric: h = tilde gamma - delta from the double-precision Z4c dumps
   (bin/pop.z4cd.NNNNN.bin), flat TT projection (gw_diag tt), raw at every dump and with
   the spatial-gauge piece removed (gw_diag gauge.tt_strain_from_conformal, G_tot) at the
   dumps that coincide with particle snapshots. Measures (rfftn coefficients h_k / N):
     rms     sqrt(sum_ab mean_x h_ab^2),
     Omega_qs = (a/(32 pi rho_c)) sum_ab sum_k w k^2 |h_ab,k|^2   (analyze.py's near-field
               measure applied to the metric),
   and, at the snapshot times, the weak-field quasi-static strain of the run's own
   particles, h_qs = S^TT/k^2 with S = 16 pi rho_c v v/a + 4 dPhi_N dPhi_N (analyze.py,
   cloud-in-cell on the 128^3 mesh; v = u/(a W) from the covariant u of the snapshot),
   compared mode by mode (correlation coefficient and rms ratio) in bands |k| <= n k_f.
4. The stop of the 0.028 run (Z): history of alpha, chi, K = Khat + 2 Theta at the cell
   the guard names, the largest K of each dump and where it lies, the densest particle
   concentration of the last snapshot.
"""
import argparse
import glob
import json
import os
import sys
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(PKG, "..", "gw_diag"))
sys.path.insert(0, os.path.join(ROOT, "python"))
import analyze as an                                   # noqa: E402
from gwdiag import binio, readers, gauge, tt           # noqa: E402
from nrpic import figstyle as fs                       # noqa: E402
from nrpic.newton import read_snapshot                 # noqa: E402

RHO_C = 3.0/(8.0*np.pi)
SIG_FID = 0.0562
L = 8.0
N_NEWTON = 64                  # fidL8: the L = 4, 64^3 run scaled by 2
BANDS = (4, 8, 16, 64)
DESIGN_QS = 1.18e-8*2**6       # Omega_qs/a of the seed-1 field at L = 8, sigma1 = 0.0562


def scale(t):
    return (1.0 + 0.5*np.asarray(t))**2


def read_hst(fn):
    """Rows of a history file, the last row of each time kept (restarts repeat rows)."""
    rows = np.loadtxt(fn)
    out = []
    for r in rows:
        while out and out[-1][0] >= r[0]:
            out.pop()
        out.append(r)
    return np.array(out)


# ---------------------------------------------------------------------------------------
# Fourier helpers in the gw_diag layout f[z, y, x], direction a on axis -1 - a
# ---------------------------------------------------------------------------------------
class Modes:
    def __init__(self, grid):
        self.grid = grid
        k = grid.kvec(real=True)
        self.k = k
        self.k2 = (k**2).sum(0)
        self.kk = np.sqrt(self.k2)
        k2s = self.k2.copy()
        k2s[0, 0, 0] = 1.0
        self.k2s = k2s
        self.w = np.asarray(grid.rfft_weights())
        self.ok = (~grid.nyquist_mask(real=True)) & (self.k2 > 0)
        self.kf = 2*np.pi/grid.L[0]
        self.nk = np.rint(self.kk/self.kf).astype(int)
        self.N = int(np.prod(grid.n))

    def measures(self, T, a):
        """rms and Omega_qs of a TT field given by its rfftn coefficients T (3, 3, ...)."""
        p = (np.abs(T)**2).sum((0, 1))*self.w*self.ok/self.N**2
        rms = float(np.sqrt(p.sum()))
        om = float(a/(32*np.pi*RHO_C)*(p*self.k2).sum())
        spec = np.bincount(self.nk[self.ok], weights=(p*self.k2)[self.ok]*a/(32*np.pi*RHO_C),
                           minlength=self.grid.n[0]//2 + 2)[:self.grid.n[0]//2 + 1]
        return rms, om, spec

    def compare(self, A, B):
        """Correlation coefficient and rms ratio |A|/|B| per band |k| <= n k_f."""
        out = {}
        cross = np.real((A*np.conj(B)).sum((0, 1)))*self.w
        pa = (np.abs(A)**2).sum((0, 1))*self.w
        pb = (np.abs(B)**2).sum((0, 1))*self.w
        for n in BANDS:
            m = self.ok & (self.nk <= n)
            sa, sb = pa[m].sum(), pb[m].sum()
            out[str(n)] = {"corr": float(cross[m].sum()/np.sqrt(sa*sb)) if sa*sb > 0 else None,
                           "rms_ratio": float(np.sqrt(sa/sb)) if sb > 0 else None}
        return out


def tt_fourier_of_real(Treal, grid):
    """rfftn coefficients of a real symmetric tensor field that is already TT."""
    return tt.tensor_rfft(Treal)


def hqs_particles(fn, grid, md):
    """Weak-field quasi-static TT strain S^TT/k^2 of a GR particle snapshot (rfftn)."""
    t, cyc, x, u, m, tag = read_snapshot(fn)
    a = float(scale(t))
    n = grid.n[0]
    W = np.sqrt(1.0 + (u*u).sum(1)/a**2)
    v = u/(a*W[:, None])                                       # dx/dt (weak field)
    comp = [(0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)]
    w = np.stack([m] + [m*v[:, i]*v[:, j] for (i, j) in comp], axis=1)
    dep = an.cic(np.mod(x, L), w, n, L).transpose(0, 3, 2, 1)   # [ix,iy,iz] -> [iz,iy,ix]
    rho = dep[0]
    rk = np.fft.rfftn(rho - rho.mean())
    phik = -4*np.pi*rk/md.k2s
    phik[0, 0, 0] = 0.0
    g = [np.fft.irfftn(1j*md.k[c]*phik, s=rho.shape) for c in range(3)]   # d_c Phi_c
    S = np.empty((3, 3) + rho.shape)
    for c, (i, j) in enumerate(comp):
        S[i, j] = S[j, i] = 16*np.pi*dep[c + 1]/a + 4.0*g[i]*g[j]/a**2
    T = tt.tt_project_fourier(S, grid)
    T = T/md.k2s
    T[:, :, 0, 0, 0] = 0.0
    del dep, S, g
    return t, a, T


def dump_job(args):
    try:
        return _dump_job(args)
    except Exception as e:                 # a broken dump (the state written at a guard stop)
        return {"file": os.path.basename(args[0]), "t": -1.0, "a": 0.0, "error": repr(e)}


def _dump_job(args):
    path, snap, do_gauge = args
    d = binio.read_bin(path, strip_prefix=True)
    grid = d["grid"]
    md = Modes(grid)
    t = float(d["time"])
    a = float(scale(t))
    chi, gt, At, trK, alpha, beta = readers.z4c_tensors(d)
    row = {"file": os.path.basename(path), "t": t, "a": a, "cycle": int(d["cycle"]),
           "alpha_mean": float(alpha.mean()), "chi_mean": float(chi.mean()),
           "K_max": float(trK.max()), "K_min": float(trK.min()),
           "K_max_at": [float(v) for v in np.array(np.unravel_index(np.argmax(trK), trK.shape))[::-1]]}
    h = gt - np.eye(3)[:, :, None, None, None]
    Traw = tt.tt_project_fourier(h, grid)
    row["rms_raw"], row["Omega_raw"], spec_raw = md.measures(Traw, a)
    row["spec_raw"] = spec_raw.tolist()
    if do_gauge:
        s = gauge.tt_strain_from_conformal(gt, grid)
        Tcor = tt_fourier_of_real(s["corrected"], grid)
        TG = tt_fourier_of_real(s["G"], grid)
        row["rms_cor"], row["Omega_cor"], spec_cor = md.measures(Tcor, a)
        row["rms_G"], row["Omega_G"], _ = md.measures(TG, a)
        row["spec_cor"] = spec_cor.tolist()
        del s
        if snap:
            tp, ap, Tq = hqs_particles(snap, grid, md)
            row["snap"] = os.path.basename(snap)
            row["t_snap"] = tp
            row["rms_qs"], row["Omega_qs_part"], spec_qs = md.measures(Tq, a)
            row["spec_qs"] = spec_qs.tolist()
            row["cmp_cor_qs"] = md.compare(Tcor, Tq)
            row["cmp_raw_qs"] = md.compare(Traw, Tq)
    return row


# ---------------------------------------------------------------------------------------
def halo_job(args):
    fn, = args
    t, cyc, x, u, m, tag = read_snapshot(fn)
    a = float(scale(t))
    n = round(len(x)**(1/3))
    W = np.sqrt(1.0 + (u*u).sum(1)/a**2)
    p = u/W[:, None]                                            # a dx/dt (weak field)
    hal, n32 = an.halo_catalog(x, p, m, tag, a, L, L/n)
    mN = RHO_C*L**3/N_NEWTON**3
    big = [h for h in hal if h["M"] >= 100*mN]
    return {"file": os.path.basename(fn), "t": float(t), "a": a, "n_halos_100": len(hal),
            "n_halos_common": len(big), "masses": [h["M"] for h in hal],
            "x": [h["x"] for h in hal], "N": [h["N"] for h in hal],
            "r_half": [h["r_half"] for h in hal], "sigma_v": [h["sigma_v"] for h in hal],
            "GM_over_r": [h["GM_over_r_phys"] for h in hal], "m_particle": float(m.mean())}


def periodic_dist(x, y):
    d = np.mod(np.asarray(x) - np.asarray(y) + 0.5*L, L) - 0.5*L
    return float(np.sqrt((d*d).sum()))


# ---------------------------------------------------------------------------------------
def analyse_run(name, d, sigma1, newton, workers, gauge_every):
    res = {"name": name, "dir": d, "sigma1": sigma1, "stage_factor": sigma1/SIG_FID}
    c = read_hst(os.path.join(d, "pop.cstat.hst"))
    h = read_hst(os.path.join(d, "pop.nrpic.hst"))
    res["cstat"] = {"t": c[:, 0].tolist(), "chi_min": c[:, 1].tolist(), "chi_max": c[:, 2].tolist(),
                    "K_min": c[:, 3].tolist(), "K_max": c[:, 4].tolist(),
                    "E_max": c[:, 6].tolist(), "H_mean": c[:, 9].tolist(),
                    "Hr_max": c[:, 10].tolist(), "Hr_mean": c[:, 11].tolist(),
                    "Mr_mean": c[:, 15].tolist()}
    res["nrpic"] = {"t": h[:, 0].tolist(), "alpha_min": h[:, 15].tolist(),
                    "alpha_max": h[:, 29].tolist(), "n_excised": h[:, 16].tolist(),
                    "push_maxit": h[:, 20].tolist(), "mean_K": h[:, 28].tolist()}
    guard = os.path.join(d, "pop.guard.txt")
    res["guard"] = open(guard).read() if os.path.exists(guard) else None
    snaps = sorted(glob.glob(os.path.join(d, "pop.part.*.bin")))
    dumps = sorted(glob.glob(os.path.join(d, "bin", "pop.z4cd.*.bin")))
    snap_t = []
    for fn in snaps:
        with open(fn, "rb") as f:
            f.read(8)
            snap_t.append(float(np.frombuffer(f.read(8), "<f8")[0]))
    snap_t = np.array(snap_t)
    # halos
    with Pool(workers) as pool:
        cats = pool.map(halo_job, [(fn,) for fn in snaps], chunksize=1)
    res["halos"] = cats
    # dumps: raw everywhere; gauge-corrected and particle comparison at snapshot times
    tasks = []
    for i, p in enumerate(dumps):
        ti = 0.25*int(os.path.basename(p).split(".")[-2])
        j = int(np.argmin(np.abs(snap_t - ti))) if len(snap_t) else -1
        at_snap = j >= 0 and abs(snap_t[j] - ti) < 0.05
        do_g = at_snap and (int(round(ti)) % gauge_every == 0) and ti > 0
        tasks.append((p, snaps[j] if (at_snap and do_g) else None, do_g))
    order = sorted(range(len(tasks)), key=lambda k: not tasks[k][2])   # heavy jobs first
    with Pool(workers) as pool:
        rows = pool.map(dump_job, [tasks[k] for k in order], chunksize=1)
    res["dump_errors"] = [r for r in rows if "error" in r]
    rows = [r for r in rows if "error" not in r]
    rows.sort(key=lambda r: r["t"])
    res["dumps"] = rows
    # comparison with fidL8 at the same stage
    if newton:
        ncat = newton["catalogs"]
        aN = np.array([cc["a"] for cc in ncat])
        mN = RHO_C*L**3/N_NEWTON**3
        cmp = []
        for cat in cats:
            stage = cat["a"]*sigma1/SIG_FID
            if stage < 4.5:
                continue
            k = int(np.argmin(np.abs(np.log(aN/stage))))
            if abs(np.log(aN[k]/stage)) > 0.08:
                continue
            nc = ncat[k]
            nm = [M for M in nc["masses"] if M >= 100*mN]
            gm = [M for M in cat["masses"] if M >= 100*mN]
            row = {"a": cat["a"], "stage": stage, "a_N": nc["a"], "n_GR": len(gm), "n_N": len(nm),
                   "M1_GR": max(gm) if gm else None, "M1_N": max(nm) if nm else None,
                   "fmass_GR": float(sum(gm)/(RHO_C*L**3)), "fmass_N": float(sum(nm)/(RHO_C*L**3))}
            # match the five largest Newtonian halos
            mt = []
            gx = [cat["x"][i] for i, M in enumerate(cat["masses"]) if M >= 100*mN]
            for i in range(min(5, len(nm))):
                xn = nc["x"][i]
                if not gx:
                    break
                dd = [periodic_dist(xn, y) for y in gx]
                jj = int(np.argmin(dd))
                mt.append({"M_N": nc["masses"][i], "M_GR": gm[jj], "dist": dd[jj]})
            row["match5"] = mt
            cmp.append(row)
        res["newton_compare"] = cmp
    return res


def stop_diagnosis(res, d):
    """Fields at the cell the guard names, over the last dumps of the stopped run."""
    g = res["guard"]
    if not g:
        return None
    import re
    pos = [float(v) for v in re.search(r"position \(([^)]*)\)", g).group(1).split(",")]
    dumps = sorted(glob.glob(os.path.join(d, "bin", "pop.z4cd.*.bin")))
    out = {"position": pos, "rows": []}
    good = []
    for p in dumps[-11:]:
        try:
            good.append((p, binio.read_bin(p, strip_prefix=True)))
        except Exception as e:
            out.setdefault("unreadable", []).append([os.path.basename(p), repr(e)])
    for p, dd in good:
        grid = dd["grid"]
        dx = grid.dx[0]
        i, j, k = (int(np.floor(pos[c]/dx)) for c in range(3))
        chi, gt, At, trK, alpha, beta = readers.z4c_tensors(dd)
        sl = (slice(max(k - 2, 0), k + 3), slice(max(j - 2, 0), j + 3), slice(max(i - 2, 0), i + 3))
        kmax_at = np.array(np.unravel_index(np.nanargmax(np.where(np.isfinite(trK), trK, -np.inf)),
                                            trK.shape))[::-1]
        out["rows"].append({"file": os.path.basename(p), "t": float(dd["time"]),
                            "alpha": float(alpha[k, j, i]), "chi": float(chi[k, j, i]),
                            "K": float(trK[k, j, i]), "Theta": float(dd["Theta"][k, j, i]),
                            "alpha_box_min": float(np.nanmin(alpha[sl])),
                            "K_box_max": float(np.nanmax(trK[sl])),
                            "K_max": float(np.nanmax(np.where(np.isfinite(trK), trK, -np.inf))),
                            "K_max_at": ((kmax_at + 0.5)*dx).tolist(),
                            "alpha_slice_z": alpha[k].tolist() if p == good[-1][0] else None,
                            "K_slice_z": trK[k].tolist() if p == good[-1][0] else None,
                            "n_nonfinite": int((~np.isfinite(trK)).sum())})
    snaps = sorted(glob.glob(os.path.join(d, "pop.part.*.bin")))
    t, cyc, x, u, m, tag = read_snapshot(snaps[-1])
    nmesh = 128
    rho = an.cic(np.mod(x, L), m, nmesh, L)                    # [ix, iy, iz]
    ijk = np.array(np.unravel_index(np.argmax(rho), rho.shape))
    xpk = (ijk + 0.5)*L/nmesh
    out["densest"] = {"t": float(t), "x": xpk.tolist(), "rho_over_mean": float(rho.max()/rho.mean()),
                      "dist_to_stop_cell": periodic_dist(xpk, pos)}
    # density around the stop cell (CIC, comoving, over the mean), 9^3 cells
    ip = np.floor(np.array(pos)/(L/nmesh)).astype(int)
    idx = [(np.arange(-4, 5) + ip[c]) % nmesh for c in range(3)]
    loc = rho[np.ix_(idx[0], idx[1], idx[2])]/rho.mean()
    out["rho_near_stop_max"] = float(loc.max())
    out["rho_slice_z"] = (rho[:, :, ip[2]]/rho.mean()).T.tolist()          # [iy, ix]
    # FoF halo nearest to the stop cell
    hal = res["halos"][-1]
    if hal["x"]:
        dd = [periodic_dist(x0, pos) for x0 in hal["x"]]
        jj = int(np.argmin(dd))
        out["nearest_halo"] = {"dist": dd[jj], "M": hal["masses"][jj], "N": hal["N"][jj],
                               "rank": jj, "x": hal["x"][jj]}
    return out


# ---------------------------------------------------------------------------------------
def figures(R, newton, od):
    fs.use_style()
    import matplotlib.pyplot as plt
    cols = fs.SERIES
    # 1. constraints and gauge
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.8))
    fig.subplots_adjust(left=0.07, right=0.99, bottom=0.17, top=0.93, wspace=0.38)
    for r, col in zip(R, cols):
        c = r["cstat"]
        t = np.array(c["t"])
        a = scale(t)
        st = a*r["stage_factor"]
        lab = r"$\sigma_1 = %g$" % r["sigma1"]
        axs[0].loglog(a, np.array(c["Hr_mean"]), color=col, lw=1.0, label=lab + r", $\langle|H|\rangle_r$")
        axs[0].loglog(a, np.array(c["Mr_mean"]), color=col, lw=1.0, ls="--", label=lab + r", $\langle|M|\rangle_r$")
        Kbg = -3*a**-1.5
        axs[1].semilogx(st, (np.array(c["K_max"]) - Kbg)/np.abs(Kbg), color=col, lw=1.0, label=lab)
        axs[1].semilogx(st, (np.array(c["K_min"]) - Kbg)/np.abs(Kbg), color=col, lw=0.8, ls=":")
        h = r["nrpic"]
        ah = scale(np.array(h["t"]))
        axs[2].semilogx(ah*r["stage_factor"], np.array(h["alpha_min"])/np.array(h["alpha_max"]),
                        color=col, lw=1.0, label=lab)
    axs[0].axhline(1e-2, **fs.GUIDE)
    axs[0].axhline(5e-2, **fs.GUIDE)
    axs[0].set_xlabel(r"$a$")
    axs[0].set_ylabel("relative constraint violation (mean)")
    axs[0].legend(fontsize=6, loc="lower right")
    axs[1].axhline(1.0, **fs.GUIDE)
    axs[1].set_xlabel(r"stage $a\,\sigma_1/0.0562$")
    axs[1].set_ylabel(r"$(K - \bar K)/|\bar K|$: max (solid), min (dotted)")
    axs[1].legend(fontsize=6.5, loc="upper left")
    axs[2].set_xlabel(r"stage $a\,\sigma_1/0.0562$")
    axs[2].set_ylabel(r"$\alpha_{\min}/\alpha_{\max}$")
    fs.save(fig, os.path.join(od, "pop_gr_constraints"))
    plt.close(fig)

    # 2. halos against the Newtonian population
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.8))
    fig.subplots_adjust(left=0.07, right=0.99, bottom=0.17, top=0.93, wspace=0.38)
    mN = RHO_C*L**3/N_NEWTON**3
    if newton:
        ncat = newton["catalogs"]
        aN = np.array([cc["a"] for cc in ncat])
        nN = np.array([sum(1 for M in cc["masses"] if M >= 100*mN) for cc in ncat])
        M1 = np.array([max(cc["masses"]) if cc["masses"] else np.nan for cc in ncat])
        axs[0].errorbar(aN, nN, yerr=2*np.sqrt(nN) + 2, color="k", marker="s", ms=3, lw=0.8,
                        capsize=1.5, label="Newtonian fidL8 (64$^3$)")
        axs[1].semilogy(aN, M1, color="k", marker="s", ms=3, lw=0.8, label="Newtonian fidL8")
    for r, col in zip(R, cols):
        a = np.array([c["a"] for c in r["halos"]])
        st = a*r["stage_factor"]
        n = np.array([c["n_halos_common"] for c in r["halos"]])
        n100 = np.array([c["n_halos_100"] for c in r["halos"]])
        M1 = np.array([max(c["masses"]) if c["masses"] else np.nan for c in r["halos"]])
        lab = r"GR $\sigma_1 = %g$ (128$^3$)" % r["sigma1"]
        axs[0].plot(st, n, color=col, marker="o", ms=3, lw=1.0, label=lab)
        axs[0].plot(st, n100, color=col, lw=0.7, ls=":")
        axs[1].semilogy(st, M1, color=col, marker="o", ms=3, lw=1.0, label=lab)
        for row in r.get("newton_compare", []):
            for mt in row["match5"]:
                axs[2].semilogx(row["stage"], mt["M_GR"]/mt["M_N"], color=col, marker="o", ms=2.5,
                                ls="none", alpha=0.8)
    axs[0].set_xlabel(r"stage $a\,\sigma_1/0.0562$")
    axs[0].set_ylabel(r"halos, $M \geq 100\,m_{\rm N}$")
    axs[0].legend(fontsize=6, loc="upper left")
    axs[0].text(0.97, 0.04, r"dotted: $\geq 100$ own particles", transform=axs[0].transAxes,
                ha="right", fontsize=6)
    axs[0].set_xlim(0, 40)
    axs[1].set_xlabel(r"stage $a\,\sigma_1/0.0562$")
    axs[1].set_ylabel("largest halo mass")
    axs[1].set_xlim(0, 40)
    axs[2].axhline(1.0, **fs.GUIDE)
    axs[2].set_xlabel(r"stage $a\,\sigma_1/0.0562$")
    axs[2].set_ylabel(r"$M_{\rm GR}/M_{\rm N}$ (5 largest)")
    fs.save(fig, os.path.join(od, "pop_gr_halos"))
    plt.close(fig)

    # 3. TT strain of the metric against the near field of the particles and the design
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.8))
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.17, top=0.93, wspace=0.40)
    for r, col in zip(R, cols):
        D = [x for x in r["dumps"] if x["t"] > 0]
        a = np.array([x["a"] for x in D])
        axs[0].loglog(a, [x["Omega_raw"] for x in D], color=col, lw=1.0,
                      label=r"metric, raw, $\sigma_1 = %g$" % r["sigma1"])
        G = [x for x in D if "Omega_cor" in x]
        ag = np.array([x["a"] for x in G])
        axs[0].loglog(ag, [x["Omega_cor"] for x in G], color=col, marker="o", ms=2.5, ls="none",
                      label="metric, gauge-corrected")
        Q = [x for x in G if "Omega_qs_part" in x]
        axs[0].loglog([x["a"] for x in Q], [x["Omega_qs_part"] for x in Q], color=col, marker="x",
                      ms=3.5, ls="none", label="particles, $S^{TT}/k^2$")
        aa = np.geomspace(1, 150, 50)
        axs[0].loglog(aa, DESIGN_QS*(r["sigma1"]/SIG_FID)**4*aa, **{**fs.GUIDE, "lw": 0.7, "color": col})
        axs[1].loglog(a, [x["rms_raw"] for x in D], color=col, lw=1.0)
        axs[1].loglog(ag, [x["rms_cor"] for x in G], color=col, marker="o", ms=2.5, ls="none")
        axs[1].loglog(ag, [x["rms_G"] for x in G], color=col, marker="^", ms=2.5, ls="none")
        for n, ls in zip((8, 64), ("-", "--")):
            axs[2].semilogx([x["a"] for x in Q], [x["cmp_cor_qs"][str(n)]["corr"] for x in Q],
                            color=col, ls=ls, marker="o", ms=2.5, lw=0.9,
                            label=(r"corr., $|k| \leq %d k_f$" % n) if col == cols[0] else None)
            axs[2].semilogx([x["a"] for x in Q], [x["cmp_cor_qs"][str(n)]["rms_ratio"] for x in Q],
                            color=col, ls=ls, marker="^", ms=2.5, lw=0.6, alpha=0.7,
                            label=("rms ratio, %d" % n) if col == cols[0] else None)
    if newton and newton.get("gw"):
        rows = np.array(newton["gw"]["rows"])
        for r, col in zip(R, cols):
            f = r["stage_factor"]
            # equal stage: a = a_N/f; Omega_qs ~ sigma^3 at equal stage (P9)
            axs[0].loglog(rows[:, 1]/f, rows[:, 9]*f**3, color=col, lw=0.6, ls="-.", alpha=0.8,
                          label=r"Newtonian fidL8 near field at equal stage" if col == cols[0] else None)
    axs[0].set_xlabel(r"$a$")
    axs[0].set_ylabel(r"$\Omega_{\rm qs}$ of the TT strain")
    axs[0].legend(fontsize=5.5, loc="upper left")
    axs[0].text(0.97, 0.04, r"dashed: design $2.9\times10^{-9}a\,(\sigma_1/0.014)^4$",
                transform=axs[0].transAxes, ha="right", fontsize=6)
    axs[1].set_xlabel(r"$a$")
    axs[1].set_ylabel(r"rms of $\Lambda h$: raw (line), corrected (o), $G_{\rm tot}$ ($\triangle$)")
    axs[2].axhline(1.0, **fs.GUIDE)
    axs[2].axhline(0.9, **{**fs.GUIDE, "lw": 0.5})
    axs[2].set_xlabel(r"$a$")
    axs[2].set_ylabel("metric against particles")
    axs[2].legend(fontsize=5.5, loc="lower left")
    fs.save(fig, os.path.join(od, "pop_gr_gw"))
    plt.close(fig)


def figure_stop(Z, od):
    if not Z:
        return
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.9))
    fig.subplots_adjust(left=0.07, right=0.97, bottom=0.16, top=0.90, wspace=0.62)
    rows = [r for r in Z["rows"]]
    t = [r["t"] for r in rows]
    axs[0].plot(t, [r["alpha"] for r in rows], "o-", ms=2.5, lw=1.0, label=r"$\alpha$")
    axs[0].plot(t, [r["alpha_box_min"] for r in rows], "s--", ms=2.5, lw=0.8, label=r"min $\alpha$, 5$^3$ cells")
    axs[0].set_xlabel(r"$t$")
    axs[0].set_ylabel("lapse at the stop cell")
    axs[0].legend(fontsize=6.5)
    ax2 = axs[0].twinx()
    ax2.plot(t, [r["K"] for r in rows], "^:", ms=2.5, lw=0.8, color=fs.SERIES[2])
    ax2.set_ylabel(r"$K$ at the stop cell", color=fs.SERIES[2], labelpad=1)
    last = [r for r in rows if r["alpha_slice_z"] is not None][0]
    al = np.array(last["alpha_slice_z"])
    im = axs[1].imshow(al, origin="lower", extent=(0, L, 0, L), cmap="viridis")
    fig.colorbar(im, ax=axs[1], fraction=0.046)
    axs[1].plot(Z["position"][0], Z["position"][1], "r+", ms=8)
    axs[1].set_title(r"$\alpha$ at $t = %.2f$, plane of the stop cell" % last["t"], fontsize=7)
    axs[1].set_xlabel(r"$x$")
    axs[1].set_ylabel(r"$y$", labelpad=1)
    rho = np.array(Z["rho_slice_z"])
    im = axs[2].imshow(np.log10(np.maximum(rho, 1e-2)), origin="lower", extent=(0, L, 0, L), cmap="magma")
    fig.colorbar(im, ax=axs[2], fraction=0.046, label=r"$\log_{10}\rho/\bar\rho$")
    axs[2].plot(Z["position"][0], Z["position"][1], "c+", ms=8)
    axs[2].set_title(r"particle density at $t = %.1f$" % Z["densest"]["t"], fontsize=7)
    axs[2].set_xlabel(r"$x$")
    fs.save(fig, os.path.join(od, "pop_gr_stop"))
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="append", required=True, help="NAME:DIR:SIGMA1")
    ap.add_argument("--newton", default=None, help="analysis_fidL8.json")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--gauge-every", type=int, default=1,
                    help="gauge-corrected strain every n snapshot times")
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    ap.add_argument("--from-json", default=None,
                    help="analysis_gr.json of an earlier run: figures and summary only")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    newton = json.load(open(args.newton))[0] if args.newton else None
    R, Z = [], None
    if args.from_json:
        R = json.load(open(args.from_json))
        Z = next((r["stop"] for r in R if r.get("stop")), None)
        args.run = []
    for spec in args.run:
        name, d, s = spec.split(":")
        r = analyse_run(name, d, float(s), newton, args.workers, args.gauge_every)
        if r["guard"]:
            Z = stop_diagnosis(r, d)
            r["stop"] = Z
        R.append(r)
        with open(os.path.join(args.out, f"analysis_gr_{name}.json"), "w") as f:
            json.dump(r, f)                    # each run as soon as it is done
        print(name, "done", flush=True)
    if not args.from_json:
        with open(os.path.join(args.out, "analysis_gr.json"), "w") as f:
            json.dump(R, f)
    figures(R, newton, args.out)
    figure_stop(Z, args.out)
    # summary lines
    for r in R:
        D = [x for x in r["dumps"] if "Omega_cor" in x]
        print(f"== {r['name']} sigma1 {r['sigma1']}")
        for x in D:
            s = (f"a {x['a']:7.2f}  rms raw {x['rms_raw']:.3e} cor {x['rms_cor']:.3e} G {x['rms_G']:.2e}"
                 f"  Om raw {x['Omega_raw']:.3e} cor {x['Omega_cor']:.3e}")
            if "Omega_qs_part" in x:
                c8 = x["cmp_cor_qs"]["8"]
                ca = x["cmp_cor_qs"]["64"]
                s += (f"  Om_qs(part) {x['Omega_qs_part']:.3e}  design {DESIGN_QS*(r['sigma1']/SIG_FID)**4*x['a']:.3e}"
                      f"  corr8 {c8['corr']:.3f} ratio8 {c8['rms_ratio']:.3f} corrAll {ca['corr']:.3f} ratioAll {ca['rms_ratio']:.3f}")
            print(s)
        for c in r["halos"]:
            print(f"halos a {c['a']:7.2f}: {c['n_halos_100']} (>=100 own), {c['n_halos_common']} (>= 800), "
                  f"largest {max(c['masses']) if c['masses'] else 0:.4f}")
        for row in r.get("newton_compare", []):
            print(f"cmp a {row['a']:.1f} stage {row['stage']:.2f} a_N {row['a_N']:.2f}: n GR {row['n_GR']} N {row['n_N']}; "
                  f"M1 {row['M1_GR']} {row['M1_N']}; match {[(round(m['M_GR']/m['M_N'],3), round(m['dist'],3)) for m in row['match5']]}")
    if Z:
        print("stop:", json.dumps({k: v for k, v in Z.items() if k not in ("rows", "rho_slice_z")}))
        for rr in Z["rows"]:
            print({k: v for k, v in rr.items() if not k.endswith("_slice_z")})


if __name__ == "__main__":
    main()
