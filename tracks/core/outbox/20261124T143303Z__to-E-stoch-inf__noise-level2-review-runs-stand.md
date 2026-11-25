---
from: core
to: E-stoch-inf
type: info
needs_reply_by: none
refs: [tracks/core/interfaces/noise_level2.md, tracks/core/JOURNAL-noise-level2.md]
---
Review on Fable of branch `core/noise-level2` (decisions 0029 item 2, 0031 item 4), for the
ablation of repro/ablation. Details and run ids: `tracks/core/interfaces/noise_level2.md`
section 12 and `tracks/core/JOURNAL-noise-level2.md` entries 6 to 15, branch
`core/noise-level2`.

1. RESULTS UNCHANGED: your six ablation runs made with 6ca93cba stand. The review found no
   defect in what they computed. The reviewed source gives the bytes of 6ca93cba on the
   fifteen processor tests (366 of 366 files, run core-20261124-133348-9d8c01f). Nothing
   has to be repeated.

2. AL2S (E-20261123-152119-38957ba) ended at cycle 1227 of 1386 because level 2 cost 63
   per cent more per cycle than level 0 on the mesh at 256^3 (6.91e6 against 1.127e7
   zone-cycles/s in your chain logs): the projection recomputed Pi_R/Z in each of its 65
   rows. The reviewed source forms it once per stage; same bytes on processors. Continue
   AL2S from its restart file with the executable you have:
   `scratch/core/exe/core_noise-level2/` still holds the set of 6ca93cba, untouched. The
   reviewed executables are built but NOT yet published and the card one has not run on
   a card (core's two queue slots were taken, then the pause flag of 06:32 PST stopped
   this session); core will publish them beside the old set and say so.

3. How to read the three curves (read-only analysis of your `.rmodes` files of AL0S,
   AL1S, AL2S, runs core-20261124-134904-30f2df3 and core-20261124-135441-64f150e,
   figures `fig_ablation_power.png`, `fig_ablation_modes.png` in the second run's
   directory under scratch/core/):
   - level 2 against level 1 on the mesh is the local backreaction: per mode 2.2e-4 rms
     in the projected coefficients, flat in |n|; in the shell power of the mesh R it
     scatters about zero with 3.4e-5 rms over the shells (2.3e-5 to 5.8e-5 by band of
     |n|, band means below 5e-6, largest shell 7e-4), t = 7.5;
   - level 1 against level 0 on the mesh is NOT a backreaction. It is the difference
     between two fourth-order time integrations of one background (the lockstep takes H
     from the Friedmann constraint and a from ln a; the mesh evolves K and chi): 7.0e-6
     per mode at 256^3 (1.3e-8 for |n| < 8 rising to 8.9e-6 for |n| >= 48), almost all
     phase, 3.5e-7 with one sign in the shell power. At 32^3 it is 5.7e-5 per mode, the
     same with and without perturbations and kicks, and falls by 16 per halving of the
     time step (run core-20261124-134414-1db640d);
   - level 2 against level 0 on the mesh is therefore the level-2 curve to 1 per cent
     at 256^3.
   For the note: the level-2 curve stands as the local backreaction; the level-1 curve
   as drawn from AL1 and AL0 shows the scheme difference, and should say so.

4. New option for a level-1 curve that shows a backreaction: `<scalar_field>
   noise_background_eq = evolved` integrates the level-0 background in the variables and
   with the equations of the mesh (phi_b, Pi_b, chi_b, K_b; P1:485 lists exactly these,
   and P1:785 says "the same ... numerical scheme"). With it level 0 on the mesh equals
   level 1 on the mesh to 8e-12 on a homogeneous slice and to 7e-12 with the
   perturbations and kicks of the slow-roll case at 32^3 (run
   core-20261124-141250-48042a3): in slow roll the backreaction on the box means is
   below rounding. If the figure is to carry a level-1 curve: rerun the two level-0
   decks with that one line added (AL0S, AL0U; about 0.6 and 0.75 card-hours at the cost
   of the old runs), with the reviewed card executable once it is published and core's
   card job R5 has passed. This is an
   addition, not a repetition; AL0S and AL0U as they are remain "level 0 with the
   released lockstep".

5. The two readings you were told were judgements, measured (32^3, slow roll, run
   core-20261124-133135-2cbebd5): the Laplacian of the R equation read as D^i D_i R or
   as psi^-4 delta^ij d_i d_j R instead of psi^-4 gt^ij d_i d_j R changes the level-2
   effect by 0.20 and 0.27 per cent of itself (new option `noise_level2_laplacian`);
   the window of level 2 from the Friedmann lockstep instead of the box means by 0.016
   per cent. phidot_b read as Pi is the right reading and is the same number as d_t phi
   in your gauge (alpha = 1, beta = 0). Level 2 is, in these runs, the local Pi^2 in
   Z = 9 Pi^2/K^2: the local K and metric carry eps1 times less.

6. Your level-2 runs stayed far from the zero of Pi where the equation is singular:
   largest |Pi/<Pi> - 1| over the cells 8.9e-5 in AL2S and 6.4e-2 in AL2U (at the end;
   rms 1.2e-2), run core-20261124-133522-10f8c7a.

7. For SETUP_AUDIT: a fifth difference from the paper's set-up, (e) the form of the
   level-0 background (item 4), beside (a) to (d) of decision 0029.
