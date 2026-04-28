"""
fusion_territoire_omega_router.py — PHASE-E DOCTRINE PERMANENTE 50%
═══════════════════════════════════════════════════════════════════════════
Commandant : STEEVE-MAX
Protocole  : BCE-4X ULTIME ABSOLU — TOP-ABSOLU

Routes :
  • GET  /api/v30/territoire/ultime-score          (lecture seule + bio_derogation)
  • GET  /api/v30/territoire/ultime-score/spec     (spec L1 JSON)
  • POST /api/v30/territoire/fusion-execute        (FUSION RÉELLE orchestrée)

DOCTRINE PERMANENTE (Article 1) :
  • Fusion autorisée si score_ultime ≥ 0.50 ET v30_alignment_score ≥ 50.

DOCTRINE TRANSITOIRE (Article 2) :
  • L'endpoint POST /fusion-execute désactive temporairement
    BIO_PRESENCE_MASK_HALT (uniquement durant l'appel) afin de fusionner
    dindon et wapiti. Aucune persistance.

DOCTRINE DE REFERMETURE (Article 3) :
  • À la fin de POST /fusion-execute, l'agrégateur est ré-appelé sans
    dérogation (snapshot post-fusion). Le masque BIO redevient actif.
  • Aucun état dérogatoire ne survit à l'appel.

DOCTRINE DE PUBLICATION (Article 5) :
  • POST /fusion-execute génère obligatoirement le rapport HTML
    `RAPPORT_PHASE-E_FUSION_TERRITOIRE_Ω_RÉELLE.html`. En cas d'échec
    d'écriture, la réponse signale `fusion_canceled=True` (annulation auto).
"""
from __future__ import annotations

import hashlib
import os
from datetime import datetime, timezone
from typing import Any, Dict, List

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter(
    prefix="/api/v30/territoire",
    tags=["PHASE-E_FUSION_TERRITOIRE_Ω"],
)

OFFICIAL_LAT = 48.206657
OFFICIAL_LNG = -68.382422

_ALLOWED_SPECIES = ("orignal", "cerf", "ours", "dindon", "wapiti")

REPORT_DIR = "/app/frontend/public/reports/audit_territoire_omega_ultime"
REPORT_REELLE_FILENAME = "RAPPORT_PHASE-E_FUSION_TERRITOIRE_Ω_RÉELLE.html"


@router.get("/ultime-score")
async def territoire_ultime_score(
    lat: float = Query(OFFICIAL_LAT),
    lon: float = Query(OFFICIAL_LNG),
    species: str = Query("orignal"),
    month: int = Query(10, ge=1, le=12),
    hour: int = Query(14, ge=0, le=23),
    bio_derogation: bool = Query(False, description="Article 2 — dérogation BIO temporaire"),
):
    """Score ULTIME PHASE-E (DOCTRINE PERMANENTE 50%)."""
    sp = (species or "orignal").lower()
    if sp not in _ALLOWED_SPECIES:
        return JSONResponse(
            status_code=400,
            content={"error": "species invalide", "allowed": list(_ALLOWED_SPECIES)},
        )
    try:
        from engines.v8_institutional.fusion_territoire_omega import compute_ultime_score
        payload = await compute_ultime_score(
            lat=lat, lon=lon, species=sp, month=month, hour=hour,
            bio_derogation=bool(bio_derogation),
        )
        return JSONResponse(content=payload)
    except RuntimeError as e:
        return JSONResponse(
            status_code=409,
            content={
                "phase": "PHASE-E_FUSION_TERRITOIRE_Ω",
                "error": str(e), "action": "FUSION_PROSCRITE", "v30_locked": False,
            },
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"phase": "PHASE-E_FUSION_TERRITOIRE_Ω",
                     "error": f"UNEXPECTED_FAILURE: {type(e).__name__}: {e}"},
        )


@router.get("/ultime-score/spec")
async def territoire_ultime_score_spec():
    """Retourne la spécification formelle L1."""
    import json
    spec_path = f"{REPORT_DIR}/FUSION_TERRITOIRE_OMEGA.json"
    if not os.path.exists(spec_path):
        return JSONResponse(status_code=404, content={"error": "spec non publiée"})
    with open(spec_path, "r", encoding="utf-8") as f:
        return JSONResponse(content=json.load(f))


@router.post("/fusion-execute")
async def territoire_fusion_execute(
    lat: float = Query(OFFICIAL_LAT),
    lon: float = Query(OFFICIAL_LNG),
    month: int = Query(10, ge=1, le=12),
    hour: int = Query(14, ge=0, le=23),
):
    """FUSION RÉELLE PHASE-E orchestrée (DOCTRINE PERMANENTE 50% + dérogation BIO).

    Étapes :
      1. Vérifie l'invariance V30.
      2. Calcule les scores des 5 espèces officielles AVEC dérogation BIO
         (Article 2 — temporaire).
      3. Détermine la fusionnabilité par espèce (seuils 50% permanents).
      4. Génère le rapport HTML obligatoire (Article 5).
      5. Ré-exécute un snapshot post-fusion SANS dérogation (Article 3 —
         refermeture automatique du masque BIO).
      6. Retourne la décision institutionnelle complète.
    """
    from engines.v8_institutional.fusion_territoire_omega import (
        compute_ultime_score, _compute_registry_echo,
        THRESHOLD_FUSION_SCORE, THRESHOLD_FUSION_V30, DOCTRINE_VERSION,
    )

    try:
        registry = _compute_registry_echo()
    except Exception as e:
        return JSONResponse(status_code=409, content={
            "phase": "PHASE-E_FUSION_RÉELLE",
            "fusion_canceled": True,
            "reason": f"V30_INTEGRITY_CHECK_FAILURE: {type(e).__name__}: {e}",
        })
    if not registry["invariant"]:
        return JSONResponse(status_code=409, content={
            "phase": "PHASE-E_FUSION_RÉELLE",
            "fusion_canceled": True,
            "reason": "V30 MUTATION DÉTECTÉE — FUSION PROSCRITE",
            "registry_lock_v30": registry,
        })

    started_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    # 2. Scores avec dérogation BIO (Article 2)
    fusion_with_derogation: List[Dict[str, Any]] = []
    fusionnable_count = 0
    for sp in _ALLOWED_SPECIES:
        try:
            payload = await compute_ultime_score(
                lat=lat, lon=lon, species=sp, month=month, hour=hour,
                bio_derogation=True,
            )
        except Exception as e:
            payload = {"species": sp, "error": f"{type(e).__name__}: {e}"}
        fusion_with_derogation.append(payload)
        if payload.get("fusionnable"):
            fusionnable_count += 1

    # 5. Snapshot post-fusion SANS dérogation (Article 3)
    post_fusion_snapshot: List[Dict[str, Any]] = []
    for sp in _ALLOWED_SPECIES:
        try:
            payload = await compute_ultime_score(
                lat=lat, lon=lon, species=sp, month=month, hour=hour,
                bio_derogation=False,  # BIO mask actif (refermé)
            )
        except Exception as e:
            payload = {"species": sp, "error": f"{type(e).__name__}: {e}"}
        post_fusion_snapshot.append(payload)

    finished_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    # 4. Génération rapport HTML obligatoire (Article 5)
    report_path = f"{REPORT_DIR}/{REPORT_REELLE_FILENAME}"
    report_url = f"/reports/audit_territoire_omega_ultime/{REPORT_REELLE_FILENAME}"
    report_status = "PENDING"
    report_sha256 = None
    try:
        html = _build_real_fusion_report(
            registry=registry,
            fusion_with_derogation=fusion_with_derogation,
            post_fusion_snapshot=post_fusion_snapshot,
            started_at=started_at, finished_at=finished_at,
            doctrine_version=DOCTRINE_VERSION,
            threshold_score=THRESHOLD_FUSION_SCORE,
            threshold_v30=THRESHOLD_FUSION_V30,
            fusionnable_count=fusionnable_count,
        )
        os.makedirs(REPORT_DIR, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html)
        # SHA-256 du rapport
        with open(report_path, "rb") as f:
            report_sha256 = hashlib.sha256(f.read()).hexdigest()
        report_status = "PUBLISHED"
        fusion_canceled = False
    except Exception as e:
        report_status = f"FAILED: {type(e).__name__}: {e}"
        # Article 5 : rapport absent → fusion annulée automatiquement
        fusion_canceled = True

    return JSONResponse(content={
        "phase": "PHASE-E_FUSION_RÉELLE",
        "doctrine_version": DOCTRINE_VERSION,
        "doctrine_articles": {
            "article_1_seuils_permanents": {
                "score_min_fusion": THRESHOLD_FUSION_SCORE,
                "v30_min_fusion": THRESHOLD_FUSION_V30,
            },
            "article_2_derogation_bio_temporaire": True,
            "article_3_refermeture_automatique": True,
            "article_4_v30_locked": True,
            "article_5_rapport_obligatoire": True,
        },
        "fusion_canceled": bool(fusion_canceled),
        "fusion_canceled_reason": (
            "RAPPORT_NON_GÉNÉRÉ — Article 5 violé · fusion auto-annulée"
            if fusion_canceled else None
        ),
        "started_at": started_at,
        "finished_at": finished_at,
        "fusionnable_count": fusionnable_count,
        "fusionnable_species": [
            p["species"] for p in fusion_with_derogation if p.get("fusionnable")
        ],
        "fusion_with_derogation": fusion_with_derogation,
        "post_fusion_snapshot": post_fusion_snapshot,
        "report": {
            "path": report_path,
            "url": report_url,
            "filename": REPORT_REELLE_FILENAME,
            "status": report_status,
            "sha256": report_sha256,
        },
        "registry_lock_v30": {
            "registry_lock_omega_sha256": registry["registry_lock_omega_sha256"],
            "engine_ia_corridors_omega_sha256": registry["engine_ia_corridors_omega_sha256"],
            "invariant": registry["invariant"],
        },
        "sha256_registry_echo": registry["sha256_registry_echo"],
        "v30_locked": True,
        "xix_recomputed": False,
        "vitaux_recomputed": False,
        "doctrine": "BCE-4X_ULTIME_ABSOLU",
    })


# ─────────────────────────────────────────────────────────────────────────
# Génération du rapport HTML obligatoire (Article 5)
# ─────────────────────────────────────────────────────────────────────────
def _band_chip_class(b: str) -> str:
    return {
        "TRÈS_FAVORABLE": "tfav", "FAVORABLE": "fav",
        "NEUTRE": "neu", "DÉFAVORABLE": "dfav", "PROSCRIT": "prs",
    }.get(b or "NEUTRE", "neu")


def _row_for(species_payload: Dict[str, Any]) -> str:
    sp = species_payload.get("species", "—")
    if "error" in species_payload:
        return f"<tr><td>{sp}</td><td colspan='6'>ERREUR · {species_payload['error']}</td></tr>"
    pct = species_payload.get("score_ultime_pct", 0.0)
    band = species_payload.get("bande", "—")
    chip = _band_chip_class(band)
    fusion = species_payload.get("fusionnable", False)
    fusion_badge = ("<span class='badge b-ok'>OUI</span>" if fusion
                    else "<span class='badge b-err'>NON</span>")
    inhibitors = " · ".join(species_payload.get("inhibitors_applied", []) or []) or "—"
    bio_nat = "OUI" if species_payload.get("bio_presence_mask_halt_natural") else "NON"
    bio_eff = "OUI" if species_payload.get("bio_presence_mask_halt") else "NON"
    der = "OUI" if species_payload.get("bio_derogation_active") else "NON"
    return (
        f"<tr><td><b>{sp}</b></td>"
        f"<td>{pct:.2f}%</td>"
        f"<td><span class='band-chip {chip}'>{band}</span></td>"
        f"<td>{fusion_badge}</td>"
        f"<td>{inhibitors}</td>"
        f"<td>BIO_HALT nat={bio_nat} · eff={bio_eff} · dérog={der}</td></tr>"
    )


def _build_real_fusion_report(*, registry: Dict[str, Any],
                              fusion_with_derogation: List[Dict[str, Any]],
                              post_fusion_snapshot: List[Dict[str, Any]],
                              started_at: str, finished_at: str,
                              doctrine_version: str,
                              threshold_score: float, threshold_v30: float,
                              fusionnable_count: int) -> str:
    fusion_rows = "\n".join(_row_for(p) for p in fusion_with_derogation)
    post_rows = "\n".join(_row_for(p) for p in post_fusion_snapshot)
    bio_post = [p for p in post_fusion_snapshot
                if p.get("bio_presence_mask_halt") is True]
    masque_referme = bool(bio_post)  # masque actif sur dindon/wapiti après fusion

    return f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>RAPPORT PHASE-E · FUSION TERRITOIRE Ω · RÉELLE</title>
<style>
:root{{--green:#00A676;--green-inner:#4CC99A;--green-outer:#B2F2D9;
  --amber:#F59E0B;--red:#DC2626;--gray:#6B7280;--bg:#F7FAFC;--ink:#0F172A;}}
*{{box-sizing:border-box;}}
body{{margin:0;font-family:Inter,system-ui,Segoe UI,Roboto,sans-serif;
  background:var(--bg);color:var(--ink);line-height:1.5;}}
.container{{max-width:1180px;margin:0 auto;padding:32px 24px 72px;}}
header.banner{{background:linear-gradient(135deg,#0B3D2E,#12563F 50%,#0B3D2E);
  color:#fff;padding:28px 24px;border-radius:12px;margin-bottom:28px;
  box-shadow:0 10px 30px rgba(0,166,118,0.18);border:2px solid var(--green);}}
header.banner h1{{font-size:28px;margin:6px 0;}}
.tag{{background:var(--green);color:#fff;padding:3px 10px;border-radius:4px;
  font-weight:700;font-size:11px;letter-spacing:1px;display:inline-block;}}
.meta{{color:var(--green-outer);font-size:13px;margin-top:10px;}}
h2{{color:var(--green);border-bottom:2px solid var(--green);padding-bottom:6px;
  margin-top:48px;font-size:20px;letter-spacing:0.3px;}}
table{{width:100%;border-collapse:collapse;margin:12px 0;font-size:13px;}}
th,td{{padding:9px 11px;text-align:left;border-bottom:1px solid #E5E7EB;}}
th{{background:var(--green);color:#fff;letter-spacing:0.3px;font-weight:700;}}
tr:nth-child(even) td{{background:#F9FDFB;}}
.badge{{padding:2px 9px;border-radius:10px;font-size:11px;font-weight:700;}}
.b-ok{{background:var(--green);color:#fff;}}.b-warn{{background:var(--amber);color:#1F2937;}}
.b-err{{background:var(--red);color:#fff;}}.b-gray{{background:#9CA3AF;color:#fff;}}
.band-chip{{padding:3px 10px;border-radius:12px;font-weight:700;font-size:11px;}}
.tfav{{background:#00A676;color:#fff;}}.fav{{background:#33B787;color:#fff;}}
.neu{{background:#C0C0C0;color:#1F2937;}}.dfav{{background:#F59E0B;color:#1F2937;}}
.prs{{background:#DC2626;color:#fff;}}
.muted{{color:var(--gray);font-size:12px;}}
code{{font-family:JetBrains Mono,Menlo,Consolas,monospace;background:#E5F6EF;
  color:#0B3D2E;padding:2px 6px;border-radius:4px;font-size:12px;}}
.kpi{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px;margin:12px 0;}}
.kpi .card{{text-align:center;border:1px solid #D1D5DB;padding:14px;border-radius:8px;background:#fff;}}
.kpi .val{{font-size:24px;font-weight:800;color:var(--green);}}
.kpi .lbl{{font-size:11px;color:var(--gray);letter-spacing:0.5px;}}
.callout{{padding:14px;border-left:6px solid var(--green);background:#F4FEF9;border-radius:6px;}}
.sha{{font-family:monospace;font-size:10px;color:var(--gray);word-break:break-all;}}
footer{{margin-top:40px;padding:16px;border-top:1px dashed var(--gray);
  text-align:center;color:var(--gray);font-size:12px;}}
</style></head><body><div class="container">
<header class="banner">
<span class="tag">BCE-4X ULTIME ABSOLU — TOP-ABSOLU · FUSION RÉELLE</span>
<h1>RAPPORT PHASE-E · FUSION TERRITOIRE Ω · RÉELLE</h1>
<div class="meta">
  Commandant : <b>STEEVE-MAX</b> · Doctrine : <b>{doctrine_version}</b><br>
  Démarré : <b>{started_at}</b> · Terminé : <b>{finished_at}</b><br>
  Waypoint officiel : <b>48.206657 / -68.382422</b>
</div>
<div class="meta" style="margin-top:4px;">
  🛡️ V30 LOCKED · XIX non recomputé · VITAUX non recomputé · Backend READ-ONLY ·
  Aucun <code>testing_agent_v3_fork</code>
</div>
</header>

<h2>1. Doctrine appliquée (5 articles)</h2>
<table>
<tr><th>Article</th><th>Énoncé</th><th>État</th></tr>
<tr><td><b>1</b></td><td>Seuils permanents : score ≥ {threshold_score:.2f} · v30 ≥ {threshold_v30:.0f}</td>
    <td><span class="badge b-ok">APPLIQUÉ</span></td></tr>
<tr><td><b>2</b></td><td>Dérogation BIO temporaire (dindon, wapiti fusionnables)</td>
    <td><span class="badge b-ok">APPLIQUÉE PENDANT FUSION</span></td></tr>
<tr><td><b>3</b></td><td>Refermeture automatique masque BIO post-fusion</td>
    <td><span class="badge {('b-ok' if masque_referme else 'b-warn')}">{('REFERMÉ ✓' if masque_referme else 'À VÉRIFIER')}</span></td></tr>
<tr><td><b>4</b></td><td>V30 LOCKED · XIX/VITAUX non recomputés · backend READ-ONLY</td>
    <td><span class="badge {('b-ok' if registry['invariant'] else 'b-err')}">
        {'INVIOLÉ' if registry['invariant'] else 'MUTATION DÉTECTÉE'}</span></td></tr>
<tr><td><b>5</b></td><td>Rapport HTML obligatoire (ce document)</td>
    <td><span class="badge b-ok">PUBLIÉ</span></td></tr>
</table>

<h2>2. KPIs de la fusion réelle</h2>
<div class="kpi">
  <div class="card"><div class="val">{fusionnable_count} / 5</div><div class="lbl">ESPÈCES FUSIONNABLES</div></div>
  <div class="card"><div class="val">5 / 5</div><div class="lbl">ESPÈCES ANALYSÉES</div></div>
  <div class="card"><div class="val">✓</div><div class="lbl">V30 INVIOLÉ</div></div>
  <div class="card"><div class="val">{('✓' if masque_referme else '⚠')}</div><div class="lbl">MASQUE BIO REFERMÉ</div></div>
  <div class="card"><div class="val">50%</div><div class="lbl">SEUIL PERMANENT</div></div>
  <div class="card"><div class="val">v30≥50</div><div class="lbl">SEUIL V30 PERMANENT</div></div>
</div>

<h2>3. Fusion RÉELLE — résultats avec dérogation BIO (Article 2)</h2>
<p class="muted">Calcul des 5 espèces officielles avec <code>bio_derogation=True</code> activé pendant l'appel.</p>
<table>
<thead><tr><th>Espèce</th><th>Score ULTIME</th><th>Bande</th>
  <th>Fusionnable</th><th>Inhibiteurs</th><th>BIO mask</th></tr></thead>
<tbody>
{fusion_rows}
</tbody></table>

<h2>4. Snapshot POST-FUSION — refermeture du masque BIO (Article 3)</h2>
<p class="muted">Calcul des 5 espèces SANS dérogation. Le masque BIO doit être réactif sur dindon/wapiti.</p>
<table>
<thead><tr><th>Espèce</th><th>Score ULTIME</th><th>Bande</th>
  <th>Fusionnable</th><th>Inhibiteurs</th><th>BIO mask</th></tr></thead>
<tbody>
{post_rows}
</tbody></table>

<h2>5. Invariance cryptographique V30 (Article 4)</h2>
<table>
<tr><th>Module V30 LOCKED</th><th>SHA-256</th><th>État</th></tr>
<tr><td><code>registry_lock_omega.py</code></td>
    <td class="sha">{registry['registry_lock_omega_sha256']}</td>
    <td><span class="badge b-ok">INVIOLÉ</span></td></tr>
<tr><td><code>engine_ia_corridors_omega.py</code></td>
    <td class="sha">{registry['engine_ia_corridors_omega_sha256']}</td>
    <td><span class="badge b-ok">INVIOLÉ</span></td></tr>
<tr><td><b>echo institutionnel</b></td>
    <td class="sha">{registry['sha256_registry_echo']}</td>
    <td><span class="badge b-ok">CONFORME</span></td></tr>
</table>

<h2>6. Conclusion institutionnelle</h2>
<div class="callout">
La FUSION RÉELLE PHASE-E a été exécutée avec la doctrine permanente 50% et la
dérogation biologique temporaire conforme à l'ordre du Commandant STEEVE-MAX.
Au total <b>{fusionnable_count} / 5 espèces</b> ont été déclarées fusionnables
durant la fusion réelle. La refermeture automatique du masque BIO est
<b>{'effective' if masque_referme else 'à contrôler'}</b> dans le snapshot
post-fusion. Aucune mutation cryptographique V30 n'est constatée. Aucune
persistance dérogatoire n'est introduite. Le présent rapport scelle
institutionnellement l'opération conformément à l'Article 5.
</div>

<footer>PHASE-E_FUSION_TERRITOIRE_Ω_RÉELLE · BCE-4X ULTIME ABSOLU — TOP-ABSOLU ·
Commandant STEEVE-MAX · Waypoint 48.206657 / -68.382422 ·
Doctrine <code>{doctrine_version}</code></footer>
</div></body></html>
"""
