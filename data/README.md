# Data Sources

This project uses synthetic, source-style data. It does not represent any real company performance.

The synthetic structure is modeled on common architectural lighting portfolio patterns: product families, lifecycle stages, long-tail SKU variants, quote activity, order velocity, lead time, certification burden, sample demand, channel fit, and collateral readiness.

- `entities.csv`: 40 SKU family records across lighting and acoustic product categories.
- `daily_metrics.csv`: 7,200 SKU family-day metric rows.
- `source_events.csv`: operating events, sales asks, quality signals, collateral gaps, and engineering reviews.
- `recommended_actions.csv`: one action recommendation per SKU family.

The data can be regenerated with:

```bash
python3 scripts/generate_synthetic_data.py
```
