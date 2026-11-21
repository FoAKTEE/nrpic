# Audit of 40 machine-located fulltext claims (claims_tracks, 2026-11-21)

**Population.** Every claim in `kb-data/db/kb.sqlite` with label `fulltext` and status
`located` on 2026-11-21 at 21:26 UTC: 502 claims. The machine resolved their locators and
found their numbers; nobody had read them.

**Draw.** `scripts/draw_audit.py --seed 20261121 --n 40`, run
`kb-20261121-212635-c33885e` (outputs `audit_sample.tsv` and `audit_strata.json` in
`scratch/kb/kb-20261121-212635-c33885e/`). The sample is stratified by track with
largest-remainder proportional allocation:

| Track | In the population | Drawn |
|---|---|---|
| A-emd-pbh | 145 | 12 |
| core | 121 | 10 |
| C-sidm | 97 | 8 |
| D-bh-dress | 65 | 5 |
| B-emd-gw | 44 | 3 |
| F-hills | 30 | 2 |

**Method.** I read each claim at its stored locator in the stored source with
`scripts/read_claim.py`, which prints the claim and the cited lines (terminal only; no paper
text is written to git). Where a claim quotes a number or phrase that the cited lines do not
show, I searched the whole file with grep. A claim is **right** when the passage at the stored
locator supports it as worded. It has a **wrong locator** when the statement is in the paper
but elsewhere. It is a **wrong statement** when the paper says otherwise or does not say it.
Claims whose text holds no statement at all were reported separately as **fragments**
(a category I had not foreseen).

**Prediction** (JOURNAL.md, "Prediction AU", written before the draw): 36-39 right, 1-4 wrong
locators, 0-1 wrong statements. Earlier audits found 29 of 30 right (wave 2, P2) and 9 of 10.

## Result

| Verdict | Count |
|---|---|
| right | 37 |
| wrong locator | 1 (102) |
| wrong statement | 0 |
| fragment, no statement | 2 (85, 620) |

The prediction held on all three counts it made. The fragment category was not foreseen.
Counting the fragments as failures, 37/40 = 92.5 per cent are right; counting only claims that
carry a statement, 37/38 = 97 per cent. Together with the earlier audits (29/30 and 9/10), the
machine locators were right for 75 of 80 audited claims [VERIFIED for this audit; the earlier
two from the claims journal]. Under a binomial reading the error rate of the 502 is then
likely between 2 and 13 per cent [JUDGEMENT].

## Per claim

| Claim | Track | Paper | Stored locator | Verdict | Action |
|---|---|---|---|---|---|
| 2 | A-emd-pbh | 2609.14218 | `2609.14218v1:MDPBH.tex:L509-547` | right | checked |
| 23 | A-emd-pbh | 2609.14218 | `2609.14218v1:MDPBH.tex:L173-174` | right | checked |
| 27 | A-emd-pbh | 2609.14218 | `2609.14218v1:MDPBH.tex:L177` | right | checked |
| 50 | A-emd-pbh | 2610.23218 | `2610.23218v1:main.tex:L307` | right | checked |
| 53 | A-emd-pbh | 2610.23218 | `2610.23218v1:main.tex:L440` | right | checked |
| 56 | A-emd-pbh | 1609.01588 | `1609.01588v2:apj_nonsphericalpbh.tex:L414-418; 1609.01588v2:apj_nonsphericalpbh.tex:L463` | right | checked |
| 58 | A-emd-pbh | 1609.01588 | `1609.01588v2:apj_nonsphericalpbh.tex:L503` | right | checked |
| 85 | A-emd-pbh | 2211.13950 | `2211.13950v3:MD_threshold10.tex:L550-563` | fragment (no statement) | annotated, left located |
| 102 | A-emd-pbh | 2507.18312 | `2507.18312v3:Main.tex:L537-538` | wrong locator (relocated) | relocated, checked |
| 105 | A-emd-pbh | 2507.18312 | `2507.18312v3:Main.tex:L549` | right | checked |
| 108 | A-emd-pbh | 2508.10070 | `2508.10070v1:main.tex:L339-353` | right | checked |
| 154 | A-emd-pbh | 1611.07906 | `1611.07906v2:asymflat.tex:L344-366` | right | checked |
| 183 | B-emd-gw | 2403.15126 | `2403.15126v1:pII_GW_Vir_C2_Arx.tex:L1074` | right | checked in batch L1 |
| 199 | B-emd-gw | 2605.04487 | `2605.04487v2:main_v3.tex:L2625` | right | checked |
| 620 | B-emd-gw | 2608.13206 | `2608.13206v3:PRD.tex:L38-39` | fragment (no statement) | annotated, left located |
| 238 | C-sidm | 2108.11967 | `2108.11967v2:main.tex:L355` | right | checked |
| 243 | C-sidm | 2601.17117 | `2601.17117v2:SIDM_MS.tex:L233` | right | checked |
| 263 | C-sidm | 2009.08163 | `2009.08163v1:paper.tex:L1059-1091` | right | checked |
| 276 | C-sidm | 2611.12831 | `2611.12831v1:main.tex:L1006` | right | checked |
| 283 | C-sidm | astro-ph/0111176 | `astro-ph/0111176v3:SMBH_SIDM_Xiv2.tex:L31-40` | right | checked |
| 285 | C-sidm | astro-ph/0111176 | `astro-ph/0111176v3:SMBH_SIDM_Xiv2.tex:L167-174` | right | checked |
| 293 | C-sidm | 2506.17641 | `2506.17641v3:sidmacc.tex:L218` | right | checked |
| 312 | C-sidm | 2601.17117 | `2601.17117v2:SIDM_MS.tex:L233` | right | checked |
| 343 | D-bh-dress | 1305.2619 | `1305.2619v1:SFWpaper.tex:L897-903` | right | checked |
| 347 | D-bh-dress | 1901.08528 | `1901.08528v2:PBH-UCMH-ArXiv-v2.tex:L149-152` | right | checked |
| 355 | D-bh-dress | 1901.08528 | `1901.08528v2:PBH-UCMH-ArXiv-v2.tex:L323` | right | checked |
| 365 | D-bh-dress | 1805.09034 | `1805.09034v3:main.tex:L208` | right | checked |
| 382 | D-bh-dress | 2302.07878 | `2302.07878v1:paper_couple_rev.tex:L100-101` | right | checked |
| 435 | F-hills | 1004.1353 | `1004.1353v2:Punc_N.tex:L58-67` | right | checked |
| 631 | F-hills | 0911.1136 | `0911.1136v1:prp.tex:L846-854` | right | checked |
| 453 | core | 2611.12831 | `2611.12831v1:main.tex:L21-25` | right | checked |
| 502 | core | 2611.12831 | `2611.12831v1:main.tex:L1140` | right | checked |
| 506 | core | 2611.12831 | `2611.12831v1:main.tex:L1338` | right | checked |
| 517 | core | 2611.12831 | `2611.12831v1:main.tex:L926; 2611.12831v1:main.tex:L943` | right | checked |
| 530 | core | 2611.12831 | `2611.12831v1:main.tex:L1485` | right | checked |
| 556 | core | 2611.12831 | `2611.12831v1:main.tex:L1138` | right | checked |
| 574 | core | 2611.12831 | `2611.12831v1:main.tex:L1140` | right | checked |
| 589 | core | 2611.12831 | `2611.12831v1:main.tex:L370-397` | right | checked |
| 595 | core | 2611.12831 | `2611.12831v1:main.tex:L376` | right | checked |
| 597 | core | 2611.12831 | `2611.12831v1:main.tex:L678` | right | checked |

Notes on single claims:
- **102** (2507.18312v3). N = 123 and 619 are in the subfigure captions at L537-538. The claim's
  "Gaussian velocities" (uncorrelated Gaussian initial velocities with dispersion set by s_v)
  is at L502. The locator was extended to `L502; L537-538` and the claim checked.
- **85** (2211.13950v3). The text is only "and L550-563", split from the note row
  `tracks/A-emd-pbh/scope/REFERENCES.md:126` together with claims 84 and 86.
- **620** (2608.13206v3). The text is only "Abstract".
- **595, 597** (2611.12831v1). The paper parts are right. The repository parts
  (`z4c_calcrhs.cpp` L714-724, `nrpic.cpp` L399-424) were not rechecked here.
- **276** (2611.12831v1 L1006). The cited key Gunther:2021pbf maps to eprint 2105.05556 in
  the stored `references.bib` (L1056-1059).
- **517**. Staley:2011ss maps to eprint 1109.0546 (`references.bib` L1621-1624).

## Actions (registered)

- Batch AU1, run `kb-20261121-212918-9b5b9df`:
  - 36 claims marked checked by kb-claims_tracks (`kb claim verify`, then `kb claim check --id`).
  - 102 relocated and checked.
  - 85 and 620 annotated and left `located`, because a fragment has nothing to check.
- Claim 183 (2403.15126, which ingest3 re-ingests) was checked last, in batch L1.
- A correction found during the audit: reading 589 showed that my evidence for claim 525
  (batch K1) wrongly said 2611.12831 gives no shift-damping profile. The profile is at L388-397.
  The claim, read in its source row ("no item-by-item ablation"), still holds, because no
  on/off comparison of the profile is reported. The correction is recorded as an annotation
  of 525 in AU1.

## What follows

- The 462 machine-located claims that were not drawn stay `located`. This audit's rate does
  not license marking them checked.
- Fragments are a defect of the seeder: it splits one note row into several claims at each
  locator. I ran a read-only lookup on kb.sqlite (2026-11-21, 21:30 UTC) for machine-located
  fulltext claims whose text is shorter than 25 characters. It finds 24. About 17 of them
  carry no checkable statement: 81, 84, 85, 171, 179, 187, 192, 213, 277, 290, 314, 424,
  431, 619-623 and 625. Seven are short but complete, for example 487, 557 and 626.
  Request to the kb lead: re-seed the split rows by joining them (README, Requests).
