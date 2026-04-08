"""
Cross-Species Intelligence — S7
=================================

K3 — BCE-4X ULTIME ABSOLU | STEEVE-MAX
Expose les inferences inter-especes K2.5.
LECTURE SEULE sur knowledge.json.
"""
from typing import Optional
from modules.bionic_knowledge_engine.knowledge_provider import _load_knowledge
from modules.species_engine.resolver import resolve


def get_cross_inference_all() -> dict:
    """Retourne la matrice complete d'inferences inter-especes K2.5."""
    k = _load_knowledge()
    csi = k.get("cross_species_inference", {})
    return {
        "competition_matrix": csi.get("competition_matrix", {}),
        "habitat_overlap": csi.get("habitat_overlap", {}),
        "disease_transmission": csi.get("disease_transmission", {}),
        "_source": "K2.5_cross_species_inference",
    }


def get_cross_inference_pair(species_a: str, species_b: str) -> Optional[dict]:
    """Retourne les inferences entre deux especes specifiques.

    Args:
        species_a, species_b: Identifiants d'especes

    Returns:
        Donnees d'inference (competition, overlap, maladies) ou None
    """
    _, k2_a = resolve(species_a)
    _, k2_b = resolve(species_b)
    if k2_a is None or k2_b is None:
        return None

    k = _load_knowledge()
    csi = k.get("cross_species_inference", {})

    # Construire les cles de paire (ordre alphabetique dans le JSON)
    pair_keys = [f"{k2_a}_{k2_b}", f"{k2_b}_{k2_a}"]

    # Competition
    comp = csi.get("competition_matrix", {})
    competition = None
    for pk in pair_keys:
        if pk in comp:
            competition = comp[pk]
            break

    # Habitat overlap
    overlap_data = csi.get("habitat_overlap", {})
    overlap = None
    for pk in pair_keys:
        if pk in overlap_data:
            overlap = overlap_data[pk]
            break

    # Aussi chercher les cles speciales (bear_all_cervids)
    if overlap is None:
        if k2_a == "bear" or k2_b == "bear":
            overlap = overlap_data.get("bear_all_cervids")

    # Maladies partagees
    disease_data = csi.get("disease_transmission", {})
    shared_diseases = []
    for disease_id, disease_info in disease_data.items():
        species_list = disease_info.get("species", [])
        if k2_a in species_list and k2_b in species_list:
            shared_diseases.append({
                "disease_id": disease_id,
                **disease_info,
            })

    return {
        "species_a": k2_a,
        "species_b": k2_b,
        "competition": competition,
        "habitat_overlap": overlap,
        "shared_diseases": shared_diseases,
        "_source": "K2.5_cross_species_inference",
    }
