#!/usr/bin/env python3
"""Offline checks of the models built by make_models.py (JOURNAL.md, predictions M1-M3).

    python3 check_models.py --ic BUILD_DIR --N N [--out DIR] [--seed 1]
                            [--king-reference DIR_OF_RUN_C-sidm-20261115-120610-b4592be]

M3: every per-model check of tracks/C-sidm/equilibria/check_equilibria.check_model
    (matching, TOV, Hamiltonian constraint of the table, rest mass, file round trip, table
    monopole, stratified ECDFs, equal-mass shell counts, invariants E <= E0, shell moments
    of two samplers, KS tests, particle form of the constraint), run unchanged with the
    module references ev -> evstatic_b and models -> model_set rebound.
M2: for the F21 family, Z(0), eps, R/M and M0/M of evstatic_b against
    tracks/C-sidm/gravothermal/tmb.solve at w0 = (1 - e^{-y0})/b, and the E_b maximum
    against the gravothermal criteria (criteria.json of run C-sidm-20261115-120722-38ab057).
M1: with --king-reference, sha256 of the King .nrp and .tab files against that run.

Writes DIR/checks.json (every number, pass flags, list of failures) and DIR/figdata.npz;
exit 1 when an enforced check fails.
"""

import argparse
import hashlib
import json
import math
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "equilibria"))
sys.path.insert(2, os.path.join(HERE, "..", "gravothermal"))

import numpy as np  # noqa: E402

import evstatic_b as evb  # noqa: E402
import model_set as ms  # noqa: E402
import check_equilibria as ce  # noqa: E402  (equilibria's checks)
import tmb  # noqa: E402

ce.ev = evb
ce.models = ms


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def check_f21(spec, crit):
    fam = ms.FAMILIES[spec["family"]]
    d = evb.integrate(fam, spec["y0"])
    w0 = ms.w0_of_y0(spec["y0"], fam.b)
    e = tmb.solve(fam.b, w0)
    pairs = dict(Z0=(d["Zc_infinity"], e["Z0"]), eps=(d["Eb"], e["eps"]),
                 R_over_M=(d["R"] / d["M"], e["R"] / e["E"]),
                 M0_over_M=(d["N"] / d["M"], e["Erest"] / e["E"]))
    rel = {k: abs(a / b - 1) for k, (a, b) in pairs.items()}
    worst = max(rel.values())
    ce.record(f"model {spec['tag']}", "F21 solver tmb.solve: max rel. diff of Z0, eps, R/M, M0/M",
              f"{worst:.1e}", ok=worst < 1e-8, w0=w0,
              values={k: dict(evstatic_b=a, tmb=b, rel=rel[k]) for k, (a, b) in pairs.items()})


def check_threshold(crit):
    ym, ebm = ms.threshold("tmb01")
    d = evb.integrate(ms.FAMILIES["tmb01"], ym)
    ref = crit["0.1"]["max_eps"]
    dz = d["Zc_infinity"] - ref["Z0"]
    ce.record("tmb01 E_b maximum", "Z0 against criteria.json max_eps", f"{d['Zc_infinity']:.8f}",
              ok=abs(dz) < 1e-6, reference=ref["Z0"], deviation=dz, y_max=ym,
              w0=ms.w0_of_y0(ym), w0_reference=ref["w0"], Eb_max=ebm, eps_reference=ref["eps"],
              locator="tracks/C-sidm/gravothermal/results/criteria.json (run "
                      "C-sidm-20261115-120722-38ab057)")
    ys = np.linspace(0.30, 0.56, 53)
    seq = [evb.integrate(ms.FAMILIES["tmb01"], v) for v in ys]
    ce.FIG["tmb01_seq_y0"] = ys
    ce.FIG["tmb01_seq_Z0"] = np.array([s["Zc_infinity"] for s in seq])
    ce.FIG["tmb01_seq_Eb"] = np.array([s["Eb"] for s in seq])
    ce.FIG["tmb01_seq_RM"] = np.array([s["R"] / s["M"] for s in seq])


def check_king_regression(ic, ref, N, seed):
    out = {}
    for spec in ms.king_specs():
        stem = f"{spec['tag']}_stratified_N{N}_s{seed}"
        for ext in ("nrp", "tab"):
            a, b = os.path.join(ic, f"{stem}.{ext}"), os.path.join(ref, f"{stem}.{ext}")
            same = os.path.exists(b) and sha256(a) == sha256(b)
            out[f"{stem}.{ext}"] = same
            ce.record("king regression", f"{stem}.{ext} byte-identical to the reference",
                      same, ok=same, reference=b)
    return out


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ic", required=True)
    p.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    p.add_argument("--N", type=int, required=True)
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--king-reference", default=None)
    p.add_argument("--criteria", default=os.path.join(HERE, "..", "gravothermal", "results",
                                                      "criteria.json"))
    p.add_argument("--only", nargs="*", default=None)
    a = p.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    crit = json.load(open(a.criteria))
    check_threshold(crit)
    if a.king_reference:
        check_king_regression(a.ic, a.king_reference, a.N, a.seed)
    specs = [s for s in ms.model_set()
             if not a.only or s["tag"] in a.only or s["family"] in a.only]
    for spec in specs:
        if spec["family"] == "tmb01":
            check_f21(spec, crit)
        ce.check_model(spec, a.ic, a.N, a.seed)
        meta = json.load(open(os.path.join(a.ic, f"{spec['tag']}_stratified_N{a.N}_s{a.seed}.json")))
        ce.RES[f"model {spec['tag']}"]["summary"] = dict(
            Zc=meta["Zc_infinity"], Eb=meta["Eb_over_M0"], R=meta["R_areal"],
            rbar_s=meta["rbar_s"], alpha_c=meta["alpha_c"],
            sum_m_W_over_psi_rel=meta["table_constraint"]["rel_diff"],
            centre_resolution=meta.get("centre_resolution"))
    ce.RES["model_set"] = specs
    ce.RES["N"] = a.N
    ce.RES["ic"] = a.ic
    fails = [(g, n) for g, d in ce.RES.items() if isinstance(d, dict)
             for n, v in d.items() if isinstance(v, dict) and v.get("pass") is False]
    npass = sum(1 for g, d in ce.RES.items() if isinstance(d, dict)
                for n, v in d.items() if isinstance(v, dict) and v.get("pass") is True)
    ce.RES["failures"] = fails
    ce.RES["passes"] = npass
    with open(os.path.join(a.out, "checks.json"), "w") as f:
        json.dump(ce.RES, f, indent=1, default=float)
    np.savez_compressed(os.path.join(a.out, "figdata.npz"), **ce.FIG)
    print(f"{npass} passed, {len(fails)} failed: {fails}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
