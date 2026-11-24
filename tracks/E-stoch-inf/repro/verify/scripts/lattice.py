#!/usr/bin/env python3
"""Fresh verifier, part 2a: my own reader of the NRSFDMP2 dumps (layout of
coord/INTERFACES/scalar_field_2.md section 4) and my own extraction of R^NR (P1:522-526).

Per dump: box means; Fourier coefficients (cell-centre convention, x1min = 0) of
  Phi_chi = +(1/2) delta ln chi             (from the determinant, exact)
  Phi_E   = +(1/4) khat_i khat_j delta gt_ij (removes the -(1/3) Laplacian of E that the
                                              determinant carries; SVT metric of P0:178-181,
                                              gamma_ij = a^2[(1 - 2 Phi) delta_ij + 2 E_,ij],
                                              so chi = a^-2 (1 + 2 Phi - (2/3) Lap E) and
                                              khat khat : delta gt = -(4/3) k^2 E)
  dphi    = phi - <phi>
for the hemisphere modes with |n|^2 <= nmax2, and the shell power of
  R = Phi_chi + Phi_E + (H/Pi_b) dphi,  H = -<K>/3, Pi_b = <Pi>   (P0:273, P1:524)
(gauge invariant: under t -> t + xi, Phi -> Phi + H xi and dphi -> dphi - Pi xi)
for every |n|^2 up to the Nyquist corner. Constraint statistics from the dumped H, M_i and,
where present, the dumped magnitudes; my own [H] = |R3| + (2/3)K^2 + |At_ij At_ij| + |16 pi E|
with R3 recovered from the dumped H (definition of [H] at P1:740).

Usage:
  python lattice.py selftest --out DIR
  python lattice.py run --dumps D1 D2 ... --nmax2 4096 --out DIR [--tag sr]
"""
import argparse
import json
import os
import struct
import sys
import time

import numpy as np
import scipy.fft as sfft

MAGIC = b"NRSFDMP2"


# ---------------------------------------------------------------- reader
def read_header(path):
    with open(path, "rb") as f:
        magic = f.read(8)
        if magic != MAGIC:
            raise ValueError(f"{path}: magic {magic!r}")
        nmb, nx1, nx2, nx3, nvar, cycle, nnoise = struct.unpack("<7q", f.read(56))
        t = struct.unpack("<d", f.read(8))[0]
        names = [f.read(16).rstrip(b"\0").decode() for _ in range(nvar)]
        off = f.tell()
    return dict(nmb=nmb, nx=(nx1, nx2, nx3), nvar=nvar, cycle=cycle, nnoise=nnoise, time=t,
                names=names, data_offset=off)


def read_fields(path, want):
    """Full-mesh arrays [k3, k2, k1] (x1 fastest) of the named variables (uniform mesh)."""
    h = read_header(path)
    nx1, nx2, nx3 = h["nx"]
    ncell = nx1*nx2*nx3
    idx = {n: h["names"].index(n) for n in want}
    blocks = []
    with open(path, "rb") as f:
        f.seek(h["data_offset"])
        for _ in range(h["nmb"]):
            lev, l1, l2, l3 = struct.unpack("<4q", f.read(32))
            struct.unpack("<6d", f.read(48))
            start = f.tell()
            arrs = {}
            for n in sorted(want, key=lambda q: idx[q]):
                f.seek(start + idx[n]*ncell*8)
                arrs[n] = np.fromfile(f, dtype="<f8", count=ncell).reshape(nx3, nx2, nx1)
            f.seek(start + h["nvar"]*ncell*8)
            blocks.append(((lev, l1, l2, l3), arrs))
    m1 = max(b[0][1] for b in blocks) + 1
    m2 = max(b[0][2] for b in blocks) + 1
    m3 = max(b[0][3] for b in blocks) + 1
    out = {n: np.empty((m3*nx3, m2*nx2, m1*nx1)) for n in want}
    for (lev, l1, l2, l3), arrs in blocks:
        if lev != 0:
            raise ValueError("refined mesh not supported")
        for n in want:
            out[n][l3*nx3:(l3+1)*nx3, l2*nx2:(l2+1)*nx2, l1*nx1:(l1+1)*nx1] = arrs[n]
    return h, out


def write_fake(path, fields, nb, time_=0.5, cycle=7):
    """Writer used only by the self-test: fields [k3,k2,k1] split into nb^3 MeshBlocks."""
    names = list(fields)
    N = fields[names[0]].shape[0]
    m = N//nb
    with open(path, "wb") as f:
        f.write(MAGIC)
        f.write(struct.pack("<7q", nb**3, m, m, m, len(names), cycle, 0))
        f.write(struct.pack("<d", time_))
        for n in names:
            f.write(n.encode().ljust(16, b"\0"))
        L = 2*np.pi
        for l3 in range(nb):
            for l2 in range(nb):
                for l1 in range(nb):
                    f.write(struct.pack("<4q", 0, l1, l2, l3))
                    f.write(struct.pack("<6d", l1*L/nb, (l1+1)*L/nb, l2*L/nb, (l2+1)*L/nb,
                                        l3*L/nb, (l3+1)*L/nb))
                    for n in names:
                        blk = fields[n][l3*m:(l3+1)*m, l2*m:(l2+1)*m, l1*m:(l1+1)*m]
                        f.write(np.ascontiguousarray(blk, dtype="<f8").tobytes())


# ---------------------------------------------------------------- Fourier tools
def hemisphere(nmax2):
    nmax = int(np.floor(np.sqrt(nmax2) + 1e-9))
    r = np.arange(-nmax, nmax + 1)
    nx, ny, nz = np.meshgrid(np.arange(0, nmax + 1), r, r, indexing="ij")
    n = np.stack([nx.ravel(), ny.ravel(), nz.ravel()], 1)
    n2 = (n**2).sum(1)
    keep = ((n[:, 0] > 0) | ((n[:, 0] == 0) & (n[:, 1] > 0)) |
            ((n[:, 0] == 0) & (n[:, 1] == 0) & (n[:, 2] > 0))) & (n2 >= 1) & (n2 <= nmax2)
    return n[keep], n2[keep]


def rgrid(N):
    """Integer wave numbers of the rfftn grid of an array [z, y, x] (last axis halved)."""
    kz = np.fft.fftfreq(N, 1.0/N)[:, None, None]
    ky = np.fft.fftfreq(N, 1.0/N)[None, :, None]
    kx = np.arange(N//2 + 1)[None, None, :].astype(float)
    return kx, ky, kz


def coeffs(F, n, N):
    """c_n of f(x) = sum_n c_n exp(i k_n.x), x at cell centres (j + 1/2) h, from F = rfftn(f)."""
    ph = np.exp(-1j*np.pi*n.sum(1)/N)
    return F[n[:, 2] % N, n[:, 1] % N, n[:, 0]]*ph/N**3


def shell_power(F, N):
    """Sum and count of |c_n|^2 per integer |n|^2 over ALL modes (both hemispheres)."""
    kx, ky, kz = rgrid(N)
    n2 = (kx**2 + ky**2 + kz**2).astype(np.int64)
    w = np.full(F.shape, 2.0)
    w[:, :, 0] = 1.0
    if N % 2 == 0:
        w[:, :, N//2] = 1.0
    p = (np.abs(F)/N**3)**2
    nb = int(n2.max()) + 1
    s = np.bincount(n2.ravel(), weights=(w*p).ravel(), minlength=nb)
    c = np.bincount(n2.ravel(), weights=w.ravel(), minlength=nb)
    return s, c


# ---------------------------------------------------------------- self-test
def selftest(out):
    os.makedirs(out, exist_ok=True)
    N, nb = 16, 2
    h = 2*np.pi/N
    xc = (np.arange(N) + 0.5)*h
    Z, Y, X = np.meshgrid(xc, xc, xc, indexing="ij")
    f1 = np.sin(1*X + 2*Y + 3*Z + 0.3)
    f2 = 1.0 + 0.01*np.cos(-2*X + 1*Y + 0.7)
    path = os.path.join(out, "fake.dump")
    write_fake(path, {"phi": f1, "chi": f2, "K": -3.0 + 0*X}, nb)
    hd, fl = read_fields(path, ["phi", "chi", "K"])
    r = {}
    r["reader_max_err_phi"] = float(np.abs(fl["phi"] - f1).max())
    r["reader_max_err_chi"] = float(np.abs(fl["chi"] - f2).max())
    r["header"] = dict(time=hd["time"], cycle=hd["cycle"], nmb=hd["nmb"], names=hd["names"])
    n = np.array([[1, 2, 3], [2, -1, 0], [1, 0, 0]])
    F = sfft.rfftn(fl["phi"])
    c = coeffs(F, n, N)
    r["coeff_sin_n123"] = [c[0].real, c[0].imag]
    r["coeff_sin_expected"] = [(np.exp(0.3j)/(2j)).real, (np.exp(0.3j)/(2j)).imag]
    # cos(-2x + y + 0.7): hemisphere mode n = (2, -1, 0) carries exp(-i 0.7)/2 x 0.01
    F2 = sfft.rfftn(fl["chi"] - 1.0)
    c2 = coeffs(F2, n, N)
    r["coeff_cos_n2m10"] = [c2[1].real, c2[1].imag]
    r["coeff_cos_expected"] = [0.005*np.cos(0.7), -0.005*np.sin(0.7)]
    s, cnt = shell_power(F, N)
    r["parseval"] = [float(s.sum()), float((fl["phi"]**2).mean())]
    ok = (r["reader_max_err_phi"] == 0 and r["reader_max_err_chi"] == 0 and
          abs(c[0] - np.exp(0.3j)/(2j)) < 1e-13 and
          abs(c2[1] - 0.005*np.exp(-0.7j)) < 1e-15 and abs(s.sum() - (fl["phi"]**2).mean()) < 1e-13)
    r["pass"] = bool(ok)
    os.remove(path)
    with open(os.path.join(out, "selftest.json"), "w") as fo:
        json.dump(r, fo, indent=1, default=float)
    print(json.dumps(r, indent=1, default=float))
    return ok


# ---------------------------------------------------------------- one dump
def analyse_dump(path, nmax2, workers=4):
    t0 = time.time()
    hd = read_header(path)
    names = hd["names"]
    want = ["phi", "Pi", "chi", "K", "alpha", "gxx", "gxy", "gxz", "gyy", "gyz", "gzz"]
    hd, fl = read_fields(path, want)
    N = fl["phi"].shape[0]
    res = dict(path=path, time=hd["time"], cycle=hd["cycle"], N=N)
    for q in ("phi", "Pi", "chi", "K", "alpha"):
        res["mean_" + q] = float(fl[q].mean())
    res["mean_neg_half_ln_chi"] = float((-0.5*np.log(fl["chi"])).mean())
    res["efolds_from_mean_chi"] = float(-0.5*np.log(fl["chi"].mean()))
    H = -res["mean_K"]/3.0
    Pib = res["mean_Pi"]
    res["H"], res["Pi_b"] = H, Pib
    n, n2 = hemisphere(nmax2)
    kx, ky, kz = rgrid(N)
    k2 = kx**2 + ky**2 + kz**2
    k2[0, 0, 0] = 1.0
    Fphi = sfft.rfftn(fl["phi"] - fl["phi"].mean(), workers=workers)
    lnchi = np.log(fl["chi"])
    Fchi = sfft.rfftn(lnchi - lnchi.mean(), workers=workers)
    del lnchi
    # khat_i khat_j F[gt_ij - delta_ij]
    kk = np.zeros_like(Fchi)
    pairs = {"gxx": (kx, kx, 1.0), "gyy": (ky, ky, 1.0), "gzz": (kz, kz, 1.0),
             "gxy": (kx, ky, 2.0), "gxz": (kx, kz, 2.0), "gyz": (ky, kz, 2.0)}
    for q, (ka, kb, m) in pairs.items():
        g = fl.pop(q)
        if q in ("gxx", "gyy", "gzz"):
            g = g - 1.0
        kk += m*ka*kb/k2*sfft.rfftn(g, workers=workers)
        del g
    FPhichi = 0.5*Fchi
    FPhiE = 0.25*kk
    FR = FPhichi + FPhiE + (H/Pib)*Fphi
    FRnoE = FPhichi + (H/Pib)*Fphi
    res["n"] = n
    res["c_R"] = coeffs(FR, n, N)
    res["c_RnoE"] = coeffs(FRnoE, n, N)
    res["c_dphi"] = coeffs(Fphi, n, N)
    res["c_Phichi"] = coeffs(FPhichi, n, N)
    res["c_PhiE"] = coeffs(FPhiE, n, N)
    s, c = shell_power(FR, N)
    res["shell_sum_R"], res["shell_cnt"] = s, c
    s2, _ = shell_power(FRnoE, N)
    res["shell_sum_RnoE"] = s2
    # one-point statistics of R in real space
    R = sfft.irfftn(FR, s=(N, N, N), workers=workers)
    res["R_rms"] = float(np.sqrt((R**2).mean()))
    q = np.percentile(R, [0.5, 2.5, 15.865, 50, 84.135, 97.5, 99.5])
    res["R_pct"] = q
    res["R_maxabs"] = float(np.abs(R).max())
    del R, FR, FRnoE, FPhichi, FPhiE, kk, Fchi, Fphi
    # constraints
    cw = [q for q in ("H", "Mx", "My", "Mz", "E", "Hmag", "Mmag", "Axx", "Axy", "Axz", "Ayy",
                      "Ayz", "Azz") if q in names]
    if "H" in cw:
        _, cf = read_fields(path, cw)
        Hc = cf["H"]
        res["mean_absH"] = float(np.abs(Hc).mean())
        res["rms_H"] = float(np.sqrt((Hc**2).mean()))
        res["mean_H"] = float(Hc.mean())
        if all(a in cf for a in ("Axx", "E")):
            K = fl["K"]
            AA = (cf["Axx"]**2 + cf["Ayy"]**2 + cf["Azz"]**2 +
                  2*(cf["Axy"]**2 + cf["Axz"]**2 + cf["Ayz"]**2))
            R3 = Hc - (2.0/3.0)*K**2 + AA + 16*np.pi*cf["E"]
            Hmine = np.abs(R3) + (2.0/3.0)*K**2 + AA + np.abs(16*np.pi*cf["E"])
            res["mean_Hmag_mine"] = float(Hmine.mean())
            res["mean_absH_over_Hmag_mine"] = float((np.abs(Hc)/Hmine).mean())
            res["max_absH_over_Hmag_mine"] = float((np.abs(Hc)/Hmine).max())
            res["p99_absH_over_Hmag_mine"] = float(np.percentile(np.abs(Hc)/Hmine, 99))
            Hc0 = Hc - Hc.mean()
            res["mean_absH_boxmean_removed_over_Hmag_mine"] = float((np.abs(Hc0)/Hmine).mean())
            if "Hmag" in cf:
                res["mean_Hmag_dumped"] = float(cf["Hmag"].mean())
                res["max_rel_diff_Hmag"] = float(np.abs(Hmine/cf["Hmag"] - 1).max())
                res["mean_absH_over_Hmag_dumped"] = float((np.abs(Hc)/cf["Hmag"]).mean())
        if all(a in cf for a in ("Mx", "My", "Mz")):
            Mabs = np.sqrt(cf["Mx"]**2 + cf["My"]**2 + cf["Mz"]**2)
            res["mean_absM"] = float(Mabs.mean())
            if "Mmag" in cf:
                r = np.where(cf["Mmag"] > 0, Mabs/np.where(cf["Mmag"] > 0, cf["Mmag"], 1), 0)
                res["mean_absM_over_Mmag_dumped"] = float(r.mean())
                res["max_absM_over_Mmag_dumped"] = float(r.max())
                res["mean_Mmag_dumped"] = float(cf["Mmag"].mean())
    res["wall_s"] = time.time() - t0
    return res


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd")
    a1 = sub.add_parser("selftest")
    a1.add_argument("--out", required=True)
    a2 = sub.add_parser("run")
    a2.add_argument("--dumps", nargs="+", required=True)
    a2.add_argument("--nmax2", type=int, default=4096)
    a2.add_argument("--out", required=True)
    a2.add_argument("--tag", default="x")
    a2.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    if a.cmd == "selftest":
        sys.exit(0 if selftest(a.out) else 1)
    os.makedirs(a.out, exist_ok=True)
    if not selftest(os.path.join(a.out, "selftest")):
        sys.exit("self-test failed")
    summary = []
    for p in a.dumps:
        r = analyse_dump(p, a.nmax2, a.workers)
        base = os.path.basename(p).replace(".dump", "")
        arrays = {k: v for k, v in r.items() if isinstance(v, np.ndarray)}
        scal = {k: v for k, v in r.items() if not isinstance(v, np.ndarray)}
        np.savez_compressed(os.path.join(a.out, f"{a.tag}_{base}.npz"), **arrays)
        summary.append(scal)
        print(json.dumps(scal, default=float), flush=True)
        with open(os.path.join(a.out, f"{a.tag}_summary.json"), "w") as f:
            json.dump(summary, f, indent=1, default=float)


if __name__ == "__main__":
    main()
