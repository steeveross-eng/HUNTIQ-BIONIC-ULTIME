"""
BDRE — Waterway Classifier (DS-8 Resolution)
BCE-4X GOLDEN V6+ | Phase 1
Classification hydrologique BDRE.

Resout la contradiction DS-8:
- AVANT: Tous les waterways = obstacles (cout 999.0)
- APRES: stream/ditch/drain = corridors navigables (berges cout 1.2)
         water/wetland = obstacles (cout 999.0/50.0)
         river/canal = obstacles au centre, corridors sur berges
"""
import logging
from typing import Dict

logger = logging.getLogger("bionic.bdre.waterway")


# Classification hydrologique BCE-4X
WATERWAY_CLASSIFICATION = {
    # Corridors navigables (berges praticables)
    "stream": {"class": "corridor", "cost": 1.2, "label": "stream_bank"},
    "ditch": {"class": "corridor", "cost": 1.0, "label": "ditch_path"},
    "drain": {"class": "corridor", "cost": 1.0, "label": "drain_path"},
    # Obstacles avec berges navigables
    "river": {"class": "mixed", "cost_center": 999.0, "cost_bank": 1.2, "label": "river_bank"},
    "canal": {"class": "mixed", "cost_center": 999.0, "cost_bank": 1.2, "label": "canal_bank"},
    # Obstacles purs
    "riverbank": {"class": "obstacle", "cost": 999.0, "label": "water_body"},
}

NATURAL_CLASSIFICATION = {
    "water": {"class": "obstacle", "cost": 999.0, "label": "water_body"},
    "wetland": {"class": "obstacle", "cost": 50.0, "label": "wetland"},
}


class WaterwayClassifier:
    """
    Classifie les elements hydrologiques selon le protocole BDRE DS-8.
    Differentie corridors navigables (berges) et obstacles (eau).
    """

    def classify(self, tags: Dict[str, str]) -> dict:
        """
        Classifier un element OSM selon ses tags.

        Args:
            tags: Tags OSM de l'element (ex: {"waterway": "stream"})

        Returns:
            {
                "class": "corridor" | "obstacle" | "mixed" | "passable",
                "cost": float,
                "label": str,
                "is_obstacle": bool,
                "is_corridor": bool,
            }
        """
        natural = tags.get("natural", "")
        waterway = tags.get("waterway", "")

        # Priorite 1: natural=water/wetland = toujours obstacle
        if natural in NATURAL_CLASSIFICATION:
            info = NATURAL_CLASSIFICATION[natural]
            return {
                "class": info["class"],
                "cost": info["cost"],
                "label": info["label"],
                "is_obstacle": True,
                "is_corridor": False,
            }

        # Priorite 2: waterway type
        if waterway in WATERWAY_CLASSIFICATION:
            info = WATERWAY_CLASSIFICATION[waterway]
            wclass = info["class"]

            if wclass == "corridor":
                return {
                    "class": "corridor",
                    "cost": info["cost"],
                    "label": info["label"],
                    "is_obstacle": False,
                    "is_corridor": True,
                }
            elif wclass == "mixed":
                return {
                    "class": "mixed",
                    "cost": info["cost_bank"],
                    "cost_center": info["cost_center"],
                    "label": info["label"],
                    "is_obstacle": True,
                    "is_corridor": True,
                }
            else:
                return {
                    "class": "obstacle",
                    "cost": info["cost"],
                    "label": info["label"],
                    "is_obstacle": True,
                    "is_corridor": False,
                }

        # Waterway inconnu: traiter comme obstacle par precaution
        if waterway:
            return {
                "class": "obstacle",
                "cost": 999.0,
                "label": "unknown_waterway",
                "is_obstacle": True,
                "is_corridor": False,
            }

        # Pas un element hydrologique
        return {
            "class": "passable",
            "cost": 1.0,
            "label": "non_hydro",
            "is_obstacle": False,
            "is_corridor": False,
        }

    def is_navigable_waterway(self, tags: Dict[str, str]) -> bool:
        """Retourne True si l'element est un cours d'eau navigable (berges)."""
        result = self.classify(tags)
        return result["is_corridor"]

    def is_obstacle(self, tags: Dict[str, str]) -> bool:
        """Retourne True si l'element est un obstacle infranchissable."""
        result = self.classify(tags)
        return result["is_obstacle"] and not result["is_corridor"]
