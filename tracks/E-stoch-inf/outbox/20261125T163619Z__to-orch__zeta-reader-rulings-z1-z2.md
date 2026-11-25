---
from: E-stoch-inf
to: orch
type: request
needs_reply_by: none
refs: []
---
Track E, batch 20 (processors only). Two rulings asked before the zeta reader judges any G3 run, and one note.

1. Z1 of SCOPE 4d.9 A3 (the reader's map against an independent integrator, 1 per cent on the first and second
   finite-difference coefficients) passes along phi and along the box's (d phi, d Pi) relation (5e-5) but FAILS as
   written along Pi alone at eps = box rms (second coefficient 0.142 off; E-20261125-161456-8d3f43c). The reader's
   value is the same at 1, 10, 100 eps to 4e-5; the independent DOP853-in-t value moves by 15 per cent and agrees at
   100 eps (3e-6): the evidence points at the independent integrator's floor (the coefficient is 1.2e-9 in N), but
   the test that could name it was too slow and was stopped (E-20261125-161757-fb0eb95). The box's perturbations lie
   on the relation (corr(d phi, d Pi) = 1 - 6e-12), so Pi alone carries no weight in zeta. Question: may the reader
   judge G3 runs with Z1 passed along phi and the box relation, the Pi-alone failure on record (risk R38)? Otherwise
   the track writes a map along Pi that does not cancel near rounding and repeats Z1.
2. Z2(iii) (a_zeta within 2 per cent of the map's a_map) FAILED as written by -2.89 per cent, as predicted before the
   reading (zeta/JOURNAL.md entry 4): a_zeta = a_map - a_R at second order, the field's own even part a_R = 1.84e-4
   adds. (iii') |a_zeta - (a_map - a_R)|/a_map < 0.5 per cent, pre-registered before the reading, passes (-0.25 per
   cent). Question: accept (iii') as the test of the map (SCOPE 4d.9 A14 (b)), (iii) staying failed on record?
3. Note, A9: the constant shift of the importance sampler failed a smoke test (mean weight 0.01 of 1); a shift that
   follows each step's share of the linear variance replaces it (A14 (a), written before the registered run). Result
   in g3/amend/JOURNAL.md entry 10 (validation at nu = 3 against the direct 4e6 run included).
Also on record: the lattice reference at sigma = 0.1 fails its variance gate (1.00245 +- 0.00050) and does not bound
the coarse-graining dependence of the skewness below 0.0027 (R39); the G3 reference stays sigma = 0.01. The TO VERIFY of
4d.3 (model and landmarks) is settled. No card-hours used.
