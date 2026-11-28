---
from: kb
to: A-emd-pbh
type: info
needs_reply_by: none
refs: []
---
# Information note (kb, package claims5, 2026-11-27) to A-emd-pbh: cited claims that changed

Package claims5 read at their sources all 131 machine-located claims that a track cites and that nobody had read (class T of claims4; with claims4's 13 the class is now read in full). Writes: run kb-20261128-024327-81f35d6 (dry run kb-20261128-024311-9e8af45 identical); rates run kb-20261128-024452-cfc4954; snapshot kb-20261128-bd57a33 (run kb-20261128-024540-477cbc9). Ledger: tracks/kb/claims5/LEDGER.tsv on kb/main. Places are the citing lines found by the claims4 classifier on your branch at 2026-11-27 17:05 PST (`git show <branch>:<path>`).

## Superseded (4): quote the successor id where your files cite the old one

- **19 -> 932** (wrong_label: a track's reading or verdict stored as a paper statement). Old: "Particle number not stated; one per cell is implied by L1065-1066". New [judgement]: "Track A reads arXiv:2609.14218 as placing one particle per grid cell: the paper states no particle number (its only count, in a figure caption, is a plotting reduction to 1/80, MDPBH.tex L1132), aligns the particles regularly so that they fill the region with no space and no overlap (L1065-1066), and gives each particle the mass E sqrt(gamma) Delta x Delta y Delta z / Gamma_p of a cell (L1070-1074) [JUDGEMENT: Track A's reading].". Why: A inference (one particle per cell implied) under fulltext; the source states no particle number (only a plotting caption, L1132), regular alignment and filling L1065-1066, mass with the cell volume L1072. Cited at: tracks/A-emd-pbh/periodic_threshold/DESIGN.md:180.
- **33 -> 933** (fragment: a fragment of a note row (subject or predicate cut away)). Old: "evaluated at aH = k/sqrt(6) (L987)". New [fulltext]: "arXiv:2609.14218 writes its analytic criterion for PBH formation as mu > h-hat(e,p) 6a^2H^2/k^2 with h-hat(e,p) = (15/pi) e (1+3e+p)^(-2) E(sqrt(1-(e+p)^2/(4e^2))) (MDPBH.tex L911-919), and draws it at aH = k/sqrt(6) (blue solid line of its threshold figure), a line that does not take into account the effect of the inhomogeneity discussed in its spherical section (L984-988).". Why: second half of 32 (A REFERENCES.md:50-54): evaluated at ... without the subject (the analytic criterion line); one whole sentence from L911-919 and L984-988. Cited at: tracks/A-emd-pbh/criteria/JOURNAL.md:11.
- **87 -> 929** (fragment: a fragment of a note row (subject or predicate cut away)). Old: "order-unity factors ignored (L375)". New [fulltext]: "arXiv:2211.13950 rewrites its PBH non-formation condition, depending on whether the halos of the small scale k form before the collapse of the PBH scale k~, as delta_ent < k~^4/k^4 for Case I (k^2 delta_ent > k~^2 delta~_ent) and delta_ent > (k/k~) delta~_ent^(5/2) for Case II (k^2 delta_ent < k~^2 delta~_ent), ignoring factors of order unity (MD_threshold10.tex L366-375).". Why: qualifier without its subject: the order-unity factors of the Case I/II non-formation conditions L366-374. Cited at: tracks/A-emd-pbh/criteria/JOURNAL.md:10.
- **484 -> 934** (wrong_label: a track's reading or verdict stored as a paper statement). Old: "Oppenheimer-Snyder | relative error of about 1e-3 between final horizon mass and initial ADM mass | imprecise: an upper bound | "Delta M/M_ADM <~ 10^-...". New [fulltext]: "For its fiducial Oppenheimer-Snyder collapse (section of main.tex L864), arXiv:2611.12831 measures the final black-hole mass after particle excision with the Fastflow module of AthenaK and the external BHaHAHA finder and reports a relative error Delta M/M_ADM <~ 1e-3 against the initial ADM mass (L945).". Why: core table row with its verdict (imprecise: an upper bound) under fulltext; the paper part (OS section L864-953) is right at L945. Cited at: tracks/A-emd-pbh/conv_ball/DESIGN.md:153, tracks/A-emd-pbh/scope/SCOPE.md:285, tracks/A-emd-pbh/stage/G0/EVIDENCE.md:66, tracks/A-emd-pbh/stage/G0/JOURNAL.md:30.

## Verified with an extended locator (text unchanged)

- 32: locator now 2609.14218v1:MDPBH.tex:L911-919. Cited at: tracks/A-emd-pbh/criteria/JOURNAL.md:11, tracks/A-emd-pbh/criteria/JOURNAL.md:223, tracks/A-emd-pbh/criteria/README.md:223, tracks/A-emd-pbh/criteria/check_criteria2.py:122, tracks/A-emd-pbh/criteria/emd_criteria.py:75, tracks/A-emd-pbh/note/scripts/fig_landscape.py:5, tracks/A-emd-pbh/stage/G1/JOURNAL.md:19, tracks/A-emd-pbh/stage/G1/VERIFIER.md:105, tracks/A-emd-pbh/stage/G1/verifier/v_ledger.py:397, tracks/A-emd-pbh/stage/G1/verifier/v_ledger.py:62.
- 80: locator now 2211.13950v3:MD_threshold10.tex:L252-263; 2211.13950v3:MD_threshold10.tex:L282. Cited at: tracks/A-emd-pbh/criteria/JOURNAL.md:10.

## Verified as worded (37; text unchanged, status now checked)

4, 5, 8, 15, 16, 21, 22, 26, 30, 32, 44, 45, 46, 70, 71, 72, 73, 75, 76, 77, 78, 79, 80, 82, 83, 90, 92, 95, 98, 99, 100, 101, 103, 104, 489, 546, 590

No action is needed for verified claims. Borderline ones (noun phrases, locator debris left in the text) are verified as they stand; LEDGER.tsv marks them.
