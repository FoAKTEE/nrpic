#!/usr/bin/env python3
"""Input files of the USR case for AthenaK, from the reference (usr_reference.json).

    python3 make_inputs.py --ref ../results/usr_reference.json --out ../inputs

Writes
  usr_base.athinput   initial slice at N* (<problem> id = stochastic) of core's branch
                      executable core_scalar-2, 32^3, nmax2 = 16 (overridden by the lists)
  usr_256.athinput    the production set-up of P1 (256^3, nmax2 = 4096) for a card
  usr_bg.athinput     homogeneous background (<problem> id = flrw), no noise: runs on the
                      release core-v0.3 as well (no option of core/scalar-2 in it)
  proc.list           the processor runs of this package (scripts/run_list_cpu.sh)
The options follow ../../ladder/inputs/sr_base.athinput (the slow-roll ladder) except the
potential, the background at N*, the mode file and the end time.
"""
import argparse
import json
import os

ROOT = "/data/haiyangw/nrpic/wt/E-stoch-inf"
PKG = "tracks/E-stoch-inf/usr"

HEAD = """# Ultra-slow-roll (Higgs inflection) case of arXiv:2512.14649 (PRD_v2.tex:405-424, set-up
# 503-519) in the units of the code (G = c = 1, time unit 1/H*, a* = 1, box 2 pi/sigma):
# written by {pkg}/scripts/make_inputs.py from the reference run {run}
# ({pkg}/results/usr_reference.json).  Potential P1:409 with lambda = 8 pi Lambda/H*^2,
# vev = v/sqrt(8 pi); background at N* = N0 + 3 (phi0, pi0); tlim = code time of
# N* + 10 e-folds.  Geodesic slicing, zero shift, no damping, no dissipation (SPEC 2.5, 4);
# Courant 0.25 (SCOPE 4 item 1).  {what}
"""

MESH = """
<mesh>
nghost    = 4
nx1       = {n}
x1min     = 0.0
x1max     = 6.283185307179586
ix1_bc    = periodic
ox1_bc    = periodic
nx2       = {n}
x2min     = 0.0
x2max     = 6.283185307179586
ix2_bc    = periodic
ox2_bc    = periodic
nx3       = {n}
x3min     = 0.0
x3max     = 6.283185307179586
ix3_bc    = periodic
ox3_bc    = periodic

<meshblock>
nx1       = {nb}
nx2       = {nb}
nx3       = {nb}

<time>
evolution  = dynamic
integrator = rk4
cfl_number = {cfl}
nlim       = -1
tlim       = {tlim:.17g}
ndiag      = 20

<z4c>
lapse_oplog     = 0.0
lapse_harmonic  = 0.0
lapse_advect    = 0.0
shift_Gamma     = 0.0
shift_eta       = 0.0
shift_advect    = 0.0
diss            = 0.0
damp_kappa1     = 0.0
damp_kappa2     = 0.0
excise_chi      = 0.0
"""

SF_NOISE = """
<scalar_field>
couple           = true
potential        = inflection
lambda           = {lam:.17e}
vev              = {vev:.17e}
diss             = 0.0
hist_dcycle      = 1
con_dcycle       = 1
dump_dt          = {dump_dt}
dump_metric      = true
dump_magnitudes  = false
dump_constraints = false
dump_noise       = false
noise            = mukhanov_sasaki
noise_nmax2      = {nmax2}
noise_sharpness  = 5.0
noise_sigma      = 1.0
noise_level      = 0
noise_projector  = stencil
noise_kick_pi    = true
noise_kick_k     = true
noise_kick_a     = true
noise_pi_sign    = 1.0
noise_mode_file  = {modefile}
noise_mode_scale = 1.0

<problem>
pgen_name      = scalar_field
id             = stochastic
phi0           = {phi0:.17e}
pi0            = {pi0:.17e}
slice_window   = true
slice_k2       = stencil
slice_delta_pi = corrected
"""

SF_BG = """
<scalar_field>
couple           = true
potential        = inflection
lambda           = {lam:.17e}
vev              = {vev:.17e}
diss             = 0.0
hist_dcycle      = 1

<problem>
pgen_name      = scalar_field
id             = flrw
phi0           = {phi0:.17e}
pi0            = {pi0:.17e}
"""


def job(base):
    return f"""
<comment>
problem   = stochastic inflection, ultra-slow-roll (inflection) case, package usr of Track E

<job>
basename  = {base}
rng_seed  = 20261115
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    r = json.load(open(a.ref))
    ci = r["code_inputs"]
    run = r.get("run_id", "(see results/README)")
    tl = r["t_code_end"]
    v = dict(lam=ci["lambda"], vev=ci["vev"], phi0=ci["phi0"], pi0=ci["pi0"], tlim=tl)
    mdir = f"{ROOT}/{PKG}/inputs"
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "usr_base.athinput"), "w") as fp:
        fp.write(HEAD.format(pkg=PKG, run=run, what="Base of the processor runs (32^3)."))
        fp.write(job("usr"))
        fp.write(MESH.format(n=32, nb=32, cfl=0.25, **v))
        fp.write(SF_NOISE.format(dump_dt=0.25, nmax2=16, modefile=f"{mdir}/modes_usr_n16.txt",
                                 **v))
    with open(os.path.join(a.out, "usr_256.athinput"), "w") as fp:
        fp.write(HEAD.format(pkg=PKG, run=run,
                             what="Production set-up of P1 (256^3, k_max = 64 dk) for one "
                                  "card; not run by this package."))
        fp.write(job("usr"))
        fp.write(MESH.format(n=256, nb=256, cfl=0.25, **v))
        fp.write(SF_NOISE.format(dump_dt=0.5, nmax2=4096,
                                 modefile=f"{mdir}/modes_usr_n4096.txt", **v))
    with open(os.path.join(a.out, "usr_bg.athinput"), "w") as fp:
        fp.write(HEAD.format(pkg=PKG, run=run,
                             what="Homogeneous background (id = flrw), 8^3, Courant 0.0625: "
                                  "the step of the 32^3 runs at 0.25."))
        fp.write(job("bg"))
        fp.write(MESH.format(n=8, nb=8, cfl=0.0625, **v))
        fp.write(SF_BG.format(**v))
    base = f"{PKG}/inputs/usr_base.athinput"
    bgi = f"{PKG}/inputs/usr_bg.athinput"
    m64 = f"scalar_field/noise_nmax2=64 scalar_field/noise_mode_file={mdir}/modes_usr_n64.txt"
    lines = [
        "# name  executable (v03: release core-v0.3; s2: core_scalar-2)  input  [overrides]",
        f"BGv03 v03 {bgi}",
        f"BGv03h v03 {bgi} time/cfl_number=0.03125",
        f"BGs2 s2 {bgi}",
        f"M16p s2 {base}",
        f"M16m s2 {base} scalar_field/noise_mode_scale=-1.0",
        f"M16l s2 {base} scalar_field/noise_mode_scale=1.0e-3",
        f"M64p s2 {base} {m64}",
        f"M64m s2 {base} {m64} scalar_field/noise_mode_scale=-1.0",
        f"NC16 s2 {base} scalar_field/noise_pi_sign=-1.0 time/tlim=3.0",
    ]
    with open(os.path.join(a.out, "proc.list"), "w") as fp:
        fp.write("\n".join(lines) + "\n")
    print("tlim", tl, "inputs written to", a.out)


if __name__ == "__main__":
    main()
