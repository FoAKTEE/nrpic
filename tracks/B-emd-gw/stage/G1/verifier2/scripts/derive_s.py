"""Second-order tensor source of crossed waves in matter domination, derived from scratch.

Metric (Poisson gauge, dust, Phi constant in time, conformal time eta, a = eta^2/4):
    g_00 = -a^2 (1 + 2 Phi),  g_0i = 0,  g_ij = a^2 [(1 - 2 Phi) delta_ij + h_ij],
    Phi = e (P1 sin kx + P2 sin ky),  h_ij = e^2 H(eta) e+_ij cos(k(x+y)),
    e+ = m m - z z,  m = (1,-1,0)/sqrt 2  (transverse-traceless for K1 = (k,k,0)).
Second-order scalar and vector parts are left out: they enter G_ij linearly as
delta_ij(.), d_i d_j(.), d_(i V_j) and drop out of the contraction with e+ at K1.
Dust T_mn = rho u_m u_n; the first-order velocity v^i = dx^i/deta is taken from the
first-order 0i equation (printed). Output: the + equation at K1 at order e^2, its
coefficient s in  H'' + 2 calH H' + K^2 H = K^2 s, and the check of the first-order
equations. Run: python3 derive_s.py  (a minute).
"""
import sympy as sp

eta, x, y, z = sp.symbols("eta x y z", real=True)
k, P1, P2, e = sp.symbols("k P1 P2 e", positive=True)
H = sp.Function("H")(eta)
X = [eta, x, y, z]
a = eta**2/4
calH = sp.diff(a, eta)/a                     # 2/eta
Phi = e*(P1*sp.sin(k*x) + P2*sp.sin(k*y))
m = sp.Matrix([1, -1, 0])/sp.sqrt(2)
zz = sp.Matrix([0, 0, 1])
ep = m*m.T - zz*zz.T
h = e**2*H*sp.cos(k*(x + y))*ep

g = sp.zeros(4, 4)
g[0, 0] = -a**2*(1 + 2*Phi)
for i in range(3):
    for j in range(3):
        g[i+1, j+1] = a**2*((1 - 2*Phi)*(1 if i == j else 0) + h[i, j])

# inverse to second order in e
g0 = g.subs(e, 0)
g1 = g.diff(e).subs(e, 0)
g2 = (g.diff(e, 2)/2).subs(e, 0)
g0i = g0.inv()
gi = g0i - e*g0i*g1*g0i + e**2*(g0i*g1*g0i*g1*g0i - g0i*g2*g0i)
gi = gi.applyfunc(sp.expand)


def trunc(expr, order=2):
    expr = sp.expand(expr)
    return sum(expr.coeff(e, n)*e**n for n in range(order + 1))


Gam = [[[trunc(sum(gi[l, s]*(sp.diff(g[s, mu], X[nu]) + sp.diff(g[s, nu], X[mu])
                              - sp.diff(g[mu, nu], X[s])) for s in range(4))/2)
         for nu in range(4)] for mu in range(4)] for l in range(4)]


def ricci(mu, nu):
    r = 0
    for l in range(4):
        r += sp.diff(Gam[l][mu][nu], X[l]) - sp.diff(Gam[l][mu][l], X[nu])
        for s in range(4):
            r += Gam[l][l][s]*Gam[s][mu][nu] - Gam[l][nu][s]*Gam[s][mu][l]
    return trunc(r)


Ric = sp.Matrix(4, 4, lambda i, j: ricci(i, j) if i <= j else 0)
for i in range(4):
    for j in range(i):
        Ric[i, j] = Ric[j, i]
R = trunc(sum(gi[i, j]*Ric[i, j] for i in range(4) for j in range(4)))
G = (Ric - g*R/2).applyfunc(trunc)

# background: 8 pi G rho_bar a^2 = 3 calH^2 (check with G_00 at e^0)
rho8 = 3*calH**2/a**2                         # 8 pi G rho_bar
print("background G_00 - 8piG rho a^2 (should be 0):",
      sp.simplify(G[0, 0].coeff(e, 0) - rho8*a**2))

# first-order velocity from G_0i = 8 pi G T_0i, T_0i = rho u_0 u_i = -rho a^2 v_i
G0x1 = sp.simplify(G[0, 1].coeff(e, 1))
print("G_0x at first order:", G0x1)
vx = sp.simplify(-G0x1/(rho8*a**2))
vy = sp.simplify(-G[0, 2].coeff(e, 1)/(rho8*a**2))
print("v_x =", vx, "  v_y =", vy)
print("v_x against -(2/(3 calH)) d_x Phi/e:",
      sp.simplify(vx + 2/(3*calH)*sp.diff(Phi/e, x)))
# first-order density from G_00 (for the record)
G001 = sp.simplify(G[0, 0].coeff(e, 1))
print("8piG delta rho a^2 (first order, from G_00 - 2 Phi background term):",
      sp.simplify(G001 - rho8*a**2*2*Phi/e))
# first-order ij traceless part must vanish for Phi = Psi
print("G_xy at first order (should be 0):", sp.simplify(G[1, 2].coeff(e, 1)))

# second-order ij equation, contracted with e+ and projected on cos(K1.x)
v = [0, vx, vy, 0]
E2 = sp.zeros(3, 3)
for i in range(3):
    for j in range(3):
        T2 = rho8*a**2*a**2*0  # placeholder to keep the structure explicit
        # T_ij = rho u_i u_j, u_i = a v_i at first order -> 8piG T_ij = rho8 a^2 v_i v_j
        E2[i, j] = G[i+1, j+1].coeff(e, 2) - rho8*a**2*v[i+1]*v[j+1]
contr = sp.expand(sum(E2[i, j]*ep[i, j] for i in range(3) for j in range(3)))
# exact discrete projection on cos(k(x+y)) over one period (trigonometric polynomial of
# degree <= 3 in each direction: an 8-point grid is exact)
M = 8
Lb = 2*sp.pi/k
acc = 0
for ix in range(M):
    for iy in range(M):
        xs, ys = Lb*ix/M, Lb*iy/M
        acc += contr.subs({x: xs, y: ys})*sp.cos(k*(xs + ys))
proj = sp.simplify(2*acc/M**2/2)      # (2/N) sum cos^2 = 1; divide by e+:e+ = 2
proj = sp.expand(proj)
print("\n+ equation at K1 (e+ contraction, cos(K1.x) part), = 0:")
print(sp.collect(proj, [H.diff(eta, 2), H.diff(eta), H]))
c2 = proj.coeff(H.diff(eta, 2))
norm = sp.expand(proj/c2)
print("normalized:", sp.collect(norm, [H.diff(eta, 2), H.diff(eta), H]))
src = sp.simplify(norm.subs({H.diff(eta, 2): 0, H.diff(eta): 0, H: 0}))
cH = sp.simplify(norm.diff(H.diff(eta)).subs(H, 0))
cK = sp.simplify(norm.subs({H.diff(eta, 2): 0, H.diff(eta): 0}).diff(H))
print("coefficient of H' :", cH, "  (2 calH =", sp.simplify(2*calH), ")")
print("coefficient of H  :", cK, "  (K^2 = 2 k^2)")
s = sp.simplify(-src/cK)
print("static solution s = ", s, " = ", sp.nsimplify(s/(P1*P2)), "* P1 P2")
