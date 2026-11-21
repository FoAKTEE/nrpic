# OPEN items of E-stoch-inf at G2 (lead of batch 5, 2026-11-21)

Criteria: `spec/scope/SCOPE.md` section 4c (fixed before production). Runs: package `g2prod`.

1. Release production ladder (g2prod, release card build core-v0.6): timing T (Slurm 4827),
   P256v6 (4828), then via the sequencer U256ap/am, U320ap, U256bp/bm, U320am, U256hp/hm, U256nc.
   None has run yet. Each is judged against `g2prod/JOURNAL.md` entry 1 and SCOPE 4c.
2. Allotment: the last three labels need the earlier runs closed or the allotment raised (asked
   of orch, outbox 20261121T204305Z). A third resolution rung at 384^3 needs the raise.
3. C4 (first full-GR kinetic run): proposed NA for Track E before the field-to-particle hand-over;
   orch to confirm.
4. C2 (three-way convergence): particle number NA; mesh by U-R; gauge: geodesic slicing only
   (RISKS R6) - a gauge variant is not planned; to be argued in the package or ruled.
5. a4res Q6: the even parts of N64q64 and N128q64 differ by 10.9 percent at one dump (t = 0.147);
   cause not found; a 3-card-minute run with common dump times would settle it (optional).
6. window: the shift error is a bound by construction (no resolution pair per window); optional
   0.4 card-hours per window at 128^3.
7. Working note G2 sections, figures per criterion, a fresh verifier (C17, C18) after the runs.
8. Lockstep record sub-stepping (core request 20261121T131020Z): top-shell numbers carry the RK4
   phase error k^5 dt^4/600 (RISKS R21) until then.
