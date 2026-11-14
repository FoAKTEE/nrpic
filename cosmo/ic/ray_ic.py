"""Light rays between the overdensity and the underdensity (cosmo/PLAN.md, C3).

A bundle is five null particles that leave one point at one time: the central ray in
the coordinate direction c of the other extremum, and four neighbours with directions
c +- eps e_1 and c +- eps e_2, where e_1 and e_2 are orthogonal to c and to each other
in the coordinate sense. The code keeps a ray at its point until the emission time and
then turns the direction into the null momentum of unit frequency for the normal
observer there (athenak/src/particles/nrpic.cpp); the analysis measures the solid angle
of the bundle with the metric at the emission.

In the particle file a ray has the mass -t_e (emission time; at least -1e-30) and its
momentum slots hold the coordinate direction.
"""
import numpy as np

E1 = np.array([1.0, -1.0, 0.0])/np.sqrt(2.0)
E2 = np.array([1.0, 1.0, -2.0])/np.sqrt(6.0)
CHAT = np.array([1.0, 1.0, 1.0])/np.sqrt(3.0)
ROLE = ("centre", "+e1", "-e1", "+e2", "-e2")


def directions(sign, eps):
    """The five coordinate directions of a bundle along sign * (1, 1, 1)."""
    c = sign*CHAT
    return np.array([c, c + eps*E1, c - eps*E1, c + eps*E2, c - eps*E2])


def bundles(t_emit, L=4.0, eps=1e-4):
    """Rays for the emission times t_emit: for each time one bundle from the overdensity
    towards the underdensity (kind 0) and one in the opposite sense (kind 1).
    Returns x, c, m and a dict of per-ray arrays (bundle, kind, role, t_emit)."""
    xs, cs, ms, bid, kind, role, te = [], [], [], [], [], [], []
    b = 0
    for t in t_emit:
        for kd, (pt, sign) in enumerate(((0.25*L, 1.0), (0.75*L, -1.0))):
            d = directions(sign, eps)
            for r in range(5):
                xs.append([pt, pt, pt])
                cs.append(d[r])
                ms.append(-max(t, 1e-30))
                bid.append(b)
                kind.append(kd)
                role.append(r)
                te.append(t)
            b += 1
    meta = {"bundle": np.array(bid), "kind": np.array(kind), "role": np.array(role),
            "t_emit": np.array(te), "eps": eps}
    return np.array(xs), np.array(cs), np.array(ms), meta
