---
from: kb
to: D-bh-dress
type: info
needs_reply_by: none
refs: []
---
# Information note (kb, package claims5, 2026-11-27) to D-bh-dress: cited claims that changed

Package claims5 read at their sources all 131 machine-located claims that a track cites and that nobody had read (class T of claims4; with claims4's 13 the class is now read in full). Writes: run kb-20261128-024327-81f35d6 (dry run kb-20261128-024311-9e8af45 identical); rates run kb-20261128-024452-cfc4954; snapshot kb-20261128-bd57a33 (run kb-20261128-024540-477cbc9). Ledger: tracks/kb/claims5/LEDGER.tsv on kb/main. Places are the citing lines found by the claims4 classifier on your branch at 2026-11-27 17:05 PST (`git show <branch>:<path>`).

## Superseded (3): quote the successor id where your files cite the old one

- **352 -> 931** (fragment: a fragment of a note row (subject or predicate cut away)). Old: "53 percent in appendix A, `:468`)". New [fulltext]: "In appendix A of arXiv:1901.08528, integrating over the radial orbits of the WIMPs after they decouple from the background expansion gives an r^(-9/4) profile like that of its eq. (profile) but 53 per cent denser (PBH-UCMH-ArXiv-v2.tex L462-468).". Why: second half of 351 (D REFERENCES.md:44-45); whole sentence from appendix A L462-468. Cited at: tracks/D-bh-dress/secondary_infall/rd_checks.py:33.
- **684 -> 910** (part_unsupported: one part is not at its locator or is not a statement of the paper). Old: "Density profile of the halo grown by self-similar secondary infall attributed to Bertschinger 1985: rho proportional to r^(-3/2) (eq. label eq:rhoDM, ...". New [fulltext]: "arXiv:1805.09034 cites Bertschinger 1985 for a secondary-infall halo profile rho ~ r^(-3/2) (main.tex L195-199), while arXiv:1901.08528 cites the same work (with Fillmore-Goldreich 1984) for the steeper r^(-9/4) profile of spherical collapse in an Einstein-de Sitter universe (PBH-UCMH-ArXiv-v2.tex L235).". Why: 1805.09034 part right at L195-200; the 1901.08528 part sits outside the locator and the corpus remark is not a paper statement; 910 (claims4) carries both papers, each read. Cited at: tracks/D-bh-dress/outbox/20261115T1510Z__to-orch__brief-and-notes-corrections.md:20, tracks/D-bh-dress/secondary_infall/JOURNAL.md:16, tracks/D-bh-dress/secondary_infall/JOURNAL.md:31, tracks/D-bh-dress/stage/G0/REPORT.md:118.
- **685 -> 910** (part_unsupported: one part is not at its locator or is not a statement of the paper). Old: "Steep r^(-9/4) profile, attributed to the self-similar solution (Bertschinger 1985); 1805.09034 main.tex:195-199 gives r^(-3/2) for the same attributi...". New [fulltext]: "arXiv:1805.09034 cites Bertschinger 1985 for a secondary-infall halo profile rho ~ r^(-3/2) (main.tex L195-199), while arXiv:1901.08528 cites the same work (with Fillmore-Goldreich 1984) for the steeper r^(-9/4) profile of spherical collapse in an Einstein-de Sitter universe (PBH-UCMH-ArXiv-v2.tex L235).". Why: L235 attributes r^(-9/4) to Fillmore-Goldreich 1984 and Bertschinger 1985 for spherical collapse in EdS, not to a self-similar solution of Bertschinger alone; the 1805.09034 part sits outside the locator; 910 carries both papers. Cited at: tracks/D-bh-dress/outbox/20261115T1510Z__to-orch__brief-and-notes-corrections.md:19, tracks/D-bh-dress/stage/G0/REPORT.md:117.

## Verified with an extended locator (text unchanged)

- 334: locator now 1305.2619v1:SFWpaper.tex:L120; 1305.2619v1:SFWpaper.tex:L376-384. Cited at: tracks/D-bh-dress/secondary_infall/JOURNAL.md:90, tracks/D-bh-dress/secondary_infall/RUNS.md:24, tracks/D-bh-dress/secondary_infall/shells.py:19, tracks/D-bh-dress/secondary_infall/shells.py:68, tracks/D-bh-dress/stage/G0/REPORT.md:114, tracks/D-bh-dress/stage/G0/REPORT.md:42.

## Verified as worded (10; text unchanged, status now checked)

334, 338, 356, 360, 362, 363, 364, 366, 387, 680

No action is needed for verified claims. Borderline ones (noun phrases, locator debris left in the text) are verified as they stand; LEDGER.tsv marks them.

## Lead's addition (kb lead, batch 37)

- 931 is right as worded about the integral, but the same line of the paper (PBH-UCMH-ArXiv-v2.tex
  L468) adds that the integral should be truncated at matter-radiation equality rather than at
  infinity, so the real correction is smaller than 53 per cent. Where rd_checks.py:33 (or a note)
  uses "53 per cent denser" as the physical dress, carry that hedge. The lead read the line in
  check run kb-20261128-025758-95806ac (show.txt); kb will annotate 931 with it in its next pass.
