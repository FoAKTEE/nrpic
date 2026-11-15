#!/usr/bin/env python3
"""Tests of the estimators of ../sfa.py on synthetic fields (no AthenaK run needed).

    python3 test_sfa.py --out DIR

T1 reader and mode coefficients: a field synthesised from known coefficients, written as
   an NRSFDMP1 dump of 8 MeshBlocks (layout of athenak/src/scalar_field/scalar_field_io.cpp
   lines 12-17), read back and analysed; L and x0 recovered.
T2 curvature perturbation on a synthetic slice built nonlinearly from R, psi and E:
   gamma_ij = a^2 [(1 - 2 psi) delta_ij + 2 d_i d_j E], chi = det(gamma)^(-1/3),
   gt = chi gamma, phi = phi_b + (phidot/H)(R - psi). The estimator must return R with an
   error of second order in the amplitude; without the gt term (what the dump alone
   allows) the error is first order when E is not zero (negative control); a wrong sign
   of <Pi> doubles nothing but makes the error of order one (second control).
T3 per-mode ratio and freezing drift: a field with planted relative deviations delta_n
   from L^(-3/2) W R alpha, with a .modes record written in the code's format; the
   estimator returns delta_n. Drift of c (1 + b e^(-2N)) between two e-folds.
T4 shell spectrum: unit-modulus amplitudes with Delta = Delta0 give Delta0 in every shell;
   Gaussian amplitudes of the code's keys give shell means consistent with Delta0.
T5 constraints: the first difference against the stencil symbol; [H] per cell from H, K,
   E with a known Ricci scalar; [M] of a plane wave against its closed form.
Writes DIR/test_sfa.json and figures DIR/fig_t*.png; exit 1 if a test fails.
"""
import argparse
import json
import os
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import sfa  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402
from nrpic import scalar_field as nsf  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

RESULTS = []


def record(tid, name, value, crit, passed, **extra):
    RESULTS.append(dict(id=tid, name=name, value=value, criterion=crit, passed=bool(passed),
                        **extra))
    print(f"{tid} {'PASS' if passed else 'FAIL'} {name}: {value:.3e} ({crit})", flush=True)


# --------------------------------------------------------------------- helpers
def write_dump(fname, fields, names, x0, L, nb, time=0.5, cycle=7, nnoise=0):
    """NRSFDMP1 file with nb^3 MeshBlocks of the fields [i, j, k] (all on the root)."""
    N = fields[names[0]].shape[0]
    m = N // nb
    h = L / N
    with open(fname, "wb") as fp:
        fp.write(b"NRSFDMP1")
        fp.write(struct.pack("<7q", nb ** 3, m, m, m, len(names), cycle, nnoise))
        fp.write(struct.pack("<d", time))
        for lz in range(nb):
            for ly in range(nb):
                for lx in range(nb):
                    fp.write(struct.pack("<4q", 0, lx, ly, lz))
                    fp.write(struct.pack("<6d", x0[0] + lx * m * h, x0[0] + (lx + 1) * m * h,
                                         x0[1] + ly * m * h, x0[1] + (ly + 1) * m * h,
                                         x0[2] + lz * m * h, x0[2] + (lz + 1) * m * h))
                    for v in names:
                        blk = fields[v][lx * m:(lx + 1) * m, ly * m:(ly + 1) * m,
                                        lz * m:(lz + 1) * m]
                        fp.write(np.ascontiguousarray(blk.transpose(2, 1, 0)).astype("<f8")
                                 .tobytes())


def spectral_d(f, L, axes):
    """Spectral derivative d_{a} d_{b} ... of a periodic field."""
    N = f.shape[0]
    k = sfa._kvec(N, L)
    F = np.fft.fftn(f)
    for a in axes:
        F = F * (1j * k[a])
    return np.fft.ifftn(F).real


def random_field(lat, rng, amp, slope=-1.5):
    c = amp * lat.q ** slope * (rng.standard_normal(lat.n2.size)
                                + 1j * rng.standard_normal(lat.n2.size)) / np.sqrt(2)
    return lat.synthesise(c), c


# ------------------------------------------------------------------------ tests
def t1(out):
    N, L, x0 = 32, 2.5, np.array([-1.25, -1.25, -1.25])
    lat = sfa.Lattice(N, L, 64)
    rng = np.random.default_rng(1)
    f, c = random_field(lat, rng, 1.0)
    fields = {v: np.zeros((N, N, N)) for v in nsf.DUMP_VARS}
    fields["phi"] = f
    fields["noise0"] = 2.0 * f
    names = nsf.DUMP_VARS + ["noise0"]
    fn = os.path.join(out, "t1.sf.00007.dump")
    write_dump(fn, fields, names, x0, L, nb=2, nnoise=1)
    d = sfa.read_dump(fn)
    err = np.abs(lat.coefficients(d["phi"]) - c).max() / np.sqrt(np.mean(np.abs(c) ** 2))
    record("T1a", "coefficients of a field read from an 8-MeshBlock dump", err, "<= 1e-13",
           err <= 1e-13)
    geo = abs(d["L"] - L) + np.abs(d["x0"] - x0).max() + abs(d["h"] - L / N)
    record("T1b", "L, x0, h recovered from the MeshBlock extents", geo, "<= 1e-15",
           geo <= 1e-15 and d["cycle"] == 7 and d["time"] == 0.5)
    err2 = np.abs(lat.coefficients(d["noise0"]) - 2 * c).max() / \
        np.sqrt(np.mean(np.abs(2 * c) ** 2))
    record("T1c", "noise field named and assembled", err2, "<= 1e-13", err2 <= 1e-13)
    os.remove(fn)


def slice_fields(lat, R, psi, E, a, hub, phidot, phib=3.0, dpi=None, dk=None):
    L = lat.L
    N = lat.N
    gam = np.empty((3, 3, N, N, N))
    for i in range(3):
        for j in range(3):
            gam[i, j] = a * a * ((1.0 - 2.0 * psi) * (i == j) + 2.0 * spectral_d(E, L, (i, j)))
    det = np.linalg.det(np.moveaxis(gam, (0, 1), (-2, -1)))
    chi = det ** (-1.0 / 3.0)
    gt = {(i, j): chi * gam[i, j] for i in range(3) for j in range(i, 3)}
    d = dict(chi=chi, phi=phib + (phidot / hub) * (R - psi),
             Pi=phidot + (0.0 if dpi is None else dpi), K=-3.0 * hub + (0.0 if dk is None else dk),
             alpha=np.ones_like(chi), h=lat.h)
    return d, gt


def t2(out):
    N, L = 32, 2 * np.pi
    lat = sfa.Lattice(N, L, 64)
    rng = np.random.default_rng(2)
    a, hub, phidot = 1.3, 0.8, -0.05
    base_r, _ = random_field(lat, rng, 1.0)
    base_p, _ = random_field(lat, rng, 0.7)
    base_e, _ = random_field(lat, rng, 0.5, slope=-3.5)   # E ~ psi/k^2
    dpi_b, _ = random_field(lat, rng, 0.3)
    dk_b, _ = random_field(lat, rng, 0.3)
    amps = np.array([1e-2, 3e-3, 1e-3, 3e-4, 1e-4, 3e-5, 1e-5])
    rows = []
    for A in amps:
        r = A * base_r / base_r.std()
        psi = A * base_p / base_r.std()
        e = A * base_e / base_r.std()
        d, gt = slice_fields(lat, r, psi, e, a, hub, phidot, dpi=A * dpi_b, dk=A * dk_b)
        rel = []
        for g, sign in ((gt, 1.0), (None, 1.0), (gt, -1.0)):
            dd = dict(d)
            if sign < 0:
                dd["Pi"] = -d["Pi"]
            est = sfa.curvature_perturbation(dd, g)
            rel.append(np.abs(est["R"] - (r - r.mean())).max() / r.std())
        rows.append(rel + [est["rms_gt_term"] / r.std()])
    rows = np.array(rows)
    slope = np.polyfit(np.log(amps[2:]), np.log(rows[2:, 0]), 1)[0]
    record("T2a", "R^NR with the gt term: relative error at amplitude 1e-5", rows[-1, 0],
           "<= 1e-3 and slope 1 +- 0.1", rows[-1, 0] <= 1e-3 and abs(slope - 1) < 0.1,
           slope=float(slope))
    slope_c = np.polyfit(np.log(amps), np.log(rows[:, 1]), 1)[0]
    record("T2b", "control without the gt term: relative error (first order)", rows[-1, 1],
           ">= 1e-2 and slope 0 +- 0.1", rows[-1, 1] >= 1e-2 and abs(slope_c) < 0.1,
           slope=float(slope_c))
    record("T2c", "control with the sign of <Pi> flipped: relative error", rows[-1, 2],
           ">= 0.5", rows[-1, 2] >= 0.5)
    # data of SPEC 5.3 (geodesic gauge at t*): delta X = 2 Phi_B, gt = delta,
    # delta phi = (phidot/H)(R - Phi_B): the estimator returns R exactly at first order
    A = 1e-5
    r = A * base_r / base_r.std()
    pb = A * base_p / base_r.std()
    d, _ = slice_fields(lat, r, pb, 0.0 * pb, 1.0, hub, phidot)
    d["chi"] = 1.0 + 2.0 * pb
    est = sfa.curvature_perturbation(d, None)
    e53 = np.abs(est["R"] - (r - r.mean())).max() / r.std()
    record("T2d", "slice of SPEC 5.3 (delta X = 2 Phi_B, delta gt = 0): relative error",
           e53, "<= 1e-4 (second order at A = 1e-5)", e53 <= 1e-4)
    fs.use_style()
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.2))
    ax[0].loglog(amps, rows[:, 0], "o-", color=fs.PAL["red"], label="estimator with $\\tilde\\gamma_{ij}$")
    ax[0].loglog(amps, rows[:, 1], "s-", color=fs.PAL["yellow"], label="without $\\tilde\\gamma_{ij}$ (dump only)")
    ax[0].loglog(amps, rows[:, 2], "^-", color=fs.PAL["green"], label="sign of $\\langle\\Pi\\rangle$ flipped")
    ax[0].loglog(amps, rows[:, 3], ":", color="k", label="rms of the $\\tilde\\gamma$ term / rms $R$")
    ax[0].loglog(amps, rows[0, 0] * amps / amps[0], **fs.GUIDE, label="$\\propto A$ (second order)")
    ax[0].set_xlabel("amplitude $A$ of $R$")
    ax[0].set_ylabel(r"max $|R^{\rm est}-R|$ / rms $R$")
    ax[0].legend(fontsize=7, loc="lower right")
    A = 1e-3
    r = A * base_r / base_r.std()
    d, gt = slice_fields(lat, r, A * base_p / base_r.std(), A * base_e / base_r.std(), a, hub,
                         phidot)
    est = sfa.curvature_perturbation(d, gt)
    est0 = sfa.curvature_perturbation(d, None)
    x = (np.arange(N) + 0.5) * lat.h
    ax[1].plot(x, r[:, 5, 9] / A, color=fs.PAL["blue"], label="$R$ planted")
    ax[1].plot(x, est["R"][:, 5, 9] / A, "--", color=fs.PAL["red"], label="estimator")
    ax[1].plot(x, est0["R"][:, 5, 9] / A, ":", color=fs.PAL["yellow"], label="without $\\tilde\\gamma_{ij}$")
    ax[1].set_xlabel("$x$ (line $j = 5$, $k = 9$)")
    ax[1].set_ylabel("$R / A$ ($A = 10^{-3}$)")
    ax[1].legend(fontsize=7)
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.15, top=0.95, wspace=0.28)
    fs.save(fig, os.path.join(out, "fig_t2_extraction"))
    plt.close(fig)
    return rows


def write_modes(fname, head, n2, r, dr, shell):
    with open(fname, "w") as fp:
        fp.write("# time %.17e  lockstep time %.17e  alpha epoch %d\n" % (head["time"],
                                                                           head["time"], 0))
        fp.write("# phi_b %.17e  Pi_b %.17e  ln_a %.17e\n" % (3.0, -0.05, np.log(head["a"])))
        fp.write("# H %.17e  a %.17e  eps1 %.17e  eps2 %.17e\n" % (head["H"], head["a"], 0.01,
                                                                   -0.02))
        fp.write("# kick factors: Pi %.17e  Khat %.17e  At %.17e\n" % (-0.06, -0.01, 0.01))
        fp.write("# n2  Re_R  Im_R  Re_dR  Im_dR  Re_shell  Im_shell\n")
        for i in range(n2.size):
            fp.write("%d %.17e %.17e %.17e %.17e %.17e %.17e\n" % (
                n2[i], r[i].real, r[i].imag, dr[i].real, dr[i].imag, shell[i].real,
                shell[i].imag))


def t3(out):
    N, L = 32, 2 * np.pi * np.exp(1.5)
    lat = sfa.Lattice(N, L, 64)
    s, inv = lat.shells()
    rng = np.random.default_rng(3)
    rq = 1e-4 * (1 + 0.3j) * np.sqrt(s) ** -1.5
    drq = rng.standard_normal(s.size) * 1e-5 + 0j
    head = dict(time=4.0, a=np.exp(4.0), H=0.9)
    fn = os.path.join(out, "t3.sf.00003.modes")
    write_modes(fn, head, s, rq, drq, 0.0 * rq)
    modes = sfa.read_modes(fn)
    hd = modes["head"]
    hok = (hd["a"] == head["a"] and hd["H"] == head["H"] and hd["eps1"] == 0.01 and
           hd["time"] == 4.0 and hd["kick_At"] == 0.01 and hd["Pi_b"] == -0.05)
    err_r = np.abs(modes["R"] - rq).max() / np.abs(rq).max()
    record("T3a", ".modes record parsed (header and rows)", err_r, "<= 1e-16 and header ok",
           err_r <= 1e-16 and hok)
    alpha = lat.alpha(seed=20261115)
    cexp = sfa.expected_coefficients(lat, modes, alpha)
    delta = 1e-3 * lat.n[:, 0] - 2e-4j * lat.n[:, 2]
    f = lat.synthesise(cexp * (1 + delta))
    ratio = sfa.per_mode_ratio(lat.coefficients(f), cexp, floor=1e-30)
    m = np.isfinite(ratio)
    err = np.abs(ratio[m] - delta[m]).max()
    w = sfa.window(lat.k, head["a"], head["H"])
    record("T3b", "planted per-mode deviations recovered (modes with W > 1e-12)",
           float(np.abs(ratio[w > 1e-12] - delta[w > 1e-12]).max()), "<= 1e-10",
           np.abs(ratio[w > 1e-12] - delta[w > 1e-12]).max() <= 1e-10, n_modes=int(m.sum()))
    # drift of c (1 + b e^{-2N}) between N = 5 and 6
    c0 = cexp[:10] + 1e-30
    b = 0.3
    ca, cb = c0 * (1 + b * np.exp(-10.0)), c0 * (1 + b * np.exp(-12.0))
    dr_ = sfa.drift(ca, cb, 5.0, 6.0)
    exact = 2 * (np.log1p(b * np.exp(-12.0)) - np.log1p(b * np.exp(-10.0)))
    record("T3c", "drift of ln|c|^2 per e-fold", float(np.abs(dr_ - exact).max()), "<= 1e-12",
           np.abs(dr_ - exact).max() <= 1e-12)
    os.remove(fn)
    fs.use_style()
    fig, ax = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH, 3.0))
    sel = w > 1e-12
    ax.plot(delta.real[sel], ratio.real[sel], ".", color=fs.PAL["red"], ms=3, label="Re")
    ax.plot(delta.imag[sel], ratio.imag[sel], ".", color=fs.PAL["blue"], ms=3, label="Im")
    xx = np.linspace(-0.01, 0.01, 3)
    ax.plot(xx, xx, **fs.GUIDE, label="planted")
    ax.set_xlabel(r"planted $\delta_n$")
    ax.set_ylabel(r"$c_n/(L^{-3/2}W_qR_q\alpha_n)-1$")
    ax.legend(fontsize=7)
    fig.subplots_adjust(left=0.2, right=0.96, bottom=0.16, top=0.95)
    fs.save(fig, os.path.join(out, "fig_t3_permode"))
    plt.close(fig)


def t4(out):
    N, L = 64, 2 * np.pi
    lat = sfa.Lattice(N, L, 256)
    d0 = 2.1e-9
    amp = np.sqrt(2 * np.pi ** 2 * d0 / lat.k ** 3) * L ** -1.5
    rng = np.random.default_rng(4)
    unit = np.exp(2j * np.pi * rng.random(lat.n2.size))
    k, dl, cnt = sfa.shell_spectrum(lat, lat.coefficients(lat.synthesise(amp * unit)))
    e = np.abs(dl / d0 - 1).max()
    record("T4a", "spectrum of unit-modulus amplitudes, Delta0 in every shell", e, "<= 1e-12",
           e <= 1e-12)
    alpha = lat.alpha(seed=20261115)
    k, dg, cnt = sfa.shell_spectrum(lat, lat.coefficients(lat.synthesise(amp * alpha)))
    # per shell M <|alpha|^2> ~ Gamma(M, 1): pooled mean over all modes
    pooled = np.sum(dg / d0 * cnt) / cnt.sum()
    z = (pooled - 1) * np.sqrt(cnt.sum())
    record("T4b", "Gaussian amplitudes of the code's keys: pooled Delta/Delta0 - 1 in sigma", abs(z),
           "|z| <= 4", abs(z) <= 4, pooled=float(pooled), modes=int(cnt.sum()))
    fs.use_style()
    fig, ax = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH, 3.0))
    ax.semilogx(k, dg / d0, ".", color=fs.PAL["red"], label="Gaussian draw (code keys)")
    fs.band(ax, k, 1 - 1 / np.sqrt(cnt), 1 + 1 / np.sqrt(cnt), fs.PAL["blue"])
    ax.semilogx(k, dl / d0, "-", color=fs.PAL["blue"], label="unit modulus")
    ax.set_xlabel("$k$")
    ax.set_ylabel(r"$\Delta(k)/\Delta_0$ per shell")
    ax.legend(fontsize=7)
    fig.subplots_adjust(left=0.18, right=0.96, bottom=0.16, top=0.95)
    fs.save(fig, os.path.join(out, "fig_t4_spectrum"))
    plt.close(fig)


def t5(out):
    N, L = 32, 1.0
    h = L / N
    x = (np.arange(N) + 0.5) * h
    X, Y, Z = np.meshgrid(x, x, x, indexing="ij")
    errs = []
    for nghost in (2, 3, 4):
        for m in (1, 3, 7):
            kk = 2 * np.pi * m / L
            f = np.sin(kk * X + 0.3)
            dnum = sfa.d1(f, h, 0, nghost)
            q = nsf.d1_symbol(kk * h, nghost) / h
            errs.append(np.abs(dnum - q * np.cos(kk * X + 0.3)).max() / q)
    e = max(errs)
    record("T5a", "first difference against the stencil symbol (orders 2, 4, 6)", e,
           "<= 1e-13", e <= 1e-13)
    rng = np.random.default_rng(5)
    lat = sfa.Lattice(N, L, 36)
    ric, _ = random_field(lat, rng, 1e-3)
    kf = -3.0 + random_field(lat, rng, 1e-4)[0]
    ef = 3.0 / (8 * np.pi) + random_field(lat, rng, 1e-4)[0]
    d = dict(K=kf, E=ef, H=ric + (2 / 3) * kf ** 2 - 16 * np.pi * ef, h=h)
    hn = sfa.ham_norm_cells(d)
    exact = np.abs(ric) + (2 / 3) * kf ** 2 + 16 * np.pi * np.abs(ef)
    e = np.abs(hn / exact - 1).max()
    record("T5b", "[H] per cell from H, K, E with a known Ricci scalar", e, "<= 1e-13",
           e <= 1e-13)
    kk = 2 * np.pi * 2 / L
    A, B, pi0 = 1e-3, 2e-4, -0.05
    d = dict(phi=3 + A * np.sin(kk * X), K=-3 + B * np.cos(kk * X), Pi=pi0 + 0 * X, h=h)
    q = nsf.d1_symbol(kk * h, 4) / h
    exact = np.abs((2 / 3) * B * q * np.sin(kk * X)) + np.abs(8 * np.pi * pi0 * A * q * np.cos(kk * X))
    mn = sfa.mom_norm_cells(d)
    e = np.abs(mn - exact).max() / exact.max()
    record("T5c", "[M] of a plane wave against its closed form", e, "<= 1e-12", e <= 1e-12)
    fs.use_style()
    fig, ax = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH, 3.0))
    ax.plot(x, exact[:, 0, 0], color=fs.PAL["blue"], label="closed form")
    ax.plot(x, mn[:, 0, 0], "--", color=fs.PAL["red"], label="estimator")
    ax.set_xlabel("$x$")
    ax.set_ylabel(r"$[\mathcal{M}]$ of the plane wave")
    ax.legend(fontsize=7)
    fig.subplots_adjust(left=0.2, right=0.96, bottom=0.16, top=0.95)
    fs.save(fig, os.path.join(out, "fig_t5_momentum_norm"))
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    t1(a.out)
    rows = t2(a.out)
    t3(a.out)
    t4(a.out)
    t5(a.out)
    with open(os.path.join(a.out, "test_sfa.json"), "w") as f:
        json.dump(dict(results=RESULTS, t2_rows=rows.tolist()), f, indent=1, default=float)
    nfail = sum(not r["passed"] for r in RESULTS)
    print(f"{len(RESULTS)} tests, {nfail} failed")
    sys.exit(1 if nfail else 0)


if __name__ == "__main__":
    main()
