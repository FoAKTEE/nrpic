#!/usr/bin/env python3
"""Prepares the card runs of package scalar2 in DIR: mode files, the inputs of Track E's
noise unit test (full base case, 64^3 x 300) and DIR/runs.list, one run per line,
    <name> <-i | -r> <input or restart file> [athena arguments...]
which tracks/core/analysis/scalar2/card_job.sh executes inside one Slurm job.

    python3 card_prepare.py --out DIR --u2 <processor U2 input of the scaled base case>
                            --etree <root of a copy of track/E-stoch-inf>

Runs: card32 (T4: the 32^3 case, 20 steps); lad<N>_<p1|m1> (T3d: ladder N = 32, 64, 128
with nmax2 = 64, mode functions scaled by +-1, to t = 3.2); u9 (U2 of the scaled base
case); uf_U1 ... uf_U8 and uf_U4 (full base case of NOISE_SPEC 9); cost128_*, cost256_*
(cost of a step with the sources and with the constraint record; mode functions from
the Bunch-Davies form at N*, which is enough for a cost measurement)."""
import argparse
import os
import sys

import common
from common import inf, np

INP = os.path.join(common.PROB, "sr_stochastic.athinput")
MODES = os.path.join(common.PROB, "sr_stochastic_modes.txt")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--u2", required=True)
    ap.add_argument("--etree", required=True)
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    lines = []
    mf = f"scalar_field/noise_mode_file={MODES}"
    quiet = ["scalar_field/dump_noise=false"]

    lines.append(f"card32 -i {INP} {mf} time/nlim=20 scalar_field/dump_dt=0.49 "
                 + " ".join(quiet))
    for n in (32, 64, 128):
        for tag, s in (("p1", 1.0), ("m1", -1.0)):
            lines.append(f"lad{n}_{tag} -i {INP} {mf} time/tlim=3.2 "
                         f"scalar_field/dump_dt=0.4 scalar_field/dump_metric=false "
                         f"scalar_field/noise_mode_scale={s} "
                         + " ".join(quiet + common.mesh_args(n)))

    # Track E's unit test: U2 of the scaled base case, and the full base case
    lines.append(f"u9 -i {os.path.abspath(a.u2)}")
    lead = os.path.join(a.etree, "tracks", "E-stoch-inf", "analysis", "lead")
    sys.path.insert(0, lead)
    import u_runs
    base = open(os.path.join(lead, "inputs", "u_base.athinput")).read()
    var = u_runs.variants(64, 0.25, 64)
    for name, ch in var.items():
        d = os.path.join(out, "uf_" + name)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "u.athinput"), "w") as fp:
            fp.write(u_runs.edit_input(base, dict(ch)))
        lines.append(f"uf_{name} -i {os.path.join(d, 'u.athinput')}")
    lines.append(f"uf_U4 -r {os.path.join(out, 'uf_U2', 'rst', 'u.00001.rst')}")

    # cost runs: mode functions of every shell up to nmax2 = 4096 from the Bunch-Davies
    # form at N* (not the integrated mode functions)
    model = inf.quadratic_model()
    bg = inf.Background(model)
    hs = bg.h_star
    n2 = inf.shells(4096)
    r, d = inf.bunch_davies(bg, np.sqrt(n2.astype(float))*hs, bg.n_star)
    cm = os.path.join(out, "modes_cost.txt")
    inf.write_mode_file(cm, n2, r*hs**1.5, d*hs**1.5,
                        header="cost runs only: Bunch-Davies form at N*")
    cf = f"scalar_field/noise_mode_file={cm}"
    off = "scalar_field/dump_dt=-1.0"
    nok = ("scalar_field/noise_kick_pi=false scalar_field/noise_kick_k=false "
           "scalar_field/noise_kick_a=false")
    for n, nmax2, nlim in ((128, 1024, 20), (256, 4096, 10)):
        m = " ".join(common.mesh_args(n))
        common_args = f"-i {INP} {cf} {off} time/nlim={nlim} scalar_field/noise_nmax2={nmax2} {m}"
        lines.append(f"cost{n}_con {common_args}")
        lines.append(f"cost{n}_src {common_args} scalar_field/con_dcycle=0")
        lines.append(f"cost{n}_nokick {common_args} scalar_field/con_dcycle=0 {nok}")
    lines.append("cost256_b8 " + f"-i {INP} {cf} {off} time/nlim=10 "
                 "scalar_field/noise_nmax2=4096 scalar_field/con_dcycle=0 "
                 + " ".join(common.mesh_args(256, 128)))
    with open(os.path.join(out, "runs.list"), "w") as fp:
        fp.write("\n".join(lines) + "\n")
    print(len(lines), "runs in", os.path.join(out, "runs.list"))


if __name__ == "__main__":
    main()
