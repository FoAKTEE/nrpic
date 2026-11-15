# What the G0 package of E-stoch-inf still lacks (2026-11-15)

1. **The group's decision** (track-specific G0 criterion, brief 798): continue, shrink or
   downgrade. Asked in `../../outbox/20261115T1410Z__to-orch__g0-decision-requested.md`;
   the owner's recommendation is in `../../spec/scope/SCOPE.md` section 9.
2. **Working note v0** (REVTeX under `tracks/E-stoch-inf/note/`, written with
   /paper-writing; checklist C5, C15): not started. Its content exists as Markdown
   (`spec/SPEC.md`, `spec/scope/SCOPE.md`, `codebase/DESIGN_REVIEW.md`,
   `noise/NOISE_SPEC.md`, `langevin/README.md`).
3. **Architecture schematic and stage-timeline schematic** (C6, C9, C10, C14;
   /sleep-paper-figure-style): not drawn. The timeline exists as a table (SCOPE.md
   section 10); the architecture (exists / to be ported / new) is described in SCOPE.md
   section 6 and DESIGN_REVIEW sections 2-6.
4. **Verifier report** (C16, VERIFIER_REPORT.md by a fresh-context verifier): not written.
   The lead's own independent checks are in EVIDENCE.md section 2; brief 13.3 asks for a
   separate verifier.
5. **Automated stage check**: `harness/bin/nrpic-stage verify E-stoch-inf G0` has not been
   run (the note and the `note/scripts/fig_*.py` it re-runs do not exist yet; the data
   figures of this package are made by scripts in the packages' `ref/`, `scripts/` and
   `analysis/lead/`, not under `note/scripts/`).
6. **Statements of the key references in the knowledge base** (C2): verified at the raw
   sources with file:line locators (SCOPE.md section 3); the errata are not yet recorded
   as knowledge-base claims (`../../outbox/20261115T1410Z__to-kb__errata-s11-references.md`).
7. **Measured card cost**: the compute estimate rests on the Z4c throughput of
   `docs/TESTLOG.md:46` plus an assumed 15 percent and an assumed synthesis rate; no card
   build of `core/scalar-field` exists yet (outbox request on the card build). The
   downgrade threshold (5 card-hours per 256^3 realisation) is 10 times above the estimate,
   so the recommendation does not hinge on it.
8. **Parts of the helpers' work the lead did not re-check independently**: the
   end-of-inflation delta-N statistics after USR, the unvalidated importance sampling of
   the phase-space solver, the extraction factors E6 and the unit mapping of SPEC 2.5 (hand
   derivations), the assumed overheads of the cost model (EVIDENCE.md section 2).
9. **Pending runs** (none waits in a queue; all need a card build or a longer processor
   slot): noise unit test U9 on a card and the 64^3 x 300 base case; the Markov-tanh A1
   rerun after core's cancellation-free window increment.
