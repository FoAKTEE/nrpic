# KB-G1: what is still open (owner kb; updated by the wave-2b lead 2026-11-19)

The four criteria of KB-G1 are met and the package now has a verifier's report (`VERIFIER.md`):
`CHECKLIST.md` has every item PASS. What KB-G2 still lacks is in `../KB-G2/OPEN.md`.

## Items of the verifier that remain open (each with the track's action: ../REVIEW-wave2.md)

- Bibliographies lost for unusual reference-list formats (verifier defect 1; WRONG for 1201.4794):
  20 TeX papers without a bibliography entry, 11 of them with status ok (502 reference items
  missing). Parser fix and re-ingest planned; the re-ingest renumbers chunks that claims point
  at, so it needs a chunk remap of the claims layer first.
- gr-qc/9906015 (priority 3) and two other plain-TeX papers: no `\eqno` numbers, sections or
  `\ref` bibliography; flagged review, a plain-TeX reader is open.
- Minor locator offsets (claim 254, FIRST_QUESTIONS Q8 L792/L793; Q9's local line range is right at
  a1c2237, on main the deposit task is at line 47): content right, left as written.
- Not checked by the verifier: the other 63 repositories of the code index, symbols, code chunks,
  claims other than fulltext, the inventory report itself.

## Fixed in wave 2b

- Parameter index of this repository stale (verifier defect 2): re-indexed at main 5deee18, run
  kb-20261119-161451-e15d1b8; the verifier's own script finds 0 stale pairs (kb-20261119-161909-08df7ea).
- Claim 25 lost L1084 (defect 4): cause was `kb claim verify --locator` (lead, wave 2), which did
  not rewrite the locator rows; fixed in code with a test, claim 25 has both rows (run
  kb-20261119-161413-31e6b85); 0 of 661 claims now disagree.
- K1 metadata and the comparison with brief section 16: done (pdf_meta; EVIDENCE.md).

## Open sub-points of the first answers (wave 1, unchanged)

- Q1, Q3: the number of filter passes and every numerical Z4c damping and gauge value are not in
  2611.12831; only the authors can supply them (decision 0002, a group step).
- Q2: how the momentum constraint is handled for the two moving clumps of Sec. 4 of 2611.12831:
  the verifier confirms the paper does not say (no "constraint" in L1313-1362). [TO VERIFY with
  the authors]
