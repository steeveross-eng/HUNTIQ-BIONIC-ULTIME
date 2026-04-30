"""
gis_audit_log_omega.py — Module audit-log persistant Phase XXIII (ORDRE N°44)
═════════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ORDRE N°44

Journalisation forensique append-only des uploads GIS protégés.
Format de stockage : JSONL (une ligne JSON par évènement) à
`/app/backend/data/gis_operational/audit_log.jsonl`.

Champs capturés :
  · ts_utc           — Horodatage ISO-8601 UTC
  · event            — UPLOAD_LOADED / UPLOAD_QUARANTINED / UPLOAD_ERROR
  · slot_id          — Identifiant canonique du slot
  · filename         — Nom du fichier déposé
  · sha256           — Empreinte SHA-256
  · size_bytes       — Taille en octets
  · http_code        — Code HTTP retourné
  · client_ip        — IP source (ou "unknown")
  · user_agent       — Header User-Agent
  · validators_summary — Résumé compact des validators (passed booléen par check)

Rétention :
  · Configurable via env `GIS_AUDIT_RETENTION_DAYS` (défaut 90)
  · Purge automatique à chaque append (fenêtre glissante)

Anti-générique strict — aucune entrée synthétique. V30 INVIOLABLE.
═════════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

AUDIT_LOG_PATH = Path("/app/backend/data/gis_operational/audit_log.jsonl")
AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


def _retention_days() -> int:
    raw = os.environ.get("GIS_AUDIT_RETENTION_DAYS", "90")
    try:
        v = int(raw)
        return v if v > 0 else 90
    except ValueError:
        return 90


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _parse_ts(s: str) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


def _summarize_validators(validators: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    if not validators:
        return []
    return [
        {"name": v.get("name"), "passed": bool(v.get("passed"))}
        for v in validators
    ]


def append_event(
    *,
    event: str,
    slot_id: str,
    filename: str,
    sha256: Optional[str],
    size_bytes: int,
    http_code: int,
    client_ip: Optional[str],
    user_agent: Optional[str],
    validators: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Append-only au JSONL + purge auto selon rétention."""
    entry = {
        "ts_utc": _utc_now_iso(),
        "event": event,
        "slot_id": slot_id,
        "filename": filename,
        "sha256": sha256,
        "size_bytes": int(size_bytes),
        "http_code": int(http_code),
        "client_ip": client_ip or "unknown",
        "user_agent": (user_agent or "")[:300],
        "validators_summary": _summarize_validators(validators),
    }

    # Purge before append (sliding window)
    purged = _purge_expired_entries()

    # Append
    with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return {"appended": entry, "purged_count": purged}


def _purge_expired_entries() -> int:
    """Retire les entrées plus anciennes que la rétention.
    Retourne le nombre d'entrées purgées.
    """
    if not AUDIT_LOG_PATH.exists():
        return 0
    cutoff = datetime.now(timezone.utc) - timedelta(days=_retention_days())
    kept: List[str] = []
    purged = 0
    with open(AUDIT_LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                purged += 1
                continue
            ts = _parse_ts(obj.get("ts_utc", ""))
            if ts is None or ts < cutoff:
                purged += 1
                continue
            kept.append(line)
    if purged > 0:
        with open(AUDIT_LOG_PATH, "w", encoding="utf-8") as f:
            for ln in kept:
                f.write(ln + "\n")
    return purged


def read_entries(
    *, slot_id: Optional[str] = None, event: Optional[str] = None,
    limit: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Lecture filtrée des entrées (les plus récentes en tête)."""
    if not AUDIT_LOG_PATH.exists():
        return []
    rows: List[Dict[str, Any]] = []
    with open(AUDIT_LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if slot_id and obj.get("slot_id") != slot_id:
                continue
            if event and obj.get("event") != event:
                continue
            rows.append(obj)
    rows.sort(key=lambda x: x.get("ts_utc", ""), reverse=True)
    if limit and limit > 0:
        rows = rows[:limit]
    return rows


def stats() -> Dict[str, Any]:
    """Statistiques agrégées (sans charger l'intégralité)."""
    counts = {"UPLOAD_LOADED": 0, "UPLOAD_QUARANTINED": 0, "UPLOAD_ERROR": 0}
    by_slot: Dict[str, int] = {}
    total = 0
    first_ts: Optional[str] = None
    last_ts: Optional[str] = None
    if AUDIT_LOG_PATH.exists():
        with open(AUDIT_LOG_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                total += 1
                ev = obj.get("event", "")
                counts[ev] = counts.get(ev, 0) + 1
                sid = obj.get("slot_id", "?")
                by_slot[sid] = by_slot.get(sid, 0) + 1
                ts = obj.get("ts_utc")
                if ts:
                    if first_ts is None or ts < first_ts:
                        first_ts = ts
                    if last_ts is None or ts > last_ts:
                        last_ts = ts
    return {
        "total_events": total,
        "events_by_type": counts,
        "events_by_slot": by_slot,
        "first_event_ts": first_ts,
        "last_event_ts": last_ts,
        "retention_days": _retention_days(),
        "log_path": str(AUDIT_LOG_PATH),
        "log_exists": AUDIT_LOG_PATH.exists(),
        "log_size_bytes": AUDIT_LOG_PATH.stat().st_size if AUDIT_LOG_PATH.exists() else 0,
    }


__all__ = [
    "AUDIT_LOG_PATH",
    "append_event",
    "read_entries",
    "stats",
]
