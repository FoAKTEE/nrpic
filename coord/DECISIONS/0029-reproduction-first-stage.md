# 0029 Reproduction of the two papers: rulings after the first stage

Status: ACCEPTED · 2026-11-22 · orchestrator (decision 0017)

First stage (packages `tracks/E-stoch-inf/repro/{scope,langevin,equations}`, batch R1):

1. arXiv:2512.14649. Every figure, Table I and 33 statements are mapped to runs
   (`repro/scope/REPRO_MAP.md`); 26 items of the set-up are audited
   (`SETUP_AUDIT.md`). Four items differ from the paper: (a) Z4c with the damping off
   where the paper evolves BSSN: the solutions differ by terms proportional to the
   constraints; (b) the stochastic backreaction: the paper's runs use its level 2, the
   code has levels 0 and 1; the paper bounds the effect on the spectrum by one part in
   ten thousand; (c) the mode equation of the noise: per-shell mode functions with the
   continuum wavenumber where the paper evolves R in real space with the lattice's
   gradients (2.7 per cent in k^2 at the cut); (d) the start of the highest slow-roll
   shells. The missing card runs are queued (eight, about four card-hours).
2. Level 2 of the backreaction is a new option of the source (`<scalar_field>
   noise_level = 2`: R and its momentum as mesh fields with local coefficients, which
   also gives item (c) the paper's form). It is needed for the paper's ablation figure
   and for runs "as in the paper". The weekly usage window does not hold a source session
   on Fable before its reset, so the option is written now on Opus (the user's rule:
   Opus when Fable has run out) on a branch of its own, `core/noise-level2`, with tests
   and a branch executable (decision 0013); it enters a release only after a review of
   the diff on Fable. The working note says which executable each run used.
3. arXiv:2401.08530. The four figures of its section V are remade. Two findings go into
   the note as findings, with their evidence: the paper's background reaches the slope of
   its potential only when integrated with a forward Euler step of 0.01 e-folds (the
   converged background stops on the plateau), and its figures are matched by the Ito
   reading of the printed equations at that step, not by the Stratonovich reading the
   text names. Seventeen misprints of the two papers are listed with the check that shows
   each (`repro/equations/ERRATA.md`); none is inherited by the code. Not confirmed: the
   noise amplitude of its appendix D in ultra-slow roll, and the factor of the Ito term.
   A fresh verifier checks these claims before the note states them.
4. Second stage, when the card runs have ended: the figures of arXiv:2512.14649 from the
   runs, the working note with the updated skill, a fresh verifier, a correction pass.
