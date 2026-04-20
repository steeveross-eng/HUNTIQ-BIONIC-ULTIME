# ANTI_CONTAMINATION_INSTITUTIONNEL_Ω — Phase X-B

> **Module :** `/app/backend/engines/v8_institutional/engine_contamination_v2_omega.py` (fonction `anti_contamination_filter`)
> **Date :** 2026-04-19

## Rôle

Module central **GATEKEEPER** institutionnel. Toute observation (caméra, GPS,
pin, note, récolte, trace, collier GPS) transitant par
`/api/v20/territoire/observations` est filtrée avant ingestion ML.

## Contrôles exécutés

| Contrôle | Règle | Sévérité |
|----------|-------|----------|
| Validation géo | `40 ≤ lat ≤ 60 ∧ -85 ≤ lon ≤ -55` (extent QC) | REJECT si hors |
| Validation source | `source_type ∈ {camera-*, gps-*, pin, note, photo-exif, video, recolte, trace, collier-gps}` | WARN |
| Confidence threshold | `confidence ≥ 0.20` | WARN si bas |
| Validation espèce | `species ∈ {cerf, chevreuil, orignal, wapiti, ours_noir, dindon_sauvage, …}` | WARN |

## Output

```json
{
  "accepted": bool,
  "severity": "OK|WARN|REJECT",
  "issues": [...],
  "confidence_adjusted": float
}
```

## Connexions institutionnelles obligatoires

Conformément à la directive Commandant, le module est connecté à :

| Engine | Point d'intégration |
|--------|---------------------|
| `ENGINE-QUALITE-DONNEES-Ω` | Rapporte `confidence_adjusted` et taux de rejet |
| `ENGINE-INCERTITUDE-Ω` | Augmente variance si WARN/REJECT sur observation clé |
| `ENGINE-CONTAMINATION-Ω V2` | Croise zone CWD avant ingestion récoltes |
| `ENGINE-GOUVERNANCE-Ω` | Log centralisé REJECT dans `/gouvernance` |
| `ENGINE-RENDER-GUARD-Ω` | Blocage propagation UI si REJECT sévère |

## Validation

- `anti_contamination_filter` est appelable directement depuis toute couche
  ingérant des données terrain.
- Le test `test_calibration_dynamique` valide indirectement via ingestion.
- Endpoint `POST /observations` déclenche la recalibration après filtre.

## Sealed
```
SEALED  — Phase X-B — 2026-04-19 — BCE-4X ULTIME ABSOLU
```
