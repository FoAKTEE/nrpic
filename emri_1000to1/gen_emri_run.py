#!/usr/bin/env python3
"""
Generate AthenaK full 3+1 NR inputs, run_meta.json, and waveforms/ directory
for 1000:1 (or configurable q) single-particle Schwarzschild EMRI inspirals.
"""

import argparse
import json
import math
import os
import sys
import numpy as np

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if THIS_DIR not in sys.path:
    sys.path.insert(0, THIS_DIR)

from pn_2sf_reference import EMRIReferenceModel

DEFAULT_OUT_ROOT = "/weka/scratch/schmidt/ssci-anima/ssci-haiyangw/nrpic_grlbv/runs/emri_1000to1"


def build_emri_ic(ref, R0, q, omega_scale=1.0, vr_scale=1.0, vr_add=0.0):
    """
    Construct isotropic Schwarzschild quasicircular + adiabatic radiation-reaction IC
    for a single particle of mass q*M0 at areal radius R0 on the +x axis.
    Supports SpEC/SpECTRE iterative eccentricity control via (omega_scale, vr_scale, vr_add),
    where vr_add is an additive areal radial velocity correction Delta(dR/dt)_0.
    """
    m0 = 1.0
    m_p = float(q)
    r_iso = 0.5 * (R0 - m0 + math.sqrt(R0 * (R0 - 2.0 * m0)))
    psi0 = 1.0 + m0 / (2.0 * r_iso)
    # Exact Schwarzschild circular 4-velocity components at R0
    ut_schw = 1.0 / math.sqrt(max(1.0 - 3.0 * m0 / R0, 1.0e-12))
    lz = math.sqrt(m0 * R0 / max(1.0 - 3.0 * m0 / R0, 1.0e-12)) * math.sqrt(1.0 + m_p)

    # Particle starts on +x axis moving in +y
    u_y = (lz / r_iso) * float(omega_scale)

    # Adiabatic radiation-reaction radial velocity + SpEC/SpECTRE eccentric correction -> isotropic u_x
    dr_dt_1sf = ref.initial_dr_dt(R0=R0, q=m_p, model="1SF")
    dr_dt_eff = dr_dt_1sf * float(vr_scale) + float(vr_add)
    dR_driso = 1.0 - (m0 * m0) / (4.0 * r_iso * r_iso)
    vr_iso = dr_dt_eff / dR_driso
    u_x = (psi0 ** 4) * ut_schw * vr_iso

    return {
        "r_iso": r_iso,
        "psi0": psi0,
        "ut_schw": ut_schw,
        "lz": lz,
        "dr_dt_1sf": dr_dt_1sf,
        "pos": np.array([r_iso, 0.0, 0.0], dtype=np.float64),
        "u_cov": np.array([u_x, u_y, 0.0], dtype=np.float64),
        "omega_orb0": (R0 ** (-1.5)) * math.sqrt(1.0 + m_p),
    }


def format_emri_athinput(
    name, ic, args, sigma_eff, m_bare, p0_bal
):
    x_p = ic["pos"][0]
    domain_half = float(args.domain_half)
    base_nx = int(args.base_nx)
    mb_nx = int(args.mb_nx)
    if base_nx % mb_nx != 0:
        raise ValueError(f"--base-nx ({base_nx}) must be divisible by --mb-nx ({mb_nx})")
    dx0 = 2.0 * domain_half / float(base_nx)
    lvl_shift = int(round(math.log2(dx0 / 8.0)))
    if abs(8.0 * (2.0 ** lvl_shift) - dx0) > 1e-6:
        raise ValueError(f"dx0 = 2*domain_half/base_nx must be 8 * 2^k (got {dx0})")
    bh_level_eff = args.bh_level + lvl_shift
    p_level_eff = args.p_level + lvl_shift
    dx_bh = dx0 / (2 ** bh_level_eff)
    dx_p = dx0 / (2 ** p_level_eff)
    num_levels = max(10, bh_level_eff + 3, p_level_eff + 3)

    p_box_hw = max(0.95, 10.0 * dx_p)
    if args.shift_eta_far < 1.999:
        eta_eff = max(float(args.shift_eta_far), 1.0e-4)
        mref = 2.0 / eta_eff
        eta_block = f"""shift_eta         = {eta_eff:.6f}
shift_eta_profile = true
shift_eta_mref    = {mref:.10f}
shift_eta_width   = {args.shift_eta_width:.4f}"""
    else:
        eta_block = f"shift_eta       = {args.shift_eta_far:.6f}"

    if args.sbc_mode == "nonwave":
        sbc_block = """extrap_order    = 4
ghost_falloff   = true
sbc_variant     = nonwave
sbc_speed       = metric"""
    else:
        sbc_block = "# Stock Sommerfeld outer BC (extrap_order=2, ghost_falloff=false, sbc_variant=sommerfeld, sbc_speed=unit)"

    if args.ssl:
        ssl_block = f"""slow_start_lapse  = true
ssl_damping_amp   = {args.ssl_amp:.4f}
ssl_damping_time  = {args.ssl_time:.4f}
ssl_damping_index = {args.ssl_index}"""
    else:
        ssl_block = "slow_start_lapse  = false"

    # Build nested static/tracker shells in physical resolution units
    if mb_nx >= 32:
        # Larger MeshBlocks (32^3 or 64^3): align shells to W_b(l) = mb_nx * dx(l) so every
        # level stays minimal (4x4x4 = 56 leaf blocks/level) without triggering 8x8x8 bloat.
        # For root = 2x2x2 (base_nx/mb_nx == 2), inner box is [-W_b, W_b]; for 4x4x4, [-2*W_b, 2*W_b].
        nroot = base_nx // mb_nx
        rad_fac = 0.90 if nroot <= 2 else 1.90
        shells = []
        for phys_lev in range(1, args.bh_level):
            eff_lev = phys_lev + lvl_shift
            if eff_lev <= 0:
                continue
            dx_l = 8.0 / (2 ** phys_lev)
            rad_l = rad_fac * mb_nx * dx_l
            if rad_l < 0.95 * domain_half:
                shells.append((rad_l, eff_lev))
    elif args.wave_zone_boost:
        shells = []
        if 1 + lvl_shift > 0 and domain_half >= 512.0:
            shells.append((124.0, 1 + lvl_shift))  # dx = 4.0 M (4x4x4 shell, avoids outer 8x8x8 bloat)
        shells.extend([
            (62.0, 3 + lvl_shift),   # dx = 1.0 M covering all extraction spheres 20..58 M
            (30.5, 4 + lvl_shift),   # dx = 0.5 M covering r <= 30.5 M (20 & 27 M spheres)
            (7.5,  5 + lvl_shift),   # dx = 0.25 M covering entire orbit (r_iso ~ 5.2..5.5 M)
        ])
        if args.bh_level >= 8:
            shells.append((2.4, bh_level_eff - 1))  # clean M/16 buffer around M/32 BH core
    else:
        shells = []
        if 1 + lvl_shift > 0 and domain_half >= 512.0:
            shells.append((124.0, 1 + lvl_shift))  # dx = 4.0 M transition shell
        for rad, plev in [(60.0, 2), (30.5, 3), (15.5, 4), (7.5, 5)]:
            if plev + lvl_shift > 0:
                shells.append((rad, plev + lvl_shift))
        if args.bh_level >= 8:
            shells.append((2.4, bh_level_eff - 1))

    bh_box_rad = 1.40 if (args.bh_level >= 8 or mb_nx >= 32) else 1.95
    co0_rad = 1.35 if (args.bh_level >= 8 or mb_nx >= 32) else 1.90

    if args.static_slab:
        rr_blocks = []
        ridx = 1
        for rad, lev in shells:
            rr_blocks.append(f"""<refined_region{ridx}>
level = {lev}
x1min = -{rad:.1f}
x1max = {rad:.1f}
x2min = -{rad:.1f}
x2max = {rad:.1f}
x3min = -{rad:.1f}
x3max = {rad:.1f}""")
            ridx += 1
        if not args.vacuum_twin:
            rr_blocks.append(f"""<refined_region{ridx}>
level = {p_level_eff}
x1min = -7.5
x1max = 7.5
x2min = -7.5
x2max = 7.5
x3min = -1.95
x3max = 1.95""")
            ridx += 1
        rr_blocks.append(f"""<refined_region{ridx}>
level = {bh_level_eff}
x1min = -{bh_box_rad:.2f}
x1max = {bh_box_rad:.2f}
x2min = -{bh_box_rad:.2f}
x2max = {bh_box_rad:.2f}
x3min = -{bh_box_rad:.2f}
x3max = {bh_box_rad:.2f}""")
        amr_cfg_block = "<mesh_refinement>\nrefinement = static\n\n" + "\n\n".join(rr_blocks)
    else:
        rr_blocks = []
        ridx = 1
        for rad, lev in shells:
            rr_blocks.append(f"""<refined_region{ridx}>
level = {lev}
x1min = -{rad:.1f}
x1max = {rad:.1f}
x2min = -{rad:.1f}
x2max = {rad:.1f}
x3min = -{rad:.1f}
x3max = {rad:.1f}""")
            ridx += 1
        rr_blocks.append(f"""<refined_region{ridx}>
level = {bh_level_eff}
x1min = -{bh_box_rad:.2f}
x1max = {bh_box_rad:.2f}
x2min = -{bh_box_rad:.2f}
x2max = {bh_box_rad:.2f}
x3min = -{bh_box_rad:.2f}
x3max = {bh_box_rad:.2f}""")
        ridx += 1
        if not args.vacuum_twin:
            rr_blocks.append(f"""<refined_region{ridx}>
level = {p_level_eff}
x1min = {x_p - p_box_hw:.4f}
x1max = {x_p + p_box_hw:.4f}
x2min = {-p_box_hw:.4f}
x2max = {p_box_hw:.4f}
x3min = {-p_box_hw:.4f}
x3max = {p_box_hw:.4f}""")

        z4c_amr_lines = ["<z4c_amr>", "method            = tracker"]
        for k_sh, (rad, lev) in enumerate(shells):
            z4c_amr_lines.append(f"radius_{k_sh}_rad      = {rad:.1f}")
            z4c_amr_lines.append(f"radius_{k_sh}_reflevel = {lev}")
        z4c_amr_block = "\n".join(z4c_amr_lines)

        if args.vacuum_twin:
            part_amr_block = """<amr_criterion0>
method = user"""
        else:
            t_buf = float(args.track_buffer_cells) if args.track_buffer_cells > 0 else (18.0 if args.variational_pic else 10.0)
            t_minr = max(1.25 if args.variational_pic else 0.85, (t_buf + 1.0) * dx_p)
            part_amr_block = f"""<amr_criterion0>
method = user

<particles_amr>
track_particles          = true
track_min_level          = {p_level_eff}
track_max_level          = {p_level_eff}
track_cells_between      = 8.0
track_buffer_cells       = {t_buf:.1f}
track_min_radius         = {t_minr:.2f}
track_hysteresis         = 1.6
track_spatial_hysteresis = 1.15
verbose                  = true"""

        amr_cfg_block = f"""<mesh_refinement>
refinement          = adaptive
max_nmb_per_rank    = {args.max_nmb_per_rank}
num_levels          = {num_levels}
ncycle_check        = 64
refinement_interval = 64

# Static initial boxes matching <z4c_amr> (+ <particles_amr> for EMRI) for clean id_solve
{chr(10).join(b + chr(10) for b in rr_blocks)}
{z4c_amr_block}

{part_amr_block}"""

    if args.vacuum_twin:
        grav_part_prob_block = """<problem>
pgen_name      = nrpic_cf
ncomp          = 1
comp0_type     = puncture
comp0_mass     = 1.0000000000
comp0_x1       = 0.0
comp0_x2       = 0.0
comp0_x3       = 0.0
comp0_p1       = 0.0
comp0_p2       = 0.0
comp0_p3       = 0.0
comp0_s1       = 0.0
comp0_s2       = 0.0
comp0_s3       = 0.0
lapse          = precollapsed
puncture_setup = false"""
    else:
        clump_p_block = ""
        if args.clump_momentum:
            p1_cl = m_bare * ic["u_cov"]
            clump_p_block = f"""comp1_p1       = {p1_cl[0]:.15e}
comp1_p2       = {p1_cl[1]:.15e}
comp1_p3       = {p1_cl[2]:.15e}
"""
        if args.pusher == "vlasov_hybrid":
            pusher_block = f"""pusher         = vlasov_hybrid
vlasov_mode    = hybrid
vlasov_pusher  = {args.vlasov_pusher}
vlasov_time_interp = {args.vlasov_time_interp}"""
        else:
            pusher_block = f"pusher         = {args.pusher}"

        if args.no_source_stage_extrap and args.source_mode == "stage_extrap":
            src_mode = "raw"
        else:
            src_mode = args.source_mode

        if src_mode == "stage_lagrangian":
            src_block = """source_density = false
source_extrap  = false
source_stage_extrap = false
source_stage_lagrangian = true"""
        elif src_mode == "stage_extrap":
            src_block = """source_density = false
source_extrap  = false
source_stage_extrap = true"""
        elif src_mode == "step_extrap":
            src_block = """source_density = true
source_extrap  = true
source_stage_extrap = false"""
        elif src_mode == "step_density":
            src_block = """source_density = true
source_extrap  = false
source_stage_extrap = false"""
        else:
            src_block = """source_density = false
source_extrap  = false
source_stage_extrap = false"""

        f_mcons = "false" if (args.no_filter_metric_conservative or args.variational_pic) else "true"
        f_unsplit = "true" if args.filter_mcons_unsplit else "false"
        f_comp = "true" if args.filter_compensate else "false"
        f_dens = "true" if (args.filter_densitized or args.variational_pic) else "false"
        f_bianchi = "true" if args.filter_bianchi_flux else "false"
        f_varpic = "true" if args.variational_pic else "false"
        varpic_lines = ""
        if args.variational_pic:
            varpic_lines = f"""variational_pic = true
variational_sigma = {args.variational_sigma:.6f}
variational_nrad  = {args.variational_nrad}
"""
        elif args.filter_bianchi_flux:
            varpic_lines = f"filter_bianchi_flux = {f_bianchi}\n"

        grav_part_prob_block = f"""<gravity>
four_pi_G   = 1.0
threshold   = 0.0
mg_bc       = robin
robin_x1    = 0.0
robin_x2    = 0.0
robin_x3    = 0.0
show_defect = 0

<particles>
particle_type  = nrpic
{pusher_block}
interp         = {args.interp}
metric         = mesh
tolerance      = 2.0e-14
max_iterations = 200
deposit        = true
deposit_shape  = {args.deposit_shape}
deposit_comp_c = {args.deposit_comp_c:.6f}
nfilter        = {args.nfilter}
filter_compensate = {f_comp}
filter_densitized = {f_dens}
filter_metric_conservative = {f_mcons}
filter_mcons_unsplit = {f_unsplit}
{varpic_lines}{src_block}
matter_stride  = 1
id_solve       = true
id_vector      = true
id_residual    = {args.id_residual}
id_vector_residual = {args.id_vector_residual}
id_psi_init    = trial
id_puncture_radius = {args.id_puncture_radius:.4f}
id_far         = multipole
id_tol         = {args.id_tol:.3e}
id_vector_tol  = {args.id_vector_tol:.3e}
id_maxit       = {args.id_maxit}
id_lin_tol     = {args.id_lin_tol:.3e}
id_lin_maxit   = {args.id_lin_maxit}
id_mg_tol      = {args.id_mg_tol:.3e}
id_dump        = false
alpha_exc      = 0.08
ah_exc_factor  = 0.85
hist_dcycle    = 20
traj_ntrack    = 1
traj_dcycle    = 4
snap_dt        = {args.slice_dt:.2f}
nparticles     = 1
p0_x1 = {ic['pos'][0]:.15e}
p0_x2 = {ic['pos'][1]:.15e}
p0_x3 = {ic['pos'][2]:.15e}
p0_u1 = {ic['u_cov'][0]:.15e}
p0_u2 = {ic['u_cov'][1]:.15e}
p0_u3 = {ic['u_cov'][2]:.15e}
p0_m  = {m_bare:.15e}

<problem>
pgen_name      = nrpic_cf
ncomp          = 2
comp0_type     = puncture
comp0_mass     = 1.0000000000
comp0_x1       = 0.0
comp0_x2       = 0.0
comp0_x3       = 0.0
comp0_p1       = {p0_bal[0]:.15e}
comp0_p2       = {p0_bal[1]:.15e}
comp0_p3       = {p0_bal[2]:.15e}
comp0_s1       = 0.0
comp0_s2       = 0.0
comp0_s3       = 0.0
comp1_type     = gaussian
comp1_mass     = {float(args.q):.15e}
comp1_sigma    = {sigma_eff:.15e}
comp1_x1       = {ic['pos'][0]:.15e}
comp1_x2       = {ic['pos'][1]:.15e}
comp1_x3       = {ic['pos'][2]:.15e}
{clump_p_block}lapse          = precollapsed
puncture_setup = false"""

    kind_str = "PURE VACUUM TWIN" if args.vacuum_twin else f"1000:1 Schwarzschild EMRI (R0={args.R0:.3f} M, q={args.q:.2e})"
    return f"""<comment>
problem = {kind_str}: {name} (L={domain_half:.0f} M, dx_BH=M/{1.0/dx_bh:.0f}, dx_p=M/{1.0/dx_p:.0f}, ssl={args.ssl}, wz_boost={args.wave_zone_boost})

<job>
basename = {name}

<mesh>
nghost    = 4
nx1       = {base_nx}
x1min     = -{domain_half:.1f}
x1max     = {domain_half:.1f}
ix1_bc    = outflow
ox1_bc    = outflow
nx2       = {base_nx}
x2min     = -{domain_half:.1f}
x2max     = {domain_half:.1f}
ix2_bc    = outflow
ox2_bc    = outflow
nx3       = {base_nx}
x3min     = -{domain_half:.1f}
x3max     = {domain_half:.1f}
ix3_bc    = outflow
ox3_bc    = outflow

<meshblock>
nx1       = {mb_nx}
nx2       = {mb_nx}
nx3       = {mb_nx}

{amr_cfg_block}

<time>
evolution  = dynamic
integrator = rk3
cfl_number = {args.cfl:.3f}
nlim       = -1
tlim       = {args.tlim:.1f}
ndiag      = 64

<z4c>
lapse_oplog     = 2.0
lapse_harmonicf = 1.0
lapse_harmonic  = 0.0
lapse_advect    = 1.0
{ssl_block}
shift_Gamma     = 0.75
{eta_block}
shift_advect    = 1.0
diss            = {args.diss:.3f}
chi_div_floor   = 1.0e-5
damp_kappa1     = {args.damp_kappa1:.4f}
damp_kappa2     = 0.0
{"bssn            = true" if args.bssn else "bssn            = false"}
{sbc_block}
co_0_type       = BH
co_0_x          = 0.0
co_0_y          = 0.0
co_0_z          = 0.0
co_0_mass       = 1.0000
co_0_radius     = {co0_rad:.2f}
co_0_reflevel   = {bh_level_eff}
tracker_mode    = ode
nrad_wave_extraction = 5
extraction_radius_0  = 20.0
extraction_radius_1  = 27.0
extraction_radius_2  = 38.0
extraction_radius_3  = 48.0
extraction_radius_4  = 58.0
extraction_nlev      = 6
waveform_dt          = 0.50

<fastflow>
find_every        = 200
metric_drvts      = interpolant
num_horizons      = 1
npunct            = 1
ntheta            = 24
lmax              = 12
use_puncture_0    = 0
initial_radius_0  = 0.50
flow_iterations_0 = 400
flow_alpha_beta_const_0 = 1.0
hmean_tol_0       = 100.0
mass_tol_0        = 1.0e-5
start_time_0      = 0.0
stop_time_0       = 5000.0
verbose           = false

{grav_part_prob_block}

<output1>
file_type = hst
dt        = 0.5

<output2>
file_type = rst
dt        = {args.rst_dt:.1f}

<output3>
file_type = bin
variable  = z4c_alpha
id        = alpha_xy
slice_x3  = 0.001
dt        = {args.slice_dt:.2f}

<output4>
file_type = bin
variable  = con_H
id        = conH_xy
slice_x3  = 0.001
dt        = {args.slice_dt:.2f}
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--out-root", default=DEFAULT_OUT_ROOT)
    ap.add_argument("--R0", type=float, default=6.50)
    ap.add_argument("--q", type=float, default=1.0e-3)
    ap.add_argument("--tlim", type=float, default=300.0)
    ap.add_argument("--omega-scale", type=float, default=1.0)
    ap.add_argument("--vr-scale", type=float, default=1.0)
    ap.add_argument("--vr-add", type=float, default=0.0, help="Additive SpEC/SpECTRE Delta(dR/dt)_0 eccentricity correction")
    ap.add_argument("--domain-half", type=float, default=256.0)
    ap.add_argument("--base-nx", type=int, default=64, help="Root grid cells per dimension (e.g. 64 or 128)")
    ap.add_argument("--mb-nx", type=int, default=16, help="MeshBlock cells per dimension (e.g. 16, 32, or 64)")
    ap.add_argument("--bh-level", type=int, default=7, help="Physical BH resolution index: dx_BH = 8 / 2^bh_level")
    ap.add_argument("--p-level", type=int, default=6, help="Physical particle resolution index: dx_p = 8 / 2^p_level")
    ap.add_argument("--nfilter", type=int, default=8)
    ap.add_argument("--damp-kappa1", type=float, default=0.02)
    ap.add_argument("--shift-eta-far", type=float, default=0.20)
    ap.add_argument("--shift-eta-width", type=float, default=1.0)
    ap.add_argument("--diss", type=float, default=0.50)
    ap.add_argument("--cfl", type=float, default=0.35)
    ap.add_argument("--max-nmb-per-rank", type=int, default=2800)
    ap.add_argument("--rst-dt", type=float, default=150.0)
    ap.add_argument("--slice-dt", type=float, default=10.0)
    ap.add_argument("--sbc-mode", choices=["stock", "nonwave"], default="stock")
    ap.add_argument("--ssl", action="store_true", help="Enable Etienne+2024 Slow-Start Lapse")
    ap.add_argument("--ssl-amp", type=float, default=0.6)
    ap.add_argument("--ssl-time", type=float, default=20.0)
    ap.add_argument("--ssl-index", type=int, default=1)
    ap.add_argument("--wave-zone-boost", action="store_true", help="Raise wave zone to dx=1M (r<=62M), 0.5M (r<=31M)")
    ap.add_argument("--clump-momentum", action="store_true", help="Set analytic smeared Bowen-York comp1_p1..3 on Gaussian particle")
    ap.add_argument("--id-residual", choices=["stencil", "code"], default="stencil")
    ap.add_argument("--id-vector-residual", choices=["stencil", "code"], default="stencil")
    ap.add_argument("--id-puncture-radius", type=float, default=1.0)
    ap.add_argument("--id-tol", type=float, default=1.0e-6)
    ap.add_argument("--id-vector-tol", type=float, default=2.0e-3)
    ap.add_argument("--id-lin-tol", type=float, default=1.0e-3)
    ap.add_argument("--id-mg-tol", type=float, default=1.0e-3)
    ap.add_argument("--id-maxit", type=int, default=25)
    ap.add_argument("--id-lin-maxit", type=int, default=50)
    ap.add_argument("--pusher", choices=["vlasov_hybrid", "midpoint", "boris"], default="vlasov_hybrid")
    ap.add_argument("--vlasov-pusher", choices=["gl4", "midpoint", "boris"], default="gl4")
    ap.add_argument("--vlasov-time-interp", choices=["quadratic", "linear"], default="quadratic")
    ap.add_argument("--interp", choices=["quintic", "bspline", "hermite"], default="quintic")
    ap.add_argument("--deposit-shape", choices=["pcs", "tsc", "cic"], default="pcs")
    ap.add_argument("--deposit-comp-c", type=float, default=0.0)
    ap.add_argument("--filter-compensate", action="store_true")
    ap.add_argument("--filter-densitized", action="store_true")
    ap.add_argument("--filter-bianchi-flux", action="store_true")
    ap.add_argument("--variational-pic", action="store_true", help="Enable exact variational spherical-Gaussian GR-PIC (Bug 10a+10b fix)")
    ap.add_argument("--variational-sigma", type=float, default=0.0, help="Gaussian width sigma (M); <=0 auto from dx & nfilter")
    ap.add_argument("--variational-nrad", type=int, default=12, help="Half-width of cubic cloud stencil in cells (max 16)")
    ap.add_argument("--track-buffer-cells", type=float, default=0.0, help="Override particles_amr track_buffer_cells")
    ap.add_argument("--bssn", action="store_true", help="Use pure BSSN (Theta=0) instead of Z4c")
    ap.add_argument("--filter-mcons-unsplit", action="store_true")
    ap.add_argument("--no-filter-metric-conservative", action="store_true")
    ap.add_argument("--source-mode", choices=["stage_lagrangian", "stage_extrap", "step_extrap", "step_density", "raw"], default="stage_extrap")
    ap.add_argument("--no-source-stage-extrap", action="store_true", help="Legacy alias for --source-mode raw")
    ap.add_argument("--vacuum-twin", action="store_true", help="Generate exact q=0 matched pure-vacuum reference twin")
    ap.add_argument("--static-slab", action="store_true")
    args = ap.parse_args()

    ref = EMRIReferenceModel()
    ic = build_emri_ic(ref, args.R0, args.q, args.omega_scale, args.vr_scale, args.vr_add)

    dx0 = 2.0 * float(args.domain_half) / float(args.base_nx)
    lvl_shift = int(round(math.log2(dx0 / 8.0)))
    dx_p = 8.0 / (2 ** args.p_level)
    dx_bh = 8.0 / (2 ** args.bh_level)
    shape_var = {"cic": 2.0 / 12.0, "tsc": 3.0 / 12.0, "pcs": 4.0 / 12.0}[args.deposit_shape]
    if args.variational_pic and args.variational_sigma > 0.0:
        sigma_eff = float(args.variational_sigma)
    else:
        sigma_eff = math.sqrt(max(shape_var + 0.5 * args.nfilter - 2.0 * args.deposit_comp_c, 0.05)) * dx_p
    m_bare = args.q * (1.0 + args.q / (math.sqrt(2.0 * math.pi) * sigma_eff))
    p0_bal = -m_bare * ic["u_cov"]

    out_dir = os.path.join(os.path.abspath(args.out_root), args.name)
    os.makedirs(out_dir, exist_ok=True)
    # CRITICAL: Z4c::WaveExtr requires waveforms/ directory to exist beforehand
    os.makedirs(os.path.join(out_dir, "waveforms"), exist_ok=True)

    ath_path = os.path.join(out_dir, f"{args.name}.athinput")
    with open(ath_path, "w") as f:
        f.write(format_emri_athinput(args.name, ic, args, sigma_eff, m_bare, p0_bal))

    meta = {
        "name": args.name,
        "vacuum_twin": bool(args.vacuum_twin),
        "R0": args.R0,
        "q": 0.0 if args.vacuum_twin else args.q,
        "tlim": args.tlim,
        "domain_half": float(args.domain_half),
        "base_nx": int(args.base_nx),
        "mb_nx": int(args.mb_nx),
        "lvl_shift": lvl_shift,
        "pusher": args.pusher,
        "vlasov_pusher": args.vlasov_pusher,
        "bssn": bool(args.bssn),
        "variational_pic": bool(args.variational_pic),
        "variational_sigma": float(args.variational_sigma),
        "variational_nrad": int(args.variational_nrad),
        "filter_bianchi_flux": bool(args.filter_bianchi_flux),
        "source_mode": args.source_mode,
        "deposit_shape": args.deposit_shape,
        "static_slab": bool(args.static_slab),
        "wave_zone_boost": bool(args.wave_zone_boost),
        "ssl": bool(args.ssl),
        "ssl_amp": args.ssl_amp,
        "ssl_time": args.ssl_time,
        "ssl_index": args.ssl_index,
        "clump_momentum": bool(args.clump_momentum),
        "id_residual": args.id_residual,
        "id_vector_residual": args.id_vector_residual,
        "id_puncture_radius": args.id_puncture_radius,
        "id_tol": args.id_tol,
        "id_vector_tol": args.id_vector_tol,
        "omega_scale": args.omega_scale,
        "vr_scale": args.vr_scale,
        "vr_add": args.vr_add,
        "bh_level": args.bh_level,
        "bh_level_eff": args.bh_level + lvl_shift,
        "p_level": args.p_level,
        "p_level_eff": args.p_level + lvl_shift,
        "dx_bh": dx_bh,
        "dx_p": dx_p,
        "nfilter": args.nfilter,
        "sigma_eff": sigma_eff,
        "m_bare": m_bare,
        "damp_kappa1": args.damp_kappa1,
        "shift_eta_far": args.shift_eta_far,
        "shift_eta_width": args.shift_eta_width,
        "diss": args.diss,
        "cfl": args.cfl,
        "sbc_mode": args.sbc_mode,
        "extraction_radii": [20.0, 27.0, 38.0, 48.0, 58.0],
        "ic": {
            k: (v.tolist() if isinstance(v, np.ndarray) else float(v))
            for k, v in ic.items()
        },
    }
    with open(os.path.join(out_dir, "run_meta.json"), "w") as f:
        json.dump(meta, f, indent=2)

    tag = "VAC-TWIN" if args.vacuum_twin else f"R0={args.R0:.3f}, q={args.q:.1e}"
    print(
        f"Generated {args.name} | {tag} | L={args.domain_half:.0f} M, dx_BH=M/{1.0/dx_bh:.0f}, dx_p=M/{1.0/dx_p:.0f}, "
        f"ssl={args.ssl}, wz={args.wave_zone_boost}, clump_p={args.clump_momentum}, "
        f"id=({args.id_residual}/{args.id_vector_residual}) | dir={out_dir}"
    )


if __name__ == "__main__":
    main()
