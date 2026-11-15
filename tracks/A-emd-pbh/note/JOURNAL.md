# JOURNAL of the package note (helper of A-emd-pbh, wave 2)

Package: the products of gate G0 that were still missing (`stage/G0/OPEN.md` items 1-3,
8): the working note v0 (REVTeX, /paper-writing), the two schematics (architecture of the
track's calculation; stage timeline; /sleep-paper-figure-style, `paperfig.py`), and
`stage/G0/STAGE_REPORT.md` from the harness template. Evidence labels as in the brief.

## 2026-11-15, entry 1: what was read, what the note uses, and the predictions (before any run)

Read: CLAUDE.md; coord/CHARTER.md to "Owners" and section 9.4; brief lines 335-365,
708-725, 834-860; the rulings `tracks/orch/outbox/20261115T1516Z__to-all__rulings-after-wave-1.md`;
decisions 0010-0015; the owner's HANDOFF.md, STATUS.md, JOURNAL.md, RISKS.md,
`stage/G0/{CHECKLIST,EVIDENCE,OPEN}.md`, `stage/G1/STATUS.md`; `scope/SCOPE.md` (whole),
`scope/REFERENCES.md` (2609.14218 entry); the READMEs and journals of the wave-2 helpers
(`runs_ball/`, `periodic_threshold/`, `newton/`), as committed at 12426de; harness/RULES.md,
`harness/bin/nrpic-stage` (what `verify` re-runs and checks); the paper-writing skill.

Locators re-read for the note [VERIFIED, `kb-data/raw/arxiv/2609.14218/v1/src/MDPBH.tex`]:
lines 1101-1103 (horizon for mu >= 0.05, none for mu <= 0.045 at e = 0.2), 1145
(threshold "around mu ~ 0.045"), 765-768 (LTB: locally naked, black hole, for mu = 0.33;
globally naked for mu = 0.32), 907-908 (deformation eigenvalues), 918 (h-hat(e, p)).

The note's numbers come only from these registered runs (outputs under
`/data/haiyangw/nrpic/scratch/A-emd-pbh/<run_id>/`):

| Run | What the note takes |
|---|---|
| A-20261115-130252-7877b7a | scope T1-T5 (lead's rerun, identical to A-emd-pbh-20261115-112625-e854f12): hoop line, finite-duration amplitudes, ball capacity, compute model |
| A-emd-pbh-20261115-120425-80492f8 | criteria scan: thresholds of six criteria at e = 0, 0.1, 0.2 |
| A-emd-pbh-20261115-130256-a7374a4 | criteria checks (lead's rerun child): 37 checks, which pass |
| A-emd-pbh-20261115-130402-f5566fb | expball G1 constraint convergence N = 32-256 (lead's rerun) |
| A-emd-pbh-20261115-122117-aa1c84d | smoothed top-hat convergence to N = 512 |
| A-20261115-130257-a7374a4 | lead's cross-checks L2-L6 (two generators, two table rules, three exact codes) |
| A-emd-pbh-20261115-153719-91b03d1 | runs_ball exact references of data set 2t (a(tau), m_AH(tau), step plan) |
| A-20261115-130948-5a2b58a | lead's predictions of SR-1/SR-2 (coordinate times, card-hours) |

### Predictions N1-N5, written before any script of this package ran

- N1 (inputs are what the runs wrote). Every file the scripts read has the sha256 that its
  run recorded in `sha256sums.txt` (runs registered by `nrpic-run` or by hand with that
  file); runs of wave 1 without the file are read as they are and marked so. Refuted by
  one mismatch.
- N2 (numbers recovered from the files). The scripts recover, to the printed digits:
  h-hat(0.2, 0) = 0.452; mu_fd = 0.048 (250 t_H), 0.019 (1000 t_H); ball capacity at
  R_b H_i = 0.9 mu <= 0.031 (q = 3) and 0.069 (q = 2); hoop-ball threshold at e = 0.2 in
  central contrast 1.08 against the particle threshold 0.108 of arXiv:2609.14218 in the
  same measure; core turnaround tau = 16.894, R_max/R_i = 1.340, first trapped sphere
  44.349 at R_i = 2.742 with m = 0.0805, core edge trapped 44.381, crunch 44.454, m_AH
  rising to 0.0960 at the crunch; constraint orders flat-ball momentum 2.00/4.00, taper
  1.99/3.90 (all cells), compensated top hat 2.00/4.00 (smooth region, H and M), smoothed
  top hat 3.98 (H) and 3.94 (M) at order 4 with N = 512; criteria 33 of 37 checks pass,
  failures T1.2b, T2.2d, T2.4a, T2.4c. Refuted by any difference in the printed digits.
- N3 (claims of the lead's documents against the files). A script checks about forty
  numbers stated in `STATUS.md`, `stage/G1/STATUS.md`, `scope/SCOPE.md` sections 1-10,
  `JOURNAL.md` (L1-L8) and `runs_ball/JOURNAL.md` against the run outputs. Expected: all
  agree to the printed digits except one that I noticed while reading, before the
  script: the lead's L3 outcome calls the error of the table cubic at the sharp edge "an
  overshoot of about 0.1 H" and SCOPE 10.3 / RISKS 11 "~10 %", while the quantity the
  cross-check run recorded, `L3.KL_overshoot_near_edge` = 0.0855 (absolute, M = 1 units,
  within 0.01 M of the edge), is about 1.4 H; it is the largest deviation from the exact
  step, so it contains the smeared jump and is not an overshoot. Refuted (in my favour or
  not) by any other mismatch, or by this one not being there.
- N4 (figures). czstyle reports no label cut at a figure edge; the cycloid of the core
  scale factor peaks at tau = 16.894 and ends at 44.454; m_AH(tau) increases
  monotonically; the largest coordinate speed of light of geodesic slicing crosses the
  stability bound at the step switches of the plan; constraint norms fall along h^2 and
  h^4 guides for the smooth models and stay flat (or rise) over all cells for the sharp
  top hat; the hoop line rises with e and lies an order of magnitude above the particle
  bracket of arXiv:2609.14218 at e = 0.2. Refuted by any figure that does not show this.
- N5 (manuscript). The note compiles with latexmk without undefined references or
  citations; the paper-writing checker reports no hype word, no boxed equation, no
  `\%`, no project names in the text (run ids are allowed only in the ledger appendix,
  by the note's guide); captions at most five lines on the rendered page.

## 2026-11-15, entry 2: outcomes of N1-N5 (runs A-20261115-161054-50848b1, A-20261115-161720-6ae975e, A-20261115-161947-09324e1)

Three runs of the same `scripts/run_all.py` (each script change got a new run): the first two
registered with `harness/bin/nrpic-run submit --package tracks/A-emd-pbh/note`; the third by
hand with `scripts/handreg.py`, because `nrpic-run` then refused ("not clean where the run's
code lives: ?? peak.horizon_summary_0.txt", an untracked file another helper's AthenaK run
writes into the worktree root; not mine, left alone). The PNGs of the three runs are
identical where the scripts did not change; the committed figures and tables are those of
A-20261115-161947-09324e1.

- N1 holds where it can be checked: the four inputs whose runs wrote `sha256sums.txt`
  (A-20261115-130252-7877b7a, A-20261115-130257-a7374a4, A-emd-pbh-20261115-153719-91b03d1,
  A-20261115-130948-5a2b58a) match; five inputs of wave-1 runs without that file were read as
  they are (`tables/claims.md`, "Inputs read").
- N2 holds: every listed number is recovered to the printed digits (script output in each
  run's `run.log`): h-hat(0.2, 0) = 0.452; mu_fd = 0.048, 0.019; ball capacity 0.031 (q = 3),
  0.069 (q = 2); hoop-ball 1.08 against particles 0.108 (ratio 10.0); tau_ta = 16.894,
  R_max/R_i = 1.3398, first trapped 44.349 at R_i = 2.742, m = 0.0805, core edge 44.381,
  crunch 44.454, m_AH at the crunch 0.0960; orders 2.00/4.00 (flat), 1.99/3.90 (taper),
  4.00/4.00 (top hat, smooth cells), 3.98/3.94 (smoothed top hat, N = 512); 33 of 37 checks,
  failures T1.2b, T2.2d, T2.4a, T2.4c.
- N3 refuted in part: 68 claims checked, 66 agree, two differ. The one I expected (L3
  "overshoot of about 0.1 H" against the recorded edge deviation 0.0855 = 1.37 H) and one I
  did not foresee: L6 "below 4.3e-15" against the recorded 4.33e-15 (a rounding of the bound).
  Both listed in `../stage/G0/STAGE_REPORT.md` with four further differences of date or
  resolution found while writing (budget line of STATUS, two exact references of data set 2t
  agreeing to their printed digits, REPORT.md superseded by decision 0012, the verifier's C1c).
- N4 holds for the final figures, each looked at: cycloid peaks at tau = 16.89 and ends at
  44.454, m_AH monotonic, coordinate light speed reaches the bound at each stage switch,
  smooth constraint norms along h^4 (top hat order 4.00, smoothed top hat 3.98/3.94 at the
  finest pair) and the sharp top hat flat (H, order 0.5) or rising (M, order -0.5) over all
  cells, hoop line rising with e and ten times the particle threshold at e = 0.2. The first
  drafts had labels cut at the figure edge (czstyle reported it) and overlapping labels; fixed
  before the registered runs; the registered runs report no cut label.
- N5 holds after three fixes: the first compile failed (apsrev4-2 needs a journal for
  `@article`; the preprints became `@misc`), the profile equation overflowed the column (split
  over two lines), and the caption of Fig. 1 was estimated past five lines (shortened). Final
  checker: 0 undefined references and citations, 0 overfull boxes, no hype, negation, `\%`,
  boxed equation or mathematics in the abstract; candidates only for run ids in the ledger
  appendix and harness names in the ledger scripts, accepted by exception 1 of
  `../WRITING_GUIDE.md`. All nine pages looked at.

Not done (scope of a few hours): the reviewers of step 4 of the paper-writing procedure for a
new paper (300- and 1000-word versions read by first-year-student reviewers) were not run; a
verifier recomputation of the note's ledger was not done (the wave-2 verifier checks the
claims, not the note).

`harness/bin/nrpic-stage verify A-emd-pbh G0` on fe07201: every check of the note passes
(note, note-pdf, style, fig-script, min-figs, rerun of the six figure scripts in a clean
export, compare, regenerate); FAIL only on `clean` and `runs`, from other helpers' work in
flight. `nrpic-stage report` then wrote `../stage/G0/STAGE_REPORT.md` (computed verdict FAIL:
C2 kb entries, C18 verifier, verify); my sections are appended to it.
