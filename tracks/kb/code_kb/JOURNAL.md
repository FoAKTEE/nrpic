# Journal of package code_kb (kb helper, wave 3 round 1)

Package: upstream watch of AthenaK (decision 0015), K7 module descriptions and task-list
order (brief 12.7), a test with evidence for each of the 25 paper-code links (request
kb paper-code-links, coord/REQUESTS.md:82), the `<z4c> nco` question, the parameter index.
Card cap 0. Every number below carries a run id or a file:line locator.

## 2026-11-20 22:19 UTC, entry 0: state at start

- Worktree wt/kb at 8b24b590 (main merged by another helper of this round); no earlier
  session of this package: `tracks/kb/code_kb/` did not exist, git status clean.
- Last watch: run kb-20261115-154646-234060c, snapshot
  `kb-data/meta/github/watch/IAS-Astrophysics__athenak/20261115T154646Z.json` (124 branches,
  main c5a0d7f9155a; compared with 20261115T132754Z: nothing new, moved or removed). Its
  report went to `tracks/kb/served/watch/code_watch_upstream.md`; `kb/reports/
  code_watch_upstream.md` still holds the 132754Z baseline report.

## W1 prediction (upstream watch), written before the run

Criterion for a message to core (brief 12.7 as the task states it): src/particles or src/z4c
changed on some branch since snapshot 20261115T154646Z, or a branch name contains pic,
vlasov, nrpic or deposit.

Expectation [JUDGEMENT]: five days have passed (2026-11-15 to 11-20). AthenaK upstream moved
main every few weeks in 2026 (main tip dated 2026-09-11 when the watch first looked), so I
expect a handful of branches to have moved (0 to 10), main possibly unchanged, and at most a
few branches with changed src/z4c or src/particles files. I expect no branch name with pic,
vlasov, nrpic or deposit, and still no branch whose src/particles mentions tmunu or deposit.
So the criterion fires only if some moved branch touched src/particles or src/z4c; I give
that about even odds.

Refuted (each separately): a branch named with pic/vlasov/nrpic/deposit; any branch whose
src/particles mentions tmunu or deposit (that would be particle back-reaction upstream, the
coupling this program built); more than 10 moved branches; main moved.
