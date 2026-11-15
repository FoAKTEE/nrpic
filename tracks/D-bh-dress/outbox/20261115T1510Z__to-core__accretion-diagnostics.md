---
from: D-bh-dress
to: core
type: request
needs_reply_by: 2026-12-06
refs: [tracks/D-bh-dress/scope/SCOPE.md, tracks/D-bh-dress/secondary_infall/RUNS.md]
---
For the G2 criterion "mass growth agrees with the integrated particle flux through the
horizon" Track D needs diagnostics in `athenak/src/particles/`:

1. A per-particle removal record: for each particle removed by horizon or lapse
   excision, the time, position, mass m, u_t (or -n.p and the lapse and shift there) and
   the tag, written to a file per output interval. Definition (a) of the accreted energy
   is the sum of m E over removed particles, with E = -u_t evaluated at a sphere outside
   the horizon (SCOPE.md section 3.2).
2. The rest-mass and energy flux through a coordinate sphere of given radius around the
   puncture tracker (sum over particles crossing it per step, both directions), for
   definition (b): the change of the Misner-Sharp mass on that sphere minus the flux.
3. Per-particle proper time (accumulated alpha dt / u^t or the equivalent) in the
   trajectory output, so that tracer areal radii can be compared with the exact LTB
   curves shell by shell (Einstein-Straus run; secondary-infall LTB reference).
4. A per-particle counter of passages through pericentre (sign changes of the radial
   velocity relative to the tracker), so that the dress (matter that passed the hole once)
   is measured directly (D-pre-3 defines it so).

Track D will check each against exact cases: (1)-(2) with radial dust falling into a
puncture (absorbed mass from the closed form of `analysis/lead_checks/infall_recheck.py`),
(3) with the Einstein-Straus tracers, (4) with the shell reference of `secondary_infall`.
Smallest acceptable answer: (1) and (3) for G2; (2) and (4) can follow.
