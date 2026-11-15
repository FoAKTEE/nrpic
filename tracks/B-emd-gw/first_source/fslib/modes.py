"""Box-mode amplitudes and per-dump diagnostics of the crossed-wave runs.

Mode amplitude. For a real field f = c cos(K.x) + s sin(K.x) on the cell-centred mesh of
gw_diag (x = xmin + (n + 1/2) dx), the rfft coefficient is F(K) = (N/2)(c - i s) e^(i K.x0),
x0 = xmin + dx/2, N the number of cells; amp(F, K) returns c - i s.

Polarizations at K1 = (k, k, 0): e+ = u u - z z, ex = u z + z u, u = (1, -1, 0)/sqrt 2;
at K2 = (k, -k, 0): u = (1, 1, 0)/sqrt 2. h_+ = (1/2) e+_ij h_ij. (gw_diag's pol_basis has
the opposite sign of e+ at K1: there u = -z, v = (-1, 1, 0)/sqrt 2.)
"""
import numpy as np

from gwdiag import tt, readers, weyl

from . import gauge

S2 = 1.0 / np.sqrt(2.0)
_Z = np.array([0.0, 0.0, 1.0])
BASIS = {}
for name, m, u in (("K1", (1, 1, 0), np.array([S2, -S2, 0.0])),
                   ("K2", (1, -1, 0), np.array([S2, S2, 0.0]))):
    BASIS[name] = (m, np.outer(u, u) - np.outer(_Z, _Z), np.outer(u, _Z) + np.outer(_Z, u))


def amp(F, grid, m):
    """c - i s of the mode with integer numbers m = (mx >= 0, my, mz) from rfft coefficients
    F (..., nz, ny, nx//2+1)."""
    mx, my, mz = m
    K = np.array([2 * np.pi * m[a] / grid.L[a] for a in range(3)])
    x0 = np.array([grid.xmin[a] + 0.5 * grid.dx[a] for a in range(3)])
    v = F[..., mz % grid.n[2], my % grid.n[1], mx]
    return 2.0 * v * np.exp(-1j * float(K @ x0)) / grid.ncell


def pol_amps(T, grid):
    """{K1: (h_+, h_x), K2: (...)} complex amplitudes c - i s from TT Fourier coefficients."""
    out = {}
    for name, (m, ep, ex) in BASIS.items():
        A = amp(T, grid, m)                   # (3, 3) complex
        out[name] = (0.5 * np.einsum("ab,ab->", ep, A), 0.5 * np.einsum("ab,ab->", ex, A))
    return out


def ms_fourier(F, grid, exclude_k0=True):
    """Volume mean of f_ij f_ij from rfft coefficients (Parseval)."""
    P = tt.power_tensor(F, grid)
    if exclude_k0:
        P = P.copy()
        P[0, 0, 0] = 0.0
    return float(P.sum())


def box_mode_power(F, grid):
    """Mean-square contribution of the four modes (+-k, +-k, 0)."""
    P = tt.power_tensor(F, grid)
    return float(P[0, 1, 1] + P[0, grid.n[1] - 1, 1])


def load(path):
    """(time, grid, chi, gt, At, trK, alpha, beta, d) from a rst or a z4c bin dump."""
    if path.endswith(".rst"):
        d = readers.read_rst(path)
    else:
        d = readers.read_bin(path)
        for n in list(d["variables"]):
            if n.startswith("z4c_"):
                d[n[4:]] = d[n]
        d["chi_psi_power"] = float(d["params"].get("z4c", {}).get("chi_psi_power", "-4.0"))
    chi, gt, At, trK, alpha, beta = readers.z4c_tensors(d)
    return d["time"], d["grid"], chi, gt, At, trK, alpha, beta, d


def analyse(path, with_gauge=True, with_weyl=False, weyl_order=6):
    t, g, chi, gt, At, trK, alpha, beta, d = load(path)
    I = np.eye(3)[:, :, None, None, None]
    h = gt - I
    htf = gauge.traceless(h)
    Fh = tt.tensor_rfft(htf)
    Th = tt.lambda_apply(Fh, tt._khat(g)[2])
    Th[:, :, 0, 0, 0] = 0.0
    Th[:, :, g.nyquist_mask(real=True)] = 0.0
    FA = tt.tensor_rfft(gauge.traceless(At))
    TA = tt.lambda_apply(FA, tt._khat(g)[2])
    TA[:, :, 0, 0, 0] = 0.0
    TA[:, :, g.nyquist_mask(real=True)] = 0.0
    r = {"time": t, "cycle": d.get("cycle"), "a": float(np.mean(chi) ** -0.5),
         "alpha_mean": float(alpha.mean()), "beta_rms": float(np.sqrt((beta ** 2).sum(axis=0).mean()))}
    ms_tf = ms_fourier(Fh, g)
    ms_tt = ms_fourier(Th, g)
    r["rms_traceless"] = np.sqrt(ms_tf)
    r["rms_TT"] = np.sqrt(ms_tt)
    r["rms_nonTT"] = np.sqrt(max(ms_tf - ms_tt, 0.0))
    r["box_mode_fraction"] = box_mode_power(Th, g) / ms_tt if ms_tt > 0 else None
    # largest TT mode amplitude anywhere (null test): 2 |T_ij| / N, component norm
    nrm = np.sqrt((np.abs(Th) ** 2).sum(axis=(0, 1))) * 2.0 / g.ncell
    r["max_TT_mode"] = float(nrm.max())
    nrmA = np.sqrt((np.abs(TA) ** 2).sum(axis=(0, 1))) * 2.0 / g.ncell
    r["max_TT_mode_A"] = float(nrmA.max())
    r["rms_traceless_A"] = np.sqrt(ms_fourier(FA, g))
    r["rms_TT_A"] = np.sqrt(ms_fourier(TA, g))
    # energies of the TT part (G = 1): rho_kin = <(d_tau h)^2>/(64 pi), d_tau h = -2 Lambda A;
    # rho_grad = chi_bar <|grad h|^2>/(64 pi); the background density 3 H^2/(8 pi), H = -<trK>/3
    kk2 = (g.kvec(real=True) ** 2).sum(axis=0)
    chib = float(np.mean(chi))
    r["rho_kin"] = 4.0 * ms_fourier(TA, g) / (64 * np.pi)
    r["rho_grad"] = chib * float((kk2 * tt.power_tensor(Th, g)).sum()) / (64 * np.pi)
    r["rho_bar"] = 3.0 * (float(np.mean(trK)) / 3.0) ** 2 / (8 * np.pi)
    # homogeneous traceless part (Bianchi-I-like shear of the box)
    h0 = htf.mean(axis=(-3, -2, -1))
    r["k0_traceless_norm"] = float(np.sqrt((h0 ** 2).sum()))
    # z dependence
    r["z_dependence"] = float(np.abs(htf - htf.mean(axis=-3, keepdims=True)).max())
    for key, T in (("h", Th), ("hdot", -2.0 * TA)):
        pa = pol_amps(T, g)
        for K, (hp, hx) in pa.items():
            r[f"{key}_{K}_plus"] = [float(hp.real), float(hp.imag)]
            r[f"{key}_{K}_cross"] = [float(hx.real), float(hx.imag)]
    if with_gauge:
        G, parts = gauge.gauge_piece(h, g, return_parts=True)
        Gh = parts["G_hat"]
        r["rms_G"] = np.sqrt(ms_fourier(Gh, g))
        r["rms_TT_minus_G"] = np.sqrt(ms_fourier(Th - Gh, g))
        r["rms_xi"] = float(np.sqrt((parts["xi"] ** 2).sum(axis=0).mean()))
        pa = pol_amps(Gh, g)
        for K, (hp, hx) in pa.items():
            r[f"G_{K}_plus"] = [float(hp.real), float(hp.imag)]
            r[f"G_{K}_cross"] = [float(hx.real), float(hx.imag)]
        # total piece with the cross terms of xi with the TT and homogeneous parts of h
        A = htf - gauge.nonTT_traceless(h, g)
        Gx = gauge.gauge_piece_A(h, A, g)
        Gth = Gh + tt.tensor_rfft(Gx)
        r["rms_Gtot"] = np.sqrt(ms_fourier(Gth, g))
        r["rms_TT_minus_Gtot"] = np.sqrt(ms_fourier(Th - Gth, g))
        pa = pol_amps(Gth, g)
        for K, (hp, hx) in pa.items():
            r[f"Gtot_{K}_plus"] = [float(hp.real), float(hp.imag)]
            r[f"Gtot_{K}_cross"] = [float(hx.real), float(hx.imag)]
        r["k0_traceless"] = [float(v) for v in np.diag(h0)]
        Gh_used = Gth
        r["box_mode_fraction_corrected"] = (box_mode_power(Th - Gh_used, g) / ms_fourier(Th - Gh_used, g)
                                            if ms_fourier(Th - Gh_used, g) > 0 else None)
        GA = gauge.gauge_piece_A(h, gauge.traceless(At), g)
        GAh = tt.tensor_rfft(GA)
        r["rms_GA"] = np.sqrt(ms_fourier(GAh, g))
        r["rms_TT_A_minus_GA"] = np.sqrt(ms_fourier(TA - GAh, g))
        r["rho_kin_corrected"] = 4.0 * ms_fourier(TA - GAh, g) / (64 * np.pi)
        r["rho_grad_corrected"] = chib * float((kk2 * tt.power_tensor(Th - Gth, g)).sum()) / (64 * np.pi)
        pa = pol_amps(-2.0 * GAh, g)
        for K, (hp, hx) in pa.items():
            r[f"GA_{K}_plus"] = [float(hp.real), float(hp.imag)]       # in units of hdot = -2 A
            r[f"GA_{K}_cross"] = [float(hx.real), float(hx.imag)]
    if with_weyl:
        gamma, K, _, _ = readers.z4c_to_adm(d)
        E, B = weyl.electric_magnetic(gamma, K, g, order=weyl_order)
        FB = tt.tensor_rfft(B)
        FE = tt.tensor_rfft(gauge.traceless(E))
        kh = tt._khat(g)[2]
        TB = tt.lambda_apply(FB, kh)
        TE = tt.lambda_apply(FE, kh)
        r["rms_B"] = np.sqrt(ms_fourier(FB, g))
        r["rms_E"] = np.sqrt(ms_fourier(FE, g))
        r["rms_LambdaB"] = np.sqrt(ms_fourier(TB, g))
        r["rms_LambdaE"] = np.sqrt(ms_fourier(TE, g))
        for key, T in (("B", TB), ("E", TE), ("Bfull", FB)):
            pa = pol_amps(T, g)
            for Kn, (hp, hx) in pa.items():
                r[f"{key}_{Kn}_plus"] = [float(hp.real), float(hp.imag)]
                r[f"{key}_{Kn}_cross"] = [float(hx.real), float(hx.imag)]
    return r
