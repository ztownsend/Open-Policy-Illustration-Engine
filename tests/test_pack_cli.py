from datetime import date
import json
from pathlib import Path

from typer.testing import CliRunner

from opie.assumptions.packs import (
    PackLineage,
    PackManifest,
    PackSignature,
    compute_pack_files,
    sign_manifest,
)
from opie.core.ledger import dumps_json
from opie.cli.main import app


def _write_pack(tmp_path: Path) -> Path:
    pack_dir = tmp_path / "pack"
    pack_dir.mkdir()
    (pack_dir / "tables").mkdir()
    (pack_dir / "tables" / "coi.csv").write_text("age,rate\n30,0.5\n")
    (pack_dir / "schedules.json").write_text('{"1": "0"}')
    files = compute_pack_files(pack_dir)
    manifest = PackManifest(
        name="CLI Pack",
        version="0.0.1",
        license="MIT",
        source="unit-test",
        effective_date=date(2025, 1, 1),
        lineage=PackLineage(parents=["seed-pack@0.0.0"], notes="unit-test"),
        files=files,
        signature=PackSignature(method="stub-sha256", value=""),
    )
    signature = sign_manifest(manifest)
    manifest = manifest.model_copy(update={"signature": signature})
    (pack_dir / "pack.json").write_text(dumps_json(manifest))
    return pack_dir


def test_pack_list_command(tmp_path: Path) -> None:
    pack_dir = _write_pack(tmp_path)
    runner = CliRunner()
    result = runner.invoke(app, ["pack", "list", "--path", str(pack_dir)])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["manifest"]["name"] == "CLI Pack"
    assert payload["manifest"]["signature"]["method"] == "stub-sha256"
    assert payload["files"] == ["schedules.json", "tables/coi.csv"]


def test_pack_validate_command(tmp_path: Path) -> None:
    pack_dir = _write_pack(tmp_path)
    runner = CliRunner()
    result = runner.invoke(app, ["pack", "validate", "--path", str(pack_dir)])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["valid"] is True
    assert payload["signature_valid"] is True

    (pack_dir / "schedules.json").write_text('{"1": "1"}')
    bad_result = runner.invoke(app, ["pack", "validate", "--path", str(pack_dir)])
    assert bad_result.exit_code == 1
    bad_payload = json.loads(bad_result.stdout)
    assert bad_payload["valid"] is False
    assert "schedules.json" in bad_payload["mismatched_checksums"]
