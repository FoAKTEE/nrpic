# What G1 of A-emd-pbh still lacks (rewritten by the g1close helper, wave 3, 2026-11-20)

The two items G1 lacked after wave 2 are closed: the data-flow schematic (C11) is drawn and
is Fig. 7 of the note, and a fresh verifier recomputed the note's ledger, `newton/` and the
criteria checks (C18, `VERIFIER.md`); its corrections are applied or rebutted with evidence
(`../../g1close/JOURNAL.md`, `README.md` section "Close-out, wave 3"). What remains, item by
item, with the smallest action that closes each:

1. **C20 (FAIL): the owner's STATUS.md, JOURNAL.md, HANDOFF.md are not current.** Last
   changed on 2026-11-15; they still give G0 as not passed, C11 and C18 as open, and the
   sentence the verifier corrected ("14 scan points within 6.3e-4", STATUS.md line 13).
   Action: the lead rewrites them at the end of wave 3 round 1 (helpers do not write them);
   the sentences to change are listed in `../../g1close/README.md`, "Requests".
2. **C18 (PASS by judgement; the gate reviewer decides): numbers of the note no fresh
   verifier recomputed.** The predicted card-hours of the two scouting runs (a cost model),
   the four cross-check differences of Table II (read from their output, checksum verified),
   and five rows that note v1 added to Table IV from the wave-2 analyses
   A-emd-pbh-20261115-163659-4dbacd0 and A-20261115-182657-53da696 (tracked-particle
   residuals, constraint norm at t = 20, two central-lapse rows, compactness on the axes).
   The note names them in App. B. Action, if the reviewer reads "every number" strictly: a
   fresh verifier recomputes these five rows from the raw outputs (processor only, about an
   hour).
3. **Wave-1 outputs: checksums recorded late.** Run A-20261120-222620-0304d9d lists the
   sha256 of the 55 files without a record of their own and the note checks its inputs
   against it, so any later change is detected; that the files are the ones the wave-1 runs
   wrote rests on the verifier's independent reconstruction of data set 2t and of the
   criteria (VERIFIER.md finding 7). Action before G2, optional: rerun the wave-1 producers
   through `nrpic-run` (seconds to minutes each; verifier weak point 3).
4. **Handled by other helpers this round, not by this package:** the SR-2 turnaround
   estimator and the re-judgement of runs_ball prediction R2 (VERIFIER.md finding 6, weak
   point 1, section 4 item 1) by the runs_ball helper; an order of the core error at a fixed
   box (weak point 2) by the conv_ball series; `docs/FORMATS.md` line 122 (`.trajmet.bin`
   records of 17 values, not 12) is core's.
5. **For G2, not gate items of G1:** AthenaK's own t = 0 constraint norms of the format-2
   tables (the cstat files of SR-1/SR-2 hold them: H_max 4.7e-4 at dx = M/2, t = 0, run
   A-emd-pbh-20261115-153845-7172b66); the cause of the energy drift of the Newtonian mode
   during sub-cell crossings (1.1e-3 to 9.3e-3, spindle 3.0e-2; analysis
   A-emd-pbh-20261115-164420-4528861).

## Automated checks (`nrpic-stage verify`) that do not pass

(filled from `VERIFY_RESULTS.md` of the run below)
