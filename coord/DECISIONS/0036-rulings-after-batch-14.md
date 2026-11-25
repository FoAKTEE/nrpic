# 0036 Rulings after batch 14: release core-v0.7; Track E's failed criterion

Status: ACCEPTED · 2026-11-24 · orchestrator (decision 0017)

1. Release core-v0.7 is on main (tag on 5f75e5b9; builds `.work/build_gpu_v07`,
   `.work/build_cpu_v07`): level 2 of the stochastic backreaction and the mode equation
   of the noise on the mesh, the step limit that counts the gauge speeds (`<z4c>
   dt_gauge`), restart outputs on the termination signal and a chain script that does not
   count an attempt cut by a signal, `lapse_leak_hole` as a mitigation, table clusters
   with momentum. Byte regression against core-v0.6 on processors: 75 of 75. Its merged
   card executable has not run on a card: the card checks wait in the shared queue
   (entries q0039, q0035, q0036) and core judges them when they have run.
2. Track E, criterion U-A4'(a) of its scope section 4c. The fresh verifier confirmed
   every criterion and the one failure on record (the even-part halving of the momentum
   constraint, 3.9245 at one dump of eleven against a bar of 3.95 to 4.05), and found
   with the quarter-amplitude pair that the miss comes from the floor estimator of 4c: a
   part of each run's even part does not scale with the amplitude, and with its level
   taken from three amplitudes every judged dump lies within 4 +- 0.005. Ruling: the
   criterion stays FAILED as written (decision 0030 item 2: no rewording); the
   three-amplitude reading stands beside it in the package and in the note as a finding
   made after the data, labelled so. The package goes to independent review when the
   lead has closed its records.
3. Knowledge base: after the claims package the lead takes the snapshot and a second
   fresh verifier reads the claims processed since the first; the orchestrator then
   judges KB-G3 on both reports.
