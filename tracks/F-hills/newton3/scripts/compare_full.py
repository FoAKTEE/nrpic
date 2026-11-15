"""P3/P4 and the finite mass-ratio scan: the full three-body driver against the
restricted limit.

  p3      m1/m2 = 3, coplanar prograde, D in {1, 0.1}, 200 effective phases in [0, 2 pi),
          M/m in {1e6, 1e5, 1e4, 1e3, 1e2, 10}; restricted reference at the same phases
          (the set-up of SKR prp.tex:590-599 and KHSR ms.tex:1101-1104), plus SKR's single
          example D = 0.1, phi = 4 pi / 5 (prp.tex:624, 631).
  p4      start-distance sensitivity: D = 0.5, coplanar prograde, m1 = m2, 200 phases,
          M/m in {1e6, 10}, start at k0 in {5, 10, 20, 40} r_t with the effective phase held.
  finiteq m1 = m2, M/m in {10, 30, 100, 1000}: disruption probability and mean |dE| vs D for
          coplanar prograde/retrograde (256 phases) and isotropic orientation (128 Fibonacci
          orientations x 16 phases), with the restricted limit on the same samples.

Run: cd tracks/F-hills/newton3 && OMP_NUM_THREADS=1 python3 scripts/compare_full.py p3|p4|finiteq [--workers 8]
"""
import argparse
import os
import sys

# one thread per worker process: the parallelism is the process pool (--workers = the
# cores of the run); nrpic-run sets the thread count to --cores, which every worker would
# inherit (finite-q run F-20261115-174959-9e8a361 used about 20 cores for 6 workers, stopped)
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"
import numpy as np
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from hills3 import restricted as R  # noqa: E402
from hills3 import threebody as T  # noqa: E402
from hills3.orbits import fibonacci_sphere  # noqa: E402
import runlib  # noqa: E402

PRO = (np.pi / 2, np.pi / 2)
RET = (np.pi / 2, -np.pi / 2)


def full(q, m1, m2, D, th, vp, ph, k0=10.0, k_end=30.0):
    m = m1 + m2
    ss = [T.HillsSetup(M=q * m, m1=m1, m2=m2, a=1.0, D=D, theta=a, varphi=b, phase=c)
          for a, b, c in zip(np.broadcast_to(th, np.shape(ph)), np.broadcast_to(vp, np.shape(ph)), ph)]
    o = T.scatter(ss, k0=k0, k_end=k_end)
    # wave 2: corrected energies (E1, E2, dE, outcome) and the definition before (E1_M,
    # E2_M, dE_M, outcome_M) from the same trajectories
    keep = ("outcome", "dE", "E1", "E2", "r12min", "energy_error", "ok", "nacc", "a12", "e1", "e2",
            "outcome_M", "dE_M", "E1_M", "E2_M", "E_tot", "W_end", "inner")
    return {k: o[k] for k in keep}


def restricted(D, th, vp, ph, k0=10.0):
    o = R.run(D, th, vp, ph, k0=k0, k_end=30.0)
    amb = o["ambiguous"] & o["ok"]
    if amb.any():
        o2 = R.run(D, np.broadcast_to(th, np.shape(ph))[amb], np.broadcast_to(vp, np.shape(ph))[amb],
                   np.asarray(ph)[amb], k0=k0, k_end=300.0)
        for k in ("E2", "disrupted", "survived", "ambiguous", "ok"):
            o[k][amb] = o2[k]
    return {k: o[k] for k in ("E2", "disrupted", "survived", "ambiguous", "ok", "rmin")}


# ---------------------------------------------------------------- p3
def p3_task(a):
    q, D = a
    ph = np.linspace(0, 2 * np.pi, 200, endpoint=False)
    if q == 0:
        return a, restricted(D, *PRO, ph)
    return a, full(q, 0.75, 0.25, D, *PRO, ph)


def run_p3(workers):
    run = runlib.start_run("P3: full three-body vs restricted limit, m1/m2=3, coplanar prograde, "
                           "D=1 and 0.1, M/m=1e6..10", cores=workers,
                           preregistered="tracks/F-hills/newton3/JOURNAL.md#P3")
    qs = [0, 1e6, 1e5, 1e4, 1e3, 1e2, 10]
    jobs = [(q, D) for q in qs for D in (1.0, 0.1)]
    with Pool(workers) as pool:
        res = dict(pool.map(p3_task, jobs))
    out = {"q": np.array(qs), "D": np.array([1.0, 0.1]), "phase": np.linspace(0, 2 * np.pi, 200, endpoint=False)}
    for (q, D), o in res.items():
        for k, v in o.items():
            out[f"{k}_q{q:g}_D{D:g}"] = v
    # SKR's single example (prp.tex:624-631)
    ex_r = R.run(0.1, *PRO, np.array([4 * np.pi / 5]), k0=10.0, k_end=30.0)
    ex_f = full(1e6, 0.75, 0.25, 0.1, *PRO, np.array([4 * np.pi / 5]))
    out["example_restricted_E2"] = ex_r["E2"]
    out["example_full_dE"] = ex_f["dE"]
    out["example_full_outcome"] = ex_f["outcome"]
    np.savez_compressed(os.path.join(run["dir"], "p3.npz"), **out)
    print("SKR example: restricted E2 %.6f full dE %.6f rel diff %.2e" %
          (ex_r["E2"][0], ex_f["dE"][0], abs(ex_f["dE"][0] / ex_r["E2"][0] - 1)))
    runlib.finish_run(run)


# ---------------------------------------------------------------- p4
def p4_task(a):
    q, k0 = a
    ph = np.linspace(0, 2 * np.pi, 200, endpoint=False)
    return a, full(q, 0.5, 0.5, 0.5, *PRO, ph, k0=k0)


def run_p4(workers):
    run = runlib.start_run("P4: start-distance sensitivity of the full driver, D=0.5 prograde, "
                           "M/m=1e6 and 10, k0=5..40", cores=workers,
                           preregistered="tracks/F-hills/newton3/JOURNAL.md#P4")
    jobs = [(q, k0) for q in (1e6, 10) for k0 in (5.0, 10.0, 20.0, 40.0)]
    with Pool(workers) as pool:
        res = dict(pool.map(p4_task, jobs))
    out = {"phase": np.linspace(0, 2 * np.pi, 200, endpoint=False)}
    for (q, k0), o in res.items():
        for k, v in o.items():
            out[f"{k}_q{q:g}_k{k0:g}"] = v
    np.savez_compressed(os.path.join(run["dir"], "p4.npz"), **out)
    runlib.finish_run(run)


# ---------------------------------------------------------------- finite q
D_FQ = np.round(np.arange(0.1, 3.01, 0.1), 6)
N_COP, N_ORI_FQ, N_PHA_FQ = 256, 128, 16


def fq_samples(kind):
    if kind == "pro":
        ph = np.linspace(0, 2 * np.pi, N_COP, endpoint=False)
        return np.full(N_COP, PRO[0]), np.full(N_COP, PRO[1]), ph
    if kind == "ret":
        ph = np.linspace(0, 2 * np.pi, N_COP, endpoint=False)
        return np.full(N_COP, RET[0]), np.full(N_COP, RET[1]), ph
    th0, vp0 = fibonacci_sphere(N_ORI_FQ)
    ph0 = np.linspace(0, 2 * np.pi, N_PHA_FQ, endpoint=False)
    return np.repeat(th0, N_PHA_FQ), np.repeat(vp0, N_PHA_FQ), np.tile(ph0, N_ORI_FQ)


def fq_task(a):
    q, kind, D = a
    th, vp, ph = fq_samples(kind)
    if q == 0:
        return a, restricted(D, th, vp, ph)
    return a, full(q, 0.5, 0.5, D, th, vp, ph)


def run_finiteq(workers):
    run = runlib.start_run("finite mass ratio: disruption probability and mean |dE| vs D for "
                           "M/m=10,30,100,1000 (m1=m2) against the restricted limit; coplanar "
                           "and isotropic", cores=workers,
                           preregistered="tracks/F-hills/newton3/JOURNAL.md#P3")
    qs = [0, 10, 30, 100, 1000]
    jobs = [(q, kind, D) for kind in ("iso", "pro", "ret") for q in qs for D in D_FQ[::-1]]
    out = {"q": np.array(qs), "D": D_FQ}
    with Pool(workers) as pool:
        for (q, kind, D), o in pool.imap_unordered(fq_task, jobs):
            for k, v in o.items():
                out[f"{k}_{kind}_q{q:g}_D{D:g}"] = v
            if q == 0:
                pd = o["disrupted"][o["ok"]].mean()
            else:
                settled = (o["outcome"] != T.UNSETTLED) & o["ok"]
                pd = (o["outcome"][settled] != T.SURVIVED).mean()
            print(f"{kind} q={q:g} D={D:g} Pdis={pd:.3f}", flush=True)
    np.savez_compressed(os.path.join(run["dir"], "finiteq.npz"), **out)
    runlib.finish_run(run)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("which", choices=["p3", "p4", "finiteq"])
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    {"p3": run_p3, "p4": run_p4, "finiteq": run_finiteq}[a.which](a.workers)
