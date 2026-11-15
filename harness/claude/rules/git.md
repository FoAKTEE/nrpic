# Git (brief 13.1; decisions 0003, 0009)

- Write only your own paths: `tracks/<ID>/**` and the globs of `tracks/<ID>/OWNERSHIP`, in your own
  worktree, on your own branch. Read other owners through git (`git show <branch>:<path>`,
  `harness/bin/nrpic-ctx show <ID> [file]`). Shared paths change through a proposal in
  `tracks/<ID>/outbox/` (`nrpic-ctx post --type proposal`).
- Commit path-limited: `git add <paths> && git commit -m "..." -- <paths>`. Never `git add -A` in a
  tree other sessions also write. One writer of the git index per worktree: helpers hand files to
  the lead. If git reports `index.lock`, wait five seconds and retry; never delete the lock.
- Subject `<ID short>(<area>): <imperative summary, at most 72 characters>`; areas: code pgen input
  run analysis fig note status ctx env kb harness fix. Body: why, evidence (run ids, test names, KB
  locators), what is NOT done. Trailers `Run-Id:`, `Gate:`, `Refs:` where they apply, then the
  attribution lines your session was given.
- Commit before every run (`nrpic-run` refuses a dirty worktree), after every logical unit, and at
  the end of every session; then `git push -u origin <your branch>`.
- Never: force-push, rewrite or rebase pushed history, `--no-verify`, commit files above 5 MB or
  secrets, amend a commit a run manifest or a tag refers to, delete a branch or a worktree, push
  another owner's branch. Tags (`stage/*`, `core-v*`) are created and pushed by the orchestrator.
- Start of session: `harness/bin/nrpic-ctx sync` (merge of main). A conflict means somebody crossed
  a boundary: stop and tell the orchestrator.
