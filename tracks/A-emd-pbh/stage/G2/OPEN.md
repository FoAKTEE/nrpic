# What G2 of A-emd-pbh still lacks (lead of batch 23, 2026-11-25 evening)

G2 is not met and the package is not ready for the fresh verifier of the whole gate. Two kinds of open items
remain: (a) new failures on record that have no ruling yet (C1 (ii) the finder on P0L6, C1 (iii) Szekeres P17/P18,
C3 after its mesh leg), for which the track asks the orchestrator (outbox g2-state-after-batch-23); (b) session work
that needs no card (C6, C10, C11, C13, C16, C17), to be done in the lead session after the rulings, then C5, C14 and
the verifier (C18). No checklist item waits for a card run. Queue (`harness/bin/nrpic-queue list --owner A-emd-pbh`):
only q0015 a-s1l-cont (waiting; SCOPE section 7, not a checklist item).

| item | state | lacks | serves it |
|---|---|---|---|
| C1 (i) expanding ball | done | | conv_ball, threshold_ball |
| C1 (ii) LTB peak P0L6 | failure on record, no ruling | shells r0 >= 1.5 follow LTB to 1-4 per cent; D2, D3, D4 refuted: the finder accepts one false surface (t = 118.1) and stalls on a resolved horizon (16-21 cells) from t = 136 (A-20261126-022753-f9e9c40) | core's answer to outbox finder-false-accept-and-stall-p0l6; a processor rerun of the finder on P0L6's restart files with core's options (no card); orch ruling |
| C1 (iii) Szekeres | analysis in progress | N64 to tau 30.25, N128 to 37.47 (guard stops), N256 to tau 21.2 (queue entry without a segment count); P17 refuted for N128; P19-P21 from N64/N128 (this session, szekeres JOURNAL entry 11) and N128/N256 (detached analysis A-20261126-023245-1dd80ad, ~3-4 h) | next lead session reads A-20261126-023245-1dd80ad; continuing N256 to tau 40 would cost ~0.8 card-hour (not queued; asked of orch) |
| C1 (iv) A2 | FAILED as written (0040 item 7) | lag located: not coordinates (central particle at rest older than 5.99 t_H on the last uncrossed slice; A-20261126-023551-f800cf5), not Newtonian resolution (N-z128 3.62 t_H); physics or numerics of the GR evolution not named | optional half-amplitude GR member (card, prediction first) if the review wants a cause before G2 |
| C3 constraints | FAILED as written (0039 item 2(c)) | mesh leg refuted (order ~0.35 from t = 0.75; A-20261126-022624-c663e0f): a defect to be explained; the gate review decides with the failure on record | particle-number leg of S2c-A on processors (next session, prediction first); core's answer on the PCS deposit (its test runs in batch 23) |
| C5 verification report | open | the package | after C17 |
| C6 rerun list | open | stage/G2/VERIFY (commands of every G2 number) | session work |
| C10 ladder schematic | open | not drawn | session work (paperfig) |
| C11 convergence figures in the note | open | note figures in zoom style | session work |
| C13 slice mosaic | open | needs 3-D dumps: the Szekeres N = 256 field dumps (uniform 256^3) are the cheapest source | session work, no card |
| C14 package documents | open | after the above | session work |
| C16 schematics on v0.7 | open | note schematics name core-v0.3 | session work |
| C17 note G2 sections | open | decision 0039 item 9: written once the remaining runs are judged; they now are, except Szekeres N256 | session work after the rulings |
| C18 fresh verifier | open | VERIFIER-C18.md covers conv_ball and threshold_ball; nothing yet for S1L/A2, P0L6, the smoothed edge, Szekeres and the note | the verifier of the whole gate, after C17 |

Corrections of batch 19 stand (decision 0040 items 2-3). Failed criteria stay failed: C3, T4, T5, A2; new in batch 23:
G (C3 mesh leg), AZ1's second clause, D2, D3, D4, A2X's bound as written.
