"""Constraint check of the written initial data (prediction P3 of JOURNAL.md).

For each case and N_y the data are written by make_shear_ic.py into a temporary
directory, read back with an own reader, and checked:
  (1) fields against the analytic Ahat_xy, K, psi, alpha;
  (2) constraints of the written fields with spectral derivatives along y and the
      analytic matter (E = rho0 W^2, S_x = rho0 W u_x): Hamiltonian
      (2/3) K^2 - Ahat_ij Ahat^ij - 16 pi E and momentum d_y Ahat_xy - 8 pi S_x
      (psi = 1, K uniform), relative to 16 pi E and to max |8 pi S_x|;
  (3) the particles: own cubic B-spline (pcs) deposit along y of E = sum m W / dV and
      S_x = sum m u_x / dV (W = sqrt(1 + u_x^2) on the flat slice), without and with
      one compensation pass (-c, 1 + 2c, -c), c = 1/6, against the analytic fields;
      the momentum residual 8 pi (S_x,dep - S_x) relative to max |8 pi S_x|;
      x and z uniformity of the lattice; total rest mass against D integrated.

    python3 check_ic.py [--cases S1,L2] [--ns 16,32,64,128,256]
Writes $NRPIC_RUN_DIR/check_ic.json and the figure check_ic.{png,pdf}; copies both into
../results and ../figs.
"""
import argparse
import json
import os
import shutil
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import shear_ref as sr  # noqa: E402
import make_shear_ic as mk  # noqa: E402
import figstyle as fs  # noqa: E402

CASES = {"S1": (0.005, 1.0), "S2": (0.005, 1.0/16), "S3": (0.005, 4.0),
         "S4": (0.005, 1.0/128), "M1": (0.05, 1.0), "M2": (0.05, 4.0),
         "L1": (0.5, 1.0), "L2": (0.5, 4.0)}


def read_fields(path):
    with open(path, "rb") as f:
        assert f.read(8) == b"NRCOSMO1"
        n1, n2, n3 = struct.unpack("qqq", f.read(24))
        arr = np.fromfile(f, dtype=np.float64).reshape(9, n3, n2, n1)
    return arr.transpose(0, 3, 2, 1)      # [v, i, j, k]


def read_particles(path):
    with open(path, "rb") as f:
        assert f.read(8) == b"NRPIC001"
        n, = struct.unpack("q", f.read(8))
        rec = np.fromfile(f, dtype=np.float64, count=7*n).reshape(n, 7)
    return rec


def pcs_weights(r):
    """cubic B-spline of width 4 cells at distance r (in cells)."""
    r = np.abs(r)
    w = np.where(r < 1.0, (4.0 - 6.0*r**2 + 3.0*r**3)/6.0,
                 np.where(r < 2.0, (2.0 - r)**3/6.0, 0.0))
    return w


def deposit_y(yp, q, L, ny):
    """sum over particles of q * W_pcs at the cell centres (periodic), per unit length."""
    h = L/ny
    yc = -0.5*L + (np.arange(ny) + 0.5)*h
    out = np.zeros(ny)
    s = (yp + 0.5*L)/h - 0.5            # position in cells from the first centre
    j0 = np.floor(s).astype(int)
    for o in (-1, 0, 1, 2):
        j = j0 + o
        w = pcs_weights(s - j)
        np.add.at(out, j % ny, q*w)
    return yc, out/h


def compensate(f, c):
    return (1.0 + 2.0*c)*f - c*(np.roll(f, 1) + np.roll(f, -1))


def spectral_dy(f, L):
    n = len(f)
    k = 2.0*np.pi*np.fft.fftfreq(n, d=L/n)
    return np.real(np.fft.ifft(1j*k*np.fft.fft(f)))


def check_one(case, ny, tmp):
    beta, HL = CASES[case]
    d = os.path.join(tmp, f"{case}_n{ny}")
    os.makedirs(d, exist_ok=True)
    meta = mk.main(["--beta", str(beta), "--HL", str(HL), "--ny", str(ny), "--out", d])
    L, b = meta["L"], meta["b"]
    F = read_fields(os.path.join(d, "fields.bin"))
    P = read_particles(os.path.join(d, "particles.nrp"))
    yc = -0.5*L + (np.arange(ny) + 0.5)*(L/ny)
    an = sr.initial_data(yc, b, L)
    res = {"case": case, "ny": ny, "beta": beta, "HL": HL, "b": b}
    # (1) fields
    res["psi_err"] = float(np.abs(F[0] - 1.0).max())
    res["K_err"] = float(np.abs(F[1] + 3.0).max())
    res["alpha_err"] = float(np.abs(F[2] - 1.0).max())
    res["Ahat_xy_err"] = float(np.abs(F[4] - an["Ahat_xy"][None, :, None]).max()
                               / np.abs(an["Ahat_xy"]).max())
    others = [3, 5, 6, 7, 8]
    res["Ahat_other_max"] = float(max(np.abs(F[v]).max() for v in others))
    res["x_z_uniform"] = float(np.abs(F[4] - F[4][:1, :, :1]).max())
    # (2) constraints with spectral derivatives and analytic matter
    ah = F[4][0, :, 0]
    K = F[1][0, :, 0]
    ham = (2.0/3.0)*K**2 - 2.0*ah**2 - 16.0*np.pi*an["rho_adm"]
    mom = spectral_dy(ah, L) - 8.0*np.pi*an["Sx"]
    res["ham_rel_spectral"] = float(np.abs(ham).max()/(16.0*np.pi*an["rho_adm"].mean()))
    res["mom_rel_spectral"] = float(np.abs(mom).max()/np.abs(8.0*np.pi*an["Sx"]).max())
    # (3) particles
    nt = meta["n_tracers"]
    nr = len(meta["rays_A_tags"]) + len(meta["rays_B_tags"])
    dust = P[nt + nr:]
    tr = P[:nt]
    rays = P[nt:nt + nr]
    res["n_dust"] = int(len(dust))
    res["rays_mass_ok"] = bool(np.all(rays[:, 6] == -1e-30))
    res["tracer_mass_rel"] = float(tr[:, 6].max()/dust[:, 6].mean())
    W = np.sqrt(1.0 + dust[:, 3]**2)
    area = L*L                             # x-z cross section of the box
    _, Edep = deposit_y(dust[:, 1], dust[:, 6]*W/area, L, ny)
    _, Sdep = deposit_y(dust[:, 1], dust[:, 6]*dust[:, 3]/area, L, ny)
    Ean, San = an["rho0"]*an["W"]**2, an["Sx"]
    for tag, (E, S) in (("raw", (Edep, Sdep)),
                        ("comp", (compensate(Edep, 1.0/6.0), compensate(Sdep, 1.0/6.0)))):
        res[f"E_rel_{tag}"] = float(np.abs(E - Ean).max()/Ean.mean())
        res[f"mom_rel_{tag}"] = float(np.abs(8.0*np.pi*(S - San)).max()
                                      / np.abs(8.0*np.pi*San).max())
    # lattice uniform in x and z: masses per (x,z) column equal
    xs = np.round((dust[:, 0] + 0.5*L)/(L/meta["nxz"]), 6)
    res["x_columns_equal"] = float(np.ptp([dust[xs == v, 6].sum() for v in np.unique(xs)])
                                   / dust[:, 6].sum())
    yy = np.linspace(-0.5*L, 0.5*L, 20001)
    Dint = np.trapezoid(sr.initial_data(yy, b, L)["D"], yy)*L*L
    res["total_mass_rel"] = float(dust[:, 6].sum()/Dint - 1.0)
    # tracers comove with the dust: u_x(tracer) = u*^x(y)
    res["tracer_ux_err"] = float(np.abs(tr[:, 3] - sr.initial_data(tr[:, 1], b, L)["ux"])
                                 .max())
    shutil.rmtree(d)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", default="S1,L2")
    ap.add_argument("--ns", default="16,32,64,128,256")
    a = ap.parse_args()
    out = os.environ.get("NRPIC_RUN_DIR", os.path.join(HERE, "..", "results"))
    tmp = os.path.join(out, "tmp_ic")
    os.makedirs(tmp, exist_ok=True)
    cases = a.cases.split(",")
    ns = [int(v) for v in a.ns.split(",")]
    rows = [check_one(c, n, tmp) for c in cases for n in ns]
    shutil.rmtree(tmp, ignore_errors=True)
    with open(os.path.join(out, "check_ic.json"), "w") as f:
        json.dump(rows, f, indent=1)
    for r in rows:
        print(f"{r['case']} N_y={r['ny']:4d}: Ahat {r['Ahat_xy_err']:.1e}, H(spec) "
              f"{r['ham_rel_spectral']:.1e}, M(spec) {r['mom_rel_spectral']:.1e}, "
              f"E raw {r['E_rel_raw']:.2e} comp {r['E_rel_comp']:.2e}, M raw "
              f"{r['mom_rel_raw']:.2e} comp {r['mom_rel_comp']:.2e}, x-columns "
              f"{r['x_columns_equal']:.1e}, mass {r['total_mass_rel']:+.1e}, tracer u_x "
              f"{r['tracer_ux_err']:.1e}")
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 1, figsize=(fs.COLUMN_WIDTH + 1.0, 3.2))
    fig.subplots_adjust(left=0.17, right=0.97, bottom=0.15, top=0.95)
    cols = {"S1": fs.PAL["blue"], "L2": fs.PAL["red"]}
    for c in cases:
        rr = [r for r in rows if r["case"] == c]
        n = np.array([r["ny"] for r in rr])
        col = cols.get(c, "k")
        ax.loglog(n, [max(r["mom_rel_spectral"], 1e-17) for r in rr], "s:", color=col,
                  label=f"{c}: fields, spectral")
        ax.loglog(n, [r["mom_rel_raw"] for r in rr], "o--", color=col,
                  label=f"{c}: pcs deposit")
        ax.loglog(n, [r["mom_rel_comp"] for r in rr], "o-", color=col,
                  label=f"{c}: pcs + compensation 1/6")
    ax.loglog(n, rows[0]["mom_rel_comp"]*(n/n[0])**-4.0, **fs.GUIDE,
              label=r"$N_y^{-4}$")
    ax.set_xlabel(r"cells along $y$, $N_y$")
    ax.set_ylabel(r"momentum residual / max $|8\pi S_x|$")
    ax.legend(fontsize=7, ncol=1, loc="lower left")
    fs.save(fig, os.path.join(out, "check_ic"))
    res_dir = os.path.join(HERE, "..", "results")
    fig_dir = os.path.join(HERE, "..", "figs")
    os.makedirs(res_dir, exist_ok=True)
    os.makedirs(fig_dir, exist_ok=True)
    shutil.copy(os.path.join(out, "check_ic.json"), res_dir)
    shutil.copy(os.path.join(out, "check_ic.png"), fig_dir)


if __name__ == "__main__":
    main()
