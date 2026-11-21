# C-sidm G1: what the gate still lacks

State at the end of the lead session of batch 2b (2026-11-21). Verdict of the lead: G1 NOT
MET. Every criterion of the track sheet is now met (C6 "all tests of C-pre-1 pass", C7 "the
baseline is reproduced") and so are C1-C5 and C9-C15; two package items are open. The
package does not ask for a pass yet.

1. Working note with the G1 results (C16). The note package was cut by the usage limit on
   2026-11-20 22:35 UTC while writing the G1 sections. Its figures and schematics exist
   (registered run C-20261120-223007-fe3f39c, committed 077b849d); `note/main.tex`,
   `references.bib`, `scripts/{common,ledger,schem_timeline}.py`, `tables/ledger.tex`,
   `tables/runinfo.tex` and `schem_timeline.*` are edited and uncommitted in the worktree.
   Remaining: the outcome of prediction N3 in `note/JOURNAL.md`; the G1 sections finished
   (box tests of waves 2 and 2b, heat T6-T8 with the wave-3 numbers, models and the rate
   restriction of C2, Juttner anchor and King onset; the cluster runs as G2 scouting); two
   boxes of the architecture schematic updated (growth-rate fit decided; T7/T8 also on the
   card); a second registered run_all; compile; manuscript checker with --compile; pages
   read; commit. Owner: C-sidm (a note helper).
2. Fresh-context verifier of the G1 material (C17). Package `verify_g1` (resumed in batch
   2b): V1a-V1c, V2, V3 done and confirming; the rest of its plan and `stage/G1/VERIFIER.md`
   outstanding. The lead then answers every WRONG or NOT CONFIRMED item. Owner: C-sidm (the
   verify_g1 helper, then the lead).
3. Minor gaps of the track's own extra tests (not of the brief's list; not blocking in the
   lead's judgement): T10b for the T4 statistics (one short card job); the MPI variant of T10
   (collisions stop on more than one rank in core-v0.5, `coord/INTERFACES/mpi.md`); T3-T5, T9,
   T11 not repeated with `coll_energy = particle`; T8 on one card seed only.
4. Reservations carried to G2: the zero-cell-size conductivity at theta 0.003 may lie 1-3
   percent below the relativistic Chapman-Enskog value of V1a (itself unreviewed); growth
   rates on runs are defined only with their fitting interval.
