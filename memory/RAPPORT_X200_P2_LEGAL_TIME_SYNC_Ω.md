# RAPPORT_X200_P2_LEGAL_TIME_SYNC_Ω

**Protocole** : BCE-4X ULTIME ABSOLU — TOP-ABSOLU  
**Phase**     : X200_P2_INTEGRATION_Ω — Axe 1 : Synchronisation MFFP 2026  
**Commandant**: STEEVE-MAX — Date : 2026-04-23 (UTC)  
**Zone**      : zone_2_bas_saint_laurent (sous-zones 2A / 2B)  
**V30**       : LOCKED — INTANGIBLE

## 1. Objet
Synchronisation annuelle du catalogue MFFP zone 2 Bas-Saint-Laurent pour
l'année 2026, avec extension institutionnelle sous-zones 2A/2B et armes
(carabine / arc / arbalète). Signature `MFFP_CATALOGUE_VERSION`.

## 2. Catalogue MFFP 2026 scellé

Constante `MFFP_CATALOGUE_VERSION = "MFFP_2026_ZONE_2_BSL_X200_P2_SYNC_Ω"`.

| Espèce    | Arme(s)                 | Sous-zone | Fenêtre(s)                              |
|-----------|-------------------------|-----------|-----------------------------------------|
| orignal   | carabine                | all       | 19 sept → 18 oct                        |
| orignal   | arc                     | all       | 12 sept → 18 oct                        |
| orignal   | arbalète                | all       | 12 sept → 18 oct                        |
| chevreuil | carabine                | **2A**    | 1 nov → 30 nov                          |
| chevreuil | arc                     | all       | 25 oct → 30 nov                         |
| chevreuil | arbalète                | all       | 25 oct → 30 nov                         |
| cerf      | (alias chevreuil V7)    | idem      | idem chevreuil                          |
| ours      | carabine, arc           | all       | 15 mai → 30 juin ; 1 sept → 31 oct      |
| dindon    | carabine, arc, arbalète | all       | 25 avril → 31 mai                       |
| **wapiti**| —                       | —         | **NON ADMISSIBLE en zone 2 (MFFP 2026)**|

La vue héritée `SEASONS_ZONE_BSL` (union toutes armes/sous-zones) reste
exposée pour la rétrocompatibilité V7 (consommée par `predictive_omega`).

## 3. API étendue — paramètres `weapon` et `subzone`

```python
is_legal(species, date, weapon=None, subzone="all")
compute_legal_time(species, iso_date=None, weapon=None, subzone="all")
```

Comportement :
- `weapon=None` → union de toutes les armes (match si ≥ 1 couvre la date).
- `weapon="carabine"` → contrainte restreinte à l'arme.
- `subzone="2A"` / `"2B"` → vérifie la compatibilité de la sous-zone.

Toute réponse porte désormais `catalogue_version` + (quand legal)
`weapons_allowed` + `matches` (fenêtres actives, par arme/sous-zone).

## 4. Preuve live (waypoint officiel)

```
POST /api/v7-ultime/legal-time/compute
     {"species":"orignal","date":"2026-10-01","weapon":"carabine"}
→ HTTP 200
   legal            = true
   weapons_allowed  = ["carabine"]
   matches[0]       = { window:{start:"09-19",end:"10-18"}, weapon:"carabine", subzone:"all" }
   catalogue_version= MFFP_2026_ZONE_2_BSL_X200_P2_SYNC_Ω
```

## 5. Tests manuels (7 cas critiques verts)

- `test_mffp_catalogue_version_stamped` ✅ — signature cryptographique.
- `test_mffp_wapiti_not_admissible_zone_2` ✅ — liste vide confirmée.
- `test_mffp_orignal_arc_starts_earlier_than_carabine` ✅ — 13 sept → arc open, carabine fermée.
- `test_mffp_chevreuil_subzone_2a_only_for_carabine` ✅ — subzone 2B rejetée pour carabine.
- `test_mffp_ours_two_windows` ✅ — printemps + automne.
- `test_mffp_catalogue_version_embedded_in_response` ✅ — traçabilité API.
- `test_mffp_weapons_allowed_listed_when_legal` ✅ — arc+carabine+arbalète sur orignal 20 sept.

## 6. Garde-fous Ω
- V30 intangible (aucun import `engines.v8_institutional.*`).
- Aucun rendu hors smoother modifié.
- DIAGNOSTIC-CORRIDORS-Ω inactif.
- Le moteur reste sous triple verrou X199 existant (non changé).

**STATUT : SCELLÉ — MFFP 2026 SYNCHRONISÉ — OPÉRATIONNEL**
