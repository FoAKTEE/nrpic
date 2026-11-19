---
from: E-stoch-inf
to: orch
type: info
needs_reply_by: none
refs: [file:tracks/E-stoch-inf/stage/G0/CHECKLIST.md, file:tracks/E-stoch-inf/stage/G1/STATUS.md, file:tracks/E-stoch-inf/stage/REVIEW-wave2.md]
---
Information on the stage packages of E-stoch-inf after wave 2b (lead, 2026-11-19).

G0: every checklist item is PASS or NA (`tracks/E-stoch-inf/stage/G0/CHECKLIST.md`,
re-collected today): verifier report `VERIFIER.md` present and its computations rerun
identically (run E-20261119-150346-a513bc8); the decision is decisions 0013/0017; the cost
is measured (0.503 card-hours per SR realisation at 256^3, run E-20261115-172618-f948386).
The package is complete for your review under decision 0016 item 4. `nrpic-stage verify`
results are in `stage/G0/VERIFY_RESULTS.md`; a `runs` or `clean` failure there comes only
from the wave-3a package `usr/` of this worktree (run E-20261119-145835-67cde45 in flight).

G1: not met and not complete for review. Spectrum (A2) and freezing (A3) are met; the
constraints converge, but the owner's A4 fails in its strict form in P1's set-up (proposal
a4-a5-rewording of today); missing: a verifier of the G1 material (request g1-verifier),
updated architecture and data-flow schematics, the G1 sections of the note. All SR evidence
is from scouting runs with core's tested-branch executable (decision 0013). Details:
`stage/G1/STATUS.md`, `OPEN.md`; review `stage/REVIEW-wave2.md`.
