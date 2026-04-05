"""
BDRE — Quality Scorer (F2)
BCE-4X GOLDEN V6+ | Phase 1
Scoring de fiabilite des sources: couverture, fraicheur, precision, completude, coherence.
Formule: SCORE = COV*0.30 + FRA*0.15 + PRE*0.25 + COM*0.20 + COH*0.10
"""
import logging
import time
from typing import Dict, Optional

logger = logging.getLogger("bionic.bdre.scorer")

# Poids BCE-4X
WEIGHTS = {
    "coverage": 0.30,
    "freshness": 0.15,
    "precision": 0.25,
    "completeness": 0.20,
    "coherence": 0.10,
}

# Seuils de decision
THRESHOLDS = {
    "fiable": 0.80,
    "acceptable": 0.60,
    "degrade": 0.40,
    "deficient": 0.20,
}


def _classify(score: float) -> str:
    """Classifier un score selon les seuils BCE-4X."""
    if score >= THRESHOLDS["fiable"]:
        return "FIABLE"
    elif score >= THRESHOLDS["acceptable"]:
        return "ACCEPTABLE"
    elif score >= THRESHOLDS["degrade"]:
        return "DEGRADE"
    elif score >= THRESHOLDS["deficient"]:
        return "DEFICIENT"
    return "INUTILISABLE"


def _fallback_level(score: float) -> int:
    """Determiner le niveau de fallback requis."""
    if score >= THRESHOLDS["acceptable"]:
        return 0
    elif score >= THRESHOLDS["degrade"]:
        return 1
    elif score >= THRESHOLDS["deficient"]:
        return 2
    elif score > 0.0:
        return 3
    return 4


class QualityScorer:
    """
    Scoring multi-criteres des sources de donnees.
    Produit un DataQualityContract (DC-BDRE-02) pour chaque evaluation.
    """

    def __init__(self, registry):
        self._registry = registry
        self._last_scores: Dict[str, dict] = {}

    def score_response(self, source_id: str, data: dict, expected_coverage: float = 0.5) -> dict:
        """
        Scorer la reponse d'une source apres reception.

        Pour les donnees terrain (trails, waterways, etc.):
        - coverage: ratio noeuds trouves / noeuds attendus
        - freshness: age du cache vs TTL
        - precision: types de donnees diversifies
        - completeness: presence de toutes les categories attendues
        - coherence: graphe connexe, pas de contradictions
        """
        metrics = self._compute_metrics(source_id, data, expected_coverage)
        score = (
            metrics["coverage"] * WEIGHTS["coverage"]
            + metrics["freshness"] * WEIGHTS["freshness"]
            + metrics["precision"] * WEIGHTS["precision"]
            + metrics["completeness"] * WEIGHTS["completeness"]
            + metrics["coherence"] * WEIGHTS["coherence"]
        )
        score = round(score, 4)

        classification = _classify(score)
        fallback = _fallback_level(score)

        result = {
            "source_id": source_id,
            "coverage": metrics["coverage"],
            "freshness": metrics["freshness"],
            "precision": metrics["precision"],
            "completeness": metrics["completeness"],
            "coherence": metrics["coherence"],
            "score": score,
            "classification": classification,
            "fallback_level": fallback,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

        self._last_scores[source_id] = result
        self._registry.update_score(source_id, score)

        logger.info(
            f"[BDRE-SCORER] {source_id}: score={score:.3f} "
            f"({classification}), fallback_level={fallback}"
        )

        return result

    def _compute_metrics(self, source_id: str, data: dict, expected_coverage: float) -> dict:
        """Calculer les 5 metriques pour une reponse."""

        # Terrain data scoring (trails, waterways, etc.)
        if "trails" in data or "has_trails" in data:
            return self._score_terrain_data(data, expected_coverage)

        # Generic data scoring
        return self._score_generic(data)

    def _score_terrain_data(self, data: dict, expected_coverage: float) -> dict:
        """Scorer les donnees terrain specifiquement."""

        # Coverage: nombre de ways trail / attendu
        trails = data.get("trails", {})
        trail_ways = trails.get("ways", [])
        trail_nodes = trails.get("node_coords", {})

        # Nombre de noeuds de sentiers
        n_trail_nodes = len(trail_nodes) if isinstance(trail_nodes, dict) else 0
        n_trail_ways = len(trail_ways)

        # Coverage basee sur le nombre de ways
        expected_ways = max(1, int(expected_coverage * 50))
        coverage = min(1.0, n_trail_ways / expected_ways)

        # Freshness: toujours 1.0 pour des donnees fraiches
        source = data.get("source", "unknown")
        if source in ("cache", "persistent_cache", "overpass"):
            freshness = 1.0
        else:
            freshness = 0.5

        # Precision: diversite des types de highway
        highway_types = set()
        for way in trail_ways:
            tags = way.get("tags", {})
            hw = tags.get("highway", "")
            if hw:
                highway_types.add(hw)
        # Plus de types = plus precis
        precision = min(1.0, len(highway_types) / 5.0) if highway_types else 0.0

        # Completeness: presence des categories essentielles
        categories_present = 0
        for cat in ("has_trails", "has_obstacles", "has_forest", "has_waterways", "has_clearings"):
            if data.get(cat, False):
                categories_present += 1
        completeness = categories_present / 5.0

        # Coherence: pas de noeuds orphelins, graphe structurellement sain
        if n_trail_ways > 0 and n_trail_nodes > 0:
            avg_nodes_per_way = n_trail_nodes / n_trail_ways
            coherence = min(1.0, avg_nodes_per_way / 10.0)
        elif n_trail_nodes == 0 and n_trail_ways == 0:
            coherence = 1.0  # Vide mais coherent
        else:
            coherence = 0.5

        return {
            "coverage": round(coverage, 4),
            "freshness": round(freshness, 4),
            "precision": round(precision, 4),
            "completeness": round(completeness, 4),
            "coherence": round(coherence, 4),
        }

    def _score_generic(self, data: dict) -> dict:
        """Scoring generique pour donnees non-terrain."""
        has_data = bool(data) and len(data) > 0
        return {
            "coverage": 1.0 if has_data else 0.0,
            "freshness": 1.0,
            "precision": 0.8 if has_data else 0.0,
            "completeness": 1.0 if has_data else 0.0,
            "coherence": 1.0,
        }

    def get_last_score(self, source_id: str) -> Optional[dict]:
        """Obtenir le dernier score pour une source."""
        return self._last_scores.get(source_id)

    def get_quality_report(self) -> dict:
        """Rapport qualite global de toutes les sources scorees."""
        sources = []
        total_score = 0.0
        count = 0

        for src_id, score_data in self._last_scores.items():
            sources.append(score_data)
            total_score += score_data["score"]
            count += 1

        avg = round(total_score / count, 4) if count > 0 else 0.0

        return {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "sources_scored": count,
            "average_score": avg,
            "global_classification": _classify(avg),
            "sources": sources,
        }
