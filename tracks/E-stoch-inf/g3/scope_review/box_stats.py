"""Scope review of G3 (items 1 and 4): an independent reader of existing 128^3 USR output.

Own parsers of the scalar-field dump (layout NRSFDMP2, coord/INTERFACES/scalar_field_2.md section 4) and of
the lockstep record `.modes`; R^NR from its definition in SCOPE 4d.1 (i):
    R^NR = dchi / (2 <chi>) + (1/4) khat_i khat_j dgt_ij + (H_b / Pi_b) dphi,   H_b = -<K> / (3 <alpha>),
formed in Fourier space with the k = 0 mode removed (no code of g3/ or ladder/ is used). sigma_lin from the
record: sum over every lattice vector 1 <= |n|^2 <= nmax2 of |W_n R_n|^2 L^-3, W = (1 + tanh(5 ln(sigma a H/k)))/2,
sigma = 1, L = 2 pi (the deck's window and box).

Per run (a mirrored pair, s = +1 and s = -1 of the same seed):
  1. one-point statistics of x = R^NR / sigma_lin: variance ratio, skewness, excess kurtosis, F_pm(nu) at
     nu = 2, 3, 4, 4.5, 5, with block-jackknife errors (8^3 blocks of 16^3 cells);
  2. the effective number of independent cells of F(nu), from the Gaussian two-point formula
     Var F = N^-3 sum_r [P2(nu, nu; rho(r)) - Q(nu)^2], P2 = Q(nu) - 2 T(nu, sqrt((1 - rho)/(1 + rho)))
     (Owen's T), with rho(r) both from the record's spectrum (ensemble) and measured on the box;
     n_eff = Q (1 - Q) / Var F; and from the block scatter;
  3. the part of Var F that is the scatter of the box variance: Var(s2_box)/sigma^4 = 2 N^-3 sum_r rho^2,
     dF/dln s2 = nu phi(nu)/2 at a fixed threshold; Gaussian standard errors of skewness and kurtosis per box,
     (6 N^-3 sum rho^3)^1/2 and (24 N^-3 sum rho^4)^1/2.
For the pair: odd part O = (R+ - R-)/2, even part E = (R+ + R-)/2 (the even part is the part of R^NR that is
even in the noise amplitude, second order and higher); the local quadratic coefficient a_R = cov(E, O^2) /
var(O^2) (R = O + a_R (O^2 - <O^2>) + ...), the skewness it implies, 6 a_R sigma, and the mean of the two
skewnesses (the odd-in-s sample fluctuation of the skewness cancels in it). The same for the chi term alone,
the phi term alone, and for the variant with the chi term in logarithmic form, (1/2)(ln chi - <ln chi>).
The one-patch delta-N reference of the 128 band (run E-20261125-115707-b845282) has skewness 0.023 (lattice
variant) to 0.028 (continuum), i.e. a = skew/(6 sigma) = 0.008 to 0.0095.

Usage: box_stats.py OUTDIR --plus DIR --minus DIR [--dump 20] [--base usr] [--workers 2]
Writes OUTDIR/box_stats.json and OUTDIR/fig_box_stats.{pdf,png}.
"""
import argparse
import json
import os
import struct
import sys

import numpy as np
from scipy import fft as sfft
from scipy.special import owens_t
from scipy.stats import norm

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python", "nrpic"))
import figstyle as fs  # noqa: E402

L_BOX = 2.0 * np.pi
SHARP, SIGMA_W = 5.0, 1.0
NUS = (2.0, 3.0, 4.0, 4.5, 5.0)
GIJ = (("gxx", 0, 0, 1.0), ("gyy", 1, 1, 1.0), ("gzz", 2, 2, 1.0),
       ("gxy", 0, 1, 2.0), ("gxz", 0, 2, 2.0), ("gyz", 1, 2, 2.0))
REF_SKEW = {"lattice": 0.0231, "continuum": 0.0282}   # ref_inflection_n32.json, s0.01(_lattice), Ne


# ------------------------------------------------------------------ own readers
def read_dump(path, want):
    """NRSFDMP2: magic, int64 nmb nx1 nx2 nx3 nvar cycle nnoise, double time, nvar names (16 bytes);
    per MeshBlock int64 level lx1 lx2 lx3, double x1min..x3max, nvar arrays nx3 x nx2 x nx1 (x fastest)."""
    with open(path, "rb") as fp:
        if fp.read(8) != b"NRSFDMP2":
            raise ValueError("not NRSFDMP2")
        nmb, nx1, nx2, nx3, nvar, cycle, nnoise = struct.unpack("<7q", fp.read(56))
        time = struct.unpack("<d", fp.read(8))[0]
        names = [fp.read(16).split(b"\0")[0].decode() for _ in range(nvar)]
        start = fp.tell()
        cells = nx1 * nx2 * nx3
        blk = 4 * 8 + 6 * 8 + nvar * cells * 8
        heads = []
        for b in range(nmb):
            fp.seek(start + b * blk)
            lev, l1, l2, l3 = struct.unpack("<4q", fp.read(32))
            heads.append((lev, l1, l2, l3))
        if any(h[0] != 0 for h in heads):
            raise ValueError("refined mesh")
        N1 = (1 + max(h[1] for h in heads)) * nx1
        N2 = (1 + max(h[2] for h in heads)) * nx2
        N3 = (1 + max(h[3] for h in heads)) * nx3
        out = {}
        for name in want:
            v = names.index(name)
            arr = np.empty((N3, N2, N1))
            for b, (_, l1, l2, l3) in enumerate(heads):
                fp.seek(start + b * blk + 80 + v * cells * 8)
                arr[l3 * nx3:(l3 + 1) * nx3, l2 * nx2:(l2 + 1) * nx2, l1 * nx1:(l1 + 1) * nx1] = \
                    np.frombuffer(fp.read(cells * 8), dtype="<f8").reshape(nx3, nx2, nx1)
            out[name] = arr
    return dict(time=time, cycle=cycle, names=names, N=N1), out


def read_modes(path):
    hdr = {}
    rows = []
    with open(path) as fp:
        for line in fp:
            if line.startswith("#"):
                w = line[1:].split()
                for i in range(len(w) - 1):
                    try:
                        hdr.setdefault(w[i], float(w[i + 1]))
                    except ValueError:
                        pass
            elif line.strip():
                rows.append([float(t) for t in line.split()])
    d = np.array(rows)
    return dict(time=hdr["time"], a=hdr["a"], H=hdr["H"], n2=d[:, 0].astype(np.int64),
                R=d[:, 1] + 1j * d[:, 2])


def amp2_grid(md, n):
    """E|c_n|^2 = |W_n R_n|^2 L^-3 on the rfft grid of an n^3 lattice (zero outside 1 <= |n|^2 <= nmax2)."""
    k1 = np.fft.fftfreq(n, 1.0 / n)
    kz = np.arange(n // 2 + 1, dtype=float)
    n2 = (k1[:, None, None] ** 2 + k1[None, :, None] ** 2 + kz[None, None, :] ** 2).astype(np.int64)
    nmax2 = int(md["n2"].max())
    lut = np.zeros(nmax2 + 1)
    k = np.sqrt(md["n2"].astype(float))
    W = 0.5 * (1.0 + np.tanh(SHARP * np.log(SIGMA_W * md["a"] * md["H"] / k)))
    lut[md["n2"]] = np.abs(W * md["R"]) ** 2 / L_BOX ** 3
    ok = (n2 >= 1) & (n2 <= nmax2)
    return np.where(ok, lut[np.minimum(n2, nmax2)], 0.0)


def half_weights(shape, n):
    w = np.full(shape, 2.0)
    w[:, :, 0] = 1.0
    if n % 2 == 0:
        w[:, :, -1] = 1.0
    return w


# ------------------------------------------------------------------ R^NR
def r_parts(f, n, workers):
    m = {v: float(f[v].mean()) for v in ("chi", "phi", "Pi", "K", "alpha")}
    hb = -m["K"] / (3.0 * m["alpha"])
    k1 = np.fft.fftfreq(n, 1.0 / n)
    kv = (np.arange(n // 2 + 1, dtype=float)[None, None, :], k1[None, :, None], k1[:, None, None])  # x, y, z
    k2 = kv[0] ** 2 + kv[1] ** 2 + kv[2] ** 2
    k2[0, 0, 0] = 1.0
    F = lambda a: sfft.rfftn(a, workers=workers)  # noqa: E731
    B = lambda X: sfft.irfftn(X, s=(n, n, n), workers=workers)  # noqa: E731
    Fchi = F(f["chi"]) / (2.0 * m["chi"])
    Fphi = (hb / m["Pi"]) * F(f["phi"])
    Fan = np.zeros_like(Fchi)
    for name, i, j, w in GIJ:
        Fan += 0.25 * w * (kv[i] * kv[j] / k2) * F(f[name])
    for X in (Fchi, Fphi, Fan):
        X[0, 0, 0] = 0.0
    chi_log = 0.5 * (np.log(f["chi"]) - np.log(f["chi"]).mean())
    return dict(chi=B(Fchi), phi=B(Fphi), aniso=B(Fan), chi_log=chi_log, means=m, H_b=hb)


def moments(x):
    xc = x - x.mean()
    v = np.mean(xc ** 2)
    return float(v), float(np.mean(xc ** 3) / v ** 1.5), float(np.mean(xc ** 4) / v ** 2 - 3.0)


def one_point(x, nb=8):
    n = x.shape[0]
    b = n // nb
    v, sk, ku = moments(x)
    rec = dict(var=v, skew=sk, exkurt=ku)
    blocks = x.reshape(nb, b, nb, b, nb, b).transpose(0, 2, 4, 1, 3, 5).reshape(nb ** 3, b ** 3)
    for nu in NUS:
        fp_, fm_ = np.mean(x > nu), np.mean(x < -nu)
        bp, bm = np.mean(blocks > nu, axis=1), np.mean(blocks < -nu, axis=1)
        q = norm.sf(nu)
        rec[f"Fp{nu:g}"] = dict(F=float(fp_), over_Q=float(fp_ / q),
                                se_block=float(bp.std(ddof=1) / np.sqrt(nb ** 3)))
        rec[f"Fm{nu:g}"] = dict(F=float(fm_), over_Q=float(fm_ / q),
                                se_block=float(bm.std(ddof=1) / np.sqrt(nb ** 3)))
    bsk = np.array([moments(bl)[1] for bl in blocks])
    rec["skew_se_block"] = float(bsk.std(ddof=1) / np.sqrt(nb ** 3))
    return rec


def neff(rho, n):
    """Gaussian box-to-box variance of F(nu) for correlation rho(r) over all N^3 displacements."""
    r = np.clip(rho.ravel(), -1.0 + 1e-12, 1.0)
    a = np.sqrt((1.0 - r) / (1.0 + r))
    res = {}
    for nu in (3.0, 4.0):
        q = norm.sf(nu)
        p2 = q - 2.0 * owens_t(nu, a)
        varF = float(np.sum(p2 - q * q) / n ** 3)
        res[f"{nu:g}"] = dict(sd_F=np.sqrt(varF), rel_sd=np.sqrt(varF) / q, n_eff=q * (1 - q) / varF)
    s2 = float(np.sum(r ** 2))
    res["var_rel_sd"] = float(np.sqrt(2.0 * s2 / n ** 3))      # sd of the box variance / sigma^2
    res["n_eff_var"] = float(n ** 3 / s2)
    res["skew_se_gauss"] = float(np.sqrt(6.0 * np.sum(r ** 3) / n ** 3))
    res["kurt_se_gauss"] = float(np.sqrt(24.0 * np.sum(r ** 4) / n ** 3))
    for nu in (3.0, 4.0):
        q = norm.sf(nu)
        sd_var_part = 0.5 * nu * norm.pdf(nu) * res["var_rel_sd"]
        res[f"{nu:g}"]["sd_F_from_box_variance"] = sd_var_part
        res[f"{nu:g}"]["share_of_varF"] = sd_var_part ** 2 / res[f"{nu:g}"]["sd_F"] ** 2
    return res


def quad_coeff(E, O):
    o2 = O * O - np.mean(O * O)
    a = float(np.mean((E - E.mean()) * o2) / np.mean(o2 * o2))
    resid = E - E.mean() - a * o2
    return dict(a=a, rms_E=float(np.std(E)), rms_resid=float(np.std(resid)),
                implied_skew=float(6.0 * a * np.std(O)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--plus", required=True)
    ap.add_argument("--minus", required=True)
    ap.add_argument("--dump", type=int, default=20)
    ap.add_argument("--base", default="usr")
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    want = ["phi", "Pi", "chi", "K", "alpha"] + [g[0] for g in GIJ]
    runs = {}
    for lab, d in (("plus", a.plus), ("minus", a.minus)):
        stem = os.path.join(d, f"{a.base}.sf.{a.dump:05d}")
        h, f = read_dump(stem + ".dump", want)
        md = read_modes(stem + ".modes")
        n = h["N"]
        A2 = amp2_grid(md, n)
        var_lin = float(np.sum(half_weights(A2.shape, n) * A2))
        p = r_parts(f, n, a.workers)
        del f
        R = p["chi"] + p["phi"] + p["aniso"]
        runs[lab] = dict(h=h, md=md, n=n, A2=A2, sig=np.sqrt(var_lin), R=R, p=p)
        print(lab, "t", h["time"], "record", md["time"], "sigma_lin", np.sqrt(var_lin),
              "sd R", R.std(), flush=True)
    n = runs["plus"]["n"]
    sig = runs["plus"]["sig"]
    out = dict(plus=a.plus, minus=a.minus, dump=a.dump, N=n, time=runs["plus"]["h"]["time"],
               record_time=runs["plus"]["md"]["time"], sigma_lin=sig,
               sigma_lin_minus=runs["minus"]["sig"], H_b=runs["plus"]["p"]["H_b"],
               means=runs["plus"]["p"]["means"])
    for lab in ("plus", "minus"):
        x = runs[lab]["R"] / sig
        rec = one_point(x)
        rec["sd_over_sigma_lin"] = float(np.sqrt(rec["var"]))
        rec["rms_parts_over_sigma_lin"] = {k: float(runs[lab]["p"][k].std() / sig)
                                           for k in ("chi", "phi", "aniso", "chi_log")}
        out[lab] = rec
    # correlation: ensemble (record) and measured (plus run)
    A2 = runs["plus"]["A2"]
    cov_ens = sfft.irfftn(A2, s=(n, n, n), workers=a.workers) * n ** 3
    rho_ens = cov_ens / cov_ens[0, 0, 0]
    X = sfft.rfftn(runs["plus"]["R"], workers=a.workers)
    cov_m = sfft.irfftn(np.abs(X) ** 2, s=(n, n, n), workers=a.workers) / n ** 3
    rho_m = cov_m / cov_m[0, 0, 0]
    out["neff_ensemble"] = neff(rho_ens, n)
    out["neff_measured"] = neff(rho_m, n)
    out["power_run"] = dict(run="E-20261125-115822-29795d6", sd_Fp3=4.96e-5, sd_Fp4=5.98e-6, n_eff_F3=5.5e5)
    # radial profiles for the figure
    k1 = np.fft.fftfreq(n, 1.0 / n)
    rr = np.sqrt(k1[:, None, None] ** 2 + k1[None, :, None] ** 2 + k1[None, None, :] ** 2)
    ib = np.rint(rr).astype(int)
    cnt = np.bincount(ib.ravel())
    prof_e = np.bincount(ib.ravel(), rho_ens.ravel()) / np.maximum(cnt, 1)
    prof_m = np.bincount(ib.ravel(), rho_m.ravel()) / np.maximum(cnt, 1)
    out["rho_profile"] = dict(r_cells=list(range(0, 16)), ensemble=prof_e[:16].tolist(),
                              measured=prof_m[:16].tolist())
    # mirrored pair: second-order part
    pair = {}
    O_tot = 0.5 * (runs["plus"]["R"] - runs["minus"]["R"])
    for key in ("total", "chi", "phi", "aniso", "total_chi_log"):
        if key == "total":
            Rp, Rm = runs["plus"]["R"], runs["minus"]["R"]
        elif key == "total_chi_log":
            Rp = runs["plus"]["R"] - runs["plus"]["p"]["chi"] + runs["plus"]["p"]["chi_log"]
            Rm = runs["minus"]["R"] - runs["minus"]["p"]["chi"] + runs["minus"]["p"]["chi_log"]
        else:
            Rp, Rm = runs["plus"]["p"][key], runs["minus"]["p"][key]
        O = 0.5 * (Rp - Rm)
        E = 0.5 * (Rp + Rm)
        # quadratic response of this part to the total linear field: E = a (O_tot^2 - <O_tot^2>) + ...
        q = quad_coeff(E, O_tot)
        q["rms_E_over_sigma_lin"] = q["rms_E"] / sig
        q["rms_O_over_sigma_lin"] = float(np.std(O) / sig)
        if key in ("total", "total_chi_log"):
            q["mean_skew_of_pair"] = 0.5 * (moments(Rp)[1] + moments(Rm)[1])
            q["skew_plus"], q["skew_minus"] = moments(Rp)[1], moments(Rm)[1]
        pair[key] = q
    out["pair"] = pair
    out["reference_a"] = {k: v / (6.0 * sig) for k, v in REF_SKEW.items()}
    with open(os.path.join(a.out, "box_stats.json"), "w") as fp:
        json.dump(out, fp, indent=1)
    print(json.dumps({k: out[k] for k in ("sigma_lin", "neff_ensemble", "neff_measured", "pair")}, indent=1))
    print(json.dumps({k: {kk: vv for kk, vv in out[k].items()} for k in ("plus", "minus")}, indent=1))

    # ------------------------------------------------------------------ figure
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.8))
    ax = axes[0, 0]
    rc = np.arange(16)
    ax.plot(rc, prof_e[:16], "-", color=fs.SERIES[0], label="ensemble (record spectrum)")
    ax.plot(rc, prof_m[:16], "o", color=fs.SERIES[1], ms=3, label="measured, one box")
    ax.axhline(0.0, color="grey", lw=0.8)
    ax.set_xlabel("separation $|r|$ [cells]")
    ax.set_ylabel(r"$\rho(r)$ of $\mathcal{R}^{\rm NR}$")
    ax.legend(fontsize=7, frameon=False)
    ax = axes[0, 1]
    x = runs["plus"]["R"] / sig
    edges = np.linspace(-6, 6, 121)
    h_, _ = np.histogram(x, bins=edges, density=True)
    c = 0.5 * (edges[1:] + edges[:-1])
    g = norm.pdf(c)
    ok = h_ > 0
    ax.semilogy(c[ok], h_[ok], "o", ms=2.5, color=fs.SERIES[1], label=r"$s=+1$, one box")
    ax.semilogy(c, g, **fs.GUIDE, label="Gaussian, $\\sigma_{\\rm lin}$")
    S = REF_SKEW["lattice"]
    edg = g * (1 + S / 6 * (c ** 3 - 3 * c))
    ax.semilogy(c, np.maximum(edg, 1e-12), color=fs.SERIES[0], lw=1.2,
                label=fr"Edgeworth, skewness {S:g} ($\delta N$ ref.)")
    ax.set_ylim(1e-7, 1)
    ax.set_xlabel(r"$x=\mathcal{R}^{\rm NR}/\sigma_{\rm lin}$")
    ax.set_ylabel("density")
    ax.legend(fontsize=6.5, frameon=False, loc="lower center")
    ax = axes[1, 0]
    O = 0.5 * (runs["plus"]["R"] - runs["minus"]["R"]) / sig
    E = 0.5 * (runs["plus"]["R"] + runs["minus"]["R"]) / sig
    be = np.linspace(-4.5, 4.5, 37)
    idx = np.digitize(O.ravel(), be)
    cb = 0.5 * (be[1:] + be[:-1])
    mE = np.array([E.ravel()[idx == i].mean() if np.sum(idx == i) > 20 else np.nan
                   for i in range(1, len(be))])
    ax.plot(cb, mE, "o", ms=3, color=fs.SERIES[1], label=r"mean even part per bin of the odd part")
    ar = pair["total"]["a"]
    ax.plot(cb, ar * sig * (cb ** 2 - np.mean(O ** 2)), color=fs.SERIES[1], lw=1.0,
            label=fr"fit $a_R={ar:.2e}$")
    for j, (kk, aref) in enumerate(out["reference_a"].items()):
        ax.plot(cb, aref * sig * (cb ** 2 - 1.0), color=fs.SERIES[2 + j], lw=1.0, ls="--",
                label=fr"$\delta N$ ref. {kk}: $a={aref:.4f}$")
    ax.set_xlabel(r"odd part $O/\sigma_{\rm lin}$")
    ax.set_ylabel(r"even part $E/\sigma_{\rm lin}$")
    ax.legend(fontsize=6.5, frameon=False)
    ax = axes[1, 1]
    lab = ["power run\n(400 boxes)", "Owen T,\nensemble", "Owen T,\nmeasured", "blocks\n(one box)",
           "box variance\npart"]
    q3 = norm.sf(3.0)
    vals = [4.96e-5 / q3, out["neff_ensemble"]["3"]["rel_sd"], out["neff_measured"]["3"]["rel_sd"],
            out["plus"]["Fp3"]["se_block"] / q3,
            out["neff_ensemble"]["3"]["sd_F_from_box_variance"] / q3]
    ax.bar(range(len(vals)), vals, color=[fs.SERIES[i % len(fs.SERIES)] for i in range(len(vals))])
    ax.set_xticks(range(len(vals)))
    ax.set_xticklabels(lab, fontsize=6.5)
    ax.set_ylabel(r"box-to-box s.d. of $F_+(3)$ / $Q(3)$")
    fig.tight_layout()
    fs.save(fig, os.path.join(a.out, "fig_box_stats"))


if __name__ == "__main__":
    main()
