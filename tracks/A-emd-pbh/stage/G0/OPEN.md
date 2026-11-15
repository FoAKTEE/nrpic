# What G0 of A-emd-pbh still lacks (lead, wave 2, 2026-11-15)

Items of `CHECKLIST.md` that are not PASS, and the remaining loose ends, with the smallest
action that closes each. Wave-1 items 1-5, 7-9 are closed (working note v0, two schematics,
STAGE_REPORT.md instead of REPORT.md under decision 0012, a fresh verifier, the key
references in the knowledge base, the amplitude conversion in `criteria/predict.py`).

1. **C18, verifier recomputation of the note's ledger.** `VERIFIER.md` checks the claims the
   plan rests on (C1-C8) but not the ledger appendix of `note/main.pdf`. The ledger is
   computed from the run outputs with checksums by `note/scripts/ledger.py` (run
   A-20261115-161947-09324e1). Action: a fresh verifier reruns `ledger.py` into its own run
   directory and checks each ledger row against the cited run's files (about one hour).
2. **One key statement still 'to_verify' in the knowledge base** (claim 25, the particle
   bracket of arXiv:2609.14218, MDPBH.tex:L1101-1103; 17 more Track-A claims, mostly "NOT
   computed" lists). Read at the source by the lead in this session. Action: kb updates the
   status (outbox request of this session).
3. **The note covers the wave-2 runs only qualitatively** (SR-1/SR-2, S1/S2, Newtonian mode).
   Not a G0 requirement; for G1/G2: rerun `note/scripts/run_all.py`, extend Sec. IV, add
   `ledger.py` to `stage/G0/VERIFY` (the note helper's request) once the ledger has been
   regenerated against the corrected SCOPE.md (its claims check locates lines there).
4. **References not read** (unchanged): arXiv:1708.09143 (Szekeres row), 2403.15126
   (waveforms), 2605.30145, 1810.03490; 2608.13206 only for its gauge part.
