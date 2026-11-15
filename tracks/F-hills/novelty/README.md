# F-hills / novelty: novelty search F-pre-5 and G0 scoping

Work package of a helper of F-hills (2026-11-15). Everything here was written by that
helper; nothing outside `tracks/F-hills/novelty/` and `tracks/F-hills/runs/<own run ids>/`
was changed.

## Contents

| path | what |
|---|---|
| `NOVELTY.md` | F-pre-5: verdict (no full-NR Hills encounter with a heavier perturber, no full-GR matter binary passing a black hole, as of 2026-11-15), the closest papers with locators, what may and may not be claimed, limits of the search |
| `scope/SCOPE.md` | G0 scope: problem, objects (decision 0005), parameter ranges, the scale estimate of brief l. 275 re-derived and checked, exit criteria G0-G3, test plan against the section-10 rows of Track F, compute estimate, risks |
| `search/SEARCH_LOG.md` | every INSPIRE and web query with time and hit count; sources read |
| `JOURNAL.md` | predictions written before each run and the outcomes (including a failed run and a failed clause) |
| `scripts/inspire_query.py`, `scripts/inspire_abstracts.py` | INSPIRE literature API clients (generic queries; raw responses kept in scratch) |
| `scripts/scale_estimate.py` | run A: closed forms of brief l. 275 against independent numerics (marginally bound orbits in Schwarzschild and Kerr, Peters quadrature, parabolic passage times, Newtonian disruption window, published NR configurations) |
| `scripts/compute_estimate.py` | runs B and C: measured cost of this repository's black-hole runs and the cost model of the Hills passages, objects (a) and (b) |
| `scripts/write_manifest.py` | writes `tracks/F-hills/runs/<run_id>/manifest.json` for these analysis runs |
| `results/*.json` | copies of the results of the final runs (A: `scale_F-hills-20261115-045435-f62d553.json`; B: `cost_F-hills-20261115-045438-f62d553.json`; C: `cost_F-hills-20261115-045918-e7d0a66.json`) |
| `figures/fig_scale_plane.png` | left: (q, a_b) plane with the plunge bound, the brief's box and numbers, published NR configurations, our fiducials; right: Peters time, binary period, passage time for q = 10 |
| `figures/fig_rmb_check.png` | marginally bound radius against spin: numerical roots against the closed form |
| `figures/fig_pdis_q10.png` | Newtonian restricted disruption probability (1804.02911 fit) mapped to r_p/r_g at q = 10, with the plunge region |
| `figures/fig_cost.png` | left: MeshBlock-cycles per second of n1e4_v19 segments and of vacuum runs; right: card-hours per passage against resolution, with F's allotment |

Run manifests: `tracks/F-hills/runs/F-hills-20261115-045124-ae6bca8` (failed, import),
`-045332-ae6bca8`, `-045407-bf52f4e`, `-045410-bf52f4e` (superseded, same numbers),
`-045435-f62d553` (A, final), `-045438-f62d553` (B, final), `-045918-e7d0a66` (C, final).
They are ignored by `.gitignore` (`runs/`) and were added with `git add -f`. Outputs are
under `/data/haiyangw/nrpic/scratch/F-hills/<run_id>/`.

## How to rerun

From the worktree, processors only, seconds each:

    cd /data/haiyangw/nrpic/wt/F-hills
    R=/data/haiyangw/nrpic/scratch/F-hills/<new_run_id>      # F-hills-<YYYYMMDD-HHMMSS>-<commit7>
    OMP_NUM_THREADS=1 python3 tracks/F-hills/novelty/scripts/scale_estimate.py $R-A /data/haiyangw/nrpic/wt/F-hills
    OMP_NUM_THREADS=1 python3 tracks/F-hills/novelty/scripts/compute_estimate.py $R-B /data/haiyangw/nrpic $R-A/results.json

The analysis scripts need numpy, scipy, matplotlib from the user site-packages, so they
run without `-I` (they read only repository files and logs). The INSPIRE clients read
downloads and run with `python3 -I`:

    python3 -I tracks/F-hills/novelty/scripts/inspire_query.py <outdir> '<query>' [size]
    python3 -I tracks/F-hills/novelty/scripts/inspire_abstracts.py <outdir> <arxiv_id> ...

Repeat the citation queries of `search/SEARCH_LOG.md` (records 2799952 = 2406.11985,
2919080 = 2505.03934) before each gate.

## Requests

To the F-hills lead (to forward; this helper does not write outbox, STATUS or HANDOFF):
1. Outbox proposal to main, correction of brief l. 275: the box "q = 10-30, a_b = 20-60
   r_gb" is partly below the plunge bound (separation needs a_b >= 38.6 r_gb at q = 30,
   29.5 at q = 20); the rest of the item (19, 86, 400; Peters 6x10^3; "few hundred" for
   starts within 5 r_t) is confirmed (run A).
2. Compute: G1 fits the 40 GPU-hours (one vacuum passage about 24 card-hours at q = 10,
   m/8, or 12 at q = 4; one clump passage about 2 to 9). G2 needs about 234 and one scan
   line 283 to 1133 card-hours (run B): an allotment request to the user through the
   orchestrator (decision 0006), or the cuts of SCOPE section 7.
3. Decision 0005 at G0: object (b) is about ten times cheaper per passage than (a) and is
   the NRPIC-only regime; suggest running one (b) passage right after the first (a)
   passage instead of after the (a) scan line.

To core:
4. Merge `core/multi-puncture` into main (three Bowen-York punctures, trackers, finders),
   or tag it, so that F-pre-3 starts from a released capability.
5. The heavy hole's tracker did not move in test 3 (JOURNAL-mp l. 515-524, candidate:
   shift damping eta = 2 in code units, 20 in units of the heavy mass): a test or an eta
   scaled with the local mass, before any Hills run, since the heavy hole's recoil enters
   the energy budget.
6. Note on `problems/puncture/by_triple.athinput`: its binary (a_b = 10 r_gb, q = 10) is
   below the plunge bound and its Newtonian pericentre (3 r_g) inside r_mb = 4 r_g, so it
   tests the machinery but would plunge as a whole; F will supply a Hills input
   (q = 10, a_b = 30 r_gb, r_p = 6 r_g, r0 = 4 r_t) with momenta from the Schwarzschild
   parabolic geodesic.
7. A benchmark of 32^3 MeshBlocks on the three-puncture mesh (the uniform-mesh smoke
   runs are twice as fast per cell as the refined 16^3 meshes), and an opinion on
   subtracting the known heavy-hole background (arXiv:1303.1540).
8. For object (b): initial data of a moving equilibrium clump with momentum (curvature of
   a boosted clump; `coord/notes/design_wave2_initial_data.md` section 3 and item 4).

To Track C (through the lead): equilibrium cluster models of compactness 0.05 to 0.1 and
their stability, for the clumps of object (b) (they must fit the Roche lobe, SCOPE
section 2).

To kb: the sources fetched for this search are in `kb-data/raw/arxiv/` (2406.11985,
2308.07365, 2505.03934, 2605.20320, 2108.01392, 2604.27429, 2610.09336); please index
them for group G21.

## Not done

No NR run was made (none was needed for this package). The MeshBlock counts of the Hills
meshes in the cost model are JUDGEMENT; the Roche-lobe factor 0.38 is [BACKGROUND] to be
checked; the Newtonian disruption window is the restricted large-q fit, not valid at
q = 10, to be replaced by F-pre-1's full three-body reference. ADS and journals outside
arXiv were not searched.
