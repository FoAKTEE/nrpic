# KB-G0: what is open (kb lead, wave 3 batch 3, 2026-11-21)

Every item of CHECKLIST.md is PASS. The verifier's report is VERIFIER.md (C5); the lead's
recheck of it is ../REVIEW-wave3.md. Minor defects left on record:

- `kb-data/raw/arxiv/*/*/source.bin` have mode 0664: "raw files are read-only" (brief 12.1)
  holds by convention (one Unix user for all sessions; CLAUDE.md rule 8). Not changed now: the
  unfinished package ingest3 fetches into kb-data/raw; a chmod is for the lead after it lands.
- Snapshots of 2026-11-15 between 13:56Z and 18:39Z: only three are tied to a stage by their run
  (verifier, "Not checked"); the others are intermediate and unused by any package.
- The pre-commit hook is installed (`git config core.hooksPath` = harness/hooks, checked
  2026-11-21; `harness/hooks/pre-commit`: files above 5 MB, secrets, manifests, paths); it does
  not recognise a paper source by content, so the kb session still checks `git status` and file
  sizes before each commit.
