"""
CORRIDORS_FUSION_VEINEUSE_OMEGA · P22Σ_V3_TERRITORY_CONTINUOUS_FUSION_VEINEUSE_Ω
═══════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT

Module de FUSION VEINEUSE LOCALE pour les corridors organic.

DOCTRINE :
  - Pour une MÊME espèce, tout corridor à ≤15-20m d'un autre est fusionné
  - La fusion crée une veine principale unique (path moyen pondéré)
  - Les corridors secondaires trop proches sont absorbés
  - L'intensité reflète le recouvrement réel (densité × fusion_count)
  - +1 niveau d'intensité par corridor fusionné, max niveau 4 (EXTRÊME)

V30_LOCK INVIOLÉ · FUSION ADD-ONLY · NEW MODULE
═══════════════════════════════════════════════════════════════════════
"""

from __future__ import annotations
import math
from typing import Any


FUSION_DISTANCE_M = 18.0  # ≤15-20m doctrinal (point milieu retenu)
FUSION_OVERLAP_RATIO_MIN = 0.30  # ≥30% des points proches pour considérer fusion


def _haversine_m(p1: list, p2: list) -> float:
    if not p1 or not p2 or len(p1) < 2 or len(p2) < 2:
        return 1e9
    lat1, lon1 = float(p1[0]), float(p1[1])
    lat2, lon2 = float(p2[0]), float(p2[1])
    R = 6371000.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
         * math.sin(dlon / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(a))


def _path_overlap_ratio(path_a: list, path_b: list,
                         max_dist_m: float = FUSION_DISTANCE_M) -> float:
    """Calcule le ratio de points de path_a à ≤max_dist_m de n'importe quel
    point de path_b. Retourne 0..1.
    """
    if not path_a or not path_b:
        return 0.0
    n_close = 0
    for pa in path_a:
        for pb in path_b:
            if _haversine_m(pa, pb) <= max_dist_m:
                n_close += 1
                break  # un seul match suffit pour le point pa
    return n_close / max(1, len(path_a))


def _path_average(paths: list[list]) -> list:
    """Moyenne géométrique pondérée de plusieurs paths.

    Aligne les paths sur un nombre de points commun (resampling à 28 pts) puis
    calcule la moyenne arithmétique de chaque vertex.
    """
    if not paths:
        return []
    if len(paths) == 1:
        return paths[0]
    target_n = 28  # cohérent avec controlPointsTarget RENDU-Ω
    resampled = []
    for path in paths:
        if not path or len(path) < 2:
            continue
        if len(path) == target_n:
            resampled.append(path)
            continue
        # resampling linéaire simple
        new_path = []
        n_orig = len(path)
        for i in range(target_n):
            t = i / (target_n - 1)
            idx_f = t * (n_orig - 1)
            idx_lo = int(math.floor(idx_f))
            idx_hi = min(idx_lo + 1, n_orig - 1)
            frac = idx_f - idx_lo
            lat = path[idx_lo][0] * (1 - frac) + path[idx_hi][0] * frac
            lon = path[idx_lo][1] * (1 - frac) + path[idx_hi][1] * frac
            new_path.append([lat, lon])
        resampled.append(new_path)

    if not resampled:
        return paths[0]

    # Moyenne arithmétique
    avg = []
    n_paths = len(resampled)
    for i in range(target_n):
        lat_sum = sum(p[i][0] for p in resampled)
        lon_sum = sum(p[i][1] for p in resampled)
        avg.append([lat_sum / n_paths, lon_sum / n_paths])
    return avg


def fuse_corridors_by_species(corridors: list[dict],
                               fusion_distance_m: float = FUSION_DISTANCE_M,
                               overlap_ratio_min: float = FUSION_OVERLAP_RATIO_MIN,
                               ) -> list[dict]:
    """Fusionne les corridors d'une même espèce en veines principales.

    Algorithm union-find : pour chaque paire (i, j) où overlap_ratio ≥ min,
    on fusionne les deux corridors.

    Output enrichi par corridor :
      - id : conservé pour le 1er corridor du cluster
      - merged_ids : liste des IDs absorbés
      - fusion_count : nombre total de corridors fusionnés (≥1)
      - intensity_level : 0-4 (FAIBLE → EXTRÊME) selon fusion_count
      - path : path moyen pondéré du cluster
      - hierarchy : promu en 'veine_principale' si fusion_count ≥ 2
    """
    if not corridors or len(corridors) < 2:
        # Pas de fusion possible — retourne tel quel avec intensity_level basé sur hier
        return [_enrich_intensity(c, fusion_count=1) for c in corridors]

    # Filtre : ne traiter que les corridors avec un path valide ≥ 2 points
    valid_corridors = [c for c in corridors
                        if isinstance(c.get("path"), list) and len(c["path"]) >= 2]
    n = len(valid_corridors)
    if n < 2:
        return [_enrich_intensity(c, fusion_count=1) for c in corridors]

    # Union-Find
    parent = list(range(n))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def union(x, y):
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[rx] = ry

    # Détection des paires fusionnables
    for i in range(n):
        for j in range(i + 1, n):
            ratio_ij = _path_overlap_ratio(
                valid_corridors[i]["path"], valid_corridors[j]["path"],
                fusion_distance_m,
            )
            if ratio_ij >= overlap_ratio_min:
                union(i, j)

    # Regroupement par cluster
    clusters: dict[int, list[int]] = {}
    for i in range(n):
        root = find(i)
        clusters.setdefault(root, []).append(i)

    # Construction des veines fusionnées
    fused: list[dict] = []
    for root, idxs in clusters.items():
        if len(idxs) == 1:
            # Pas de fusion — intensity 0/1 selon hier original
            c = valid_corridors[idxs[0]]
            fused.append(_enrich_intensity(c, fusion_count=1))
            continue

        # Fusion réelle
        members = [valid_corridors[i] for i in idxs]
        fusion_count = len(members)
        merged_ids = [m.get("id") for m in members[1:]]
        primary = dict(members[0])  # copie shallow
        primary["path"] = _path_average([m["path"] for m in members])
        primary["merged_ids"] = merged_ids
        primary["fusion_count"] = fusion_count
        primary["hierarchy"] = "veine_principale" if fusion_count >= 2 else primary.get("hierarchy")
        primary["fusion_doctrine"] = "P22Σ_V3_FUSION_VEINEUSE"
        # Intensity level renforcée par recouvrement
        primary = _enrich_intensity(primary, fusion_count=fusion_count)
        fused.append(primary)

    # Ajout des corridors invalides (sans path) tels quels
    invalid_corridors = [c for c in corridors
                         if not (isinstance(c.get("path"), list) and len(c.get("path", [])) >= 2)]
    fused.extend(_enrich_intensity(c, fusion_count=1) for c in invalid_corridors)

    return fused


def _enrich_intensity(corridor: dict, fusion_count: int = 1) -> dict:
    """Calcule et attache `intensity_level` (0-4) selon fusion_count + hierarchy.

    Doctrine :
      - fusion_count = 1 et hier=capillaire   → niveau 0 FAIBLE
      - fusion_count = 1 et hier=secondaire   → niveau 1 MODÉRÉ
      - fusion_count = 1 et hier=principale   → niveau 2 MOYEN
      - fusion_count = 2-3                    → niveau 3 ÉLEVÉ
      - fusion_count ≥ 4                      → niveau 4 EXTRÊME
    """
    enriched = dict(corridor)
    hier = (enriched.get("hierarchy") or "").lower()

    if fusion_count >= 4:
        level = 4
    elif fusion_count >= 2:
        level = 3
    elif "principale" in hier:
        level = 2
    elif "secondaire" in hier:
        level = 1
    else:
        level = 0

    enriched["intensity_level"] = level
    enriched["intensity_label"] = ["FAIBLE", "MODÉRÉ", "MOYEN", "ÉLEVÉ", "EXTRÊME"][level]
    enriched.setdefault("fusion_count", fusion_count)
    return enriched


def fusion_summary(corridors_after_fusion: list[dict]) -> dict[str, Any]:
    """Synthèse de la fusion appliquée."""
    n_fused = sum(1 for c in corridors_after_fusion
                  if (c.get("fusion_count") or 1) >= 2)
    n_intensity = {f"level_{i}": 0 for i in range(5)}
    for c in corridors_after_fusion:
        lvl = c.get("intensity_level", 0)
        n_intensity[f"level_{lvl}"] += 1
    total_absorbed = sum((c.get("fusion_count") or 1) - 1
                         for c in corridors_after_fusion)
    return {
        "n_corridors_after_fusion": len(corridors_after_fusion),
        "n_fused_clusters": n_fused,
        "n_corridors_absorbed": total_absorbed,
        "intensity_distribution": n_intensity,
        "fusion_distance_m": FUSION_DISTANCE_M,
        "overlap_ratio_min": FUSION_OVERLAP_RATIO_MIN,
        "doctrine": "P22Σ_V3_FUSION_VEINEUSE_Ω",
    }
