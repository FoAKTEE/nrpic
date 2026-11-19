# Journal of work package s7_s8 (brief lines 554-625: sections 7 and 8)

Owner kb (helper), wave 3a, branch `kb/brief-check`, worktree `wt/kb-brief`.

## Entry 1, 2026-11-19T15:30Z: scope and predictions (written before any source was read)

Scope. Brief lines 554-625: section 7 (26 open questions, lines 556-592) and section 8 (where to
look for surprises, lines 596-622). Labelled statements: one [TO VERIFY] (line 583, the
Einstein-de Sitter case of question 20), one [BACKGROUND] (line 604, instabilities and the sign
of the gravitomagnetic interaction), and the blanket [JUDGEMENT] of section 8 (line 598). The
rest of the checkable content is unlabelled specific claims about cited papers: 35 arXiv
identifiers, each cited as relevant to a question or candidate, plus five explicit claims (lines
566, 569, 583, 613, 615). All 35 cited papers are in the store (checked 15:28Z: one directory
each under `kb-data/raw/arxiv/`).

Predictions (P) and what would refute them:

- P1. Every one of the 35 citations points to a paper that treats the topic the question names
  (abstract and body). Refuted by a citation whose paper is about something else (a CORRECTED
  row). I expect at most two or three imprecise ones, most likely among the many-paper citations
  (Q3, Q5, Q22, Q24), where a paper may be cited for a neighbouring topic.
- P2. Line 566 (convergence proof in spherical symmetry only, math/0209336): CONFIRMED for the
  paper; "none in three dimensions" survives an INSPIRE search of the papers citing it.
  Refuted by a convergence proof of a particle method for Einstein-Vlasov without symmetry.
- P3. Line 569 (Wu and Most: peak curvature of the prolate test still depends on resolution):
  CONFIRMED in 2611.12831 with a locator in the prolate section. Refuted if the paper states
  convergence of the peak curvature.
- P4. Line 583 [TO VERIFY] (stability of an Einstein-de Sitter-type background under
  Einstein-Vlasov): no theorem exists for the decelerating, spatially flat, Lambda = 0 case
  with massive Vlasov matter, and the notion itself is delicate because linear density
  perturbations grow on that background. Verdict expected NOT FOUND for a theorem, with the
  results that do exist (Milne, Lambda > 0, symmetric cases, accelerated or linearly expanding
  fluids) listed. Refuted by a paper proving nonlinear future stability of a k = 0, Lambda = 0,
  decelerating FLRW solution with Vlasov matter.
- P5. Line 604 [BACKGROUND]: the gravitomagnetic interaction of parallel (co-moving) mass
  currents is repulsive, opposite to the attraction of parallel electric currents. CONFIRMED,
  but I expect the store to hold no paper that states it in these words; then the verdict is
  CONFIRMED by a derivation or NOT FOUND in the store. The Newtonian instabilities (Jeans,
  radial-orbit, two-stream) are textbook (Binney and Tremaine is not on arXiv), so the locator
  may have to be a review in the store.
- P6. Line 613: "the mean-field limit has not been proved in general relativity" survives the
  search (no proof that many black holes converge to an Einstein-Vlasov solution). Refuted by
  such a proof.
- P7. Line 615: the phase sensitivity of the Newtonian restricted three-body separation
  probability is stated in a paper of the store (Sari, Kobayashi, Rossi 2010, or the F track's
  sources). Refuted if the store's Hills papers report phase-averaged results only.
- P8. Open questions. Most are still open; I expect PARTLY ANSWERED for Q1 (gauge for dust
  collapse: 2610.23218 itself proposes a lapse), Q2 (the cited paper answers the toy model),
  Q11 (threshold in EMD with particles, 2609.14218), Q13 (2609.03051 itself), Q19 (Burnett:
  results without symmetry in a generalized wave gauge), Q22 (the cited papers), and OPEN for
  Q6, Q7, Q8, Q16, Q18, Q20, Q23, Q25, Q26. Refuted for any question by a paper that answers it
  in full (ANSWERED); I expect none.

Method. TeX sources of the store, searched with `scripts/locate.py` (regex, file:line), and
`kb search` against the read-only snapshot `kb-data/db/current`; citing papers through
`harness/bin/nrpic-fetch-arxiv --inspire-query "refersto:arxiv:<id>"` (queries in
`specs/inspire_queries.txt`, run one after another by `scripts/run_inspire.sh`).

## Entry 2, 2026-11-19T15:38Z: first outcomes of the searches, and the prediction of run 1

Outcome so far (source reading, no run):

- The first INSPIRE batch failed as a search: `refersto:arxiv:<id>` is not resolved by
  INSPIRE, and every such query returned the unfiltered most recent records (hits_total 25291;
  stored, kept on record). Title queries worked. Second batch uses `refersto:recid:<n>` with
  the record ids of `kb-data/meta/inspire/<id>.json` (`specs/inspire_queries2.txt`); answers
  that other kb sessions had already stored today are reused without a new request
  (`specs/inspire_reused.txt`).
- P4 is refuted in part, and the brief's [TO VERIFY] of line 583 has an answer: two 2026
  papers by Fajman and co-authors, already in the store, treat the Einstein-de Sitter case for
  fluids: a proof of nonlinear stability for Einstein-Euler with a polytropic equation of state
  (n > 3) on T^3 (`2607.09326/v1/src/main.tex:141, 307`) and Gowdy-symmetric numerics
  (`2606.16879/v1/src/main_v2.tex:43`); for dust the background is linearly unstable
  (`2607.09326/v1/src/main.tex:317`). For Einstein-Vlasov with massive particles near
  Einstein-de Sitter I found no result: P4's "NOT FOUND for a theorem" survives for Vlasov
  matter only.
- P3 confirmed (`2611.12831/v1/src/main.tex:975`); P2's "proof in spherical symmetry"
  confirmed (`math_0209336/v1/src/main.tex:156-158, 221`).

Run 1 (`scripts/gem_sign.py`, processors, seconds): the [BACKGROUND] sign statement of line
604, checked by derivation because no paper of the store states it.

- Prediction. In linearized GR (harmonic gauge) the transverse coordinate acceleration of a
  test particle with velocity w at distance b from a mass M moving with V (both along x) is
  b^2 a_y / M = -[2 gamma^2 (1 - V w)^2 - (1 - w^2)]. Split by metric component, the
  gravitomagnetic h_0x part is +4 gamma^2 V w: repulsive (away from the source) for co-moving
  currents (V w > 0); the electromagnetic magnetic part for like charges, -gamma V w, is
  attractive for co-moving currents. The co-moving total is -(1 - V^2) = -1/gamma^2
  (attractive, the rest-frame Newtonian force transformed). The independent finite-difference
  evaluation of the full-metric Christoffel symbols agrees with the symbolic result to better
  than 1e-5 (relative) on a 13 x 13 grid of (V, w) in [-0.9, 0.9].
- Refuted if: the h_0x part is attractive for V w > 0; the co-moving total differs from
  -1/gamma^2; or the numerical and symbolic accelerations differ by more than 1e-5.
- Caveat written before the run: the split into "electric" and "magnetic" parts is gauge
  dependent; only the total is invariant (as a coordinate acceleration in the source's
  harmonic coordinates). The verdict on the brief's sentence rests on the standard
  linearized-harmonic split.
