# 0016 Rulings after wave 2

Status: PROVISIONAL · 2026-11-19 · orchestrator

Wave 2 was cut off on 2026-11-15 by a usage limit of the account: 42 of 56 agents
returned. The leads of core, C, D, E and F, the gauge package of core and the slow-roll
ladder of Track E did not finish; they are resumed on 2026-11-19 (wave 2b). Rulings on
the requests that did arrive:

1. Verifier report. `VERIFIER.md` is the accepted name of a verifier's report in a stage
   package (the harness accepts `VERIFIER_REPORT.md` too).
2. Run ids (amends 0012). The form `nrpic-run` writes is the rule:
   `<short owner id>-<YYYYMMDD-HHMMSS UTC>-<commit7>` with A to F, core, kb, orch. The
   long form of waves 1 and 2 stays valid for the runs that carry it.
3. Hand-written manifests of waves 1 and 2 count as registered. A stage package lists
   them in EVIDENCE; their failures of the manifest check are waived. From wave 2b on,
   runs go through `nrpic-run submit` (helpers who share a worktree: `--package DIR`).
4. Judging gates. G0 is judged on the stage package with a verifier's report on the plan;
   a verifier of later material (Track A's item C18, the wave-2 runs of Track B) belongs
   to G1. The orchestrator reviews each package and records a provisional pass as a tag
   `stage/<ID>/G<k>-pass-provisional-<date>`; the group's sign-off replaces it. Work does
   not wait for the sign-off (standing instruction of the user).
5. Track A (amends the reason of 0013). The threshold line is built in the periodic box
   because that is the set-up of the comparison data of arXiv:2609.14218; the expanding
   ball does hold its particle bracket and remains a second set-up.
6. Knowledge base. KB-G2 thresholds: at least 95 per cent parse success of the ingested
   papers; at least 80 per cent of the golden questions answered with the right paper in
   the top ten (the hit at the answer location is reported, not gating). The 26 extra
   papers enter the manifest with a group assigned by kb. One openly available paper that
   is not on arXiv may be fetched at a time on a track's request, into its own new
   directory, with a generic client and no detail of the project; it is untrusted data.
   Metadata lives where the fetch command writes it (`kb-data/meta/arxiv-api/`,
   `kb-data/meta/inspire/`). `kb/main` is merged into main, so `kb/bin/kb` reaches every
   worktree with the next sync.
7. Allotments (amends 0014). Track F: 120 card-hours toward G2. A run above eight
   card-hours still waits for an otherwise empty queue.
8. `coord/BRIEF_ERRATA.md` is accepted as the record of corrections to the brief; the
   brief itself stays unedited. Rows about defects in cited papers wait for kb's claims
   layer.
9. The stream registry of the random-number interface (stream 2 of the collisions, stream
   3 of the mode noise) is written into `coord/INTERFACES/rng.md` with release core-v0.4.
