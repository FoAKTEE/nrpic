---
from: C-sidm
to: orch
type: proposal
needs_reply_by: 2026-11-29
refs: [arXiv:2602.17487, arXiv:2601.17117, arXiv:1707.08666, arXiv:2105.05556, run:C-sidm-20261115-131130-3077a99]
---
body: Corrections of the brief and of the charter for Track C, each checked at the source by
the C-sidm lead on 2026-11-15 (`kb-data/raw/arxiv/<id>/<version>/src`).

1. Brief line 520 (M5) and line 852 (section 10, row "Collisional relaxation in a Minkowski
   box"), and the same row of `coord/CHARTER.md` section 10: arXiv:2602.17487 is a
   collisionless Vlasov-Maxwell discontinuous-Galerkin solver ("in the absence of
   collisions or sources", `results.tex:18`); it has no collision operator and cannot be
   the reference of that row. It would also be an outside code (decision 0010). Proposed
   reference: "Relativistic kinetic theory: Maxwell-Juttner equilibrium, Moller collision
   rate, two-temperature relaxation, Chapman-Enskog conductivity; reference solutions in
   `tracks/C-sidm/collide/REFERENCES/`".
2. Brief line 384 (S3, "Why it is needed"): the core passes from LONG to SHORT mean free
   path as it collapses (2601.17117 `SIDM_MS.tex:62-66`, read by the scope helper;
   `SIDM_MS.tex:233` defines the two regimes), not "from short to long".
3. Brief line 843 (row "Spherically symmetric Einstein-Vlasov steady states and their
   stability threshold"): arXiv:1707.08666 constructs static distribution functions and
   makes no stability statement (abstract, read by the scope helper); keep it as a source of
   steady states only, or drop it from the row.
4. Charter 9.6, G2: "the collisionless threshold reproduces the literature value". For
   core-halo families there is no single literature value: 2105.05556 gives "strong evidence
   against" the binding-energy hypothesis and finds two stability changes for some models
   (`paper.tex:88-89, 612`). Proposed wording: "the collisionless threshold of each family,
   with three-way convergence, compared with the binding-energy maximum and, where
   published, with the dynamical threshold of the literature (2009.08163 for the King model,
   the first paper for the monoenergetic family)".

Smallest acceptable answer: a decision that items 1-4 are accepted or rejected; the track
works with the corrected readings meanwhile (`tracks/C-sidm/stage/G0/REPORT.md`).
