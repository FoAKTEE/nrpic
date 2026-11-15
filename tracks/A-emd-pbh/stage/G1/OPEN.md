# What G1 of A-emd-pbh still lacks (lead, wave 2, 2026-11-15)

Items of `CHECKLIST.md` that are not PASS, with the smallest action that closes each. The
three track criteria of the sheet (T1-T3, as amended by decision 0013) are met
(`STATUS.md` section 1).

1. **C11, data-flow schematic** (minimum figure of brief 13.4): not drawn. Action: one
   paperfig.py schematic in `note/scripts/schem_dataflow.py`: data generators (expball
   tables and lattices, make_peak_ic, make_deformed_ball) -> AthenaK (nrpic_cf, nrpic_cosmo,
   Newtonian mode) -> outputs (trajectories, histories, tables, horizon summaries) ->
   comparison (runs_ball/compare.py, analyse_scouting.py, analyze_newton.py) against the
   exact references (expball/exact.py, criteria/, newton references) -> ledger.
2. **C18, verifier for G1**: `VERIFIER.md` covers T1 and part of T2; T3 (`newton/`) and the
   criteria package's check list were not examined by a fresh verifier; the lead's checks
   (`../REVIEW-wave2.md`) are a second agent but not a fresh one. Action: a fresh verifier
   given `newton/` (tables, runs) and `criteria/` (results JSON), plus the note's ledger
   (as G0 item 1).
3. Not a gate item, recorded for G2: AthenaK's own t = 0 constraint norms of the format-2
   tables were not extracted from SR-1/SR-2 (the cstat files hold them: H_max 4.7e-4 at
   dx = M/2, t = 0, run A-emd-pbh-20261115-153845-7172b66).
