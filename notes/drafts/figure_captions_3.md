# Caption for the prolate-collapse figure (to be edited by the writer)

fig_prolate is a full-width figure (`figure*`, `width=\textwidth`, drawn at 7.0 in).
The caption below has 705 visible characters, an estimated 4.8 lines at full width
(the checker counts 147 characters per line). The labels sit inside the panels, so the
caption names only the elements that the labels do not explain.

\caption{With $10^4$ macroparticles, the cold prolate spheroid collapses through a
spindle whose two curvature maxima on the axis move inward, and an apparent horizon
forms at the time found in Ref.~\cite{Wu:2026nrpic}. Top: macroparticles projected on
the $x$--$z$ plane (own scale per panel); circles, maxima of the Kretschmann scalar $I$;
black curve, first apparent horizon. Bottom left: largest $I$ and $|z|$ of its maximum
on the axis, with the outermost macroparticle and the polar radius of the horizon.
Bottom middle: smallest lapse, fraction of macroparticles remaining, and excision
threshold (dotted). Bottom right: apparent-horizon mass $M_{\rm AH}$. Dashed: first
apparent horizon; blue: total mass $M$ and times shown in Ref.~\cite{Wu:2026nrpic}.}

## What the text must say next to the figure

- The panels show the snapshots nearest to the original's times. Snapshots exist every
  0.5 M, so the third panel is at 27.5 M; the original's narrow spindle is at 27.75 M.
  The other three panels (0, 20.5, 32 M) are at the original's times exactly.
- The sample has reflection symmetry in z, so the two maxima of I are exact mirror
  images at +z and -z. The maximum lies on the axis (cells next to it) from 18.5 M on.
- The maximum does not move along a single track. The axis has several ridges of high
  energy density, and the largest I jumps between them. |z| of the maximum: 7.09 M at
  18.5 M; 5.03 at 20.0; 4.97 at 20.5; 4.59 at 22.25 (the time of the original's
  curvature slice); 4.22 at 23.5; 3.91 at 24.25. It then jumps to 2.78 at 24.5 and 2.72
  at 25.0, falling to 2.41 at 26.0. Next it jumps to 0.72 at 26.25 and stays at 0.66
  to 0.72 until 28.0. It moves back out to 1.84 at 28.25 and to 1.59 at 29.0, then
  falls steadily: 1.28 at 30.0, 1.03 at 31.0, 0.72 at 32.0, 0.47 at 33.0, 0.28 at 34.0
  to 34.5 M. Overall it moves inward from about 7 M to 0.3 M, but not monotonically.
- The jump of the largest I near 16 M marks the two finest mesh levels appearing.
  The time step falls from 0.0625 to 0.015625 M at t = 15.75 M. The largest I is 0.059
  at 15.5 M, 2.7 at 15.75 M and 16.5 at 16.0 M, so it jumps by a factor of 280 in
  0.5 M. Before 18.5 M the maximum jumps between positions off the axis.
- The maxima lie inside the matter. From 18.5 to 23.5 M they sit where the energy
  density is largest (except at 20.0 M, where I peaks at |z| = 5.03 M and the energy
  density at 6.72 M). From 23.75 M on the two separate. At 27.75 M the largest I is at |z| = 0.66 M
  and the largest energy density at |z| = 1.97 M.
- At the first horizon the matter still reaches beyond the horizon along the axis. The
  outermost macroparticle is at |z| = 1.94 M and the horizon pole at 1.33 M. By 33.5 M
  the outermost macroparticle is at 1.25 M.

## Numbers (all from the run; t, lengths in M, I in M^-4, energy density in M^-2)

Setup (for the appendix table):
- Cold homogeneous prolate spheroid: eccentricity 0.9, polar semi-axis b = 10 M along
  z, equatorial semi-axis a_eq = 4.359 M. Total (ADM) mass M = 1, particle rest mass
  1.09815 M. N = 10^4 equal-mass macroparticles at rest, a Monte Carlo sample with
  reflection and half-turn symmetry. Conformally flat, time-symmetric data, initial
  lapse 1.
- Mesh: [-128, 128]^3 M, root cells of 4 M, seven levels, finest cells M/16. A static
  level-4 region (cells of M/4) covers |x|, |y| <= 5 M and |z| <= 11 M; the
  Loehner indicator controls refinement. CFL 0.25: time step 0.0625 M, then
  0.015625 M from 15.75 M.
- Deposition: cloud at the finest local level, four binomial filter passes plus the
  compensation pass. Lapse excision at alpha_exc = 0.05.
- Apparent-horizon searches every 0.25 M from 20 M. End time 45 M.
- MeshBlocks: 512 at the start; at most 1352 (first at 17.70 M); 1184 at the end.

Outcomes:
- Largest Kretschmann scalar: I = 1203.3 at t = 27.75 M, on the axis at
  (0.031, 0.031, -0.656) M. Its mirror image sits at z = +0.656 M. At the original's
  slice time, 22.25 M, the largest I is 526.9 at |z| = 4.59 M. Values at the original's
  three times: 102.5 at 20.5 M (|z| = 4.97), 1203.3 at 27.75 M (|z| = 0.66), 319.1 at
  32 M (|z| = 0.72).
- Largest energy density: E = 0.8235 at t = 23.5 M, on the axis at |z| = 4.22 M.
- Spindle (outermost macroparticle |z|; |x| enclosing 90 percent of the particles):
  9.82 and 3.19 M at 0; 6.73 and 0.94 M at 20.5 M; 4.04 and 0.11 M at 27.5 M; 1.94 and
  0.10 M at 32 M.
- First apparent horizon: t = 32.0 M (no horizon in the searches from 20 to 31.75 M).
  M_AH = 0.9291, mean coordinate radius 0.998 M, polar radius 1.33 M, equatorial
  radius 0.88 M.
- Smallest lapse: 0.0867 at the first horizon, 0.0168 at 45 M (still falling).
- Horizon mass: largest value 0.9666 at 33.75 M. After that it falls: 0.9635 at 35 M,
  0.9567 at 40 M, 0.9489 at 44.75 M (the last search). Over the last 5 M the values
  are 0.95670 (40), 0.95468 (41), 0.95279 (42), 0.95110 (43), 0.94968 (44) and 0.94888
  (44.75 M). The slope after 40 M is -1.65e-3 per M, steady and not levelling off. At
  44.75 M the horizon is nearly round: polar radius 1.33 M, equatorial 1.21 M.
- Particle removal: the first particles are removed at t = 33.78 M (352 in that step;
  smallest lapse 0.055 at 33.75 M), and the last at 38.80 M. All 10^4 are removed;
  the removed rest mass, 1.098148 M, equals the rest mass of the data, and none escaped.
- Hamiltonian constraint, ||H|| = sqrt(H-norm2) as in the dust figure and the tables:
  largest 6.31 at t = 27.5 M (start 0.54, end 0.57). The lattice dust run peaks at
  1.90 on the same measure.

## For the writer: what the data do not support, or what disagrees elsewhere

- The horizon mass ends 5 percent below M. It peaks 3 percent below M and is still
  falling at the end. The original reports agreement with the initial mass to 1e-3
  (2e6 particles, cells of M/64). The figure states the deficit and does not explain
  it.
- method.tex (Sec. on filtering) says the prolate collapse runs keep one or two plain
  binomial passes. This run uses four passes plus the compensation pass, so the
  sentence needs changing if this run is the one shown.
- The test log entry of 14:12 compares a constraint "largest value 49.7 at 27.7 M"
  with "the lattice dust run peaks at 1.9". The 49.7 is the C-norm2 column, unsquared
  (its square root is 7.05). The 1.9 is sqrt(H-norm2). On the like-for-like measure
  the prolate peak is 6.31 at 27.5 M.
