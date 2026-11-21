import sys, numpy as np
sys.path.insert(0, "/data/haiyangw/nrpic/wt/D-bh-dress/tracks/D-bh-dress/verifier_g1")
import v3_kerr as K

def zamo(r, a, n=160, pmax=None):
    D = r*r + a*a - 2*r
    A = (r*r + a*a)**2 - a*a*D
    al = np.sqrt(D*r*r/A); gpp = A/(r*r); om = 2*a*r/A
    if pmax is None:
        # largest |p| with E < 1 over the two phi directions: al*sqrt(1+p^2) + om*sqrt(gpp)*p*mu = 1
        ps = np.linspace(0, 2, 200001)
        ok = (al*np.sqrt(1+ps**2) - om*np.sqrt(gpp)*ps) < 1
        pmax = ps[ok].max()*1.001
    # spherical grid in local momentum p (|p| = gamma v), cos(angle to phi-direction), azimuth
    x, w = np.polynomial.legendre.leggauss(n)
    p = 0.5*pmax*(x+1); wp = 0.5*pmax*w
    mu = x; wmu = w                         # cos of angle between p and e_phi
    nb = 2*n; be = (np.arange(nb)+0.5)*2*np.pi/nb; wb = np.full(nb, 2*np.pi/nb)
    N0 = 0.0; Nphi = 0.0
    for i in range(n):
        P = p[i]
        g = np.sqrt(1+P*P)
        pphi = P*mu[:, None]*np.ones(nb)[None, :]
        pt = P*np.sqrt(1-mu[:, None]**2)
        pr = pt*np.cos(be)[None, :]; pth = pt*np.sin(be)[None, :]
        Lz = np.sqrt(gpp)*pphi
        E = al*g + om*Lz
        Q = (r*pth)**2
        v = K.valid_orbit(r, E.ravel(), Q.ravel(), Lz.ravel(), a).reshape(E.shape)
        wt = wp[i]*P*P*wmu[:, None]*wb[None, :]*v
        N0 += np.sum(wt)
        Nphi += np.sum(wt*pphi/g)
    return np.sqrt(N0**2 - Nphi**2), N0, Nphi

for a, r in ((0.0, 7.6), (0.0, 300.0), (0.8, 300.0), (0.8, 12.0), (0.8, 6.6)):
    rho, N0, Nphi = zamo(r, a)
    sp = K.Spike(a, "constf", nE=32, nL=32, npsi=12)
    d = sp.density(r)
    print(a, r, "zamo", rho, "invariants", d["rho_dimless"], "ratio", d["rho_dimless"]/rho, flush=True)
