"""layer_interpretation_manual_omega.py — P18 LAYER_INTERPRETATION_MANUAL_Ω
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI_GÉNÉRIQUE_STRICT

P18 — Manual doctrinal d'interprétation des 18 couches :
  · Définitions explicites par couche
  · Usage opérationnel (comment lire la métrique)
  · Exemples d'interprétation
  · Export HTML + PDF

DOCTRINE :
  · Contenu strictement documentaire / institutionnel
  · Aucune métrique fabriquée
  · Références explicites aux overlays producteurs
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


MANUAL_ROOT = Path(
    "/app/backend/data/pipelines/layer_interpretation_manual")
MANUAL_HISTORY_PATH = MANUAL_ROOT / "manual_history.jsonl"
MANUAL_STORE = MANUAL_ROOT / "store"


# 18 couches doctrinales
LAYERS_CATALOG: List[Dict[str, str]] = [
    {"code": "L01_NDVI_DENSE_GRID",
     "name": "NDVI Dense Grid (NASA MOD13Q1)",
     "definition": "Normalized Difference Vegetation Index "
                    "(250m, 16-day composite).",
     "usage": "NDVI 0.4-0.7 = habitat optimal cerf; >0.75 = couverture dense.",
     "example": "Cellule NDVI=0.62 → optimal cerf Odocoileus virginianus.",
     "source_overlay": "nasa_ndvi_dense_grid"},
    {"code": "L02_HABITAT_OUTPUTS_12",
     "name": "Habitat Outputs 12/12",
     "definition": "Agrégation 12 métriques habitat doctrinales.",
     "usage": "Score habitat composite ≥0.7 = zone primaire.",
     "example": "12 outputs = saline, alimentation, rut, repos, etc.",
     "source_overlay": "habitat_complete_merge"},
    {"code": "L03_ANTHROPOGENIC_PRESSURE",
     "name": "Pression anthropique (OSM + WorldPop)",
     "definition": "Densité humaine + infrastructures routes/bâtiments.",
     "usage": "p95>0.7 = éviter implantation affût.",
     "example": "OSM highway + population density fusion.",
     "source_overlay": "anthropogenic_pressure"},
    {"code": "L04_TEMPORAL_RUT",
     "name": "Rut Temporal Window",
     "definition": "Fenêtres temporelles doctrinales espèce.",
     "usage": "Cerf oct-nov / orignal sep-oct / ours juin-juil.",
     "example": "Rut cerf = activation stratégies d'appel.",
     "source_overlay": "temporal_rut"},
    {"code": "L05_MULTI_YEAR_TREND",
     "name": "Mann-Kendall Decadal Trend",
     "definition": "Tendance statistique 10 ans NDVI (τ, p<0.05).",
     "usage": "Tendance significative négative = habitat en dégradation.",
     "example": "τ=-0.42, p=0.01 → déclin significatif.",
     "source_overlay": "multi_year_dense_grid"},
    {"code": "L06_USGS_SOIL",
     "name": "USGS SoilGrids",
     "definition": "Propriétés sol (pH, argile, organique).",
     "usage": "Sol argileux + pH neutre = saline favorable.",
     "example": "Clay>30% + pH 6.8 = site saline prioritaire.",
     "source_overlay": "usgs_soil"},
    {"code": "L07_OPEN_TOPOGRAPHY",
     "name": "Open Topography (SRTM 30m)",
     "definition": "Modèle élévation + pente.",
     "usage": "Pente 5-15% = corridors déplacement naturels.",
     "example": "Élévation 250m pente 8% = passage évident.",
     "source_overlay": "open_topography"},
    {"code": "L08_GBIF_OCCURRENCES",
     "name": "GBIF Species Occurrences",
     "definition": "Observations espèces géoréférencées (7M+ entrées).",
     "usage": "Croiser présence historique avec prédiction habitat.",
     "example": "10 obs cerf dans 5km → validation doctrinale.",
     "source_overlay": "gbif"},
    {"code": "L09_OPENWEATHERMAP",
     "name": "OpenWeatherMap Conditions",
     "definition": "Température, humidité, vent, pression.",
     "usage": "Vent <15 km/h = conditions affût optimales.",
     "example": "NE 8 km/h, 2°C = journée favorable.",
     "source_overlay": "openweathermap"},
    {"code": "L10_CANOPY_COVER",
     "name": "Canopy Height / Cover",
     "definition": "Hauteur canopée (GEDI/GLAD).",
     "usage": "20-25m = couverture optimale orignal.",
     "example": "Canopée 22m → habitat orignal qualifié.",
     "source_overlay": "canopy"},
    {"code": "L11_RSF_SSF",
     "name": "Resource / Step Selection Functions",
     "definition": "Modèles sélection ressources ind/pop.",
     "usage": "Probabilité sélection > 0.6 = zone attractive.",
     "example": "RSF cerf = 0.72 sur pixel donné.",
     "source_overlay": "rsf_ssf"},
    {"code": "L12_COPERNICUS_GLAD",
     "name": "Copernicus GLAD Land Cover",
     "definition": "Classification couverture sol (forêt, prairie, etc.).",
     "usage": "Mosaïque forêt-prairie = écotone privilégié.",
     "example": "Écotone feuillus/clairière = haute qualité.",
     "source_overlay": "copernicus_glad"},
    {"code": "L13_BIO_PROFILE_135",
     "name": "BIO_PROFILE_135 Couplage",
     "definition": "Profil bioréacteur institutionnel (6 scores).",
     "usage": "Fusion pondérée BP135 ↔ BIO_REACTEUR.",
     "example": "score_fusion = 0.5×BR + 0.5×BP135.",
     "source_overlay": "bio_reacteur_overlay"},
    {"code": "L14_MERKLE_TREE_ANCHOR",
     "name": "Merkle Tree Anchor (Bitcoin OTS)",
     "definition": "Root Merkle ancrée blockchain Bitcoin.",
     "usage": "Vérification indépendante intégrité via OpenTimestamps.",
     "example": "Root SHA256 → OTS stamp → Bitcoin block.",
     "source_overlay": "merkle_tree_anchor"},
    {"code": "L15_MULTI_SIGNATURE",
     "name": "Multi-Signature (PGP + Ed25519)",
     "definition": "Doubles signatures cryptographiques manifests.",
     "usage": "Vérification authenticité via 2 chaînes indépendantes.",
     "example": "PGP armor + Ed25519 hex fingerprints.",
     "source_overlay": "multi_signature"},
    {"code": "L16_COMMANDANT_VALIDATION",
     "name": "Commandant Validation Audit (P22)",
     "definition": "Audit doctrinal des approbations formelles.",
     "usage": "Trace APPROVED/REJECTED/PENDING par scope.",
     "example": "P14 Merkle anchor → APPROVED by STEEVE-MAX.",
     "source_overlay": "commandant_validations"},
    {"code": "L17_MESSAGING_ENGINE",
     "name": "Messaging Engine Channels (P23)",
     "definition": "Canaux diffusion rapports (email + internal).",
     "usage": "social_media exclu doctrinalement.",
     "example": "Report SHA → delivery JSONL internal trace.",
     "source_overlay": "messaging_engine"},
    {"code": "L18_OTS_UPGRADE_AUTOMATION",
     "name": "OTS Upgrade Automation (P24)",
     "definition": "Automation 6h upgrade preuves Bitcoin pending→confirmed.",
     "usage": "Transition preuves OTS calendar → block attested.",
     "example": "pending_next_block → UPGRADED_BITCOIN_ATTESTED.",
     "source_overlay": "ots_upgrade_automation"},
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def generate_layer_interpretation_manual(
    include_pdf: bool = True,
    include_html: bool = True,
    persist: bool = True,
) -> Dict[str, Any]:
    """Génère le manual doctrinal 18 couches (anti-générique strict)."""
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        require_guardrails_enforced, log_forensic_event,
    )
    require_guardrails_enforced(
        "generate_layer_interpretation_manual")

    t0 = time.time()
    manual = {
        "manifest_id": "LAYER_INTERPRETATION_MANUAL_Ω",
        "ordre": "P18_LAYER_INTERPRETATION_MANUAL_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "n_layers": len(LAYERS_CATALOG),
        "layers": LAYERS_CATALOG,
        "generated_at_utc": _utc_now(),
        "anti_generique_strict": True,
        "v30_lock": "INVIOLÉ",
    }
    manual_sha256 = hashlib.sha256(
        json.dumps(manual, sort_keys=True,
                   ensure_ascii=False, default=str).encode("utf-8")
    ).hexdigest()
    manual["manual_sha256"] = manual_sha256

    files_generated: Dict[str, Any] = {}
    if persist:
        MANUAL_STORE.mkdir(parents=True, exist_ok=True)
        prefix = f"{manual_sha256[:16]}_layer_manual"
        json_path = MANUAL_STORE / f"{prefix}.json"
        json_path.write_text(
            json.dumps(manual, ensure_ascii=False, indent=2),
            encoding="utf-8")
        files_generated["json_path"] = str(json_path)
        files_generated["json_sha256"] = hashlib.sha256(
            json_path.read_bytes()).hexdigest()
        if include_html:
            html_path = MANUAL_STORE / f"{prefix}.html"
            html_path.write_text(
                _render_html(manual), encoding="utf-8")
            files_generated["html_path"] = str(html_path)
            files_generated["html_sha256"] = hashlib.sha256(
                html_path.read_bytes()).hexdigest()
        if include_pdf:
            pdf_path = MANUAL_STORE / f"{prefix}.pdf"
            _render_pdf(manual, pdf_path)
            files_generated["pdf_path"] = str(pdf_path)
            files_generated["pdf_sha256"] = hashlib.sha256(
                pdf_path.read_bytes()).hexdigest()
        MANUAL_ROOT.mkdir(parents=True, exist_ok=True)
        with open(MANUAL_HISTORY_PATH, "a",
                  encoding="utf-8") as f:
            f.write(json.dumps({
                "manual_sha256": manual_sha256,
                "n_layers": len(LAYERS_CATALOG),
                "files": files_generated,
                "generated_at_utc": _utc_now(),
            }, ensure_ascii=False, default=str) + "\n")

    log_forensic_event(
        scope="HOOK_ACTIVATIONS",
        event="LAYER_INTERPRETATION_MANUAL_GENERATED",
        details={
            "manual_sha256": manual_sha256,
            "n_layers": len(LAYERS_CATALOG),
        },
        persist=True)

    manual["files_generated"] = files_generated
    manual["elapsed_s"] = round(time.time() - t0, 3)
    return manual


def _render_html(manual: Dict[str, Any]) -> str:
    rows = "".join(
        f"<tr><td><code>{l['code']}</code></td>"
        f"<td><b>{l['name']}</b></td>"
        f"<td>{l['definition']}</td>"
        f"<td>{l['usage']}</td>"
        f"<td><i>{l['example']}</i></td>"
        f"<td><code>{l['source_overlay']}</code></td></tr>"
        for l in manual["layers"])
    return f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8"/>
<title>MANUAL · 18 LAYERS INTERPRETATION</title>
<style>
  body{{font-family:Georgia,serif;background:#0f1419;color:#e8e4d9;
        margin:0;padding:2rem;line-height:1.5}}
  h1{{color:#d4a017;border-bottom:2px solid #d4a017;font-size:1.8rem}}
  table{{border-collapse:collapse;width:100%;margin:1rem 0;font-size:.85rem}}
  th,td{{border:1px solid #3d4654;padding:.5rem;text-align:left;
         vertical-align:top}}
  th{{background:#1d2330;color:#d4a017}}
  code{{color:#7cb518;font-family:monospace;font-size:.8rem}}
  .sha{{word-break:break-all;font-family:monospace;font-size:.7rem}}
</style></head>
<body>
<h1>MANUAL D'INTERPRÉTATION · 18 COUCHES DOCTRINALES</h1>
<p><b>Ordre :</b> {manual['ordre']}<br/>
<b>Doctrine :</b> {manual['doctrine']}<br/>
<b>Generated UTC :</b> {manual['generated_at_utc']}<br/>
<b>Manual SHA-256 :</b> <span class="sha">{manual['manual_sha256']}</span><br/>
<b>V30 LOCK :</b> INVIOLÉ · <b>ANTI-GÉNÉRIQUE :</b> STRICT</p>

<table><thead><tr>
<th>Code</th><th>Nom</th><th>Définition</th>
<th>Usage</th><th>Exemple</th><th>Source overlay</th>
</tr></thead><tbody>{rows}</tbody></table>

<hr/>
<p style="font-size:.75rem;opacity:.6">
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · {manual['generated_at_utc']}
</p>
</body></html>
"""


def _render_pdf(manual: Dict[str, Any], out_path: Path) -> None:
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title", parent=styles["Heading1"],
        textColor=colors.HexColor("#d4a017"),
        fontSize=16, spaceAfter=10)
    small = ParagraphStyle(
        "small", parent=styles["Normal"],
        fontSize=7, leading=9)
    doc = SimpleDocTemplate(
        str(out_path), pagesize=landscape(A4),
        title="Layer Interpretation Manual",
        leftMargin=24, rightMargin=24,
        topMargin=24, bottomMargin=24)
    story: List[Any] = []
    story.append(Paragraph(
        "MANUAL D'INTERPRÉTATION · 18 COUCHES DOCTRINALES",
        title_style))
    story.append(Paragraph(
        f"<b>Ordre:</b> {manual['ordre']} · "
        f"<b>Generated UTC:</b> {manual['generated_at_utc']} · "
        f"<b>V30 LOCK:</b> INVIOLÉ", styles["Normal"]))
    story.append(Paragraph(
        f"<b>SHA-256:</b> <font face='Courier' size='7'>"
        f"{manual['manual_sha256']}</font>", styles["Normal"]))
    story.append(Spacer(1, 8))
    table_data = [[
        Paragraph("<b>Code</b>", small),
        Paragraph("<b>Nom</b>", small),
        Paragraph("<b>Définition</b>", small),
        Paragraph("<b>Usage</b>", small),
        Paragraph("<b>Exemple</b>", small),
        Paragraph("<b>Source</b>", small),
    ]]
    for l in manual["layers"]:
        table_data.append([
            Paragraph(l["code"], small),
            Paragraph(l["name"], small),
            Paragraph(l["definition"], small),
            Paragraph(l["usage"], small),
            Paragraph(f"<i>{l['example']}</i>", small),
            Paragraph(l["source_overlay"], small),
        ])
    t = Table(table_data,
               colWidths=[90, 110, 170, 140, 140, 100])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0),
         colors.HexColor("#1d2330")),
        ("TEXTCOLOR", (0, 0), (-1, 0),
         colors.HexColor("#d4a017")),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(t)
    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · "
        "ANTI-GÉNÉRIQUE STRICT",
        styles["Italic"]))
    doc.build(story)


def get_layer_manual_status() -> Dict[str, Any]:
    if not MANUAL_HISTORY_PATH.exists():
        return {
            "manifest_id": "LAYER_INTERPRETATION_MANUAL_STATUS_Ω",
            "current_status": "NO_MANUAL_GENERATED",
            "v30_lock": "INVIOLÉ",
            "scanned_at_utc": _utc_now(),
        }
    lines = MANUAL_HISTORY_PATH.read_text(
        encoding="utf-8").splitlines()
    last = json.loads(lines[-1]) if lines else None
    return {
        "manifest_id": "LAYER_INTERPRETATION_MANUAL_STATUS_Ω",
        "current_status": "ACTIVE" if lines else "NO_MANUAL",
        "n_manuals_generated": len(lines),
        "n_layers": len(LAYERS_CATALOG),
        "last_manual_sha256": (
            last.get("manual_sha256") if last else None),
        "last_generated_utc": (
            last.get("generated_at_utc") if last else None),
        "store_path": str(MANUAL_STORE),
        "v30_lock": "INVIOLÉ",
        "scanned_at_utc": _utc_now(),
    }


__all__ = [
    "MANUAL_ROOT",
    "MANUAL_STORE",
    "MANUAL_HISTORY_PATH",
    "LAYERS_CATALOG",
    "generate_layer_interpretation_manual",
    "get_layer_manual_status",
]
