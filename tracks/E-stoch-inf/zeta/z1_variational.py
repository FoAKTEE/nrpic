#!/usr/bin/env python3
"""Z1 and Z2(iii), (iii') with the expected values the verifier asked for (g3/zeta_verify/README.md Requests 1-2;
decision 0042 item 1; zeta/JOURNAL.md entry 8).

    z1_variational.py OUT --run <dir of E-20261125-153148-cfad424> --deck <usr_base.athinput>
                      --lead-json <zeta_tests.json of E-20261125-161456-8d3f43c>

Changes against zeta_reader.py's Z1 (which stays on record as run, FAILED as written along Pi alone):
(1) expected values: the exact first and second derivatives of N from the variational equations of the
    verifier's integrator (g3/zeta_verify/scripts/zv_lib.py map_derivatives, long double, RK4 in N, steps 1e-3
    and 5e-4), not a float64 DOP853 integration whose round-off floor (4-5e-10 in N) lies at the second-order
    change along Pi alone;
(2) the state: the box's own background, the lockstep record of the dump at N_f (phi_b, Pi_b, H of
    usr.sf.00001.modes), with the cells' convention v = Pi/H at fixed K (zeta_of), instead of the reader's own
    DOP853 background 0.03 e-folds away.
Reader: zeta_reader.py's V, dV, map_rk4 verbatim through ast, its phi_e, 4000 steps; five-point stencils at
+-eps, +-2 eps with the eps of the lead's record (box rms at s = 1). Expected c1 = g.d, c2 = d.Hess.d.
Writes OUT/z1_variational.json and OUT/fig_z1_variational.png (and .pdf).
"""
import argparse
import ast
import json
import os
import sys
import types

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TRK = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(TRK, "g3", "zeta_verify", "scripts"))
sys.path.insert(0, os.path.join(TRK, "repro", "figs", "figures"))
import zv_lib as Z  # noqa: E402
import figstyle as fs  # noqa: E402

LD = Z.LD


def lead_namespace(src, lam, vev, phi_e, msteps):
    tree = ast.parse(open(src).read())
    keep = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ("V", "dV", "map_rk4")]
    assert len(keep) == 3
    ns = dict(np=np, LAM=lam, VEV=vev, PHI_E=phi_e, SQ2=np.sqrt(2.0), PI4=4.0 * np.pi, PI8=8.0 * np.pi,
              a=types.SimpleNamespace(msteps=msteps))
    exec(compile(ast.Module(body=keep, type_ignores=[]), src, "exec"), ns)
    return ns


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--run", required=True)
    ap.add_argument("--deck", required=True)
    ap.add_argument("--lead-json", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    L = json.load(open(a.lead_json))
    lam, vev, phi_e = L["deck"]["lam"], L["deck"]["vev"], L["phi_e"]
    hdr = Z.read_modes_header(os.path.join(a.run, "zp4", "usr.sf.00001.modes"))
    phi_b, Pi_b, Hl = hdr["phi_b"], hdr["Pi_b"], hdr["H"]
    ns = lead_namespace(os.path.join(HERE, "zeta_reader.py"), lam, vev, phi_e, 4000)
    pot = Z.Inflection(lam, vev)
    der = {}
    for h in (1e-3, 5e-4):
        Nb, Na, Nab, _ = Z.map_derivatives(pot, LD(phi_b), LD(Pi_b) / LD(Hl), LD(phi_e), h)
        g, Hm = Z.to_phi_pi(Na, Nab, LD(Hl))
        der[h] = (np.array(g, dtype=float), np.array(Hm, dtype=float))
    g, Hm = der[1e-3]
    res = dict(state=dict(phi_b=phi_b, Pi_b=Pi_b, H=Hl, source="lockstep record zp4/usr.sf.00001.modes"),
               phi_e=phi_e, exact=dict(N_phi=g[0], N_Pi=g[1], N_phiphi=Hm[0, 0], N_phiPi=Hm[0, 1], N_PiPi=Hm[1, 1],
                                       step_change_rel=dict(
                                           N_phi=der[5e-4][0][0] / g[0] - 1, N_Pi=der[5e-4][0][1] / g[1] - 1,
                                           N_phiphi=der[5e-4][1][0, 0] / Hm[0, 0] - 1,
                                           N_PiPi=der[5e-4][1][1, 1] / Hm[1, 1] - 1)))
    js = np.array([-2, -1, 0, 1, 2], float)
    z1 = {}
    for lab in ("phi", "Pi", "box", "Pi_x10", "Pi_x100"):
        ep, eP = L["Z1"][lab]["eps_phi"], L["Z1"][lab]["eps_Pi"]
        n = ns["map_rk4"](phi_b + js * ep, (Pi_b + js * eP) / Hl)
        c1 = (-n[4] + 8 * n[3] - 8 * n[1] + n[0]) / 12.0
        c2 = (-n[4] + 16 * n[3] - 30 * n[2] + 16 * n[1] - n[0]) / 12.0
        d = np.array([ep, eP])
        e1 = float(g @ d)
        e2 = float(d @ Hm @ d)
        z1[lab] = dict(eps_phi=ep, eps_Pi=eP, c1_reader=float(c1), c2_reader=float(c2), c1_exact=e1, c2_exact=e2,
                       rel_c1=float(c1 / e1 - 1), rel_c2=float(c2 / e2 - 1),
                       old_rel_c1_vs_dop=L["Z1"][lab]["rel_c1"], old_rel_c2_vs_dop=L["Z1"][lab]["rel_c2"])
        print("Z1", lab, z1[lab], flush=True)
    res["Z1"] = z1
    res["Z1_pass"] = bool(all(abs(z1[k]["rel_c1"]) < 0.01 and abs(z1[k]["rel_c2"]) < 0.01 for k in ("phi", "Pi", "box")))
    res["Z1_old_pass_as_written"] = L["Z1_pass"]
    # Z2 (iii), (iii') with a_map at the lockstep state along the box relation (direction (1, r), r of the pairs)
    r = L["pairs"]["q"]["slope_dPi_on_dphi"]
    d = np.array([1.0, r])
    a_map = 0.5 * float(d @ Hm @ d) / float(g @ d) ** 2
    aq, aR = L["Z2"]["a_q"], L["Z2"]["a_R"]
    res["Z2"] = dict(r=r, a_map_lockstep=a_map, a_map_old=L["Z2"]["a_map"], a_q=aq, a_R=aR,
                     iii=aq / a_map - 1, iii_prime=(aq - (a_map - aR)) / a_map,
                     pass_iii=bool(abs(aq / a_map - 1) < 0.02), pass_iii_prime=bool(abs((aq - (a_map - aR)) / a_map) < 0.005),
                     old_iii=L["Z2"]["iii"], old_iii_prime=L["Z2"]["iii_prime"])
    print("Z2", res["Z2"], flush=True)
    with open(os.path.join(a.out, "z1_variational.json"), "w") as fp:
        json.dump(res, fp, indent=1)
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(fs.COLUMN_WIDTH * 1.3, 2.8))
    labs = ["phi", "Pi", "box", "Pi_x10", "Pi_x100"]
    x = np.arange(len(labs))
    tiny = 1e-12
    ax.semilogy(x - 0.15, [max(abs(z1[k]["old_rel_c2_vs_dop"]), tiny) for k in labs], "v", color=fs.SERIES[1],
                label=r"$c_2$: reader vs DOP853 at own background (as run)")
    ax.semilogy(x + 0.15, [max(abs(z1[k]["rel_c2"]), tiny) for k in labs], "o", color=fs.SERIES[0],
                label=r"$c_2$: reader vs variational at lockstep state")
    ax.semilogy(x + 0.15, [max(abs(z1[k]["rel_c1"]), tiny) for k in labs], "s", mfc="none", color=fs.SERIES[0],
                label=r"$c_1$: reader vs variational at lockstep state")
    ax.axhline(0.01, **fs.GUIDE)
    ax.text(4.3, 0.013, "bar 1%", fontsize=6.5, ha="right")
    ax.set_xticks(x)
    ax.set_xticklabels([r"$\phi$", r"$\Pi$", "box", r"$\Pi\times10$", r"$\Pi\times100$"])
    ax.set_ylabel("|relative difference|")
    ax.set_xlabel("direction of the stencil (eps = box rms; x10, x100 diagnostics)")
    ax.legend(fontsize=6, frameon=False, loc="upper left")
    ax.set_ylim(1e-9, 10)
    fig.tight_layout()
    fs.save(fig, os.path.join(a.out, "fig_z1_variational"))


if __name__ == "__main__":
    main()
