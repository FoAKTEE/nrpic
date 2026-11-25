"""Step (4) of the package: my numbers against the lead's reader (zeta/zeta_reader.py, run
E-20261125-161456-8d3f43c), per quantity, after my own numbers existed (JOURNAL entry 3).

The lead's Z1 is taken at the lead's own background state of N_f (DOP853 from the deck's slice),
with phi_e from the same background, eps = 4 x the box's s = 1/4 spread and five-point stencils;
here my variational map and my long-double finite differences are evaluated at exactly that
state, that end surface and those eps, so the comparison is like with like.

Usage: compare_lead.py <lead zeta_tests.json> <my pairs.json> <deck> <outdir>
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import zv_lib as Z  # noqa: E402
from analyse_pairs import deck_value  # noqa: E402

LD = Z.LD


def digits(a, b):
    a, b = float(a), float(b)
    if a == b:
        return 16.0
    return float(-np.log10(abs(a / b - 1)))


def main(lead_json, mine_json, deck, out):
    os.makedirs(out, exist_ok=True)
    L = json.load(open(lead_json))
    M = json.load(open(mine_json))
    pot = Z.Inflection(float(deck_value(deck, "scalar_field", "lambda")),
                       float(deck_value(deck, "scalar_field", "vev")))
    pf, pif = LD(L["bg_Nf"]["phi"]), LD(L["bg_Nf"]["Pi"])
    Hf = np.sqrt(Z.hubble2_from_pi(pot, pf, pif))     # the lead's Z1 states use Friedmann H
    phi_e = LD(L["phi_e"])
    N0, Na, Nab, _ = Z.map_derivatives(pot, pf, pif / Hf, phi_e, 1e-3)
    # derivatives in (phi, Pi) with H from Friedmann at each state (the lead's convention for Z1):
    # y0 = Pi/H_F(phi, Pi); its derivatives by central differences of the closed form in long double
    def y0(p, P):
        return P / np.sqrt(Z.hubble2_from_pi(pot, p, P))
    hp, hP = LD(1e-6) * abs(pf), LD(1e-4) * pif
    yp = (y0(pf + hp, pif) - y0(pf - hp, pif)) / (2 * hp)
    yP = (y0(pf, pif + hP) - y0(pf, pif - hP)) / (2 * hP)
    ypp = (y0(pf + hp, pif) + y0(pf - hp, pif) - 2 * y0(pf, pif)) / hp ** 2
    yPP = (y0(pf, pif + hP) + y0(pf, pif - hP) - 2 * y0(pf, pif)) / hP ** 2
    ypP = (y0(pf + hp, pif + hP) - y0(pf + hp, pif - hP) - y0(pf - hp, pif + hP)
           + y0(pf - hp, pif - hP)) / (4 * hp * hP)
    J = np.array([[LD(1), LD(0)], [yp, yP]], dtype=LD)              # d(phi0, y0)/d(phi, Pi)
    Hy = [np.zeros((2, 2), dtype=LD), np.array([[ypp, ypP], [ypP, yPP]], dtype=LD)]
    Npi = J.T @ Na
    Npipi = J.T @ Nab @ J + Na[1] * Hy[1]
    rows = {}
    r = L["pairs"]["q"]["slope_dPi_on_dphi"]
    for lab in ("phi", "Pi", "box", "Pi_x10", "Pi_x100"):
        z = L["Z1"][lab]
        ep, eP = LD(z["eps_phi"]), LD(z["eps_Pi"])
        d1 = Npi[0] * ep + Npi[1] * eP
        d2 = Npipi[0, 0] * ep * ep + 2 * Npipi[0, 1] * ep * eP + Npipi[1, 1] * eP * eP
        js = np.array([-2, -1, 0, 1, 2], dtype=LD)
        ph = pf + js * ep
        pi = pif + js * eP
        Hs = np.sqrt(Z.hubble2_from_pi(pot, ph, pi))
        n = Z.efolds_to_surface(pot, ph, pi / Hs, phi_e, 1e-3)
        c1 = (-n[4] + 8 * n[3] - 8 * n[1] + n[0]) / 12
        c2 = (-n[4] + 16 * n[3] - 30 * n[2] + 16 * n[1] - n[0]) / 12
        rows[lab] = dict(exact_c1=float(d1), exact_c2=float(d2), my_fd_c1=float(c1), my_fd_c2=float(c2),
                         lead_c1_reader=z["c1_reader"], lead_c2_reader=z["c2_reader"],
                         lead_c1_dop=z["c1_dop"], lead_c2_dop=z["c2_dop"],
                         rel_reader_c2=float(LD(z["c2_reader"]) / d2 - 1),
                         rel_dop_c2=float(LD(z["c2_dop"]) / d2 - 1),
                         rel_reader_c1=float(LD(z["c1_reader"]) / d1 - 1),
                         rel_dop_c1=float(LD(z["c1_dop"]) / d1 - 1),
                         rel_myfd_c2=float(c2 / d2 - 1), rel_myfd_c1=float(c1 / d1 - 1))
        print(lab, rows[lab], flush=True)
    d1b = Npi[0] + r * Npi[1]
    d2b = Npipi[0, 0] + 2 * r * Npipi[0, 1] + r * r * Npipi[1, 1]
    a_map_leadstate = float(0.5 * d2b / d1b ** 2)
    # per-quantity agreement of the lattice numbers (same dumps, independent code)
    q, h = L["pairs"]["q"], L["pairs"]["h"]
    mq, mh = M["Z"]["s1/4"], M["Z"]["s1/2"]
    lat = {
        "Z0 (s=1/4)": (q["Z0"], mq["Z0_ratio"]),
        "Z0 (s=1/2)": (h["Z0"], mh["Z0_ratio"]),
        "rms O_zeta (s=1/4)": (q["sigma_Oz"], mq["rms_zeta1"]),
        "a_zeta (s=1/4)": (q["a_zeta"], mq["a_zeta"]),
        "a_zeta (s=1/2)": (h["a_zeta"], mh["a_zeta"]),
        "a_R (s=1/4)": (q["a_R"], mq["a_R"]),
        "a_R (s=1/2)": (h["a_R"], mh["a_R"]),
        "box relation r": (q["slope_dPi_on_dphi"], mq["r_relation"]),
        "a_map along the relation (lead: DOP853 at its N_f state; mine: exact at the lockstep)":
            (L["Z2"]["a_map"], mq["map_along_relation"]["a_map"]),
        "a_map along the relation, both at the lead's N_f state (mine exact)":
            (L["Z2"]["a_map"], a_map_leadstate),
        "Z2(iii)": (L["Z2"]["iii"], mq["Z2iii"]),
        "Z2(iii')": (L["Z2"]["iii_prime"], mq["Z2iiiprime"]),
        "phi_e (lead: own background from the deck's slice; mine: same construction)":
            (L["phi_e"], M["end_surface_alt"]["phi_e_from_deck_slice"]),
    }
    latt = {k: dict(lead=float(a), mine=float(b), digits=digits(a, b)) for k, (a, b) in lat.items()}
    for k, v in latt.items():
        print(f"{k}: lead {v['lead']:.10g} mine {v['mine']:.10g} digits {v['digits']:.1f}")
    res = dict(lead_state=dict(phi=float(pf), Pi=float(pif), H_F=float(Hf), phi_e=float(phi_e)),
               lockstep_minus_lead_state=dict(dphi=M["background"]["phi_b"] - float(pf),
                                              rel_dPi=M["background"]["Pi_b"] / float(pif) - 1),
               exact_at_lead_state=dict(N=float(N0), N_phi=float(Npi[0]), N_Pi=float(Npi[1]),
                                        N_phiphi=float(Npipi[0, 0]), N_phiPi=float(Npipi[0, 1]),
                                        N_PiPi=float(Npipi[1, 1]), a_map_relation=a_map_leadstate),
               Z1=rows, lattice=latt)
    with open(os.path.join(out, "compare_lead.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    # figure
    sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "..", "python"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(8.0, 3.0))
    ax = axs[0]
    labs = list(rows)
    x = np.arange(len(labs))
    for key, c, m, lab in (("rel_reader_c2", fs.PAL["red"], "o", "lead's reader (RK4 in $\\phi$)"),
                           ("rel_dop_c2", fs.PAL["yellow"], "s", "lead's DOP853 in $t$ (Z1 reference)"),
                           ("rel_myfd_c2", fs.PAL["blue"], "^", "my long-double differences")):
        ax.semilogy(x, [max(abs(rows[k][key]), 1e-12) for k in labs], m, color=c, label=lab)
    ax.axhline(0.01, color=fs.PAL["green"], ls="--", lw=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([k.replace("_", "\n") for k in labs], fontsize=7)
    ax.set_ylabel("$|c_2/c_2^{\\rm exact} - 1|$ (5-point)")
    ax.set_title("Z1 second coefficient at the lead's $N_f$ state", fontsize=8)
    ax.legend(fontsize=6)
    ax = axs[1]
    ks = [k for k in latt if not k.startswith("phi_e")]
    dg = [latt[k]["digits"] for k in ks]
    ax.barh(np.arange(len(ks)), dg, color=fs.PAL["blue"])
    ax.set_yticks(np.arange(len(ks)))
    short = [k.split(" (lead")[0].replace(", both at the lead's N_f state (mine exact)", " (same state)")
             for k in ks]
    ax.set_yticklabels(short, fontsize=6)
    ax.set_xlabel("agreeing digits, lead vs mine")
    ax.invert_yaxis()
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "fig_compare_lead"))


if __name__ == "__main__":
    main(*sys.argv[1:5])
