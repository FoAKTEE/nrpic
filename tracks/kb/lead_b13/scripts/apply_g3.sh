#!/bin/bash
# kb lead batch 13: claims named by the KB-G3 verifier (682, 781, 714, 809, 804) and the claims the
# ingest4 papers serve (409, 447, 449, 450, 452). Every passage was read by the lead at the
# locator given (raw TeX under kb-data/raw/arxiv, INSPIRE records under kb-data/meta/inspire).
# Run inside nrpic-run (writes $NRPIC_RUN_DIR/log.txt, before.tsv, after.tsv).
cd /data/haiyangw/nrpic/wt/kb || exit 2
test -n "${NRPIC_RUN_DIR:-}" || { echo 'not inside nrpic-run'; exit 2; }
KB="python3 -I kb/bin/kb"
BY=kb-lead-b13
IDS="682 781 714 809 804 409 447 449 450 452"
fail=0
snap() { for c in $IDS "$@"; do $KB claim show "$c" | python3 -I -c 'import json,sys; d=json.load(sys.stdin); print(d["claim_id"], d["label"], d["status"], sum(1 for l in d.get("locators",[]) if l.get("resolved")), len(d.get("locators",[])), sep="\t")'; done; }
snap > "$NRPIC_RUN_DIR/before.tsv"

# 682: the claim text gives the 15 per cent to the Gondolo-Silk distribution and says D read its
# numbers off Fig. 1; the source gives the 15 per cent to the 4Gm variant, and D computed both.
out=$($KB claim add --by $BY --track D-bh-dress --label fulltext --kind number --paper 1305.2619 \
  --origin tracks/kb/stage/KB-G3/VERIFIER.md \
  --locator '1305.2619v1:SFWpaper.tex:L443' \
  --evidence 'supersedes 682 (verifier KB-G3 item 1a); read at 1305.2619v1 SFWpaper.tex L443; D values in run D-bh-dress-20261115-145636-5259f48 reference.json constf' \
  --text 'arXiv:1305.2619 (SFWpaper.tex L443): the Gondolo-Silk distribution vanishes at r = 8Gm and is "a factor of three" smaller at its peak than the fully relativistic one; replacing 8Gm by 4Gm in the Gondolo-Silk formula gives a distribution that peaks "about 15%" higher than the numerical (relativistic) result. D-bh-dress computed the two numbers as 2.59 (relativistic peak over Gondolo-Silk peak) and 9.2 per cent (4Gm variant over relativistic) in run D-bh-dress-20261115-145636-5259f48 (reference.json, constf: 2.5897, 0.0922); they are not read off Fig. 1.') || fail=1
echo "$out"; N682=$(echo "$out" | sed -n 's/^claim \([0-9]*\) added$/\1/p')
test -n "$N682" && $KB claim relocate "$N682" --by $BY --locator '1305.2619v1:SFWpaper.tex:L443' || fail=1
$KB claim refute 682 --by $BY --evidence "wrong as worded (verifier KB-G3 item 1a, confirmed by the lead at 1305.2619v1 SFWpaper.tex L443): the 15 per cent belongs to the 4Gm variant, not to the Gondolo-Silk distribution; D's 2.59 and 9.2 per cent are computed in run D-bh-dress-20261115-145636-5259f48, not read off Fig. 1. The paper is not refuted, the claim text is. Superseded by claim $N682." || fail=1

# 781 (brief L426): whether NRPIC keeps AthenaK's single time step for all levels. Answer yes.
$KB claim verify 781 --by $BY --locator '2611.12831v1:main.tex:L75; 2611.12831v1:main.tex:L676' \
  --evidence 'answered yes (verifier KB-G3 item 1c): 2611.12831v1 main.tex L75 (caption of the NRPIC cycle) "Particles and fields share a common global time step"; L676 one timestep advances the geometry, then the particles. Only the time-step part is supported; "slows everything down" is the brief'"'"'s inference.' || fail=1

# 714 (brief L113): whether the full text of 2611.12831 discusses cosmologization. Answer no.
out=$($KB claim add --by $BY --track brief --label fulltext --kind result --paper 2611.12831 \
  --origin tracks/kb/stage/KB-G3/VERIFIER.md \
  --locator '2611.12831v1:main.tex:L867; 2611.12831v1:main.tex:L877; 2611.12831v1:main.tex:L1142' \
  --evidence 'answers seed 714; search of every .tex file of 2611.12831v1 (main.tex is the only one) for cosmolog, periodic, expanding, FLRW, Friedmann' \
  --text 'arXiv:2611.12831v1 does not discuss cosmology in its full text: the strings "cosmolog" and "periodic" occur nowhere in main.tex (its only TeX file); FLRW appears only as the interior geometry of the Oppenheimer-Snyder solution (L867, L877) and "expanding" only for the diffuse cloud of an unbound cluster model (L1142).') || fail=1
echo "$out"; N714=$(echo "$out" | sed -n 's/^claim \([0-9]*\) added$/\1/p')
test -n "$N714" && $KB claim relocate "$N714" --by $BY --locator '2611.12831v1:main.tex:L867; 2611.12831v1:main.tex:L877; 2611.12831v1:main.tex:L1142' || fail=1

# 804 (brief L1751): umbrella of six [BACKGROUND] statements; each part has a checked claim.
$KB claim verify 804 --by $BY \
  --locator 'gr-qc/0107076v1:paper.tex:L61; gr-qc/9804040v1:rrs98.tex:L55-56; 1707.03595v4:Spin_PBH.tex:L64-67; 1011.4920v2:inhomogeneities-paper.tex:L38-46; 2002.12778v2:CKSY2021.tex:L276-291; 1901.08528v2:PBH-UCMH-ArXiv-v2.tex:L235; 0911.1136v1:prp.tex:L86-88; astro-ph/0309084v1:ms.tex:L59' \
  --evidence 'processed (verifier KB-G3 item 1c): every part is carried by a checked claim: Type I nature of collisionless critical collapse = claim 720; spin prediction of 1707.03595 = 741 (and 167); Green-Wald tracelessness = 732; horizon mass and energy fraction at neutrino decoupling = 778 (855 judgement; 854 refutes a misprint of astro-ph/0608642); r^(-9/4) profile = 370, 355, 685 (777 background); Hills scaling laws = 764 (626, 654). Locators are those of the checked claims.' || fail=1

# 809 (brief L1756): eight ids "without an INSPIRE record". Store: 4 records, 4 not found.
# 409 (D): authors of the four ids, and the ids of Croker-Weiner 2019 and Faraoni-Jacques 2007.
$KB claim verify 409 --by $BY \
  --locator '2307.02474v2:BH-CosmoCoupled-minMass.tex:L51-56; 2307.10708v1:main.tex:L24-26; 2306.08199v2:coupled_bh.tex:L105-109; 1904.03781v3:level3.tex:L39-50; 2107.06643v1:level1.tex:L35-44; 0707.1350v1:main.tex:L79-94' \
  --evidence 'authors from the INSPIRE records (kb-data/meta/inspire): 2307.02474 Amendola, Rodrigues, Kumar (MNRAS 528, 2377); 2307.10708 Gao, Li (ApJ 956, 128); 2306.08199 Ghodla, Easther, Briel (OJAp 2023); 1904.03781 Croker, Nishimura, Farrah (doi 10.3847/1538-4357/ab5aff). The unchecked identifiers: Croker and Weiner 2019 ApJ 882, 19 = arXiv:2107.06643 (INSPIRE: doi 10.3847/1538-4357/ab32da); Faraoni and Jacques 2007 PRD 76, 063510 = arXiv:0707.1350 (INSPIRE: doi 10.1103/PhysRevD.76.063510). Locators are the abstracts of the six papers.' || fail=1

# 447 (F): Maeda-Okawa abstract. Supported at the level of the abstract lines of the TeX source.
$KB claim verify 447 --by $BY --locator '2605.22525v2:Kerr_eccentric.tex:L101-117' \
  --evidence 'abstract lines of the TeX source (F labelled it [VERIFIED: abstract]): local inertial frame in Kerr, tidal effects through the Riemann curvature; four regimes for unbound orbits: adiabatic, tidally affected, chaotic, disruptive. INSPIRE: Maeda, Okawa, PRD 114, 084078 (2026). "Not NR" is consistent with the abstract (a frame-based model).' || fail=1

# 449 (F): matter binaries on fixed backgrounds; each item read in its abstract (and 2508.03463 L168 for the Newtonian self-gravity).
$KB claim verify 449 --by $BY \
  --locator '2508.03463v2:Binary.tex:L39-54; 2508.03463v2:Binary.tex:L168; 2601.04870v2:Binary_kerr_Final.tex:L45-63; 2609.20338v1:Final.tex:L39-54; 2608.22735v2:article.tex:L58-62; 2608.16986v1:aanda.tex:L85-98; 2610.27775v1:Submit.tex:L71-75' \
  --evidence 'abstract lines (F labelled it [VERIFIED: abstracts]): 2508.03463 SPH, two WDs, non-spinning IMBH, Schwarzschild geodesics with Newtonian self-gravity (L168); 2601.04870 SPH, spinning IMBH, geodesics with Newtonian self- and mutual gravity; 2609.20338 SPH, eccentric WD binaries, Schwarzschild IMBH; 2608.22735 restricted three-body and SPH, solar-like star plus WD; 2608.16986 GRSPH (SPHINCS_BSSN) in the Kerr metric with a Newtonian self-gravity module, single stars; 2610.27775 GRSPH on a fixed BH background with an improved weak-field self-gravity, "keeps a binary of two polytropes stable over ten orbits" (L74) as a test. None evolves the spacetime.' || fail=1

# 450 (F): single stars in full NR / GR hydrodynamics.
$KB claim verify 450 --by $BY \
  --locator '1201.4389v1:paper.tex:L32-54; 1502.05740v2:ms.tex:L50-52; 1408.1695v2:main.tex:L30-39; 2212.10891v2:paper.tex:L71-73; 1303.1540v2:main.tex:L25-38' \
  --evidence 'abstract lines (F labelled it [VERIFIED: abstracts]): 1201.4389 NR, WDs and a spinning IMBH; 1502.05740 fully GR, ultra-close encounters of solar-type stars; 1408.1695 hydrodynamics with full GR, a star colliding with a massive BH; 2212.10891 fully GR, WDs on elliptic orbits (e ~ 1/3-2/3) about a 1e5 Msun BH; 1303.1540 (East and Pretorius, INSPIRE PRD 87, 101502) full Einstein equations with the background truncation error subtracted, radial infall of a solar-type star, mass ratios >= 1e6. Each simulates one object, no binary.' || fail=1

# 452 (F): partly right; a precise claim is added and 452 is annotated.
out=$($KB claim add --by $BY --track F-hills --label fulltext --kind result --paper 2602.06961 \
  --origin tracks/F-hills/novelty/NOVELTY.md \
  --locator '2602.06961v1:apssamp.tex:L77-85; 2610.20594v1:apssamp.tex:L79-88; 2610.20594v1:apssamp.tex:L1469' \
  --evidence 'checks the factual part of claim 452; author and abstract lines read by the lead' \
  --text 'arXiv:2602.06961 (Heinze, Schaefer, Bruegmann, Jena) gives the general N-body 2PN Hamiltonian in ADM gauge and integrates its equations of motion (pn-nbody code); arXiv:2610.20594 (Heinze, Cao) constrains the outer orbit of a hierarchical black-hole triple from two merger events with Peters equations and integrates with the same pn-nbody code (L1469); it is not itself a PN N-body dynamics paper. Both share an author with the BAM binary-single study arXiv:2505.03934.') || fail=1
echo "$out"; N452=$(echo "$out" | sed -n 's/^claim \([0-9]*\) added$/\1/p')

# annotations (claims that stay to_verify, with the answer)
cat > "$NRPIC_RUN_DIR/annotate.tsv" <<EOT
714	processed (verifier KB-G3 item 1c): answered NO by claim $N714: the full text of 2611.12831v1 does not discuss cosmology (no "cosmolog" or "periodic" in main.tex; FLRW only as the Oppenheimer-Snyder interior L867, L877). The label stays to_verify because the seed is a question; claim $N714 carries the answer.
809	processed (verifier KB-G3 item 1c): INSPIRE records in kb-data/meta/inspire: found and agreeing with the arXiv record in title and first author for 0909.0749 (Wiltshire, INSPIRE 830327), gr-qc/0012059 (Olabarrieta, 538829), astro-ph/9607124 (Widrow, 421260), 2510.11611 (Joana, Yuwen, 3068527); status not-found on 2026-11-19 for 2409.16053, 1609.03053, 1612.06734, 1709.00267 (arXiv records only: AthenaK, Stone et al.; GEMPIC, Kraus et al.; Morrison; Andersson, Fajman). The statement stays to_verify for those four.
452	processed: partly right. 2602.06961 is a PN N-body paper of the Jena group (Bruegmann co-author); 2610.20594 is a Peters-equation method for hierarchical triples that uses the pn-nbody code, not a PN N-body dynamics paper; see claim $N452. "Likely competitors" and "repeat the citation queries" are F's judgement and advice; the label stays to_verify for them.
EOT
python3 -I tracks/kb/lead_b13/scripts/annotate.py annotate "$NRPIC_RUN_DIR/annotate.tsv" || fail=1
test -n "$N452" && $KB claim relocate "$N452" --by $BY --locator '2602.06961v1:apssamp.tex:L77-85; 2610.20594v1:apssamp.tex:L79-88; 2610.20594v1:apssamp.tex:L1469' || fail=1

snap $N682 $N714 $N452 > "$NRPIC_RUN_DIR/after.tsv"
$KB claim stats > "$NRPIC_RUN_DIR/stats.txt" 2>&1
echo "new claims: 682->$N682 714->$N714 452->$N452" | tee "$NRPIC_RUN_DIR/new_ids.txt"
echo "fail=$fail"
exit $fail
