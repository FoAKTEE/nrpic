"""K2 initial data: test particles drawn from the adiabatically grown Kerr spike
(FdRW method, kerr_lib.py) for the AthenaK problem generator nrpic_geodesic with the
analytic Cartesian Kerr-Schild metric of spin a (along +z).

Exactness. The phase-space density on a slice t_KS = const is f(E, C, Lz) per
d^3x d^3p_i(KS) (canonical variables of the t_KS Hamiltonian). We draw (r, theta, E, l, phi_C,
sign u_r, sign u_theta, phi) by rejection from the BL-slice measure of kerr_lib (Lz = l sin,
C = C_U + (C_V - C_U)(1 - cos phi_C)/2) times the Jacobian of p(BL) -> p(KS) at fixed x,
    d^3p(KS) = (1 + delta_t' v^r_BL) d^3p(BL),  delta_t' = 2 r/Delta,
    v^r_BL = Delta^2 u_r(BL)/(A E - 2 a r Lz),
so the weight per (d ln r, d cos theta, dE, dl, dphi_C, dphi) is
    w = r (2/Delta^{3/2}) f [A E - 2 a r Lz + 2 r Delta u_r(BL)],
u_r(BL) = s_r sqrt(C_V - C)/sqrt(Delta), u_theta = s_th sqrt(C - C_U). The particle is then
placed at t_KS = 0 with u_i(KS) = u_i(BL) + (2 r E - a Lz)/Delta delta_i^r (CKS components
by nrpic.kerr.convert_state). With --slice bl the Jacobian factor is left out (the
uncorrected sampling of wave 1, for a control run).

f is the Hernquist DF (M = 1e12 Msun, r_s = 20 kpc, m = 4e6 Msun) restricted to E <= E_cut,
a function of the invariants only, hence stationary (Jeans).

Proposal: cells in (ln r, |cos theta|), uniform inside a cell, E = E_lb + (E_cut - E_lb) u^2,
l uniform in the cell's l box, phi_C uniform in [0, pi]; envelope per cell = 2 x the
largest weight/proposal of a pilot sample; violations are counted.

usage: python3 sample_kerr.py --out DIR --n N --nfiles K [--a 0.8] [--ecut 0.99] [--seed S]
Writes kerr_<k>.nrp, ic_meta.npz, ic_summary.json.
"""
import argparse
import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "python"))
from kerr_lib import Kerr, KerrHernquist  # noqa: E402
from nrpic import io as nio, kerr as nk  # noqa: E402

warnings.simplefilter("ignore", RuntimeWarning)


class Target:
    def __init__(self, K, H, ecut, slice_):
        self.K, self.H, self.ecut, self.slice = K, H, ecut, slice_

    def __call__(self, lr, mu, E, l, phic, sr):
        """Weight w per (d ln r, d mu, dE, dl, dphi_C, dphi); also returns the state."""
        K, a = self.K, self.K.a
        r = np.exp(lr)
        th = np.arccos(mu)
        s = np.sin(th)
        D = K.Delta(r)
        A = (r * r + a * a) ** 2 - a * a * D * s * s
        Lz = l * s
        cu = l * l + a * a * (1 - E * E) * mu * mu
        cv = K.CV(E, Lz, r)
        w = np.zeros_like(E)
        ok = (E < self.ecut) & (cv > cu) & (D > a * a * s * s)
        st = {}
        if ok.any():
            i = np.nonzero(ok)[0]
            Cc, ru, end = K.ccrit(E[i], Lz[i], r[i])
            C = cu[i] + (cv[i] - cu[i]) * 0.5 * (1 - np.cos(phic[i]))
            good = (~end) & (C > Cc)
            j = i[good]
            if j.size:
                f = self.H(K, E[j], C[good], Lz[j], r[j], ru[good])
                f = np.where(np.isfinite(f), f, 0.0)
                urbl = sr[j] * np.sqrt(np.clip(cv[j] - C[good], 0, None)) / np.sqrt(D[j])
                base = A[j] * E[j] - 2 * a * r[j] * Lz[j]
                jac = base + (2 * r[j] * D[j] * urbl if self.slice == "ks" else 0.0)
                w[j] = r[j] * 2.0 / D[j] ** 1.5 * f * jac
                st = {"idx": j, "C": C[good], "urbl": urbl, "uth_abs": np.sqrt(C[good] - cu[j])}
        return w, st


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=48000)
    ap.add_argument("--nfiles", type=int, default=12)
    ap.add_argument("--a", type=float, default=0.8)
    ap.add_argument("--ecut", type=float, default=0.99)
    ap.add_argument("--rmax", type=float, default=110.0)
    ap.add_argument("--nx", type=int, default=36)
    ap.add_argument("--nmu", type=int, default=6)
    ap.add_argument("--npilot", type=int, default=3000)
    ap.add_argument("--slice", choices=["ks", "bl"], default="ks")
    ap.add_argument("--seed", type=int, default=20261116)
    args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    rng = np.random.default_rng(args.seed)
    K = Kerr(args.a)
    H = KerrHernquist(m_sun=4e6)
    T = Target(K, H, args.ecut, args.slice)
    summ = {"args": vars(args)}

    # ---- cells and their boxes ---------------------------------------------------------
    rin = K.rp + 0.3
    xe = np.linspace(np.log(rin), np.log(args.rmax), args.nx + 1)
    me = np.linspace(0.0, 1.0, args.nmu + 1)
    # E_min and l bounds on a grid refined 2x (cell corners, edge midpoints, centres)
    xr = np.linspace(xe[0], xe[-1], 2 * args.nx + 1)
    mr = np.linspace(0.0, 1.0, 2 * args.nmu + 1)
    Emn = np.ones((xr.size, mr.size))
    Llo = np.full_like(Emn, np.inf); Lhi = np.full_like(Emn, -np.inf)
    for i, x in enumerate(xr):
        for j, m in enumerate(mr):
            th = np.arccos(min(m, 1.0))
            r = np.exp(x)
            if K.Delta(r) <= args.a ** 2 * np.sin(th) ** 2:
                continue
            Emn[i, j] = K.Emin(r, th)
            lo, hi, ok = K.l_bounds(np.array([args.ecut]), r, th)
            if ok[0]:
                Llo[i, j], Lhi[i, j] = lo[0], hi[0]
    cells = []
    for i in range(args.nx):
        for j in range(args.nmu):
            sub = (slice(2 * i, 2 * i + 3), slice(2 * j, 2 * j + 3))
            elb = Emn[sub].min() - 0.002
            if elb >= args.ecut:
                continue
            lo, hi = Llo[sub].min(), Lhi[sub].max()
            if not np.isfinite(lo):
                continue
            pad = 0.02 * (hi - lo)
            cells.append([xe[i], xe[i + 1], me[j], me[j + 1], max(elb, 0.5), lo - pad, hi + pad])
    cells = np.array(cells)
    nc = len(cells)
    summ["n_cells"] = nc
    print("cells", nc, f"{time.time() - t0:.0f} s", flush=True)

    def propose(ci, m):
        c = cells[ci]
        u = rng.random((6, m))
        lr = c[:, 0] + (c[:, 1] - c[:, 0]) * u[0]
        mu = c[:, 2] + (c[:, 3] - c[:, 2]) * u[1]
        uu = u[2]
        E = c[:, 4] + (args.ecut - c[:, 4]) * uu * uu
        l = c[:, 5] + (c[:, 6] - c[:, 5]) * u[3]
        phic = np.pi * u[4]
        sr = np.where(u[5] < 0.5, 1.0, -1.0)
        jac = 2 * uu * (args.ecut - c[:, 4])          # dE/du
        return lr, mu, E, l, phic, sr, jac

    # ---- pilot: envelope per cell -------------------------------------------------------
    M = np.zeros(nc)
    ci = np.repeat(np.arange(nc), args.npilot)
    for k0 in range(0, ci.size, 200000):
        cc = ci[k0:k0 + 200000]
        lr, mu, E, l, phic, sr, jac = propose(cc, cc.size)
        w, _ = T(lr, mu, E, l, phic, sr)
        np.maximum.at(M, cc, w * jac)
    nzero = int(np.sum(M == 0))
    M *= 2.0
    vol = (cells[:, 1] - cells[:, 0]) * (cells[:, 3] - cells[:, 2]) * (cells[:, 6] - cells[:, 5])
    P = M * vol
    summ["pilot"] = {"cells_without_hit": nzero, "envelope_factor": 2.0,
                     "proposals": int(ci.size)}
    print("pilot done", f"{time.time() - t0:.0f} s", "cells without hit", nzero, flush=True)

    # ---- rejection sampling -------------------------------------------------------------
    acc = {k: [] for k in ("lr", "mu", "E", "l", "phic", "sr", "C", "urbl", "uth")}
    nacc, ntry, nviol, maxratio = 0, 0, 0, 0.0
    Pn = P / P.sum()
    while nacc < args.n:
        m = 400000
        cc = rng.choice(nc, size=m, p=Pn)
        lr, mu, E, l, phic, sr, jac = propose(cc, m)
        w, st = T(lr, mu, E, l, phic, sr)
        ratio = w * jac / M[cc]
        nviol += int(np.sum(ratio > 1)); maxratio = max(maxratio, float(ratio.max()))
        a_ = rng.random(m) < ratio
        ntry += m
        if not st:
            continue
        sel = a_[st["idx"]]
        j = st["idx"][sel]
        for k, v in (("lr", lr[j]), ("mu", mu[j]), ("E", E[j]), ("l", l[j]), ("phic", phic[j]),
                     ("sr", sr[j]), ("C", st["C"][sel]), ("urbl", st["urbl"][sel]),
                     ("uth", st["uth_abs"][sel])):
            acc[k].append(v)
        nacc += int(sel.sum())
        print(f"accepted {nacc} of {ntry} proposals, {time.time() - t0:.0f} s", flush=True)
    A_ = {k: np.concatenate(v)[:args.n] for k, v in acc.items()}
    n = args.n
    summ["rejection"] = {"proposals": ntry, "accepted": nacc, "acceptance": nacc / ntry,
                         "envelope_violations": nviol, "max_ratio": maxratio}

    # ---- states -------------------------------------------------------------------------
    r = np.exp(A_["lr"])
    hemi = np.where(rng.random(n) < 0.5, 1.0, -1.0)
    th = np.arccos(A_["mu"] * hemi)
    s = np.sin(th)
    Lz = A_["l"] * s
    E = A_["E"]; C = A_["C"]
    uth = np.where(rng.random(n) < 0.5, 1.0, -1.0) * A_["uth"]
    ph = 2 * np.pi * rng.random(n)
    x_bl = np.stack([r, th, ph], axis=1)
    u_bl = np.stack([A_["urbl"], uth, Lz], axis=1)
    _, x_cks, u_cks = nk.convert_state(0.0, x_bl, u_bl, "bl", "cks", a=args.a, M=1.0, u_t=-E)
    Ec, Lzc, Qc = nk.invariants("cks", x_cks, u_cks, a=args.a, M=1.0)
    summ["conversion_check"] = {"max_rel_dE": float(np.max(np.abs(Ec / E - 1))),
                                "max_abs_dLz": float(np.max(np.abs(Lzc - Lz))),
                                "max_abs_dQ": float(np.max(np.abs(Qc - (C - Lz * Lz))))}
    # radial turning points (for the analysis: pericentres)
    Cc, ru, end = K.ccrit(E, Lz, r)
    r1, r2, r3, r4 = K.radial_roots(E, C, Lz, r, ru)
    mass = np.full(n, 1e-6 / n)
    files = []
    perm = rng.permutation(n)
    for k, idx in enumerate(np.array_split(perm, args.nfiles)):
        idx = np.sort(idx)
        fn = out / f"kerr_{k}.nrp"
        nio.write_nrp(fn, x_cks[idx], u_cks[idx], mass[idx], np.zeros(idx.size, int))
        files.append({"file": fn.name, "n": int(idx.size), "index": idx.tolist()})
    np.savez(out / "ic_meta.npz", E=E, Lz=Lz, C=C, Q=C - Lz * Lz, r=r, th=th, x=x_cks, u=u_cks,
             ra=r1, rp=r2, r3=r3, urbl=A_["urbl"])
    summ["files"] = [{"file": f["file"], "n": f["n"]} for f in files]
    summ["file_index"] = {f["file"]: f["index"] for f in files}
    summ["r_quantiles"] = np.quantile(r, [0, 0.01, 0.1, 0.5, 0.9, 0.99, 1]).tolist()
    summ["rp_min"] = float(r2.min()); summ["ra_max"] = float(r1.max())
    summ["frac_r_lt_16"] = float(np.mean(r < 16.0))
    summ["Lz_mean"] = float(Lz.mean())
    summ["wall_s"] = time.time() - t0
    (out / "ic_summary.json").write_text(json.dumps(summ))
    print(json.dumps({k: v for k, v in summ.items() if k != "file_index"}, indent=1))


if __name__ == "__main__":
    main()
