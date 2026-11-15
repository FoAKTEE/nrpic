# 0009 Sessions and models

Status: ACCEPTED (user instruction of 2026-11-15) · orchestrator

The tracks run as agents started by the orchestrator in waves, one lead per worktree and
wave, with helpers for independent work packages. A lead is the only writer of its
worktree's git index. Models: Fable at the highest effort for derivations, design and
production code, which goes into the source tree (`athenak/src/`, `python/nrpic/`);
Opus at the highest effort for everything else (baselines, literature, knowledge base,
harness, analysis, figures, notes, independent verification). When Fable is exhausted,
Opus takes over its work. Everything is tracked in git.
