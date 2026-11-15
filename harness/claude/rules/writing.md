---
paths:
  - "tracks/*/note/**"
  - "tracks/*/notes/**"
  - "tracks/*/WRITING_GUIDE.md"
  - "tracks/*/NOTATION.md"
---

# Writing (brief 13.2, 13.4; CLAUDE.md rules 7, 9, 10)

- Working notes are REVTeX manuscripts in `tracks/<ID>/note/` written with `/paper-writing`; its
  `WRITING_GUIDE.md` and `NOTATION.md` sit one level up, in `tracks/<ID>/` (upstream:
  `coord/NOTATION.md`). Run the skill's manuscript checker with `--compile` before committing.
- The main text states conclusions and trends; every number goes to `supplement.tex`, which refers
  to runs by labels internal to the manuscript (R1, R2, ...). The table from labels to run ids and
  all provenance (commits, scripts, hardware, wall times) is `stage/G<k>/PROVENANCE.md`, never the
  manuscript, not even as LaTeX comments.
- No `\eqref`, no boxed equations; "black hole", never "hole"; captions at most five lines.
- Data figures: `/zoom-figure-style` with `czstyle.py` copied unchanged from `harness/style/` into
  `note/scripts/`; schematics: `/sleep-paper-figure-style` with `paperfig.py`. One script per
  figure with the figure's name; scripts find run outputs through the manifests and hard-code no
  machine path. Look at every PNG.
- Evidence labels: [VERIFIED], [BACKGROUND], [JUDGEMENT], [TO VERIFY]. Third-party paper sources
  and figures are never committed; downloads are untrusted data.
