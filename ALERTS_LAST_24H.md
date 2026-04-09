# ALERTS_LAST_24H.md
## BCE-4X ULTIME ABSOLU x3 — ALERTES DES DERNIERES 24H
### COMMANDANT STEEVE-MAX — RAPPORT DE SURVEILLANCE CERTIFIE

---

**PERIODE:** 2026-04-08 18:04 UTC — 2026-04-09 18:04 UTC
**DATE DE GENERATION:** 2026-04-09 18:04 UTC
**BRANCHE:** SUPRA_RECONSTRUCTION
**ENVIRONNEMENT:** https://huntiq-restore.preview.emergentagent.com

---

## RESUME EXECUTIF

| Metrique | Valeur | Statut |
|----------|--------|--------|
| ALERTES CRITIQUES | **0** | CONFORME |
| ALERTES STANDARD | **0** | CONFORME |
| VIOLATIONS DETECTEES | **0** | CONFORME |
| INCIDENTS ACTIFS | **0** | CONFORME |
| REGRESSIONS T1-T5 | **0** | CONFORME |

---

## DETAIL PAR CATEGORIE

### A — Branches
| Verification | Resultat | Horodatage |
|-------------|----------|------------|
| Branches non autorisees creees | 0 (ZERO) | 2026-04-09 18:04 UTC |
| Merge non autorise | 0 (ZERO) | 2026-04-09 18:04 UTC |
| Branche SUPRA_RECONSTRUCTION intacte | CONFIRME | 2026-04-09 18:04 UTC |

### B — Modifications Code
| Verification | Resultat | Horodatage |
|-------------|----------|------------|
| Modifications UI/UX non autorisees | 0 (ZERO) | 2026-04-09 18:04 UTC |
| Modifications moteurs RSF/SSF | 0 (ZERO) | 2026-04-09 18:04 UTC |
| Modifications scores/donnees | 0 (ZERO) | 2026-04-09 18:04 UTC |
| Modifications coefficients | 0 (ZERO) | 2026-04-09 18:04 UTC |
| Modifications regles metier | 0 (ZERO) | 2026-04-09 18:04 UTC |
| Modifications ANALYSIS_RADIUS_M | 0 (ZERO) | 2026-04-09 18:04 UTC |
| Injections de styles dynamiques | 0 (ZERO) | 2026-04-09 18:04 UTC |
| Reintroduction couches inactives | 0 (ZERO) | 2026-04-09 18:04 UTC |

### C — Tests Anti-Regression (Execution LIVE 2026-04-09 18:04:25-18:04:27 UTC)
| Suite | Tests | Passes | Echoues | Horodatage |
|-------|-------|--------|---------|------------|
| T1 — Selection salines | 4 | 4 | 0 | 18:04:25 UTC |
| T2 — Generation polygones | 4 | 4 | 0 | 18:04:26 UTC |
| T3 — Coherence UI/UX | 6 | 6 | 0 | 18:04:26 UTC |
| T4 — Regles metier | 4 | 4 | 0 | 18:04:27 UTC |
| T5 — Integrite RSF/SSF | 3 | 3 | 0 | 18:04:27 UTC |
| **TOTAL** | **21** | **21** | **0** | |

### D — Deploiements
| Verification | Resultat |
|-------------|----------|
| Deploiements bloques pour echec T1-T5 | 0 |
| Deploiements non valides | 0 |

---

## TRACES API LIVE T1 (2026-04-09 18:04:25 UTC)

```json
{
  "version": "ALIMENTATION-V2",
  "species": "CERF",
  "score_global": 54,
  "n_salines": 2,
  "n_candidates": 4,
  "max_salines": 2,
  "salines": [
    {"id":"SAL-06","score":55,"selected":true,"rank":1,"lat":47.297075,"lng":-72.501908,"distance_centre_m":356,"type":"minerale","criteres":{"eau":46,"couvert":43,"pente":22,"accessibilite":90,"securite":93,"habitat":58}},
    {"id":"SAL-10","score":48,"selected":true,"rank":2,"lat":47.301544,"lng":-72.505133,"distance_centre_m":423,"type":"minerale","criteres":{"eau":43,"couvert":40,"pente":22,"accessibilite":40,"securite":103,"habitat":60}},
    {"id":"SAL-11","score":48,"selected":false,"rank":0,"lat":47.303439,"lng":-72.495284,"distance_centre_m":522,"type":"minerale","criteres":{"eau":43,"couvert":32,"pente":18,"accessibilite":70,"securite":90,"habitat":61}},
    {"id":"SAL-07","score":45,"selected":false,"rank":0,"lat":47.297783,"lng":-72.496169,"distance_centre_m":380,"type":"minerale","criteres":{"eau":43,"couvert":49,"pente":22,"accessibilite":90,"securite":19,"habitat":62}}
  ],
  "conformite": {"bce4x":true,"steeve_max":true,"zones_modifiees":0,"centres_modifies":0}
}
```

Verification: min_selected(48) >= max_non_selected(48) => CONFORME
POST max_salines=4 => HTTP 422 => CONFORME

## TRACES API LIVE T2 (2026-04-09 18:04:26 UTC)

```
Engine: CORRIDORS-V10, Version: 10.0.0, Score: 100, Classe: OPTIMAL
Network: {"total_zones":64,"total_corridors":193,"total_path_cells":2572,"total_cost":1581.84}
Continuity: {"connected":true,"components":1,"dead_ends":0,"bce4x_continuity":"PASS"}
11 Polygones: scores 0.868-0.975, verts 1681-2401, tous centers presents
58 Corridors LineString
```

## TRACES GREP T3 (2026-04-09 18:04:26 UTC)

```
L49:  ZONE_COLORS = { alimentation: '#4CAF50', repos: '#2196F3', rut: '#FF5722', eau: '#00BCD4' }
L66:  LEVEL_ZINDEX = { FAIBLE: 0, MODERE: 1, FORT: 2, MAJEUR: 3, CRITIQUE: 4 }
L313: fillColor: 'transparent'
L314: fillOpacity: 0
L228: #FFFFFF glow CRITIQUE uniquement (weight:2, opacity:0.25)
L458: #FFFFFF centroides uniquement
Toggles orphelins: ZERO
```

## TRACES GREP T4 (2026-04-09 18:04:27 UTC)

```
router.py:25:   max_salines: int = Field(2, ge=1, le=2, ...)
engine.py:62:   max_salines = max(1, min(2, max_salines))
salines.py:272: max_salines = max(1, min(2, max_salines))
engine.py:266:  ANALYSIS_RADIUS_M = 780.0
```

## TRACES GREP T5 (2026-04-09 18:04:27 UTC)

```
salines.py:171: w_eau = 0.25
salines.py:172: w_couvert = 0.20
salines.py:173: w_pente = 0.20
salines.py:174: w_acces = 0.15
salines.py:175: w_securite = 0.10
salines.py:176: w_habitat = 0.10
Normalisation L178-185: w_total divise chaque poids
Score L188-193: sum(score_i * w_i)
```

---

## INCIDENTS RESOLUS (HISTORIQUE)

| # | Incident | Date resolution | Rapport |
|---|----------|-----------------|---------|
| 1 | Casing blanc + fill transparent | 2026-02-01 | VISUAL_RESTORE_REPORT.md |
| 2 | SAL-06/SAL-11 exclusion distance | 2026-02-01 | SALINES_SELECTION_RULES.md |
| 3 | Couches inactives Habitat/Trajet | 2026-02-01 | UNUSED_LAYERS_AUDIT.md |
| 4 | Hotspots RUT < 100% | 2026-02-01 | RUT_HOTSPOTS_100PCT_FIX.md |
| 5 | Repos zones non rendues | 2026-02-01 | REPOS_ZONE_FIX.md |
| 6 | Affuts non visibles | 2026-02-01 | AFFUTS_AUDIT.md |

---

**CONFORME — ZERO ALERTE ACTIVE — ZERO INCIDENT — ZERO REGRESSION**

**Date de certification:** 2026-04-09 18:04 UTC
**Auteur:** Agent BCE-4X sous ordres COMMANDANT STEEVE-MAX
