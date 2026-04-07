# SUPRA_ECARTS_DETAILLES.md
# ============================================================
# RAPPORT D'ECARTS DETAILLE — SUPRA v2 & 5 ONGLETS
# ============================================================
# Protocole: BCE-4X-GLOBAL-PLUS-TOTAL
# Autorite: COMMANDANT STEEVE-MAX
# Branche: BIONIC_REWRITE_P0
# Date: 2026-02-07
# Statut: LIVRABLE INSTITUTIONNEL — EN ATTENTE DE VALIDATION
# Reference: SUPRA_ONGLETS_AUDIT_COMPLET.md (commit 9ea1007)
# ============================================================

---

# PARTIE I — 14 ECARTS COMPLETS

---

## E01 — COMPOSANT IC DUPLIQUE x5

| Attribut | Valeur |
|---|---|
| **Severite** | MAJEUR |
| **Modules affectes** | Frontend — AnalyseTab, IntelligenceTab, FicheTab, ComparezTab, CommandezTab |
| **Fichier** | `frontend/src/components/territoire/NutritionPointDetailPanel.jsx` |
| **Lignes** | 407, 714, 820, 1030, 1135 |
| **Norme violee** | DRY / NoCodeDuplication BCE-4X |

### Description technique
Le composant utilitaire `IC` (IconCircle) est un helper JSX qui rend une icone Lucide dans un cercle colore. Il est defini **5 fois de maniere identique** a l'interieur de chaque composant de tab:

**Preuve technique — Definition identique (5 occurrences):**
```jsx
// Ligne 407 (AnalyseTab), 714 (IntelligenceTab), 820 (FicheTab),
// 1030 (ComparezTab), 1135 (CommandezTab)
const IC = ({ Icon, color, sz = 28 }) => (
  <div className="rounded-full flex items-center justify-center flex-shrink-0"
    style={{ width: sz, height: sz, backgroundColor: `${color}20` }}>
    <Icon style={{ color, width: sz * 0.5, height: sz * 0.5 }} />
  </div>
);
```

### Impact sur SUPRA
- **Coherence:** Toute modification du style IC doit etre replicee 5 fois manuellement. Risque d'incoherence visuelle si une instance est oubliee.
- **Poids:** ~40 lignes de code redondant (8 lignes x 5 definitions).
- **Onglets affectes:** TOUS les 5 onglets.

### Reproduction
```bash
grep -n "const IC" frontend/src/components/territoire/NutritionPointDetailPanel.jsx
# Resultat: lignes 407, 714, 820, 1030, 1135
```

---

## E02 — DONNEES PREMIUM HARDCODEES EN FRONTEND

| Attribut | Valeur |
|---|---|
| **Severite** | MODERE |
| **Modules affectes** | Frontend — AnalyseTab (donnees statiques) |
| **Fichier** | `frontend/src/components/territoire/NutritionPointDetailPanel.jsx` |
| **Lignes** | 83-116 |
| **Norme violee** | Separation donnees/presentation BCE-4X |

### Description technique
Trois structures de donnees sont definies directement dans le code frontend, sans aucun endpoint backend correspondant:

**Preuve technique — PHYSIOLOGY_DATA (ligne 83):**
```jsx
const PHYSIOLOGY_DATA = {
  chevreuil: {
    printemps: "Sortie d'hiver. Les reserves minerales sont au plus bas...",
    ete: "Phase de croissance maximale du panache...",
    pre_rut: "Transition hormonale. Le testosterone monte...",
    rut: "Activite maximale. Perte de poids de 20-30%...",
    post_rut: "Recuperation energetique...",
    hiver: "Phase de survie. Metabolisme ralenti...",
  },
  orignal: {
    printemps: "Sortie d'hivernage. Deficience severe en sodium...",
    ete: "Panache en velours. Croissance rapide...",
    rut: "Activite territoriale intense...",
    hiver: "Metabolisme hivernal. Besoins reduits...",
  },
};
```

**Preuve technique — MALE_BEHAVIOR (ligne 100):**
```jsx
const MALE_BEHAVIOR = {
  chevreuil: {
    printemps: "Les males visitent les salines 2-4 fois/semaine...",
    // ... (6 saisons)
  },
  // ECART: orignal ABSENT de MALE_BEHAVIOR (present dans PHYSIOLOGY_DATA)
};
```

**Preuve technique — SUPPORT_HIERARCHY (ligne 111):**
```jsx
const SUPPORT_HIERARCHY = [
  { name: 'Bois mou (epinette, sapin)', score: 95, color: BIONIC.green, ... },
  { name: 'Bois dur (erable, bouleau)', score: 70, color: BIONIC.yellow, ... },
  { name: 'Sol nu / terre', score: 45, color: BIONIC.orange, ... },
  { name: 'Bloc mineral commercial', score: 60, color: BIONIC.yellow, ... },
];
```

### Impact sur SUPRA
- **Maintenance:** Toute modification des textes narratifs ou de la hierarchie des supports necessite un redeploiement frontend complet.
- **Completude:** MALE_BEHAVIOR ne contient que le chevreuil (pas l'orignal). Le frontend fait un fallback silencieux: `MALE_BEHAVIOR[species]?.[season] || MALE_BEHAVIOR.chevreuil?.printemps`
- **Onglets affectes:** ANALYSE (section PREMIUM — Physiologie, Comportement, Support).
- **Sous-ecart:** Asymetrie donnees — chevreuil = 6 saisons dans MALE_BEHAVIOR, orignal = 0 saisons.

### Reproduction
```bash
grep -n "PHYSIOLOGY_DATA\|MALE_BEHAVIOR\|SUPPORT_HIERARCHY" \
  frontend/src/components/territoire/NutritionPointDetailPanel.jsx
# Resultat: lignes 83, 100, 111, 403, 404, 673
```

---

## E03 — SESSION PANIER LOCALSTORAGE SANS VALIDATION SERVEUR

| Attribut | Valeur |
|---|---|
| **Severite** | MINEUR |
| **Modules affectes** | Frontend — Fonction `getSalineSession()` / Backend — ecommerce_router |
| **Fichier Frontend** | `NutritionPointDetailPanel.jsx` lignes 49-56 |
| **Fichier Backend** | `modules/saline_engine/ecommerce_router.py` |
| **Norme violee** | Securite session BCE-4X |

### Description technique
L'identifiant de session panier est genere cote client et stocke dans `localStorage`:

**Preuve technique — Generation session (ligne 49):**
```jsx
const getSalineSession = () => {
  let sid = localStorage.getItem('saline_session_id');
  if (!sid) {
    sid = 'sal_' + Math.random().toString(36).substr(2, 12);
    localStorage.setItem('saline_session_id', sid);
  }
  return sid;
};
```

Le backend accepte ce `session_id` sans validation ni authentification. Tout `session_id` formate `sal_*` est accepte.

### Impact sur SUPRA
- **Securite:** Un utilisateur peut forger un `session_id` et acceder/modifier le panier d'un autre utilisateur (si l'ID est devinee).
- **Persistence:** Le panier est lie au navigateur (localStorage). Changement de navigateur = perte du panier.
- **Onglets affectes:** COMMANDEZ (panier + checkout).

### Reproduction
```bash
grep -n "getSalineSession\|saline_session_id" \
  frontend/src/components/territoire/NutritionPointDetailPanel.jsx
# Resultat: lignes 49-56, 250, 258, 269
```

---

## E04 — ALIAS BACKWARD-COMPAT NON UTILISES (CODE MORT)

| Attribut | Valeur |
|---|---|
| **Severite** | INFO |
| **Modules affectes** | Frontend — NutritionPointDetailPanel.jsx |
| **Fichier** | `NutritionPointDetailPanel.jsx` |
| **Lignes** | 166-167 |
| **Norme violee** | Code mort / Proprete BCE-4X |

### Description technique
Deux alias sont declares mais jamais utilises dans l'ensemble du fichier:

**Preuve technique (ligne 166-167):**
```jsx
// Backward compat aliases
const Card = GoldenCard;
const CollapsibleSection = GoldenCollapsible;
```

**Verification:**
```bash
grep -c "\bCard\b" NutritionPointDetailPanel.jsx     # Occurrences de "Card"
# Toutes les occurrences sont GoldenCard, ProductCard, ou card: (objet BIONIC)
# Card et CollapsibleSection ne sont JAMAIS references comme composants JSX
```

### Impact sur SUPRA
- **Negligeable.** Code inerte qui n'affecte pas le fonctionnement.
- **Onglets affectes:** Aucun.

---

## E05 — SOIL ENGINE V1 DETERMINISTE NON CERTIFIE

| Attribut | Valeur |
|---|---|
| **Severite** | MAJEUR |
| **Modules affectes** | Backend — `modules/soil_engine/router.py` |
| **Fichier** | `modules/soil_engine/router.py` |
| **Lignes** | 1-33 (documentation), 42-329 (implementation) |
| **Norme violee** | Certitude donnees BCE-4X |

### Description technique
Le SOIL ENGINE V1 utilise un hash MD5 des coordonnees GPS pour attribuer un type de sol parmi 7 possibilites. Le score est **SIMULE, PAS MESURE**.

**Preuve technique — Methode de classification (extrait):**
```python
# modules/soil_engine/router.py
SOIL_TYPES = {
    "loam_sableux": { "nom": "Loam sableux", "retention_mineraux": 62, ... },
    "argile_limoneuse": { ... },
    "sable_grossier": { ... },
    "tourbe": { ... },
    "moraine": { ... },
    "roc_affleurant": { ... },
    "alluvial": { ... },
}
# Attribution: hash MD5(lat:lng) -> index dans SOIL_TYPES
```

**Documentation existante (lignes 4-25):**
```
VERSION: V1 — INTERNE — NON CERTIFIEE
STATUT: Deterministe (GPS hash) — AUCUNE donnee pedologique reelle integree
LIMITES V1:
- Classification DETERMINISTE basee sur un hash MD5 des coordonnees GPS
- AUCUNE integration de donnees pedologiques reelles (IRDA, MFFP, MRNF, CGQ)
- AUCUNE integration LiDAR reelle
- Le score de sol est SIMULE, PAS MESURE
```

### Impact sur SUPRA
- **ANALYSE:** Le panneau "Sol — Analyse pedologique" affiche des donnees simulees comme si elles etaient reelles (score, type, texture, pH).
- **FICHE:** Le panneau "Sol — Type detecte" affiche egalement des donnees simulees.
- **Credibilite:** L'utilisateur final ne voit aucun avertissement que le sol est simule.
- **Onglets affectes:** ANALYSE, FICHE.
- **Statut connu:** Documente dans le code source. Plan V2 prevu (P1-P6).

### Reproduction
```bash
grep -n "NON CERTIFIEE\|SIMULE\|hash MD5" backend/modules/soil_engine/router.py
# Resultat: lignes 4, 5, 9, 13
```

---

## E06 — DOUBLE SOURCE SOL (SALINE ENGINE vs SOIL ENGINE)

| Attribut | Valeur |
|---|---|
| **Severite** | MODERE |
| **Modules affectes** | Frontend — AnalyseTab / Backend — saline_engine + soil_engine |
| **Fichier Frontend** | `NutritionPointDetailPanel.jsx` lignes 509-541 |
| **Fichiers Backend** | `modules/saline_engine/engines/soil_composition_engine.py` + `modules/soil_engine/router.py` |
| **Norme violee** | Coherence sources BCE-4X |

### Description technique
L'onglet ANALYSE affiche les donnees de sol provenant de **deux sources distinctes**:

**Source 1:** `engines.soil` (depuis `ultraData.engines.soil`) — provient de `saline_engine/engines/soil_composition_engine.py`
**Source 2:** `soilData` (depuis l'appel direct `/api/v1/soil/analyze`) — provient de `modules/soil_engine/router.py`

**Preuve technique — Logique d'affichage (lignes 509-541):**
```jsx
{(engines.soil || soilData) && (
  <GoldenCard testId="info-card-sol" ...>
    {soilData ? (
      // Affiche SOIL ENGINE V1 (9 metriques detaillees)
      <>
        {[{ l: 'Type', v: soilData.soil_name }, { l: 'Classe', v: soilData.soil_class }, ...]}
      </>
    ) : (
      // Fallback: saline_engine soil (3 metriques basiques)
      <>
        {[{ l: 'Type', v: engines.soil?.soil_type }, { l: 'pH', v: engines.soil?.pH }, ...]}
      </>
    )}
  </GoldenCard>
)}
```

### Impact sur SUPRA
- **Incoherence:** Si les deux sources retournent des types de sol differents pour les memes coordonnees, l'utilisateur voit le resultat de soil_engine (prioritaire) dans ANALYSE, mais saline_engine est toujours charge en arriere-plan.
- **Gaspillage:** Deux appels API pour la meme donnee conceptuelle.
- **Onglets affectes:** ANALYSE (panneau Sol), FICHE (panneau Sol detecte — utilise uniquement soilData).

---

## E07 — CONFLIT MAPPING SAISON AUTOMATIQUE vs STATIQUE

| Attribut | Valeur |
|---|---|
| **Severite** | MINEUR |
| **Modules affectes** | Frontend — NutritionPointDetailPanel (composant parent) |
| **Fichier** | `NutritionPointDetailPanel.jsx` |
| **Lignes** | 213-214 |
| **Norme violee** | Determinisme saisonnier BCE-4X |

### Description technique
Le composant definit un `seasonMap` qui mappe les mois aux saisons, mais utilise AUSSI `np.season` (provenant du point nutritionnel):

**Preuve technique (lignes 213-215):**
```jsx
const seasonMap = {
  1:'hiver', 2:'hiver', 3:'printemps', 4:'printemps',
  5:'ete', 6:'ete', 7:'ete', 8:'pre_rut', 9:'pre_rut',
  10:'rut', 11:'post_rut', 12:'hiver'
};
const month = new Date().getMonth() + 1;
```

**Utilisation mixte:**
- `season` (ligne 211): `np?.season || 'printemps'` — **statique** (provient du point)
- `seasonMap[month]` (ligne 232-234): **dynamique** (date actuelle du navigateur)

Le `season` statique est envoye au supra-panel (ligne 226), mais `seasonMap[month]` est envoye a saline/analyze (ligne 232) et salines-ultime/fiche (ligne 233).

### Impact sur SUPRA
- **Incoherence potentielle:** Si le point nutritionnel a `season: 'printemps'` mais qu'on est en octobre, le supra-panel recoit 'printemps' et saline/analyze recoit 'rut'. Deux onglets affichent des donnees de saisons differentes.
- **Onglets affectes:** ANALYSE (mix de donnees supra-panel et saline), FICHE (salines-ultime utilise seasonMap).

---

## E08 — BOUCLE ENRICHISSEMENT PRODUITS N+1

| Attribut | Valeur |
|---|---|
| **Severite** | MODERE |
| **Modules affectes** | Backend — `engines/nutrition_intelligence/router.py` (endpoint supra-panel) |
| **Fichier** | `engines/nutrition_intelligence/router.py` |
| **Lignes** | 244-265 |
| **Norme violee** | Performance BCE-4X |

### Description technique
L'endpoint `/api/v6/nutrition-intelligence/supra-panel` enrichit chaque produit individuellement avec 3 appels synchrones par produit:

**Preuve technique (lignes 244-265):**
```python
enriched_products = []
for p in products.get("products", []):
    pid = p.get("product_id")
    quality = analyze_product_quality(pid) if pid else {}        # x6010
    availability = get_product_availability(pid, "QC") if pid else {}  # x6011
    compliance = compute_compliance_score(pid) if pid else {}    # x6012
    p["quality"] = { ... }
    p["availability"] = { ... }
    p["compliance"] = { ... }
    enriched_products.append(p)
```

### Impact sur SUPRA
- **Performance:** Pour N produits, 3*N appels de fonction synchrones. Avec le catalogue actuel (~15 produits), cela represente 45 appels.
- **Latence:** Temps de reponse du supra-panel proportionnel au nombre de produits.
- **Onglets affectes:** TOUS (le supra-panel est l'appel principal qui alimente ANALYSE, INTELLIGENCE, COMPAREZ, COMMANDEZ).

### Reproduction
```bash
grep -n "for p in products" backend/engines/nutrition_intelligence/router.py
# Resultat: ligne 245
```

---

## E09 — DIVISION COLONNES NON EQUILIBREE (INTELLIGENCE)

| Attribut | Valeur |
|---|---|
| **Severite** | MINEUR |
| **Modules affectes** | Frontend — IntelligenceTab |
| **Fichier** | `NutritionPointDetailPanel.jsx` |
| **Lignes** | 709-711 |
| **Norme violee** | Equilibre visuel GOLDEN |

### Description technique
La repartition des produits en 3 colonnes utilise `Math.ceil(n/3)`:

**Preuve technique (lignes 709-711):**
```jsx
const third = Math.ceil(productList.length / 3);
const col1 = productList.slice(0, third);
const col2 = productList.slice(third, third * 2);
const col3 = productList.slice(third * 2);
```

**Cas problematique:** Pour 7 produits:
- `third = Math.ceil(7/3) = 3`
- col1 = 3 produits, col2 = 3 produits, col3 = 1 produit
- Desequilibre visuel: 3 | 3 | 1

### Impact sur SUPRA
- **Visuel:** Desequilibre mineur des colonnes dans certains cas.
- **Onglets affectes:** INTELLIGENCE uniquement.

---

## E10 — COMPAREZ IGNORE LE 4eme PRODUIT

| Attribut | Valeur |
|---|---|
| **Severite** | MODERE |
| **Modules affectes** | Frontend — ComparezTab |
| **Fichier** | `NutritionPointDetailPanel.jsx` |
| **Lignes** | 301, 1057-1058, 1073 |
| **Norme violee** | Coherence UX BCE-4X |

### Description technique
L'utilisateur peut selectionner jusqu'a 4 produits (contrainte ligne 301), mais l'affichage est limite a 3 colonnes:

**Preuve technique — Selection (ligne 301):**
```jsx
const toggleCompare = (pid) => {
  setCompareIds(prev =>
    prev.includes(pid)
      ? prev.filter(x => x !== pid)
      : prev.length < 4 ? [...prev, pid] : prev  // MAX 4
  );
};
```

**Preuve technique — Affichage (ligne 1073):**
```jsx
{padded.slice(0, 3).map((p, idx) => {   // AFFICHE MAX 3
```

### Impact sur SUPRA
- **UX:** L'utilisateur selectionne 4 produits dans INTELLIGENCE, bascule vers COMPAREZ, et ne voit que 3 produits. Le 4eme est silencieusement ignore sans message.
- **Onglets affectes:** COMPAREZ (affichage), INTELLIGENCE (selection).

### Reproduction
Selectionner 4 produits dans INTELLIGENCE → aller dans COMPAREZ → observer que seuls 3 sont affiches.

---

## E11 — SCORING DETERMINISTE FICHE (SALINES ULTIME)

| Attribut | Valeur |
|---|---|
| **Severite** | MINEUR |
| **Modules affectes** | Backend — `modules/salines_ultime_engine/router.py` |
| **Fichier** | `modules/salines_ultime_engine/router.py` |
| **Lignes** | 75-78, 82-213 |
| **Norme violee** | Certitude donnees BCE-4X (meme famille que E05) |

### Description technique
Les 5 scores de la FICHE SALINE ULTIME utilisent un hash MD5 pour generer des valeurs reproductibles mais non reelles:

**Preuve technique (lignes 75-78):**
```python
def _seed(lat: float, lng: float, key: str) -> float:
    """Graine deterministe pour reproductibilite."""
    h = hashlib.md5(f"{lat:.6f}:{lng:.6f}:{key}".encode()).hexdigest()
    return int(h[:8], 16) / 0xFFFFFFFF
```

Les 30 sous-criteres (6 par score) sont tous derives de cette graine.

### Impact sur SUPRA
- **Identique a E05:** Les scores affiches dans l'onglet FICHE sont reproductibles mais ne refletent pas la realite terrain.
- **Onglets affectes:** FICHE exclusivement.
- **Statut:** Non documente dans le code source (contrairement a E05 qui est bien documente).

---

## E12 — FICHIER MONOLITHIQUE 1259 LIGNES

| Attribut | Valeur |
|---|---|
| **Severite** | INFO |
| **Modules affectes** | Frontend — NutritionPointDetailPanel.jsx |
| **Fichier** | `NutritionPointDetailPanel.jsx` |
| **Lignes** | 1-1259 |
| **Norme violee** | Modularite BCE-4X (recommandation 300 lignes max/composant) |

### Description technique
Tous les composants suivants sont dans un seul fichier:

| Composant | Lignes (approx.) | Role |
|---|---|---|
| Constantes + helpers | 1-180 | BIONIC, GOLDEN, GaugeMini, GoldenCard, GoldenCollapsible, SupraButton, TABS |
| NutritionPointDetailPanel | 192-388 | Composant principal + fetchAll + fetchCart |
| AnalyseTab | 396-701 | Onglet ANALYSE (305 lignes) |
| IntelligenceTab | 707-778 | Onglet INTELLIGENCE (71 lignes) |
| FicheTab | 784-1021 | Onglet FICHE (237 lignes) |
| ComparezTab | 1027-1132 | Onglet COMPAREZ (105 lignes) |
| CommandezTab | 1134-1256 | Onglet COMMANDEZ (122 lignes) |

### Impact sur SUPRA
- **Maintenabilite:** Difficulte a naviguer et modifier un fichier unique de 1259 lignes.
- **Onglets affectes:** TOUS (indirect — tout changement impacte le meme fichier).

---

## E13 — PRODUCT_ID FALLBACK ARTIFICIEL (COMMANDEZ)

| Attribut | Valeur |
|---|---|
| **Severite** | MINEUR |
| **Modules affectes** | Frontend — CommandezTab |
| **Fichier** | `NutritionPointDetailPanel.jsx` |
| **Ligne** | 1163 |
| **Norme violee** | Integrite donnees BCE-4X |

### Description technique
Le bouton d'ajout au panier dans la section recette utilise un fallback si `product_id` est absent:

**Preuve technique (ligne 1163):**
```jsx
<SupraButton size="sm"
  onClick={() => addToCart(item.product_id || `sal_00${i+1}`)}
  disabled={cartLoading}
  testId={`order-add-${i}`}>
```

L'expression `item.product_id || 'sal_00${i+1}'` genere un identifiant artificiel (`sal_001`, `sal_002`, etc.) qui pourrait correspondre — ou non — a un produit reel du catalogue.

### Impact sur SUPRA
- **Risque:** Un produit sans `product_id` ajoutera un article potentiellement inexistant ou incorrect au panier.
- **Onglets affectes:** COMMANDEZ (section Recette complete).

---

## E14 — MOTEURS NON AFFICHES (x6030, x7000)

| Attribut | Valeur |
|---|---|
| **Severite** | INFO |
| **Modules affectes** | Backend — x6030_product_ecosystem.py, x7000_supplier_product_engine.py |
| **Fichiers** | `engines/nutrition_intelligence/x6030_product_ecosystem.py`, `x7000_supplier_product_engine.py` |
| **Endpoints** | `/api/v6/nutrition-intelligence/products/ecosystem`, `/supplier/*` |
| **Norme violee** | Potentiel non exploite |

### Description technique
Deux sous-moteurs sont pleinement implementes avec endpoints operationnels mais aucun onglet SUPRA ne les consomme:

**x6030 — Product Ecosystem Connector:**
- `get_product_ecosystem(product_id)` — Ecosysteme complet d'un produit
- `get_all_ecosystems()` — Tous les ecosystemes
- `get_product_tracability(product_id)` — Tracabilite

**x7000 — Supplier Product Engine:**
- `submit_product(data)` — Soumission produit fournisseur
- `review_submission(id, approved, notes)` — Revue humaine
- `activate_product(id)` — Activation magasin
- `get_submission(id)`, `get_all_submissions(status)` — Recuperation soumissions
- `get_pipeline_stats()` — Statistiques pipeline

### Impact sur SUPRA
- **Aucun impact fonctionnel.** Ces moteurs sont disponibles pour usage futur (Admin, Dashboard fournisseur).
- **Onglets affectes:** Aucun actuellement.

---

# PARTIE II — MATRICE D'IMPACT

## Vue d'ensemble: Ecarts par onglet

| Ecart | SUPRA (Parent) | ANALYSE | FICHE | INTELLIGENCE | COMPAREZ | COMMANDEZ | Backend |
|---|---|---|---|---|---|---|---|
| E01 IC x5 | — | IMPACTE | IMPACTE | IMPACTE | IMPACTE | IMPACTE | — |
| E02 Hardcode | — | IMPACTE | — | — | — | — | — |
| E03 Session | — | — | — | — | — | IMPACTE | IMPACTE |
| E04 Code mort | IMPACTE | — | — | — | — | — | — |
| E05 Soil V1 | — | IMPACTE | IMPACTE | — | — | — | IMPACTE |
| E06 Double sol | — | IMPACTE | IMPACTE | — | — | — | IMPACTE |
| E07 Saison | IMPACTE | IMPACTE | IMPACTE | — | — | — | — |
| E08 Boucle N+1 | — | IMPACTE | — | IMPACTE | IMPACTE | IMPACTE | IMPACTE |
| E09 Colonnes | — | — | — | IMPACTE | — | — | — |
| E10 4e produit | — | — | — | IMPACTE | IMPACTE | — | — |
| E11 Fiche det. | — | — | IMPACTE | — | — | — | IMPACTE |
| E12 Monolithe | IMPACTE | IMPACTE | IMPACTE | IMPACTE | IMPACTE | IMPACTE | — |
| E13 Fallback ID | — | — | — | — | — | IMPACTE | — |
| E14 Non affiche | — | — | — | — | — | — | IMPACTE |
| **TOTAL** | **2** | **6** | **5** | **4** | **3** | **4** | **6** |

## Classement des onglets par niveau d'impact

| Rang | Entite | Ecarts | Majeurs | Moderes |
|---|---|---|---|---|
| 1 | ANALYSE | 6 | 1 (E05) | 3 (E02, E06, E08) |
| 2 | Backend | 6 | 1 (E05) | 2 (E06, E08) |
| 3 | FICHE | 5 | 1 (E05) | 1 (E06) |
| 4 | INTELLIGENCE | 4 | 1 (E01) | 1 (E08, E10) |
| 5 | COMMANDEZ | 4 | 1 (E01) | 1 (E08) |
| 6 | COMPAREZ | 3 | 1 (E01) | 1 (E10) |
| 7 | SUPRA Parent | 2 | 0 | 0 |

## Dependances entre ecarts

```
E05 (Soil V1) ←── E06 (Double sol) ←── E11 (Fiche deterministe)
                    [Meme famille: donnees simulees]

E01 (IC x5) ←── E12 (Monolithe)
                 [Cause racine: fichier monolithique favorise la duplication]

E10 (4e produit COMPAREZ) ←── E09 (Colonnes desequilibrees)
                               [Meme famille: gestion de grille]
```

---

# PARTIE III — MATRICE DE TESTS INSTITUTIONNELS BCE-4X

## Tests Requis Avant Reconstruction

| ID Test | Ecart | Type | Description | Commande / Methode | Resultat attendu | Priorite |
|---|---|---|---|---|---|---|
| T01 | E01 | Code | Compter les definitions IC | `grep -c "const IC" NutritionPointDetailPanel.jsx` | Doit retourner 1 (apres fix) | HAUTE |
| T02 | E02 | API | Endpoint donnees PREMIUM | `curl -s POST {API}/api/v6/nutrition-intelligence/premium-data` | 200 + JSON avec PHYSIOLOGY_DATA, MALE_BEHAVIOR, SUPPORT_HIERARCHY | HAUTE |
| T03 | E03 | Securite | Validation session serveur | `curl -s GET {API}/api/v1/saline/shop/cart/INVALID_ID` | 400 ou 404 (pas 200 avec panier vide) | MOYENNE |
| T04 | E04 | Code | Alias supprimes | `grep -c "const Card = \|const CollapsibleSection = " NutritionPointDetailPanel.jsx` | Doit retourner 0 | BASSE |
| T05 | E05 | Code | Documentation SOIL V1 | `grep -c "NON CERTIFIEE\|SIMULE" soil_engine/router.py` | > 0 (deja present) | INFO |
| T06 | E06 | Frontend | Source unique sol ANALYSE | Screenshot ANALYSE — panneau Sol | Doit afficher une seule source coherente | HAUTE |
| T07 | E07 | API | Coherence saison | Comparer reponses supra-panel (season) vs saline/analyze (seasonMap) | Meme saison dans les deux reponses | MOYENNE |
| T08 | E08 | Perf | Temps reponse supra-panel | `time curl -s POST {API}/api/v6/nutrition-intelligence/supra-panel` | < 2s pour 15 produits | MOYENNE |
| T09 | E09 | Frontend | Equilibre colonnes INTELLIGENCE | Screenshot INTELLIGENCE avec 7 produits | 3 colonnes equilibrees (3-2-2 ou 2-3-2) | BASSE |
| T10 | E10 | Frontend | Affichage 4 produits COMPAREZ | Screenshot COMPAREZ avec 4 produits selectionnes | 4 produits visibles | HAUTE |
| T11 | E11 | Code | Documentation FICHE deterministe | Verifier presence documentation scoring | Documentation ajoutee dans router.py | BASSE |
| T12 | E12 | Code | Taille fichier principal | `wc -l NutritionPointDetailPanel.jsx` | < 500 lignes (apres modularisation) | MOYENNE |
| T13 | E13 | Frontend | Fallback product_id | Verifier que tous les items order ont un product_id valide | Aucun `sal_00X` artificiel dans le panier | BASSE |
| T14 | E14 | API | Endpoints x6030/x7000 actifs | `curl -s GET {API}/api/v6/nutrition-intelligence/products/ecosystem/all` | 200 + JSON | INFO |
| T15 | — | Regression | Onglet ANALYSE rendu complet | Screenshot ANALYSE avec donnees | Grille 3 colonnes, Score, Gauge, Mineraux visibles | CRITIQUE |
| T16 | — | Regression | Onglet FICHE rendu complet | Screenshot FICHE avec donnees | 5 scores, 20 sources, CriteriaRow cliquables | CRITIQUE |
| T17 | — | Regression | Onglet INTELLIGENCE fonctionnel | Screenshot INTELLIGENCE + clic Comparer | Produits en grille, bouton Comparer toggle | CRITIQUE |
| T18 | — | Regression | Onglet COMMANDEZ + Stripe | Screenshot COMMANDEZ + ajout panier | Panier mis a jour, bouton Checkout present | CRITIQUE |
| T19 | — | Regression | GUIDE PRO en tete | Screenshot ANALYSE scrolle en haut | PedagogieModule en premiere position | CRITIQUE |
| T20 | — | Regression | BCE-4X Lock actif | `grep "data-bce4x-locked" NutritionPointDetailPanel.jsx` | >= 1 occurrence | CRITIQUE |

## Recapitulatif Tests

| Priorite | Nombre | IDs |
|---|---|---|
| CRITIQUE | 6 | T15, T16, T17, T18, T19, T20 |
| HAUTE | 4 | T01, T02, T06, T10 |
| MOYENNE | 4 | T03, T07, T08, T12 |
| BASSE | 4 | T04, T09, T11, T13 |
| INFO | 2 | T05, T14 |
| **TOTAL** | **20** | — |

---

# PARTIE IV — PLAN DE RECONSTRUCTION SEQUENCE (ROADMAP P0-R)

## Principe directeur
Chaque phase est **atomique**: elle produit un livrable testable et committable independamment. ZERO action de la phase N+1 avant validation de la phase N.

## Sequence de reconstruction

### PHASE R0 — PREPARATION (Pre-requis)
| Etape | Action | Ecarts | Livrable |
|---|---|---|---|
| R0.1 | Creer branche isolee `SUPRA_RECONSTRUCTION` depuis `BIONIC_REWRITE_P0` | — | Branche creee |
| R0.2 | Snapshot de reference: screenshot des 5 onglets en etat actuel | — | 5 screenshots de reference |
| R0.3 | Baseline de performance: `time curl supra-panel` | E08 | Temps de reference note |

### PHASE R1 — NETTOYAGE CODE MORT (Risque: ZERO)
| Etape | Action | Ecarts | Tests |
|---|---|---|---|
| R1.1 | Supprimer alias `Card` et `CollapsibleSection` (lignes 166-167) | E04 | T04 |
| R1.2 | Commit + verification regression | — | T15-T20 (screenshots) |

### PHASE R2 — EXTRACTION IC (Risque: FAIBLE)
| Etape | Action | Ecarts | Tests |
|---|---|---|---|
| R2.1 | Creer `territoire/ui/IconCircle.jsx` avec le composant IC | E01 | — |
| R2.2 | Remplacer les 5 definitions par imports | E01 | T01 |
| R2.3 | Commit + verification regression | — | T15-T20 |

### PHASE R3 — MODULARISATION TABS (Risque: MODERE)
| Etape | Action | Ecarts | Tests |
|---|---|---|---|
| R3.1 | Creer `territoire/supra/AnalyseTab.jsx` | E12 | — |
| R3.2 | Creer `territoire/supra/FicheTab.jsx` | E12 | — |
| R3.3 | Creer `territoire/supra/IntelligenceTab.jsx` | E12 | — |
| R3.4 | Creer `territoire/supra/ComparezTab.jsx` | E12 | — |
| R3.5 | Creer `territoire/supra/CommandezTab.jsx` | E12 | — |
| R3.6 | Extraire constantes/helpers dans `territoire/supra/constants.js` | E12 | — |
| R3.7 | Reduire NutritionPointDetailPanel.jsx a orchestrateur (~400 lignes) | E12 | T12 |
| R3.8 | Commit + verification regression COMPLETE | — | T15-T20 |

### PHASE R4 — CORRECTIONS UX (Risque: FAIBLE)
| Etape | Action | Ecarts | Tests |
|---|---|---|---|
| R4.1 | Corriger affichage COMPAREZ pour 4 produits (grid-cols-4 ou layout 2x2) | E10 | T10 |
| R4.2 | Equilibrer colonnes INTELLIGENCE (algorithme round-robin) | E09 | T09 |
| R4.3 | Supprimer fallback product_id artificiel (afficher avertissement) | E13 | T13 |
| R4.4 | Commit + verification regression | — | T15-T20 |

### PHASE R5 — COHERENCE DONNEES (Risque: MODERE)
| Etape | Action | Ecarts | Tests |
|---|---|---|---|
| R5.1 | Unifier source sol: choisir SOIL ENGINE ou SALINE ENGINE (pas les deux) | E06 | T06 |
| R5.2 | Harmoniser saison: utiliser seasonMap partout OU np.season partout | E07 | T07 |
| R5.3 | Documenter scoring deterministe FICHE (comme SOIL ENGINE V1) | E11 | T11 |
| R5.4 | Commit + verification regression | — | T15-T20 |

### PHASE R6 — OPTIMISATION BACKEND (Risque: MODERE)
| Etape | Action | Ecarts | Tests |
|---|---|---|---|
| R6.1 | Creer fonctions batch dans x6010, x6011, x6012 | E08 | — |
| R6.2 | Remplacer boucle N+1 par appels batch dans supra-panel | E08 | T08 |
| R6.3 | Benchmark: comparer temps avant/apres | E08 | T08 (< 2s) |
| R6.4 | Commit + verification regression | — | T15-T20 |

### PHASE R7 — EXTERNALISATION DONNEES PREMIUM (Risque: FAIBLE)
| Etape | Action | Ecarts | Tests |
|---|---|---|---|
| R7.1 | Creer endpoint `/api/v6/nutrition-intelligence/premium-data` | E02 | T02 |
| R7.2 | Migrer PHYSIOLOGY_DATA, MALE_BEHAVIOR, SUPPORT_HIERARCHY vers backend | E02 | — |
| R7.3 | Frontend: fetch au lieu de hardcode | E02 | T02 |
| R7.4 | Ajouter donnees MALE_BEHAVIOR pour orignal | E02 | — |
| R7.5 | Commit + verification regression | — | T15-T20 |

### PHASE R8 — AUDIT POST-RECONSTRUCTION
| Etape | Action | Livrable |
|---|---|---|
| R8.1 | Re-executer les 20 tests (T01-T20) | Rapport de tests |
| R8.2 | Screenshots des 5 onglets reconstruits | 5 screenshots |
| R8.3 | Diff avec screenshots de reference (R0.2) | Rapport de comparaison |
| R8.4 | Produire `SUPRA_RECONSTRUCTION_VALIDATION.md` | Rapport final |
| R8.5 | Soumettre au Commandant pour CERTIFICATION | En attente validation |

### PHASE R9 — VERROUILLAGE BCE-4X-LOCK
| Etape | Action | Livrable |
|---|---|---|
| R9.1 | Generer SHA256 de tous les fichiers SUPRA reconstruits | Hash manifest |
| R9.2 | Mettre a jour `BCE4X_GLOBAL_LOCK.json` | Lock file |
| R9.3 | Merge `SUPRA_RECONSTRUCTION` dans `BIONIC_REWRITE_P0` | Branche fusionnee |
| R9.4 | Supprimer branche `SUPRA_RECONSTRUCTION` | Nettoyage |

## Calendrier estimatif

| Phase | Duree estimee | Dependances |
|---|---|---|
| R0 Preparation | 10 min | Aucune |
| R1 Nettoyage | 5 min | R0 |
| R2 IC Extraction | 15 min | R1 |
| R3 Modularisation | 45 min | R2 |
| R4 Corrections UX | 20 min | R3 |
| R5 Coherence donnees | 25 min | R4 |
| R6 Optimisation backend | 30 min | R5 |
| R7 Externalisation Premium | 25 min | R6 |
| R8 Audit post-reconstruction | 20 min | R7 |
| R9 Verrouillage | 10 min | R8 + Validation Commandant |
| **TOTAL** | **~3h 25min** | — |

---

# ANNEXE A — REGISTRE DES FICHIERS SOUS PERIMETRE

| # | Fichier | Type | Ecarts associes |
|---|---|---|---|
| 1 | `frontend/src/components/territoire/NutritionPointDetailPanel.jsx` | Frontend | E01, E02, E03, E04, E07, E09, E10, E12, E13 |
| 2 | `frontend/src/components/territoire/PinnablePanel.jsx` | Frontend | — |
| 3 | `frontend/src/components/territoire/PedagogieModule.jsx` | Frontend | — |
| 4 | `frontend/src/components/territoire/ui/ShareBionicButton.jsx` | Frontend | — |
| 5 | `frontend/src/components/territoire/ui/CriteriaDetailModal.jsx` | Frontend | — |
| 6 | `backend/engines/nutrition_intelligence/router.py` | Backend | E08 |
| 7 | `backend/engines/nutrition_intelligence/__init__.py` | Backend | — |
| 8 | `backend/engines/nutrition_intelligence/x5100_mineral_score.py` | Backend | — |
| 9 | `backend/engines/nutrition_intelligence/x5200_mineral_recommendation.py` | Backend | — |
| 10 | `backend/engines/nutrition_intelligence/x5300_order_engine.py` | Backend | — |
| 11 | `backend/engines/nutrition_intelligence/x5500_energy_protein.py` | Backend | — |
| 12 | `backend/engines/nutrition_intelligence/x5600_site_guide.py` | Backend | — |
| 13 | `backend/engines/nutrition_intelligence/x5700_cost_engine.py` | Backend | — |
| 14 | `backend/engines/nutrition_intelligence/x5800_recipe_engine.py` | Backend | — |
| 15 | `backend/engines/nutrition_intelligence/x5900_evidence_engine.py` | Backend | — |
| 16 | `backend/engines/nutrition_intelligence/x6000_product_score.py` | Backend | — |
| 17 | `backend/engines/nutrition_intelligence/x6010_product_quality_analyzer.py` | Backend | E08, E14 |
| 18 | `backend/engines/nutrition_intelligence/x6011_market_availability_engine.py` | Backend | E08, E14 |
| 19 | `backend/engines/nutrition_intelligence/x6012_regulatory_compliance_engine.py` | Backend | E08, E14 |
| 20 | `backend/engines/nutrition_intelligence/x6020_terrain_solutions.py` | Backend | — |
| 21 | `backend/engines/nutrition_intelligence/x6030_product_ecosystem.py` | Backend | E14 |
| 22 | `backend/engines/nutrition_intelligence/x7000_supplier_product_engine.py` | Backend | E14 |
| 23 | `backend/modules/saline_engine/router.py` | Backend | — |
| 24 | `backend/modules/saline_engine/ecommerce_router.py` | Backend | E03 |
| 25 | `backend/modules/saline_engine/engines/soil_composition_engine.py` | Backend | E06 |
| 26 | `backend/modules/saline_engine/engines/nutrient_deficiency_engine.py` | Backend | — |
| 27 | `backend/modules/saline_engine/engines/wildlife_nutritional_engine.py` | Backend | — |
| 28 | `backend/modules/saline_engine/engines/vegetation_forage_engine.py` | Backend | — |
| 29 | `backend/modules/saline_engine/engines/hydrology_leaching_engine.py` | Backend | — |
| 30 | `backend/modules/saline_engine/engines/seasonal_metabolism_engine.py` | Backend | — |
| 31 | `backend/modules/saline_engine/engines/saline_recommendation_engine.py` | Backend | — |
| 32 | `backend/modules/salines_ultime_engine/router.py` | Backend | E11 |
| 33 | `backend/modules/soil_engine/router.py` | Backend | E05 |

---

*Rapport genere conformement au protocole BCE-4X-GLOBAL-PLUS-TOTAL*
*Autorite: COMMANDANT STEEVE-MAX*
*Branche: BIONIC_REWRITE_P0*
*Date: 2026-02-07*
