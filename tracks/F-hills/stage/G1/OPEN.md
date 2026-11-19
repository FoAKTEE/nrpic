# G1 of F-hills: what the gate still lacks (2026-11-19, lead, wave 2b)

1. **The complete vacuum passage (T4).** P1 (run F-20261119-150017-b45ec5f, Slurm 4650, chain of
   up to 26 segments, 17-20 card-hours expected) waits in a shared card queue; the next session
   follows it (`harness/bin/nrpic-run status F-20261119-150017-b45ec5f`,
   `scripts/submit_chain.sh --status /data/haiyangw/nrpic/scratch/F-hills/F-20261119-150017-b45ec5f`),
   closes it with `nrpic-run finish` and analyses it against the predictions in `JOURNAL.md`.
   Known risks: member horizon masses drift (0.6-1.1e-4 per member mass per unit time at m/8 in
   single punctures); the heavy hole's finder fails in the first few M; a tree above 2700 slots
   would stop a segment (wave-1 maximum along the Newtonian track 2080); tracker files survive
   restarts only through the wrapper.
2. **Junk radiation of the three-hole data (T3).** Not measured: S3/S2 stopped before the pulse
   reached 30 m. From P1's spheres (40-90 M) and S2g (run F-20261119-143443-f11ebb9, pending).
3. **F-pre-2 for Kerr (T2).** 2402.02178's inclined-binary statement is not reproduced; the
   equatorial Kerr HRNA exists. Also open from the second check: the flat-space moving-binary
   test of HRNA's self-acceleration (R3) in `geodesic_binary/tests`.
4. **G1 schematics and note.** Updated architecture and a data-flow diagram (brief 13.4) are not
   drawn; the note has no G1 section on the NR runs (E2, E3, E7, E11, P1).
5. **Verifier (C18).** No VERIFIER.md; asked of orch.
6. **Gauge.** S2g (mass-scaled damping) pending; its outcome decides whether the profile is
   tested with three holes before the next passages. Core: has `shift_eta_profile` run with three
   holes? (outbox).
7. **Small defects listed, not fixed.** `three_punctures/scripts/newton_start.py` reads the
   pre-fix energy fields; `nr_first/scripts/single_analysis.py` repeats the last mass for times
   after a run's end in `m_at`.
8. **Second agent on the newton3 energy derivation.** The numbers agree between two codes (V10
   against V5b); the derivation was read, not re-derived.
9. **For G2.** q = 4 at m/16 needs 2864 MeshBlocks, above one card's 2700 slots (two cards or 32^3
   blocks: core's benchmark bench16/bench32 not run); a q = 10 passage needs momenta from a GR
   parabola (second check; V9a).
