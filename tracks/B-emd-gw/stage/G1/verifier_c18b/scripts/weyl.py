"""verifier_c18b, ledger line 124: gauge difference of the magnetic Weyl part and of the flat
TT strain at K1 = (k, k, 0) between zero shift (cw_eps1) and the Gamma driver (cw_eps1_gd),
run B-20261115-165353-b592d43 (64^3, L = 4, double-precision restart dumps every unit of t).

    python3 weyl.py OUTDIR

Own restart reader (layout of athenak/src/outputs/restart.cpp WriteOutputFile: text, int
nmb, int root_level, RegionSize (9 double), 2 RegionIndcs, double time, double dt, int ncycle,
nmb LogicalLocation (4 int32), nmb float cost, double z4c last_output_time, uint64 data size,
then per MeshBlock the 22 Z4c arrays (order of z4c.hpp: chi, gxx..gzz, Khat, Axx..Azz,
Gamx..z, Theta, alpha, betax..z) with ghost cells, first index fastest). The data are the
file's tail; the header fields are read backwards from the data.
Checks of the reader: t = 0 dump against the code's own NRFIELD2 field dump at t = 0 (chi,
Khat, Theta, alpha); det(gtilde) = 1 and gtilde^ij Atilde_ij = 0 at every dump.

Quantities (own definitions, spectral derivatives on the periodic mesh):
  gamma_ij = gtilde_ij / chi,  K = Khat + 2 Theta,  K_ij = (Atilde_ij + gtilde_ij K / 3) / chi,
  B_ij = sym_ij eps_i^{kl} D_k K_lj  (full nonlinear expression: Christoffels of gamma,
         eps^{mkl} = [mkl] / sqrt(gamma), index lowered with gamma),
  h_ij = gtilde_ij - delta_ij (traceless part);
  mode amplitude amp(f) = (2/N) sum f exp(-i K1.x) at the cell centres = c - i s;
  polarizations at K1: u = (1, -1, 0)/sqrt2, z; e+ = uu - zz, ex = uz + zu,
  f_+ = (1/2) e+_ij amp(f_ij), f_x = (1/2) ex_ij amp(f_ij) (TT at K1 already).
Line 124 reads: median over common dumps with 1.5 < a <= 64 of |X_z - X_g| / max(|X_z|, |X_g|),
X = sine part of B_x (magnetic Weyl), and X = cosine part of h_+ (flat TT strain).
"""
import json
import os
import struct
import sys

import numpy as np

RUN = "/data/haiyangw/nrpic/scratch/B-emd-gw/B-20261115-165353-b592d43"
NZ = 22
NAMES = ["chi", "gxx", "gxy", "gxz", "gyy", "gyz", "gzz", "Khat", "Axx", "Axy", "Axz", "Ayy",
         "Ayz", "Azz", "Gamx", "Gamy", "Gamz", "Theta", "alpha", "betax", "betay", "betaz"]
SYM = {"xx": (0, 0), "xy": (0, 1), "xz": (0, 2), "yy": (1, 1), "yz": (1, 2), "zz": (2, 2)}


def read_rst(path, n=64, nb=32, ng=4):
    nmb = (n//nb)**3
    no = nb + 2*ng
    dsz = nmb*NZ*no**3*8
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        f.seek(size - dsz - 8)
        ds = struct.unpack("<Q", f.read(8))[0]
        assert ds in (dsz, dsz//nmb), (ds, dsz)   # restart.cpp writes the size per MeshBlock
        p = size - dsz - 8 - 8 - 4*nmb - 16*nmb
        f.seek(p)
        lloc = np.frombuffer(f.read(16*nmb), "<i4").reshape(nmb, 4)
        f.seek(p - 4 - 8 - 8)
        t, dt = struct.unpack("<2d", f.read(16))
        cyc = struct.unpack("<i", f.read(4))[0]
        f.seek(size - dsz)
        raw = np.frombuffer(f.read(dsz), "<f8").reshape(nmb, NZ, no, no, no)
    out = {nm: np.empty((n, n, n)) for nm in NAMES}     # indexed [i, j, k] = (x, y, z)
    for m in range(nmb):
        lx1, lx2, lx3, lev = lloc[m]
        blk = raw[m][:, ng:ng + nb, ng:ng + nb, ng:ng + nb]   # [var, k, j, i]
        for v, nm in enumerate(NAMES):
            out[nm][lx1*nb:(lx1 + 1)*nb, lx2*nb:(lx2 + 1)*nb, lx3*nb:(lx3 + 1)*nb] = \
                blk[v].transpose(2, 1, 0)
    return t, cyc, out


def read_field(path):
    with open(path, "rb") as f:
        magic = f.read(8)
        t = struct.unpack("<d", f.read(8))[0]
        n1, n2, n3 = struct.unpack("<3q", f.read(24))
        nc = n1*n2*n3
        o = {"t": t}
        for key in ("E", "chi"):
            o[key] = np.fromfile(f, "<f4", nc).astype(float).reshape(n3, n2, n1).transpose(2, 1, 0)
        for key in ("H", "Mx", "My", "Mz", "Khat", "Theta", "alpha"):
            o[key] = np.fromfile(f, "<f8", nc).reshape(n3, n2, n1).transpose(2, 1, 0)
    return o


class Spec:
    def __init__(self, n, L):
        k = 2*np.pi*np.fft.fftfreq(n, d=L/n)
        k1 = k.copy()
        k1[n//2] = 0.0
        self.k = np.meshgrid(k1, k1, k1, indexing="ij")
        self.h = L/n
        self.n = n
        self.L = L

    def d(self, f, a):
        return np.real(np.fft.ifftn(1j*self.k[a]*np.fft.fftn(f)))


def tensor(o, base):
    T = np.empty((3, 3) + o[base + "xx"].shape)
    for s, (a, b) in SYM.items():
        T[a, b] = o[base + s]
        T[b, a] = o[base + s]
    return T


def magnetic_weyl(o, sp):
    chi = o["chi"]
    gt = tensor(o, "g")
    At = tensor(o, "A")
    K = o["Khat"] + 2.0*o["Theta"]
    g = gt/chi
    Kij = (At + gt*K/3.0)/chi
    gi = np.linalg.inv(np.moveaxis(g, (0, 1), (-2, -1)))
    gi = np.moveaxis(gi, (-2, -1), (0, 1))
    dg = np.array([[[sp.d(g[i, j], k) for j in range(3)] for i in range(3)] for k in range(3)])  # [k, i, j]
    # Gamma^m_kl = (1/2) g^mn (d_k g_nl + d_l g_nk - d_n g_kl)
    # low[n, k, l] = 1/2 (d_k g_nl + d_l g_nk - d_n g_kl)
    low = 0.5*(dg.transpose(1, 0, 2, 3, 4, 5) + dg.transpose(1, 2, 0, 3, 4, 5) - dg)
    # dg[k, i, j] = d_k g_ij ; dg.transpose(1,0,2)[n,k,l] = dg[k,n,l] = d_k g_nl ;
    # dg.transpose(1,2,0)[n,k,l] = dg[l,n,k] = d_l g_nk ; dg[n,k,l] = d_n g_kl
    Gam = np.einsum("mn...,nkl...->mkl...", gi, low)
    dK = np.array([[[sp.d(Kij[i, j], k) for j in range(3)] for i in range(3)] for k in range(3)])  # [k, l, j]
    DK = dK - np.einsum("mkl...,mj...->klj...", Gam, Kij) - np.einsum("mkj...,lm...->klj...", Gam, Kij)
    det = np.linalg.det(np.moveaxis(g, (0, 1), (-2, -1)))
    eps = np.zeros((3, 3, 3))
    eps[0, 1, 2] = eps[1, 2, 0] = eps[2, 0, 1] = 1.0
    eps[0, 2, 1] = eps[2, 1, 0] = eps[1, 0, 2] = -1.0
    # eps_i^{kl} = g_im [mkl] / sqrt(det)
    epsl = np.einsum("im...,mkl->ikl...", g, eps)/np.sqrt(det)
    B = np.einsum("ikl...,klj...->ij...", epsl, DK)
    return 0.5*(B + B.transpose(1, 0, 2, 3, 4))


def amp(f, sp, m=(1, 1, 0)):
    x = (np.arange(sp.n) + 0.5)*sp.h
    kk = 2*np.pi/sp.L
    ph = np.exp(-1j*kk*(m[0]*x[:, None, None] + m[1]*x[None, :, None] + m[2]*x[None, None, :]))
    return 2.0*np.sum(f*ph, axis=(-3, -2, -1))/f.shape[-1]**3


def pol(T, sp):
    u = np.array([1.0, -1.0, 0.0])/np.sqrt(2)
    z = np.array([0.0, 0.0, 1.0])
    ep = np.outer(u, u) - np.outer(z, z)
    ex = np.outer(u, z) + np.outer(z, u)
    A = np.array([[amp(T[i, j], sp) for j in range(3)] for i in range(3)])
    return 0.5*np.sum(ep*A), 0.5*np.sum(ex*A)


def analyse(case, sp):
    d = os.path.join(RUN, case, "rst")
    rows = []
    files = sorted(f for f in os.listdir(d) if f.endswith(".rst"))
    for fn in files:
        t, cyc, o = read_rst(os.path.join(d, fn))
        gt = tensor(o, "g")
        det = np.linalg.det(np.moveaxis(gt, (0, 1), (-2, -1)))
        gti = np.moveaxis(np.linalg.inv(np.moveaxis(gt, (0, 1), (-2, -1))), (-2, -1), (0, 1))
        trA = np.einsum("ij...,ij...->...", gti, tensor(o, "A"))
        B = magnetic_weyl(o, sp)
        h = gt - np.eye(3)[:, :, None, None, None]
        h = h - np.eye(3)[:, :, None, None, None]*np.einsum("ii...->...", h)/3.0
        Bp, Bx = pol(B, sp)
        hp, hx = pol(h, sp)
        rows.append({"file": fn, "t": t, "cycle": cyc, "a": (1 + 0.5*t)**2,
                     "a_chi": float(np.mean(o["chi"])**-0.5),
                     "max_det_gt_minus_1": float(np.abs(det - 1).max()),
                     "max_trA": float(np.abs(trA).max()),
                     "B_plus": [Bp.real, Bp.imag], "B_cross": [Bx.real, Bx.imag],
                     "h_plus": [hp.real, hp.imag], "h_cross": [hx.real, hx.imag],
                     "rms_B": float(np.sqrt(np.mean(B**2)))})
        print(case, fn, f"t={t:.3f} a={(1 + 0.5*t)**2:.2f} Bx={Bx:.4e} h+={hp:.4e}", flush=True)
        if fn == files[0]:
            f0 = read_field(os.path.join(RUN, case, "cw.field.00000.bin"))
            rows[-1]["check_t0_vs_field_dump"] = {
                "t_field": f0["t"],
                "chi_max_rel": float(np.abs(o["chi"]/f0["chi"] - 1).max()),
                "Khat_max_abs": float(np.abs(o["Khat"] - f0["Khat"]).max()),
                "Theta_max_abs": float(np.abs(o["Theta"] - f0["Theta"]).max()),
                "alpha_max_abs": float(np.abs(o["alpha"] - f0["alpha"]).max())}
            print(rows[-1]["check_t0_vs_field_dump"], flush=True)
    return rows


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    sp = Spec(64, 4.0)
    # check of the derivative and of B on an analytic field: a TT wave in flat space,
    # gamma = delta + h, h_+ = A cos(K.x) along e+, K_ij = -(1/2) d_t h_ij with h ~ cos(K.x - w t)
    # at t = 0: K_ij = -(1/2) w A sin(K.x) e+_ij. Linear B_ij = sym eps_i^{kl} d_k K_lj.
    x = (np.arange(64) + 0.5)*sp.h
    X, Y, Z = np.meshgrid(x, x, x, indexing="ij")
    kk = 2*np.pi/4.0
    ph = kk*(X + Y)
    Aamp, w = 1e-6, kk*np.sqrt(2)
    u = np.array([1.0, -1.0, 0.0])/np.sqrt(2)
    zz = np.array([0.0, 0.0, 1.0])
    ep = np.outer(u, u) - np.outer(zz, zz)
    test = {"chi": np.ones_like(X), "Khat": np.zeros_like(X), "Theta": np.zeros_like(X)}
    for s, (a, b) in SYM.items():
        test["g" + s] = (1.0 if a == b else 0.0) + 0*X
        test["A" + s] = -0.5*w*Aamp*np.sin(ph)*ep[a, b]
    Bt = magnetic_weyl(test, sp)
    Btp, Btx = pol(Bt, sp)
    # expected: B = curl of K; for h_+ ~ cos, K ~ -(w A/2) sin(K.x) e+; eps_i^{kl} d_k K_lj
    # = (w A/2)(-cos) (Khat x e+) ... its cross amplitude has modulus (1/2) w A |K1| (own algebra:
    # nhat x e+ = ex up to sign, |K1| = kk sqrt2)
    expect = 0.5*w*Aamp*kk*np.sqrt(2)
    res = {"analytic_check": {"B_cross": [Btx.real, Btx.imag], "B_plus": [Btp.real, Btp.imag],
                              "expected_abs_B_cross": expect,
                              "rel_err": float(abs(abs(Btx) - expect)/expect)}}
    print("analytic", res["analytic_check"], flush=True)
    z = analyse("cw_eps1", sp)
    g = analyse("cw_eps1_gd", sp)
    res["cw_eps1"], res["cw_eps1_gd"] = z, g
    tz = {round(r["t"], 6): r for r in z}
    comm = [(tz[round(r["t"], 6)], r) for r in g if round(r["t"], 6) in tz]
    a, dB, dh, dBc, dhs = [], [], [], [], []
    def rel(x, y):
        m = max(abs(x), abs(y))
        return abs(x - y)/m if m > 0 else float("nan")
    for rz, rg in comm:
        if rz["t"] == 0.0:
            continue                    # conformally flat data: h = 0 in both
        a.append(rz["a"])
        bz, bg = rz["B_cross"][1], rg["B_cross"][1]
        hz, hg = rz["h_plus"][0], rg["h_plus"][0]
        dB.append(rel(bz, bg))
        dh.append(rel(hz, hg))
        Bz, Bg = complex(*rz["B_cross"]), complex(*rg["B_cross"])
        Hz, Hg = complex(*rz["h_plus"]), complex(*rg["h_plus"])
        dBc.append(rel(Bz, Bg))
        dhs.append(rel(Hz, Hg))
    a, dB, dh, dBc, dhs = map(np.array, (a, dB, dh, dBc, dhs))
    sel = (a > 1.5) & (a <= 64)
    res["common"] = {"a": a.tolist(), "dB_sin": dB.tolist(), "dh_cos": dh.tolist(),
                     "dB_complex": dBc.tolist(), "dh_complex": dhs.tolist()}
    res["n_selected"] = int(sel.sum())
    res["median_dB_sin_le64"] = float(np.median(dB[sel]))
    res["median_dh_cos_le64"] = float(np.median(dh[sel]))
    res["median_dB_complex_le64"] = float(np.median(dBc[sel]))
    res["median_dh_complex_le64"] = float(np.median(dhs[sel]))
    with open(os.path.join(out, "weyl_c18b.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps({k: v for k, v in res.items() if k.startswith("median") or k == "n_selected"}))
    figure(res, out)


def figure(res, out):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH*0.75, 2.8))
    ax = axs[0]
    for case, c in (("cw_eps1", fs.PAL["blue"]), ("cw_eps1_gd", fs.PAL["red"])):
        r = res[case]
        a = np.array([x["a"] for x in r])
        ax.loglog(a, np.abs([x["B_cross"][1] for x in r]), "o-", ms=3, color=c,
                  label=f"$|B_\\times|$ sin, {case.replace('_', ' ')}")
        ax.loglog(a, np.abs([x["h_plus"][0] for x in r]), "s--", ms=3, mfc="none", color=c,
                  label=f"$|h_+|$ cos, {case.replace('_', ' ')}")
    ax.set_xlabel("$a$")
    ax.set_ylabel("amplitude at $K_1$")
    ax.legend(fontsize=5.5)
    ax.set_title("(a) the two gauges", fontsize=8)
    ax = axs[1]
    a = np.array(res["common"]["a"])
    ax.loglog(a, res["common"]["dB_sin"], "o-", ms=3, color=fs.PAL["red"], label="magnetic Weyl")
    ax.loglog(a, res["common"]["dh_cos"], "s-", ms=3, color=fs.PAL["blue"], label="flat TT strain")
    ax.axvspan(1.5, 64, color="grey", alpha=0.12)
    ax.axhline(res["median_dB_sin_le64"], color=fs.PAL["red"], lw=0.8, ls=":")
    ax.axhline(res["median_dh_cos_le64"], color=fs.PAL["blue"], lw=0.8, ls=":")
    ax.set_xlabel("$a$")
    ax.set_ylabel("relative gauge difference")
    ax.legend(fontsize=6)
    ax.set_title("(b) line 124 (dotted: medians)", fontsize=8)
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "weyl_c18b"))


if __name__ == "__main__":
    main()
