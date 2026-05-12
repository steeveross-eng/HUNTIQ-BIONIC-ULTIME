"""AUDIT_SUPRA_CORRIDORS_REPORT_Ω · Endpoint HTTPS téléchargeable
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · FUSION ADD-ONLY · V30_LOCK

Sert le rapport supra-détaillé (Markdown brut + PDF) en HTTPS public, sans
authentification, sans compression, sans troncature.

Endpoints :
  GET /api/v20/audit/corridors-supra-report.md   → text/markdown brut
  GET /api/v20/audit/corridors-supra-report.txt  → text/plain (alias)
  GET /api/v20/audit/corridors-supra-report.pdf  → application/pdf (archivable)
  GET /api/v20/audit/corridors-supra-report      → JSON {url, size, sha256, generated_at}
"""

from __future__ import annotations

import hashlib
import io
import re
from pathlib import Path

import markdown as md_lib
from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse, Response
from fpdf import FPDF

router = APIRouter(prefix="/api/v20/audit", tags=["AUDIT_SUPRA_CORRIDORS_Ω"])

REPORT_PATH = Path("/app/memory/AUDIT_SUPRA_CORRIDORS_V90.md")
PDF_CACHE_PATH = Path("/app/memory/AUDIT_SUPRA_CORRIDORS_V90.pdf")

# P22Σ_FUSION_VEINEUSE_Ω · 2026-05-12 · STEEVE-MAX
FUSION_REPORT_PATH = Path("/app/memory/FUSION_VEINEUSE_REPORT_P22SIGMA.md")
FUSION_PDF_CACHE = Path("/app/memory/FUSION_VEINEUSE_REPORT_P22SIGMA.pdf")


def _read_report() -> bytes:
    if not REPORT_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Rapport non trouvé : {REPORT_PATH}",
        )
    return REPORT_PATH.read_bytes()


def _build_pdf(markdown_text: str) -> bytes:
    """Convertit le Markdown en PDF via fpdf2 (write_html + parsing minimal).

    Stratégie :
      1. markdown.markdown(text, extensions=['tables','fenced_code'])
         → HTML rendu
      2. Pré-traitement HTML : supprimer/simplifier les tags non supportés
         par fpdf2 (figcaption, etc.), forcer des polices Helvetica.
      3. fpdf2 write_html() rend l'HTML simplifié en PDF.
    """
    html = md_lib.markdown(
        markdown_text,
        extensions=["tables", "fenced_code", "sane_lists"],
        output_format="html5",
    )

    # Nettoyer/simplifier HTML pour fpdf2 (qui supporte un sous-ensemble HTML)
    # - retirer emoji unicode hors plage de la police Helvetica par défaut
    #   (fpdf2 raterait sinon les bytes hors latin-1)
    # - retirer les ancres internes <a href="#..."> et id="..." (fpdf2 exige
    #   set_link pour les Named Destinations, non géré ici)
    html_clean = html
    # 1. Strip internal anchors that fpdf2 tries to resolve as named destinations
    html_clean = re.sub(r'<a\s+href="#[^"]*"[^>]*>(.*?)</a>', r"\1", html_clean, flags=re.DOTALL)
    html_clean = re.sub(r'\s+id="[^"]*"', "", html_clean)
    # 2. Replacements doctrinaux pour préserver le sens
    replacements = {
        "🟦": "[1]", "🟧": "[2]", "🟩": "[3]", "🟫": "[4]", "🟪": "[5]",
        "🟥": "[!]", "📑": "[TOC]", "Ω": "Omega",
        "·": "·",  # garde le bullet
        "→": "->", "←": "<-", "↔": "<->",
        "≤": "<=", "≥": ">=", "≠": "!=",
        "—": "--", "–": "-",
        "…": "...",
        "✅": "[OK]", "❌": "[KO]", "⚠️": "[!]", "📦": "[ARCH]",
        "🔴": "[P0]", "🟡": "[P1]", "🟢": "[P2]",
        "📋": "[DOC]", "🔗": "[URL]", "🛡️": "[LOCK]",
        "🆕": "[NEW]",
    }
    for src, dst in replacements.items():
        html_clean = html_clean.replace(src, dst)

    # Encoder en latin-1 safe : remplacer caractères hors plage par '?'
    html_safe = html_clean.encode("latin-1", errors="replace").decode("latin-1")

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", size=10)

    # En-tête institutionnel
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(255, 106, 0)  # orange BCE-4X
    pdf.cell(0, 8, "AUDIT SUPRA-DETAILLE OMEGA · CORRIDORS · V90",
             new_x="LMARGIN", new_y="NEXT", align="L")
    pdf.set_font("Helvetica", size=8)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 5, "BCE-4X ULTIME ABSOLU · COMMANDANT STEEVE-MAX",
             new_x="LMARGIN", new_y="NEXT", align="L")
    pdf.ln(4)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", size=9)

    # Corps : write_html (fpdf2 supporte h1-h6, p, ul/ol/li, table, code, pre, b/strong/em/i)
    try:
        pdf.write_html(html_safe)
    except Exception as exc:
        # Fallback : rendu texte brut si write_html échoue
        pdf.set_font("Courier", size=8)
        text_safe = re.sub(r"<[^>]+>", "", html_safe)
        pdf.multi_cell(0, 4, text_safe)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(200, 0, 0)
        pdf.ln(4)
        pdf.cell(0, 5, f"[Fallback mode] write_html failed: {exc}")

    # Footer signature
    pdf.ln(8)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(
        0, 4,
        "Rapport genere par Agent BCE-4X ULTIME ABSOLU · "
        "subordonne du COMMANDANT STEEVE-MAX",
        new_x="LMARGIN", new_y="NEXT",
    )

    out = bytes(pdf.output())
    return out


def _get_or_build_pdf() -> bytes:
    """Retourne le PDF cached si à jour, sinon le régénère."""
    if not REPORT_PATH.exists():
        raise HTTPException(404, f"Source markdown introuvable : {REPORT_PATH}")
    md_mtime = REPORT_PATH.stat().st_mtime
    if PDF_CACHE_PATH.exists() and PDF_CACHE_PATH.stat().st_mtime >= md_mtime:
        return PDF_CACHE_PATH.read_bytes()
    # Rebuild
    md_text = REPORT_PATH.read_text(encoding="utf-8")
    pdf_bytes = _build_pdf(md_text)
    PDF_CACHE_PATH.write_bytes(pdf_bytes)
    return pdf_bytes


@router.get("/corridors-supra-report.md")
async def get_report_markdown() -> Response:
    """Sert le rapport en text/markdown brut (téléchargeable directement)."""
    data = _read_report()
    return Response(
        content=data,
        media_type="text/markdown; charset=utf-8",
        headers={
            "Content-Length": str(len(data)),
            "Cache-Control": "public, max-age=300",
            "Content-Disposition": (
                'inline; filename="AUDIT_SUPRA_CORRIDORS_V90.md"'
            ),
            "X-Audit-Authority": "BCE-4X-ULTIME-ABSOLU-STEEVE-MAX",
        },
    )


@router.get("/corridors-supra-report.txt")
async def get_report_text() -> PlainTextResponse:
    """Alias text/plain pour clients ne supportant pas text/markdown."""
    data = _read_report().decode("utf-8")
    return PlainTextResponse(
        content=data,
        headers={
            "Cache-Control": "public, max-age=300",
            "Content-Disposition": (
                'inline; filename="AUDIT_SUPRA_CORRIDORS_V90.txt"'
            ),
            "X-Audit-Authority": "BCE-4X-ULTIME-ABSOLU-STEEVE-MAX",
        },
    )


@router.get("/corridors-supra-report.pdf")
async def get_report_pdf() -> Response:
    """Sert le rapport au format PDF (archivable, persistant)."""
    pdf_bytes = _get_or_build_pdf()
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Length": str(len(pdf_bytes)),
            "Cache-Control": "public, max-age=300",
            "Content-Disposition": (
                'inline; filename="AUDIT_SUPRA_CORRIDORS_V90.pdf"'
            ),
            "X-Audit-Authority": "BCE-4X-ULTIME-ABSOLU-STEEVE-MAX",
        },
    )


@router.get("/corridors-supra-report")
async def get_report_meta() -> dict:
    """Métadonnées JSON : URL téléchargement, taille, SHA256, date."""
    data = _read_report()
    stat = REPORT_PATH.stat()
    sha_md = hashlib.sha256(data).hexdigest()

    # Construire (ou regénérer) le PDF si nécessaire pour exposer sa taille/sha
    try:
        pdf_bytes = _get_or_build_pdf()
        sha_pdf = hashlib.sha256(pdf_bytes).hexdigest()
        pdf_size = len(pdf_bytes)
    except Exception:
        sha_pdf = None
        pdf_size = 0

    return {
        "ok": True,
        "engine": "AUDIT_SUPRA_CORRIDORS_Ω",
        "report_path": str(REPORT_PATH),
        "size_bytes": len(data),
        "size_kb": round(len(data) / 1024, 2),
        "sha256": sha_md,
        "mtime": stat.st_mtime,
        "download_url_md":   "/api/v20/audit/corridors-supra-report.md",
        "download_url_txt":  "/api/v20/audit/corridors-supra-report.txt",
        "download_url_pdf":  "/api/v20/audit/corridors-supra-report.pdf",
        "pdf_size_bytes":    pdf_size,
        "pdf_sha256":        sha_pdf,
        "media_type":        "text/markdown; charset=utf-8",
        "encoding":          "UTF-8",
        "compression":       "none",
        "authentication":    "none (audit institutionnel ouvert)",
        "doctrine":          "V90 · BCE-4X ULTIME ABSOLU",
    }


# ═══════════════════════════════════════════════════════════════════════════
# P22Σ_FUSION_VEINEUSE_Ω · Rapport d'exécution (2026-05-12 · STEEVE-MAX)
# ═══════════════════════════════════════════════════════════════════════════

def _read_fusion_report() -> bytes:
    if not FUSION_REPORT_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Rapport fusion non trouvé : {FUSION_REPORT_PATH}",
        )
    return FUSION_REPORT_PATH.read_bytes()


def _get_or_build_fusion_pdf() -> bytes:
    if not FUSION_REPORT_PATH.exists():
        raise HTTPException(404, f"Source markdown introuvable : {FUSION_REPORT_PATH}")
    md_mtime = FUSION_REPORT_PATH.stat().st_mtime
    if FUSION_PDF_CACHE.exists() and FUSION_PDF_CACHE.stat().st_mtime >= md_mtime:
        return FUSION_PDF_CACHE.read_bytes()
    md_text = FUSION_REPORT_PATH.read_text(encoding="utf-8")
    pdf_bytes = _build_pdf(md_text)
    FUSION_PDF_CACHE.write_bytes(pdf_bytes)
    return pdf_bytes


@router.get("/fusion-veineuse-report.md")
async def get_fusion_markdown() -> Response:
    data = _read_fusion_report()
    return Response(
        content=data,
        media_type="text/markdown; charset=utf-8",
        headers={
            "Content-Length": str(len(data)),
            "Cache-Control": "public, max-age=300",
            "Content-Disposition": (
                'inline; filename="FUSION_VEINEUSE_REPORT_P22SIGMA.md"'
            ),
            "X-Audit-Authority": "BCE-4X-ULTIME-ABSOLU-STEEVE-MAX",
        },
    )


@router.get("/fusion-veineuse-report.txt")
async def get_fusion_text() -> PlainTextResponse:
    data = _read_fusion_report().decode("utf-8")
    return PlainTextResponse(
        content=data,
        headers={
            "Cache-Control": "public, max-age=300",
            "Content-Disposition": (
                'inline; filename="FUSION_VEINEUSE_REPORT_P22SIGMA.txt"'
            ),
            "X-Audit-Authority": "BCE-4X-ULTIME-ABSOLU-STEEVE-MAX",
        },
    )


@router.get("/fusion-veineuse-report.pdf")
async def get_fusion_pdf() -> Response:
    pdf_bytes = _get_or_build_fusion_pdf()
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Length": str(len(pdf_bytes)),
            "Cache-Control": "public, max-age=300",
            "Content-Disposition": (
                'inline; filename="FUSION_VEINEUSE_REPORT_P22SIGMA.pdf"'
            ),
            "X-Audit-Authority": "BCE-4X-ULTIME-ABSOLU-STEEVE-MAX",
        },
    )


@router.get("/fusion-veineuse-report")
async def get_fusion_meta() -> dict:
    data = _read_fusion_report()
    sha_md = hashlib.sha256(data).hexdigest()
    try:
        pdf_bytes = _get_or_build_fusion_pdf()
        sha_pdf = hashlib.sha256(pdf_bytes).hexdigest()
        pdf_size = len(pdf_bytes)
    except Exception:
        sha_pdf = None
        pdf_size = 0
    return {
        "ok": True,
        "engine": "P22Σ_FUSION_VEINEUSE_Ω",
        "report_path": str(FUSION_REPORT_PATH),
        "size_bytes": len(data),
        "size_kb": round(len(data) / 1024, 2),
        "sha256": sha_md,
        "mtime": FUSION_REPORT_PATH.stat().st_mtime,
        "download_url_md":   "/api/v20/audit/fusion-veineuse-report.md",
        "download_url_txt":  "/api/v20/audit/fusion-veineuse-report.txt",
        "download_url_pdf":  "/api/v20/audit/fusion-veineuse-report.pdf",
        "pdf_size_bytes":    pdf_size,
        "pdf_sha256":        sha_pdf,
        "render_sha256":     "70dae2579e3bb2e986dce282944709d38c997d24a343072c562a5cf360dd1cda",
        "doctrine":          "P22Σ_V4_BACKBONE_SUBNETS_Ω · V90 · BCE-4X ULTIME ABSOLU",
    }
