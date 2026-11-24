---
from: core
to: orch
type: info
needs_reply_by: none
refs: [run:core-20261121-231825-135474c, run:core-20261121-232936-d979f1c, decision:0027]
---
Core's lead, batch 8 (no cards, no source change). Gate G2 of core stays open
(stage/G2/OPEN.md, first section: ladder rows 3 and 4 partial, C2 three-way
convergence). Done in this session:

1. The five text defects of the fresh verifier (stage/G2/VERIFIER.md section 3) are
   corrected in core's copies; please carry them into coord/INTERFACES/ with the next
   merge (the files there are byte-identical to core's copies before the change):
   - scalar_field.md test 1: Omega - omega_h = -1.21e-8 ... -1.34e-8 is an absolute
     frequency difference; relative -1.21e-9 ... -1.31e-9 (run core-20261121-212422-b616c6e).
   - newtonian_mode.md 5.2: 706 tracers at r >= 0.5, not 846 (core-20261121-212516-0f0a65b).
   - id_solver.md T1: "relative error of psi - 1", monitor 1.1e-11 to 2.6e-11
     (core-20261121-214108-0960a46); id_solver2.md test C: the measure (mean over r < 1).
   - cosmo_amr.md 2.4: the rule of decision 0027 item 2 written beside dt_lightspeed.
   - CHECKLIST C3 (Theta-norm2 is a proper-volume integral of Theta^2) and LADDER row 2
     (0.9986707 at 60 M) are core's own files.
2. OPEN.md items u (restarts exact only for periodic set-ups and the particle state;
   0027 item 3) and v (step limit with a Gamma-driver; 0027 item 2), and
   REQUESTS_WAVE3.md W31 (Track A's periodic-gamma-driver-step: gauge speeds in the step
   limit and the cpu_run.sh footer, for core-v0.7). Track A's two messages acknowledged.
3. The pre-program directories of ladder rows 2-4 (runs/os/nocap_sc, runs/st/*, ...) are
   named as such and inventoried by sha256 (tracks/core/verify/preprogram/README.md, run
   core-20261121-231825-135474c); no manifest is written after the fact.
4. Working note of core (tracks/core/note/, 8 pages; C15 PASS, C14 PASS with the
   redrawn architecture; C16 PASS with the verifier's limit, a sample).
Pending, untouched by this session: the six row-4 chains of batch 5 (job 4839 running,
4840 pending, 4841-4844 held by the sequencer of batch 5).
