# Evidence of G2 of A-emd-pbh (interim; lead of batch 11, 2026-11-24, rows added to batch 23)

Interim package: G2 is NOT complete (OPEN.md). Run manifests: `../../runs/<run id>/manifest.json`;
outputs under `/data/haiyangw/nrpic/scratch/A-emd-pbh/<run id>/`. Predictions and outcomes:
the package journals named in each row.

| Criterion | Main runs | Analysis (registered) | Journal |
|---|---|---|---|
| Convergence of horizon formation in mesh, particle number, ball radius, boundary (C2, C7) | conv_ball card jobs A-20261121-075926-d10c2c1, -083336-6a82131, -091934-ac62f5f, -110017-471b0ae; C-R1.25 A-20261122-141100-f00cfc2 | A-20261121-120257-a2eb839 (convergence.md, fig_convergence.png); C-R1.25 in A-20261124-131120-5c974ce | conv_ball/JOURNAL.md 4-12; threshold_ball entry 4 (T5) |
| Horizon-mass error against the source's OS test (C8) | as above | A-20261121-120257-a2eb839; threshold scan A-20261124-131120-5c974ce | conv_ball/README.md; threshold_ball entry 4 |
| Horizon formation across amplitude, finite-duration threshold (C1, C7) | queue lines 3-12: A-20261121-204149-c48bd33, -204250-0bf45c7, -235851-d2200d7 (failed), A-20261122-003952-552f805, -051554-7662f22, -054155-4b3d92e, -100756-829dcf9, -101357-9a73701, -132959-dfba903, -141100-f00cfc2 | A-20261124-131120-5c974ce (threshold.md, threshold.json, fig_threshold_outcome.png, fig_threshold_slice_or_finder.png) | threshold_ball entries 1, 4 |
| Constraint norms (C3, C12) | conv_ball A, B, C, A-N8, A-N64, B-N8; threshold B-d0.42, B-d0.40, A-d0.42 | A-20261124-132249-2e6b5f2 (K), A-20261124-132342-d5dc06e (K2; fig_constraint_conv.png) | threshold_ball entries 6, 7 |
| Periodic box: Gamma-driver remedy on the refined mesh; P0L against exact LTB (C1, C9) | A-20261122-235305-4ea0aa5 (P0L), A-20261123-025907-97bab8d (S1L, continuing) | A-20261124-130507-10510ac (job2_q), A-20261124-130142-9a2d6a2 (compare_ltb), A-20261124-131430-d1a2ee6 (line_trapped, F1), A-20261124-131232-e7b58f8 (finder restarts, F2) | periodic_threshold/JOURNAL.md 2026-11-21 13:20Z, 23:15Z; 2026-11-24 13:00Z-13:40Z |
| A-mesh guard stop (C19) | A-20261121-235851-d2200d7 | processor restarts A-20261124-132016-ecf12c3 (G1-G3) | threshold_ball entry 5 |
| Constraints: the smoothed-edge test (C3; 0040 item 6) | data A-20261125-160436-462452d (failed attempts A-20261125-160221-b68396f, -160306-280d150 on record); slices and PCS twin A-20261125-160633-594a474 (S1-A, S2-B stopped by hand); test D A-20261125-161039-cb046d7; CIC members A-20261125-161154-62ce3dc (running) | A-20261125-160849-8c01b54 (t = 0, fig_edge.png), A-20261125-161248-eecc672 (F1, fig_edge.png), fig_edge_d.png in -161039-cb046d7 | threshold_ball entry 13 |
| Oblate collapse against Zel'dovich (A2, C1 iv): Newtonian control | A-20261125-160633-e38d321 (N-z done, N-f, N-z128 running) | A-20261125-162905-d0ef1d7 (fig_a2_crossing.png), A-20261125-162951-bb0fb26 (fig_a2_compare.png) | periodic_threshold/JOURNAL.md 2026-11-25 08:10 PST |
| C3 mesh leg (threshold_ball entry 14) | S2c-A, S2c-B A-20261125-161154-62ce3dc (closed); PCS twin A-20261125-160633-594a474 (closed failed) | A-20261126-022624-c663e0f (fig_edge.png) | threshold_ball/JOURNAL.md entry 14 |
| A2: shift-invariant crossing and the dust clock (A2X); Newtonian control at 128^3 (AZ1) | S1L A-20261123-025907-97bab8d (snapshots); N-z128 in A-20261125-160633-e38d321 (closed) | A-20261126-022545-5af99fb (fig_a2x.png; earlier bound runs -022220-99b7be8, -022338-0edc27c, -022438-a08cc5f), A-20261126-022631-dafbb4f (fig_a2_compare.png) | periodic_threshold/JOURNAL.md 2026-11-25 18:21 PST |
| Periodic LTB on six levels and the finder (C1 ii; D1-D5) | P0L6 A-20261125-044641-7d5bd16 (q0013, closed, 4.87 card-hours) | A-20261126-022753-f9e9c40 (fig_job2_q.png, fig_line_trapped.png, fig_compare_ltb_P0L6.png); status file peak.horizon_status_0.txt | periodic_threshold/JOURNAL.md 2026-11-25 18:35 PST |
| Szekeres series (C1 iii; P17-P21) | N64, N128 A-20261125-213939-0ad9f29 (q0040, closed failed: guard stops); N256 A-20261125-231808-0784bc9 (q0041, closed stopped at tau 21.2) | A-20261126-023242-f3f0578 (N64/N128); A-20261126-023245-1dd80ad (N128/N256, detached); stopped attempt A-20261126-022804-0bc68c2 | szekeres/JOURNAL.md entries 11 (and 12) |

Figures looked at by the lead in batch 11 (PNG read): fig_compare_ltb_P0L.png, fig_job2_q.png,
fig_line_trapped.png, fig_threshold_outcome.png, fig_threshold_slice_or_finder.png,
fig_constraint_conv.png (two versions); conv_ball's fig_convergence.png was checked in batch 5
(REVIEW-wave3 section 6).

Figures looked at by the lead in batch 20: fig_edge.png (two versions), fig_edge_d.png, fig_a2_crossing.png (N-z), fig_a2_compare.png.

Card-hours to G2 (nrpic-run budget at the end of batch 11): see STATUS.md.

Figures looked at by the lead in batch 23: fig_edge.png (S2c-B), fig_a2x.png, fig_a2_compare.png (four curves), fig_line_trapped.png and fig_compare_ltb_P0L6.png (P0L6), the Szekeres figures of A-20261126-023242-f3f0578.
