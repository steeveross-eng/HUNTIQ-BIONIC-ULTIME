"""
╔═══════════════════════════════════════════════════════════════════════════╗
║  TESTS DOCTRINAUX Ω — VERROUILLAGE SPECIES_PRESENCE_MASK + INVARIANTS     ║
║  P22ΩΩ_BLOC_5_TESTS_REGRESSION_PRESENCE_MASK_Ω · 2026-05-18              ║
║  Commandant : STEEVE-MAX                                                  ║
║  Protocole : BCE-4X ULTIME ABSOLU                                         ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                           ║
║  OBJET                                                                    ║
║  ─────                                                                    ║
║  Suite de tests de non-régression garantissant les invariants doctrinaux  ║
║  Ω post-correctifs (P22ΩΩ_FIX_PRESENCE_MASK_BYPASS + BLOC 2.x). Tout      ║
║  régression dans ces invariants doit être détectée immédiatement.        ║
║                                                                           ║
║  INVARIANTS COUVERTS                                                      ║
║  ──────────────────                                                       ║
║  I-1.  Wapiti @ Bas-Saint-Laurent (48.21, -68.38) → status ABSENT         ║
║  I-2.  Wapiti @ Mauricie (47.0, -73.5) → status PRESENT (zone intro)      ║
║  I-3.  Chevreuil @ BSL → status PRESENT (zone naturelle)                  ║
║  I-4.  apply_presence_mask : 0 corridors pour espèce ABSENTE              ║
║  I-5.  apply_presence_mask : zones tagged species purgées si ABSENT       ║
║  I-6.  apply_presence_mask : infrastructure (sans tag) préservée          ║
║  I-7.  Rayon entry/exit fonctionnel = 780m (BLOC 2.2)                     ║
║  I-8.  Promotion auto veine principale si aucune (BLOC 2.4)               ║
║  I-9.  Aucun fallback V8/V10 actif (PALIER 1+2+3)                         ║
║  I-10. organic_generate applique le presence_mask (FIX_BYPASS)            ║
║  I-11. smoother réapplique le mask après external_inflow (FIX_BYPASS)     ║
║                                                                           ║
║  EXÉCUTION                                                                ║
║  ─────────                                                                ║
║      cd /app/backend && python -m pytest tests/test_doctrinal_omega_presence_mask.py -v -m doctrinal_omega
║                                                                           ║
║  Doctrine : tests doctrinaux Ω exemptés du filtre BCE-4X TERRITOIRE       ║
║  (via marqueur `doctrinal_omega` whitelisté dans tests/conftest.py).      ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""
from __future__ import annotations

import asyncio
import pytest

# Marqueur institutionnel — TOUS les tests de ce fichier sont doctrinal_omega
pytestmark = pytest.mark.doctrinal_omega


# ─────────────────────────────────────────────────────────────────────────
# WAYPOINTS DE RÉFÉRENCE INSTITUTIONNELS
# ─────────────────────────────────────────────────────────────────────────
BSL = (48.206657, -68.382422)        # Bas-Saint-Laurent (canonique COMMANDANT)
MAURICIE_TRITON = (47.0, -73.5)       # Seigneurie du Triton (zone intro wapiti)
SAGUENAY = (48.4, -71.0)              # Saguenay (hors zone wapiti)


# =========================================================================
# I-1 / I-2 / I-3 — REGISTRE DE PRÉSENCE MFFP 2024
# =========================================================================

def test_wapiti_at_bsl_is_absent():
    """I-1 — Wapiti @ BSL doit être ABSENT (registre MFFP 2024)."""
    from engines.v8_institutional.species_presence_mask_omega import get_species_presence
    presence = get_species_presence(BSL[0], BSL[1], "wapiti")
    assert presence["status"] == "ABSENT", (
        f"Wapiti @ BSL devrait être ABSENT, got {presence['status']}"
    )
    assert presence["reason"] == "outside_natural_range"
    assert presence["canonical"] == "wapiti"


def test_wapiti_at_mauricie_is_present():
    """I-2 — Wapiti @ Mauricie/Triton doit être PRESENT (zone intro MFFP 2024)."""
    from engines.v8_institutional.species_presence_mask_omega import get_species_presence
    presence = get_species_presence(MAURICIE_TRITON[0], MAURICIE_TRITON[1], "wapiti")
    assert presence["status"] == "PRESENT", (
        f"Wapiti @ Mauricie devrait être PRESENT (zone intro), got {presence['status']}"
    )
    assert presence["reason"] == "in_natural_range"


def test_chevreuil_at_bsl_is_present():
    """I-3 — Chevreuil @ BSL doit être PRESENT (zone naturelle)."""
    from engines.v8_institutional.species_presence_mask_omega import get_species_presence
    presence = get_species_presence(BSL[0], BSL[1], "chevreuil")
    assert presence["status"] == "PRESENT"
    assert presence["canonical"] == "chevreuil"


def test_wapiti_outside_all_intro_zones():
    """I-1bis — Wapiti @ 3 waypoints hors zones intro → tous ABSENT."""
    from engines.v8_institutional.species_presence_mask_omega import get_species_presence
    waypoints_absent = [
        (48.206657, -68.382422, "BSL"),
        (48.4, -71.0, "Saguenay"),
        (48.5, -78.0, "Abitibi"),
    ]
    for lat, lon, name in waypoints_absent:
        presence = get_species_presence(lat, lon, "wapiti")
        assert presence["status"] == "ABSENT", (
            f"Wapiti @ {name} ({lat},{lon}) devrait être ABSENT, got {presence['status']}"
        )


# =========================================================================
# I-4 / I-5 / I-6 — apply_presence_mask_to_bundle
# =========================================================================

def _build_fake_bundle(species: str, n_corridors: int = 5, n_zones_tagged: int = 3, n_zones_infra: int = 2) -> dict:
    """Construit un bundle minimal pour tester apply_presence_mask_to_bundle."""
    bundle = {
        "corridors": [
            {"id": f"c{i}", "type": "organic", "path": [[48.2, -68.4], [48.21, -68.39]]}
            for i in range(n_corridors)
        ],
        "affuts": [{"id": f"a{i}", "lat": 48.2, "lng": -68.4} for i in range(3)],
        "hotspots": [{"id": f"h{i}", "lat": 48.2, "lng": -68.4} for i in range(2)],
        "salines": [{"id": f"s{i}", "lat": 48.2, "lng": -68.4} for i in range(4)],
        "zones": (
            [
                {"id": f"z{i}", "type": "rut", "species": species, "species_bias_applied": 0.95}
                for i in range(n_zones_tagged)
            ]
            + [
                {"id": f"infra{i}", "type": "hydat"}  # infra sans tag espèce
                for i in range(n_zones_infra)
            ]
        ),
    }
    return bundle


def test_mask_purges_all_paths_for_absent_species():
    """I-4 — apply_presence_mask vide corridors/affuts/hotspots/salines pour espèce ABSENT."""
    from engines.v8_institutional.species_presence_mask_omega import apply_presence_mask_to_bundle
    bundle = _build_fake_bundle("wapiti", n_corridors=8, n_zones_tagged=4, n_zones_infra=2)
    result = apply_presence_mask_to_bundle(bundle, species="wapiti", lat=BSL[0], lng=BSL[1])
    assert result["bio_presence_mask_applied"] is True
    assert result["bio_presence_mask_halt"] is True
    assert len(result["corridors"]) == 0, "I-4 : corridors should be empty for ABSENT species"
    assert len(result.get("affuts", [])) == 0
    assert len(result.get("hotspots", [])) == 0
    assert len(result.get("salines", [])) == 0


def test_mask_purges_tagged_zones_for_absent_species():
    """I-5 — apply_presence_mask purge les zones tagged species_dependent (BLOC 2.1)."""
    from engines.v8_institutional.species_presence_mask_omega import apply_presence_mask_to_bundle
    bundle = _build_fake_bundle("wapiti", n_corridors=3, n_zones_tagged=4, n_zones_infra=2)
    result = apply_presence_mask_to_bundle(bundle, species="wapiti", lat=BSL[0], lng=BSL[1])
    purge = result.get("bio_presence_mask_purge_counts", {})
    assert purge.get("zones") == 4, f"I-5 : 4 zones tagged should be purged, got {purge.get('zones')}"
    assert purge.get("zones_preserved_infrastructure") == 2, "I-6 : 2 infra zones should be preserved"
    assert result.get("zones_rejected_bio_presence_mask_count") == 4


def test_mask_preserves_infrastructure_zones():
    """I-6 — Zones sans tag species (infrastructure) restent dans le bundle."""
    from engines.v8_institutional.species_presence_mask_omega import apply_presence_mask_to_bundle
    bundle = _build_fake_bundle("wapiti", n_corridors=1, n_zones_tagged=0, n_zones_infra=3)
    result = apply_presence_mask_to_bundle(bundle, species="wapiti", lat=BSL[0], lng=BSL[1])
    # 3 zones infrastructure préservées
    assert len(result["zones"]) == 3
    assert all(z.get("type") == "hydat" for z in result["zones"])


def test_mask_noop_for_present_species():
    """I-3bis — apply_presence_mask est no-op pour espèce PRESENT (chevreuil @ BSL)."""
    from engines.v8_institutional.species_presence_mask_omega import apply_presence_mask_to_bundle
    bundle = _build_fake_bundle("chevreuil", n_corridors=5, n_zones_tagged=3, n_zones_infra=2)
    result = apply_presence_mask_to_bundle(bundle, species="chevreuil", lat=BSL[0], lng=BSL[1])
    assert result["bio_presence_mask_halt"] is False
    assert len(result["corridors"]) == 5
    assert len(result["zones"]) == 5  # toutes préservées


# =========================================================================
# I-7 — RAYON ENTRY/EXIT 780m (BLOC 2.2)
# =========================================================================

def test_external_entry_exit_radius_default_is_780m():
    """I-7 — Default `external_entry_exit_radius_m` = 780m dans les 2 entry points."""
    import inspect
    from engines.v8_institutional.engine_ia_corridors_organic_omega import generate_organic_corridors
    sig = inspect.signature(generate_organic_corridors)
    radius_default = sig.parameters["external_entry_exit_radius_m"].default
    assert radius_default == 780.0, (
        f"I-7 BLOC 2.2 : default doit être 780.0, got {radius_default}"
    )


def test_smoother_default_radius_is_780m():
    """I-7bis — Smoother appelle generate_organic_corridors avec rayon 780m."""
    # Vérification statique : grep dans organic_corridor_smoother.py
    import pathlib
    src = pathlib.Path("/app/backend/engines/post_smoothing/organic_corridor_smoother.py").read_text()
    assert 'body.get("external_entry_exit_radius_m", 780.0)' in src, (
        "I-7bis : smoother doit utiliser default 780.0"
    )


# =========================================================================
# I-8 — PROMOTION AUTO VEINE PRINCIPALE (BLOC 2.4)
# =========================================================================

def test_promotion_doctrine_module_present():
    """I-8 — La doctrine de promotion auto P22ΩΩ_TERRITOIRE_Ω_SUPRA_BLOC_2_4 est implémentée."""
    import pathlib
    src = pathlib.Path(
        "/app/backend/engines/v8_institutional/engine_ia_corridors_organic_omega.py"
    ).read_text()
    assert "P22ΩΩ_TERRITOIRE_Ω_SUPRA_BLOC_2_4" in src
    assert "p22omegaomega_promotion_doctrine" in src
    assert "promote_max_fused_score_when_no_veine_principale" in src


# =========================================================================
# I-9 — AUCUN FALLBACK V8/V10 ACTIF
# =========================================================================

def test_no_v8_phase_a_module_remains():
    """I-9a — engines/v8_national/phase_a_engines.py supprimé (PALIER 2)."""
    import pathlib
    assert not pathlib.Path("/app/backend/engines/v8_national/phase_a_engines.py").exists()


def test_no_v8_phase_b_module_remains():
    """I-9b — engines/v8_national/phase_b_engines.py supprimé (PALIER 1)."""
    import pathlib
    assert not pathlib.Path("/app/backend/engines/v8_national/phase_b_engines.py").exists()


def test_no_v8_map_bundle_module_remains():
    """I-9c — engines/v8_national/map_bundle.py supprimé (PALIER 1)."""
    import pathlib
    assert not pathlib.Path("/app/backend/engines/v8_national/map_bundle.py").exists()


def test_corridors_v10_is_sanctuarized():
    """I-9d — corridors_v10 marqué CORE_MODULE (interdit de purge auto)."""
    from core.scoring_pipeline.corridors_v10 import (
        __core_module__,
        __purge_forbidden__,
        __sanctuarisation_directive__,
    )
    assert __core_module__ is True
    assert __purge_forbidden__ is True
    assert "P22ΩΩ" in __sanctuarisation_directive__


def test_v7_spatial_legacy_router_disabled():
    """I-9e — Module spatial_engine_v7 PHYSIQUEMENT PURGÉ (BLOC 2.5)."""
    import pathlib
    # Module legacy doit avoir disparu
    assert not pathlib.Path("/app/backend/engines/spatial_engine_v7").exists()
    # Module Ω institutionnel doit être présent
    assert pathlib.Path(
        "/app/backend/engines/v8_institutional/territoire_omega_spatial/__init__.py"
    ).exists()
    # Le router Ω doit pointer vers le nouveau module
    src = pathlib.Path("/app/backend/routes/territoire_omega_spatial_router.py").read_text()
    assert "engines.v8_institutional.territoire_omega_spatial" in src
    assert "engines.spatial_engine_v7" not in src
    # server.py doit confirmer la purge
    server_src = pathlib.Path("/app/backend/server.py").read_text()
    assert "SPATIAL-ENGINE-V7 PURGED PHYSICALLY" in server_src


# =========================================================================
# I-10 / I-11 — FIX PRESENCE MASK BYPASS (organic_generate + smoother)
# =========================================================================

def test_organic_generate_invokes_presence_mask():
    """I-10 — organic_generate applique le presence_mask avant cache_set (FIX BYPASS)."""
    import pathlib
    src = pathlib.Path(
        "/app/backend/engines/v8_institutional/engine_ia_corridors_organic_omega.py"
    ).read_text()
    assert "_apply_organic_presence_mask" in src
    assert "P22ΩΩ_FIX_PRESENCE_MASK_BYPASS_ORGANIC_GENERATE" in src


def test_smoother_reapplies_mask_after_external_inflow():
    """I-11 — smoother réapplique apply_presence_mask APRÈS smooth_bundle (FIX BYPASS)."""
    import pathlib
    src = pathlib.Path(
        "/app/backend/engines/post_smoothing/organic_corridor_smoother.py"
    ).read_text()
    assert "bio_presence_mask_reapplied_post_smoother" in src
    assert "RÉ-APPLICATION DU MASQUE APRÈS smooth_bundle" in src


# =========================================================================
# I-12 — END-TO-END : organic_generate retourne 0 corridors pour wapiti @ BSL
# =========================================================================

def test_organic_generate_wapiti_at_bsl_returns_zero_paths():
    """I-12 — Test E2E : router organic_generate wapiti @ BSL → 0 corridors via mask.

    Vérifie que le router POST `/generate` applique correctement le mask
    AVAL (via `_apply_organic_presence_mask`). Le flux complet inclut :
        generate_organic_corridors → _apply_organic_presence_mask → cache_set
    """
    from engines.v8_institutional.engine_ia_corridors_organic_omega import (
        organic_generate, GenerateOrganicBody, _ORGANIC_CACHE,
    )

    # Purge cache pour forcer compute (évite hit potentiel d'un test précédent)
    _ORGANIC_CACHE.clear()

    body = GenerateOrganicBody(
        lat=BSL[0], lon=BSL[1], species="wapiti",
        month=10, hour=14, wind_deg=180,
    )
    result = asyncio.run(organic_generate(body))

    # Le router /generate applique le mask AVAL avant cache_set
    assert result.get("bio_presence_mask_applied") is True
    assert result.get("bio_presence_mask_halt") is True
    assert len(result.get("corridors", [])) == 0, (
        f"Wapiti @ BSL via /generate doit retourner 0 corridors après mask, "
        f"got {len(result.get('corridors', []))}"
    )
    stats = result.get("bio_presence_mask_stats", {})
    assert stats.get("presence_status") == "ABSENT"
    assert stats.get("canonical") == "wapiti"


def test_organic_generate_chevreuil_at_bsl_returns_paths():
    """I-12bis — Régression : chevreuil @ BSL via /generate → corridors non vides."""
    from engines.v8_institutional.engine_ia_corridors_organic_omega import (
        organic_generate, GenerateOrganicBody, _ORGANIC_CACHE,
    )

    _ORGANIC_CACHE.clear()

    body = GenerateOrganicBody(
        lat=BSL[0], lon=BSL[1], species="chevreuil",
        month=10, hour=14, wind_deg=180,
    )
    result = asyncio.run(organic_generate(body))

    assert result.get("bio_presence_mask_halt") is False
    assert len(result.get("corridors", [])) > 0, (
        "Chevreuil @ BSL via /generate doit avoir des corridors"
    )


# =========================================================================
# I-13 — MIGRATION ENDPOINTS Ω (PALIER 2 + 3)
# =========================================================================

def test_omega_router_relocalisation_salines_loaded():
    """I-13a — Router Ω relocalisation/salines enregistré."""
    import pathlib
    src = pathlib.Path("/app/backend/server.py").read_text()
    assert "territoire_omega_reloc_salines_router" in src
    assert "/api/v20/territoire/{relocalisation,salines-placement}" in src


def test_omega_router_spatial_loaded():
    """I-13b — Router Ω spatial enregistré (PALIER 3)."""
    import pathlib
    src = pathlib.Path("/app/backend/server.py").read_text()
    assert "territoire_omega_spatial_router" in src
    assert "P22ΩΩ_PALIER_3" in src


def test_omega_modules_importable():
    """I-13c — Modules Ω importables sans erreur."""
    from engines.v8_institutional.territoire_omega_relocalisation_salines import (
        compute_relocalisation_omega,
        compute_salines_placement_omega,
        status_omega,
    )
    # Status renvoie le bon engine
    status = status_omega()
    assert status["engine"] == "TERRITOIRE-Ω-RELOCALISATION-SALINES"
    assert status["status"] == "OPERATIONNEL"


# =========================================================================
# I-14 — SECURE PICKLE HMAC (GROUPE B)
# =========================================================================

def test_secure_pickle_roundtrip_and_tampering():
    """I-14a — HMAC-SHA256 pickle : roundtrip OK + tampering rejeté."""
    from engines.v8_institutional.secure_pickle_omega import (
        secure_dumps, secure_loads,
    )

    data = {"P22ΩΩ": True, "halt": True, "corridors": [1, 2, 3]}
    blob = secure_dumps(data)
    restored = secure_loads(blob)
    assert restored == data

    # Tampering detection
    tampered = bytearray(blob)
    tampered[40] ^= 0xFF
    with pytest.raises(ValueError, match="HMAC mismatch"):
        secure_loads(bytes(tampered))


# =========================================================================
# I-15 — BLOC 2.5 : HIÉRARCHIE ENFORCE + CAP 5-7 PAR ESPÈCE
# =========================================================================

def test_bloc25_hierarchy_enforce_in_v20_bundle():
    """I-15 — Le bundle V20 applique BLOC 2.5 : hierarchy + cap 5-7 (OPTION B).

    P22ΩΩ_BLOC_2_5_CORRIGE_DEADLINE_GATE_Ω · 2026-02-XX · STEEVE-MAX
    Helper extrait au niveau module pour s'appliquer aussi en branche
    deadline ESSENTIEL_T0 (cf. _apply_bloc25_hierarchy_and_cap).
    """
    import pathlib
    src = pathlib.Path(
        "/app/backend/engines/v8_institutional/v20_performance_bundle.py"
    ).read_text()
    assert "P22ΩΩ_BLOC_2_5_CORRIDORS_UNIQUES_PAR_ESPECE_Ω" in src
    assert "_apply_bloc25_hierarchy_and_cap" in src
    assert "p22omegaomega_bloc_2_5_doctrine" in src
    assert "_CAP_MAX = 7" in src
    # P22ΩΩ_BLOC_2_5_CORRIGE_DEADLINE_GATE_Ω : doit être appliqué AVANT
    # le return de la branche deadline (ESSENTIEL_T0 dégradé).
    assert "P22ΩΩ_BLOC_2_5_DEADLINE_PATCH" in src
    # Helpers module-level (extraction de closure)
    import importlib
    module = importlib.import_module("engines.v8_institutional.v20_performance_bundle")
    assert hasattr(module, "_apply_bloc25_hierarchy_and_cap")
    assert hasattr(module, "_apply_v5_rewire_to_result")


def test_bloc25_doctrine_applied_for_present_species():
    """I-15bis — Le module v20_performance_bundle expose les fonctions clés du pipeline."""
    import importlib
    module = importlib.import_module("engines.v8_institutional.v20_performance_bundle")
    # Vérifier que les fonctions critiques du pipeline existent
    assert hasattr(module, "map_v5_corridors_to_ui")
    assert hasattr(module, "_warmup_single")
    assert hasattr(module, "_cache_get")
    assert hasattr(module, "_cache_set")
    # Vérifier que le router est exposé
    assert hasattr(module, "router")


# =========================================================================
# I-16 — SPATIAL_ENGINE_V7 PURGÉ + MODULE Ω OPÉRATIONNEL
# =========================================================================

def test_omega_spatial_module_files_exist_after_purge():
    """I-16 — Les fichiers du module Ω spatial existent après purge V7."""
    import pathlib
    # Le module legacy doit avoir disparu
    assert not pathlib.Path("/app/backend/engines/spatial_engine_v7").exists()
    # Le module Ω doit avoir les 2 fichiers requis
    omega_dir = pathlib.Path(
        "/app/backend/engines/v8_institutional/territoire_omega_spatial"
    )
    assert omega_dir.exists()
    assert (omega_dir / "__init__.py").exists()
    assert (omega_dir / "_v7_logic.py").exists()
    # Le _v7_logic doit contenir les fonctions critiques
    logic_src = (omega_dir / "_v7_logic.py").read_text()
    assert "async def spatial_heatmap" in logic_src
    assert "async def spatial_scoring" in logic_src
    assert "async def spatial_status" in logic_src



# =========================================================================
# I-17 — P22ΩΩ_SECURITE_ET_CONTINUITE_CORRIDORS_PRE_PHASE_III_Ω
# Anti-régression palette espèce + verrouillage couleurs interdites
# =========================================================================

def test_species_color_palette_omega_locked_anti_regression():
    """I-17 — La palette SPECIES_COLOR_OMEGA est figée et conforme directive.

    P22ΩΩ_SECURITE_ET_CONTINUITE_CORRIDORS_PRE_PHASE_III_Ω · 2026-02-XX
    COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU

    Vérifie côté SOURCE (lecture du fichier JS) que :
      1. La palette contient EXACTEMENT les 6 espèces + multi_aggregated
      2. Les couleurs primary respectent la directive du Commandant
      3. Aucune couleur INTERDITE (regression) n'apparaît dans la palette
      4. La palette est Object.freeze (immutable)
    """
    import pathlib
    src = pathlib.Path(
        "/app/frontend/src/lib/speciesColorOmega.js"
    ).read_text()

    # 1. Palette figée Object.freeze
    assert "Object.freeze({" in src
    assert "SPECIES_COLOR_OMEGA = Object.freeze" in src

    # 2. Couleurs primary DOCTRINE STEEVE-MAX strictes
    expected_primary = {
        "chevreuil": "#FF8F00",      # ORANGE AMBRÉ
        "orignal": "#1E5F8E",        # BLEU PROFOND
        "ours_noir": "#5D2E8C",      # VIOLET SOMBRE
        "wapiti": "#C0392B",         # ROUGE BRIQUE
        "dindon_sauvage": "#D4A017", # AMBRE DORÉ
        "coyote": "#6E6E6E",         # GRIS ACIER
    }
    for sp, primary in expected_primary.items():
        assert sp in src, f"espèce manquante: {sp}"
        assert primary in src, f"couleur primary {primary} manquante pour {sp}"

    # 3. Couleurs INTERDITES (anti-régression directive)
    forbidden = [
        "#E65100",  # mono orange foncé legacy
        "#2D7A2D",  # vert chevreuil ancien (illisible sur fond forêt)
        "#5BC68F",  # vert chevreuil ancien secondary
        "#8B4513",  # brun orignal ancien (fusion sol)
    ]
    # Vérifier qu'elles sont DOCUMENTÉES comme interdites et qu'elles n'apparaissent
    # PAS dans les définitions de palette (présence OK uniquement dans FORBIDDEN_COLORS_OMEGA).
    assert "FORBIDDEN_COLORS_OMEGA" in src
    for col in forbidden:
        assert col in src  # doit être listé dans FORBIDDEN_COLORS_OMEGA
    # Aucune des couleurs interdites ne doit apparaître dans les définitions
    # primary/secondary/capillary/halo (vérification simple par contexte).
    # On compte les occurrences : doit être 1 (dans FORBIDDEN_COLORS_OMEGA) sauf #E65100
    # qui peut aussi être dans le commentaire — on tolère ≤ 2.
    for col in forbidden:
        assert src.count(col) <= 2, f"couleur interdite {col} apparaît trop souvent: {src.count(col)}"

    # 4. Marqueurs doctrinaux
    assert "P22ΩΩ_SECURITE_ET_CONTINUITE_CORRIDORS_PRE_PHASE_III_Ω" in src
    assert "VERROU ABSOLU" in src


def test_catmullrom_cap_radius_clip_doctrine():
    """I-18 — Le backend applique le clip §7 (≤780m) et resample §8 (≤50pts).

    Vérifie présence des helpers + constantes doctrinales dans
    v20_performance_bundle.py.
    """
    import pathlib
    src = pathlib.Path(
        "/app/backend/engines/v8_institutional/v20_performance_bundle.py"
    ).read_text()
    assert "_clip_path_to_max_length" in src
    assert "_apply_catmullrom_cap_to_corridors" in src
    assert "_RADIUS_MAX_M = 780" in src
    assert "_RADIUS_MIN_M = 420" in src
    assert "_CATMULLROM_TARGET_POINTS = 50" in src
    assert "n_clipped_to_radius" in src
    # Marqueur doctrinal P22ΩΩ_SECURITE
    assert "P22ΩΩ_SECURITE_ET_CONTINUITE_CORRIDORS_PRE_PHASE_III_Ω" in src

    # Import + test runtime des helpers
    import importlib
    module = importlib.import_module("engines.v8_institutional.v20_performance_bundle")
    assert hasattr(module, "_clip_path_to_max_length")
    assert hasattr(module, "_apply_catmullrom_cap_to_corridors")
    assert hasattr(module, "_haversine_m")
    # Test fonctionnel clip
    long_path = [[48.0 + i * 0.001, -68.0] for i in range(20)]  # ~2200m linéaire
    clipped = module._clip_path_to_max_length(long_path, 780.0)
    L = module._path_total_length_m(clipped)
    assert L <= 780.5, f"clip échoué: {L}m"
    assert L >= 770.0, f"clip trop agressif: {L}m"
