# Journal of the KB-G1 verifier (helper of kb, wave 2b)

Independent verification of the knowledge base for gate KB-G1, as a fresh reader: the
leads' reviews (`REVIEW.md`, `../REVIEW-wave2.md`, `VERIFY_RESULTS.*`, `STAGE_REPORT.md`)
were not read before the verdicts were written. Database: the snapshot `kb-data/db/current`
opened read-only (`sqlite3 ... ?mode=ro`). My code lives in `verifier/`; it does not import
`kb/kbtool`.

## 2026-11-19 14:05 UTC: plan and predictions (written before any check ran)

Snapshot: `kb-data/db/current -> kb-20261115-a848a06.sqlite` (709 papers, 54502 equations,
64857 bibliography entries, 688 claims, 3454 parameter rows; counted by a read-only query).

### Test P: twenty papers against their TeX source

Sample: 10 papers drawn at random from priority 3 and 10 from the other papers with
`source_kind = 'tex'`, seed 20261119 (`verifier/sample.py`). For each paper my own parser
(`verifier/texcount.py`) finds the main file (the file with `\documentclass` and
`\begin{document}`), flattens `\input`/`\include`/`\subfile`/`\import`, strips comments,
`\iffalse ... \fi` and `comment` environments, and counts

- display equations: one per top-level display environment (equation, align, eqnarray,
  gather, multline, alignat, flalign, displaymath, dmath, IEEEeqnarray, starred forms) and
  one per `\[ \]` and `$$ $$` pair;
- sections: `\section`, `\subsection`, `\subsubsection` (starred or not), per level;
- bibliography: `\bibitem` in the `.bbl` that belongs to the main file, `\bibitem` in an
  inline `thebibliography`, and the number of distinct cited keys found in the `.bib`
  files named by `\bibliography{...}`.

Prediction: for at least 18 of 20 papers the knowledge base's numbers agree with mine
exactly or within max(2, 3 %) per quantity, and every larger difference has a definitional
cause I can name (e.g. counting rows versus environments, a `.bbl` versus a `.bib` choice).
Refuted if three or more papers differ beyond that tolerance, or if any difference comes
from text the knowledge base lost (a missed `\input`, a dropped appendix, a truncated
bibliography).

Verdict rule per paper: CONFIRMED when all three quantities agree within tolerance or the
difference has a named definitional cause that I checked in the source; NOT CONFIRMED when a
difference stays unexplained; WRONG when the knowledge base is shown to have lost or
invented content.

### Test C: ten statements of the claims layer at their locators

Sample: 10 claims with label `fulltext` and at least one resolved locator, seed 20261119.
For each I read the source lines of the locator myself and judge whether the passage
supports the claim as worded. Prediction: at least 8 of 10 CONFIRMED; refuted if two or
more are WRONG (locator points at a passage that does not support or contradicts the claim).

### Test K: ten entries of the parameter index against this repository's source

Sample: 10 rows of `params` with `repo_id = 'local/nrpic'`, seed 20261119. For each I read
the file at the indexed commit (`repos.commit_sha`) with `git show <sha>:<path>` and check
that the recorded line holds a parameter-reading call with the recorded block, name, type
and default; I also look the call up on today's `main`. Prediction: 10 of 10 CONFIRMED at
the indexed commit; refuted if any row names a wrong block, name or default. Extra recall
check on one file (`athenak/src/particles/particles.cpp`): every `pin->GetOrAdd*`/`Get*`
call in the file has a row. Prediction: recall 100 % for calls with literal block and name.

### Test Q: the first questions answered again from the sources

I answer the nine questions of brief 12.9 from the TeX sources and the code, without reading
the answers in `FIRST_QUESTIONS.md` first, then compare. Prediction: no answer of
`FIRST_QUESTIONS.md` is WRONG; refuted by a number, locator or statement that the source
contradicts.

## 2026-11-19 14:10-14:25 UTC: outcomes

Development runs went to `scratch/kb/tmp/verifier_dev/` while the parsers were debugged; the
registered runs are `kb-20261119-142015-7620bd4` (P, C, K, Q), `kb-20261119-142303-f38a48c`
(follow-up of P) and `kb-20261119-142448-3ea268d` (follow-up of C). All three manifests are
hand-written: `nrpic-run submit --package tracks/kb/stage/KB-G1` was refused at 14:16 and
14:19 UTC because other kb helpers had uncommitted code in `kb/kbtool/` in this worktree.

**Test P** (prediction: >= 18 of 20 within tolerance, no lost content). Count part held: 18
of 20 papers agree on every quantity. "No lost content" FAILED: 1201.4794 has no
bibliography entry although its source has 46 AASTeX `\reference` items (parse status `ok`),
and gr-qc/9906015 (plain TeX, flagged `review`) has no sections, numbers or references.
Along the way my first parser was wrong twice, not the knowledge base: (a) I counted
environments, the knowledge base counts numbered rows of align/eqnarray; once I counted
numbered rows the numbers agree in 20 of 20; (b) my appendix detection missed
`\begin{appendices}` and `\counterwithin`. Old-style `\documentstyle` main files and the
plain-TeX file needed a fallback in my parser. Follow-up run 2: 20 of 707 TeX papers have no
bibliography entry; 14 have a list my parser recognizes, 11 of those are `ok`
(502 items missing) — a systematic gap in the bibliography reader (REVTeX-3 `references`
environment, AASTeX `\reference`, `\bibitem` aliases, `\harvarditem`).
Figures: `fig_papers.png` (four log-log panels, KB against mine; the two WRONG papers sit at
the lower edge of the bibliography panel), `fig_zero_bib.png`; both looked at.

**Test C** (prediction: >= 8 of 10, refuted by two WRONG). Held: 10 of 10 CONFIRMED. Notes:
claim 25 lost its second locator (L1084) between `claims.locator` and `claim_locators`; run 3
shows it is the only such case among 649 claims (a single count, no figure). Claim 254's
locator ends 11 lines before the collapse statement.

**Test K** (prediction: 10 of 10, recall 100 %). Held: 10 of 10, and 83 of 83 calls in
`particles/` and `pgen/nrpic/` at the indexed commit. Not predicted: the index is stale against
today's `main` (101 (block, name) pairs in 12 files missing: scalar field, collisions,
punctures, Bowen-York, geodesic, rng, kick, Newtonian). My own regex first missed defaults with
two levels of parentheses and treated commented-out calls as live; fixed before the registered
run. Figure: `fig_summary.png`, top right.

**Test Q** (prediction: no answer WRONG). Held. My answers, written before reading
`FIRST_QUESTIONS.md`, agree with it on all nine questions; it is more detailed in places
(AMR deposition, refinement thresholds, resampling, code defaults), and those details check
out. Equation numbers: 185 of 185 labels in the four papers equal my numbering; the 9 cited
numbers equal; 73 of 73 paper locators and 18 of 18 code locators contain the cited item
(two of my own regular expressions needed fixing: a `$` inside "0.01 au", and a sentence
that runs from L792 onto L793). Figure: `fig_summary.png`, bottom panels.
