"""
audit_longitudinal_omega.py — BLOC 3 PHASE XIV
═════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3
AUDIT LONGITUDINAL Ω — historique inter-phases, diffs SHA-256, paths

Génère :
  - snapshot SHA-256 de tous les artefacts (Phase XII + XIII)
  - diff inter-snapshots (premier snapshot = baseline)
  - historique des paths BIO_PROFILE_Ω propagés (275 paths)
  - vérification continue pipeline BIO-REACTEURS_Ω → TERRITOIRE_Ω
═════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List

BIO_PROFILE_DIR = Path("/app/frontend/public/reports/bio_profile_omega")
BIO_REACTEUR_DIR = Path("/app/frontend/public/reports/bio_reacteurs_omega")
V30_DIR = Path("/app/backend/engines/v8_institutional")
HISTORY_DIR = Path("/app/frontend/public/reports/audit_longitudinal_omega")
HISTORY_DIR.mkdir(parents=True, exist_ok=True)
HISTORY_FILE = HISTORY_DIR / "history_snapshots_omega.jsonl"

ESPECES = ["CHEVREUIL", "ORIGNAL", "OURS_NOIR", "WAPITI", "DINDON_SAUVAGE"]


def _sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _enumerate_artefacts() -> List[Dict[str, Any]]:
    """Liste structurée des artefacts surveillés."""
    out = []
    # Phase XII
    for esp in ESPECES:
        for fn in (f"BIO_PROFILE_Ω_{esp}.json", f"BIO_PROFILE_Ω_{esp}.html",
                   f"BIO_PROFILE_Ω_{esp}.csv", f"MANIFEST_BIO_PROFILE_Ω_{esp}.json"):
            p = BIO_PROFILE_DIR / fn
            if p.exists():
                out.append({"phase": "XII", "espece": esp, "filename": fn,
                            "size": p.stat().st_size, "sha256": _sha(p),
                            "path": str(p)})
    # Phase XIII
    for esp in ESPECES:
        for fn in (f"BIO_REACTEUR_Ω_{esp}.json", f"MATRICE_PROPAGATION_Ω_{esp}.csv"):
            p = BIO_REACTEUR_DIR / fn
            if p.exists():
                out.append({"phase": "XIII", "espece": esp, "filename": fn,
                            "size": p.stat().st_size, "sha256": _sha(p),
                            "path": str(p)})
    for fn in ("INDEX_BIO_REACTEURS_Ω.html",
               "SCEAU_PHASE_XIII_BIO_REACTEURS_Ω.html",
               "SCEAU_PHASE_XIII_BIO_REACTEURS_Ω.json"):
        p = BIO_REACTEUR_DIR / fn
        if p.exists():
            out.append({"phase": "XIII", "espece": "ALL", "filename": fn,
                        "size": p.stat().st_size, "sha256": _sha(p),
                        "path": str(p)})
    # V30
    for fn in ("registry_lock_omega.py", "engine_ia_corridors_omega.py"):
        p = V30_DIR / fn
        if p.exists():
            out.append({"phase": "V30_LOCK", "espece": None, "filename": fn,
                        "size": p.stat().st_size, "sha256": _sha(p),
                        "path": str(p)})
    return out


def take_snapshot() -> Dict[str, Any]:
    """Prend un snapshot horodaté + écrit dans history JSONL (append-only)."""
    arts = _enumerate_artefacts()
    snap = {
        "snapshot_at_utc": datetime.now(timezone.utc).isoformat(),
        "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
        "phase": "PHASE_XIV_AUDIT_LONGITUDINAL_Ω",
        "issued_by": "COMMANDANT STEEVE-MAX",
        "artefact_count": len(arts),
        "by_phase": {
            "XII": sum(1 for a in arts if a["phase"] == "XII"),
            "XIII": sum(1 for a in arts if a["phase"] == "XIII"),
            "V30_LOCK": sum(1 for a in arts if a["phase"] == "V30_LOCK"),
        },
        "artefacts": arts,
    }
    # Append au history
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "snapshot_at_utc": snap["snapshot_at_utc"],
            "artefact_count": snap["artefact_count"],
            "by_phase": snap["by_phase"],
            "shas_keyed": {a["filename"]: a["sha256"] for a in arts},
        }, ensure_ascii=False) + "\n")
    return snap


def list_history() -> List[Dict[str, Any]]:
    if not HISTORY_FILE.exists():
        return []
    out = []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def diff_against_baseline() -> Dict[str, Any]:
    """Compare le snapshot live au PREMIER snapshot enregistré."""
    history = list_history()
    if not history:
        return {"ok": False, "error": "Aucun historique disponible"}
    baseline = history[0]
    live = take_snapshot()
    base_shas = baseline["shas_keyed"]
    live_shas = {a["filename"]: a["sha256"] for a in live["artefacts"]}
    added = sorted(set(live_shas) - set(base_shas))
    removed = sorted(set(base_shas) - set(live_shas))
    modified = sorted([fn for fn in (set(base_shas) & set(live_shas))
                       if base_shas[fn] != live_shas[fn]])
    return {
        "ok": True,
        "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
        "phase": "PHASE_XIV_AUDIT_LONGITUDINAL_Ω",
        "baseline_at_utc": baseline["snapshot_at_utc"],
        "live_at_utc": live["snapshot_at_utc"],
        "history_count": len(history) + 1,
        "added": added,
        "removed": removed,
        "modified": modified,
        "stable": (not added and not removed and not modified),
        "artefact_count_baseline": baseline["artefact_count"],
        "artefact_count_live": live["artefact_count"],
    }


def list_paths_propagation() -> Dict[str, Any]:
    """Inventaire complet des paths BIO_PROFILE_Ω propagés (275 attendus)."""
    out = []
    total_paths = 0
    for esp in ESPECES:
        p = BIO_REACTEUR_DIR / f"BIO_REACTEUR_Ω_{esp}.json"
        if not p.exists():
            continue
        with open(p, "r", encoding="utf-8") as f:
            r = json.load(f)
        for eng_name, eng_def in r.get("bio_reacteur_outputs", {}).items():
            for path in eng_def.get("bio_profile_paths", []):
                out.append({
                    "espece": esp, "engine": eng_name, "path": path,
                    "param_label": eng_def.get("param_label"),
                })
                total_paths += 1
    return {
        "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
        "phase": "PHASE_XIV_AUDIT_LONGITUDINAL_Ω",
        "total_paths": total_paths,
        "expected_paths": 275,
        "match": total_paths == 275,
        "paths": out,
    }


def pipeline_continuity_check() -> Dict[str, Any]:
    """Vérification continue du pipeline BIO-REACTEURS_Ω → TERRITOIRE_Ω.

    Pour chaque espèce :
      - BIO_PROFILE_Ω.json existe et lisible
      - BIO_REACTEUR_Ω.json existe, anti_generique_pass=True
      - source_biologique.sha256 == SHA-256 réel du BIO_PROFILE
      - 13 ENGINE outputs présents
    """
    rows = []
    all_ok = True
    for esp in ESPECES:
        bp = BIO_PROFILE_DIR / f"BIO_PROFILE_Ω_{esp}.json"
        br = BIO_REACTEUR_DIR / f"BIO_REACTEUR_Ω_{esp}.json"
        if not bp.exists() or not br.exists():
            rows.append({"espece": esp, "ok": False, "error": "fichier manquant"})
            all_ok = False
            continue
        with open(br, "r", encoding="utf-8") as f:
            r = json.load(f)
        bp_actual_sha = _sha(bp)
        bp_decl_sha = r.get("source_biologique", {}).get("sha256")
        ok = (
            r.get("anti_generique_pass") is True
            and bp_decl_sha == bp_actual_sha
            and len(r.get("bio_reacteur_outputs", {})) == 13
            and r.get("contraintes_respectees", {}).get("fallback_active") is False
            and r.get("contraintes_respectees", {}).get("interpolation_active") is False
        )
        rows.append({
            "espece": esp,
            "ok": ok,
            "anti_generique_pass": r.get("anti_generique_pass"),
            "bp_actual_sha256": bp_actual_sha,
            "bp_declared_sha256": bp_decl_sha,
            "engines_count": len(r.get("bio_reacteur_outputs", {})),
        })
        if not ok:
            all_ok = False
    return {
        "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
        "phase": "PHASE_XIV_PIPELINE_CONTINUITY_CHECK",
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "all_ok": all_ok,
        "espece_count": len(rows),
        "espece_reports": rows,
    }


def full_longitudinal_report() -> Dict[str, Any]:
    """Rapport complet pour endpoint API."""
    return {
        "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
        "phase": "PHASE_XIV_AUDIT_LONGITUDINAL_Ω",
        "issued_by": "COMMANDANT STEEVE-MAX",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "snapshot": take_snapshot(),
        "diff_baseline": diff_against_baseline(),
        "pipeline_continuity": pipeline_continuity_check(),
        "paths_propagation_summary": {
            "total_paths": list_paths_propagation()["total_paths"],
            "expected_paths": 275,
            "match": list_paths_propagation()["match"],
        },
        "history_snapshots_count": len(list_history()),
    }


__all__ = [
    "take_snapshot", "list_history", "diff_against_baseline",
    "list_paths_propagation", "pipeline_continuity_check",
    "full_longitudinal_report",
    "HISTORY_FILE",
]
