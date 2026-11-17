# Metric-contract simulator: build brief

Build one interactive page that teaches how metric definitions change a
decision. It is a standalone tool page on the static portfolio site, in the
spirit of FutureProof's data-drift simulator, but about measurement contracts
instead of drift.

## Done-state

A reader opens `docs/tools/metric-contract/` and, in eight guided steps, watches
the same checkout test produce opposite answers. Each step has one dial, one
prediction gate, and one sentence to keep. The last step is a scored sandbox.
The page is static, deterministic, and every quoted number comes from the
generator with asserts that fail on drift.

## Non-goals

- No backend, no build step, no framework, no analytics, no login.
- No new case study. This is a tool page, not case 12.
- No generic statistics course. One story, one dataset.
- Do not touch `feat-001` (cases 9-11 review pass). It stays `planned`.

## Where things live

- `docs/tools/metric-contract/index.html` and `page.css`, `page.js`
- `docs/tools/metric-contract/data/sim.json` (generated; commit it)
- `docs/tools/metric-contract/preview.png` (headless screenshot)
- `scripts/sim/generate_metric_contract.py` (seeded generator)
- `scripts/sim/verify_metric_contract.py` (asserts, wired into `make check`)
- Small edits: `docs/index.html` (one card/link), `Makefile` (one line),
  `feature_list.json` (`feat-002`, `in_progress`), `progress.md`, `CHANGELOG.md`

Shared assets are at `docs/assets/` (`style.css`, `theme.js`,
`plotly.min.js`). Load them with `../../assets/...`. Keep the site's palette and
light/dark toggle behaviour.

## The story and the data

A donation checkout A/B test. Control shows preset gift amounts; treatment
removes them. Traffic is 50/50, about 4,000 visitors a day, six weeks.

Ground truth is built into the generator, not asserted by prose:

- Control: donation rate 3.2%, mean gift $38.
- Treatment: donation rate 3.6% (+12.5%), mean gift $33 (-13%).
- Revenue per visitor therefore falls about 2.3%.
- Sessions per visitor are equal across variants.
- Treatment donors convert sooner but not more in total over 7 days.
- D7 repeat donation has no true effect.
- A second null test (email subject line) has no true effect at all.

Tune these parameters if the mechanics require it. Never hardcode a derived
number in HTML or prose. Read it from `data/sim.json` or from the assert module.
The verify script prints how many assertions passed; do not quote a count in
prose.

## Step script

Each step: left pane narrative, one control, one prediction gate, one idea to
keep, one "try this". Next stays disabled with a sublabel until the gate action
happens (`Press play first`, `Pick an answer first`, `Make your guess first`).

| # | Title | Dial | Prediction gate | Idea to keep |
|---|-------|------|-----------------|--------------|
| 1 | Two numbers, one decision | none (play only) | "Is a higher donation rate the same as more money?" | A conversion win is not a money win. Read the metric the decision needs. |
| 2 | The denominator decides | per visitor / session / donor | "Which denominator makes the treatment look best?" | A metric is a contract: numerator, denominator, window, population. State it before the test. |
| 3 | The window decides | 1h / 24h / 7d | "Does the revenue lift survive a 7-day window?" | A win that decays with the window was timing, not money. |
| 4 | Mature cohorts only | all cohorts / mature only | "Repeat rate drops in the final week. Is that real?" | You cannot compare a cohort that has not had time to happen. |
| 5 | Peeking invents winners | daily / fixed 28 days / always-valid | "With no true effect, how often does daily checking declare a winner?" | The stopping rule is part of the design, not an operational detail. |
| 6 | Twelve metrics, one "win" | 1 primary / 12 guardrails | "With 12 null metrics, what is the chance at least one flags?" | Pre-register the primary metric. Everything else is exploratory. |
| 7 | A new sample is the judge | four contract presets | "Which of these contracts will still hold?" | A contract that works once is a coincidence. A holdout tests the test. |
| 8 | Sandbox: price your contract | denominator, window, stopping rule, ship threshold | none | Measurement choices have a price. Pay it knowingly. |

Step 2 must show three different lifts from one dataset; step 3 must show the
lift decay; step 4 must show a false decline that disappears with mature
cohorts; step 5 must show a false-winner rate near one in four for daily
checking against 5% for the other two; step 6 must show about 46% for 12 nulls;
step 7 must show the selected guardrail flipping on the holdout.

The sandbox score is expected dollars lost per 100k visitors across 200
day-bootstrap replays, measured against the true effect (regret). Show the score
live when a dial moves. Do not require pressing play to see it. Pick a
challenge sentence from the computed numbers, not a hand-written threshold.

## UI behaviour

- Two columns on desktop: narrative left (~40%), simulation right. One column
  below 900px, narrative first.
- Sim header: `Day N`, week, one-line state narration, play/pause, 1x/4x.
- Main chart: the selected metric over 42 days, control vs treatment, shaded
  band for outcomes not yet due, event annotations where the scenario changes.
- Scrub: dragging the timeline redraws the state at that day. Playback is a
  redraw loop, not a canned animation.
- Step progress: eight marks, current step filled.
- A `New control` chip on the step that introduces a dial.
- Keyboard: space toggles play, arrows scrub, every control reachable by Tab.
- `prefers-reduced-motion`: start paused, no auto-advance.
- Theme: follow the site's `data-theme` and the existing toggle. Charts must
  re-render on theme change (see `docs/assets/widgets.js` for the pattern).
- Charts: Plotly is vendored, but a small hand-drawn SVG is acceptable and
  likely simpler for the scrub/play loop. Pick one and keep it consistent.
- No network requests. No external fonts.

## Data and evidence gate

`scripts/sim/generate_metric_contract.py`:
- Visitor-level simulation: each visitor gets sessions, a donation, a gift and a
  delay; every aggregate on the page is summed from those visitors.
- Fixed seed `20261116`. Python stdlib only (numpy is not installed).
- Writes `docs/tools/metric-contract/data/sim.json`, target under 250 KB.
- Contains daily per-variant counts by window, the maturity series, 400 null-test
  replays with daily counts, 400 replays of 12 null guardrails, holdout rows, and
  the sandbox regret grid.
- Deterministic: rerun produces byte-identical output. Assert that in the
  verify script (hash or equality).

`scripts/sim/verify_metric_contract.py`:
- Recomputes the facts from the JSON and asserts: conversion lift > 0, revenue
  per visitor lift < 0, denominator ordering, window decay ordering, the
  maturity false decline, daily-peek false-winner rate in [0.16, 0.34],
  fixed-horizon and sequential rates < 0.09, one-metric and 12-metric flag
  rates, the selected guardrail flipping on the holdout, and the sandbox regret
  ordering.
- Prints `N assertions passed`. Exits 1 on any failure.
- Wire it into `make check` and into `feat-002.verification`.

## Budget and stop rule

Model: `openai-codex/gpt-6-luna`, thinking medium. It is the cheapest model on
that provider ($0.10 / $0.50 per M input/output, $0.01 per M cached read,
$0.125 per M cache write) with a 272K context window.

Grounding: the 2026-11-06 site session in this repo used 197 tool calls, 2.08M
fresh input, 29.4M cached read and 289K output, about $0.65 at these rates.

- Target: <= 150 tool calls, <= 2.5M fresh input, <= 30M cached read, <= 300K
  output. Expected spend $0.55-0.75.
- Hard stop at 220 calls, 3.5M fresh input, 40M cached read or 400K output,
  whichever comes first. Stop and report instead of pushing through.
- Keep the session under 272K context. Above it the input price doubles. If
  context is climbing past 200K, summarise state into the todo list instead of
  carrying history.
- Run `cost_report` (scope `session`) when the build is done and report the
  numbers.
- Read files once. Use offset/limit. Batch edits per file. No web research. No
  rereading the same file to "refresh context".
- One verification round: run the gate when the build is complete, fix only
  what it reports, then stop.

## Checks and commit

1. `make check` (includes the new verify script).
2. `python3 scripts/sim/verify_metric_contract.py`.
3. Headless acceptance pass: `node scripts/sim/acceptance.mjs` (serve `docs/`
   first). It clicks through all eight steps, checks that every dial changes the
   readout, checks the sandbox score reacts, fails on console errors, and writes
   `preview.png`. Mobile at 390x844 is a screenshot check. Use the local
   Playwright:
   `/var/home/kg/.pi/agent/npm/node_modules/playwright/index.mjs` with
   `/var/home/kg/.cache/ms-playwright/chromium-1248/chrome-linux64/chrome`.
   Serve with `python3 -m http.server` in `docs/` or use a `file://` load that
   tolerates the fetch. If the fetch needs HTTP, serve it.
4. `git status` clean of unrelated files. Commit explicit paths only, never
   `git add -A`. Message: `Add metric-contract simulator: 8-step page, scored
   sandbox, asserted data`.
5. Update `progress.md` and `CHANGELOG.md` (newest first, dated 2026-11-16) with
   your own lines only.

## Report at end

Send one intercom message to `gh-showcases-simulator4portfolio-plan`
(`01a1e585`) with: files added, gate result, screenshot path, calls and cost
used, and anything a reviewer must check by eye. If blocked or over budget, send
the same message and stop.
