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
