"""K3 of khsr_note checked with the verifier's own three-body integrator (vnewton.rhs).

KHSR set-up (arXiv:1201.4794 Sec. 6.2 as used by khsr_note): M/m = 1e6, m1 = 0.75, m2 = 0.25,
circular prograde coplanar binary of separation a = 1, r_t = a (M/m)^(1/3); centre-of-mass orbit
with pericentre D r_t and semi-major axis r_a r_t (parabola for r_a = inf); start at 10 r_t
inbound; stop when the members' centre of mass reaches 30 r_t outbound. Outcome from two-body
energies at the end. Phases uniform in [0, 2 pi) at the start.

Run: python tracks/F-hills/stage/G1/verifier/scripts/vkhsr.py --out <dir> [--nphase 128 --workers 4]
"""
import argparse
import json
import os
import sys
from multiprocessing import Pool

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"
import numpy as np
from scipy.integrate import solve_ivp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vnewton  # noqa: E402
import figstyle  # noqa: E402

MBH, M1, M2, A = 1.0e6, 0.75, 0.25, 1.0
MB = M1 + M2
RT = A * (MBH / MB) ** (1.0 / 3.0)
MASSES = np.array([MBH, M1, M2])


def initial(D, ra, phi):
    rp = D * RT
    mu = MBH + MB
    e = 1.0 if not np.isfinite(ra) else 1.0 - rp / (ra * RT)
    p = rp * (1 + e)
    r0 = 10 * RT
    f0 = -np.arccos((p / r0 - 1) / e)
    rhat = np.array([np.cos(f0), np.sin(f0), 0.0])
    fhat = np.array([-np.sin(f0), np.cos(f0), 0.0])
    h = np.sqrt(mu / p)
    xc = r0 * rhat
    vc = h * e * np.sin(f0) * rhat + h * (1 + e * np.cos(f0)) * fhat
    w = np.sqrt(MB / A ** 3)
    rr = A * np.array([np.cos(phi), np.sin(phi), 0.0])
    vr = A * w * np.array([-np.sin(phi), np.cos(phi), 0.0])
    # barycentric: put the heavy mass so that the total momentum and centre of mass vanish
    x1, x2 = xc + (M2 / MB) * rr, xc - (M1 / MB) * rr
    v1, v2 = vc + (M2 / MB) * vr, vc - (M1 / MB) * vr
    xM = -(MB * xc) / MBH
    vM = -(MB * vc) / MBH
    return np.array([xM, x1, x2]), np.array([vM, v1, v2])


def run_one(args):
    D, ra, phi = args
    X0, V0 = initial(D, ra, phi)
    y0 = np.concatenate([X0.ravel(), V0.ravel()])

    def ev(t, y, m):
        x = y[:9].reshape(3, 3)
        v = y[9:].reshape(3, 3)
        xc = (M1 * x[1] + M2 * x[2]) / MB - x[0]
        vc = (M1 * v[1] + M2 * v[2]) / MB - v[0]
        out = np.dot(xc, vc) > 0
        return (np.linalg.norm(xc) - 30 * RT) if out else -1.0
    ev.terminal = True
    ev.direction = 1
    sol = solve_ivp(vnewton.rhs, (0.0, 5.0e4), y0, method="DOP853", rtol=1e-11, atol=1e-11,
                    args=(MASSES,), events=ev)
    y = sol.y[:, -1]
    x = y[:9].reshape(3, 3)
    v = y[9:].reshape(3, 3)
    Ep = vnewton.two_body_energy(M1, M2, x[1], x[2], v[1], v[2])
    E1 = vnewton.two_body_energy(M1, MBH, x[1], x[0], v[1], v[0])
    E2 = vnewton.two_body_energy(M2, MBH, x[2], x[0], v[2], v[0])
    Et0 = vnewton.energy(MASSES, X0[None], V0[None])[0]
    Et1 = vnewton.energy(MASSES, x[None], v[None])[0]
    return {"D": D, "ra": ra, "phi": phi, "Ep": float(Ep), "E1": float(E1), "E2": float(E2),
            "t_end": float(sol.t[-1]), "status": int(sol.status), "dE_rel": float(abs(Et1 / Et0 - 1))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--nphase", type=int, default=128)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    phis = 2 * np.pi * (np.arange(a.nphase) + 0.5) / a.nphase
    cases = [(D, ra) for D in (0.5, 1.0) for ra in (np.inf, 100.0)]
    jobs = [(D, ra, float(p)) for D, ra in cases for p in phis]
    with Pool(a.workers) as pool:
        rows = pool.map(run_one, jobs, chunksize=4)
    unit = (M1 * M2 / A) * (MBH / MB) ** (1.0 / 3.0)
    res = {"setup": {"M": MBH, "m1": M1, "m2": M2, "a": A, "r_t": RT, "nphase": a.nphase, "unit_E": unit}, "cases": []}
    for D, ra in cases:
        rr = [r for r in rows if r["D"] == D and r["ra"] == ra]
        n = len(rr)
        dis = [r for r in rr if r["Ep"] > 0]
        P1 = sum(1 for r in dis if r["E1"] > 0 and r["E2"] <= 0) / n
        P2 = sum(1 for r in dis if r["E2"] > 0 and r["E1"] <= 0) / n
        Pbb = sum(1 for r in dis if r["E1"] <= 0 and r["E2"] <= 0) / n
        Pbf = sum(1 for r in dis if r["E1"] > 0 and r["E2"] > 0) / n
        Pdis = len(dis) / n
        sig = lambda p: float(np.sqrt(max(p * (1 - p), 1.0 / n) / n))
        res["cases"].append({"D": D, "r_a": "inf" if not np.isfinite(ra) else ra, "n": n, "P1": P1, "P2": P2,
                             "Pdis": Pdis, "Pboth_bound": Pbb, "Pboth_free": Pbf,
                             "sigma": {"P1": sig(P1), "P2": sig(P2), "Pdis": sig(Pdis), "Pboth_bound": sig(Pbb)},
                             "P1_over_P2": P1 / P2 if P2 > 0 else None,
                             "n_status_not_event": sum(1 for r in rr if r["status"] != 1),
                             "max_dE_rel": max(r["dE_rel"] for r in rr)})
    with open(os.path.join(a.out, "vkhsr.json"), "w") as f:
        json.dump(res, f, indent=1)
    figstyle.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(8, 3.2))
    fig.subplots_adjust(left=0.1, right=0.98, bottom=0.16, top=0.92, wspace=0.3)
    for k, (D, ra) in enumerate(cases):
        rr = sorted([r for r in rows if r["D"] == D and r["ra"] == ra], key=lambda r: r["phi"])
        axx = ax[0] if not np.isfinite(ra) else ax[1]
        col = figstyle.SERIES[0] if D == 0.5 else figstyle.SERIES[1]
        axx.plot([r["phi"] for r in rr], [r["E1"] / unit for r in rr], "o", ms=2, color=col, label=f"D = {D}, m1")
        axx.plot([r["phi"] for r in rr], [r["E2"] / unit for r in rr], "x", ms=2, color=col, label=f"D = {D}, m2")
    for axx, t in zip(ax, ("parabola", "r_a = 100 r_t")):
        axx.axhline(0, **figstyle.THIN); axx.set_xlabel("phase at the start"); axx.set_ylabel("member energy with M [unit]")
        axx.set_title(t, fontsize=10); axx.legend(fontsize=7, ncol=2)
    figstyle.save(fig, os.path.join(a.out, "fig_v_khsr"))
    print(json.dumps(res["cases"], indent=0))


if __name__ == "__main__":
    main()
