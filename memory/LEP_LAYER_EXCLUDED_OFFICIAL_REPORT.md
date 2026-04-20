# LEP_CRITICAL_HABITAT_NATIONAL — EXCLUSION OFFICIELLE

> **COMMANDANT :** STEEVE-MAX
> **DATE :** 2026-04-20T16:00:00Z
> **STATUT :** ✅ OFFICIAL — EXCLUDED
> **PROTOCOLE :** BCE-4X ULTIME ABSOLU

---

## Directive source

```
EXCLUDE_LAYER LEP_CRITICAL_HABITAT NATIONAL
REASON "Dataset trop lourd, non essentiel, impact nul sur les engines"
STATUS OFFICIAL
```

---

## Actions d'exclusion exécutées

| # | Action | État |
|---|--------|------|
| 1 | Retrait de `LEP-INGESTION-Ω` de `ENGINES_LOCKED` | ✅ Lock = 35 engines |
| 2 | Bump version registre → `V20-SUPRA-LOCKED-PHASE-XI-SUPRA-E-2026-04` | ✅ |
| 3 | Nouveau SHA-256 scellé : `0675cbe335c89c8a57771bb168053faaecc2b66d7aacef2e4db4535a6998fddc` | ✅ |
| 4 | Désactivation du router LEP dans `server.py` (commenté, motif cité) | ✅ 404 sur `/api/v20/territoire/lep/*` |
| 5 | Retrait de `test_lep_ingestion_omega` de `SUITES` (self_audit_omega) | ✅ SELF-AUDIT-Ω = 56/56 |
| 6 | Section LEP du Health Panel → statut `EXCLUDED (OFFICIAL)` avec référence directive | ✅ |
| 7 | Mise à jour `ENGINE_REGISTRY_LOCKED.md` avec nouveau hash + justificatif | ✅ |
| 8 | Conservation du module source `lep_ingestion_omega.py` pour réactivation future ultérieure | ✅ (inerte) |
| 9 | Conservation des dossiers `/app/data/territoire_omega/data_primary_fgdb_lep` et `data_secondary_geojson_lep` (vides) | ✅ |

## Impact sur les autres engines

Conforme à la directive (*« impact nul sur les engines »*) : **ZÉRO**.

- Aucun engine actif n'importait `lep_ingestion_omega` (validé par `grep -rn lep_ingestion` backend → 1 seule occurrence dans `lep_ingestion_omega.py` lui-même)
- `BionicLayersV8.jsx` ne référençait pas encore la couche LEP (rendu prévu pour Annexe 4 non livré du fait du blocage réseau ECCC + maintenant officiellement exclu)
- `federal_datasets_omega.py` conserve ses mocks SARA mais n'a pas été modifié pour dépendre de LEP-INGESTION-Ω

## Conformité SELF-AUDIT-Ω post-exclusion

| Suite | Résultat |
|-------|----------|
| Total | **56/56 ✅ CONFORME** |
| `test_engine_registry_locked` | OK — hash `0675cbe335c89c8a…` validé |
| `test_visual_live_macro_stable` | OK — 3.1 MB ≥ 30 KB |
| `test_visual_live_mid_stable` | OK — 3.1 MB ≥ 30 KB |
| `test_visual_live_detail_stable` | OK — 3.1 MB ≥ 30 KB |

## Traçabilité institutionnelle

- **Décision :** COMMANDANT STEEVE-MAX, message 2026-04-20
- **Execution :** agent principal (main.E1)
- **Traçage** : commits/diffs des fichiers modifiés disponibles via `git log`
- **Réversibilité :** toute réactivation future nécessite directive `REACTIVATE_LAYER LEP_CRITICAL_HABITAT_NATIONAL STATUS OFFICIAL` — le module source reste présent, il suffit de décommenter le router dans `server.py` et de remettre `LEP-INGESTION-Ω` dans `ENGINES_LOCKED`.

## Conclusion

Exclusion exécutée conformément sans interprétation. BIONIC OS V20-SUPRA reste
**CONFORME 56/56** avec 35 engines scellés.
