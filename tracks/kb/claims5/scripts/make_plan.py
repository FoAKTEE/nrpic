#!/usr/bin/env python3
"""Package claims5: build the write plan plans/P1_claims5.json from work/verdicts_T.tsv.

    python3 -I make_plan.py [--out plans/P1_claims5.json]

Each verdict row becomes one action of tracks/kb/claims3/scripts/apply.py:
  right / right_locator -> verify (with the extended locator of LOCATOR_PLUS where given);
  not right             -> supersede, by a new whole-sentence text (SUCCESSOR, read at the
                           source lines named in its locator) or by an existing claim (TO);
  plus one 'add' (ADD): Track C's own reproduction split off claim 230, label judgement.
Every successor text states only what its locator lines say; a track's reading keeps the
track's name and the label judgement. Standard library only; reads nothing under kb-data.
"""
import argparse
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)

LOCATOR_PLUS = {
    324: "2009.08163v1:paper.tex:L941-956",
    173: "2403.15126v1:pII_GW_Vir_C2_Arx.tex:L610-612",
    639: "0710.0879v2:first.tex:L141-146; 0710.0879v2:first.tex:L161-176; 0710.0879v2:first.tex:L288-291",
    334: "1305.2619v1:SFWpaper.tex:L120; 1305.2619v1:SFWpaper.tex:L376-384",
    445: "2402.02178v1:main.tex:L94-112; 2402.02178v1:main.tex:L216-234",
    32: "2609.14218v1:MDPBH.tex:L911-919",
    80: "2211.13950v3:MD_threshold10.tex:L252-263; 2211.13950v3:MD_threshold10.tex:L282",
}

# successors: id -> (label, locator, text)
SUCCESSOR = {
    182: ("fulltext", "2403.15126v1:pII_GW_Vir_C2_Arx.tex:L1030-1031",
          "In arXiv:2403.15126, when sigma is decreased with the sigma-dependent ratio <t_max>/t_k kept fixed, "
          "the shape of the average GW spectrum nearly does not change: it decreases roughly as sigma^(7/2), and "
          "its peak shifts to smaller frequencies as omega_peak ~ sigma^(3/2) (pII_GW_Vir_C2_Arx.tex L1030-1031)."),
    234: ("fulltext", "2108.11967v2:main.tex:L283",
          "arXiv:2108.11967 compares with the fully relativistic N-body simulations of Shapiro and Teukolsky "
          "(1985), in which the system can collapse to a black hole at fractional binding energy epsilon ~ 0.035 "
          "and Z(0) ~ 0.5, in excellent agreement with its semi-analytical method; since in several unstable "
          "cases of those simulations the adiabatic index condition is not satisfied, it calls the criterion "
          "gamma_cr > <gamma> 'a sufficient, but may not be necessary condition' (main.tex L283)."),
    193: ("fulltext", "2605.04487v2:main_v3.tex:L2234-2238",
          "arXiv:2605.04487 builds its initial particle load by a glass-like relaxation and a quadrupole "
          "clean-up designed to reduce artificial GW emission seeded purely by shot noise: the residual initial "
          "quadrupole is |Q_ij| ~ 1e-1 (code units) for a purely random realization and as small as ~1e-14 "
          "after the procedure (main_v3.tex L2234-2238)."),
    329: ("judgement", "2602.17487v1:results.tex:L18; 2602.17487v1:methods.tex:L196",
          "Track C reads arXiv:2602.17487, the continuum Vlasov solver that the brief names for collisions, as "
          "a collisionless solver: its Vlasov equation is reduced 'in the absence of collisions or sources' "
          "(results.tex L18) and its validation runs are counter-streaming instabilities in collisionless "
          "plasmas (methods.tex L196) [JUDGEMENT: Track C's reading]."),
    230: ("fulltext", "2108.11967v2:main.tex:L122-146",
          "arXiv:2108.11967 writes the number density, density, energy density and pressure of its truncated "
          "distribution as integrals I(b, w) (eqs. eos and integrals, main.tex L122-139) and closes the model "
          "with the Tolman-Oppenheimer-Volkoff equations for M(r) and w(r), with M = 0 and w = w(0) at r = 0 "
          "and M = M(R), w = 0 at r = R (L141-146)."),
    87: ("fulltext", "2211.13950v3:MD_threshold10.tex:L366-375",
         "arXiv:2211.13950 rewrites its PBH non-formation condition, depending on whether the halos of the "
         "small scale k form before the collapse of the PBH scale k~, as delta_ent < k~^4/k^4 for Case I "
         "(k^2 delta_ent > k~^2 delta~_ent) and delta_ent > (k/k~) delta~_ent^(5/2) for Case II "
         "(k^2 delta_ent < k~^2 delta~_ent), ignoring factors of order unity (MD_threshold10.tex L366-375)."),
    242: ("fulltext", "2601.17117v2:SIDM_MS.tex:L341-344",
          "arXiv:2601.17117 closes its equations with the ideal-gas law P = (gamma - 1) epsilon rho, gamma the "
          "adiabatic index, and states a value only for the non-relativistic case, gamma = 5/3 "
          "(SIDM_MS.tex L341-344)."),
    352: ("fulltext", "1901.08528v2:PBH-UCMH-ArXiv-v2.tex:L462-468",
          "In appendix A of arXiv:1901.08528, integrating over the radial orbits of the WIMPs after they "
          "decouple from the background expansion gives an r^(-9/4) profile like that of its eq. (profile) "
          "but 53 per cent denser (PBH-UCMH-ArXiv-v2.tex L462-468)."),
    19: ("judgement", "2609.14218v1:MDPBH.tex:L1064-1074; 2609.14218v1:MDPBH.tex:L1132",
         "Track A reads arXiv:2609.14218 as placing one particle per grid cell: the paper states no particle "
         "number (its only count, in a figure caption, is a plotting reduction to 1/80, MDPBH.tex L1132), "
         "aligns the particles regularly so that they fill the region with no space and no overlap "
         "(L1065-1066), and gives each particle the mass E sqrt(gamma) Delta x Delta y Delta z / Gamma_p of a "
         "cell (L1070-1074) [JUDGEMENT: Track A's reading]."),
    33: ("fulltext", "2609.14218v1:MDPBH.tex:L911-919; 2609.14218v1:MDPBH.tex:L984-988",
         "arXiv:2609.14218 writes its analytic criterion for PBH formation as mu > h-hat(e,p) 6a^2H^2/k^2 with "
         "h-hat(e,p) = (15/pi) e (1+3e+p)^(-2) E(sqrt(1-(e+p)^2/(4e^2))) (MDPBH.tex L911-919), and draws it at "
         "aH = k/sqrt(6) (blue solid line of its threshold figure), a line that does not take into account the "
         "effect of the inhomogeneity discussed in its spherical section (L984-988)."),
    484: ("fulltext", "2611.12831v1:main.tex:L864; 2611.12831v1:main.tex:L945",
          "For its fiducial Oppenheimer-Snyder collapse (section of main.tex L864), arXiv:2611.12831 measures "
          "the final black-hole mass after particle excision with the Fastflow module of AthenaK and the "
          "external BHaHAHA finder and reports a relative error Delta M/M_ADM <~ 1e-3 against the initial ADM "
          "mass (L945)."),
    252: ("fulltext", "2601.17117v2:SIDM_MS.tex:L520; 2601.17117v2:SIDM_MS.tex:L672-676",
          "arXiv:2601.17117 names two limits of its fluid model: a velocity-dependent cross-section, expected "
          "as high as sigma >~ 100 cm^2/g at low velocities and suppressed at v >~ 1e3 km/s, could "
          "fundamentally alter the late-time evolution (SIDM_MS.tex L520); and where the relaxation time "
          "approaches the shell-crossing time, a rigorous treatment requires the full collisional Boltzmann "
          "equation, which the paper replaces by the phenomenological pressure factor "
          "f_P = (t_r/t_sc + 1)^(-1) (L672-676)."),
    248: ("fulltext", "2601.17117v2:SIDM_MS.tex:L457",
          "arXiv:2601.17117 finds that, although its formalism includes bulk velocity, the core evolution in "
          "the late non-relativistic self-similar phase can still be approximated as quasi-static, because the "
          "bulk velocity in the deep core stays negligible against the local sound speed; non-equilibrium "
          "effects matter only in the rapidly expanding outer envelope (SIDM_MS.tex L457)."),
}
TO = {684: 910, 685: 910, 451: 638, 306: "succ:234"}
ADD = {"after": 230, "text": (
    "Track C reproduces the equilibrium sequence of arXiv:2108.11967 with "
    "tracks/C-sidm/scope/scripts/king_sequence.py (run C-sidm-20261115-115348-eb8b752) "
    "[JUDGEMENT: Track C's run, not re-run by kb]."),
    "label": "judgement", "kind": "result", "paper": "2108.11967", "locator": "2108.11967v2:main.tex:L122-146",
    "track": "C-sidm"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(PKG, "plans", "P1_claims5.json"))
    a = ap.parse_args()
    with open(os.path.join(PKG, "work", "verdicts_T.tsv")) as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    acts, made = [], {}
    for r in rows:
        cid = int(r["claim_id"])
        ev = f"claims5 T (k={r['k']}): {r['verdict']}{' [borderline]' if r['borderline'] == '1' else ''}; {r['note']}"
        if r["right"] == "1":
            x = {"do": "verify", "id": cid, "evidence": ev}
            if cid in LOCATOR_PLUS:
                x["locator"] = LOCATOR_PLUS[cid]
            acts.append(x)
            continue
        if cid in SUCCESSOR:
            label, loc, text = SUCCESSOR[cid]
            made[cid] = len(acts)
            acts.append({"do": "supersede", "id": cid, "evidence": ev, "text": text, "label": label,
                         "locator": loc, "origin": "tracks/kb/claims5"})
            if ADD["after"] == cid:
                acts.append({"do": "add", "text": ADD["text"], "label": ADD["label"], "kind": ADD["kind"],
                             "paper": ADD["paper"], "locator": ADD["locator"], "track": ADD["track"],
                             "origin": "tracks/kb/claims5",
                             "evidence": "claims5: C's run part of claim 230, split off (wrong_label); the run id "
                                         "and script path are from 230's text, the script exists on track/C-sidm"})
        elif cid in TO:
            to = TO[cid]
            if isinstance(to, str):
                to = "@%d" % made[int(to.split(":")[1])]
            acts.append({"do": "supersede", "id": cid, "evidence": ev, "to": to})
        else:
            raise SystemExit(f"no action for not-right claim {cid}")
    plan = {"by": "kb-claims5",
            "note": "claims5: verdicts of the 131 unread cited machine-located claims (class T of claims4, "
                    "k = 48-178 of order run kb-20261128-003945-e1d65ba); JOURNAL.md entry 2, work/verdicts_T.tsv",
            "actions": acts}
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as f:
        json.dump(plan, f, indent=1)
        f.write("\n")
    n = {}
    for x in acts:
        k = x["do"] + ("+loc" if x.get("locator") and x["do"] == "verify" else "") + ("->id" if "to" in x else "")
        n[k] = n.get(k, 0) + 1
    print(json.dumps({"actions": len(acts), "by_kind": n}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
