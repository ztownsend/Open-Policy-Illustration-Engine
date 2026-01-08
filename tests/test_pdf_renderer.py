import json
from pathlib import Path

from opie import run_illustration
from opie.core.types import IllustrationRequest
from opie_pdf.render import render_pdf


def test_pdf_renderer_writes_pdf(tmp_path: Path) -> None:
    payload = json.loads(Path("examples/term_request.json").read_text())
    request = IllustrationRequest.model_validate(payload)
    result = run_illustration(request)

    out_path = tmp_path / "out.pdf"
    render_pdf(result, out_path)

    data = out_path.read_bytes()
    assert data.startswith(b"%PDF")
    assert b"OPIE Illustration" in data
