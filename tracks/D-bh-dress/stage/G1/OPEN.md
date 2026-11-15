# What the G1 package of D-bh-dress still lacks

Against `CHECKLIST.md` (items OPEN) and `STATUS.md`.

1. C2: the Einstein-Straus analysis pipeline on AthenaK output. ES-1
   (D-20261115-172726-60ba4c2) and V-1 (D-20261115-172730-c6d151b) are running on the cards;
   then `tracks/D-bh-dress/es_runs/tools/finish.sh`, every figure looked at, the outcome
   against predictions 1-4 and A1-A6 in `es_runs/JOURNAL.md` entry 2.
2. C7: the D-pre-3 profile criterion. As written ("reproduce the r^-9/4 profile", SCOPE:
   "slope -9/4 +- 0.05 on [2 dx, r_ta/2]") it fails for an exact code (verifier C4); the
   proposal to judge against the self-similar m(lambda) and the matched shells is with orch
   (outbox). If the wording stays, the long Newtonian-mode run to a/a_i = 30-100 (refined
   mesh, point mass of core/requests-adf) is needed.
3. C9: the architecture schematic redrawn with core's dfix executables (tracer rule,
   accretion diagnostics, analytic excision, Newtonian point mass exist on
   `scratch/core/exe/core_requests-adf/`).
4. C17: a fresh-context verifier of the wave-2 baselines (Kerr reference and stationarity,
   Newtonian-mode masses, ES-1/V-1 analysis), in particular the Hernquist action matching at
   L_z != 0 (4 per cent below FdRW at the a = 0.8 peak) and the 1-4 per cent inner-range
   offsets of the Kerr run.
5. Not required for G1 but open: ES-1G (core's lapse executable not published); boundary
   control of D-pre-4 (R4); the G2 cost with the measured MeshBlock counts (verifier C8).
