"""P1: initial data of the second round (ledger rows 198, 199) and card-hours (row 216).

Row 198: the two initial-data tools without jitter (make_waves A = 0 against make_east eps0):
largest differences of positions, velocities, masses (relative) and of the nine fields, read
from particles.nrp (NRPIC001) and fields.bin (NRCOSMO1) by the layouts of docs/FORMATS.md.
Row 199: the residuals recorded by the tool in id.json (read, not recomputed).
Row 216: card-hours recorded by the batch manifest and by the Slurm log of the batch.
"""
import json
import os
import re

import numpy as np

SC = "/data/haiyangw/nrpic/scratch/B-emd-gw"
WT = "/data/haiyangw/nrpic/wt/B-emd-gw"
OUT = os.environ.get("NRPIC_RUN_DIR", f"{SC}/tmp/p1")
os.makedirs(OUT, exist_ok=True)


def read_nrp(p):
    raw = np.fromfile(p, np.uint8)
    assert raw[:8].tobytes() == b"NRPIC001"
    n = int(raw[8:16].view(np.int64)[0])
    rec = raw[16:16 + 56 * n].view(np.float64).reshape(n, 7)
    sp = raw[16 + 56 * n:16 + 60 * n].view(np.int32)
    assert raw.size == 16 + 60 * n
    return rec, sp


def read_fields(p):
    raw = np.fromfile(p, np.uint8)
    assert raw[:8].tobytes() == b"NRCOSMO1"
    n = raw[8:32].view(np.int64)
    nc = int(np.prod(n))
    arr = raw[32:32 + 72 * nc].view(np.float64).reshape(9, nc)
    assert raw.size == 32 + 72 * nc
    return n, arr


res = {}
a = f"{SC}/B-20261119-141216-9c98929/jit0"
b = f"{SC}/B-20261115-161656-03d75e1/eps0"
ra, sa = read_nrp(f"{a}/particles.nrp")
rb, sb = read_nrp(f"{b}/particles.nrp")
na, fa = read_fields(f"{a}/fields.bin")
nb, fb = read_fields(f"{b}/fields.bin")
names = ["psi", "K", "alpha", "Axx", "Axy", "Axz", "Ayy", "Ayz", "Azz"]
res["row198"] = {"N": [len(ra), len(rb)], "max_dx": float(np.abs(ra[:, :3] - rb[:, :3]).max()),
                 "max_du": float(np.abs(ra[:, 3:6] - rb[:, 3:6]).max()),
                 "max_dm_rel": float(np.abs(ra[:, 6] / rb[:, 6] - 1).max()),
                 "species_equal": bool(np.array_equal(sa, sb)),
                 "fields_n": [na.tolist(), nb.tolist()],
                 "fields_maxabs_diff": {nm: float(np.abs(fa[i] - fb[i]).max()) for i, nm in enumerate(names)},
                 "bytes_identical_particles": bool(open(f"{a}/particles.nrp", "rb").read() == open(f"{b}/particles.nrp", "rb").read()),
                 "bytes_identical_fields": bool(open(f"{a}/fields.bin", "rb").read() == open(f"{b}/fields.bin", "rb").read())}
ic = {}
for c in ("jit0p3", "jit0p1", "jit0"):
    with open(f"{SC}/B-20261119-141216-9c98929/{c}/id.json") as f:
        j = json.load(f)
    ic[c] = {k: j.get(k) for k in ("max_momentum_residual", "max_hamiltonian_residual", "max_hamiltonian_term",
                                   "jitter", "seed", "N", "delta", "ratios")}
res["row199_idjson"] = ic
# also the masses and positions of the jittered lattice: jitter along y, z only, bounded by A h
for c, A in (("jit0p3", 0.3), ("jit0p1", 0.1)):
    r, _ = read_nrp(f"{SC}/B-20261119-141216-9c98929/{c}/particles.nrp")
    d = r[:, :3] - ra[:, :3]
    d = (d + 2.0) % 4.0 - 2.0
    res.setdefault("jitter_check", {})[c] = {"max_dx_over_h": float(np.abs(d[:, 0]).max() / 0.0625),
                                            "max_dy_over_h": float(np.abs(d[:, 1]).max() / 0.0625),
                                            "max_dz_over_h": float(np.abs(d[:, 2]).max() / 0.0625),
                                            "rms_dy_over_h": float(np.sqrt(np.mean(d[:, 1] ** 2)) / 0.0625)}
m = json.load(open(f"{WT}/tracks/B-emd-gw/runs/B-20261119-142833-19edd82/manifest.json"))
res["row216"] = {"manifest_resources": m.get("resources"), "wall": m.get("wall_time_s", m.get("resources", {}).get("wall_s"))}
logs = [f for f in os.listdir(f"{SC}/B-20261119-142833-19edd82") if f.startswith("batch.list.slurm")]
txt = open(f"{SC}/B-20261119-142833-19edd82/{logs[0]}").read() if logs else ""
res["row216"]["slurm_log_tail"] = txt[-1500:]
with open(os.path.join(OUT, "p1_ic.json"), "w") as f:
    json.dump(res, f, indent=1)
print(json.dumps(res, indent=1))
