"""Plane-wave pancake: relativistic runs (AthenaK) and the Newtonian particle-mesh
reference against the Zel'dovich solution, plus constraints and plane symmetry.

    python3 analyze_pancake.py --gr GRRUN --newton NWRUN --out DIR

GRRUN holds L1_n32, L1_n64, L1_n96, L4_n64 (run B-emd-gw-20261115-115217-69ab1db),
NWRUN holds n32, n64 (newton.npz of scripts/newton_pancake.py). Writes DIR/pancake.json
and the figures DIR/pancake_*.{png,pdf}.
"""
import argparse
import glob
import json
import os
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "python"))
import zeldovich as Z  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402

A_EVAL = [2.0, 5.0, 10.0, 15.0, 18.0, 20.0]
A_CON = [1.5, 2.0, 5.0, 10.0, 15.0, 18.0, 20.0, 21.0, 22.0, 25.0, 30.0, 35.0, 41.9]


# ---------------------------------------------------------------------------------------
# readers
# ---------------------------------------------------------------------------------------
def unwrap(x, q, L):
    return q + np.mod(x - q + 0.5*L, L) - 0.5*L


def load_gr(rundir):
    idj = json.load(open(os.path.join(rundir, "id.json")))
    n, L, d = idj["n"], idj["L"], idj["delta"]
    ntr = 3*n - 2
    fid = np.load(os.path.join(rundir, "fiducial.npz"))
    q = fid["q"][:n, 0]
    r = np.fromfile(os.path.join(rundir, "east.traj.bin")).reshape(-1, 8)
    m = np.fromfile(os.path.join(rundir, "east.trajmet.bin")).reshape(-1, 17)
    nt = len(r)//ntr
    r = r[:nt*ntr].reshape(nt, ntr, 8)
    m = m[:nt*ntr].reshape(nt, ntr, 17)
    for i in range(nt):
        o = np.argsort(r[i, :, 1])
        r[i] = r[i, o]
        o = np.argsort(m[i, :, 1])
        m[i] = m[i, o]
    assert np.all(r[:, :, 1] == np.arange(ntr)[None, :]), "trajectory tags incomplete"
    t = r[:, 0, 0]
    x = unwrap(r[:, :n, 2], q[None, :], L)
    u = r[:, :n, 5:8]
    alpha = m[:, :n, 2]
    beta = m[:, :n, 3:6]
    g = m[:, :n, 6:12]       # xx xy xz yy yz zz
    G = np.empty(g.shape[:2] + (3, 3))
    idx = [(0, 0, 0), (0, 1, 1), (0, 2, 2), (1, 1, 3), (1, 2, 4), (2, 2, 5)]
    for i, j, c in idx:
        G[..., i, j] = g[..., c]
        G[..., j, i] = g[..., c]
    Gi = np.linalg.inv(G)
    uu = np.einsum("tpij,tpj->tpi", Gi, u)      # u^i = gamma^ij u_j
    W = np.sqrt(1.0 + (uu*u).sum(axis=-1))
    v = alpha*uu[..., 0]/W - beta[..., 0]       # dx/dt
    # spread of the x line from the y and z lines (plane symmetry, tracked particles)
    out = {"kind": "gr", "dir": rundir, "n": n, "L": L, "d": d, "t": t,
           "a": (1.0 + 0.5*t)**2, "x": x, "v": v, "q": q, "x0": x[0], "u_perp":
           np.abs(u[..., 1:]).max(axis=(1, 2)), "alpha": alpha, "gxx": g[..., 0]}
    c = np.loadtxt(os.path.join(rundir, "east.cstat.hst"))
    out["cstat"] = c
    return out


def load_newton(rundir, scale=1.0):
    z = np.load(os.path.join(rundir, "newton.npz"))
    L = float(z["L"])*scale
    out = {"kind": "newton", "dir": rundir, "n": int(z["n"]), "L": L,
           "d": float(z["delta"]), "t": z["tau"], "a": z["a"],
           "x": z["x"]*scale, "v": z["v"]*scale, "q": z["q"]*scale,
           "x0": z["x"][0]*scale, "prof_tau": z["prof_tau"],
           "prof_delta": z["prof_delta"], "prof_spread": z["prof_spread_x"]*scale,
           "prof_vperp": z["prof_max_vperp"]*scale}
    return out


def read_field(path):
    with open(path, "rb") as f:
        magic = f.read(8)
        t = struct.unpack("d", f.read(8))[0]
        n = np.fromfile(f, dtype=np.int64, count=3)
        nc = int(n[0]*n[1]*n[2])
        shape = (int(n[2]), int(n[1]), int(n[0]))
        out = {"t": t}
        for key in ("E", "chi"):
            out[key] = np.fromfile(f, dtype=np.float32, count=nc).astype(float) \
                .reshape(shape).transpose(2, 1, 0)
        if magic == b"NRFIELD2":
            for key in ("H", "Mx", "My", "Mz", "Khat", "Theta", "alpha"):
                out[key] = np.fromfile(f, dtype=np.float64, count=nc).reshape(shape) \
                    .transpose(2, 1, 0)
    return out


def read_snapshot(path):
    with open(path, "rb") as f:
        f.read(8)
        t, = struct.unpack("d", f.read(8))
        n, = struct.unpack("q", f.read(8))
        f.read(8)
        d = np.fromfile(f, dtype=np.float64, count=7*n).reshape(n, 7)
        tag = np.fromfile(f, dtype=np.int32, count=n)
    return t, d, tag


def lattice_plane_of_tag(n, L):
    """Lattice index along x of every tag, reproducing the order of make_east.py."""
    q1 = (np.arange(n) + 1.0)*L/n
    ic = int(np.argmin(np.abs(q1 - 0.25*L)))
    I = [b.ravel() for b in np.meshgrid(np.arange(n), np.arange(n), np.arange(n),
                                        indexing="ij")]
    on = [(I[1] == ic) & (I[2] == ic), (I[0] == ic) & (I[2] == ic),
          (I[0] == ic) & (I[1] == ic)]
    centre = on[0] & on[1]
    first = np.concatenate([np.flatnonzero(on[0]), np.flatnonzero(on[1] & ~centre),
                            np.flatnonzero(on[2] & ~centre)])
    rest = np.ones(n**3, dtype=bool)
    rest[first] = False
    order = np.concatenate([first, np.flatnonzero(rest)])
    return I[0][order]


# ---------------------------------------------------------------------------------------
# comparisons
# ---------------------------------------------------------------------------------------
def zel(run):
    """Zel'dovich positions and velocities of the run's sheets at its record times."""
    xz = np.empty_like(run["x"])
    vz = np.empty_like(run["v"])
    for i, a in enumerate(run["a"]):
        xz[i], vz[i], _ = Z.continuum(run["x0"], a, run["d"], run["L"])
    return xz, vz


def errors(run):
    k = 2.0*np.pi/run["L"]
    d = run["d"]
    xz, vz = zel(run)
    a = run["a"]
    with np.errstate(divide="ignore", invalid="ignore"):
        ex = np.abs(run["x"] - xz).max(axis=1)/((a - 1.0)*d/k)
        ev = np.abs(run["v"] - vz).max(axis=1)/(np.sqrt(a)*d/k)
    return ex, ev, xz, vz


def at(arr, a_rec, a):
    i = int(np.argmin(np.abs(a_rec - a)))
    return float(arr[i]), float(a_rec[i])


def lagrangian_density_error(run, a):
    """Largest |rho_run / rho_Zel - 1| over sheets from centred differences of positions
    (the same mass differences in both, so they cancel)."""
    i = int(np.argmin(np.abs(run["a"] - a)))
    x = run["x"][i]
    xz, _, _ = Z.continuum(run["x0"], run["a"][i], run["d"], run["L"])
    dx = np.roll(x, -1) - np.roll(x, 1)
    dxz = np.roll(xz, -1) - np.roll(xz, 1)
    dx[0] += run["L"]
    dx[-1] += run["L"]
    dxz[0] += run["L"]
    dxz[-1] += run["L"]
    return float(np.abs(dxz/dx - 1.0).max())


def deposit_1d(x, m, n, L, comp=True):
    """Plane-averaged density of sheets x (masses m per sheet, mean one) on n cells with
    the cubic cloud and the compensation pass of the production configuration (along x
    only: the y and z passes leave a plane-symmetric field unchanged)."""
    h = L/n
    xi = np.mod(x, L)/h - 0.5
    i0 = np.floor(xi).astype(int)
    s = xi - i0
    wts = [(1.0 - s)**3/6.0, (3.0*s**3 - 6.0*s**2 + 4.0)/6.0,
           (-3.0*s**3 + 3.0*s**2 + 3.0*s + 1.0)/6.0, s**3/6.0]
    rho = np.zeros(n)
    for c, w in enumerate(wts):
        np.add.at(rho, (i0 - 1 + c) % n, m*w)
    rho *= n/m.sum()
    if comp:
        c1, c2 = 1.0/6.0, 0.4666666666666667
        up, um, upp = np.roll(rho, -1), np.roll(rho, 1), np.roll(rho, -2)
        f = c1*(up - rho) - (c2/16.0)*(upp - 3.0*up + 3.0*rho - um)
        rho = rho - f + np.roll(f, 1)
    return rho


# ---------------------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gr", required=True)
    ap.add_argument("--newton", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res = {"gr_run": a.gr, "newton_run": a.newton}

    gr = {c: load_gr(os.path.join(a.gr, c)) for c in ("L1_n32", "L1_n64", "L1_n96", "L4_n64")
          if os.path.exists(os.path.join(a.gr, c, "east.traj.bin"))}
    nw = {f"N_n{n}": load_newton(os.path.join(a.newton, f"n{n}")) for n in (32, 64)
          if os.path.exists(os.path.join(a.newton, f"n{n}", "newton.npz"))}
    if "N_n64" in nw:
        nw["N4_n64"] = load_newton(os.path.join(a.newton, "n64"), scale=4.0)
    runs = {**gr, **nw}

    # exact-sheet crossing of each lattice (positions at a = 1 of the run)
    for name, r in runs.items():
        e = {}
        ex, ev, xz, vz = errors(r)
        r["ex"], r["ev"] = ex, ev
        for aa in A_EVAL:
            e[f"ex_a{aa:g}"], _ = at(ex, r["a"], aa)
            e[f"ev_a{aa:g}"], _ = at(ev, r["a"], aa)
            e[f"rhoL_a{aa:g}"] = lagrangian_density_error(r, aa)
        e["a_cross"] = Z.first_crossing_a(r["x"], r["a"])
        ag = np.linspace(15.0, 25.0, 20001)
        xzz = np.array([Z.continuum(r["x0"], aa, r["d"], r["L"])[0] for aa in ag])
        e["a_cross_zeldovich_sheets"] = Z.first_crossing_a(xzz, ag)
        e["a_end"] = float(r["a"][-1])
        e["n"], e["L"] = r["n"], r["L"]
        res[name] = e
        print(name, json.dumps({k: (round(v, 6) if isinstance(v, float) else v)
                                for k, v in e.items()}))

    # relativistic minus Newtonian positions at equal time, same cells
    for gname, nname in (("L1_n32", "N_n32"), ("L1_n64", "N_n64"), ("L4_n64", "N4_n64")):
        if gname not in gr or nname not in nw:
            continue
        g, w = gr[gname], nw[nname]
        k = 2.0*np.pi/g["L"]
        dd = {}
        for aa in A_EVAL + [21.0]:
            ig = int(np.argmin(np.abs(g["a"] - aa)))
            xw = np.array([np.interp(g["t"][ig], w["t"], w["x"][:, j])
                           for j in range(g["n"])])
            vw = np.array([np.interp(g["t"][ig], w["t"], w["v"][:, j])
                           for j in range(g["n"])])
            ag = g["a"][ig]
            dd[f"dx_a{aa:g}"] = float(np.abs(g["x"][ig] - xw).max()/((ag - 1.0)*g["d"]/k))
            dd[f"dv_a{aa:g}"] = float(np.abs(g["v"][ig] - vw).max()/(np.sqrt(ag)*g["d"]/k))
        dd["a_cross_ratio_gr_over_newton"] = res[gname]["a_cross"]/res[nname]["a_cross"]
        res[f"diff_{gname}_{nname}"] = dd
        print("diff", gname, nname, json.dumps({k: round(v, 6) for k, v in dd.items()}))

    # constraints
    cols = {"Hr_max": 10, "Hr_mean": 11, "Mr_max": 14, "Mr_mean": 15, "Z_mean": 17,
            "Theta_mean": 18, "E_min": 5, "E_max": 6}
    for name, g in gr.items():
        c = g["cstat"]
        ac = (1.0 + 0.5*c[:, 0])**2
        con = {}
        for key, col in cols.items():
            con[key] = {f"{aa:g}": at(c[:, col], ac, aa)[0] for aa in A_CON}
        con["finite"] = bool(np.isfinite(c).all())
        g["acon"] = ac
        res[f"constraints_{name}"] = con
        print("constraints", name, "Hr_mean", {k: f"{v:.2e}" for k, v in con["Hr_mean"].items()})
        print("constraints", name, "Mr_mean", {k: f"{v:.2e}" for k, v in con["Mr_mean"].items()})

    # plane symmetry: snapshots of the relativistic runs, Newtonian profile records
    for name, g in gr.items():
        n, L = g["n"], g["L"]
        plane = lattice_plane_of_tag(n, L)
        sym = []
        for p in sorted(glob.glob(os.path.join(g["dir"], "east.part.*.bin"))):
            t, dsn, tag = read_snapshot(p)
            ix = plane[tag]
            xl = np.empty(n)
            onl = tag < n
            xl[tag[onl]] = dsn[onl, 0]
            dx = dsn[:, 0] - xl[ix]
            dx -= L*np.round(dx/L)
            sym.append({"t": t, "a": (1 + t/2)**2, "spread_x_over_L": float(np.abs(dx).max()/L),
                        "max_u_perp": float(np.abs(dsn[:, 4:6]).max()),
                        "max_u_x": float(np.abs(dsn[:, 3]).max()), "N": int(len(tag))})
        res[f"symmetry_{name}"] = sym
        print("symmetry", name, [(round(s["a"], 2), f"{s['spread_x_over_L']:.1e}",
                                  f"{s['max_u_perp']:.1e}") for s in sym])
    for name, w in nw.items():
        res[f"symmetry_{name}"] = [{"tau": float(t), "spread_x_over_L": float(s/w["L"]),
                                    "max_v_perp": float(vp)} for t, s, vp in
                                   zip(w["prof_tau"], w["prof_spread"], w["prof_vperp"])]

    # Eulerian profiles at the field dumps of the 64-cell relativistic run
    prof = {}
    if "L1_n64" in gr:
        g = gr["L1_n64"]
        for p in sorted(glob.glob(os.path.join(g["dir"], "east.field.*.bin"))):
            f = read_field(p)
            prof[os.path.basename(p)] = f
    res["field_files_L1_n64"] = sorted(prof.keys())

    with open(os.path.join(a.out, "pancake.json"), "w") as fh:
        json.dump(res, fh, indent=1, default=float)
    make_figures(runs, gr, nw, prof, res, a.out)


# ---------------------------------------------------------------------------------------
def make_figures(runs, gr, nw, prof, res, out):
    fs.use_style()
    import matplotlib.pyplot as plt
    P = fs.PAL
    style = {"L1_n32": dict(color=P["red"], ls=":", lw=1.2),
             "L1_n64": dict(color=P["red"], ls="-"),
             "L1_n96": dict(color=P["yellow"], ls="-"),
             "L4_n64": dict(color=P["green"], ls="-"),
             "N_n32": dict(color=P["blue"], ls=":", lw=1.2),
             "N_n64": dict(color=P["blue"], ls="--")}
    label = {"L1_n32": "GR, $L=1$, 32", "L1_n64": "GR, $L=1$, 64",
             "L1_n96": "GR, $L=1$, 96", "L4_n64": "GR, $L=4$, 64",
             "N_n32": "Newton PM, 32", "N_n64": "Newton PM, 64"}

    # 1. errors against Zel'dovich
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.3))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.14, top=0.95, wspace=0.27)
    for name in ("N_n32", "N_n64", "L1_n32", "L1_n64", "L1_n96", "L4_n64"):
        if name not in runs:
            continue
        r = runs[name]
        m = (r["a"] > 1.05) & (r["a"] < 21.5)
        axs[0].semilogy(r["a"][m], r["ex"][m], label=label[name], **style[name])
        axs[1].semilogy(r["a"][m], r["ev"][m], **style[name])
    for ax in axs:
        ax.axvline(21.0, **fs.MASK_LINE)
        ax.set_xlabel(r"$a$")
        ax.set_xlim(1, 21.5)
    axs[0].set_ylabel(r"max $|x - x_{\rm Z}|\,/\,[(a-1)\delta/k]$")
    axs[1].set_ylabel(r"max $|v - v_{\rm Z}|\,/\,[a^{1/2}\delta/k]$")
    axs[0].legend(loc="upper left", ncol=2, fontsize=8)
    fs.save(fig, os.path.join(out, "pancake_errors"))
    plt.close(fig)

    # 2. profiles: Eulerian density (mesh) and velocity of the sheets, a = 5, 15, 20
    if "L1_n64" in gr and "N_n64" in nw:
        g, w = gr["L1_n64"], nw["N_n64"]
        L, d = g["L"], g["d"]
        k = 2.0*np.pi/L
        targets = [5.0, 15.0, 20.0]
        fig, axs = plt.subplots(3, 3, figsize=(fs.FULL_WIDTH, 6.6), sharex=True)
        fig.subplots_adjust(left=0.09, right=0.98, bottom=0.08, top=0.97, wspace=0.3,
                            hspace=0.08)
        xc = (np.arange(g["n"]) + 0.5)*L/g["n"]
        xf = np.linspace(0, L, 4001)
        fields = list(prof.values())
        for j, aa in enumerate(targets):
            # relativistic: field dump nearest to aa
            af = np.array([(1 + 0.5*f["t"])**2 for f in fields])
            f = fields[int(np.argmin(np.abs(af - aa)))]
            af_ = (1 + 0.5*f["t"])**2
            E = f["E"].mean(axis=(1, 2))
            dE = E/E.mean() - 1.0
            # Newtonian mesh profile nearest to aa
            ap_ = (1 + 0.5*w["prof_tau"])**2
            ip = int(np.argmin(np.abs(ap_ - aa)))
            dN = w["prof_delta"][ip]
            # Zel'dovich: continuum, and the deposit of the Zel'dovich sheets
            rz = Z.eulerian_density(xf, af_, d, L) - 1.0
            xzs, _, _ = Z.continuum(g["x0"], af_, d, L)
            dz_dep = deposit_1d(xzs, np.ones_like(xzs), g["n"], L) - 1.0
            ax = axs[0, j]
            ax.plot(xf, rz, **fs.GUIDE, label="Zel'dovich")
            ax.plot(xc, dN, color=P["blue"], ls="none", marker="o", ms=3,
                    label="Newton PM 64")
            ax.plot(xc, dE, color=P["red"], ls="none", marker="x", ms=3,
                    label="GR 64 ($E$)")
            ax.set_title(f"$a = {af_:.1f}$", fontsize=10)
            ax2 = axs[1, j]
            ax2.axhline(0.0, **fs.THIN)
            ax2.plot(xc, dN - dz_dep, color=P["blue"], marker="o", ms=2.5, lw=1.0,
                     label="PM $-$ deposit(Z)")
            ax2.plot(xc, dE - dz_dep, color=P["red"], marker="x", ms=2.5, lw=1.0,
                     label="GR $-$ deposit(Z)")
            ax2.plot(xc, dz_dep - (Z.eulerian_density(xc, af_, d, L) - 1.0),
                     color="grey", lw=1.0, label="deposit(Z) $-$ Z")
            # velocities of the sheets
            ig = int(np.argmin(np.abs(g["a"] - aa)))
            iw = int(np.argmin(np.abs(w["a"] - aa)))
            ax3 = axs[2, j]
            xz, vz, _ = Z.continuum(g["x0"], g["a"][ig], d, L)
            o = np.argsort(np.mod(xz, L))
            ax3.plot(np.mod(xz, L)[o], vz[o]/(d/k), **fs.GUIDE)
            ax3.plot(np.mod(w["x"][iw], L), w["v"][iw]/(d/k), color=P["blue"], ls="none",
                     marker="o", ms=3)
            ax3.plot(np.mod(g["x"][ig], L), g["v"][ig]/(d/k), color=P["red"], ls="none",
                     marker="x", ms=3)
            ax3.set_xlabel(r"$x/L$", labelpad=-1)
        axs[0, 0].set_ylabel(r"density contrast")
        axs[1, 0].set_ylabel(r"residual")
        axs[2, 0].set_ylabel(r"$v\,/\,(\delta/k)$")
        axs[0, 0].legend(loc="upper right", fontsize=7)
        axs[1, 0].legend(loc="lower right", fontsize=7)
        fs.save(fig, os.path.join(out, "pancake_profiles"))
        plt.close(fig)

    # 3. relativistic minus Newtonian positions over the sheets
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH, 3.0))
    fig.subplots_adjust(left=0.115, right=0.98, bottom=0.16, top=0.9, wspace=0.38)
    for j, (gname, nname) in enumerate((("L1_n32", "N_n32"), ("L1_n64", "N_n64"),
                                        ("L4_n64", "N4_n64"))):
        if gname not in gr or nname not in nw:
            continue
        g, w = gr[gname], nw[nname]
        k = 2.0*np.pi/g["L"]
        cols = fs.series_colors(4)
        for c, aa in zip(cols, (5.0, 10.0, 15.0, 20.0)):
            ig = int(np.argmin(np.abs(g["a"] - aa)))
            xw = np.array([np.interp(g["t"][ig], w["t"], w["x"][:, jj])
                           for jj in range(g["n"])])
            ag = g["a"][ig]
            axs[j].plot(g["x0"]/g["L"], (g["x"][ig] - xw)/((ag - 1.0)*g["d"]/k),
                        color=c, lw=1.2, label=f"$a = {ag:.0f}$")
        axs[j].set_title(label[gname] + " $-$ PM", fontsize=9)
        axs[j].set_xlabel(r"$x_0/L$")
    axs[0].set_ylabel(r"$(x_{\rm GR} - x_{\rm PM})\,/\,[(a-1)\delta/k]$")
    axs[0].legend(loc="best", fontsize=7)
    fs.save(fig, os.path.join(out, "pancake_grdiff"))
    plt.close(fig)

    # 4. phase space through and after the crossing
    fig, axs = plt.subplots(1, 4, figsize=(fs.FULL_WIDTH, 2.6), sharey=True)
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.18, top=0.9, wspace=0.06)
    for j, aa in enumerate((21.5, 25.0, 30.0, 41.9)):
        for name, mk in (("N_n64", "o"), ("L1_n64", "x"), ("L1_n96", "+"),
                         ("L4_n64", "s")):
            if name not in runs:
                continue
            r = runs[name]
            i = int(np.argmin(np.abs(r["a"] - aa)))
            if abs(r["a"][i] - aa) > 0.5:
                continue
            k = 2.0*np.pi/r["L"]
            xx = np.mod(r["x"][i]/r["L"] - 0.25 + 0.5, 1.0) - 0.5
            axs[j].plot(xx, r["v"][i]/(r["d"]/k)/np.sqrt(r["a"][i]),
                        ls="none", marker=mk, ms=2.5, mfc="none",
                        color=style[name]["color"], label=label[name])
        axs[j].set_title(f"$a = {aa:.0f}$", fontsize=10)
        axs[j].set_xlabel(r"$x/L - 1/4$")
        axs[j].set_xlim(-0.12, 0.12)
    axs[0].set_ylabel(r"$v\,/\,(a^{1/2}\delta/k)$")
    axs[0].legend(loc="lower left", fontsize=6)
    fs.save(fig, os.path.join(out, "pancake_phase"))
    plt.close(fig)

    # 5. constraints
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.2))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.15, top=0.95, wspace=0.27)
    for name in ("L1_n32", "L1_n64", "L1_n96", "L4_n64"):
        if name not in gr:
            continue
        c = gr[name]["cstat"]
        ac = gr[name]["acon"]
        axs[0].loglog(ac, c[:, 11], label=label[name], **style[name])
        axs[0].loglog(ac, c[:, 10], alpha=0.35, **{**style[name], "lw": 1.0})
        axs[1].loglog(ac, c[:, 15], **style[name])
        axs[1].loglog(ac, c[:, 14], alpha=0.35, **{**style[name], "lw": 1.0})
    for ax in axs:
        ax.axvline(21.0, **fs.MASK_LINE)
        ax.set_xlabel(r"$a$")
    axs[0].set_ylabel(r"$H_r$ (mean; max faint)")
    axs[1].set_ylabel(r"$M_r$ (mean; max faint)")
    axs[0].legend(loc="upper left", fontsize=8)
    fs.save(fig, os.path.join(out, "pancake_constraints"))
    plt.close(fig)

    # 6. where the constraint violation sits (64 cells, L = 1): H and M_x along x
    if prof:
        fields = list(prof.values())
        fig, axs = plt.subplots(2, 1, figsize=(fs.COLUMN_WIDTH*1.6, 4.4), sharex=True)
        fig.subplots_adjust(left=0.15, right=0.97, bottom=0.11, top=0.97, hspace=0.08)
        sel = [f for f in fields if (1 + 0.5*f["t"])**2 > 1.5]
        sel = [sel[i] for i in np.linspace(0, len(sel) - 1, 5).astype(int)]
        cols = fs.series_colors(len(sel))
        n = sel[0]["E"].shape[0]
        xc = (np.arange(n) + 0.5)/n
        for c, f in zip(cols, sel):
            af = (1 + 0.5*f["t"])**2
            E = f["E"].mean(axis=(1, 2))
            sc = 16.0*np.pi*E.mean()
            axs[0].semilogy(xc, np.abs(f["H"].mean(axis=(1, 2)))/sc + 1e-16, color=c,
                            lw=1.2, label=f"$a = {af:.0f}$")
            axs[1].semilogy(xc, np.abs(f["Mx"].mean(axis=(1, 2))) + 1e-16, color=c, lw=1.2)
        axs[0].set_ylabel(r"$|H|\,/\,16\pi\langle E\rangle$")
        axs[1].set_ylabel(r"$|M_x|$")
        axs[1].set_xlabel(r"$x/L$")
        axs[0].legend(loc="upper right", fontsize=7, ncol=2)
        fs.save(fig, os.path.join(out, "pancake_constraint_profiles"))
        plt.close(fig)


if __name__ == "__main__":
    main()
