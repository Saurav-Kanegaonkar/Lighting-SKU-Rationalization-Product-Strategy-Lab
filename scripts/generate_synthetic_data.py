import csv
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUTS = ROOT / "analysis" / "outputs"

random.seed(47)

categories = [
    ("Recessed Linear", "Specification", 0.73, 0.50, 0.45),
    ("Suspended Linear", "Specification", 0.70, 0.48, 0.42),
    ("Architectural Downlights", "Specification", 0.78, 0.44, 0.35),
    ("Acoustic Pendants", "Acoustic", 0.68, 0.58, 0.52),
    ("Acoustic Baffles", "Acoustic", 0.63, 0.61, 0.57),
    ("Healthcare Luminaires", "Healthcare", 0.74, 0.54, 0.49),
    ("Contractor Packages", "Contractor", 0.82, 0.34, 0.28),
    ("Controls Ready Kits", "Connected", 0.66, 0.56, 0.61),
]

lifecycles = ["Launch", "Growth", "Core", "Mature", "Decline"]
channels = ["Agent", "Distributor", "Contractor", "Specifier", "Healthcare"]
owners = ["Product", "Sales", "Operations", "Engineering", "Marketing"]


def clamp(value, low, high):
    return max(low, min(high, value))


def currency(value):
    return round(value, 2)


def rationalization_score(row):
    long_tail = clamp((row["active_skus"] - 18) / 55, 0, 1)
    weak_velocity = clamp((18 - row["order_velocity"]) / 17, 0, 1)
    margin_gap = clamp((0.38 - row["gross_margin_pct"]) / 0.18, 0, 1)
    complexity = row["complexity_index"] / 100
    lead_time = clamp((row["lead_time_days"] - 12) / 28, 0, 1)
    channel_pull = 1 - row["channel_fit"] / 100
    quality_drag = clamp((row["return_rate"] - 0.018) / 0.06, 0, 1)
    score = (
        long_tail * 22
        + weak_velocity * 18
        + margin_gap * 18
        + complexity * 14
        + lead_time * 10
        + channel_pull * 10
        + quality_drag * 8
    )
    return round(clamp(score * 1.65, 0, 99), 1)


def action_for(row):
    score = row["rationalization_score"]
    if score >= 70:
        return "Prune redundant variants"
    if row["gross_margin_pct"] < 0.34 and row["order_velocity"] >= 10:
        return "Improve cost or pricing"
    if row["sample_requests"] > 115 and row["quote_win_rate"] < 0.31:
        return "Refresh launch collateral"
    if row["lead_time_days"] > 25:
        return "Simplify stocked options"
    if row["lifecycle"] == "Launch":
        return "Run launch readiness review"
    return "Monitor in quarterly review"


def generate_entities():
    rows = []
    family_id = 1
    for category, platform, velocity_base, complexity_base, launch_base in categories:
        for variant in range(1, 6):
            lifecycle = random.choices(lifecycles, [0.13, 0.22, 0.31, 0.24, 0.10])[0]
            channel = random.choice(channels)
            lifecycle_modifier = {
                "Launch": 0.78,
                "Growth": 1.10,
                "Core": 1.24,
                "Mature": 0.92,
                "Decline": 0.55,
            }[lifecycle]
            active_skus = int(clamp(random.gauss(24 + complexity_base * 38, 9), 8, 78))
            revenue = currency(random.uniform(120000, 980000) * lifecycle_modifier * velocity_base)
            gross_margin_pct = round(clamp(random.gauss(0.37 + random.uniform(-0.04, 0.05), 0.045), 0.22, 0.53), 3)
            order_velocity = round(clamp(random.gauss(10 + velocity_base * 12, 4.2) * lifecycle_modifier, 1.2, 31), 1)
            quote_count = int(clamp(random.gauss(85 + velocity_base * 80, 30), 18, 230))
            sample_requests = int(clamp(random.gauss(35 + launch_base * 120, 28), 8, 190))
            quote_win_rate = round(clamp(random.gauss(0.33 + velocity_base * 0.08, 0.06), 0.16, 0.58), 3)
            return_rate = round(clamp(random.gauss(0.018 + complexity_base * 0.036, 0.014), 0.004, 0.096), 3)
            lead_time_days = int(clamp(random.gauss(10 + complexity_base * 28, 7), 5, 45))
            complexity_index = int(clamp(random.gauss(30 + complexity_base * 70, 12), 18, 96))
            cert_count = int(clamp(random.gauss(2 + complexity_base * 6, 1.5), 1, 11))
            channel_fit = int(clamp(random.gauss(67 + velocity_base * 20 - complexity_base * 12, 10), 32, 96))
            strategic_fit = int(clamp(random.gauss(58 + launch_base * 33, 12), 25, 98))
            row = {
                "entity_id": f"SKU{family_id:03d}",
                "entity_name": f"{category} Family {variant}",
                "category": category,
                "platform": platform,
                "lifecycle": lifecycle,
                "primary_channel": channel,
                "owner": random.choice(owners),
                "active_skus": active_skus,
                "annual_revenue": revenue,
                "gross_margin_pct": gross_margin_pct,
                "order_velocity": order_velocity,
                "quote_count": quote_count,
                "sample_requests": sample_requests,
                "quote_win_rate": quote_win_rate,
                "return_rate": return_rate,
                "lead_time_days": lead_time_days,
                "complexity_index": complexity_index,
                "certification_count": cert_count,
                "channel_fit": channel_fit,
                "strategic_fit": strategic_fit,
            }
            row["rationalization_score"] = rationalization_score(row)
            row["recommended_move"] = action_for(row)
            rows.append(row)
            family_id += 1
    return rows


def write_csv(path, rows, fieldnames):
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def generate_daily_metrics(entities):
    rows = []
    for entity in entities:
        for day in range(1, 181):
            season = 1 + 0.12 * math.sin(day / 18)
            revenue = float(entity["annual_revenue"]) / 180 * random.uniform(0.62, 1.42) * season
            orders = max(0, round(entity["order_velocity"] / 5 * random.uniform(0.25, 1.65), 1))
            margin = clamp(entity["gross_margin_pct"] + random.gauss(0, 0.018), 0.18, 0.56)
            quality = clamp(100 - entity["return_rate"] * 420 - random.uniform(0, 12), 55, 99)
            rows.append(
                {
                    "entity_id": entity["entity_id"],
                    "period_day": day,
                    "booked_revenue": currency(revenue),
                    "orders": orders,
                    "margin_pct": round(margin, 3),
                    "quality_score": round(quality, 1),
                    "lead_time_days": int(clamp(random.gauss(entity["lead_time_days"], 3), 3, 55)),
                    "risk_score": round(entity["rationalization_score"] * random.uniform(0.78, 1.14), 1),
                }
            )
    return rows


def generate_events(entities):
    event_types = ["Sales ask", "Customer quote", "Ops exception", "Engineering review", "Collateral gap", "Quality signal"]
    rows = []
    event_id = 1
    weighted_entities = sorted(entities, key=lambda row: row["rationalization_score"], reverse=True)
    for entity in weighted_entities:
        count = int(clamp(2 + entity["rationalization_score"] / 10 + random.gauss(0, 1.5), 2, 13))
        for _ in range(count):
            event_type = random.choice(event_types)
            impact = currency(random.uniform(5500, 52000) * (1 + entity["rationalization_score"] / 100))
            rows.append(
                {
                    "event_id": f"EVT{event_id:04d}",
                    "entity_id": entity["entity_id"],
                    "event_type": event_type,
                    "severity": random.choices(["Watch", "Medium", "High"], [0.34, 0.45, 0.21])[0],
                    "estimated_impact": impact,
                    "note": f"{event_type} tied to {entity['category'].lower()} portfolio decision",
                }
            )
            event_id += 1
    return rows


def generate_actions(entities):
    rows = []
    for entity in entities:
        score = entity["rationalization_score"]
        effort = "High" if entity["complexity_index"] > 72 else "Medium" if entity["complexity_index"] > 48 else "Low"
        revenue_at_risk = float(entity["annual_revenue"]) * clamp(score / 180, 0.08, 0.52)
        margin_lift = clamp((0.42 - entity["gross_margin_pct"]) * 100, 1.2, 9.4)
        rows.append(
            {
                "action_id": f"ACT-{entity['entity_id']}",
                "entity_id": entity["entity_id"],
                "recommended_move": entity["recommended_move"],
                "owner": entity["owner"],
                "effort": effort,
                "expected_margin_lift_pts": round(margin_lift, 1),
                "revenue_at_risk": currency(revenue_at_risk),
                "launch_readiness": int(clamp((entity["strategic_fit"] + entity["channel_fit"] + 100 - entity["complexity_index"]) / 3, 24, 96)),
                "next_artifact": random.choice(["Sell sheet", "Cut sheet", "Sales FAQ", "Cost review", "Variant map", "Field survey"]),
            }
        )
    return rows


def write_analysis(entities, actions):
    ranked = sorted(entities, key=lambda row: row["rationalization_score"], reverse=True)
    priority_rows = []
    for rank, entity in enumerate(ranked[:18], 1):
        action = next(row for row in actions if row["entity_id"] == entity["entity_id"])
        priority_rows.append(
            {
                "rank": rank,
                "entity_id": entity["entity_id"],
                "entity_name": entity["entity_name"],
                "category": entity["category"],
                "lifecycle": entity["lifecycle"],
                "rationalization_score": entity["rationalization_score"],
                "annual_revenue": entity["annual_revenue"],
                "gross_margin_pct": entity["gross_margin_pct"],
                "active_skus": entity["active_skus"],
                "order_velocity": entity["order_velocity"],
                "recommended_move": entity["recommended_move"],
                "expected_margin_lift_pts": action["expected_margin_lift_pts"],
                "launch_readiness": action["launch_readiness"],
            }
        )
    write_csv(
        OUTPUTS / "priority_queue.csv",
        priority_rows,
        [
            "rank",
            "entity_id",
            "entity_name",
            "category",
            "lifecycle",
            "rationalization_score",
            "annual_revenue",
            "gross_margin_pct",
            "active_skus",
            "order_velocity",
            "recommended_move",
            "expected_margin_lift_pts",
            "launch_readiness",
        ],
    )
    total_revenue = sum(float(row["annual_revenue"]) for row in entities)
    high_score = [row for row in entities if row["rationalization_score"] >= 65]
    launch_ready = [row for row in actions if int(row["launch_readiness"]) >= 70]
    (ROOT / "analysis" / "executive_findings.md").write_text(
        "\n".join(
            [
                "# Executive Findings",
                "",
                "## What I analyzed",
                "",
                f"I modeled {len(entities)} lighting SKU families across product category, lifecycle, channel, margin, velocity, lead time, certification burden, and launch readiness.",
                "",
                "## Findings",
                "",
                f"- The top rationalization queue contains {len(high_score)} SKU families with a score of 65 or higher.",
                f"- Modeled annual revenue across the portfolio is ${total_revenue:,.0f}.",
                f"- {len(launch_ready)} SKU families are strong enough for launch or collateral acceleration after pruning, pricing, or variant cleanup.",
                f"- The highest priority family is {ranked[0]['entity_name']} with a score of {ranked[0]['rationalization_score']}.",
                "",
                "## Recommendation",
                "",
                "Use the priority queue to separate prune, improve, refresh, and monitor decisions before asking sales, engineering, marketing, and operations to act.",
                "",
            ]
        )
    )
    (ROOT / "analysis" / "analysis_plan.md").write_text(
        "\n".join(
            [
                "# Analysis Plan",
                "",
                "1. Score each SKU family on long-tail complexity, margin gap, order velocity, lead time, quality drag, and channel fit.",
                "2. Group results into prune, improve, refresh, launch review, and monitor moves.",
                "3. Translate the queue into cross-functional work artifacts: variant maps, cut sheets, sell sheets, cost reviews, field surveys, and sales FAQs.",
                "4. Review top-ranked families with product, sales, engineering, operations, and marketing before changing public offers.",
                "",
            ]
        )
    )
    (ROOT / "analysis" / "sql_checks.sql").write_text(
        "\n".join(
            [
                "-- Checks for SKU rationalization source tables",
                "select entity_id, count(*) from daily_metrics group by entity_id having count(*) <> 180;",
                "select entity_id from entities where gross_margin_pct < 0 or gross_margin_pct > 1;",
                "select entity_id from entities where active_skus <= 0 or order_velocity < 0;",
                "select entity_id from recommended_actions where recommended_move is null;",
                "",
            ]
        )
    )


def main():
    DATA.mkdir(exist_ok=True)
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    entities = generate_entities()
    daily = generate_daily_metrics(entities)
    events = generate_events(entities)
    actions = generate_actions(entities)

    write_csv(DATA / "entities.csv", entities, list(entities[0].keys()))
    write_csv(DATA / "daily_metrics.csv", daily, list(daily[0].keys()))
    write_csv(DATA / "source_events.csv", events, list(events[0].keys()))
    write_csv(DATA / "recommended_actions.csv", actions, list(actions[0].keys()))
    write_analysis(entities, actions)


if __name__ == "__main__":
    main()
