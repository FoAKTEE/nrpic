# C-sidm G0: what the gate still lacks

State at the end of the wave-2b lead session (2026-11-19). Every checklist item is PASS or
NA; the package is complete for the orchestrator's review under decision 0016 item 4 (G0 is
judged on the package with a verifier's report on the plan: `VERIFIER.md`). Nothing below
blocks G0; the lines say who can close them.

## Open, not blocking G0

1. Fresh verifier of the note's ledger: the 39 ledger rows of the working note v0 are
   regenerated from the registered JSON by `note/scripts/ledger.py` (rerun and compared by
   `nrpic-stage verify`), and the three rows that differed were recomputed by the lead
   (L11); no fresh-context verifier recomputed them. Under decision 0016 item 4 a verifier
   of later material belongs to G1, where it is listed (`../G1/OPEN.md` item 6).
2. Knowledge base: the key references are kb claims 229-331 and errata 610-618 (snapshot
   kb-20261115-44b7406). kb's one open point, the file name of the astro-ph/0111176
   locator, is `SMBH_SIDM_Xiv2.tex:289-291` (v3); sent to kb on 2026-11-19 (outbox). Two of
   kb's locator remarks do not hold for v2 of the sources (2601.17117 line 481 also carries
   the numbers; 2010.15132 `smbh.tex:116` contains "2.1"): same message. Owner: kb.
3. Shared text: brief corrections are in `coord/BRIEF_ERRATA.md` (decisions 0013, 0016
   item 8); nothing open on the track's side.

## Scientific items the scope depends on (carried to G1/G2)

4. The collisionless threshold of the core-halo family F21 b = 0.1 may lie away from the
   eps maximum (2105.05556 `paper.tex:599, 612`); the G2 scan must cover Z(0) up to about 1.
5. The collisionless King controls of wave 2 drift outward (alpha_c +0.033 at the threshold
   model within 200 M, run C-20261115-191420-8538aa4); cause unknown; it bears on the G2
   threshold and on the reading of the collisional runs (`../REVIEW-wave2.md` section 7).
6. Literature not obtainable here: Cercignani and Kremer (book), Nanbu and Yonemura 1998,
   the DSMC cell-size papers (kb: not in the corpus). Gurian and May (arXiv:2505.15903) and
   Ambrus et al. 2022 (arXiv:2201.09277) are fetched by kb; not yet read by the track.

## Closed in waves 2 and 2b

- Working note v0, schematics (wave-1 items 1, 2): `note/`, run C-20261115-171741-0e0da67.
- `nrpic-stage verify` (item 4): run on the committed tip, `VERIFY_RESULTS.md`.
- Verifier report on the plan (C18): `VERIFIER.md` (decision 0016 items 1 and 4).
- Juttner Gamma_1 onset (item 6): Z(0) = 0.5331, runs C-20261115-165315-7b473b8 and
  C-20261115-193332-48771b4.
- F21 b = 0.1 particle files (item 7): run C-20261115-170742-84990ed (N = 1e5), AthenaK read
  test C-20261115-174557-8978b36.
- Growth-rate pipeline (item 8): validated on the first paper's runs for collapse times
  (18 of 18 numbers, run C-20261115-170346-298a1ba); the growth-rate fit has a known bias
  with a fix tested on synthetic signals only (G1 item, `../G1/OPEN.md`).
- Cost of one collision (item 9): 3.4-3.9e-9 s per tested pair on one A100, 3.3-6.7e-7 s on
  one core (runs C-20261115-180525-94ddd22, C-20261115-165500-c67e036); particle mode 1.68
  times cell mode on a processor (run C-20261119-143146-226b0e0).
- Momentum-constraint ratio of the King files (item 12): not chased; superseded by the
  constraint norms of the F21 read test (0.66 of the reference, squared).
