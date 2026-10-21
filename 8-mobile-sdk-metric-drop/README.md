# Did the SDK release break DAU measurement?

> **Fictional portfolio case.** The game, incident, event records, and results are synthetic. This project does not describe a real employer or business outcome.

## Business question

A mobile game dashboard reports a DAU decline after a staged analytics SDK rollout. Should the team change acquisition or product plans, or investigate its event tracking first?

## Dataset

`data/events.csv` contains generated client events from 1 May through 14 June 2026. It has event and received timestamps (naive UTC for this simulation), user IDs, platform, app version, country, and acquisition channel. The deterministic generator injects:

- ordinary day-to-day variation in active users;
- an SDK rollout for Android on 12 May and iOS on 15 May;
- missing user IDs for a subset of upgraded players, plus a small pre-rollout background rate;
- retry duplicates on some post-rollout session-start events;
- longer event delivery delays after rollout.

`data/simulation_truth.csv` contains the known active-user totals used to validate this simulation. It is an evaluation oracle—not an input available to an analyst in a real incident.

Regenerate both files from this directory with:

```bash
python generate_data.py
```

## Analysis

Open `8-mobile-sdk-metric-drop.ipynb` in Jupyter. The notebook:

1. defines observed DAU as distinct non-null users with an `app_open` or `session_start` event;
2. compares observed DAU with the simulation truth;
3. checks missing IDs, retry rows, and event delivery delays by day and app version;
4. compares availability at a 24-hour snapshot with the final event-time count;
5. explains why a date-aligned change is not, by itself, causal evidence.

Install the notebook dependencies with `pip install -r requirements.txt`.

## Findings in the generated sample

The simulation keeps the underlying active-user count near its designed baseline. After both platforms roll out, observed DAU coverage is about 92% of simulated true DAU because 8% of upgraded players have missing IDs on all client events. The mean true DAU also varies slightly from day to day by design. Retry rows increase event volume but do not inflate the distinct-user DAU metric used here. Delayed events also make a 24-hour snapshot less complete than the eventual event-time count.

These are expected properties of the generator, not discoveries about a real game. Check the notebook outputs after regenerating the data; do not copy simulation figures into a CV as business impact.

## Recommendation in a real incident

Temporarily mark client-event DAU as provisional. Check ID completeness, duplicate handling, event delay, rollout coverage, and agreement with an independent server-side activity source. Do not alter UA budgets or product features based only on a degraded dashboard.

## Limitations

The rollout is not randomized. There is no real backend log, campaign-cost table, or experiment design. The simulation cannot prove the SDK caused a real decline or estimate business impact. A real investigation needs the event contract, rollout logs, server-side activity, and engineering validation.
