"""
P22I_MULTI_ANCHOR_CHAINED_CORRIDORS_Ω · Module institutionnel multi-nœuds
══════════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT

Objectif :
  - Générer des corridors multi-nœuds (alim → repos → rut → thermique).
  - Activer la logique chained_corridors() dans le pipeline ORGANIC.
  - Renforcer la cohérence comportementale par espèce.
  - Améliorer la continuité et la structure du réseau.

Stratégie biologique (P22I_V2 — graph-traversal réel) :
  1. Construire un graphe d'adjacence depuis les `source_id` des corridors atomiques.
  2. DFS limité pour trouver des chemins ≥ 3 nœuds (≥ 2 transitions).
  3. Concaténer les paths corridors successifs en super-corridors chained.
  4. Préserver les corridors atomiques d'origine ET ajouter les chains.
  5. Anti-générique : aucune chain artificielle — uniquement basée sur le
     graphe réel issu du moteur V30.

V30_LOCK INVIOLÉ · FUSION ADD-ONLY · ENGINE EXTERNE
"""

from __future__ import annotations

import math
from typing import Any

# Doctrine biologique : séquences canoniques par espèce (référence/audit)
SPECIES_CHAIN_SEQUENCES: dict[str, list[list[str]]] = {
    "chevreuil": [
        ["alimentation", "repos", "rut"],
        ["alimentation", "repos"],
    ],
    "orignal": [
        ["alimentation", "humide", "repos", "thermique"],
        ["alimentation", "humide", "repos"],
        ["alimentation", "repos", "thermique"],
    ],
    "ours_noir": [
        ["alimentation", "repos", "thermique"],
        ["alimentation", "repos"],
    ],
    "dindon_sauvage": [
        ["alimentation", "repos"],
    ],
    "wapiti": [
        ["alimentation", "repos", "rut", "thermique"],
        ["alimentation", "repos", "rut"],
    ],
}

CHAINED_PREFIX = "chained_"

# Limites doctrinales graph-traversal
DEFAULT_MIN_CHAIN_NODES = 3   # 3 nodes minimum (= 2 transitions)
DEFAULT_MAX_CHAIN_NODES = 5   # 5 nodes maximum (anti-explosion combinatoire)
DEFAULT_MAX_CHAINS = 12       # nombre max de chains générées par espèce


def _haversine_m(p1: tuple[float, float], p2: tuple[float, float]) -> float:
    """Distance haversine en mètres."""
    lat1, lon1 = p1
    lat2, lon2 = p2
    R = 6371000.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = (math.sin(dphi / 2) ** 2
         + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2)
    return 2 * R * math.asin(min(1.0, math.sqrt(a)))


def _node_endpoints(corridor: dict) -> tuple[dict, dict]:
    """Retourne les deux endpoint nodes (node_from, node_to) du corridor."""
    nf = (corridor.get("node_from") or corridor.get("source_node")
          or corridor.get("node_a") or corridor.get("start_node") or {})
    nt = (corridor.get("node_to") or corridor.get("target_node")
          or corridor.get("node_b") or corridor.get("end_node") or {})
    return nf, nt


def _node_type_of_endpoint(corridor: dict, end: str = "start") -> str:
    """Extrait le type biologique du nœud start ou end (compat tests legacy)."""
    nf, nt = _node_endpoints(corridor)
    n = nf if end == "start" else nt
    return (n.get("type") or "").lower()


def _build_node_graph(corridors: list[dict]) -> dict[str, list[tuple[str, dict]]]:
    """Construit un graphe d'adjacence : source_id → [(neighbor_source_id, corridor)]."""
    graph: dict[str, list[tuple[str, dict]]] = {}
    for c in corridors:
        nf, nt = _node_endpoints(c)
        sid_a = nf.get("source_id")
        sid_b = nt.get("source_id")
        if not sid_a or not sid_b or sid_a == sid_b:
            continue
        graph.setdefault(sid_a, []).append((sid_b, c))
        graph.setdefault(sid_b, []).append((sid_a, c))
    return graph


def _concatenate_paths(paths: list[list[list[float]]]) -> list[list[float]]:
    """Concatène une liste de paths en un seul path continu.

    Si la fin d'un path et le début du suivant sont à <30m, on évite le doublon.
    """
    if not paths:
        return []
    out: list[list[float]] = []
    for i, p in enumerate(paths):
        if not p:
            continue
        if i == 0:
            out.extend([list(pt) for pt in p])
        else:
            if out and len(p) > 0:
                last = out[-1]
                first = p[0]
                if _haversine_m((last[0], last[1]),
                                (first[0], first[1])) < 30.0:
                    out.extend([list(pt) for pt in p[1:]])
                else:
                    out.extend([list(pt) for pt in p])
            else:
                out.extend([list(pt) for pt in p])
    return out


def _find_chains_in_graph(graph: dict[str, list[tuple[str, dict]]],
                           min_len: int = DEFAULT_MIN_CHAIN_NODES,
                           max_len: int = DEFAULT_MAX_CHAIN_NODES,
                           max_chains: int = DEFAULT_MAX_CHAINS,
                           ) -> list[list[dict]]:
    """DFS limité pour chemins de longueur ∈ [min_len, max_len] nodes.

    Retourne une liste de chemins, chaque chemin = liste de corridors successifs
    (les arêtes du parcours). Déduplication par signature normalisée.
    """
    chains: list[list[dict]] = []
    seen_signatures: set[tuple[str, ...]] = set()

    def dfs(current: str, path_corridors: list[dict],
            visited: set[str]) -> None:
        if len(chains) >= max_chains:
            return
        # Nombre de nodes parcourus = len(path_corridors) + 1 (start)
        n_nodes_now = len(path_corridors) + 1
        if n_nodes_now >= min_len:
            sig = tuple(sorted(c.get("id", "") for c in path_corridors))
            if sig not in seen_signatures:
                seen_signatures.add(sig)
                chains.append(list(path_corridors))
        if n_nodes_now >= max_len:
            return
        for (nbr, corr) in graph.get(current, []):
            if nbr in visited:
                continue
            visited.add(nbr)
            path_corridors.append(corr)
            dfs(nbr, path_corridors, visited)
            path_corridors.pop()
            visited.remove(nbr)

    for start in list(graph.keys()):
        if len(chains) >= max_chains:
            break
        visited: set[str] = {start}
        dfs(start, [], visited)

    return chains


def chain_corridors_for_species(corridors: list[dict], species: str,
                                  min_chain_nodes: int = DEFAULT_MIN_CHAIN_NODES,
                                  max_chain_nodes: int = DEFAULT_MAX_CHAIN_NODES,
                                  ) -> list[dict]:
    """Génère des corridors multi-nœuds chained (graph-traversal réel).

    Préserve les corridors atomiques d'origine ET ajoute les chains.
    """
    if not corridors or not species:
        return list(corridors)

    graph = _build_node_graph(corridors)
    if not graph:
        return list(corridors)

    chain_paths = _find_chains_in_graph(
        graph, min_len=min_chain_nodes, max_len=max_chain_nodes,
    )
    if not chain_paths:
        return list(corridors)

    chains_out: list[dict] = []
    for chain_idx, chain_corridors_seq in enumerate(chain_paths):
        if len(chain_corridors_seq) < (min_chain_nodes - 1):
            continue

        # Reconstruction de la séquence de types parcourus
        sequence_types: list[str] = []
        last_sid: str | None = None
        for i, c in enumerate(chain_corridors_seq):
            nf, nt = _node_endpoints(c)
            sid_a = nf.get("source_id")
            sid_b = nt.get("source_id")
            ta = (nf.get("type") or "?").lower()
            tb = (nt.get("type") or "?").lower()
            if i == 0:
                sequence_types.append(ta)
                sequence_types.append(tb)
                last_sid = sid_b
            else:
                if sid_a == last_sid:
                    sequence_types.append(tb)
                    last_sid = sid_b
                else:
                    sequence_types.append(ta)
                    last_sid = sid_a

        # Concaténer les paths
        paths = [c.get("path", []) for c in chain_corridors_seq]
        chained_path = _concatenate_paths(paths)
        if len(chained_path) < 4:
            continue

        # Longueur totale
        total_length_m = 0.0
        for i in range(1, len(chained_path)):
            total_length_m += _haversine_m(
                (chained_path[i - 1][0], chained_path[i - 1][1]),
                (chained_path[i][0], chained_path[i][1]),
            )

        chain_id = f"{CHAINED_PREFIX}{species}_{chain_idx:03d}"
        n_nodes = len(sequence_types)

        # Niveau d'intensité = fonction de la longueur de la chain
        if n_nodes >= 4:
            intensity_level = 4
            intensity_label = "EXTRÊME"
        else:
            intensity_level = 3
            intensity_label = "ÉLEVÉ"

        chains_out.append({
            "id": chain_id,
            "path": chained_path,
            "hierarchy": "veine_principale",
            "type": "chained_multi_anchor",
            "species": species,
            "_p22i_role": "CHAINED_CORRIDOR",
            "_p22i_sequence": sequence_types,
            "_p22i_n_transitions": len(chain_corridors_seq),
            "_p22i_n_nodes": n_nodes,
            "_p22i_source_corridor_ids": [c.get("id") for c in chain_corridors_seq],
            "length_m": total_length_m,
            "intensity_level": intensity_level,
            "intensity_label": intensity_label,
            "fusion_count": 1,
            "score": sum(float(c.get("score", 0)) for c in chain_corridors_seq) / len(chain_corridors_seq),
        })

    return list(corridors) + chains_out


def chained_summary(original_corridors: list[dict],
                    output_corridors: list[dict]) -> dict[str, Any]:
    """Synthèse statistique des corridors chained générés."""
    n_chains = sum(1 for c in output_corridors
                   if c.get("_p22i_role") == "CHAINED_CORRIDOR")
    chain_ids = [c.get("id") for c in output_corridors
                 if c.get("_p22i_role") == "CHAINED_CORRIDOR"]
    sequences_used = list({tuple(c.get("_p22i_sequence", []))
                           for c in output_corridors
                           if c.get("_p22i_role") == "CHAINED_CORRIDOR"})
    n_extreme = sum(1 for c in output_corridors
                    if c.get("_p22i_role") == "CHAINED_CORRIDOR"
                    and c.get("intensity_level") == 4)
    return {
        "n_atomic_corridors": len(original_corridors),
        "n_chained_corridors": n_chains,
        "n_extreme_chains": n_extreme,
        "n_total_after_chain": len(output_corridors),
        "chained_ids": chain_ids,
        "sequences_used": [list(s) for s in sequences_used],
        "doctrine": "P22I_MULTI_ANCHOR_CHAINED_CORRIDORS_Ω",
    }
