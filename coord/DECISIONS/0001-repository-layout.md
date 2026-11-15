# 0001 Repository layout (D1)

Status: ACCEPTED (fixed by the existing repository) · 2026-11-15 · orchestrator

Decision. The program lives in the existing project repository (`origin` =
FoAKTEE/nrpic), which vendors AthenaK under `athenak/` (upstream commit c5a0d7f plus the
NRPIC additions; Kokkos is a submodule). This is the alternative of D1 in the brief: the
repository already holds 219 commits of the independent rebuild, its paper and the
cosmology extension, so it is not converted into a fork of AthenaK.

Mapping of the brief's paths (section 11.1) onto this repository:

| Brief | Here |
|---|---|
| `$NRPIC_HOME/repo` | the main checkout, `/data/haiyangw/nrpic` (branch `main`) |
| `$NRPIC_HOME/wt/<ID>` | `wt/<ID>` inside the main checkout (git-ignored) |
| `$NRPIC_HOME/kb-data`, `scratch`, `cache`, `locks` | `kb-data/`, `scratch/`, `cache/`, `locks/` inside the main checkout (git-ignored) |
| `src/`, `inputs/` | `athenak/src/`, `problems/` |
| `harness/`, `coord/`, `kb/`, `tracks/` | the same, at the top level |

Why the worktrees are inside the main checkout: the sessions of this program are agents
started by the orchestrator, and they may write only under the working directory of the
job. `git worktree add wt/<ID>` gives the same isolation of branch and index as a sibling
directory.

Consequence. A linked worktree has no Kokkos checkout; a session that builds runs
`git submodule update --init --reference <main checkout>/athenak/kokkos athenak/kokkos`
once in its worktree (wrapped by `harness/bin/nrpic-env`). Earlier outputs stay in `runs/`
(git-ignored); new registered runs go to `scratch/<ID>/<run_id>/`.
