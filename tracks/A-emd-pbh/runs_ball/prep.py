#!/usr/bin/env python3
"""Inputs and exact references of the scouting runs SR-1 and SR-2 (package runs_ball).

1. Reorders the lattice particles of data set 2t so that the tracked particles come first
   (the tag of a particle is its position in the file; <particles> traj_ntrack = n_track
   writes the first n_track to the trajectory files): the K particles nearest to each of
   the target shells R_i = 0.5, 1.2, 2.0, 2.4, 2.6, 2.74, 2.8, 2.9, 3.0, 3.2, 4.0, 6.0,
   8.0 M (initial areal radius; dense where the horizon forms) and a random sample over the whole ball. Positions, momenta and masses are
   unchanged; the script checks that the multiset of records is the same.
2. Exact references from expball/exact.py: per tracked particle (its own shell: m, E,
   turnaround, trapping and crunch proper times, largest areal radius); global events
   (core turnaround, first trapped sphere on a fine shell grid, crunch); the apparent-
   horizon mass on the slices of constant proper time, m_AH(tau) (outermost shell with
   R = 2m); the central density rho_c(tau); the largest coordinate speed of light of the
   comoving coordinates of SR-1 and the step plan derived from it.

    prep.py --out <dir> [--per-shell 100] [--sample 600] [--seed 7]
"""
import argparse
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C            # noqa: E402
from nrpic import io as nio   # noqa: E402

TARGETS = (0.5, 1.2, 2.0, 2.4, 2.6, 2.74, 2.8, 2.9, 3.0, 3.2, 4.0, 6.0, 8.0)
C_MAX = 0.618    # largest stable cfl x coordinate speed, RK4 + diss 0.5 (gauge/, run A-emd-pbh-20261115-113755-cac3c4b)


def coordinate_speeds(ball, tau, Ri, rbar):
    """Largest radial and tangential coordinate speed of light of the comoving isotropic
    coordinates (SR-1) over the shells Ri (initial isotropic radii rbar) at proper times
    tau: c_r = sqrt(1 + 2E) / |dR/drbar|, c_T = rbar / R (LTB: ds^2 = -dtau^2 +
    R'^2/(1+2E) drbar^2 + R^2 dOmega^2)."""
    sh = C.XE.Shells(ball, Ri)
    R = sh.R(tau)                                   # shells x times
    dR = np.gradient(R, rbar, axis=0)
    with np.errstate(divide="ignore", invalid="ignore"):
        cr = np.sqrt(1.0 + 2.0 * sh.E)[:, None] / np.abs(dR)
        ct = rbar[:, None] / R
    alive = R > 0
    cr = np.where(alive, cr, np.nan)
    ct = np.where(alive, ct, np.nan)
    return np.nanmax(cr, axis=0), np.nanmax(ct, axis=0), np.nanargmax(np.where(np.isfinite(cr), cr, -1), axis=0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--per-shell", type=int, default=100)
    ap.add_argument("--sample", type=int, default=600)
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    ball = C.ball2t()

    # ---------------------------------------------------------------- particles
    x, u, m, sp = nio.read_nrp(C.LAT2T)
    rbar = np.sqrt(np.sum(x * x, axis=1))
    Ri = ball.R_of_rbar(rbar)
    Ri = np.minimum(Ri, ball.R_out)
    chosen, group = [], {}
    for T in TARGETS:
        d = np.abs(Ri - T)
        idx = np.argsort(d, kind="stable")[: a.per_shell]
        for i in idx:
            group.setdefault(int(i), f"R{T:g}")
        chosen.append(idx)
    rng = np.random.default_rng(a.seed)
    samp = rng.choice(len(m), size=a.sample, replace=False)
    for i in samp:
        group.setdefault(int(i), "sample")
    track = np.array(sorted(group), dtype=int)
    rest = np.setdiff1d(np.arange(len(m)), track)
    order = np.concatenate([track, rest])
    xo, uo, mo, so = x[order], u[order], m[order], sp[order]
    pfile = os.path.join(a.out, C.STEM2T + "_lat38_track.nrp")
    nio.write_nrp(pfile, xo, uo, mo, so)
    # check: same records
    x2, u2, m2, s2 = nio.read_nrp(pfile)
    rec1 = np.concatenate([x, u, m[:, None]], axis=1)
    rec2 = np.concatenate([x2, u2, m2[:, None]], axis=1)
    same = bool(np.array_equal(np.sort(rec1.view([("", "<f8")] * 7), axis=0),
                               np.sort(rec2.view([("", "<f8")] * 7), axis=0)))
    n_track = len(track)

    # ---------------------------------------------------------------- exact per tracked particle
    Ri_t = Ri[track]
    sh = C.XE.Shells(ball, Ri_t)
    tracked = dict(n_track=int(n_track), particle_file=pfile, same_records=same,
                   sum_m=float(m.sum()), sum_m_reordered=float(m2.sum()),
                   tag=list(range(n_track)), source_index=[int(i) for i in track],
                   group=[group[int(i)] for i in track],
                   x0=xo[:n_track].tolist(), rbar0=rbar[track].tolist(), R_i=Ri_t.tolist(),
                   m=sh.m.tolist(), E=sh.E.tolist(), tau_ta=sh.tau_ta.tolist(),
                   tau_c=sh.tau_c.tolist(), tau_ah=sh.tau_ah.tolist(), R_max=sh.R_max.tolist(),
                   rest_mass=float(m[track].sum()))
    C.write_json(os.path.join(a.out, "tracked.json"), tracked)

    # ---------------------------------------------------------------- global exact events
    grid = np.concatenate([np.linspace(0.005, 2.4, 480), np.linspace(2.4005, 3.4, 8000),
                           np.linspace(3.401, ball.R_out, 1200)])
    S = C.XE.Shells(ball, grid)
    fh = S.first_horizon()
    core = C.XE.Shells(ball, np.array([0.5]))
    edge = C.XE.Shells(ball, np.array([2.4]))
    tau_first, tau_crunch = fh["tau_ah"], float(core.tau_c[0])
    # apparent horizon on slices of constant proper time: outermost shell with tau_ah <= tau
    k0 = fh["index"]
    outer = slice(k0, None)
    taus_ah = np.linspace(tau_first, tau_crunch, 401)
    m_ah, Ri_ah, R_ah = [], [], []
    for t in taus_ah:
        ok = np.nonzero(S.tau_ah[outer] <= t)[0]
        if len(ok) == 0:
            m_ah.append(np.nan); Ri_ah.append(np.nan); R_ah.append(np.nan)
            continue
        j = k0 + ok.max()
        # linear interpolation between shell j and j+1 for the root of tau_ah = t
        if j + 1 < len(grid) and S.tau_ah[j + 1] > t:
            w = (t - S.tau_ah[j]) / (S.tau_ah[j + 1] - S.tau_ah[j])
            mm = S.m[j] + w * (S.m[j + 1] - S.m[j])
            rr = grid[j] + w * (grid[j + 1] - grid[j])
        else:
            mm, rr = S.m[j], grid[j]
        m_ah.append(mm); Ri_ah.append(rr); R_ah.append(2 * mm)
    # inner trapping boundary too (inner root): for the record
    rho_c0 = float(ball.at(np.array([1e-3]))["rho"][0])
    tt = np.linspace(0.0, tau_crunch, 4001)
    a_core = core.R(tt)[0] / core.R_i[0]
    # coordinate speeds of SR-1
    Rgrid = np.concatenate([np.linspace(0.02, 2.4, 120), np.linspace(2.42, ball.R_out * 0.999, 200)])
    rbg = ball.rbar_of_R(Rgrid)
    tts = np.concatenate([np.linspace(0, 42, 85), np.linspace(42.05, tau_crunch - 1e-3, 400)])
    cr, ct, kmax = coordinate_speeds(ball, tts, Rgrid, rbg)
    cmax = np.maximum(cr, ct)
    stages, t0, cfl = [], 0.0, 0.25
    while t0 < tau_crunch - 0.03 and cfl > 1e-3:
        bad = tts[(tts > t0) & (cfl * cmax > 0.9 * C_MAX)]
        t1 = float(bad.min()) if bad.size else tau_crunch
        if t1 > t0:
            stages.append(dict(t_from=round(t0, 4), t_to=round(t1, 4), cfl=cfl,
                               cmax_end=float(np.interp(t1, tts, cmax))))
        t0, cfl = t1, 0.5 * cfl
    ex = dict(
        model=dict(M=ball.M, H=ball.H, t_i=ball.t_i, R_b=ball.Rb if hasattr(ball, "Rb") else None,
                   R_out=ball.R_out, rest_mass=float(m.sum()), rho_c0=rho_c0),
        core=dict(tau_ta=float(core.tau_ta[0]), R_max_over_R_i=float(core.R_max[0] / core.R_i[0]),
                  tau_c=tau_crunch, tau_ah_edge=float(edge.tau_ah[0]), m_edge=float(edge.m[0])),
        first_trapped=dict(tau=tau_first, R_i=fh["R_i"], m=fh["m"], R=2 * fh["m"],
                           rbar_i=float(ball.rbar_of_R(np.array([fh["R_i"]]))[0]),
                           shell_grid_spacing=float(grid[k0 + 1] - grid[k0])),
        m_ah=dict(tau=taus_ah.tolist(), m=m_ah, R_i=Ri_ah, R=R_ah),
        central=dict(tau=tt[a_core > 0].tolist(), a=a_core[a_core > 0].tolist(),
                     rho=(rho_c0 / a_core[a_core > 0] ** 3).tolist()),
        sr1_speeds=dict(tau=tts.tolist(), c_r=cr.tolist(), c_T=ct.tolist(), c_max=cmax.tolist(),
                        R_i_at_max=Rgrid[kmax].tolist()),
        sr1_stages=stages, C_MAX=C_MAX,
        shell_crossing_before_crunch=float(S.shell_crossing(np.linspace(0, tau_crunch - 1e-6, 400))),
    )
    C.write_json(os.path.join(a.out, "exact.json"), ex)
    print(f"tracked {n_track} particles (same records: {same}); file {pfile}")
    print(f"core turnaround tau = {ex['core']['tau_ta']:.6f}, R_max/R_i = {ex['core']['R_max_over_R_i']:.6f}")
    print(f"first trapped sphere tau = {tau_first:.6f} at R_i = {fh['R_i']:.5f} (rbar_i = "
          f"{ex['first_trapped']['rbar_i']:.5f}), m = {fh['m']:.6f}")
    print(f"core edge trapped tau = {ex['core']['tau_ah_edge']:.6f}; crunch tau = {tau_crunch:.6f}")
    for s in stages:
        print(f"  stage cfl {s['cfl']:.6g}: t {s['t_from']} -> {s['t_to']} (c_max at end {s['cmax_end']:.3f})")
    print(f"m_AH at tau = {taus_ah[200]:.4f}: {m_ah[200]:.5f}; at tau = {taus_ah[-2]:.4f}: {m_ah[-2]:.5f}")

    # ---------------------------------------------------------------- figure
    from nrpic import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(8.0, 3.3))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.15, top=0.92, wspace=0.32)
    ax = fig.add_subplot(1, 3, 1)
    ax.semilogy(tts, cmax, color=fs.PAL["red"], label="largest $c$ (SR-1)")
    ax.semilogy(tt[a_core > 0], 1.0 / a_core[a_core > 0], color=fs.PAL["blue"], ls="--", label="$R_i/R$ core")
    for s in stages:
        ax.plot([s["t_from"], s["t_to"]], [C_MAX / s["cfl"]] * 2, color="k", lw=1.0)
    ax.set_xlabel(r"$\tau\,/M$")
    ax.set_ylabel("coordinate speed of light")
    ax.legend(loc="upper left", fontsize=8)
    ax.set_title("SR-1 step plan (black: 0.618/cfl)", fontsize=9)
    ax = fig.add_subplot(1, 3, 2)
    ax.plot(S.R_i, S.tau_ah, color=fs.PAL["blue"])
    ax.axhline(tau_first, **fs.GUIDE)
    ax.axhline(tau_crunch, color="grey", lw=1.0)
    ax.set_xlim(0, 5)
    ax.set_ylim(44.2, 45.2)
    ax.set_xlabel(r"$R_i\,/M$")
    ax.set_ylabel(r"$\tau_{\rm AH}(R_i)\,/M$")
    ax.set_title("trapping time per shell", fontsize=9)
    ax = fig.add_subplot(1, 3, 3)
    ax.plot(taus_ah, m_ah, color=fs.PAL["blue"])
    ax.set_xlabel(r"$\tau\,/M$")
    ax.set_ylabel(r"$m_{\rm AH}(\tau)\,/M$")
    ax.set_title("horizon mass, slices of constant $\\tau$", fontsize=9)
    fs.save(fig, os.path.join(a.out, "fig_exact_references"))
    figdir = os.path.join(C.HERE, "figs")
    os.makedirs(figdir, exist_ok=True)
    fs.save(fig, os.path.join(figdir, "fig_exact_references"))


if __name__ == "__main__":
    main()
