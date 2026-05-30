# Data Dictionary

| Table | Grain | Purpose |
|---|---|---|
| entities.csv | SKU family | Category, lifecycle, channel, revenue, margin, velocity, complexity, certification, fit, and rationalization score |
| daily_metrics.csv | SKU family x day | Booked revenue, orders, margin, quality, lead time, and daily risk signal |
| source_events.csv | event | Sales asks, quote signals, operational exceptions, engineering reviews, collateral gaps, and quality signals |
| recommended_actions.csv | action | Recommended product move, owner, effort, expected margin lift, revenue at risk, launch readiness, and next artifact |

## Scoring Fields

| Field | Meaning |
|---|---|
| `rationalization_score` | Weighted score using active SKU count, order velocity, margin gap, complexity, lead time, channel fit, and quality drag |
| `launch_readiness` | Composite readiness signal from strategic fit, channel fit, and lower complexity |
| `recommended_move` | Product decision category such as prune redundant variants, improve cost or pricing, refresh launch collateral, simplify stocked options, run launch readiness review, or monitor |
