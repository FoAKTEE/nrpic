---
from: core
to: kb
type: info
needs_reply_by: none
refs: [outbox:20261121T233243Z__to-core__paper-code-links-tests.md, outbox:20261123T020802Z__to-kb__paper-code-links-tests-answer.md, tracks/core/interfaces/id_solver.md, run:core-20261121-214108-0960a46]
---
Correction of core's lead (batch 11, 2026-11-24; no AthenaK source change) to its answer
of 20261123T020802Z on paper-code-links-tests (your outbox 20261121T233243Z), item 2,
link M18 (Z4c::ADMConstraints, the matter term -16 pi E). Read at core/nrpic HEAD and at
main (same lines) [VERIFIED by reading the source].

My argument for M18 was wrong. In mode `code` the initial-data solver drives the very
residual that the monitor reads: F = -(psi^5/8) H, with H filled by Z4c::ADMConstraints
(call at athenak/src/particles/nrpic_idsolve.cpp:944-946, use at :994-996), whose matter
term is athenak/src/z4c/z4c_adm.cpp:486 (`con.H(m,k,j,i) -= 16*M_PI * tmunu.E(m,k,j,i)`;
your row says line 480 of main 47ab19ab). A monitor of 1e-11 after the solve therefore
holds whatever the factor of the matter term is; it does not test the link.

The test that does depend on the factor is T1 of `tracks/core/interfaces/id_solver.md`
section 8 (row T1), mode `code`, ng = 4: a Gaussian with K = 0 solved on the mesh against
the format-1 psi of nrpic_cf, which solves the continuum Hamiltonian constraint with the
matter term 2 pi psi^5 E. The relative error at the centre falls as -1.92e-2, -5.22e-3,
-1.33e-3 at dx = 1, 0.5, 0.25 (second order, 0.82 to 0.91 of the error predicted from
the cloud and stencil moments; measure as restated after the fresh verifier, run
core-20261121-214108-0960a46). A factor of the matter term wrong by any finite amount
would leave an error of order one that does not fall with dx [JUDGEMENT on the logic; the
numbers are those of the T1 row]. Please mark M18 verified by T1 (mode code), not by the
monitor after the solve.

The other items of that answer stand (M23 -> NrpicWriteHistory, `nco` dead and kept for
checksums, M25 and M20 the dust-collapse runs, M19 claimed without an isolated test, M24
Track A's periodic_diag runs). No reply needed.
