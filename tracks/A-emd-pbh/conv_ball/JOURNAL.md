# JOURNAL of the package conv_ball (helper of A-emd-pbh, wave 3, round 1)

G2 convergence series of horizon formation in the expanding ball (data set 3): mesh
spacing, particle number, ball radius, outer boundary. Brief of the package: PLAN-wave3.md
round 1, package 3 (card cap 6 card-hours, executable core_gauge for every member).

## 2026-11-20, entry 1: what was read, design inputs found (no simulation run yet)

Read: CLAUDE.md, coord/CHARTER.md to "Owners" and 9.4, decisions 0010, 0013, 0014, 0016,
0017-0019, harness/RULES.md, PLAN-wave3.md, runs_ball/README.md and JOURNAL.md entries 7-10,
the runs_ball scripts at 9cddbfc6, expball/README.md, core_gauge/READY, core/gauge
cosmo_gauge.md section 7 and problems/ball/ball_collapse.athinput, the source paper
main.tex lines 930-952 and 1476-1492.

Facts checked in the files (planner's FACTS):
- BH-1R (run A-20261119-164634-f1fe887, bh_smr/athena.log): 568 MeshBlocks of 32^3,
  1317216 particles, 1024 cycles, 1769 s, gpu_mem_peak_MiB = 80633 [VERIFIED].
- BH-1 at uniform M/8 (bh_n256 of run A-20261119-144419-13d5601): its athena.log says 64
  MeshBlocks (root grid 4 x 4 x 4, blocks of 64^3), not 512 as the planner wrote; peak
  41223 MiB, 545 s for 512 cycles [VERIFIED]. sr1l_n256 of the same job (same mesh, 28768
  particles) peaked at 41195 MiB and took 1.056 s per cycle against 1.0645 s: particles cost
  about 2e-4 MiB and 6e-8 s per particle and step (nested.py, cost model).
- Source paper: fiducial OS horizon-mass error Delta M/M_ADM <~ 1e-3 (main.tex:945); AMR
  particle sequence RMS 2.061e-3, 9.362e-4, 7.347e-4 for A1-A3, no monotonic trend for the
  fixed-N SMR sequence (main.tex:1484-1485) [VERIFIED].

Design input, run A-20261120-222355-cc8e0af (`scripts/geometry_probe.py` on BH-1R; figure
fig_geometry.png looked at): the finder's horizon sits at mean coordinate radius
0.418-0.443 M (first found t = 10.875, 41 searches to 15.875); the core shells (R_i <= 2.6)
start at coordinate radius <= 2.43 M and are at r < 0.4 M when the horizon is first found;
the core-edge group reaches its exact trapping proper time at t ~ 10.9, when the finder first
reports a horizon; outer shells move out to r ~ 7 M by t = 16; particles are first removed at
t = 12.70; 1.72 s per cycle.

Design chosen (to be written into DESIGN.md; code committed in a9c36d98): nested static
geometry, finest box [-1, 1]^3, level boxes at 1, 2, 4, 8 M, outer boundary 16 M (32 M for
the boundary leg), each level box 4 MeshBlocks wide; members A, B, C with finest cells M/16,
M/32, M/64 (root 32^3, 64^3, 128^3 in blocks of 8^3, 16^3, 32^3; 288 leaf blocks each);
nested lattice with one particle per local cell (77704 particles for A: tested in
scratch/A-emd-pbh/tmp/conv_ball/preptest, not a result; its table is byte-identical to that
of data set 3, run A-20261119-143524-334e553). Model numbers (design_calc.py, code test in
tmp, NOT yet a registered run): C about 41 GiB and 1.3 card-hours (a chain of two segments),
B 0.12, A 0.02 card-hours; the series with the N, R_b and boundary legs about 2.1
card-hours.

## 2026-11-20 14:34 PST, entry 2: PAUSED (locks/PAUSE present: five-hour window at 97 per cent)

Stopped here, nothing running, no card job submitted. Committed: scripts (copies of runs_ball
at 9cddbfc6 with adjusted paths, geometry_probe.py, nested.py, design_calc.py, prep_bh.py with
--M, --edge-w and --nested, make_decks.py) and decks/nest{16,32,64}_L{16,32}.athinput.
Next steps on restart, in order:
1. registered run of design_calc.py (--exact .../A-20261119-143524-334e553/exact.json
   --probe .../A-20261120-222355-cc8e0af), look at fig_design.png, write DESIGN.md;
2. predictions for every member in this journal, commit;
3. registered prep runs: data set 3 with --nlat --nested nestA:16:16:1 nestA2:16:16:2
   nestA4:16:16:4 nestB:32:16:1 nestB2:32:16:2 nestC:64:16:1; the larger balls
   (--HRb 0.875 --M 1.953125 --R1 0.52 --R2 0.76 --edge-w 0.16836734693877542; and
   lam = 1.35: --HRb 0.945 --M 2.460375 --R1 0.48148148148148145 --R2 0.7037037037037037)
   with nestA and nestB;
4. processor smoke tests of the decks with core_gauge/athena_cpu (nlim 2; nest32/nest64 with
   a reduced mesh override);
5. card job 1 (batch, 58 min): A, B, A-N8, A-N64, A-R1.25, A-L32, B-N8; then the chain of C.
