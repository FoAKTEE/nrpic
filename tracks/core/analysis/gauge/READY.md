READY of core/gauge (work package "gauge" of core, waves 2 and 2b): gauge conditions for
expanding matter and for black holes of unequal mass. Written 2026-11-15; rewritten
2026-11-19 when the package closed (every test analysed; no change of the source).
Evidence and every number: branch core/gauge, tracks/core/JOURNAL-gauge.md (entries 1 to
9) and tracks/core/interfaces/cosmo_gauge.md section 7 (git show core/gauge:<path>).
Scripts and figures: tracks/core/analysis/gauge/ (figs/).

STATUS
  athena_cpu  processor executable (scripts/build_cpu.sh) of source commit b4430da:
              TESTED (L1, L2, P, E1, E2, H and the byte regression R below).
  athena_gpu  card executable (scripts/build_gpu.sh, CUDA 12.6, one A100) of the same
              source: TESTED on a card (L1, L2, L3, ES, P, E1, E2).
  The executables and COMMIT are those published on 2026-11-15: athenak/src of the
  branch has not changed since b4430da.
Everything not named below behaves as release core-v0.3: output files of existing
set-ups are byte-identical when the new parameters are absent (regression R: geo,
boris, dep, east, os, and a binary puncture with trackers and horizon finder).
Both new terms are read only if their parameters are present in <z4c>; an input must
declare a parameter to change it on the command line (AthenaK accepts on the command
line only parameters that the input file has).

NEW OPTIONS
1. <z4c> lapse_leak = 1/T  (absent or 0: off), lapse_leak_alpha = alpha_0 (default 1)
     d_t alpha = [1+log right-hand side] - (alpha/T) max(ln(alpha/alpha_0), 0)
   The excess of the lapse over alpha_0 relaxes on the time T. Where matter expands the
   1+log lapse no longer grows as 1 + 6 ln a (alpha = exp(6 T H) instead), so no lapse
   front runs inward from a sharp surface; where the lapse is at or below alpha_0
   (collapse, black holes, a puncture alone) the condition IS plain 1+log.
   Choice of T: T <= 0.1 R/sqrt(2 alpha) for the smallest expanding region of radius R
   that must be followed (balls of 5 to 10 M: T = 0.25 to 0.5 M), and lapse_leak x dt
   below about 2.7 (dt = the global step). T down to dx/8 ran without loss.
   Example (expanding dust ball; initial data problems/ic/make_ball.py):
     python3 problems/ic/make_ball.py --Rb 10 --h 0.5 --out ID --prefix ball
     athena_cpu -i problems/ball/ball_leak.athinput -d RUN \
        particles/particle_file=ID/ball.nrp problem/comp0_file=ID/ball.tab \
        particles/traj_ntrack=<traj_ntrack of ID/ball.json>
   (z4c/lapse_leak=0.0 on the command line gives the old 1+log with the same file.)
   Example (bound ball through its collapse to a black hole, card):
     python3 problems/ic/make_ball.py --Rb 5 --e0 0.16 --RE 10 --h 0.25 --out ID --prefix b
     athena_gpu -i problems/ball/ball_collapse.athinput -d RUN \
        particles/particle_file=ID/b.nrp problem/comp0_file=ID/b.tab \
        particles/traj_ntrack=<traj_ntrack of ID/b.json>   [refined_region3/level=5]
   Tested:
   - L1 marginally bound ball R_b = 10 M, cells 1 and M/2, t = 10 M: areal radius of the
     core shells against the exact solution at their proper time 1.2e-3 (T = 1 M,
     cells M/2) against 7.7e-2 with the old 1+log (which does not converge); central
     lapse within 0.2 per cent (T = 0.5 M) and 2.8 per cent (T = 1 M) of its homogeneous
     value, no front; coordinate light speed at the particles 1.13 instead of 2.32.
   - L2 bound ball R_b = 5 M to its turnaround, cells M/4: shell errors 9.2e-3 (core) to
     2.5e-3 with T = 0.5 M, against 0.11 to 1.3e-2 with the conformal-time lapse of wave
     1; turnaround at 1.248 to 1.250 R_0 (exact 1.25). T = 1 M is too long for this
     ball (a 20 per cent dip of the central lapse at t = 4 M, core error 3.3e-2).
   - L3 the same ball through turnaround and collapse to a black hole, T = 0.5 M, static
     mesh, cells M/8 and M/16 at the centre, 45 M (card): apparent horizon from
     t = 29 M (cells M/8) and 28.25 M (M/16) on, found in every later search,
     mass 0.9980 to 1.0003 (M/8) and 0.9994 to 1.0006 (M/16; 0.99997 at 44.5 M), exact 1;
     plain 1+log: 0.9964 to 1.0002. The hole is three times smaller in coordinates than
     with plain 1+log (horizon radius 0.73 M against 2.34 M), so give the centre cells
     of M/16 or finer with a matching particle lattice: at M/8 the central lapse stays
     at 0.074 and the surface shells are 3.6 per cent slow near R = 2.5 M (largest 12.7;
     plain 1+log largest 10.1); M/16 halves both. The shells of the interior follow the
     exact solution 4 to 7 times better than with plain 1+log at M/8.
   - P one puncture, cells m/8, 10 M (processors) and 20 M (card, full mesh): identical
     byte for byte to plain 1+log (the lapse never exceeds 1); Track D's 500 M puncture
     run never had a lapse above 0.9972, so it is what lapse_leak gives.
   - H homogeneous dust universe (periodic, t = 2/H_0): lapse and scale factor follow
     the exact ordinary differential equation of the condition to 6e-6 (T = 0.2/H_0) and
     5e-8 at the end (T = 0.05/H_0, 1.6 steps; 2.1e-4 in the first three steps, 5e-7 with
     a four times smaller step).
   - ES Track D's Einstein-Straus data (M = 1, wall at 36 M), T = 2 M, 30 M (card):
     horizon mass 0.99997 at t = 10 M, drift 1.0e-3 to t = 30 M (the same drift as the
     vacuum puncture alone on the same cells); wall on the exact curve to 6e-5; lapse in
     the dust 1.04 to 1.06 (plain 1+log would reach 2.37); largest lapse 1.11, in the
     vacuum bubble; lapse at the puncture 0.03 to 0.05 after a start-up bump to 0.23;
     no dust enters the bubble.

2. <z4c> shift_eta_profile = true (absent: false), shift_eta_mref = M_ref (default 1),
   shift_eta_width = w (default 2), shift_eta_width_local (default false)
     eta(x) = shift_eta [1 + sum_A (M_ref/m_A - 1)/(1 + |x - x_A|^2/(w m_min)^2)]
   over the compact-object trackers A that have a mass <z4c> co_<A>_mass > 0 (written by
   <problem> puncture_setup = true; at most 8), x_A their current positions, m_min the
   smallest of these masses (with shift_eta_width_local = true: w m_A). eta tends to
   shift_eta M_ref/m_A at hole A and to shift_eta far away: with shift_eta = 2 and
   M_ref = 1 every hole gets eta m_A = 2 in its own units. This is the profile of
   arXiv:2611.12831 (text below its shift equation, width 2); the paper's same factor
   on kappa_1 is NOT implemented.
   Example (unequal Bowen-York pair, mass ratio 4):
     athena_cpu -i problems/puncture/by_unequal.athinput -d RUN
   (z4c/shift_eta_profile=false gives the constant eta of release core-v0.3.)
   Example (one hole, damping set in units ten times smaller than its mass):
     athena_cpu -i problems/puncture/by_eta.athinput -d RUN \
        z4c/shift_eta=20.0 z4c/shift_eta_profile=true z4c/shift_eta_mref=0.1
   Tested (processors on a small mesh and a card on the full mesh; the tracker speeds
   agree to four digits between the two):
   - E1 one boosted hole, t = 5 m: far-away eta m = 20 brought to 2 at the hole by the
     profile: tracker at 0.55 of the speed with eta m = 2 (width 2), 0.86 (width 8);
     0.22 without the profile. Far-away eta m = 0.2 raised to 2: 1.27 (width 2), 1.04
     (width 4), 1.02 (width 8); 1.97 without. Horizon masses unchanged (1e-5).
   - E2 pair m = 1 and 0.25 (shift_eta = 2, M_ref = 1, width 2), t = 4 M: heavy tracker
     equal to the eta = 2 run within 0.8 per cent; light tracker 22 per cent faster than
     with constant eta = 8 (36 per cent with constant eta = 2); both horizons found in
     every search, masses unchanged to 2e-4; constraint norm at the end as with constant
     eta (one early spike at t = 0.5 M, larger than in the constant-eta runs).
   So with the paper's width the profile takes a light hole part of the way to its
   own-units behaviour; width 4 to 8 takes one hole nearly all the way.
   Recommended for Track F: shift_eta = 2/M, shift_eta_profile = true,
   shift_eta_mref = M (heavy mass), shift_eta_width = 4 (add the line to the input).
   A wide profile raises eta at a neighbour by (M_ref/m - 1)/(1 + D^2/(w m)^2) at
   separation D (for Track F's hills_q10_m8 input with width 4: 0.4 per cent at a member,
   2.4 per cent at the heavy hole at periapsis).

WHAT A PUNCTURE INSIDE EXPANDING DUST NEEDS (Track D)
   lapse 1+log with advection and lapse_leak (the hole is sliced as before, the dust
   lapse stays near exp(6 T H)); Gamma-driver with shift_eta = 2/M, zero shift at the
   start; lapse = table (psi^-2) or precollapsed; an outer boundary further than the
   light travel time of the run (outflow is not transparent for the Painleve-Gullstrand
   exterior, whose K_ij falls as r^-3/2). Example: problems/es/es_gauge.athinput (Track
   D's Einstein-Straus data, make_es.py --Rb 56 --w_out 4 --hp 2.0; give
   particles/particle_file and problem/comp0_file). Test ES above.

NOT TESTED
   lapse_leak_alpha other than 1; shift_eta_width_local = true; more than two holes;
   widths other than 2 on a pair (a card run with widths 4 and 8 on the pair of E2,
   run core-20261119-143517-ec2f4fc, was queued when the package closed; its prediction
   is in journal entry 8); runs longer than 6 m with the profile; a Hills passage
   (Track F's R4); Einstein-Straus runs longer than 30 M or with a finer dust mesh;
   a puncture inside dust with a transparent outer boundary.
