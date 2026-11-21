# What the G1 package of D-bh-dress still lacks

State after the lead session of batch 2a (2026-11-21). Against `CHECKLIST.md` (items OPEN)
and `STATUS.md`. Verdict of the lead: G1 NOT MET; the package is not complete for the
orchestrator's review under decision 0016 item 4. Closed since 2026-11-19: C9 (architecture
schematic redrawn, run D-20261120-222429-026731f) and C17 (fresh-context verifier,
`VERIFIER.md`).

1. C7: the D-pre-3 profile criterion. As written ("reproduce the r^-9/4 profile"; SCOPE:
   "slope -9/4 +- 0.05 on [2 dx, r_ta/2]") an exact code fails it (G0 verifier C4). The
   proposal `d-pre-3-criterion` (2026-11-15) is still open at orch (`coord/REQUESTS.md`;
   asked again in outbox 2026-11-21). If the wording stays: the Newtonian-mode run to
   a/a_i = 30 of package `secondary_infall` (design D-20261120-222358-e98ffbd, timing
   0.66 s per step on six threads, matched shells to a/a_i = 30 done; about 0.4-0.8 h on
   processors; isolated box, so processors, not cards, per core's correction of 2026-11-21).
2. C16: the working note v1 (text c2e0571d, figures and ledger run D-20261120-223535-24f7f90)
   must be compiled, pass `check_manuscript.py --compile`, have every page read, and carry the
   verifier's wording corrections (dress at a/a_i = 2; profile "about 25 per cent, sensitive
   to r_ta"; Hernquist gap [JUDGEMENT] in FdRW's curve; hole mass a choice; ledger: the
   radius of "wall radius against the closed form", table residuals as upper bounds, the seeded
   self-similar model described). Package `note`, cut on 2026-11-20.
3. Recorded, not required for G1: the verifier's NOT CONFIRMED items (Hernquist on the axis;
   eight ledger rows: box mid-transition orders, cost model, wall radius against the closed
   form, smallest detectable change (two rows), chi^2 median, SFW Fig. 1 read-off, loss-cone
   probes, self-similar lambda^(9/4), passed and captured fractions, radiation era); a second
   sampler seed for the Kerr inner-range deficits (V4).
4. G2 material, recorded here because it changes the plan: the late common drift of ES-1/V-1
   after 165 M is the outer boundary in vacuum (V-1B, faces at +-384 M: |drift| <= 4.8e-5 over
   100-200 M, D-20261120-222625-63abd72; lead Z3); ES-1G's +6.96e-3 growth is in the slice and
   arrives with the exterior mass lost from the faces (es_runs K1-K2), not yet tested with the
   faces at +-384 M.
