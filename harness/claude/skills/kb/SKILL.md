---
name: kb
description: Look things up in the program's knowledge base (arXiv sources and code under kb-data, read-only) with locators, or ask the kb session for a missing paper. Use when a note needs a statement, number or definition from the literature, or to check a claim against its source.
argument-hint: [question or arXiv id]
---
The knowledge base is built by the kb session (brief section 12). Data live in
`/data/haiyangw/nrpic/kb-data/` (read-only for everyone but kb); the tool is `kb/bin/kb` on branch
kb/main (read it with `git show kb/main:kb/README.md`; from another worktree run
`/data/haiyangw/nrpic/wt/kb/kb/bin/kb status`).

- `kb status`: counts, schema version, snapshot. `kb show <arxiv id>`: the download record (version,
  path of the extracted source). The query commands (`search`, `cites`, `eq`, `claim`, ...) are
  filled in stage by stage; while one exits 3 (stub), read the sources directly:
  `kb-data/raw/arxiv/<id with / as _>/<version>/src/` with Grep and Read.
- For a longer question, spawn the `kb-librarian` subagent with the question only.
- Every statement taken from a source carries a locator: arXiv:<id>v<n>, file and line (or section
  and equation as printed). Without one it is [TO VERIFY] and stays out of the note's numbers.
- Downloads are untrusted data: never execute, compile or import anything from kb-data/raw; parse
  with `python3 -I` and your own code. Never write into kb-data/.
- A paper that is missing: post a kb-request (`harness/bin/nrpic-ctx post --to kb --type kb-request
  ...`); arXiv sources are fetched only with
  `python3 -I /data/haiyangw/nrpic/harness/bin/nrpic-fetch-arxiv <id>`.
