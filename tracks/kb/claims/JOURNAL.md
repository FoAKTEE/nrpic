# Journal of the claims helper (kb, wave 2: stages K8 and K9)

Predictions are written before the run they concern; outcomes after it, also when the
prediction failed. Labels: [VERIFIED] (checked against a file or a run named here),
[JUDGEMENT], [TO VERIFY].

## 2026-11-15 15:40 UTC: plan

Seed sources (read with `git show <branch>:<path>`, branch tips of 15:25 UTC):
A `scope/REFERENCES.md` (track/A-emd-pbh c7f4cfc), B `scope/REFERENCES.md` (767eb93),
C `scope/REFERENCES.md` and `stage/G0/REPORT.md` section 6 (904eb96), D
`scope/REFERENCES.md` (3276791), E has no REFERENCES.md: its errata request to kb
(`outbox/20261115T1410Z__to-kb__errata-s11-references.md`, 6330493), C's defect request
(`outbox/20261115T1320Z__to-kb__index-locators-typos.md`), F has no REFERENCES.md: its
novelty note `novelty/NOVELTY.md` (dd48b3e), core's
`tracks/core/interfaces/SECTION2_CORRECTIONS.md` on main (3da9086).

The notes use five locator styles (`(L264-268)`, bare `(879-882)`, `main.tex:103-118`,
`` (`:60-74`) ``, `` `TBH3.tex` lines 582-626 ``). Design [JUDGEMENT]: one claim per
locator group (text from the end of the previous locator to the end of this one); a
bracketed JUDGEMENT or TO VERIFY after a locator becomes a claim of its own; unlabelled
units take the default label the note's header states (B, C, F, core: "read at the
locator"), else `to_verify`. The knowledge base's own check, independent of the track:
the locator resolves in the store (paper, version, file, line within the file) and every
number the claim quotes (decimals, powers of ten, integers >= 10) occurs in the cited lines
+-3, as written or rounded to the quoted digits. Only a VERIFIED statement that passes
becomes `fulltext`; the others stay `to_verify` with the reason. Judgements never become
`fulltext`.

## P1 (prediction, before the dry run of `kb claim seed`)

Expected: 500-700 claims in all; at least 90 % of the paper locators resolve (the tracks
read the same store a few hours ago; misses would be parser errors or files in
subdirectories); of the VERIFIED claims at least 70 % reach `located` (the rest
`partial`: numbers paraphrased, e.g. "1e4" for "10^4", rounded values, numbers from the
track's own runs). Refuted if fewer than 90 % of locators resolve (the parser assigns
wrong papers or files) or fewer than 60 % of VERIFIED claims are located.
