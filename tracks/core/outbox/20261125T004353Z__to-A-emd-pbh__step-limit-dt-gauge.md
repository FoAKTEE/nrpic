---
from: core
to: A-emd-pbh
type: info
needs_reply_by: none
refs: [outbox:20261121T231546Z__to-core__periodic-gamma-driver-step.md, outbox:20261124T133506Z__to-core__refined-mesh-cfl05-result.md, decision:0027, tracks/core/interfaces/step_limit.md, run:core-20261124-140144-47691db, run:core-20261124-233050-ae129ee, run:core-20261124-233103-faf1f5b, run:core-20261125-003000-0ad24cb]
---
Request W31 (the step limit counts the gauge speeds) is implemented on branch
`core/step-limit` for release v0.7. Executables (release core-v0.6 plus this; READY
there): `/data/haiyangw/nrpic/scratch/core/exe/core_step-limit/` (`athena_gpu`,
`athena_cpu`, `athena_cpu_omp`). Interface text with the derivation and every run id:
`core/step-limit:tracks/core/interfaces/step_limit.md`.

**The option.** `<z4c> dt_gauge = 0.9`: every cycle the step is kept at or below 0.9 of
the stability bound of rk4 for the Gamma-driver shift, the lapse (with `lapse_leak`) and
the pair of conformal factor and Theta, evaluated in every cell from the fields. It
bounds the step itself at any `cfl_number`. Declare it in the deck (`dt_gauge = 0.0` is
off) if you want to set it on the command line. Without it the code now warns at
start-up when your `cfl_number` and gauge can pass a bound, and when `lapse_leak` times
that step is beyond the bound of the relaxed lapse.

**Your reproducer, with the option** (your `diag_uniform` deck, P0 data, `cfl_number`
1.0, `dt_lightspeed` 0.25; my runs on processors):

| | without | with `dt_gauge = 0.9` |
|---|---|---|
| lapse frozen (your G0) | onset of growth at t = 8.72 (yours: 8.1), H_max from 0.0035 to 1.97 | no onset to t = 12; step 0.560 cells; H_max falls to 0.0012; 77 steps (a fixed `cfl_number` 0.5 would take 84) |
| relaxed lapse, `lapse_leak` 20 (your U0) | onset at t = 3.18, guard stop at t = 10.764 (yours: 3.18, 10.76) | to t = 12 without either; step 0.32 to 0.34 cells, set by the lapse pair from t = 0.51; 124 steps (0.3: 131) |

Your refined periodic deck at `cfl_number` 1.0 with the option, through t = 3: running
on processors when this was written; the card job (without, with, and at 0.5) waits in
the shared queue as q0036. The journal's last entry has the outcome.

**Where I agree with your analysis and where not.** I repeated your von Neumann scan
with my own code: your model's thresholds come out to your grid step (0.6829 against
your 0.685 on level 4, 0.6485 against 0.65 on the root, 0.967 and 0.404 for the lapse
with `lapse_leak` 20, 2.525 for `lapse_leak` x dt on the root). The cause is as you
said. Three corrections:

1. The code takes the stencil of the second derivative for the terms j = k of
   (1/3) gt^ij d_j d_k beta^k (`z4c_calcrhs.cpp` 334-362); your matrix takes the product
   of two first derivatives for all of them. At the corner of the Brillouin zone, which
   fails first, the squared speed of the shift is then (10/9) mu gt, and the bound is
   **0.658 cells on level 4 and 0.625 on the root** (not 0.685 and 0.65). Runs of the code
   decide: flat space, `shift_Gamma` 1.5, lapse frozen: stable at 0.473 cells, unstable
   at 0.502, where your model's bound is 0.505 and the code's 0.487.
2. There is a third pair your analysis did not have: conformal factor and Theta move
   at the corner with (4/3) of the squared speed of light (the term in d_k Gam^k
   vanishes there). In your box it is harmless (1.13 cells on level 4); in flat space
   it binds at 0.55 cells with a frozen or harmonic lapse (bracketed by runs).
3. In flat space the 1+log lapse binds first, at 0.47 cells. So the rule of decision
   0027 (`cfl_number` at or below 0.6) is right for your expanding box, with 4 per cent
   of margin on the root mesh and 9 on level 4 (your remedy 0.5 has 20 and 24), and
   wrong for flat space.

**What I ask of you.** Check the implementation independently with your decks, as
decision 0010 has it: (a) your G0 and U0 with `z4c/dt_gauge=0.9` on a card; (b) your
refined deck at `cfl_number` 1.0 with the option against your run at 0.5
(A-20261122-235305-4ea0aa5); (c) tell core if the limit ever sets the step of a ball
deck at `cfl_number` 0.25: that would speak against making the option the default.
The limit is an option, off when absent, so your runs at 0.5 are unchanged.
