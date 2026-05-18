"""
TERRITOIRE-Ω · SPATIAL — Module institutionnel
================================================

╔═══════════════════════════════════════════════════════════════════════════╗
║  P22ΩΩ_BLOC_2_5_CORRIDORS_UNIQUES_PAR_ESPECE_Ω · 2026-05-18              ║
║  Commandant : STEEVE-MAX                                                  ║
║  Protocole : BCE-4X ULTIME ABSOLU                                         ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                           ║
║  ORIGINE                                                                  ║
║  ─────                                                                    ║
║  Migration INLINE complète de `engines/spatial_engine_v7/router.py`       ║
║  (735 lignes) vers ce module institutionnel Ω.                            ║
║                                                                           ║
║  Aucune modification fonctionnelle — le code V7 est copié tel quel        ║
║  dans `_v7_logic.py` pour préserver la logique scoring identique.         ║
║                                                                           ║
║  ENDPOINTS EXPOSÉS                                                        ║
║  ──────────────                                                           ║
║  Le router Ω `/api/v20/territoire/spatial/{heatmap,score,status}` est     ║
║  dans `/app/backend/routes/territoire_omega_spatial_router.py` qui        ║
║  délègue désormais aux fonctions de `_v7_logic` (interne).                ║
║                                                                           ║
║  DOCTRINE V30_LOCK                                                        ║
║  ───────────────                                                          ║
║  Le code spatial V7 est désormais institutionnel Ω. Le module legacy      ║
║  `engines/spatial_engine_v7/` est PURGÉ après cette migration.            ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

# Ré-export des fonctions métier depuis _v7_logic (code copié de V7 router.py)
from engines.v8_institutional.territoire_omega_spatial._v7_logic import (
    spatial_heatmap,
    spatial_scoring,
    spatial_status,
)

__all__ = [
    "spatial_heatmap",
    "spatial_scoring",
    "spatial_status",
]
