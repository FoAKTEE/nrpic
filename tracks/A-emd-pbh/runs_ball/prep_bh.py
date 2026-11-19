#!/usr/bin/env python3
"""Data set 3 of the package runs_ball (wave 2b): an expanding ball whose first apparent
horizon is large enough for the meshes of this machine, built with expball (A-pre-1), and
its exact references.

Model (expball/model.py): Einstein-de Sitter ball with H R_b = HRb, a compensated top-hat
core (closed FLRW, mean contrast delta_c inside R1, underdense shell R1 < R < R2, Einstein-
de Sitter from R2 to the C^4 taper of half width w at R_b). The first trapped sphere is the
core edge R1 (all core shells crunch together; 2m/R grows as R_i^2 inside the core), so the
first horizon encloses the whole core, m = (1 + delta_c) (R1/R_b)^3 M. The taper is chosen
so that the matter edge sits at rbar_m = rm, a multiple of every lattice spacing used:
lattices of n_lat sites across 2 rm put one site at each cell centre of meshes with
dx = 2 rm / n_lat whose faces include 0.

Writes into --out:
  <stem>.tab                         table format 2 (expball/table.py; exterior pg)
  lat<n>/<stem>_lat<n>_track.nrp     mass-weighted lattice, tracked particles first
  lat<n>/tracked.json, lat<n>/exact.json   per lattice (the --prep directory of compare.py)
  exact.json                          global exact events, m_AH(tau), central a(tau), lapse reference
  <stem>_shells.txt                   R_i rbar_i m E tau_ta tau_c tau_AH on a fine shell grid
  fig_bh_exact.png/pdf                shells, trapping time per shell, m_AH(tau), central lapse reference

    prep_bh.py --out DIR [--HRb 0.7 --dc 1.5 --R1 0.65 --R2 0.95 --rm 4.25 --nlat 34 51 68]
"""
import argparse
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C            # noqa: E402
from nrpic import io as nio   # noqa: E402
from expball import particles as XP, table as XT   # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--HRb", type=float, default=0.7)
    ap.add_argument("--dc", type=float, default=1.5)
    ap.add_argument("--R1", type=float, default=0.65, help="core radius / R_b")
    ap.add_argument("--R2", type=float, default=0.95, help="outer radius of the compensation / R_b")
    ap.add_argument("--rm", type=float, default=4.25, help="isotropic radius of the matter edge (M)")
    ap.add_argument("--nlat", type=int, nargs="+", default=[34, 51, 68])
    ap.add_argument("--per-shell", type=int, default=60)
    ap.add_argument("--sample", type=int, default=600)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--leak", type=float, default=8.0, help="lapse_leak rate of the reference")
    ap.add_argument("--table-points", type=int, default=4000)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    Rb = 2.0 / a.HRb ** 2
    w = a.rm - Rb
    spec = dict(profile="tophat", HRb=a.HRb, M=1.0, delta_c=a.dc, R1=a.R1 * Rb, R2=a.R2 * Rb,
                edge_width=w, R1_over_Rb=a.R1, R2_over_Rb=a.R2, rm=a.rm)
    ball = C.ball_from_spec(spec)
    rm = ball.matter_rbar()
    assert abs(rm - a.rm) < 1e-9, (rm, a.rm)
    stem = (f"expball_tophat_HRb{a.HRb:g}_dc{a.dc:g}_R1{a.R1:g}_R2{a.R2:g}_rm{a.rm:g}").replace(".", "p")
    summ = ball.summary()
    print("model:", {k: summ[k] for k in ("H", "Rb", "M_misner_sharp", "t_i", "rest_mass", "psi_centre",
                                         "max_2m_over_R", "R_at_max_2m_over_R", "delta_u", "rbar_matter")})

    # ------------------------------------------------------------ table
    drbar = rm / a.table_points
    tab = os.path.join(a.out, stem + ".tab")
    hdr = dict(generator="tracks/A-emd-pbh/runs_ball/prep_bh.py (expball/table.py)", model="tophat",
               H=repr(ball.H), Rb=repr(ball.Rb), M=repr(ball.M), t_i=repr(ball.t_i),
               units="G = c = 1, M_ADM = M", alpha="1 (proper-time slicing of the dust)",
               betar="-v/(psi^2 sqrt(1+2E)) (shift of the dust's proper-time slicing)")
    XT.write_format2(tab, ball, drbar, 1.5 * rm, header=hdr)

    # ------------------------------------------------------------ exact events
    R1, R2 = spec["R1"], spec["R2"]
    grid = np.concatenate([np.linspace(0.005, R1, 400), np.linspace(R1 * (1 + 1e-12), R2, 4000),
                           np.linspace(R2 * (1 + 1e-9), ball.R_out * 0.99999, 400)])
    S = C.XE.Shells(ball, grid)
    fh = S.first_horizon()
    core = C.XE.Shells(ball, np.array([0.1 * R1]))
    edge = C.XE.Shells(ball, np.array([R1]))
    tau_first, tau_crunch = fh["tau_ah"], float(core.tau_c[0])
    k0 = fh["index"]
    taus_ah = np.linspace(tau_first, tau_first + 12.0, 481)
    m_ah, Ri_ah = [], []
    for t in taus_ah:
        ok = np.nonzero(S.tau_ah[k0:] <= t)[0]
        if len(ok) == 0:
            m_ah.append(np.nan); Ri_ah.append(np.nan)
            continue
        j = k0 + ok.max()
        if j + 1 < len(grid) and S.tau_ah[j + 1] > t:
            wj = (t - S.tau_ah[j]) / (S.tau_ah[j + 1] - S.tau_ah[j])
            m_ah.append(S.m[j] + wj * (S.m[j + 1] - S.m[j])); Ri_ah.append(grid[j] + wj * (grid[j + 1] - grid[j]))
        else:
            m_ah.append(S.m[j]); Ri_ah.append(grid[j])
    m_ah, Ri_ah = np.array(m_ah), np.array(Ri_ah)
    tt = np.linspace(0.0, tau_crunch, 4001)
    a_core = core.R(tt)[0] / core.R_i[0]
    alive = a_core > 0
    rho_c0 = float(ball.at(np.array([1e-3]))["rho"][0])
    lt, ltau, lal = C.relaxed_lapse_reference(tt[alive][:-1], a_core[alive][:-1], a.leak, t_end=60.0)
    ex = dict(
        spec=spec, stem=stem, table=os.path.basename(tab),
        model=dict(M=ball.M, H=ball.H, t_i=ball.t_i, R_b=ball.Rb, R_out=ball.R_out, rest_mass=ball.rest_mass(),
                   rho_c0=rho_c0, rbar_matter=rm, max_2m_over_R=summ["max_2m_over_R"], psi_centre=summ["psi_centre"],
                   delta_u=summ.get("delta_u")),
        core=dict(R1=R1, tau_ta=float(core.tau_ta[0]), R_max_over_R_i=float(core.R_max[0] / core.R_i[0]),
                  tau_c=tau_crunch, tau_ah_edge=float(edge.tau_ah[0]), m_edge=float(edge.m[0])),
        first_trapped=dict(tau=tau_first, R_i=fh["R_i"], m=fh["m"], R=2 * fh["m"],
                           rbar_i=float(ball.rbar_of_R(np.array([fh["R_i"]]))[0]),
                           compression_Rmax_over_RAH=float(S.R_max[k0] / (2 * fh["m"])),
                           shell_grid_spacing=float(grid[k0 + 1] - grid[k0])),
        m_ah=dict(tau=taus_ah.tolist(), m=m_ah.tolist(), R_i=Ri_ah.tolist(), R=(2 * m_ah).tolist()),
        m_R2=float(ball.at(np.array([R2 * 0.999999]))["m"][0]),
        central=dict(tau=tt[alive].tolist(), a=a_core[alive].tolist(), rho=(rho_c0 / a_core[alive] ** 3).tolist()),
        lapse_reference=dict(rate=a.leak, t=lt.tolist(), tau=ltau.tolist(), alpha=lal.tolist()),
        shell_crossing_before_crunch=float(S.shell_crossing(np.linspace(0, tau_crunch * 0.999, 600))),
        edge_R_at_first_trapped=float(C.XE.Shells(ball, np.array([ball.R_out * 0.99999])).R(np.array([tau_first]))[0, 0]),
        report_taus=[round(x, 3) for x in (0.5 * float(core.tau_ta[0]), float(core.tau_ta[0]),
                                           0.5 * (float(core.tau_ta[0]) + tau_first), tau_first - 1.0,
                                           tau_first - 0.3, tau_first)],
    )
    C.write_json(os.path.join(a.out, "exact.json"), ex)
    with open(os.path.join(a.out, stem + "_shells.txt"), "w") as fh_:
        fh_.write("# exact shells (expball/exact.py): R_i rbar_i m E tau_ta tau_c tau_AH\n")
        rbg = ball.rbar_of_R(grid)
        for row in zip(grid, rbg, S.m, S.E, S.tau_ta, S.tau_c, S.tau_ah):
            fh_.write(" ".join(f"{v:.15e}" for v in row) + "\n")

    # ------------------------------------------------------------ lattices and tracked particles
    targets = [0.3 * R1, 0.6 * R1, 0.85 * R1, R1 - 0.05, R1 + 0.05, R1 + 0.15, R1 + 0.3, R1 + 0.5,
               R1 + 0.8, 0.5 * (R1 + R2) + 0.4, R2 - 0.1, R2 + 0.1]
    targets = sorted(set(round(x, 3) for x in targets))
    lat_info = {}
    for n in a.nlat:
        d = os.path.join(a.out, f"lat{n}")
        os.makedirs(d, exist_ok=True)
        x, u, m, sp = XP.lattice(ball, n)
        h = 2.0 * rm / n
        rbar = np.sqrt(np.sum(x * x, axis=1))
        Ri = np.minimum(ball.R_of_rbar(rbar), ball.R_out)
        group = {}
        for T in targets:
            idx = np.argsort(np.abs(Ri - T), kind="stable")[: a.per_shell]
            for i in idx:
                group.setdefault(int(i), f"R{T:g}")
        rng = np.random.default_rng(a.seed)
        for i in rng.choice(len(m), size=min(a.sample, len(m)), replace=False):
            group.setdefault(int(i), "sample")
        track = np.array(sorted(group), dtype=int)
        order = np.concatenate([track, np.setdiff1d(np.arange(len(m)), track)])
        pfile = os.path.join(d, f"{stem}_lat{n}_track.nrp")
        nio.write_nrp(pfile, x[order], u[order], m[order], sp[order])
        x2, u2, m2, s2 = nio.read_nrp(pfile)
        rec1 = np.concatenate([x, u, m[:, None]], axis=1)
        rec2 = np.concatenate([x2, u2, m2[:, None]], axis=1)
        same = bool(np.array_equal(np.sort(rec1.view([("", "<f8")] * 7), axis=0),
                                   np.sort(rec2.view([("", "<f8")] * 7), axis=0)))
        sh = C.XE.Shells(ball, Ri[track])
        tracked = dict(n_track=int(len(track)), particle_file=pfile, same_records=same, n_particles=int(len(m)),
                       h=h, n_lat=n, sum_m=float(m.sum()), tag=list(range(len(track))),
                       source_index=[int(i) for i in track], group=[group[int(i)] for i in track],
                       x0=x[track].tolist(), rbar0=rbar[track].tolist(), R_i=Ri[track].tolist(),
                       m=sh.m.tolist(), E=sh.E.tolist(), tau_ta=sh.tau_ta.tolist(), tau_c=sh.tau_c.tolist(),
                       tau_ah=sh.tau_ah.tolist(), R_max=sh.R_max.tolist())
        C.write_json(os.path.join(d, "tracked.json"), tracked)
        C.write_json(os.path.join(d, "exact.json"), ex)
        lat_info[n] = dict(h=h, N=int(len(m)), n_track=int(len(track)), same_records=same, file=pfile,
                           sum_m=float(m.sum()))
        print(f"lattice n_lat = {n}: h = {h:.6f}, N = {len(m)}, tracked {len(track)}, same records {same}, "
              f"sum m = {m.sum():.8f} (continuum {ball.rest_mass():.8f})")
    C.write_json(os.path.join(a.out, "lattices.json"), lat_info)
    print(f"core: turnaround tau = {ex['core']['tau_ta']:.6f}, R_max/R_i = {ex['core']['R_max_over_R_i']:.6f}, "
          f"crunch {tau_crunch:.6f}")
    print(f"first trapped sphere: tau = {tau_first:.6f}, R_i = {fh['R_i']:.6f} (rbar {ex['first_trapped']['rbar_i']:.6f}), "
          f"m = {fh['m']:.6f}, R_AH = {2 * fh['m']:.6f}, compression {ex['first_trapped']['compression_Rmax_over_RAH']:.4f}")
    print(f"m_AH(tau) at tau_first + 0, 2, 4, 8, 12: {[round(float(np.interp(tau_first + d_, taus_ah, m_ah)), 6) for d_ in (0, 2, 4, 8, 12)]}")
    print(f"matter edge at tau_first: R = {ex['edge_R_at_first_trapped']:.4f}; m(R2) = {ex['m_R2']:.6f}; "
          f"shell crossing before crunch: {ex['shell_crossing_before_crunch']}")
    for tq in (1, 2, 4, 6, 8, 10):
        if tq <= lt[-1]:
            print(f"  lapse reference (rate {a.leak}): t = {tq}: alpha_c = {np.interp(tq, lt, lal):.5f}, tau_c = {np.interp(tq, lt, ltau):.4f}")
    for lev in (0.5, 0.1):
        j = np.nonzero(lal < lev)[0]
        if len(j):
            print(f"  lapse reference below {lev} at t = {lt[j[0]]:.3f} (tau_c = {ltau[j[0]]:.4f})")
    print(f"  lapse reference ends at t = {lt[-1]:.3f}, tau_c = {ltau[-1]:.4f}")

    # ------------------------------------------------------------ figure
    from nrpic import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(8.0, 6.2))
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.09, top=0.95, wspace=0.30, hspace=0.40)
    ax = fig.add_subplot(2, 2, 1)
    tp = np.linspace(0, tau_first + 6, 600)
    pick = [0.5 * R1, R1, R1 + 0.15, R1 + 0.5, R1 + 0.8, 0.5 * (R1 + R2), R2, ball.R_out * 0.999]
    cols = fs.series_colors(len(pick), "viridis") if hasattr(fs, "series_colors") else [None] * len(pick)
    for c_, Rp in zip(cols, pick):
        s1 = C.XE.Shells(ball, np.array([Rp]))
        Rt = s1.R(tp)[0]
        ok = Rt > 0
        ax.plot(tp[ok], Rt[ok], color=c_, lw=1.2, label=f"$R_i={Rp:.2f}$")
        ax.plot(tp[ok], np.full(ok.sum(), 2 * s1.m[0]), color=c_, lw=0.6, ls=":")
    ax.axvline(tau_first, **fs.GUIDE)
    ax.set_xlabel(r"$\tau\,/M$")
    ax.set_ylabel(r"$R\,/M$ (dotted: $2m$)")
    ax.set_ylim(0, 12)
    ax.legend(fontsize=6, ncol=2, loc="upper left")
    ax.set_title("exact shells", fontsize=10)
    ax = fig.add_subplot(2, 2, 2)
    fin = np.isfinite(S.tau_ah)
    ax.plot(S.R_i[fin], S.tau_ah[fin], color=fs.PAL["blue"], label=r"$\tau_{\rm AH}(R_i)$")
    ax.plot(S.R_i, np.where(np.isfinite(S.tau_c), S.tau_c, np.nan), color=fs.PAL["red"], lw=1.0, label=r"$\tau_c(R_i)$")
    ax.axhline(tau_first, **fs.GUIDE)
    ax.axvline(R1, **fs.MASK_LINE)
    ax.set_xlim(0, R2 * 1.02)
    ax.set_ylim(0, tau_first + 15)
    ax.set_xlabel(r"$R_i\,/M$")
    ax.set_ylabel(r"$\tau\,/M$")
    ax.legend(fontsize=8)
    ax.set_title("trapping and crunch per shell", fontsize=10)
    ax = fig.add_subplot(2, 2, 3)
    ax.plot(taus_ah, m_ah, color=fs.PAL["blue"], label=r"$m_{\rm AH}(\tau)$")
    ax.axhline(ex["m_R2"], **fs.GUIDE)
    ax.set_xlabel(r"$\tau\,/M$")
    ax.set_ylabel(r"$m\,/M$")
    ax.legend(fontsize=8)
    ax.set_title("horizon mass on slices of constant $\\tau$ (dashed: $m(R_2)$)", fontsize=9)
    ax = fig.add_subplot(2, 2, 4)
    ax.plot(lt, lal, color=fs.PAL["red"], label=r"$\alpha_c$ reference")
    ax.plot(lt, ltau / max(ltau[-1], 1e-9), color=fs.PAL["blue"], lw=1.0, label=r"$\tau_c/\tau_c^{\rm end}$")
    ax.set_xlabel(r"$t\,/M$")
    ax.set_ylabel("lapse")
    ax.legend(fontsize=8)
    ax.set_title(f"relaxed 1+log at the centre, rate {a.leak:g}", fontsize=10)
    fs.save(fig, os.path.join(a.out, "fig_bh_exact"))


if __name__ == "__main__":
    main()
