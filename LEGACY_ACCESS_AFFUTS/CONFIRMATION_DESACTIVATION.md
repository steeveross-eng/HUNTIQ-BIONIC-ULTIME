# CONFIRMATION DESACTIVATION SECURISEE — ACCES AUX AFFUTS
## ORDONNANCE STEEVE-MAX 2026-04-07
## Statut : COMPLETE — MODE OFF ACTIVE

---

## 1. INVENTAIRE COMPLET — FAIT

| Element | Quantite |
|---------|----------|
| Fichiers archives | 66 |
| Geometries identifiees | 6 |
| Tables/Caches | 5 |
| Endpoints API | 8 |
| Couches frontend | 4 |
| Triggers automatiques | 3 |
| Regles BCE-4X | 7 |

Inventaire detaille : `/app/LEGACY_ACCESS_AFFUTS/INVENTAIRE_COMPLET.md`

## 2. ARCHIVE INSTITUTIONNELLE — FAIT

| Element | Statut |
|---------|--------|
| Emplacement | `/app/LEGACY_ACCESS_AFFUTS/` |
| Taille | 2.7 MB (66 fichiers) |
| Backend complet | Engines + Modules V6/V7 + Data |
| Frontend complet | Couches + Hooks |
| Documentation | Norme BCE-4X + Rapport non-regression |
| Reactivation possible | OUI — instructions dans chaque fichier |

## 3. MODE OFF — ACTIF

### Backend desactive :
| Composante | Methode | Statut |
|------------|---------|--------|
| Calcul acces orchestrateur | `ACCESS_ROUTES_ENABLED = False` | OFF |
| Endpoint `/api/v1/hunt/access-route` | Retourne `{status: disabled}` | OFF |
| Endpoint `/api/v6/access/compute` | Retourne `{status: disabled}` | OFF |
| Endpoint `/api/v6/access/compute-batch` | Retourne `{status: disabled}` | OFF |
| Endpoint `/api/v7/clarity/compute` | Retourne `{status: disabled}` | OFF |
| Endpoint `/api/v7/clarity/score` | Retourne `{status: disabled}` | OFF |

### Frontend desactive :
| Composante | Methode | Statut |
|------------|---------|--------|
| StandsMapLayer (lignes acces) | `ACCESS_ROUTES_ENABLED = false` | OFF |
| AccessRouteV6Layer | Commentaire JSX | OFF |
| HuntingPathLayer | Commentaire JSX | OFF |

### IMPORTANT : Donnees NON supprimees
- Les donnees en base (caches terrain, routes certifiees, corridors) sont PRESERVEES
- Elles ne sont simplement plus exposees ni calculees
- Mode OFF = desactivation, PAS suppression

## 4. VALIDATION POST-DESACTIVATION — FAIT

| Test | Resultat |
|------|----------|
| Orchestration (affuts visibles, acces OFF) | PASS |
| Endpoint access-route (MODE OFF) | PASS |
| V6 access (MODE OFF) | PASS |
| V7 clarity (MODE OFF) | PASS |
| Alimentation (4/4 INTACT) | PASS |
| BDRE Health (17 endpoints INTACT) | PASS |
| Cache Institutionnel (CONFORME) | PASS |
| Frontend (aucune erreur) | PASS |

### Ce qui RESTE fonctionnel :
- Affuts : visibles, recommandation par score ACTIVE
- Zones contamination : INTACTES
- Zones ecologiques : INTACTES
- Sites alimentation : INTACTS (4/4)
- Corridors de deplacement : INTACTS
- Cache institutionnel : INTACT
- BDRE engine : INTACT (17 endpoints)

### Ce qui est desactive :
- Lignes d'acces sur la carte (cyan/dashed)
- Calcul automatique des routes d'acces (A*, BDRE cascade)
- Endpoints V6/V7 d'acces
- Penetrations 90°, corridors calcules, points intermediaires

## 5. REACTIVATION FUTURE

Pour reactiver les acces aux affuts :

### Backend :
1. `orchestrator.py` : Mettre `ACCESS_ROUTES_ENABLED = True`
2. `router.py` : Restaurer le code depuis `/LEGACY_ACCESS_AFFUTS/backend/engines/hunt_orchestrator/router.py`
3. `access_engine_v6/router.py` : Restaurer depuis l'archive
4. `access_clarity_v7/router.py` : Restaurer depuis l'archive

### Frontend :
1. `StandsMapLayer.jsx` : Mettre `ACCESS_ROUTES_ENABLED = true`
2. `MapContent.jsx` : Decommenter les blocs AccessRouteV6Layer et HuntingPathLayer

---

**Signe : Agent BCE-4X | Autorite : COMMANDANT STEEVE-MAX**
**Date : 2026-04-07 | ZÉRO RÉGRESSION — ZÉRO PERTE — ZÉRO BAVURE**
