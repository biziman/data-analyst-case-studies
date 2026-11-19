# Progress — GH Showcases

## Current State

- Harness aligned with `~/projects/harness-kit` (hk:core refreshed) and
  `~/fedorka-soul` (context-budget rule, master/worker routing added as perks).
- `make check` now runs the case evidence gate (`make evidence`): every case-1
  site fact is asserted against `docs/cases/01-mobile-game-acquisition/data/`,
  and `preview.png` regenerates byte-identically. It passes.
- `feature_list.json` is reorganized in delivery order with dependencies.
  Last completed: feat-009 (harness), feat-002 (simulator).
- Environment: repo-local `.venv` (CPython 3.12, `make setup`) with numpy,
  pandas 2.x, scipy, matplotlib 3.10.8, nbformat and nbclient. Cases 9-10 run
  through `.venv/bin/python`; see PREREQUISITES.md. System Python 3.15 still
  runs the stdlib cases and the evidence gate.
- Branch: `main` is the delivery branch, ahead of `origin/main`. `TODO.md`
  still says work happens on `linkedin-site` — stale, fix in feat-004.

## Blockers

- feat-007 (publish post 1) waits on the owner's date call and on feat-004.

## Next Action

- A worker takes feat-006 (case 11 review), then feat-001 (case 9), then
  feat-003 (case 10). The master does not start another feature while one is
  in-progress.
