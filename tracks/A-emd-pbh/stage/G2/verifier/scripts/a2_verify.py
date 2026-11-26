#!/usr/bin/env python3
"""Fresh verifier of gate G2 (Track A), item V2: first shell crossing of the triaxial peaks S1L, S1L-h and of the
Newtonian controls, with readers of my own.

- Snapshot format from the AthenaK source (nrpic_io.cpp 1112-1117): "NRPSNAP1", double time, int64 N, int64 ncycle,
  N records of 7 doubles (x^i, u_i, m), N int32 tags, N int32 species, N doubles (proper time of each particle).
- Lattice: the Lagrangian site of each tag from snapshot 0 (nearest site of the lattice of spacing L/n; the offset
  of the lattice is the median fractional position).
- Event (independent of the spatial coordinates): sign of J = det(dx/dq), forward differences on the periodic
  lattice (differences unwrapped to the nearest image); a crossing is J <= 0 in some lattice cell.
- Clocks: coordinate time t/t_H = (1 + 1.5 t)/r_m^3 (GR) or (1 + eta/2)^3/r_m^3 (Newtonian mode, conformal
  time); the dust's own clock: the proper time of the particles at the corners of the first-crossing cell
  (t/t_H = (1 + 1.5 tau)/r_m^3).
- Zel'dovich reference (JOURNAL entry 1): lambda = eigenvalues of -d psi_i/d q_j at the central site, psi = x - q
  of snapshot 0 (centred differences); a_sc = 1/lambda_max; t_Z/t_H = (a_sc/r_m^2)^(3/2).

    python -I a2_verify.py --out DIR --member NAME=DIR:gr|newton:IDJSON ...

test_lattice() checks the readers first on a synthetic Zel'dovich lattice with a known deformation tensor.
"""
import argparse
import glob
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import figstyle as fs  # noqa: E402


def read_snap(path):
    with open(path, "rb") as f:
        assert f.read(8) == b"NRPSNAP1", path
        t = float(np.frombuffer(f.read(8), "<f8")[0])
        N = int(np.frombuffer(f.read(8), "<i8")[0])
        ncyc = int(np.frombuffer(f.read(8), "<i8")[0])
        rec = np.frombuffer(f.read(56 * N), "<f8").reshape(N, 7)
        tag = np.frombuffer(f.read(4 * N), "<i4")
        _sp = np.frombuffer(f.read(4 * N), "<i4")
        rest = f.read()
    tau = np.frombuffer(rest[:8 * N], "<f8") if len(rest) >= 8 * N else None
    return dict(t=t, N=N, ncyc=ncyc, x=rec[:, :3].copy(), u=rec[:, 3:6].copy(), m=rec[:, 6].copy(), tag=tag.copy(),
                tau=None if tau is None else tau.copy())


def wrap(d, L):
    return d - L * np.round(d / L)


class Lattice:
    def __init__(self, x0, tag0, n, L):
        self.n, self.L, self.h = n, L, L / n
        u = (x0 + L / 2) / self.h
        self.off = float(np.median(u - np.floor(u)))
        ijk = np.mod(np.round(u - self.off).astype(np.int64), n)
        self.site_of_tag = {}
        idx = (ijk[:, 0] * n + ijk[:, 1]) * n + ijk[:, 2]
        assert len(np.unique(idx)) == len(idx) == n ** 3, "not one particle per site"
        self.tagmax = int(tag0.max())
        self.map = np.full(self.tagmax + 1, -1, np.int64)
        self.map[tag0] = idx
        g = (np.arange(n) + self.off) * self.h - L / 2
        self.q1 = g

    def grid(self, x, tag, fill=np.nan):
        n = self.n
        X = np.full((n ** 3, x.shape[1]) if x.ndim == 2 else (n ** 3,), fill)
        ok = tag <= self.tagmax
        X[self.map[tag[ok]]] = x[ok]
        return X.reshape((n, n, n) + ((x.shape[1],) if x.ndim == 2 else ()))


def jac_forward(X, L, h):
    d = []
    for a in range(3):
        d.append(wrap(np.roll(X, -1, axis=a) - X, L) / h)      # column a: dx/dq_a
    M = np.stack(d, axis=-1)                                   # [..., i(component), a]
    return np.linalg.det(M)


def axial_sep(X, L, h):
    return [np.nanmin(wrap(np.roll(X[..., a], -1, axis=a) - X[..., a], L) / h) for a in range(3)]


def deformation(X, lat):
    """-d psi_i/d q_j at the site nearest the origin (centred differences), psi = x - q."""
    n, L, h = lat.n, lat.L, lat.h
    q = np.stack(np.meshgrid(lat.q1, lat.q1, lat.q1, indexing="ij"), axis=-1)
    psi = wrap(X - q, L)
    c = int(np.argmin(np.abs(lat.q1)))
    D = np.zeros((3, 3))
    for j in range(3):
        sp = [c, c, c]
        sm = [c, c, c]
        sp[j] = (c + 1) % n
        sm[j] = (c - 1) % n
        D[:, j] = -(psi[tuple(sp)] - psi[tuple(sm)]) / (2 * h)
    lam, vec = np.linalg.eigh(0.5 * (D + D.T))
    return dict(site=[c, c, c], q=float(lat.q1[c]), D=D.tolist(), lam=lam[::-1].tolist(),
                axis_of_max=[float(v) for v in vec[:, -1]])


def test_lattice():
    """x = q + a psi(q), psi = grad phi (inward), phi = A exp(-sum (q_i/s_i)^2 / 2): lambda at the centre = A/s_i^2;
    the lattice of the runs (64 sites on 20), so the centred difference carries the truncation of the real data."""
    n, L = 64, 20.0
    h = L / n
    g = (np.arange(n) + 0.5) * h - L / 2
    q = np.stack(np.meshgrid(g, g, g, indexing="ij"), axis=-1)
    A, s = 0.5, np.array([3.0, 2.5, 2.0])
    phi = A * np.exp(-0.5 * np.sum((q / s) ** 2, axis=-1))
    psi = -(q / s ** 2) * phi[..., None]               # grad phi: inward, a peak
    lam_exact = A / s ** 2
    rows = []
    x0 = q + psi
    tag = np.arange(n ** 3, dtype=np.int32)
    lat = Lattice(x0.reshape(-1, 3), tag, n, L)
    X0 = lat.grid(x0.reshape(-1, 3), tag)
    dfm = deformation(X0, lat)
    # centred difference of a Gaussian at a site h/2 off the centre: compare with the analytic tensor at that site
    qc = np.array([dfm["q"]] * 3)
    # analytic -d psi_i/d q_j at qc
    ph = A * math.exp(-0.5 * float(np.sum((qc / s) ** 2)))
    Dex = -(np.diag(1 / s ** 2) - np.outer(qc / s ** 2, qc / s ** 2)) * ph
    lam_site = np.sort(np.linalg.eigvalsh(-Dex))[::-1]
    for a in (1.0, 2.0, 1 / lam_exact[2] * 0.95, 1 / lam_exact[2] * 1.05):
        x = q + a * psi
        X = lat.grid(x.reshape(-1, 3), tag)
        J = jac_forward(X, L, h)
        rows.append(dict(a=a, minJ=float(J.min()), nneg=int((J <= 0).sum())))
    ok = (abs(dfm["lam"][0] - lam_site[0]) / lam_site[0] < 0.02 and rows[2]["minJ"] > 0 and rows[3]["minJ"] <= 0)
    return dict(lam_measured=dfm["lam"], lam_site=lam_site.tolist(), lam_centre=sorted(lam_exact.tolist())[::-1],
                rows=rows, passed=bool(ok))


def analyse(name, d, clock, idjson):
    with open(idjson) as f:
        idd = json.load(f)
    n, L, rm = int(idd["n"]), float(idd["L"]), float(idd["r_m"])
    files = sorted(glob.glob(os.path.join(d, "peak.part.*.bin")))
    s0 = read_snap(files[0])
    lat = Lattice(s0["x"], s0["tag"], n, L)
    X0 = lat.grid(s0["x"], s0["tag"])
    dfm = deformation(X0, lat)
    lam = dfm["lam"]
    tz = [(1.0 / (l * rm ** 2)) ** 1.5 if l > 0 else None for l in lam]

    def clk(t):
        return (1 + 1.5 * t) / rm ** 3 if clock == "gr" else (1 + t / 2) ** 3 / rm ** 3

    rows = []
    for fp in files:
        s = read_snap(fp)
        X = lat.grid(s["x"], s["tag"])
        J = jac_forward(X, L, lat.h)
        fin = np.isfinite(J)
        mJ = float(np.nanmin(J))
        am = np.unravel_index(np.nanargmin(np.where(fin, J, np.inf)), J.shape)
        row = dict(t=s["t"], t_tH=clk(s["t"]), N=s["N"], minJ=mJ, nneg=int(np.sum(J[fin] <= 0)),
                   argmin=[int(v) for v in am], argmin_q=[float(lat.q1[v]) for v in am],
                   sep=[float(v) for v in axial_sep(X, L, lat.h)])
        if s["tau"] is not None and clock == "gr":
            T = lat.grid(s["tau"], s["tag"])
            corners = [T[tuple((np.array(am) + np.array([a, b, c])) % n)] for a in (0, 1) for b in (0, 1) for c in (0, 1)]
            row["tau_corners_min"] = float(np.nanmin(corners))
            row["tau_corners_max"] = float(np.nanmax(corners))
            ci = int(np.argmin(np.abs(lat.q1)))
            row["tau_centre"] = float(T[ci, ci, ci])
            U = lat.grid(s["u"], s["tag"])
            row["u_centre_abs"] = float(np.linalg.norm(U[ci, ci, ci]))
        rows.append(row)
    # bracket of the first crossing
    br = None
    for r0, r1 in zip(rows[:-1], rows[1:]):
        if r0["minJ"] > 0 and r1["minJ"] <= 0:
            br = dict(t=[r0["t"], r1["t"]], t_tH=[r0["t_tH"], r1["t_tH"]], cell=r1["argmin"], cell_q=r1["argmin_q"],
                      nneg=r1["nneg"])
            if "tau_corners_min" in r0:
                br["tau_tH_last_positive"] = [(1 + 1.5 * r0["tau_corners_min"]) / rm ** 3,
                                              (1 + 1.5 * r0["tau_corners_max"]) / rm ** 3]
                br["tau_tH_first_crossed"] = [(1 + 1.5 * r1["tau_corners_min"]) / rm ** 3,
                                              (1 + 1.5 * r1["tau_corners_max"]) / rm ** 3]
                br["tau_centre_tH"] = [(1 + 1.5 * r0["tau_centre"]) / rm ** 3, (1 + 1.5 * r1["tau_centre"]) / rm ** 3]
            break
        if rows[0]["minJ"] <= 0:
            br = dict(note="crossed in snapshot 0")
    # first axis: first snapshot with a non-positive neighbour separation along each axis
    axes = {}
    for a, nm in enumerate("xyz"):
        for r0, r1 in zip(rows[:-1], rows[1:]):
            if r0["sep"][a] > 0 and r1["sep"][a] <= 0:
                axes[nm] = [r0["t_tH"], r1["t_tH"]]
                break
    return dict(name=name, dir=d, clock=clock, n=n, L=L, r_m=rm, mu=idd.get("mu"), e=idd.get("e"),
                deformation=dfm, t_zeldovich_tH=tz, lattice_offset=lat.off, rows=rows, bracket=br, axis_brackets=axes)


def figure(res, path):
    fs.use_style()
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.0))
    a = fs.inch_axes(fig, 0.6, 0.45, 3.3, 2.35)
    b = fs.inch_axes(fig, 4.55, 0.45, 3.3, 2.35)
    col = {"S1L": fs.PAL["red"], "S1L-h": fs.PAL["orange"], "N-z": fs.PAL["green"], "N-z128": fs.PAL["yellow"]}
    for nm, m in res["members"].items():
        t = [r["t_tH"] for r in m["rows"]]
        J = [r["minJ"] for r in m["rows"]]
        a.plot(t, J, "o-", ms=2.5, color=col.get(nm, "k"), label=nm)
        tz = m["t_zeldovich_tH"][0]
        a.axvline(tz, color=col.get(nm, "k"), ls=":", lw=0.8)
        lam = m["deformation"]["lam"][0]
        tt = np.linspace(min(t), max(t), 200)
        aa = (tt * m["r_m"] ** 3) ** (2 / 3) / 1.0
        b.plot(t, [r["sep"][2] for r in m["rows"]], "o-", ms=2.5, color=col.get(nm, "k"), label=nm)
        b.plot(tt, 1 - lam * aa, ":", color=col.get(nm, "k"), lw=0.8)
    a.axvspan(3.4, 5.0, color=fs.PAL["blue"], alpha=0.12, lw=0)
    a.axvspan(12.5, 15.2, color=fs.PAL["blue"], alpha=0.12, lw=0)
    a.axhline(0, color="k", lw=0.6)
    a.set_xlim(0, 22)
    a.set_ylim(-0.3, 1.05)
    a.set_xlabel(r"$t/t_H$ (coordinate clock)")
    a.set_ylabel(r"$\min J$, $J=\det(\partial x/\partial q)$")
    a.legend(fontsize=6, loc="upper right")
    b.axhline(0, color="k", lw=0.6)
    b.set_xlim(0, 22)
    b.set_ylim(-0.3, 1.05)
    b.set_xlabel(r"$t/t_H$")
    b.set_ylabel(r"$\min\,\Delta z/h$ (dotted: $1-\lambda_z a$)")
    return fs.save(fig, path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--member", action="append", default=[], help="NAME=DIR:gr|newton:IDJSON")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res = dict(test=test_lattice(), members={})
    print("lattice test:", json.dumps(res["test"]), flush=True)
    for spec in a.member:
        nm, rest = spec.split("=", 1)
        d, clock, idj = rest.split(":")
        m = analyse(nm, d, clock, idj)
        res["members"][nm] = m
        print(nm, "lambda", ["%.5f" % v for v in m["deformation"]["lam"]], "tZ", m["t_zeldovich_tH"],
              "bracket", json.dumps(m["bracket"]), "axes", m["axis_brackets"], flush=True)
    res["figure"] = figure(res, os.path.join(a.out, "fig_a2_verify"))
    with open(os.path.join(a.out, "a2_verify.json"), "w") as f:
        json.dump(res, f, indent=1)


if __name__ == "__main__":
    main()
