"""Lead DB updates D1 (wave 2b): claims layer changes asked for by the KB-G1 verifier and by the
tracks' messages, through the `kb claim` commands (each holds locks/kb-writer.lock).

  1. claim 25: locator rows rebuilt from its locator string (L1084 was missing; verifier defect 4);
  2. claims 249 and 313 (C-sidm): add 2601.17117v2 SIDM_MS.tex:L481, which carries all three
     numbers (C's message 20261119T151725Z, read by the lead);
  3. seven Track B statements on S2 key references (B's kb-request 20261115T191057Z): added with
     B's wording, then verified by the lead, who read each cited passage at the source;
  4. C's seed-fraction statement (astro-ph/0111176v3 SMBH_SIDM_Xiv2.tex:L289-291), read by the lead;
  5. four D-bh-dress annotations of 1707.06302 (D's kb-request 20261115T195105Z) as track
     results: (a), (b) judgement, (c), (d) to_verify, with D's run ids as evidence.
Writes db_updates.json (claim ids) into $NRPIC_RUN_DIR. Paper text is never written.
Usage: python3 -I w2b_db_updates.py WORKTREE
"""
import json
import os
import re
import subprocess
import sys

wt = sys.argv[1]
out = os.environ["NRPIC_RUN_DIR"]
KB = [os.path.join(wt, "kb", ".venv", "bin", "python"), "-I", os.path.join(wt, "kb", "bin", "kb")]
BY = "kb lead (wave 2b)"
log = []


def kb(*args):
    r = subprocess.run(KB + list(args), capture_output=True, text=True)
    log.append({"args": list(args), "rc": r.returncode, "stdout": r.stdout.strip()[-400:], "stderr": r.stderr.strip()[-400:]})
    if r.returncode not in (0,):
        print(json.dumps(log[-1]), file=sys.stderr)
    return r


res = {}
r = kb("claim", "relocate", "25", "--by", BY, "--evidence", "KB-G1 verifier defect 4 (run kb-20261119-142448-3ea268d)",
       "--locator", "2609.14218v1:MDPBH.tex:L1084; 2609.14218v1:MDPBH.tex:L1101-1103")
res["relocate_25"] = r.stdout.strip()
for cid in ("249", "313"):
    r = kb("claim", "relocate", cid, "--by", BY,
           "--evidence", "C-sidm message 20261119T151725Z: L481 carries M_BH ~ 200 M_sun, 3e-8 and 580 t_0",
           "--locator", "2601.17117v2:SIDM_MS.tex:L476; 2601.17117v2:SIDM_MS.tex:L481")
    res[f"relocate_{cid}"] = r.stdout.strip()

B = [
    ("1002.3278", "1002.3278v1:JLM_gw_v2.tex:L111-124",
     "GWs from pre-reheating structure: computed in the linear limit, estimated for halo collapse, tidal "
     "interactions, evaporation and turbulence"),
    ("2212.00425", "2212.00425v2:main.tex:L82",
     "N-body inflaton-halo simulations extended to GW emission; spectrum well matched by semi-analytic estimates "
     "from halo collapse and tidal evolution"),
    ("2312.12499", "2312.12499v2:main.tex:L107-115",
     "Hybrid N-body and lattice simulation; nonlinearity enhances GW production up to at least the inverse "
     "light-crossing time of the largest halos; a fully relativistic treatment is needed at higher frequencies (115)"),
    ("1704.03500", "1704.03500v1:GW2nd_ApJ.tex:L245",
     "Induced second-order tensor modes are gauge dependent; the power spectrum depends on the hypersurface condition"),
    ("2012.14016", "2012.14016v2:almostgaugeindependentarxiv_revised_2.tex:L92-102",
     "Newton (shear-free) gauge suitable; induced GW spectrum invariant under reasonable gauge changes once the "
     "source is inactive; in dust domination a particular solution can be gauged away while the source is active"),
    ("2610.08045", "2610.08045v1:main.tex:L40-49",
     "Third-order induced GWs in matter domination: kernels grow secularly, Omega^(3) ~ x^6 against "
     "Omega^(2) ~ x^2 at x = k eta >> 1"),
    ("2109.01398", "2109.01398v2:template_review.tex:L109",
     "Review of induced GWs: general formulation, compact formulas, non-standard expansion histories"),
]
res["B"] = []
for pid, loc, text in B:
    r = kb("claim", "add", "--text", text, "--paper", pid, "--locator", loc, "--label", "to_verify", "--kind", "result",
           "--by", BY, "--track", "B-emd-gw",
           "--origin", "B-emd-gw kb-request 20261115T191057Z; tracks/B-emd-gw/stage/G0/EVIDENCE.md, section Wave 2",
           "--evidence", "B lead read the abstract at the source (snapshot kb-20261115-44b7406)")
    m = re.search(r"claim (\d+) added", r.stdout)
    cid = m.group(1) if m else None
    v = kb("claim", "verify", cid, "--by", BY, "--locator", loc,
           "--evidence", "kb lead read the cited lines at the source on 2026-11-19; supported as worded") if cid else None
    res["B"].append({"paper": pid, "claim": cid, "verify": v.stdout.strip() if v else None})

r = kb("claim", "add", "--text", "The collapsing core holds 1e-8 to 1e-6 of the total halo mass (seed fraction)",
       "--paper", "astro-ph/0111176", "--locator", "astro-ph/0111176v3:SMBH_SIDM_Xiv2.tex:L289-291",
       "--label", "to_verify", "--kind", "number", "--by", BY, "--track", "C-sidm",
       "--origin", "C-sidm message 20261119T151725Z item 1 (row 'Seed fraction 1e-8 to 1e-6')",
       "--evidence", "C lead gave the file name")
m = re.search(r"claim (\d+) added", r.stdout)
res["C_seed"] = m.group(1) if m else None
if res["C_seed"]:
    v = kb("claim", "verify", res["C_seed"], "--by", BY, "--locator", "astro-ph/0111176v3:SMBH_SIDM_Xiv2.tex:L289-291",
           "--evidence", "kb lead read the cited lines at the source on 2026-11-19; supported as worded")
    res["C_seed_verify"] = v.stdout.strip()

D = [
    ("judgement", "1707.06302v2:kerrdm.tex:L1372-1377",
     "Erratum (D-bh-dress): eq. (lmax) has a sign typo; the root must contain a^2 + x(x - 2) = Delta(x)",
     "run D-bh-dress-20261115-171615-8adbbdd"),
    ("judgement", "1707.06302v2:kerrdm.tex:L584; 1707.06302v2:kerrdm.tex:L624",
     "Erratum (D-bh-dress): figure figequator1 is drawn with 1/4 of the prefactor printed in the equatorial-current "
     "equation (ratio 0.2500-0.2505 at a = 0, 0.5, 0.8)", "run D-bh-dress-20261115-171615-8adbbdd"),
    ("to_verify", "1707.06302v2:kerrdm.tex:L787",
     "D-bh-dress: the constant-f theta = pi/3 curve of fig_rho_theta is not reproducible inside 8 Gm (rises 1-1.5 Gm "
     "further out; peak value agrees to 0.2 per cent)", "run D-bh-dress-20261115-171615-8adbbdd"),
    ("to_verify", "1707.06302v2:kerrdm.tex:L936",
     "D-bh-dress: the Hernquist Kerr curves lie 4 per cent above an independent recomputation at the a = 0.8 "
     "equatorial peak (3.922e18 against 4.083e18 GeV/cm^3); cause open", "run D-bh-dress-20261115-171615-8adbbdd"),
]
res["D"] = []
for label, loc, text, ev in D:
    r = kb("claim", "add", "--text", text, "--paper", "1707.06302", "--locator", loc, "--label", label,
           "--kind", "result", "--by", BY, "--track", "D-bh-dress",
           "--origin", "D-bh-dress kb-request 20261115T195105Z", "--evidence", ev)
    m = re.search(r"claim (\d+) added", r.stdout)
    cid = m.group(1) if m else None
    rl = kb("claim", "relocate", cid, "--by", BY, "--locator", loc, "--evidence", "locator rows of a track result") \
        if cid else None
    res["D"].append({"claim": cid, "label": label, "relocate": rl.stdout.strip() if rl else None})
res["stats"] = kb("claim", "stats", "--json").stdout
with open(os.path.join(out, "db_updates.json"), "w") as f:
    json.dump({"result": res, "log": log}, f, indent=1)
print(json.dumps(res, indent=1)[:4000])
sys.exit(0 if all(e["rc"] == 0 for e in log) else 1)
