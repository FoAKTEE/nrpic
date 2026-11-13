"""Reduce the dust-collapse runs to the arrays of fig_dust.py.

This is the only script of the dust-collapse figure that reads the simulation outputs
and the analysis modules of the repository; the figure script reads
paper/data/dust.npz alone. Dust ball of initial areal radius R_0 = 5 M and unit total
mass, 9328 particles on a cubic lattice, adaptive mesh, four runs:

- ref:   cloud at the finest local level (published deposition rule), lattice masses
         corrected so that they sum to the rest mass of the initial data;
- adapt: as ref with the adaptive cloud level (any number of levels coarser);
- mc1:   as adapt with clouds at most one level coarser than the particle's block;
- pub:   as ref with the published lattice mass rule m_p = rho_0 psi^6 h^3.

Kept per run: the central lapse, central energy density and proper time of the central
normal observer while particles are present (every record), the apparent-horizon
mass reported by the corrected finder against time, the norm of the Hamiltonian
constraint against time, and the particle rest mass at t = 0. Also kept: the lapse
bound alpha = 1 + 6 ln(R/R_0) and the cycloid density against proper time, the
initial density rho_0, the rest mass of the initial data and the lapse threshold of
particle excision.

    python3 paper/scripts/make_data_dust.py
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.dont_write_bytecode = True        # leave the analysis folders untouched
sys.path.insert(0, str(REPO / "analysis" / "diag"))
sys.path.insert(0, str(REPO / "python"))
from common import H, read_athena_hst, read_horizon, read_nrpic_hst  # noqa: E402
from nrpic import oppenheimer_snyder as osn  # noqa: E402

OS = REPO / "runs" / "os"
RUNS = {"ref": OS / "nocap_sc", "adapt": OS / "adapt_sc", "mc1": OS / "adapt_mc1",
        "pub": OS / "nocap_v4"}
STRIDE = 1                            # the live part has about 1100 records
ALPHA_EXC = 0.1                       # lapse threshold of particle excision in these runs
OUT = HERE.parent / "data" / "dust.npz"


def main():
    data = {"rho0": osn.rho0(), "rest_mass": osn.rest_mass(),
            "tau_coll": osn.collapse_time(), "alpha_exc": ALPHA_EXC}
    full = {}
    for key, d in RUNS.items():
        h = read_nrpic_hst(str(d / "os.nrpic.hst"))
        live = h[:, H["np"]] > 0
        hl = h[live]
        idx = np.unique(np.r_[np.arange(0, len(hl), STRIDE), len(hl) - 1])
        data[f"{key}_t"] = hl[idx, H["time"]]
        data[f"{key}_tau"] = hl[idx, H["tau_probe"]]
        data[f"{key}_alpha"] = hl[idx, H["alpha_probe"]]
        data[f"{key}_E"] = hl[idx, H["e_probe"]]
        data[f"{key}_m0"] = h[0, H["sum_m"]]
        ah = read_horizon(str(d / "os.horizon_summary_0.txt"))
        data[f"{key}_ah_t"], data[f"{key}_ah_M"] = ah[:, 0], ah[:, 1]
        z = read_athena_hst(str(d / "os.z4c.user.hst"))
        data[f"{key}_z_t"], data[f"{key}_Hnorm"] = z["time"], np.sqrt(z["H-norm2"])
        full[key] = (h, ah, z)
        print(f"{key:6s} {d.relative_to(REPO)}: {len(h)} records, particles until "
              f"t = {hl[-1, 0]:.2f} (kept {len(idx)}), {len(ah)} horizon rows, "
              f"{len(z['time'])} constraint rows")
    tau = np.linspace(0.0, 0.995 * data["tau_coll"], 800)
    data["an_tau"] = tau
    data["an_alpha"] = np.array([float(osn.staley_lower_bound(x)) for x in tau])
    data["an_rho"] = np.array([float(osn.cycloid_rho(x)) for x in tau])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT, **data)
    print(f"{OUT}  {OUT.stat().st_size / 1e6:.3f} MB")

    # spot checks against docs/TESTLOG.md
    print("spot checks (TESTLOG):")
    print(f"  particle rest mass: published rule {data['pub_m0']:.5f}, corrected "
          f"{data['ref_m0']:.5f}, continuum {data['rest_mass']:.5f} "
          f"(log 1.16874, 1.15515; ratio {data['pub_m0'] / data['rest_mass']:.4f}, log 1.0118)")
    for key, ref in (("ref", "16.39, 1.00035; 1.0003, 1.0001, 1.0000; 0.9995, 0.9990, 0.9988, 0.9987"),
                     ("adapt", "16.39, 0.9971; 1.0003, 1.0006, 1.0012; 1.0026, 1.0047, 1.0068, 1.0065"),
                     ("mc1", "1.0006 at formation; 1.0011, 1.0011 at 20, 25; 0.9923, 0.9903 at 40, 59"),
                     ("pub", "16.43, 1.0114 (earlier run of the same setup)")):
        h, ah, z = full[key]
        at = lambda tq: ah[np.argmin(np.abs(ah[:, 0] - tq)), 1]
        Hn = np.sqrt(z["H-norm2"])
        print(f"  {key}: first horizon t = {ah[0, 0]:.2f}, M = {ah[0, 1]:.5f}; M at t = 18, 20, 22, "
              f"25, 30, 40, 59: " + ", ".join(f"{at(x):.4f}" for x in (18, 20, 22, 25, 30, 40, 59))
              + f"\n      largest ||H|| {Hn.max():.2f} at t = {z['time'][np.argmax(Hn)]:.1f}, "
              f"||H|| at t = 60: {Hn[-1]:.3f};   log: {ref}")
    h = full["ref"][0]
    a, tau_c = h[:, H["alpha_probe"]], h[:, H["tau_probe"]]
    lb = np.array([float(osn.staley_lower_bound(x)) for x in tau_c])
    w = tau_c <= 2.6
    print(f"  ref: max |alpha_c - bound| for tau_c <= 2.6 M: {np.abs(a[w] - lb[w]).max():.1e} "
          "(log, static mesh: 1e-4)")


if __name__ == "__main__":
    main()
