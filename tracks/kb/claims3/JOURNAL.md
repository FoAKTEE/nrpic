# JOURNAL of the kb package claims3 (wave 3, batch 14, 2026-11-24)

Helper of owner kb, one work package (decision 0035 item 5; stage/KB-G3/OPEN.md O1-O3, O5).
Entries are appended; nothing is rewritten. Predictions are written before the test or the
write they concern; outcomes follow, also when a prediction fails.

## Entry 0, 2026-11-24 18:09 PST: state at the start

- `git merge --no-edit main` in wt/kb: clean merge (decision 0035, batch-14 spec). No PAUSE flag.
- tracks/kb/claims3 did not exist; no stranded files of this package. Worktree clean.
- Working database kb-data/db/kb.sqlite: 864 claims; db/current -> kb-20261124-9872d21.
- Only kb package of batch 14 (harness/workflows/batch-14.json items[2]); no other helper
  writes kb/ in this batch, so the tool change of item 2 goes into kb/kbtool (kb/** is kb's,
  tracks/kb/OWNERSHIP), committed with this package as claims_brief did for its seeder.

## Entry 1, 2026-11-24 18:16 PST: definitions and predictions (before any write or draw)

### Item 2: `kb claim supersede` (tool)
Design: `supersede(con, old, by, evidence, text=... | to=N)`. With `--text` it adds a new claim
(kind, paper, track copied from the old one unless given; label fulltext needs a locator, whose
rows are written at once, so no separate relocate), with `--to N` an existing claim takes the
place. The old claim gets label refuted and a new status `superseded` (so that a claim text
corrected is told apart from a statement of a paper refuted), one event `supersede` on each
side, and a row in a new side table `claim_links(from_id, to_id, relation, at, by, evidence)`.
`kb claim show` lists the links both ways. Refused: an unknown id, the claim itself, a claim
already superseded, a target that is refuted or superseded.
- P4a. New tests in kb/tests/test_claims_supersede.py pass; the whole kb suite passes with them
  (baseline count taken before the change). Refuted by any failing test.
- P4b. Backfill of the first case: 682 -> 862 gets its link row and status superseded, its label
  stays refuted, 862 is unchanged but for the event; `kb claim show 682` names 862. Refuted if
  any other claim row changes (checked by a before/after dump of claims and claim_meta).

### Item 1: brief seeds 803 and 805
- P1 (803, "status of stability results for matter-dominated FLRW under Einstein-Vlasov").
  Expected from what the store is said to hold (1709.00267, 1706.09501/claim 752): the store has
  proofs of future nonlinear stability for Vlasov matter on accelerated or linearly expanding
  backgrounds (Lambda > 0; the Milne geometry, k = -1, Lambda = 0, which is vacuum-dominated),
  and no proof for a matter-dominated decelerating FLRW (Einstein-de Sitter type) under
  Einstein-Vlasov. Outcome form: 803 answered by an annotation, and the answer as a new
  fulltext claim with locators in the papers read (the 714 -> 863 rule). Refuted if a paper in
  the store proves nonlinear stability of a matter-dominated Lambda = 0 FLRW under
  Einstein-Vlasov, or if the store holds no stability paper for FLRW with Vlasov matter at all.
- P2 (805, three derivations to check). Expected: each of the three was re-derived by a track
  with registered runs: the expanding dust ball by A and core (coord/notes/
  derivations_to_check.md section 1, Checked), the Einstein-Straus bubble by D (section 2, four
  corrections), the strong-field Hills scale by F (novelty run A
  F-hills-20261115-045435-f62d553; F's verifier V3 F-hills-20261115-144954-b5b0bce).
  Outcome: 805 annotated with those locators. Refuted if a part has no recorded derivation
  with a run or a symbolic check in the track's branch (that part then stays open, with reason).

### Item 3: the weak class, sample of thirty
Query (scripts/weak_class.py, docstring): P = claims labelled fulltext, abstract or title_only;
W = those of P whose label was set by a pipeline step (WA auto locator check, WQ claims_tracks
queue, WB claims_brief join/defects, WM 12.8 map), minus those a person has read against their
own wording (audits P2 and AU, the leads' readings, the KB-G3 verifier's verdict files) and the
claims named in items 1 and 4. Count on kb.sqlite at 18:14 PST (read-only, no draw):
W = 573 of P = 713: WA 426, WQ 90, WB 43, WM 14; allocation of 30: WA 22, WQ 5, WB 2, WM 1.
Seed of the draw: 20261125 (file SEED, committed with this entry, before the draw).
Verdicts, decided per claim at every stored locator in the raw source (the full line where
needed, whole-file search for a quoted number or phrase not in the cited lines):
- right: every factual part of the text (numbers, attributions, what a statement is about) is
  supported by the cited passage as worded;
- right, locator incomplete: the wording is supported, but part of it is at a line outside the
  locator (relocated; counted right);
- wrong: the text says something the source does not say, or says it of another object
  (corrected by supersede);
- fragment: no statement (re-seeded or closed as in item 4; counted not right).
- P3a. 25 to 29 of 30 right (83-97 per cent; the verifier's 17/18 in S1 and S2 and the audit's
  37/40). Refuted if fewer than 24 or all 30 are right.
- P3b. The errors sit in WA (cut texts, locators) and WQ (wording against reading); none in WM.
  Refuted if an error is found in WM, or no error in WA and WQ together.
- Rate reported with the Clopper-Pearson 95 per cent interval, and the stratum-weighted estimate.

### Item 4: fragments
The twenty named: 85, 620, 549 and claims_tracks/AUDIT.md's 81, 84, 171, 179, 187, 192, 213, 277,
290, 314, 424, 431, 619, 621, 622, 623, 625. Rule: re-seed from the note row of the origin commit
(a whole sentence, all its locators, read at the source, verified) and supersede the fragment by
it; where a sibling claim of the same row already carries the statement, close the fragment
with `--to` that claim; where the row holds no statement either (a bare "Abstract" heading of a
served record), close it with the reason and no successor is invented.
- P5. Every fragment traces to its note row at its origin commit (git show); at least 12 of the
  20 get a re-seeded whole-sentence claim; none is left open. Refuted if a note row cannot be
  found or a fragment stays without an action.

### Item 5: downloads table
- P6. With an exclusion list kb/manifests/downloads_excluded.tsv (0707.4654, 1006.1632; decision
  0035 item 5) read by `kb verify-downloads`, a registered run of verify-downloads leaves 763
  rows (765 - 2): the two ids absent, gr-qc/0608095 still present (not named by 0035), the
  files under kb-data/raw/arxiv/0707.4654 and 1006.1632 unchanged (sha256 of source.bin before
  and after); exit 1 only for the known gr-qc/9412071. Refuted by any other change in the
  count or by a changed file.

## Entry 2, 2026-11-24 18:24 PST: draw done; tool changes and their tests

- Draw (run kb-20261125-021654-6799dfd, seed 20261125, after commit 6799dfda): W = 573 as
  counted in entry 1; sample of 30 in `weak_sample.tsv` of the run directory (WA 22, WQ 5, WB 2,
  WM 1).
- P4a outcome: HELD. `kb claim supersede` (kb/kbtool/claims_db.py `supersede`, `links`; CLI in
  claims_cli.py; status `superseded`; table claim_links; `refute` refuses a superseded claim;
  `kb claim show` lists links and `superseded_by`; qa_figures counts the new status) with four
  tests in kb/tests/test_claims_supersede.py. Downloads exclusion (kb/manifests/
  downloads_excluded.tsv read by kbtool/inventory.py) with one test in test_inventory.py. Whole
  suite before: 269 tests (1 xfail), after: 274 (1 xfail), all others pass. The first CLI test
  failed once on my own test parser (no --data-root on the test's top parser), fixed in the test.

## Entry 3, 2026-11-24 18:36 PST: readings done; outcomes of P1, P2, P3 (by reading); predictions for the writes

All readings at the raw sources (kb-data/raw/arxiv, as text; `claims_tracks/scripts/read_claim.py`,
`scripts/grep_src.py`), the full line where the stored one was cut, whole-file search for words
not in the cited lines. Nothing is written to the database before the registered runs below.

### P3 outcome (item 3, sample of 30 of run kb-20261125-021654-6799dfd)
Verdicts (one row per claim in `SAMPLE_VERDICTS.tsv`, written by `scripts/ledger.py`):
- right 26: 6, 40*, 88, 163, 214, 233, 235, 292, 328, 348, 373*, 407, 468, 474*, 479, 501, 568,
  578 (WA); 720, 721* (WB); 775 (WM); 308, 467, 662, 669*, 673 (WQ). (* = right, locator
  incomplete: a supported part sits outside the stored locator: 40 L89, 373 L241, 474 L838-840,
  721 L189 and 2511.20567 L62-64, 669 L463; the locators are extended.)
- not right 4, all in WA: 29 fragment (subject and condition "for mu <= 0.045" cut away), 126 part
  unsupported ("as arXiv:2109.04896" is A's comparison, not stated by 2306.11810), 482 cut text and
  wrong label (a [JUDGEMENT] that the Hermite weights are the Catmull-Rom weights stored as
  fulltext; the paper never says Catmull-Rom), 572 fragment (a cut citation list joined to one
  supported clause).
- Rate right 26/30 = 86.7 per cent; Clopper-Pearson 95 per cent interval and the stratum-weighted
  estimate are computed by `scripts/ledger.py` (registered run below).
- P3a HELD (25-29 predicted). P3b HELD in its refutation clause (no error in WM; errors in WA),
  but its description failed in part: I expected errors in WQ (wording against reading, the 682
  case) and found none in the five WQ claims; all four errors are cuts or mislabels of the
  seeder (WA). Five claims carry a cut start ("i.e.", "and", "which") yet a complete statement
  (373, 467 right; 29, 482, 572 not), a pattern the fragment query of claims_tracks (text shorter
  than 25 characters) does not catch.

### P1 outcome (seed 803)
Store search (scripts/seed803_search.py, to be registered): 20 papers by title or by chunks with
Vlasov + FLRW/Friedmann/de Sitter/Robertson + stab. Read at abstract or cited lines: 1709.00267
L363, L391-393; 1106.1367 L2184-2217; 1402.7085 L50-54; 2012.14241 L329-330; 2306.17774 L49;
1904.13290 L333; 2402.08544 L152; 2607.09326 L96, L136-178, L311, L317-321; 2606.16879 L43;
1306.6223 L157-160 (Lambda > 0); gr-qc/0512031 L143-148 (Bianchi I dynamics); the others are
Minkowski stability, static clusters, Vlasov-Poisson or high-frequency limits (titles).
- P1 HELD in its refutation clauses: no paper in the store proves or tests nonlinear stability of a
  matter-dominated Lambda = 0 FLRW under Einstein-Vlasov, and the store does hold FLRW stability
  papers with Vlasov matter. Not foreseen: (a) a decelerated FLRW IS proven stable under
  Einstein-massless-Vlasov (2306.17774, radiation-like, spherical perturbations on R^3), and
  Bianchi I massless data isotropize to a radiative EdS (1904.13290); (b) the matter-dominated EdS
  IS proven nonlinearly stable for a polytropic fluid with n > 3 on T^3 (2607.09326), with
  numerical Gowdy evidence (2606.16879), while dust is linearly unstable. My "accelerated or
  linearly expanding backgrounds only" was too narrow.
- Write: a new fulltext claim carrying the answer with 13 locators; 803 annotated (stays
  to_verify, a question, as 714 -> 863); 790 (brief L583, the same question for EdS) annotated
  with a pointer.

### P2 outcome (seed 805)
- HELD: each part has a re-derivation with symbolic checks and runs on the tracks' branches: dust
  ball A (expball/DERIVATION.md section 8, A-emd-pbh-20261115-121654-6bfb707 and others) and core
  (JOURNAL-id.md, check_derivation.py); Einstein-Straus D (einstein_straus/DERIVATION.md, run
  D-bh-dress-20261115-042626-f3da881, 48 identities, four corrections), with the a, m_p of
  sections 3-4 recomputed in D's G1 gate review (GATE_REVIEW.md L76); Hills scale F (run
  F-hills-20261115-045435-f62d553, verifier V3 F-hills-20261115-144954-b5b0bce; correction: part of
  the brief's box lies below the plunge bound). Write: 805 annotated with these locators; it
  stays to_verify (an instruction). No question to the tracks was needed: the answers are in git.

### Item 4 plan (P5)
20 fragments traced to their note rows at the origin commits (git show): 12 superseded by a new
whole-sentence claim read at the source (619, 620, 621, 622, 625 abstract-labelled; 81, 84,
179, 192, 213, 277, 424 fulltext), 85 joined to 84's new claim, 5 closed with `--to` the
sibling that carries the row's statement (623 -> 624, 290 -> 289, 314 -> 313, 431 -> 430; 85),
3 withdrawn because the row has no statement for them (171, 187: "Abstract: line(s) ..."
pointers; 549: a list heading). `withdraw` was added to the tool for these (status withdrawn,
label refuted; test in test_claims_supersede.py; 276 tests).

### Predictions for the registered writes (plans in `plans/`, dry runs agreed)
- W2 (plan_item2, 682 -> 862): 1 action, no new claim, 682 refuted/superseded with one link,
  others' hash unchanged, exit 0.
- W3 (plan_item3): 30 actions, 4 new claims (successors of 29, 126, 482, 572), every locator
  row of the touched claims resolved, others unchanged, exit 0.
- W1 (plan_item1): 4 actions, 1 new claim with 13 resolved locator rows, others unchanged.
- W4 (plan_item4): 20 actions, 12 new claims, 3 withdrawn, 5 links to existing claims, others
  unchanged.
Refuted by an exit other than 0, a locator row that does not resolve, or a changed hash of the
other claims.
