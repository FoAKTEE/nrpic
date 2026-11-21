import sys, math, numpy as np, multiprocessing as mp
sys.path.insert(0, "/data/haiyangw/nrpic/wt/D-bh-dress/tracks/D-bh-dress/verifier_g1")
import v4_kerr_stat as W
d = np.load("/data/haiyangw/nrpic/scratch/D-bh-dress/D-bh-dress-20261115-172646-ed6a510/expected.npz")
x, mu, nx = d["x"], d["mu"], d["n_x"]
pts = [(i, j) for i in (22, 24, 26, 30, 36) for j in (0, 3, 5, 7, 8)]
def job(p):
    i, j = p
    r = float(np.exp(x[i])); m = float(mu[j])
    R = W.Ref(0.99, nE=40, nL=40, npsi=16)
    v, _ = R.n_over_sin(r, m)
    return r, m, v, nx[i, j] / (2 * math.pi * r)
with mp.get_context("fork").Pool(2) as pool:
    for r, m, v, t in pool.map(job, pts):
        print("r %.3f mu %.3f mine %.4g track-grid %.4g ratio %.4f" % (r, m, v, t, v / t if t else float('nan')), flush=True)
