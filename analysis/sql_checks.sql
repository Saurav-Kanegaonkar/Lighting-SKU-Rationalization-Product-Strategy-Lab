-- Checks for SKU rationalization source tables
select entity_id, count(*) from daily_metrics group by entity_id having count(*) <> 180;
select entity_id from entities where gross_margin_pct < 0 or gross_margin_pct > 1;
select entity_id from entities where active_skus <= 0 or order_velocity < 0;
select entity_id from recommended_actions where recommended_move is null;
