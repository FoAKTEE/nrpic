"""verifier_c18b, ledger lines 49-61: the plane-wave pancake through shell crossing.

    python3 pancake.py OUTDIR

Own readers and own reductions of the raw outputs (no code of the track is imported):
  relativistic runs  B-emd-gw-20261115-115217-69ab1db/{L1_n32,L1_n64,L1_n96,L4_n64},
                     B-emd-gw-20261115-115902-a3207d7/L1_n64_p2  (AthenaK, one card)
     east.traj.bin    float64 records (t, tag, x, y, z, u_x, u_y, u_z)     docs/FORMATS.md:121
     east.trajmet.bin float64 records of 17, column 12 = proper time        docs/FORMATS.md:122
     east.part.*.bin  NRPSNAP1 snapshots                                   docs/FORMATS.md:123
     east.cstat.hst   constraint statistics, header names the columns
     east.field.*.bin NRFIELD2 dumps (nrpic_io.cpp NrpicWriteEnergyField)
  Newtonian runs     B-emd-gw-20261115-115239-69ab1db/{n32,n64}, B-emd-gw-20261115-122451-01801f6/n32_p2
     newton.npz       tau, a, x (ntau, nsheet), q, L, delta
Reference: Zel'dovich plane wave, growing mode, a = (1 + t/2)^2 (t conformal time,
H0 = 1): x(x0, a) = x0 + (a - 1)(d/k) cos(k x0) for the element at x0 at a = 1 (own
derivation: d/dtau(a ds/dtau) = (3/2) s has the growing solution s ~ a; at a = 1 the
velocity field (d/k) cos kx of the initial data, cosmo/ic convention). Crossing of the
exact sheets: the smallest over neighbour pairs of
a = 1 + (x0_{j+1} - x0_j) / ((d/k)(cos k x0_j - cos k x0_{j+1})).
"""
import glob
import json
import os
import struct
import sys

import numpy as np

S = "/data/haiyangw/nrpic/scratch/B-emd-gw"
GR = {"L1_n32": f"{S}/B-emd-gw-20261115-115217-69ab1db/L1_n32",
      "L1_n64": f"{S}/B-emd-gw-20261115-115217-69ab1db/L1_n64",
      "L1_n96": f"{S}/B-emd-gw-20261115-115217-69ab1db/L1_n96",
      "L4_n64": f"{S}/B-emd-gw-20261115-115217-69ab1db/L4_n64",
      "L1_n64_p2": f"{S}/B-emd-gw-20261115-115902-a3207d7/L1_n64_p2"}
NW = {"N_n32": f"{S}/B-emd-gw-20261115-115239-69ab1db/n32",
      "N_n64": f"{S}/B-emd-gw-20261115-115239-69ab1db/n64",
      "N_n32_p2": f"{S}/B-emd-gw-20261115-122451-01801f6/n32_p2"}
DELTA = 0.05


def a_of_t(t):
    return (1.0 + 0.5*np.asarray(t, float))**2


def t_of_a(a):
    return 2.0*(np.sqrt(a) - 1.0)


def read_gr(d):
    idj = json.load(open(os.path.join(d, "id.json")))
    L, n = float(idj["L"]), int(idj["n"])*int(idj["ppc"])
    r = np.fromfile(os.path.join(d, "east.traj.bin")).reshape(-1, 8)
    m = np.fromfile(os.path.join(d, "east.trajmet.bin")).reshape(-1, 17)
    times = np.unique(r[:, 0])
    # x line: the tags whose y and z are those of tag 0 at t = 0 and that move along x
    r0 = r[r[:, 0] == 0.0]
    y0, z0 = r0[r0[:, 1] == 0.0][0, 3:5]
    on = (np.abs(r0[:, 3] - y0) < 1e-12) & (np.abs(r0[:, 4] - z0) < 1e-12)
    tags = np.sort(r0[on, 1]).astype(int)
    assert len(tags) == n and (tags == np.arange(n)).all(), (d, len(tags), n)
    X = np.full((len(times), n), np.nan)
    TAU = np.full((len(times), n), np.nan)
    it = np.searchsorted(times, r[:, 0])
    pos = {t: j for j, t in enumerate(tags)}
    sel = np.isin(r[:, 1].astype(int), tags)
    jj = np.array([pos[t] for t in r[sel, 1].astype(int)])
    X[it[sel], jj] = r[sel, 2]
    itm = np.searchsorted(times, m[:, 0])
    selm = np.isin(m[:, 1].astype(int), tags)
    jm = np.array([pos[t] for t in m[selm, 1].astype(int)])
    TAU[itm[selm], jm] = m[selm, 12]
    assert np.isfinite(X).all() and np.isfinite(TAU).all()
    # order by initial position and unwrap in time (periodic box)
    o = np.argsort(X[0])
    X, TAU = X[:, o], TAU[:, o]
    X = X[0] + np.cumsum(np.vstack([np.zeros(n), np.diff(X, axis=0)]) -
                         L*np.round(np.vstack([np.zeros(n), np.diff(X, axis=0)])/L), axis=0)
    X -= L*np.floor(X[0]/L)[None, :]          # initial positions into [0, L)
    o = np.argsort(X[0])
    X, TAU = X[:, o], TAU[:, o]
    return {"t": times, "a": a_of_t(times), "x": X, "tau": TAU, "L": L, "n": n,
            "dir": d, "x0": X[0].copy()}


def read_nw(d):
    z = np.load(os.path.join(d, "newton.npz"))
    L = float(z["L"])
    x = np.array(z["x"], float)
    n = x.shape[1]
    dx = np.diff(x, axis=0)
    x = x[0] + np.cumsum(np.vstack([np.zeros(n), dx - L*np.round(dx/L)]), axis=0)
    x -= L*np.floor(x[0]/L)[None, :]          # initial positions into [0, L)
    x = x[:, np.argsort(x[0])]
    t = np.array(z["tau"], float)
    assert np.allclose(np.array(z["a"]), a_of_t(t), rtol=1e-12), "a != (1+tau/2)^2"
    return {"t": t, "a": a_of_t(t), "x": x, "L": L, "n": n, "dir": d, "x0": x[0].copy(),
            "delta": float(z["delta"])}


def first_crossing(run):
    """Smallest a at which a neighbour pair (in initial order, periodic) swaps, by linear
    interpolation of the gap in a between records."""
    x, a, L = run["x"], run["a"], run["L"]
    gap = np.diff(np.hstack([x, x[:, :1] + L]), axis=1)
    best = (np.inf, None, None)
    for j in range(gap.shape[1]):
        g = gap[:, j]
        neg = np.flatnonzero(g <= 0.0)
        if len(neg) == 0:
            continue
        i = neg[0]
        f = g[i - 1]/(g[i - 1] - g[i])
        ac = a[i - 1] + f*(a[i] - a[i - 1])
        if ac < best[0]:
            best = (ac, j, (i, f))
    return best


def zel_x(x0, a, d, L):
    k = 2*np.pi/L
    return x0 + (a - 1.0)*(d/k)*np.cos(k*x0)


def exact_sheet_crossing(x0, d, L):
    """a at which neighbours j, j+1 of the exact Zel'dovich motion meet (closed form)."""
    k = 2*np.pi/L
    xs = np.sort(x0)
    xn = np.append(xs[1:], xs[0] + L)
    dc = (d/k)*(np.cos(k*xs) - np.cos(k*xn))
    with np.errstate(divide="ignore"):
        am1 = (xn - xs)/dc
    am1[dc <= 0] = np.inf
    return float(1.0 + am1.min())


def at_a(run, key, a0):
    """Linear interpolation in t of run[key] (ntime, nsheet) at the scale factor a0."""
    t0 = t_of_a(a0)
    i = int(np.searchsorted(run["t"], t0))
    f = (t0 - run["t"][i - 1])/(run["t"][i] - run["t"][i - 1])
    return (1 - f)*run[key][i - 1] + f*run[key][i]


def norm(run, a0):
    k = 2*np.pi/run["L"]
    return (a0 - 1.0)*DELTA/k


def read_cstat(d):
    path = os.path.join(d, "east.cstat.hst")
    head = [ln for ln in open(path) if ln.startswith("# [")][0]
    names = [w.split("=")[1] for w in head[1:].split()]
    c = np.loadtxt(path)
    return {nm: c[:, i] for i, nm in enumerate(names)}


def read_field(path):
    with open(path, "rb") as f:
        magic = f.read(8)
        t = struct.unpack("<d", f.read(8))[0]
        n1, n2, n3 = struct.unpack("<3q", f.read(24))
        nc = n1*n2*n3
        out = {"t": t, "magic": magic}
        for key in ("E", "chi"):
            out[key] = np.fromfile(f, "<f4", nc).astype(float).reshape(n3, n2, n1)
        assert magic == b"NRFIELD2"
        for key in ("H", "Mx", "My", "Mz", "Khat", "Theta", "alpha"):
            out[key] = np.fromfile(f, "<f8", nc).reshape(n3, n2, n1)
        rest = f.read()
        assert len(rest) == 0, len(rest)
    return out


def hr_mean_from_dump(fd):
    """Cell average of |H| / sqrt(R^2 + (2/3 K^2)^2 + (A.A)^2 + (16 pi E)^2) with
    R = H - (2/3) K^2 + A.A + 16 pi E and A.A dropped (not in the dump; of order (delta K)^2)."""
    K = fd["Khat"] + 2.0*fd["Theta"]
    k23 = (2.0/3.0)*K*K
    e16 = 16.0*np.pi*fd["E"]
    R = fd["H"] - k23 + e16
    den = np.sqrt(R*R + k23*k23 + e16*e16)
    return float(np.mean(np.abs(fd["H"])/den))


def read_snap(path):
    with open(path, "rb") as f:
        assert f.read(8) == b"NRPSNAP1"
        t = struct.unpack("<d", f.read(8))[0]
        n, cyc = struct.unpack("<2q", f.read(16))
        rec = np.fromfile(f, "<f8", 7*n).reshape(n, 7)
        tag = np.fromfile(f, "<i4", n)
    return t, rec, tag


def symmetry(d, L, nline):
    snaps = sorted(glob.glob(os.path.join(d, "east.part.*.bin")))
    t0, r0, tag0 = read_snap(snaps[0])
    assert t0 == 0.0
    # lattice plane of each particle: its initial x (plane-symmetric data: identical x)
    xi0 = dict(zip(tag0.tolist(), r0[:, 0].tolist()))
    out = []
    for p in snaps:
        t, r, tag = read_snap(p)
        x0 = np.array([xi0[tg] for tg in tag.tolist()])
        keys = np.round(x0/L*1e9).astype(np.int64)
        u, inv = np.unique(keys, return_inverse=True)
        # reference member of each plane: the x-line observer (tags 0 .. nline-1)
        ref = np.full(len(u), np.nan)
        line = tag < nline
        ref[inv[line]] = r[line, 0]
        assert np.isfinite(ref).all()
        dx = r[:, 0] - ref[inv]
        dx -= L*np.round(dx/L)
        lo = np.full(len(u), np.inf)
        hi = np.full(len(u), -np.inf)
        np.minimum.at(lo, inv, dx)
        np.maximum.at(hi, inv, dx)
        out.append({"t": t, "a": float(a_of_t(t)), "nplanes": int(len(u)),
                    "spread_over_L": float(np.abs(dx).max()/L),
                    "range_over_L": float((hi - lo).max()/L),
                    "max_u_perp": float(np.abs(r[:, 4:6]).max())})
    return out


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    res = {}
    gr = {k: read_gr(v) for k, v in GR.items()}
    nw = {k: read_nw(v) for k, v in NW.items()}
    for k, r in nw.items():
        assert abs(r["delta"] - DELTA) < 1e-15
    # first crossings
    for k, r in {**gr, **nw}.items():
        ac, j, (i, f) = first_crossing(r)
        e = {"a_cross": ac, "pair": j, "a_last_record": float(r["a"][-1]),
             "a_cross_exact_sheets": exact_sheet_crossing(r["x0"], DELTA, r["L"])}
        if "tau" in r:
            tp = [(1 - f)*r["tau"][i - 1, jj] + f*r["tau"][i, jj] for jj in (j, (j + 1) % r["n"])]
            e["tau_p_cross"] = [float(v) for v in tp]
            e["a_p_cross"] = [float((1 + 1.5*v)**(2.0/3.0)) for v in tp]
            # check of the proper-time column: sheets far from the pancake, tau vs EdS
            e["tau_vs_eds_last"] = float(np.median(r["tau"][-1]) /
                                         ((a_of_t(r["t"][-1])**1.5 - 1)/1.5))
        # departure from Zel'dovich at a = 10 (positions interpolated to a = 10)
        x10 = at_a(r, "x", 10.0)
        e["ex_a10"] = float(np.abs(x10 - zel_x(r["x0"], 10.0, DELTA, r["L"])).max()/norm(r, 10.0))
        res[k] = e
    # relativistic minus Newtonian at a = 10, same sheets (initial positions matched)
    for g, w, s in (("L1_n32", "N_n32", 1.0), ("L1_n64", "N_n64", 1.0), ("L4_n64", "N_n64", 4.0)):
        G, W = gr[g], nw[w]
        xg = at_a(G, "x", 10.0)
        xw = at_a(W, "x", 10.0)*s
        x0w = W["x0"]*s
        # match sheets by initial position
        idx = np.array([int(np.argmin(np.abs((x0w - q + 0.5*G["L"]) % G["L"] - 0.5*G["L"])))
                        for q in G["x0"]])
        mis = float(np.abs((x0w[idx] - G["x0"] + 0.5*G["L"]) % G["L"] - 0.5*G["L"]).max())
        dxa = xg - xw[idx]
        res[f"dx_{g}_{w}"] = {"dx_a10": float(np.abs(dxa).max()/norm(G, 10.0)),
                              "max_initial_mismatch": mis}
    res["ratio_L4_over_L1"] = res["dx_L4_n64_N_n64"]["dx_a10"]/res["dx_L1_n64_N_n64"]["dx_a10"]
    # constraints: the code's statistics and my own from the field dumps
    for k in ("L1_n64", "L1_n64_p2"):
        c = read_cstat(GR[k])
        ac = a_of_t(c["time"])
        con = {}
        for a0 in (10.0, 15.0):
            i = int(np.argmin(np.abs(ac - a0)))
            con[f"Hr_mean_a{a0:g}_nearest"] = float(c["Hr_mean"][i])
            con[f"Hr_mean_a{a0:g}_interp"] = float(np.interp(a0, ac, c["Hr_mean"]))
            con[f"Mr_mean_a{a0:g}_nearest"] = float(c["Mr_mean"][i])
            con[f"Mr_mean_a{a0:g}_interp"] = float(np.interp(a0, ac, c["Mr_mean"]))
            con[f"a_nearest_{a0:g}"] = float(ac[i])
        sel = (ac >= 22.0) & (ac <= 42.0)
        con["Hr_mean_max_22_42_all_records"] = float(c["Hr_mean"][sel].max())
        con["a_of_that_max"] = float(ac[sel][np.argmax(c["Hr_mean"][sel])])
        con["Hr_mean_at_5_epochs"] = {}
        for a0 in (22.0, 25.0, 30.0, 35.0, 41.9):
            i = int(np.argmin(np.abs(ac - a0)))
            con["Hr_mean_at_5_epochs"][f"{a0:g}"] = float(c["Hr_mean"][i])
        con["Hr_mean_max_5_epochs"] = max(con["Hr_mean_at_5_epochs"].values())
        dumps = []
        for p in sorted(glob.glob(os.path.join(GR[k], "east.field.*.bin"))):
            fd = read_field(p)
            i = int(np.argmin(np.abs(c["time"] - fd["t"])))
            dumps.append({"a": float(a_of_t(fd["t"])), "Hr_mean_mine": hr_mean_from_dump(fd),
                          "Hr_mean_code": float(c["Hr_mean"][i]),
                          "dt_to_record": float(c["time"][i] - fd["t"])})
        con["dumps"] = dumps
        res[f"con_{k}"] = con
    # plane symmetry from the snapshots of every relativistic run
    sym = {}
    for k, d in GR.items():
        sym[k] = symmetry(d, gr[k]["L"], gr[k]["n"])
    res["symmetry"] = sym
    res["symmetry_max_spread_over_L"] = max(s["spread_over_L"] for v in sym.values() for s in v)
    res["symmetry_max_range_over_L"] = max(s["range_over_L"] for v in sym.values() for s in v)
    res["symmetry_max_u_perp"] = max(s["max_u_perp"] for v in sym.values() for s in v)
    with open(os.path.join(out, "pancake_c18b.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)
    np.savez(os.path.join(out, "pancake_series.npz"),
             **{f"{k}_a": r["a"] for k, r in {**gr, **nw}.items()},
             **{f"{k}_ex": np.abs(r["x"] - zel_x(r["x0"][None, :], r["a"][:, None], DELTA, r["L"])).max(axis=1)
                / np.maximum((r["a"] - 1)*DELTA/(2*np.pi/r["L"]), 1e-30) for k, r in {**gr, **nw}.items()},
             **{f"{k}_mingap": np.diff(np.hstack([r["x"], r["x"][:, :1] + r["L"]]), axis=1).min(axis=1)
                / (r["L"]/r["n"]) for k, r in {**gr, **nw}.items()})
    print(json.dumps({k: v for k, v in res.items() if k != "symmetry"}, indent=1, default=float))
    figure(gr, nw, res, out)


def figure(gr, nw, res, out):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 2.8))
    ax = axs[0]
    cols = {"L1_n32": fs.PAL["yellow"], "L1_n64": fs.PAL["blue"], "L1_n96": fs.PAL["green"],
            "L4_n64": fs.PAL["red"], "L1_n64_p2": fs.PAL["orange"]}
    for k, r in gr.items():
        g = np.diff(np.hstack([r["x"], r["x"][:, :1] + r["L"]]), axis=1).min(axis=1)/(r["L"]/r["n"])
        ax.plot(r["a"], g, color=cols[k], label=k.replace("_", " "))
        ax.plot(res[k]["a_cross"], 0, "o", ms=3, color=cols[k])
    for k, ls in (("N_n32", ":"), ("N_n64", "--")):
        r = nw[k]
        g = np.diff(np.hstack([r["x"], r["x"][:, :1] + r["L"]]), axis=1).min(axis=1)/(r["L"]/r["n"])
        ax.plot(r["a"], g, color="k", ls=ls, lw=1.0, label=k.replace("_", " ") + " (Newton)")
    ax.axvline(21.0, **fs.MASK_LINE)
    ax.axhline(0.0, **fs.THIN)
    ax.set_xlim(15, 25)
    ax.set_ylim(-0.3, 0.6)
    ax.set_xlabel(r"$a$ (coordinate label)")
    ax.set_ylabel(r"smallest sheet gap$/h$")
    ax.legend(fontsize=6, loc="upper right")
    ax.set_title("(a) first crossing", fontsize=8)
    ax = axs[1]
    for k, r in {**gr, **nw}.items():
        ex = np.abs(r["x"] - zel_x(r["x0"][None, :], r["a"][:, None], DELTA, r["L"])).max(axis=1)
        nn = (r["a"] - 1.0)*DELTA/(2*np.pi/r["L"])
        m = r["a"] > 1.05
        c = cols.get(k, "k")
        ls = "-" if k in gr else ("--" if k == "N_n64" else ":")
        ax.semilogy(r["a"][m], ex[m]/nn[m], color=c, ls=ls, lw=1.0 if k in nw else 1.5)
    ax.axvline(10.0, **fs.MASK_LINE)
    ax.set_xlim(1, 21)
    ax.set_xlabel(r"$a$")
    ax.set_ylabel(r"max$|x-x_{\rm Z}|/[(a-1)\delta/k]$")
    ax.set_title(r"(b) departure from Zel'dovich", fontsize=8)
    ax = axs[2]
    for k in ("L1_n64", "L1_n64_p2"):
        c = read_cstat(GR[k])
        ac = a_of_t(c["time"])
        ax.semilogy(ac, c["Hr_mean"], color=cols[k], label=f"{k.replace('_', ' ')}, cstat.hst")
        d = res[f"con_{k}"]["dumps"]
        ax.semilogy([x["a"] for x in d], [x["Hr_mean_mine"] for x in d], "o", ms=3,
                    mfc="none", color=cols[k], label="own, from field dumps")
        ep = res[f"con_{k}"]["Hr_mean_at_5_epochs"]
        ax.semilogy([float(e) for e in ep], list(ep.values()), "x", ms=4, color="k")
    ax.axvspan(22, 42, color="grey", alpha=0.12)
    ax.set_xlabel(r"$a$")
    ax.set_ylabel(r"mean $|\mathcal{H}|$ relative")
    ax.legend(fontsize=6, loc="lower right")
    ax.set_title(r"(c) constraint (x: the five epochs)", fontsize=8)
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "pancake_c18b"))


if __name__ == "__main__":
    main()
