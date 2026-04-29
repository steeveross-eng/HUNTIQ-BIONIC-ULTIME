"""
BDRE — Source Selector (F4)
BCE-4X GOLDEN V6+ | Phase 3
Selection dynamique de la meilleure source selon le score BDRE.
Hook interne — pas d'endpoint API.
"""
import logging

logger = logging.getLogger("bionic.bdre.source_selector")


class SourceSelector:
    """
    Selectionne la meilleure source disponible pour une requete terrain.
    Utilise les scores du registre pour determiner la strategie.
    """

    def __init__(self, registry, scorer):
        self._registry = registry
        self._scorer = scorer

    def select_best_source(self, required_category: str = "trails") -> dict:
        """
        Selectionner la meilleure source pour une categorie donnee.

        Args:
            required_category: "trails", "obstacles", "elevation", etc.

        Returns:
            {
                "source_id": str,
                "score": float,
                "status": str,
                "strategy": "primary" | "fallback_level_N",
            }
        """
        from .source_registry import EXTERNAL_SOURCES

        candidates = []
        for src_id, src_def in EXTERNAL_SOURCES.items():
            if src_def.get("category") == required_category:
                health = self._registry.get_health(src_id)
                if health["status"] not in ("down", "not_connected"):
                    candidates.append({
                        "source_id": src_id,
                        "score": health["score"],
                        "status": health["status"],
                    })

        if not candidates:
            return {
                "source_id": "NONE",
                "score": 0.0,
                "status": "no_source_available",
                "strategy": "fallback_level_4",
            }

        # Trier par score decroissant
        candidates.sort(key=lambda c: c["score"], reverse=True)
        best = candidates[0]

        if best["score"] >= 0.60:
            strategy = "primary"
        elif best["score"] >= 0.40:
            strategy = "fallback_level_1"
        elif best["score"] >= 0.20:
            strategy = "fallback_level_2"
        else:
            strategy = "fallback_level_3"

        best["strategy"] = strategy
        logger.info(
            f"[BDRE-SELECT] Best source for '{required_category}': "
            f"{best['source_id']} score={best['score']:.3f} strategy={strategy}"
        )
        return best
