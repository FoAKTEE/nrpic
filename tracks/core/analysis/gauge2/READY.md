READY of core/gauge-2 (source item gauge-2 of core, batch 4b of wave 3, 2026-11-21): the
relaxed lapse, second pass (decision 0022 item 3).
Evidence and every number: branch core/gauge-2, tracks/core/JOURNAL-gauge-2.md (entries 1
to 10) and tracks/core/interfaces/cosmo_gauge.md section 9 (git show core/gauge-2:<path>).
Scripts, lists, inputs, figures, numbers: tracks/core/analysis/gauge2/.

STATUS
  athena_cpu  processor executable (scripts/build_cpu.sh) of source commit 984110c3:
              TESTED (T7, byte regression; see below).
  athena_gpu  card executable (scripts/build_gpu.sh, CUDA 12.6, one A100) of the same
              source: see CARD CHECK at the end.
  The card tests of the option (Einstein-Straus 100 M, vacuum set-up, cause tests) ran
  with the card build of the earlier commit 90f52f4d, which also held two factors that
  were refuted and removed (below). The processor build of 984110c3 writes the bytes of
  the processor build of 90f52f4d on a run with the option active (T7).
Everything not named below behaves as release core-v0.6: output files of existing
set-ups are byte-identical when the new parameter is absent (regress_v04.py, twelve
set-ups, 75 of 75 items; first pass `lapse_leak` on the expanding ball L1: 17 of 17
files).

NEW OPTION
  <z4c> lapse_leak_hole = r_h   (absent or 0: off)
     d_t alpha = [1+log right-hand side] - (alpha/T) w_h(x) max(ln(alpha/alpha_0), 0)
     w_h = product over the compact-object trackers A of S(|x - x_A|/r_h - 1),
     S(s) = s^2 (3 - 2 s) for 0 < s < 1, 0 below, 1 above;   1/T = lapse_leak
  The relaxation of `lapse_leak` is switched off within r_h of every tracker
  (<z4c> co_<A>_type) and acts in full beyond 2 r_h. Without a tracker the option does
  nothing. A puncture without a tracker needs one: add to <z4c>
     co_0_type = BH
     co_0_x = 0.0      (co_0_y, co_0_z likewise: the position of the puncture)
  A parameter must stand in the input file to be changed on the command line.
  Why: on a slice whose vacuum has diverging normal observers around the hole (the
  bubble of Einstein-Straus data) `lapse_leak` holds the lapse of that vacuum just
  above 1 and so stretches its coordinates; the normal observers carry the stretching
  into the hole, the horizon shrinks in the coordinates (0.78 to 0.88 M after 200 M at
  T = 2 M) and its mass drifts late (Track D: +1.3e-3 in vacuum, +7e-3 with dust over
  100 to 200 M at cells M/8). The option frees the zone around the hole.
  Choice of r_h: 2 r_h inside the matter that needs the relaxation, r_h well beyond
  6 M (6 M does not help; 16 M is the tested value for Track D's bubble with its wall
  at 33 M in the coordinates).
  Example (Track D's Einstein-Straus data, make_es.py --Rb 56 --w_out 4 --hp 2.0):
     athena_gpu -i problems/es/es_gauge_hole.athinput -d RUN \
        particles/particle_file=ID/es.nrp problem/comp0_file=ID/es.tab
  (z4c/lapse_leak_hole=0.0 on the command line gives the first pass with the same file.)
  Example (the same slice in vacuum, reduced mesh; faces at 64 M reach the hole after
  50 to 70 M, see the header of the input for longer runs):
     athena_gpu -i tracks/core/analysis/gauge2/inputs/v8_var.athinput -d RUN \
        particles/particle_file=ID/v1.nrp problem/comp0_file=ID/v1.tab \
        z4c/lapse_leak_hole=16.0

  Tested (card build of 90f52f4d unless said; r_h = 16 M, T = 2 M, finest cells M/8):
  - Einstein-Straus data, 100 M: horizon radius 1.59, 1.61, 1.63, 1.65 M at 25, 50, 75,
    100 M (first pass, Track D's ES-1G: 1.40, 1.33, 1.18, 1.06 M); horizon mass 1.00085
    to 1.00129 over 40 to 100 M (wiggles of 2e-4 between 33 and 78 M while the lapse
    front of the freed zone dies out, flat afterwards; ES-1G 1.00098 to 1.00125,
    rising); wall tracers on the exact curve to 2.1e-4 (30 M), 4.3e-4 (60 M), 6.3e-4
    (100 M) (first pass on the same lattice 6.2e-5 at 30 M; plain 1+log 2.2e-3 at
    200 M in Track D's run); lapse in the dust within 1.2 per cent of the homogeneous
    model; largest lapse 1.62 at 15 to 20 M (inside r_h), 1.05 from 80 M.
  - the same slice in vacuum, reduced mesh, valid to 65 M: horizon radius 1.90, 1.39,
    1.59, 1.75 M at 20, 30, 50, 65 M (first pass 1.38, 1.42, 1.33, 1.24 M; plain 1+log
    2.06, 1.91, 2.04, 2.09 M); horizon mass within 8.2e-5 over 35 to 65 M (first pass
    8.4e-5, plain 1+log 1.7e-5).
  - r_h = 6 M (vacuum, 30 M): no better than the first pass (radius 1.44 M at 30 M).
  - without a tracker (expanding ball L1 to 10 M at cells 1 M, first steps of the bound
    ball L2 and of the collapse L3; processors): the bytes of the first pass.
  - a radius beyond the mesh (processors, coarse vacuum mesh): the bytes of plain 1+log.
  NOT tested: runs longer than 100 M on the Einstein-Straus data; other radii than 6
  and 16 M; more than one tracker; a moving hole; MPI; a tracker placed where a hole
  will form (collapse); see LATE DRIFT below for the vacuum run to 200 M.

TRIED AND REMOVED (in commit 90f52f4d, not in these executables)
  lapse_leak_rho (relaxation only where the matter density exceeds a threshold): plain
  1+log in vacuum byte for byte, but wrong next to matter: bound ball L2 shell errors 3
  to 47 times the first pass, collapse L3 turnaround at 1.32 to 1.35 R_0 (exact 1.25)
  and horizon mass 3 per cent high, Einstein-Straus wall off by 6e-2, horizon mass
  swinging by 4e-3. lapse_leak_onset (smooth onset of the term): no effect on the
  defect. Inputs that carry these lines run unchanged (the parameters are not read).

LATE DRIFT (vacuum, 200 M; card job F, card build of 984110c3, faces at 256 M)
  Horizon mass, drift from its value at 100 M over 100 to 199.5 M:
     plain 1+log (Track D's V-1B)        [-4.8e-5, +2.0e-5]   radius 2.15 to 2.20 M
     first pass (Track D's V-1GB)        [-5.6e-4, +1.26e-3]  radius 1.09 to 0.875 M
     lapse_leak_hole = 16                [0, +2.08e-4]        radius 1.64 to 1.31 M
  With the option the mass has transient wiggles of up to 2e-4 until 116 M and is then
  flat within 4.4e-5 to 199.5 M, 2.5e-4 above the control. The horizon radius is steady
  near 1.6 M until about 110 M and then falls again, at -3.5e-3 per M at the end: the
  option delays the shrinking by about 100 M, it does not stop it. It is a mitigation
  for runs of up to about 200 M at cells of M/8 (10 cells in the horizon radius at
  200 M instead of 7), NOT a cure: the level of plain 1+log is not reached.
  Cheapest set-up that shows the defect in the mass: the vacuum set-up at finest cells
  M/4 (refined_region1/level=4 with the faces at +-128 M), 100 M, 4 minutes on a card:
  first pass 3.1e-2 against 1.7e-3 for plain 1+log (largest minus smallest, 40 to 99 M).

CARD CHECK
  athena_gpu (984110c3) ran card job F (run core-20261121-190709-8b205e5: the 200 M
  vacuum run with the option, and plain 1+log and the first pass at M/4), all exit 0.
  It did not rerun the Einstein-Straus test; that ran with the card build of 90f52f4d
  (kept: scratch/core/gauge2/exe/athena_gpu_90f52f4), whose processor twin writes the
  same bytes as athena_cpu here with the option active.
  Card time of the item: 1.49 card-hours (jobs A 0.32, B 0.68, F 0.49).
