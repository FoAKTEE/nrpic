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
