"""
EXPORT-INSTITUTIONNEL-V20-Ω — PDF signé (Phase X-D)
=====================================================
Agrège les rapports Phase X / X-B / X-C + hashes officiels Document
Maître + Registry Lock dans un PDF institutionnel signé.

Signature : HMAC-SHA256 du contenu concaténé avec clé interne.

Endpoint :
  GET /api/v20/territoire/export/institutionnel/v20
"""
import hashlib
import hmac
import io
from datetime import datetime, timezone
from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from engines.v8_institutional.engine_science_omega import register_engine, mark_call
from engines.v8_institutional.registry_lock_omega import get_registry_lock_status

register_engine(
    "EXPORT-INSTITUTIONNEL-V20-Ω",
    "V1-PHASE-X-D-2026-04",
    "Export PDF institutionnel signé (rapports + hashes + HMAC)",
    "GOUVERNANCE",
    [],
)

router = APIRouter(prefix="/api/v20/territoire", tags=["V20 Export Institutionnel"])

REPORTS = [
    ("PHASE X-B REPORT", "/app/memory/PHASE_X_B_VALIDATION_REPORT.md"),
    ("PHASE XI REPORT", "/app/memory/PHASE_XI_VALIDATION_REPORT.md"),
    ("PHASE X-C REPORT", "/app/memory/PHASE_X_C_VALIDATION_REPORT.md"),
]

# Clé interne (non-secrète pour ce MVP ; rotation via env var en prod)
_SIGN_KEY = b"BCE-4X-ULTIME-ABSOLU-STEEVE-MAX-V20"


def _build_signature(content: bytes) -> str:
    return hmac.new(_SIGN_KEY, content, hashlib.sha256).hexdigest()


def _read_report(path: str) -> str:
    p = Path(path)
    if not p.exists():
        return f"⚠ Rapport manquant : {path}"
    return p.read_text(encoding="utf-8")


def _build_pdf() -> tuple[bytes, dict]:
    mark_call("EXPORT-INSTITUTIONNEL-V20-Ω")
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                             topMargin=2 * cm, bottomMargin=2 * cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleGov", parent=styles["Title"],
                                  fontSize=20, textColor=HexColor("#0e1117"),
                                  alignment=1, spaceAfter=20)
    h2 = ParagraphStyle("H2Gov", parent=styles["Heading2"],
                         textColor=HexColor("#1f2937"), spaceBefore=14, spaceAfter=8)
    body = ParagraphStyle("BodyGov", parent=styles["BodyText"],
                           fontSize=9, leading=12, textColor=HexColor("#111827"))
    mono = ParagraphStyle("MonoGov", parent=styles["Code"],
                           fontSize=8, leading=10, textColor=HexColor("#1f2937"),
                           fontName="Courier")

    lock = get_registry_lock_status()
    now = datetime.now(timezone.utc).isoformat()

    story = []
    story.append(Paragraph("BIONIC OS V20-SUPRA<br/>EXPORT INSTITUTIONNEL SIGNÉ", title_style))
    story.append(Paragraph(f"Émis le {now}", body))
    story.append(Paragraph("Protocole : BCE-4X ULTIME ABSOLU · Commandant STEEVE-MAX", body))
    story.append(Spacer(1, 12))

    # Hash table
    hash_data = [
        ["Artefact", "SHA-256"],
        ["Document Maître", lock["document_maitre"]["sha256"][:48] + "…"],
        ["Registry Lock", lock["sha256"][:48] + "…"],
        ["Registry version", lock["version"]],
        ["Engines scellés", str(lock["engines_count"])],
    ]
    tbl = Table(hash_data, colWidths=[4 * cm, 13 * cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#0e1117")),
        ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#f3f4f6")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.25, HexColor("#9ca3af")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(tbl)
    story.append(PageBreak())

    # Reports
    for title, path in REPORTS:
        story.append(Paragraph(title, h2))
        raw = _read_report(path)
        # Simplification : on coupe en paragraphes de ~100 lignes
        for line in raw.split("\n"):
            safe = (line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
            if safe.strip().startswith("#"):
                story.append(Paragraph(f"<b>{safe}</b>", body))
            elif safe.strip().startswith("```"):
                continue
            elif safe.strip().startswith("|"):
                story.append(Paragraph(f"<font face='Courier' size='7'>{safe}</font>", mono))
            else:
                story.append(Paragraph(safe or "&nbsp;", body))
        story.append(PageBreak())

    # Signature page
    story.append(Paragraph("SIGNATURE INSTITUTIONNELLE", h2))
    # Concat pour signature
    payload_to_sign = (
        f"{now}|DOCMAITRE={lock['document_maitre']['sha256']}|"
        f"REGISTRY={lock['sha256']}|ENGINES={lock['engines_count']}"
    ).encode("utf-8")
    signature = _build_signature(payload_to_sign)

    sig_data = [
        ["Horodatage UTC", now],
        ["Algorithme", "HMAC-SHA256"],
        ["Payload signé", payload_to_sign.decode("utf-8")[:88] + "…"],
        ["Signature", signature],
        ["Autorité", "Commandant STEEVE-MAX · BCE-4X ULTIME ABSOLU"],
    ]
    sig_tbl = Table(sig_data, colWidths=[4 * cm, 13 * cm])
    sig_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), HexColor("#1f2937")),
        ("TEXTCOLOR", (0, 0), (0, -1), HexColor("#f3f4f6")),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.25, HexColor("#9ca3af")),
    ]))
    story.append(sig_tbl)

    doc.build(story)
    pdf_bytes = buf.getvalue()
    buf.close()

    metadata = {
        "generated_at": now,
        "size_bytes": len(pdf_bytes),
        "signature_hmac_sha256": signature,
        "payload_signed": payload_to_sign.decode("utf-8"),
        "reports_included": [t for t, _ in REPORTS],
        "registry_sha256": lock["sha256"],
        "document_maitre_sha256": lock["document_maitre"]["sha256"],
        "algorithm": "HMAC-SHA256",
    }
    return pdf_bytes, metadata


@router.get("/export/institutionnel/v20")
async def export_v20(metadata_only: bool = False):
    """Export PDF institutionnel signé V20-SUPRA. ?metadata_only=true pour JSON."""
    pdf_bytes, meta = _build_pdf()
    if metadata_only:
        return meta
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'attachment; filename="BIONIC_OS_V20_EXPORT.pdf"',
            "X-Signature-HMAC-SHA256": meta["signature_hmac_sha256"],
            "X-Registry-SHA256": meta["registry_sha256"],
            "X-Generated-At": meta["generated_at"],
        },
    )
