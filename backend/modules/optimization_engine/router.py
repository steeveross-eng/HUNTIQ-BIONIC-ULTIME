"""
optimization_engine — Module d'Auto-Optimisation BIONIC™
Restauré depuis V2 et adapté BCE-4X pour V6

Fonctionnalités:
- Gestion des propositions d'optimisation
- Version management et snapshots
- Processus d'approbation administrateur
- Auto-analyse du système
- Notifications par email
- Toggle ON/OFF du module

BCE-4X: Conforme | MAX ULTRA: Conforme | STEEVE-MAX: Conforme
Date: 2026-03-23
Source: V2/auto_optimization.py (restauration sélective)
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
import os
import json

# ================================
# CONFIGURATION
# ================================

router = APIRouter(prefix="/api/admin/optimization", tags=["Auto-Optimization"])

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'bionic_db')

# Limites
MAX_VERSIONS = 50
MAX_PROPOSALS = 100

# Email
try:
    import resend
    RESEND_AVAILABLE = True
except ImportError:
    RESEND_AVAILABLE = False

# MongoDB client
_client = None
_db = None

def get_db():
    """Obtient la connexion MongoDB"""
    global _client, _db
    if _db is None:
        _client = AsyncIOMotorClient(MONGO_URL)
        _db = _client[DB_NAME]
    return _db

# ================================
# MODÈLES PYDANTIC
# ================================

class OptimizationProposal(BaseModel):
    """Proposition d'optimisation système"""
    title: str = Field(..., description="Titre de la proposition")
    description: str = Field(..., description="Description détaillée")
    type: str = Field(default="optimization", description="Type: optimization, performance, security, fix, feature, config")
    impact: str = Field(default="medium", description="Impact: low, medium, high, critical")
    affected_modules: List[str] = Field(default=[], description="Modules impactés")
    benefits: List[str] = Field(default=[], description="Bénéfices attendus")
    risks: List[str] = Field(default=[], description="Risques potentiels")
    requires_restart: bool = Field(default=False, description="Nécessite un redémarrage")
    estimated_time: str = Field(default="instant", description="Temps estimé")

class ProposalApproval(BaseModel):
    """Approbation d'une proposition"""
    admin_notes: str = Field(default="", description="Notes de l'administrateur")

class ProposalRejection(BaseModel):
    """Rejet d'une proposition"""
    rejection_reason: str = Field(default="", description="Raison du rejet")

class VersionBackup(BaseModel):
    """Configuration de backup versionné"""
    description: str = Field(default="", description="Description du backup")
    modules: List[str] = Field(
        default=["bionic", "territory", "waypoints", "zones", "config"],
        description="Modules à sauvegarder"
    )

class ModuleConfig(BaseModel):
    """Configuration du module d'optimisation"""
    enabled: bool = Field(default=True, description="Module activé")
    email_notifications: bool = Field(default=False, description="Notifications email")
    notification_email: Optional[EmailStr] = Field(default=None, description="Email de notification")
    auto_analyze_interval_hours: int = Field(default=24, description="Intervalle d'auto-analyse (heures)")

# ================================
# HELPERS
# ================================

def serialize_doc(doc: dict) -> dict:
    """Sérialise un document MongoDB pour JSON"""
    if doc is None:
        return None
    result = dict(doc)
    if "_id" in result:
        result["id"] = str(result["_id"])
        del result["_id"]
    return result

def serialize_docs(docs: List[dict]) -> List[dict]:
    """Sérialise une liste de documents"""
    return [serialize_doc(d) for d in docs]

# ================================
# CONFIGURATION DU MODULE
# ================================

@router.get("/config", response_model=Dict[str, Any])
async def get_config():
    """Récupère la configuration actuelle du module d'optimisation"""
    try:
        db = get_db()
        config = await db.optimization_config.find_one({"type": "module_settings"})
        
        if config:
            return {
                "enabled": config.get("enabled", True),
                "email_notifications": config.get("email_notifications", False),
                "notification_email": config.get("notification_email"),
                "auto_analyze_interval_hours": config.get("auto_analyze_interval_hours", 24)
            }
        
        # Valeurs par défaut
        return {
            "enabled": True,
            "email_notifications": False,
            "notification_email": None,
            "auto_analyze_interval_hours": 24
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur configuration: {str(e)}")

@router.post("/config")
async def update_config(config: ModuleConfig):
    """Met à jour la configuration du module d'optimisation"""
    try:
        db = get_db()
        
        await db.optimization_config.update_one(
            {"type": "module_settings"},
            {"$set": {
                "type": "module_settings",
                "enabled": config.enabled,
                "email_notifications": config.email_notifications,
                "notification_email": config.notification_email,
                "auto_analyze_interval_hours": config.auto_analyze_interval_hours,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }},
            upsert=True
        )
        
        return {
            "message": "Configuration mise à jour",
            "config": config.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/toggle")
async def toggle_module(enabled: bool = True):
    """Active ou désactive le module d'auto-optimisation"""
    try:
        db = get_db()
        
        await db.optimization_config.update_one(
            {"type": "module_settings"},
            {"$set": {
                "type": "module_settings",
                "enabled": enabled,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }},
            upsert=True
        )
        
        status = "activé" if enabled else "désactivé"
        return {
            "message": f"Module d'auto-optimisation {status}",
            "enabled": enabled
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ================================
# NOTIFICATIONS EMAIL
# ================================

async def send_optimization_email(subject: str, html_content: str) -> bool:
    """Envoie une notification email pour les événements d'optimisation"""
    try:
        db = get_db()
        config = await db.optimization_config.find_one({"type": "module_settings"})
        
        if not config or not config.get("email_notifications") or not config.get("notification_email"):
            return False
        
        if not RESEND_AVAILABLE:
            return False
        
        # Récupérer la clé API
        resend_config = await db.backup_config.find_one({"type": "resend_api"})
        api_key = resend_config.get("api_key") if resend_config else os.environ.get("RESEND_API_KEY")
        
        if not api_key:
            return False
        
        resend.api_key = api_key
        
        params = {
            "from": "BIONIC™ Auto-Optimization <noreply@scentscience.com>",
            "to": [config["notification_email"]],
            "subject": subject,
            "html": html_content
        }
        
        resend.Emails.send(params)
        return True
    except Exception:
        return False

def generate_proposal_email_html(proposals: List[dict]) -> str:
    """Génère le HTML pour les notifications de propositions"""
    type_icons = {
        "performance": "⚡",
        "security": "🔒",
        "optimization": "🚀",
        "fix": "🔧",
        "feature": "✨",
        "config": "⚙️"
    }
    
    proposals_html = ""
    for p in proposals:
        icon = type_icons.get(p.get("type", "optimization"), "📋")
        proposals_html += f"""
        <div style="background: #f8f9fa; border-left: 4px solid #4ecca3; padding: 15px; margin: 10px 0; border-radius: 4px;">
            <h3 style="margin: 0 0 10px 0; color: #1a1a2e;">{icon} {p.get('title', 'Sans titre')}</h3>
            <p style="margin: 0; color: #666;">{p.get('description', '')}</p>
            <div style="margin-top: 10px;">
                <span style="background: #4ecca3; color: #000; padding: 2px 8px; border-radius: 12px; font-size: 11px; margin-right: 5px;">
                    {p.get('type', 'optimization').upper()}
                </span>
                <span style="background: #e9ecef; color: #495057; padding: 2px 8px; border-radius: 12px; font-size: 11px;">
                    Impact: {p.get('impact', 'medium')}
                </span>
            </div>
        </div>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto;">
        <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 30px; text-align: center;">
            <h1 style="color: #4ecca3; margin: 0;">🧠 BIONIC™ Auto-Optimisation</h1>
            <p style="color: #888; margin: 10px 0 0 0;">Nouvelles propositions d'optimisation</p>
        </div>
        <div style="padding: 30px; background: #fff;">
            <p>Bonjour,</p>
            <p>Le module d'auto-optimisation BIONIC™ a généré <strong>{len(proposals)} nouvelle(s) proposition(s)</strong> :</p>
            {proposals_html}
            <div style="margin-top: 30px; padding: 20px; background: #4ecca3; border-radius: 8px; text-align: center;">
                <a href="#" style="color: #000; text-decoration: none; font-weight: bold; font-size: 16px;">
                    ➜ Accéder au panneau d'administration
                </a>
            </div>
        </div>
        <div style="background: #1a1a2e; color: #888; padding: 20px; text-align: center; font-size: 12px;">
            <p>Module d'Auto-Optimisation BIONIC™ V6 — BCE-4X Compliant</p>
        </div>
    </body>
    </html>
    """

# ================================
# PROPOSITIONS D'OPTIMISATION
# ================================

@router.get("/proposals")
async def get_proposals(status: Optional[str] = None, limit: int = 50):
    """Récupère les propositions d'optimisation"""
    try:
        db = get_db()
        query = {}
        if status:
            query["status"] = status
        
        cursor = db.optimization_proposals.find(query).sort("created_at", -1).limit(limit)
        proposals = await cursor.to_list(length=limit)
        
        return serialize_docs(proposals)
    except Exception:
        return []

@router.post("/proposals")
async def create_proposal(proposal: OptimizationProposal):
    """Crée une nouvelle proposition d'optimisation"""
    try:
        db = get_db()
        
        proposal_data = {
            **proposal.dict(),
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "created_by": "system"
        }
        
        result = await db.optimization_proposals.insert_one(proposal_data)
        
        return {
            "id": str(result.inserted_id),
            "message": "Proposition créée avec succès",
            **proposal_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/proposals/{proposal_id}/approve")
async def approve_proposal(proposal_id: str, approval: ProposalApproval):
    """Approuve une proposition d'optimisation"""
    try:
        db = get_db()
        
        # Vérifier existence
        proposal = await db.optimization_proposals.find_one({"_id": ObjectId(proposal_id)})
        if not proposal:
            raise HTTPException(status_code=404, detail="Proposition non trouvée")
        
        # Créer backup avant approbation
        backup_id, version_id = await create_version_backup_internal(
            f"Backup automatique avant approbation: {proposal.get('title', 'Unknown')}"
        )
        
        # Mettre à jour le statut
        await db.optimization_proposals.update_one(
            {"_id": ObjectId(proposal_id)},
            {"$set": {
                "status": "approved",
                "approved_at": datetime.now(timezone.utc).isoformat(),
                "admin_notes": approval.admin_notes,
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "backup_version_id": version_id
            }}
        )
        
        return {
            "message": "Proposition approuvée avec succès",
            "proposal_id": proposal_id,
            "backup_created": backup_id is not None,
            "backup_version": version_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/proposals/{proposal_id}/reject")
async def reject_proposal(proposal_id: str, rejection: ProposalRejection):
    """Rejette une proposition d'optimisation"""
    try:
        db = get_db()
        
        await db.optimization_proposals.update_one(
            {"_id": ObjectId(proposal_id)},
            {"$set": {
                "status": "rejected",
                "rejected_at": datetime.now(timezone.utc).isoformat(),
                "rejection_reason": rejection.rejection_reason,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return {
            "message": "Proposition rejetée",
            "proposal_id": proposal_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/proposals/{proposal_id}")
async def delete_proposal(proposal_id: str):
    """Supprime une proposition"""
    try:
        db = get_db()
        result = await db.optimization_proposals.delete_one({"_id": ObjectId(proposal_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Proposition non trouvée")
        
        return {"message": "Proposition supprimée", "proposal_id": proposal_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ================================
# GESTION DES VERSIONS
# ================================

async def create_version_backup_internal(description: str = "") -> tuple:
    """Crée un backup versionné (usage interne)"""
    try:
        db = get_db()
        timestamp = datetime.now(timezone.utc)
        version_id = f"BIONIC_v{timestamp.strftime('%Y%m%d_%H%M%S')}"
        
        version_data = {
            "version_id": version_id,
            "description": description or f"Backup automatique - {timestamp.strftime('%d/%m/%Y %H:%M')}",
            "created_at": timestamp.isoformat(),
            "modules": ["waypoints", "zones", "config"],
            "module_snapshots": {},
            "source": "optimization_engine"
        }
        
        # Capturer les snapshots
        try:
            waypoints = await db.waypoints.find({}, {"_id": 0}).to_list(length=10000)
            version_data["module_snapshots"]["waypoints"] = waypoints
        except:
            version_data["module_snapshots"]["waypoints"] = []
        
        try:
            zones = await db.zones.find({}, {"_id": 0}).to_list(length=10000)
            version_data["module_snapshots"]["zones"] = zones
        except:
            version_data["module_snapshots"]["zones"] = []
        
        try:
            config = await db.app_config.find_one({}, {"_id": 0})
            version_data["module_snapshots"]["config"] = config or {}
        except:
            version_data["module_snapshots"]["config"] = {}
        
        result = await db.optimization_versions.insert_one(version_data)
        return str(result.inserted_id), version_id
    except Exception:
        return None, None

@router.get("/versions")
async def get_versions(limit: int = 50):
    """Récupère l'historique des versions sauvegardées"""
    try:
        db = get_db()
        
        cursor = db.optimization_versions.find().sort("created_at", -1).limit(min(limit, MAX_VERSIONS))
        versions = await cursor.to_list(length=limit)
        
        # Nettoyer les snapshots pour réduire la taille de réponse
        result = []
        for v in versions:
            clean_v = serialize_doc(v)
            if "module_snapshots" in clean_v:
                clean_v["module_snapshots"] = {
                    k: f"{len(v) if isinstance(v, list) else 1} items"
                    for k, v in clean_v["module_snapshots"].items()
                }
            result.append(clean_v)
        
        return result
    except Exception:
        return []

@router.post("/versions")
async def create_version_backup(backup: VersionBackup):
    """Crée un backup versionné de l'état actuel"""
    try:
        db = get_db()
        timestamp = datetime.now(timezone.utc)
        version_id = f"BIONIC_v{timestamp.strftime('%Y%m%d_%H%M%S')}"
        
        version_data = {
            "version_id": version_id,
            "description": backup.description or f"Backup manuel - {timestamp.strftime('%d/%m/%Y %H:%M')}",
            "created_at": timestamp.isoformat(),
            "modules": backup.modules,
            "module_snapshots": {},
            "source": "manual"
        }
        
        # Capturer les modules demandés
        for module in backup.modules:
            try:
                if module == "waypoints":
                    data = await db.waypoints.find({}, {"_id": 0}).to_list(length=10000)
                    version_data["module_snapshots"]["waypoints"] = data
                elif module == "zones":
                    data = await db.zones.find({}, {"_id": 0}).to_list(length=10000)
                    version_data["module_snapshots"]["zones"] = data
                elif module == "config":
                    config = await db.app_config.find_one({}, {"_id": 0})
                    version_data["module_snapshots"]["config"] = config or {}
            except:
                version_data["module_snapshots"][module] = []
        
        result = await db.optimization_versions.insert_one(version_data)
        
        # Nettoyer anciennes versions si nécessaire
        total = await db.optimization_versions.count_documents({})
        if total > MAX_VERSIONS:
            oldest = db.optimization_versions.find().sort("created_at", 1).limit(total - MAX_VERSIONS)
            async for old in oldest:
                await db.optimization_versions.delete_one({"_id": old["_id"]})
        
        return {
            "id": str(result.inserted_id),
            "version_id": version_id,
            "message": "Backup créé avec succès",
            "modules_saved": backup.modules
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/versions/{version_id}/restore")
async def restore_version(version_id: str):
    """Restaure une version précédente"""
    try:
        db = get_db()
        
        # Trouver la version
        version = await db.optimization_versions.find_one({"_id": ObjectId(version_id)})
        if not version:
            raise HTTPException(status_code=404, detail="Version non trouvée")
        
        # Créer backup de l'état actuel
        await create_version_backup_internal(
            f"Backup pré-restauration vers {version.get('version_id', 'unknown')}"
        )
        
        # Restaurer les snapshots
        snapshots = version.get("module_snapshots", {})
        restored_modules = []
        
        for module, data in snapshots.items():
            try:
                if module == "waypoints" and data:
                    await db.waypoints.delete_many({})
                    if len(data) > 0:
                        await db.waypoints.insert_many(data)
                    restored_modules.append("waypoints")
                elif module == "zones" and data:
                    await db.zones.delete_many({})
                    if len(data) > 0:
                        await db.zones.insert_many(data)
                    restored_modules.append("zones")
                elif module == "config" and data:
                    await db.app_config.replace_one({}, data, upsert=True)
                    restored_modules.append("config")
            except Exception:
                pass
        
        # Marquer la restauration
        await db.optimization_versions.update_one(
            {"_id": ObjectId(version_id)},
            {"$set": {"last_restored_at": datetime.now(timezone.utc).isoformat()}}
        )
        
        return {
            "message": f"Version {version.get('version_id')} restaurée avec succès",
            "restored_modules": restored_modules,
            "backup_created": True
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ================================
# AUTO-ANALYSE
# ================================

@router.post("/analyze")
async def run_auto_analysis():
    """Exécute une auto-analyse du système et génère des suggestions"""
    try:
        db = get_db()
        
        # Vérifier si le module est activé
        config = await db.optimization_config.find_one({"type": "module_settings"})
        if config and not config.get("enabled", True):
            return {
                "message": "Module d'auto-optimisation désactivé",
                "suggestions_count": 0,
                "suggestions": [],
                "module_enabled": False
            }
        
        suggestions = []
        new_proposals = []
        
        # Analyse 1: Waypoints sans coordonnées
        try:
            invalid_waypoints = await db.waypoints.count_documents({
                "$or": [
                    {"lat": {"$exists": False}},
                    {"lng": {"$exists": False}},
                    {"lat": None},
                    {"lng": None}
                ]
            })
            if invalid_waypoints > 0:
                suggestions.append({
                    "title": f"Nettoyage de {invalid_waypoints} waypoints invalides",
                    "description": f"Détecté {invalid_waypoints} waypoints sans coordonnées valides.",
                    "type": "optimization",
                    "impact": "low",
                    "affected_modules": ["waypoints", "territory"],
                    "benefits": ["Réduction de la taille de la base de données"],
                    "risks": ["Perte de données potentiellement récupérables"]
                })
        except:
            pass
        
        # Analyse 2: Nombre de versions
        try:
            version_count = await db.optimization_versions.count_documents({})
            if version_count > MAX_VERSIONS * 0.8:
                suggestions.append({
                    "title": "Nettoyage des anciennes versions",
                    "description": f"Le système conserve {version_count} versions sur {MAX_VERSIONS} max.",
                    "type": "optimization",
                    "impact": "low",
                    "affected_modules": ["config"],
                    "benefits": ["Libération d'espace de stockage"],
                    "risks": []
                })
        except:
            pass
        
        # Analyse 3: Propositions en attente
        try:
            pending = await db.optimization_proposals.count_documents({"status": "pending"})
            if pending > 10:
                suggestions.append({
                    "title": f"Revue de {pending} propositions en attente",
                    "description": f"Il y a {pending} propositions d'optimisation en attente de décision.",
                    "type": "config",
                    "impact": "medium",
                    "affected_modules": ["admin"],
                    "benefits": ["Maintien d'un système optimisé"],
                    "risks": []
                })
        except:
            pass
        
        # Créer les propositions dans la base
        for suggestion in suggestions:
            # Vérifier si une proposition similaire existe
            existing = await db.optimization_proposals.find_one({
                "title": suggestion["title"],
                "status": "pending"
            })
            if not existing:
                suggestion["status"] = "pending"
                suggestion["created_at"] = datetime.now(timezone.utc).isoformat()
                suggestion["updated_at"] = datetime.now(timezone.utc).isoformat()
                suggestion["created_by"] = "auto_analysis"
                await db.optimization_proposals.insert_one(suggestion)
                new_proposals.append(suggestion)
        
        # Notification email
        if new_proposals:
            email_config = await db.optimization_config.find_one({"type": "module_settings"})
            if email_config and email_config.get("email_notifications"):
                email_html = generate_proposal_email_html(new_proposals)
                await send_optimization_email(
                    f"🧠 BIONIC™: {len(new_proposals)} nouvelle(s) proposition(s)",
                    email_html
                )
        
        return {
            "message": "Analyse terminée",
            "suggestions_count": len(suggestions),
            "new_proposals_count": len(new_proposals),
            "suggestions": suggestions,
            "module_enabled": True,
            "analyzed_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ================================
# STATISTIQUES
# ================================

@router.get("/stats")
async def get_optimization_stats():
    """Récupère les statistiques du module d'optimisation"""
    try:
        db = get_db()
        
        stats = {
            "proposals": {
                "total": await db.optimization_proposals.count_documents({}),
                "pending": await db.optimization_proposals.count_documents({"status": "pending"}),
                "approved": await db.optimization_proposals.count_documents({"status": "approved"}),
                "rejected": await db.optimization_proposals.count_documents({"status": "rejected"})
            },
            "versions": {
                "total": await db.optimization_versions.count_documents({}),
                "max_allowed": MAX_VERSIONS
            },
            "module": {
                "enabled": True
            }
        }
        
        # Vérifier l'état du module
        config = await db.optimization_config.find_one({"type": "module_settings"})
        if config:
            stats["module"]["enabled"] = config.get("enabled", True)
            stats["module"]["email_notifications"] = config.get("email_notifications", False)
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
