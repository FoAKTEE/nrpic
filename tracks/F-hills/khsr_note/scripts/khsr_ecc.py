#!/usr/bin/env python3
"""KHSR (Kobayashi, Hainick, Sari & Rossi, arXiv:1201.4794) Sec. 6.2 / Fig. 4 with newton3.

The ejection of a member of a circular coplanar binary (M/m = 1e6, m1/m2 = 3, KHSR
ms.tex:752) whose centre of mass approaches the heavy mass on an elliptic orbit of semi-major
axis r_a (KHSR's set r_a/r_t = 500, 200, 130, 100 and the parabola, ms.tex:1145-1147):

  direct      the full Newtonian three-body driver of newton3 (hills3.threebody.scatter,
              unchanged) on the elliptic orbit, e = 1 - D r_t / r_a, 512 effective phases
              in [0, 2 pi), start 10 r_t, end 30 r_t outbound
  parabolic   KHSR's parabolic approximation (eq. Eipara, ms.tex:364-369; ms.tex:586-591):
              the parabolic energy changes dE(phi), shifted by the initial member energies
              I_i = (m_i/m) E_bar (ms.tex:258, 320); m1 is ejected when I_1 - dE > 0, m2 when
              I_2 + dE > 0. dE from (a) newton3's restricted parabolic problem on a dense D
              grid (2000 phases in [0, pi) and the symmetry dE(phi + pi) = -dE(phi),
              ms.tex:291-297) and (b) the direct parabolic runs at the same 512 phases.

Also K1 (E_bar against r_a, ms.tex:746-749) and K2 (start radii with equal times to the
pericentre, ms.tex:624-626). Predictions: tracks/F-hills/khsr_note/JOURNAL.md, entry K.
Energies in units of (G m1 m2 / a)(M/m)^(1/3).

Run (registered): harness/bin/nrpic-run submit --kind scouting --gate G1 --package
tracks/F-hills/khsr_note --cores 4 --purpose "..." -- .venv/bin/python
tracks/F-hills/khsr_note/scripts/khsr_ecc.py --workers 4
Output: $NRPIC_RUN_DIR (or --out): khsr_ecc.json, khsr_samples.npz, log lines on stdout.
"""
import argparse
import json
import os
import sys
import time

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"
import numpy as np
from multiprocessing import Pool
from scipy.optimize import brentq

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "tracks", "F-hills", "newton3"))
from hills3 import threebody as T  # noqa: E402
from hills3 import restricted as R  # noqa: E402
from hills3.orbits import conic_time_from_pericentre  # noqa: E402

MM = 1.0e6                       # M/m (ms.tex:752)
M1, M2 = 0.75, 0.25              # m1/m2 = 3, m = 1 (ms.tex:752)
RA = [np.inf, 500.0, 200.0, 130.0, 100.0]       # r_a/r_t (ms.tex:1145-1147)
D_DIRECT = {"pro": [0.1, 0.3, 0.5, 1.0, 1.5, 2.0], "ret": [0.1, 0.2, 0.3]}
D_LINES = {"pro": list(np.round(np.linspace(0.05, 2.15, 43), 4)),
           "ret": list(np.round(np.linspace(0.025, 0.425, 17), 4))}
SENSE = {"pro": (np.pi / 2, np.pi / 2), "ret": (np.pi / 2, -np.pi / 2)}
NPH = 512
NPH_LINES = 2000
DIS = (T.EJECT1, T.EJECT2, T.BOTHBOUND, T.BOTHFREE)


def ebar(ra):
    """KHSR's E_bar of the centre-of-mass orbit: E = -G M m / (2 r_a) in units of
    (G m1 m2/a)(M/m)^(1/3), with a = r_t (m/M)^(1/3); m = 1."""
    if not np.isfinite(ra):
        return 0.0
    return -0.5 * MM ** (1.0 / 3.0) / (M1 * M2) / ra


def parabolic_approx(dE, dis, eb):
    """KHSR's parabolic approximation from samples dE (energy change of m2, uniform in phase
    over [0, 2 pi)) and the disruption mask, for the orbital energy eb (units)."""
    I1, I2 = M1 * eb, M2 * eb
    e1 = dis & (I1 - dE > 0)       # m1 leaves with E1 = I1 - dE
    e2 = dis & (I2 + dE > 0)       # m2 leaves with E2 = I2 + dE
    both = e1 & e2                 # only for eb > 0; not in the cases here
    eej = np.concatenate([(I1 - dE)[e1], (I2 + dE)[e2]])
    return dict(P1=float(e1.mean()), P2=float(e2.mean()), Pej=float((e1 | e2).mean()),
                Pboth=float(both.mean()), Pdis=float(dis.mean()),
                Eej=float(eej.mean()) if eej.size else float("nan"),
                n1=int(e1.sum()), n2=int(e2.sum()),
                mean_abs_dE=float(np.abs(dE[dis]).mean()) if dis.any() else float("nan"))


def direct_task(args):
    sense, D, ra = args
    th, vp = SENSE[sense]
    e = 1.0 if not np.isfinite(ra) else 1.0 - D / ra
    ph = np.linspace(0.0, 2 * np.pi, NPH, endpoint=False)
    ss = [T.HillsSetup(M=MM, m1=M1, m2=M2, a=1.0, D=D, e_orb=e, theta=th, varphi=vp, phase=p)
          for p in ph]
    t0 = time.time()
    o = T.scatter(ss, k0=10.0, k_end=30.0)
    # orbital energy of the start state (K1): E_orb of the binary's centre of mass about M
    P = T._stack(ss[:1])
    x, v, _ = T.initial_state_arrays(P, 10.0 * P["r_t"])
    en0 = T.member_energies(x, v, np.array([[MM, M1, M2]]))
    unit = ss[0].energy_unit
    keep = {k: np.asarray(o[k]) for k in ("outcome", "dE", "E1", "E2", "r12min", "energy_error",
                                          "ok", "inner")}
    keep["E_orb0"] = float(en0["E_orb"][0] / unit)
    keep["e_orb"] = e
    keep["wall"] = time.time() - t0
    return args, keep


def lines_task(args):
    sense, D = args
    th, vp = SENSE[sense]
    ph = np.linspace(0.0, np.pi, NPH_LINES, endpoint=False)
    o = R.run(D, th, vp, ph, k0=10.0, k_end=30.0)
    amb = o["ambiguous"] & o["ok"]
    if amb.any():   # as newton3 compare_full.restricted: wide pairs followed to 300 r_t
        o2 = R.run(D, th, vp, ph[amb], k0=10.0, k_end=300.0)
        for k in ("E2", "disrupted", "survived", "ambiguous", "ok"):
            o[k][amb] = o2[k]
    return args, {k: np.asarray(o[k]) for k in ("E2", "disrupted", "ok", "ambiguous")}


def k2_radii():
    """Start radii on conics with D = 1 (r_p = r_t; units r_t, G M = 1, tides neglected as
    KHSR say) whose time to pericentre equals the parabola's from 15 r_t (ms.tex:624-626)."""
    tp = float(conic_time_from_pericentre(1.0, 1.0, 1.0, 15.0))
    out = {"t_parabola_15": tp}
    for e, hi in ((0.9, 1.9 / 0.1 - 1e-9), (1.1, 200.0)):
        f = lambda r: float(conic_time_from_pericentre(1.0, e, 1.0, r)) - tp  # noqa: E731
        out[f"r0_e{e}"] = brentq(f, 1.0 + 1e-9, hi, xtol=1e-12)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", ""))
    ap.add_argument("--quick", action="store_true", help="development check: 16 phases, 2 cases")
    a = ap.parse_args()
    if not a.out:
        sys.exit("give --out or run under nrpic-run")
    os.makedirs(a.out, exist_ok=True)
    global NPH, NPH_LINES
    t_start = time.time()
    jobs_d = [(s, D, ra) for s in ("pro", "ret") for D in D_DIRECT[s] for ra in RA]
    jobs_l = [(s, D) for s in ("pro", "ret") for D in D_LINES[s]]
    if a.quick:
        NPH, NPH_LINES = 16, 32
        jobs_d = [("pro", 1.0, np.inf), ("pro", 1.0, 100.0)]
        jobs_l = [("pro", 1.0)]
    summary = {"source": "KHSR arXiv:1201.4794 v1 ms.tex (kb-data/raw/arxiv/1201.4794/v1/src)",
               "M_over_m": MM, "m1": M1, "m2": M2, "r_a_over_r_t": [str(r) for r in RA],
               "n_phase_direct": NPH, "n_phase_lines": NPH_LINES, "k0": 10.0, "k_end": 30.0}
    # K1 closed form
    summary["K1"] = {"E_bar_coefficient_at_ra100": ebar(100.0),
                     "KHSR_printed": -2.7, "locator": "ms.tex:746-749"}
    # K2 Kepler times
    summary["K2"] = dict(k2_radii(), KHSR_printed={"e0.9": 12.2, "e1.1": 17.4},
                         locator="ms.tex:624-626")
    print("K1", summary["K1"], flush=True)
    print("K2", summary["K2"], flush=True)
    with Pool(a.workers) as pool:
        res_l = dict(pool.map(lines_task, jobs_l))
        print(f"lines done {time.time() - t_start:.0f} s", flush=True)
        res_d = {}
        for args, r in pool.imap_unordered(direct_task, jobs_d):
            res_d[args] = r
            print(f"direct {args} e={r['e_orb']:.6f} wall {r['wall']:.1f} s "
                  f"fail {int((~r['ok']).sum())}", flush=True)
    # parabolic approximation lines (restricted, symmetric extension to [0, 2 pi))
    lines = {}
    for (s, D), r in res_l.items():
        dE = np.concatenate([r["E2"], -r["E2"]])
        dis = np.concatenate([r["disrupted"], r["disrupted"]]) & np.concatenate([r["ok"], r["ok"]])
        for ra in RA:
            lines.setdefault(s, {}).setdefault(str(ra), []).append(
                dict(D=float(D), **parabolic_approx(dE, dis, ebar(ra))))
    summary["lines"] = lines
    # direct runs and the parabolic approximation from the direct parabolic runs
    points = {}
    npz = {}
    for (s, D, ra), r in sorted(res_d.items(), key=lambda kv: (kv[0][0], kv[0][1], -kv[0][2])):
        # samples whose integration failed (integrate_many ok = False: step size underflow
        # in a near-collision of the members) are left out of every statistic; their number
        # is n_fail (first run F-20261121-212049-d91381f kept them: outliers in E and dE)
        ok = np.asarray(r["ok"], dtype=bool)
        oc = r["outcome"][ok]
        ej1, ej2 = oc == T.EJECT1, oc == T.EJECT2
        eej = np.concatenate([r["E1"][ok][ej1], r["E2"][ok][ej2]])
        dis = np.isin(oc, DIS)
        par = res_d[(s, D, np.inf)]
        pok = np.asarray(par["ok"], dtype=bool)
        par_dis = np.isin(par["outcome"][pok], DIS)
        pa = parabolic_approx(np.where(par_dis, par["dE"][pok], 0.0), par_dis, ebar(ra))
        row = dict(D=D, r_a=str(ra), e_orb=r["e_orb"], E_bar=ebar(ra), E_orb0=r["E_orb0"],
                   P1=float(ej1.mean()), P2=float(ej2.mean()), Pej=float((ej1 | ej2).mean()),
                   Pdis=float(dis.mean()), Pboth_bound=float((oc == T.BOTHBOUND).mean()),
                   Pboth_free=float((oc == T.BOTHFREE).mean()),
                   Psurv=float((oc == T.SURVIVED).mean()), Punsettled=float((oc == T.UNSETTLED).mean()),
                   n1=int(ej1.sum()), n2=int(ej2.sum()),
                   Eej=float(eej.mean()) if eej.size else float("nan"),
                   mean_abs_dE=float(np.abs(r["dE"][ok][dis]).mean()) if dis.any() else float("nan"),
                   max_energy_error=float(np.nanmax(np.abs(r["energy_error"][ok]))),
                   n_fail=int((~r["ok"]).sum()), wall_s=r["wall"],
                   parabolic_from_direct=pa)
        points.setdefault(s, []).append(row)
        tag = f"{s}_D{D}_ra{ra}"
        for k in ("outcome", "dE", "E1", "E2", "r12min", "energy_error", "inner", "ok"):
            npz[f"{tag}_{k}"] = r[k]
    summary["direct"] = points
    summary["wall_total_s"] = time.time() - t_start
    with open(os.path.join(a.out, "khsr_ecc.json"), "w") as fh:
        json.dump(summary, fh, indent=1)
    np.savez_compressed(os.path.join(a.out, "khsr_samples.npz"), **npz)
    print(f"done {summary['wall_total_s']:.0f} s", flush=True)


if __name__ == "__main__":
    main()
