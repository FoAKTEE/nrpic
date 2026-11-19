"""Per-dump diagnostics of the crossed-wave runs (verifier2, my own code).

    python3 scan.py OUTDIR LABEL:RUNDIR [LABEL:RUNDIR ...]     (env NWORK, default 8)

For every bin dump (single precision, RUNDIR/bin/*.z4c.*.bin) and every restart dump
(double precision, RUNDIR/rst/*.rst) of each case: the flat transverse-traceless (TT)
amplitudes of h = tilde gamma - delta and of tilde A at K1 = (k,k,0) and K2 = (k,-k,0),
k = 2 pi / L, polarizations e+ = m m - z z, ex = m z + z m with m = (1,-1,0)/sqrt 2 for K1
and m = (1,1,0)/sqrt 2 for K2; cos and sin parts relative to the cell-centre coordinates,
so that h_ij = c e+_ij cos(K.x) + d e+_ij sin(K.x). The full TT projection of h and tilde A
at every wave vector: the total TT power, the fraction in the four box modes +-K1, +-K2,
the largest TT amplitude anywhere; the plane-symmetry quantities max|gyy-gzz|, max|gyz|,
max|gxy|, max|gxz| (same for tilde A); the amplitudes of sin(kx), sin(ky) in chi and alpha
(first-order potentials Phi_1, Phi_2: chi a^2 = 1 + 2 Phi, alpha = a (1 + Phi)).
Writes OUTDIR/<LABEL>.json.
"""
import glob
import json
import os
import sys
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import athio  # noqa: E402

L = 4.0
COMP = [(0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)]


def tensors(v, prefix):
    names = ["xx", "xy", "xz", "yy", "yz", "zz"]
    return [v[prefix + n] for n in names]


def fft6(comps, sub_identity):
    n = comps[0].shape[0]
    out = np.empty((3, 3, n, n, n), dtype=np.complex128)
    for (i, j), c in zip(COMP, comps):
        f = c - (1.0 if (sub_identity and i == j) else 0.0)
        F = np.fft.fftn(f)/n**3
        out[i, j] = F
        out[j, i] = F
    # phase of the cell centres x = (i + 1/2) h
    q = np.fft.fftfreq(n, 1.0/n)
    ph = np.exp(-1j*np.pi*(q[:, None, None] + q[None, :, None] + q[None, None, :])/n)
    return out*ph


def tt(F):
    n = F.shape[2]
    q = np.fft.fftfreq(n, 1.0/n)
    K = np.stack(np.meshgrid(q, q, q, indexing="ij"))
    kk = np.sqrt((K**2).sum(0))
    kk[0, 0, 0] = 1.0
    nv = K/kk
    P = np.eye(3)[:, :, None, None, None] - nv[:, None]*nv[None, :]
    PFP = np.einsum("il...,lm...,mj...->ij...", P, F, P)
    tr = np.einsum("lm...,lm...->...", P, F)
    T = PFP - 0.5*P*tr
    T[:, :, 0, 0, 0] = 0.0
    return T


def pol(F, idx, which):
    s2 = np.sqrt(2.0)
    f = F[:, :, idx[0], idx[1], idx[2]]
    if which == "K1":
        m = np.array([1.0, -1.0, 0.0])/s2
    else:
        m = np.array([1.0, 1.0, 0.0])/s2
    z = np.array([0.0, 0.0, 1.0])
    ep = np.outer(m, m) - np.outer(z, z)
    ex = np.outer(m, z) + np.outer(z, m)
    cp = (f*ep).sum()   # = (c - i d) e+:e+/2 = c - i d
    cx = (f*ex).sum()
    return [cp.real, -cp.imag, cx.real, -cx.imag]


def sin_amp(f, idx):
    F = np.fft.fftn(f)/f.shape[0]**3
    n = f.shape[0]
    ph = np.exp(-1j*np.pi*sum(idx)/n)
    c = F[idx]*ph
    return float(-2.0*c.imag), float(F[0, 0, 0].real)


def analyze(args):
    path, kind = args
    if kind == "bin":
        d = athio.read_bin(path)
        v = {k[4:]: x for k, x in d["var"].items()}
    else:
        d = athio.read_rst_z4c(path)
        v = d["var"]
    n = v["gxx"].shape[0]
    t = d["time"]
    rec = {"file": os.path.basename(path), "kind": kind, "time": t, "cycle": d["cycle"],
           "a_hom": (1.0 + t/2.0)**2, "chi_mean": float(v["chi"].mean()),
           "alpha_mean": float(v["alpha"].mean())}
    i1 = (1, 1, 0)
    i2 = (1, n - 1, 0)
    out = {}
    for name, comps, sub in (("h", tensors(v, "g"), True), ("A", tensors(v, "A"), False)):
        F = fft6(comps, sub)
        T = tt(F)
        pw = (np.abs(T)**2).sum(axis=(0, 1))
        box = sum(pw[i] for i in [i1, i2, (n - 1, n - 1, 0), (n - 1, 1, 0)])
        out[name] = {
            "K1": pol(F, i1, "K1"), "K2": pol(F, i2, "K2"),
            "tt_power": float(pw.sum()), "tt_box_fraction": float(box/pw.sum()) if pw.sum() > 0 else 0.0,
            "tt_max_amp": float(np.sqrt(np.abs(T)**2).max()),
            "traceless_rms": float(np.sqrt(sum(((c - c.mean())**2).mean()*(2 if i != j else 1)
                                              for (i, j), c in zip(COMP, comps)))),
        }
        c = dict(zip(["xx", "xy", "xz", "yy", "yz", "zz"], comps))
        out[name]["max_yy_zz"] = float(np.abs(c["yy"] - c["zz"]).max())
        out[name]["max_yz"] = float(np.abs(c["yz"]).max())
        out[name]["max_xy"] = float(np.abs(c["xy"]).max())
        out[name]["max_xz"] = float(np.abs(c["xz"]).max())
    rec.update(out)
    rec["chi_sin_x"], _ = sin_amp(v["chi"], (1, 0, 0))
    rec["chi_sin_y"], _ = sin_amp(v["chi"], (0, 1, 0))
    rec["alpha_sin_x"], _ = sin_amp(v["alpha"], (1, 0, 0))
    rec["alpha_sin_y"], _ = sin_amp(v["alpha"], (0, 1, 0))
    return rec


def main():
    outdir = sys.argv[1]
    os.makedirs(outdir, exist_ok=True)
    nwork = int(os.environ.get("NWORK", "8"))
    for spec in sys.argv[2:]:
        label, rundir = spec.split(":", 1)
        jobs = [(p, "bin") for p in sorted(glob.glob(os.path.join(rundir, "bin", "*.z4c.*.bin")))]
        jobs += [(p, "rst") for p in sorted(glob.glob(os.path.join(rundir, "rst", "*.rst")))]
        with Pool(nwork) as pool:
            recs = pool.map(analyze, jobs, chunksize=1)
        recs.sort(key=lambda r: (r["kind"], r["time"]))
        with open(os.path.join(outdir, f"{label}.json"), "w") as f:
            json.dump({"label": label, "rundir": rundir, "records": recs}, f)
        nb = sum(r["kind"] == "bin" for r in recs)
        print(f"{label}: {nb} bin, {len(recs) - nb} rst dumps", flush=True)


if __name__ == "__main__":
    main()
