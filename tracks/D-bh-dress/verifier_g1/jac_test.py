import numpy as np
def metric(r, th, a):
    S2 = r*r + a*a*np.cos(th)**2; D = r*r + a*a - 2*r
    g = np.zeros((4,4))
    g[0,0] = -(1 - 2*r/S2); g[1,1] = S2/D; g[2,2] = S2
    g[0,3] = g[3,0] = -2*a*r*np.sin(th)**2/S2
    g[3,3] = (r*r + a*a + 2*r*a*a*np.sin(th)**2/S2)*np.sin(th)**2
    return g, S2, D
def invariants(p, r, th, a):
    g, S2, D = metric(r, th, a)
    mu = np.sqrt(-p @ g @ p)
    u = p/mu
    ul = g @ u
    E = -ul[0]; Lz = ul[3]
    C = S2**2*u[2]**2 + Lz**2/np.sin(th)**2 + a*a*np.cos(th)**2*(1 - E*E)
    return np.array([E, C, Lz, mu])
for a, r, th in ((0.0, 7.0, np.pi/2), (0.8, 7.0, np.pi/2), (0.8, 6.0, 1.1)):
    g, S2, D = metric(r, th, a)
    # a timelike momentum: pick spatial parts and solve p^t from mu = 1
    pr, pth, pph = 0.11, 0.013, 0.021
    # solve g_tt pt^2 + 2 g_tph pt pph + g_phph pph^2 + g_rr pr^2 + g_thth pth^2 = -1 for pt > 0
    A = g[0,0]; B = 2*g[0,3]*pph; Cc = g[3,3]*pph**2 + g[1,1]*pr**2 + g[2,2]*pth**2 + 1
    pt = (-B - np.sqrt(B*B - 4*A*Cc))/(2*A)
    p = np.array([pt, pr, pth, pph])
    J = np.zeros((4,4)); h = 1e-6
    for k in range(4):
        dp = np.zeros(4); dp[k] = h
        J[:, k] = (invariants(p+dp, r, th, a) - invariants(p-dp, r, th, a))/(2*h)
    detJ = abs(np.linalg.det(J))
    mu = 1.0; u = p
    ul = g @ u
    formula = 2*S2**2*D*abs(ul[1])*abs(u[2])*np.sin(th)**2/mu**3
    # alternative: without Delta, with Delta^0 etc.
    print("a=%.1f r=%.1f th=%.2f  numeric |J| = %.8g  paper formula = %.8g  ratio = %.8f" % (a, r, th, detJ, formula, detJ/formula))
