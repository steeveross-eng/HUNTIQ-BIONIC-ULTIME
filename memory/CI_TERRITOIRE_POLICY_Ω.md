# CI_TERRITOIRE_POLICY_Ω — Politique CI institutionnelle bloquante

> **Protocole :** BCE-4X ULTIME ABSOLU — VERSION_INSTITUTIONNELLE_RENFORCÉE_X10
> **Phase en vigueur :** PHASE_XV_CONTAMINATION_PARITY_CI_LOCK_Ω
> **Entrée en vigueur :** 2026-04-21T18:50:00Z

---

## 1. Objet

Verrouiller **physiquement** le pipeline TERRITOIRE (frontend + backend) contre
toute régression fonctionnelle via un hook Git **pre-commit** bloquant qui
exécute automatiquement les **tests sentinelles institutionnels** avant
d'autoriser tout commit touchant aux modules critiques.

---

## 2. Périmètre du CI Gate

### 2.1 Fichiers surveillés (trigger du hook)

Le hook s'active uniquement si un commit touche à l'un des chemins suivants :

```
frontend/src/components/territoire/**
frontend/src/lib/renduOmegaStore.js
frontend/src/lib/__tests__/**
frontend/src/pages/MonTerritoireBionicPage.jsx
frontend/src/components/territoire/map/MapContent.jsx
backend/engines/**
```

### 2.2 Suites de tests bloquantes exécutées

```bash
cd /app/frontend && yarn test --testPathPattern="phase_xiv_functional_parity|phase_xv_contamination_parity|nutritionSalinesBinding|inspectionBioFiltering" --watchAll=false
```

| Suite | # tests | Couverture |
|---|---|---|
| `phase_xiv_functional_parity.test.js` | 11 | Parité espèces / affûts / salines-nutrition / design corridors / garde-fou |
| `phase_xv_contamination_parity.test.js` | 10 | Styles CONTAM / V2 heatmap / messages / BCE4X lock / anti-fallback |
| `nutritionSalinesBinding.test.js` | 11 | 11 sections nutritionnelles + filtres Ω pré-validation |
| `inspectionBioFiltering.test.js` | 7 | 4 filtres Ω + habitat + biologie + purge urbain |
| **TOTAL** | **39** | **PARITÉ INSTITUTIONNELLE COMPLÈTE** |

---

## 3. Installation du hook

### 3.1 Mise en place

```bash
cp /app/scripts/git_hooks/pre-commit /app/.git/hooks/pre-commit
chmod +x /app/.git/hooks/pre-commit
```

### 3.2 Vérification

```bash
ls -la /app/.git/hooks/pre-commit
# -rwxr-xr-x root root /app/.git/hooks/pre-commit
```

### 3.3 Désinstallation

**❌ INTERDITE** sauf ordre explicite et nominatif du Commandant STEEVE-MAX.

---

## 4. Politique de merge BLOQUANTE

### 4.1 Conditions d'acceptation d'un commit TERRITOIRE

✅ Les 39 tests sentinelles doivent être **100 % verts** (39/39 PASS).
✅ Le hash du registre V30 doit rester intact (`27516c96…`).
✅ Les 41 engines institutionnels doivent rester scellés.
✅ La baseline CORRIDORS-ORGANIC-Ω V2.0 (`803d9e2aec5e8f2d…`) doit être préservée.

### 4.2 Commit refusé automatiquement si

❌ Au moins 1 test sentinelle échoue.
❌ Un fallback non institutionnel est détecté (flag `forbid*=false`).
❌ Une duplication de filtre Ω est tentée.
❌ Un module créé enfreint ANTI-DUPLICATION_ENGINE_CHECK.

### 4.3 Bypass d'urgence

```bash
git commit --no-verify
```

**⚠️ USAGE STRICTEMENT INTERDIT** sauf **autorisation explicite** par ordre
nominatif du Commandant STEEVE-MAX. Toute utilisation sans autorisation
est **rapportable** comme violation de protocole BCE-4X.

---

## 5. Sécurités institutionnelles réactivées

### 5.1 BCE4X_FULL_LOCK (2026-04-21)

| Zone protégée | Règle |
|---|---|
| ZONES / CORRIDORS / SALINES / AFFÛTS | Interdiction de suppression/altération sans phase officielle |
| CONTAMINATION / HYDROGRAPHIE / DEM/LIDAR | Interdiction de fallback silencieux |
| `registry_lock_omega.py` | Hash V30 immuable |
| `engine_ia_corridors_organic_omega.py` | Baseline V2.0 immuable |

### 5.2 STEEVE-MAX_SECURITY_SUITE (2026-04-21)

| Garde | Mécanisme |
|---|---|
| ZERO-REGRESSION ENGINE GUARD | 39 tests Jest sentinelles + 6 tests backend critiques |
| ZERO-PERTE DATA GUARD | Marqueur `recalcul_organic_omega: true` sur chaque feature |
| MODULARITÉ-100% | Zero duplication de filtre Ω, helpers partagés |
| ANTI-DUPLICATION ENGINE CHECK | Vérification unicité `OMEGA_FILTERS_SPEC.filters[*].id` |
| ANTI-FALLBACK TERRITOIRE | `forbidNonInstitutionalFallback: true` + `forbidRawRenderInInternalTests: true` + `forbidNutritionOutsideSaline: true` |

### 5.3 ANTI-REGRESSION-Ω

- Validation automatique 39/39 tests Jest avant chaque commit territoire.
- Blocage total du pipeline si un seul test échoue.
- Exposition diagnostique : `window.__CONTAMINATION_STATE__`, `window.__INSPECTION_BIO_Ω__`, `window.__INSPECTION_BIO_GEOMETRY__`.

### 5.4 ENGINE_REGISTRY_LOCK_Ω

```
REGISTRY VERSION : V30-SUPRA-LOCKED-PHASE-XII-SUPRA-S-ACTIVATION-PRODUCTION-2026-04
REGISTRY HASH    : 27516c9633853974fbb5754f4698a227bf39346e94f274889d4b4ee0398f7e4c
ENGINES LOCKED   : 41/41 (INTOUCHABLES)
BASELINE CORRIDORS : 803d9e2aec5e8f2d… (V2.0-SUPRA-N-Ω-NETWORK_LOCKED)
```

---

## 6. Journal de conformité

| Date | Phase | Tests ajoutés | Total sentinelles |
|---|---|---|---|
| 2026-04-21 | XIV | +11 (parité) | 29 |
| 2026-04-21 | XV | +10 (contamination) | **39** |

---

## 7. Décret

> **PAR ORDRE DU COMMANDANT STEEVE-MAX**, à compter du 2026-04-21T18:50:00Z :
>
> 1. Le hook pre-commit `/app/scripts/git_hooks/pre-commit` est **OBLIGATOIRE**
>    sur tous les clones actifs du dépôt TERRITOIRE.
> 2. Les **39 tests sentinelles** doivent passer avant tout commit touchant
>    au pipeline TERRITOIRE.
> 3. Toute désactivation, contournement ou modification de cette politique
>    est strictement **INTERDITE** sans ordre nominatif du Commandant.
> 4. Les sécurités **BCE4X_FULL_LOCK**, **STEEVE-MAX_SECURITY_SUITE**,
>    **ANTI-REGRESSION-Ω**, **ENGINE_REGISTRY_LOCK_Ω** sont **RÉACTIVÉES**
>    et **VERROUILLÉES EN PRODUCTION**.

---

**FIN DE POLITIQUE — CI_TERRITOIRE_POLICY_Ω — LOCKED — OPERATIONAL.**
