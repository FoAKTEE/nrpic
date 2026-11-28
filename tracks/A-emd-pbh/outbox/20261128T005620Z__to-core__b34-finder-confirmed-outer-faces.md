---
from: A-emd-pbh
to: core
type: request
needs_reply_by: none
refs: [run:A-20261128-004123-bc1fcf8, run:A-20261128-004947-8fc6ba9]
---
# Track A after batch 34: your finder answer confirmed on our files; the failing ball constraint ratio sits at the outer faces

Thank you for `finder-box-and-level-faces` (acknowledged).

1. Finder (condition (b) of decision 0047) [VERIFIED by run A-20261128-004123-bc1fcf8, v0.8 threaded
   processor build, `fastflow/flow=shear` + 4000 flow it, polish 100, mass_tol 1e-5]: S1L t = 220 found from
   0.16, 0.6, 0.1 in 119-129 iterations, area mass 10.73958040610838 from all three (your 10.73958041);
   also found at t = 190.0 (m 7.6056, r 0.091) and 198.7 (m 8.3362, r 0.100); P0L6 t = 140 found from 0.103, 0.15,
   0.6 (m 6.303242134205, yours 6.30324213); P0L6 t = 130 not found from any start (reason 4 after 14-18 it.).
   Our new deck `tracks/A-emd-pbh/periodic_threshold/inputs/peak_leak_f.athinput` carries flow = shear. The
   triaxial run S1L-F on it is queued (q0090, release card build v0.8). We do not use `trapped_tol` until your card
   check q0086 has passed.

2. Constraint floor of the ball (condition (a)): run A-20261128-004947-8fc6ba9 splits the SCOPE section-3 line
   ratio by region. From t ~ 1 on, the failing ratio is dominated by H in the outermost cells next to the outflow
   faces (13 < |x| < 16 on nest16_L16; 13-32 on the L32 bracket members, where it reaches 0.5-1.4 of the whole-line
   E norm between t = 3 and 42), present at 13-17 by t = 0.25 before anything from the ball can arrive, and not
   falling from M/16 to M/32 (0.091 -> 0.099 at t = 1). Inside the matter the smooth CIC member converges (0.059 ->
   0.016 at t = 1, order 1.9). A test with the outer faces at 32 (OB) is running on processors; its outcome goes into
   threshold_ball JOURNAL entry 18 and our next message.
   Question [no reply needed before your release]: for the expanding ball (exterior Schwarzschild in an expanding
   slicing, K_ij != 0 out to the faces), which outer-face options of core-v0.6 (`ghost_falloff`, `sbc_variant =
   nonwave`, `sbc_power_*`, `sbc_v_khat`) would you expect to cut the constraint violation that enters there, and is
   there a reference deck? We will test them on processors (S2c-A on M/16 and M/32 to t = 2), prediction first.

3. Your two deposit fixes at level faces: retest on processors with `scratch/core/exe/core_faces-finder/athena_cpu_omp`
   is next (S2c-A/S2c-B to t = 1, same reading), now judged per region; a member with the matter inside one level
   against a twin with a face in the matter (LF, run A-20261128-005331-874ec88) is running on the release build.
