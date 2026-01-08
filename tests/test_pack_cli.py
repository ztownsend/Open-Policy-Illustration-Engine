import json
from pathlib import Path

from typer.testing import CliRunner

from opie.assumptions.packs import compute_pack_checksum
from opie.cli.main import app


def _write_pack(tmp_path: Path) -> Path:
    pack_dir = tmp_path / "pack"
    pack_dir.mkdir()
    (pack_dir / "tables").mkdir()
    (pack_dir / "tables" / "coi.csv").write_text("age,rate\n30,0.5\n")
    (pack_dir / "schedules.json").write_text('{"1": "0"}')
    checksum = compute_pack_checksum(pack_dir)
    manifest = {
        "name": "CLI Pack",
        "version": "0.0.1",
        "license": "MIT",
        "source": "unit-test",
        "checksum": checksum,
    }
    (pack_dir / "pack.json").write_text(json.dumps(manifest, sort_keys=True))
    return pack_dir


def test_pack_list_command(tmp_path: Path) -> None:
    pack_dir = _write_pack(tmp_path)
    runner = CliRunner()
    result = runner.invoke(app, ["pack", "list", "--path", str(pack_dir)])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["manifest"]["name"] == "CLI Pack"
    assert payload["files"] == ["schedules.json", "tables/coi.csv"]


def test_pack_validate_command(tmp_path: Path) -> None:
    pack_dir = _write_pack(tmp_path)
    runner = CliRunner()
    result = runner.invoke(app, ["pack", "validate", "--path", str(pack_dir)])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["valid"] is True

    bad_manifest = {
        "name": "CLI Pack",
        "version": "0.0.1",
        "license": "MIT",
        "source": "unit-test",
        "checksum": "deadbeef",
    }
    (pack_dir / "pack.json").write_text(json.dumps(bad_manifest, sort_keys=True))
    bad_result = runner.invoke(app, ["pack", "validate", "--path", str(pack_dir)])
    assert bad_result.exit_code == 1
    bad_payload = json.loads(bad_result.stdout)
    assert bad_payload["valid"] is False
