# What G2 of A-emd-pbh still lacks (lead of batch 17, 2026-11-25)

G2 is not met and the package is not ready for review. Checklist: 9 PASS, 10 OPEN, 1 FAIL (C3).
Each item with what it lacks and the queue entry that serves it (`harness/bin/nrpic-queue list
--owner A-emd-pbh`).

| item | lacks | queue entry / next step |
|---|---|---|
| C1 code paths of section 10 | (iii) Szekeres card series; (ii) the periodic LTB case P0L forms no horizon in the finder (slice traps at r ~ 0.075, under four finest cells); (iv) A's oblate/prolate row (SCOPE A2) has no run | (iii) q0040 a-szk-n64-128 and q0041 a-szk-n256 (added batch 17, p2; predictions P17-P21, szekeres entries 8, 10); (ii) q0013 a-p0l6 (in Slurm, job 5282, run A-20261125-044641-7d5bd16; predictions D1-D5); (iv) none: ask orch whether core's prolate test covers the row or A must run A2 (outbox) |
| C3 constraints behave | FAIL: norms flat in mesh and particle number before t ~ 6 (K, K2 refuted), not localized (K3 refuted); ratio to 16 pi E above 0.1 on every member including M/64 (1.94, C-d0.42) | processor test K4 (threshold_ball entry 10; command at its end; no card); ruling of orch on the 0.1 bound (asked 2026-11-24, outbox constraint-bound-ruling) |
| C5 verification report | waits for C1, C3, C18 | none |
| C6 reproducibility package | a single rerun list for G2; threshold_ball/README.md | session work, no card |
| C10 ladder schematic | not drawn | session work (paperfig) |
| C11 convergence figures | not drawn into the note in zoom-figure style (gauge leg not run: boundary leg chosen) | session work |
| C13 slice mosaic | nested runs write line outputs only; needs 3D outputs of one member | a short card run with mesh dumps (not queued: decide with C17) |
| C14 package documents | interim package | after C1, C3 |
| C16 schematics on v0.7 | note schematics name core-v0.3 | session work |
| C17 note G2 sections | none written | session work |
| C18 fresh-context verifier | conv_ball and threshold_ball numbers not recomputed by a second agent | helper session (orch to schedule) |

Also from SCOPE section 7 (G2, not a checklist item): "one triaxial particle run of phase 1 to horizon
formation with the constraint bound of section 3": S1L (e = 0.2) is that run; q0015 a-s1l-cont (p5)
continues it from t = 198.7 of 220 (predictions S1-S3, periodic_threshold JOURNAL 2026-11-21 13:20Z).

Removed in batch 17: q0014 a-cd040 (C-d0.40 on mesh C, 14 card-hours): no G2 item waits for the lower
end of the mesh-C bracket (threshold_ball JOURNAL, note after entry 11). Mesh-C upper end holds
(C-d0.42 black hole, tau_det 43.705; A-20261125-115027-17b419e).

Mesh A at threshold stops at the guard 2.3 M after detection (cause not named; G1 repeats the card
stop exactly, G2 moves it, G3 not judged: run A-20261124-132016-ecf12c3 still not closed). Not a
checklist item; on record under C19.
