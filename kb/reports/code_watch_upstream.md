# kb watch upstream: IAS-Astrophysics/athenak, 20261115T132754Z

Tool kbtool 0.1.0. Compared with: clone record IAS-Astrophysics__athenak.json (2026-11-15T13:02:32Z). Snapshot:
`kb-data/meta/github/watch/IAS-Astrophysics__athenak/20261115T132754Z.json`; bare clone `kb-data/raw/watch/IAS-Astrophysics__athenak/20261115T132754Z.git`.

## Branch tips

- default branch `main` at c5a0d7f9155a70149931bf0be5a4ffb673f2532a
- 124 branches; new 0, removed 0, moved 0
- names containing pic, vlasov, nrpic or deposit (brief 12.7): none

## Branches named in brief line 130

| branch | tip | commit date | particles files | pushers | src/particles lines with tmunu/deposit | with z4c/adm |
|---|---|---|---|---|---|---|
| `particles_gr` | 8b04c1a8589d | 2025-05-20 | 7 | drift, leap_frog, lagrangian_tracer, lagrangian_mc, boris, only_gr, full_gr, gca_gr | 0 | 17 |
| `feature/particles-infrastructure` | db13b273e222 | 2026-09-06 | 11 | drift, leap_frog, lagrangian_tracer, lagrangian_mc | 0 | 0 |
| `particles_montecarlo` | 89cfd29dd62f | 2024-05-16 | 4 | drift, leap_frog, lagrangian_tracer, lagrangian_mc | 0 | 0 |
| `feature/lagrangian_mc` | 03fefe379779 | 2024-08-12 | 4 | drift, leap_frog, lagrangian_tracer, lagrangian_mc | 0 | 0 |
| `fix/update-prtcl` | 20b900ad616b | 2025-03-14 | 4 | drift, leap_frog, lagrangian_tracer, lagrangian_mc | 0 | 0 |
| `tracer_particle` | 7440f21c05cc | 2026-04-17 | 4 | drift, leap_frog, lagrangian_tracer, lagrangian_mc | 0 | 0 |
| `collapse` | 9c01609878c5 | 2026-05-25 | 4 | drift, leap_frog, lagrangian_tracer, lagrangian_mc | 0 | 0 |
| `project/tidal-interactions` | 7d6570741156 | 2026-09-15 | 4 | drift, leap_frog, lagrangian_tracer, lagrangian_mc | 0 | 0 |
| `id_solve` | c8de3ca7a78d | 2025-04-21 | 4 | drift, leap_frog, lagrangian_tracer, lagrangian_mc | 0 | 0 |
| `id_solve_porting` | 1319500b2037 | 2026-05-20 | 4 | drift, leap_frog, lagrangian_tracer, lagrangian_mc | 0 | 0 |
| `project/collapse_relaxation` | 8f19675f6ac1 | 2026-05-26 | 4 | drift, leap_frog, lagrangian_tracer, lagrangian_mc | 0 | 0 |

## Particle-spacetime coupling (test of brief line 125, every branch)

Branches inspected: 124 of 124. Branches whose `src/particles` has a line matching `z4c|tmunu|\badm\b|padm|adm::|deposit` (case-insensitive, the test of brief line 125): 7. Of these, lines with `tmunu` or `deposit` (matter handed to the spacetime): 0 branches; the others only read the metric (`z4c`, `adm`).
- `circumbinary_radiation` 6f9c7ad0f001 (2026-05-21): 0 tmunu/deposit lines, 13 z4c/adm lines, e.g.
    - `src/particles/particles.cpp:19:#include "coordinates/adm.hpp"`
    - `src/particles/particles.cpp:66:      if (pmy_pack->padm == nullptr) {`
    - `src/particles/particles.cpp:68:                  << std::endl << "null_geodesic particle pusher requires <adm> "`
- `circumbinary_stable` ccd38a7858d4 (2026-06-13): 0 tmunu/deposit lines, 13 z4c/adm lines, e.g.
    - `src/particles/particles.cpp:19:#include "coordinates/adm.hpp"`
    - `src/particles/particles.cpp:66:      if (pmy_pack->padm == nullptr) {`
    - `src/particles/particles.cpp:68:                  << std::endl << "null_geodesic particle pusher requires <adm> "`
- `flash-beam` 329872479fb4 (2026-07-08): 0 tmunu/deposit lines, 17 z4c/adm lines, e.g.
    - `src/particles/particles.cpp:19:#include "coordinates/adm.hpp"`
    - `src/particles/particles.cpp:66:      if (pmy_pack->padm == nullptr) {`
    - `src/particles/particles.cpp:68:                  << std::endl << "null_geodesic particle pusher requires <adm> "`
- `particles_gr` 8b04c1a8589d (2025-05-20): 0 tmunu/deposit lines, 17 z4c/adm lines, e.g.
    - `src/particles/boris_gr.cpp:54:		// Compute 3x3 ADM spatial metric from metric `
    - `src/particles/boris_gr.cpp:63:		//Use definition of the Lorentz factor in ADM formalism`
    - `src/particles/gca_gr.cpp:66:	Real ADM[3][3];`
- `port-radsrc-rr-tweaks-to-dyn-radiation` 9ade2afe0e40 (2026-06-02): 0 tmunu/deposit lines, 13 z4c/adm lines, e.g.
    - `src/particles/particles.cpp:19:#include "coordinates/adm.hpp"`
    - `src/particles/particles.cpp:66:      if (pmy_pack->padm == nullptr) {`
    - `src/particles/particles.cpp:68:                  << std::endl << "null_geodesic particle pusher requires <adm> "`
- `project/m1_vs_boltzmann` 3cf1c63ae375 (2026-09-24): 0 tmunu/deposit lines, 13 z4c/adm lines, e.g.
    - `src/particles/particles.cpp:19:#include "coordinates/adm.hpp"`
    - `src/particles/particles.cpp:66:      if (pmy_pack->padm == nullptr) {`
    - `src/particles/particles.cpp:68:                  << std::endl << "null_geodesic particle pusher requires <adm> "`
- `temp/static-monopole` 43512ede6992 (2025-03-17): 0 tmunu/deposit lines, 17 z4c/adm lines, e.g.
    - `src/particles/boris_gr.cpp:54:		// Compute 3x3 ADM spatial metric from metric `
    - `src/particles/boris_gr.cpp:63:		//Use definition of the Lorentz factor in ADM formalism`
    - `src/particles/gca_gr.cpp:66:	Real ADM[3][3];`

Branches with `nrpic` or `vlasov` anywhere under `src/`: 0.
Branches whose `src/z4c` mentions particles: 0.

## `main` at c5a0d7f9155a (2026-09-11T15:50:16-04:00)

- modules under src/: bvals, coordinates, cyclic_zoom, diffusion, driver, dyn_grmhd, eos, geodesic-grid, gravity, hydro, ion-neutral, mesh, mhd, multigrid, outputs, particles, pgen, radiation, reconstruct, shearing_box, srcterms, tasklist, units, utils, z4c
- src/particles: particles.cpp, particles.hpp, particles_pushers.cpp, particles_tasks.cpp
- pushers: drift, leap_frog, lagrangian_tracer, lagrangian_mc; particle types: cosmic_ray
- modules that mention tmunu: dyn_grmhd, mesh, outputs, tasklist, z4c

## Particle-related branches by name

| branch | commit date | subject | particles files | pushers | tmunu/deposit lines | z4c/adm lines |
|---|---|---|---|---|---|---|
| `adm_quantities` | 2025-07-29 | stage local changes | 4 | drift, leap_frog, lagrangian_tracer, lagrangian_mc | 0 | 0 |
| `collapse` | 2026-05-25 | Add scalar Poisson composite mask diagnostics | 4 | drift, leap_frog, lagrangian_tracer, lagrangian_mc | 0 | 0 |
| `feature/lagrangian_mc` | 2024-08-12 | reset particle z position on initialization | 4 | drift, leap_frog, lagrangian_tracer, lagrangian_mc | 0 | 0 |
| `feature/particles-infrastructure` | 2026-09-06 | yet more linting | 11 | drift, leap_frog, lagrangian_tracer, lagrangian_mc | 0 | 0 |
| `fix/update-prtcl` | 2025-03-14 | Realign to main (some mess with git) and implement | 4 | drift, leap_frog, lagrangian_tracer, lagrangian_mc | 0 | 0 |
| `four_metric_to_adm` | 2024-11-01 | restore linting script | 4 | drift, leap_frog, lagrangian_tracer, lagrangian_mc | 0 | 0 |
| `id_solve` | 2025-04-21 | initial version of loading id_solve data | 4 | drift, leap_frog, lagrangian_tracer, lagrangian_mc | 0 | 0 |
| `id_solve_porting` | 2026-05-20 | stage local changes | 4 | drift, leap_frog, lagrangian_tracer, lagrangian_mc | 0 | 0 |
| `particles_gr` | 2025-05-20 | Same error as in boris. | 7 | drift, leap_frog, lagrangian_tracer, lagrangian_mc, boris, only_gr, full_gr, gca_gr | 0 | 17 |
| `particles_montecarlo` | 2024-05-16 | Merge branch 'particles_smr' into 'master' | 4 | drift, leap_frog, lagrangian_tracer, lagrangian_mc | 0 | 0 |
| `project/collapse_relaxation` | 2026-05-26 | add time varying eta strategy | 4 | drift, leap_frog, lagrangian_tracer, lagrangian_mc | 0 | 0 |
| `project/tidal-interactions` | 2026-09-15 | Removed monopole and dipole moments from Newtonian | 4 | drift, leap_frog, lagrangian_tracer, lagrangian_mc | 0 | 0 |
| `tetrad` | 2026-02-20 | Added option for less aggressive flooring. | 4 | drift, leap_frog, lagrangian_tracer, lagrangian_mc | 0 | 0 |
| `tetrad-rebase` | 2026-10-30 | Typo fixes to HLLD. | 4 | drift, leap_frog, lagrangian_tracer, lagrangian_mc | 0 | 0 |
| `tracer_particle` | 2026-04-17 | Import commits from feature/lagrangian_mc to the c | 4 | drift, leap_frog, lagrangian_tracer, lagrangian_mc | 0 | 0 |
| `z4c-matter-intel` | 2024-04-30 | Commented out printf calls in dyngr_tov.cpp | 4 | drift, leap_frog, lagrangian_tracer, lagrangian_mc | 0 | 0 |
| `z4c-matter-rebase-pwp` | 2024-07-08 | Fix calculation of the specific internal energy fo | 4 | drift, leap_frog, lagrangian_tracer, lagrangian_mc | 0 | 0 |
| `z4c-matter-rebase-sgrid` | 2024-07-31 | The SGRID BNS initial data works now | 4 | drift, leap_frog, lagrangian_tracer, lagrangian_mc | 0 | 0 |

## Changes of src/particles and src/z4c since the previous snapshot

- first inspected snapshot: this one is the baseline

## Message for core

Nothing that brief 12.7 asks to report.
