"""
SELF-AUDIT-ALERTS-Ω — Canal WebSocket institutionnel (Phase X-D)
==================================================================
Broadcast temps réel des alertes critiques :
  - SELF-AUDIT non-conforme
  - perf_guard severity > warning
  - registry_lock altéré

Endpoint WebSocket :
  /ws/self-audit-alert

Endpoint REST (test/declenchement manuel + last alerts) :
  POST /api/v20/territoire/self-audit-alert/trigger (debug/admin)
  GET  /api/v20/territoire/self-audit-alert/last
"""
import json
import asyncio
from collections import deque
from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from engines.v8_institutional.engine_science_omega import register_engine, mark_call

register_engine(
    "SELF-AUDIT-ALERTS-Ω",
    "V1-PHASE-X-D-2026-04",
    "Canal WebSocket alertes SELF-AUDIT / perf / registry",
    "GOUVERNANCE",
    [],
)

router = APIRouter(tags=["V20 Alerts"])
rest_router = APIRouter(prefix="/api/v20/territoire", tags=["V20 Alerts REST"])

_CLIENTS: List[WebSocket] = []
_LAST_ALERTS: deque = deque(maxlen=50)
_LOCK = asyncio.Lock()


class AlertPayload(BaseModel):
    kind: str  # self-audit | perf-guard | registry-lock
    severity: str = "critical"  # info|warning|critical
    message: str
    details: dict = {}


async def broadcast_alert(alert: dict):
    """Envoie l'alerte à tous les clients connectés."""
    mark_call("SELF-AUDIT-ALERTS-Ω")
    payload = {**alert, "emitted_at": datetime.now(timezone.utc).isoformat()}
    _LAST_ALERTS.appendleft(payload)
    dead = []
    async with _LOCK:
        clients = list(_CLIENTS)
    for ws in clients:
        try:
            await ws.send_text(json.dumps(payload))
        except Exception:
            dead.append(ws)
    if dead:
        async with _LOCK:
            for ws in dead:
                if ws in _CLIENTS:
                    _CLIENTS.remove(ws)
    return payload


@router.websocket("/ws/self-audit-alert")
async def ws_self_audit_alert(websocket: WebSocket):
    await websocket.accept()
    async with _LOCK:
        _CLIENTS.append(websocket)
    try:
        # Greet + historique
        await websocket.send_text(json.dumps({
            "kind": "hello",
            "severity": "info",
            "message": "SELF-AUDIT-ALERTS-Ω channel opened",
            "last_alerts": list(_LAST_ALERTS)[:5],
            "emitted_at": datetime.now(timezone.utc).isoformat(),
        }))
        while True:
            # Keepalive: on accepte mais ne traite pas les messages client
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        async with _LOCK:
            if websocket in _CLIENTS:
                _CLIENTS.remove(websocket)


@rest_router.post("/self-audit-alert/trigger")
async def trigger_alert(payload: AlertPayload):
    """Déclenchement manuel (admin/debug) — broadcast vers tous les clients WS."""
    return await broadcast_alert(payload.model_dump())


@rest_router.get("/self-audit-alert/last")
async def last_alerts(limit: int = 10):
    """Retourne les N dernières alertes broadcastées."""
    return {"count": len(_LAST_ALERTS), "alerts": list(_LAST_ALERTS)[:limit]}


def check_and_emit_from_audit(audit_result: dict, previous_hash: str | None = None, current_hash: str | None = None):
    """Appelable depuis self_audit_omega après chaque audit. Lance les alertes si critères remplis."""
    emitted = []
    if audit_result.get("conforme") is False:
        emitted.append({
            "kind": "self-audit",
            "severity": "critical",
            "message": "SELF-AUDIT NON-CONFORME",
            "details": {
                "ok": sum(1 for s in audit_result.get("suites", []) if s.get("statut") == "OK"),
                "total": len(audit_result.get("suites", [])),
            },
        })
    perf = audit_result.get("perf_guard") or {}
    if perf.get("severity_max") in ("warning", "fail"):
        emitted.append({
            "kind": "perf-guard",
            "severity": "warning" if perf["severity_max"] == "warning" else "critical",
            "message": f"PERF-GUARD severity {perf['severity_max']}",
            "details": {"issues": perf.get("issues", [])[:5]},
        })
    if previous_hash and current_hash and previous_hash != current_hash:
        emitted.append({
            "kind": "registry-lock",
            "severity": "critical",
            "message": "REGISTRY-LOCK hash modifié",
            "details": {"previous": previous_hash[:16], "current": current_hash[:16]},
        })
    # Broadcast (fire-and-forget)
    for a in emitted:
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(broadcast_alert(a))
        except Exception:
            _LAST_ALERTS.appendleft({**a, "emitted_at": datetime.now(timezone.utc).isoformat()})
    return emitted
