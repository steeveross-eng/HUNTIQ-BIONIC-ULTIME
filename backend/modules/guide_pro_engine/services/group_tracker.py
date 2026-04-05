"""
Group Tracker — Suivi temps reel groupe de chasse
BIONIC OS V8.5 | Phase E-1 | BCE-4X GOLDEN V6+

DataContract: DC-16 GroupPositionContract
EventBus: EB-21 guide:group:position, EB-22 guide:alert:spread

Points de Fusion:
  PF-E2: gestionnaire_engine → positions LIVE
  PF-E4: gestionnaire_engine → alertes SECOURS
"""

import logging
import math
from typing import Dict, List

logger = logging.getLogger("guide_pro.group_tracker")


def _haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Distance en metres entre deux coordonnees."""
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlng / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def get_group_positions(session: Dict) -> Dict:
    """
    Recuperer les positions LIVE de tous les membres du groupe.
    Point de Fusion PF-E2: Consomme gestionnaire_engine en LECTURE.
    """
    guide_id = session.get("guide_id", "")
    clients = session.get("clients", [])
    territory_id = session.get("territory_id", "")

    positions = []
    all_user_ids = [guide_id] + [c["user_id"] for c in clients if c.get("consent_gps")]

    # Tenter de recuperer les positions via gestionnaire_engine
    try:
        from modules.gestionnaire_engine.router import _positions_store
        for uid in all_user_ids:
            if uid in _positions_store:
                pos = _positions_store[uid]
                positions.append({
                    "user_id": uid,
                    "lat": pos.get("lat", 0),
                    "lng": pos.get("lng", 0),
                    "timestamp": pos.get("timestamp", ""),
                    "is_guide": uid == guide_id,
                })
    except Exception:
        logger.debug("[GROUP TRACKER] gestionnaire_engine non disponible, positions simulees")
        # Fallback: positions non disponibles
        for uid in all_user_ids:
            positions.append({
                "user_id": uid,
                "lat": 0, "lng": 0,
                "timestamp": "",
                "is_guide": uid == guide_id,
                "status": "no_gps",
            })

    # Calculer la dispersion du groupe
    spread_m = _calculate_group_spread(positions)
    max_spread = session.get("config", {}).get("max_group_spread_m", 500.0)
    spread_alert = spread_m > max_spread

    result = {
        "success": True,
        "session_id": session.get("session_id", ""),
        "positions": positions,
        "spread_m": round(spread_m, 1),
        "max_spread_m": max_spread,
        "spread_alert": spread_alert,
        "members_count": len(positions),
        "members_with_gps": len([p for p in positions if p.get("lat", 0) != 0]),
    }

    if spread_alert:
        logger.warning(
            f"[GROUP TRACKER] ALERTE DISPERSION: {spread_m:.0f}m > {max_spread:.0f}m "
            f"(session {session.get('session_id', '?')})"
        )

    return result


def _calculate_group_spread(positions: List[Dict]) -> float:
    """Calculer la dispersion maximale du groupe (distance max entre deux membres)."""
    valid_positions = [p for p in positions if p.get("lat", 0) != 0 and p.get("lng", 0) != 0]
    if len(valid_positions) < 2:
        return 0.0

    max_dist = 0.0
    for i in range(len(valid_positions)):
        for j in range(i + 1, len(valid_positions)):
            d = _haversine(
                valid_positions[i]["lat"], valid_positions[i]["lng"],
                valid_positions[j]["lat"], valid_positions[j]["lng"],
            )
            max_dist = max(max_dist, d)

    return max_dist
