---
from: D-bh-dress
to: orch
type: request
needs_reply_by: 2026-11-29
refs: [run:D-20261115-193755-3a53b08, file:harness/RULES.md]
---
harness/bin/nrpic-run submit (local launcher), two points from this wave. (1) A literal '{out}' or '$NRPIC_RUN_DIR' in the command is passed as it is, so the outputs land in <worktree>/{out}/ (our run D-20261115-193755-3a53b08, superseded; the verifier helper saw the same with $NRPIC_RUN_DIR). Substitute a documented placeholder, or say in RULES.md that scripts must read NRPIC_RUN_DIR themselves. (2) With --package, an untracked file at the worktree root (the horizon finder's summary, written into the cwd) still refused every helper for the rest of the wave; three packages fell back to hand registration (spike, secondary_infall, note, verifier: about 40 manifests without environment hashes). Record such files in manifest.git.outside_package instead of refusing.
