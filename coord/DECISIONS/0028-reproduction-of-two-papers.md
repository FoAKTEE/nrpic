# 0028 Full reproduction of arXiv:2512.14649 and arXiv:2401.08530, with a working note

Status: ACCEPTED · 2026-11-22 · requested by the user; planned by the orchestrator

The user asked on 2026-11-22 whether the two papers on stochastic inflation (arXiv:2401.08530,
"Stochastic Inflation in General Relativity"; arXiv:2512.14649, "Stochastic Inflation in
Numerical Relativity") can be reproduced in full with this repository's AthenaK, and for
a working note on it written with the updated paper-writing skill.

1. Owner: Track E, packages under `tracks/E-stoch-inf/repro/`.
   - `scope`: map of every figure, table and quantitative statement of arXiv:2512.14649
     to a run of ours; audit of the paper's set-up against our inputs; the card runs
     that are missing, in the paper's set-up.
   - `langevin`: the numerical part of arXiv:2401.08530 (two coupled Langevin equations of
     one patch in the uniform-field gauge, fifty thousand paths, four figures). This is
     not a computation of numerical relativity (the paper says that no such code exists
     in that gauge): it is reproduced with a reference integrator in Python, which
     decision 0010 allows outside the source tree.
   - `equations`: the stochastic equations of both papers checked with computer algebra
     and mapped to the lines of `athenak/src/scalar_field/` that implement them.
   - then `figs` (the figures of arXiv:2512.14649 from the runs), `note` (the working
     note) and `verify` (a fresh verifier), once the card runs have ended.
2. What "reproduced" can mean here: the authors' code is not public and their random
   realisations are their own, so agreement is statistical and against the linear
   solution and the numbers the papers print; nothing read off their figures is committed
   as data (rule 9; decision 0023 item 4), and their figures are never committed.
3. The working note is written with the user's updated skill (unpacked for the agents at
   `scratch/orch/skills/paper-writing-updated/paper-writing/`; source file
   `/data/haiyangw/claude/find/paper-writing-updated.skill`), manuscript under
   `tracks/E-stoch-inf/repro/note/manuscript/`, guide and notation one level above.
4. Models: these sessions run on Opus, the derivation checks included; a review of the
   derivations on Fable follows after the reset of the weekly usage window if a check
   leaves a doubt (decision 0026 item 6). This request goes before the second half of the
   analysis round (batch 10b) where the window does not allow both.
