# G3 of Track E: what is open (batch 34, 2026-11-27 afternoon)

G3 is not ready for its fresh verifier. Scope: spec/scope/SCOPE.md 4d with 4d.9 A1-A14. Definition of "G3 met": A13
("the statistic of 4d.1 measured on 128 mirrored pairs ..."). Reading of this batch: g3/JOURNAL.md entries 14-17;
stage/REVIEW-wave3.md part L.

Done (each with its registered run):
- Reference (A1, A9, A10 except the sigma = 0.1 bound), zeta reader cleared (Z0, Z1 variational, Z2(i), Z2(iii');
  decision 0042 item 1); table map of the reader (entry 12).
- G3-C (4d.4 + A6) PASSES (E-20261126-115943-32970f2); G3-R (4d.5 + A7) PASSES (E-20261126-120438-9d48377).
- Baseline read on 71 complete mirrored pairs (0-70) of 128: see entry 17 for (V), (T), A5 and the mirroring.

Open, in the order they close:
1. Baseline pairs 71-127 (m071 and 112 runs): the first re-queue (q0071-q0075) was preempted within seconds by another
   user's partition (entry 16); queued again as q0079-q0083 (G3B07b-G3B11b, priority 2). When they end: close, read with
   `read_pilot.py --map table --msteps 4000 --save-fields` (one registered run per card run), rerun `g3/pairs_g3.py
   --pairs 0-127` with every reading run (command in g3/README.md and entry 17). A13 asks for 128 pairs; the statement
   on 71 pairs is interim.
2. Level 2 (4d.7 + A11, reported, not judged): nothing has run yet. G3L00 (q0066) and its re-queue (q0076) were
   preempted before any member finished; G3L01 (q0077), G3L02 (q0078, with baseline pairs 126-127) wait in Slurm;
   G3L00b (q0084) queued. The kdriver records of A8 come with G3L00b.
3. sigma = 0.1 coarse-graining bound of A10 (R39): not reached; paired-noise reference runs at sigma = 0.01, 0.05, 0.1.
4. A4 (the box's d phi, d Pi at N_f against the reference's state): not computed on the baseline (the per-member reader
   does not record it); a small script over the saved fields or the dumps.
5. Package: the fresh verifier (decision 0016) once 1-2 have closed; it recomputes (V), (T) and A5 from the dumps with
   its own reader, G3-C and G3-R, and repeats the table check against the long-double map on a second member.
6. Reservations carried: geodesic slicing only (A8); U-A4'(a) of G2 stays FAILED as written (answered by G3-C).
