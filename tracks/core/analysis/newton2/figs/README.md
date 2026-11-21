# Figures and result files of work package newton2

Each figure (`.png`, `.pdf`) and its result file (`.json`) is the output of one
registered run of the script named, copied unchanged from `scratch/core/<analysis run>/`.
Scripts: `tracks/core/analysis/newton2/`. Manifests: `tracks/core/runs/<run id>/`.
Predictions and outcomes: `tracks/core/JOURNAL-newton2.md`.

| Stem | Test | Script | Case runs | Analysis run (source of the files) |
|---|---|---|---|---|
| `t1_fft` | T1: Fourier solver against multigrid, numpy, mixed radix | `t1_fft.py` | core-20261119-144414-c629377 | core-20261119-145129-e89a132 |
| `t2_pancake` | T2: Track B's pancake against Zel'dovich, n = 16, 32, 64 | `t2_pancake.py` (Track B's `analyze_pancake.py`) | core-20261119-150559-c1ff7ca; n = 64: card job core-20261119-145346-2f89b86 | core-20261120-222443-f0bc314 |
| `t3_groups` | T3: group history on the exact pancake | `t3_groups.py` | core-20261119-160919-c6a7279; card twin in core-20261119-145346-2f89b86 | core-20261120-222422-4ef2e80 |
| `t4a_generator` | T4a: deformed ball of `make_ic.py` against Track A's generator | `t4a_generator.py` | core-20261119-152228-0ad3c0e | core-20261119-152928-6be4984 |
| `t4b_embedded` | T4b, T4c: embedded ellipsoid, Fourier and multigrid, 64^3 | `t4b_embedded.py` | core-20261119-162746-a02d334, core-20261119-162455-e05ffa1 | core-20261120-222425-078bcc0 |
| `t4d_convergence` | T4d: embedded ellipsoid against kernels (64^3 only; 96^3 to 256^3 are in card job core-20261121-080215-df3af65) | `t4d_convergence.py` | the two of T4b; case emb64_pcs_fft of card job core-20261120-221835-4870ae5 | core-20261121-081511-37acd23 |
| `t5_infall` | T5: secondary infall onto the fixed point mass | `t5_infall.py` | core-20261119-165257-61d4b78 | core-20261120-222417-4ca3f76 |
| `t6_smr` | T6: ball across the level boundary, lattice 0.0625 | `t6_smr.py` | core-20261119-160027-2c0c171 | core-20261120-222437-191d56a |
| `t6b_smr` | T6b: ball inside the fine region, lattice 0.0625 | `t6_smr.py` | core-20261119-165447-0b9cb1e | core-20261120-222429-8971bdb |
| `t6c_coarse` | T6c: lattice of two cells on the uniform 64^3 mesh | `t6_smr.py` | core-20261120-221737-74eed8b | core-20261120-222151-512227c |
| `t6c_in` | T6c: lattice of the fine cell size, ball inside the fine region | `t6_smr.py` | card job core-20261120-221835-4870ae5 (decks: core-20261120-221659-da814e5) | core-20261121-081457-ac86529 |
| `t6c_x` | T6c: lattice of the fine cell size, ball across the level boundary | `t6_smr.py` | the same card job | core-20261121-081505-3fa1046 |
| `t7_energy` | T7: Layzer-Irvine drift against the step | `t7_energy.py` | core-20261119-153710-13876fa and the cases mg, fftsp of T1 | core-20261119-160023-99dc253 |
| `t8_selfforce` | T8: self-force of one particle against its place in the cell | `t8_selfforce.py` | core-20261119-152207-d4e656c | core-20261119-152742-a6810bd |
| `t10_regress` | T10: byte regression of the pre-merge build against the branch start and release core-v0.3 | `t10_regress.py` | core-20261119-152944-b2f41d3 | core-20261119-160915-40df1d6 |
| `card_judge` | card twins of T1 and throughput (T9), pre-merge card build | `card_judge.py` | card job core-20261119-145346-2f89b86 (decks: core-20261119-145326-d509829) | core-20261120-220427-5d8547f |
| `t11_merged` | T11a, T11b: merged processor build against release core-v0.5 and against the pre-merge build (the card panel is empty until job core-20261121-080215-df3af65 is judged) | `t11_merged.py` | core-20261121-080231-a98a070 (`analysis/release/regress_v04.py`), core-20261121-080229-0095e95 | core-20261121-080954-30dec42 |
| `ready_examples` | T12: example lines of READY with the published processor executable | `ready_examples.py` (runs its own cases) | - | core-20261121-081316-b153b46 |

Runs on record that produced no file here: analyses core-20261119-144855-2a2ef23
(started too early, failed), core-20261119-144933-515de0f (wrote outside its run
directory), core-20261119-162128-1cd17b2 (deck fault), core-20261121-081152-5fc1ea4
(comparison script divided by a zero column); card job core-20261120-221728-59d6e64
(stopped before it started); the first versions of several figures before layout
corrections (journal).
