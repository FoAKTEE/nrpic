# What the G0 package of E-stoch-inf still lacks (2026-11-19, lead of wave 2b)

Every checklist item is PASS or NA (CHECKLIST.md, collected 2026-11-19). The items that
were open on 2026-11-15 and how they closed:

1. The group's decision (C8): decision 0013 (continue to G1 and G2), accepted by the user with
   decision 0017.
2. Working note v0, schematics (C5-C7, C10, C11, C15-C17): written in wave 2 (`../../note/`).
3. Verifier report (C18): `VERIFIER.md` (wave 2), rerun by the lead (REVIEW-wave2.md).
4. Automated stage check: `nrpic-stage verify` (VERIFY_RESULTS.md of this session).
5. Statements of the key references (C2): read at file:line; errata are kb claims 603-609.
6. Measured card cost: 0.503 card-hours per SR realisation at 256^3 (run
   E-20261115-172618-f948386).
7. STATUS, HANDOFF (C20): rewritten 2026-11-19.

Still open, not required for G0 (carried to G1/G2 in `../G1/OPEN.md`):
- The key statements of the references are read at the source, not held as knowledge-base
  claims; only the errata are claims.
- Parts of the helpers' work nobody has re-checked: the end-of-inflation delta-N statistics
  after USR and the importance sampling of the phase-space solver (`langevin/`).
- The USR cost per realisation (estimate 0.63 card-hours by step count) and the synthesis
  cost with MeshBlocks smaller than 256^3 are not measured.
- The schematic `schem_timeline.png` still shows "the group's decision pending", and the
  right x-axis label of `fig_background.png` is cut at the edge (note v0, to be redrawn with
  the G1 sections).
- `nrpic-stage verify` fails `runs` only on the run of the wave-3a package `usr/`
  (E-20261119-144116-8aa7c22) while it is running, and `clean` while that package's file
  `usr/scripts/analyse_runs.py` is uncommitted; neither belongs to this package (see
  STAGE_REPORT.md, notes on the verification).
