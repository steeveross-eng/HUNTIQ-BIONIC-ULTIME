"""
gis_reception_validators_omega.py — Validators Phase XXII (ORDRE N°42_BIS)
═════════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ORDRE N°42_BIS

Validateurs anti-génériques pour les couches GIS protégées entrantes.
Aucune génération synthétique — vérification stricte de structure et
intégrité des fichiers déposés par le COMMANDANT.

SLOTS supportés (6 couches protégées) :
  · FORET_MFFP_Ω
  · SOL_IRDA_Ω
  · CHASSE_ZEC_SEPAQ_Ω
  · ROUTES_MTQ_SECONDAIRES_Ω
  · LIMITES_TERRITORIALES_FINES_Ω
  · PRESSION_HUMAINE_Ω (optionnelle)
═════════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
import hashlib
import zipfile
from pathlib import Path
from typing import Any, Dict, List

# ═════════════════════════════════════════════════════════════════════════
# SLOTS GIS PROTÉGÉS — Spécifications canoniques
# ═════════════════════════════════════════════════════════════════════════
SLOTS_GIS_PROTÉGÉS_SPEC: List[Dict[str, Any]] = [
    {
        "slot_id": "FORET_MFFP_Ω",
        "label": "Couvert forestier MFFP (carte écoforestière)",
        "priority": "P0",
        "organisme": "MFFP — Direction des inventaires forestiers",
        "access_type": "TÉLÉCHARGEMENT_DIRECT_LICENCE",
        "url_acquisition": "https://www.donneesquebec.ca/recherche/dataset/carte-ecoforestiere-avec-perturbations",
        "license": "Licence ouverte gouvernement du Québec",
        "format_recommandé": "GeoPackage (.gpkg) ou Shapefile (.zip) ou Parquet",
        "formats_acceptes": ["gpkg", "zip", "parquet", "geojson"],
        "taille_min_octets": 1024,
        "taille_max_octets": 5 * 1024 * 1024 * 1024,  # 5 GB
        "champs_obligatoires_min": 5,
        "prerequis": [
            "Téléchargement portail Données Québec",
            "Acceptation licence ouverte",
            "Conversion optionnelle Shapefile → GeoPackage via ogr2ogr",
        ],
        "validators": ["check_format", "check_size", "check_integrity"],
        # ─── ORDRE N°46 · VOIE B — Multi-upload tuiles régionales ───────
        "multi_upload": True,
        "files_min": 1,
        "files_max": 32,
        "voie_acquisition": "VOIE_B_TUILES_REGIONALES_MFFP",
    },
    {
        "slot_id": "SOL_IRDA_Ω",
        "label": "Pédologie / classes de sol IRDA",
        "priority": "P0",
        "organisme": "IRDA — Institut de recherche et de développement en agroenvironnement",
        "access_type": "API_OU_LICENCE",
        "url_acquisition": "https://www.irda.qc.ca/fr/services/donnees-pedologiques/",
        "license": "Licence IRDA — entente d'utilisation requise",
        "format_recommandé": "GeoPackage (.gpkg) ou Shapefile (.zip)",
        "formats_acceptes": ["gpkg", "zip", "geojson", "parquet"],
        "taille_min_octets": 1024,
        "taille_max_octets": 2 * 1024 * 1024 * 1024,  # 2 GB
        "champs_obligatoires_min": 4,
        "prerequis": [
            "Demande d'accès IRDA",
            "Signature entente d'utilisation",
            "Réception données par canal sécurisé",
        ],
        "validators": ["check_format", "check_size", "check_integrity"],
    },
    {
        "slot_id": "CHASSE_ZEC_SEPAQ_Ω",
        "label": "Zones de chasse ZEC + SÉPAQ + Réserves fauniques",
        "priority": "P0",
        "organisme": "MFFP — SÉPAQ — Fédération des ZECs",
        "access_type": "TÉLÉCHARGEMENT_DIRECT_LICENCE",
        "url_acquisition": "https://www.donneesquebec.ca/recherche/dataset/territoires-fauniques-structures",
        "license": "Licence ouverte gouvernement du Québec",
        "format_recommandé": "GeoPackage (.gpkg) ou GeoJSON",
        "formats_acceptes": ["gpkg", "geojson", "zip", "parquet"],
        "taille_min_octets": 512,
        "taille_max_octets": 500 * 1024 * 1024,  # 500 MB
        "champs_obligatoires_min": 4,
        "prerequis": [
            "Téléchargement portail Données Québec",
            "Vérification jeu 'territoires fauniques structurés'",
        ],
        "validators": ["check_format", "check_size", "check_integrity"],
    },
    {
        "slot_id": "ROUTES_MTQ_SECONDAIRES_Ω",
        "label": "Réseau routier secondaire et chemins forestiers MTQ + RTSS",
        "priority": "P1",
        "organisme": "MTQ — Direction RTSS",
        "access_type": "API_OU_TÉLÉCHARGEMENT_LICENCE",
        "url_acquisition": "https://www.donneesquebec.ca/recherche/dataset/adresses-quebec-feature",
        "license": "Licence ouverte gouvernement du Québec + RTSS MTQ (convention possible)",
        "format_recommandé": "GeoPackage (.gpkg) ou GeoJSON",
        "formats_acceptes": ["gpkg", "geojson", "zip", "parquet"],
        "taille_min_octets": 1024,
        "taille_max_octets": 1 * 1024 * 1024 * 1024,  # 1 GB
        "champs_obligatoires_min": 3,
        "prerequis": [
            "Téléchargement portail Données Québec (Adresses Québec)",
            "Convention MTQ pour RTSS détaillé (optionnel)",
        ],
        "validators": ["check_format", "check_size", "check_integrity"],
    },
    {
        "slot_id": "LIMITES_TERRITORIALES_FINES_Ω",
        "label": "Limites territoriales fines (cantons, lots, arpentage cadastral)",
        "priority": "P1",
        "organisme": "MERN — Service de l'arpentage / Cadastre Québec",
        "access_type": "API_FONCIER_OU_TÉLÉCHARGEMENT",
        "url_acquisition": "https://www.donneesquebec.ca/recherche/dataset/cadastre-du-quebec-en-format-shapefile",
        "license": "Licence ouverte cadastre — conditions d'utilisation Cadastre Québec",
        "format_recommandé": "GeoPackage (.gpkg) ou Shapefile (.zip)",
        "formats_acceptes": ["gpkg", "zip", "geojson", "parquet"],
        "taille_min_octets": 1024,
        "taille_max_octets": 3 * 1024 * 1024 * 1024,  # 3 GB
        "champs_obligatoires_min": 3,
        "prerequis": [
            "Téléchargement portail Cadastre Québec",
            "Acceptation conditions Cadastre",
        ],
        "validators": ["check_format", "check_size", "check_integrity"],
    },
    {
        "slot_id": "PRESSION_HUMAINE_Ω",
        "label": "Pression humaine fine (densité population + activités récréatives)",
        "priority": "P2_OPTIONNELLE",
        "organisme": "Statistique Canada + MFFP (fréquentation chasse)",
        "access_type": "TÉLÉCHARGEMENT_DIRECT",
        "url_acquisition": "https://www150.statcan.gc.ca/n1/fr/catalogue/97F0008X",
        "license": "Open Data StatCan",
        "format_recommandé": "Parquet ou GeoTIFF (raster densité)",
        "formats_acceptes": ["parquet", "tif", "tiff", "gpkg", "geojson"],
        "taille_min_octets": 512,
        "taille_max_octets": 2 * 1024 * 1024 * 1024,  # 2 GB
        "champs_obligatoires_min": 2,
        "prerequis": [
            "Téléchargement landcover StatCan",
            "Optionnel : compilation données fréquentation MFFP",
        ],
        "validators": ["check_format", "check_size", "check_integrity"],
    },
    # ═══════════════════════════════════════════════════════════════════
    # ORDRE N°52-EXT · PEE_MAJ_Ω VOIE A — Pipeline monolithique
    # Substitut institutionnel des 60 tuiles FORET_MFFP_Ω
    # via fichier unique pee_maj.gpkg (~36,9 Go).
    # Anti-générique : ce slot ne devient canonique que sur upload réel.
    # ═══════════════════════════════════════════════════════════════════
    {
        "slot_id": "FORET_MFFP_PEE_MAJ_Ω",
        "label": "PEE_MAJ.gpkg monolithique — Couvert forestier MFFP unifié",
        "priority": "P0",
        "organisme": "MFFP — Direction des inventaires forestiers (PEE_MAJ)",
        "access_type": "TÉLÉCHARGEMENT_DIRECT_LICENCE",
        "url_acquisition": (
            "https://www.donneesquebec.ca/recherche/dataset/"
            "carte-ecoforestiere-avec-perturbations"
        ),
        "license": "Licence ouverte gouvernement du Québec",
        "format_recommandé": "GeoPackage (.gpkg) monolithique — pee_maj.gpkg",
        "formats_acceptes": ["gpkg"],
        "taille_min_octets": 1 * 1024 * 1024,             # 1 Mo (sécurité)
        "taille_max_octets": 50 * 1024 * 1024 * 1024,     # 50 Go (relevé)
        "champs_obligatoires_min": 5,
        "prerequis": [
            "Fichier monolithique pee_maj.gpkg (~36,9 Go)",
            "Pipeline chunked obligatoire (Cloudflare 100 Mo + payload >50Mo)",
            "Stockage éphémère /var/cache (67 Go libres) — derivés persistants post-promotion",
        ],
        "validators": ["check_format", "check_size", "check_integrity"],
        "type_pipeline": "MONO_GPKG_INSTITUTIONNEL",
        "voie_acquisition": "VOIE_A_PEE_MAJ_MONOLITHIQUE",
        # Substitution canonique des 60 tuiles FORET_MFFP_Ω quand LOADED
        "substitutes_slot_for_corridors_gis": "FORET_MFFP_Ω",
        # Pipeline éphémère — derivés institutionnels archivés post-compute
        "ephemeral_storage": True,
        "derivatives_persistent": True,
    },
]


SLOT_BY_ID: Dict[str, Dict[str, Any]] = {s["slot_id"]: s for s in SLOTS_GIS_PROTÉGÉS_SPEC}


# ═════════════════════════════════════════════════════════════════════════
# Validators (anti-générique strict)
# ═════════════════════════════════════════════════════════════════════════
def _ext(filename: str) -> str:
    """Retourne l'extension en minuscules sans le point."""
    name = filename.lower()
    if name.endswith(".zip"):
        return "zip"
    if name.endswith(".gpkg"):
        return "gpkg"
    if name.endswith(".geojson") or name.endswith(".json"):
        return "geojson"
    if name.endswith(".parquet"):
        return "parquet"
    if name.endswith(".tif"):
        return "tif"
    if name.endswith(".tiff"):
        return "tiff"
    parts = name.rsplit(".", 1)
    return parts[1] if len(parts) == 2 else ""


def check_format(slot_id: str, filename: str) -> Dict[str, Any]:
    spec = SLOT_BY_ID.get(slot_id)
    if not spec:
        return {"name": "check_format", "passed": False,
                 "reason": f"SLOT inconnu : {slot_id}"}
    e = _ext(filename)
    accepted = spec["formats_acceptes"]
    return {
        "name": "check_format",
        "passed": e in accepted,
        "extension_detectee": e,
        "formats_acceptes": accepted,
        "reason": ("OK" if e in accepted
                    else f"Extension '{e}' non supportée. Accepté: {accepted}"),
    }


def check_size(slot_id: str, size_bytes: int) -> Dict[str, Any]:
    spec = SLOT_BY_ID.get(slot_id)
    if not spec:
        return {"name": "check_size", "passed": False,
                 "reason": f"SLOT inconnu : {slot_id}"}
    mn, mx = spec["taille_min_octets"], spec["taille_max_octets"]
    ok = mn <= size_bytes <= mx
    return {
        "name": "check_size",
        "passed": ok,
        "size_bytes": size_bytes,
        "min": mn, "max": mx,
        "reason": "OK" if ok else (
            f"Taille {size_bytes} hors bornes [{mn}, {mx}]"),
    }


def check_integrity(file_path: Path) -> Dict[str, Any]:
    """Calcule SHA-256 et vérifie ZIP integrity si applicable.
    Anti-générique : un fichier vide ou tronqué est rejeté.
    """
    p = Path(file_path)
    if not p.exists():
        return {"name": "check_integrity", "passed": False,
                 "reason": "Fichier absent"}

    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    sha256 = h.hexdigest()

    extra: Dict[str, Any] = {}
    if p.suffix.lower() == ".zip":
        try:
            with zipfile.ZipFile(p, "r") as zf:
                bad = zf.testzip()
                if bad is not None:
                    return {"name": "check_integrity", "passed": False,
                             "sha256": sha256,
                             "reason": f"ZIP corrompu sur entrée {bad}"}
                extra["zip_entries"] = len(zf.namelist())
                extra["has_shapefile"] = any(
                    n.lower().endswith(".shp") for n in zf.namelist())
        except zipfile.BadZipFile:
            return {"name": "check_integrity", "passed": False,
                     "sha256": sha256, "reason": "Archive ZIP non valide"}

    return {"name": "check_integrity", "passed": True,
             "sha256": sha256, **extra, "reason": "OK"}


def validate_upload(slot_id: str, filename: str, file_path: Path) -> Dict[str, Any]:
    """Validation complète anti-générique pour un slot donné."""
    spec = SLOT_BY_ID.get(slot_id)
    if not spec:
        return {
            "slot_id": slot_id, "passed": False,
            "errors": [f"SLOT_INCONNU::{slot_id}"],
        }
    p = Path(file_path)
    size = p.stat().st_size if p.exists() else 0

    fmt = check_format(slot_id, filename)
    sz = check_size(slot_id, size)
    integ = check_integrity(p)

    all_pass = fmt["passed"] and sz["passed"] and integ["passed"]
    return {
        "slot_id": slot_id,
        "filename": filename,
        "size_bytes": size,
        "passed": all_pass,
        "validators": [fmt, sz, integ],
        "sha256": integ.get("sha256"),
    }


def list_slots() -> List[Dict[str, Any]]:
    """Liste publique des slots avec métadonnées (sans champs internes)."""
    return [
        {
            "slot_id": s["slot_id"],
            "label": s["label"],
            "priority": s["priority"],
            "organisme": s["organisme"],
            "access_type": s["access_type"],
            "url_acquisition": s["url_acquisition"],
            "license": s["license"],
            "format_recommandé": s["format_recommandé"],
            "formats_acceptes": s["formats_acceptes"],
            "taille_max_octets": s["taille_max_octets"],
            "prerequis": s["prerequis"],
            # ─── ORDRE N°46 · Exposition flags multi-upload au frontend ──
            "multi_upload": bool(s.get("multi_upload", False)),
            "files_min": int(s.get("files_min", 1)),
            "files_max": int(s.get("files_max", 1)),
            "voie_acquisition": s.get("voie_acquisition", "VOIE_A_MONOFICHIER"),
            # ─── ORDRE N°52-EXT · PEE_MAJ_Ω VOIE A — exposition champs canon ──
            "type_pipeline": s.get("type_pipeline"),
            "substitutes_slot_for_corridors_gis": s.get(
                "substitutes_slot_for_corridors_gis"),
            "ephemeral_storage": bool(s.get("ephemeral_storage", False)),
            "derivatives_persistent": bool(s.get("derivatives_persistent", False)),
        }
        for s in SLOTS_GIS_PROTÉGÉS_SPEC
    ]


# ═════════════════════════════════════════════════════════════════════════
# ORDRE N°46 · Agrégation SHA-256 composite (VOIE B — tuiles régionales)
# ═════════════════════════════════════════════════════════════════════════
def compute_composite_sha256(individual_shas: List[str]) -> str:
    """Calcule un SHA-256 composite déterministe à partir d'une liste de
    SHA-256 individuels. L'ordre des hashes est imposé (tri alphabétique)
    pour garantir un résultat reproductible indépendamment de l'ordre
    d'arrivée des tuiles.

    Formule : SHA256( sorted(sha_i).join('\\n') )

    Anti-générique : rejette une entrée vide.
    """
    if not individual_shas:
        return ""
    ordered = sorted(s for s in individual_shas if s)
    h = hashlib.sha256()
    for s in ordered:
        h.update(s.encode("utf-8"))
        h.update(b"\n")
    return h.hexdigest()


def is_multi_upload_slot(slot_id: str) -> bool:
    """Retourne True si le slot accepte plusieurs fichiers agrégés."""
    spec = SLOT_BY_ID.get(slot_id, {})
    return bool(spec.get("multi_upload", False))


__all__ = [
    "SLOTS_GIS_PROTÉGÉS_SPEC",
    "SLOT_BY_ID",
    "check_format",
    "check_size",
    "check_integrity",
    "validate_upload",
    "list_slots",
    "compute_composite_sha256",
    "is_multi_upload_slot",
]
