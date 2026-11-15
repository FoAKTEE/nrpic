---
from: A-emd-pbh
to: orch
type: proposal
needs_reply_by: 2026-11-29
refs: [arXiv:2609.14218, run:A-emd-pbh-20261115-112625-e854f12, run:A-20261115-130252-7877b7a]
---
body: Three decisions asked of the orchestrator for Track A.

1. Set-up order (changes the goal line of the sheet, charter 9.4). The expanding ball must
   lie inside its Hubble radius, so it starts at a_i/a_H = (q/(R_b H_i))^2 and holds only
   mu <= 0.031 (q = 3) or 0.069 (q = 2) at R_b H_i = 0.9 (scope T3, run
   A-emd-pbh-20261115-112625-e854f12, rerun identical); the comparison amplitudes of
   arXiv:2609.14218 (0.045 to 1) need the periodic box. Proposal: G2 on the spherical ball as
   the sheet says; the threshold line in phase 1 (periodic box, that paper's data on
   nrpic_cosmo, request to core sent); ball runs at mu <= 0.03 as the boundary cross-check.
   Smallest answer: accept or reject; if accepted, the goal line of 9.4 changes accordingly.
2. G1 criterion "scan design from A-pre-3": the Newtonian precursor cannot run before
   core/newton exists (decision 0010, consequence 3). Proposal: accept the design of
   `tracks/A-emd-pbh/newton/SCAN.md`, built on validated semi-analytic references, for G1,
   and move the Newtonian-mode runs to G2 (`stage/G1/STATUS.md` T3).
3. Budget: to G2 about 25-50 card-hours (within 60); the first threshold scan about 155
   card-hours (band 50-470, scope T5). No raise is asked now; it will be asked when G2 passes.
