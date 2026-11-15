"""Compute estimate for the two test cases of arXiv:2512.14649 on this machine
(DESIGN_REVIEW.md, section 8). Every input carries its locator; the assumptions are
marked [JUDGEMENT] and are the numbers to be replaced by measurements of core's
implementation.

Usage: python3 cost.py <outdir> <d1.json> <d2.json>
"""
import json
import math
import os
import sys

INPUTS = {
    # measured
    "z4c_gpu_zcps": (2.0e7, "docs/TESTLOG.md:46, Z4c uniform 128^3, RK4, nghost 4, one A100"),
    "z4c_cpu_zcps": (1.5e4, "run E-stoch-inf-20261115-122727-a1c2237 (D1), one core"),
    # paper
    "efolds_quad": (8.0, "2512.14649 PRD_v2.tex:420, N_f - N* ~ 8 (quadratic)"),
    "efolds_usr": (10.0, "2512.14649 PRD_v2.tex:420, N_f - N* ~ 10 (inflection)"),
    "sigma": (1.0, "2512.14649 PRD_v2.tex:519"),
    "theta_ic_paper": (0.025, "2502.06783 main_V2PRD.tex:492 (Courant factor of the "
                              "companion initial-condition runs; not stated in 2512.14649)"),
    "theta_athenak": (0.25, "cosmo/TESTLOG.md:18 (step of a quarter cell, production)"),
    # assumptions
    "sf_rhs_overhead": (0.15, "[JUDGEMENT] scalar-field RHS, Tmunu, kick: +15 percent of Z4c"),
    "gpu_fp64_eff": (3.0e12, "[JUDGEMENT] sustained FP64 flop/s of the synthesis on an A100"),
    "flops_per_cmac": (8.0, "complex multiply-add"),
    "fields_per_synthesis": (6, "S_R and five components of k_i k_j S_R / k^2 (review 5.3)"),
}


def steps(N, theta, efolds, sigma=1.0):
    """N_T = N sigma/(2 pi theta) * efolds (2512.14649 PRD_v2.tex:721, H dt = 2 pi theta
    /(N sigma) in cosmic time with L k_sigma* = 2 pi)."""
    return N*sigma/(2.0*math.pi*theta)*efolds


def main(outdir, d1p, d2p):
    v = {k: x[0] for k, x in INPUTS.items()}
    d1 = json.load(open(d1p))
    d2 = json.load(open(d2p))
    ops = {(r["N"], r["block"]): r["cmacs_hermitian"] for r in d2["ops_table"]}
    mem = {(r["N"], r["block"]): r["scalar_field_GB"] for r in d1["extrapolation"]}
    rows = []
    for N in (64, 128, 256):
        b = min(N, 128)
        cells = N**3
        t_z4c = cells/v["z4c_gpu_zcps"]
        t_sf = v["sf_rhs_overhead"]*t_z4c
        t_syn = ops[(N, b)]*v["flops_per_cmac"]*v["fields_per_synthesis"]/v["gpu_fp64_eff"]
        for case, ef in (("quadratic", v["efolds_quad"]), ("inflection", v["efolds_usr"])):
            for theta in (v["theta_athenak"], v["theta_ic_paper"]):
                ns = steps(N, theta, ef)
                for per in ("step", "stage"):
                    nsyn = 1 if per == "step" else 4
                    t_step = t_z4c + t_sf + nsyn*t_syn
                    rows.append(dict(N=N, block=b, case=case, theta=theta, noise_per=per,
                                     steps=round(ns), sec_per_step=t_step,
                                     synthesis_share=nsyn*t_syn/t_step,
                                     card_hours=ns*t_step/3600.0,
                                     memory_GB=mem.get((N, b))))
    # processor alternative for scouting at 64^3 (one core)
    cpu = []
    for case, ef in (("quadratic", v["efolds_quad"]), ("inflection", v["efolds_usr"])):
        ns = steps(64, v["theta_athenak"], ef)
        cpu.append(dict(N=64, case=case, steps=round(ns),
                        core_hours=ns*64**3*(1 + v["sf_rhs_overhead"])
                        / v["z4c_cpu_zcps"]/3600.0))
    res = dict(inputs=INPUTS, rows=rows, cpu=cpu)
    with open(os.path.join(outdir, "cost.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    print(f"{'N':>4} {'case':>10} {'theta':>6} {'noise':>6} {'steps':>7} "
          f"{'s/step':>7} {'syn%':>5} {'card-h':>7} {'GB':>5}")
    for r in rows:
        print(f"{r['N']:>4} {r['case']:>10} {r['theta']:>6} {r['noise_per']:>6} "
              f"{r['steps']:>7} {r['sec_per_step']:>7.3f} {100*r['synthesis_share']:>5.1f} "
              f"{r['card_hours']:>7.3f} {r['memory_GB'] or 0:>5.1f}")
    for c in cpu:
        print(c)


if __name__ == "__main__":
    main(*sys.argv[1:4])
