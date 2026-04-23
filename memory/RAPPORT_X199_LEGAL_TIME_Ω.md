# RAPPORT_X199_LEGAL_TIME_Ω

**Protocole** : BCE-4X ULTIME ABSOLU — TOP-ABSOLU  
**Phase**     : X199_ACTIVATION_Ω — moteur #4 (racine)  
**Commandant**: STEEVE-MAX — Date : 2026-04-23 (UTC)  
**Zone**      : zone_2_bas_saint_laurent  
**V30**       : LOCKED — INTANGIBLE

## 1. Activation
- `FEATURE_FLAG_ACTIVE = True` dans `engines/legal_time_omega/router.py`.
- Triple verrou X199.

## 2. Catalogue institutionnel zone 2 BSL (référence MFFP)
| Espèce    | Fenêtre(s) légale(s) |
|-----------|----------------------|
| orignal   | 19 sept – 18 oct     |
| chevreuil | 1 nov – 30 nov       |
| cerf      | 1 nov – 30 nov       |
| ours      | 15 mai – 30 juin, 1 sept – 31 oct |
| dindon    | 25 avril – 31 mai    |
| wapiti    | **non admissible en zone 2** |

Offsets d'heures légales : `sunrise −30 min` / `sunset +30 min`.

## 3. API livrée
- `is_legal(species, date)` → `{ legal: bool, window?, next_windows?, reason? }`.
- `compute_legal_time(species, iso_date=None)` → enveloppe avec `engine_id`, `zone`, `legal_hours_offset_min`.

## 4. Preuves live
```
POST /api/v7-ultime/legal-time/compute {"species":"orignal","date":"2026-10-01"}
→ legal=true, window={start:"09-19", end:"10-18"}, zone=zone_2_bas_saint_laurent
```

## 5. Tests manuels (catalogue MFFP confirmé)
- `test_orignal_in_season_october_1` ✅
- `test_orignal_out_of_season_december` ✅ (`reason=out_of_season`)
- `test_wapiti_not_allowed_zone_2` ✅ (`reason=species_not_allowed_in_zone`)
- `test_ours_two_windows_spring_and_fall` ✅
- `test_legal_time_flag_on` ✅

## 6. Garde-fous Ω
- Aucun SDK externe (logique déterministe).
- V30 intangible.
- DIAGNOSTIC-CORRIDORS-Ω inactif.
- Synchronisation annuelle du catalogue = tâche institutionnelle future (ordre dédié).

**STATUT : SCELLÉ — ACTIVÉ — OPÉRATIONNEL**
