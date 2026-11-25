# G3 of Track E: what is open (batch 20, 2026-11-25)

G3 is not ready for review. The scope is fixed (spec/scope/SCOPE.md 4d with the amendments 4d.9 A1-A14; A14 written in
batch 20 after smoke tests and before the registered runs it governs); no G3 production run on the cards has run yet.

1. Reference proper: direct 4e6 (E-20261125-152832-c301e92: gate 0.99865 +- 0.00058, skewness 0.0199 +- 0.0012);
   importance-sampled nu = 4 (A9 with A14 (a)): E-20261125-160658-855db8c (outcome in g3/amend/JOURNAL.md entry 10);
   lattice sigma = 0.1 (E-20261125-160722-a6d1f26): variance gate FAILED (1.00245 +- 0.00050), skewness 0.0182 +-
   0.0014; the coarse-graining bound of A10 (below 0.0027) is NOT reached (R39).
2. zeta reader (zeta/zeta_reader.py, E-20261125-161456-8d3f43c): Z0, Z2(i), Z2(iii') pass; Z2(iii) FAILED as written
   (-2.89 per cent; predicted); Z1 FAILED as written along Pi alone (0.142; passes along phi and the box relation).
   The reader judges no G3 run until the orchestrator rules (outbox 2026-11-25 batch 20). TO VERIFY of 4d.3 settled.
3. Cost of the zeta map on 128^3 (R41): about 11 core-minutes per dump; to be cut before the baseline is read.
4. Card runs in the shared queue, all waiting (cards held by another partition): q0050 G3P (pilot), q0051 G3C,
   q0052 G3R (priority 2), q0053 G3B00, q0054 G3B01 (priority 5, after G3P). The remaining baseline pairs and the
   16 level-2 pairs wait for the pilot's measured cost (A12).
5. Reservations carried: geodesic slicing only (A8); U-A4'(a) of G2 stays FAILED as written (answered by G3-C).
6. Package items (C5, C6, C9-C17): result figures, ledger, schematic of the parameter space, working-note section,
   fresh verifier: after the runs.
