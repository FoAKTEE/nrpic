# KB-G2: rechecks by the lead

- The retrieval numbers (golden questions) of the helper of wave 2b were rescored by the lead from
  the ranked lists with own code (check B2, run kb-20261119-155310-e600e38): identical in every
  mode and question. The parse-status counts and the metadata were recounted by own SQL (B1, run
  kb-20261119-155134-17d6704). Per package: `../REVIEW-wave2.md` (section "Wave 2b"); figure
  `tracks/kb/note/figures/fig_w2b_review.png`.
- The QA run of this package (Q1, run kb-20261119-161633-1d05960) is the lead's own, on snapshot
  kb-20261119-a782f1e. Since wave 3 it is recomputed by an independent verifier (VERIFIER.md:
  own scorer, own parse scan, blind held-out set of 24 questions).
- Wave 3 batch 3: the lead checked the verifier from its artefacts, not its conclusions
  (`../REVIEW-wave3.md`, run kb-20261121-125746-a03875b, figure
  `../review_wave3/figures/fig_lead_check_vg2.png`): paper hits and rank-1 counts recounted from
  the raw hit lists (equal in all six set-mode pairs); snapshot counts by own SQL (status, papers
  without bibliography, citation rows without entries, abstracts, repositories without code
  chunks: all equal); the database columns of the verifier's parse scan equal to own SQL for
  710 of 710 papers; its definition of parse success re-evaluated by own code (679, 670 equal);
  three bibliography defects confirmed at the source; held-out set committed before the first
  search; C6b confirmed (no snapshot id in `kb show`, `kb cites` or a search hit).
