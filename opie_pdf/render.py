"""Minimal PDF renderer for IllustrationResult payloads."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from opie.core.types import IllustrationResult


def _escape_pdf_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _build_pdf(lines: list[str]) -> bytes:
    leading = 14
    x_start = 72
    y_start = 720
    text_lines = [
        "BT",
        "/F1 12 Tf",
        f"{x_start} {y_start} Td",
    ]
    for line in lines:
        text_lines.append(f"({_escape_pdf_text(line)}) Tj")
        text_lines.append(f"0 -{leading} Td")
    text_lines.append("ET")
    stream = "\n".join(text_lines).encode("ascii")

    objects: list[bytes] = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
        f"<< /Length {len(stream)} >>\nstream\n".encode("ascii") + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]

    pdf = bytearray()
    pdf.extend(b"%PDF-1.4\n")
    offsets = []
    for idx, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{idx} 0 obj\n".encode("ascii"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")

    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))

    pdf.extend(b"trailer\n")
    pdf.extend(f"<< /Size {len(objects) + 1} /Root 1 0 R >>\n".encode("ascii"))
    pdf.extend(f"startxref\n{xref_offset}\n".encode("ascii"))
    pdf.extend(b"%%EOF\n")
    return bytes(pdf)


def _lines_from_result(result: dict[str, Any]) -> list[str]:
    lines: list[str] = ["OPIE Illustration"]
    product_code = result.get("product_code")
    if product_code:
        lines.append(f"Product: {product_code}")
    metadata = result.get("metadata", {})
    calc_version = metadata.get("calc_version")
    if calc_version:
        lines.append(f"Calc version: {calc_version}")
    ledgers = result.get("ledgers") or {}
    for scenario, ledger in ledgers.items():
        rows = ledger.get("rows", [])
        lines.append(f"Scenario: {scenario} (rows={len(rows)})")
        for row in rows[:5]:
            lines.append(
                "t={t} status={status} av_eop={av} csv={csv} premium={premium}".format(
                    t=row.get("t"),
                    status=row.get("policy_status"),
                    av=row.get("account_value_eop"),
                    csv=row.get("cash_surrender_value"),
                    premium=row.get("premium"),
                )
            )
        if len(rows) > 5:
            lines.append("...")
    return lines


def render_pdf(result: IllustrationResult | dict[str, Any], out_path: Path) -> None:
    payload: dict[str, Any]
    if isinstance(result, IllustrationResult):
        payload = result.model_dump(mode="python")
    else:
        payload = dict(result)
    lines = _lines_from_result(payload)
    pdf_bytes = _build_pdf(lines)
    out_path.write_bytes(pdf_bytes)


def render_pdf_from_json(in_path: Path, out_path: Path) -> None:
    payload = json.loads(in_path.read_text())
    render_pdf(payload, out_path)
