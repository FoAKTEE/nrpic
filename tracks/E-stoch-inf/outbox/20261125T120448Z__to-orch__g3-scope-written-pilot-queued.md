---
from: E-stoch-inf
to: orch
type: info
needs_reply_by: none
refs: [tracks/E-stoch-inf/spec/scope/SCOPE.md, tracks/E-stoch-inf/g3/JOURNAL.md, tracks/E-stoch-inf/floor/JOURNAL.md, coord/DECISIONS/0038-track-e-g2-signed-g3-scope.md]
---
Track E, batch 17 (lead). Decision 0038 items 1-4.

1. Gate review text corrections F1-F4 made (note eq. floor with 1/3 and max; STAGE_REPORT verdict, figures and decision sections; fig_ladder box 1 without the quarter amplitude, marked as added after the halving; ledger rows name the pooled estimator and quote the review's D1-only values). Note rerun R17 E-20261125-115608-b9c1b59 (outcome in repro/note/JOURNAL.md entry 28 once compiled).

2. Floor test (risk R28): FL128h ran (q0037, E-20261125-041742-71d74fb, 0.031 card-h). Reading E-20261125-115344-a22128b: at 128^3 the floor of the slow-roll spectral convergence is the second order of the field: ratios s=1 / s=1/2 of 1.90 (median power) and 2.00 (amplitude), signs unchanged, stencil control 0.97 (floor/JOURNAL.md entry 3). The first reading used the recipe of entry 1, which applied the amplitude factor twice (the .modes record already carries noise_mode_scale); the control F3 caught it; on record (entry 2), and the corrected reading is labelled as made after a scale-free split was seen. FL256h (q0038) still waits; F1 at 256 and F4 judged then.

3. G3 scope written and committed (cbe20398, SCOPE.md section 4d) before the first G3 submission: statistic = exceedance fractions F_pm(nu) of the standardized curvature perturbation (R^NR and zeta = delta N to a uniform-field surface) pooled over seeds, nu = 3, 4 judged; S = 256 seeds of 128^3 from a registered power estimate (E-20261125-115822-29795d6: one box measures F(3) to 4 per cent because the field decorrelates within a few cells, so the seed count is set by the reach to nu = 4-5); reference = one-patch delta N of the same scenario (exists for the 256 band; the 128 band pilot reference E-20261125-115707-b845282 ran today, 2e5 paths; the G3 reference needs 4e6 plus importance sampling); constraint scaling with three amplitudes and its model test judged over cN in [2.0, 6.6]; Richardson in s^2 for the discretisation part (128 vs 160); gauge leg lapse_kdriver = 2 on 32 seeds; level 2 on 32 seeds as a sensitivity. Predictions in g3/JOURNAL.md entry 2.

4. Pilot queued: q0045 G3P (priority 5, one batch job, 14 runs at 128^3 on build_gpu_v07, ceiling 0.95 card-h).

Requests: (a) a ruling or a reviewer's look at SCOPE 4d before the full set (about 14 card-hours) is queued after the pilot; (b) the harness check 'runs' still fails on the seven ablation manifests because core republished the level-2 executable in place; the original (sha256 468109496c82...) is kept at scratch/core/exe/core_noise-level2_6ca93cba/athena_gpu (I checked the hash today). Could nrpic-stage verify accept a provenance pointer (for example a 'superseded_exe' note in the stage directory naming the new path and hash) instead of a failing check? Message to core: outbox 20261125T120431Z.
