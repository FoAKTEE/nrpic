# What G0 of A-emd-pbh still lacks (2026-11-15)

Items of `CHECKLIST.md` that are not PASS, with the smallest action that closes each.

1. **REPORT.md of this stage directory was not written.** The session that assembled the
   package runs as a workflow subagent, and its harness refuses to write files named as
   reports. The scoping content is in `scope/SCOPE.md` sections 1-9 (helper) and section 10
   (lead's decisions and corrections), the artefacts in `EVIDENCE.md`, the gate items in
   `CHECKLIST.md`. Action: a lead session that can write it assembles REPORT.md from those
   three, or the orchestrator runs `harness/bin/nrpic-stage report A-emd-pbh G0`, which writes
   `STAGE_REPORT.md` from `CHECKLIST.md`.
2. **Working note v0** (charter 9.2 main product; checklist C5, C15): a REVTeX note under
   `note/`, written with /paper-writing, with the problem statement, the threshold
   definition, the expanding-ball data (DERIVATION.md sections 1-8) and the test plan; its
   checker run with `--compile`. Not started.
3. **Two schematics** (C6, C9, C10, C14), with /sleep-paper-figure-style: the track
   architecture in three states (exists: NRPIC coupling, format-2 reader on core/id-extrinsic,
   flow horizon finder, conformal-time lapse; to be ported: none; new: phase-1 generator,
   Newtonian mode, K_ref lapse, dispersion data, finder spin projection) and the gate
   timeline (SCOPE.md 10.8). Not started.
4. **Verifier report** (C16): a fresh agent given the artefacts, not the conclusions. The
   lead's re-check (`EVIDENCE.md`, journal L1-L8) is a second agent for the helpers' numbers
   but not for the lead's own decisions and cross-checks.
5. **Reference statements in the knowledge base** (C2): read and located at the raw store
   (`scope/REFERENCES.md`, seven locators re-read by the lead), not yet kb entries. Request:
   `outbox/20261115T1320Z__to-kb__ingest-s1-references.md`.
6. **References not read**: arXiv:1708.09143 (section-10 row "Szekeres", test A4),
   2403.15126 (waveforms), 2605.30145 (spherical CDM-peak collapse), 1810.03490
   (inhomogeneity criterion); 2608.13206 only for its gauge part.
7. **criteria rerun**: started as A-20261115-130252-01e8b64 (`check_criteria.py`, about
   14 minutes); its outcome is recorded in `stage/G1/STATUS.md` and `JOURNAL.md` if it
   finished within the session, otherwise it is listed there as pending.
8. **`nrpic-stage verify`** not run: it needs `note/scripts/` and a `stage/G0/VERIFY` command
   list, which come with item 2.
9. **Amplitude convention** settled in SCOPE.md 10.1, but `criteria/predict.py` does not yet
   print the conversion delta_c = e deltabar_ent for the Gaussian profile of
   arXiv:2609.14218; add a row before the tables are used in a note.

Closed in this session: the [TO VERIFY] on the horizon-mass error of the source paper's
Oppenheimer-Snyder test (SCOPE.md 10.4); the run manifests are committed under `runs/`.
