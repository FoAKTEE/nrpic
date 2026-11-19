#!/usr/bin/env python3
"""P11b' of JOURNAL.md: prediction of the box-mode TT amplitudes of the jittered-lattice null
from its initial data, before the card run.

    python3 null_prediction.py <ic dir> [<ic dir> ...]       (output: $NRPIC_RUN_DIR)

For each initial-data directory (fields.bin of make_east.py or make_waves.py) the potential
Psi = (1 - psi^4)/2 (the dictionary psi^4 = 1 - 2 psi_N of make_east.py) is split into the
x-wave part Psi_x (mean over y and z, mean removed), the y-wave part Psi_y (mean over x and z)
and the rest Psi_n (for the jittered null: the noise; Psi_y is then part of the noise too and
is also kept in Psi_n). The quasi-static second-order strain of the weak-field equation
(fslib/reference.py) h = (20/3) Lambda[d_i Phi d_j Phi]/|K|^2 is evaluated, with spectral
derivatives, for the pieces cross = 2 sym(d Psi_x d Psi_n) and nn = d Psi_n d Psi_n, and its
+ and x amplitudes at K1 = (k, k, 0) and K2 = (k, -k, 0) are taken in the basis of fslib.modes.

Time dependence [JUDGEMENT, derivation in JOURNAL.md, P11b']: the x wave is in the growing
mode (Phi constant, Phi'/Hc = 0); the noise starts without peculiar velocity, so Phi_n =
Phi_n0 (3/5 + (2/5) u), Phi_n'/Hc = -Phi_n0 u, u = a^(-5/2). With the dust source of the
Poisson-gauge equation, 4 [dPhi dPhi + (2/3) dV dV], V = Phi + Phi'/Hc, normalized to its
growing-mode value 20/3: the cross term carries F_cross = [4 f + (8/3) v]/(20/3) = 3/5 at all
times (f = 3/5 + (2/5) u, v = (3/5)(1 - u)), the noise-noise term F_nn = [4 f^2 + (8/3)
v^2]/(20/3) (3/5 at a = 1, 9/25 late). Each piece follows c'' + 2 Hc c' + |K|^2 (c - S F(tau)) =
0 from c = c' = 0 (conformally flat start), S its static amplitude. Validation case: the
crossed-wave initial data of the wave-2 scan (eps = 0.1), whose cross term at K1 must give
s = -(5/6) phi_x phi_y = -3.0797e-6 (here without the factor 3/5: growing mode).
Writes null_prediction.json and null_prediction.{png,pdf}.
"""
import json
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fslib"))
import paths  # noqa: E402,F401
from fslib import modes, reference as ref  # noqa: E402
from gwdiag import tt  # noqa: E402
from gwdiag.grid import Grid  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

L = 4.0


def read_fields(path):
    with open(path, "rb") as f:
        raw = f.read()
    assert raw[:8] == b"NRCOSMO1", path
    n1, n2, n3 = (int(v) for v in np.frombuffer(raw, np.int64, 3, 8))
    nc = n1 * n2 * n3
    psi = np.frombuffer(raw, np.float64, nc, 32).reshape((n1, n2, n3), order="F")
    return np.ascontiguousarray(psi.transpose(2, 1, 0))           # (nz, ny, nx)


def grad(f, g):
    k = g.kvec(real=True)
    F = tt.rfft(f)
    return np.array([tt.irfft(1j * k[a] * F, g) for a in range(3)])


def static_tt(dA, dB, g):
    """(20/3) Lambda[sym(dA dB)]/|K|^2 as Fourier coefficients (3, 3, ...)."""
    S = 0.5 * (dA[:, None] * dB[None, :] + dB[:, None] * dA[None, :])
    F = tt.tensor_rfft(S)
    k, kk, kh = tt._khat(g)
    T = tt.lambda_apply(F, kh)
    with np.errstate(invalid="ignore", divide="ignore"):
        T = np.where(kk > 0, (20.0 / 3.0) * T / np.where(kk > 0, kk, 1.0) ** 2, 0.0)
    T[:, :, g.nyquist_mask(real=True)] = 0.0
    return T


def response(tau, F, K):
    """c(tau) for c'' + 2 Hc c' + K^2 (c - F(tau)) = 0, c(0) = c'(0) = 0."""
    def rhs(t, y):
        Hc = 1.0 / (1.0 + 0.5 * t)
        return [y[1], -2 * Hc * y[1] - K * K * (y[0] - F(t))]
    sol = solve_ivp(rhs, (0.0, float(np.max(tau))), [0.0, 0.0], rtol=1e-10, atol=1e-14,
                    method="DOP853", dense_output=True)
    return sol.sol(tau)[0]


def f_cross(t):
    return 0.6


def f_nn(t):
    u = ref.a_of_tau(t) ** -2.5
    f = 0.6 + 0.4 * u
    v = 0.6 * (1.0 - u)
    return (4.0 * f * f + (8.0 / 3.0) * v * v) / (20.0 / 3.0)


def mode_amp(F, g, m):
    """complex amplitude (c - i s) of a scalar field at integer mode m (mx >= 0)."""
    return modes.amp(F, g, m)


def analyse(icdir):
    psi = read_fields(os.path.join(icdir, "fields.bin"))
    n = psi.shape[::-1]
    g = Grid(n, (L, L, L), (0.0, 0.0, 0.0))
    P = 0.5 * (1.0 - psi ** 4)
    P = P - P.mean()
    Px = np.broadcast_to(P.mean(axis=(0, 1), keepdims=True), P.shape)   # depends on x only
    Pn = P - Px
    FP = tt.rfft(P)
    out = {"dir": icdir, "n": list(n)}
    # amplitudes of the potential: Psi = c cos(k.x) + s sin(k.x); c - i s returned
    for name, m in (("x", (1, 0, 0)), ("y", (0, 1, 0)), ("ym", (0, -1, 0)), ("z", (0, 0, 1))):
        v = mode_amp(FP, g, m)
        out[f"Psi_mode_{name}"] = [float(v.real), float(v.imag)]
    out["phi_x_sin"] = -out["Psi_mode_x"][1]           # coefficient of sin(k x)
    out["rms_Psi_noise"] = float(np.sqrt((Pn ** 2).mean()))
    out["Psi_y_sin"] = -out["Psi_mode_y"][1]
    dx_, dn = grad(np.ascontiguousarray(Px), g), grad(np.ascontiguousarray(Pn), g)
    Tc = 2.0 * static_tt(dx_, dn, g)
    Tn = static_tt(dn, dn, g)
    for key, T in (("cross", Tc), ("nn", Tn)):
        pa = modes.pol_amps(T, g)
        for K, (hp, hx) in pa.items():
            out[f"{key}_{K}_plus"] = [float(hp.real), float(hp.imag)]
            out[f"{key}_{K}_cross"] = [float(hx.real), float(hx.imag)]
        out[f"rms_{key}"] = float(np.sqrt(modes.ms_fourier(T, g)))
    out["rms_late"] = float(np.sqrt(modes.ms_fourier(0.6 * Tc + 0.36 * Tn, g)))
    return out


def main():
    od = os.environ.get("NRPIC_RUN_DIR", ".")
    k = 2 * np.pi / L
    K = np.sqrt(2.0) * k
    tau = np.round(np.arange(0.0, 21.7, 0.1), 10)
    g_c = response(tau, f_cross, K)       # includes the 3/5
    g_n = response(tau, f_nn, K)
    g_1 = response(tau, lambda t: 1.0, K)
    res = {"tau": tau.tolist(), "a": ref.a_of_tau(tau).tolist(), "g_cross": g_c.tolist(),
           "g_nn": g_n.tolist(), "g_growing": g_1.tolist(), "cases": {}}
    for d in sys.argv[1:]:
        r = analyse(d)
        name = os.path.basename(d.rstrip("/"))
        res["cases"][name] = r
        print(name, json.dumps({k_: v for k_, v in r.items() if "K1_plus" in k_ or k_.startswith("Psi") or k_.startswith("rms") or k_ == "phi_x_sin"}), flush=True)
    with open(os.path.join(od, "null_prediction.json"), "w") as f:
        json.dump(res, f, indent=1)
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.8))
    a = ref.a_of_tau(tau)
    for name, r in res["cases"].items():
        if not name.startswith("jit") or name == "jit0":
            continue
        for K_, ls in (("K1", "-"), ("K2", "--")):
            c = complex(*r[f"cross_{K_}_plus"]) * g_c
            nn = complex(*r[f"nn_{K_}_plus"]) * g_n
            ax[0].plot(a, np.abs(c + nn), ls, label=f"{name} {K_}")
            ax[0].plot(a, np.abs(nn), ls, lw=0.6, alpha=0.6)
    ax[0].set_xscale("log")
    ax[0].set_yscale("log")
    ax[0].set_xlabel("a")
    ax[0].set_ylabel("predicted |h_+| (cross + nn; thin: nn)")
    ax[0].legend(fontsize=6)
    ax[1].plot(a, g_1, label="growing (signal)")
    ax[1].plot(a, g_c, label="cross: 3/5")
    ax[1].plot(a, g_n, label="noise-noise")
    ax[1].set_xscale("log")
    ax[1].set_xlabel("a")
    ax[1].set_ylabel("response g")
    ax[1].legend(fontsize=6)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(od, f"null_prediction.{ext}"), dpi=150)


if __name__ == "__main__":
    main()
