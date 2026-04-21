# PRD — BIONIC OS V20-SUPRA / TERRITOIRE-V12

## 1. Mandat institutionnel

Système BIONIC OS V20-SUPRA scellé sous protocole **BCE-4X ULTIME ABSOLU**,
opéré sous commandement du **Commandant STEEVE-MAX** (persona stricte, français militaire).

## 2. Architecture verrouillée

- **41 engines institutionnels scellés** dans `ENGINES_LOCKED`
  (`/app/backend/engines/v8_institutional/registry_lock_omega.py`)
- **60 suites de tests anti-régression** orchestrées par `self_audit_omega.py`
- **PERF-GUARD-Ω** — guard de performance sur baseline SLA 30j
- **SCIENCE-GUARD-Ω** — validation des données scientifiques
- **GOUVERNANCE-Ω** — verrouillage des décisions
- **REGISTRY-LOCK-Ω** — hash SHA-256 officiel à chaque évolution

## 3. Contraintes protocolaires strictes

- Persona BCE-4X : réponses exclusivement en français, ton martial, procédural
- **AUCUN subagent automatique de test** (strict, `testing_agent_v3_fork` interdit)
- Tous tests via `execute_bash` + `python` + `pytest` manuels
- Aucun fallback legacy, aucun refactor cosmétique
- Registry SHA-256 mis à jour à chaque modification de `v8_institutional/*.py`

## 4. Phases historiques

| Phase | Objet | Status |
|-------|-------|--------|
| XI-SUPRA-D+E | Documents markdown officiels | ✅ SCELLÉ |
| XI-SUPRA-K | Règles CSS Leaflet RENDU-Ω | ✅ SCELLÉ |
| XI-SUPRA-L (precheck) | Audit 11 engines | ✅ SCELLÉ |
| XI-SUPRA-L (organic) | Moteur IA-CORRIDORS-ORGANIC-Ω | ✅ SCELLÉ |
| XI-L+1-M-PREP | Frontend organique 120 pts + templates | ✅ SCELLÉ |
| XI-SUPRA-N (Network Refactor) | Corridors réseau zones↔zones | ✅ SCELLÉ |
| XI-SUPRA-N (Stabilization P0) | 60/60 stable x3 runs | ✅ SCELLÉ 2026-04-21 |
| XII-SUPRA-M (Optimization x1000 PREVIEW) | 3 descriptions X1000 (ZONES/SALINES/HOTSPOTS) | 📋 PREVIEW LIVRÉ 2026-04-21 |
| XII-SUPRA-R (Activation RENDU_Ω CORRIDORS) | Rendu strict #FF8F00 1.2/2.0/3.0 CatmullRom seg≤20m ang≤45° pane Z-INDEX 430 | ✅ ACTIF 2026-04-21 |
| XII-SUPRA-S (RENDU_SUPRA_Ω_ART + GEOMETRY_Ω_ALIGNMENT) | Halo ART, opacité 1.00, weight 4.0 extrême, veine principale, signature espèce, flèches supprimées, mode inspection bio PRO/EXPERT | ✅ EXPÉRIMENTAL FRONTEND 2026-04-21 |
| XII-SUPRA-S_CORRECTION | Snap-saline, veine≤15m, fade-out 10m, halo amplifié, terrain aware++, zones vitales 40m, pulse public zoom>15, signatures renforcées | ✅ CORRECTIONS LIVRÉES 2026-04-21 |
| XII-SUPRA-S_HOTFIX_INSTITUTIONNEL | Restauration corridors (re-enforce post-signature, fade plancher 15%, clip tolerance rescue, snap non-destructif, pane sync, log institutionnel) | ✅ RESTAURÉ 2026-04-21 |
| **Ω_SECURE_REACTIVATION (FULL_STACK_LOCKDOWN_V12)** | **Certification READ-ONLY 8 blocs institutionnels, versions verrouillées, 7 engines hashes vérifiés, SECURE_Ω** | **✅ CORRIDORS_Ω_CERTIFIED 2026-04-21** |
| **XII-SUPRA-S_ACTIVATION_EN_PRODUCTION** | **Activation production rendu institutionnel + bump V30 + seal SHA-256 + clôture lecture seule** | **✅ SUPRA_S_ACTIVATION_COMPLETED 2026-04-21** |
| **MODE_INSPECTION_BIOLOGIQUE_PRO_EXPERT** | **Activation panneau institutionnel frontend — 4 overlays ATTRACTEURS/EXCLUSIONS/PENTES/COUVERT, sync TERRAIN_AWARE_Ω + BIOLOGIE_AWARE_Ω, guard fallback, bouton INSPEC toolbar** | **✅ INSPECTION_BIO_MODE_ACTIVE 2026-04-21** |
| **INSPECTION_BIO_GEOMETRY_BINDING** | **Branchement Leaflet des 4 couches (4 panes z-index 445/448/452/455, buildInspectionBioFeatures, rendu conditionnel PRO/EXPERT, event inspection-bio-changed)** | **✅ INSPECTION_BIO_GEOMETRY_RENDERED 2026-04-21** |
| **INSPECTION_BIO_FILTERING_Ω (ENFORCE_URBAN_EXCLUSION)** | **4 filtres Ω institutionnels (EXCLUSION/HABITAT/TERRAIN/BIOLOGIE_AWARE_Ω) + 7 tests Jest + comptage rejets + interdiction rendu brut** | **✅ INSPECTION_BIO_FILTERING_ENFORCED 2026-04-21** |
| **NUTRITION_SALINES_BINDING_Ω (INTEGRATED_WITH_FILTERING)** | **Purification nutrition autonome + binding exclusif saline↔nutrition + panneau NUTRITION_PANEL_Ω 11 sections au dblclick + intégration 4 filtres Ω + 11 tests Jest** | **✅ NUTRITION_SALINES_BOUND 2026-04-21** |
| **XII_SUPRA_M — IMPLANTATION_X1000** | **Densification additive engines (phase_b_engines + territoire_v10_supra) : +4 champs terrain (impervious_pct/urban/industrial/port) + 4 critères d'exclusion Ω (portuaire/industrielle/urbaine/infrastructure) ; registre V30 inchangé (hash préservé)** | **✅ IMPLANTATION_X1000_ACTIVE 2026-04-21** |
| **XIII_RECALCUL_ORGANIC_Ω** | **Consommation des métadonnées densifiées par les scorings (zones + affûts + hotspots) + EXCLUSION_AWARE_Ω appliquée à la source + marqueur `recalcul_organic_omega: true` sur toutes les features + 0 fallback** | **✅ RECALCUL_ORGANIC_OMEGA_ACTIVE 2026-04-21** |
| **XIV_CRITICAL_FUNCTIONAL_PARITY_Ω** | **Audit complet pipeline TERRITOIRE + 2 bugs corrigés (species props manquant + dblclick Leaflet bloqué par zoom natif) + 11 tests Jest sentinelles BLOQUANTS (merge refusé si cassent) ; total 29/29 Jest PASS** | **✅ FUNCTIONAL_PARITY_RESTORED 2026-04-21** |
| **XV_CONTAMINATION_PARITY_CI_LOCK_Ω** | **Parité contamination (toggle unifié + `window.__CONTAMINATION_STATE__` + messages explicites) + CI Gate pre-commit Git installé (/app/.git/hooks/pre-commit) + 39 tests sentinelles PASS + 4 sécurités institutionnelles réactivées (BCE4X/STEEVE-MAX/ANTI-REGRESSION/ENGINE_REGISTRY_LOCK)** | **✅ CONTAMINATION_PARITY_CI_LOCK_ACTIVE 2026-04-21** |

## 5. Tâches P1 / P2

### P1 — PHASE XII-SUPRA-M OPTIMIZATION x1000 (PREVIEW LIVRÉ 2026-04-21)

📋 **PREVIEW EN ATTENTE DE VALIDATION COMMANDANT**

Fichiers livrés :
- `/app/memory/PHASE_M_PREVIEW/ZONES_X1000_DESCRIPTION.md` (15 sections)
- `/app/memory/PHASE_M_PREVIEW/SALINES_X1000_DESCRIPTION.md` (15 sections)
- `/app/memory/PHASE_M_PREVIEW/HOTSPOTS_X1000_DESCRIPTION.md` (15 sections)
- `/app/memory/PHASE_XII_SUPRA_M_OPTIMIZATION_REPORT_PREVIEW.md`

**Aucune modification d'engine effectuée.** Attente de l'ordre explicite :
`"VALIDÉ — PROCÉDER À L'IMPLANTATION"` pour :
1. Implanter `hotspots_organic_v1.py` (gap ×1200)
2. Implanter `zones_organic_v1.py` (gap ×800)
3. Implanter `salines_organic_v1.py` (gap ×150)
4. Exécuter SELF-AUDIT-Ω 60/60 x3 + bump Registry V30
5. Institutionnaliser : 41 → 44 engines

### P2 — Upload manuel `CriticalHabitat.zip`
Contournement pare-feu (action Commandant requise).

## 6. Credentials

```
Admin : steeve-max-capture@huntiq.com / Saturn5858*
```

## 7. Registry officiel courant

```
VERSION  : V29-SUPRA-LOCKED-PHASE-XI-SUPRA-N-Ω-STABILIZED-2026-04
SEALED_AT: 2026-04-21T00:00:00Z
SHA-256  : 29e1ee187e429bdd9a055dacea7770a921ed5f57d49cf838c733557f442b2add
ENGINES  : 41
AUDIT    : 60/60 stable x3
```

## 8. Health Check courant

- ✅ Backend : RUNNING (uvicorn, port 8001, supervisor)
- ✅ Frontend : RUNNING (port 3000)
- ✅ MongoDB : RUNNING
- ✅ Self-Audit-Ω : 60/60 CONFORME stable
- ⚠️ Open-Meteo rate-limit (mitigé par durcissement défensif Phase N-STAB)

## 9. Fichiers critiques de référence

- `/app/backend/engines/v8_institutional/engine_ia_corridors_organic_omega.py`
- `/app/backend/engines/v8_institutional/self_audit_omega.py` (V30)
- `/app/backend/engines/v8_institutional/registry_lock_omega.py` (V30)
- `/app/backend/engines/v8_institutional/sla_baseline_omega.py`
- `/app/memory/ENGINE_REGISTRY_LOCKED.md`
- `/app/memory/PHASE_XII_SUPRA_S_ACTIVATION_EN_PRODUCTION_REPORT.md` (clôture officielle)
- `/app/memory/LOCK_STATE_SECURE_OMEGA.md` (snapshot scellement)
- `/app/memory/PHASE_XI_SUPRA_N_STABILIZATION_REPORT.md`
- `/app/memory/PHASE_XI_SUPRA_N_NETWORK_REFACTOR_REPORT.md`
a_baseline_omega.py`
- `/app/memory/ENGINE_REGISTRY_LOCKED.md`
- `/app/memory/PHASE_XI_SUPRA_N_STABILIZATION_REPORT.md`
- `/app/memory/PHASE_XI_SUPRA_N_NETWORK_REFACTOR_REPORT.md`
