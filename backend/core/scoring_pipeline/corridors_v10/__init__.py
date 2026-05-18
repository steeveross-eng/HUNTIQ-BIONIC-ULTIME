"""
CORRIDORS-V10 — CORE_MODULE Métier interne (sanctuarisé)
=========================================================

╔═══════════════════════════════════════════════════════════════════════════╗
║  SANCTUARISATION INSTITUTIONNELLE                                         ║
║  Directive : P22ΩΩ_PALIERS_1_4_PURGE_IMMEDIATE_Ω · 2026-05-18            ║
║  Commandant : STEEVE-MAX                                                  ║
║  Protocole : BCE-4X ULTIME ABSOLU                                         ║
╚═══════════════════════════════════════════════════════════════════════════╝

🔒 STATUT : CORE_MODULE — INTERDICTION DE PURGE AUTOMATIQUE

Bien que le router HTTP `/api/v10/corridors/*` soit désactivé depuis la
purge V6 et que le nom du module suggère un legacy V10, ce module est en
réalité un MODULE MÉTIER INTERNE essentiel au scoring V20/V30 actif.

## Dépendances actives (audit P22ΩΩ BLOC 3 · 2026-05-18) :

  ┌────────────────────────────────────────────────────┬─────────────────────────────┐
  │ Consommateur                                       │ Fonction importée           │
  ├────────────────────────────────────────────────────┼─────────────────────────────┤
  │ bce/exclusion_layer_bce4x.py:69                    │ cost_surface._load_cell_data │
  │ bce/exclusion_layer_bce4x.py:165                   │ cost_surface._load_cell_data │
  │ core/scoring_pipeline/score_consolide.py:28        │ engine.score_point_consolidated │
  │ engines/wildlife_behavior_omega/router.py:28       │ species_profiles.CORRIDOR_PROFILES │
  │ modules/score_consolide.py:29                      │ engine.score_point_consolidated │
  └────────────────────────────────────────────────────┴─────────────────────────────┘

## Composants fournis :

  - engine.py            : `score_point_consolidated()` — scoring multi-critères
  - cost_surface.py      : `_load_cell_data()` — surface de coût raster
  - species_profiles.py  : `CORRIDOR_PROFILES` — paramètres comportementaux

## Restrictions :

  ❌ NE PAS supprimer ce module (5 cassures cascade backend immédiates)
  ❌ NE PAS réactiver le router HTTP /api/v10/corridors/* (legacy supprimé V6)
  ✅ Modifications internes autorisées si tous les consommateurs sont mis à jour
  ✅ Refactoring vers `engines/v8_institutional/` autorisé avec migration coordonnée

## Doctrine institutionnelle :

  Le nom « corridors_v10 » est trompeur mais conservé pour stabilité des imports.
  Renommer ce module impliquerait de mettre à jour 5 fichiers consommateurs +
  cache de modules Python — opération différée (palier 5 hypothétique).

═══════════════════════════════════════════════════════════════════════════
Version : 10.0.0 (sanctuarisé · CORE_MODULE depuis 2026-05-18)
═══════════════════════════════════════════════════════════════════════════
"""

# Marqueur institutionnel pour audit automatisé / scripts purge
__core_module__ = True
__purge_forbidden__ = True
__sanctuarisation_directive__ = "P22ΩΩ_PALIERS_1_4_PURGE_IMMEDIATE_Ω"
__sanctuarisation_date__ = "2026-05-18"
__commandant__ = "STEEVE-MAX"
__active_consumers__ = (
    "bce.exclusion_layer_bce4x",
    "core.scoring_pipeline.score_consolide",
    "engines.wildlife_behavior_omega.router",
    "modules.score_consolide",
)
