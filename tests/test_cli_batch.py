import json
from pathlib import Path

from typer.testing import CliRunner

from opie.cli.main import app


def test_cli_batch(tmp_path: Path) -> None:
    payload = json.loads(Path("examples/term_request.json").read_text())
    payload2 = dict(payload)
    payload2["issue_age"] = payload["issue_age"] + 1

    in_path = tmp_path / "in.ndjson"
    out_path = tmp_path / "out.ndjson"
    in_path.write_text("\n".join([json.dumps(payload), json.dumps(payload2), ""]))

    runner = CliRunner()
    result = runner.invoke(app, ["batch", "--in", str(in_path), "--out", str(out_path)])
    assert result.exit_code == 0
    lines = [line for line in out_path.read_text().splitlines() if line.strip()]
    assert len(lines) == 2
    first = json.loads(lines[0])
    assert first["product_code"] == "level_term"
