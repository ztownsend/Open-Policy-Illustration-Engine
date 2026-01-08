"""Assumption pack helpers for portable, checksummed bundles."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from opie.core.errors import AssumptionError


class PackManifest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    version: str
    license: str
    source: str
    checksum: str


@dataclass(frozen=True)
class PackValidationResult:
    manifest: PackManifest
    files: list[str]
    computed_checksum: str
    valid: bool


def resolve_pack_root(path: Path) -> Path:
    if path.is_dir():
        return path
    if path.is_file() and path.name == "pack.json":
        return path.parent
    raise AssumptionError("pack path must be a directory or pack.json", values={"path": str(path)})


def _pack_file_paths(root: Path) -> list[Path]:
    files = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.name == "pack.json":
            continue
        files.append(path)
    files.sort(key=lambda item: item.relative_to(root).as_posix())
    return files


def list_pack_files(root: Path) -> list[str]:
    return [path.relative_to(root).as_posix() for path in _pack_file_paths(root)]


def compute_pack_checksum(root: Path) -> str:
    hasher = sha256()
    for path in _pack_file_paths(root):
        rel = path.relative_to(root).as_posix()
        hasher.update(rel.encode("utf-8"))
        hasher.update(b"\n")
        hasher.update(path.read_bytes())
        hasher.update(b"\n")
    return hasher.hexdigest()


def load_manifest(root: Path) -> PackManifest:
    manifest_path = root / "pack.json"
    if not manifest_path.exists():
        raise AssumptionError("pack.json not found", values={"path": str(manifest_path)})
    payload = json.loads(manifest_path.read_text())
    return PackManifest.model_validate(payload)


def validate_pack(root: Path) -> PackValidationResult:
    manifest = load_manifest(root)
    files = list_pack_files(root)
    computed = compute_pack_checksum(root)
    valid = computed == manifest.checksum
    return PackValidationResult(
        manifest=manifest,
        files=files,
        computed_checksum=computed,
        valid=valid,
    )
