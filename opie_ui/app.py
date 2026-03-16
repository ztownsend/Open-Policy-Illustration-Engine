"""UI Explorer for OPIE."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from opie.api.app import app as api_app

app = FastAPI(title="OPIE Explorer")
app.mount("/api", api_app)

_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>OPIE Explorer</title>
  <style>
    :root {
      --ink: #1a1a1a;
      --muted: #5e5a52;
      --paper: #fff8ef;
      --accent: #c14a1c;
      --accent-2: #2f6f6a;
      --panel: #fffdf8;
      --shadow: rgba(15, 10, 5, 0.12);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Iowan Old Style", "Palatino Linotype", "Book Antiqua", Palatino, serif;
      color: var(--ink);
      background: radial-gradient(1200px 600px at 10% 10%, #ffe8d1 0%, #fff8ef 55%, #f7efe6 100%);
    }
    header {
      padding: 32px 24px 12px;
      display: flex;
      flex-direction: column;
      gap: 8px;
      animation: rise 600ms ease-out both;
    }
    h1 {
      font-size: clamp(28px, 3vw, 40px);
      letter-spacing: 0.5px;
      margin: 0;
    }
    p.lede {
      margin: 0;
      color: var(--muted);
      max-width: 720px;
    }
    main {
      display: grid;
      grid-template-columns: minmax(260px, 1fr) minmax(320px, 2fr);
      gap: 20px;
      padding: 12px 24px 32px;
    }
    .card {
      background: var(--panel);
      border-radius: 18px;
      padding: 18px;
      box-shadow: 0 20px 40px var(--shadow);
      animation: fadeIn 700ms ease-out both;
    }
    .controls {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 12px;
    }
    .preset-bar {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }
    button {
      border: none;
      background: var(--accent);
      color: #fff;
      padding: 10px 14px;
      border-radius: 999px;
      cursor: pointer;
      font-size: 14px;
      letter-spacing: 0.2px;
    }
    button.secondary {
      background: transparent;
      color: var(--accent);
      border: 1px solid var(--accent);
    }
    button.small {
      padding: 6px 10px;
      font-size: 12px;
    }
    .toggle {
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
    }
    .toggle label {
      border: 1px solid #e2d6c8;
      border-radius: 999px;
      padding: 6px 12px;
      cursor: pointer;
      font-size: 13px;
    }
    .toggle input { display: none; }
    .toggle input:checked + span {
      background: var(--accent-2);
      color: #fff;
      border-radius: 999px;
      padding: 6px 12px;
    }
    .columns {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
      gap: 6px;
      margin-bottom: 12px;
    }
    .columns label {
      display: flex;
      align-items: center;
      gap: 6px;
      background: #fff;
      border: 1px solid #efe4d7;
      border-radius: 10px;
      padding: 6px 8px;
      font-size: 12px;
      color: var(--muted);
    }
    .columns input {
      accent-color: var(--accent-2);
    }
    textarea {
      width: 100%;
      min-height: 260px;
      border-radius: 12px;
      border: 1px solid #eadfd2;
      padding: 12px;
      font-family: "Courier New", Courier, monospace;
      font-size: 12px;
      background: #fff;
    }
    .status {
      font-size: 13px;
      color: var(--muted);
      margin-top: 6px;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 12px;
    }
    th, td {
      text-align: left;
      padding: 8px 6px;
      border-bottom: 1px solid #efe4d7;
    }
    tr.lapsed {
      background: #ffe3dd;
    }
    .diff-box {
      background: #f7f1e8;
      border-radius: 12px;
      padding: 12px;
      font-size: 12px;
      margin-bottom: 12px;
    }
    .diff-cell {
      background: #fff1e1;
      color: #7c2f10;
    }
    .diff-same {
      color: var(--muted);
    }
    .alloc-panel {
      margin-bottom: 12px;
      padding: 12px;
      background: #f7f1e8;
      border-radius: 12px;
    }
    .alloc-panel h3 {
      margin: 0 0 8px;
      font-size: 14px;
      color: var(--muted);
    }
    .alloc-bar {
      display: flex;
      height: 28px;
      border-radius: 8px;
      overflow: hidden;
      margin-bottom: 8px;
    }
    .alloc-segment {
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 11px;
      font-weight: bold;
      color: #fff;
    }
    .alloc-legend {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      font-size: 12px;
    }
    .alloc-legend-item {
      display: flex;
      align-items: center;
      gap: 4px;
    }
    .alloc-dot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }
    @keyframes rise {
      from { opacity: 0; transform: translateY(-8px); }
      to { opacity: 1; transform: translateY(0); }
    }
    @media (max-width: 900px) {
      main {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <header>
    <h1>OPIE Explorer</h1>
    <p class="lede">Run scenarios, inspect the ledger, and surface the first diff without leaving your browser.</p>
  </header>
  <main>
    <section class="card">
      <h2>Request Builder</h2>
      <div class="controls">
        <button id="run">Run Illustration</button>
        <button id="downloadCsv" class="secondary">Download CSV</button>
        <button id="copyRequest" class="secondary">Copy Request</button>
        <button id="copyResult" class="secondary">Copy Result</button>
        <button id="exportRequest" class="secondary">Export Request</button>
        <button id="exportResult" class="secondary">Export Result</button>
      </div>
      <textarea id="request"></textarea>
      <div id="status" class="status">Ready.</div>
    </section>
    <section class="card">
      <h2>Ledger Viewer</h2>
      <div class="controls">
        <div class="toggle">
          <label><input type="radio" name="scenario" value="current" checked><span>Current</span></label>
          <label><input type="radio" name="scenario" value="guaranteed"><span>Guaranteed</span></label>
          <label><input type="radio" name="scenario" value="diff"><span>Diff</span></label>
        </div>
      </div>
      <div class="controls">
        <div class="preset-bar">
          <button id="colsCore" class="secondary small">Core</button>
          <button id="colsValue" class="secondary small">Values</button>
          <button id="colsCharges" class="secondary small">Charges</button>
          <button id="colsLoans" class="secondary small">Loans</button>
          <button id="colsAll" class="secondary small">All</button>
        </div>
      </div>
      <div id="columns" class="columns"></div>
      <div id="allocPanel" class="alloc-panel" style="display:none;">
        <h3>Index Account Allocation</h3>
        <div id="allocBar" class="alloc-bar"></div>
        <div id="allocLegend" class="alloc-legend"></div>
      </div>
      <div id="diff" class="diff-box">Run an illustration to see diffs.</div>
      <div style="overflow:auto; max-height: 420px;">
        <table id="ledger"></table>
      </div>
    </section>
  </main>
  <script>
    const defaultRequest = {
      product_code: "simple_ul",
      issue_age: 35,
      issue_gender: "M",
      risk_class: "NT",
      face_amount: "100000",
      issue_date: "2024-01-01",
      duration_months: 12,
      premium_schedule: [{ start_month: 1, end_month: 12, amount: "200" }],
      scenarios: {
        current: {
          crediting_rate_annual: "0.04",
          premium_load_pct: "0.05",
          monthly_policy_fee: "5",
          monthly_per_thousand_admin_fee: "0.1",
          interest_mode: "nominal_div_12",
          coi_table: { "35": "0.6", "36": "0.6" },
          surrender_charge_schedule: { "1": "200", "12": "0" }
        },
        guaranteed: {
          crediting_rate_annual: "0.02",
          premium_load_pct: "0.05",
          monthly_policy_fee: "5",
          monthly_per_thousand_admin_fee: "0.1",
          interest_mode: "nominal_div_12",
          coi_table: { "35": "0.8", "36": "0.8" },
          surrender_charge_schedule: { "1": "300", "12": "0" }
        }
      }
    };

    const requestEl = document.getElementById("request");
    const statusEl = document.getElementById("status");
    const diffEl = document.getElementById("diff");
    const ledgerEl = document.getElementById("ledger");
    const columnsEl = document.getElementById("columns");
    const runBtn = document.getElementById("run");
    const downloadCsvBtn = document.getElementById("downloadCsv");
    const copyRequestBtn = document.getElementById("copyRequest");
    const copyResultBtn = document.getElementById("copyResult");
    const exportRequestBtn = document.getElementById("exportRequest");
    const exportResultBtn = document.getElementById("exportResult");
    const colsCoreBtn = document.getElementById("colsCore");
    const colsValueBtn = document.getElementById("colsValue");
    const colsChargesBtn = document.getElementById("colsCharges");
    const colsLoansBtn = document.getElementById("colsLoans");
    const colsAllBtn = document.getElementById("colsAll");

    let result = null;

    requestEl.value = JSON.stringify(defaultRequest, null, 2);
    renderColumnPicker();

    function setStatus(message) {
      statusEl.textContent = message;
    }

    const columnDefs = [
      { key: "t", label: "t" },
      { key: "policy_year", label: "year" },
      { key: "attained_age", label: "age" },
      { key: "policy_status", label: "status" },
      { key: "premium", label: "premium" },
      { key: "cumulative_premium", label: "cum_prem" },
      { key: "account_value_bop", label: "av_bop" },
      { key: "account_value_mid_raw", label: "av_mid" },
      { key: "account_value_eop", label: "av_eop" },
      { key: "cash_surrender_value", label: "csv" },
      { key: "surrender_charge", label: "surr" },
      { key: "death_benefit", label: "db" },
      { key: "charges_total", label: "charges" },
      { key: "charges_assessed", label: "chg_assess" },
      { key: "charges_paid", label: "chg_paid" },
      { key: "charge_shortfall", label: "chg_short" },
      { key: "interest_credited", label: "interest" },
      { key: "net_amount_at_risk", label: "nar" },
      { key: "corridor_uplift", label: "corridor" },
      { key: "rider_charges", label: "rider_chg" },
      { key: "withdrawal", label: "withdrawal" },
      { key: "loan_draw", label: "loan_draw" },
      { key: "loan_repayment", label: "loan_repay" },
      { key: "loan_interest", label: "loan_int" },
      { key: "loan_balance", label: "loan_bal" }
    ];

    const columnPresets = {
      core: ["t", "policy_status", "premium", "account_value_eop", "cash_surrender_value", "death_benefit"],
      values: ["t", "account_value_bop", "account_value_mid_raw", "account_value_eop", "interest_credited"],
      charges: ["t", "premium", "charges_total", "charges_assessed", "charges_paid", "charge_shortfall"],
      loans: ["t", "withdrawal", "loan_draw", "loan_repayment", "loan_interest", "loan_balance"],
      all: columnDefs.map((col) => col.key)
    };

    let selectedColumns = new Set(columnPresets.core);

    function downloadFile(filename, contents, type) {
      const blob = new Blob([contents], { type });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      link.click();
      URL.revokeObjectURL(url);
    }

    function downloadJSON(filename, payload) {
      downloadFile(filename, JSON.stringify(payload, null, 2), "application/json");
    }

    function downloadCSV(filename, csvText) {
      downloadFile(filename, csvText, "text/csv");
    }

    function copyText(label, text) {
      const fallbackCopy = () => {
        const helper = document.createElement("textarea");
        helper.value = text;
        helper.style.position = "fixed";
        helper.style.opacity = "0";
        document.body.appendChild(helper);
        helper.focus();
        helper.select();
        try {
          document.execCommand("copy");
          setStatus(`${label} copied.`);
        } catch (err) {
          setStatus(`Unable to copy ${label.toLowerCase()}.`);
        }
        document.body.removeChild(helper);
      };

      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(
          () => setStatus(`${label} copied.`),
          () => fallbackCopy()
        );
      } else {
        fallbackCopy();
      }
    }

    function getSelectedColumns() {
      const columns = columnDefs.filter((col) => selectedColumns.has(col.key));
      return columns.length ? columns : [columnDefs[0]];
    }

    function renderColumnPicker() {
      columnsEl.innerHTML = columnDefs.map((col) => {
        return (
          `<label>` +
          `<input type="checkbox" data-key="${col.key}">` +
          `<span>${col.label}</span>` +
          `</label>`
        );
      }).join("");
      columnsEl.querySelectorAll("input").forEach((input) => {
        const key = input.dataset.key;
        input.checked = selectedColumns.has(key);
        input.addEventListener("change", () => {
          if (input.checked) {
            selectedColumns.add(key);
          } else {
            selectedColumns.delete(key);
          }
          render();
        });
      });
    }

    function applyPreset(name) {
      selectedColumns = new Set(columnPresets[name] || columnPresets.core);
      renderColumnPicker();
      render();
    }

    function formatValue(value) {
      return value === null || value === undefined ? "-" : value;
    }

    function numericDelta(a, b) {
      const numA = Number(a);
      const numB = Number(b);
      if (!Number.isFinite(numA) || !Number.isFinite(numB)) {
        return "";
      }
      const delta = numB - numA;
      return delta.toFixed(2);
    }

    function buildTable(rows) {
      const columns = getSelectedColumns();
      const header = `<tr>${columns.map(col => `<th>${col.label}</th>`).join("")}</tr>`;
      const body = rows.map(row => {
        const cells = columns.map(col => `<td>${formatValue(row[col.key])}</td>`).join("");
        const cls = row.policy_status === "lapsed" ? "lapsed" : "";
        return `<tr class="${cls}">${cells}</tr>`;
      }).join("");
      ledgerEl.innerHTML = header + body;
    }

    function buildDiffTable(currentRows, guaranteedRows) {
      const columns = getSelectedColumns();
      const header = `<tr>${columns.map(col => `<th>${col.label}</th>`).join("")}</tr>`;
      const maxLen = Math.max(currentRows.length, guaranteedRows.length);
      const rows = [];

      for (let i = 0; i < maxLen; i++) {
        const a = currentRows[i] || {};
        const b = guaranteedRows[i] || {};
        const rowClass = a.policy_status === "lapsed" || b.policy_status === "lapsed" ? "lapsed" : "";
        const cells = columns.map((col) => {
          const valA = a[col.key];
          const valB = b[col.key];
          const same = valA === valB;
          const delta = same ? "" : numericDelta(valA, valB);
          const suffix = delta ? ` (delta ${delta})` : "";
          const text = same
            ? `${formatValue(valA)}`
            : `${formatValue(valA)} -> ${formatValue(valB)}${suffix}`;
          const cls = same ? "diff-same" : "diff-cell";
          return `<td class="${cls}">${text}</td>`;
        }).join("");
        rows.push(`<tr class="${rowClass}">${cells}</tr>`);
      }

      ledgerEl.innerHTML = header + rows.join("");
    }

    function firstDiff(currentRows, guaranteedRows) {
      const maxLen = Math.max(currentRows.length, guaranteedRows.length);
      for (let i = 0; i < maxLen; i++) {
        if (i >= currentRows.length) {
          return `Row missing in current at t=${i + 1}`;
        }
        if (i >= guaranteedRows.length) {
          return `Row missing in guaranteed at t=${i + 1}`;
        }
        const a = currentRows[i];
        const b = guaranteedRows[i];
        const keys = Array.from(new Set([...Object.keys(a), ...Object.keys(b)])).sort();
        for (const key of keys) {
          if (a[key] !== b[key]) {
            return `First diff at t=${i + 1} field=${key}: ${a[key]} vs ${b[key]}`;
          }
        }
      }
      return "No differences found";
    }

    function render() {
      if (!result) {
        ledgerEl.innerHTML = "";
        diffEl.textContent = "Run an illustration to see diffs.";
        return;
      }
      const scenario = document.querySelector("input[name='scenario']:checked").value;
      const currentRows = result.ledgers.current.rows;
      const guaranteedRows = result.ledgers.guaranteed.rows;
      diffEl.textContent = firstDiff(currentRows, guaranteedRows);
      if (scenario === "diff") {
        buildDiffTable(currentRows, guaranteedRows);
      } else {
        buildTable(result.ledgers[scenario].rows);
      }
    }

    const allocColors = ["#c14a1c", "#2f6f6a", "#8b6914", "#5b3e8a", "#1a6b3f"];

    function renderAllocPanel() {
      const panel = document.getElementById("allocPanel");
      const bar = document.getElementById("allocBar");
      const legend = document.getElementById("allocLegend");
      let payload;
      try { payload = JSON.parse(requestEl.value); } catch { panel.style.display = "none"; return; }
      if (payload.product_code !== "indexed_ul") { panel.style.display = "none"; return; }
      const accounts = (payload.scenarios && payload.scenarios.current && payload.scenarios.current.index_accounts) || [];
      if (!accounts.length) { panel.style.display = "none"; return; }
      panel.style.display = "block";
      bar.innerHTML = accounts.map((a, i) => {
        const pct = (parseFloat(a.allocation) * 100).toFixed(0);
        const color = allocColors[i % allocColors.length];
        return `<div class="alloc-segment" style="width:${pct}%;background:${color}">${pct}%</div>`;
      }).join("");
      legend.innerHTML = accounts.map((a, i) => {
        const color = allocColors[i % allocColors.length];
        const strategy = a.strategy_type === "fixed" ? `Fixed ${(parseFloat(a.fixed_rate)*100).toFixed(1)}%` : `${a.strategy_type} (cap ${(parseFloat(a.cap)*100).toFixed(0)}%, part ${(parseFloat(a.participation)*100).toFixed(0)}%)`;
        return `<span class="alloc-legend-item"><span class="alloc-dot" style="background:${color}"></span>${a.name}: ${strategy}</span>`;
      }).join("");
    }

    function escapeCsvValue(value) {
      if (value === null || value === undefined) {
        return "";
      }
      const text = String(value);
      if (text.includes("\"") || text.includes(",") || text.includes("\n")) {
        return `"${text.replace(/\"/g, "\"\"")}"`;
      }
      return text;
    }

    function buildCsv(rows, columns) {
      const header = columns.map((col) => escapeCsvValue(col.label)).join(",");
      const body = rows.map((row) => {
        return columns.map((col) => escapeCsvValue(row[col.key])).join(",");
      }).join("\n");
      return `${header}\n${body}`;
    }

    function buildDiffCsv(currentRows, guaranteedRows, columns) {
      const header = columns.flatMap((col) => [
        `${col.label}_current`,
        `${col.label}_guaranteed`,
        `${col.label}_delta`
      ]).join(",");
      const maxLen = Math.max(currentRows.length, guaranteedRows.length);
      const bodyRows = [];
      for (let i = 0; i < maxLen; i++) {
        const a = currentRows[i] || {};
        const b = guaranteedRows[i] || {};
        const cells = columns.flatMap((col) => {
          const valA = a[col.key];
          const valB = b[col.key];
          const delta = numericDelta(valA, valB);
          return [
            escapeCsvValue(valA),
            escapeCsvValue(valB),
            escapeCsvValue(delta)
          ];
        });
        bodyRows.push(cells.join(","));
      }
      return `${header}\n${bodyRows.join("\n")}`;
    }

    runBtn.addEventListener("click", async () => {
      let payload;
      try {
        payload = JSON.parse(requestEl.value);
      } catch (err) {
        setStatus("Invalid JSON in request.");
        return;
      }
      setStatus("Running...");
      const response = await fetch("/api/v1/illustrations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (!response.ok) {
        setStatus(`Error: ${response.status}`);
        return;
      }
      result = await response.json();
      setStatus("Done. Ledger updated.");
      renderAllocPanel();
      render();
    });

    exportRequestBtn.addEventListener("click", () => {
      let payload;
      try {
        payload = JSON.parse(requestEl.value);
      } catch (err) {
        setStatus("Invalid JSON in request.");
        return;
      }
      downloadJSON("opie_request.json", payload);
    });

    exportResultBtn.addEventListener("click", () => {
      if (!result) {
        setStatus("Run an illustration first.");
        return;
      }
      downloadJSON("opie_result.json", result);
    });

    downloadCsvBtn.addEventListener("click", () => {
      if (!result) {
        setStatus("Run an illustration first.");
        return;
      }
      const scenario = document.querySelector("input[name='scenario']:checked").value;
      const columns = getSelectedColumns();
      let csvText = "";
      let filename = "opie_ledger.csv";
      if (scenario === "diff") {
        csvText = buildDiffCsv(result.ledgers.current.rows, result.ledgers.guaranteed.rows, columns);
        filename = "opie_ledger_diff.csv";
      } else {
        csvText = buildCsv(result.ledgers[scenario].rows, columns);
        filename = `opie_ledger_${scenario}.csv`;
      }
      downloadCSV(filename, csvText);
      setStatus("CSV downloaded.");
    });

    copyRequestBtn.addEventListener("click", () => {
      let payload;
      try {
        payload = JSON.parse(requestEl.value);
      } catch (err) {
        setStatus("Invalid JSON in request.");
        return;
      }
      copyText("Request", JSON.stringify(payload, null, 2));
    });

    copyResultBtn.addEventListener("click", () => {
      if (!result) {
        setStatus("Run an illustration first.");
        return;
      }
      copyText("Result", JSON.stringify(result, null, 2));
    });

    colsCoreBtn.addEventListener("click", () => applyPreset("core"));
    colsValueBtn.addEventListener("click", () => applyPreset("values"));
    colsChargesBtn.addEventListener("click", () => applyPreset("charges"));
    colsLoansBtn.addEventListener("click", () => applyPreset("loans"));
    colsAllBtn.addEventListener("click", () => applyPreset("all"));

    document.querySelectorAll("input[name='scenario']").forEach((input) => {
      input.addEventListener("change", render);
    });
  </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    return HTMLResponse(_HTML)
