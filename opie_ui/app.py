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
    const runBtn = document.getElementById("run");
    const exportRequestBtn = document.getElementById("exportRequest");
    const exportResultBtn = document.getElementById("exportResult");

    let result = null;

    requestEl.value = JSON.stringify(defaultRequest, null, 2);

    function setStatus(message) {
      statusEl.textContent = message;
    }

    function downloadJSON(filename, payload) {
      const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      link.click();
      URL.revokeObjectURL(url);
    }

    function buildTable(rows) {
      const columns = [
        { key: "t", label: "t" },
        { key: "policy_status", label: "status" },
        { key: "premium", label: "premium" },
        { key: "account_value_eop", label: "av_eop" },
        { key: "cash_surrender_value", label: "csv" },
        { key: "death_benefit", label: "db" }
      ];
      const header = `<tr>${columns.map(col => `<th>${col.label}</th>`).join("")}</tr>`;
      const body = rows.map(row => {
        const cells = columns.map(col => `<td>${row[col.key] ?? "-"}</td>`).join("");
        const cls = row.policy_status === "lapsed" ? "lapsed" : "";
        return `<tr class="${cls}">${cells}</tr>`;
      }).join("");
      ledgerEl.innerHTML = header + body;
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
        buildTable(currentRows);
      } else {
        buildTable(result.ledgers[scenario].rows);
      }
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
