# What the G1 package of D-bh-dress still lacks

State after the lead session of wave 2b (2026-11-19). Against `CHECKLIST.md` (items OPEN)
and `STATUS.md`. Verdict of the lead: G1 NOT MET; the package is not complete for the
orchestrator's review under decision 0016 item 4 (no verifier of the G1 material).

1. C17: a fresh-context verifier of the G1 material (decision 0016 item 4): the wave-2
   baselines (Kerr reference and AthenaK stationarity, Newtonian-mode masses and profile) and
   the ES-1/V-1 outcome, recomputed from the manifests without the helpers' or leads'
   conclusions; in particular the Hernquist action matching at L_z != 0 (4 per cent below
   FdRW at the a = 0.8 peak) and the 1-4 per cent inner-range offsets of the Kerr run.
   Requested from orch (outbox 2026-11-19).
2. C7: the D-pre-3 profile criterion. As written ("reproduce the r^-9/4 profile"; SCOPE:
   "slope -9/4 +- 0.05 on [2 dx, r_ta/2]") an exact code fails it (verifier C4). The
   proposal `d-pre-3-criterion` (2026-11-15) is open at orch (`coord/REQUESTS.md`). If the
   wording stays, the Newtonian-mode run to a/a_i = 30-100 on a refined mesh with core's
   point mass is needed (two to four card-hours [JUDGEMENT]).
3. C9: the architecture schematic redrawn with core's wave-2 executables (tracer rule,
   accretion diagnostics, analytic excision, Newtonian point mass on core/requests-adf;
   lapse_leak on core/gauge) and the ES-1/V-1/ES-1G chain.
4. Not required for G1 but open and recorded: ES-1G (D-20261119-142633-6f72922, queued);
   the cause of the late common horizon drift of ES-1 and V-1 after t ~ 165 M; the
   null-test floor in the ES set-up; the boundary control of D-pre-4 (R4); the G2 cost with
   the measured MeshBlock counts (verifier C8).
