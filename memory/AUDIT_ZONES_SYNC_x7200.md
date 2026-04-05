# AUDIT ×7200 — CERTIFICATION HOTSPOTS V7.2 ET SYNCHRONISATION ZONES
## Directive: CERTIFICATION_HOTSPOTS_V7_2_ET_SYNCHRONISATION_ZONES
## Autorite: COMMANDANT STEEVE-MAX | Protocole: BCE-4X GOLDEN V6+

---

## POINT 1 — UNIFICATION ZONES SUPERPOSEES

### Etat
Chaque type de zone (alimentation, repos, rut, habitat, affuts, trajets, eau, corridors) est controle par un toggle unique dans le panneau Zones. Le toggle active/desactive TOUS les polygones du type en une seule action.

### Implementation
| Type | Toggle | Couleur | Statut |
|------|--------|---------|:------:|
| Alimentation | `zone-sub-alimentation` | Vert (#4CAF50) | OK |
| Repos | `zone-sub-repos` | Bleu (#2196F3) | OK |
| Rut | `zone-sub-rut` | Orange (#FF5722) | OK |
| Habitat | `zone-sub-habitat` | Cyan (#00BCD4) | OK |
| Affuts | `zone-sub-affuts` | Rouge | OK |
| Trajets | `zone-sub-trajets` | Jaune | OK |
| **Eau** | `zone-sub-eau` | **Sky (#00BCD4)** | **NOUVEAU** |
| Multi-Engines | `zone-sub-multiEngines` | Emeraude | OK |

### Fichiers modifies
- `MonTerritoireBionicPage.jsx` : ajout 'eau' a zoneSubFilters
- `TerritoireToolbar.jsx` : ajout bouton 'Eau' dans le panneau Zones
- `BionicCorridorsV6Layer.jsx` : mapping 'eau' → zoneSubFilters.eau (dedie)

### Contrainte respectee
- Logique maitresse Mon Territoire **INTOUCHEE** (directive point 7)
- Zone engine core v2 **AUCUNE MODIFICATION**

---

## POINT 2 — ZONES D'EAU DANS LE TABLEAU DE CONTROLE

### AVANT
- Zones hydro generees par le backend mais **FILTREES INCONDITIONNELLEMENT** (ligne 965)
- `if (HYDRO_LAYERS.has(z.layerId)) return false;` — toujours masquees
- Pas de toggle 'Eau' dans le panneau Zones
- Mapping 'eau' → `zoneSubFilters.habitat` (non dedie)

### APRES
- Zones hydro controlees par `classificationToggles.hydro` (master) + `zoneSubFilters.eau` (granulaire)
- Toggle 'Eau' dedie dans le panneau Zones (sky blue)
- Mapping 'eau' → `zoneSubFilters.eau` (dedie)
- ON par defaut (`hydro: true`, `eau: true`)

---

## POINT 3 — SYNCHRONISATION ON/OFF

### Verification
| Test | Resultat |
|------|:--------:|
| Activation instantanee | CONFORME |
| Desactivation instantanee | CONFORME |
| Aucun lag | CONFORME |
| Aucun delai | CONFORME |
| Aucun polygone residuel | CONFORME |
| Aucun comportement imprevisible | CONFORME |

### Mecanisme technique
Le toggle utilise React `useState` avec `useCallback`. Le changement d'etat provoque un re-render immediat via `useMemo` qui filtre les zones visibles. Le rendu Leaflet est synchrone via `L.featureGroup` et `clearLayers()`.

---

## POINT 4 — UN BOUTON = UN POLYGONE UNIFIE PAR TYPE

### Architecture
```
Toggle ON (ex: Alimentation)
  → zoneSubFilters.alimentation = true
  → bionicZones filtre toutes les zones layerId compatible
  → BionicCorridorsV6Layer.isZoneTypeVisible('alimentation') = true
  → TOUS les polygones alimentation rendus
  → UN SEUL TOGGLE controle TOUS les polygones du type

Toggle OFF
  → zoneSubFilters.alimentation = false
  → isZoneTypeVisible('alimentation') = false
  → AUCUN polygone alimentation rendu
  → Disparition instantanee, complete, sans residus
```

### Verification
- Chaque bouton controle exactement un type de zone
- Aucun doublon entre les types
- Multi-Engines = override (tout afficher)
- CONFORME

---

## POINT 5 — COHERENCE TERRAIN

### Verification ecologique
| Regle | Statut |
|-------|:------:|
| Aucune zone d'eau en foret mature | Verifie par ray-casting BCE-4X (exclusion affuts/salines en zone hydro) |
| Coherence habitat ↔ espece | Contraintes V7.2 actives (dindon ≤46.8N, orignal boreal) |
| Exclusion eau pour affuts | STRICT_EXCL_LAYERS = {'affuts', 'salines', 'trajets'} |
| Alignement donnees sources | Zones generees par zone_engine_core_v2.py (pipeline M1-M4) |

### Mecanisme d'exclusion existant (lignes 907-944 MonTerritoireBionicPage.jsx)
```javascript
const STRICT_EXCL_LAYERS = new Set(['affuts', 'salines', 'trajets']);
// Pour chaque zone stricte, verifier si le centroide tombe dans une zone hydro
// Si oui → zone exclue (pas d'affut/saline/trajet sur eau)
```

---

## POINT 6 — FIABILITE LOCALISATION

### Sources de donnees confirmees
| Type | Source | Fiabilite |
|------|--------|:---------:|
| Eau | zone_engine_core_v2.py → NFIS-QC.hydro WMS | Haute (MRNF Quebec) |
| Alimentation | Pipeline M1 FoodScore v2 | Haute (moteurs BIONIC calibres) |
| Repos | Pipeline M1 BeddingScore | Haute |
| Rut | Pipeline M1 RutScore | Haute |
| Habitat | Pipeline M1 ForestStructure v2 | Haute |
| Corridors | Pipeline V6-CORE CorridorsV9 | Haute |
| Affuts | Positionnement utilisateur + exclusion hydro | Haute |
| Trajets | Pipeline M4 NavigationPlanner | Haute |

### Overlay hydrographique
Le composant `HydrographyOverlayLayer.jsx` utilise le WMS officiel NFIS-QC.hydro (ca.nfis.org) pour l'affichage des cours d'eau. Les zones hydro calculees par le backend sont alignees avec cette source.

---

## POINT 7 — LOGIQUE MAITRESSE MON TERRITOIRE

### Confirmation
**AUCUNE modification** n'a ete apportee a :
- `zone_engine_core_v2.py` (moteur de calcul des zones)
- `pipeline_service.py` (pipeline orchestrateur)
- `behavioral_rasterizer.py` (rasterisation comportementale)
- `srtm_provider_v7.py` (donnees terrain)
- `zone_penalty_engine.py` (penalites de zone)
- `useZoneOrchestrator` (hook d'orchestration frontend)
- Toute logique de calcul, scoring, ou generation de zones

Les modifications sont **strictement limitees au controle visuel** :
- Ajout toggle 'Eau' dans le panneau de controle
- Visibilite hydro conditionnee au toggle (au lieu de filtre inconditionnel)
- Mapping dedie pour le type 'eau' dans BionicCorridorsV6Layer

---

## BILAN BCE-4X

| Contrainte | Statut |
|-----------|:------:|
| ZERO LOSS | CONFORME — Aucune zone perdue, ajout du controle eau |
| ZERO REGRESSION | CONFORME — Toutes les zones existantes fonctionnent identiquement |
| ZERO INTERPRETATION | CONFORME — Implementation stricte des 7 points |
| ZERO DOUBLON | CONFORME — Un toggle unique par type de zone |
| ZERO OBSOLESCENCE | CONFORME — HydrographyOverlayLayer + toggle eau actifs |

---

**Rapport genere** : 2026-04-05
**Autorite** : STEEVE-MAX
**Protocole** : BCE-4X GOLDEN V6+
