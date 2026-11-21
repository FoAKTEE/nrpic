"""verifier_c18b, ledger line 199: constraint residuals of the jittered initial data.

    python3 residuals.py OUTDIR

Run B-20261119-141216-9c98929 wrote, per case (jit0p3, jit0p1, jit0), fields.bin (NRCOSMO1:
magic, 3 int64 (n1, n2, n3), then psi, K, alpha, Ahat_xx, xy, xz, yy, yz, zz as float64,
first index fastest; make_waves.py write_fields) and particles.nrp (NRPIC001, int64 N, N x 7
float64 x y z u_x u_y u_z m, N int32 species; docs/FORMATS.md). The constraints of the
slice gamma_ij = psi^4 delta_ij, K_ij = psi^-2 Ahat_ij + (1/3) psi^4 delta_ij K
(conformally flat, conformal-thin-sandwich-free form; my own statement of them):

    H := lap psi - (1/12) K^2 psi^5 + (1/8) psi^-7 Ahat_ij Ahat_ij + 2 pi psi^-1 Ehat = 0,
    M_i := d_j Ahat_ij - (2/3) psi^6 d_i K - 8 pi Shat_i = 0,

with Ehat = psi^6 E and Shat_i = psi^6 S_i the deposited sums per coordinate volume (the
code deposits m W and m u_i, nrpic.cpp; W = sqrt(1 + psi^-4 u.u) at the particle), cloud =
cubic B-spline (deposit_shape = pcs, nrpic.cpp lines 966-972), then the code's compensation
pass per direction (NrpicCompensateLimited, c = 1/6, c2 = 7/15, no limiter). Derivatives in
Fourier space (own implementation): Laplacian -|k|^2 for every mode; first derivatives i k
with the Nyquist wave number set to zero (variant A) or kept as i k_N (variant B, which is
not a real derivative; reported only to show the sensitivity). psi at the particles: tensor
cubic Lagrange interpolation of the cell-centred psi (it enters only through W - 1 ~ 2e-5).
The momentum residual is reported also per Fourier shell to show where it sits.
"""
import json
import os
import sys

import numpy as np

RUN = "/data/haiyangw/nrpic/scratch/B-emd-gw/B-20261119-141216-9c98929"
CASES = ("jit0p3", "jit0p1", "jit0")
C1, C2 = 1.0/6.0, 0.4666666666666667


def read_fields(path):
    with open(path, "rb") as f:
        assert f.read(8) == b"NRCOSMO1"
        n = tuple(int(v) for v in np.fromfile(f, "<i8", 3))
        nc = n[0]*n[1]*n[2]
        arr = [np.fromfile(f, "<f8", nc).reshape(n, order="F") for _ in range(9)]
        assert len(f.read()) == 0
    return n, arr[0], arr[1], arr[2], arr[3:]


def read_nrp(path):
    with open(path, "rb") as f:
        assert f.read(8) == b"NRPIC001"
        N = int(np.fromfile(f, "<i8", 1)[0])
        rec = np.fromfile(f, "<f8", 7*N).reshape(N, 7)
        sp = np.fromfile(f, "<i4", N)
        assert len(f.read()) == 0
    return rec, sp


def bspline3(s):
    return [(1 - s)**3/6, (3*s**3 - 6*s**2 + 4)/6, (-3*s**3 + 3*s**2 + 3*s + 1)/6, s**3/6]


def lagrange3(s):
    # nodes at -1, 0, 1, 2 (cell-centre offsets), evaluation at s in [0, 1)
    return [-s*(s - 1)*(s - 2)/6, (s + 1)*(s - 1)*(s - 2)/2, -(s + 1)*s*(s - 2)/2,
            (s + 1)*s*(s - 1)/6]


def stencil(x, n, h):
    i0, w = [], []
    for d in range(3):
        xi = x[:, d]/h - 0.5
        fl = np.floor(xi)
        i0.append(fl.astype(np.int64) - 1)
        w.append(xi - fl)
    return i0, w


def deposit(x, q, n, h):
    """Sum of q (N, ncomp) with the cubic B-spline cloud, per coordinate volume."""
    i0, s = stencil(x, n, h)
    W = [bspline3(s[d]) for d in range(3)]
    out = np.zeros((q.shape[1], n[0]*n[1]*n[2]))
    for a in range(4):
        ia = (i0[0] + a) % n[0]
        for b in range(4):
            ib = (i0[1] + b) % n[1]
            wab = W[0][a]*W[1][b]
            for c in range(4):
                ic = (i0[2] + c) % n[2]
                idx = (ia*n[1] + ib)*n[2] + ic
                w = wab*W[2][c]
                for k in range(q.shape[1]):
                    out[k] += np.bincount(idx, weights=w*q[:, k], minlength=out.shape[1])
    return out.reshape((q.shape[1],) + tuple(n))/h**3


def interp(f, x, n, h):
    i0, s = stencil(x, n, h)
    L = [lagrange3(s[d]) for d in range(3)]
    v = np.zeros(len(x))
    for a in range(4):
        ia = (i0[0] + a) % n[0]
        for b in range(4):
            ib = (i0[1] + b) % n[1]
            for c in range(4):
                ic = (i0[2] + c) % n[2]
                v += L[0][a]*L[1][b]*L[2][c]*f[ia, ib, ic]
    return v


def compensate(u):
    """The code's pass u - (F_{i+1/2} - F_{i-1/2}), F_{i+1/2} = c (u_{i+1} - u_i)
    - (c2/16)(u_{i+2} - 3 u_{i+1} + 3 u_i - u_{i-1}), directions in turn, periodic."""
    for ax in range(3):
        up = np.roll(u, -1, ax)
        upp = np.roll(u, -2, ax)
        um = np.roll(u, 1, ax)
        F = C1*(up - u) - (C2/16)*(upp - 3*up + 3*u - um)
        u = u - F + np.roll(F, 1, ax)
    return u


def wavenumbers(n, h, nyq_zero):
    ks = []
    for d in range(3):
        k = 2*np.pi*np.fft.fftfreq(n[d], d=h)
        if nyq_zero and n[d] % 2 == 0:
            k1 = k.copy()
            k1[n[d]//2] = 0.0
        else:
            k1 = k
        ks.append((k, k1))
    return ks


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    res = {}
    for case in CASES:
        d = os.path.join(RUN, case)
        idj = json.load(open(os.path.join(d, "id.json")))
        n, psi, K, alpha, A = read_fields(os.path.join(d, "fields.bin"))
        rec, sp = read_nrp(os.path.join(d, "particles.nrp"))
        h = float(idj["box"][0])/n[0]
        assert abs(h - idj["h"]) < 1e-15 and np.allclose(idj["box"], [h*v for v in n])
        x, u, m = rec[:, :3], rec[:, 3:6], rec[:, 6]
        psip = interp(psi, x, n, h)
        Wl = np.sqrt(1 + (u*u).sum(axis=1)/psip**4)
        q = np.column_stack([m*Wl, m*u[:, 0], m*u[:, 1], m*u[:, 2]])
        D = deposit(x, q, n, h)
        Dc = np.array([compensate(D[k]) for k in range(4)])
        Ehat, Shat = Dc[0], Dc[1:]
        AA = A[0]**2 + A[3]**2 + A[5]**2 + 2*(A[1]**2 + A[2]**2 + A[4]**2)
        Afull = [[A[0], A[1], A[2]], [A[1], A[3], A[4]], [A[2], A[4], A[5]]]
        r = {"N": int(len(m)), "n": list(n), "h": h, "mass_sum": float(m.sum()),
             "mass_sum_id_json": idj["total_rest_mass"],
             "deposit_integral_over_mass": float(D[0].sum()*h**3/(m*Wl).sum())}
        for variant, nyq in (("A_nyquist_zero", True), ("B_nyquist_kept", False)):
            ks = wavenumbers(n, h, nyq)
            kx, ky, kz = np.meshgrid(ks[0][0], ks[1][0], ks[2][0], indexing="ij")
            k2 = kx**2 + ky**2 + kz**2
            k1 = np.meshgrid(ks[0][1], ks[1][1], ks[2][1], indexing="ij")

            def ifft(F):
                return np.real(np.fft.ifftn(F))
            lap = ifft(-k2*np.fft.fftn(psi))
            Hres = lap - K**2*psi**5/12 + psi**-7*AA/8 + 2*np.pi*Ehat/psi
            Kf = np.fft.fftn(K)
            Af = [[np.fft.fftn(Afull[i][j]) for j in range(3)] for i in range(3)]
            Mres = []
            for i in range(3):
                div = ifft(sum(1j*k1[j]*Af[i][j] for j in range(3)))
                dK = ifft(1j*k1[i]*Kf)
                Mres.append(div - (2/3)*psi**6*dK - 8*np.pi*Shat[i])
            v = {"max_hamiltonian_residual": float(np.abs(Hres).max()),
                 "max_hamiltonian_term": float(np.abs(2*np.pi*Ehat/psi).max()),
                 "max_momentum_residual": float(max(np.abs(mm).max() for mm in Mres)),
                 "max_momentum_source": float(np.abs(8*np.pi*Shat).max())}
            if variant == "A_nyquist_zero":
                # where the momentum residual sits: power per |k| shell and on Nyquist planes
                P = sum(np.abs(np.fft.fftn(mm))**2 for mm in Mres)
                kmag = np.sqrt(k2)/(2*np.pi/(n[0]*h))
                shell = np.rint(kmag).astype(int)
                tot = P.sum()
                v["momentum_residual_power_share_shell_ge_28"] = float(P[shell >= 28].sum()/tot) if tot > 0 else 0.0
                nyq_mask = np.zeros(n, bool)
                nyq_mask[n[0]//2, :, :] = True
                nyq_mask[:, n[1]//2, :] = True
                nyq_mask[:, :, n[2]//2] = True
                v["momentum_residual_power_share_on_nyquist_planes"] = float(P[nyq_mask].sum()/tot) if tot > 0 else 0.0
                np.save(os.path.join(out, f"{case}_Hres.npy"), Hres.astype(np.float32))
                np.save(os.path.join(out, f"{case}_Mres_x.npy"), Mres[0].astype(np.float32))
                np.save(os.path.join(out, f"{case}_Mres_y.npy"), Mres[1].astype(np.float32))
            if variant == "A_nyquist_zero":
                # sensitivity of H to the interpolation of psi to the particles (enters via W)
                from scipy import ndimage
                cx = np.stack([x[:, dd]/h - 0.5 for dd in range(3)])
                sens = {}
                for nm, pp in (("cubic_bspline_ndimage", ndimage.map_coordinates(psi, cx, order=3, mode="grid-wrap")),
                               ("linear_ndimage", ndimage.map_coordinates(psi, cx, order=1, mode="grid-wrap"))):
                    W2 = np.sqrt(1 + (u*u).sum(axis=1)/pp**4)
                    E2 = compensate(deposit(x, (m*W2)[:, None], n, h)[0])
                    H2 = lap - K**2*psi**5/12 + psi**-7*AA/8 + 2*np.pi*E2/psi
                    sens[nm] = {"max_hamiltonian_residual": float(np.abs(H2).max()),
                                "max_abs_psi_difference_at_particles": float(np.abs(pp - psip).max())}
                v["interpolation_sensitivity"] = sens
            r[variant] = v
        r["id_json"] = {k: idj[k] for k in ("max_hamiltonian_residual", "max_hamiltonian_term",
                                             "max_momentum_residual", "jitter")}
        res[case] = r
        print(case, json.dumps(r, indent=1), flush=True)
    with open(os.path.join(out, "residuals_c18b.json"), "w") as f:
        json.dump(res, f, indent=1)
    figure(res, out)


def figure(res, out):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.8))
    for col, case in enumerate(("jit0p3", "jit0p1")):
        ax = axs[col]
        M = np.load(os.path.join(out, f"{case}_Mres_y.npy"))
        n = M.shape
        im = ax.imshow(M[:, :, n[2]//3].T, origin="lower", cmap="RdBu_r",
                       vmin=-np.abs(M).max(), vmax=np.abs(M).max())
        ax.set_xlabel("i (x)")
        ax.set_ylabel("j (y)")
        ax.set_title(f"(%s) $M_y$ residual, {case}" % "ab"[col], fontsize=8)
        fs.side_colorbar(fig, ax, im, "")
    ax = axs[2]
    cases = list(res)
    x = np.arange(len(cases))
    mine = [res[c]["A_nyquist_zero"]["max_momentum_residual"] for c in cases]
    led = [res[c]["id_json"]["max_momentum_residual"] for c in cases]
    hm = [res[c]["A_nyquist_zero"]["max_hamiltonian_residual"] for c in cases]
    hl = [res[c]["id_json"]["max_hamiltonian_residual"] for c in cases]
    ax.semilogy(x - 0.1, np.maximum(mine, 1e-18), "o", color=fs.PAL["blue"], label="momentum, own")
    ax.semilogy(x + 0.1, np.maximum(led, 1e-18), "s", mfc="none", color=fs.PAL["blue"], label="momentum, id.json")
    ax.semilogy(x - 0.1, np.maximum(hm, 1e-18), "o", color=fs.PAL["red"], label="Hamiltonian, own")
    ax.semilogy(x + 0.1, np.maximum(hl, 1e-18), "s", mfc="none", color=fs.PAL["red"], label="Hamiltonian, id.json")
    ax.set_xticks(x)
    ax.set_xticklabels(cases)
    ax.set_ylabel("largest residual")
    ax.legend(fontsize=6)
    ax.set_title("(c) line 199", fontsize=8)
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "residuals_c18b"))


if __name__ == "__main__":
    main()
