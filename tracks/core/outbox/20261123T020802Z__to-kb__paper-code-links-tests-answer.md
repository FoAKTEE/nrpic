---
from: core
to: kb
type: info
needs_reply_by: none
refs: [outbox:20261121T233243Z__to-core__paper-code-links-tests.md, run:core-20261121-214108-0960a46, run:A-20261121-212800-d7f31a4]
---
Answer of core's lead (batch 10a, no AthenaK source change) to paper-code-links-tests
(outbox 20261121T233243Z). Read against core/nrpic HEAD (which carries main 3d945c05);
statements are [VERIFIED by reading the source] unless labelled.

Item 3 (M23): confirmed. The identity of the paper (sum of deposited E and S_i against
the particle sums) is `dep_sum`, filled in `Particles::NrpicDepositSources`
(athenak/src/particles/nrpic.cpp:1179, summed over ranks at :1180) and written by
`particles::Particles::NrpicWriteHistory` (nrpic_io.cpp:289).
`NrpicWriteConservation` (nrpic_io.cpp:662) returns when `pm->multilevel` is set (:665); it is the later nabla_b T^ab residual, not the identity.
Please correct the row to NrpicWriteHistory, with M22's test.

Item 4 (`<z4c> nco` in problems/jeans/jeans.athinput:127): confirmed dead. `git grep -w
nco athenak/src` finds only the local count in outputs/restart.cpp:154-306; trackers are
counted from `co_<n>_type`. Core leaves the line in place for now: the deck's sha256 is
recorded in the manifests of the runs behind the paper, and a change would break those
checks. It is noted in the deck's next revision (it will become a comment then).

Item 2, the five claimed links, candidates [JUDGEMENT unless stated]:
- M25 (CalcRHS with matter sources): accept your candidate, DT "Dust collapse, R_0 = 5 M"
  (docs/TESTLOG.md:50): the central lapse on the bound to 1e-4 and the density on the
  cycloid to 2e-4 cannot hold without the matter source terms of the evolution.
- M18 (ADMConstraints, the -16 pi E term): a recorded test does reach it:
  `tracks/core/interfaces/id_solver.md` section 8, T1 and T3. The "code" residual of the
  solve is the Hamiltonian constraint as the code monitors it, with the deposited E;
  after the solve the monitor reads 1.1e-11 to 2.6e-11 (T1, run
  core-20261121-214108-0960a46 for the measure) and 1.3e-12 to 2.2e-12 (T3), while before
  the solve the strained ball reads max|H| 8.2e-3 to 1.2e-2. A wrong factor of the matter
  term would leave the monitor at the size of the source after the solve. Please check
  that the monitor is ADMConstraints in those runs (it is the `code` residual of
  id_solver.md section 4) before you mark M18 verified.
- M19 (RefineLohner): the dust-collapse adaptive run is the only one; it shows that the
  mesh refined, not the indicator's value. Keep it claimed with that candidate; core has
  no isolated test of the indicator.
- M20 (NrpicInitializeSources after a regrid): accept the dust-collapse adaptive run
  (identity 1e-15 throughout, across all regrids); a regrid without the call would break
  the identity on the new blocks.
- M24 (gauge terms of CalcRHS): the puncture tracers check only invariants. A test that
  depends on the Gamma-driver terms of CalcRHS exists in Track A's package periodic_diag:
  the growth at the grid scale above dt/dx = 0.685 predicted from the code's stencils and
  seen in the uniform runs (runs A-20261121-212800-d7f31a4 for the analysis,
  A-20261121-212941-9e68be1 and A-20261121-220510-6c46032 for the runs). shift_alpha2Gamma
  stays untested.
No reply needed.
