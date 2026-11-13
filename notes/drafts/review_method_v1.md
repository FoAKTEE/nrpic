# Review of the first draft of the system and method sections (2026-11-13)

Checked equation by equation against `notes/method_brief.md` and the source. Automated
checks (`check_manuscript.py`): clean except the intended statement of the two
unimplemented features.

Correct as written: characteristic equations; midpoint update; triad identities and the
tetrad equation of motion; Boris rotation (Lorentz factor from the midpoint mean of the
tetrad momentum, as in the code); both gauges; Hermite weights; cloud-in-cell weights,
leaf weights, adaptive cap, conservation identity; Z4c variables and gauge; relaxation;
refinement indicator; Kretschmann decomposition; initial data.

To change in the revision pass:

1. method, reconstruction: "Two ghost cells surround every block" -> the stencil needs at
   least two ghost cells; the runs use more.
2. method, spacetime: the shift speed parameter is written mu, which is also a spacetime
   index. Rename (mu_S) and add to NOTATION.md.
3. method, pushers: the sentence with the polar-coordinate analogy does not parse (the
   analogy clause is not connected to the main clause). Say it in two sentences: free
   motion in polar coordinates has straight-line solutions, yet a finite step that
   evaluates the rotation of the unit vectors at the midpoint and projects at the end
   points makes an error that Cartesian axes do not; the triad is such a set of unit
   vectors, fixed by the metric only up to a rotation.
4. system: the Vlasov equation is written with a derivative with respect to u^mu while f
   is declared a function of u_j. Use one set of variables.
5. Both: many sentences run past forty words with two or three subordinate clauses and
   paired dashes. Split them; one statement per sentence; at most one dash pair per
   paragraph.
6. method, numerical methods: the horizon-finder sentence should say what was done
   (stopping tolerance on the change of mass between iterations, search every few
   cycles), without "instead of".
7. method, spacetime: the order of the finite differences is a property of the runs
   (sixth order on refined meshes); keep one clause, drop the host-code requirement.
8. method, pushers, last paragraph: say what was observed, which triad reproduces which
   published numbers. Do not write that the test "identifies each choice" of the
   original code: agreement of digits shows that these two triads are sufficient, and
   other constructions that coincide with them on these orbits are not excluded.
9. method, deposition: the sentence on per-cell cloud-in-cell at a coarse-fine interface
   claims that the weight defect "excites constraint violations as matter crosses
   interfaces". That scheme was never run here. Keep the arithmetic (the weights of a
   straddling particle do not sum to one, so the mesh integrals differ from the particle
   sums) and drop the untested consequence.
10. method, numerical methods: the horizon-finder sentence states as fact that a tighter
    tolerance removes an underestimate of the area. A vacuum puncture read with the
    tighter tolerance still gives a mass 2 to 3 percent low (docs/TESTLOG.md, calibration
    entry). Rewrite after the calibration runs; until then describe only the settings.
11. Anything that names a cause ("because", "so", "driven by", "sets the error") needs a
    run that isolates that cause, or it is rewritten as the observation. Check each one
    against docs/TESTLOG.md before the next pass.
