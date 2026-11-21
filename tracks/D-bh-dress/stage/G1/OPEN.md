# What the G1 package of D-bh-dress still lacks

State after the lead session of batch 4a (2026-11-21). Against `CHECKLIST.md` and `STATUS.md`.
Verdict of the lead: every G1 item PASS; the package is complete for the orchestrator's
independent review under decision 0016 item 4 (the lead does not pass the gate). Closed in this
session: C7 (D-pre-3 under decision 0021 item 2; Q16 and the lead's checks Y2, Y5 in
`../REVIEW-wave3.md` section 9.2) and C16 (working note v1, section 9.3).

Nothing required for G1 is open. Recorded for the reviewer and for G2:

1. The automated verify (`VERIFY_RESULTS.md`) fails "clean" while the package `drift_controls`
   (cut on 2026-11-20, still in progress) has three untracked tools in the worktree
   (`drift_controls/tools/compare_runs.py`, `count_blocks.py`, `slice_profiles.py`); they are not
   G1 evidence and are left to their package. See `VERIFY_RESULTS.md` for the rest.
2. Not confirmed by a second agent (recorded, not required): the Hernquist curve on the Kerr axis;
   eight ledger rows of the note (box mid-transition orders, cost model, wall radius against the
   closed form, smallest detectable change (two rows), chi^2 median, SFW Fig. 1 read-off,
   loss-cone probes, self-similar lambda^(9/4), passed and captured fractions, radiation era); a
   second sampler seed for the Kerr inner-range deficits (V4).
3. D-pre-3 beyond G1: the approach to the self-similar solution on lambda = 0.01-0.06 needs a clean
   run to a/a_i ~ 30 (initial ball resolved by about nine cells: nx ~ 450-500 or a refined centre);
   Q16 has one resolution; no run used the fixed point mass `newton_pm_mass` (core measured it in
   its own run: M_ta within 0.7 per cent of the closed form).
4. G2 material that changed the plan: the late horizon growth under lapse_leak is not the outer
   boundary (ES-1GB, D-20261121-125900-ea4c442) and appears in vacuum too (V-1GB,
   D-20261121-125909-06f856e); decision 0022 item 3 moves the null test to 1+log or to core's
   corrected option. The vacuum floor with 1+log and the faces at +-384 M is 4.8e-5 over 100-200 M
   at M/8 (V-1B).
5. Wording of the program: the brief's "reproduce the r^(-9/4) profile" (errata row 1.7 of
   `coord/BRIEF_ERRATA.md`); `coord/REQUESTS.md` still lists `d-pre-3-criterion` as open although
   decision 0021 item 2 ruled on it (asked to close, outbox of this session).
