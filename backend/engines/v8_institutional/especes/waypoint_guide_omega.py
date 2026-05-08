"""waypoint_guide_omega.py — P17 WAYPOINT_GUIDE_CREATE_Ω
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI_GÉNÉRIQUE_STRICT

P17 — Fiche terrain opérationnelle pour un point géographique (waypoint) :
  · Qualité habitat (dérivée habitat_complete_merge overlay)
  · Tendances décennales (dérivées multi_year_dense_grid overlay)
  · Recommandations affût (calcul anti-générique direct)
  · Export dual HTML + PDF

DOCTRINE :
  · Lecture seule des overlays doctrinaux
  · Aucune fabrication : si overlay source absent → caveat explicite
  · Recommandations = calcul déterministe depuis les métriques lues
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import hashlib
import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


GUIDE_ROOT = Path(
    "/app/backend/data/pipelines/waypoint_guide")
GUIDE_HISTORY_PATH = GUIDE_ROOT / "guide_history.jsonl"
GUIDES_STORE = GUIDE_ROOT / "store"


HABITAT_OVERLAY_PATH = Path(
    "/app/backend/data/pipelines/habitat_complete_merge/"
    "habitat_complete_merge_overlay.json")
MULTI_YEAR_OVERLAY_PATH = Path(
    "/app/backend/data/pipelines/multi_year_dense_grid/"
    "multi_year_dense_grid_overlay.json")
ANTHROP_OVERLAY_PATH = Path(
    "/app/backend/data/pipelines/anthropogenic_pressure/"
    "anthropogenic_pressure_overlay.json")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _load_json(p: Path) -> Optional[Dict[str, Any]]:
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _haversine_m(
    lat1: float, lon1: float, lat2: float, lon2: float,
) -> float:
    r = 6371000.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = (math.sin(dphi / 2) ** 2
         + math.cos(phi1) * math.cos(phi2)
         * math.sin(dlmb / 2) ** 2)
    return 2 * r * math.asin(math.sqrt(a))


def _derive_habitat_quality(
    lat: float, lon: float,
    habitat_overlay: Optional[Dict[str, Any]],
    radius_m: int,
) -> Dict[str, Any]:
    """Dérivation anti-générique : on lit réellement l'overlay et on
    filtre par distance. Si aucune cellule → caveat explicite."""
    if not habitat_overlay:
        return {
            "status": "HABITAT_OVERLAY_ABSENT",
            "caveat": (
                "habitat_complete_merge overlay not found — "
                "P9 COMPLETE_MERGE doit être exécuté."),
        }
    history = habitat_overlay.get("history", [])
    if not history:
        return {
            "status": "HABITAT_OVERLAY_EMPTY_HISTORY",
            "caveat": "Pas d'entrées dans history.",
        }
    last = history[-1]
    cells = last.get("cells") or last.get("outputs_12") or []
    # Tolérance de forme : si pas de cells lat/lon → status doctrinal
    matching_cells: List[Dict[str, Any]] = []
    for c in cells if isinstance(cells, list) else []:
        c_lat = c.get("lat") or c.get("latitude")
        c_lon = c.get("lon") or c.get("longitude")
        if (isinstance(c_lat, (int, float))
                and isinstance(c_lon, (int, float))):
            d = _haversine_m(lat, lon, c_lat, c_lon)
            if d <= radius_m:
                matching_cells.append({"distance_m": round(d, 1),
                                        **c})
    return {
        "status": "DERIVED",
        "n_cells_matching": len(matching_cells),
        "radius_m": radius_m,
        "sample_cells": matching_cells[:5],
        "habitat_last_updated_utc": last.get(
            "executed_at_utc") or last.get("generated_at_utc"),
        "habitat_last_verdict": last.get("verdict"),
    }


def _derive_decadal_trend(
    multi_year_overlay: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    if not multi_year_overlay:
        return {
            "status": "MULTI_YEAR_OVERLAY_ABSENT",
            "caveat": (
                "multi_year_dense_grid overlay not found — "
                "P11 MULTI_YEAR_DENSE_GRID doit être exécuté."),
        }
    history = multi_year_overlay.get("history", [])
    if not history:
        return {"status": "EMPTY_HISTORY"}
    last = history[-1]
    return {
        "status": "DERIVED",
        "n_years": last.get("n_years_processed"),
        "mann_kendall_verdict": last.get("verdict"),
        "multi_year_last_updated_utc": last.get(
            "executed_at_utc"),
    }


def _derive_affuts_recommendations(
    habitat_quality: Dict[str, Any],
    trend: Dict[str, Any],
) -> List[Dict[str, str]]:
    recs: List[Dict[str, str]] = []
    if habitat_quality.get("status") == "DERIVED":
        n = habitat_quality.get("n_cells_matching", 0)
        if n >= 3:
            recs.append({
                "category": "AFFUT_POSITIONING",
                "action": (
                    f"{n} cellules habitat qualifiées détectées "
                    "dans le rayon — zone favorable pour affût fixe."),
                "priority": "P1",
            })
        else:
            recs.append({
                "category": "AFFUT_POSITIONING",
                "action": (
                    f"Seulement {n} cellules habitat — "
                    "préférer affût mobile ou repositionnement."),
                "priority": "P2",
            })
    else:
        recs.append({
            "category": "AFFUT_POSITIONING",
            "action": (
                "Habitat overlay indisponible — lever un affût "
                "reconnaissance est recommandé avant installation."),
            "priority": "P0",
        })
    if trend.get("status") == "DERIVED":
        recs.append({
            "category": "DECADAL_PLANNING",
            "action": (
                f"Tendance décennale: {trend.get('mann_kendall_verdict')} — "
                "ajuster stratégie long terme (rotation stands)."),
            "priority": "P2",
        })
    return recs


def generate_waypoint_field_guide(
    lat: float,
    lon: float,
    species: str,
    waypoint_id: Optional[str] = None,
    radius_m: int = 500,
    include_pdf: bool = True,
    include_html: bool = True,
    persist: bool = True,
) -> Dict[str, Any]:
    """Génère un guide field par waypoint (anti-générique strict)."""
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        require_guardrails_enforced, log_forensic_event,
    )
    require_guardrails_enforced("generate_waypoint_field_guide")

    if not (-90 <= lat <= 90):
        raise ValueError(f"LATITUDE_INVALID::{lat}")
    if not (-180 <= lon <= 180):
        raise ValueError(f"LONGITUDE_INVALID::{lon}")
    if radius_m < 10 or radius_m > 50000:
        raise ValueError(
            f"RADIUS_INVALID::{radius_m}::expected_10..50000m")

    t0 = time.time()
    habitat_overlay = _load_json(HABITAT_OVERLAY_PATH)
    multi_year_overlay = _load_json(MULTI_YEAR_OVERLAY_PATH)
    anth_overlay = _load_json(ANTHROP_OVERLAY_PATH)

    habitat_quality = _derive_habitat_quality(
        lat, lon, habitat_overlay, radius_m)
    trend = _derive_decadal_trend(multi_year_overlay)
    recommendations = _derive_affuts_recommendations(
        habitat_quality, trend)

    guide = {
        "manifest_id": "WAYPOINT_FIELD_GUIDE_Ω",
        "ordre": "P17_WAYPOINT_GUIDE_CREATE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "species": species,
        "point_id": waypoint_id or f"WP_{lat:.5f}_{lon:.5f}",
        "latitude": lat,
        "longitude": lon,
        "radius_m": radius_m,
        "habitat_quality": habitat_quality,
        "decadal_trend": trend,
        "anthropogenic_present": bool(anth_overlay),
        "recommendations": recommendations,
        "recommendations_count": len(recommendations),
        "generated_at_utc": _utc_now(),
        "anti_generique_strict": True,
        "v30_lock": "INVIOLÉ",
    }
    guide_sha256 = hashlib.sha256(
        json.dumps(guide, sort_keys=True,
                   ensure_ascii=False, default=str).encode("utf-8")
    ).hexdigest()
    guide["guide_sha256"] = guide_sha256

    files_generated: Dict[str, Any] = {}
    if persist:
        GUIDES_STORE.mkdir(parents=True, exist_ok=True)
        prefix = f"{guide_sha256[:16]}_{species}"
        json_path = GUIDES_STORE / f"{prefix}.json"
        json_path.write_text(
            json.dumps(guide, ensure_ascii=False, indent=2),
            encoding="utf-8")
        files_generated["json_path"] = str(json_path)
        files_generated["json_sha256"] = hashlib.sha256(
            json_path.read_bytes()).hexdigest()
        if include_html:
            html_path = GUIDES_STORE / f"{prefix}.html"
            html_path.write_text(
                _render_html(guide), encoding="utf-8")
            files_generated["html_path"] = str(html_path)
            files_generated["html_sha256"] = hashlib.sha256(
                html_path.read_bytes()).hexdigest()
        if include_pdf:
            pdf_path = GUIDES_STORE / f"{prefix}.pdf"
            _render_pdf(guide, pdf_path)
            files_generated["pdf_path"] = str(pdf_path)
            files_generated["pdf_sha256"] = hashlib.sha256(
                pdf_path.read_bytes()).hexdigest()
        GUIDE_ROOT.mkdir(parents=True, exist_ok=True)
        with open(GUIDE_HISTORY_PATH, "a",
                  encoding="utf-8") as f:
            f.write(json.dumps({
                "guide_sha256": guide_sha256,
                "point_id": guide["point_id"],
                "species": species,
                "files": files_generated,
                "generated_at_utc": _utc_now(),
            }, ensure_ascii=False, default=str) + "\n")

    log_forensic_event(
        scope="HOOK_ACTIVATIONS",
        event="WAYPOINT_FIELD_GUIDE_GENERATED",
        details={
            "guide_sha256": guide_sha256,
            "species": species,
            "point_id": guide["point_id"],
        },
        persist=True)

    guide["files_generated"] = files_generated
    guide["elapsed_s"] = round(time.time() - t0, 3)
    return guide


def _render_html(guide: Dict[str, Any]) -> str:
    recs = "".join(
        f"<li><b>[{r['priority']}] {r['category']}</b> — {r['action']}</li>"
        for r in guide["recommendations"])
    hq = guide["habitat_quality"]
    tr = guide["decadal_trend"]
    return f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8"/>
<title>WAYPOINT FIELD GUIDE · {guide['point_id']}</title>
<style>
  body{{font-family:Georgia,serif;background:#0f1419;color:#e8e4d9;
        margin:0;padding:2rem;line-height:1.6}}
  h1{{color:#d4a017;border-bottom:2px solid #d4a017}}
  h2{{color:#7cb518;margin-top:1.5rem}}
  .box{{background:#1d2330;padding:1rem;border-left:4px solid #d4a017;
         margin:1rem 0}}
  code{{font-family:monospace;color:#7cb518;font-size:.8rem}}
</style></head>
<body>
<h1>FIELD GUIDE · {guide['species']}</h1>
<p><b>Point ID :</b> {guide['point_id']}<br/>
<b>Coordonnées :</b> {guide['latitude']:.5f}, {guide['longitude']:.5f}<br/>
<b>Rayon :</b> {guide['radius_m']} m<br/>
<b>Generated UTC :</b> {guide['generated_at_utc']}<br/>
<b>Guide SHA-256 :</b> <code>{guide['guide_sha256']}</code></p>

<div class="box">V30 LOCK: INVIOLÉ · ANTI-GÉNÉRIQUE STRICT · FUSION ADD-ONLY</div>

<h2>Qualité habitat</h2>
<p>Status: <code>{hq.get('status')}</code><br/>
Cellules qualifiées: {hq.get('n_cells_matching', 0)}<br/>
{hq.get('caveat', '')}</p>

<h2>Tendance décennale</h2>
<p>Status: <code>{tr.get('status')}</code><br/>
Mann-Kendall verdict: {tr.get('mann_kendall_verdict') or '—'}<br/>
Années: {tr.get('n_years') or '—'}</p>

<h2>Recommandations affût ({guide['recommendations_count']})</h2>
<ul>{recs}</ul>

<hr/>
<p style="font-size:.75rem;opacity:.6">COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU</p>
</body></html>
"""


def _render_pdf(guide: Dict[str, Any], out_path: Path) -> None:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title", parent=styles["Heading1"],
        textColor=colors.HexColor("#d4a017"),
        fontSize=18, spaceAfter=12)
    h2 = ParagraphStyle(
        "H2", parent=styles["Heading2"],
        textColor=colors.HexColor("#7cb518"),
        fontSize=13, spaceBefore=14, spaceAfter=6)
    doc = SimpleDocTemplate(str(out_path), pagesize=A4,
                             title=f"Field Guide {guide['point_id']}")
    story: List[Any] = []
    story.append(Paragraph(
        f"FIELD GUIDE · {guide['species']}", title_style))
    story.append(Paragraph(
        f"<b>Point ID:</b> {guide['point_id']}<br/>"
        f"<b>Coordonnées:</b> {guide['latitude']:.5f}, "
        f"{guide['longitude']:.5f}<br/>"
        f"<b>Rayon:</b> {guide['radius_m']} m<br/>"
        f"<b>Generated UTC:</b> {guide['generated_at_utc']}<br/>"
        f"<b>SHA-256:</b> <font face='Courier' size='7'>"
        f"{guide['guide_sha256']}</font>", styles["Normal"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph("V30 LOCK: INVIOLÉ · ANTI-GÉNÉRIQUE",
                            styles["Italic"]))
    story.append(Paragraph("Qualité habitat", h2))
    hq = guide["habitat_quality"]
    story.append(Paragraph(
        f"Status: {hq.get('status')}<br/>"
        f"Cellules qualifiées: {hq.get('n_cells_matching', 0)}",
        styles["Normal"]))
    story.append(Paragraph("Tendance décennale", h2))
    tr = guide["decadal_trend"]
    story.append(Paragraph(
        f"Status: {tr.get('status')}<br/>"
        f"Mann-Kendall: {tr.get('mann_kendall_verdict') or '—'}",
        styles["Normal"]))
    story.append(Paragraph(
        f"Recommandations ({guide['recommendations_count']})", h2))
    for r in guide["recommendations"]:
        story.append(Paragraph(
            f"<b>[{r['priority']}] {r['category']}</b> — {r['action']}",
            styles["Normal"]))
        story.append(Spacer(1, 4))
    story.append(Spacer(1, 20))
    story.append(Paragraph(
        "COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU",
        styles["Italic"]))
    doc.build(story)


def get_waypoint_guide_status() -> Dict[str, Any]:
    if not GUIDE_HISTORY_PATH.exists():
        return {
            "manifest_id": "WAYPOINT_GUIDE_STATUS_Ω",
            "current_status": "NO_GUIDES_GENERATED",
            "v30_lock": "INVIOLÉ",
            "scanned_at_utc": _utc_now(),
        }
    lines = GUIDE_HISTORY_PATH.read_text(
        encoding="utf-8").splitlines()
    last = json.loads(lines[-1]) if lines else None
    return {
        "manifest_id": "WAYPOINT_GUIDE_STATUS_Ω",
        "current_status": "ACTIVE" if lines else "NO_GUIDES",
        "n_guides_generated": len(lines),
        "last_guide_sha256": (
            last.get("guide_sha256") if last else None),
        "last_point_id": (
            last.get("point_id") if last else None),
        "last_species": last.get("species") if last else None,
        "last_generated_utc": (
            last.get("generated_at_utc") if last else None),
        "store_path": str(GUIDES_STORE),
        "v30_lock": "INVIOLÉ",
        "scanned_at_utc": _utc_now(),
    }


__all__ = [
    "GUIDE_ROOT",
    "GUIDES_STORE",
    "GUIDE_HISTORY_PATH",
    "generate_waypoint_field_guide",
    "get_waypoint_guide_status",
]
