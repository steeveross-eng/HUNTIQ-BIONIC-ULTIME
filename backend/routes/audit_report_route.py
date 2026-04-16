"""
ENGINES-AUDIT-Ω-V13 — Public report endpoints
Serves audit reports as plain text — NO AUTH
"""
from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
import os

router = APIRouter(prefix="/api/v8/audit", tags=["Audit Report"])

@router.get("/engines-report", response_class=PlainTextResponse)
async def get_engines_report():
    path = "/app/memory/ENGINES_AUDIT_REPORT.md"
    if os.path.exists(path):
        with open(path, "r") as f:
            return PlainTextResponse(f.read(), media_type="text/plain; charset=utf-8")
    return PlainTextResponse("Report not found", status_code=404)

@router.get("/engines-report-raw-full", response_class=PlainTextResponse)
async def get_engines_report_raw_full():
    """RAW DUMP COMPLET — 827 fichiers, ~222,000 lignes, code source integral."""
    path = "/app/memory/ENGINES_AUDIT_REPORT_RAW_FULL.md"
    if os.path.exists(path):
        with open(path, "r") as f:
            return PlainTextResponse(f.read(), media_type="text/plain; charset=utf-8")
    return PlainTextResponse("Raw report not found", status_code=404)
