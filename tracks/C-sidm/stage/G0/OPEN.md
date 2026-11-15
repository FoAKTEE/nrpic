# C-sidm G0: what the gate still lacks

State at the end of the lead session of 2026-11-15. Items of `CHECKLIST.md` (harness) that
are not PASS, and the open scientific items that the G0 scope depends on. Each line says
who can close it.

## Products of charter 9.2 not yet made

1. Working note v0 (REVTeX under `tracks/C-sidm/note/`, written with `/paper-writing`,
   guide and notation one level above the manuscript): not started. Content exists in
   `REPORT.md` and `scope/SCOPE.md`. Owner: C-sidm, wave 2.
2. Architecture schematic (exists / to be ported / new, `/sleep-paper-figure-style`) and
   the stage-timeline schematic: not drawn; the timeline is a table in `REPORT.md`
   section 9. Owner: C-sidm, wave 2.
3. Verifier subagent report (`VERIFIER_REPORT.md`, fresh context, numbers recomputed from
   the manifests): not run. The lead's review (`REVIEW.md`, runs
   C-sidm-20261115-131130-3077a99 and -131135-3077a99) rechecked every package from its
   artefacts, but the lead read the helpers' conclusions, so it is not the fresh-context
   check of brief 13.3. Owner: orchestrator or C-sidm.
4. `nrpic-stage verify` on a clean export: not run (the package has no `note/scripts`
   yet; the reruns of the review play that role for now).
5. The key references are verified in `kb-data/raw` sources by file:line, not through a
   knowledge-base index (kb has not indexed them). Owner: kb (outbox request).

## Scientific items the scope still depends on

6. Fluid onset with the adiabatic index of a Juttner gas, Gamma_1 = 1 + 1/c_v, instead of
   F21's gamma = 1 + p/u, for the F21 b = 0.1 sequence (the Kn -> 0 anchor; a few minutes
   with `gravothermal/tmb.fem_lowest` and `collide/REFERENCES/mj.py`). Owner: C-sidm.
7. F21 b = 0.1 models as particle files (generalise `equilibria/evstatic.py` from the King
   b = 1 kernel exp(1 - E/E0) - 1 to exp((1 - E/E0)/b) - 1) and their AthenaK read test.
   Owner: C-sidm (equilibria helper), wave 2.
8. Growth-rate extraction of the threshold runs (alpha_c(t), mass radii; fit over several
   periods after saturation) validated on the first paper's monoenergetic outputs
   (`runs/st/`, main checkout). Owner: C-sidm.
9. Cost of one collision: unmeasured until core's operator exists (T2 measures it). The G2
   and G3 estimates rest on an assumed multiplier. Owner: core, then C-sidm.
10. Literature [TO VERIFY]: the identifier of "Gurian:2025zpc" (collisional Boltzmann SIDM,
    `SIDM_MS.tex:672`); Shapiro & Teukolsky 1985 (not on arXiv); Ipser 1969; the
    relativistic conductivity of hard spheres (Cercignani & Kremer); the higher-Sonine
    factor (~1.025); Nanbu & Yonemura 1998; the DSMC cell-size and time-step error papers;
    the critical-collapse references of row 844 (gr-qc/9804040, gr-qc/0107076,
    1409.5176), not read; 1707.08666 read only at the abstract. Owner: kb (outbox).
11. Whether a collisionless F21 b = 0.1 model near threshold leaves an envelope (decides
    whether a mass fraction below one exists without collisions). Owner: C-sidm, wave 2
    runs.
12. The equilibria package's momentum-constraint integral of the King files in AthenaK is
    1.42 times that of the monoenergetic reference (run C-sidm-20261115-125308-54870b9);
    cause not tested. Owner: C-sidm.

## Corrections of shared text proposed, not yet accepted

13. Brief lines 384, 520, 843, 852 and the charter's row "Collisional relaxation in a
    Minkowski box"; the G2 phrase "the literature value" (outbox
    `20261115T1320Z__to-orch__brief-corrections.md`). Owner: orchestrator.
