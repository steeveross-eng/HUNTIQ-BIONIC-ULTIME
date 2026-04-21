# PLAN_MAINTENANCE_Ω — TERRITOIRE
> **Ordre :** `PHASE_ZERO_PLUS_CONSOLIDATION_GOUVERNANCE_Ω` — X30
> **Cadence :** Continue
> **Responsable :** Équipe Emergent

## Périmètre
Maintenir l'environnement TERRITOIRE (frontend + backend + CI + registre Ω)
dans un état fonctionnel permanent, sans dégradation furtive.

## Checklists de maintenance

### Quotidienne (automatique)
- [ ] Hook `pre-commit` Jest exécuté sur chaque commit TERRITOIRE
- [ ] `yarn test --watchAll=false` → 57/57 PASS
- [ ] Supervisor : backend + frontend RUNNING
- [ ] Endpoint `/api/omega/ci-status` → `status:"OK"`

### Hebdomadaire (manuelle)
- [ ] Vérification SHA-256 V30 (`registry_lock_omega.py`)
- [ ] Contrôle `LOCK_STATE_SECURE_OMEGA.md` à jour
- [ ] Audit `fallback`/`raw`/`bypass` via `grep -rE "bypass|raw_render" /app/frontend/src`
- [ ] Vérification absence de dépendances orphelines (`yarn list`, `pip check`)

### Mensuelle (rapport signé)
- [ ] Relecture institutionnelle du `/app/memory/PHASE_ZERO_AUDIT_REPORT_Ω.md`
- [ ] Mise à jour `LOCK_STATE_SECURE_OMEGA.md` si phases nouvelles
- [ ] Signature du Commandant sur rapport mensuel

## Outils de maintenance
| Outil | Emplacement | Usage |
|---|---|---|
| Jest runner | `/app/frontend/` | `yarn test` |
| Pre-commit hook | `.git/hooks/pre-commit` | Bloquant TERRITOIRE |
| Self-audit Ω | `backend/engines/v8_institutional/self_audit_omega.py` | Lecture seule |
| Registry lock | `backend/engines/v8_institutional/registry_lock_omega.py` | V30 — figé |
| CI_STATUS endpoint | `/api/omega/ci-status` | Dashboard live |

## Procédure d'ajout d'une phase
1. Émettre ordre signé du Commandant
2. Vérifier `PHASE_LOCK_GATE_Ω.md` → conditions remplies
3. Créer `/app/memory/PHASE_XVII_<NOM>_ORDER.md` (ordre reçu)
4. Exécuter la phase en lecture-écriture strictement scopée
5. Ajouter tests Jest sentinelles (+N tests)
6. Exécuter `yarn test` → tous verts
7. Mettre à jour `LOCK_STATE_SECURE_OMEGA.md`
8. Signer rapport de clôture `/app/memory/PHASE_XVII_*_REPORT.md`

## Dépendances critiques
- Node 20+ / Yarn (frontend)
- Python 3.11+ / FastAPI / MongoDB (backend)
- Jest + React Testing Library (tests)
- Git + hook `pre-commit`

## Signature
Agent Emergent — sous autorité COMMANDANT STEEVE-MAX
