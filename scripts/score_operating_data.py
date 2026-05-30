import csv

ranked = []
with open("analysis/outputs/priority_queue.csv", newline="") as f:
    for row in csv.DictReader(f):
        ranked.append(row)

for row in ranked[:10]:
    print(
        f"{row['rank']}. {row['entity_name']}: "
        f"score={float(row['rationalization_score']):.1f}, "
        f"margin={float(row['gross_margin_pct']) * 100:.1f}%, "
        f"active_skus={row['active_skus']}, "
        f"move={row['recommended_move']}"
    )
