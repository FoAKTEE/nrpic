#!/usr/bin/env python3
"""Prediction tables of the analytic criteria for the first scouting runs of Track A:

  SR-1   expanding ball, data set 2t (run A-emd-pbh-20261115-130609-947c898; stage/G1/STATUS.md
         section 3; runs_ball/sr1.athinput), geodesic slicing, planned end tau = 44.37
  S1, S2 periodic box with the peak of arXiv:2609.14218 (periodic_threshold/JOURNAL.md, entry
         "S1 and S2 ... written before submission"): e = 0.2, p = 0, eps_i = k/(a_i H_i) = 1,
         box 20/k, 64^3 lattice (one particle per root cell); mu = 0.5 to tau = 14 (30 t_H)
         and mu = 0.03 to tau = 28.9 (250 t_H)

    python3 scouting_table.py [--out DIR]

Writes scouting_predictions.md, scouting_predictions.json and fig_scouting_predictions.
{pdf,png}. Every criterion row is predict.predict() of this package; the rows are given with
the amplitude in both measures (central contrast, mean inside r_m; SCOPE.md 10.1) where the
two differ. Exact spherical references come from expball (SR-1) and from ltb2609 (S1, S2,
e = 0 of the same mu).
"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "python"))
import emd_criteria as C  # noqa: E402
import ltb2609 as L  # noqa: E402
import predict as P  # noqa: E402

DATASET_2T = ("/data/haiyangw/nrpic/scratch/A-emd-pbh/A-emd-pbh-20261115-130609-947c898/"
              "expball_smooth_tophat_HRb0p5_dc1_R10p3_R20p75_w0p1875.json")


def tophat_times(delta):
    """Exact top hat (2507.18312:211-214, criteria R5): turnaround, R = 2M, crunch in a/a_H."""
    return dict(a_ta=float(C.tophat_amax(delta)), a_bh=float(C.tophat_aBH(delta)),
                a_c=float(C.tophat_acoll(delta)))


# ------------------------------------------------------------------- SR-1
def sr1(tau_end=44.37, tau_seg1=42.0):
    from expball.model import Ball, SmoothTopHat
    from expball.exact import Shells
    with open(DATASET_2T) as f:
        ds = json.load(f)
    mo = ds["model"]
    ball = Ball(mo["H"], mo["Rb"], SmoothTopHat(mo["delta_c"], mo["R1"], mo["R2"]),
                edge_width=mo["edge_width"])
    H, t_i, R1 = ball.H, ball.t_i, mo["R1"]
    core = ball.at(np.array([0.5 * R1]))
    Dc, y = float(core["Delta"][0]), float(core["y"][0])
    dL_i = 0.6 * y * (1 + Dc) ** (1 / 3)                 # linear contrast on the slice
    rhat1 = R1 * (1 + Dc) ** (1 / 3)                      # comoving areal radius, a_i = 1
    aH_core = (H * rhat1) ** 2                            # a_H/a_i of the core edge
    dH = dL_i * aH_core                                   # delta at horizon entry (top hat)
    tH = t_i * (H * rhat1) ** 3
    # compaction function on the slice: C = (3/5)(-2E), exact for t_b = 0 (2507 198-205)
    Rg = np.linspace(1e-3, mo["R2"], 6001)
    a = ball.at(Rg)
    Cr = 0.6 * (-2.0 * a["E"])
    j = int(np.argmax(Cr))
    Rm = float(Rg[j])
    rhat_m = Rm * (1 + float(a["Delta"][j])) ** (1 / 3)
    Cmax = float(Cr[j])
    # exact shells
    sh = Shells(ball, np.array([R1]))
    tau_ah_exact = float(sh.tau_ah[0])
    tau_ta_exact, tau_c_exact = float(sh.tau_ta[0]), float(sh.tau_c[0])
    th = tophat_times(dH)
    tau_of = lambda aa: tH * aa ** 1.5 - t_i              # a/a_H -> tau
    a_of = lambda tau: ((t_i + tau) / tH) ** (2 / 3)      # tau -> a/a_H
    lat = ds["particles"].get("lattice", {})
    h = 0.5                                               # lattice spacing (STATUS section 3)
    n_core = int(round(4 / 3 * math.pi * R1 ** 3 / h ** 3))
    rows = P.predict(dH, 0.0, 0.0, 0.0, a_of(tau_end), None, None, 1.0, "ball", 1.0, 1.0,
                     "tophat", None, n_core, H * rhat1, "lattice")
    rows_seg1 = P.predict(dH, 0.0, 0.0, 0.0, a_of(tau_seg1), None, None, 1.0, "ball")
    for r in rows:
        if r["a_form"] is not None and np.isfinite(r["a_form"]):
            r["tau_form"] = float(tau_of(r["a_form"]))
    return dict(
        case="SR-1", source="stage/G1/STATUS.md section 3; data set 2t " + ds["run_id"],
        H=H, t_i=t_i, Delta_core=Dc, y_core=y, deltaL_slice=dL_i, rhat_core=rhat1,
        aH_over_ai_core=aH_core, delta_H_core=dH, t_H_core=tH,
        compaction=dict(R_m=Rm, rhat_m=rhat_m, C_max=Cmax, aH_over_ai=(H * rhat_m) ** 2,
                        note="smoothed top hat: C peaks outside the homogeneous core"),
        tophat_R5=dict(a=th, tau_ta=tau_of(th["a_ta"]), tau_bh=tau_of(th["a_bh"]),
                       tau_c=tau_of(th["a_c"])),
        expball_exact=dict(tau_ta_core=tau_ta_exact, tau_ah_core_edge=tau_ah_exact,
                           tau_c_core=tau_c_exact,
                           first_trapped=ds["predictions"]["first_horizon"]),
        err_R5_vs_expball=dict(ta=abs(tau_of(th["a_ta"]) / tau_ta_exact - 1),
                               bh=abs(tau_of(th["a_bh"]) / tau_ah_exact - 1),
                               c=abs(tau_of(th["a_c"]) / tau_c_exact - 1)),
        zeldovich_point=dict(a=3.0 / dH, tau=tau_of(3.0 / dH)),
        tau_end=tau_end, a_end=a_of(tau_end), tau_seg1=tau_seg1, a_seg1=a_of(tau_seg1),
        n_core_lattice=n_core, lattice_file=lat.get("file", "lat38"),
        rows=rows, rows_seg1=[dict(id=r["id"], collapse=r["collapse"]) for r in rows_seg1])


# ------------------------------------------------------------------- S1, S2
def periodic(name, mu, e=0.2, p=0.0, eps_i=1.0, t_end_tH=30.0, n_root=64, box_k=20.0):
    amp = P.amplitude_measures(mu, "mu")
    aH = 6.0 / eps_i ** 2                                  # a_H/a_i, k^2/(aH)^2 = 6 (714)
    HR_ini = math.sqrt(6.0) / eps_i                        # a_i H_i r_m
    aend = t_end_tH ** (2 / 3)
    dx = box_k / n_root                                    # in 1/k
    n_rm = int(round(4 / 3 * math.pi * 6 ** 1.5 / dx ** 3))
    out = dict(case=name, mu=mu, e=e, p=p, eps_i=eps_i, aH_over_ai=aH, HR_ini=HR_ini,
               t_end_tH=t_end_tH, a_end=aend, n_particles_in_rm=n_rm, amplitude=amp,
               source="periodic_threshold/JOURNAL.md, S1 and S2 written before submission")
    for feed, d in (("central", amp["delta_c"]), ("mean", amp["deltabar"])):
        # region "ball" (q = 0) for R3: the peak's axes and the tidal field of its periodic
        # images are both aligned with the box axes, so the first-order torque vanishes
        # [JUDGEMENT]; "peak" would take q from the shape alone.
        rows = P.predict(d, e, p, 0.0, aend, None, None, 1.0, "ball", 1.0, 1.0, "tophat",
                         None, n_rm, HR_ini, "lattice")
        for r in rows:
            if r["a_form"] is not None and np.isfinite(r["a_form"]):
                r["t_form_tH"] = float(r["a_form"] ** 1.5)
        out[f"rows_{feed}"] = rows
    # deformation eigenvalues at entry (908 with k^2/(aH)^2 = 6) and Zel'dovich axis collapse
    lam = 0.8 * mu * np.array([1 + 3 * e + p, 1 - 2 * p, 1 - 3 * e + p])
    out["zeldovich_axes_t_tH"] = [float((1 / l) ** 1.5) if l > 0 else math.inf for l in lam]
    out["hoop_mu"] = float(C.hoop_threshold_delta(e, p) * 5 / 12)   # mu on the hoop line, 913-918
    th = tophat_times(amp["deltabar"])
    out["tophat_rm_t_tH"] = dict(ta=th["a_ta"] ** 1.5, bh=th["a_bh"] ** 1.5, c=th["a_c"] ** 1.5)
    pr = L.Profile2609(mu, 1.0, 1.0)
    out["ltb_e0"] = dict(t_s0_tH=float(pr.t_s(0.0) / pr.t_H),
                         t_ah_rm_tH=float(pr.t_ah(pr.r_m) / pr.t_H),
                         t_s_rm_tH=float(pr.t_s(pr.r_m) / pr.t_H),
                         C_max=float(pr.compaction(pr.r_m)),
                         verdict="forms (locally naked)" if mu >= L.MU_LOCALLY_NAKED else
                         ("no PBH (globally naked)" if mu <= L.MU_GLOBALLY_NAKED else "between"),
                         locator=L.THRESHOLD_LOCATOR)
    out["mdpbh_particles_e0.2"] = dict(
        bracket=(0.045, 0.05), verdict="horizon" if mu >= 0.05 else
        ("no horizon" if mu <= 0.045 else "inside bracket"),
        locator="2609.14218 MDPBH.tex:1101-1103, 1144-1145 (caveat: constraint violation, "
                "1146-1150)")
    out["fd_250"] = dict(delta_fd=250 ** (-2 / 3), locator="1707.03595:925")
    return out


# ------------------------------------------------------------------- output
def fmt_rows(rows, key_t, t_end):
    lines = []
    for r in rows:
        col = r["collapse"]
        v = "n/a" if col is None else ("yes" if col else "no")
        t = r.get(key_t)
        ts = "-" if t is None else f"{t:.4g}"
        dth = "-" if r["delta_th"] is None else f"{r['delta_th']:.4g}"
        lines.append(f"| {r['id']} | {r['criterion']} | {v} | {dth} | {ts} | {r['source']} |")
    return lines


def write_md(res, path):
    s = res["SR-1"]
    L_ = ["# Predictions of the analytic criteria for the first scouting runs", "",
          f"Run: {res.get('run_id', 'unregistered')}. Script: `criteria/scouting_table.py`. "
          "Labels: every number below is computed in this run from the formulas with the "
          "locators given in `emd_criteria.py` and `ltb2609.py` [VERIFIED as arithmetic]; "
          "whether a criterion applies to the run is [JUDGEMENT].", "",
          "## SR-1 (expanding ball, data set 2t, geodesic slicing)", "",
          f"Core: Delta = {s['Delta_core']:g} inside R_i = 2.4 M on the slice (H = {s['H']:g}, "
          f"t_i = {s['t_i']:.4f}); linear contrast on the slice {s['deltaL_slice']:.5f}; horizon "
          f"entry of the core edge at a_H/a_i = {s['aH_over_ai_core']:.5f} (t_H = "
          f"{s['t_H_core']:.5f} M); delta_H = {s['delta_H_core']:.5f} (top hat: central = mean). "
          f"Compaction maximum on the slice at R = {s['compaction']['R_m']:.3f} M (outside the "
          f"homogeneous core), C_max = {s['compaction']['C_max']:.5f}.", "",
          "| quantity | criteria (R5, exact top hat of 2507.18312) | expball exact | relative difference |",
          "|---|---|---|---|",
          f"| turnaround of the core, tau | {s['tophat_R5']['tau_ta']:.6f} | "
          f"{s['expball_exact']['tau_ta_core']:.6f} | {s['err_R5_vs_expball']['ta']:.1e} |",
          f"| R = 2M of the core edge, tau | {s['tophat_R5']['tau_bh']:.6f} | "
          f"{s['expball_exact']['tau_ah_core_edge']:.6f} | {s['err_R5_vs_expball']['bh']:.1e} |",
          f"| crunch of the core, tau | {s['tophat_R5']['tau_c']:.6f} | "
          f"{s['expball_exact']['tau_c_core']:.6f} | {s['err_R5_vs_expball']['c']:.1e} |", "",
          f"First trapped sphere of the data set (expball, smoothing region): tau = "
          f"{s['expball_exact']['first_trapped']['tau_ah']:.3f} at R_i = "
          f"{s['expball_exact']['first_trapped']['R_i']:.3f}. Zel'dovich point collapse of the "
          f"sphere (R1 with e = p = 0): a/a_H = {s['zeldovich_point']['a']:.1f}, tau = "
          f"{s['zeldovich_point']['tau']:.1f}, after the planned end tau = {s['tau_end']} "
          f"(a/a_H = {s['a_end']:.1f}).", "",
          f"Rows (predict.predict, delta = {s['delta_H_core']:.5f}, e = p = 0, sigma_v = 0, "
          f"a_end/a_H = {s['a_end']:.2f}, lattice N = {s['n_core_lattice']} in the core, "
          "H R on the slice = H rhat_core):", "",
          "| row | criterion | collapse | delta_th | tau of formation | source |",
          "|---|---|---|---|---|---|"]
    L_ += fmt_rows(s["rows"], "tau_form", s["tau_end"])
    L_ += ["", f"With the end of segment 1 (tau = {s['tau_seg1']}): "
           + ", ".join(f"{r['id']} {'n/a' if r['collapse'] is None else ('yes' if r['collapse'] else 'no')}"
                       for r in s["rows_seg1"]), ""]
    for key in ("S1", "S2"):
        c = res[key]
        a = c["amplitude"]
        L_ += [f"## {key} (periodic box, mu = {c['mu']}, e = {c['e']}, p = {c['p']}, "
               f"eps_i = {c['eps_i']}, end {c['t_end_tH']:g} t_H)", "",
               f"Amplitude: mu = {a['mu']:g}; delta_c (central) = {a['delta_c']:.4g}; deltabar "
               f"(mean in r_m) = {a['deltabar']:.4g}; C_max (nonlinear compaction) = "
               f"{a['C_max']:.4g}. Start a_i = a_H/{c['aH_over_ai']:g} (a_i H_i r_m = "
               f"{c['HR_ini']:.3f}); about {c['n_particles_in_rm']} lattice particles inside "
               f"r_m.", "",
               f"Zel'dovich collapse of the three axes (908 at entry): t/t_H = "
               + ", ".join(f"{t:.3g}" for t in c["zeldovich_axes_t_tH"])
               + f". Hoop line at e = {c['e']}: mu = {c['hoop_mu']:.4f}. Top hat of the "
               f"compaction shell (deltabar): turnaround {c['tophat_rm_t_tH']['ta']:.3g}, R = 2M "
               f"{c['tophat_rm_t_tH']['bh']:.3g}, crunch {c['tophat_rm_t_tH']['c']:.3g} t_H.", "",
               f"Exact spherical LTB of the same mu (e = 0, ltb2609): central crunch "
               f"{c['ltb_e0']['t_s0_tH']:.4g} t_H, R = 2M of the r_m shell "
               f"{c['ltb_e0']['t_ah_rm_tH']:.4g} t_H; threshold mu_c in (0.32, 0.33] "
               f"({c['ltb_e0']['locator']}): {c['ltb_e0']['verdict']}. Particle runs of "
               f"2609.14218 at e = 0.2, bracket (0.045, 0.05] "
               f"({c['mdpbh_particles_e0.2']['locator']}): {c['mdpbh_particles_e0.2']['verdict']}.",
               ""]
        for feed in ("central", "mean"):
            L_ += [f"Rows with the {feed} measure (delta = "
                   f"{a['delta_c'] if feed == 'central' else a['deltabar']:.4g}):", "",
                   "| row | criterion | collapse | delta_th | t/t_H of formation | source |",
                   "|---|---|---|---|---|---|"]
            L_ += fmt_rows(c[f"rows_{feed}"], "t_form_tH", c["t_end_tH"])
            L_ += [""]
    with open(path, "w") as f:
        f.write("\n".join(L_) + "\n")


def figure(res, out):
    from nrpic import figstyle as fs
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fs.use_style()
    fig = plt.figure(figsize=(fs.FULL_WIDTH, 3.9))
    axes = [fs.inch_axes(fig, 0.95 + 2.62 * i, 0.85, 1.6, 2.75) for i in range(3)]
    cases = [("SR-1", "tau_form", None), ("S1", "t_form_tH", "central"), ("S2", "t_form_tH", "central")]
    for ax, (key, kt, feed) in zip(axes, cases):
        c = res[key]
        items = []
        if key == "SR-1":
            to_t = lambda tau: tau
            end = c["tau_end"]
            for r in c["rows"]:
                items.append((r["id"], r.get(kt), r["collapse"]))
            items.append(("exact ball", c["expball_exact"]["first_trapped"]["tau_ah"], True))
            items.append(("Zel'dovich", c["zeldovich_point"]["tau"], False))
            xlabel = r"$\tau$ of formation ($M$)"
        else:
            end = c["t_end_tH"]
            for r in c[f"rows_{feed}"]:
                items.append((r["id"], r.get(kt), r["collapse"]))
            for r in c["rows_mean"]:
                if r["id"] in ("R1", "R5") and r.get(kt) is not None:
                    items.append((r["id"] + " (mean)", r[kt], r["collapse"]))
            items.append(("LTB e=0 crunch", c["ltb_e0"]["t_s0_tH"], c["mu"] >= 0.33))
            items.append(("ZA 1st axis", c["zeldovich_axes_t_tH"][0], None))
            xlabel = r"$t/t_H$ of formation"
        ys = np.arange(len(items))[::-1]
        for y, (lab, t, col) in zip(ys, items):
            colr = (fs.PAL["blue"] if col else (fs.PAL["red"] if col is False else "grey"))
            if t is not None and np.isfinite(t):
                ax.plot([t], [y], "o", color=colr, ms=4)
            else:
                ax.plot([end * 1.5], [y], ">", color=colr, ms=4)
        ax.axvline(end, **fs.GUIDE)
        ax.set_yticks(ys)
        ax.set_yticklabels([it[0] for it in items], fontsize=6.5)
        ax.set_xscale("log")
        ax.set_xlabel(xlabel, labelpad=-1)
        ttl = key if key == "SR-1" else f"{key}: $\\mu={c['mu']}$, $e={c['e']}$"
        ax.set_title(ttl, fontsize=8)
    h = [axes[0].plot([], [], "o", color=fs.PAL["blue"])[0],
         axes[0].plot([], [], "o", color=fs.PAL["red"])[0],
         axes[0].plot([], [], "o", color="grey")[0],
         axes[0].plot([], [], ">", color="k")[0],
         axes[0].plot([], [], **fs.GUIDE)[0]]
    fig.legend(h, ["forms by the end", "does not form by the end", "n/a (needs statistics)",
                   "no formation time", "end of the run"], loc="lower center", ncol=5,
               fontsize=6.5, frameon=False, bbox_to_anchor=(0.5, 0.0))
    fs.save(fig, os.path.join(out, "fig_scouting_predictions"))
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    def body(out, run_id=None):
        res = dict(run_id=run_id, **{"SR-1": sr1()},
                   S1=periodic("S1", 0.5, t_end_tH=30.0),
                   S2=periodic("S2", 0.03, t_end_tH=250.0))
        with open(os.path.join(out, "scouting_predictions.json"), "w") as f:
            json.dump(res, f, indent=1, default=float)
        write_md(res, os.path.join(out, "scouting_predictions.md"))
        figure(res, out)
        with open(os.path.join(out, "scouting_predictions.md")) as f:
            print(f.read())

    if a.out:
        os.makedirs(a.out, exist_ok=True)
        body(a.out)
        return
    import runlog
    inputs = [os.path.join(HERE, f) for f in ("scouting_table.py", "predict.py", "ltb2609.py",
                                              "emd_criteria.py")]
    inputs += [DATASET_2T, os.path.join(L.EXPBALL_DIR, "expball", "model.py"),
               os.path.join(L.EXPBALL_DIR, "expball", "exact.py")]
    with runlog.Run("criteria2: prediction tables for SR-1 (data set 2t) and the periodic "
                    "scouting runs S1 (mu 0.5) and S2 (mu 0.03)", "scouting", inputs) as run:
        print("run", run.run_id)
        body(run.out, run.run_id)


if __name__ == "__main__":
    main()
