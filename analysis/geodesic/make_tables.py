#!/usr/bin/env python3
"""Print the Markdown tables of docs/results_geodesic.md from the result summaries.

Reads problems/kerr/results/kerr_summary.json and problems/schwarzschild/results/schw_summary.json
(written by analyze_kerr.py and analyze_schwarzschild.py) and prints one Markdown section per
table to stdout.

Usage: python3 analysis/geodesic/make_tables.py > /tmp/tables.md
"""

from __future__ import annotations

import numpy as np

from geo_common import (KERR_RESULTS, PAPER_PASSAGE, SCHW_RESULTS, STANDALONE_PASSAGE, fmt,
                        load_json)

PUSHER = {"mid": "midpoint", "bsym": "Boris sym", "bchol": "Boris chol"}
METRIC = {"ks": "analytic sph. KS", "cks": "analytic Cart. KS", "lat": "lattice dx=0.025",
          "bl": "analytic BL", "mesh": "mesh"}


def f2(v, nd=2):
    return fmt(v, nd)


def unconv(b):
    h = b.get("hist", {})
    if not h:
        return "-", "-"
    return str(h["n_unconverged_steps"]), str(h["max_iterations"])


def table(rows, head):
    out = ["| " + " | ".join(head) + " |", "|" + "|".join("---" for _ in head) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def part_c(K):
    C = K["C"]
    runs = C["runs"]
    print("### C1. Maximum relative invariant errors, dt = 0.01 M, t = 230 M\n")
    rows = []
    for pusher in ("mid", "bsym", "bchol"):
        for metric in ("ks", "lat", "cks"):
            b = runs.get(f"kerr_passage/{pusher}_{metric}_dt0.01")
            if b is None:
                continue
            key = f"{pusher}_{metric}"
            pap = PAPER_PASSAGE.get(key)
            sta = STANDALONE_PASSAGE.get(key)
            if key == "mid_ks":
                pap_s = "2.8e-8, round-off, 1.3e-7"
            else:
                pap_s = ", ".join(f"{v:.1e}" for v in pap) if pap else "-"
            sta_s = ", ".join(f"{v:.3e}" for v in sta) if sta else "-"
            nu, mi = unconv(b)
            rows.append([PUSHER[pusher], METRIC[metric], fmt(b["max_dE"]), fmt(b["max_dLz"]),
                         fmt(b["max_dQ"]), pap_s, sta_s, f"{nu} / {mi}"])
    print(table(rows, ["pusher", "metric input", "max dE/E", "max dLz/Lz", "max dQ/Q",
                       "paper (E, Lz, Q)", "standalone build (E, Lz, Q)",
                       "unconverged steps / max iter"]))
    print()
    print("### C2. Final-position error at t = 230 M vs dt\n")
    conv = C["dt_convergence_ks"]
    dts = sorted({d for c in conv.values() for d in c["dt"]})
    rows = []
    for metric in ("ks", "cks", "lat"):
        for pusher in ("mid", "bsym", "bchol"):
            c = conv.get(pusher if metric == "ks" else f"{pusher}_{metric}")
            if c is None:
                continue
            errs = dict(zip(c["dt"], c["err"]))
            rows.append([PUSHER[pusher], METRIC[metric]] + [fmt(errs.get(d), 2) for d in dts] +
                        [f"{c['order']:.3f}", ", ".join(f"{p:.2f}" for p in c["pairwise"])])
    print(table(rows, ["pusher", "metric"] + [f"dt={d:g}" for d in dts] +
                ["fitted order (all dt)", "pairwise orders"]))
    print()
    print("Interpolation effect alone: max |(r/M, theta, phi)_lattice - (r/M, theta, phi)_Cartesian"
          " analytic| at t = 230 M, same pusher and dt:\n")
    rows = []
    for pusher in ("mid", "bsym", "bchol"):
        c = conv.get(f"{pusher}_lat")
        if c is None or "lat_minus_cks_final" not in c:
            continue
        e = dict(zip(c["dt"], c["lat_minus_cks_final"]))
        rows.append([PUSHER[pusher]] + [fmt(e.get(d), 2) for d in dts])
    print(table(rows, ["pusher"] + [f"dt={d:g}" for d in dts]))
    print()
    print("Max relative energy error vs dt:\n")
    rows = []
    for metric in ("ks", "cks", "lat"):
        for pusher in ("mid", "bsym", "bchol"):
            c = conv.get(pusher if metric == "ks" else f"{pusher}_{metric}")
            if c is None:
                continue
            e = dict(zip(c["dt"], c["dE"]))
            rows.append([PUSHER[pusher], METRIC[metric]] + [fmt(e.get(d), 2) for d in dts])
    print(table(rows, ["pusher", "metric"] + [f"dt={d:g}" for d in dts]))
    print()
    print("Components (dr/M, dtheta, dphi) of the final error and invariants for every dt:\n")
    rows = []
    for name in sorted(runs):
        b = runs[name]
        m = b["meta"]
        nu, mi = unconv(b)
        rows.append([name.split("/")[1], fmt(b["final_pos_err"]),
                     ", ".join(f"{v:+.2e}" for v in b["final_pos_err_components"]),
                     fmt(b["max_dE"]), fmt(b["max_dLz"]), fmt(b["max_dQ"]),
                     f"{b['r_peri']:.6f}" if b.get("r_peri") else "-",
                     f"{b['t_peri']:.4f}" if b.get("t_peri") else "-",
                     f"{nu} / {mi}", f"{b['log'].get('cpu_time_s', 0):.1f}"])
    print(table(rows, ["run", "final err", "(dr, dth, dphi)", "max dE/E", "max dLz/Lz", "max dQ/Q",
                       "r_p / M", "t_p / M", "unconv / max it", "athena time [s]"]))
    ex = C["exact"]
    print(f"\nExact: r_p = {ex['r_peri']:.10f} M, t_p = {ex['t_peri']:.8f} M; final state "
          f"(r, theta, phi) = {ex['final_state']['x']}.\n")


def part_d(K):
    D = K["D"]["runs"]
    print("### D. CPU vs GPU\n")
    rows = []
    for name, b in sorted(D.items()):
        rows.append([name.split("/")[1], f"{b['n_records_cpu']} / {b['n_records_gpu']}",
                     fmt(b["max_dt"]), fmt(b["max_abs_dx"]), fmt(b["max_abs_du"]),
                     fmt(b["max_abs_d_rthph"]), fmt(b["final_abs_dx"]), str(b["bitwise_identical"]),
                     str(b["first_differing_record"]), fmt(b["max_dE"]), fmt(b["final_pos_err"])])
    print(table(rows, ["run", "records CPU/GPU", "max |dt|", "max |dx| (all records)",
                       "max |du|", "max |d(r,th,ph)|", "final |dx|", "bitwise identical",
                       "first differing record", "CPU max dE/E", "CPU final pos err"]))
    print()


def part_b(K):
    B = K["B"]
    print("### B. Boyer-Lindquist orbits (a = 0.9)\n")
    for key, lab in (("bl_equatorial_eccentric", "equatorial eccentric, t_end = 4550 M"),
                     ("bl_inclined", "inclined, t_end = 3850 M")):
        ex = B["exact"][key]
        print(f"**{lab}.** Exact: r in [{ex['radial_range'][0]:.6f}, {ex['radial_range'][1]:.6f}], "
              f"theta in [{ex['theta_range'][0]:.6f}, {ex['theta_range'][1]:.6f}], "
              f"T_r = {ex['periods']['T_r']:.6f} M, final (r, theta, phi) = "
              f"{[round(v, 9) for v in ex['final_state']['x']]}\n")
        rows = []
        for name, b in sorted(B["runs"].items()):
            if b["meta"]["orbit"] != key:
                continue
            nu, mi = unconv(b)
            extra = ""
            if key == "bl_inclined":
                extra = (f"{b['theta_range'][0]:.5f}-{b['theta_range'][1]:.5f}; "
                         f"{b['nodal_advance_mean']:.7f} (ref. {b['nodal_advance_mean_reference']:.7f})")
            rows.append([name.split("/")[1], f"{b['r_min']:.6f} - {b['r_max']:.6f}",
                         fmt(b["max_dE"]), fmt(b["max_dLz"]),
                         fmt(b["max_dQ"]) + ("" if b["dQ_relative"] else " (abs)"),
                         fmt(b["final_pos_err"]),
                         ", ".join(f"{v:+.2e}" for v in b["final_pos_err_components"]),
                         f"{b['periapsis_advance_mean']:.7f} ({b['periapsis_advance_mean_exact']:.7f})",
                         fmt(b["pericenter_time_err_max"], 1), extra, f"{nu} / {mi}",
                         f"{b['log'].get('cpu_time_s', 0):.0f}"])
        print(table(rows, ["run", "r range / M", "max dE/E", "max dLz/Lz", "max dQ/Q",
                           "final pos err", "(dr, dth, dphi)",
                           "periapsis advance / rad per T_r (exact)", "max |t_peri err|",
                           "theta range; mean nodal advance / rad (reference traj.)",
                           "unconv / max it", "time [s]"]))
        print()


def part_e(K):
    E = K["E"]
    print("### E. Kerr a = 0.9 on the mesh (inclined orbit in Cartesian KS, dt = 0.01 M, "
          "t = 600 M)\n")
    rows = []
    for name, b in sorted(E["runs"].items(), key=lambda kv: (kv[1]["meta"]["pusher"],
                                                            kv[1]["meta"]["metric"],
                                                            -(kv[1]["meta"].get("dx") or 0))):
        m = b["meta"]
        nu, mi = unconv(b)
        rec = b.get("reconstruction_err")
        rows.append([name.split("/")[1], PUSHER[m["pusher"]], METRIC[m["metric"]].split()[0]
                     if m["metric"] != "cks" else "analytic Cart. KS",
                     f"{m['dx']:g}" if m.get("dx") else "-",
                     fmt(b["max_dE"]), fmt(b["max_dLz"]), fmt(b["max_dQ"]),
                     fmt(b["final_pos_err"]), fmt(b["max_pos_err_checkpoints"]),
                     "-" if rec is None else f"{rec['alpha']:.1e} / {rec['beta']:.1e} / {rec['gamma']:.1e}",
                     f"{nu} / {mi}"])
    print(table(rows, ["run", "pusher", "metric", "dx/M", "max dE/E", "max dLz/Lz", "max dQ/Q",
                       "final pos err", "max pos err (checkpoints every 50 M)",
                       "reconstruction err alpha / beta / gamma", "unconv / max it"]))
    print()
    rows = []
    for k, c in E["dx_convergence"].items():
        rows.append([k, ", ".join(fmt(e) for e in c["err"]), f"{c['order']:.2f}",
                     ", ".join(f"{p:.2f}" for p in c["pairwise"]), f"{c['order_dE']:.2f}",
                     f"{c['order_dQ']:.2f}"])
    print(table(rows, ["series", "final err (dx = 0.5, 0.25, 0.125)" if False else
                       "final err (ascending dx)", "fitted order", "pairwise", "order dE",
                       "order dQ"]))
    print()
    rows = [[k, fmt(v["max_abs_dx"]), fmt(v["max_abs_du"]), str(v["bitwise_identical"])]
            for k, v in E["mesh_vs_lattice"].items()]
    print(table(rows, ["mesh run", "max |x_mesh - x_lattice|", "max |u_mesh - u_lattice|",
                       "bitwise identical"]))
    print()


def part_a(S):
    print("### A. Schwarzschild\n")
    orbs = S["orbits"]
    for k, o in orbs.items():
        inv = o["invariants"]
        print(f"- **{k}**: {o['description']}; E = {inv['E']!r}, L_z = {inv['Lz']!r}, "
              f"Q = {inv['Q']:.6g}, t_end = {o['t_end']} M; IC (ks) x = {o['initial_state']['ks']['x']},"
              f" u = {o['initial_state']['ks']['u']}; IC (cks) x = {o['initial_state']['cks']['x']},"
              f" u = {o['initial_state']['cks']['u']}")
    print()
    conv = S["dt_convergence"]
    dts = [0.08, 0.04, 0.02, 0.01, 0.005]
    print("#### A1. Final-position error vs dt, analytic metric\n")
    rows = []
    for k, c in conv.items():
        errs = dict(zip(c["dt"], c["final_err"]))
        rows.append([c["orbit"], PUSHER[c["pusher"]], c["metric"]] +
                    [fmt(errs.get(d)) for d in dts] +
                    [f"{c['order_final']:.3f}", ", ".join(f"{p:.2f}" for p in c["pairwise_final"]),
                     f"{c['order_max']:.3f}"])
    print(table(rows, ["orbit", "pusher", "metric"] + [f"dt={d:g}" for d in dts] +
                ["order (final)", "pairwise", "order (max over checkpoints)"]))
    print()
    print("#### A2. Invariant errors (max relative; Q absolute for the circular orbit)\n")
    rows = []
    for k, c in conv.items():
        byd = {d: (a, q, l) for d, a, q, l in zip(c["dt"], c["dE"], c["dQ"], c["dLz"])}
        rows.append([c["orbit"], PUSHER[c["pusher"]], c["metric"]] +
                    [("-" if d not in byd else
                      f"{fmt(byd[d][0], 1)} / {fmt(byd[d][1], 1)} / {fmt(byd[d][2], 1)}")
                     for d in dts] + [f"{c['order_dE']:.2f}"])
    print(table(rows, ["orbit", "pusher", "metric"] + [f"dE / dQ / dLz, dt={d:g}" for d in dts] +
                ["order dE"]))
    print()
    runs = S["runs"]
    nun = sum(1 for b in runs.values() if b.get("hist", {}).get("n_unconverged_steps", 0) > 0)
    mxit = max(b.get("hist", {}).get("max_iterations", 0) for b in runs.values())
    print(f"Runs with unconverged steps: {nun} of {len(runs)}; largest iteration count {mxit}.\n")
    print("#### A3. Mesh metric (dt = 0.01 M), errors vs dx\n")
    rows = []
    for k, c in S["dx_convergence"].items():
        a = c.get("analytic_cks_same_dt") or {}
        rows.append([c["orbit"], PUSHER[c["pusher"]], c["metric"]] +
                    [f"{fmt(e)} ({fmt(m, 1)})" for e, m in zip(c["final_err"], c["max_err"])] +
                    [f"{c['order_final']:.2f}", ", ".join(f"{p:.2f}" for p in c["pairwise_final"]),
                     f"{c['order_max']:.2f}",
                     ", ".join(fmt(v, 1) for v in c["dE"]), f"{c['order_dE']:.2f}",
                     f"{fmt(a.get('final_err'), 1)} / {fmt(a.get('dE'), 1)}"])
    print(table(rows, ["orbit", "pusher", "metric", "dx=0.125: final (max)", "dx=0.25", "dx=0.5",
                       "order final", "pairwise", "order max", "max dE/E (asc. dx)", "order dE",
                       "analytic Cart. KS same dt: final / dE"]))
    print()
    rows = []
    for name, b in sorted(runs.items()):
        if not name.startswith("schw_mesh/") or "reconstruction_err" not in b:
            continue
        r = b["reconstruction_err"]
        rows.append([name.split("/")[1], fmt(r["alpha"], 2), fmt(r["beta"], 2), fmt(r["gamma"], 2),
                     "/".join(unconv(b))])
    print(table(rows, ["mesh run", "max |alpha err|", "max |beta err|", "max |gamma err|",
                       "unconv / max it"]))
    print()
    rows = [[k, fmt(v["max_abs_dx"]), fmt(v["max_abs_du"]), str(v["bitwise_identical"])]
            for k, v in S["mesh_vs_lattice"].items()]
    print(table(rows, ["case", "max |x_mesh - x_lattice|", "max |u_mesh - u_lattice|",
                       "bitwise identical"]))
    print()


def main():
    K = load_json(KERR_RESULTS / "kerr_summary.json") if (KERR_RESULTS / "kerr_summary.json").exists() else {}
    S = load_json(SCHW_RESULTS / "schw_summary.json") if (SCHW_RESULTS / "schw_summary.json").exists() else {}
    if "C" in K:
        part_c(K)
    if "D" in K:
        part_d(K)
    if "B" in K:
        part_b(K)
    if "E" in K:
        part_e(K)
    if S:
        part_a(S)


if __name__ == "__main__":
    np.set_printoptions(precision=4)
    main()
