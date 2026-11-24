# Journal of package ingest4 (kb helper, wave 3 batch 11)

Package brief: batch-11 task "ingest4" (sources the tracks asked for and the store does not hold;
the six old-style reference lists that ingest3 left; QA with the parse rate against the bar;
answers to the requesting tracks). Session start 2026-11-24 12:51 UTC (04:51 PST). No PAUSE flag.
kb/main at a9d5bdb2 (main bc180c26 merged, "Already up to date"), tree clean, no stranded files of
an earlier ingest4 (the directory did not exist). Card time of this package: 0.

## Entry 1 (2026-11-24 13:05 UTC): what the requests and the store say before any run

Requests (read from the senders' branches):
- A (track/A-emd-pbh, outbox 20261121T080816Z): (1) a source that the t = const slices of the
  quasi-spherical Szekeres dust solution are conformally flat; (2) how the apparent horizon of a
  Szekeres model relates to R = 2M (Krasinski and Bolejko 2012). kb's answer of batch 9
  (tracks/kb/outbox/20261121T235027Z__to-A-emd-pbh__refutation-742-and-szekeres.md) gave
  1612.08222v3 L162 (Cotton-York tensor zero) and 2605.30145v1 L535 (R = 2M) and left the
  Krasinski-Bolejko paper and a conformal-flatness source to this package.
- C (track/C-sidm, outbox 20261121T081156Z, reply by 2026-11-28): (1) hard-sphere conductivity
  beyond the first Chapman-Enskog approximation, relativistic or not; (2) DSMC cell-size and step
  errors of transport coefficients (Alexander-Garcia-Alder 1998, Garcia-Wagner 2000,
  Hadjiconstantinou 2000).
- F and D: the thirteen ids of tracks/kb/claims_tracks/README.md "orch (manifest)". The store
  already holds 2605.22525 (ok, G21, added by ingest3's frontier step), so 12 are missing:
  F 2609.20338, 2608.22735, 2608.16986, 2610.27775, 2212.10891, 1303.1540, 2602.06961,
  2610.20594; D 2307.02474, 2307.10708, 2306.08199, 1904.03781. Claims 409 (D), 447, 449, 450,
  452 (F) wait for them; claims 413 (Einstein-Straus 1945) and 416 (ApJS 58, 39, 1985) cite
  originals that predate arXiv.

The six old-style papers (all status review): the parse score is below 0.75 because title,
abstract and sections score 0 (parse_json.quality.components); the quality score has no
bibliography component. Reference formats, read in kb-data/build/tex/<key>/flat.tex (data, not
run):
- astro-ph/0306304: `\begin{center}References\end{center}` then `\begin{enumerate}` with `\item`;
  numeric citations `[1]` in the text.
- astro-ph/9306009: `\centerline{\bf References}`, `\def\i#1{\par\hang\indent\llap{[#1]\quad}...}`,
  entries `\i\Guth ...` with `\def\Guth{1}`; citations `\r{\Guth,\Olive}`.
- astro-ph/9510056: `\begref{References}` then `\ref` paragraphs (A&A macros, author-year text).
- astro-ph/9607124: `{\Large \noindent \bf References}` then `\noindent[1] ...` paragraphs.
- gr-qc/9604001: `{\bf References}` then `[1] ...` separated by `\next`.
- gr-qc/9906015: `\centerline{\rmm References}` then `\ref` paragraphs (author-year).

## Predictions (written before run 1)

- P1 (identification of the 12 ids): the arXiv API returns a record for each of the 12 and each
  title fits the subject the claim gives it; at least 11 of 12 come as TeX (one may be PDF only).
  Refuted if an id has no record or a title does not fit.
- P2 (Track A): INSPIRE finds the Krasinski-Bolejko paper on apparent horizons in quasi-spherical
  Szekeres models with an arXiv id (probability 0.85 [JUDGEMENT]). A paper on arXiv stating in
  words that the t = const slices are conformally flat is found by INSPIRE title/abstract or
  full-text queries with probability 0.5; the classical statement (Berger, Eardley and Olson 1977)
  predates arXiv and would be recorded, not fetched. Refuted if the queries return no such paper
  (then the answer says "not found" with the queries).
- P3 (Track C, DSMC): at least two of the three named DSMC papers have no arXiv e-print (INSPIRE
  may hold no record at all, being a high-energy index); an arXiv paper on the cell-size or
  step error of DSMC transport coefficients is found through INSPIRE with probability 0.3.
- P4 (Track C, conductivity): an arXiv paper giving the relativistic heat conductivity of a gas
  of hard spheres (constant cross section) at more than one moment order is found (probability
  0.8); a non-relativistic Sonine-series table on arXiv with probability 0.4.
- P5 (ingest of the additions): every fetched TeX addition parses with status ok except at most
  one review; the recorded parse rate stays at or above 96.5 % (now 719 of 744 = 96.64 %).
- P6 (old-style lists): entries for all six papers, each count equal to an independent count of
  the entry markers in the source (my own grep in run R-count, made before the parser runs);
  citation rows for the four numeric papers (0306304, 9306009, 9607124, 9604001), none for the
  two author-year papers (9510056, 9906015). The parse status of the six stays review (score has
  no bibliography term) unless headings or titles are also recovered.
- P7 (no regression): a dry run over all other TeX papers changes no paper's entries or citation
  rows: the new rule fires only where no recognised list exists (at most 3 others change, and only
  by gaining entries).
- P8 (QA): golden questions with the hybrid mode stay at 28 of 32 (paper) within one; the
  recorded parse rate is reported against the 95 % bar and passes it.
