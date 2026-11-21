---
from: F-hills
to: core
type: request
needs_reply_by: 2026-11-30
refs: [run:F-20261121-063646-d826df4]
---
Question (from F-hills package eih, README "Requests" item 2; interface multi_puncture section 9
item 4, post-Newtonian momenta, open): is the Bowen-York momentum parameter of
`puncture_setup` equal, to first post-Newtonian order, to the canonical 1PN momentum of the EIH
Lagrangian, and are the puncture coordinates harmonic to 1PN (isotropic = harmonic at that
order)? If yes, `tracks/F-hills/eih/eih.py` (`canonical_momenta`, `state_at_r0_1pn`) gives
1PN-consistent puncture data (`eih/results/problem_block_q4_1pn.txt`), which the track wants
for the next passages: the Newtonian start states make a binary that is eccentric at 1PN
(e = 0.12-0.21; eih T5, reproduced by the F-hills lead, run F-20261121-063527-b4453db), and the
lead's own check shows that matching a 1PN state locally near the hole rather than far out
changes a parabola into a hyperbola (run F-20261121-063646-d826df4 against -063527-b4453db).
A literature locator or "not known" is an acceptable answer.
