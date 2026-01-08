"""Assumption pack helpers for portable, checksummed bundles."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from hashlib import sha256
import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, field_validator

from opie.core.errors import AssumptionError
from opie.core.ledger import dumps_json


class PackFile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str
    checksum: str

    @field_validator("path")
    @classmethod
    def _validate_path(cls, value: str) -> str:
        if value.startswith(("/", "\\")):
            raise ValueError("pack file paths must be relative")
        if value in {"", ".", "./"}:
            raise ValueError("pack file path must be a file")
        if ".." in Path(value).parts:
            raise ValueError("pack file paths must not include '..'")
        return value


class PackSignature(BaseModel):
    model_config = ConfigDict(extra="forbid")

    method: str
    value: str
    key_id: str | None = None


class PackLineage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    parents: list[str] = Field(default_factory=list)
    notes: str | None = None


class PackManifest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    version: str
    license: str
    source: str
    effective_date: date
    lineage: PackLineage | None = None
    files: list[PackFile]
    signature: PackSignature

    @field_validator("files")
    @classmethod
    def _validate_files(cls, value: list[PackFile]) -> list[PackFile]:
        paths = [item.path for item in value]
        if len(paths) != len(set(paths)):
            raise ValueError("pack file paths must be unique")
        if paths != sorted(paths):
            raise ValueError("pack files must be sorted by path")
        if any(path == "pack.json" for path in paths):
            raise ValueError("pack.json must not be listed in pack files")
        return value


@dataclass(frozen=True)
class PackValidationResult:
    manifest: PackManifest
    files: list[str]
    missing_files: list[str]
    extra_files: list[str]
    mismatched_checksums: dict[str, dict[str, str]]
    signature_valid: bool
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
    return [item.path for item in compute_pack_files(root)]


def compute_file_checksum(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def compute_pack_files(root: Path) -> list[PackFile]:
    files: list[PackFile] = []
    for path in _pack_file_paths(root):
        rel = path.relative_to(root).as_posix()
        files.append(PackFile(path=rel, checksum=compute_file_checksum(path)))
    return files


def compute_pack_checksum(root: Path) -> str:
    hasher = sha256()
    for item in compute_pack_files(root):
        hasher.update(item.path.encode("utf-8"))
        hasher.update(b"\n")
        hasher.update(item.checksum.encode("utf-8"))
        hasher.update(b"\n")
    return hasher.hexdigest()


def _signature_payload(manifest: PackManifest) -> str:
    payload = manifest.model_dump(mode="python", exclude={"signature"})
    return dumps_json(payload)


def sign_manifest(manifest: PackManifest) -> PackSignature:
    digest = sha256(_signature_payload(manifest).encode("utf-8")).hexdigest()
    return PackSignature(method="stub-sha256", value=digest)


def verify_signature(manifest: PackManifest) -> bool:
    method = manifest.signature.method
    if method == "none":
        return True
    if method != "stub-sha256":
        return False
    expected = sign_manifest(manifest).value
    return manifest.signature.value == expected


def load_manifest(root: Path) -> PackManifest:
    manifest_path = root / "pack.json"
    if not manifest_path.exists():
        raise AssumptionError("pack.json not found", values={"path": str(manifest_path)})
    payload = json.loads(manifest_path.read_text())
    return PackManifest.model_validate(payload)


def validate_pack(root: Path) -> PackValidationResult:
    manifest = load_manifest(root)
    computed_files = compute_pack_files(root)
    computed_paths = [item.path for item in computed_files]
    computed_map = {item.path: item.checksum for item in computed_files}
    manifest_map = {item.path: item.checksum for item in manifest.files}

    missing = sorted(path for path in manifest_map if path not in computed_map)
    extra = sorted(path for path in computed_map if path not in manifest_map)
    mismatched: dict[str, dict[str, str]] = {}
    for path in sorted(set(computed_map).intersection(manifest_map)):
        expected = manifest_map[path]
        actual = computed_map[path]
        if expected != actual:
            mismatched[path] = {"expected": expected, "computed": actual}

    signature_valid = verify_signature(manifest)
    valid = not missing and not extra and not mismatched and signature_valid
    return PackValidationResult(
        manifest=manifest,
        files=computed_paths,
        missing_files=missing,
        extra_files=extra,
        mismatched_checksums=mismatched,
        signature_valid=signature_valid,
        valid=valid,
    )
