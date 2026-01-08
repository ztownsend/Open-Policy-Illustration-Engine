import json
import zipfile
from pathlib import Path

from opie import run_illustration
from opie.bundle import create_bundle, verify_bundle
from opie.core.types import IllustrationRequest


def test_bundle_create_and_verify(tmp_path: Path) -> None:
    payload = json.loads(Path("examples/term_request.json").read_text())
    request = IllustrationRequest.model_validate(payload)
    result = run_illustration(request)

    bundle_path = tmp_path / "bundle.zip"
    create_bundle(request, result, bundle_path)

    verification = verify_bundle(bundle_path)
    assert verification.valid is True
    assert verification.missing_files == []
    assert verification.mismatched_checksums == {}


def test_bundle_verify_detects_mismatch(tmp_path: Path) -> None:
    payload = json.loads(Path("examples/term_request.json").read_text())
    request = IllustrationRequest.model_validate(payload)
    result = run_illustration(request)

    bundle_path = tmp_path / "bundle.zip"
    create_bundle(request, result, bundle_path)

    tampered_path = tmp_path / "tampered.zip"
    with zipfile.ZipFile(bundle_path, "r") as original:
        files = {name: original.read(name) for name in original.namelist()}

    files["result.json"] = files["result.json"] + b"\n"

    with zipfile.ZipFile(tampered_path, "w", compression=zipfile.ZIP_STORED) as out:
        for name, data in files.items():
            out.writestr(name, data)

    verification = verify_bundle(tampered_path)
    assert verification.valid is False
    assert "result.json" in verification.mismatched_checksums
