---
name: stage-check
description: Assemble and verify the stage-gate package of one track (working note, figures, report, proposed tag). Use only when a stage check is requested.
disable-model-invocation: true
argument-hint: [track-id] [gate]
arguments: [track, gate]
---
Stage check for track $track, gate $gate (if these are empty, take the two words of $ARGUMENTS).
Work in the worktree of $track (`/data/haiyangw/nrpic/wt/$track`). Do the ten steps in order; never
skip or reorder one. If a step fails, stop, write the failure into
tracks/$track/stage/$gate/STAGE_REPORT.md (`harness/bin/nrpic-stage report $track $gate`), commit
it, and ask the orchestrator for the tag stage/$track/$gate-fail-<date>.

1. `harness/bin/nrpic-ctx sync` (merge of main; stop on a conflict).
2. `harness/bin/nrpic-stage collect $track $gate` -> tracks/$track/stage/$gate/CHECKLIST.md. Judge
   each item: set `status:` to PASS, FAIL or NA and write the evidence (run ids, figures, KB
   locators). Commit the code, notes and figures the package rests on (path-limited).
3. `harness/bin/nrpic-stage verify $track $gate`: re-runs every figure script and the commands
   listed in tracks/$track/stage/$gate/VERIFY on a clean export of HEAD and compares; fix every
   FAIL, commit, run it again until it passes.
4. Data figures: invoke the skill `zoom-figure-style`; follow its workflow and its checks before
   delivering. Use the project's czstyle.py (the copy in tracks/$track/note/scripts/, identical to
   harness/style/). One script per figure in tracks/$track/note/scripts/, reading registered run
   outputs only, saved with save(fig, stem). Look at every PNG.
5. Schematics: invoke the skill `sleep-paper-figure-style`; with the project's paperfig.py draw (a)
   the track architecture with the status legend exists / to be ported / new, (b) the gate
   timeline with the current position. Look at the PNGs.
6. Working note: invoke the skill `paper-writing`; write or revise tracks/$track/note/main.tex and
   supplement.tex under its rules; run its manuscript checker with --compile and fix what it
   reports. Provenance (labels R1, R2, ... to run ids) goes to stage/$gate/PROVENANCE.md.
   If figures or tables changed in steps 4-6, commit and repeat step 3.
7. Spawn the `verifier` subagent with no context except the paths of the note, the manifests,
   PROVENANCE.md and the checklist; it writes stage/$gate/VERIFIER.md (decision 0016). Optionally the
   `figure-checker` subagent on note/figures/.
8. `harness/bin/nrpic-stage report $track $gate --decision "<the decision requested from the group>"`
   -> STAGE_REPORT.md with the verdict and the proposed tag.
9. Commit the package path-limited:
   `git add tracks/$track && git commit -m "<ID short>(note): stage $gate package" -- tracks/$track`,
   then `git push -u origin <your branch>`. The tag stage/$track/$gate-pass-<date> (or -fail-) is
   created and pushed by the orchestrator after its review (decision 0003): name it in step 10.
10. `harness/bin/nrpic-ctx post --to all --type info --slug stage-$gate --body "<one paragraph + paths
    + proposed tag>"`, rewrite STATUS.md, append to JOURNAL.md, then stop and wait for sign-off.
    No production runs for the next gate before the sign-off.
