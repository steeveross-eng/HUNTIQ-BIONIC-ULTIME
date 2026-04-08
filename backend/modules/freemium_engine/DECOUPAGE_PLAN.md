# R8.3 — Preparation Decoupage freemium_engine
# BCE-4X GOLDEN V6+ | STEEVE-MAX | ZERO ABSOLU
# STATUS: PREPARATION UNIQUEMENT — Aucune execution

## Etat actuel (post-R7)

```
modules/freemium_engine/
  __init__.py
  router.py (337 lignes — CRUD subscription + pricing + check-access)
  services/
    __init__.py
    upsell_notifier.py
```

`premium_guard.py` (272 lignes — tier gating, guards Depends(), source unique TIER_LIMITS)

## Architecture cible (R9 ou post-SUPRA)

```
modules/freemium_engine/
  __init__.py
  router_subscription.py   <-- CRUD subscription (get, upgrade)
  router_pricing.py         <-- Pricing + tier comparison
  router_access.py          <-- check-access + quota endpoints (delegue a premium_guard)
  services/
    __init__.py
    upsell_notifier.py
```

## Plan de decoupage

### 1. router_subscription.py (Extraction depuis router.py)
- Endpoints: `/subscription/{user_id}`, `/subscription/upgrade`
- Logique: CRUD pure sur collection `subscriptions`
- Dependances: MongoDB, datetime

### 2. router_pricing.py (Extraction depuis router.py)
- Endpoints: `/pricing`, `/tiers/compare`, `/` (info)
- Logique: Lecture seule des constantes TIER_LIMITS, FEATURES, PRICING
- Dependances: premium_guard.TIER_LIMITS

### 3. router_access.py (Extraction depuis router.py)
- Endpoints: `/check-access`, `/quota/{user_id}/{feature}`, `/quota/{user_id}/{feature}/increment`, `/upsell-events/{user_id}`
- Logique: Delegation a premium_guard.check_quota + premium_guard._get_user_tier
- Dependances: premium_guard, upsell_notifier

### 4. __init__.py (Mise a jour)
- Importer les 3 sous-routeurs
- Maintenir la compatibilite prefix `/api/v1/freemium`

## Contraintes ZERO ABSOLU
- Aucun changement d'URL d'endpoint
- Aucun changement de structure de reponse
- Aucun impact frontend
- Tests identiques pre/post decoupage
- Validation Commandant requise avant execution

## Estimation
- Effort: Faible (decoupage pur, aucune logique nouvelle)
- Risque: Minimal (pas de changement fonctionnel)
- Prerequis: Validation Commandant STEEVE-MAX
