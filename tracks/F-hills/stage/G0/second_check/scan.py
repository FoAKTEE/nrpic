#!/usr/bin/env python3
"""SC1, SC3, SC4, SC6: phase scans at q = 10 (M = 1, m1 = m2 = 0.05, a0 = 3) with the
integrators of models.py. Usage:
    scan.py <outdir> [nproc] [nphase]
Writes scan.jsonl (one encounter per line) and scan_summary.json."""
import json
import math
import os
import sys
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import models as mdl  # noqa: E402

# label: (model, gamma_ic, r0_rt)
MODELS = {
    "NF4": ("newton_fixed", False, 4.0),     # lead's "Newton, hole fixed"
    "NF20": ("newton_fixed", False, 20.0),
    "NT4": ("newton_full", False, 4.0),      # full three-body (newton3's model)
    "H4": ("hrna", False, 4.0),              # lead's HRNA (2404 data at the NR release radius)
    "HG4": ("hrna", True, 4.0),              # HRNA, Gamma-corrected binary
    "H20": ("hrna", False, 20.0),
    "S4raw": ("hrna_sym", False, 4.0),       # diagnostic: pair factor at the CM, 2404 data
    "S4": ("hrna_sym", True, 4.0),           # diagnostic, Gamma-corrected binary
    "S20": ("hrna_sym", True, 20.0),
}
RPS = [7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 15.0, 17.0]


def one(args):
    label, rp, phase = args
    model, gic, r0 = MODELS[label]
    try:
        r = mdl.run(model, rp, phase, gamma_ic=gic, r0_rt=r0)
    except Exception as exc:  # recorded, never hidden
        return dict(label=label, rp=rp, phase=phase, error=repr(exc))
    r["label"] = label
    return r


def clean(o):
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return None if not math.isfinite(float(o)) else float(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    return o


def main(out, nproc, nph):
    os.makedirs(out, exist_ok=True)
    phases = np.linspace(0.0, 2 * math.pi, nph, endpoint=False)
    jobs = [(lab, rp, float(ph)) for lab in MODELS for rp in RPS for ph in phases]
    rows = []
    with Pool(nproc) as pool, open(os.path.join(out, "scan.jsonl"), "w") as fh:
        for r in pool.imap_unordered(one, jobs, chunksize=8):
            r = clean(r)
            fh.write(json.dumps(r) + "\n")
            rows.append(r)
    summ = {}
    for lab in MODELS:
        summ[lab] = []
        for rp in RPS:
            rr = [r for r in rows if r["label"] == lab and r["rp"] == rp]
            good = [r for r in rr if "error" not in r]
            # superluminal members (point-mass near-collisions under HRNA) are reported, and
            # left out of the fractions
            ok = [r for r in good if r["status"] != "superluminal"]
            sep = np.mean([r["separated"] for r in ok])
            cap = np.mean([any(r["plunged"]) for r in ok])
            grc = np.mean([any(r["gr_capture_criterion"]) for r in ok])
            cmp_ = [r["cm_peri"][1] for r in ok if r.get("cm_peri")]
            summ[lab].append(dict(
                rp=rp, n=len(rr), n_err=len(rr) - len(good),
                n_superluminal=len(good) - len(ok),
                n_nearcollision=sum((r.get("sep_min") or 1.0) < 0.01 for r in ok),
                close_member_encounter=float(np.mean([(r.get("sep_min") or 1.0) < 0.1
                                                      for r in good])),
                n_tmax=sum(r["status"] == "tmax" for r in ok),
                separated=float(sep), captured=float(cap), gr_criterion_any=float(grc),
                single_ejection=float(np.mean([r["outcome"] in (1, 2) for r in ok])),
                survived=float(np.mean([r["outcome"] == 0 for r in ok])),
                cm_peri_median=float(np.median(cmp_)) if cmp_ else None,
                cm_peri_p16=float(np.percentile(cmp_, 16)) if cmp_ else None,
                cm_peri_p84=float(np.percentile(cmp_, 84)) if cmp_ else None,
                member_below_4M=float(np.mean([min(r["rmin"]) < 4.0 for r in ok])),
                dL_cm_to_2rt_median=float(np.median([r["cm_EL_2rt"][1] - r["cm_EL_release"][1]
                                                     for r in ok if r.get("cm_EL_2rt")]))))
            s = summ[lab][-1]
            print(f"{lab:6s} rp={rp:5.1f} sep={s['separated']:.3f} cap={s['captured']:.3f} "
                  f"grc={s['gr_criterion_any']:.3f} cm_peri={s['cm_peri_median']} "
                  f"tmax={s['n_tmax']} err={s['n_err']}", flush=True)
    json.dump(dict(phases=phases.tolist(), rps=RPS, models={k: list(v) for k, v in MODELS.items()},
                   summary=summ), open(os.path.join(out, "scan_summary.json"), "w"), indent=1)


if __name__ == "__main__":
    a = sys.argv[1:]
    out = a[0] if a else os.environ["NRPIC_RUN_DIR"]
    nproc = int(a[1]) if len(a) > 1 else int(os.environ.get("NRPIC_CORES", "12"))
    nph = int(a[2]) if len(a) > 2 else 180
    main(out, nproc, nph)
