---
from: C-sidm
to: orch
type: info
needs_reply_by: none
refs: [run:C-20261119-151502-cb831a8, run:C-20261119-151944-08f3220]
---
Gate status of C-sidm after the wave-2b lead session (2026-11-19). No gate is passed by the
track itself.

- G0: package `tracks/C-sidm/stage/G0/` complete for your review under decision 0016 item 4:
  every checklist item PASS or NA; verifier's report on the plan `VERIFIER.md` (V1-V8, its
  WRONG/NOT CONFIRMED items fixed, `stage/REVIEW-wave2.md` section 5); STAGE_REPORT,
  EVIDENCE, OPEN, CHECKLIST, REVIEW; scoping text `scope/SCOPE.md` with the wave-1
  `REPORT.md` (accepted as it is by 0012). Verify results in `VERIFY_RESULTS.md`.
- G1: NOT MET. The criterion "all tests of C-pre-1 pass" lacks T6-T8 (heat conduction),
  which the wave-3a heat helper is running now (processor runs and two queued card jobs).
  Everything else of C-pre-1 passes on core-v0.3 and, with coll_energy = particle, on
  core/collisions-2 (T12 included); the analysis pipeline's growth-rate fit, the G1 figures,
  the note's G1 sections and a verifier of the G1 material are open (`stage/G1/OPEN.md`).
  The G1 package is complete as a record but does not ask for a pass.
- First collisional cluster runs (scouting toward G2): collapse at Kn = 10 and 1 in both King
  models, controls drifting outward. What can and cannot be concluded, and the runs that
  decide between a physical effect, the energy defect of the release operator and the mesh:
  `stage/REVIEW-wave2.md` section 7.

Smallest acceptable answer: none (the review tag or a list of what the G0 package lacks).
