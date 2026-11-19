#!/usr/bin/env python3
"""Phase scans of the Hills encounters of the plan with the three references, from the SAME
coordinate start state (predictions: ../JOURNAL.md entry 4).

Start state: newton3's `initial_state_arrays` (binary centre of mass on the Newtonian
parabola about M + m at r0 = 4 r_t, barycentric positions and velocities, circular binary,
effective phase phi), i.e. the construction of the NR inputs of three_punctures and nr_first
(without the integration from 10 r_t). From it:
  newton  full Newtonian three-body problem (newton3.threebody.scatter), end when the
          Newtonian conic is at 30 r_t outbound
  eih     the EIH equations (eih.scatter), same end, the start velocities read as EIH
          coordinate velocities (as the other baselines read them); stopped when a member comes
          closer to M than 2 M (harmonic) -> outcome 6 (EIH turns every parabolic orbit around
          beyond 2.7 M, T4, so this is a safeguard), or when the members come closer than
          2 (m1 + m2) -> outcome 7. EIH has no capture: the analysis applies the GR-capture
          proxy rMmin < 5.35 M (T4) and the trust radius 12 M afterwards.
  eihp    the same with newton3's momenta m v read as canonical 1PN momenta (the reading of
          the Bowen-York momenta of the NR inputs; JOURNAL entry 6)
  hrna    geodesic_binary/hrna.py (2404.16270 Eq. CoordtEqs, Schwarzschild, hole fixed) from
          the same positions and velocities relative to M (as lead check V6a and nr_first E6);
          stops as hrna.run_encounter (CM beyond 30 r_t, or bound CM turning beyond 10 r_t);
          outcome 6 = a member crossed 2.5 M inwards
Outcome codes of newton3: 0 survived, 1 m2 ejected (m1 bound), 2 m1 ejected, 3 both bound,
4 both free, 5 unsettled; 6 captured (eih, hrna), 7 members merged (eih).
Configurations of the plan (three_punctures/PLAN.md section 3, nr_first P1): q = 10: M = 1,
m1 = m2 = 0.05, a = 3 (r_p line 7 ... 17 M); q = 4: m1 = m2 = 0.125, a = 5 (r_p line 9.82 ...
16 M); coplanar prograde and retrograde; nphase effective phases in [0, 2 pi).
Needs numba (python of scratch/F-hills/venv-gb). Usage:
  scan.py [--nphase 360] [--workers 14] [--models newton,eih,hrna] [--only q10|q4] [outdir]
"""
import argparse
import json
import math
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
TRK = os.path.dirname(PKG)
sys.path.insert(0, PKG)
sys.path.insert(0, os.path.join(TRK, "geodesic_binary"))
import eih  # noqa: E402
from hills3 import threebody as tb  # noqa: E402

CONFIGS = {
    "q10": dict(M=1.0, m1=0.05, m2=0.05, a=3.0, rps=[7, 8, 9, 10, 11, 12, 13, 15, 17]),
    "q4": dict(M=1.0, m1=0.125, m2=0.125, a=5.0, rps=[9.82, 11, 12, 13, 14, 16]),
}
R_STOP = 2.0         # eih stop (harmonic); EIH turns every parabolic orbit around at >= 2.7 M
R_TRUST = 12.0       # T4: below about 12 M the 1PN differential deflection is off by > 50 %
R_GRCAP = 5.35       # T4: EIH pericentre of the L = 4 M parabola (GR captures every L < 4 M)


def setups(cfg, rp, sense, nphase):
    ph = 2 * np.pi * np.arange(nphase) / nphase
    return [tb.HillsSetup(M=cfg["M"], m1=cfg["m1"], m2=cfg["m2"], a=cfg["a"], rp=rp,
                          phase=p, theta=np.pi / 2,
                          varphi=(np.pi / 2 if sense > 0 else -np.pi / 2)) for p in ph]


def run_newton(cfg, rp, sense, nphase):
    ss = setups(cfg, rp, sense, nphase)
    r = tb.scatter(ss, k0=4.0, k_end=30.0)
    en = r["_en"]
    masses = np.array([[cfg["M"], cfg["m1"], cfg["m2"]]] * nphase)
    vinf = eih.vinf_out(r, masses)
    return dict(outcome=r["outcome"], E1=r["E1"], E2=r["E2"], E_out=r["E_out"], vinf=vinf,
                rMmin=r["rMmin"].min(axis=1), r12min=r["r12min"] * cfg["a"],
                inner=en["inner"], energy_error=r["energy_error"])


def run_eih(cfg, rp, sense, nphase, reading="velocity"):
    ss = setups(cfg, rp, sense, nphase)
    r = eih.scatter(ss, k0=4.0, k_end=30.0, r_trust=R_TRUST, r_stop=R_STOP, reading=reading)
    out = r["outcome"].copy()
    stopped = (r["flag"] & eih.FLAG_STOPPED) > 0
    deep = r["rMmin"].min(axis=1) < R_STOP * cfg["M"] * (1 + 1e-9)
    merged = r["r12min"] < 2 * (cfg["m1"] + cfg["m2"])
    out[stopped & deep] = 6
    out[stopped & merged & ~deep] = 7
    return dict(outcome=out, E1=r["E1"], E2=r["E2"], E_out=r["E_out"], vinf=r["vinf"],
                rMmin=r["rMmin"].min(axis=1), rM1=r["rMmin"][:, 0], rM2=r["rMmin"][:, 1],
                r12min=r["r12min"], inner=r["_en"]["inner"], flag=r["flag"],
                E1PN_err=r["E1PN_err"], dE1PN_u=r["dE1PN_u"], EN_err=r["EN_err"],
                P1PN_err=r["P1PN_err"], J1PN_err=r["J1PN_err"], ok=r["ok"])


def run_eihp(cfg, rp, sense, nphase):
    return run_eih(cfg, rp, sense, nphase, reading="canonical")


def run_hrna(cfg, rp, sense, nphase):
    import hrna
    if hrna._WK is None:
        hrna._WK = hrna._work()
    ss = setups(cfg, rp, sense, nphase)
    P = tb._stack(ss)
    rt = float(P["r_t"][0])
    x, v, t0 = tb.initial_state_arrays(P, 4.0 * rt)
    m1, m2, a0 = cfg["m1"], cfg["m2"], cfg["a"]
    T0 = 2 * math.pi * math.sqrt(a0 ** 3 / (m1 + m2))
    keys = ("outcome", "E1_u", "E2_u", "vinf_exact", "plunged", "r_peri", "status", "Eb_end")
    res = {k: np.zeros(nphase) for k in keys}
    for i in range(nphase):
        y0 = np.concatenate([x[i, 1] - x[i, 0], v[i, 1] - v[i, 0], x[i, 2] - x[i, 0],
                             v[i, 2] - v[i, 0]])
        status, t, y, diag, rec_t, rec_y, nrec, nsteps, nrej = hrna.integrate(
            hrna.LAW_HRNA, hrna.COORDS_SCH, hrna.PAIR_GRAVITY, cfg["M"], 0.0, m1, m2, 0.0, 0.0,
            y0, T0 / 200.0, 1e-12, 1e-14, 30.0 * rt, 10.0 * rt, 2.5, 3000.0, 20_000_000, a0, 0,
            hrna._A, hrna._B, hrna._C, hrna._E3, hrna._E5, hrna._WK)
        s = hrna.summarize(hrna.LAW_HRNA, hrna.COORDS_SCH, cfg["M"], 0.0, m1, m2, a0, y, diag, T0)
        s["status"] = status
        for k in keys:
            res[k][i] = s[k]
    res["outcome"] = res["outcome"].astype(int)
    return res


def task(args):
    model, qname, rp, sense, nphase = args
    cfg = CONFIGS[qname]
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    t = time.time()
    fn = dict(newton=run_newton, eih=run_eih, eihp=run_eihp, hrna=run_hrna)[model]
    res = fn(cfg, rp, sense, nphase)
    res["wall"] = time.time() - t
    return (model, qname, rp, sense), res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("outdir", nargs="?", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--nphase", type=int, default=360)
    ap.add_argument("--workers", type=int, default=14)
    ap.add_argument("--models", default="newton,eih,eihp,hrna")
    ap.add_argument("--only", default=None)
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    tasks = []
    for qname, cfg in CONFIGS.items():
        if a.only and qname != a.only:
            continue
        for rp in cfg["rps"]:
            for sense in (1, -1):
                for model in a.models.split(","):
                    tasks.append((model, qname, rp, sense, a.nphase))
    # the eih tasks are the slowest: start them first
    order = {"eih": 0, "eihp": 0, "hrna": 1, "newton": 2}
    tasks.sort(key=lambda t: (order[t[0]], -t[2]))
    results = {}
    t0 = time.time()
    with Pool(a.workers) as pool:
        for key, res in pool.imap_unordered(task, tasks):
            results[key] = res
            print(f"{time.time() - t0:8.1f}s done {key} wall {res['wall']:.1f}s", flush=True)
    arrays = {}
    for (model, qname, rp, sense), res in results.items():
        tag = f"{model}|{qname}|{rp}|{sense}"
        for k, v in res.items():
            if isinstance(v, np.ndarray):
                arrays[f"{tag}|{k}"] = v
    np.savez_compressed(os.path.join(a.outdir, "scan.npz"), **arrays)
    with open(os.path.join(a.outdir, "scan_meta.json"), "w") as fh:
        json.dump(dict(configs=CONFIGS, nphase=a.nphase, models=a.models, r_stop=R_STOP,
                       r_trust=R_TRUST, r_grcap=R_GRCAP,
                       walls={"|".join(map(str, k)): r["wall"] for k, r in results.items()}),
                  fh, indent=1)
    print(f"total {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
