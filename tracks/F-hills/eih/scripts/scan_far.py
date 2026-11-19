#!/usr/bin/env python3
"""Far-release EIH line (predictions: ../JOURNAL.md entry 8, F1-F4).

  eihfar     EIH from 40 r_t: circular binary (release phase, 2404 convention; --binary 1pn:
             the circular speed of the isolated EIH binary, default; newton: Newtonian), its
             centre of mass on the 1PN parabola with J/mu = L of the GR parabola with areal
             pericentre r_p (2404.16270 appendix.tex l. 175) (eih.far_states); end when the
             Newtonian parabola with the same L is at 30 r_t outbound
  newtonfar  newton3 (full Newton) from 40 r_t on its own parabola with pericentre r_p
             (effective phases), end at 30 r_t outbound
  hrna2404   geodesic_binary/hrna.py with 2404's initial data at 4 r_t (SC1's H4 set-up),
             end at 30 r_t; outcome 6 = a member crossed 2.5 M
Configurations as scan.py. Needs numba (venv-gb).
Usage: scan_far.py [--nphase 360] [--workers 13] [--k0 40] [outdir]
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
from hills3.orbits import conic_time_from_pericentre  # noqa: E402
import importlib.util  # noqa: E402
_spec = importlib.util.spec_from_file_location("eih_scan", os.path.join(HERE, "scan.py"))
_scan = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_scan)
CONFIGS, setups = _scan.CONFIGS, _scan.setups

K0 = 40.0
BINARY = "1pn"      # the binary's internal circular speed: '1pn' (default) or 'newton'


def L_gr(rp, M=1.0):
    return math.sqrt(2.0 * M * rp * rp / (rp - 2.0 * M))


def run_eihfar(cfg, rp, sense, nphase):
    M, m1, m2, a0 = cfg["M"], cfg["m1"], cfg["m2"], cfg["a"]
    mb = m1 + m2
    rt = a0 * (M / mb) ** (1 / 3)
    r0 = K0 * rt
    J = L_gr(rp, M)
    ph = 2 * np.pi * np.arange(nphase) / nphase
    x, v = eih.far_states(M, m1, m2, a0, J, r0, ph, sense, binary=BINARY)
    Mt = M + mb
    rpN = J * J / (2 * Mt)
    t_in = conic_time_from_pericentre(np.array([rpN]), np.array([1.0]), np.array([Mt]),
                                      np.array([r0]))[0]
    t_out = conic_time_from_pericentre(np.array([rpN]), np.array([1.0]), np.array([Mt]),
                                       np.array([30 * rt]))[0]
    masses = np.array([[M, m1, m2]] * nphase)
    T0 = 2 * math.pi * math.sqrt(a0 ** 3 / mb)
    r = eih.evolve_states(masses, x, v, np.zeros(nphase), np.full(nphase, t_in + t_out),
                          rtol=1e-11, h_scale=np.full(nphase, T0), r_trust=12.0, r_stop=2.0)
    unit = m1 * m2 / a0 * (M / mb) ** (1 / 3)
    out = r["outcome"].copy()
    deep = r["rMmin"].min(axis=1) < 2.0 * (1 + 1e-9)
    out[((r["flag"] & eih.FLAG_STOPPED) > 0) & deep] = 6
    en = r["_en"]
    return dict(outcome=out, E_out=en["E_out"] / unit, E_in=en["E_in"] / unit,
                rMmin=r["rMmin"].min(axis=1), r12min=r["r12min"],
                dE1PN_u=r["dE1PN"] / unit, ok=r["ok"], E12_end=en["E12"] / unit,
                J_per_mu=np.full(nphase, J))


def run_newtonfar(cfg, rp, sense, nphase):
    ss = setups(cfg, rp, sense, nphase)
    r = tb.scatter(ss, k0=K0, k_end=30.0)
    return dict(outcome=r["outcome"], E_out=r["E_out"], rMmin=r["rMmin"].min(axis=1),
                r12min=r["r12min"] * cfg["a"])


def run_hrna2404(cfg, rp, sense, nphase):
    import hrna
    keys = ("outcome", "E1_u", "E2_u", "plunged", "status")
    res = {k: np.zeros(nphase) for k in keys}
    ph = 2 * np.pi * np.arange(nphase) / nphase
    for i in range(nphase):
        o = hrna.run_encounter(law="hrna", m1=cfg["m1"], m2=cfg["m2"], a=cfg["a"], rp=rp,
                               phase=ph[i], sense=sense, r0_rt=4.0, rf_rt=30.0)
        for k in keys:
            res[k][i] = o[k]
    res["outcome"] = res["outcome"].astype(int)
    return res


def task(args):
    model, qname, rp, sense, nphase = args
    t = time.time()
    fn = dict(eihfar=run_eihfar, newtonfar=run_newtonfar, hrna2404=run_hrna2404)[model]
    res = fn(CONFIGS[qname], rp, sense, nphase)
    res["wall"] = time.time() - t
    return (model, qname, rp, sense), res


def main():
    global K0, BINARY
    ap = argparse.ArgumentParser()
    ap.add_argument("outdir", nargs="?", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--nphase", type=int, default=360)
    ap.add_argument("--workers", type=int, default=13)
    ap.add_argument("--k0", type=float, default=40.0)
    ap.add_argument("--models", default="eihfar,newtonfar,hrna2404")
    ap.add_argument("--binary", default="1pn", choices=("1pn", "newton"))
    a = ap.parse_args()
    K0 = a.k0
    BINARY = a.binary
    os.makedirs(a.outdir, exist_ok=True)
    tasks = [(m, q, rp, s, a.nphase) for q, cfg in CONFIGS.items() for rp in cfg["rps"]
             for s in (1, -1) for m in a.models.split(",")]
    order = {"eihfar": 0, "hrna2404": 1, "newtonfar": 2}
    tasks.sort(key=lambda t: (order[t[0]], -t[2]))
    results = {}
    t0 = time.time()
    with Pool(a.workers) as pool:
        for key, res in pool.imap_unordered(task, tasks):
            results[key] = res
            print(f"{time.time() - t0:8.1f}s done {key} wall {res['wall']:.1f}s", flush=True)
    arrays = {f"{m}|{q}|{rp}|{s}|{k}": v for (m, q, rp, s), res in results.items()
              for k, v in res.items() if isinstance(v, np.ndarray)}
    np.savez_compressed(os.path.join(a.outdir, "scan_far.npz"), **arrays)
    summ = {}
    for (m, q, rp, s), res in sorted(results.items()):
        o = res["outcome"]
        d = dict(separated=float(np.mean((o != 0) & (o != 5))),
                 survived=float(np.mean(o == 0)), unsettled=float(np.mean(o == 5)),
                 captured=float(np.mean(o == 6)),
                 single=float(np.mean((o == 1) | (o == 2))),
                 both_free=float(np.mean(o == 4)), both_bound=float(np.mean(o == 3)))
        if "rMmin" in res:
            d["inside_5.35M"] = float(np.mean(res["rMmin"] < 5.35))
            d["inside_12M"] = float(np.mean(res["rMmin"] < 12.0))
        if "dE1PN_u" in res:
            d["dE1PN_units_median_abs"] = float(np.median(np.abs(res["dE1PN_u"])))
            d["not_ok"] = int(np.sum(~res["ok"].astype(bool)))
        if m in ("eihfar", "newtonfar"):
            sel = (o == 1) | (o == 2)
            d["E_ej_mean"] = float(np.mean(res["E_out"][sel])) if sel.any() else None
        else:
            e = np.where(o == 1, res["E2_u"], np.where(o == 2, res["E1_u"], np.nan))
            d["E_ej_mean"] = float(np.nanmean(e)) if np.isfinite(e).any() else None
        summ.setdefault(q, {}).setdefault(str(s), {}).setdefault(str(rp), {})[m] = d
    with open(os.path.join(a.outdir, "scan_far_summary.json"), "w") as fh:
        json.dump(dict(k0=K0, binary=BINARY, nphase=a.nphase, summary=summ,
                       walls={"|".join(map(str, k)): r["wall"] for k, r in results.items()}),
                  fh, indent=1)
    # figure
    sys.path.insert(0, os.path.join(TRK, "..", "..", "python"))
    from nrpic import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    col = dict(newtonfar="grey", hrna2404=fs.PAL["green"], eihfar=fs.PAL["red"])
    lab = dict(newtonfar=f"Newton, from {K0:g} r_t", hrna2404="HRNA, 2404 data, 4 r_t",
               eihfar=f"EIH, 1PN parabola, from {K0:g} r_t")
    fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.6), sharey=True)
    for r_, q in enumerate(("q10", "q4")):
        for c_, s in enumerate((1, -1)):
            ax = axs[r_, c_]
            rps = [float(x) for x in CONFIGS[q]["rps"]]
            for m in ("newtonfar", "hrna2404", "eihfar"):
                v = summ[q][str(s)]
                ax.plot(rps, [v[str(rp) if str(rp) in v else str(int(rp))][m]["separated"]
                              for rp in rps], "o-", color=col[m], label=lab[m], ms=4)
                key = "captured" if m == "hrna2404" else "inside_5.35M"
                ax.plot(rps, [v[str(rp) if str(rp) in v else str(int(rp))][m][key]
                              for rp in rps], "x--", color=col[m], lw=1, ms=5)
            ax.set_title(f"{q}, {'prograde' if s > 0 else 'retrograde'}", fontsize=9)
            ax.set_ylim(-0.03, 1.03)
            ax.set_xlabel(r"pericentre $r_p/M$ (Newton: Newtonian; EIH, HRNA: GR areal via $L$)",
                          fontsize=7)
            if c_ == 0:
                ax.set_ylabel("fraction of phases")
    axs[0, 0].legend(frameon=False, fontsize=6.5, loc="lower left")
    axs[0, 1].text(0.02, 0.02, "solid: separated; dashed: HRNA capture,\n"
                   "Newton/EIH member inside 5.35 M", transform=axs[0, 1].transAxes, fontsize=6.5)
    fig.tight_layout()
    fs.save(fig, os.path.join(a.outdir, "fig_scan_far"))
    plt.close(fig)
    print(f"total {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
