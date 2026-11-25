# What G2 of A-emd-pbh still lacks (lead of batch 19, 2026-11-25)

G2 is not met and the package is not ready for review. Checklist: 9 PASS, 10 OPEN, 1 FAIL (C3).
Each item with what it lacks and the queue entry or session that serves it (`harness/bin/nrpic-queue
list --owner A-emd-pbh`).

| item | lacks | queue entry / next step |
|---|---|---|
| C1 code paths of section 10 | (ii) P0L6: the finder must hold the periodic LTB horizon; (iii) the Szekeres card series; (iv) A2 analysis of S1L's snapshots | (ii) q0013 a-p0l6: chain A-20261125-044641-7d5bd16 at t = 138 of 140, segment 7 resubmitted as Slurm 5296 (pending); first status-file find at t = 118.1 (read with predictions D1-D5); (iii) q0040 a-szk-n64-128, q0041 a-szk-n256 (waiting, p2; P17-P21); (iv) no card: A2 prediction in periodic_threshold JOURNAL 2026-11-25 07:15 PST, analysis of A-20261123-025907-97bab8d's 20 snapshots on processors; if the snapshots cannot bracket the first crossing within [3.4, 5.0] t_H, one oblate member (<= 6 card-hours, p2) |
| C3 constraints behave | FAIL as written (bound 0.1 kept, decision 0039 item 2(c)). K4 shows the floor independent of step and source timing (A-20261125-150851-5545f8e) | the smoothed-edge test (data set 3 with prep_bh.py --edge-w, meshes A and B, processors, t <= 5; prediction first): not run. If smoothed members meet 0.1 and converge, G2 is judged on them; otherwise the review decides with the failure on record |
| C5 verification report | waits for C1, C3, C18 | none |
| C6 reproducibility package | a single rerun list for G2 (stage/G2/VERIFY) | session work, no card |
| C10 ladder schematic | not drawn | session work (paperfig) |
| C11 convergence figures | not in the note in zoom-figure style (boundary leg chosen, no gauge leg) | session work |
| C13 slice mosaic | nested runs write line outputs only | a short card run with mesh dumps (not queued; decide with C17) |
| C14 package documents | interim package | after C1, C3 |
| C16 schematics on v0.7 | note schematics name core-v0.3 | session work |
| C17 note G2 sections | none written (decision 0039 item 9: in the lead sessions that judge the remaining runs) | session work |
| C18 fresh-context verifier | conv_ball and threshold_ball verified (VERIFIER-C18.md) and every finding answered (A-20261125-151126-7f79a83, threshold_ball entry 12); A-R1.35's ddet and the turnaround columns unchecked; no verifier yet for S1L/A2, Szekeres, P0L6, the smoothed edge and the note | a second verifier pass once C1 and C17 have their numbers |

Corrections of batch 19 (decision 0040 items 2-3): mass medians of B-d0.42, B-d0.40, B-d0.35, C-d0.42 and
both A members withdrawn and replaced by the bracket the tracked particles allow; ddet orders of conv_ball
stated with their interpolation spread (1.2-1.5, 1.75-2.1); the threshold's time measure named (proper time
of the core edge = synchronous time of the exact solution). Failed criteria stay failed: C3, T4 (both halves:
the mass half is not decidable, the time half fails under every interpolation), T5.

Also from SCOPE section 7 (G2, not a checklist item): "one triaxial particle run of phase 1 to horizon
formation with the constraint bound of section 3": S1L (e = 0.2) is that run; q0015 a-s1l-cont (p5,
waiting) continues it from t = 198.7 of 220 (predictions S1-S3, periodic_threshold JOURNAL 2026-11-21 13:20Z).
It is not needed for A2.

Mesh A at threshold stops at the guard 2.3 M after detection (A-20261125-120158-b76bfe3); not a checklist
item; on record under C19.
