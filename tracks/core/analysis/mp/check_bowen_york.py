#!/usr/bin/env python3
"""Checks of python/nrpic/bowen_york.py that need no simulation (journal: "Reference
checks done before any code test" and "the isolated corrections need the background
factor"):
 1. Abar_ij is traceless, symmetric and divergence free;
 2. its surface integrals give P_ADM = P and J_ADM = S;
 3. the closed-form correction of arXiv:0711.1165 satisfies
    lap u = -(1/8) psi_BL^-7 Abar^2 for momentum, spin and both;
 4. the multipole solver without iteration reproduces the closed form and the ADM mass
    m + (5/8) P^2/m + (2/5) S^2/m^3;
 5. ADM mass of the full solution against the second-order one;
 6. closed-form Hamiltonian residual of several punctures with no correction, the
    plain sum of isolated corrections, and the background-rescaled corrections.
Prints numbers; exits non-zero if a check is outside its tolerance.
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "..", "python"))
from nrpic import bowen_york as by  # noqa: E402

FAIL = []


def check(name, value, tol):
    ok = abs(value) <= tol
    print(f"{'ok  ' if ok else 'FAIL'} {name}: {value:.3e} (tolerance {tol:.0e})")
    if not ok:
        FAIL.append(name)


def lap(f, x, h):
    c = np.array([1 / 90, -3 / 20, 3 / 2, -49 / 18, 3 / 2, -3 / 20, 1 / 90])
    out = 0.0
    for j in range(3):
        for k, ck in zip(range(-3, 4), c):
            e = np.zeros(3)
            e[j] = k * h
            out = out + ck * f(x + e)
    return out / h**2


def main():
    rng = np.random.default_rng(1)
    pos = np.array([0.3, -0.2, 0.1])
    P = np.array([0.2, -0.1, 0.35])
    S = np.array([-0.3, 0.25, 0.1])
    m = 0.8

    # 1
    x = rng.normal(size=(20, 3)) * 2.0
    A = by.abar(x, pos, P, S)
    check("trace of Abar", np.max(np.abs(np.trace(A, axis1=-1, axis2=-2))), 1e-14)
    check("asymmetry of Abar", np.max(np.abs(A - np.swapaxes(A, -1, -2))), 1e-14)
    h = 1e-2
    c1 = [-1 / 60, 3 / 20, -3 / 4, 0, 3 / 4, -3 / 20, 1 / 60]
    div = 0.0
    for j in range(3):
        for k, ck in zip(range(-3, 4), c1):
            e = np.zeros(3)
            e[j] = k * h
            div = div + ck * by.abar(x + e, pos, P, S)[..., :, j] / h
    check("divergence of Abar (sixth-order differences)", np.max(np.abs(div)), 1e-8)

    # 2
    mu, w = np.polynomial.legendre.leggauss(40)
    ph = np.linspace(0, 2 * np.pi, 81)[:-1]
    MU, PH = np.meshgrid(mu, ph, indexing="ij")
    st = np.sqrt(1 - MU**2)
    n = np.stack([st * np.cos(PH), st * np.sin(PH), MU], axis=-1)
    W = w[:, None] * (2 * np.pi / len(ph)) * np.ones_like(PH)
    for rad in (5.0, 50.0):
        An = np.einsum("...ij,...j->...i", by.abar(pos + rad * n, pos, P, S), n)
        Padm = np.einsum("ab,abi->i", W, An) * rad**2 / (8 * np.pi)
        Jadm = np.einsum("ab,abi->i", W, np.cross(rad * n, An)) * rad**2 / (8 * np.pi)
        check(f"P_ADM - P at r = {rad:g}", np.max(np.abs(Padm - P)), 1e-13)
        check(f"J_ADM - S at r = {rad:g}", np.max(np.abs(Jadm - S)), 1e-13)

    # 3
    for name, (Pc, Sc) in {"momentum": (P, 0 * S), "spin": (0 * P, S),
                           "momentum and spin": (P, S)}.items():
        pc = [{"pos": pos, "m": m, "P": Pc, "S": Sc}]
        f = lambda y: by.approx_u(y, pos, m, Pc, Sc)  # noqa: E731
        worst = 0.0
        for rad in (0.02, 0.1, 0.5, 2.0):
            d = rng.normal(size=(200, 3))
            d /= np.linalg.norm(d, axis=1)[:, None]
            xs = pos + rad * d
            rhs = -0.125 * by.abar2(xs, pc) / by.psi_bl(xs, pc)**7
            lp = np.array([lap(f, xi[None, :], 0.05 * rad)[0] for xi in xs])
            worst = max(worst, np.max(np.abs(lp - rhs)) / np.max(np.abs(rhs)))
        check(f"closed form, {name}: |lap u - source| / max |source|", worst, 1e-4)

    # 4, 5
    for (Pz, Sz) in ((0.3, 0.0), (0.0, 0.4), (0.3, 0.4)):
        sol = by.solve_axisym(m, Pz, Sz, lmax=4, nonlinear=False)
        rr = np.array([0.01, 0.1, 0.4, 1.0, 5.0, 40.0]) * m
        err = 0.0
        for mu_ in (-0.9, -0.3, 0.0, 0.5, 1.0):
            pts = np.stack([rr * math.sqrt(1 - mu_**2), 0 * rr, rr * mu_], axis=-1)
            ua = by.approx_u(pts, np.zeros(3), m, (0, 0, Pz), (0, 0, Sz))
            pl = by._legendre(4, mu_)
            un = sum(np.interp(np.log(rr), np.log(sol["r"]), sol["ul"][q]) * pl[l]
                     for q, l in enumerate(sol["lvals"]))
            err = max(err, np.max(np.abs(un / ua - 1)))
        check(f"multipole solver vs closed form, P = {Pz}, S = {Sz}", err, 1e-5)
        check(f"ADM mass, second order, P = {Pz}, S = {Sz}",
              sol["m_adm"] - by.adm_mass_approx(m, Pz, Sz), 1e-7)
    for Pz in (0.1, 0.3, 0.6, 1.0):
        lin = by.solve_axisym(1.0, Pz, 0.0, nonlinear=False)
        non = by.solve_axisym(1.0, Pz, 0.0, nonlinear=True)
        print(f"     m = 1, P = {Pz}: M_ADM second order {lin['m_adm']:.5f}, full"
              f" {non['m_adm']:.5f} ({non['iterations']} iterations)")

    # 6
    def residuals(pts, puncs):
        psi_bl = by.psi_bl(pts, puncs)
        ab = sum(by.abar(pts, p["pos"], p["P"], p["S"]) for p in puncs)
        a2 = np.sum(ab * ab, axis=(-1, -2))
        out = {"none": -a2 / psi_bl**12}
        for mode in ("plain", "background"):
            psi = psi_bl.copy()
            lp = 0.0
            for c, p in enumerate(puncs):
                lam = 1.0
                if mode == "background":
                    lam += sum(0.5 * q["m"] / np.linalg.norm(q["pos"] - p["pos"])
                               for j, q in enumerate(puncs) if j != c)
                a = by.abar(pts, p["pos"], p["P"], p["S"])
                _, r = by._disp(pts, p["pos"])
                psi += by.approx_u(pts, p["pos"], p["m"], p["P"], p["S"], lam=lam)
                lp += -0.125 * np.sum(a * a, axis=(-1, -2)) / (lam + 0.5 * p["m"] / r)**7
            out[mode] = -8 * lp / psi**5 - a2 / psi**12
        return psi_bl, out

    z = np.zeros(3)
    cases = {
        "two punctures 3 apart (test 1a)": (
            [{"pos": np.array([-1.5, 0, 0]), "m": 1.0, "P": np.array([0, 0.3, 0]), "S": z},
             {"pos": np.array([1.5, 0, 0]), "m": 0.5, "P": np.array([0, -0.3, 0]),
              "S": np.array([0, 0, 0.1])}], 4.0, 128),
        "binary d = 10 (test 2)": (
            [{"pos": np.array([-5.0, 0, 0]), "m": 0.5, "P": np.array([0, -0.0791, 0]),
              "S": z},
             {"pos": np.array([5.0, 0, 0]), "m": 0.5, "P": np.array([0, 0.0791, 0]),
              "S": z}], 8.0, 256),
        "light moving puncture 20 from a heavy one at rest": (
            [{"pos": np.array([0.0, 0, 0]), "m": 0.5, "P": np.array([0, 0.2, 0]), "S": z},
             {"pos": np.array([20.0, 0, 0]), "m": 10.0, "P": z, "S": z}], 2.0, 128)}
    for name, (puncs, half, nn) in cases.items():
        g = (np.arange(nn) + 0.5) / nn * 2 * half - half
        X, Y, Z = np.meshgrid(g, g, g, indexing="ij")
        pts = np.stack([X.ravel(), Y.ravel(), Z.ravel()], -1)
        psi_bl, out = residuals(pts, puncs)
        mask = psi_bl <= 2.0
        r = {k: float(np.sqrt(np.mean(v[mask]**2))) for k, v in out.items()}
        print(f"     {name}: rms H over cells with psi_BL <= 2: none {r['none']:.3e},"
              f" plain sum {r['plain']:.3e}, background {r['background']:.3e}")
        check(f"{name}: background below none", r["background"] / r["none"] - 0.5, 0.5)
    if FAIL:
        print("FAILED:", FAIL)
        sys.exit(1)


if __name__ == "__main__":
    main()
