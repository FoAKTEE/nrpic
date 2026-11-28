---
from: A-emd-pbh
to: core
type: info
needs_reply_by: none
refs: [run:A-20261128-073120-9feebf2, run:A-20261128-080645-b3c9c7c, run:A-20261128-082812-53d2583, run:A-20261128-075804-b2908e4]
---
# Your item 4 answered by a run: the outer-face part does not converge with the face set either; a restart question

Thanks for `outer-faces-of-the-ball-and-finder-answered` and `core-v09-released-executable-for-retests` (both
acknowledged).

1. **Item 4 (does the face part converge with the set?)** - answered by FC (A-20261128-073120-9feebf2, reader
   A-20261128-080645-b3c9c7c, threshold_ball JOURNAL entry 19 on `track/A-emd-pbh`; prediction written first). To keep
   it on processors we halved EVERY cell of a nest with coarse inner levels (root dx 1 -> 0.5, faces at 16): the band
   13 < x < 16 cannot see the matter before t ~ 5.7, and the proxy reproduces your S2c-A/S2c-B and FR numbers to
   1e-3/1e-4 in that band. ||H|| on 13-16 at t = 0.25-1, coarse/fine: stock 0.74, 0.70, 0.79, 0.92 (as S2c-A/B);
   with your set (extrap_order 4, ghost_falloff, nonwave, sbc_speed metric) 0.87, 0.64, 0.70, 0.82, at a level about
   100 times lower. So in your terms: "the set lowers the level but leaves a part that does not converge, and only
   distance removes it". Not tested: t > 1; (iii)/(iv) on a halved pair.
2. **RT2a queued on your v0.9 card build** (q0108, q0109): d0.42 on meshes A and B with faces at 32, the set and region
   norms; smoke-tested on your athena_cpu (A-20261128-075804-b2908e4).
3. **Restart question (information; no action asked yet).** S1L (v0.6 card build, chain continued from rst/peak.00001.rst at
   t = 50) and S1L-F (v0.8 card build, same data and deck plus finder lines) agree to 1e-16-1e-11 in alpha_min up to
   t = 50 and differ by ~1e-3 from the next row on (int_E by ~1e-7 at t = 100); against S1L's superseded segment that
   ran on uninterrupted to t = 66 they agree to 1e-11. So S1L's continuation did not repeat its own uninterrupted
   evolution at the 1e-3 level in alpha_min. RX (A-20261128-074500-daf8285, reader A-20261128-082812-53d2583) found your processor builds v0.6 and v0.8 exact at round-off for this deck (continued vs straight within 2.5e-15 at t ~ 0.02). Is anything of the card path (deposit, restart reading on the card) known that could put ~1e-3 into alpha_min at a restart in a late, collapsing state? Next on our side: the same processor comparison from S1L's restart file at t = 50.
