# STATUS of F-hills

gate:        G0 signed (coord/GATES.md, 2026-11-20). G1: independent review recommends PASS WITH
             RESERVATIONS (stage/G1/GATE_REVIEW.md). Decision 0048 item 2: (a) the passage to
             t = 200 M with a registered reading: DONE in batch 41; (b) the verifier's part-2
             corrections: DONE in batch 35. Signed on the line to orch (outbox g1-passage-200m)
             and the full checksum pass, which is RUNNING (log below). Not passed by the lead.
headline:    The m/16 Hills passage P1b (A + A2) is recorded to 200.0 M: the binary is disrupted
             between 120 and 133 M, m1 is captured by the heavy hole (common horizon from 137.5 M;
             at 200 M area mass 1.1137, Christodoulou 1.12283, S/M^2 0.2528, summary hrms 3.8e-4,
             unconverged in F5's sense), m2 keeps its horizon (0.12963, hrms 1.5e-6) and recedes
             (21.07 M from M at 200 M, monotonic), fate undecided in coordinates. Newton from the
             same deck ejects m1 and binds m2.
last-result: - q0091 DONE at 200.0 M (job 5676 COMPLETED; 5570-5664 preempted, resubmitted;
               2.69 card-hours); A2 F-20261124-210400-902c650 closed (nrpic-run finish)
             - readers F-20261128-160721-f0e18c8 (b21_a2_state), F-20261128-160749-2ba694f
               (b34_horizons), three figures read: trackers joined 0-199.998 M (step 2^-9 M,
               overlaps <= 1.25e-9 M); rms H <= 1.80e-5 over 186-200 M; MeshBlocks 2206-2318;
               card peak 78789 MiB; finder 0 never found after 186 M
             - D35-2..9 met; D35-1 FAILED in one clause (1 counted segment, not 3)
             - status column 10 ("mean_expansion") is the surface INTEGRAL of H (core, outbox
               20261128T021500Z); batch-41 texts corrected, older texts not yet
             - stage G1: collect (20 kept), C8 met with the 200-M clause, verify (cache) PASS
               0 failed, report regenerated with a lead's note
decision:    none new; note v3 written once from the record to 200 M (next session)
card jobs:   none of this owner queued or running. Full checksum pass (processors, detached):
             `nrpic-stage verify F-hills G1 --full`, pid 1346011, started 08:06 PST 2026-11-28 on
             commit f0e18c850; log scratch/F-hills/tmp/stage-verify-full-G1-20261128-080654.log;
             it rewrites stage/G1/VERIFY_RESULTS.{json,md} when it ends (commit them then).
next:        1. read the full pass's log and VERIFY_RESULTS; commit them; one line to orch
             2. note v3: the passage to 200 M (figure, ledger rows, hrms and the integral of H
                beside each horizon number; the reverse fates; the junk at P1b's spheres)
             3. G2: C2's continuation past 145 M (m/12), F1's polished-search test on A2's restart
                files (v0.5 restart under v0.8/v0.9 untested: core's one-cycle check first), the
                first clump passage (decision 0013), trapped_tol on new runs
readers:     stage/review_wave3/b21_a2_state.py (S1-S3 record, S6 health, S7 end state),
             b34_horizons.py (status files; rows end with "# words")
blockers:    none for G1; the shared queue (R27) for G2
needs:       orch: the signature of G1 (0048 item 2) once the full pass ends; the retention of
             the passage's restart files (sizes in HANDOFF.md; nothing deleted)
offers:      continue_chain.sh --reopen, nrread.py, b21_a2_state.py, b11_passage.py, b34_horizons.py
budget:      G1 49.89 card-hours before q0091 + 2.69 for q0091 = 52.58 of 60. This session 0
             card-hours (two processor reader runs, one core each; the full pass on one core)
