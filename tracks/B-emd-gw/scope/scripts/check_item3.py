"""Symbolic checks of item 3 of coord/notes/derivations_to_check.md (plane symmetry and
gravitational waves), and of the form of the plane-symmetric growing mode.

    python3 check_item3.py OUTDIR

Writes OUTDIR/check_item3.json and OUTDIR/check_item3.txt. Units G = c = 1.
Predictions and outcomes: ../JOURNAL.md (checks 1A to 1E).
"""
import json
import os
import sys

import sympy as sp


def tt_projector_along_x():
    """(1A) Flat-space TT projection Lambda_ijkl T_kl for khat = e_x."""
    T = sp.Matrix(3, 3, lambda i, j: sp.Symbol(f"T{min(i, j)}{max(i, j)}"))
    P = sp.diag(0, 1, 1)
    proj = P*T*P - sp.Rational(1, 2)*P*(P*T).trace()
    expected = sp.zeros(3, 3)
    expected[1, 1] = (T[1, 1] - T[2, 2])/2
    expected[2, 2] = -(T[1, 1] - T[2, 2])/2
    expected[1, 2] = expected[2, 1] = T[1, 2]
    ok_form = sp.simplify(proj - expected) == sp.zeros(3, 3)
    A, B = sp.symbols("A B")
    Tsym = T.subs({T[0, 0]: A, T[1, 1]: B, T[2, 2]: B, T[1, 2]: 0})
    proj_sym = sp.simplify(P*Tsym*P - sp.Rational(1, 2)*P*(P*Tsym).trace())
    # off-diagonal xy, xz components are left free in Tsym on purpose: they must drop out
    return {"projection_has_expected_form": bool(ok_form),
            "projection_of_diag_ABB_plus_Txy_Txz": str(proj_sym),
            "vanishes_for_E2_symmetric": bool(proj_sym == sp.zeros(3, 3))}


def rotation_invariance():
    """(1B) Symmetric tensors invariant under rotations about x."""
    q = sp.symbols("qxx qxy qxz qyy qyz qzz")
    Q = sp.Matrix([[q[0], q[1], q[2]], [q[1], q[3], q[4]], [q[2], q[4], q[5]]])
    out = {}
    for name, th in (("90deg", sp.pi/2), ("generic", sp.Symbol("theta"))):
        R = sp.Matrix([[1, 0, 0], [0, sp.cos(th), -sp.sin(th)], [0, sp.sin(th), sp.cos(th)]])
        eqs = [sp.simplify(e) for e in (R*Q*R.T - Q)]
        sol = sp.solve([e for e in eqs if e != 0], [q[1], q[2], q[4], q[5]], dict=True)
        out[name] = [str(s) for s in sol]
    return out


def christoffel(g, coords):
    ginv = g.inv()
    n = len(coords)
    G = [[[0]*n for _ in range(n)] for _ in range(n)]
    for a in range(n):
        for b in range(n):
            for c in range(n):
                G[a][b][c] = sp.simplify(sum(ginv[a, d]*(sp.diff(g[d, b], coords[c]) +
                                                       sp.diff(g[d, c], coords[b]) -
                                                       sp.diff(g[b, c], coords[d]))
                                             for d in range(n))/2)
    return G


def divergence_of_harmonic_candidate():
    """(1C) D_a Q^a_b for Q = diag(A, -A/2, -A/2)(x) on diag(X^2, Y^2, Y^2)(t, x)."""
    t, x, y, z = sp.symbols("t x y z")
    X = sp.Function("X")(t, x)
    Y = sp.Function("Y")(t, x)
    A = sp.Function("A")(x)
    co = [x, y, z]
    g = sp.diag(X**2, Y**2, Y**2)
    Gm = christoffel(g, co)
    Q = sp.diag(A, -A/2, -A/2)          # mixed components Q^a_b
    div = []
    for b in range(3):
        s = sum(sp.diff(Q[a, b], co[a]) for a in range(3))
        s += sum(Gm[a][a][c]*Q[c, b] for a in range(3) for c in range(3))
        s -= sum(Gm[c][a][b]*Q[a, c] for a in range(3) for c in range(3))
        div.append(sp.simplify(s))
    expected_x = sp.diff(A, x) + 3*A*sp.diff(Y, x)/Y
    sol = sp.dsolve(sp.Eq(expected_x.subs(Y, sp.Function("Y")(x)), 0), A)
    return {"divergence_components": [str(d) for d in div],
            "x_component_equals_dA_plus_3A_dlnY": bool(sp.simplify(div[0] - expected_x) == 0),
            "y_z_components_vanish": bool(div[1] == 0 and div[2] == 0),
            "solution": str(sol)}


def projection_onto_harmonic_mode():
    """(1D) (X/Y)(K^x_x - K^y_y) = -d/dt (X/Y) with K_ij = -(1/2) d_t gamma_ij."""
    t, x = sp.symbols("t x")
    X = sp.Function("X")(t, x)
    Y = sp.Function("Y")(t, x)
    Kxx = -sp.diff(X, t)/X                # mixed K^x_x for unit lapse, zero shift
    Kyy = -sp.diff(Y, t)/Y
    integrand = (X/Y)*(Kxx - Kyy)
    ok = sp.simplify(integrand + sp.diff(X/Y, t)) == 0
    # linear regime: X = a (1 + D psi' + c1 zeta), Y = a (1 + c2 zeta); the integral of
    # X/Y over a period is L + O(2) because psi', zeta have zero mean
    eps = sp.Symbol("epsilon")
    a = sp.Function("a")(t)
    D = sp.Function("D")(t)
    psi1 = sp.Function("psip")(x)
    zeta = sp.Function("zeta")(x)
    c1, c2 = sp.symbols("c1 c2")
    ratio = sp.series(a*(1 + eps*(D*psi1 + c1*zeta))/(a*(1 + eps*c2*zeta)), eps, 0, 2).removeO()
    return {"integrand_identity_holds": bool(ok),
            "X_over_Y_to_first_order": str(sp.expand(ratio))}


def flat_transverse_zeldovich():
    """(1E) Hamiltonian constraint for X = a (1 + D psi'), Y = a, dust at rest."""
    t, x, y, z = sp.symbols("t x y z")
    a = sp.Function("a")(t)
    D = sp.Function("D")(t)
    psi1 = sp.Function("psip")(x)
    X = a*(1 + D*psi1)
    co = [x, y, z]
    g = sp.diag(X**2, a**2, a**2)
    Gm = christoffel(g, co)
    # Ricci scalar of the slice
    n = 3
    Ric = sp.zeros(3, 3)
    for b in range(n):
        for c in range(n):
            s = 0
            for a_ in range(n):
                s += sp.diff(Gm[a_][b][c], co[a_]) - sp.diff(Gm[a_][b][a_], co[c])
                for d in range(n):
                    s += Gm[a_][a_][d]*Gm[d][b][c] - Gm[a_][c][d]*Gm[d][b][a_]
            Ric[b, c] = sp.simplify(s)
    R = sp.simplify(sum(g.inv()[i, j]*Ric[i, j] for i in range(3) for j in range(3)))
    H = sp.diff(a, t)/a
    Kx = -sp.diff(X, t)/X
    Ky = -H
    rho0 = 3*H**2/(8*sp.pi)
    rho = rho0/(1 + D*psi1)
    ham = R + 2*(2*Kx*Ky + Ky**2) - 16*sp.pi*rho
    ham_num = sp.simplify(sp.numer(sp.together(ham)))
    Ddot = sp.Symbol("Ddot")
    solD = sp.solve(ham_num.subs(sp.diff(D, t), Ddot), Ddot)
    return {"ricci_scalar_of_slice": str(R),
            "hamiltonian_constraint_numerator": str(ham_num),
            "dD_dt_required": [str(s) for s in solD]}


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    res = {
        "1A_tt_projector_along_x": tt_projector_along_x(),
        "1B_rotation_invariance": rotation_invariance(),
        "1C_divergence_of_harmonic_candidate": divergence_of_harmonic_candidate(),
        "1D_projection_onto_harmonic_mode": projection_onto_harmonic_mode(),
        "1E_flat_transverse_zeldovich": flat_transverse_zeldovich(),
    }
    with open(os.path.join(out, "check_item3.json"), "w") as f:
        json.dump(res, f, indent=1)
    with open(os.path.join(out, "check_item3.txt"), "w") as f:
        for k, v in res.items():
            f.write(f"{k}:\n")
            for kk, vv in (v.items() if isinstance(v, dict) else [("", v)]):
                f.write(f"  {kk}: {vv}\n")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
