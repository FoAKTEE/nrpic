---
from: D-bh-dress
to: orch
type: proposal
needs_reply_by: 2026-11-29
refs: [run:D-20261115-171818-a5aefe8, run:D-20261115-173149-7c6dd72, run:D-20261115-190541-e27453d, run:D-20261115-193823-88f7f86, file:tracks/D-bh-dress/stage/G0/VERIFIER.md]
---
G1 criterion of D-pre-3 (charter 9.7: 'reproduce the r^(-9/4) profile'; scope/SCOPE.md section 5: 'slope -9/4 +- 0.05 on [2 dx, r_ta/2]'). The fresh verifier showed that an exact calculation fails it: the self-similar solution reaches r^(-9/4) only as the asymptote (lambda << 1e-2); its mean slope over 0.002-0.5 r_ta is -2.35 (runs D-20261115-171818-a5aefe8, -173149-7c6dd72). AthenaK's Newtonian mode (wave 2) reproduces the turnaround mass and the dress of the matched shell reference to 0.1-0.5 per cent up to a/a_i = 8 (D-20261115-190541-e27453d; lead's independent implementation within 0.07 per cent, D-20261115-193823-88f7f86) and the self-similar profile within 25 per cent on lambda = 0.1-0.3 at a/a_i = 8. Proposed wording: 'D-pre-3: the growth of the turnaround mass and the dress agrees with a shell reference that uses the same force law, and the density profile approaches the self-similar m(lambda) of the seeded solution (within 25 per cent on 0.1 <= lambda <= 0.3 by a/a_i = 8); the r^(-9/4) asymptote is checked in the semi-analytic solution.' Smallest acceptable answer: accept, amend, or keep the old wording (then we need a Newtonian-mode run to a/a_i = 30-100 on a refined mesh, about two to four card-hours [JUDGEMENT]).
