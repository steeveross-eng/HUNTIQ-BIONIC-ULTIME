# HUNTIQ-V6/V7 — Product Requirements Document
## GOLDEN-BCE-4X | STEEVE-MAX Protocol

---

## Original Problem Statement
Reconstruction et evolution du projet HUNTIQ (V6→V7), une application modulaire full-stack
(FastAPI + React + MongoDB) dediee a la chasse intelligente. Le projet suit un protocole
strict de gouvernance (GOLDEN-BCE-4X / STEEVE-MAX) avec validation explicite a chaque phase.

## Core Requirements
- Architecture modulaire avec 90+ engines backend
- Master Switch central controlant tous les modules publics
- Protocole ZERO PERTE, ZERO REGRESSION
- Toutes les modifications sur branche `Work1`
- Validation STEEVE-MAX obligatoire avant chaque action majeure

## User Personas
- **STEEVE-MAX**: Administrateur/proprietaire, autorite ultime sur toutes les decisions
- **Chasseurs**: Utilisateurs finaux (non actifs — systeme en mode LOCKED)

---

## What Has Been Implemented

### Phase Import & Governance (Complete)
- Clone bionic-v3-dev, inventaire, archive ZIP
- GOVERNANCE.md, EMERGENT_PROTOCOL.md, SECURITY_POLICY.md
- Branche Work1 creee et active

### Audits Complets (Complete)
- Engine Audit: 84+ modules verifies
- Coherence Audit (Phase 5B): duplications identifiees
- Historical Audit (Phase 5C): V1-V6 compares, auto_optimization restaure
- V5 Module Audit (x1500): 10 modules predictifs audites, 7 complets mais inactifs
- V5 Module Documentation (x1700): Modes d'emploi et UI plans pour 10 modules
- Admin/Admin Premium Audit (x1800): 29 modules audites, plan de refonte complet

### SALINE INTELLIGENCE ULTRA (Complete)
- 7 moteurs scientifiques backend
- Integration Stripe e-commerce
- Frontend immersif
- 100% pass rate testing agent

### P0 Admin Refactor (STEEVE-MAX x1900) — Complete (2026-03-25)
- 22 switches publics crees dans Master Switch
- Master Switch Guard (dependency injectable) avec 35 module mappings
- 10 modules obsoletes/dupliques retires de CORE_ROUTERS (81→71)
- 6 fusions executees (admin, strategy x2, geospatial, geolocation, collaborative)
- Deduplication Parametres & Maintenance
- Mode systeme LOCKED — tous switches OFF jusqu'a directive x3000
- Rapport: `audit/p0_admin_refactor_done.md`

---

## Prioritized Backlog

### P0 (COMPLETE)
- ~~Refactoring Admin Premium~~

### P1 — En attente directive STEEVE-MAX x2000
- Integration UI des 10 modules predictifs V5 (Mon Territoire, Intelligence, Vision Faune, etc.)
- Activation et enregistrement des 7 modules predictifs dans server.py
- Connexion modules predictifs au Master Switch
- Documentation des 5 modules complexes (SEO 51ep, affiliate_ads 24ep, marketing 22ep)
- Securisation des 8 modules dangereux

### P2 — Futur
- BSAA-2: Implementation BIONIC Social Ads Automation
- Completion des 6 modules partiels (<=50%)
- Ecosysteme unifie + moteur ecologique central (directive x2000)

### P3 — Long terme
- Merge Work1 → main
- Nettoyage repos historiques
- Mise a jour archive ZIP finale

---

## Architecture
```
/app/HUNTIQ-V6-import/
  backend/
    modules/ (71 modules actifs dans CORE_ROUTERS)
      master_switch/ (22 switches + guard.py)
      admin_engine/ (module admin unique, 1485L)
      saline_engine/ (7 moteurs scientifiques)
      bionic_engine_p0/ (moteur principal territoire)
      ... (65+ autres modules)
    server.py (point d'entree)
    server_orchestrator.py (registration)
  frontend/
    src/pages/SalineIntelligencePage.jsx
    src/theme/bionic_theme.css
  audit/ (12+ rapports)
  architecture/ (6+ specs)
```

## Key Decisions
- Master Switch en mode LOCKED jusqu'a STEEVE-MAX x3000
- admin_engine est le module admin unique (admin_unified retire)
- strategy_master_engine est le module strategie unique
- networking_engine absorbe collaborative_engine
- Dossiers physiques des modules retires conserves (ZERO PERTE)

---

**Derniere mise a jour:** 2026-03-25 — P0 Complete
**Branche active:** Work1
