from datetime import date
from pathlib import Path

from opie.assumptions.packs import (
    PackLineage,
    PackManifest,
    PackSignature,
    compute_pack_files,
    list_pack_files,
    load_manifest,
    resolve_pack_root,
    sign_manifest,
    validate_pack,
)
from opie.core.ledger import dumps_json


def _write_pack(tmp_path: Path) -> Path:
    pack_dir = tmp_path / "pack"
    pack_dir.mkdir()
    tables_dir = pack_dir / "tables"
    tables_dir.mkdir()
    (tables_dir / "coi.csv").write_text("age,rate\n30,0.5\n")
    (pack_dir / "schedules.json").write_text('{"1": "0"}')
    files = compute_pack_files(pack_dir)
    manifest = PackManifest(
        name="Test Pack",
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


def test_pack_validation_roundtrip(tmp_path: Path) -> None:
    pack_dir = _write_pack(tmp_path)
    manifest = load_manifest(pack_dir)
    result = validate_pack(pack_dir)
    assert result.valid is True
    assert result.signature_valid is True
    assert result.missing_files == []
    assert result.extra_files == []
    assert result.mismatched_checksums == {}
    assert result.files == ["schedules.json", "tables/coi.csv"]
    assert manifest.effective_date.isoformat() == "2025-01-01"


def test_pack_validation_failure(tmp_path: Path) -> None:
    pack_dir = _write_pack(tmp_path)
    (pack_dir / "schedules.json").write_text('{"1": "1"}')
    result = validate_pack(pack_dir)
    assert result.valid is False
    assert "schedules.json" in result.mismatched_checksums


def test_pack_signature_invalid(tmp_path: Path) -> None:
    pack_dir = _write_pack(tmp_path)
    manifest = load_manifest(pack_dir)
    bad_manifest = manifest.model_copy(
        update={"signature": PackSignature(method="stub-sha256", value="bad")}
    )
    (pack_dir / "pack.json").write_text(dumps_json(bad_manifest))
    result = validate_pack(pack_dir)
    assert result.signature_valid is False
    assert result.valid is False


def test_pack_signature_none_is_valid(tmp_path: Path) -> None:
    pack_dir = _write_pack(tmp_path)
    manifest = load_manifest(pack_dir)
    updated = manifest.model_copy(update={"signature": PackSignature(method="none", value="")})
    (pack_dir / "pack.json").write_text(dumps_json(updated))
    result = validate_pack(pack_dir)
    assert result.signature_valid is True
    assert result.valid is True


def test_pack_validation_detects_missing_file(tmp_path: Path) -> None:
    pack_dir = _write_pack(tmp_path)
    (pack_dir / "schedules.json").unlink()
    result = validate_pack(pack_dir)
    assert result.valid is False
    assert "schedules.json" in result.missing_files


def test_pack_validation_detects_extra_file(tmp_path: Path) -> None:
    pack_dir = _write_pack(tmp_path)
    (pack_dir / "extra.json").write_text("{}")
    result = validate_pack(pack_dir)
    assert result.valid is False
    assert "extra.json" in result.extra_files


def test_resolve_pack_root_accepts_pack_json(tmp_path: Path) -> None:
    pack_dir = _write_pack(tmp_path)
    pack_path = resolve_pack_root(pack_dir / "pack.json")
    assert pack_path == pack_dir
    assert list_pack_files(pack_path)
