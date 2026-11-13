"""Reduce the prolate-spheroid collapse run to the arrays of fig_prolate.py.

This is the only script of the prolate-collapse figure that reads the simulation
outputs and the analysis modules of the repository; the figure script reads
paper/data/prolate.npz alone. Cold homogeneous prolate spheroid of collisionless
matter, eccentricity 0.9, polar semi-axis b = 10 M along z, total (ADM) mass M = 1,
10^4 equal-mass macroparticles at rest (Monte Carlo sample with reflection and
half-turn symmetry), adaptive mesh with finest cells of M/16, four binomial filter
passes plus the compensation pass, lapse excision at 0.05, evolved to 45 M.

Kept:
- four particle snapshots (x and z of every particle) at the snapshot times nearest
  to the times of the original paper's figure (0, 20.5, 27.75, 32 M; 27.75 M lies
  half-way between two snapshots, the earlier one, 27.5 M, is taken);
- from every snapshot (every 0.5 M): time, particle number, largest |z| of the
  particles (the tip of the spindle);
- the curvature history (every 0.25 M): largest Kretschmann scalar on the mesh and its
  position, largest energy density and its position;
- the particle history (every step): smallest lapse on the mesh, particle number,
  number of removed particles, MeshBlock count, and the time step (from the record
  times; it drops when finer mesh levels appear);
- the apparent-horizon searches (every 0.25 M from 20 M): time, irreducible mass,
  area, mean coordinate radius; from the shape coefficients the coordinate radius
  along +z and -z and in the equatorial direction at every detection, and the
  section of the first horizon in the plane y = 0;
- the norm of the Hamiltonian constraint against time (sqrt of H-norm2).

    python3 paper/scripts/make_data_prolate.py
"""
import re
import sys
from math import factorial
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.dont_write_bytecode = True        # leave the analysis folders untouched
sys.path.insert(0, str(REPO / "analysis" / "diag"))
from common import (H, keep_last, read_athena_hst, read_curv_hst,  # noqa: E402
                    read_nrpic_hst, read_snapshot, snapshot_files, snapshot_times)

RUN = REPO / "runs" / "prolate" / "e09_v8"
BASE = "prol"
M_TOT = 1.0                           # ADM mass of the initial data (component mass)
ALPHA_EXC = 0.05                      # lapse threshold of particle excision
DX_FINEST = 1.0 / 16.0                # finest cell size of the run
B_POLAR = 10.0                        # polar semi-axis of the initial spheroid
ECC = 0.9
LMAX = 8                              # degree of the horizon shape expansion
# times of the original paper's figure: onset of axial focusing, narrow spindle,
# configuration after the first apparent horizon; its curvature slice is at 22.25 M
T_ORIGINAL = np.array([20.5, 27.75, 32.0])
T_ORIGINAL_SLICE = 22.25
# snapshots shown (every 0.5 M exist; 27.75 M is not a snapshot time)
T_SNAP = (0.0, 20.5, 27.5, 32.0)
OUT = HERE.parent / "data" / "prolate.npz"


# ---- apparent-horizon shape --------------------------------------------------------
def ylm(l, m, theta, phi):
    """Complex spherical harmonic in the Wigner-d form of the horizon finder
    (real and imaginary part)."""
    w = np.zeros_like(theta, dtype=float)
    c, s = np.cos(theta / 2.0), np.sin(theta / 2.0)
    for k in range(max(0, m), min(l + m, l) + 1):
        w += ((-1.0) ** k * c ** (2 * l + m - 2 * k) * s ** (2 * k - m)
              / (factorial(l + m - k) * factorial(l - k) * factorial(k) * factorial(k - m)))
    w *= np.sqrt((2 * l + 1) / (4 * np.pi)) * factorial(l) * np.sqrt(
        factorial(l + m) * factorial(l - m))
    return w * np.cos(m * phi), w * np.sin(m * phi)


def horizon_radius(coef, theta, phi):
    """Coordinate radius r(theta, phi) about the origin from the coefficients of the
    shape file (per l: a_l0, then a_lm^c, a_lm^s for m = 1 .. l; the m > 0 basis is
    sqrt(2) times the real and imaginary parts)."""
    r, i = np.zeros_like(theta, dtype=float), 0
    for l in range(LMAX + 1):
        re_, _ = ylm(l, 0, theta, phi)
        r += coef[i] * re_
        i += 1
        for m in range(1, l + 1):
            re_, im_ = ylm(l, m, theta, phi)
            r += np.sqrt(2.0) * (coef[i] * re_ + coef[i + 1] * im_)
            i += 2
    return r


def read_shapes(path):
    """{time: coefficient array} from the shape file (the last block of each time)."""
    out, t = {}, None
    for line in open(path):
        if line.startswith("#"):
            t = float(re.search(r"Time\s*=\s*([-+0-9.eE]+)", line).group(1))
        elif line.strip() and t is not None:
            out[t] = np.array(line.split(), dtype=float)
    return out


def read_horizon_all(path):
    """Every search of the summary file: time, mass, area, mean radius, min radius
    (nan where no horizon was found), de-duplicated in time."""
    rows = []
    for line in open(path):
        if line.startswith("#") or not line.strip():
            continue
        x = line.split()
        rows.append([float(x[1]), float(x[2]), float(x[7]), float(x[10]), float(x[11])])
    return keep_last(np.array(rows))


def main():
    d = RUN
    data = {"m_tot": M_TOT, "alpha_exc": ALPHA_EXC, "dx_finest": DX_FINEST,
            "b": B_POLAR, "ecc": ECC, "t_original": T_ORIGINAL,
            "t_original_slice": T_ORIGINAL_SLICE}

    # particle history
    h = read_nrpic_hst(str(d / f"{BASE}.nrpic.hst"))
    t = h[:, H["time"]]
    data.update(h_t=t, h_alpha_min=h[:, H["alpha_min"]], h_np=h[:, H["np"]],
                h_nexc=h[:, H["n_excised"]], h_nmb=h[:, H["nmb"]],
                h_dt=np.r_[np.diff(t), np.nan], n0=h[0, H["np"]],
                rest_mass=h[0, H["sum_m"]], m_excised_end=h[-1, H["m_excised"]])

    # snapshots
    files = snapshot_files(str(d), BASE)
    ts = snapshot_times(files)
    zmax, nsnap = np.full(len(files), np.nan), np.zeros(len(files))
    for k, p in enumerate(files):
        _, q, tag, _ = read_snapshot(p)
        nsnap[k] = len(tag)
        if len(tag):
            zmax[k] = np.abs(q[:, 2]).max()
    data.update(snap_t=ts, snap_n=nsnap, snap_zmax=zmax)
    for j, tw in enumerate(T_SNAP):
        k = int(np.argmin(np.abs(ts - tw)))
        tk, q, tag, _ = read_snapshot(files[k])
        data[f"p{j}_t"] = tk
        data[f"p{j}_x"] = q[:, 0].astype(np.float32)
        data[f"p{j}_z"] = q[:, 2].astype(np.float32)

    # curvature history
    c = read_curv_hst(str(d / f"{BASE}.curv.hst"))
    data.update(c_t=c[:, 0], c_I=c[:, 1], c_Ix=c[:, 2], c_Iy=c[:, 3], c_Iz=c[:, 4],
                c_E=c[:, 5], c_Ex=c[:, 6], c_Ey=c[:, 7], c_Ez=c[:, 8])

    # apparent horizon
    ah = read_horizon_all(d / f"{BASE}.horizon_summary_0.txt")
    data.update(ah_t_search=ah[:, 0], ah_M=ah[:, 1], ah_area=ah[:, 2],
                ah_rmean=ah[:, 3], ah_rmin=ah[:, 4])
    found = np.isfinite(ah[:, 1])
    shapes = read_shapes(d / f"{BASE}.horizon_shape_0.txt")
    tf = ah[found, 0]
    zero, pi = np.array([0.0]), np.array([np.pi])
    rp = np.array([horizon_radius(shapes[x], zero, zero)[0] for x in tf])
    rs = np.array([horizon_radius(shapes[x], pi, zero)[0] for x in tf])
    re_ = np.array([horizon_radius(shapes[x], np.array([np.pi / 2]), zero)[0] for x in tf])
    data.update(ah_t=tf, ah_r_north=rp, ah_r_south=rs, ah_r_eq=re_)
    t1 = tf[0]
    th = np.linspace(0.0, np.pi, 181)
    r_pos = horizon_radius(shapes[t1], th, np.zeros_like(th))      # x > 0 half
    r_neg = horizon_radius(shapes[t1], th, np.full_like(th, np.pi))  # x < 0 half
    sec_x = np.r_[r_pos * np.sin(th), -(r_neg * np.sin(th))[::-1]]
    sec_z = np.r_[r_pos * np.cos(th), (r_neg * np.cos(th))[::-1]]
    data.update(ah_first_t=t1, ah_sec_x=sec_x, ah_sec_z=sec_z)

    # constraints
    z = read_athena_hst(str(d / f"{BASE}.z4c.user.hst"))
    data.update(z_t=z["time"], z_Hnorm=np.sqrt(z["H-norm2"]))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT, **data)
    print(f"{d.relative_to(REPO)}: {len(h)} history records t = {t[0]:g} .. {t[-1]:g}; "
          f"{len(files)} snapshots; {len(c)} curvature records; {len(ah)} horizon "
          f"searches, {found.sum()} found; {len(shapes)} shapes")
    print(f"{OUT}  {OUT.stat().st_size / 1e6:.3f} MB")
    summary(data)


def summary(D):
    print("summary:")
    print("  snapshots shown: " + ", ".join(f"{D[f'p{j}_t']:g} M" for j in range(4)))
    # curvature
    cI, ct = D["c_I"], D["c_t"]
    i = int(np.argmax(cI))
    print(f"  largest Kretschmann scalar {cI[i]:.4g} M^-4 at t = {ct[i]:g} M, position "
          f"({D['c_Ix'][i]:.4f}, {D['c_Iy'][i]:.4f}, {D['c_Iz'][i]:.4f}) M")
    rc = np.hypot(D["c_Ix"], D["c_Iy"])
    print("  curvature maximum: |z| and cylindrical radius R of its cell, 18 .. 36 M:")
    for k in np.where((ct >= 18) & (ct <= 36))[0]:
        print(f"    t = {ct[k]:6.2f}  I = {cI[k]:8.2f}  |z| = {abs(D['c_Iz'][k]):6.3f}  "
              f"R = {rc[k]:.3f}  largest E {D['c_E'][k]:.3f} at |z| = "
              f"{abs(D['c_Ez'][k]):.3f}")
    j = int(np.argmax(D["c_E"]))
    print(f"  largest energy density {D['c_E'][j]:.4g} M^-2 at t = {ct[j]:g} M, position "
          f"({D['c_Ex'][j]:.4f}, {D['c_Ey'][j]:.4f}, {D['c_Ez'][j]:.4f}) M")
    dt = D["h_dt"]
    k = int(np.argmax(dt < 0.5 * dt[0]))
    print(f"  time step falls from {dt[0]:g} to {dt[k]:g} M at t = {D['h_t'][k]:.4f} M "
          f"(finer levels appear); I before/after: "
          f"{cI[ct <= D['h_t'][k]][-1]:.3g} / {cI[ct > D['h_t'][k]][0]:.3g}")
    # horizon
    M, tf = D["ah_M"][np.isfinite(D["ah_M"])], D["ah_t"]
    print(f"  first horizon t = {tf[0]:g} M, mass {M[0]:.5f}; largest {M.max():.5f} at "
          f"{tf[np.argmax(M)]:g} M; last {M[-1]:.5f} at {tf[-1]:g} M")
    print("  horizon mass over the last 5 M: " + ", ".join(
        f"{a:g}: {b:.5f}" for a, b in zip(tf, M) if a >= tf[-1] - 5.0 and
        (abs(a - round(a)) < 1e-9 or a == tf[-1])))
    p = np.polyfit(tf[tf >= 40], M[tf >= 40], 1)
    print(f"  slope of the horizon mass after 40 M: {p[0]:.2e} per M")
    print(f"  first horizon: polar radii {D['ah_r_north'][0]:.4f} / {D['ah_r_south'][0]:.4f}, "
          f"equatorial {D['ah_r_eq'][0]:.4f}, mean {D['ah_rmean'][np.isfinite(D['ah_M'])][0]:.4f}, "
          f"smallest on the finder's grid {D['ah_rmin'][np.isfinite(D['ah_M'])][0]:.4f} "
          f"(section: x in [{D['ah_sec_x'].min():.4f}, {D['ah_sec_x'].max():.4f}])")
    # particles, lapse, mesh
    ht, ne, n = D["h_t"], D["h_nexc"], D["h_np"]
    k0, k1 = int(np.argmax(ne > 0)), int(np.argmax(n == 0))
    print(f"  particles removed from t = {ht[k0]:.4f} M ({ne[k0]:.0f} in that step); last "
          f"removed at t = {ht[k1]:.4f} M; removed rest mass {D['m_excised_end']:.6f} of "
          f"{D['rest_mass']:.6f}")
    k = int(np.argmax(D["h_nmb"]))
    print(f"  largest MeshBlock count {D['h_nmb'][k]:.0f}, first at t = {ht[k]:.4f} M; at the "
          f"end {D['h_nmb'][-1]:.0f}")
    a1 = D["h_alpha_min"][np.argmin(np.abs(ht - tf[0]))]
    print(f"  smallest lapse at the first horizon {a1:.4f}; at the end "
          f"{D['h_alpha_min'][-1]:.4f}")
    Hn, zt = D["z_Hnorm"], D["z_t"]
    print(f"  ||H|| largest {Hn.max():.3f} at t = {zt[np.argmax(Hn)]:g} M; start {Hn[0]:.3f}, "
          f"end {Hn[-1]:.3f}")


if __name__ == "__main__":
    main()
