# 📋 DOCUMENTATION CIRCULAR IMPORT — `bce_corridor_v9` ↔ `corridors_v9`

**Date** : 2026-05-18
**Directive parente** : P22ΩΩ_QUALITY_GROUPE_B
**Doctrine** : BCE-4X ULTIME ABSOLU
**Commandant** : STEEVE-MAX
**Classification** : Pattern doctrinairement accepté

---

## 🎯 OBJET

Le rapport de revue de code automatisé a signalé un « circular import »
entre :
- `bce/bce_corridor_v9.py` (validateur visuel BCE-4X)
- `modules/bionic_engine_p0/engines/corridors_v9.py` (engine génération corridors)

Ce document analyse le pattern, démontre son innocuité runtime, et
documente la décision doctrinale de **préservation tel quel**.

---

## 🔬 STRUCTURE DU PATTERN

### Direction 1 : `corridors_v9` → `bce_corridor_v9`
```python
# modules/bionic_engine_p0/engines/corridors_v9.py:453
def enrich_corridor(self, corridor: Dict) -> Dict:
    try:
        from bce.bce_corridor_v9 import enrich_corridor as bce_enrich
        corridor = bce_enrich(corridor)
    except Exception as e:
        logger.warning(f"Enrichment failed: {e}")
    return corridor
```
**Import LAZY** : à l'intérieur de la méthode `enrich_corridor()` —
résolu uniquement lors d'un appel effectif.

### Direction 2 : `bce_corridor_v9` → `corridors_v9`
```python
# bce/bce_corridor_v9.py:408
def validate_corridor_visual_balance(corridors: List[Dict]) -> Dict[str, Any]:
    from modules.bionic_engine_p0.engines.corridors_v9 import BAND_RATIO, BAND_COLORS
    # ... utilise BAND_RATIO et BAND_COLORS pour valider
```
**Import LAZY** : à l'intérieur de la fonction `validate_corridor_visual_balance()`.

---

## 🟢 POURQUOI LE PATTERN EST INNOCUOUS

### 1. Mécanique Python : imports lazy = résolus au runtime
Lorsqu'un `import` est placé **à l'intérieur d'une fonction**, Python ne
le résout que lors de l'appel effectif de la fonction. À ce moment-là,
les **deux modules sont déjà entièrement chargés** au top-level, donc
aucun cycle d'initialisation n'a lieu.

### 2. Indépendance d'initialisation
Au top-level, NI `bce_corridor_v9.py` NI `corridors_v9.py` ne s'importent
mutuellement. Chacun a ses imports propres (NutritionEngine, WeatherEngine,
DisturbanceEngine, etc.) qui sont résolus normalement.

### 3. Aucune erreur observée
Le backend boot OK avec ce pattern depuis des semaines. Aucun
`ImportError`, `AttributeError`, ou crash au démarrage.

### 4. Dépendance bidirectionnelle INTENTIONNELLE
La logique métier requiert ce couplage :
- **BCE valide** les paramètres visuels (`BAND_RATIO`, `BAND_COLORS`)
  que `corridors_v9` définit.
- **corridors_v9 enrichit** ses corridors via `bce_enrich()` après
  construction (post-traitement BCE).

Découpler complètement nécessiterait :
- Un 3e module shared `corridor_visual_params.py`
- Mise à jour de TOUS les imports existants (~12 fichiers consommateurs)
- Risque de régression non-justifié par le gain

---

## 🔴 POURQUOI NE PAS REFACTORER

### Coût/bénéfice défavorable
| Option | Coût | Bénéfice | Décision |
|---|---|---|---|
| Préserver lazy bidirectionnel | 0 (déjà documenté) | Stable | ✅ **Adoptée** |
| Extraire 3e module shared | ~12 imports à modifier + tests régression complets | Cosmétique (rapport satisfait) | ❌ Différé |
| Dependency injection | Refactor majeur ~30 callsites | Cosmétique | ❌ Différé |

### Risques de la refactorisation
- Mise à jour de constantes `BAND_RATIO`/`BAND_COLORS` (utilisées en
  rendu frontend via API)
- Tests régression complets requis sur scoring + rendering V20/V30
- Aucun gain fonctionnel observable

---

## 📋 RÉFÉRENCES DOCTRINAIRES

* `/app/backend/bce/bce_corridor_v9.py:403-408` — docstring complète in-source
* `/app/backend/modules/bionic_engine_p0/engines/corridors_v9.py:450-465`
  — docstring complète in-source
* `/app/memory/P22OMEGAOMEGA_PURGE_LEGACY_V8_V7_PLAN.md` — confirme
  `corridors_v9` comme CORE_MODULE non purgeable

---

## 🎖️ DÉCISION INSTITUTIONNELLE

**Le circular import lazy bidirectionnel entre `bce_corridor_v9` et
`corridors_v9` est DOCTRINAIREMENT ACCEPTÉ et PRÉSERVÉ en l'état.**

Toute tentative future de purge ou refactorisation devra :
1. Émettre une directive explicite (`P22ΩΩ_REFACTOR_BCE_CORRIDORS_V9_DECOUPLING`)
2. Inclure un audit d'impact complet
3. Valider tous les consommateurs (BAND_RATIO, BAND_COLORS, enrich_corridor)

Le rapport automatisé qui signale ce pattern comme « circular import »
constitue un FAUX POSITIF de sévérité **basse** (analyse statique
incapable de détecter la nature lazy des imports).
