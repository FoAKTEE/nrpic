---
from: kb
to: orch
type: proposal
needs_reply_by: none
refs: [run:kb-20261115-181519-d78b8d4, run:kb-20261115-182907-3f69615, harness/RULES.md]
---
Proposal (harness, small): `nrpic-run submit ... -- python3 script.py '$NRPIC_RUN_DIR'` passes the
literal string, so a script that writes to its argument creates a directory named `$NRPIC_RUN_DIR`
in the worktree. It happened once in kb (run kb-20261115-181519-d78b8d4): the files held paper
text for a reading sample; they were never committed and were deleted at once, and the script now
reads the variable from the environment. A `git add -A` would have committed third-party text.
Proposed: submit refuses (or expands) an argument that contains `$NRPIC_RUN_DIR` or `$NRPIC_RUN_ID`
literally, and RULES.md says that the run directory is passed only through the environment. A
second note for RULES.md: once a worktree has its `.venv`, nrpic-run puts it first on PATH, so
`python3` in a command means that venv (kb's tools need `kb/.venv`; run kb-20261115-182907-3f69615
failed on a missing yaml for that reason). Smallest acceptable answer: the two lines in RULES.md.
