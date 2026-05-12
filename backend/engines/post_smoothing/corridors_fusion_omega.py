"""
CORRIDORS_FUSION_VEINEUSE_OMEGA · P22Σ_V3_TERRITORY_CONTINUOUS_FUSION_VEINEUSE_Ω
═══════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT

Module de FUSION VEINEUSE LOCALE pour les corridors organic.

DOCTRINE V3 (initiale) :
  - Pour une MÊME espèce, tout corridor à ≤15-20m d'un autre est fusionné
  - La fusion crée une veine principale unique (path moyen pondéré)
  - Les corridors secondaires trop proches sont absorbés
  - L'intensité reflète le recouvrement réel (densité × fusion_count)
  - +1 niveau d'intensité par corridor fusionné, max niveau 4 (EXTRÊME)

DOCTRINE V4 — BACKBONE + SUBNETS (2026-05-12 · STEEVE-MAX) :
  - Conserve le backbone fusionné (clusters principaux)
  - Préserve 5-7 sous-corridors représentatifs par cluster (selon density)
  - Limite l'absorption à 60-70% (au lieu de 94%)
  - Granularité opérationnelle restaurée par zone fonctionnelle

V30_LOCK INVIOLÉ · FUSION ADD-ONLY · NEW MODULE
═══════════════════════════════════════════════════════════════════════
"""

from __future__ import annotations
import math
from typing import Any


FUSION_DISTANCE_M = 18.0  # ≤15-20m doctrinal (point milieu retenu)
# P22Σ_V4 · 2026-05-12 · ratio relevé à 0.50 pour générer plus de clusters distincts
# (chaque cluster ≈ une zone fonctionnelle : saline/eau/repos/refuge/rut)
# Avec 0.30 trop permissif → 1 méga-cluster ; avec 0.50 → plusieurs clusters distincts
FUSION_OVERLAP_RATIO_MIN = 0.50  # ≥50% des points proches pour considérer fusion

# P22Σ_V4 · BACKBONE+SUBNETS · 2026-05-12 · STEEVE-MAX
# Granularité opérationnelle : préserve les sous-corridors par cluster
SUBNET_MIN_PER_CLUSTER = 5             # min 5 corridors par cluster (sub + backbone)
SUBNET_MAX_PER_CLUSTER = 7             # max 7 corridors par cluster
MAX_ABSORPTION_RATIO = 0.70            # absorption max 70% (au lieu de 94%)

# P22Σ_V5 · CAP GLOBAL TERRITOIRE · 2026-05-12 · STEEVE-MAX
# Limite le nombre TOTAL de corridors sur l'ensemble du territoire (600m+30%)
# Ces caps s'appliquent APRÈS la fusion par cluster (V4 BACKBONE+SUBNETS).
CAP_MAX_BACKBONES = 2                  # max 2 backbones par territoire
CAP_MAX_SUBNETS = 5                    # max 5 subnets par territoire
CAP_MAX_TOTAL_CORRIDORS = 7            # cap global 5-7 corridors par territoire
CAP_DROP_ISOLATED_FIRST = True         # supprime isolés en priorité si dépassement
CAP_DROP_CONNECTORS_IF_OVER = True     # supprime connectors si total > cap


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
                               subnet_min: int = SUBNET_MIN_PER_CLUSTER,
                               subnet_max: int = SUBNET_MAX_PER_CLUSTER,
                               max_absorption_ratio: float = MAX_ABSORPTION_RATIO,
                               ) -> list[dict]:
    """Fusionne les corridors d'une même espèce en veines principales.

    DOCTRINE V4 — BACKBONE + SUBNETS :
      - Pour chaque cluster détecté, créer 1 backbone fusionné (veine_principale)
      - + préserver SUBNET_MIN..SUBNET_MAX sous-corridors représentatifs (veine_secondaire)
      - Absorption max plafonnée à MAX_ABSORPTION_RATIO (70%)

    Output enrichi par corridor :
      - id : conservé pour le 1er corridor du cluster
      - merged_ids : liste des IDs absorbés
      - fusion_count : nombre total de corridors fusionnés (≥1)
      - intensity_level : 0-4 (FAIBLE → EXTRÊME) selon fusion_count
      - path : path moyen pondéré du cluster (backbone) OU path original (subnet)
      - hierarchy :
          * 'veine_principale' = backbone fusionné (1 par cluster)
          * 'veine_secondaire' = sous-corridors préservés (5-7 par cluster)
          * 'capillaire' = corridors isolés (1 seul dans son cluster)
      - subnet_role : 'backbone' / 'subnet' / 'isolated' (V4)
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

    # ═══════════════════════════════════════════════════════════════════════
    # V4 · BACKBONE + SUBNETS : préserver 5-7 sous-corridors par cluster
    # ═══════════════════════════════════════════════════════════════════════
    fused: list[dict] = []
    for _root, idxs in clusters.items():
        if len(idxs) == 1:
            # Singleton — capillaire (pas de fusion possible)
            c = valid_corridors[idxs[0]]
            enriched = _enrich_intensity(c, fusion_count=1)
            enriched["subnet_role"] = "isolated"
            fused.append(enriched)
            continue

        # Cluster fusionnable
        members = [valid_corridors[i] for i in idxs]
        n_members = len(members)

        # Plafond d'absorption : on ne peut absorber qu'au plus MAX_ABSORPTION_RATIO du cluster
        # → max absorbed = floor(n_members * max_absorption_ratio)
        max_absorbed = max(1, int(math.floor(n_members * max_absorption_ratio)))
        # → n_subnets_to_preserve = n_members - 1 (backbone) - max_absorbed
        n_potential_subnets = max(0, n_members - 1 - max_absorbed)

        # On veut au moins subnet_min sous-corridors, au plus subnet_max
        n_subnets = min(subnet_max, max(subnet_min, n_potential_subnets))
        # Mais on ne peut pas avoir plus de subnets que de membres - 1 (le backbone)
        n_subnets = min(n_subnets, n_members - 1)
        # Si le cluster est trop petit pour atteindre subnet_min, garder tous les membres
        if n_members - 1 < subnet_min:
            n_subnets = n_members - 1  # tous les non-backbone deviennent subnets

        # ─── Sélection des subnets : tri par "représentativité" ───
        # Plus le score / intensité est élevé, plus le corridor est représentatif
        sorted_members = sorted(
            members,
            key=lambda c: float(c.get("intensity") or c.get("score") or 0),
            reverse=True,
        )

        # Backbone = membre #0 (top intensité), avec path moyen du cluster
        backbone_src = sorted_members[0]
        fusion_count = n_members - n_subnets  # cluster réellement absorbé dans backbone
        backbone = dict(backbone_src)
        # Path moyen pondéré : moyenne des paths des corridors absorbés (= cluster - subnets)
        absorbed_members = sorted_members[:fusion_count]
        backbone["path"] = _path_average([m["path"] for m in absorbed_members])
        backbone["merged_ids"] = [m.get("id") for m in absorbed_members[1:]]
        backbone["fusion_count"] = fusion_count
        backbone["hierarchy"] = "veine_principale"
        backbone["fusion_doctrine"] = "P22Σ_V4_BACKBONE_SUBNETS"
        backbone["subnet_role"] = "backbone"
        backbone["cluster_size"] = n_members
        backbone["cluster_subnets"] = n_subnets
        backbone = _enrich_intensity(backbone, fusion_count=fusion_count)
        fused.append(backbone)

        # Subnets : préserver les top-N suivants comme veines secondaires (intensité réduite)
        subnet_members = sorted_members[fusion_count: fusion_count + n_subnets]
        for sub_idx, sub_m in enumerate(subnet_members):
            sub = dict(sub_m)
            sub["hierarchy"] = "veine_secondaire"
            sub["fusion_doctrine"] = "P22Σ_V4_BACKBONE_SUBNETS"
            sub["subnet_role"] = "subnet"
            sub["fusion_count"] = 1
            sub["subnet_parent_id"] = backbone.get("id")
            sub["subnet_rank"] = sub_idx + 1
            sub = _enrich_intensity(sub, fusion_count=1)
            # Force intensity_level = 1 (MODÉRÉ) pour les subnets (sous le backbone niveau 3-4)
            sub["intensity_level"] = 1
            sub["intensity_label"] = "MODÉRÉ"
            fused.append(sub)

    # Ajout des corridors invalides (sans path) tels quels
    invalid_corridors = [c for c in corridors
                         if not (isinstance(c.get("path"), list) and len(c.get("path", [])) >= 2)]
    fused.extend(_enrich_intensity(c, fusion_count=1) for c in invalid_corridors)

    return fused


def cap_global_corridors(corridors: list[dict],
                         max_backbones: int = CAP_MAX_BACKBONES,
                         max_subnets: int = CAP_MAX_SUBNETS,
                         max_total: int = CAP_MAX_TOTAL_CORRIDORS,
                         drop_isolated_first: bool = CAP_DROP_ISOLATED_FIRST,
                         drop_connectors_if_over: bool = CAP_DROP_CONNECTORS_IF_OVER,
                         ) -> tuple[list[dict], dict]:
    """P22Σ_V5 · CAP GLOBAL TERRITOIRE (s'applique APRÈS fusion par cluster).

    Limite le nombre TOTAL de corridors retournés sur tout le territoire :
      - max 2 backbones (top intensité)
      - max 5 subnets (top intensité)
      - max 7 corridors au total
    Stratégie de drop :
      1. Drop les connectors en premier (si activé)
      2. Drop les isolés ensuite (si activé)
      3. Drop les subnets les moins intenses
      4. Drop les backbones excédentaires (rare)

    Returns
    -------
    (corridors_capped, cap_summary)
    """
    if not corridors:
        return corridors, {"applied": False, "reason": "empty"}

    # Tri par rôle pour gestion granulaire
    backbones = []
    subnets = []
    isolated = []
    connectors = []
    others = []  # corridors sans subnet_role (ex: legacy ou non fusionnés)
    for c in corridors:
        role = c.get("subnet_role")
        if c.get("type") == "connector":
            connectors.append(c)
        elif role == "backbone":
            backbones.append(c)
        elif role == "subnet":
            subnets.append(c)
        elif role == "isolated":
            isolated.append(c)
        else:
            others.append(c)

    # Tri par intensité décroissante au sein de chaque catégorie
    def intensity_key(c):
        return -(c.get("intensity_level", 0) * 100 + (c.get("intensity") or c.get("score") or 0))

    backbones.sort(key=intensity_key)
    subnets.sort(key=intensity_key)
    isolated.sort(key=intensity_key)
    others.sort(key=intensity_key)

    # Stats avant cap
    n_before = len(corridors)
    n_before_by_role = {
        "backbone": len(backbones), "subnet": len(subnets),
        "isolated": len(isolated), "connector": len(connectors),
        "other": len(others),
    }

    # Cap par catégorie
    backbones = backbones[:max_backbones]
    subnets = subnets[:max_subnets]

    # Compose le résultat ordonné par priorité doctrinale :
    #   backbone > subnet > other (corridors non fusionnés) > isolated > connector
    result = list(backbones) + list(subnets)

    # Si on n'a pas encore atteint max_total, ajouter les "others" (corridors organiques
    # non capturés par la fusion par cluster — typiquement plusieurs zones distinctes)
    remaining_slots = max_total - len(result)
    if remaining_slots > 0 and others:
        # Tri par intensité, on prend les meilleurs others
        result.extend(others[:remaining_slots])
        remaining_slots = max_total - len(result)

    # Reste-t-il de la place pour isolés / connectors ?
    if remaining_slots > 0 and isolated and not drop_isolated_first:
        result.extend(isolated[:remaining_slots])
        remaining_slots = max_total - len(result)
    if remaining_slots > 0 and connectors and not drop_connectors_if_over:
        result.extend(connectors[:remaining_slots])
        remaining_slots = max_total - len(result)

    # Sanity final : tronquer à max_total au cas où
    capped = result[:max_total]

    # Stats après cap
    n_after_by_role = {"backbone": 0, "subnet": 0, "isolated": 0, "connector": 0, "other": 0}
    for c in capped:
        role = c.get("subnet_role") or c.get("type") or "other"
        if role == "connector":
            n_after_by_role["connector"] += 1
        elif role in n_after_by_role:
            n_after_by_role[role] += 1
        else:
            n_after_by_role["other"] += 1

    cap_summary = {
        "applied": True,
        "doctrine": "P22Σ_V5_CAP_GLOBAL_TERRITOIRE",
        "max_backbones": max_backbones,
        "max_subnets": max_subnets,
        "max_total_corridors": max_total,
        "drop_isolated_first": drop_isolated_first,
        "drop_connectors_if_over": drop_connectors_if_over,
        "n_corridors_before_cap": n_before,
        "n_corridors_after_cap": len(capped),
        "before_by_role": n_before_by_role,
        "after_by_role": n_after_by_role,
        "dropped": n_before - len(capped),
    }
    return capped, cap_summary


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
    """Synthèse de la fusion appliquée (doctrine V4 BACKBONE+SUBNETS)."""
    n_fused = sum(1 for c in corridors_after_fusion
                  if (c.get("fusion_count") or 1) >= 2)
    n_intensity = {f"level_{i}": 0 for i in range(5)}
    for c in corridors_after_fusion:
        lvl = c.get("intensity_level", 0)
        n_intensity[f"level_{lvl}"] += 1
    total_absorbed = sum((c.get("fusion_count") or 1) - 1
                         for c in corridors_after_fusion)

    # P22Σ_V4 — Stats BACKBONE+SUBNETS
    n_backbone = sum(1 for c in corridors_after_fusion
                     if c.get("subnet_role") == "backbone")
    n_subnets = sum(1 for c in corridors_after_fusion
                    if c.get("subnet_role") == "subnet")
    n_isolated = sum(1 for c in corridors_after_fusion
                     if c.get("subnet_role") == "isolated")

    return {
        "n_corridors_after_fusion": len(corridors_after_fusion),
        "n_fused_clusters": n_fused,
        "n_corridors_absorbed": total_absorbed,
        "intensity_distribution": n_intensity,
        "fusion_distance_m": FUSION_DISTANCE_M,
        "overlap_ratio_min": FUSION_OVERLAP_RATIO_MIN,
        "doctrine": "P22Σ_V4_BACKBONE_SUBNETS_Ω",
        # V4 stats
        "n_backbone": n_backbone,
        "n_subnets": n_subnets,
        "n_isolated": n_isolated,
        "subnet_min_per_cluster": SUBNET_MIN_PER_CLUSTER,
        "subnet_max_per_cluster": SUBNET_MAX_PER_CLUSTER,
        "max_absorption_ratio": MAX_ABSORPTION_RATIO,
    }
