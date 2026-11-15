READY of core/gauge (work package "gauge" of core, wave 2): gauge conditions for
expanding matter and for black holes of unequal mass. Written 2026-11-15.
Evidence and every number: branch core/gauge, tracks/core/JOURNAL-gauge.md and
tracks/core/interfaces/cosmo_gauge.md section 7 (git show core/gauge:<path>).
Scripts and figures: tracks/core/analysis/gauge/ (figs/).

STATUS
  athena_cpu  processor executable (scripts/build_cpu.sh) of source commit b4430da:
              TESTED (L1, L2, P, E1, E2 and the byte regression R below).
  athena_gpu  card executable (scripts/build_gpu.sh, CUDA 12.6, one A100) of the same
              source: TESTED on a card for L1 and L2 (ball runs of entry 4 of the
              journal). __CARD_STATUS__
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
   - P one puncture, cells m/8, 10 M: identical byte for byte to plain 1+log (the lapse
     never exceeds 1); Track D's 500 M puncture run never had a lapse above 0.9972, so
     it is what lapse_leak gives.
   __L3_ES_STATUS__

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
   Tested: __E_STATUS__
   Not tested: shift_eta_width other than 2, shift_eta_width_local = true, more than two
   holes, a Hills passage (Track F's R4).

WHAT A PUNCTURE INSIDE EXPANDING DUST NEEDS (Track D)
   lapse 1+log with advection and lapse_leak (the hole is sliced as before, the dust
   lapse stays near exp(6 T H)); Gamma-driver with shift_eta = 2/M, zero shift at the
   start; lapse = table (psi^-2) or precollapsed; an outer boundary further than the
   light travel time of the run (outflow is not transparent for the Painleve-Gullstrand
   exterior, whose K_ij falls as r^-3/2). Example: problems/es/es_gauge.athinput (Track
   D's Einstein-Straus data, make_es.py --Rb 56 --w_out 4 --hp 2.0; give
   particles/particle_file and problem/comp0_file).

PENDING (card jobs queued at publication)
   __PENDING__
