"""Request 3 of the README, closed here: the lead's map (zeta/zeta_reader.py: V, dV, map_rk4, taken
verbatim from its source with the ast module, not rewritten) against my map (zv_lib) at G3
amplitudes, |zeta| up to 3 e-folds (sigma_lin of the G3 box 0.494, so 6 sigma).

States: (a) along the box's linear relation dPi = r dphi from the lockstep state at N_f;
(b) on the background trajectory itself, the lockstep state moved by tau e-folds with my FKG,
where N = N_b - tau exactly (a property, not a reference code). Both maps use the lead's phi_e
and v = Pi/H_b (fixed K, as zeta_of in the lead's reader).

Usage: large_amp.py <lead zeta_reader.py> <lead zeta_tests.json> <my pairs.json> <deck> <outdir>
"""
import ast
import json
import os
import sys
import types

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import zv_lib as Z  # noqa: E402
from analyse_pairs import deck_value  # noqa: E402

LD = Z.LD


def lead_namespace(src_path, lam, vev, phi_e, msteps=4000):
    tree = ast.parse(open(src_path).read())
    keep = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ("V", "dV", "map_rk4")]
    assert len(keep) == 3
    ns = dict(np=np, LAM=lam, VEV=vev, PHI_E=phi_e, SQ2=np.sqrt(2.0), PI4=4.0 * np.pi, PI8=8.0 * np.pi,
              a=types.SimpleNamespace(msteps=msteps))
    exec(compile(ast.Module(body=keep, type_ignores=[]), src_path, "exec"), ns)
    return ns


def main(lead_src, lead_json, mine_json, deck, out):
    os.makedirs(out, exist_ok=True)
    lam = float(deck_value(deck, "scalar_field", "lambda"))
    vev = float(deck_value(deck, "scalar_field", "vev"))
    L = json.load(open(lead_json))
    M = json.load(open(mine_json))
    phi_e = L["phi_e"]
    ns = lead_namespace(lead_src, lam, vev, phi_e)
    pot = Z.Inflection(lam, vev)
    bg = M["background"]
    phi_b, Pi_b, Hb = bg["phi_b"], bg["Pi_b"], bg["H_lockstep"]
    r = M["Z"]["s1/4"]["r_relation"]
    d1 = M["Z"]["s1/4"]["map_along_relation"]["d1"]
    zs = np.linspace(-3.0, 3.0, 25)
    res = {}
    # (a) along the linear relation
    dphi = zs / d1
    ph = phi_b + dphi
    pi = Pi_b + r * dphi
    NL = np.asarray(ns["map_rk4"](ph, pi / Hb), dtype=float)
    NM = Z.efolds_to_surface(pot, ph.astype(LD), (pi / Hb).astype(LD), LD(phi_e), 1e-3)
    NM2 = Z.efolds_to_surface(pot, ph.astype(LD), (pi / Hb).astype(LD), LD(phi_e), 5e-4)
    res["relation"] = dict(zeta1=zs.tolist(), N_lead=NL.tolist(), N_mine=[float(v) for v in NM],
                           diff=[float(LD(a) - b) for a, b in zip(NL, NM)],
                           mine_step_change=[float(a - b) for a, b in zip(NM2, NM)])
    # (b) on the trajectory: states moved by tau, N = N_b - tau exactly
    taus = np.linspace(-3.0, 3.0, 13)
    pts = []
    for tau in taus:
        p, y = Z.integrate_to_N(pot, LD(phi_b), LD(Pi_b) / LD(Hb), LD(tau), 1e-4) if tau != 0 else \
            (LD(phi_b), LD(Pi_b) / LD(Hb))
        pts.append((p, y))
    ph2 = np.array([float(p) for p, _ in pts])
    y2 = np.array([float(y) for _, y in pts])
    NL2 = np.asarray(ns["map_rk4"](ph2, y2), dtype=float)
    NM3 = Z.efolds_to_surface(pot, np.array([p for p, _ in pts], dtype=LD),
                              np.array([y for _, y in pts], dtype=LD), LD(phi_e), 1e-3)
    N0 = NM3[len(taus) // 2]
    res["trajectory"] = dict(tau=taus.tolist(), N_lead=NL2.tolist(), N_mine=[float(v) for v in NM3],
                             lead_minus_exact=[float(LD(a) - (LD(NL2[len(taus) // 2]) - LD(t)))
                                               for a, t in zip(NL2, taus)],
                             mine_minus_exact=[float(b - (N0 - LD(t))) for b, t in zip(NM3, taus)])
    da = np.array(res["relation"]["diff"])
    res["summary"] = dict(max_abs_diff_relation=float(np.abs(da).max()),
                          max_abs_diff_relation_mean_removed=float(np.abs(da - da.mean()).max()),
                          max_abs_lead_minus_exact_traj=float(np.max(np.abs(res["trajectory"]["lead_minus_exact"]))),
                          max_abs_mine_minus_exact_traj=float(np.max(np.abs(res["trajectory"]["mine_minus_exact"]))),
                          max_abs_mine_step_change=float(np.max(np.abs(res["relation"]["mine_step_change"]))))
    print(json.dumps(res["summary"], indent=1))
    with open(os.path.join(out, "large_amp.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "..", "python"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(7.0, 3.0))
    ax = axs[0]
    ax.plot(zs, np.abs(da - da.mean()), "o", color=fs.PAL["red"], ms=3, label="lead $-$ mine (mean removed)")
    ax.plot(zs, np.abs(res["relation"]["mine_step_change"]), "s", color=fs.PAL["blue"], ms=3, mfc="none",
            label="mine: step $10^{-3}\\to 5\\times10^{-4}$")
    ax.set_yscale("log")
    ax.set_xlabel("$\\zeta_1$ along the box relation (e-folds)")
    ax.set_ylabel("$|\\Delta N|$")
    ax.axhline(0.494e-4, color=fs.PAL["green"], ls="--", lw=0.8, label="$10^{-4}\\sigma_{\\rm lin}$ (G3)")
    ax.legend(fontsize=6)
    ax = axs[1]
    ax.plot(taus, np.maximum(np.abs(res["trajectory"]["lead_minus_exact"]), 1e-16), "o", color=fs.PAL["red"],
            ms=3, label="lead's map")
    ax.plot(taus, np.maximum(np.abs(res["trajectory"]["mine_minus_exact"]), 1e-16), "s", color=fs.PAL["blue"],
            ms=3, mfc="none", label="my map")
    ax.set_yscale("log")
    ax.set_xlabel("shift $\\tau$ along the trajectory (e-folds)")
    ax.set_ylabel("$|N - (N_b - \\tau)|$")
    ax.legend(fontsize=6)
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "fig_large_amp"))


if __name__ == "__main__":
    main(*sys.argv[1:6])
