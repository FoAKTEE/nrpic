#!/usr/bin/env python3
"""
Generate AthenaK full 3+1 Numerical Relativity inputs (Z4c spinning/nonspinning
central SMBH puncture + 2 gravitating BH particles via gl4/quintic/mcons NRPIC
with id_solve constraint solver) for AGN Binary-EMRI ZKL runs on gb204.

Reads run configurations from zkl_emri_nr/data/zkl_scout_matrix.json and uses
exact Kerr/Schwarzschild circular outer kinematics composed via special-relativistic
4-velocity boost and conformal isotropic factor psi(x)^2 to populate inline covariant
momenta p{0,1}_u{1,2,3}, balanced by central SMBH recoil comp0_p = -P_particles.
"""

import argparse
import json
import math
import os
import sys
import numpy as np

SCOUT_JSON = "/home/schmidt/ssci-haiyangw/nrpic/zkl_emri_nr/data/zkl_scout_matrix.json"
DEFAULT_RUN_ROOT = "/weka/scratch/schmidt/ssci-anima/ssci-haiyangw/nrpic_grlbv/runs/zkl_nr"


def bare_mass_default(chi0):
    """Return initial trial Bowen-York bare mass for M_ADM ~ 1.0."""
    ac = abs(chi0)
    if ac < 1e-6:
        return 1.0000
    if abs(ac - 0.7) < 0.05:
        return 0.7518
    if abs(ac - 0.9) < 0.05:
        return 0.4535
    # Smooth interpolation approximation for general |chi| <= 0.9
    return 1.0 - 0.67 * (ac ** 2.4)


def initial_ah_radius(chi0):
    ac = abs(chi0)
    if ac < 1e-6:
        return 0.50
    if ac < 0.75:
        return 0.38
    return 0.30


def sr_boost_u4(v_boost, u_loc_spatial):
    """
    Exact special-relativistic boost of a local rest-frame spatial velocity u_loc (|u_loc|<1)
    by frame 3-velocity v_boost (|v_boost|<1) into global Eulerian orthonormal 4-velocity (u0, u_vec).
    """
    vb = np.asarray(v_boost, dtype=np.float64)
    ul = np.asarray(u_loc_spatial, dtype=np.float64)
    vb2 = float(np.dot(vb, vb))
    W = 1.0 / math.sqrt(max(1.0 - vb2, 1e-12))

    ul2 = float(np.dot(ul, ul))
    gam_loc = 1.0 / math.sqrt(max(1.0 - ul2, 1e-12))
    u0_l = gam_loc
    uv_l = gam_loc * ul

    vb_dot_uv = float(np.dot(vb, uv_l))
    u0_out = W * (u0_l + vb_dot_uv)
    if vb2 > 1e-16:
        u_out = uv_l + ((W - 1.0) / vb2) * vb_dot_uv * vb + W * u0_l * vb
    else:
        u_out = uv_l
    return u0_out, u_out


def build_relativistic_triple_ic(
    m0, m1, m2, a_out, a_in, e0, inc_deg, chi0, omega_deg=45.0, lan_deg=0.0
):
    """
    Construct isotropic-coordinate initial data (x, covariant u_i) for 2 gravitating
    particles orbiting a central SMBH puncture (m0, chi0) at x_0 = (0, 0, 0).
    """
    m_bin = m1 + m2
    m_tot = m0 + m_bin
    psi0 = 1.0 + m0 / (2.0 * a_out)
    R_areal = a_out * (psi0 ** 2)

    # Exact Kerr equatorial circular conserved specific angular momentum (Bardeen-Press-Teukolsky 1972)
    u = math.sqrt(m0 / R_areal)
    num = math.sqrt(m0 * R_areal) * (1.0 - 2.0 * chi0 * (u ** 3) + (chi0 ** 2) * (u ** 4))
    den = math.sqrt(max(1.0 - 3.0 * (u ** 2) + 2.0 * chi0 * (u ** 3), 1e-8))
    l_z = num / den * math.sqrt(m_tot / m0)

    # Outer binary COM at (+a_out, 0, 0) moving in +y
    r_com_iso = np.array([a_out, 0.0, 0.0], dtype=np.float64)
    u_orth_com_y = l_z / (a_out * (psi0 ** 2))
    W_com = math.sqrt(1.0 + u_orth_com_y ** 2)
    v_com_vec = np.array([0.0, u_orth_com_y / W_com, 0.0], dtype=np.float64)

    # Local proper Fermi-normal binary at apoapsis
    r_apo = a_in * (1.0 + e0)
    v_apo = math.sqrt((m_bin / a_in) * (1.0 - e0) / (1.0 + e0))
    r_loc0 = np.array([r_apo, 0.0, 0.0], dtype=np.float64)
    v_loc0 = np.array([0.0, v_apo, 0.0], dtype=np.float64)

    ci, si = math.cos(math.radians(inc_deg)), math.sin(math.radians(inc_deg))
    co, so = math.cos(math.radians(omega_deg)), math.sin(math.radians(omega_deg))
    cl, sl = math.cos(math.radians(lan_deg)), math.sin(math.radians(lan_deg))
    rz_w = np.array([[co, -so, 0.0], [so, co, 0.0], [0.0, 0.0, 1.0]])
    rx_i = np.array([[1.0, 0.0, 0.0], [0.0, ci, -si], [0.0, si, ci]])
    rz_o = np.array([[cl, -sl, 0.0], [sl, cl, 0.0], [0.0, 0.0, 1.0]])
    rot = rz_o @ rx_i @ rz_w

    R_prop = rot @ r_loc0
    U_prop = rot @ v_loc0

    # Transform local proper separation to isotropic background (length contraction along V_com + psi0^-2)
    vb2 = float(np.dot(v_com_vec, v_com_vec))
    vhat = v_com_vec / math.sqrt(max(vb2, 1e-18))
    r_iso_rel = (1.0 / (psi0 ** 2)) * (
        R_prop - (1.0 - 1.0 / W_com) * float(np.dot(R_prop, vhat)) * vhat
    )

    x1 = r_com_iso - (m2 / m_bin) * r_iso_rel
    x2 = r_com_iso + (m1 / m_bin) * r_iso_rel

    # Internal velocities in COM proper rest frame
    U1_loc = -(m2 / m_bin) * U_prop
    U2_loc = +(m1 / m_bin) * U_prop

    # Local conformal factors psi(x_k) including companion self-potential
    r1 = float(np.linalg.norm(x1))
    r2 = float(np.linalg.norm(x2))
    r12 = float(np.linalg.norm(x2 - x1))
    psi1 = 1.0 + m0 / (2.0 * r1) + m2 / (2.0 * r12)
    psi2 = 1.0 + m0 / (2.0 * r2) + m1 / (2.0 * r12)

    # Boost to local Eulerian orthonormal frame and scale by psi(x_k)^2 to covariant u_i
    _, u1_orth = sr_boost_u4(v_com_vec, U1_loc)
    _, u2_orth = sr_boost_u4(v_com_vec, U2_loc)

    u1_cov = (psi1 ** 2) * u1_orth
    u2_cov = (psi2 ** 2) * u2_orth

    # Exact balancing ADM momentum on central SMBH puncture (zero total momentum)
    p0_cov = -(m1 * u1_cov + m2 * u2_cov)

    return {
        "x1": x1,
        "u1": u1_cov,
        "x2": x2,
        "u2": u2_cov,
        "p0": p0_cov,
        "v_com": v_com_vec,
        "psi0": psi0,
        "l_z": l_z,
        "r12_iso": r12,
    }


def circ_ring_regions(level, r_in, r_out, zmax, nseg=24, start_idx=10):
    """Generate tight axis-aligned <refined_region> blocks covering a circular annulus."""
    out = []
    idx = start_idx
    for k in range(nseg):
        th0 = 2.0 * math.pi * k / nseg
        th1 = 2.0 * math.pi * (k + 1) / nseg
        xs, ys = [], []
        for th in (th0, 0.5 * (th0 + th1), th1):
            for r in (r_in, r_out):
                xs.append(r * math.cos(th))
                ys.append(r * math.sin(th))
        out.append(
            f"""<refined_region{idx}>
level = {level}
x1min = {min(xs):.4f}
x1max = {max(xs):.4f}
x2min = {min(ys):.4f}
x2max = {max(ys):.4f}
x3min = {-zmax:.4f}
x3max = {zmax:.4f}
"""
        )
        idx += 1
    return "\n".join(out)


def mesh_preset_params(preset):
    """Return verified power-of-2 static circular-ring or dynamic AMR mesh parameters."""
    if preset == "amr_dyn":
        return {
            "domain_half": 64.0,
            "mesh_nx": 64,
            "mb_nx": 16,
            "dx0": 2.0,
            "wave_level": 1,
            "ring_level": 5,
            "default_bh_level": 6,
            "bh_box": 0.85,
            "co_radius": 0.85,
            "max_nmb_per_rank": 2400,
            "num_levels": 10,
            "ncycle_check": 16,
            "refinement_interval": 16,
            "track_min_level": 5,
            "track_max_level": 8,
            "track_cells_between": 8.0,
            "track_buffer_cells": 14.0,
            "track_min_radius": 1.00,
            "track_hysteresis": 2.5,
            "track_spatial_hysteresis": 1.12,
        }
    if preset == "m16_64_L5":
        return {
            "domain_half": 64.0,
            "mesh_nx": 64,
            "mb_nx": 16,
            "dx0": 2.0,
            "wave_level": None,
            "ring_level": 5,
            "default_bh_level": 6,
            "ring_rin": 14.3,
            "ring_rout": 15.7,
            "ring_zmax": 0.72,
            "ring_nseg": 64,
            "bh_box": 0.85,
        }
    if preset == "t3_32":
        return {
            "domain_half": 48.0,
            "mesh_nx": 64,
            "mb_nx": 32,
            "dx0": 1.5,
            "wave_level": None,
            "ring_level": 4,
            "default_bh_level": 6,
            "ring_rin": 14.0,
            "ring_rout": 16.0,
            "ring_zmax": 0.95,
            "ring_nseg": 24,
            "bh_box": 0.90,
        }
    if preset == "m6_32":
        return {
            "domain_half": 96.0,
            "mesh_nx": 64,
            "mb_nx": 32,
            "dx0": 3.0,
            "wave_level": 2,
            "ring_level": 5,
            "default_bh_level": 7,
            "ring_rin": 14.0,
            "ring_rout": 16.0,
            "ring_zmax": 0.95,
            "ring_nseg": 24,
            "bh_box": 0.90,
        }
    if preset == "m8_16":
        return {
            "domain_half": 96.0,
            "mesh_nx": 32,
            "mb_nx": 16,
            "dx0": 6.0,
            "wave_level": 3,
            "ring_level": 6,
            "default_bh_level": 8,
            "ring_rin": 14.0,
            "ring_rout": 16.0,
            "ring_zmax": 0.95,
            "ring_nseg": 24,
            "bh_box": 0.90,
        }
    raise ValueError(f"Unknown mesh_preset: {preset}")


def format_athinput(
    cfg, ic, tlim, mesh_preset, bh_level, comp0_mass, nfilter, matter_stride, cfl, diss, rst_dt, snap_dt, slice_dt, traj_dcycle,
    damp_kappa1=None, shift_eta=None, max_nmb_per_rank=None, track_max_level=None, track_cells_between=None, track_buffer_cells=None, track_min_radius=None
):
    run_name = cfg["name"]
    chi0 = float(cfg["chi0"])
    m0 = 1.0
    ah_rad = initial_ah_radius(chi0)
    mp = mesh_preset_params(mesh_preset)
    is_amr = (mesh_preset == "amr_dyn")
    L = mp["domain_half"]
    nx = mp["mesh_nx"]
    mb = mp["mb_nx"]
    dx_bin = mp["dx0"] / (2 ** mp["ring_level"])
    sigma_eff = math.sqrt(4.0 / 12.0 + 0.5 * nfilter) * dx_bin
    m1_bare = float(cfg["m1"]) * (1.0 + float(cfg["m1"]) / (math.sqrt(2.0 * math.pi) * sigma_eff))
    m2_bare = float(cfg["m2"]) * (1.0 + float(cfg["m2"]) / (math.sqrt(2.0 * math.pi) * sigma_eff))
    p0_bal = -(m1_bare * ic["u1"] + m2_bare * ic["u2"])
    bh_box = 0.48 if (mesh_preset in ("m16_64_L5", "amr_dyn") and bh_level >= 7) else mp["bh_box"]
    dx_bh = mp["dx0"] / (2 ** bh_level)

    k1 = float(damp_kappa1) if damp_kappa1 is not None else (0.50 if is_amr else 0.02)
    eta0 = float(shift_eta) if shift_eta is not None else (0.07 if is_amr else 2.0)

    if is_amr:
        xcm0 = 0.5 * (ic["x1"] + ic["x2"])
        max_nmb = int(max_nmb_per_rank) if max_nmb_per_rank is not None else mp["max_nmb_per_rank"]
        tmax_lvl = int(track_max_level) if track_max_level is not None else mp["track_max_level"]
        tcb = float(track_cells_between) if track_cells_between is not None else mp["track_cells_between"]
        tbc = float(track_buffer_cells) if track_buffer_cells is not None else mp["track_buffer_cells"]
        tmr = float(track_min_radius) if track_min_radius is not None else mp["track_min_radius"]
        co_rad = bh_box if bh_level >= 7 else mp["co_radius"]
        eta_mref = 2.0 / eta0
        mesh_ref_block = f"""<mesh_refinement>
refinement          = adaptive
max_nmb_per_rank    = {max_nmb}
num_levels          = {mp['num_levels']}
ncycle_check        = {mp['ncycle_check']}
refinement_interval = {mp['refinement_interval']}

# Wave zone (L1 covering r <= 24 M)
<refined_region1>
level = {mp['wave_level']}
x1min = -24.0
x1max = 24.0
x2min = -24.0
x2max = 24.0
x3min = -24.0
x3max = 24.0

# Central SMBH puncture core (dx_BH = M/{1.0/dx_bh:.2f}, >=32 cells across evolved D_AH)
<refined_region2>
level = {bh_level}
x1min = -{bh_box:.2f}
x1max = {bh_box:.2f}
x2min = -{bh_box:.2f}
x2max = {bh_box:.2f}
x3min = -{bh_box:.2f}
x3max = {bh_box:.2f}

# Initial L5 binary box centered at binary COM
<refined_region3>
level = {mp['ring_level']}
x1min = {xcm0[0] - tmr:.4f}
x1max = {xcm0[0] + tmr:.4f}
x2min = {xcm0[1] - tmr:.4f}
x2max = {xcm0[1] + tmr:.4f}
x3min = {xcm0[2] - tmr:.4f}
x3max = {xcm0[2] + tmr:.4f}

<z4c_amr>
method            = tracker
radius_0_rad      = 24.0
radius_0_reflevel = {mp['wave_level']}

<amr_criterion0>
method = user

<particles_amr>
track_particles          = true
track_min_level          = {mp['track_min_level']}
track_max_level          = {tmax_lvl}
track_cells_between      = {tcb:.2f}
track_buffer_cells       = {tbc:.2f}
track_min_radius         = {tmr:.2f}
track_hysteresis         = {mp['track_hysteresis']:.2f}
track_spatial_hysteresis = {mp['track_spatial_hysteresis']:.2f}
verbose                  = true
"""
        eta_ext_lines = f"""shift_eta            = {eta0:.6f}
shift_eta_profile    = true
shift_eta_mref       = {eta_mref:.10f}
shift_eta_width      = 2.0"""
    else:
        ring_blocks = circ_ring_regions(
            mp["ring_level"], mp["ring_rin"], mp["ring_rout"], mp["ring_zmax"],
            nseg=mp["ring_nseg"], start_idx=10
        )
        wave_block = ""
        if mp["wave_level"] is not None:
            wave_block = f"""# Wave zone (dx = 0.75 M covering GW extraction radii 22, 26, 30 M)
<refined_region1>
level = {mp['wave_level']}
x1min = -35.0
x1max = 35.0
x2min = -35.0
x2max = 35.0
x3min = -35.0
x3max = 35.0

"""
        co_rad = 1.2
        mesh_ref_block = f"""<mesh_refinement>
refinement = static

{wave_block}# Central SMBH puncture core (dx_BH = M/{1.0/dx_bh:.2f}, >=32 cells across evolved D_AH)
<refined_region2>
level = {bh_level}
x1min = -{bh_box:.2f}
x1max = {bh_box:.2f}
x2min = -{bh_box:.2f}
x2max = {bh_box:.2f}
x3min = -{bh_box:.2f}
x3max = {bh_box:.2f}

# {mp['ring_nseg']}-segment circular orbital annulus (r in [{mp['ring_rin']}, {mp['ring_rout']}] M, |z| <= {mp['ring_zmax']} M; dx_bin = M/{1.0/dx_bin:.2f})
{ring_blocks}"""
        eta_ext_lines = f"shift_eta       = {eta0:.6f}"

    return f"""<comment>
problem = AGN Binary-EMRI ZKL full 3+1 NR: {run_name} ({cfg['suite']}, {mesh_preset}, m1={cfg['m1']}, m2={cfg['m2']}, a_in={cfg['a_in']}, I0={cfg['inc']} deg, chi0={chi0})

<job>
basename = {run_name}

<mesh>
nghost    = 4
nx1       = {nx}
x1min     = {-L:.1f}
x1max     = {L:.1f}
ix1_bc    = outflow
ox1_bc    = outflow
nx2       = {nx}
x2min     = {-L:.1f}
x2max     = {L:.1f}
ix2_bc    = outflow
ox2_bc    = outflow
nx3       = {nx}
x3min     = {-L:.1f}
x3max     = {L:.1f}
ix3_bc    = outflow
ox3_bc    = outflow

<meshblock>
nx1       = {mb}
nx2       = {mb}
nx3       = {mb}

{mesh_ref_block}<time>
evolution  = dynamic
integrator = rk3
cfl_number = {cfl:.2f}
nlim       = -1
tlim       = {tlim:.1f}
ndiag      = 64

<z4c>
lapse_oplog     = 2.0
lapse_harmonicf = 1.0
lapse_harmonic  = 0.0
lapse_advect    = 1.0
shift_Gamma     = 0.75
{eta_ext_lines}
shift_advect    = 1.0
diss            = {diss:.2f}
chi_div_floor   = 1.0e-5
damp_kappa1     = {k1:.4f}
damp_kappa2     = 0.0
co_0_type       = BH
co_0_x          = 0.0
co_0_y          = 0.0
co_0_z          = 0.0
co_0_mass       = {m0:.4f}
co_0_radius     = {co_rad:.2f}
co_0_reflevel   = {bh_level}
tracker_mode    = ode
nrad_wave_extraction = 3
extraction_radius_0  = 22.0
extraction_radius_1  = 30.0
extraction_radius_2  = 38.0
extraction_nlev      = 2
waveform_dt          = 0.1

<fastflow>
find_every        = 40
metric_drvts      = interpolant
num_horizons      = 1
npunct            = 1
ntheta            = 24
lmax              = 12
use_puncture_0    = 0
initial_radius_0  = {ah_rad:.2f}
flow_iterations_0 = 400
flow_alpha_beta_const_0 = 1.0
hmean_tol_0       = 100.0
mass_tol_0        = 1.0e-5
start_time_0      = 0.0
stop_time_0       = 5000.0
verbose           = false

<gravity>
four_pi_G   = 1.0
threshold   = 0.0
mg_bc       = robin
robin_x1    = 0.0
robin_x2    = 0.0
robin_x3    = 0.0
show_defect = 0

<particles>
particle_type  = nrpic
pusher         = vlasov_hybrid
vlasov_mode    = hybrid
vlasov_pusher  = gl4
vlasov_time_interp = quadratic
interp         = quintic
metric         = mesh
tolerance      = 2.0e-14
max_iterations = 200
deposit        = true
deposit_shape  = pcs
deposit_comp_c = 0.0
nfilter        = {nfilter}
filter_compensate = false
filter_metric_conservative = true
filter_mcons_unsplit = false
source_stage_extrap = true
matter_stride  = {matter_stride}
id_solve       = true
id_vector      = true
id_residual    = stencil
id_vector_residual = stencil
id_psi_init    = trial
id_puncture_radius = 1.0
id_far         = multipole
id_tol         = 1.0e-7
id_vector_tol  = 1.0e-4
id_maxit       = 25
id_lin_tol     = 1.0e-3
id_lin_maxit   = 50
id_mg_tol      = 1.0e-3
id_dump        = false
alpha_exc      = 0.08
ah_exc_factor  = 0.85
hist_dcycle    = 40
traj_ntrack    = 2
traj_dcycle    = {traj_dcycle}
snap_dt        = {snap_dt:.2f}
nparticles     = 2
p0_x1 = {ic['x1'][0]:.15e}
p0_x2 = {ic['x1'][1]:.15e}
p0_x3 = {ic['x1'][2]:.15e}
p0_u1 = {ic['u1'][0]:.15e}
p0_u2 = {ic['u1'][1]:.15e}
p0_u3 = {ic['u1'][2]:.15e}
p0_m  = {m1_bare:.15e}
p1_x1 = {ic['x2'][0]:.15e}
p1_x2 = {ic['x2'][1]:.15e}
p1_x3 = {ic['x2'][2]:.15e}
p1_u1 = {ic['u2'][0]:.15e}
p1_u2 = {ic['u2'][1]:.15e}
p1_u3 = {ic['u2'][2]:.15e}
p1_m  = {m2_bare:.15e}

<problem>
pgen_name      = nrpic_cf
ncomp          = 3
comp0_type     = puncture
comp0_mass     = {comp0_mass:.10f}
comp0_x1       = 0.0
comp0_x2       = 0.0
comp0_x3       = 0.0
comp0_p1       = {p0_bal[0]:.15e}
comp0_p2       = {p0_bal[1]:.15e}
comp0_p3       = {p0_bal[2]:.15e}
comp0_s1       = 0.0
comp0_s2       = 0.0
comp0_s3       = {chi0:.6f}
comp1_type     = gaussian
comp1_mass     = {float(cfg['m1']):.10f}
comp1_sigma    = {sigma_eff:.10f}
comp1_x1       = {ic['x1'][0]:.15e}
comp1_x2       = {ic['x1'][1]:.15e}
comp1_x3       = {ic['x1'][2]:.15e}
comp2_type     = gaussian
comp2_mass     = {float(cfg['m2']):.10f}
comp2_sigma    = {sigma_eff:.10f}
comp2_x1       = {ic['x2'][0]:.15e}
comp2_x2       = {ic['x2'][1]:.15e}
comp2_x3       = {ic['x2'][2]:.15e}
lapse          = precollapsed
puncture_setup = false

<output1>
file_type = hst
dt        = 0.5

<output2>
file_type = rst
dt        = {rst_dt:.1f}

<output3>
file_type = bin
variable  = z4c_alpha
id        = alpha_xy
slice_x3  = 0.001
dt        = {slice_dt:.2f}

<output4>
file_type = bin
variable  = z4c_alpha
id        = alpha_xz
slice_x2  = 0.001
dt        = {slice_dt:.2f}

<output5>
file_type = bin
variable  = con_H
id        = conH_xy
slice_x3  = 0.001
dt        = {slice_dt:.2f}
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True, help="Run name in zkl_scout_matrix.json, or 'phase1'/'all'")
    ap.add_argument("--out-root", default=DEFAULT_RUN_ROOT)
    ap.add_argument("--subdir", default=None, help="Optional override directory name under out-root")
    ap.add_argument("--tlim", type=float, default=1800.0)
    ap.add_argument("--mesh-preset", choices=("amr_dyn", "m16_64_L5", "t3_32", "m6_32", "m8_16"), default="m16_64_L5",
                    help="Mesh preset (amr_dyn = compact dynamic L5->L8 AMR; m16_64_L5/t3_32/m6_32/m8_16 = static)")
    ap.add_argument("--bh-level", type=int, default=None,
                    help="Override central SMBH core level (default: 6/7 for m16_64_L5/amr_dyn, 6 for t3_32, 7 for m6_32, 8 for m8_16)")
    ap.add_argument("--comp0-mass", type=float, default=None, help="Override central puncture bare mass")
    ap.add_argument("--nfilter", type=int, default=None, help="Deposit smoothing filter passes (default: 6 for amr_dyn, 4 otherwise)")
    ap.add_argument("--matter-stride", type=int, default=None, help="Matter/particle stride in cycles (default: 1 for amr_dyn, 4 otherwise)")
    ap.add_argument("--cfl", type=float, default=0.35)
    ap.add_argument("--diss", type=float, default=0.2)
    ap.add_argument("--damp-kappa1", type=float, default=None, help="Override Z4c kappa1 damping (default: 0.50 for amr_dyn, 0.02 otherwise)")
    ap.add_argument("--shift-eta", type=float, default=None, help="Override Gamma-driver shift eta (default: 0.07 for amr_dyn, 2.0 otherwise)")
    ap.add_argument("--max-nmb-per-rank", type=int, default=None, help="Override adaptive max_nmb_per_rank (default: preset)")
    ap.add_argument("--track-max-level", type=int, default=None, help="Override AMR binary max level (default: preset)")
    ap.add_argument("--track-cells-between", type=float, default=None, help="Override AMR cells between particles (default: preset)")
    ap.add_argument("--track-buffer-cells", type=float, default=None, help="Override AMR buffer cells around particles (default: preset)")
    ap.add_argument("--track-min-radius", type=float, default=None, help="Override AMR minimum box half-width (default: preset)")
    ap.add_argument("--rst-dt", type=float, default=200.0)
    ap.add_argument("--snap-dt", type=float, default=5.0)
    ap.add_argument("--slice-dt", type=float, default=5.0)
    ap.add_argument("--traj-dcycle", type=int, default=4)
    args = ap.parse_args()

    with open(SCOUT_JSON, "r") as f:
        matrix = json.load(f)
    by_name = {row["name"]: row for row in matrix}

    if args.run == "phase1":
        names = ["GR_low_a082", "FID_I82_chi0", "I20_subcrit", "GR_high_a055", "I86_high", "SPIN_p07", "SPIN_m07"]
    elif args.run == "all":
        names = [row["name"] for row in matrix]
    else:
        if args.run not in by_name:
            sys.exit(f"Unknown run '{args.run}'. Available: {list(by_name)}")
        names = [args.run]

    mp = mesh_preset_params(args.mesh_preset)
    is_amr = (args.mesh_preset == "amr_dyn")
    nfilter = args.nfilter if args.nfilter is not None else (6 if is_amr else 4)
    matter_stride = args.matter_stride if args.matter_stride is not None else (1 if is_amr else 4)
    k1 = float(args.damp_kappa1) if args.damp_kappa1 is not None else (0.50 if is_amr else 0.02)
    eta0 = float(args.shift_eta) if args.shift_eta is not None else (0.07 if is_amr else 2.0)

    for name in names:
        cfg = by_name[name]
        chi0 = float(cfg["chi0"])
        if args.bh_level is not None:
            bh_lvl = args.bh_level
        elif args.mesh_preset in ("m16_64_L5", "amr_dyn") and abs(chi0) > 0.75:
            bh_lvl = 7
        else:
            bh_lvl = mp["default_bh_level"]
        dx_bin = mp["dx0"] / (2 ** mp["ring_level"])
        dx_bh = mp["dx0"] / (2 ** bh_lvl)
        sigma_eff = math.sqrt(4.0 / 12.0 + 0.5 * nfilter) * dx_bin
        m1_bare = float(cfg["m1"]) * (1.0 + float(cfg["m1"]) / (math.sqrt(2.0 * math.pi) * sigma_eff))
        m2_bare = float(cfg["m2"]) * (1.0 + float(cfg["m2"]) / (math.sqrt(2.0 * math.pi) * sigma_eff))
        cmass = args.comp0_mass if args.comp0_mass is not None else bare_mass_default(chi0)
        ic = build_relativistic_triple_ic(
            1.0, cfg["m1"], cfg["m2"], cfg["a_out"], cfg["a_in"], cfg["e0"], cfg["inc"], chi0
        )
        folder = args.subdir if (args.subdir and len(names) == 1) else name
        out_dir = os.path.join(args.out_root, folder)
        os.makedirs(out_dir, exist_ok=True)
        ath_path = os.path.join(out_dir, f"{name}.athinput")
        with open(ath_path, "w") as f:
            f.write(
                format_athinput(
                    cfg, ic, args.tlim, args.mesh_preset, bh_lvl, cmass, nfilter,
                    matter_stride, args.cfl, args.diss,
                    args.rst_dt, args.snap_dt, args.slice_dt, args.traj_dcycle,
                    damp_kappa1=args.damp_kappa1,
                    shift_eta=args.shift_eta,
                    max_nmb_per_rank=args.max_nmb_per_rank,
                    track_max_level=args.track_max_level,
                    track_cells_between=args.track_cells_between,
                    track_buffer_cells=args.track_buffer_cells,
                    track_min_radius=args.track_min_radius,
                )
            )
        meta = {
            "cfg": cfg,
            "mesh_preset": args.mesh_preset,
            "bh_level": bh_lvl,
            "dx_bin": dx_bin,
            "dx_bh": dx_bh,
            "nfilter": nfilter,
            "matter_stride": matter_stride,
            "damp_kappa1": k1,
            "shift_eta": eta0,
            "cfl": args.cfl,
            "diss": args.diss,
            "sigma_eff": sigma_eff,
            "m1_bare": m1_bare,
            "m2_bare": m2_bare,
            "comp0_mass": cmass,
            "tlim": args.tlim,
            "ic": {k: (v.tolist() if isinstance(v, np.ndarray) else float(v)) for k, v in ic.items()},
        }
        if is_amr:
            meta.update({
                "ring_level": mp["ring_level"],
                "track_max_level": int(args.track_max_level) if args.track_max_level is not None else mp["track_max_level"],
                "track_cells_between": float(args.track_cells_between) if args.track_cells_between is not None else mp["track_cells_between"],
                "track_buffer_cells": float(args.track_buffer_cells) if args.track_buffer_cells is not None else mp["track_buffer_cells"],
                "track_min_radius": float(args.track_min_radius) if args.track_min_radius is not None else mp["track_min_radius"],
                "max_nmb_per_rank": int(args.max_nmb_per_rank) if args.max_nmb_per_rank is not None else mp["max_nmb_per_rank"],
            })
        meta_path = os.path.join(out_dir, "run_meta.json")
        with open(meta_path, "w") as f:
            json.dump(meta, f, indent=2)
        print(
            f"Generated {name:16s} | {args.mesh_preset} | L_BH={bh_lvl} (dx_BH=M/{1.0/dx_bh:.2f}, dx_bin=M/{1.0/dx_bin:.2f}) | "
            f"nf={nfilter} ms={matter_stride} k1={k1:.2f} eta={eta0:.2f} | "
            f"comp0_mass={cmass:.4f} | sig={sigma_eff:.4f} | r12_iso={ic['r12_iso']:.4f} | dir={out_dir}"
        )


if __name__ == "__main__":
    main()
