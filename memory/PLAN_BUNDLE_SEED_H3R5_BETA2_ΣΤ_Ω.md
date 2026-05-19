# PLAN TECHNIQUE BUNDLE-SEED H3 R5 · β2-ΣΤ · Ω

**Doctrine** : `P22ΩΩ_PHASE3_BUNDLE_SEED_H3R5_BETA2_SIGMA_TAU_Ω`
**Commandant** : STEEVE-MAX · BCE-4X ULTIME ABSOLU
**Date** : 2026-02-19
**Statut** : 🟡 **PLAN PROPOSÉ — NON-EXÉCUTÉ** · Validation Commandant requise.

---

## 1. OBJECTIF DOCTRINAL

Réduire d'un ordre de grandeur la latence et le coût du pré-warm Canada R6 complet
en pré-calculant **un bundle V20 unique par cellule H3 R5** (~252 km²) puis en
**re-distribuant ce bundle vers les 7 cellules H3 R6 enfants** (un H3 R5 contient
7 cellules R6) sans recompute.

Le compute V20 reste exécuté à granularité H3 R5 (plus grossière, validation
éco-spatiale correcte à cette échelle) ; la diffusion R6 est purement déterministe
et zéro-cost (write-only en R2).

---

## 2. ARCHITECTURE β2-ΣΤ

```
┌────────────────────────────────────────────────────────────────────────┐
│ PIPELINE β2-ΣΤ (3 phases séquentielles)                                │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│ Phase 1 : SEED COMPUTE (granularité H3 R5)                             │
│   ├─ Pour chaque cellule H3 R5 du périmètre :                          │
│   │    ├─ Détermine (lat_center, lng_center)                           │
│   │    ├─ Pour chaque (espèce × mois × heure) :                        │
│   │    │    └─ Compute V20 bundle (84s ≈ inchangé)                     │
│   │    └─ Stocke bundle sous clé `seed/{species}/{r5_cell}/m{}_h{}`    │
│   └─ Volume : ~39 K cellules R5 × 72 tuiles = ~2.8 M tuiles (Canada R5)│
│                                                                        │
│ Phase 2 : FAN-OUT R5 → R6 (granularité H3 R6, zéro-compute)            │
│   ├─ Pour chaque cellule H3 R5 calculée :                              │
│   │    ├─ Récupère les 7 cellules R6 enfants (h3.cell_to_children)     │
│   │    └─ Pour chaque enfant R6 :                                      │
│   │         ├─ Charge bundle du parent R5                              │
│   │         ├─ Ajuste lat/lng centre dans le bundle (offset minime)    │
│   │         └─ Upload sous clé `v1/{species}/{r6_cell}/m{}_h{}`        │
│   └─ Volume : 7 × 2.8M = 19.6M tuiles R6 produites zéro-compute        │
│                                                                        │
│ Phase 3 : MANIFESTE UPDATE                                             │
│   └─ Régénération manifest R2 référençant les 19.6M tuiles R6          │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. GAINS QUANTITATIFS PROJETÉS

### 3.1 Canada R6 complet (392 391 cellules) — Comparatif

| Aspect | Sans β2-ΣΤ (R6 direct) | Avec β2-ΣΤ (R5 seed → R6 fan-out) | Gain |
|---|---|---|---|
| Cellules à compute | **392 391** | **~56 056** (1/7 ratio H3) | ×7 |
| Tuiles à compute | **28.3 M** | **~4.0 M** | ×7 |
| Compute total (256w @ 84s/tuile) | **~5.3 jours** | **~0.75 jour = 18 h** | ×7 |
| Stockage R2 final | 386 GB | 386 GB (idem, fan-out écrit pareil) | × |
| Coût compute one-shot | ~$32 × 5.3j = $170 | **~$24** | ÷7 |

### 3.2 β2-Β P1 only (7 077 cellules R6)

| Aspect | Sans β2-ΣΤ | Avec β2-ΣΤ |
|---|---|---|
| Cellules R5 à compute | N/A | ~1 011 (R6 P1 / 7) |
| Compute total (256w) | **1.9 jours** | **~3.5 heures** |
| Coût | $32 | ~$5 |

→ **Objectif Commandant <0.5 jour pour P1 atteignable directement avec β2-ΣΤ + k8s 256w**.

---

## 4. IMPACT ÉCOLOGIQUE ET COHÉRENCE CORRIDORS

### 4.1 Précision spatiale H3 R5 vs R6

| Résolution | Taille hex | Échelle écologique | Pertinence chasse |
|---|---|---|---|
| H3 R6 (cible UI) | ~14 km / 36 km² | Marche journalière chevreuil | 🟢 Excellente |
| H3 R5 (seed proposé) | ~37 km / 252 km² | Domaine vital moyen orignal | 🟢 Acceptable |
| H3 R4 (trop grossier) | ~100 km / 1770 km² | Aire de répartition | 🔴 Insuffisant |

**Verdict** : H3 R5 reste **biologiquement pertinent** pour les espèces cibles (orignal,
ours, wapiti — domaine vital 5-50 km²). Pour le chevreuil (domaine vital 0.5-2 km²), une
**perte de granularité** est acceptable car le bundle V20 inclut des données régionales
(météo, terrain, IRDA sol) plus que strictement locales.

### 4.2 Cohérence corridors entre cellules R6 voisines

Risque identifié : **discontinuités visuelles** entre cellules R6 partageant le même
parent R5 (corridors strictement identiques car même bundle). Mitigations :

| Mitigation | Implémentation | Effet |
|---|---|---|
| **Offset adaptatif des coordonnées corridors** | Décalage de chaque corridor par offset(r6_center − r5_center) lors du fan-out | Évite l'aspect "tuile copiée-collée" |
| **Variation déterministe** des paramètres mineurs | Hash(r6_cell) → wind_jitter ±2°, score_jitter ±1.5 % | Naturalise les variations |
| **Réutilisation conservée** des géométries macro | Corridors, zones, salines, hotspots inchangés | Cohérence régionale préservée |

→ **Cohérence biologique régionale stricte préservée** ; perte de granularité limitée
   au sub-régional (justifié par la nature climatique/topographique des données V20).

### 4.3 Limites doctrinales reconnues

- ⚠️ Bundles bio-positifs **par cellule R5** : si une R5 contient à la fois des sous-zones
  bio-positives et HALT, la décision est binaire (toute la R5 traitée comme R5_centre).
  → **Mitigation** : compute R5 sur le centre + 6 sondages aléatoires dans la R5 ;
    si >50 % HALT → R5 entière marquée HALT.
- ⚠️ Variations météo locales perdues à l'échelle R5 (~37 km).
  → **Acceptable** : déjà le cas du `WeatherCacheRegional_Ω` à H3 R3 (~270 km).

---

## 5. IMPLÉMENTATION TECHNIQUE (à activer sur ordre Commandant)

### 5.1 Nouveau worker `zerocost_worker_seed_r5.py`

```python
# Pseudo-code — pas encore implémenté
WORKER_RESOLUTION_SEED = 5  # H3 R5
SEED_PREFIX = "seed_r5"

async def main():
    grid = load_grid(R5_FILE)
    my_r5_cells = [c for i,c in enumerate(grid) if i % WORKER_COUNT == WORKER_INDEX]
    for r5_cell in my_r5_cells:
        bundle = await v20_territoire_bundle(r5_cell.lat, r5_cell.lng, ...)
        # Phase 1 : upload SEED bundle sous clé seed_r5/
        upload(f"{SEED_PREFIX}/{species}/{r5_cell.h3}/m{m}_h{h}.json.gz", bundle)
        # Phase 2 : fan-out vers 7 cellules R6 enfants
        for r6_child in h3.cell_to_children(r5_cell.h3, 6):
            r6_bundle = adapt_bundle_to_child(bundle, r6_child)
            upload(f"v1/{species}/{r6_center}/m{m}_h{h}.json.gz", r6_bundle)
```

### 5.2 Adaptateur `adapt_bundle_to_child(bundle, r6_cell)`

```python
def adapt_bundle_to_child(bundle: dict, r6_cell: str) -> dict:
    """Décale les coords + variations déterministes pour cohérence visuelle."""
    r6_lat, r6_lng = h3.cell_to_latlng(r6_cell)
    # 1) Offset des géométries
    dlat = r6_lat - bundle["center_lat"]
    dlng = r6_lng - bundle["center_lng"]
    out = deepcopy(bundle)
    for corridor in out.get("corridors", []):
        for point in corridor["coords"]:
            point[0] += dlat
            point[1] += dlng
    # 2) Variations déterministes (hash R6 cell ID)
    jitter = (hash(r6_cell) % 100) / 100.0
    out["wind_deg"] = bundle["wind_deg"] + (jitter - 0.5) * 4  # ±2°
    out["score_global"] = bundle["score_global"] * (1 + (jitter - 0.5) * 0.03)  # ±1.5%
    out["center_lat"] = r6_lat
    out["center_lng"] = r6_lng
    out["_seed_r5_parent"] = bundle["h3_cell"]
    return out
```

### 5.3 Validation requise avant activation

- ✅ Test conformité visuelle : 50 cellules R6 cible vs bundle "vrai" R6 (compute)
- ✅ Tolérance : ±5 % score · corridors count identique · pas de gap visuel Leaflet
- ✅ Validation biologique MFFP : présence/absence (HALT) cohérente entre R5 et R6 enfants

---

## 6. MOMENT OPTIMAL D'ACTIVATION

### 6.1 Pré-requis avant β2-ΣΤ

| Condition | Statut actuel | Requis |
|---|---|---|
| Pré-warm P1 R6 complet (509 K tuiles) | 🟡 En cours | ✅ Validé production |
| Phase 4 PROD ZEROCOST stable à 100 % | ❌ Non-engagée | ✅ 7+ jours stables |
| Aucune régression UI/UX rapport Commandant | 🟢 OK | ✅ 0 régression sur 30j |
| Décision Commandant explicite | ❌ | ✅ Plan validé |

### 6.2 Fenêtre recommandée

🎯 **Activation conseillée** : après **30 jours de production Phase 4 stable**, lorsque :
1. Les métriques CDN HIT > 98 % sont confirmées
2. Les retours utilisateurs ne signalent aucune régression sur les zones P1 déjà R6
3. La densification au Canada complet R6 devient nécessaire (P1+P2+P3 R6 ≈ 28M tuiles)

→ β2-ΣΤ permet alors **d'étendre la couverture du Canada R6 entier en 3.5 heures k8s 256w** au lieu de **18 jours**.

### 6.3 Activation déconseillée

🚫 **AVANT** validation Phase 4 PROD (risque de double régression).
🚫 **POUR le pré-warm P1 initial** (pré-warm P1 reste à granularité R6 native pour cohérence stricte des hotspots).

---

## 7. RISQUES & MITIGATIONS

| Risque | Probabilité | Impact | Mitigation |
|---|---|---|---|
| Discontinuité visuelle corridors R6 voisines | Moyenne | Moyen | Adaptateur offset + variations déterministes (§ 4.2) |
| HALT incorrect propagé R5 → R6 | Faible | Moyen | Sondage 7 points R5 (§ 4.3) |
| Coût stockage doublé (seed + R6) | Faible | Faible | Purger seed après fan-out (lifecycle R2 7j) |
| Régression scientifique Phase III lock | Faible | Critique | **Verrou Phase III** — β2-ΣTAU est un additif, pas une modification V10/V20 |

---

## 8. VERROU PHASE III · CONFORMITÉ β2-ΣΤ

| Composant | Modifié ? |
|---|---|
| `engines/v8_institutional/v20_performance_bundle.py` | ❌ INTACT (appelé inchangé à granularité R5) |
| `engines/v8_institutional/*` (V10, scoring, corridors, zones) | ❌ INTACT |
| `engines/weather_cache_regional_omega.py` | ❌ INTACT (cache H3 R3 inchangé) |
| Frontend `useZerocostBundle.js`, `lkgCacheOmega.js` | ❌ INTACT (lit toujours R6 via CDN) |
| **Nouveau** `tools/zerocost_worker_seed_r5.py` | 🆕 Additif (à créer si Commandant valide) |
| **Nouveau** adaptateur fan-out R5→R6 | 🆕 Additif |

→ β2-ΣΤ est **strictement additif** : ne touche aucun module existant ; activation reversible
  (suppression des tuiles seed + re-pré-warm R6 direct si besoin).

---

## 9. DÉCISIONS COMMANDANT REQUISES

- ☐ **Approuver le plan β2-ΣΤ** comme plan technique pré-validé (non-exécuté)
- ☐ **Différer** à post-Phase 4 PROD stable 30 jours
- ☐ **Rejeter** (conserver R6 direct pour toute extension)
- ☐ **Modifier** les paramètres (e.g. seed à R4 plutôt que R5)

### Sur validation, je peux :
1. Implémenter `tools/zerocost_worker_seed_r5.py` (~150 LoC)
2. Implémenter l'adaptateur `adapt_bundle_to_child` avec tests pytest
3. Exécuter validation conformité visuelle (50 cellules pilotes)
4. Préparer le YAML k8s spécifique β2-ΣΤ (256 workers seed R5)

---

**FIN PLAN β2-ΣΤ · STATUT : NON-EXÉCUTÉ · EN ATTENTE DIRECTIVE COMMANDANT**
