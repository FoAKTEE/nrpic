---
name: ctx
description: Context sharing between the owners of the NRPIC-cosmology program through git (status of other tracks, messages addressed to me, posting a request or proposal, syncing main). Use at session start and end, before asking another track for something, and when the brief mentions unread messages.
argument-hint: [sync|brief|board|show|inbox|ack|post|digest|audit] [args]
---
All context goes through `harness/bin/nrpic-ctx` (brief 11.3). Files are the record; messages
between sessions are only a doorbell. Run it from your own worktree.

Read (never writes, never merges):
- `harness/bin/nrpic-ctx brief`: who I am, gate, STATUS summary, inbox count, how far main is ahead.
- `harness/bin/nrpic-ctx show <ID> [FILE]`: a file of tracks/<ID>/ at the tip of that owner's branch
  (default STATUS.md).
- `harness/bin/nrpic-ctx board`: STATUS of every owner.
- `harness/bin/nrpic-ctx inbox [--show]`: messages addressed to me or to all, not yet acknowledged.
- `harness/bin/nrpic-ctx audit`: commits touching foreign paths, oversized files, untracked roots.

Write (only on your own branch, committed):
- `harness/bin/nrpic-ctx sync`: merge main into your branch; first thing in every session.
- `harness/bin/nrpic-ctx ack <n|file>... [--note TEXT]`: acknowledge inbox messages.
- `harness/bin/nrpic-ctx post --to <ID|core|kb|orch|all> --type <info|request|proposal|interface-change|blocker|kb-request> --slug <slug> --body-file <file> [--reply-by YYYY-MM-DD] [--refs a,b]`:
  a message in tracks/<me>/outbox/. The body says what is asked or announced, why, the evidence
  (run ids, KB locators), and the smallest acceptable answer. To change shared content (coord/,
  harness/, CLAUDE.md, core code) post a proposal; code proposals also get a branch
  proposal/<ID>/<slug>.

At the end of a session: rewrite STATUS.md (at most 60 lines), append one JOURNAL.md entry,
rewrite HANDOFF.md for a reader with no memory, commit, push your branch.
