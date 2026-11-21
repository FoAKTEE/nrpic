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

## Close-out, wave 3 (g1close helper, 2026-11-20)

| What | Runs | Where |
|---|---|---|
| Fresh verifier of G1 (C18): ledger of the note, criteria checks, newton/, runs_ball | A-20261119-142905-c813c01 | `VERIFIER.md`, `verifier/`, `figs/` |
| Data-flow schematic (C11) | A-20261119-143347-37240f3 | `note/figures/schem_dataflow.png`, Fig. 7 of the note |
| The verifier's findings checked at their sources (median, bang times, units, criteria tallies, Newtonian band) | A-20261120-222454-d16dbc6 | `../../g1close/JOURNAL.md` entry 2, `findings.json`, `fig_g1close_findings.png` |
| Integrity of the wave-1 outputs behind the ledger (VERIFIER.md finding 7): sha256 of the 55 files of the seven run directories without `sha256sums.txt` (A-emd-pbh-20261115-120425-80492f8, -122117-aa1c84d, -130256-a7374a4, -130402-f5566fb, -130609-947c898, -161813-6c820fb, -163358-9b2d048); the eight directories with one verified, 0 mismatches; nothing written into the listed directories | A-20261120-222620-0304d9d | `../../g1close/JOURNAL.md` entry 3; listing `scratch/A-emd-pbh/A-20261120-222620-0304d9d/` |
| Note v1 (figures, schematics, ledger, parameter table, claims check) | A-20261120-223316-92c27f5, A-20261121-030037-3f015fa (the committed copies) | `note/`, `../../g1close/JOURNAL.md` entries 5-7 |

## Hand-written manifests of waves 1 and 2 (decision 0016 item 3)

The package relies on these runs, whose manifests were written by hand before 2026-11-19
(besides those named above and in `../G0/EVIDENCE.md`); their failures of the manifest check
are waived by that decision. Listed in full because a range such as "-153409/-153415" is not
expanded by `nrpic-stage verify`.

- Note v0: A-20261115-161947-09324e1.
- Lead's reruns of wave 1 (failed, on record): A-emd-pbh-20261115-125932-574c747, A-emd-pbh-20261115-125932-779f753.
- Newtonian mode (T3): A-emd-pbh-20261115-153409-dc27b98, A-emd-pbh-20261115-153415-dc27b98, A-emd-pbh-20261115-153424-dc27b98, A-emd-pbh-20261115-161309-9d3703a, A-emd-pbh-20261115-161537-aa788d9, A-emd-pbh-20261115-162554-d32d331, A-emd-pbh-20261115-164220-dd9fec7, A-emd-pbh-20261115-164450-4528861.
- Expanding ball, SR-1/SR-2 (analysis pipeline): A-emd-pbh-20261115-153719-91b03d1, A-emd-pbh-20261115-153843-7172b66, A-emd-pbh-20261115-153845-7172b66, A-emd-pbh-20261115-155056-ec1b816, A-emd-pbh-20261115-162359-d32d331, A-emd-pbh-20261115-163141-73eb185, A-emd-pbh-20261115-164353-96e301d, A-emd-pbh-20261115-164539-0b18e84, A-emd-pbh-20261115-164541-0b18e84, A-emd-pbh-20261115-164733-b2aaf0c.
- Criteria (T2): A-emd-pbh-20261115-161813-6c820fb, A-emd-pbh-20261115-162524-d32d331, A-emd-pbh-20261115-163443-c0b21e5.
- Periodic box (set-up tests and scouting runs named in note Sec. V): A-emd-pbh-20261115-153520-0576e01, A-emd-pbh-20261115-153527-0576e01, A-emd-pbh-20261115-154250-527a6d1, A-emd-pbh-20261115-154735-69e8f8b, A-emd-pbh-20261115-154740-69e8f8b, A-emd-pbh-20261115-155737-8422a4a, A-emd-pbh-20261115-155754-8422a4a, A-emd-pbh-20261115-155802-9a6596f, A-emd-pbh-20261115-160349-9d232d2, A-emd-pbh-20261115-160557-962be1a, A-emd-pbh-20261115-160718-e04c0cc, A-emd-pbh-20261115-161134-f3949f8, A-emd-pbh-20261115-161829-dba94f6, A-emd-pbh-20261115-170751-a2287be.
