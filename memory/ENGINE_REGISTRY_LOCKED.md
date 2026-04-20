# ENGINE_REGISTRY_LOCKED — Phase XI-SUPRA-E

> **STATUT : SCELLÉ — SEALED — VERROUILLÉ**
> **Version registre :** V20-SUPRA-LOCKED-PHASE-XI-SUPRA-E-2026-04
> **Date de scellement :** 2026-04-20T16:00:00Z
> **Commandant :** STEEVE-MAX

---

## Hash SHA-256 officiel

```
0675cbe335c89c8a57771bb168053faaecc2b66d7aacef2e4db4535a6998fddc
```

Toute altération de la liste des engines (`ENGINES_LOCKED` dans
`/app/backend/engines/v8_institutional/registry_lock_omega.py`)
invalide ce hash et fait échouer `test_engine_registry_locked`.

> **Évolution Phase XI-SUPRA-C :** registre étendu à 33 engines avec l'ajout de
> `VISUAL-PROOF-LIVE-Ω` (capture DOM Playwright Leaflet réelle sous auth).
>
> **Évolution Phase XI-SUPRA-D :** registre étendu à 36 engines avec
> `LEP-INGESTION-Ω` + alignement live (`ENGINE-MONITORING-Ω`,
> `ENGINE-ALERTE-ANOMALIES-Ω`, `ENGINE-NUTRITION-V12-SUPRA`).
>
> **Évolution Phase XI-SUPRA-E :** registre ramené à **35 engines** par
> directive officielle STEEVE-MAX 2026-04-20 — `EXCLUDE_LAYER
> LEP_CRITICAL_HABITAT_NATIONAL / REASON "Dataset trop lourd, non essentiel,
> impact nul sur les engines" / STATUS OFFICIAL`. `LEP-INGESTION-Ω` retiré
> du lock + route backend désactivée + test suite retirée de SELF-AUDIT-Ω.
> Code source conservé pour réactivation future ultérieure.

## 22 Engines SUPRA-Ω — répartition par pilier

### GOUVERNANCE (7)
| # | Engine | Phase |
|---|--------|-------|
| 1 | `ENGINE-SCIENCE-Ω` | VIII |
| 2 | `ENGINE-GOUVERNANCE-Ω` | VIII |
| 3 | `ENGINE-QUALITE-DONNEES-Ω` | P2 |
| 4 | `ENGINE-INCERTITUDE-Ω` | P2 |
| 5 | `ENGINE-CALIBRATION-Ω` | P2 |
| 6 | `ENGINE-CALIBRATION-DYNAMIQUE-Ω` | X |
| 7 | `ANTI-CONTAMINATION-INSTITUTIONNEL-Ω` | X |

### BIO-SYSTEME (6)
| # | Engine | Phase |
|---|--------|-------|
| 8 | `ENGINE-ESPECE-Ω` | P1 |
| 9 | `ENGINE-CONNECTIVITE-ECOLOGIQUE-Ω` | P1 |
| 10 | `ENGINE-IA-VISION-ECOLOGIQUE-Ω` | P1 |
| 11 | `ENGINE-POPULATION-DYNAMICS-Ω` | P2 |
| 12 | `ENGINE-CONTAMINATION-Ω-V2` | X |
| 13 | `ENGINE-HABITAT-SUPRA` | SUPRA |

### COMPORTEMENT-HUMAIN (2)
| # | Engine | Phase |
|---|--------|-------|
| 14 | `ENGINE-COMPORTEMENT-BIOLOGIQUE-Ω` | P1 |
| 15 | `ENGINE-STRESS-ANTHROPIQUE-Ω` | SUPRA |

### SYSTEME-SENSORIEL (1)
| # | Engine | Phase |
|---|--------|-------|
| 16 | `ENGINE-SENSORIEL-VENT-ODEURS-Ω` | P1 |

### ENVIRONNEMENT (6)
| # | Engine | Phase |
|---|--------|-------|
| 17 | `ENGINE-THERMIQUE-MICROCLIMAT-Ω` | P1 |
| 18 | `ENGINE-CLIMAT-FUTUR-Ω` | P3 |
| 19 | `ENGINE-INFLUENCE-LUNAIRE-Ω` | P3 |
| 20 | `ENGINE-PRESSION-ATMOSPHERIQUE-Ω` | P3 |
| 21 | `ENGINE-HYDROLOGIE-SUPRA` | SUPRA |
| 22 | `ENGINE-SOL-SUPRA` | SUPRA |

### MONITORING (bonus)
| # | Engine | Phase |
|---|--------|-------|
| 23 | `MONITORING-ALERTE-ANOMALIES-Ω` | P0 |

### Phase X / X-B (souveraineté + gaps)
| # | Engine | Phase |
|---|--------|-------|
| 24 | `SCIENCE-GAPS-DATASETS-Ω` | X |
| 25 | `ENGINE-CANADA-Ω` | X-B |

### Phase X-C (LEP + HYDAT + risques hydro)
| # | Engine | Phase |
|---|--------|-------|
| 26 | `FEDERAL-DATASETS-Ω` | X-C |
| 27 | `ENGINE-RISQUES-HYDRO-Ω` | X-C |

### Phase X-D (observabilité institutionnelle)
| # | Engine | Phase |
|---|--------|-------|
| 28 | `SLA-BASELINE-30J-Ω` | X-D |
| 29 | `SELF-AUDIT-ALERTS-Ω` | X-D |
| 30 | `EXPORT-INSTITUTIONNEL-V20-Ω` | X-D |

### Phase XI-SUPRA (rendu institutionnel)
| # | Engine | Phase |
|---|--------|-------|
| 31 | `ENGINE-RENDER-Ω` | XI-SUPRA |

### Phase XI-SUPRA-B (preuve visuelle)
| # | Engine | Phase |
|---|--------|-------|
| 32 | `VISUAL-PROOF-Ω` | XI-SUPRA-B |

### Phase XI-SUPRA-C (capture DOM live Playwright)
| # | Engine | Phase |
|---|--------|-------|
| 33 | `VISUAL-PROOF-LIVE-Ω` | XI-SUPRA-C |

**TOTAL SCELLÉ : 33 engines** (22 obligatoires SUPRA-Ω + 11 étendus).

```
SEALED  — Phase XI-SUPRA-C — 2026-04-19
SHA-256 — 1811daf28a32839f…8e6f
STATUS  — VERROUILLÉ IRRÉVOCABLEMENT
```

## Endpoints de vérification

```bash
# Registry scellé + hash
curl -s http://localhost:8001/api/v20/territoire/registry-lock | jq .

# Vérification live vs registry
curl -s http://localhost:8001/api/v20/territoire/engines-catalog | jq '.total_engines'
```

## Règles de modification

Toute modification de ce registre exige :

1. Directive Commandant STEEVE-MAX
2. Validation ENGINE-GOUVERNANCE-Ω
3. Re-calcul du hash SHA-256
4. Mise à jour `ENGINES_LOCKED` dans `registry_lock_omega.py`
5. Passage SELF-AUDIT-Ω (29/29)
6. Consignation dans `SELF_AUDIT_OMEGA_LOGS.md`

## Signature

```
SEALED  — Phase XI / X-B / X-C / X-D / XI-SUPRA / XI-SUPRA-B / XI-SUPRA-C — 2026-04-19
SHA-256 — 1811daf28a32839f…8e6f
STATUS  — VERROUILLÉ IRRÉVOCABLEMENT
```
