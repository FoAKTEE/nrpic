#!/usr/bin/env python3
"""V0: the verifier's readers, TT projector and FoF on analytic cases (before any claim).

    python3 v0_tests.py OUTDIR
Writes OUTDIR/v0_tests.json; exit status 1 if a test fails.
"""
import json
import os
import struct
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vlib  # noqa: E402

out = sys.argv[1] if len(sys.argv) > 1 else "."
os.makedirs(out, exist_ok=True)
rng = np.random.default_rng(20261127)
res = {}


def check(name, val, bound):
    ok = bool(val <= bound)
    res[name] = {"value": float(val), "bound": bound, "pass": ok}
    print(f"{name:40s} {val:.3e} <= {bound:.1e}  {'PASS' if ok else 'FAIL'}")


# 1. synthetic AthenaK binary dump, 2x2x2 meshblocks written in shuffled order ------------
N, nb = 16, 8
L = 2.0
x = (np.arange(N) + 0.5)*L/N - 1.0
Z, Y, X = np.meshgrid(x, x, x, indexing="ij")
fA = np.sin(2*np.pi*X/L) + 0.3*np.cos(2*np.pi*(2*Y + Z)/L)
fB = X*Y - Z
fn = os.path.join(out, "synthetic.bin")
names = ["vA", "vB"]
pre = ("Athena binary output version=1.1\n  size of preheader=5\n  time=1.25e+00\n"
       "  cycle=7\n  size of location=8\n  size of variable=8\n  number of variables=2\n"
       "  variables:  vA  vB  \n")
par = "<mesh>\nnx1 = 16\n"
blocks = [(i, j, k) for k in range(2) for j in range(2) for i in range(2)]
rng.shuffle(blocks)
with open(fn, "wb") as f:
    f.write(pre.encode())
    f.write(f"  header offset={len(par)}\n".encode())
    f.write(par.encode())
    for (i, j, k) in blocks:
        f.write(struct.pack("10i", 4, 11, 4, 11, 4, 11, i, j, k, 0))
        f.write(struct.pack("6d", -1 + i, i, -1 + j, j, -1 + k, k))
        for arr in (fA, fB):
            f.write(arr[k*nb:(k+1)*nb, j*nb:(j+1)*nb, i*nb:(i+1)*nb].astype(np.float64).tobytes())
d, h = vlib.read_mesh(fn, names)
check("mesh reader vA max diff", np.abs(d["vA"] - fA).max(), 0.0)
check("mesh reader vB max diff", np.abs(d["vB"] - fB).max(), 0.0)
check("mesh reader time", abs(h["time"] - 1.25), 0.0)

# 2. synthetic particle snapshot ----------------------------------------------------------
n = 1000
rec = rng.normal(size=(n, 7))
tag = np.arange(n, dtype=np.int32)[::-1].copy()
fnp = os.path.join(out, "synthetic.part.bin")
with open(fnp, "wb") as f:
    f.write(b"NRPSNAP1")
    f.write(np.float64(3.5).tobytes())
    f.write(np.int64(n).tobytes())
    f.write(np.int64(42).tobytes())
    f.write(rec.tobytes())
    f.write(tag.tobytes())
    f.write(np.zeros(n, np.int32).tobytes())
    f.write(rec[:, 0].tobytes())
s = vlib.read_snapshot(fnp)
check("particle reader x", np.abs(s["x"] - rec[:, :3]).max(), 0.0)
check("particle reader m", np.abs(s["m"] - rec[:, 6]).max(), 0.0)
check("particle reader tag", float(np.abs(s["tag"] - tag).max()), 0.0)
check("particle reader t", abs(s["t"] - 3.5), 0.0)

# 3. history reader with a repeated row -----------------------------------------------------
fnh = os.path.join(out, "synthetic.hst")
with open(fnh, "w") as f:
    f.write("# test\n# [1]=time [2]=q\n0 1\n1 2\n2 3\n# [1]=time [2]=q\n1 20\n2 30\n3 40\n")
hh = vlib.read_hst(fnh)
check("hst reader keeps last repeated rows",
      float(np.abs(hh["q"] - np.array([1, 20, 30, 40])).max() + np.abs(hh["time"] - np.arange(4)).max()), 0.0)

# 4. TT projector ---------------------------------------------------------------------------
N = 32
L = 8.0
KX, KY, KZ = vlib.kgrid((N, N, N), L)
# Nyquist planes are excluded everywhere (a real field's Nyquist modes cannot carry a
# direction-dependent projection with Hermitian symmetry); zero them in the test inputs
NYQ = (np.abs(KX) == N//2) | (np.abs(KY) == N//2) | (np.abs(KZ) == N//2)
rnd = {(i, j): np.where(NYQ, 0, np.fft.rfftn(rng.normal(size=(N, N, N)))) for _, i, j in vlib.COMP}
T = vlib.tt_project(rnd, KX, KY, KZ)
hTT = {key: np.fft.irfftn(T[key], s=(N, N, N), axes=(0, 1, 2)) for key in T}
# idempotence and the energy identity on a field that is TT by construction
p, *_ = vlib.tt_power(hTT, L)
direct = sum((1.0 if i == j else 2.0)*(hTT[i, j]**2).mean() for _, i, j in vlib.COMP)
check("TT: energy of a TT field (rel)", abs(p.sum() - direct)/direct, 1e-12)
T2 = vlib.tt_project({k: np.fft.rfftn(v) for k, v in hTT.items()}, KX, KY, KZ)
num = sum(np.abs(T2[k] - np.fft.rfftn(hTT[k])).max() for k in T2)
den = max(np.abs(np.fft.rfftn(hTT[k])).max() for k in T2)
check("TT: idempotent (rel)", num/den, 1e-12)
# transversality and tracelessness of the output
kv = [KX, KY, KZ]
Tf = {k: np.fft.rfftn(v) for k, v in hTT.items()}
div = max(np.abs(sum(kv[i]*Tf[min(i, j), max(i, j)] for i in range(3))).max() for j in range(3))
tr = np.abs(Tf[0, 0] + Tf[1, 1] + Tf[2, 2]).max()
check("TT: k_i h_ij (rel)", div/(den*N/2), 1e-12)
check("TT: trace (rel)", tr/den, 1e-12)
# pure gauge d_i xi_j + d_j xi_i and pure trace delta_ij phi give no TT power
xi = [np.where(NYQ, 0, np.fft.rfftn(rng.normal(size=(N, N, N)))) for _ in range(3)]
G = {(i, j): 1j*(kv[i]*xi[j] + kv[j]*xi[i]) for _, i, j in vlib.COMP}
gr = {k: np.fft.irfftn(v, s=(N, N, N), axes=(0, 1, 2)) for k, v in G.items()}
pg, *_ = vlib.tt_power(gr, L)
ref = sum((gr[k]**2).mean() for k in gr)
check("TT: pure gauge removed (rel)", pg.sum()/ref, 1e-24)
phi = rng.normal(size=(N, N, N))
tf = {(i, j): (phi if i == j else 0*phi) for _, i, j in vlib.COMP}
pt, *_ = vlib.tt_power(tf, L)
check("TT: trace field removed (rel)", pt.sum()/(3*(phi**2).mean()), 1e-24)

# 5. FoF on Plummer clumps (one across the periodic boundary) and a sparse background -------
L = 10.0
cent = np.array([[2.0, 2.0, 2.0], [7.0, 3.0, 6.0], [0.05, 5.0, 9.95], [5.0, 8.0, 1.0]])
npc = [400, 250, 300, 120]
pts, truth = [], []
for c, (cc, nn) in enumerate(zip(cent, npc)):
    r = 0.05*rng.standard_normal((nn, 3))
    pts.append(np.mod(cc + r, L))
    truth += [c]*nn
bg = rng.uniform(0, L, size=(2000, 3))
dmin = np.min([np.linalg.norm((bg - c + L/2) % L - L/2, axis=1) for c in cent], axis=0)
bg = bg[dmin > 1.0][:500]
pts.append(bg)
truth += [-1]*500
xp = np.vstack(pts)
truth = np.array(truth)
cnt, msum, lab, order = vlib.halo_counts(xp, np.ones(len(xp)), L, 0.1, 50)
mism = 0
for c in range(len(npc)):
    labs = np.unique(lab[truth == c])
    mism += (len(labs) != 1)
ok_counts = sorted(cnt.tolist()) == sorted(npc)
check("FoF: clumps found, one label each", float(mism + (0 if ok_counts else 1)), 0.0)
res["fof_counts"] = cnt.tolist()

json.dump(res, open(os.path.join(out, "v0_tests.json"), "w"), indent=1)
nfail = sum(1 for v in res.values() if isinstance(v, dict) and not v["pass"])
print("failed:", nfail)
sys.exit(1 if nfail else 0)
