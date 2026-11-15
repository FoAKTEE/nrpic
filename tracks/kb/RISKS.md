# RISKS of kb

Updated 2026-11-15 (kb lead, wave 2). Likelihood and effect: low / medium / high.

| Risk | Likelihood | Effect | Watch | Response |
|---|---|---|---|---|
| Parse errors hidden behind a good quality score give tracks wrong equation numbers or locators (wave 1: 28 papers; wave 2: astro-ph/0003278 with sections in its source and none in the database) | medium | high | three independent counters agree on the K9 sample (W4); C2 now separates "no sectioning command" from "command present, nothing extracted" | `kb qa run` with the sampled count each stage; notes cite the snapshot id so a later fix can be traced |
| A track takes a `located` claim for a checked one: the automatic check proves only that the locator resolves and the numbers occur, not that the passage says it | medium | high | `kb claim show` gives status and checked_by; audits 29/30 (helper) and 9/10 (lead) supported | only `checked` claims count as read by a person; parser fragments (claim 193) found by audits; audit 10 claims per wave |
| Retrieval misses the answer location although the paper is found (answer location 23/32, paper 28/32; four of ten FIRST_QUESTIONS missed by every mode) | high | medium | golden set and the ten held-out questions, rescored independently | `--text-only` when the words are known; finer chunks or windowed vectors, chosen on one set and checked on the other |
| KB-G2 cannot be judged: no thresholds or hit level in CHARTER; one manifest paper not ingested | high | medium | coord/REQUESTS.md | outbox kb-g2-thresholds, kb-g2-hit-level; PDF reader for gr-qc/9412071 next session |
| Paper text or third-party figures leave the machine through commits (wave 2: a run wrote a reading sample into the worktree through a literal `$NRPIC_RUN_DIR`; deleted, never committed) | low | high | `git status` and sizes before each commit; pre-commit hook not installed (decision 0008) | scripts read the run directory from the environment; proposal to orch (nrpic-run-literal-run-dir) |
| Two writers of the claims layer undo each other (wave 2: a `--rebuild` deleted 330 rows of another helper) | low | medium | ingest_log of kb.sqlite; digest of claims before and after each load (W6) | rebuild touches only rows of its own seed (guard, test); claim ids frozen once a snapshot holds them; one writer at a time under locks/kb-writer.lock |
| A download escapes its directory or is executed | low | high | `kb verify-downloads`; the fetch command's limits and content checks (decision 0015) | never run code from kb-data/raw; read with python3 -I code outside it |
| Upstream AthenaK publishes a particle-spacetime coupling and nobody notices | medium | medium | `kb watch upstream` each wave (decision 0015); last run kb-20261115-154646-234060c: unchanged | run it at the start of each kb session |
| Tracks treat `claimed` paper-code links as verified | medium | medium | `kb link list` shows status | core names tests (outbox paper-code-links, open since wave 1) |
| Runs exceed kb's core allotment when registered by hand (wave 2: 12 and 16 threads) | medium | low | nrpic-run enforces 8 | register every run with nrpic-run submit |
| Snapshots fill the disk (up to 1 GB each, eight now, 6.1 GB) | medium | low | `du -sh kb-data/db` | keep the ones cited in notes; prune others by name |
| New papers lack tags and vectors because ingest does not call those steps | medium | low | `kb embed --check --work` | run tags, embed, check, snapshot after every ingest (W9b); later: call them from ingest |
