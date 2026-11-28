# G1 of F-hills: what the gate still lacks (2026-11-27, lead, batch 35)

The independent gate review (`GATE_REVIEW.md`, batch 34a) recommends PASS WITH RESERVATIONS.
Decision 0048 item 2 leaves two things before the tag: (a) the passage continued to t = 200 M,
(b) the corrections of the verifier's part 2. (b) is done in batch 35 (item 2 below). (a) is
queued (item 1). When a registered reading shows the record to 200 M with its health checks,
the gate is signed without a further review (0048 item 2). The lead does not pass the gate.

1. **Trackers to t = 200 M (scope criterion (iv); 0048 item 2(a)): QUEUED, not yet met.** The
   record ends at 186.0 M because Slurm refused the chain's next submission (I/O error,
   `chain/slurm-5492.out`). Queue entry **q0091** (label F-A2-to200, priority 2) continues A2
   (F-20261124-210400-902c650) in place from `rst/hills.00166.rst` with the same executable, deck
   and `<fastflow> diagnostics = true` (`binary_conv/scripts/continue_chain.sh --reopen ... 31
   --extra-input binary_conv/inputs/fastflow_diag.athinput`; dry run passed). Predictions D35-1..9
   (JOURNAL batch 35, commit 72543633f, before queuing): 3 counted segments, 2.4-3.2 card-hours
   (decision 0048 says "about one card-hour"; at 5.2-5.3 M per 50-min segment 14 M need about 2.7),
   m2 at 20.5-21.5 M from M at 200 M, the remnant's Christodoulou mass 1.1220-1.1235 and S/M^2
   0.2520-0.2540 with hrms 1e-4 to 1e-3. To do when it has run: `sacct` shows every job COMPLETED
   (or cut by a signal and resubmitted); `harness/bin/nrpic-run finish F-20261124-210400-902c650`
   (closes it again from the chain's STATUS); registered readings with
   `stage/review_wave3/b21_a2_state.py` (S1-S3 record and health, S6, S7 end state) and
   `b34_horizons.py` (status files to 200 M); D35-1..9 judged in JOURNAL; C8 and EVIDENCE.md
   updated; one line to the orchestrator with the run ids.
2. **The verifier's part-2 corrections (0048 item 2(b)): APPLIED in batch 35.** Answered one by
   one in `../REVIEW-wave3.md` (batch 35) and written into CHECKLIST C8 and C18, `STATUS.md` T4
   and EVIDENCE.md: 186.0 M against the criterion's 200 M (and the continuation); F1 decided for
   86.6-131 M by the summary's hrms (upper branch 1.00422 converged; the decline and the lower
   branches unconverged), open only during m1's approach; m2's mass range split into the
   converged searches (0.12939-0.12964) and the unconverged branch of 160.6-179.2 M (hrms
   0.15-0.23); "1.55e-3 by 133 M" restated (on the converged branch the heavy hole changes by
   6.4e-5 from 86.6 to 131 M; 1.00444 at 133 M and 1.00531 at 135 M during m1's approach); the
   source of MeshBlocks 2584 (run A, not A2; A2: 1968-2514); horizon numbers quoted with hrms;
   the capture's wave recorded at 40 M only, with no ring-down; the A2-A2 overlap of 1.25e-9 M
   at 104 M. Reader corrected and rerun: F-20261128-020208-d7c6f1c (figure title from the
   chain's state, no longer PARTIAL).
3. **Failed predictions on record (not blocking; C19).** A2-1 (timing), A2-2, A2-3, A2-4,
   A2-5's heavy-hole clause, H2 in part, H4, C25-1's tracker clause, C25-3's rate clause, D34-1,
   D34-2 in part (JOURNAL batches 21, 25, 34; VERIFIER.md sections 4 and 14 for the verifiers').
4. **Reservations carried to G2 (GATE_REVIEW section 6; 0048 item 2).** One resolution only for
   an outcome that reverses the Newtonian fates (C2 at m/12 stopped at 106.69 M; continue past
   145 M); 'found' is not converged (quote hrms; polished searches with core-v0.8 on A2's restart
   files between 87 and 133 M as the independent test of F1); m2's fate undecided in coordinates;
   criterion (iii)'s junk at its edge (19.8 percent), measured with P1's m/8 binary, not at P1b's
   spheres; parts no verifier checked (Kerr part of F-pre-2, EIH, ledger tables 3-5 except the
   rows named in C18, P1's remnant spin and radiated energy, S2g's junk scaling); a `--full`
   checksum pass over the gate's runs is not on record; the first clump passage (decision 0013)
   is due.
5. **Note.** v2.1 (batch 35): the schematics redrawn to core-v0.8 (F-20261128-020409-a3edb04;
   numbers and ledger equal to v2's) and the m/16 passage no longer called "queued". Note v3
   (the passage section with its figure and ledger rows, horizon numbers with hrms, the two
   reverse fates, the junk at P1b's spheres) is written after the 200-M reading, so that it is
   written once with the final record.
6. **Small defects listed, not fixed.** `three_punctures/scripts/newton_start.py` reads the
   pre-fix energy fields; `nr_first/scripts/single_analysis.py` repeats the last mass after a
   run's end; binary_conv's README "Results" rows for A2 (186 M) and B2 out of date;
   geodesic_binary S4 (chart 'cks') carries the slicing pump; `nrread.read_table` skips status
   rows (use `b34_horizons.status()` or `b21_a2_state.status_rows()`); b11_passage's energies
   of m1 after the merger are meaningless and its M is the pre-merger mass; `note/main.pdf` is
   1.37 MB (above the 1-MB guideline, as v2 was).
