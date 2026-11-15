"""Verifier of B-emd-gw: symbolic checks of claims C1, C4, C5 (independent of scope/scripts).

    python3 v1_symbolic.py OUTDIR

C1  plane symmetry and the TT projector along x; rotation (E(2)) versus translation
    symmetry; the 90-degree rotation; the single global TT tensor of a slice
    diag(X^2, Y^2, Y^2)(x) on the torus, and the projection of K_ij onto it.
C4  Hamiltonian constraint for dust at rest (synchronous, comoving) with transverse
    metric a(t)^2: only the decaying mode; and the growing mode with a curvature
    perturbation zeta(x) in the transverse metric (to show what it needs).
C5  conformal Newtonian gauge with a static potential against the code's lapse
    condition d_t alpha = -(1/3) alpha^2 K, zero shift; the initial lapse of
    cosmo/ic/make_east.py.

Writes OUTDIR/v1_symbolic.json. Every check is a sympy simplification to zero.
"""
import json
import os
import sys

import sympy as sp

res = {}


def zero(expr):
    return sp.simplify(expr) == 0


# ------------------------------------------------------------------------------- C1
S = sp.Matrix(3, 3, lambda i, j: sp.Symbol(f"S{min(i, j)}{max(i, j)}"))
P = sp.diag(0, 1, 1)                                   # projector transverse to khat = x
TT = P*S*P - sp.Rational(1, 2)*P*(P*S).trace()
expect = sp.Matrix([[0, 0, 0],
                    [0, (S[1, 1] - S[2, 2])/2, S[1, 2]],
                    [0, S[1, 2], (S[2, 2] - S[1, 1])/2]])
res["C1_TT_along_x_keeps_only_(Syy-Szz)/2_and_Syz"] = bool(zero((TT - expect).norm()))

th = sp.Symbol("theta", real=True)
R = sp.Matrix([[1, 0, 0], [0, sp.cos(th), -sp.sin(th)], [0, sp.sin(th), sp.cos(th)]])
cond = (R*S*R.T - S)
eqs = [sp.simplify(cond[i, j]) for i in range(3) for j in range(i, 3)]
# invariance for all theta: coefficients of cos/sin must vanish
sol_SO2 = sp.solve([sp.expand(e).coeff(sp.sin(th)) for e in eqs]
                   + [sp.expand(e.subs(th, sp.pi/2)) for e in eqs],
                   [S[0, 1], S[0, 2], S[1, 2], S[2, 2]], dict=True)
res["C1_SO2_invariant_tensor"] = str(sol_SO2)
R90 = R.subs(th, sp.pi/2)
sol_C4 = sp.solve(list(R90*S*R90.T - S), [S[0, 1], S[0, 2], S[1, 2], S[2, 2]], dict=True)
res["C1_C4_invariant_tensor"] = str(sol_C4)
for name, sol in (("SO2", sol_SO2), ("C4", sol_C4)):
    TTs = TT.subs(sol[0])
    res[f"C1_TT_vanishes_under_{name}"] = bool(zero(TTs.norm()))
# translations alone: S = f(x) diag(0, s, -s) is translation invariant in y, z
Stran = sp.diag(0, 1, -1)
TTt = P*Stran*P - sp.Rational(1, 2)*P*(P*Stran).trace()
res["C1_translation_only_counterexample_TT_nonzero"] = bool(not zero(TTt.norm()))
# reflection y -> -y alone kills Syz but not Syy - Szz
Ry = sp.diag(1, -1, 1)
sol_R = sp.solve(list(Ry*S*Ry.T - S), [S[0, 1], S[1, 2]], dict=True)
res["C1_reflection_y_only_leaves_Syy_minus_Szz"] = str(sol_R)

# global TT tensor of gamma = diag(X^2, Y^2, Y^2)(x)
x, y, z, t = sp.symbols("x y z t", real=True)
X = sp.Function("X", positive=True)(x)
Y = sp.Function("Y", positive=True)(x)
f = sp.Function("f")(x)
g = sp.diag(X**2, Y**2, Y**2)
gi = g.inv()
co = (x, y, z)


def christoffel(g, gi):
    G = [[[0]*3 for _ in range(3)] for _ in range(3)]
    for a in range(3):
        for b in range(3):
            for c in range(3):
                G[a][b][c] = sp.simplify(sum(gi[a, d]*(sp.diff(g[d, b], co[c])
                                         + sp.diff(g[d, c], co[b]) - sp.diff(g[b, c], co[d]))
                                         for d in range(3))/2)
    return G


Gam = christoffel(g, gi)
Amix = sp.diag(f, -f/2, -f/2)                          # A^i_j, traceless
Aup = Amix*gi                                          # A^{ij} = A^i_k gamma^{kj}
div = []
for i in range(3):
    d = sum(sp.diff(Aup[i, j], co[j]) for j in range(3))
    d += sum(Gam[i][j][k]*Aup[k, j] for j in range(3) for k in range(3))
    d += sum(Gam[j][j][k]*Aup[i, k] for j in range(3) for k in range(3))
    div.append(sp.simplify(d))
sol_f = sp.dsolve(sp.Eq(sp.numer(sp.together(div[0])), 0), f)
res["C1_divergence_free_f"] = str(sol_f)
res["C1_f_is_c_over_Y3"] = bool(zero(sp.simplify(sol_f.rhs*Y**3).diff(x)))
res["C1_y_z_divergence_vanish"] = bool(zero(div[1]) and zero(div[2]))
# projection of K_ij = -(1/(2 alpha)) d_t gamma_ij on A (unit lapse, zero shift)
Xt = sp.Function("Xt", positive=True)(t, x)
Yt = sp.Function("Yt", positive=True)(t, x)
al = sp.Function("alpha", positive=True)(t, x)
gt = sp.diag(Xt**2, Yt**2, Yt**2)
Kdd = -gt.diff(t)/(2*al)
fA = 1/Yt**3
Aup_t = sp.diag(fA, -fA/2, -fA/2)*gt.inv()
integrand = sp.simplify(sum(Kdd[i, j]*Aup_t[i, j] for i in range(3) for j in range(3))
                        * Xt*Yt**2)
target_unit = -sp.diff(Xt/Yt, t)
res["C1_projection_integrand_alpha1_equals_-d_t(X/Y)"] = bool(
    zero(integrand.subs(al, 1) - target_unit))
res["C1_projection_integrand_general_lapse"] = str(sp.simplify(integrand))

# ------------------------------------------------------------------------------- C4
tt, H0 = sp.symbols("t H0", positive=True)
a = tt**sp.Rational(2, 3)                               # EdS, synchronous comoving, t0 = 1
H = sp.diff(a, tt)/a
rhob = 3*H**2/(8*sp.pi)
D = sp.Function("D")(tt)
eps, C = sp.symbols("epsilon C")
psi1 = sp.Function("psi")(x)
Xe = a*(1 + eps*D*psi1.diff(x))
gam = sp.diag(Xe**2, a**2, a**2)
Kd = -gam.diff(tt)/2
gin = gam.inv()
Kmix = gin*Kd
trK = Kmix.trace()
KK = (Kmix*Kmix).trace()
# 3-curvature of diag(X(x)^2, a^2, a^2) is zero (one-dimensional coordinate change)
# continuity for dust at rest: rho * sqrt(gamma) independent of t
rho = rhob*a**3/(Xe*a**2)*(1 + eps*C*psi1.diff(x))
ham = trK**2 - KK - 16*sp.pi*rho
lin = sp.simplify(sp.diff(ham, eps).subs(eps, 0))
odeD = sp.solve(sp.Eq(lin, 0), D.diff(tt))[0]
res["C4_dD/dt"] = str(sp.simplify(odeD))
res["C4_dD/dt_equals_-(3/2)H(D-C)"] = bool(zero(odeD + sp.Rational(3, 2)*H*(D - C)))
solD = sp.dsolve(sp.Eq(D.diff(tt), odeD), D)
res["C4_D(t)"] = str(solD)
# growing mode with a curvature perturbation zeta(x) = w(x) in the whole metric
zeta = sp.Function("zeta")(x)
E = sp.Function("E")(tt)
g2 = sp.diag(a**2*(1 + 2*eps*zeta + 2*eps*E*zeta.diff(x, 2)), a**2*(1 + 2*eps*zeta),
             a**2*(1 + 2*eps*zeta))
gi2 = g2.inv()
co2 = (x, y, z)
Gm2 = [[[sum(gi2[a_, d]*(sp.diff(g2[d, b], co2[c]) + sp.diff(g2[d, c], co2[b])
                         - sp.diff(g2[b, c], co2[d])) for d in range(3))/2
          for c in range(3)] for b in range(3)] for a_ in range(3)]
Ric = sp.zeros(3, 3)
for b in range(3):
    for c in range(3):
        Ric[b, c] = sum(sp.diff(Gm2[a_][b][c], co2[a_]) - sp.diff(Gm2[a_][b][a_], co2[c])
                        + sum(Gm2[a_][a_][d]*Gm2[d][b][c] - Gm2[a_][c][d]*Gm2[d][b][a_]
                              for d in range(3)) for a_ in range(3))
R3 = sum(gi2[b, c]*Ric[b, c] for b in range(3) for c in range(3))
R3lin = sp.simplify(sp.diff(R3, eps).subs(eps, 0))
K2 = -g2.diff(tt)/2
Km2 = gi2*K2
# dust at rest; rest mass per coordinate volume (1 + 3 zeta) so that the initial density
# contrast is -E zeta'' only (delta_0 = 0)
rho2 = rhob*a**3*(1 + 3*eps*zeta)/sp.sqrt(g2.det())
ham2 = R3 + Km2.trace()**2 - (Km2*Km2).trace() - 16*sp.pi*rho2
lin2 = sp.simplify(sp.diff(ham2, eps).subs(eps, 0))
lin2c = sp.simplify(lin2/zeta.diff(x, 2))
res["C4_R3_linear"] = str(R3lin)
res["C4_growing_mode_equation"] = str(sp.simplify(lin2c))
Eg = sp.Rational(9, 10)*tt**sp.Rational(2, 3)
res["C4_E=(9/10)t^(2/3)_solves_with_zeta"] = bool(zero(lin2c.subs(E, Eg).doit()))

# ------------------------------------------------------------------------------- C5
tau = sp.Symbol("tau", positive=True)
Phi = sp.Function("Phi")(x, y, z)
A_ = sp.Function("a", positive=True)(tau)
alpha = A_*sp.sqrt(1 + 2*Phi)
gam5 = A_**2*(1 - 2*Phi)*sp.eye(3)
K5 = -(gam5.inv()*gam5.diff(tau)).trace()/(2*alpha)
lapse_rhs = -sp.Rational(1, 3)*alpha**2*K5
res["C5_Newtonian_gauge_static_Phi_obeys_lapse_condition_exactly"] = bool(
    zero(sp.diff(alpha, tau) - lapse_rhs))
# initial data of make_east.py: alpha = sqrt(1 + 2 psi_N), gamma^(1/6) = psi^2 with
# psi^4 = 1 - 2 psi_N to first order; ratio alpha / gamma^(1/6) against the Newtonian one
pN = sp.Symbol("psi_N")
ratio_id = sp.sqrt(1 + 2*pN)/sp.sqrt(1 - 2*pN)
ratio_newt = (alpha/sp.sqrt(1 - 2*Phi)/A_).subs(Phi, pN)
res["C5_initial_ratio_equals_Newtonian_ratio"] = bool(zero(ratio_id - ratio_newt))

out = sys.argv[1] if len(sys.argv) > 1 else os.environ["NRPIC_RUN_DIR"]
os.makedirs(out, exist_ok=True)
with open(os.path.join(out, "v1_symbolic.json"), "w") as fh:
    json.dump(res, fh, indent=1)
for k_, v in res.items():
    print(f"{k_}: {v}")
