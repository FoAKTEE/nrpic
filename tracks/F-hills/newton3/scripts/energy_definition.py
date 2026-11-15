"""Q1-Q3 of the wave-2 journal: member energies at finite mass ratio, old against corrected.

  Q1  the two passages of stage/G1/STATUS.md (q = 10 and 4; start states of the input
      files rebuilt with puncture_state: 10 r_t -> 4 r_t) integrated to t = 1500 M with
      SciPy DOP853 (rtol 1e-12): ejected member's energy against M alone (old) and against
      the barycentre of M and the captured member (corrected), the captured member's
      energy, the coupling W, E1 + E2 + W - E_tot.
  Q2  end-time independence: scatter() at k_end = 30 and 100 r_t, coplanar prograde,
      128 phases, M/m = 10 and 4 (m1 = m2), D = 0.5 and 1.2.
  Q3  restricted limit: M/m = 1e6, m1/m2 = 3, D = 0.1 and 1, 128 phases.

Run (from the worktree root, through the harness):
  harness/bin/nrpic-run submit --kind scouting --gate G1 --package tracks/F-hills/newton3 \
      --cores 1 --purpose "..." -- python3 tracks/F-hills/newton3/scripts/energy_definition.py
"""
import json
import os
import shutil
import sys

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

PASSAGES = {"q10": dict(M=1.0, m1=0.05, m2=0.05, a=3.0, rp=8.0, phase=np.radians(130.0)),
            "q4": dict(M=1.0, m1=0.125, m2=0.125, a=5.0, rp=1.2378 * 5.0 * 4.0 ** (1 / 3),
                       phase=np.radians(127.0))}


def passage(kw, t_end=1500.0, n_out=30001):
    s = T.HillsSetup(**kw)
    st = T.puncture_state(s, k0=4.0, k_from=10.0)
    m = st["masses"]
    rhs = T._rhs_factory(m[None, :], np.array([1.0]))
    idx0 = np.zeros(1, dtype=int)
    sol = solve_ivp(lambda t, y: rhs(np.array([t]), y[None, :], idx0)[0], (0.0, t_end),
                    np.concatenate([st["positions"].ravel(), st["velocities"].ravel()]),
                    method="DOP853", rtol=1e-12, atol=1e-14, dense_output=True)
    tt = np.linspace(0.0, t_end, n_out)
    Y = sol.sol(tt).T
    X, V = Y[:, :9].reshape(-1, 3, 3), Y[:, 9:].reshape(-1, 3, 3)
    en = T.member_energies(X, V, m)
    return s, st, tt, X, en


def main():
    run = runlib.start_run("Q1-Q3 (wave 2): member energies at finite mass ratio, old (against M) "
                           "vs corrected (Jacobi); passages q=10, 4; end-time independence; "
                           "restricted limit", cores=1,
                           preregistered="tracks/F-hills/newton3/JOURNAL.md#wave-2")
    S = {"Q1": {}, "Q2": {}, "Q3": {}}
    fs.use_style()
    fig, axs = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 5.6))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.09, top=0.95, wspace=0.27, hspace=0.38)
    # ---------------------------------------------------------------- Q1
    for j, (name, kw) in enumerate(PASSAGES.items()):
        s, st, tt, X, en = passage(kw)
        u = s.energy_unit
        late, later = tt >= 300.0, tt >= 1000.0
        ie = 0 if en["inner"][-1] == 2 else 1             # 0: m1 ejected
        Enew = (en["E1"] if ie == 0 else en["E2"]) / u
        Eold = (en["E1_M"] if ie == 0 else en["E2_M"]) / u
        Ecap = (en["E2"] if ie == 0 else en["E1"]) / u
        W = en["W"] / u
        ident = (en["E1"] + en["E2"] + en["W"] - en["E_tot"]) / u
        S["Q1"][name] = dict(
            ejected=f"m{ie + 1}", E_tot_units=float(en["E_tot"][0] / u), unit=u,
            E_ej_new_end=float(Enew[-1]), E_cap_end=float(Ecap[-1]),
            E_ej_new_ptp_t300=float(np.ptp(Enew[late])), E_ej_new_ptp_t1000=float(np.ptp(Enew[later])),
            E_ej_old_ptp_t300=float(np.ptp(Eold[late])), E_ej_old_min_t300=float(Eold[late].min()),
            E_ej_old_max_t300=float(Eold[late].max()), E_ej_old_mean_t300=float(Eold[late].mean()),
            W_max_t300=float(np.abs(W[late]).max()), W_max_t1000=float(np.abs(W[later]).max()),
            identity_max=float(np.abs(ident).max()),
            captured_orbit=dict(a=float(en["a_in"][-1]), e=float(en["e_in"][-1]), rp=float(en["rp_in"][-1])),
            start_state_checks=st["checks"])
        print(name, json.dumps({k: v for k, v in S["Q1"][name].items() if k != "start_state_checks"}),
              flush=True)
        ax = axs[0, j]
        ax.plot(tt, Eold, color=fs.PAL["blue"], lw=1.0, label="against $M$ alone (before)")
        ax.plot(tt, Enew, color=fs.PAL["red"], lw=1.4, label="against the barycentre of $M$ + captured")
        ax.set_xlim(0, 1500)
        lo, hi = Eold[late].min(), Eold[late].max()
        ax.set_ylim(lo - 0.25 * (hi - lo), hi + 0.35 * (hi - lo))
        ax.set_xlabel(r"$t\,[M]$")
        ax.set_ylabel(r"$E_{\rm ej}$ [units]")
        ax.set_title(f"{name}: energy of the ejected member m{ie + 1} (full Newton)", fontsize=9)
        ax.legend(frameon=False, fontsize=7, loc="upper right")
        ax = axs[1, 0]
        c = fs.PAL["red"] if name == "q10" else fs.PAL["blue"]
        ax.semilogy(tt[1:], np.abs(W[1:]), color=c, lw=1.0, label=f"{name}: $|W|$")
        ax.semilogy(tt[1:], np.abs(Enew[1:] - Enew[-1]) + 1e-14, color=c, lw=1.0, ls="--",
                    label=f"{name}: $|E_{{\\rm ej}}(t) - E_{{\\rm ej}}(1500)|$")
        ax.semilogy(tt[1:], np.abs(ident[1:]) + 1e-16, color=c, lw=0.6, ls=":",
                    label=f"{name}: $|E_1 + E_2 + W - E_{{\\rm tot}}|$")
    ax = axs[1, 0]
    ax.axvline(300, **fs.MASK_LINE)
    ax.set_xlim(0, 1500)
    ax.set_ylim(1e-16, 10)
    ax.set_xlabel(r"$t\,[M]$")
    ax.set_ylabel("[units]")
    ax.legend(frameon=False, fontsize=6, loc="lower left", ncol=1)
    ax.set_title("coupling and settling of the corrected energies", fontsize=9)
    # ---------------------------------------------------------------- Q2
    ph = np.linspace(0, 2 * np.pi, 128, endpoint=False)
    ax = axs[1, 1]
    cols = fs.series_colors(4)
    k = 0
    for q in (10.0, 4.0):
        for D in (0.5, 1.2):
            ss = [T.HillsSetup(M=q, m1=0.5, m2=0.5, a=1.0, D=D, phase=p) for p in ph]
            a = T.scatter(ss, k_end=30.0)
            b = T.scatter(ss, k_end=100.0)
            single = np.isin(a["outcome"], [T.EJECT1, T.EJECT2]) & (a["outcome"] == b["outcome"])
            dn = np.abs(a["dE"] - b["dE"])
            do = np.abs(a["dE_M"] - b["dE_M"])
            S["Q2"][f"q{q:g}_D{D:g}"] = dict(
                n_single=int(single.sum()), max_new=float(dn[single].max()), max_old=float(do[single].max()),
                median_new=float(np.median(dn[single])), median_old=float(np.median(do[single])),
                same_outcome=float(np.mean(a["outcome"] == b["outcome"])),
                same_outcome_old=float(np.mean(a["outcome_M"] == b["outcome_M"])),
                max_abs_W_end_k30=float(np.nanmax(np.abs(np.where(single, a["W_end"], np.nan)))))
            print("Q2", q, D, S["Q2"][f"q{q:g}_D{D:g}"], flush=True)
            ax.semilogy(ph[single] / np.pi, do[single], "o", ms=2.2, mfc="none", color=cols[k],
                        label=f"M/m={q:g}, D={D:g}: before")
            ax.semilogy(ph[single] / np.pi, dn[single] + 1e-16, ".", ms=3, color=cols[k],
                        label="corrected")
            k += 1
    ax.axhline(1e-3, **fs.MASK_LINE)
    ax.set_xlim(0, 2)
    ax.set_ylim(1e-12, 3)
    ax.set_xlabel(r"effective phase $\phi/\pi$")
    ax.set_ylabel(r"$|\Delta E(100\,r_t) - \Delta E(30\,r_t)|$")
    ax.legend(frameon=False, fontsize=5.5, ncol=2, loc="lower right")
    ax.set_title("single ejections: end-time dependence of $\\Delta E$", fontsize=9)
    path = os.path.join(run["dir"], "fig_energy_definition")
    files = fs.save(fig, path)
    os.makedirs(os.path.join(PKG, "figures"), exist_ok=True)
    for f in files:
        shutil.copy(f, os.path.join(PKG, "figures"))
    plt.close(fig)
    # ---------------------------------------------------------------- Q3
    for D in (0.1, 1.0):
        ss = [T.HillsSetup(M=1e6, m1=0.75, m2=0.25, a=1.0, D=D, phase=p) for p in ph]
        o = T.scatter(ss)
        d = np.isin(o["outcome"], [T.EJECT1, T.EJECT2])
        rel = np.abs(o["dE"][d] - o["dE_M"][d]) / np.abs(o["dE"][d])
        S["Q3"][f"D{D:g}"] = dict(n=int(d.sum()), max_rel=float(rel.max()), median_rel=float(np.median(rel)),
                                  same_outcome=float(np.mean(o["outcome"] == o["outcome_M"])))
        print("Q3", D, S["Q3"][f"D{D:g}"], flush=True)
    with open(os.path.join(run["dir"], "energy_definition.json"), "w") as fh:
        json.dump(S, fh, indent=2)
    with open(os.path.join(PKG, "results", "energy_definition.json"), "w") as fh:
        json.dump(S, fh, indent=2)
    runlib.finish_run(run, results={"Q1": {k: {kk: v[kk] for kk in ("E_ej_new_end", "E_cap_end",
                                                                     "E_ej_old_ptp_t300", "E_ej_new_ptp_t300")}
                                           for k, v in S["Q1"].items()}})


if __name__ == "__main__":
    main()
