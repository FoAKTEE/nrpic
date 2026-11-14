"""Checks of spectrum.py and random_field.py; one PASS/FAIL line per check.

    python3 test_spectrum.py [--figdir DIR] [--seed S]

With --figdir the diagnostic figures (project style, python/nrpic/figstyle.py) are written
to DIR as PDF and PNG. Exit status 1 if any check fails. Runs in about 10 s on one core.
"""
import argparse
import os
import sys

import numpy as np
from scipy import integrate, special

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cosmo_id as cid                     # noqa: E402
import random_field as rf                  # noqa: E402
import spectrum as sp                      # noqa: E402

RESULTS = []


def check(name, ok, msg):
    print(f"{'PASS' if ok else 'FAIL'}  {name}: {msg}", flush=True)
    RESULTS.append(bool(ok))


def info(name, msg):
    print(f"INFO  {name}: {msg}", flush=True)


def rel(a, b):
    return np.abs(np.asarray(a)/np.asarray(b) - 1.0)


# ---------------------------------------------------------------------------------------
def test_transfer(P, fig):
    om, ob, h = P["omega_m"], P["omega_b"], P["h"]
    k = np.logspace(-3, 0, 3001)
    te = sp.transfer_eh(k, om, ob, h, wiggles=True)
    tn = sp.transfer_eh(k, om, ob, h, wiggles=False)
    tb = sp.transfer_bbks(k, om, ob, h)
    d = rel(tn, tb)
    check("EH no-wiggle vs BBKS (Sugiyama Gamma), 1e-3<k<1",
          d.max() < 0.10, f"max |T_nw/T_BBKS - 1| = {d.max():.4f} at k = {k[d.argmax()]:.3g}")
    d = rel(te, tn)
    check("EH full vs EH no-wiggle, 1e-3<k<1", d.max() < 0.10,
          f"max |T/T_nw - 1| = {d.max():.4f} at k = {k[d.argmax()]:.3g} "
          f"(range {(te/tn - 1).min():+.4f} .. {(te/tn - 1).max():+.4f})")
    ks = np.array([1e-5, 1e-4])
    vals = {"EH": sp.transfer_eh(ks, om, ob, h), "EH-nw": sp.transfer_eh(ks, om, ob, h,
                                                                        wiggles=False),
            "BBKS": sp.transfer_bbks(ks, om, ob, h)}
    worst = max(abs(v[0] - 1.0) for v in vals.values())
    check("T -> 1 at small k", worst < 1e-3 and all(abs(v[1] - 1.0) < 2e-3
                                                     for v in vals.values()),
          "1 - T(1e-5, 1e-4) = " + ", ".join(f"{n} {1 - v[0]:.1e} {1 - v[1]:.1e}"
                                            for n, v in vals.items()))
    fig["transfer"] = (k, te, tn, tb)


def test_normalisation(P, G):
    for name, par in (("Planck18", P), ("GRAMSES", G)):
        s8 = float(sp.sigma_r(8.0, 0.0, par))
        check(f"sigma8 normalisation ({name}), sigma_r on the log grid",
              abs(s8/par["sigma8"] - 1.0) < 1e-4,
              f"sigma_r(8) = {s8:.6f}, input {par['sigma8']}")
    # independent adaptive quadrature of the same spectrum
    w = sp.tophat_window

    def integrand(lnk):
        kk = np.exp(lnk)
        return kk**3*sp.linear_power(kk, 0.0, P)/(2*np.pi**2)*w(8.0*kk)**2

    s2, err = integrate.quad(integrand, np.log(1e-6), np.log(1e4), limit=2000,
                             epsabs=0.0, epsrel=1e-10)
    s8 = np.sqrt(s2)
    check("sigma8 normalisation (Planck18), adaptive quad over ln k",
          abs(s8/P["sigma8"] - 1.0) < 1e-4,
          f"sigma8 = {s8:.7f} (relative {s8/P['sigma8'] - 1:+.1e}), input {P['sigma8']}")
    q = dict(P, sigma8=None)
    s8a = float(sp.sigma_r(8.0, 0.0, q))
    info("sigma8 from A_s (Planck18, EH, massless neutrinos)",
         f"{s8a:.4f} for A_s = {P['A_s']:.4e}, n_s = {P['n_s']}; Planck quotes "
         f"{P['sigma8']} ({s8a/P['sigma8'] - 1:+.1%})")
    for z in (0.0, 49.0, 99.0, 1000.0):
        info(f"P(k, z={z:g}) Planck18 at k = 0.0245, 0.045, 0.1 h/Mpc",
             " ".join(f"{v:.4g}" for v in sp.linear_power(np.array([0.0245, 0.045, 0.1]),
                                                           z, P)) + " (Mpc/h)^3")


def test_growth(P, fig):
    a = np.logspace(-4, 1, 60)
    d = np.abs(sp.growth_factor(a, 1.0, 0.0)/a - 1.0).max()
    f = np.abs(sp.growth_rate(a, 1.0, 0.0) - 1.0).max()
    check("EdS growth D = a, f = 1 (1e-4 < a < 10)", d < 1e-14 and f < 1e-14,
          f"max |D/a - 1| = {d:.1e}, max |f - 1| = {f:.1e}")

    om, ol = P["omega_m"], P["omega_l"]
    d1 = float(sp.growth_factor(1.0, om, ol))
    oma, ola = om, ol
    cpt = 2.5*oma/(oma**(4/7) - ola + (1 + oma/2)*(1 + ola/70))
    check("D(a=1)/a vs Carroll-Press-Turner (Planck18)", abs(d1/cpt - 1) < 0.01,
          f"D(1) = {d1:.5f}, CPT {cpt:.5f}, ratio - 1 = {d1/cpt - 1:+.2e}")

    aa = np.logspace(-3, 0, 200)
    fr = sp.growth_rate(aa, om, ol)
    lin = sp.omega_m_of_a(aa, om, ol)**0.55
    dr = rel(fr, lin)
    check("growth rate vs Omega_m(a)^0.55 (Planck18, 1e-3 < a < 1)", dr.max() < 0.01,
          f"max |f/Om^0.55 - 1| = {dr.max():.2e} at a = {aa[dr.argmax()]:.3g}; "
          f"f(a=1) = {fr[-1]:.5f} vs {lin[-1]:.5f}")

    # closed form for flat LCDM and adaptive quadrature for curved models
    hyp = a*special.hyp2f1(1/3, 1, 11/6, -a**3*ol/om)
    dh = rel(sp.growth_factor(a, om, ol), hyp).max()
    worst = 0.0
    for omx, olx in ((0.3, 0.0), (0.3, 0.5), (0.5, 0.7), (1.2, 0.0)):
        for ax in (0.01, 0.3, 1.0, 3.0):
            gx = lambda u: omx + (1 - omx - olx)*u + olx*u**3   # noqa: E731
            if gx(np.linspace(0, ax, 200)).min() <= 0:
                continue
            # QAWS rule for the weight u^(3/2); plain quad stops at its default epsabs
            I, _ = integrate.quad(lambda u: gx(u)**-1.5, 0, ax, weight="alg",
                                  wvar=(1.5, 0.0), epsabs=0.0, epsrel=1e-13)
            ref = 2.5*omx*np.sqrt(gx(ax))/ax**1.5*I
            worst = max(worst, abs(float(sp.growth_factor(ax, omx, olx))/ref - 1))
    check("growth quadrature vs 2F1 (flat) and scipy quad (curved)",
          dh < 1e-12 and worst < 1e-10,
          f"max rel. error {dh:.1e} (flat LCDM, 1e-4<a<10), {worst:.1e} "
          f"(Om, OL) = (0.3,0), (0.3,0.5), (0.5,0.7), (1.2,0)")
    eps = 1e-5
    fd = (np.log(sp.growth_factor(aa*np.exp(eps), 0.3, 0.5))
          - np.log(sp.growth_factor(aa*np.exp(-eps), 0.3, 0.5)))/(2*eps)
    df = np.abs(fd - sp.growth_rate(aa, 0.3, 0.5)).max()
    check("growth_rate vs numerical d ln D/d ln a (Om=0.3, OL=0.5)", df < 1e-8,
          f"max difference {df:.1e}")
    fig["growth"] = (aa, sp.growth_factor(aa, om, ol)/aa, fr, lin)


# ---------------------------------------------------------------------------------------
def test_field(P, seed, fig):
    L, n = 256.0, 128
    pk = lambda k: sp.linear_power(k, 0.0, P)              # noqa: E731
    delta = rf.gaussian_field(n, L, pk, seed)

    k, pm, nm = rf.measure_power(delta, L)
    ke, pe, se, ne = rf.expected_power(n, L, pk)
    pull = (pm - pe)/se
    chi2 = float(np.mean(pull**2))
    check(f"measured P vs input, {n}^3, L = {L:g} Mpc/h, {len(k)} bins of width k_f",
          0.5 < chi2 < 1.6 and np.array_equal(nm, ne),
          f"reduced chi^2 = {chi2:.3f} (nu = {len(k)}), max |pull| = "
          f"{np.abs(pull).max():.2f}, mean pull = {pull.mean():+.3f}")
    rms = delta.std()
    check("mean zero", abs(delta.mean()) < 1e-14*rms,
          f"<delta> = {delta.mean():.1e}, rms {rms:.3f}")

    F = rf._mesh_coefficients(n, L, pk, seed, half=False)
    z = np.fft.ifftn(F)
    herm = np.abs(F - np.conj(np.roll(F[::-1, ::-1, ::-1], 1, axis=(0, 1, 2)))).max()
    imag = np.abs(z.imag).max()/np.abs(z.real).max()
    same = np.abs(z.real - delta).max()/np.abs(delta).max()
    check("field real (complex inverse FFT of all n^3 modes, Nyquist planes included)",
          imag < 1e-13 and herm < 1e-13*np.abs(F).max() and same < 1e-13,
          f"max|Im|/max|Re| = {imag:.1e}, max|F(-k) - F*(k)|/max|F| = "
          f"{herm/np.abs(F).max():.1e}, rfft path vs full {same:.1e}")

    c = rf.fourier_coefficients(delta, L)
    cm = rf.gaussian_modes(n, L, pk, seed)
    i1 = np.fft.fftfreq(n)*n
    ix, iy, iz = np.meshgrid(i1, i1, i1, indexing="ij")
    kk = 2*np.pi/L*np.sqrt(ix**2 + iy**2 + iz**2)
    nyq = (np.abs(ix) == n//2) | (np.abs(iy) == n//2) | (np.abs(iz) == n//2)
    r = np.abs(c)**2*L**3/np.where(kk > 0, pk(np.where(kk > 0, kk, 1.0)), 1.0)
    m_nyq, m_in = r[nyq].mean(), r[~nyq & (kk > 0)].mean()
    e_nyq, e_in = 1/np.sqrt(nyq.sum()/2), 1/np.sqrt((~nyq).sum()/2)
    check("<|delta_k|^2> L^3/P = 1 on and off the Nyquist planes",
          abs(m_nyq - 1) < 4*e_nyq and abs(m_in - 1) < 4*e_in
          and np.abs(c - cm).max() < 1e-13*np.abs(cm).max(),
          f"Nyquist planes {m_nyq:.4f} (+-{e_nyq:.4f}, {nyq.sum()} modes), interior "
          f"{m_in:.4f} (+-{e_in:.4f}); gaussian_modes vs measured coefficients "
          f"{np.abs(c - cm).max()/np.abs(cm).max():.1e}")

    # resolution independence: common modes of 64^3 and 128^3
    d64 = rf.gaussian_field(64, L, pk, seed)
    c64 = rf.fourier_coefficients(d64, L)
    v = np.arange(-31, 32)
    A = c64[np.ix_(v % 64, v % 64, v % 64)]
    B = c[np.ix_(v % n, v % n, v % n)]
    dmax = np.abs(A - B).max()/np.abs(B).max()
    x64 = (np.arange(64) + 0.5)*L/64
    check("same seed, 64^3 vs 128^3: Fourier coefficients of the modes |n_i| <= 31",
          dmax < 1e-12, f"max |delta_k(64) - delta_k(128)| / max |delta_k| = {dmax:.1e} "
          f"over {A.size} modes")
    d2 = rf.gaussian_field(n, L, pk, seed + 1)
    c2 = rf.fourier_coefficients(d2, L)[np.ix_(v % n, v % n, v % n)]
    info("different seed, same modes", f"max |difference| / max = "
         f"{np.abs(c2 - B).max()/np.abs(B).max():.2f} (control)")

    # cut-offs
    kc = 2*np.pi/40.0                       # C256 of arXiv:1904.07841
    ds = rf.gaussian_field(n, L, pk, seed, kcut=kc, cut="sharp")
    cs = rf.fourier_coefficients(ds, L)
    above, below = kk > kc, (kk > 0) & (kk <= kc)
    pa = (np.abs(cs[above])**2).max()
    pb = (np.abs(cs[below])**2).mean()
    keep = np.abs(cs[below] - c[below]).max()/np.abs(c[below]).max()
    check(f"sharp cut-off kcut = 2pi/40 = {kc:.4f} h/Mpc removes all power above kcut",
          pa < 1e-28*pb and keep < 1e-12,
          f"max |delta_k|^2 above / mean below = {pa/pb:.1e}; modes kept equal the uncut "
          f"field to {keep:.1e} ({below.sum()} modes below kcut)")
    kg = 0.2
    dg = rf.gaussian_field(n, L, pk, seed, kcut=kg, cut="gaussian")
    pkg = lambda q: pk(q)*np.exp(-(q/kg)**2)      # noqa: E731
    kg_, pg, _ = rf.measure_power(dg, L)
    _, pge, sge, _ = rf.expected_power(n, L, pkg)
    use = pge > 1e-12*pge.max()
    chig = float(np.mean(((pg - pge)/sge)[use]**2))
    cg = rf.fourier_coefficients(dg, L)
    filt = np.abs(cg[kk > 0] - c[kk > 0]*np.exp(-0.5*(kk[kk > 0]/kg)**2)).max()
    check(f"gaussian cut-off kcut = {kg} h/Mpc: P exp(-k^2/kcut^2)",
          0.5 < chig < 1.6 and filt < 1e-13*np.abs(c).max(),
          f"reduced chi^2 = {chig:.3f} ({use.sum()} bins); field = uncut field x "
          f"exp(-k^2/(2 kcut^2)) to {filt/np.abs(c).max():.1e}")

    # deconvolution operator
    worst = 0.0
    k0, p0, _ = rf.measure_power(d64, L)
    for p in (1, 2, 3):
        Fw = np.fft.rfftn(d64)*np.sqrt(rf.bspline_window(64, L, p))
        _, pw, _ = rf.measure_power(np.fft.irfftn(Fw, s=(64,)*3, axes=(0, 1, 2)), L,
                                    deconvolve=p)
        worst = max(worst, rel(pw, p0).max())
    check("deconvolve = 1, 2, 3 undoes a sinc^(p+1) window", worst < 1e-10,
          f"max relative difference {worst:.1e}")
    fig["power"] = dict(k=k, pm=pm, pe=pe, se=se, pull=pull, k64=k0, p64=p0,
                        ks=rf.measure_power(ds, L)[:2], kg=(kg_, pg, pge), kc=kc, kgc=kg)
    fig["slices"] = (d64, delta, ds, L)


def test_zeldovich(fig):
    L, n, amp = 100.0, 32, 0.3
    x = (np.arange(n) + 0.5)*L/n
    X = np.meshgrid(x, x, x, indexing="ij")
    worst_psi = worst_j = 0.0
    for m in ((1, 0, 0), (1, 2, 3), (0, 5, -2)):
        kv = 2*np.pi/L*np.array(m, float)
        ph = kv[0]*X[0] + kv[1]*X[1] + kv[2]*X[2]
        delta = amp*np.sin(ph)
        psi = rf.zeldovich(delta, L)
        k2 = (kv*kv).sum()
        for i in range(3):
            ana = amp*kv[i]*np.cos(ph)/k2
            worst_psi = max(worst_psi, np.abs(psi[i] - ana).max()/(amp/np.sqrt(k2)))
        J = rf.displacement_jacobian(delta, L)
        worst_j = max(worst_j, np.abs(J - (1 - delta)).max())
    check("Zel'dovich displacement of plane waves = A k cos(k.x)/k^2",
          worst_psi < 1e-13, f"max error / (A/k) = {worst_psi:.1e}, k = (1,0,0), (1,2,3), "
          "(0,5,-2) x 2pi/L")
    check("Jacobian of plane waves = 1 - delta (A = 0.3)", worst_j < 1e-13,
          f"max |J - (1 - delta)| = {worst_j:.1e}")

    # random field: -div psi = delta when the Nyquist planes are empty; with them, only
    # the Nyquist-plane modes differ (the Torus derivative skips the Nyquist component)
    P = sp.PLANCK18
    pk = lambda k: sp.linear_power(k, 0.0, P)            # noqa: E731
    Ln, nn = 256.0, 64
    tor = cid.Torus(nn, Ln)
    dn = rf.gaussian_field(nn, Ln, pk, 11, zero_nyquist=True)
    psi = rf.zeldovich(dn, Ln)
    div = sum(tor.grad(psi[i])[i] for i in range(3))
    e = np.abs(-div - dn).max()/np.abs(dn).max()
    d = rf.gaussian_field(nn, Ln, pk, 11)
    psi = rf.zeldovich(d, Ln)
    r = rf.fourier_coefficients(-sum(tor.grad(psi[i])[i] for i in range(3)) - d, Ln)
    i1 = np.abs(np.fft.fftfreq(nn)*nn)
    on = ((i1[:, None, None] == nn//2) | (i1[None, :, None] == nn//2)
          | (i1[None, None, :] == nn//2))
    off = np.abs(r[~on]).max()/np.abs(rf.fourier_coefficients(d, Ln)).max()
    check("random field: -div psi = delta (Nyquist planes zero); otherwise only "
          "Nyquist-plane modes differ", e < 1e-13 and off < 1e-13,
          f"max |-div psi - delta| / max |delta| = {e:.1e}; with Nyquist planes, largest "
          f"off-plane difference {off:.1e}, rms of the real-space difference "
          f"{np.sqrt((np.abs(r)**2).sum())/d.std():.3f} rms(delta)")
    J = rf.displacement_jacobian(d, Ln)
    info("random field Jacobian (Planck18 z=0, 64^3, 256 Mpc/h)",
         f"min J = {J.min():.3f} (shell crossing where J < 0), mean J = {J.mean():.4f}")


# ---------------------------------------------------------------------------------------
def figures(fig, outdir):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "python"))
    from nrpic import figstyle as fs
    fs.use_style()
    os.makedirs(outdir, exist_ok=True)
    out = []

    # transfer functions and growth
    k, te, tn, tb = fig["transfer"]
    aa, da, fr, lin = fig["growth"]
    f = plt.figure(figsize=(fs.FULL_WIDTH, 4.6))
    ax1 = fs.inch_axes(f, 0.75, 1.95, 3.1, 2.5)
    ax2 = fs.inch_axes(f, 0.75, 0.45, 3.1, 1.5)
    ax3 = fs.inch_axes(f, 4.75, 1.95, 3.1, 2.5)
    ax4 = fs.inch_axes(f, 4.75, 0.45, 3.1, 1.5)
    ax1.loglog(k, tb, color=fs.PAL["blue"], label="BBKS (Sugiyama)")
    ax1.loglog(k, tn, color=fs.PAL["yellow"], label="EH no-wiggle")
    ax1.loglog(k, te, color=fs.PAL["red"], label="EH full")
    ax1.set_ylabel("$T(k)$")
    ax1.legend(loc="lower left")
    ax1.set_xticklabels([])
    ax2.semilogx(k, te/tn - 1, color=fs.PAL["red"], label="EH full / no-wiggle $-1$")
    ax2.semilogx(k, tn/tb - 1, color=fs.PAL["yellow"], label="no-wiggle / BBKS $-1$")
    ax2.axhline(0, **fs.GUIDE)
    for s in (-0.1, 0.1):
        ax2.axhline(s, **fs.MASK_LINE)
    ax2.set_xlabel("$k$ [$h$/Mpc]", labelpad=-2)
    ax2.set_ylabel("ratio $-1$")
    ax2.legend(loc="lower left", fontsize=8)
    for ax in (ax1, ax2):
        ax.set_xlim(k[0], k[-1])
    ax3.semilogx(aa, da, color=fs.PAL["red"], label="$D(a)/a$")
    ax3.semilogx(aa, fr, color=fs.PAL["red"], ls="--", label="$f$")
    ax3.semilogx(aa, lin, **fs.GUIDE, label=r"$\Omega_m(a)^{0.55}$")
    ax3.set_xticklabels([])
    ax3.legend(loc="lower left")
    ax3.set_ylabel("growth (Planck 2018)")
    ax4.semilogx(aa, fr/lin - 1, color=fs.PAL["red"])
    ax4.axhline(0, **fs.GUIDE)
    ax4.set_xlabel("$a$", labelpad=-2)
    ax4.set_ylabel(r"$f/\Omega_m^{0.55}-1$")
    for ax in (ax3, ax4):
        ax.set_xlim(aa[0], aa[-1])
    out += fs.save(f, os.path.join(outdir, "spectrum_transfer_growth"))
    plt.close(f)

    # measured spectra
    p = fig["power"]
    f = plt.figure(figsize=(fs.FULL_WIDTH, 4.6))
    ax1 = fs.inch_axes(f, 0.8, 1.95, 7.0, 2.5)
    ax2 = fs.inch_axes(f, 0.8, 0.45, 7.0, 1.5)
    fs.band(ax1, p["k"], p["pe"] - p["se"], p["pe"] + p["se"], fs.PAL["blue"])
    ax1.loglog(p["k"], p["pe"], color=fs.PAL["blue"], label="input, mode average")
    ax1.loglog(p["k"], p["pm"], "o", ms=3, color=fs.PAL["red"], label="$128^3$")
    ax1.loglog(p["k64"], p["p64"], "s", ms=3, mfc="none", color=fs.PAL["green"],
               label="$64^3$, same seed")
    ks, ps = p["ks"]
    ax1.loglog(ks, ps, "^", ms=3, color=fs.PAL["orange"],
               label=f"sharp cut $k_c = 2\\pi/40$")
    kg_, pg, pge = p["kg"]
    ax1.loglog(kg_, pg, "v", ms=3, color=fs.PAL["yellow"],
               label=f"Gaussian cut $k_c = {p['kgc']}$")
    ax1.loglog(kg_, pge, **fs.GUIDE)
    ax1.axvline(p["kc"], **fs.MASK_LINE)
    ax1.set_ylim(3e1, 8e4)
    ax1.set_ylabel(r"$P(k)$ [(Mpc/$h$)$^3$]")
    ax1.set_xticklabels([])
    ax1.legend(loc="upper right", ncol=2)
    ax2.semilogx(p["k"], p["pull"], "o", ms=3, color=fs.PAL["red"])
    ax2.axhline(0, **fs.GUIDE)
    for s in (-2, 2):
        ax2.axhline(s, **fs.MASK_LINE)
    ax2.set_ylabel(r"$(P - \bar P)/\sigma$")
    ax2.set_xlabel("$k$ [$h$/Mpc]", labelpad=-2)
    for ax in (ax1, ax2):
        ax.set_xlim(0.02, 1.7)
    out += fs.save(f, os.path.join(outdir, "spectrum_power"))
    plt.close(f)

    # slices
    d64, d128, dsh, L = fig["slices"]
    fig2, axes, cax = fs.slice_mosaic(1, 3, panel=2.1, left=0.6, bottom=0.45,
                                      cbar="right")
    vmax = 3*d128.std()
    for ax, d, t in zip(axes[0], (d64, d128, dsh),
                        ("$64^3$", "$128^3$, same seed", "$128^3$, $k \\leq 2\\pi/40$")):
        im = ax.imshow(d[:, :, d.shape[2]//2].T, origin="lower", extent=(0, L, 0, L),
                       cmap=fs.CMAP["diverging"], vmin=-vmax, vmax=vmax,
                       interpolation="none", rasterized=True)
        ax.text(0.04, 0.95, t, transform=ax.transAxes, va="top", fontsize=9,
                bbox=dict(fc="white", ec="none", alpha=0.7, pad=1.5))
        ax.set_xticks([64, 128, 192])
        ax.set_yticks([64, 128, 192])
    for ax in axes[0][1:]:
        ax.set_yticklabels([])
    axes[0][1].set_xlabel("$x$ [Mpc/$h$]", labelpad=-2)
    axes[0][0].set_ylabel("$y$ [Mpc/$h$]")
    fig2.colorbar(im, cax=cax, label=r"$\delta$ (slice at $z = L/2$)")
    out += fs.save(fig2, os.path.join(outdir, "spectrum_slices"))
    plt.close(fig2)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--figdir", default="")
    ap.add_argument("--seed", type=int, default=1904)
    a = ap.parse_args()
    P, G = sp.PLANCK18, sp.GRAMSES
    fig = {}
    test_transfer(P, fig)
    test_normalisation(P, G)
    test_growth(P, fig)
    test_field(P, a.seed, fig)
    test_zeldovich(fig)
    npass = sum(RESULTS)
    print(f"{npass} of {len(RESULTS)} checks passed")
    if a.figdir:
        for p in figures(fig, a.figdir):
            print("wrote", p)
    sys.exit(0 if npass == len(RESULTS) else 1)


if __name__ == "__main__":
    main()
