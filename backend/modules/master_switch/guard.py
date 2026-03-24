"""
Master Switch Guard — P0-3 STEEVE-MAX x1900
=============================================

Dependency injectable dans n'importe quel routeur FastAPI pour verifier
si le module est active via le Master Switch avant d'executer la requete.

Usage dans un routeur:
    from modules.master_switch.guard import require_switch

    @router.get("/endpoint")
    async def my_endpoint(switch=Depends(require_switch("payments"))):
        ...

Si le switch est OFF ou si le global est OFF, retourne HTTP 503.
Si le Master Switch n'est pas initialise, le mode par defaut est LOCKED (tout OFF).

STEEVE-MAX x1900: Mode LOCKED jusqu'a directive x3000.
"""

from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging

logger = logging.getLogger(__name__)

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'bionic_db')

_client = None
_db = None


def _get_db():
    global _client, _db
    if _db is None:
        _client = AsyncIOMotorClient(MONGO_URL)
        _db = _client[DB_NAME]
    return _db


def require_switch(switch_id: str):
    """
    FastAPI dependency factory.
    Retourne une fonction async qui verifie le Master Switch.

    Args:
        switch_id: Identifiant du switch (ex: "payments", "ecommerce", "seo")

    Returns:
        Dependency function pour FastAPI Depends()
    """
    async def _check_switch():
        db = _get_db()

        switches_doc = await db.master_switches.find_one({"_type": "switches"})

        if not switches_doc:
            # Pas initialise = LOCKED par defaut = tout OFF
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "module_locked",
                    "switch_id": switch_id,
                    "reason": "Master Switch non initialise — mode LOCKED",
                    "message": f"Le module '{switch_id}' est verrouille. Contactez l'administrateur."
                }
            )

        switches = switches_doc.get("switches", {})

        # Verifier le switch global d'abord
        global_switch = switches.get("global", {})
        if not global_switch.get("is_active", False):
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "system_locked",
                    "switch_id": "global",
                    "reason": "Master Switch Global est OFF",
                    "message": "Le systeme est verrouille globalement. Aucun module public n'est accessible."
                }
            )

        # Verifier le switch specifique du module
        module_switch = switches.get(switch_id, {})
        if not module_switch.get("is_active", False):
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "module_locked",
                    "switch_id": switch_id,
                    "reason": f"Switch '{switch_id}' est OFF",
                    "message": f"Le module '{switch_id}' est desactive via le Master Switch."
                }
            )

        # Verifier le mode systeme (LOCKED = tout bloque)
        mode_doc = await db.master_switches.find_one({"_type": "system_mode"})
        if mode_doc:
            current_mode = mode_doc.get("current_mode", "LOCKED")
            if current_mode == "LOCKED":
                raise HTTPException(
                    status_code=503,
                    detail={
                        "error": "system_locked",
                        "switch_id": switch_id,
                        "reason": "Systeme en mode LOCKED",
                        "message": "Le systeme est en mode LOCKED. Aucune activation publique autorisee."
                    }
                )

        return {"switch_id": switch_id, "is_active": True}

    return _check_switch


async def is_switch_active(switch_id: str) -> bool:
    """
    Verification programmatique (non-dependency).
    Retourne True si le module est actif, False sinon.
    """
    db = _get_db()

    switches_doc = await db.master_switches.find_one({"_type": "switches"})
    if not switches_doc:
        return False

    switches = switches_doc.get("switches", {})

    # Global OFF = tout OFF
    if not switches.get("global", {}).get("is_active", False):
        return False

    # Module specifique
    return switches.get(switch_id, {}).get("is_active", False)


# Mapping module_name -> switch_id pour resolution automatique
MODULE_TO_SWITCH = {
    "payment_engine": "payments",
    "saline_ecommerce": "payments",
    "products_engine": "ecommerce",
    "cart_engine": "ecommerce",
    "orders_engine": "ecommerce",
    "customers_engine": "ecommerce",
    "freemium_engine": "freemium",
    "upsell_engine": "freemium",
    "marketing_engine": "marketing",
    "marketing_calendar_engine": "marketing",
    "seo_engine": "seo",
    "seo_suppliers": "seo",
    "messaging_engine": "messaging",
    "notification_unified_engine": "messaging",
    "affiliate_switch_engine": "affiliate",
    "affiliate_ads_engine": "affiliate",
    "ad_spaces_engine": "ad_spaces",
    "contact_engine": "contacts",
    "tracking_engine": "contacts",
    "networking_engine": "networking",
    "trigger_engine": "triggers",
    "rules_engine": "triggers",
    "backup_cloud_engine": "backups",
    "saline_engine": "saline_intelligence",
    "territory_engine": "territory",
    "bionic_engine_p0": "territory",
    "predictive_engine": "predictions",
    "wildlife_behavior_engine": "predictions",
    "weather_engine": "weather",
    "weather_fauna_simulation_engine": "weather",
    "camera_engine": "cameras",
    "hunting_trip_logger": "trips",
    "alerts_engine": "alerts",
    "scoring_engine": "scoring",
    "waypoint_scoring_engine": "scoring",
}


def require_switch_for_module(module_name: str):
    """
    Convenience: resout automatiquement le switch_id depuis le nom du module.
    """
    switch_id = MODULE_TO_SWITCH.get(module_name, module_name)
    return require_switch(switch_id)


logger.info("Master Switch Guard loaded — 22 switches, 35 module mappings")
