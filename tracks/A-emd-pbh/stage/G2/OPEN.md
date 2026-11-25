# What G2 of A-emd-pbh still lacks (lead of batch 20, 2026-11-25)

G2 is not met and the package is not ready for review. Checklist: 9 PASS, 10 OPEN, 1 FAIL (C3).
Each item with what it lacks and the queue entry or session that serves it (`harness/bin/nrpic-queue
list --owner A-emd-pbh`).

| item | lacks | queue entry / next step |
|---|---|---|
| C1 code paths of section 10 | (ii) P0L6: the finder must hold the periodic LTB horizon; (iii) the Szekeres card series; (iv) A2 analysis of S1L's snapshots | (ii) q0013 a-p0l6: chain A-20261125-044641-7d5bd16 at t = 138 of 140, segment 7 resubmitted as Slurm 5296 (pending); first status-file find at t = 118.1 (read with predictions D1-D5); (iii) q0040 a-szk-n64-128, q0041 a-szk-n256 (waiting, p2; P17-P21); (iv) A2 run and FAILED: S1L's first crossing (z, as predicted) at 6.1-6.4 t_H against the band [3.4, 5.0] (A-20261125-151715-66f198f); next: Newtonian-mode control of the same particles on processors to tell a relativistic lag from the initial velocities; no oblate card member (the snapshots bracket the crossing) |
| C3 constraints behave | FAIL as written for every member run so far (bound 0.1 kept, 0039 item 2(c)). Batch 20 (threshold_ball entry 13): the floor at t = 0 is the top hat's jumps (momentum constraint: S2's falls 60-fold A to B) PLUS the PCS deposit at the refinement boundaries (Hamiltonian: smooth S2 keeps 0.134 / 0.116 on A / B with PCS, 0.0064 / 5.8e-4 with CIC; A-20261125-160849-8c01b54, -161039-cb046d7, -161248-eecc672) | F2: S2 with CIC evolved (A to t = 5, B to t = 1; run A-20261125-161154-62ce3dc on processors, detached) and its PCS twin S2-A (A-20261125-160633-594a474): read with edge_compare.py by the next session. Then the review decides whether G2 is judged on smooth members with the CIC cloud (a deposit choice, not a moved bound) or with the failure on record |
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
