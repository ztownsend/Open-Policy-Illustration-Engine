import json
from pathlib import Path

from opie.assumptions.packs import (
    compute_pack_checksum,
    list_pack_files,
    load_manifest,
    resolve_pack_root,
    validate_pack,
)


def _write_pack(tmp_path: Path) -> Path:
    pack_dir = tmp_path / "pack"
    pack_dir.mkdir()
    tables_dir = pack_dir / "tables"
    tables_dir.mkdir()
    (tables_dir / "coi.csv").write_text("age,rate\n30,0.5\n")
    (pack_dir / "schedules.json").write_text('{"1": "0"}')
    checksum = compute_pack_checksum(pack_dir)
    manifest = {
        "name": "Test Pack",
        "version": "0.0.1",
        "license": "MIT",
        "source": "unit-test",
        "checksum": checksum,
    }
    (pack_dir / "pack.json").write_text(json.dumps(manifest, sort_keys=True))
    return pack_dir


def test_pack_validation_roundtrip(tmp_path: Path) -> None:
    pack_dir = _write_pack(tmp_path)
    manifest = load_manifest(pack_dir)
    result = validate_pack(pack_dir)
    assert result.valid is True
    assert result.computed_checksum == manifest.checksum
    assert result.files == ["schedules.json", "tables/coi.csv"]


def test_pack_validation_failure(tmp_path: Path) -> None:
    pack_dir = _write_pack(tmp_path)
    manifest = load_manifest(pack_dir)
    bad_manifest = {
        "name": manifest.name,
        "version": manifest.version,
        "license": manifest.license,
        "source": manifest.source,
        "checksum": "deadbeef",
    }
    (pack_dir / "pack.json").write_text(json.dumps(bad_manifest, sort_keys=True))
    result = validate_pack(pack_dir)
    assert result.valid is False


def test_resolve_pack_root_accepts_pack_json(tmp_path: Path) -> None:
    pack_dir = _write_pack(tmp_path)
    pack_path = resolve_pack_root(pack_dir / "pack.json")
    assert pack_path == pack_dir
    assert list_pack_files(pack_path)
