"""Verify Stage 2 C++/Kokkos kernels against python/nrpic/vlasov_gr.py and plot parity diagnostics."""

import math
import subprocess
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import special

ROOT = Path(__file__).resolve().parents[3]
SCRATCH_BIN = Path("/weka/scratch/schmidt/ssci-anima/ssci-haiyangw/nrpic_grlbv/vlasov_kernel_test")
sys.path.insert(0, str(ROOT / "python"))

from nrpic import collide as _coll
from nrpic import kerr as _kerr
from nrpic import vlasov_gr as vg


def main():
    assert SCRATCH_BIN.exists(), f"Compile C++ test binary first: {SCRATCH_BIN}"
    in_file = SCRATCH_BIN.parent / "stage2_parity_in.txt"
    out_file = SCRATCH_BIN.parent / "stage2_parity_out.txt"

    rng = np.random.default_rng(12345)

    # 1. Thermos across theta in [1e-7, 1e4] (80 points)
    thetas = np.geomspace(1e-7, 1e4, 80)

    # 2. Flux cases across curved metrics & beta_F in [-1.2, 1.2] (30 points)
    flux_cases = []
    betaFs = np.linspace(-1.2, 1.2, 30)
    for bF in betaFs:
        M = rng.normal(size=(3, 3))
        g = M @ M.T + 0.4 * np.eye(3)
        A = rng.normal(size=3)
        u_bar = rng.normal(scale=2.0, size=3)
        Ms = rng.normal(size=(3, 3))
        Sig = Ms @ Ms.T + 1e-3 * np.eye(3)
        D_s = 1.75
        alp_f = 0.88
        flux_cases.append((g, A, D_s, u_bar, Sig, alp_f, float(bF)))

    # 3. SolveFaceBetaF + PairingCostMatrix (10 random 3-basis cases)
    betaf_cases = []
    for _ in range(10):
        Da = rng.uniform(0.05, 1.0, size=3)
        Db = rng.uniform(0.05, 1.0, size=3)
        ua = rng.normal(scale=1.5, size=(3, 3))
        ub = rng.normal(scale=1.5, size=(3, 3))
        Sa = np.array([m @ m.T + 1e-2 * np.eye(3) for m in rng.normal(size=(3, 3, 3))])
        Sb = np.array([m @ m.T + 1e-2 * np.eye(3) for m in rng.normal(size=(3, 3, 3))])
        betaf_cases.append((Da, ua, Sa, Db, ub, Sb))

    # 4. Kerr-Schild CubatureGeodesicKick + BasisStressEnergy (5 positions)
    kick_cases = []
    for r0 in (3.0, 5.0, 8.0, 12.0, 20.0):
        x0 = np.array([r0, 0.3 * r0, 0.1 * r0])
        ak = _kerr.adm("cks", x0, a=0.9, M=1.0)
        adm = vg.AdmState(ak.alpha, ak.beta, ak.gamma, ak.dalpha, ak.dbeta, ak.dgamma)
        u0 = np.array([-0.2, 2.5 / math.sqrt(r0 / 3.0), 0.15])
        Ms = rng.normal(size=(3, 3)) * 0.15
        Sig0 = Ms @ Ms.T + 1e-3 * np.eye(3)
        kick_cases.append((adm, 0.1, u0, Sig0))

    # 5. BGK + HLLC cases (5 curved-metric cases)
    bgk_cases = []
    for _ in range(5):
        M = rng.normal(size=(3, 3)) * 0.2
        g = M @ M.T + np.eye(3)
        adm = vg.AdmState(0.85, np.array([0.1, -0.05, 0.02]), g, np.zeros(3), np.zeros((3, 3)), np.zeros((3, 3, 3)))
        m_v = rng.uniform(0.2, 1.0, size=3)
        u_v = rng.normal(scale=1.2, size=(3, 3))
        S_v = np.array([m @ m.T * 0.2 + 0.02 * np.eye(3) for m in rng.normal(size=(3, 3, 3))])
        bgk_cases.append((adm, 0.5, 8.0, 0.4, 0.15, m_v, u_v, S_v))

    with open(in_file, "w") as f:
        for th in thetas:
            f.write(f"THERMO {th:.17e}\n")
        for g, A, D_s, u_bar, Sig, alp_f, bF in flux_cases:
            vals = list(g.ravel()) + list(A) + [D_s] + list(u_bar) + list(Sig.ravel()) + [alp_f, bF]
            f.write("FLUX " + " ".join(f"{v:.17e}" for v in vals) + "\n")
        for Da, ua, Sa, Db, ub, Sb in betaf_cases:
            parts = [str(len(Da)), str(len(Db))]
            for D_arr, u_arr, S_arr in ((Da, ua, Sa), (Db, ub, Sb)):
                for a in range(len(D_arr)):
                    parts.append(f"{D_arr[a]:.17e}")
                    parts.extend(f"{v:.17e}" for v in u_arr[a])
                    parts.extend(f"{v:.17e}" for v in S_arr[a].ravel())
            f.write("BETAF " + " ".join(parts) + "\n")
        for adm, dt, u0, Sig0 in kick_cases:
            vals = (
                [adm.alp]
                + list(adm.beta)
                + list(adm.g.ravel())
                + list(adm.dalp)
                + list(adm.dbeta.ravel())
                + list(adm.dg.ravel())
                + [dt]
                + list(u0)
                + list(Sig0.ravel())
            )
            f.write("KICK " + " ".join(f"{v:.17e}" for v in vals) + "\n")
        for adm, V_a, sig_mu, dt, bF, m_v, u_v, S_v in bgk_cases:
            vals = [adm.alp] + list(adm.beta) + list(adm.g.ravel()) + [V_a, sig_mu, dt, bF]
            for al in range(len(m_v)):
                vals.append(m_v[al])
                vals.extend(u_v[al])
                vals.extend(S_v[al].ravel())
            f.write(f"BGK_HLLC {len(m_v)} " + " ".join(f"{v:.17e}" for v in vals) + "\n")

    subprocess.run([str(SCRATCH_BIN)], check=True)
    subprocess.run([str(SCRATCH_BIN), "--eval-table", str(in_file), str(out_file)], check=True)

    lines = out_file.read_text().strip().splitlines()
    idx = 0

    # Compare THERMO
    err_kve2, err_kve3, err_cs2, err_vmol, err_thinv = [], [], [], [], []
    for th in thetas:
        toks = lines[idx].split(); idx += 1
        assert toks[0] == "THERMO"
        _, k2_c, k3_c, wm_c, hr_c, cs2_c, ga_c, thinv_c, vm_c = [float(x) for x in toks[1:]]
        z = 1.0 / th
        k2_p = float(special.kve(2, z)) if z < 1e8 else math.sqrt(math.pi/(2*z))*(1 + 15/(8*z))
        k3_p = float(special.kve(3, z)) if z < 1e8 else math.sqrt(math.pi/(2*z))*(1 + 35/(8*z))
        wm_p, hr_p, cs2_p, ga_p = vg.synge_thermo(th)
        vm_p = math.sqrt(16.0 * th / math.pi) if th < 1e-6 else float(_coll.mj_vmol(th))
        thinv_p = vg.safe_mj_theta_from_w(wm_p)
        err_kve2.append(abs(k2_c - k2_p) / max(abs(k2_p), 1e-300))
        err_kve3.append(abs(k3_c - k3_p) / max(abs(k3_p), 1e-300))
        err_cs2.append(abs(cs2_c - cs2_p) / max(abs(cs2_p), 1e-12))
        err_vmol.append(abs(vm_c - vm_p) / max(abs(vm_p), 1e-12))
        err_thinv.append(abs(thinv_c - thinv_p) / max(1.0, abs(thinv_p)))
    assert max(err_kve2) < 1e-13 and max(err_kve3) < 1e-13
    assert max(err_cs2) < 1e-11 and max(err_vmol) < 1e-13 and max(err_thinv) < 1e-12

    # Compare FLUX
    err_flux = []
    for g, A, D_s, u_bar, Sig, alp_f, bF in flux_cases:
        toks = lines[idx].split(); idx += 1
        assert toks[0] == "FLUX"
        nums = [float(x) for x in toks[1:]]
        normA_c, Fm_c = nums[0], nums[1]
        FP_c = np.array(nums[2:5])
        FE_c = nums[5]
        FPi_c = np.array(nums[6:15]).reshape(3, 3)
        normA_p, e_up, e_dn = vg.face_triad(g, A)
        Fm_p, FP_p, FPi_p, FE_p = vg.onesided_flux_coord(D_s, u_bar, Sig, alp_f, normA_p, e_up, e_dn, bF)
        e_rel = max(
            abs(normA_c - normA_p) / max(normA_p, 1.0),
            abs(Fm_c - Fm_p) / max(abs(Fm_p), 1.0),
            float(np.linalg.norm(FP_c - FP_p)) / max(float(np.linalg.norm(FP_p)), 1.0),
            float(np.linalg.norm(FPi_c - FPi_p)) / max(float(np.linalg.norm(FPi_p)), 1.0),
            abs(FE_c - FE_p) / max(abs(FE_p), 1.0),
        )
        err_flux.append(e_rel)
    assert max(err_flux) < 1e-13, f"Flux max err {max(err_flux)}"

    # Compare BETAF + PAIRING
    err_betaf, err_pair = [], []
    for Da, ua, Sa, Db, ub, Sb in betaf_cases:
        toks = lines[idx].split(); idx += 1
        assert toks[0] == "BETAF"
        bF_c = float(toks[1])
        C_c = np.array([float(x) for x in toks[2:]]).reshape(3, 3)
        bF_p = vg.solve_face_beta_F(Da, ua, Sa, Db, ub, Sb)
        C_p = vg.pairing_cost_matrix(Da, ua, Sa, Db, ub, Sb, bF_p)
        err_betaf.append(abs(bF_c - bF_p) / max(abs(bF_p), 1.0))
        err_pair.append(float(np.max(np.abs(C_c - C_p))))
    assert max(err_betaf) < 1e-12, f"betaF max err {max(err_betaf)}"
    assert max(err_pair) < 1e-11, f"C_eb max err {max(err_pair)}"

    # Compare KICK + STRESS-ENERGY
    err_kick_u, err_kick_S, err_se = [], [], []
    for adm, dt, u0, Sig0 in kick_cases:
        toks = lines[idx].split(); idx += 1
        assert toks[0] == "KICK"
        nums = [float(x) for x in toks[1:]]
        u_c = np.array(nums[0:3])
        S_c = np.array(nums[3:12]).reshape(3, 3)
        E_c = nums[12]
        P_c = np.array(nums[13:16])
        Sij_c = np.array(nums[16:25]).reshape(3, 3)
        u_p, S_p = vg.cubature_geodesic_kick(u0, Sig0, adm, None, dt, n_q=3)
        gi, _ = vg.inv3_sym(adm.g)
        E_p, P_p, Sij_p = vg.basis_stress_energy(1.5, u_p, S_p, gi, n_q=3)
        err_kick_u.append(float(np.linalg.norm(u_c - u_p)))
        err_kick_S.append(float(np.linalg.norm(S_c - S_p)))
        err_se.append(max(abs(E_c - E_p)/E_p, float(np.linalg.norm(P_c - P_p)), float(np.linalg.norm(Sij_c - Sij_p))))
    assert max(err_kick_u) < 1e-12 and max(err_kick_S) < 1e-12 and max(err_se) < 1e-12

    # Compare BGK + HLLC
    err_bgk, err_hllc = [], []
    for adm, V_a, sig_mu, dt, bF, m_v, u_v, S_v in bgk_cases:
        toks = lines[idx].split(); idx += 1
        assert toks[0] == "BGK_HLLC"
        nums = [float(x) for x in toks[1:]]
        Nb = len(m_v)
        off = 0
        uc_out = np.zeros((Nb, 3)); Sc_out = np.zeros((Nb, 3, 3))
        for al in range(Nb):
            uc_out[al] = nums[off:off+3]; off += 3
            Sc_out[al] = np.array(nums[off:off+9]).reshape(3, 3); off += 9
        FD_c, FP_c, FE_c, FPi_c = nums[off], np.array(nums[off+1:off+4]), nums[off+4], np.array(nums[off+5:off+14]).reshape(3, 3)
        up_out, Sp_out = vg.mj_bgk_relax_cell(m_v, u_v, S_v, V_a, adm, sig_mu, dt)
        DL = m_v / V_a; DR = 0.5 * m_v / V_a
        FD_p, FP_p, FPi_p, FE_p = vg.rel_hllc_flux_tetrad(DL, u_v, S_v, m_v, DR, up_out, Sp_out, m_v, bF)
        err_bgk.append(max(float(np.max(np.abs(uc_out - up_out))), float(np.max(np.abs(Sc_out - Sp_out)))))
        err_hllc.append(max(abs(FD_c - FD_p), float(np.linalg.norm(FP_c - FP_p)), abs(FE_c - FE_p), float(np.linalg.norm(FPi_c - FPi_p))))
    assert max(err_bgk) < 1e-12 and max(err_hllc) < 1e-12

    print("ALL C++ <-> PYTHON KERNEL PARITY CHECKS PASSED:")
    print(f"  Kve2 max rel err  : {max(err_kve2):.3e}")
    print(f"  Kve3 max rel err  : {max(err_kve3):.3e}")
    print(f"  cs2  max rel err  : {max(err_cs2):.3e}")
    print(f"  vmol max rel err  : {max(err_vmol):.3e}")
    print(f"  Flux max rel err  : {max(err_flux):.3e}")
    print(f"  betaF max rel err : {max(err_betaf):.3e}")
    print(f"  C_eb max abs err  : {max(err_pair):.3e}")
    print(f"  Kick max abs err  : {max(err_kick_u):.3e} / {max(err_kick_S):.3e}")
    print(f"  BGK  max abs err  : {max(err_bgk):.3e}")
    print(f"  HLLC max abs err  : {max(err_hllc):.3e}")

    # Plot 2x2 parity diagnostic figure
    plt.rcParams.update({"font.size": 9, "xtick.direction": "in", "ytick.direction": "in", "figure.dpi": 200})
    fig, axes = plt.subplots(2, 2, figsize=(9.2, 6.4), constrained_layout=True)

    ax = axes[0, 0]
    ax.loglog(thetas, np.maximum(err_kve2, 1e-16), label=r"$K_2(z)e^z$", lw=1.4)
    ax.loglog(thetas, np.maximum(err_kve3, 1e-16), "--", label=r"$K_3(z)e^z$", lw=1.4)
    ax.loglog(thetas, np.maximum(err_cs2, 1e-16), ":", label=r"$c_s^2(\theta)$", lw=1.6)
    ax.loglog(thetas, np.maximum(err_vmol, 1e-16), "-.", label=r"$\langle v_{\rm Mol}\rangle$", lw=1.3)
    ax.set_ylim(1e-17, 1e-11)
    ax.set_xlabel(r"Dimensionless temperature $\theta = k_B T / m$")
    ax.set_ylabel("C++ vs Python relative error")
    ax.set_title("(a) Relativistic Synge & Bessel thermodynamics")
    ax.legend(frameon=False, loc="upper left", ncol=2, fontsize=8)

    ax = axes[0, 1]
    ax.semilogy(betaFs, np.maximum(err_flux, 1e-16), "o-", ms=3, lw=1.3, label="Curved-metric Top-Hat flux")
    ax.set_ylim(1e-17, 1e-12)
    ax.set_xlabel(r"Normal-observer face velocity $\beta_F$")
    ax.set_ylabel("Max relative flux error")
    ax.set_title("(b) Exact 1D-sliced + 2D-cubature flux parity")
    ax.legend(frameon=False, loc="best")

    ax = axes[1, 0]
    radii = [3.0, 5.0, 8.0, 12.0, 20.0]
    ax.semilogy(radii, np.maximum(err_kick_u, 1e-16), "o-", lw=1.4, label=r"$|\Delta \bar{u}|$")
    ax.semilogy(radii, np.maximum(err_kick_S, 1e-16), "s--", lw=1.4, label=r"$|\Delta \Sigma|$")
    ax.semilogy(radii, np.maximum(err_se, 1e-16), "^:", lw=1.5, label=r"$(E, P_i, S_{ij})$")
    ax.set_ylim(1e-17, 1e-11)
    ax.set_xlabel(r"Kerr-Schild radius $r / M$ ($a = 0.9M$)")
    ax.set_ylabel("C++ vs Python error")
    ax.set_title("(c) Kerr cubature geodesic kick & stress-energy")
    ax.legend(frameon=False, loc="best")

    ax = axes[1, 1]
    cats = [r"$\beta_F$ Brent", r"$C^{\rm eb}$", "MJ BGK", "Rel. HLLC"]
    vals = [max(err_betaf), max(err_pair), max(err_bgk), max(err_hllc)]
    ax.bar(cats, np.maximum(vals, 1e-16), color=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"], alpha=0.85)
    ax.set_yscale("log")
    ax.set_ylim(1e-17, 1e-10)
    ax.set_ylabel("Max error across test suite")
    ax.set_title("(d) Root-finder, pairing, BGK, and HLLC parity")

    out_dir = ROOT / "vlasov_gr" / "notes" / "figs"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_png = out_dir / "diag_stage2_kernel_parity.png"
    fig.savefig(out_png)
    print(f"Saved {out_png}")


if __name__ == "__main__":
    main()
