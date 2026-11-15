"""P5: convergence of the restricted results with tolerance, end radius and start radius.

(a) rtol in {1e-10, 1e-12, 1e-13} for D in {1e-5, 1.8e-5, 3.2e-5, 1e-4, 1e-3, 0.1, 1},
    coplanar prograde, 600 phases in [0, pi);
(b) k_end in {30, 100} and k0 in {10, 20} at rtol 1e-10 for D in {1e-3, 0.1, 1, 2}.
Run: cd tracks/F-hills/newton3 && OMP_NUM_THREADS=1 python3 scripts/convergence.py [--workers 8]
"""
import argparse
import json
import os
import sys
import numpy as np
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from hills3 import restricted as R  # noqa: E402
import runlib  # noqa: E402

PH = np.linspace(0, np.pi, 600, endpoint=False)


def task(a):
    D, rtol, k0, k_end = a
    o = R.run(D, np.pi / 2, np.pi / 2, PH, k0=k0, k_end=k_end, rtol=rtol, atol=rtol * 1e-3)
    ok = o["ok"]
    d = o["disrupted"] & ok
    return a, {"P": float(d.sum() / ok.sum()), "Emean": float(np.abs(o["E2"][d]).mean()),
               "E2": o["E2"].tolist(), "dis": o["disrupted"].tolist(), "ok": ok.tolist(),
               "fail": int((~ok).sum()), "amb": int((o["ambiguous"] & ok).sum())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()
    run = runlib.start_run("P5: convergence of restricted results with rtol, end radius and start "
                           "radius", cores=args.workers,
                           preregistered="tracks/F-hills/newton3/JOURNAL.md#P5")
    jobs = [(D, rt, 10.0, 30.0) for D in (1e-5, 1.8e-5, 3.2e-5, 1e-4, 1e-3, 0.1, 1.0)
            for rt in (1e-10, 1e-12, 1e-13)]
    jobs += [(D, 1e-10, k0, ke) for D in (1e-3, 0.1, 1.0, 2.0) for k0, ke in
             ((10.0, 30.0), (10.0, 100.0), (20.0, 30.0))]
    jobs = list(dict.fromkeys(jobs))
    with Pool(args.workers) as pool:
        res = dict(pool.map(task, jobs))
    out = {f"D={a[0]:g} rtol={a[1]:g} k0={a[2]:g} k_end={a[3]:g}": v for a, v in res.items()}
    with open(os.path.join(run["dir"], "convergence.json"), "w") as fh:
        json.dump(out, fh)
    for k, v in out.items():
        print(f"{k:42s} P={v['P']:.4f} <|E|>={v['Emean']:.4f} fail={v['fail']} amb={v['amb']}")
    runlib.finish_run(run)


if __name__ == "__main__":
    main()
