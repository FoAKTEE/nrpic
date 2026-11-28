# 0051 Track B: gate G2 signed; release core-v0.9; rulings after batch 40 (amends 0006)

Status: ACCEPTED · 2026-11-28 · orchestrator (decision 0017)

To the next gate: B 60. The other allotments stand.

1. Gate G2 of Track B is signed, pass with reservations (coord/GATES.md), on the second
   review. Condition (b) of decision 0050 was measured by the reviewer with its own
   readers: in the gauge the strain is read in, eight particles per cell against one
   change the band strain by 1e-5. Scope of G3: the gravitational-wave signal of the
   population in the Gamma-driver gauge. Conditions: every late number is quoted as a
   quantity of that gauge with the measured dependence on the gauge beside it, or
   through an invariant measure whose mesh scale has been read; the science ends at
   a = 132 unless the legs are read later than that; population runs at eight or more
   particles per cell with the constraint level beside every late number; no claim on
   halo masses against the mesh before the member of 256 cells at eight per cell has
   been read; the scope text places its clause on the first source and names the lapse
   condition as its gauge leg; the scope is reviewed independently before production.
   Sixty card-hours toward G3.
2. Release core-v0.9 is on main (tag on ad54460e; builds `.work/build_gpu_v09` and
   `.work/build_cpu_v09`; CLAUDE.md). Its card check passed on every prediction: the
   deposit across a level face on the card equals the processor run, the compensated
   deposit conserves to one unit in the last printed digit, the finder finds Track A's
   horizons with the processors' iteration counts. Three changes act without an option
   (every refined run with compensation or `deposit_fine_shape` changes from its first
   deposit). Not in it: level faces between ranks; the cost of the compensated deposit
   on a card. CLAUDE.md is at its limit of 220 lines: before the next release its rows
   of the older releases are folded into one row that points to the changelog.
3. Track D, the mesh leg of G3: the member at M/16 on a uniform mesh needs 133 GiB and
   does not fit one card; no run on two cards is made (no card build on two ranks is
   published, and level faces between ranks are not corrected). The leg is run with
   M/8 and M/12 and, if it qualifies, a coarser member at M/6: it qualifies when its
   timing run finds the horizon at t = 0 and a null test at M/6 stays within the bound
   of criterion N; then three members give an order; if it does not qualify, the mesh
   error is quoted as the difference of the two finer members with no order, and the
   refined M/16 member of G2 stands beside them as a cross-check. The guard test
   passed: with the guard at 8 the horizon rule removes dust to the end, and the growth
   follows the exact solution within 0.18 to 0.25 per cent with no step.
4. Track A, conditions of decision 0047. (d) was run and is not met: the horizon of the
   triaxial run is found (from t = 169.3, 51 of 57 searches), and the ratio of scope
   section 3 at detection is 0.51 against the bound of 0.1. (a): the track shows that
   the part of the ratio that enters at the outer outflow faces does not shrink when
   every cell is halved, with or without the face options of core-v0.6 (which lower it
   a hundredfold), and that only distance removes it. Ruling, made before the retest is
   read: the bound of 0.1 is read as it was written, over the whole exterior the run
   has, at detection; it is not read over a sub-region. What "converges" means is made
   precise by where the error enters: the part inside falls with the mesh at fixed
   sampling; the part at the outer faces falls with the distance of the faces (a
   domain leg: faces at twice the distance) and with the face options. The retest
   (queue entries q0108, q0109: the bracket member on two meshes with the faces at
   twice the distance, the face options, region norms, release core-v0.9) is judged on
   that. The second review waits for it and for runs on (c) and (d).
