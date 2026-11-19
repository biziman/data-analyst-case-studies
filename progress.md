# Progress — GH Showcases

## Current State

- Harness aligned with `~/projects/harness-kit` (hk:core refreshed) and
  `~/fedorka-soul` (context-budget rule, master/worker routing added as perks).
- `make check` now runs the case evidence gate (`make evidence`): every case-1
  site fact is asserted against `docs/cases/01-mobile-game-acquisition/data/`,
  and `preview.png` regenerates byte-identically. It passes.
- `feature_list.json` is reorganized in delivery order with dependencies.
  Last completed: feat-009 (harness), feat-002 (simulator).
- Environment gap: there is no venv and system Python 3.15 has no numpy,
  pandas, scipy or matplotlib. Cases 9-10 cannot run until feat-005 lands.
  `uv` is installed; use it for a repo-local `.venv`.
- Branch: `main` is the delivery branch, 3 commits ahead of `origin/main`.
  `TODO.md` still says work happens on `linkedin-site` — stale, fix in feat-004.

## Blockers

- feat-005 (environment) blocks case 9 and case 10 review.
- feat-007 (publish post 1) waits on the owner's date call and on feat-004.

## Next Action

- Start feat-005 (reproducible analysis environment), then feat-006 (case 11
  review), then feat-001 (case 9), feat-003 (case 10), feat-004 (close-out).
