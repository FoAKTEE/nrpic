# What G2 of A-emd-pbh still lacks (lead of batch 11, 2026-11-24)

G2 is not met and the package is not ready for review. Checklist: 9 PASS, 10 OPEN, 1 FAIL.

1. **Constraints behave (C3, FAIL).** The constraint norms of the expanding ball do not converge
   before t ~ 6 in mesh spacing (K refuted) or in particle number (K2 refuted); the momentum
   constraint of the t = 0 data grows with the mesh. Next: the same member with smoothed edges of
   the top hat on two meshes (prep_bh.py --edge-w), which can refute the candidate (density jumps).
   Also a ruling of orch on the 0.1 bound of SCOPE section 3 (requests).
2. **Code paths of section 10 (C1).** Szekeres not run (round 1 cut); the periodic LTB case P0L
   forms no horizon in the finder (the slice traps at r ~ 0.075, under four finest cells): six-level
   rerun queued (peak_leak6, queue_b11 line 1).
3. **Threshold on mesh C.** C-d0.42 continuing (Slurm 5150); C-d0.40 needs its nestC lattice and a
   chain (queue_b11 line 2, T7). Mesh A at threshold stops at the guard 2.3 M after detection
   (cause not named; processor test G1-G3 running).
4. **Package items.** Verification-ladder schematic (C10), slice mosaic (C13), schematics on
   v0.6 (C16), working-note G2 sections (C17), a fresh-context verifier of conv_ball and
   threshold_ball numbers (C18), VERIFY list and threshold_ball/README.md (C6).
