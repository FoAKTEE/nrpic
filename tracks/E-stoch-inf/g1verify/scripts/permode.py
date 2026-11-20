"""Pass over the dumps of p runs: box means and R^NR_n per mode (g1verify, V1-V3).

usage: permode.py OUTDIR KEY [KEY ...]      (KEY = catalogue name, e.g. L32p, P256)
Writes OUTDIR/permode_<KEY>.npz: time, cycle, means of phi, Pi, chi, K, alpha per dump,
wave vectors n (hemisphere, |n|^2 <= nmax2), R^NR_n per dump (complex), and the parts of
the lowest modes; and checks the sha256 of every dump read against the run's
sha256sums.txt (the files are read once, sequentially, eleven of 22 variables).
"""
import os
import sys
import time
import json
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nrsf, alpha as A, rnr, catalog as C  # noqa: E402

out = sys.argv[1]
keys = sys.argv[2:]
os.makedirs(out, exist_ok=True)
runs = C.catalog()
VARS = ["phi", "Pi", "chi", "K", "alpha"] + rnr.GT
log = {}
for key in keys:
    r = runs[key]
    if not r["metric"]:
        raise SystemExit(f"{key}: dumps without gt_ij")
    sums = C.sums(r["run_id"])
    nv = A.hemisphere(r["nmax2"])
    files = nrsf.dumps(r["dir"])
    T, CY, M, RN = [], [], [], []
    shaok = []
    t0 = time.time()
    for p in files:
        fld, digest, h = nrsf.read_hashed(p, VARS)     # one sequential pass, hashed
        rel = os.path.relpath(p, os.path.join(C.SCR, r["run_id"]))
        shaok.append(sums.get(rel) == digest)
        Rn, m = rnr.rnr_coefficients(fld, nv)
        T.append(h["time"])
        CY.append(h["cycle"])
        M.append([m[k] for k in ("phi", "Pi", "chi", "K", "alpha")])
        RN.append(Rn)
        del fld
        print(f"{key} {os.path.basename(p)} t={h['time']:.4f} sha_ok={shaok[-1]} {time.time()-t0:.0f}s",
              flush=True)
    np.savez(os.path.join(out, f"permode_{key}.npz"), time=np.array(T), cycle=np.array(CY),
             means=np.array(M), n=nv, R=np.array(RN))
    log[key] = dict(run_id=r["run_id"], dir=r["dir"], ndumps=len(files), sha_all_ok=bool(all(shaok)),
                    sha_ok=shaok, nmodes=int(len(nv)), seconds=time.time() - t0)
with open(os.path.join(out, "permode_" + "_".join(keys) + ".json"), "w") as f:
    json.dump(log, f, indent=1)
print(json.dumps({k: {kk: v[kk] for kk in ("ndumps", "sha_all_ok", "seconds")} for k, v in log.items()}))
