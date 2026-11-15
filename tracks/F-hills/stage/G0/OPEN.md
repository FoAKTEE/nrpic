# G0 of F-hills: what the gate still lacks

1. **Stage check not run.** The package has not been put through `harness/bin/nrpic-stage`
   (`/stage-check`); no `STAGE_REPORT.md` or `VERIFIER_REPORT.md` exists. The main document
   is `SCOPING.md` (the requested name `REPORT.md` was refused by the session's write tool);
   the orchestrator may rename it.
2. **No second agent has checked the results that matter** (CLAUDE.md, decision 0009): the
   novelty verdict (`novelty/NOVELTY.md`), the reproduction of 0911.1136/1804.02911 (newton3)
   and of 2404.16270 (geodesic_binary), and the lead's V6/V7 finding that the geodesic
   reference plunges a member in most phases at r_p <= 12 M. The lead re-ran tests and
   reproduced nine restricted points independently (V1-V4b), but the lead belongs to the same
   owner.
3. **Decision 0005 not formally confirmed.** Proposed: keep (a) -> (b) -> (c), run one (b)
   passage right after the first (a) passage (outbox to orch).
4. **Compute allotment.** G1 fits the 40 card-hours of decision 0006 with no margin; G2
   (about 120) and G3 (about 500) do not. Answer from orch/user needed (outbox).
5. **Mass ratio of the scan lines.** Convergence at q = 10 needs m/16 meshes of 2654-4544
   MeshBlocks, beyond one card with margin; the build has no MPI. Proposed: the convergence
   triple and the first scan line at q = 4, q = 10 as the headline passage; or two-card MPI
   from core (outbox).
6. **Capability not released.** `core/multi-puncture` is PROPOSED, not on `main`, not listed in
   `CLAUDE.md`; F has therefore run none of its code (R0, R2, R4 and the passage are pending).
7. **Known defect to fix in the next wave**: newton3's member energies at finite q (two-body
   with M alone, not conserved when the other member is captured; V5b). Needs the barycentric
   definition in `newton3/hills3/threebody.py` and reruns of finiteq, P3 (M/m <= 100) and the
   three_punctures scans.
8. **Unverified items carried**: the Roche-lobe factor 0.38 (Eggleton 1983, from memory); the
   quadrupole energy of a parabolic flyby used by three_punctures (no locator); the factor-ten
   disagreement between core's and the helper's junk estimates from spheres at 10-14 m; SKR's
   retrograde disruption criterion (hypothesis H1) and its D-uniform averages; 2402.02178 not
   reproduced; cause of HRNA's release-radius dependence (C2).
9. **Correction to the brief l. 275 not yet accepted** (outbox proposal to orch).
10. **Object (b) inputs missing**: moving equilibrium clump data (core) and a stable clump
    model with compactness above 0.044 at a_b = 30 r_gb (Track C); neither requested before
    this session (outbox).
