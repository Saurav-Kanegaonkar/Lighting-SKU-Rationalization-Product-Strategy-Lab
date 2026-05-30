const currency = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

const percent = new Intl.NumberFormat("en-US", {
  style: "percent",
  maximumFractionDigits: 1,
});

const number = new Intl.NumberFormat("en-US");

const numericFields = new Set([
  "active_skus",
  "annual_revenue",
  "gross_margin_pct",
  "order_velocity",
  "quote_count",
  "sample_requests",
  "quote_win_rate",
  "return_rate",
  "lead_time_days",
  "complexity_index",
  "certification_count",
  "channel_fit",
  "strategic_fit",
  "rationalization_score",
  "rank",
  "expected_margin_lift_pts",
  "launch_readiness",
  "revenue_at_risk",
]);

const parseCsv = (text) => {
  const lines = text.trim().split(/\r?\n/);
  const headers = lines.shift().split(",");
  return lines.map((line) => {
    const values = line.split(",");
    return headers.reduce((row, header, index) => {
      const raw = values[index] ?? "";
      row[header] = numericFields.has(header) ? Number(raw) : raw;
      return row;
    }, {});
  });
};

const loadCsv = async (path) => {
  const response = await fetch(path);
  if (!response.ok) throw new Error(`Unable to load ${path}`);
  return parseCsv(await response.text());
};

const groupBy = (rows, key) =>
  rows.reduce((groups, row) => {
    const value = row[key];
    groups[value] = groups[value] || [];
    groups[value].push(row);
    return groups;
  }, {});

const average = (rows, key) =>
  rows.reduce((total, row) => total + Number(row[key] || 0), 0) / rows.length;

const sum = (rows, key) =>
  rows.reduce((total, row) => total + Number(row[key] || 0), 0);

const scoreClass = (score) => {
  if (score >= 72) return "high";
  if (score >= 55) return "medium";
  return "watch";
};

const renderSummary = (entities, actions) => {
  const topQueue = entities.filter((row) => row.rationalization_score >= 65);
  const marginPool = sum(actions, "revenue_at_risk");
  const launchReady = actions.filter((row) => row.launch_readiness >= 70);
  const totalSkus = sum(entities, "active_skus");

  document.querySelector("#summary").innerHTML = [
    ["Modeled revenue", currency.format(sum(entities, "annual_revenue")), "synthetic portfolio"],
    ["Active SKU variants", number.format(totalSkus), "long-tail families"],
    ["Priority queue", number.format(topQueue.length), "families at 65+"],
    ["Margin pool", currency.format(marginPool), "revenue at risk"],
    ["Launch ready", number.format(launchReady.length), "workstreams"],
  ]
    .map(
      ([label, value, meta]) => `
        <article class="summary-card">
          <span>${label}</span>
          <strong>${value}</strong>
          <em>${meta}</em>
        </article>
      `
    )
    .join("");
};

const renderCategoryChart = (entities) => {
  const categories = Object.entries(groupBy(entities, "category"))
    .map(([category, rows]) => ({
      category,
      revenue: sum(rows, "annual_revenue"),
      score: average(rows, "rationalization_score"),
      margin: average(rows, "gross_margin_pct"),
      skus: sum(rows, "active_skus"),
    }))
    .sort((a, b) => b.revenue - a.revenue);

  const maxRevenue = Math.max(...categories.map((row) => row.revenue));

  document.querySelector("#category-chart").innerHTML = categories
    .map(
      (row) => `
        <article class="bar-row">
          <div class="bar-label">
            <strong>${row.category}</strong>
            <span>${currency.format(row.revenue)} revenue, ${number.format(row.skus)} SKUs</span>
          </div>
          <div class="bar-track" aria-hidden="true">
            <span style="width:${Math.max(8, (row.revenue / maxRevenue) * 100)}%"></span>
          </div>
          <b class="risk-pill ${scoreClass(row.score)}">${row.score.toFixed(1)}</b>
        </article>
      `
    )
    .join("");
};

const renderCategoryMix = (entities) => {
  const categories = Object.entries(groupBy(entities, "category"))
    .map(([category, rows]) => ({
      category,
      count: rows.length,
      margin: average(rows, "gross_margin_pct"),
      complexity: average(rows, "complexity_index"),
      readiness: average(rows, "strategic_fit"),
    }))
    .sort((a, b) => b.complexity - a.complexity);

  document.querySelector("#category-mix").innerHTML = categories
    .map(
      (row) => `
        <article class="category-card">
          <span>${row.category}</span>
          <strong>${number.format(row.count)} families</strong>
          <dl>
            <div><dt>Margin</dt><dd>${percent.format(row.margin)}</dd></div>
            <div><dt>Complexity</dt><dd>${row.complexity.toFixed(0)}</dd></div>
            <div><dt>Strategic fit</dt><dd>${row.readiness.toFixed(0)}</dd></div>
          </dl>
        </article>
      `
    )
    .join("");
};

const queueRow = (row, action) => `
  <tr>
    <td>${row.rank}</td>
    <td>
      <strong>${row.entity_name}</strong>
      <span>${row.category}</span>
    </td>
    <td>${row.lifecycle}</td>
    <td><b class="risk-pill ${scoreClass(row.rationalization_score)}">${row.rationalization_score.toFixed(1)}</b></td>
    <td>${percent.format(row.gross_margin_pct)}</td>
    <td>${number.format(row.active_skus)}</td>
    <td>${row.recommended_move}</td>
    <td>${action ? action.expected_margin_lift_pts.toFixed(1) : row.expected_margin_lift_pts.toFixed(1)} pts</td>
  </tr>
`;

const renderQueue = (queue, actions, filter = "All") => {
  const actionByEntity = Object.fromEntries(actions.map((row) => [row.entity_id, row]));
  const rows = queue.filter((row) => filter === "All" || row.recommended_move === filter);
  document.querySelector("#queue-table").innerHTML = rows
    .map((row) => queueRow(row, actionByEntity[row.entity_id]))
    .join("");
};

const renderMoveFilter = (queue, actions) => {
  const filter = document.querySelector("#move-filter");
  const moves = [...new Set(queue.map((row) => row.recommended_move))].sort();
  filter.innerHTML = [`<option value="All">All moves</option>`]
    .concat(moves.map((move) => `<option value="${move}">${move}</option>`))
    .join("");
  filter.addEventListener("change", () => renderQueue(queue, actions, filter.value));
};

const renderReadiness = (actions, entities) => {
  const entityById = Object.fromEntries(entities.map((row) => [row.entity_id, row]));
  const artifactGroups = Object.entries(groupBy(actions, "next_artifact"))
    .map(([artifact, rows]) => ({
      artifact,
      rows,
      readiness: average(rows, "launch_readiness"),
      revenueAtRisk: sum(rows, "revenue_at_risk"),
    }))
    .sort((a, b) => b.readiness - a.readiness);

  document.querySelector("#readiness-board").innerHTML = artifactGroups
    .map((group) => {
      const lead = group.rows.sort((a, b) => b.launch_readiness - a.launch_readiness)[0];
      const entity = entityById[lead.entity_id];
      return `
        <article class="readiness-item">
          <div>
            <span>${group.artifact}</span>
            <strong>${group.readiness.toFixed(0)} readiness</strong>
            <em>${entity.category}, ${lead.recommended_move.toLowerCase()}</em>
          </div>
          <b>${currency.format(group.revenueAtRisk)}</b>
        </article>
      `;
    })
    .join("");
};

const activateTabs = () => {
  const tabs = document.querySelectorAll(".tab");
  const views = document.querySelectorAll(".view");
  const setView = (viewName) => {
    tabs.forEach((item) => item.classList.toggle("is-active", item.dataset.view === viewName));
    views.forEach((view) => view.classList.toggle("is-active", view.id === `${viewName}-view`));
  };
  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      setView(tab.dataset.view);
    });
  });
  const requestedView = new URLSearchParams(window.location.search).get("view");
  if (["portfolio", "queue", "launch"].includes(requestedView)) {
    setView(requestedView);
  }
};

const start = async () => {
  const [entities, actions, queue] = await Promise.all([
    loadCsv("data/entities.csv"),
    loadCsv("data/recommended_actions.csv"),
    loadCsv("analysis/outputs/priority_queue.csv"),
  ]);

  renderSummary(entities, actions);
  renderCategoryChart(entities);
  renderCategoryMix(entities);
  renderMoveFilter(queue, actions);
  renderQueue(queue, actions);
  renderReadiness(actions, entities);
  activateTabs();
};

start().catch((error) => {
  document.querySelector(".workspace").innerHTML = `<section class="panel error">${error.message}</section>`;
});
