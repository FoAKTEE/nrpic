# Review of the first draft of the test-particle section (2026-11-13)

Automated checks: clean. Content follows the three results documents. To change in the
revision pass:

1. Wrong citation: the Kerr invariants are cited to the 1985 cluster paper. Cite Carter
   (add the entry) or drop the citation.
2. "grazes the event horizon": the pericentre is outside the horizon by a third of its
   radius. Say "passes close to the event horizon".
3. Last sentence: the run in progress is a head-on collision of two black holes, not an
   inspiral and merger.
4. "Vertical epicycles and Kerr nodal precession set the ring thickness": no run
   isolates this. Remove.
5. Filter paragraph: say what was measured (after the filter the integrals differ from
   the particle sums once particles cross refinement boundaries; before it they do not)
   and that the filter on the mesh is not conservative across levels. Drop "per
   boundary-crossing particle".
6. Captions against the figures as they are:
   - fig:passage has no blue curves. Top row: radius against time; the trajectory near
     the black hole; position error against time step with a second-order guide. Bottom
     row: errors of the three invariants against time. Red implicit midpoint, yellow
     Boris symmetric gauge, green Boris Cholesky gauge; solid analytic spherical
     Kerr-Schild, dashed analytic Cartesian, dotted reconstructed on the mesh.
   - fig:tpcluster and fig:tracers: use the captions in notes/drafts/figure_captions.md
     (they describe the panels as drawn). fig:tracers is one column wide (figure, not
     figure*). The post-filter residual is not in the figure; the text states it.
   - fig:orbits and fig:convergence: still to be checked against the PDFs by me.
7. Every paragraph opens with a gerund clause of the same shape ("Sending ...",
   "Applying ...", "Varying ...", "Comparing ...", "Replacing ...", "Accumulating ...",
   "Lowering ...", "Evolving ...", "Tracking ...", "Following ..."). Open with the
   question or the physical situation in a plain subject-verb sentence instead; vary.
8. Several sentences carry three or four technical noun stacks ("indistinguishable
   third-order-convergent invariant errors set by Hermite reconstruction"). One fact per
   sentence.
9. NOTATION.md needs: particle proper time tau, Misner-Sharp mass, M_eff.
