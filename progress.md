# Progress — GH Showcases

## Current State

- Harness aligned with `~/projects/harness-kit` (hk:core refreshed) and
  `~/fedorka-soul` (context budget, master/worker routing, shared resources).
  Feature statuses now include `blocked` (prepared work waiting on an external
  actor, counted as started but not occupying the WIP slot).
- `make check` runs the case-1 evidence gate (`make evidence`) plus the
  simulator gate; both pass.
- Environment: `make setup` builds `.venv` (CPython 3.12, numpy, pandas 2.x,
  scipy, matplotlib 3.10.8 pinned, nbformat, nbclient). `.venv/` is ignored.
- All 11 case reviews are done. Cases 9–11 were reviewed on 2026-11-19
  (commits `89088a9`, `ed28c22`, `98358e5`); case 10 gained its missing figure.
- Simulator copy/dial review is done (feat-008): 18 browser acceptance checks
  passed, preview byte-identical, two copy fixes (step 3 window wording,
  ambiguous step 7 gate).
- Publishing calendar re-planned: post 1 Fri 2026-11-20, then Tue/Fri through
  Tue 2027-01-05. Ten posts in 2026. Dates live in `LINKEDIN_PLAN.md`,
  `scripts/cases/*.json` and `docs/index.html`.
- `main` is pushed and level with `origin/main`.

## Blockers

- feat-007 (publish post 1): prepared and scheduled for 2026-11-20; waits on
  the owner's manual post, then the tracking row and Featured pin.
- GitHub Pages still serves `linkedin-site`; flipping it to `main/docs` waits on
  the owner's approval after feat-008 (now passed).

## Next Action

- After the post: record the URL, pin to Featured, run
  `make verify-feature F=feat-007`.
- Then flip Pages to `main/docs` and verify the simulator page loads.
