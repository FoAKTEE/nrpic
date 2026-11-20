#!/usr/bin/env python3
"""Writes the AthenaK input decks of the G2 convergence series (package conv_ball, Track A,
wave 3) into conv_ball/decks/: nest<HF>_L<OUTER>.athinput for the nested geometry of
nested.py (finest cells M/HF inside [-1, 1]^3, level boundaries at 1, 2, 4, 8 (, 16) M,
outer boundary at OUTER). Everything else is the BH-1R deck (runs_ball/bh_smr.athinput at
commit 9cddbfc6, copy in scripts/): data set 3 through horizon formation with the relaxed
1+log lapse (lapse_leak = 8) and the Gamma-driver, particles excised below alpha = 0.1,
PCS clouds at the finest local level with the fourth-order cloud compensation, finder from
t = 9 with initial coordinate radius 1 M, 400 iterations, mass tolerance 1e-5. Cadences in
code time are those of BH-1R (finder and trajectories every 0.125 M, histories every cycle,
line outputs every 0.25 M); restart files every 4 M (chains).

    make_decks.py [--outdir DIR]
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nested as NS           # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))

TEMPLATE = """# conv_ball (Track A, wave 3): data set 3 on the nested static mesh "{name}" of the G2
# convergence series (tracks/A-emd-pbh/conv_ball/DESIGN.md). Written by scripts/make_decks.py.
# Root {n}^3 cells of M/{hroot_inv:g} over [-{outer:g}, {outer:g}]^3 in MeshBlocks of {nb}^3; {L} static
# levels, level l covering [-{outer:g}/2^l, {outer:g}/2^l]^3; finest cells M/{hf:g} inside [-1, 1]^3
# ({blocks} leaf MeshBlocks, {cells} leaf cells). Physics, gauge, deposit and finder as BH-1R
# (runs_ball/bh_smr.athinput at 9cddbfc6). Give on the command line:
#   problem/comp0_file=<prep>/<stem>.tab
#   particles/particle_file=<prep>/<lattice>/<stem>_<lattice>_track.nrp   particles/traj_ntrack=<n_track>

<comment>
problem   = expanding dust ball, data set 3, relaxed 1+log lapse, nested static mesh {name}

<job>
basename  = ball

<mesh>
nghost    = 4
nx1       = {n}
x1min     = -{outer:.1f}
x1max     = {outer:.1f}
ix1_bc    = outflow
ox1_bc    = outflow
nx2       = {n}
x2min     = -{outer:.1f}
x2max     = {outer:.1f}
ix2_bc    = outflow
ox2_bc    = outflow
nx3       = {n}
x3min     = -{outer:.1f}
x3max     = {outer:.1f}
ix3_bc    = outflow
ox3_bc    = outflow

<meshblock>
nx1       = {nb}
nx2       = {nb}
nx3       = {nb}

<mesh_refinement>
refinement       = static
{regions}
<time>
evolution  = dynamic
integrator = rk4
cfl_number = 0.25
nlim       = -1
tlim       = 16.0
ndiag      = 10

<z4c>
lapse_oplog     = 2.0
lapse_harmonicf = 1.0
lapse_harmonic  = 0.0
lapse_volume    = 0.0
lapse_advect    = 1.0
lapse_leak      = 8.0      # 1/T of the relaxation of the excess lapse; T = 0.125 M
lapse_leak_alpha = 1.0     # reference lapse
shift_Gamma     = 0.75
shift_eta       = 2.0
shift_advect    = 1.0
diss            = 0.5
chi_div_floor   = 1.0e-5
damp_kappa1     = 0.02
damp_kappa2     = 0.0
excise_chi      = 0.0

<fastflow>
find_every        = {every}
metric_drvts      = interpolant
num_horizons      = 1
npunct            = 0
ntheta            = 16
lmax              = 8
use_puncture_0    = -1
center_x_0        = 0.0
center_y_0        = 0.0
center_z_0        = 0.0
initial_radius_0  = 1.0
flow_iterations_0 = 400
flow_alpha_beta_const_0 = 1.0
hmean_tol_0       = 100.0
mass_tol_0        = 1.0e-5
start_time_0      = 9.0
stop_time_0       = 1000.0
verbose           = false

<particles>
particle_type  = nrpic
pusher         = midpoint
metric         = mesh
interp         = bspline
tolerance      = 1.0e-10
max_iterations = 50
deposit        = true
deposit_shape  = pcs
deposit_comp_c = 0.1666666666666667
deposit_comp_c2 = 0.4666666666666667
nfilter        = 0
filter_compensate = false
source_density = true
source_extrap  = true
alpha_exc      = 0.1
hist_dcycle    = 1
cstat_dcycle   = 1
traj_dcycle    = {every}
traj_ntrack    = 0
snap_dt        = 4.0
field_constraints = true
field_time1    = 4.0
field_time2    = 8.0
field_time3    = 10.0
field_time4    = 12.0
particle_file  = ball.nrp

<problem>
pgen_name  = nrpic_cf
ncomp      = 1
comp0_type = table
comp0_file = ball.tab
lapse      = table
lapse_comp = 0
shift      = zero

<output1>
file_type = hst
dt        = 0.25

<output2>
file_type = rst
dt        = 4.0

<output3>
file_type = tab
variable  = adm
dt        = 0.25
slice_x2  = 0.01
slice_x3  = 0.01
data_format = %.12e

<output4>
file_type = tab
variable  = z4c
dt        = 0.25
slice_x2  = 0.01
slice_x3  = 0.01
data_format = %.12e

<output5>
file_type = tab
variable  = con
dt        = 0.25
slice_x2  = 0.01
slice_x3  = 0.01
data_format = %.12e

<output6>
file_type = tab
variable  = tmunu
dt        = 0.25
slice_x2  = 0.01
slice_x3  = 0.01
data_format = %.12e
"""


def deck(hf_inv, outer):
    g = NS.nest_blocks(1.0 / hf_inv, outer)
    regions = []
    for l in range(1, g["L"] + 1):
        b = 0.975 * outer / 2 ** l
        regions.append(f"\n<refined_region{l}>\nlevel = {l}\n" + "".join(
            f"x{k}min = {-b:.5f}\nx{k}max = {b:.5f}\n" for k in (1, 2, 3)))
    every = int(round(0.125 / (0.25 / hf_inv)))
    name = f"nest{hf_inv}_L{int(outer)}"
    txt = TEMPLATE.format(name=name, n=g["n_root"], hroot_inv=1.0 / g["levels"][0][1], outer=outer, nb=g["block"],
                          L=g["L"], hf=hf_inv, blocks=g["leaf_blocks"], cells=g["leaf_cells"],
                          regions="".join(regions) + "\n", every=every)
    return name, txt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default=os.path.join(os.path.dirname(HERE), "decks"))
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    for hf_inv, outer in ((16, 16.0), (32, 16.0), (64, 16.0), (16, 32.0), (32, 32.0), (64, 32.0)):
        name, txt = deck(hf_inv, outer)
        p = os.path.join(a.outdir, name + ".athinput")
        with open(p, "w") as f:
            f.write(txt)
        print(p)


if __name__ == "__main__":
    main()
