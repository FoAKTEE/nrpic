# Captions suggested for the schematic figures (to be edited by the writer)

fig_cycle: One step of the particle-mesh cycle. Blue stages act on the mesh, red stages
on the macroparticles; each arrow is labelled by what it passes, and bars mark the metric
averaged over the step. The dashed branch is the regrid, after which the metric, block
ownership and sources are rebuilt on the new mesh.

fig_deposition: A cloud keeps unit weight across a refinement boundary, and the level cap
stops it shrinking with the mesh (two-dimensional cartoon; each level divides the
particles per cell by four here, by eight in three dimensions). Left: a cloud-in-cell
cloud (red square) shares one particle among four cells. Middle: each cloud lives on the
lattice of one level (dashed virtual cells); virtual cells over a coarser leaf are summed
into it, those over finer leaves are spread uniformly over them. The lower cloud is a
capped one. Right: the same particles on a fine mesh, deposited on the finest level and
on a capped coarser level. Shading: deposited density; numbers: leaf-cell weights.

fig_hypergraph: How the code was assembled. Each row is a capability taken from an
existing code or published method, grouped by origin; each red column is a component
built here, a hyperedge joining the capabilities it combines (dots). The red rows at the
bottom are built components reused inside the coupled cycle and the adaptive mesh.

fig_tp_cluster: Clusters of 10^4 test particles around a black hole of spin a = 0.9 M.
Top: a cluster started on a circular orbit phase-mixes into a ring (orbital plane, mesh
metric; black disk: the black hole). Bottom left: median (solid) and 99th percentile
(dashed) of the relative errors of the geodesic energy and L_z; colour marks the pusher,
thick curves the mesh metric (yellow edges: the spacetime Boris run under the implicit
midpoint run), thin curves the analytic metric. Bottom right, for a cluster of lower
angular momentum, part of which plunges: the conservation identity before the filter
(red) against the rate of refinement-level changes (grey, right axis), and the particles
removed by lapse excision (red) against exact geodesics (blue dashed).
(Text must add: after the filter the integrals are off by 1e-4 to 1e-3 at level
boundaries; 3345 removed against 3339 predicted.)

fig_tracers: Test particles around a puncture of mass M evolved in moving-puncture gauge.
Top: areal radius against proper time for a radial infall and a plunge (red) and the
exact geodesics (blue dashed). Middle: relative difference for mass M (solid) and for the
Misner-Sharp mass of the slice (dotted); grey: R = 2M. Bottom: mass implied by each
circular orbit (red) and Misner-Sharp mass of the slice (black).
(NOTATION.md needs entries: particle proper time tau, Misner-Sharp mass.)
