"""Q5 of the wave-2 journal: Newtonian predictions for the passages at q = 10 and q = 4
(stage/G1/STATUS.md: P1 and its q = 4 fallback) with the corrected member energies.

  passage  the start state of the input file (three_punctures/inputs/hills_q{10,4}_m8),
           rebuilt with puncture_state (10 r_t -> 4 r_t) and, as a cross-check, parsed
           from the file; full Newton to t = 1500 M (SciPy DOP853, rtol 1e-12): outcome,
           energies (corrected and against M alone), captured orbit, pericentre times of
           the captured member, closest approaches, ejection speed.
  scan     360 effective phases (as three_punctures/scripts/newton_start.py), coplanar
           prograde, start at 4 r_t on the unperturbed conic and at 10 r_t, end at 30 r_t:
           outcome fractions and ejection energies, corrected and before.

Run (from the worktree root):
  harness/bin/nrpic-run submit --kind scouting --gate G1 --package tracks/F-hills/newton3 \
      --cores 4 --purpose "..." -- python3 tracks/F-hills/newton3/scripts/passages.py --workers 4
"""
import argparse
import json
import os
import shutil
import sys

# one thread per worker process: the parallelism is the process pool (--workers = the
# cores of the run); nrpic-run sets the thread count to --cores, which every worker would
# inherit (finite-q run F-20261115-174959-9e8a361 used about 20 cores for 6 workers, stopped)
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
sys.path.insert(0, PKG)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(PKG, "..", "..", "..", "python"))
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from scipy.integrate import solve_ivp  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402
from hills3 import threebody as T  # noqa: E402
import runlib  # noqa: E402

INPUTS = os.path.join(PKG, "..", "three_punctures", "inputs")
CONFIGS = {"q10": (dict(M=1.0, m1=0.05, m2=0.05, a=3.0, rp=8.0), 130.0, "hills_q10_m8.athinput"),
           "q4": (dict(M=1.0, m1=0.125, m2=0.125, a=5.0, rp=1.2378 * 5.0 * 4.0 ** (1 / 3)), 127.0,
                  "hills_q4_m8.athinput")}
NPH = 360
PHASES = np.linspace(0.0, 2 * np.pi, NPH, endpoint=False)
R_MB = 4.0      # marginally bound radius of Schwarzschild (proxy used by three_punctures)


def follow(masses, x, v, t_end=1500.0, n_out=30001):
    rhs = T._rhs_factory(masses[None, :], np.array([1.0]))
    idx0 = np.zeros(1, dtype=int)
    sol = solve_ivp(lambda t, y: rhs(np.array([t]), y[None, :], idx0)[0], (0.0, t_end),
                    np.concatenate([x.ravel(), v.ravel()]), method="DOP853", rtol=1e-12,
                    atol=1e-14, dense_output=True)
    tt = np.linspace(0.0, t_end, n_out)
    Y = sol.sol(tt).T
    return tt, Y[:, :9].reshape(-1, 3, 3), Y[:, 9:].reshape(-1, 3, 3)


def minima(t, r):
    i = np.where((r[1:-1] < r[:-2]) & (r[1:-1] <= r[2:]))[0] + 1
    return [float(t[k]) for k in i], [float(r[k]) for k in i]


def passage(name):
    kw, phase_deg, fn = CONFIGS[name]
    s = T.HillsSetup(**kw, phase=np.radians(phase_deg))
    st = T.puncture_state(s, k0=4.0, k_from=10.0)
    m = st["masses"]
    u = s.energy_unit
    out = {"setup": st["params"], "r_t": st["r_t"], "start_checks": st["checks"],
           "t_start_rel_unperturbed_pericentre": st["t"], "unit": u}
    # cross-check: the state as written in the input file (order m1, m2, M)
    ref = T.parse_problem_block(open(os.path.join(INPUTS, fn)).read())
    xf = ref["positions"][[2, 0, 1]]
    vf = ref["momenta"][[2, 0, 1]] / ref["masses"][[2, 0, 1], None]
    tt, X, V = follow(m, st["positions"], st["velocities"])
    en = T.member_energies(X, V, m)
    end = T.evolve_states(m[None], xf[None], vf[None], 0.0, 1500.0, rtol=1e-12)
    enf = end["_en"]
    ie = 1 if en["inner"][-1] == 2 else 2
    ic = 3 - ie
    mu_out = m[ie] * (m[0] + m[ic]) / m.sum()
    E_ej = float(en[f"E{ie}"][-1])
    late = tt >= 300
    r1 = np.linalg.norm(X[:, 1] - X[:, 0], axis=1)
    r2 = np.linalg.norm(X[:, 2] - X[:, 0], axis=1)
    r12 = np.linalg.norm(X[:, 2] - X[:, 1], axis=1)
    rc = r2 if ic == 2 else r1
    tp, rp = minima(tt, rc)
    out.update(
        outcome=T.OUTCOME_NAMES[T.classify(T.member_energies(X[-1:], V[-1:], m), X[-1:], V[-1:], m)[0][0]],
        ejected=f"m{ie}", captured=f"m{ic}",
        E_ej_units=E_ej / u, E_ej_M=E_ej, E_cap_units=float(en[f"E{ic}"][-1] / u),
        E_tot_units=float(en["E_tot"][0] / u), dE_units=float(((m[1] / (m[1] + m[2])) * en["E2"][-1]
                                                              - (m[2] / (m[1] + m[2])) * en["E1"][-1]) / u),
        E_ej_units_ptp_t300=float(np.ptp(en[f"E{ie}"][late] / u)),
        E_ej_before_units_range_t300=[float(en[f"E{ie}_M"][late].min() / u), float(en[f"E{ie}_M"][late].max() / u)],
        v_inf=float(np.sqrt(2 * E_ej / mu_out)),
        captured_orbit=dict(a=float(en["a_in"][-1]), e=float(en["e_in"][-1]), rp=float(en["rp_in"][-1])),
        captured_pericentre_times=tp[:6], captured_pericentre_radii=rp[:6],
        rmin_1M=float(r1.min()), rmin_2M=float(r2.min()), t_rmin_cap=float(tt[np.argmin(rc)]),
        # what a run of the code that ends at these times can compare with
        at_times={f"t{tq:g}": dict(E_ej_units=float(np.interp(tq, tt, en[f"E{ie}"]) / u),
                                   E_ej_before_units=float(np.interp(tq, tt, en[f"E{ie}_M"]) / u),
                                   E_cap_units=float(np.interp(tq, tt, en[f"E{ic}"]) / u),
                                   W_units=float(np.interp(tq, tt, en["W"]) / u),
                                   r_ej_from_M=float(np.interp(tq, tt, r1 if ie == 1 else r2)),
                                   r_ej_from_origin=float(np.interp(tq, tt, np.linalg.norm(X[:, ie], axis=1))))
                  for tq in (100.0, 150.0, 200.0, 250.0, 270.0)},
        binary_separation_t40=float(np.interp(40.0, tt, r12)),
        input_file_state=dict(E_ej_units=float(enf[f"E{ie}"][0] / u),
                              outcome=T.OUTCOME_NAMES[int(end["outcome"][0])],
                              outcome_before=T.OUTCOME_NAMES[int(end["outcome_M"][0])],
                              captured_a=float(enf["a_in"][0]), captured_e=float(enf["e_in"][0]),
                              max_abs_dx_rebuilt_vs_file=float(np.abs(xf - st["positions"]).max()),
                              max_abs_dp_rebuilt_vs_file=float(np.abs(ref["momenta"][[2, 0, 1]]
                                                                      - st["momenta"]).max())))
    return out, (tt, r1, r2, r12, en, u, ie)


def scan_task(a):
    name, k0 = a
    kw, _, _ = CONFIGS[name]
    o = T.scatter([T.HillsSetup(**kw, phase=p) for p in PHASES], k0=k0, k_end=30.0)
    keep = ("outcome", "outcome_M", "E1", "E2", "E1_M", "E2_M", "dE", "dE_M", "rMmin", "ok",
            "energy_error", "W_end")
    return a, {k: np.asarray(o[k]) for k in keep}


def scan_summary(o):
    """Fractions over the trajectories that finished (ok); the stalled ones (a near
    head-on approach of the members, step below 1e-14 t, JOURNAL P0) are counted apart."""
    ok = o["ok"]
    n_fail = int((~ok).sum())
    o = {k: v[ok] for k, v in o.items()}
    on, oo = o["outcome"], o["outcome_M"]
    single = np.isin(on, [T.EJECT1, T.EJECT2])
    Eej = np.where(on == T.EJECT1, o["E1"], np.where(on == T.EJECT2, o["E2"], np.nan))
    singo = np.isin(oo, [T.EJECT1, T.EJECT2])
    Eejo = np.where(oo == T.EJECT1, o["E1_M"], np.where(oo == T.EJECT2, o["E2_M"], np.nan))
    rmin = o["rMmin"].min(axis=1)
    return dict(
        n_finished=int(ok.sum()), n_stalled=n_fail,
        fractions={T.OUTCOME_NAMES[k]: float(np.mean(on == k)) for k in range(6)},
        fractions_before={T.OUTCOME_NAMES[k]: float(np.mean(oo == k)) for k in range(6)},
        outcome_changed=float(np.mean(on != oo)),
        disrupted=float(np.mean(np.isin(on, [1, 2, 3, 4]))),
        E_ej_mean=float(np.nanmean(Eej[single])) if single.any() else None,
        E_ej_median=float(np.nanmedian(Eej[single])) if single.any() else None,
        E_ej_range=[float(np.nanmin(Eej[single])), float(np.nanmax(Eej[single]))] if single.any() else None,
        E_ej_mean_before=float(np.nanmean(Eejo[singo])) if singo.any() else None,
        E_ej_max_abs_change=float(np.nanmax(np.abs(Eej - Eejo)[single & singo])) if (single & singo).any() else None,
        frac_rmin_below_4M=float(np.mean(rmin < R_MB)),
        min_rmin=float(rmin.min()), max_energy_error=float(np.abs(o["energy_error"]).max()),
        max_abs_W_end_single=float(np.nanmax(np.abs(np.where(single, o["W_end"], np.nan)))) if single.any() else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    run = runlib.start_run("Q5 (wave 2): Newtonian predictions for the q=10 and q=4 passages with the "
                           "corrected member energies; 360-phase scans from 4 and 10 r_t",
                           cores=args.workers,
                           extra_inputs=[os.path.join(INPUTS, c[2]) for c in CONFIGS.values()],
                           preregistered="tracks/F-hills/newton3/JOURNAL.md#wave-2")
    S = {"passage": {}, "scan": {}}
    series = {}
    for name in CONFIGS:
        S["passage"][name], series[name] = passage(name)
        print(name, json.dumps({k: v for k, v in S["passage"][name].items()
                                if k not in ("setup", "start_checks")}), flush=True)
    jobs = [(name, k0) for name in CONFIGS for k0 in (4.0, 10.0)]
    with Pool(args.workers) as pool:
        scans = dict(pool.map(scan_task, jobs))
    np.savez_compressed(os.path.join(run["dir"], "passage_scans.npz"),
                        **{f"{k}_{n}_k{k0:g}": v for (n, k0), o in scans.items() for k, v in o.items()})
    for (name, k0), o in scans.items():
        S["scan"][f"{name}_k{k0:g}"] = scan_summary(o)
        print(name, k0, json.dumps(S["scan"][f"{name}_k{k0:g}"]), flush=True)
    # the phase window of three_punctures/scripts/newton_start.py (lines 117-125): single
    # ejection from 4 and from 10 r_t, the same outcome, no member closer than 4.5 to M
    S["window"] = {}
    for name in CONFIGS:
        a, b = scans[(name, 4.0)], scans[(name, 10.0)]
        rmin4, rmin10 = a["rMmin"].min(axis=1), b["rMmin"].min(axis=1)
        idx = int(round(CONFIGS[name][1]))
        for tag, oa, ob in (("corrected", a["outcome"], b["outcome"]),
                            ("before", a["outcome_M"], b["outcome_M"])):
            good = (np.isin(oa, [1, 2]) & np.isin(ob, [1, 2]) & (oa == ob) & (rmin4 > 4.5)
                    & (rmin10 > 4.5) & a["ok"] & b["ok"])
            lo = idx
            while good[(lo - 1) % NPH] and idx - lo < NPH:
                lo -= 1
            hi = idx
            while good[(hi + 1) % NPH] and hi - idx < NPH:
                hi += 1
            S["window"][f"{name}_{tag}"] = dict(chosen_phase_deg=CONFIGS[name][1], chosen_is_good=bool(good[idx]),
                                                window_deg=[lo, hi] if good[idx] else None,
                                                n_good=int(good.sum()))
        print(name, "window", S["window"][f"{name}_corrected"], S["window"][f"{name}_before"], flush=True)
    with open(os.path.join(run["dir"], "passages.json"), "w") as fh:
        json.dump(S, fh, indent=2)
    with open(os.path.join(PKG, "results", "passages.json"), "w") as fh:
        json.dump(S, fh, indent=2)
    # ---------------------------------------------------------------- figure
    fs.use_style()
    fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.8))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.08, top=0.95, wspace=0.25, hspace=0.42)
    deg = np.degrees(PHASES)
    for j, name in enumerate(CONFIGS):
        ax = axs[0, j]
        for k0, col in ((10.0, fs.PAL["red"]), (4.0, fs.PAL["blue"])):
            o = scans[(name, k0)]
            on, oo = o["outcome"], o["outcome_M"]
            Eej = np.where(on == T.EJECT1, o["E1"], np.where(on == T.EJECT2, o["E2"], np.nan))
            Eejo = np.where(oo == T.EJECT1, o["E1_M"], np.where(oo == T.EJECT2, o["E2_M"], np.nan))
            ax.plot(deg, Eej, "-", color=col, lw=1.1, label=f"start {k0:g} $r_t$, corrected")
            ax.plot(deg, Eejo, ".", color=col, ms=1.6, label=f"start {k0:g} $r_t$, against $M$ alone")
            Eej = np.where(o["ok"], Eej, np.nan)
            low = o["rMmin"].min(axis=1) < R_MB
            ax.plot(deg[~o["ok"]], np.full((~o["ok"]).sum(), -0.1), "x", color=col, ms=4)
            ax.plot(deg[low], np.full(low.sum(), -0.3 if k0 == 10 else -0.5), "|", color=col, ms=5)
        ax.axvline(CONFIGS[name][1], **fs.MASK_LINE)
        ax.set_xlim(0, 360)
        ax.set_xlabel("effective phase at the start [deg]")
        ax.set_ylabel(r"$E_{\rm ej}$ [units]")
        ax.set_title(f"{name}: single ejections; |: a member inside 4 M; x: stalled", fontsize=9)
        ax.set_ylim(-0.7, 2.7)
        ax.legend(frameon=False, fontsize=6, loc="upper center", ncol=2)
        ax = axs[1, j]
        tt, r1, r2, r12, en, u, ie = series[name]
        ax.semilogy(tt, r1, color=fs.PAL["blue"], lw=1.1, label=r"$|x_1 - x_M|$")
        ax.semilogy(tt, r2, color=fs.PAL["red"], lw=1.1, label=r"$|x_2 - x_M|$")
        ax.semilogy(tt, r12, color="k", lw=0.8, label=r"$|x_2 - x_1|$")
        ax.axhline(R_MB, **fs.GUIDE, label="4 M")
        ax.set_xlim(0, 600)
        ax.set_ylim(1, 400)
        ax.set_xlabel(r"$t\,[M]$ from the start state (4 $r_t$)")
        ax.set_ylabel(r"distance $[M]$")
        P = S["passage"][name]
        ax.set_title(f"{name} passage: {P['outcome']}, $E_{{\\rm ej}}$ = {P['E_ej_units']:+.3f} units\n"
                     f"captured: a = {P['captured_orbit']['a']:.2f} M, e = {P['captured_orbit']['e']:.3f}",
                     fontsize=8)
        ax.legend(frameon=False, fontsize=7, loc="upper left", ncol=2)
    files = fs.save(fig, os.path.join(run["dir"], "fig_passages"))
    for f in files:
        shutil.copy(f, os.path.join(PKG, "figures"))
    plt.close(fig)
    runlib.finish_run(run, results={n: {k: S["passage"][n][k] for k in ("outcome", "E_ej_units", "E_cap_units")}
                                    for n in CONFIGS})


if __name__ == "__main__":
    main()
