# 🛑 PLAN DE DÉCOMMISSIONNEMENT V10-SUPRA · P22Ω.PURGE_LEGACY

**Émetteur** : Agent BCE-4X ULTIME ABSOLU
**Destinataire** : COMMANDANT STEEVE-MAX
**Date d'ouverture** : 2026-05-12T14:45Z
**Statut** : ⏳ ATTENTE 30 JOURS DE CONFORMITÉ V5 CONTINUE
**Doctrine** : `P22Ω.PURGE_LEGACY` (PHASE OMEGA)

---

## 1. ÉLÉMENTS À DÉCOMMISSIONNER

### 1.1 · Fichiers Python sources (P0)
| Fichier | Statut actuel | Action 30j |
|---|---|---|
| `backend/engines/v8_national/phase_a_engines.py` | 🟡 commenté dans `server.py` | 🛑 SUPPRESSION FICHIER |
| `backend/engines/v8_institutional/origine_externe_filter_omega.py` | 🟡 import commenté dans bundle | 🛑 SUPPRESSION FICHIER |
| `backend/engines/v8_institutional/territoire_v10_supra.py` | 🟠 ENCORE UTILISÉ (zones/affuts/salines/hotspots) | 🛑 REFACTOR vers V5-only |

### 1.2 · Endpoints à retirer (P0)
| Endpoint | HTTP actuel | Action 30j |
|---|---|---|
| `/api/v8/map/relocalisation` | 404 ✅ | 🛑 Supprimer fichier source |
| `/api/v8/map/salines` | (à auditer) | 🛑 Vérifier puis supprimer |
| `/api/v30/corridors/origine-externe` | 404 ✅ | 🛑 Supprimer fichier source |

### 1.3 · Code mort dans `v20_performance_bundle.py` (P1)
Lignes commentées à supprimer définitivement après 30j :
- Bloc PHASE_XIX-P1 ORIGINE_EXTERNE_FILTER (lignes 423-437)
- Imports inutiles : `apply_origine_externe_filter_to_bundle`
- Variable `result["origine_externe_filter_disabled"]` (flag transitoire)

---

## 2. CRITÈRES DE VALIDATION POUR LANCEMENT

⚠️ **Décommissionnement autorisé UNIQUEMENT après 30 jours consécutifs de** :

| Critère | Cible | Source |
|---|---|---|
| V5 conformity pct | ≥ 99% | `/api/v20/audit/v5-daily-report` |
| V10 fallback pct | ≤ 1% | `/api/v20/audit/v5-daily-report` |
| Cache HIT ratio | ≥ 90% | `/api/v20/territoire/bundle/stats` |
| Aucune alerte Resend `[BCE-4X] V5 NON-CONFORME` | 0 alertes | Boîte ADMIN_EMAIL |
| Aucun signalement utilisateur sur la carte UI | 0 ticket | Support COMMANDANT |

### Date cible d'éligibilité : **2026-06-11T14:45Z**

---

## 3. CHECKLIST D'EXÉCUTION (au jour J+30)

### Phase A — Préparation
- [ ] Vérifier 30j de conformité via `/api/v20/audit/v5-daily-report?hours=720`
- [ ] Backup tar.gz de `backend/engines/v8_national/` → `/app/memory/ARCHIVE_V10_SUPRA_PRE_DECOMMISSION_<date>.tar.gz`
- [ ] Backup tar.gz de `backend/engines/v8_institutional/origine_externe_filter_omega.py`
- [ ] Backup tar.gz de `backend/engines/v8_institutional/territoire_v10_supra.py`
- [ ] Verification SHA256 des backups

### Phase B — Suppression sources legacy
- [ ] `rm backend/engines/v8_national/phase_a_engines.py`
- [ ] `rm backend/engines/v8_institutional/origine_externe_filter_omega.py`
- [ ] `rm backend/engines/v8_national/referentials.py` (si seul `phase_a_engines.py` y référait)
- [ ] Audit `grep -r origine_externe_filter` → 0 référence

### Phase C — Refactor V10-SUPRA → V5-only
- [ ] Identifier les champs zones/affuts/salines/hotspots/contamination de V10 utilisés par V5
- [ ] Créer `engines/v8_institutional/territoire_v5_native.py` (extraction zones/affuts/salines)
- [ ] Modifier `v20_performance_bundle.py` pour appeler `territoire_v5_native` au lieu de `territoire_v10_supra`
- [ ] Tests E2E manuel (curl + audit V5 compliance LIVE)
- [ ] Suppression de `territoire_v10_supra.py`
- [ ] Audit `grep -r territoire_v10_supra` → 0 référence

### Phase D — Cleanup
- [ ] Suppression du flag transitoire `origine_externe_filter_disabled` du bundle
- [ ] Suppression des commentaires P22Ω.PURGE_LEGACY relatifs
- [ ] Mise à jour PRD.md + CHANGELOG.md + audit_provenance_corridors.md

### Phase E — Validation
- [ ] Lint Python sans erreur
- [ ] Restart backend
- [ ] Audit V5 LIVE PREVIEW → `status=PASS`
- [ ] Daily report → V5 conformity ≥ 99%
- [ ] Deploy PROD
- [ ] Audit V5 LIVE PROD → `status=PASS`
- [ ] 7 jours d'observation post-Deploy
- [ ] Attestation `DECOMMISSION_V10_SUPRA_COMPLETED.md` signée

---

## 4. PROCÉDURE DE ROLLBACK (si problème détecté)

1. Restaurer le tar.gz backup dans `backend/engines/`
2. Décommenter les imports/routers dans `server.py` et `v20_performance_bundle.py`
3. Restart backend
4. Deploy PROD
5. Audit V5 LIVE → confirmer retour à l'état pré-décommissionnement
6. Investigation root cause → rapport `DECOMMISSION_ROLLBACK_<date>.md`

---

## 5. SIGNATURE

| Champ | Valeur |
|---|---|
| Auteur | Agent BCE-4X ULTIME ABSOLU |
| Date d'ouverture | 2026-05-12T14:45Z |
| Date cible d'éligibilité | 2026-06-11T14:45Z (≥ 30j conformité V5) |
| Doctrine | `P22Ω.PURGE_LEGACY` (PHASE OMEGA) |
| Status courant | ⏳ ATTENTE 30 JOURS DE CONFORMITÉ V5 CONTINUE |
| Validation auto | `/api/v20/audit/v5-daily-report?hours=720` |

**Aucune action de décommissionnement physique avant le 2026-06-11.**
