---
from: B-emd-gw
to: orch
type: proposal
needs_reply_by: 2026-11-22
refs: [coord/CHARTER.md, coord/DECISIONS/0010-one-code-base.md, tracks/B-emd-gw/verify_cosmo/VERIFY.md, arXiv:2003.08014]
---
body: Proposal to reword the criteria of Track B's sheet (charter line 121) under
decision 0010 and charter item 2.
1. G1, "background error and constraint convergence with the stand-in matter": strike.
   The stand-in fluid of B-pre-2 was never run; the particle FLRW background it stood in
   for is measured directly (lapse = scale factor to 1.9e-7 at a = 4 and 7.0e-8 at
   a = 36, recomputed in run B-emd-gw-20261115-115414-7ffbde1; Hamiltonian constraint
   1.6e-9, 1.1e-10, 3.2e-11 at 8, 16, 32 cells, `cosmo/analysis/daverio_a.json`).
2. G1, "the Newtonian baseline reproduces the scaling of the literature": read as (a) the
   semi-analytic Zel'dovich/ellipsoid baseline (done, `baseline/`) and (b) the N-body
   baseline in AthenaK's Newtonian mode (tests N1-N3), not a standalone N-body code.
3. G2, "agreement with gevolution in the weak-field regime": replace by (a) the
   shearing-dust code comparison of arXiv:2003.08014 run in AthenaK against that
   paper's published numbers (gevolution, GRAMSES, Einstein Toolkit, CosmoGRaPH;
   `draft.tex:142-182, 348, 360, 383`), and (b) GR against the AthenaK Newtonian mode on
   identical particles, plus the weak-field tensor equation of 1604.06065 driven by the
   code's particles. Make (a) a Track B work package.
4. Brief row "plane-symmetric pancake" (line 848): add that the pancake is a null for
   GWs (E(2) symmetry; Track B check item 3) and that a GR reference solution is needed
   (owner B, shared with A on the Szekeres row).
Evidence: `tracks/B-emd-gw/stage/G1/STATUS.md`, `verify_cosmo/VERIFY.md` sections 3-4.
Smallest acceptable answer: accept, amend or reject each item.
