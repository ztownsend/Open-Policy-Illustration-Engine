"""Artifact bundle creation and verification."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import zipfile
from pydantic import BaseModel, ConfigDict

from opie.core.ledger import dumps_json
from opie.core.types import IllustrationRequest, IllustrationResult


class BundleManifest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    bundle_version: str
    files: dict[str, str]
    checksums: dict[str, str]


@dataclass(frozen=True)
class BundleVerificationResult:
    valid: bool
    missing_files: list[str]
    mismatched_checksums: dict[str, dict[str, str]]
    computed_checksums: dict[str, str]


def _checksum_bytes(data: bytes) -> str:
    return sha256(data).hexdigest()


def _zipinfo(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name)
    info.date_time = (1980, 1, 1, 0, 0, 0)
    info.compress_type = zipfile.ZIP_STORED
    return info


def create_bundle(
    request: IllustrationRequest,
    result: IllustrationResult,
    out_path: Path,
) -> None:
    request_json = dumps_json(request).encode("utf-8")
    assumptions_payload = {
        "product_code": request.product_code,
        "scenarios": request.scenarios,
    }
    assumptions_json = dumps_json(assumptions_payload).encode("utf-8")
    result_json = dumps_json(result).encode("utf-8")

    files = {
        "request": "request.json",
        "assumptions": "assumptions.json",
        "result": "result.json",
    }
    checksums = {
        files["request"]: _checksum_bytes(request_json),
        files["assumptions"]: _checksum_bytes(assumptions_json),
        files["result"]: _checksum_bytes(result_json),
    }
    manifest = BundleManifest(
        bundle_version="v1",
        files=files,
        checksums=checksums,
    )
    manifest_json = dumps_json(manifest).encode("utf-8")

    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_STORED) as bundle:
        bundle.writestr(_zipinfo("bundle.json"), manifest_json)
        bundle.writestr(_zipinfo(files["request"]), request_json)
        bundle.writestr(_zipinfo(files["assumptions"]), assumptions_json)
        bundle.writestr(_zipinfo(files["result"]), result_json)


def verify_bundle(path: Path) -> BundleVerificationResult:
    missing_files: list[str] = []
    mismatched: dict[str, dict[str, str]] = {}
    computed: dict[str, str] = {}

    with zipfile.ZipFile(path, "r") as bundle:
        names = set(bundle.namelist())
        if "bundle.json" not in names:
            return BundleVerificationResult(
                valid=False,
                missing_files=["bundle.json"],
                mismatched_checksums={},
                computed_checksums={},
            )
        manifest_payload = json.loads(bundle.read("bundle.json"))
        manifest = BundleManifest.model_validate(manifest_payload)

        for _, filename in manifest.files.items():
            if filename not in names:
                missing_files.append(filename)
                continue
            data = bundle.read(filename)
            checksum = _checksum_bytes(data)
            computed[filename] = checksum
            expected = manifest.checksums.get(filename)
            if expected is None or expected != checksum:
                mismatched[filename] = {
                    "expected": expected or "",
                    "computed": checksum,
                }

    valid = not missing_files and not mismatched
    return BundleVerificationResult(
        valid=valid,
        missing_files=missing_files,
        mismatched_checksums=mismatched,
        computed_checksums=computed,
    )
