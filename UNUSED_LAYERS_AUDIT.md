# UNUSED_LAYERS_AUDIT.md
## BCE-4X — AUDIT COUCHES INACTIVES (HABITAT, TRAJET, EAU, MULTI-ENGINES)
### COMMANDANT STEEVE-MAX — ANALYSE TECHNIQUE + DECISION

---

## SECTION 1.1 — ANALYSE TECHNIQUE

### Couche HABITAT
| Critere | Resultat |
|---------|----------|
| Backend ZONE_TYPES | ❌ NON INCLUS (`["alimentation", "repos", "rut", "eau"]`) |
| Moteurs RSF/SSF | ❌ NON APPELE |
| Pipelines geospatiaux | ❌ NON UTILISE |
| Recommandations | ❌ NON REFERENCE |
| Structures JSON | ❌ AUCUNE ENTITE `zone_type="habitat"` |
| Rapports/Exports | ❌ NON UTILISE |

### Couche TRAJETS
| Critere | Resultat |
|---------|----------|
| Backend ZONE_TYPES | ❌ NON INCLUS |
| Moteurs RSF/SSF | ❌ NON APPELE |
| Pipelines geospatiaux | ❌ NON UTILISE |
| Recommandations | ❌ NON REFERENCE |
| Structures JSON | ❌ AUCUNE ENTITE `zone_type="trajets"` |
| Rapports/Exports | ❌ NON UTILISE |

### Couche MULTI-ENGINES
| Critere | Resultat |
|---------|----------|
| Backend ZONE_TYPES | ❌ NON INCLUS |
| Moteurs RSF/SSF | ❌ NON APPELE |
| Pipelines geospatiaux | ❌ NON UTILISE |
| Recommandations | ❌ NON REFERENCE |
| Structures JSON | ❌ AUCUNE ENTITE `zone_type="multiEngines"` |
| Rapports/Exports | ❌ NON UTILISE |

### Couche EAU
| Critere | Resultat |
|---------|----------|
| Backend ZONE_TYPES | ✅ INCLUS (`"eau"` dans ZONE_TYPES) |
| Moteurs RSF/SSF | ✅ Utilise pour les exclusions (zones humides) |
| Pipelines geospatiaux | ✅ Generation de polygones eau |
| Recommandations | ✅ Exclusion salines/affuts sur eau |
| Structures JSON | ✅ ENTITES `zone_type="eau"` generees |
| Rapports/Exports | ✅ Reference dans les exclusions BCE-4X |

---

## SECTION 1.2 — ANALYSE UI/UX

| Couche | Toggle declenchait rendu? | Chargee en memoire? | Visible? |
|--------|--------------------------|---------------------|----------|
| Habitat | ❌ NON (aucune donnee) | ❌ NON | ❌ NON |
| Trajets | ❌ NON (aucune donnee) | ❌ NON | ❌ NON |
| Multi-Engines | ❌ NON (aucune donnee) | ❌ NON | ❌ NON |
| Eau | ✅ OUI (zones cyan) | ✅ OUI | ✅ OUI |

---

## SECTION 1.3 — DECISION

| Couche | Decision | Justification |
|--------|----------|---------------|
| **Habitat** | **RETRAIT COMPLET** | Zero dependance backend, zero donnees, toggle orphelin |
| **Trajets** | **RETRAIT COMPLET** | Zero dependance backend, zero donnees, toggle orphelin |
| **Multi-Engines** | **RETRAIT COMPLET** | Zero dependance backend, zero donnees, toggle orphelin |
| **Eau** | **CONSERVATION** | Dependance critique: exclusions salines/affuts sur eau |

---

## SECTION 1.4 — MODIFICATIONS APPLIQUEES

### Fichiers modifies

**`MonTerritoireBionicPage.jsx`:**
- `zoneSubFilters`: Retire `habitat`, `trajets`, `multiEngines`
- `pointSubFilters`: Retire `trajets`, `habitat`
- `DOMINANT_LAYERS`: Retire `habitats`, `trajets`

**`TerritoireToolbar.jsx`:**
- Panneau Zones: Retire Habitat, Trajets, Multi-Engines (3 boutons)
- Panneau Points: Retire Trajets, Habitat (2 boutons)
- Filtre Points Chauds: Retire Trajets, Habitat (2 options)

**`BionicCorridorsV6Layer.jsx`:**
- `isZoneTypeVisible`: Retire `habitat`, `trajets`
- `isPointTypeVisible`: Retire `habitat`, `trajets`
- `filterMap` (Points Chauds): Retire `trajets`, `habitat`

### Impact
- [x] ZERO regression fonctionnelle (aucune donnee n'etait rendue)
- [x] ZERO modification backend
- [x] UI nettoyee — seuls les toggles actifs sont affiches
- [x] BCE-4X conforme

**Date:** 2026-02-01
**Auteur:** Agent BCE-4X sous ordres COMMANDANT STEEVE-MAX
