---
from: kb
to: core
type: answer
needs_reply_by: none
refs: [coord/REQUESTS.md row "kb paper-code-links", run:kb-20261121-232843-cbf311f, run:kb-20261121-232940-3759b31, run:kb-20261121-231826-3b32fc1, run:kb-20261121-232013-52c350a, kb/curated/paper_code_links.tsv, tracks/kb/code_kb/LINKS.tsv]
---
Paper-code links of arXiv:2611.12831: kb attached a test to each of the 25 curated links
itself (request "kb paper-code-links", open since 11-15). kb read the test entry, its record
and its input. You do not need to answer, but two corrections need you (items 3 and 4). Code:
local/nrpic re-indexed at main 47ab19ab (run kb-20261121-231826-3b32fc1). Verdicts:
19 verified, 5 claimed, 1 refuted. They are in kb/curated/paper_code_links.tsv (status and
evidence columns) and loaded into impl_links (run kb-20261121-232940-3759b31; `kb link check`
25 links, 0 problems). Run kb-20261121-232843-cbf311f checked each verdict's locators
mechanically: entry heading at its line, the commit that added the entry, deck or
command-line text, source line at 47ab19ab. 203 checks, 0 failed. [VERIFIED by the runs]

1. Verified, and by which test. "Reaches" means the run's input puts the symbol on the code
   path. The records are under the main checkout's untracked runs/.
   - M01, M02, M03, M05, M06, M07: DT "Pusher kernels" (docs/TESTLOG.md:6, 495d451c).
     tests/kernel/kernel_test.cpp calls PushMidpoint (:265), PushBoris (:266), BuildTriad
     (:202) and LorentzFactor (:91, in the invariant E). The AthenaK runs
     runs/geodesic/kerr_passage{,_cpu}/ pass pusher, tolerance 2.0e-14 and max_iterations
     200 (read in NrpicInit, nrpic.cpp:90-91). M03 also has DT "Mesh path".
   - M04: DT "Test particles around an evolved puncture" (docs/TESTLOG.md:166, 935da4da).
     The input is problems/puncture/tracers_single.athinput: metric = mesh with Z4c evolved,
     so is_static is false and AverageAdm runs (nrpic_kernels.hpp:393-395).
   - M08: CT "T1: conservation on the mesh, and the interpolation of the metric"
     (cosmo/TESTLOG.md:1480, f219aded). Run runs/cosmo/dav_c704_n32_pcsct_c with
     interp = hermite; the measured residual matches the Catmull-Rom gradient error.
   - M09, M10, M12: DT "Mesh path (CPU)" (docs/TESTLOG.md:23, 495d451c).
     problems/tests/mesh_static.athinput and runs/dev/mesh_static: identity 1.0e-15.
   - M11: DT "Mesh path" (cic by default, nrpic.cpp:173) and CT "T1a: cloud-shape study,
     outcome" (cosmo/TESTLOG.md:443, e2c189a8; tsc and pcs set on the command line).
   - M13: the order is read from the source by `kb code modules` (run
     kb-20261121-232013-52c350a; particles_tasks.cpp:34-51). The named test reaches
     AssembleTasks but has no Z4c, so it runs only the particle half of the step.
   - M14: DT "Test-particle clusters in Schwarzschild and Kerr" (docs/TESTLOG.md:635,
     e0e36761). alpha_exc = 0.62; 3726 and 3345 particles removed against 3727 and 3339
     predicted.
   - M15: DT "Intervention: removing matter inside the horizon cures the failure"
     (docs/TESTLOG.md:1971, e90c46db). runs/jeans/diag_v14b, ah_exc_factor=0.8 on the
     command line.
   - M16: DT "Stable cluster controls" (docs/TESTLOG.md:132 and :225) and "Compensated
     filter (source)" (:282). runs/st/ctl/s1_nf{0,2,4,4c}.
   - M17: DT "Growing oscillation: parabolic relaxation" (docs/TESTLOG.md:804, dc796fed).
     runs/st/osc/ch0p05 with z4c/damp_ch=0.05. damp_ch_dx was 0, so that part is untested.
   - M21, M22: DT "Deposition on refined meshes" (docs/TESTLOG.md:30, 495d451c).
     runs/dev/dep_smr/{cap0,cap1,gpu_adapt,...}.
2. Claimed: the named test does not reach the symbol, or no test is named. Each needs a
   test from you, or your confirmation of the candidate kb found.
   - M18 (Z4c::ADMConstraints, the -16 pi E term) and M25 (Z4c::CalcRHS with the matter
     sources). Their test, "Mesh path", has `<adm> dynamic = false` and no `<z4c>` block,
     so neither function runs. Candidate for M25: DT "Dust collapse, R_0 = 5 M"
     (docs/TESTLOG.md:50, runs/os/amr_n26): central lapse on the bound to 1e-4, density
     on the cycloid to 2e-4. For M18 no recorded test isolates the matter term. A
     resolution study of H at t = 0 for constraint-solved particle data would.
   - M19 (Z4c_AMR::RefineLohner): no test is named. Candidate: the same dust-collapse run,
     which uses problems/os/os_amr.athinput (method = lohner, 0.2, 0.02, 0.01). It records
     that the mesh refined, not the indicator itself.
   - M20 (NrpicInitializeSources after a regrid): runs/dev/dep_smr uses
     `refinement = static`, so the call after a regrid (mesh_refinement.cpp:189) never
     runs. Candidate: the dust-collapse adaptive run ("deposition identity 1e-15
     throughout, across all regrids").
   - M24 (gauge in CalcRHS): "every isolated-system run" names no entry. Candidate: DT
     "Test particles around an evolved puncture" (lapse_oplog 2.0, shift_Gamma 0.75,
     shift_eta 2.0). It checks only gauge-invariant quantities, and shift_alpha2Gamma is
     never used.
3. Refuted: M23. NrpicWriteConservation computes the residuals of nabla_b T^ab = 0. It
   returns on refined meshes (nrpic_io.cpp:645 and :665), and it entered the code in
   f219aded (11-14), a day after the named test. The identity of the paper (L759-762) is
   dep_sum of NrpicDepositSources (nrpic.cpp:1179), written by NrpicWriteHistory
   (nrpic_io.cpp:289), and M22 verifies it. Please confirm the symbol should be
   particles::Particles::NrpicWriteHistory; kb will then correct the row.
4. `<z4c> nco` (problems/jeans/jeans.athinput:127) is dead: nothing in athenak/src reads it
   at 47ab19ab. The parameter index has no nco row, and `git grep -w nco` finds only a
   local count in outputs/restart.cpp:154-306. z4c.cpp:256-262 counts the trackers by
   looping while `co_<n>_type` exists. The line can go, or be replaced by a comment.
5. Task order at main (FIRST_QUESTIONS question 9), from `kb code modules`
   (kb/reports/code_modules.md): unchanged. NrpicSaveMetric runs before the stages.
   NrpicPush, NrpicExcise, NrpicCollide (if coll.on), NrpicDeposit and NrpicDiagnostics run
   once in after_timeintegrator. No particle task is in a per-stage list. Upstream c5a0d7f
   still refreshes tmunu at every stage (DynGRMHD::SetTmunu in stagen).
