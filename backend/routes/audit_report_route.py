"""
ENGINES-AUDIT-Ω-V13 — Public report endpoint
Serves the complete audit report as plain text
NO AUTH required — institutional public access
"""
from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
import os

router = APIRouter(prefix="/api/v8/audit", tags=["Audit Report V13"])

@router.get("/engines-report", response_class=PlainTextResponse)
async def get_engines_report():
    """Serve complete engines audit report — no auth, no truncation."""
    report_path = "/app/memory/ENGINES_AUDIT_REPORT.md"
    if os.path.exists(report_path):
        with open(report_path, "r") as f:
            content = f.read()
        return PlainTextResponse(content, media_type="text/plain; charset=utf-8")
    return PlainTextResponse("Report not found", status_code=404)
