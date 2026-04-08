# PLAN DE REPARATION DU PIPELINE DE VISIBILITE

**Protocole:** BCE-4X ULTIME ABSOLU x3
**Classification:** PLAN DE REPARATION — COMMANDANT STEEVE-MAX
**Date:** Fevrier 2026

---

## 1. CORRECTIONS EXECUTEES

| # | Bug | Fichier | Ligne | Action | Statut |
|---|---|---|---|---|---|
| 1 | multiEngines court-circuit | BionicCorridorsV6Layer.jsx | L252 | Suppression condition `multiEngines` | **FAIT** |
| 2 | saisonniers court-circuit | BionicCorridorsV6Layer.jsx | L265 | Suppression condition `saisonniers` | **FAIT** |
| 3 | Aliasing alimentation/trajets | BionicCorridorsV6Layer.jsx | L253 | Mapping direct par type | **FAIT** |
| 4 | Aliasing repos/habitat | BionicCorridorsV6Layer.jsx | L254 | Mapping direct par type | **FAIT** |
| 5 | Aliasing rut/affuts | BionicCorridorsV6Layer.jsx | L255 | Mapping direct par type | **FAIT** |
| 6 | Aliasing point alimentation/trajets | BionicCorridorsV6Layer.jsx | L281 | Mapping direct par type | **FAIT** |
| 7 | Aliasing point repos/habitat | BionicCorridorsV6Layer.jsx | L282 | Mapping direct par type | **FAIT** |
| 8 | Aliasing point rut/affuts | BionicCorridorsV6Layer.jsx | L283 | Mapping direct par type | **FAIT** |
| 9 | Ghost element CSS | BionicCorridorsV6Layer.jsx | L34-47 | Extraction CSS dans fichier externe | **FAIT** |

## 2. VERIFICATION DE SYNCHRONISATION

| Test | Toggle | Attendu | Resultat |
|---|---|---|---|
| Zone alimentation OFF | `zoneSubFilters.alimentation = false` | Zone invisible | **SYNCHRONISE** |
| Zone repos OFF | `zoneSubFilters.repos = false` | Zone invisible | **SYNCHRONISE** |
| Zone rut OFF | `zoneSubFilters.rut = false` | Zone invisible | **SYNCHRONISE** |
| Zone eau OFF | `zoneSubFilters.eau = false` | Zone invisible | **SYNCHRONISE** |
| Corridor normaux OFF | `corridorSubFilters.normaux = false` | FAIBLE+MODERE invisibles | **SYNCHRONISE** |
| Corridor intenses OFF | `corridorSubFilters.intenses = false` | FORT+MAJEUR invisibles | **SYNCHRONISE** |
| Corridor extreme OFF | `corridorSubFilters.extreme = false` | CRITIQUE invisible | **SYNCHRONISE** |

---

*BCE-4X ULTIME ABSOLU x3 — COMMANDANT STEEVE-MAX*
