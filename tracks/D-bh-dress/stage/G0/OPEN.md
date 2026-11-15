# What the G0 package of D-bh-dress still lacks

Against `CHECKLIST.md` (from `nrpic-stage collect D-bh-dress G0`) and the task of wave 1.

1. Working note v0 (REVTeX under `tracks/D-bh-dress/note/`, written with /paper-writing,
   manuscript checker with --compile): not started. Content exists in `scope/SCOPE.md`,
   `einstein_straus/DERIVATION.md` and this package.
2. Schematics with /sleep-paper-figure-style: track architecture (exists / to be ported /
   new: puncture + particles + finder exist on main; format 2 on `core/id-extrinsic`;
   Newtonian mode on `core/newton`; lapse for expanding dust, accretion diagnostics,
   analytic-metric excision, puncture on the torus are new) and the stage timeline. Not
   drawn.
3. Verifier subagent with a fresh context and only the artefacts: not run. The lead's
   re-checks (JOURNAL.md, L1-L6) were made with the helpers' reports in hand, so they do
   not count as an artefact-only verification. Items most in need: SCOPE.md section 3
   (null-test wording), `einstein_straus/DERIVATION.md` sections 3-4 (conditions on f,
   a < 1), the LTB mapping with the over-massive hole (JOURNAL.md L5).
4. `nrpic-stage verify` (clean export, reruns) and `nrpic-stage report`: not run.
5. References not read at the source: Bertschinger 1985, Fillmore-Goldreich 1984,
   Einstein-Straus 1945 and its stability literature (not on arXiv; kb request); the
   brief's 1712.06383, 2002.10771, 2411.12007, astro-ph/9906391; lattices on the torus.
   The search for an existing full-NR particle-dark-matter environment (brief line 235)
   has not been made.
6. The cost of the matched vacuum controls and of the boundary control is judged, not
   computed with the model (REPORT.md section 7).
7. The parameter choice of the Einstein-Straus first run (outer dust edge 60 M) needs a
   regenerated data set and its offline check (`make_es.py --Rb 56 --w_out 4`, then
   `offline_check.py`).
