"""One pass over the dumps of a 256^3 (or smaller) run of the reproduction of arXiv:2512.14649.

For each selected dump it writes <out>/<label>/d<NNNNN>.npz with
- the box means and the percentiles (figlib.QUANT) over the lattice of the contrasts
  phi/<phi> - 1, Pi/<Pi> - 1, K/<K> - 1, of R^NR(x) and, where the dump has them, of |H|/[H],
  |H - <H>|/[H], |M|/[M] (Figs. 2, 4; P1:444-463);
- binned spectra (lattice shells, hemisphere count) of R^NR, K, Kt (sum_ij |Kt_ij(k)|^2 with
  Kt_ij = At_ij/chi) and sqrt(3 Kt_ij Kt^ij/2) (Figs. 3, 5, 6; P1:451-470, 549-561);
- per injected shell (|n|^2 <= nmax2): sums of |c_NR|^2, |c_lin|^2, |c_NR - c_lin|^2 over the modes,
  c_lin = s L^-3/2 W R_k alpha_n from the lockstep `.modes` file of the dump (Figs. 3, 5, 7, 9).

R^NR: the linear extraction of ladder_lib.curvature on the whole lattice,
R = c[chi]/(2<chi>) + (1/4) khat_i khat_j c[gt_ij] + (H_b/Pi_b) c[phi], H_b = -<K>/(3<alpha>).

Usage: dumppass.py --run DIR --base sr --label P256v6 --out OUTDIR [--dumps 0,17 | --every 2]
       [--seed 20261115] [--scale 1.0] [--workers 3] [--fft-workers 2] [--no-spectra]
"""
import argparse
import json
import os
import sys
import time

import numpy as np
from scipy import fft as sfft

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figlib as fl  # noqa: E402

GPAIRS = (("gxx", 0, 0, 1.0), ("gyy", 1, 1, 1.0), ("gzz", 2, 2, 1.0),
          ("gxy", 0, 1, 2.0), ("gxz", 0, 2, 2.0), ("gyz", 1, 2, 2.0))
APAIRS = (("Axx", 0, 0, 1.0), ("Ayy", 1, 1, 1.0), ("Azz", 2, 2, 1.0),
          ("Axy", 0, 1, 2.0), ("Axz", 0, 2, 2.0), ("Ayz", 1, 2, 2.0))
BASE_VARS = ["phi", "Pi", "chi", "K", "alpha"] + [g[0] for g in GPAIRS]
A_VARS = [a[0] for a in APAIRS]
C_VARS = ["H", "Mx", "My", "Mz", "Hmag", "Mmag"]


def one_dump(path, args, shells_cache={}):
    t0 = time.time()
    h = fl.ll.read_header(path)
    N = h["nx"][0]
    have = set(h["names"])
    want = list(BASE_VARS)
    if not args.no_spectra:
        want += [a for a in A_VARS if a in have]
    cons = all(c in have for c in C_VARS)
    if cons:
        want += C_VARS
    elif "H" in have:
        want += ["H", "Mx", "My", "Mz"]
    _, f = fl.ll.read_dump(path, want)
    t_read = time.time() - t0
    out = dict(time=h["time"], cycle=h["cycle"], N=N)
    mean = {v: float(f[v].mean()) for v in ["phi", "Pi", "K", "chi", "alpha"]}
    out.update({f"mean_{k}": v for k, v in mean.items()})
    out["efolds_chi"] = -0.5 * np.log(mean["chi"])
    for v in ["phi", "Pi", "K"]:
        out[f"pct_d{v}"] = fl.percentiles(f[v] / mean[v] - 1.0)
    # R^NR on the whole lattice
    W = args.fft_workers
    rf = lambda a: sfft.rfftn(a, workers=W)  # noqa: E731
    kz = np.fft.fftfreq(N, 1.0 / N)[:, None, None]
    ky = np.fft.fftfreq(N, 1.0 / N)[None, :, None]
    kx = np.arange(N // 2 + 1, dtype=float)[None, None, :]
    k2 = kx * kx + ky * ky + kz * kz
    k2[0, 0, 0] = 1.0
    kv = (kx, ky, kz)
    hb = -mean["K"] / (3.0 * mean["alpha"])
    F = rf(f["chi"]) / (2.0 * mean["chi"]) + (hb / mean["Pi"]) * rf(f["phi"])
    for name, i, j, w in GPAIRS:
        F += 0.25 * w * (kv[i] * kv[j] / k2) * rf(f[name])
    F[0, 0, 0] = 0.0
    Rx = sfft.irfftn(F, s=(N,) * 3, workers=W)
    out["pct_R"] = fl.percentiles(Rx)
    out["rms_R"] = float(np.sqrt(np.mean(Rx * Rx)))
    del Rx
    # constraints per cell
    if "H" in f:
        Mn = np.sqrt(f["Mx"] ** 2 + f["My"] ** 2 + f["Mz"] ** 2)
        out["mean_H"] = float(f["H"].mean())
        out["rms_H"] = float(np.sqrt(np.mean(f["H"] ** 2)))
        out["mean_absM"] = float(Mn.mean())
        if cons:
            rH = np.abs(f["H"]) / f["Hmag"]
            out["pct_H"] = fl.percentiles(rH)
            out["avg_H"] = float(rH.mean())
            rH0 = np.abs(f["H"] - out["mean_H"]) / f["Hmag"]
            out["pct_H0"] = fl.percentiles(rH0)
            out["avg_H0"] = float(rH0.mean())
            rM = Mn / f["Mmag"]
            out["pct_M"] = fl.percentiles(rM)
            out["avg_M"] = float(rM.mean())
            out["mean_Hmag"] = float(f["Hmag"].mean())
            out["mean_Mmag"] = float(f["Mmag"].mean())
            del rH, rH0, rM
        del Mn
    if not args.no_spectra:
        if N not in shells_cache:
            shells_cache[N] = fl.Shells(N)
        sh = shells_cache[N]
        fac = sh.delta_factor() / float(N) ** 6
        out["shell_n2"] = sh.n2
        out["shell_count"] = sh.count

        def spec(Fa):
            return sh.bin(fac * (Fa.real ** 2 + Fa.imag ** 2))

        out["specR_mean"], out["specR_min"], out["specR_max"] = spec(F)
        FK = rf(f["K"])
        FK[0, 0, 0] = 0.0
        out["specK_mean"], out["specK_min"], out["specK_max"] = spec(FK)
        del FK
        if all(a in f for a in A_VARS):
            pKt = np.zeros(F.shape)
            ichi = 1.0 / f["chi"]
            for name, i, j, w in APAIRS:
                Fa = rf(f[name] * ichi)
                Fa[0, 0, 0] = 0.0
                pKt += w * (Fa.real ** 2 + Fa.imag ** 2)
            out["specKt_mean"], out["specKt_min"], out["specKt_max"] = sh.bin(fac * pKt)
            del pKt, ichi
            # Kt_ij Kt^ij = At_ij At^ij with the conformal inverse metric (det gt = 1)
            g = {n: f[n] for n, _, _, _ in GPAIRS}
            gi = dict(xx=g["gyy"] * g["gzz"] - g["gyz"] ** 2,
                      yy=g["gxx"] * g["gzz"] - g["gxz"] ** 2,
                      zz=g["gxx"] * g["gyy"] - g["gxy"] ** 2,
                      xy=g["gxz"] * g["gyz"] - g["gxy"] * g["gzz"],
                      xz=g["gxy"] * g["gyz"] - g["gxz"] * g["gyy"],
                      yz=g["gxy"] * g["gxz"] - g["gxx"] * g["gyz"])
            det = g["gxx"] * gi["xx"] + g["gxy"] * gi["xy"] + g["gxz"] * gi["xz"]
            for kk in gi:
                gi[kk] = gi[kk] / det
            A = {"xx": f["Axx"], "yy": f["Ayy"], "zz": f["Azz"], "xy": f["Axy"],
                 "xz": f["Axz"], "yz": f["Ayz"]}

            def comp(a, b):
                key = "".join(sorted(a + b))
                return key

            # Aup^ij = gi^ik gi^jl A_kl; AA = A_ij Aup^ij
            idx = "xyz"
            AA = np.zeros_like(f["chi"])
            for i in idx:
                for j in idx:
                    Aup = np.zeros_like(f["chi"])
                    for k in idx:
                        for l in idx:
                            Aup += gi[comp(i, k)] * gi[comp(j, l)] * A[comp(k, l)]
                    AA += A[comp(i, j)] * Aup
                    del Aup
            Q = np.sqrt(1.5 * np.maximum(AA, 0.0))
            out["mean_Q"] = float(Q.mean())
            out["mean_det_gt"] = float(det.mean())
            FQ = rf(Q)
            FQ[0, 0, 0] = 0.0
            out["specQ_mean"], out["specQ_min"], out["specQ_max"] = spec(FQ)
            del FQ, Q, AA, gi, g
        # injected modes against the lockstep linear reference
        mpath = path[:-len(".dump")] + ".modes"
        if os.path.exists(mpath):
            md = fl.read_modes_file(mpath)
            nmax2 = int(md["n2"].max())
            modes = fl.ll.Modes(N, nmax2)
            alpha = fl.alpha_modes(modes, args.seed)
            c_nr = F[modes.iz, modes.iy, modes.ix] * modes.shift / float(N) ** 3
            idx = np.searchsorted(md["n2"], modes.n2)
            assert np.array_equal(md["n2"][idx], modes.n2)
            wk = fl.window(modes.k, md["a"], md["H"])
            c_lin = args.scale * fl.L_BOX ** -1.5 * wk * md["R"][idx] * alpha
            sn = modes.shell_of
            nsh = modes.shell_n2.size
            out["inj_n2"] = modes.shell_n2
            out["inj_count"] = np.bincount(sn, minlength=nsh)
            out["inj_pnr"] = np.bincount(sn, weights=np.abs(c_nr) ** 2, minlength=nsh)
            out["inj_plin"] = np.bincount(sn, weights=np.abs(c_lin) ** 2, minlength=nsh)
            out["inj_pdiff"] = np.bincount(sn, weights=np.abs(c_nr - c_lin) ** 2, minlength=nsh)
            out["inj_W"] = fl.window(np.sqrt(modes.shell_n2.astype(float)), md["a"], md["H"])
            # MS expectation per shell (unwindowed, P1's dashed line), Delta = k^3 |R_k|^2/(2 pi^2)
            out["ms_n2"] = md["n2"]
            out["ms_delta"] = md["n2"].astype(float) ** 1.5 * np.abs(md["R"]) ** 2 / (2 * np.pi ** 2)
            out["ms_a"], out["ms_H"] = md["a"], md["H"]
            out["ms_eps1"], out["ms_eps2"] = md["eps1"], md["eps2"]
            out["ms_time"] = md["time"]
            # largest per-mode deviation among modes with W > 1/2 (rms and max of |dc|/|c_lin|)
            sel = wk > 0.5
            if sel.any():
                rel = np.abs(c_nr[sel] - c_lin[sel]) / np.abs(c_lin[sel])
                out["inj_rel_rms"] = float(np.sqrt(np.mean(rel ** 2)))
                out["inj_rel_max"] = float(rel.max())
    out["t_read_s"] = t_read
    out["t_total_s"] = time.time() - t0
    return out


def worker(task):
    path, outpath, args = task
    if os.path.exists(outpath) and not args.redo:
        return outpath, "exists"
    res = one_dump(path, args)
    np.savez(outpath, **{k: np.asarray(v) for k, v in res.items()})
    return outpath, f"t={res['time']:.4f} read {res['t_read_s']:.0f}s total {res['t_total_s']:.0f}s"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--base", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dumps", default=None, help="comma-separated dump indices")
    ap.add_argument("--every", type=int, default=1)
    ap.add_argument("--last", action="store_true", help="only the last dump")
    ap.add_argument("--seed", type=int, default=20261115)
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--fft-workers", type=int, default=2)
    ap.add_argument("--no-spectra", action="store_true")
    ap.add_argument("--redo", action="store_true")
    args = ap.parse_args()
    files = fl.dump_files(args.run, args.base)
    if not files:
        raise SystemExit(f"no dumps {args.base}.sf.*.dump in {args.run}")
    if args.dumps:
        want = {int(x) for x in args.dumps.split(",")}
        files = [p for p in files if int(p.split(".")[-2]) in want]
    elif args.last:
        files = files[-1:]
    else:
        files = files[::args.every] if files[-1] in files[::args.every] else \
            files[::args.every] + files[-1:]
    od = os.path.join(args.out, args.label)
    os.makedirs(od, exist_ok=True)
    with open(os.path.join(od, "meta.json"), "w") as fp:
        json.dump(dict(run=args.run, base=args.base, seed=args.seed, scale=args.scale,
                       dumps=[os.path.basename(p) for p in files]), fp, indent=1)
    tasks = [(p, os.path.join(od, "d" + p.split(".")[-2] + ".npz"), args) for p in files]
    if args.workers > 1:
        from multiprocessing import Pool
        with Pool(args.workers) as pool:
            for o, msg in pool.imap_unordered(worker, tasks):
                print(os.path.basename(o), msg, flush=True)
    else:
        for t in tasks:
            o, msg = worker(t)
            print(os.path.basename(o), msg, flush=True)


if __name__ == "__main__":
    main()
