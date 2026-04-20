# ENGINE CORRIDORS — DESCRIPTION OFFICIELLE & FINALE — VERSION Ω

> **COMMANDANT :** STEEVE-MAX
> **DATE :** 2026-04-20T18:00:00Z
> **PHASE :** XI-SUPRA-H
> **STATUT :** 🔒 **NORME INSTITUTIONNELLE UNIQUE ET OBLIGATOIRE**
> **AUTORITÉ :** Directive Commandement — toute autre description de corridors est ARCHIVE NON ACTIVE

---

## §0. IDENTITÉ FONDAMENTALE — IA-ASSISTÉE

`ENGINE CORRIDORS-Ω` est le moteur autonome de génération, validation et
publication des corridors animaliers dans BIONIC OS V20-SUPRA. Il est
**strictement IA-assisté** : sa logique géométrique, écologique, hydrologique
et comportementale est contrôlée par le moteur interne `ENGINE IA-CORRIDORS`
(§3), qui orchestre l'analyse topologique, les données de vision, les
observations terrain et les modèles comportementaux propres à chaque espèce.

**Portée :** génération d'un réseau continu, organique, spécifique à
l'espèce, cohérent avec le terrain réel et le comportement animal, dans un
rayon fonctionnel autour du waypoint utilisateur.

**Totale indépendance :** aucun corridor n'est lié à un affût, un abri, une
trace humaine ou une infrastructure de chasse. L'engine matérialise
uniquement le flux animal réel (§4).

## §1. SPÉCIFICITÉ PAR ESPÈCE — INTÉGRATION IA VISION ET IA-CORRIDORS

Règle d'or institutionnelle : **« un corridor = une espèce = une logique ».**

Aucune génération multi-espèces n'est permise dans un même corridor. Pour
chaque espèce ciblée (`cerf`, `orignal`, `wapiti`, `chevreuil`, `ours`,
`coyote`, etc.), un profil comportemental dédié est injecté par
`IA-CORRIDORS` à partir de :

- `IA VISION` : détections cartographiques automatisées (sentes, gagnages,
  abris visibles, rivières franchissables, ponts à castor, etc.)
- **Données terrain** : relevés locaux, observations consignées, données
  hydrologiques et forestières officielles
- **Modèles comportementaux par espèce** : sensibilité à la pente, besoin
  d'abri, préférence hydrique, motif journalier, saisonnalité

Le profil produit une **signature comportementale unique** utilisée comme
contrat de génération.

## §2. CE QUE LE CORRIDOR MATÉRIALISE — FLUX ANIMAL RÉEL IA

Le corridor N'EST PAS :
- un itinéraire optimal de chasse
- une ligne de tir
- une connexion vers un poste d'observation
- une route planifiée

Le corridor **EST** :
- la matérialisation spatiale du **flux animal réel** tel qu'inféré par
  `IA-CORRIDORS` à partir de la topologie, de l'hydrologie, de l'écologie
  et du comportement spécifique à l'espèce
- une **probabilité de passage** traduite en polyline organique Catmull-Rom
- un vecteur IA-assisté de **flux biologique**, indépendant de toute
  activité humaine

## §3. ENGINE IA-CORRIDORS — SECTION OBLIGATOIRE

`ENGINE IA-CORRIDORS` est une section interne scellée de l'engine CORRIDORS-Ω.
Elle est seule responsable de :

### 3.1 Analyse multi-couches
- **Topologie** : pentes, crêtes, combes, exutoires naturels
- **Hydrologie** : cours d'eau, points de franchissement, distance à l'eau
- **Écologie** : couverture forestière, gagnages, lisières, abris
- **Comportement** : motifs journaliers, sensibilité vent, rayon vital
- **Besoins naturels** : nourriture, eau, repos, reproduction

### 3.2 Fusion IA Vision + terrain
Injection et réconciliation des :
- détections `IA VISION` (sentes, abris, franchissements)
- observations terrain locales
- données officielles (hydro/forêt/relief)

### 3.3 Cartes produites
- **Carte de coût** (cost_surface par pixel, 0-1)
- **Carte de probabilité comportementale** (P_passage par cellule)
- **Carte de flux animal réel** (vecteurs directionnels)
- **Carte d'attractivité biologique** (multiplicateur écologique)

### 3.4 Génération & optimisation du réseau
- Sélection des corridors candidats
- Fusion des segments courts (< 40 m) en réseau continu
- Lissage Catmull-Rom par cellule IA
- Application du **rayon fonctionnel 600 m ± 30 %** autour du waypoint
  (soit **420 m à 780 m**)

### 3.5 Validation biologique/écologique/terrain-aware
Toute sortie d'`IA-CORRIDORS` DOIT passer les 6 contraintes obligatoires :

| Contrainte | Seuil |
|---|---|
| Segments droits | **≤ 20 m** |
| Angle entre deux segments consécutifs | **≤ 45°** |
| Isolement (orphelin du réseau) | **INTERDIT** |
| Spécificité espèce (profil assigné) | **OBLIGATOIRE** |
| Rayon fonctionnel autour waypoint | **420 m ≤ d ≤ 780 m** |
| Validation IA-CORRIDORS | **OBLIGATOIRE avant publication** |

Un corridor qui échoue à UNE seule de ces contraintes est **rejeté
automatiquement** par `ENGINE-TERRITOIRE-ANTI-REGRESSION-Ω`.

## §4. STRUCTURES NATURELLES — ANALYSÉES PAR IA-CORRIDORS

Les structures naturelles utilisées par `IA-CORRIDORS` comme substrats
d'inférence :

- **Topologie** : crêtes, combes, plateaux, vallées
- **Hydrologie** : ruisseaux, étangs, marais, zones humides
- **Écologie** : lisières forestières, clairières, régénérations, ravins
- **Comportementaux** : reposées, gagnages, traces, passages récents

Aucun élément anthropique (chemin forestier, affût, route, cabane) n'entre
dans cette analyse.

## §5. GÉOMÉTRIE — GÉNÉRÉE/OPTIMISÉE PAR IA-CORRIDORS

### 5.1 Structure organique
- **Polyline Catmull-Rom** avec 5 à 35 points de contrôle
- **Aucune ligne droite** > 20 m (rejet anti-regression)
- **Courbure continue** par interpolation cubique
- **Sinuosité espèce-dépendante** (0.2 à 0.7 selon profil)

### 5.2 Rayon fonctionnel
- Rayon : **600 m ± 30 %** autour du waypoint
- Borne basse : **420 m** (corridor minimum)
- Borne haute : **780 m** (corridor maximum)
- Tout corridor avec `start-to-end distance < 420 m` OU `> 780 m` est rejeté

### 5.3 Largeur écologique
- Largeur du corridor : **2 m à 10 m** (zone de passage physique)
- Représentée visuellement par `weight` Leaflet (échelle linéaire)
- Dépendante de la taille de l'espèce et de la topologie locale

### 5.4 Cardinalité
- Nombre de corridors par waypoint : déterminé par `IA-CORRIDORS` en
  fonction du profil espèce (5 à 12 typiquement)
- Pas de minimum/maximum imposé au-delà de l'interdiction d'isolement

## §6. CONTRAINTES OFFICIELLES — VALIDÉES PAR IA-CORRIDORS

| Dimension | Contrainte | Sanction si violation |
|---|---|---|
| **Topologique** | Pente ≤ `slope_tol` espèce | Corridor rejeté |
| **Hydrologique** | Distance eau ≥ 10 m (sauf franchissement) | Corridor rejeté |
| **Écologique** | Cover index ≥ 0.3 | Corridor rejeté |
| **Comportementale** | Profil espèce respecté | Corridor rejeté |
| **Géométrique** | Segments droits ≤ 20 m | Corridor rejeté |
| **Géométrique** | Angles ≤ 45° entre segments | Corridor rejeté |
| **Spatiale** | Longueur `start-to-end` ∈ [420, 780] m | Corridor rejeté |
| **Réseau** | Connecté au réseau (non isolé) | Corridor rejeté |
| **Spécificité** | Un corridor = une espèce = une logique | Corridor rejeté |
| **IA-CORRIDORS** | Validation obligatoire avant publication | Corridor rejeté |

## §7. SYNTHÈSE ULTIME — IA-ASSISTÉE

`ENGINE CORRIDORS-Ω` est **entièrement piloté par IA-CORRIDORS**.

Sa signature institutionnelle :
- **Autonome** : aucune dépendance aux affûts, abris, infrastructure humaine
- **Multi-espèces strictes** : profil unique par corridor
- **Organique** : Catmull-Rom, pas de droite > 20 m, pas d'angle > 45°
- **Fonctionnel** : rayon 600 m ± 30 % (420–780 m)
- **Écologique** : largeur 2–10 m
- **Validée IA-CORRIDORS** avant publication

Toute génération qui dévie de cette norme est automatiquement rejetée par
`ENGINE-TERRITOIRE-ANTI-REGRESSION-Ω` et journalisée. La baseline
`TERRITOIRE_Ω_STABLE` exige la conformité stricte à ce document.

---

## §8. VERROUILLAGE INSTITUTIONNEL

Document scellé par directive STEEVE-MAX 2026-04-20.

- **Version :** Ω-V1.0-2026-04-20
- **Statut :** NORME UNIQUE ET OBLIGATOIRE
- **Archives remplacées :** `/app/memory/_ARCHIVE_NON_ACTIVE/AFFUTS_CORRIDOR_*.md`,
  `AUDIT_CORRIDORS_EAU_*.md` (non actifs)
- **Anti-regression :** `ENGINE-IA-CORRIDORS-Ω` + `ENGINE-TERRITOIRE-ANTI-REGRESSION-Ω`
- **Test suite :** `test_ia_corridors_omega.py` (SELF-AUDIT-Ω)

**Toute référence aux affûts dans l'engine CORRIDORS a été définitivement supprimée.**
