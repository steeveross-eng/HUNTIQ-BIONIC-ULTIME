# ENGINE_REGISTRY_LOCKED — Phase XI

> **STATUT : SCELLÉ — SEALED — VERROUILLÉ**
> **Version registre :** V20-SUPRA-LOCKED-PHASE-XI-2026-04
> **Date de scellement :** 2026-04-19
> **Commandant :** STEEVE-MAX

---

## Hash SHA-256 officiel

```
f75eaa19baaec7a7a0a1fddebe8d7363b389b65108bfbca7b4468f8a058bb340
```

Toute altération de la liste des engines (`ENGINES_LOCKED` dans
`/app/backend/engines/v8_institutional/registry_lock_omega.py`)
invalide ce hash et fait échouer `test_engine_registry_locked`.

> **Évolution Phase XI-SUPRA :** registre étendu à 31 engines avec l'ajout de
> `ENGINE-RENDER-Ω` (moteur central de rendu — 14 couches obligatoires).

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

**TOTAL SCELLÉ : 31 engines** (22 obligatoires SUPRA-Ω + 9 étendus gouvernance/environnement/observabilité/rendu).

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
SEALED  — Phase XI / X-B / X-C / X-D / XI-SUPRA — 2026-04-19
SHA-256 — f75eaa19baaec7a7…b340
STATUS  — VERROUILLÉ IRRÉVOCABLEMENT
```
