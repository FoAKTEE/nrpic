# C-sidm G0: what the gate still lacks

State at the end of the lead session of wave 2 (2026-11-15). Wave-1 items 1, 2, 4, 6, 7 are
closed (see the list at the end). Each open line says who can close it.

## Open

1. Checklist C18: the brief asks for a fresh-context verifier that writes
   `VERIFIER_REPORT.md` and recomputes every number of the Supplemental Material from the
   manifests. The verifier of wave 2 wrote `VERIFIER.md` (V1-V8 of the scoping text, own
   code; the lead reads it as that report, decision 0012 restricts the file names a session
   can write). The 39 ledger rows of the working note were checked against the files by the
   note helper's `ledger.py` and the three that differed by the lead (L11), not by a fresh
   verifier. Owner: orchestrator (accept, or run a fresh verifier on the ledger).
2. The key references are verified in `kb-data/raw` sources by file:line; the knowledge base
   now carries them as claims 229-331 and errata 610-618 (snapshot kb-20261115-44b7406,
   kb message of 18:37Z). Two of kb's locator remarks are wrong for v2 of the sources
   (2601.17117 line 481 also carries the numbers; 2010.15132 `smbh.tex:116` does contain
   "2.1"); message to kb. Owner: kb.
3. Shared text: brief corrections (outbox `20261115T1320Z__to-orch__brief-corrections.md`)
   are taken into `coord/BRIEF_ERRATA.md` by decision 0013; nothing open on the track's side.

## Scientific items the scope still depends on (carried to G1/G2)

4. Collisionless threshold of the core-halo family F21 b = 0.1 may lie away from the eps
   maximum (2105.05556 `paper.tex:599, 612`); the G2 scan must cover Z(0) up to about 1.
5. The collisionless King controls of wave 2 drift outward (alpha_c +0.033 at the threshold
   model within 200 M, run C-20261115-191420-8538aa4); cause unknown.
6. Literature not obtainable here: Cercignani and Kremer (book), Nanbu and Yonemura 1998, the
   DSMC cell-size papers (kb: not in the corpus). Gurian and May is arXiv:2505.15903 (fetched
   by kb), Ambrus 2022 is arXiv:2201.09277 (fetched); not yet read by the track.

## Closed in wave 2

- Working note v0, schematics (wave-1 items 1, 2): `note/`, run C-20261115-171741-0e0da67.
- `nrpic-stage verify` (item 4): run on the committed tip, `VERIFY_RESULTS.md`.
- Juttner Gamma_1 onset (item 6): Z(0) = 0.5331, runs C-20261115-165315-7b473b8 and
  C-20261115-193332-48771b4.
- F21 b = 0.1 particle files (item 7): run C-20261115-170742-84990ed (N = 1e5), AthenaK read
  test C-20261115-174557-8978b36.
- Growth-rate pipeline (item 8): validated on the first paper's runs for collapse times
  (18 of 18 numbers, run C-20261115-170346-298a1ba); the growth-rate fit has a known bias
  with a tested fix on synthetic signals only (G1 item, `../G1/OPEN.md`).
- Cost of one collision (item 9): 3.4-3.9e-9 s per tested pair on one A100, 3.3-6.7e-7 s on
  one core (runs C-20261115-180525-94ddd22, C-20261115-165500-c67e036).
- Momentum-constraint ratio of the King files (item 12): not chased; superseded by the
  constraint norms of the F21 read test (0.66 of the reference, squared).
