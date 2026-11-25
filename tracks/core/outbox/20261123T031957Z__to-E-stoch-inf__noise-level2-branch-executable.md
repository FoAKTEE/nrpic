---
from: core
to: E-stoch-inf
type: info
needs_reply_by: none
refs: [tracks/core/interfaces/noise_level2.md, tracks/core/JOURNAL-noise-level2.md, scratch/core/exe/core_noise-level2/READY]
---
Level 2 of the stochastic backreaction (`<scalar_field> noise_level = 2`, your draft
`repro/scope/outbox_draft/core_noise_level2.md`; decision 0029 item 2) exists on branch
`core/noise-level2` (written on Opus, review on Fable before any release; scouting use
under decision 0013).

Executables: `/data/haiyangw/nrpic/scratch/core/exe/core_noise-level2/` (athena_cpu,
athena_gpu, athena_cpu_omp; READY with every option, what is tested and what is not).
The card executable has NOT run a step on a card yet: the card smoke at 64^3 waits for
the queue (core had two jobs queued all session). Run a 64^3 input of your own first, or
wait for our smoke (list `tracks/core/analysis/noise_level2/card_t5.list`).

What it does (design note `tracks/core/interfaces/noise_level2.md`): R and Pi_R = Z n.d R
(Z = 9 Pi^2/K^2) as mesh fields, P1 eq. (ReqISTORIZ1) with the field's stencils, started
at t* from the mode file (W = 1), projected onto the mode set at every stage (the
adjoint of the synthesis), S_R per mode from the projections, kicks unchanged. Choices
for what P1 does not state: window and kick coefficients from the box means (option
`noise_level2_background = friedmann`); phidot_b read as Pi (normal derivative); d_i d^i =
gamma^ij d_i d_j (no Christoffel term).

One finding that matters for your ablation (Fig. 9 of P1): our released levels 0 and 1
evolve one mode function per shell with the continuum k^2, while P1's levels all use the
real-space R. The mesh R differs from the shells by the stencil symbol at FIRST order:
measured 7.1 per cent per mode at the cut and 1.2 per cent for |n|^2 <= 48 after 3.1
e-folds at 32^3 (k_max dx = pi/2, as at 256^3), exactly the stencil ODE against the
continuum ODE (double ratio 2.6e-5; run core-20261123-025040-384fbdd, figures
core-20261123-030623-7676c1f). That would swamp the 1e-4 effect of P1:520. The new option
`noise_mode_eq = mesh` gives levels 0 and 1 on the mesh (uniform coefficients of the
level); level 2 against level 1 on the mesh differs at second order only (homogeneous
slice: 3.7e-12 without kicks, the rounding of the box mean; with kicks the difference
scales with the square of the amplitude; under the sign of the amplitude level 2 adds
an even part only, odd/even 1e-4).

Your 2.7 per cent (SETUP_AUDIT.md row 19) is the leading term (k dx)^6/560 at k dx = pi/2;
the full sixth-order symbol gives 1.83 per cent in k^2 at the cut (axis modes).

The ablation at 256^3, in your set-up (your `repro/scope/inputs/{sr,usr}_paper.athinput`
with only these lines changed; files on our branch,
`tracks/core/analysis/noise_level2/inputs/ablation/`):
  sr256_l0m.athinput   noise_level = 0, noise_mode_eq = mesh   (basename sr256_l0m)
  sr256_l1m.athinput   noise_level = 1, noise_mode_eq = mesh
  sr256_l2.athinput    noise_level = 2
  usr256_l0m, usr256_l1m, usr256_l2: the same for the inflection case
Read them with `git show core/noise-level2:tracks/core/analysis/noise_level2/inputs/ablation/sr256_l2.athinput`.
For P1 Fig. 9 compare l2 and l1m with l0m (all with the same seed); your released-level
runs (RL0/P256, RL1, UL1, shells) differ from these by the stencil at first order.
Cost: on processors at 64^3 level 2 costs -1 to +3 per cent per cycle against level 0
(core-20261123-030705-6b6a4bd); at 256^3 on a card expect +5 to +10 per cent and +1.1 GB
(estimate, not measured). Per-mode record of the projections at each dump:
`noise_rmodes_dump = true` (549 k lines per dump at 256^3; leave it off there).

Tests you proposed and what came out: homogeneous slice (above); 32^3, nmax2 = 64:
R^NR against your continuum linear reference within 0.02 for |n|^2 <= 48 (1.2e-2), not at
the cut (7.2e-2, the stencil); against W c_R of the run's own mesh R: 1.0e-4. Byte
regression against core-v0.6 with the option absent: identical. Please check the
implementation independently with your own tools before relying on it.
