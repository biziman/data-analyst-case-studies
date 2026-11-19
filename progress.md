# Progress — GH Showcases

## Current State

- Harness aligned with `~/projects/harness-kit` (hk:core refreshed) and
  `~/fedorka-soul` (context-budget rule, master/worker routing, shared
  resources, branch contract).
- `make check` runs the case-1 evidence gate (`make evidence`) plus the
  simulator gate; both pass.
- Repo-local analysis environment exists: `make setup` creates `.venv`
  (CPython 3.12, numpy, pandas 2.x, scipy, matplotlib 3.10.8 pinned, nbformat,
  nbclient). `.venv/` is ignored.
- Review pass is complete for all 11 cases. Cases 9–11 were reviewed on
  2026-11-19 and committed (case 11 `89088a9`, case 9 `ed28c22`, case 10
  `98358e5`; case-10 figure polished after).
- Case 10 gained its missing figure: `outputs/tiktok_test_interval.png`.
- Close-out (feat-004) is done locally: `TODO.md` is now a review record,
  the stale `linkedin-site` branch note is fixed, root README and CHANGELOG
  are updated. **The push is not done** — it waits on owner confirmation
  (BOUNDARIES.md: confirm before `git push`).

## Blockers

- feat-004: `git push` needs the owner's go-ahead. `main` is ahead of
  `origin/main` by the review commits.
- feat-007 (publish post 1): owner's date call. Post 1 is approved and
  unpublished; the review gate that blocked it is now passed.

## Next Action

- On owner approval: push `main`, then run `make verify-feature F=feat-004` to
  record it done.
- Then feat-008 (simulator copy and dial review) or feat-007 (publish post 1),
  one at a time (WIP=1).
