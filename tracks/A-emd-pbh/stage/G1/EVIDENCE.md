# Evidence of G1 of A-emd-pbh (lead, wave 2, 2026-11-15)

Criterion by criterion with run ids: `STATUS.md` (sections 1-2 and 6). The lead's check of
the wave-2 helpers: `../REVIEW-wave2.md`. Run manifests: `../../runs/<run id>/manifest.json`,
outputs under `/data/haiyangw/nrpic/scratch/A-emd-pbh/<run id>/`.

| Criterion | Main runs | Lead's check |
|---|---|---|
| T1 constraint residuals of A-pre-1 converge at the expected order | A-emd-pbh-20261115-121654-6bfb707, -122121-aa1c84d, -122117-aa1c84d | rerun A-emd-pbh-20261115-130402-f5566fb identical; verifier A-20261115-161239-1c41333 (own construction, orders 2 and 4), reproduced A-20261115-182514-3bb6846; time orientation by evolution (SR-1/SR-2, A-20261115-182314-bebd0cf) |
| T2 prediction table of A-pre-2 | A-emd-pbh-20261115-115120-2eb3117, -120425-80492f8; wave 2: -161543-36e461d, -162306-80396e4, -163358-9b2d048, -162303-80396e4 | reruns A-20261115-130252-01e8b64 (wave 1), A-20261115-182502-dae304d (wave 2) identical; source statements read (REVIEW section 3, criteria2) |
| T3 scan design from A-pre-3 (decision 0013) | `newton/SCAN.md`; wave 2 Newtonian-mode runs A-emd-pbh-20261115-153409/-153415/-153437-dc27b98, analysis -164420-4528861, range -164757-b8bc9a3 | rerun A-20261115-182402-a46812c identical; own estimator A-20261115-182314-bebd0cf |
| Analysis pipeline validated | runs_ball analyses A-emd-pbh-20261115-163659-4dbacd0, A-20261115-182657-53da696; periodic -171930-878a114 | reruns A-20261115-182200-532a5f6, A-20261115-182347-8ee3fcc identical; own reader A-20261115-182314-bebd0cf |

Figures looked at by the lead in wave 2 (PNG read): `runs_ball/figs/fig_resolution_summary.png`
(before and after the dx = M/4 runs), `sr2_n256_horizon.png`, `sr1_n256L32_fields.png`;
`periodic_threshold/figures/fig_scouting_histories.png`, `fig_t1_solve_change.png`;
`newton/figs/fig_newton_scan_summary.png`, `fig_newton_gr_range.png`; the lead's
`fig_review_wave2.png` (run A-20261115-182314-bebd0cf).

Null results and failed runs of wave 2 (kept on record): SR-1 non-finite before the
collapse; no horizon in SR-1/SR-2/S1/S2; S1 non-finite at 21.9 t_H; failed or superseded
analysis runs A-emd-pbh-20261115-162133-208f933, -162237-a614467, -161253-b8c1dc9,
-161542-36e461d, -162505-d32d331; stopped processor runs -153856-9d731b1, -153903-9d731b1,
-154356-527a6d1; the lead's own A-20261115-182021-6cb33de (time-offset bug) and
A-20261115-182329-ad14d95 (unexpanded output path). Refuted predictions are listed in
the helpers' journals and in `../REVIEW-wave2.md` section 2.
