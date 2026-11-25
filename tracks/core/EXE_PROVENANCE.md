# Provenance of core's published executables that were replaced in place

Core publishes tested executables under `scratch/core/exe/<name>/` (decision 0013), each with
COMMIT, SHA256SUMS and READY. **Rule from 2026-11-25: a published executable is never replaced
in place. Every publication gets a directory name of its own** (for example
`core_<branch>_<source commit 8>/`), and a later build goes to a new directory, so a run manifest
that names a path and a sha256 keeps resolving. The old name may keep a `PROVENANCE` file that
points at the newer directory; it never gets new binaries.

This file records the one known exception before the rule.

## scratch/core/exe/core_noise-level2/ (branch core/noise-level2)

[VERIFIED by `sha256sum` and `stat`, 2026-11-25T12:05Z, core lead, batch 17]

| Set | Source commit | Built | athena_gpu sha256 (bytes) | Where it is now |
|---|---|---|---|---|
| 1, superseded | 6ca93cbabfe6e11332d70579224d8d942c31735d (release core-v0.6 + level 2; in core-v0.7) | 2026-11-22 19:18 PST, wt/core-s2, `scripts/build_gpu.sh .work/build_gpu_nl2` (CUDA 12.6) | 468109496c825a40d1b76f0c3af7658c0d403518b25e7d02f99fb3cb1cc8acb9 (110564064) | `scratch/core/exe/core_noise-level2_6ca93cba/` (moved aside 2026-11-24 13:19 PST) and, as hard links to the same inodes, `scratch/core/exe/core_noise-level2/superseded/6ca93cba/`; `sha256sum -c SHA256SUMS` there: OK for all three |
| 2, current | 64f150ec (= 6ca93cba + 746869ef + 64f150ec, after the review of 2026-11-24) | 2026-11-24 06:12-06:26 PST, same build directories, rebuilt in place | d7069a4e09330f7a6a3cd6ce0383df19cdd5d34a5a46f54d15b5cc2b4f0ecc34 (110677168) | `scratch/core/exe/core_noise-level2/` |

Set 1 processor builds: athena_cpu 108e8065e5aee64e142dc0eab67623d4adcae6364c82f41991e7011b557a6b95
(268862592 bytes), athena_cpu_omp 7318cacab14b92a22c5136daff0b85a1cf6e6d69f86ba6eb8b9e7546ab97577b
(321405760 bytes). The build tree `wt/core-s2/.work/build_gpu_nl2` now holds set 2 (its
`src/athena` hashes d7069a4e...); set 1 exists only as the kept copies above.

### Track E's seven ablation runs (decision 0038 item 3)

Their manifests (branch track/E-stoch-inf) name `scratch/core/exe/core_noise-level2/athena_gpu`
with sha256 468109496c82..., which is set 1. The copy each run actually executed is still in its
own directory and hashes the same:

| Run | Launcher | Copy that ran | sha256 of the copy |
|---|---|---|---|
| E-20261123-035724-b661081 | batch | `batch.list.exe` (2026-11-22 19:57 PST) | 468109496c82... |
| E-20261123-152119-38957ba | chain | `chain/athena` (= `chain/nrc-9ee51fd0`, same inode) | 468109496c82... |
| E-20261123-153146-d965002 | chain | `chain/athena` (= `chain/nrc-4fa80fa7`) | 468109496c82... |
| E-20261123-153347-18e7c21 | chain | `chain/athena` (= `chain/nrc-fcf2bbe8`) | 468109496c82... |
| E-20261123-164235-49b0945 | chain | `chain/athena` (= `chain/nrc-6f20ccc0`) | 468109496c82... |
| E-20261123-183822-4abbcae | chain | `chain/athena` (= `chain/nrc-1975b85e`) | 468109496c82... |
| E-20261123-192948-348e2e5 | chain | `chain/athena` (= `chain/nrc-af45da37`) | 468109496c82... |

Each chain was started once (one "start/resume" line in `chain/events.log`, executable
`scratch/core/exe/core_noise-level2/athena_gpu`, copied at 07:21-11:29 PST on 2026-11-23, before
the replacement on 2026-11-24). So the seven runs used set 1, source 6ca93cba, as their manifests
say; the run check fails only because the file at the recorded path was replaced afterwards.

A run check can resolve such a manifest through `scratch/core/exe/core_noise-level2/PROVENANCE`
(the same facts as this table) or through the copy in the run directory.

Not checked: whether any other directory under `scratch/core/exe/` was rebuilt in place before
this rule (no `sha256sum -c` over all of them was run; about 19 GB) [TO VERIFY].
