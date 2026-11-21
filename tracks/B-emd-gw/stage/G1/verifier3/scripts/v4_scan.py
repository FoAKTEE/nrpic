#!/usr/bin/env python3
"""V4 on the first-source scan (JOURNAL entry 14): difference of c_+(1,1,0) of Lambda(gt - delta)
between the zero-shift run cw_eps1 and the Gamma-driver run cw_eps1_gd, before and after
my second-order gauge piece, at a = 5, 10, 20, 40, 60 (64^3 card runs and 32^3 processor
companions).

Per dump pair (same index in both runs; times checked equal):
  c_zs, c_gd   + coefficient at m = (1,1,0) (khat = (1,1,0)/sqrt 2, my e+ basis) of
               Lambda(ht), ht = gt/det(gt)^(1/3) - delta (also with gt as stored, 'raw');
  route A      zeta_A = int_0^t beta dt (trapezoid over all dumps of the gd run), symmetric
               conformal form G = Lambda[L_zeta htbar - (2/3) div zeta htbar];
  route B      zeta_B from the first-order difference ht_gd - ht_zs, same G;
  route T      each gauge mapped to its own spatially transverse coordinates (the reference
               metric A = Lambda ht + mean traceless part, zeta_T from the traceless non-TT
               part of ht), one-sided form; the README/fslib method, my implementation;
  each with spectral products on the N grid and on a 2N grid (Fourier-upsampled fields:
  no aliasing of the products into m = (1,1,0)).
Values at t(a) = 2 (sqrt a - 1) by linear interpolation between the bracketing dumps.
Writes $NRPIC_RUN_DIR/v4_scan.json and v4_scan.png/pdf. Env: V4_RES (default "64,32").
"""
import glob
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import diag  # noqa: E402
import exact  # noqa: E402
import figstyle as fs  # noqa: E402
import v4lib  # noqa: E402

OUT = os.environ.get("NRPIC_RUN_DIR", os.path.join(HERE, "..", "results", "tmp_v4s"))
os.makedirs(OUT, exist_ok=True)
SCR = "/data/haiyangw/nrpic/scratch/B-emd-gw"
RUNS = {64: ("B-20261115-165353-b592d43/cw_eps1", "B-20261115-165353-b592d43/cw_eps1_gd"),
        32: ("B-20261115-165525-f7c2004/cw_eps1", "B-20261115-165525-f7c2004/cw_eps1_gd")}
AVALS = [5.0, 10.0, 20.0, 40.0, 60.0]
EYE = np.eye(3)[:, :, None, None, None]
ep, ex, _, _, _ = exact.pol_tensors((1.0, 1.0, 0.0))
M110 = (1, 1, 0)


def header_time(path):
    with open(path, "rb") as f:
        raw = f.read(400).decode("latin1")
    for line in raw.splitlines():
        if line.strip().startswith("time="):
            return float(line.split("=", 1)[1])
    raise ValueError(path)


def cplus(T, grid):
    return diag.mode_coeff(0.5 * np.einsum("ab,ab...->...", ep, T), grid, M110)


def upsample(f, grid, fac=2):
    """spectral interpolation of real periodic fields (last 3 axes) onto fac*N cells."""
    n = grid.n
    m = tuple(fac * v for v in n)
    F = np.fft.fftn(f, axes=(-3, -2, -1))
    out = np.zeros(f.shape[:-3] + m, dtype=complex)
    sl = []
    for a in range(3):
        k = np.fft.fftfreq(n[a], 1.0 / n[a]).astype(int)
        k[np.abs(k) == n[a] // 2] = 10 ** 6          # drop Nyquist
        sl.append(k)
    for i, ki in enumerate(sl[0]):
        if ki == 10 ** 6:
            continue
        for j, kj in enumerate(sl[1]):
            if kj == 10 ** 6:
                continue
            ks = sl[2]
            good = ks != 10 ** 6
            out[..., ki % m[0], kj % m[1], ks[good] % m[2]] = F[..., i, j, np.nonzero(good)[0]]
    g2 = diag.Grid(m, grid.L, grid.xmin + 0.5 * grid.h - 0.5 * grid.h / fac)
    # keep the same physical sample positions: x_i = xmin + (i + 1/2) h; on the fine grid the
    # first centre is xmin2 + h/(2 fac); the phase factor below shifts the data accordingly.
    kv = g2.kvecs(real=False)
    shift = (grid.xmin + 0.5 * grid.h) - (g2.xmin + 0.5 * g2.h)
    ph = np.exp(-1j * (kv[0] * shift[0] + kv[1] * shift[1] + kv[2] * shift[2]))
    fine = np.real(np.fft.ifftn(out * ph, axes=(-3, -2, -1))) * (np.prod(m) / np.prod(n))
    return fine, g2


def transverse_piece(ht, grid):
    """route T: Lambda ht - Lambda ht_T for ht's own spatially transverse coordinates."""
    tr = np.einsum("aa...->...", ht)
    htl = ht - EYE * tr / 3.0
    hTT = diag.tt_project(htl, grid)
    h0 = htl.mean(axis=(-3, -2, -1), keepdims=True)
    D = htl - hTT - h0
    zT = v4lib.zeta_from_difference(D, grid, conformal=True)
    A = hTT + h0
    return v4lib.gauge_piece(zT, grid, h_old=A, conformal=True, form="one"), zT


def pair_numbers(h_zs, h_gd, zA, grid):
    """complex + coefficients at (1,1,0) for one pair of dumps on one grid."""
    r = {}
    r["c_zs"] = cplus(diag.tt_project(h_zs, grid), grid)
    r["c_gd"] = cplus(diag.tt_project(h_gd, grid), grid)
    r["G_A"] = cplus(v4lib.gauge_piece(zA, grid, h_old=h_zs, h_new=h_gd, conformal=True, form="sym"), grid)
    zB = v4lib.zeta_from_difference(h_gd - h_zs, grid, conformal=True)
    r["G_B"] = cplus(v4lib.gauge_piece(zB, grid, h_old=h_zs, h_new=h_gd, conformal=True, form="sym"), grid)
    GTz, zTz = transverse_piece(h_zs, grid)
    GTg, zTg = transverse_piece(h_gd, grid)
    r["GT_zs"] = cplus(GTz, grid)
    r["GT_gd"] = cplus(GTg, grid)
    rmsA = float(np.sqrt(np.mean(zA ** 2)))
    r["zeta_A rms"] = rmsA
    r["|zeta_B - zeta_A| / |zeta_A|"] = float(np.sqrt(np.mean((zB - zA) ** 2)) / rmsA) if rmsA > 0 else None
    # transverse coordinates X_T = x_zs + xi_zs = x_gd + xi_gd and x_zs = x_gd + zeta: zeta = xi_gd - xi_zs
    r["|(zT_gd - zT_zs) - zeta_A| / |zeta_A|"] = (float(np.sqrt(np.mean((zTg - zTz - zA) ** 2)) / rmsA)
                                                    if rmsA > 0 else None)
    r["max |d zeta_A|"] = float(np.max(np.abs(v4lib.grad_vec(zA, grid))))
    return r


def do_res(N):
    zs_dir, gd_dir = RUNS[N]
    fz = sorted(glob.glob(f"{SCR}/{zs_dir}/bin/*.z4c.*.bin"))
    fg = sorted(glob.glob(f"{SCR}/{gd_dir}/bin/*.z4c.*.bin"))
    tz = np.array([header_time(f) for f in fz])
    tg = np.array([header_time(f) for f in fg])
    nmin = min(len(tz), len(tg))
    tdiff = float(np.max(np.abs(tz[:nmin] - tg[:nmin])))
    tmax = 2 * (np.sqrt(max(AVALS)) - 1) + 0.3
    need = int(np.searchsorted(tg, tmax)) + 1
    # zeta_A(t) at every gd dump: trapezoid of beta
    zeta = None
    zetas = {}
    prev_b, prev_t = None, None
    for i in range(min(need, len(fg))):
        d = diag.read_bin(fg[i], want=["z4c_betax", "z4c_betay", "z4c_betaz"])
        b = np.array([d["vars"]["z4c_betax"], d["vars"]["z4c_betay"], d["vars"]["z4c_betaz"]])
        if zeta is None:
            zeta = np.zeros_like(b)
            beta0_max = float(np.max(np.abs(b)))
        else:
            zeta = zeta + 0.5 * (b + prev_b) * (d["time"] - prev_t)
        prev_b, prev_t = b, d["time"]
        zetas[i] = zeta.copy()
    rows = []
    for a in AVALS:
        ta = 2 * (np.sqrt(a) - 1)
        i1 = int(np.searchsorted(tz, ta))
        i0 = i1 - 1
        w = (ta - tz[i0]) / (tz[i1] - tz[i0])
        vals = []
        for i in (i0, i1):
            dz = diag.read_bin(fz[i])
            dg = diag.read_bin(fg[i])
            grid = dz["grid"]
            gtz = diag.sym_from(dz["vars"], "z4c_g")
            gtg = diag.sym_from(dg["vars"], "z4c_g")
            hz = v4lib.conformal(gtz) - EYE
            hg = v4lib.conformal(gtg) - EYE
            rec = {"t": dz["time"], "N grid": pair_numbers(hz, hg, zetas[i], grid)}
            rec["raw gt: c_zs"] = cplus(diag.tt_project(gtz - EYE, grid), grid)
            rec["raw gt: c_gd"] = cplus(diag.tt_project(gtg - EYE, grid), grid)
            rec["max |det gt - 1|"] = float(max(np.max(np.abs(diag.inv3(gtz)[1] - 1)),
                                                np.max(np.abs(diag.inv3(gtg)[1] - 1))))
            hz2, g2 = upsample(hz, grid)
            hg2, _ = upsample(hg, grid)
            zA2, _ = upsample(zetas[i], grid)
            rec["2N grid"] = pair_numbers(hz2, hg2, zA2, g2)
            # float32 floor: add a second rounding-sized perturbation (uniform +-ulp/2 of the
            # stored values) to both metrics and recompute the route-A residual
            rng = np.random.default_rng(i)
            ulp = np.spacing(np.float32(1.0)) / 2
            hz_n = v4lib.conformal(gtz * (1 + ulp * rng.uniform(-1, 1, gtz.shape))) - EYE
            hg_n = v4lib.conformal(gtg * (1 + ulp * rng.uniform(-1, 1, gtg.shape))) - EYE
            q0 = rec["N grid"]
            qn = pair_numbers(hz_n, hg_n, zetas[i], grid)
            rec["float32 floor: |change of (c_gd - c_zs - G_A)|"] = abs(
                (qn["c_gd"] - qn["c_zs"] - qn["G_A"]) - (q0["c_gd"] - q0["c_zs"] - q0["G_A"]))
            rec["rms ht_zs nonTT"] = float(np.sqrt(np.mean((hz - diag.tt_project(hz, grid)) ** 2)))
            vals.append(rec)
        out = {"a": a, "t(a)": ta, "dumps": [os.path.basename(fz[i0]), os.path.basename(fz[i1])],
               "t_dumps": [vals[0]["t"], vals[1]["t"]], "w": w}
        for key in ("raw gt: c_zs", "raw gt: c_gd"):
            out[key] = complex((1 - w) * vals[0][key] + w * vals[1][key])
        out["max |det gt - 1|"] = max(v["max |det gt - 1|"] for v in vals)
        out["float32 floor rel"] = max(v["float32 floor: |change of (c_gd - c_zs - G_A)|"] for v in vals) / abs(
            (1 - w) * vals[0]["N grid"]["c_zs"] + w * vals[1]["N grid"]["c_zs"])
        out["rms ht_zs nonTT"] = (1 - w) * vals[0]["rms ht_zs nonTT"] + w * vals[1]["rms ht_zs nonTT"]
        for gname in ("N grid", "2N grid"):
            q = {}
            for key in vals[0][gname]:
                v0, v1 = vals[0][gname][key], vals[1][gname][key]
                q[key] = None if v0 is None else (1 - w) * v0 + w * v1
            c_zs, c_gd = q["c_zs"], q["c_gd"]
            den = abs(c_zs)
            q["rel raw |c_gd - c_zs|"] = abs(c_gd - c_zs) / den
            q["rel after A |c_gd - c_zs - G_A|"] = abs(c_gd - c_zs - q["G_A"]) / den
            q["rel after B |c_gd - c_zs - G_B|"] = abs(c_gd - c_zs - q["G_B"]) / den
            q["rel after T |(c_gd - GT_gd) - (c_zs - GT_zs)|"] = abs((c_gd - q["GT_gd"]) - (c_zs - q["GT_zs"])) / den
            q["rel |G_A - G_B|"] = abs(q["G_A"] - q["G_B"]) / den
            q["rel |GT_gd - GT_zs - G_A|"] = abs(q["GT_gd"] - q["GT_zs"] - q["G_A"]) / den
            out[gname] = q
        rows.append(out)
        print(f"N{N} a={a}: raw {out['N grid']['rel raw |c_gd - c_zs|']:.3g} "
              f"A {out['N grid']['rel after A |c_gd - c_zs - G_A|']:.3g} "
              f"B {out['N grid']['rel after B |c_gd - c_zs - G_B|']:.3g} "
              f"T {out['N grid']['rel after T |(c_gd - GT_gd) - (c_zs - GT_zs)|']:.3g} | 2N: "
              f"A {out['2N grid']['rel after A |c_gd - c_zs - G_A|']:.3g} "
              f"T {out['2N grid']['rel after T |(c_gd - GT_gd) - (c_zs - GT_zs)|']:.3g} | f32 floor {out['float32 floor rel']:.3g}",
              flush=True)
    return {"zs": zs_dir, "gd": gd_dir, "max |t_zs - t_gd| over dumps": tdiff, "max |beta| at t=0": beta0_max,
            "rows": rows}


def cjson(o):
    if isinstance(o, complex):
        return [o.real, o.imag]
    if isinstance(o, dict):
        return {k: cjson(v) for k, v in o.items()}
    if isinstance(o, list):
        return [cjson(v) for v in o]
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.complexfloating):
        return [float(o.real), float(o.imag)]
    return o


t0 = time.time()
res = {}
for N in [int(v) for v in os.environ.get("V4_RES", "64,32").split(",")]:
    res[N] = do_res(N)
res["wall_s"] = time.time() - t0
with open(os.path.join(OUT, "v4_scan.json"), "w") as fh:
    json.dump(cjson(res), fh, indent=1)

fs.use_style()
import matplotlib.pyplot as plt  # noqa: E402

fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.3), sharey=True)
fig.subplots_adjust(left=0.08, right=0.99, bottom=0.15, top=0.9, wspace=0.06)
for ax, N in zip(axs, [k for k in res if isinstance(k, int)]):
    rows = res[N]["rows"]
    a = np.array([r["a"] for r in rows])
    for key, lab, col, mk in (("rel raw |c_gd - c_zs|", "raw difference", fs.PAL["blue"], "o"),
                              ("rel after A |c_gd - c_zs - G_A|", r"after $G$ ($\zeta=\int\beta$)", fs.PAL["red"], "s"),
                              ("rel after B |c_gd - c_zs - G_B|", r"after $G$ ($\zeta$ from $\Delta h$)", fs.PAL["yellow"], "^"),
                              ("rel after T |(c_gd - GT_gd) - (c_zs - GT_zs)|", "after transverse-reference pieces", fs.PAL["green"], "v")):
        ax.loglog(a, [r["N grid"][key] for r in rows], mk + "-", color=col, ms=4, lw=1.0, label=lab)
        ax.loglog(a, [r["2N grid"][key] for r in rows], mk + ":", color=col, ms=3, lw=0.8, mfc="none")
    ax.set_title(f"$N={N}$: $c_+(k,k,0)$, zero shift vs Gamma driver", fontsize=9)
    ax.set_xlabel("a", labelpad=-2)
    ax.set_xticks(AVALS)
    ax.set_xticklabels([str(int(v)) for v in AVALS])
    ax.minorticks_off()
axs[0].set_ylabel(r"$|\Delta c_+|/|c_+^{\rm zs}|$")
axs[0].legend(loc="lower right", fontsize=6)
for ax, N in zip(axs, [k for k in res if isinstance(k, int)]):
    rows = res[N]["rows"]
    ax.loglog([r["a"] for r in rows], [r["float32 floor rel"] for r in rows], "x", color="k", ms=4,
              label="float32 rounding floor (est.)")
axs[1].legend(loc="lower right", fontsize=6)
axs[1].text(0.02, 0.03, "solid: products on N grid; dotted: on 2N grid", transform=axs[1].transAxes, fontsize=7)
fs.save(fig, os.path.join(OUT, "v4_scan"))
print("wall", res["wall_s"])
