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


def build_emri_ic(ref, R0, q, omega_scale=1.0, vr_scale=1.0):
    """
    Construct isotropic Schwarzschild quasicircular + adiabatic radiation-reaction IC
    for a single particle of mass q*M0 at areal radius R0 on the +x axis.
    """
    m0 = 1.0
    m_p = float(q)
    r_iso = 0.5 * (R0 - m0 + math.sqrt(R0 * (R0 - 2.0 * m0)))
    psi0 = 1.0 + m0 / (2.0 * r_iso)
    #Exact Schwarzschild circular 4-velocity components at R0
    ut_schw = 1.0 / math.sqrt(max(1.0 - 3.0 * m0 / R0, 1.0e-12))
    lz = math.sqrt(m0 * R0 / max(1.0 - 3.0 * m0 / R0, 1.0e-12)) * math.sqrt(1.0 + m_p)

    # Particle starts on +x axis moving in +y
    u_y = (lz / r_iso) * float(omega_scale)

    # Adiabatic radiation-reaction radial velocity converted to isotropic covariant u_x
    dr_dt_1sf = ref.initial_dr_dt(R0=R0, q=m_p, model="1SF")
    dR_driso = 1.0 - (m0 * m0) / (4.0 * r_iso * r_iso)
    vr_iso = dr_dt_1sf / dR_driso
    u_x = (psi0 ** 4) * ut_schw * vr_iso * float(vr_scale)

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
    p_box_hw = max(0.95, 10.0 * (8.0 / (2 ** args.p_level)))
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

    dx_bh = 8.0 / (2 ** args.bh_level)
    dx_p = 8.0 / (2 ** args.p_level)

    if args.static_slab:
        amr_cfg_block = f"""<mesh_refinement>
refinement = static

# Static nested shells + L={args.p_level} equatorial orbital slab (zero dynamic regridding)
<refined_region1>
level = 2
x1min = -60.0
x1max = 60.0
x2min = -60.0
x2max = 60.0
x3min = -60.0
x3max = 60.0

<refined_region2>
level = 3
x1min = -30.5
x1max = 30.5
x2min = -30.5
x2max = 30.5
x3min = -30.5
x3max = 30.5

<refined_region3>
level = 4
x1min = -15.5
x1max = 15.5
x2min = -15.5
x2max = 15.5
x3min = -15.5
x3max = 15.5

<refined_region4>
level = 5
x1min = -7.5
x1max = 7.5
x2min = -7.5
x2max = 7.5
x3min = -7.5
x3max = 7.5

<refined_region5>
level = {args.p_level}
x1min = -7.5
x1max = 7.5
x2min = -7.5
x2max = 7.5
x3min = -1.95
x3max = 1.95

<refined_region6>
level = {args.bh_level}
x1min = -1.95
x1max = 1.95
x2min = -1.95
x2max = 1.95
x3min = -1.95
x3max = 1.95"""
    else:
        amr_cfg_block = f"""<mesh_refinement>
refinement          = adaptive
max_nmb_per_rank    = {args.max_nmb_per_rank}
num_levels          = 10
ncycle_check        = 64
refinement_interval = 64

# Static initial boxes matching <z4c_amr> + <particles_amr> for clean id_solve
<refined_region1>
level = 2
x1min = -60.0
x1max = 60.0
x2min = -60.0
x2max = 60.0
x3min = -60.0
x3max = 60.0

<refined_region2>
level = 3
x1min = -30.5
x1max = 30.5
x2min = -30.5
x2max = 30.5
x3min = -30.5
x3max = 30.5

<refined_region3>
level = 4
x1min = -15.5
x1max = 15.5
x2min = -15.5
x2max = 15.5
x3min = -15.5
x3max = 15.5

<refined_region4>
level = 5
x1min = -7.5
x1max = 7.5
x2min = -7.5
x2max = 7.5
x3min = -7.5
x3max = 7.5

<refined_region5>
level = {args.bh_level}
x1min = -1.95
x1max = 1.95
x2min = -1.95
x2max = 1.95
x3min = -1.95
x3max = 1.95

<refined_region6>
level = {args.p_level}
x1min = {x_p - p_box_hw:.4f}
x1max = {x_p + p_box_hw:.4f}
x2min = {-p_box_hw:.4f}
x2max = {p_box_hw:.4f}
x3min = {-p_box_hw:.4f}
x3max = {p_box_hw:.4f}

<z4c_amr>
method            = tracker
radius_0_rad      = 60.0
radius_0_reflevel = 2
radius_1_rad      = 30.5
radius_1_reflevel = 3
radius_2_rad      = 15.5
radius_2_reflevel = 4
radius_3_rad      = 7.5
radius_3_reflevel = 5

<amr_criterion0>
method = user

<particles_amr>
track_particles          = true
track_min_level          = {args.p_level}
track_max_level          = {args.p_level}
track_cells_between      = 8.0
track_buffer_cells       = 10.0
track_min_radius         = {max(0.85, 11.0 * dx_p):.2f}
track_hysteresis         = 1.6
track_spatial_hysteresis = 1.15
verbose                  = true"""

    return f"""<comment>
problem = 1000:1 Schwarzschild EMRI full 3+1 NR: {name} (R0={args.R0:.3f} M, q={args.q:.2e}, dx_BH=M/{1.0/dx_bh:.0f}, dx_p=M/{1.0/dx_p:.0f})

<job>
basename = {name}

<mesh>
nghost    = 4
nx1       = 64
x1min     = -256.0
x1max     = 256.0
ix1_bc    = outflow
ox1_bc    = outflow
nx2       = 64
x2min     = -256.0
x2max     = 256.0
ix2_bc    = outflow
ox2_bc    = outflow
nx3       = 64
x3min     = -256.0
x3max     = 256.0
ix3_bc    = outflow
ox3_bc    = outflow

<meshblock>
nx1       = 16
nx2       = 16
nx3       = 16

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
shift_Gamma     = 0.75
{eta_block}
shift_advect    = 1.0
diss            = {args.diss:.3f}
chi_div_floor   = 1.0e-5
damp_kappa1     = {args.damp_kappa1:.4f}
damp_kappa2     = 0.0
{sbc_block}
co_0_type       = BH
co_0_x          = 0.0
co_0_y          = 0.0
co_0_z          = 0.0
co_0_mass       = 1.0000
co_0_radius     = 1.90
co_0_reflevel   = {args.bh_level}
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
nfilter        = {args.nfilter}
filter_compensate = false
filter_metric_conservative = true
filter_mcons_unsplit = false
source_stage_extrap = true
matter_stride  = 1
id_solve       = true
id_vector      = true
id_residual    = stencil
id_vector_residual = stencil
id_psi_init    = trial
id_puncture_radius = 1.0
id_far         = multipole
id_tol         = 1.0e-6
id_vector_tol  = 2.0e-3
id_maxit       = 25
id_lin_tol     = 1.0e-3
id_lin_maxit   = 50
id_mg_tol      = 1.0e-3
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
lapse          = precollapsed
puncture_setup = false

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
    ap.add_argument("--bh-level", type=int, default=7)
    ap.add_argument("--p-level", type=int, default=7)
    ap.add_argument("--nfilter", type=int, default=8)
    ap.add_argument("--damp-kappa1", type=float, default=0.02)
    ap.add_argument("--shift-eta-far", type=float, default=0.20)
    ap.add_argument("--shift-eta-width", type=float, default=1.0)
    ap.add_argument("--diss", type=float, default=0.50)
    ap.add_argument("--cfl", type=float, default=0.35)
    ap.add_argument("--max-nmb-per-rank", type=int, default=2400)
    ap.add_argument("--rst-dt", type=float, default=150.0)
    ap.add_argument("--slice-dt", type=float, default=10.0)
    ap.add_argument("--sbc-mode", choices=["stock", "nonwave"], default="stock")
    ap.add_argument("--static-slab", action="store_true")
    args = ap.parse_args()

    ref = EMRIReferenceModel()
    ic = build_emri_ic(ref, args.R0, args.q, args.omega_scale, args.vr_scale)

    dx_p = 8.0 / (2 ** args.p_level)
    dx_bh = 8.0 / (2 ** args.bh_level)
    sigma_eff = math.sqrt(4.0 / 12.0 + 0.5 * args.nfilter) * dx_p
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
        "R0": args.R0,
        "q": args.q,
        "tlim": args.tlim,
        "static_slab": bool(args.static_slab),
        "omega_scale": args.omega_scale,
        "vr_scale": args.vr_scale,
        "bh_level": args.bh_level,
        "p_level": args.p_level,
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

    print(
        f"Generated {args.name} | R0={args.R0:.3f} (r_iso={ic['r_iso']:.4f}), q={args.q:.1e} | "
        f"dx_BH=M/{1.0/dx_bh:.0f}, dx_p=M/{1.0/dx_p:.0f}, nf={args.nfilter}, sig={sigma_eff:.4f} M | "
        f"k1={args.damp_kappa1:.3f}, eta_far={args.shift_eta_far:.3f}, w={args.shift_eta_width:.2f}, diss={args.diss:.2f} | "
        f"u_x={ic['u_cov'][0]:.3e}, u_y={ic['u_cov'][1]:.6f} | dir={out_dir}"
    )


if __name__ == "__main__":
    main()
