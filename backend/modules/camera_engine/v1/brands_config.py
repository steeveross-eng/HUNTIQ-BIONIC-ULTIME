"""
Camera Engine — Brands & Models Configuration
CAMERA-BRANDS-Ω-FINAL: Liste officielle Canada/USA
Maintenue par Emergent — AUCUN texte libre autorisé.
"""

CAMERA_BRANDS_CONFIG = {
    "spypoint": {
        "label": "Spypoint",
        "models": [
            "FLEX", "FLEX-G36", "FLEX-S", "FLEX-E",
            "LINK-MICRO-S-LTE", "LINK-MICRO-LTE", "LINK-S", "LINK-S-DARK",
            "FORCE-20", "FORCE-PRO", "FORCE-DARK",
            "Autres modeles"
        ]
    },
    "browning": {
        "label": "Browning",
        "models": [
            "SPEC OPS", "SPEC OPS EDGE", "SPEC OPS ADVANTAGE",
            "STRIKE FORCE HD PRO-X", "STRIKE FORCE PRO DCL",
            "DARK OPS HD PRO", "DARK OPS PRO", "DARK OPS EXTREME",
            "DEFENDER", "RECON FORCE", "COMMAND OPS",
            "Autres modeles"
        ]
    },
    "bushnell": {
        "label": "Bushnell",
        "models": [
            "CORE DS", "CORE DS NO GLOW", "CORE S-4K",
            "CELLUCORE 20", "CELLUCORE 30",
            "TROPHY CAM", "PRIME", "IMPULSE",
            "Autres modeles"
        ]
    },
    "moultrie": {
        "label": "Moultrie",
        "models": [
            "MOBILE EDGE", "MOBILE EDGE PRO",
            "DELTA CELLULAR", "DELTA BASE",
            "MCG-14001", "A-900", "M-8000", "M-50i",
            "Autres modeles"
        ]
    },
    "tactacam": {
        "label": "Tactacam Reveal",
        "models": [
            "REVEAL X", "REVEAL X PRO", "REVEAL X 2.0",
            "REVEAL X GEN 2.0", "REVEAL SK",
            "Autres modeles"
        ]
    },
    "stealth_cam": {
        "label": "Stealth Cam",
        "models": [
            "DS4K", "FUSION X", "FUSION X PRO",
            "G42NG", "GX45NGW", "QS20", "QS24NGK", "RVOLT",
            "Autres modeles"
        ]
    },
    "wildgame": {
        "label": "Wildgame Innovations",
        "models": [
            "TERRA EXTREME", "ENCOUNTER 2.0", "ENCOUNTER CELL",
            "TERRA X", "TERRA CELL", "SHADOW MICRO",
            "Autres modeles"
        ]
    },
    "cuddeback": {
        "label": "Cuddeback / CuddeLink",
        "models": [
            "DUAL CELL", "J-SERIES", "J-1422", "J-1521", "J-1538",
            "CUDDELINK CELL", "LONG RANGE IR",
            "Autres modeles"
        ]
    },
    "covert": {
        "label": "Covert",
        "models": [
            "WC30", "WC30-A", "LC32",
            "BLACKHAWK LTE", "BLACKHAWK 12.2", "CODE BLACK LTE",
            "Autres modeles"
        ]
    },
    "reconyx": {
        "label": "Reconyx",
        "models": [
            "HYPERFIRE 2", "HYPERFIRE 2 HIGH OUTPUT",
            "HP2X", "HF2X", "ULTRAFIRE XS8",
            "Autres modeles"
        ]
    },
    "exodus": {
        "label": "Exodus",
        "models": [
            "LIFT II", "RIVAL", "TREK", "TREK CELL", "RENDER",
            "Autres modeles"
        ]
    },
    "spartan": {
        "label": "Spartan",
        "models": [
            "GOLIVE", "GOLIVE 2", "GOCAM", "GOCAM 2",
            "Autres modeles"
        ]
    },
    "primos": {
        "label": "Primos",
        "models": [
            "AUTOPILOT", "AUTOPILOT NO GLOW",
            "PROOF CAM", "BULLET PROOF 2",
            "Autres modeles"
        ]
    },
    "gardepro": {
        "label": "GardePro",
        "models": [
            "A3", "A3S", "E5", "E5S", "E6", "E8", "X50",
            "Autres modeles"
        ]
    },
    "campark": {
        "label": "Campark",
        "models": [
            "T200", "T150", "TC20", "T80", "T100",
            "Autres modeles"
        ]
    },
    "meidase": {
        "label": "Meidase",
        "models": [
            "S3", "S3 PRO", "S800", "P60", "P80",
            "Autres modeles"
        ]
    },
    "creativexp": {
        "label": "CreativeXP",
        "models": [
            "GS1", "GS2", "GS3", "GL1", "GL2",
            "Autres modeles"
        ]
    },
    "wosports": {
        "label": "Wosports",
        "models": [
            "G400", "G600", "LT-100", "4G LTE",
            "Autres modeles"
        ]
    },
    "gsm_outdoors": {
        "label": "GSM Outdoors",
        "models": [
            "MUDDY PRO CAM", "MUDDY MANIFEST", "MUDDY CELLULAR",
            "Autres modeles"
        ]
    },
    "boly": {
        "label": "Boly / BolyGuard",
        "models": [
            "BG310-M", "BG584", "BG590", "BG600",
            "BG668-E36W", "BG668-E36W LTE",
            "BG960-K30", "BG960-K30W", "BG960-K30 LTE", "BG668-M",
            "Autres modeles"
        ]
    },
    "other": {
        "label": "Autres",
        "models": [
            "Autres modeles"
        ]
    }
}

CAMERA_TYPES = [
    {"value": "cellulaire", "label": "Camera cellulaire (LTE)"},
    {"value": "reguliere", "label": "Camera reguliere (non cellulaire)"}
]

def get_valid_brands():
    """Return list of valid brand values."""
    return list(CAMERA_BRANDS_CONFIG.keys())

def get_valid_models(brand: str):
    """Return list of valid models for a brand."""
    config = CAMERA_BRANDS_CONFIG.get(brand)
    if not config:
        return ["Autres modeles"]
    return config["models"]

def validate_brand_model(brand: str, model: str) -> bool:
    """Validate brand+model combination."""
    if brand not in CAMERA_BRANDS_CONFIG:
        return False
    valid_models = CAMERA_BRANDS_CONFIG[brand]["models"]
    return model in valid_models
