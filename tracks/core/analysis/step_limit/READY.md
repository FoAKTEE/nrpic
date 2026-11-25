READY: executables of branch core/step-limit (core, batches 11 and 13, 2026-11-24)
==================================================================================
athena_cpu (serial), athena_cpu_omp (threaded), athena_gpu (one A100): release core-v0.6
plus two items for release v0.7. Source commit, build lines and checksums: COMMIT,
SHA256SUMS. Interface texts (what, why, every test with its run id):
  tracks/core/interfaces/step_limit.md      step limit of the gauge sectors
  tracks/core/interfaces/preempted_runs.md  restart file on SIGTERM, chain script
Journal with predictions and outcomes: tracks/core/JOURNAL-step-limit.md (branch
core/step-limit). No output file of a run changes when the option is absent and no
signal arrives: byte regression against core-v0.6 PASS, 75 of 75 items, with the final
serial build (run core-20261125-000250-6dc7307).

1. New option
-------------
<z4c> dt_gauge = f      (real; default 0 = off; needs integrator rk3 or rk4, three dimensions)
    Every cycle the step is kept at or below f times the stability bound of the scheme
    for three pairs of fields, evaluated in every cell: the Gamma-driver shift, the lapse
    (1+log, harmonic, with the relaxation lapse_leak), and the pair of conformal factor
    and Theta. It bounds the step itself at any cfl_number and does nothing where the
    step is already smaller. Use f = 0.9 (rk4, nghost 4).
    To set it on the command line the input must declare it (dt_gauge = 0.0 is off).
  Example input:  problems/tests/z4c_step_limit.athinput
      athena -i problems/tests/z4c_step_limit.athinput                    stable, step 0.421 cells
      athena -i problems/tests/z4c_step_limit.athinput z4c/dt_gauge=0.0   warning, guard stop at cycle 9
  Messages: "Z4c step limit: dt_gauge = 0.9 keeps the step ... Gamma-driver shift B1,
  lapse B2, light B3" at start-up (bounds in units of the smallest cell; "light" is the
  pair of conformal factor and Theta), and one line the first time each sector sets the
  step.

2. Acts without an option
-------------------------
a. Warning at start-up (log only, no output file changes) when cfl_number and the gauge
   allow a step above a bound: "### WARNING (Z4c step limit): cfl_number x (smallest
   cell) = ... exceeds the stability bound ... for the sector ...; Set <z4c> dt_gauge =
   0.9, or cfl_number at or below X", and a second line when lapse_leak x that step is
   beyond the bound of the relaxed lapse (2.785 for rk4, less at the grid scale).
b. SIGTERM (preemption, scancel, time limit of the batch system): the run finishes the
   cycle in progress, writes its restart outputs (file_type = rst) and nothing else,
   prints "Terminating on signal SIGTERM", and exits with status 143. Continue with
   athena -r rst/<newest>.rst. Before, the run died at once and wrote nothing.
   Examples: problems/tests/term_signal_periodic.athinput, term_signal_particles.athinput
c. scripts/submit_chain.sh (of this branch; it reaches the tracks with the merge into
   main): an attempt cut by a signal before ATHENA_WALL does not count against
   MAX_SEGMENTS; the job waits for the executable to write its restart file; no job is
   queued after the last segment; MAX_TERM_IN_A_ROW (default 20).

3. What the bounds are (cells; rk4, nghost 4, diss 0.5)
-------------------------------------------------------
flat space (lapse 1, conformal factor 1): 1+log lapse 0.468; conformal factor and Theta
0.554 (binds with a frozen or harmonic lapse); Gamma-driver shift_Gamma 0.75: 0.660,
1.0: 0.594. Track A's expanding box (lapse 1.06, chi 0.12, shift_Gamma 0.75, eta 2):
shift 0.658 on level 4 and 0.625 on the 64-cell root (Track A's analysis: 0.685, 0.65;
the code takes the second-derivative stencil where its model takes the product of two
first derivatives); lapse with lapse_leak 20: 0.967 and 0.404; lapse_leak x step <= 2.52
at the grid scale of the root mesh. The rule "cfl_number <= 0.6 with a Gamma-driver"
(decision 0027) holds there with 4 per cent of margin and fails in flat space.

4. Tested (runs under scratch/core/<run id>/; all on processors)
----------------------------------------------------------------
Step limit, builds of source 476fe0c (the final builds reproduce them byte for byte with
the limit binding: F1, run core-20261125-003154-965cb92):
- bounds of the kernel against the Python twin to 2.4e-6 cells; each bound bracketed by
  runs of the code: stable at 0.93 and 0.97 of the bound, unstable at 1.03 and 1.07,
  stable at 1.07 with dt_gauge = 0.9 (shift, 1+log lapse, frozen and harmonic lapse)
  [core-20261124-140144-47691db]
- Track A's uniform-mesh reproducer at cfl_number 1.0: without the option the onset of
  growth at t = 8.72 (lapse frozen) and at t = 3.18 with a guard stop at t = 10.76
  (relaxed lapse); with dt_gauge = 0.9 smooth to t = 12 in both, steps of 0.56 and 0.32
  cells [core-20261124-233050-ae129ee, core-20261124-233103-faf1f5b]
- cost of the bound per cycle: 1 per cent, inside the scatter [core-20261125-001339-5005deb];
  cost in steps: 77 against 84 of a fixed cfl_number 0.5 (frozen lapse), 124 against
  131 of 0.3 (relaxed lapse)
- east, os, c4 of the regression with dt_gauge = 1.0: histories byte-identical, the
  limit never sets the step [core-20261125-003008-668d147]
Stop on SIGTERM, final builds:
- serial: signal part-way, continuation from the restart file written on the signal,
  comparison with the uninterrupted run: periodic box without matter, the same with
  two signals, with the signal during the set-up, particles coupled to Z4c (two stop
  cycles). State identical bit for bit (data of the last restart file, .prt companion),
  every output file byte-identical but two that any restart changes: the header lines
  of the mesh history are repeated, and *.cons.hst loses one record when the
  continuation starts one or two cycles before it is due (the release does the same)
  [core-20261124-234903-61e194c]; threaded build, one thread, the same
  [core-20261125-003452-288cbda]
- 256^3 cells of Z4c: restart file of 4.2 GB written in 3.2 s; the grace period of the
  batch system is 30 s (KillWait; GraceTime 0) [core-20261124-235925-5ee2c95]
- chain script with fake sbatch and fake executable: 58 checks [core-20261125-000640-5c4b644]

5. NOT tested
-------------
- No run of athena_gpu at all yet. The card job q0036 of the shared queue (Track A's
  refined periodic deck at cfl_number 1.0 without and with dt_gauge, and at 0.5) is its
  first; until tracks/core/JOURNAL-step-limit.md reports it, a track that uses
  athena_gpu runs it first on a short deck of its own.
- Track A's refined periodic deck (four levels) with dt_gauge = 0.9 through the time of
  its failure: the processor run was at t = 0.9 of 3.0 when this was written (run
  core-20261124-233029-c745838, 30 s per cycle on three threads); the last entry of the
  journal says how it ended.
- SIGTERM: several MPI ranks; a card; refinement (.amr) and scalar field (.sf)
  companions; asymptotically flat set-ups; a real preemption by Slurm.
- Step limit: punctures, horizons, shift_eta_profile, rk3, nghost 2 and 3 in runs of the
  code; adaptive refinement; several ranks.
