# BDRE — MONITORING DES APIs EXTERNES V2
## BCE-4X GOLDEN V6+ | Directive STEEVE-MAX
## Date: 2026-04-06
## Corrections: Aucune requise (document conforme)

---

## HISTORIQUE DES CORRECTIONS

| Correction | Description | Statut |
|------------|-------------|--------|
| Aucune | Document conforme selon BDRE_CONFORMITY_REPORT.md | CONFORME |

---

## 1. REGISTRE DES APIs MONITOREES

### 1.1 APIs actives

| ID | API | Endpoint | Protocole | Authentification |
|---|---|---|---|---|
| API-01 | Overpass (miroir 1) | https://overpass-api.de/api/interpreter | POST | Aucune |
| API-02 | Overpass (miroir 2) | https://overpass.kumi.systems/api/interpreter | POST | Aucune |
| API-03 | Overpass (miroir 3) | https://lz4.overpass-api.de/api/interpreter | POST | Aucune |
| API-05 | WeatherAPI | https://api.weatherapi.com/v1/ | GET | API Key |
| API-06 | Nominatim | https://nominatim.openstreetmap.org/ | GET | Aucune |

### 1.2 APIs non connectees (futures)

| ID | API | Statut | Priorite |
|---|---|---|---|
| API-07 | Foret Ouverte (MFFP Quebec) | NON CONNECTE | P1 |
| API-08 | VGO (Vegetal Quebec) | NON CONNECTE | P2 |
| API-09 | SRTM/Copernicus DEM | NON CONNECTE | P1 |
| API-10 | Canadian GeoBase | NON CONNECTE | P2 |

---

## 2. METRIQUES DE MONITORING

### 2.1 Par API

| Metrique | Description | Seuil alerte |
|---|---|---|
| disponibilite | % de reponses HTTP 200 sur 24h | < 95% |
| latence_avg_ms | Temps de reponse moyen | > 5000ms |
| latence_p95_ms | 95e percentile latence | > 15000ms |
| taux_erreur | % de reponses non-200 | > 10% |
| donnees_vides | % de reponses valides mais vides | > 50% |
| derniere_reponse | Timestamp derniere reponse OK | > 1h |

### 2.2 Par source de donnees

| Metrique | Description | Seuil alerte |
|---|---|---|
| couverture_zone | % de la zone demandee couverte | < 30% |
| fraicheur_cache | Age du cache vs TTL | > TTL |
| noeuds_graphe | Nombre de noeuds dans le graphe | < 10 |
| composantes_connexes | Nombre de sous-graphes deconnectes | > 3 |
| score_bdre | Score BDRE global | < 0.40 |

---

## 3. STRATEGIE DE ROTATION DES MIROIRS

### 3.1 Rotation existante (TNE terrain_sources.py)

```
Strategie actuelle:
1. Lancer les 3 miroirs en parallele (ThreadPoolExecutor)
2. Prendre la premiere reponse valide
3. Annuler les autres
4. Si toutes echouent: pas de retry (actuel)
5. Timeout adaptatif: 8s base + 2s/km
```

### 3.2 Amelioration BDRE

```
Strategie BDRE:
1. Consulter le registre de sante des miroirs (F1)
2. Exclure les miroirs en panne (disponibilite < 80%)
3. Prioriser le miroir avec la meilleure latence historique
4. Lancer en parallele (garder la strategie existante)
5. Scorer la reponse (couverture, completude) (F2)
6. Si score < 0.40: declencher pipeline hybride (F5)
7. Logger dans le journal d'audit (F6)
```

---

## 4. ALERTES

### 4.1 Niveaux d'alerte

| Niveau | Declenchement | Action |
|--------|--------------|--------|
| INFO | Score source > 0.60 mais < 0.80 | Log seulement |
| WARNING | Score source < 0.40 | Fallback + log |
| CRITICAL | Toutes sources primaires < 0.20 | Alerte STEEVE-MAX + fallback max |
| EMERGENCY | ZERO donnee disponible pour un territoire | Blocage pipeline + alerte |

### 4.2 Canal d'alerte

```
BDRE -> EventBus EB-BDRE-05 -> Dashboard STEEVE-MAX
BDRE -> Journal audit -> /api/v1/bdre/audit/log
BDRE -> Logger Python -> /var/log/supervisor/backend.err.log
```

---

## 5. ETAT ACTUEL DU MONITORING (TERRITOIRE 48.19, -68.39)

| API | Disponibilite | Latence | Donnees vides | Score BDRE |
|-----|-------------|---------|---------------|-----------|
| API-01 Overpass DE | 100% | ~3500ms | 0% | 0.31 (trails deficients) |
| API-05 WeatherAPI | 100% | ~200ms | 0% | 0.81 (fiable) |
| API-06 Nominatim | 100% | ~150ms | 0% | N/A (non utilise pour terrain) |

**Note**: Les APIs fonctionnent correctement. Le probleme n'est PAS la disponibilite
des APIs mais la PAUVRETE des donnees OSM pour cette zone forestiere isolee.

---

**STATUT: SPECIFICATION MONITORING V2 COMPLETE — AUCUNE CORRECTION REQUISE**
**EN ATTENTE VALIDATION STEEVE-MAX**
