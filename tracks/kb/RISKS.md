# RISKS of kb

Updated 2026-11-15 (kb lead, wave 1). Likelihood and effect: low / medium / high.

| Risk | Likelihood | Effect | Watch | Response |
|---|---|---|---|---|
| Parse errors hidden behind a good quality score give tracks wrong equation numbers or locators (found twice this session: \nc aliases, composite shorthands; 28 papers) | medium | high | independent counts on drawn papers (journal L5, L10, L11); equation rows per paper against `\begin{equation` counts | K9: a sampled independent-count check in `kb qa run`; notes cite the snapshot id so a later fix can be traced |
| No sanctioned metadata path: no titles/abstracts for 36/27 papers, no cross-check with brief 16, 17661 unresolved bibliography entries; KB-G2 blocked | high | medium | outbox `__to-orch__metadata-path` | parse what the store has; ask once per week |
| Paper text or third-party figures leave the machine through commits (reports, curated statements) | low | high | `git diff --stat` before each commit; reports carry ids and counts only | own wording in curated files; nothing under kb-data is committed |
| A download escapes its directory or is executed | low | high | `kb verify-downloads` checks members, links, exec bits, sizes | never run code from kb-data/raw; propose limits in nrpic-fetch-arxiv (outbox) |
| Upstream AthenaK publishes a particle-spacetime coupling and nobody notices | medium | medium | `kb watch upstream` (baseline 2026-11-15, no scheduler) | outbox `__to-orch__watch-scheduler`; run it at the start of each kb session |
| Tracks treat `claimed` paper-code links as verified | medium | medium | `kb link list` shows status | core names tests (outbox `__to-core__paper-code-links`) |
| Equation numbers of real papers cannot be checked against LaTeX output (no .aux, no compiling downloads) | medium | medium | cross-check against `\ref`-resolved numbers in the papers' own text | label numbers as computed by kb; check against the PDF when one is stored |
| Snapshots fill the disk (0.81 GB each, four now) | high | low | `du -sh kb-data/db` | keep the last three and those cited in notes; prune others by name |
| Embedding stage too slow on 8 cores, or no model approved | medium | low | timed scouting run on 1000 chunks | full-text search (exists) until vectors exist; outbox `__to-orch__embedding-model` |
| Other sessions add store entries at any time, so counts move between runs | high | low | verify-downloads reports extras | numbers always with a run id |
| A long-running writer keeps an old module after a fix (lock, parser) | low | medium | process list before a fix lands | restart writers after fixes; one writer at a time |
