# CHARTE OFFICIELLE BionicLegend — LEGENDE ULTIME BCE-4X
## BCE-4X GOLDEN V6+ | BRANCHE: BIONIC_REWRITE_P0
## DATE: 2026-04-07
## STATUT: CERTIFIE — EN ATTENTE VALIDATION STEEVE-MAX

---

# ================================================================
# SECTION 1 — DOCUMENTATION STRUCTURELLE
# ================================================================

## 1.1 — Logique complète d'affichage

```
BionicLegend.jsx
  |
  +-- Props d'entree:
  |     pipelineState  : { ready: bool }
  |     zoneCount      : number (zones ecologiques affichees)
  |     corridorCount  : number (corridors actifs)
  |     windDeg        : number (direction vent en degres)
  |     corridorData   : object (distribution par niveau)
  |     selectedSpecies: string (espece active)
  |     showCorridors  : bool (toggle corridors)
  |
  +-- State interne:
  |     isOpen         : bool (collapsed/expanded)
  |     expandedBlocks : { zones: bool, corridors: bool, factors: bool }
  |     hiddenItems    : { [itemId]: bool } (items masques par l'utilisateur)
  |
  +-- Rendu:
        COLLAPSED (isOpen=false):
          [Layers icon] LEGENDE {zoneCount}z {corridorCount}c >
          -> Click: setIsOpen(true)
        
        EXPANDED (isOpen=true):
          HEADER: "LEGENDE BIONIC" + ChevronDown
          SPECIES TAG: espece selectionnee
          BLOC A: Zones ecologiques (6 items)
          BLOC B: Corridors normatifs (5 niveaux)
          BLOC C: Facteurs environnementaux (7 items)
          FOOTER: "BCE-4X + Steeve-MAX | CORE"
```

## 1.2 — Conditions d'activation par module

| Module | Route | Rendu | Condition |
|--------|-------|:-----:|-----------|
| ANALYSE TERRITOIRE | `/analyse-territoire` | **OUI** | TOUJOURS (persistant dans MonTerritoireBionicPage) |
| MON TERRITOIRE | `/mon-territoire` | **OUI** | TOUJOURS (meme composant MonTerritoireBionicPage) |
| MON TERRITOIRE BIONIC | `/mon-territoire-bionic` | **OUI** | TOUJOURS (meme composant) |
| INTELLIGENCE | `/intelligence-v6` | NON | Dashboard analytique sans carte |
| DASHBOARD | `/dashboard` | NON | Dashboard sans carte |
| SUPRA | `/supra/:id` | NON | Panneau lateral, pas de carte |

**Regle : BionicLegend est rendue UNIQUEMENT dans les pages avec MapContainer.**

## 1.3 — Diagramme de rendu React

```
App.js
  |
  +-- <Route path="/analyse-territoire">
  |     +-- MonTerritoireBionicPage.jsx
  |           |
  |           +-- <MapContainer>
  |           |     +-- <TileLayer />
  |           |     +-- <MapContent>
  |           |     |     +-- <StandsMapLayer showLegend={false} />  <-- DESACTIVEE
  |           |     |     +-- <ContaminationOverlayLayer />
  |           |     |     +-- ...
  |           |     +-- </MapContent>
  |           |
  |           +-- <BionicLegend />  <-- LEGENDE ULTIME (position: absolute bottom-14 left-2)
  |           |     +-- COLLAPSED: bouton toggle
  |           |     +-- EXPANDED: 3 blocs (zones, corridors, facteurs)
  |           |
  |           +-- <MeteoWidget />
  |           +-- <ScoreChasse />
  |           +-- ...
```

## 1.4 — Dependances et points d'injection

| Dependance | Type | Detail |
|-----------|------|--------|
| `BionicLegend.jsx` | Fichier source | `/app/frontend/src/components/territoire/BionicLegend.jsx` (279 lignes) |
| `MonTerritoireBionicPage.jsx` | Point d'injection | Ligne 1292 — `<BionicLegend ... />` |
| `MapContent.jsx` | Desactivation concurrente | `showLegend={false}` (StandsMapLayer) |
| `lucide-react` | Icons | ChevronRight, ChevronDown, Trees, Navigation, Layers, Eye, EyeOff |
| React hooks | State | useState (isOpen, expandedBlocks, hiddenItems), useCallback, useMemo |

---

# ================================================================
# SECTION 2 — CHARTE OFFICIELLE BionicLegend
# ================================================================

## 2.1 — Typographies officielles

| Element | Taille | Poids | Couleur | Classe |
|---------|:------:|:-----:|---------|--------|
| Label collapsed "LEGENDE" | 10px | bold | gray-200 | text-[10px] font-bold |
| Compteurs collapsed | 9px | normal | gray-500 | text-[9px] |
| Header expanded "LEGENDE BIONIC" | 10px | bold | gray-100 | text-[10px] font-bold tracking-wider |
| Species tag | 9px | semibold | cyan-400/80 | text-[9px] font-semibold |
| Section title (Zones/Corridors/Facteurs) | 9px | bold | gray-300 | text-[9px] font-bold uppercase tracking-wider |
| Item label | 10px | normal | gray-300 | text-[10px] |
| Badge (compteur) | 9px | mono | gray-400 | text-[9px] font-mono |
| Footer | 8px | normal | gray-600 | text-[8px] |

## 2.2 — Couleurs officielles

### Zones ecologiques
| Zone | Couleur | Hex |
|------|---------|-----|
| Habitat optimal | Vert fonce | `#2E7D32` |
| Zone de rut | Orange-rouge | `#FF5722` |
| Zone de repos | Bleu | `#1976D2` |
| Alimentation | Jaune | `#F9A825` |
| Zones humides | Cyan | `#00ACC1` |
| Forets matures | Vert profond | `#1B5E20` |

### Corridors normatifs
| Niveau | Couleur | Hex | Largeur | Tiret |
|--------|---------|-----|:-------:|:-----:|
| CRITIQUE | Rouge sombre | `#CC0000` | 4m | OUI |
| MAJEUR | Rouge | `#FF0000` | 6m | NON |
| FORT | Orange | `#FF8C00` | 11m | NON |
| MODERE | Jaune | `#FFD700` | 17m | NON |
| FAIBLE | Gris | `#BFBFBF` | 26m | NON |

### Facteurs environnementaux
| Facteur | Couleur | Hex |
|---------|---------|-----|
| NDVI | Vert moyen | `#66BB6A` |
| Pentes | Brun | `#8D6E63` |
| Orientation | Violet | `#AB47BC` |
| Ensoleillement | Orange | `#FFA726` |
| Altitude relative | Gris-bleu | `#78909C` |
| Pression humaine | Rouge clair | `#EF5350` |
| Hydrologie | Bleu clair | `#29B6F6` |

### Couleurs structurelles
| Element | Couleur |
|---------|---------|
| Background | `#0c0c14/95` (rgba 12,12,20,0.95) |
| Border | gray-700/50 |
| Section separator | gray-800/40 |
| Hover | white/5 |
| Icon accent | cyan-400 |
| Footer text | gray-600 |

## 2.3 — Icones officielles (Lucide-React)

| Icone | Usage | Composant |
|-------|-------|-----------|
| `Layers` | Header + Bloc Facteurs | Icon generale legende |
| `Trees` | Bloc Zones ecologiques | Ecologie |
| `Navigation` | Bloc Corridors | Direction/deplacement |
| `ChevronRight` | Indicateur collapsed | Fleche ouvrir |
| `ChevronDown` | Indicateur expanded / bloc | Fleche fermer |
| `Eye` | Item visible | Visibilite ON |
| `EyeOff` | Item masque | Visibilite OFF |

## 2.4 — Structure officielle

```
BionicLegend
  |
  +-- MODE COLLAPSED
  |     [Layers] LEGENDE {N}z {N}c [>]
  |     Dimensions: auto-width, padding px-3 py-2
  |     Border: 1px gray-700/50, border-radius-lg
  |
  +-- MODE EXPANDED
        Width: 248px
        Max-height: 440px
        Overflow: auto
        |
        +-- HEADER
        |     [Layers] LEGENDE BIONIC [v]
        |     border-bottom gray-800/60
        |
        +-- SPECIES TAG
        |     Espece active (cyan)
        |     border-bottom gray-800/40
        |
        +-- BLOC A: ZONES ECOLOGIQUES
        |     [Trees] "ZONES ECOLOGIQUES" [N] [v]
        |     6 items: swatch-carre + label + toggle oeil
        |
        +-- BLOC B: CORRIDORS NORMATIFS
        |     [Navigation] "CORRIDORS" [N] [v]
        |     5 items: swatch-ligne + label + compteur + toggle oeil
        |
        +-- BLOC C: FACTEURS ENVIRONNEMENTAUX
        |     [Layers] "FACTEURS" [v]
        |     7 items: swatch-cercle + label + toggle oeil
        |
        +-- FOOTER
              "BCE-4X + Steeve-MAX" | "CORE"
```

## 2.5 — Items BCE-4X officiels

### BLOC A — Zones ecologiques (6 items)
1. Habitat optimal (#2E7D32)
2. Zone de rut (#FF5722)
3. Zone de repos (#1976D2)
4. Alimentation (#F9A825)
5. Zones humides (#00ACC1)
6. Forets matures (#1B5E20)

### BLOC B — Corridors normatifs (5 niveaux)
1. CRITIQUE (#CC0000) — dash, 4m
2. MAJEUR (#FF0000) — solid, 6m
3. FORT (#FF8C00) — solid, 11m
4. MODERE (#FFD700) — solid, 17m
5. FAIBLE (#BFBFBF) — solid, 26m

### BLOC C — Facteurs environnementaux (7 items)
1. NDVI (#66BB6A)
2. Pentes (#8D6E63)
3. Orientation (#AB47BC)
4. Ensoleillement (#FFA726)
5. Altitude relative (#78909C)
6. Pression humaine (#EF5350)
7. Hydrologie (#29B6F6)

**Total: 18 items officiels BCE-4X**

## 2.6 — Regles d'utilisation inter-modules

| Regle | Detail |
|-------|--------|
| R1 | BionicLegend est la SEULE legende autorisee sur les pages carte |
| R2 | Aucune autre legende (StandsMapLayer, DOM custom) ne doit etre rendue |
| R3 | BionicLegend est PERSISTANTE (visible des le chargement de la carte) |
| R4 | Position: absolute bottom-14 left-2 z-[1000] |
| R5 | Ne doit JAMAIS chevaucher: boutons zoom, meteo, GPS, waypoints |
| R6 | Chaque item est individuellement masquable (toggle Eye/EyeOff) |
| R7 | Les compteurs (zones, corridors) se mettent a jour dynamiquement |
| R8 | L'espece affichee correspond a selectedSpecies du store global |
| R9 | Background: 95% opacite, backdrop-blur-sm pour lisibilite carte |
| R10 | Max-height 440px avec scroll vertical pour ecrans reduits |

---

# ================================================================
# SECTION 3 — PREUVES INTER-MODULES
# ================================================================

## 3.1 — Verification automatisee

```
Page /analyse-territoire:
  BionicLegend: 1 (ATTENDU: 1)  CONFORME
  StandsMapLayer legend: 0 (ATTENDU: 0)  CONFORME
  Total legendes: 1  CONFORME
  BionicLegend visible: true  CONFORME
```

## 3.2 — Etat par module

| Module | BionicLegend | Visible | Duplication |
|--------|:------------:|:-------:|:-----------:|
| ANALYSE TERRITOIRE | RENDUE | **OUI** | **0** |
| MON TERRITOIRE | RENDUE | **OUI** | **0** |
| INTELLIGENCE | NON RENDUE | N/A | **0** |
| DASHBOARD | NON RENDUE | N/A | **0** |

## 3.3 — Validation absence de duplication

| Test | Resultat |
|------|:--------:|
| BionicLegend count == 1 | **PASS** |
| StandsMapLayer legend count == 0 | **PASS** |
| DOM custom legend count == 0 | **PASS** |
| Total legendes actives == 1 | **PASS** |

---

# ================================================================
# SECTION 4 — INTEGRATION P1 (HARMONISATION x1000%)
# ================================================================

## 4.1 — BionicLegend comme pivot P1

BionicLegend definit les REFERENCES VISUELLES pour toute l'harmonisation P1:

| Reference | Source BionicLegend | Application P1 |
|-----------|--------------------|--------------| 
| Couleurs zones | 6 couleurs (#2E7D32...) | Tous les composants zones |
| Couleurs corridors | 5 niveaux (#CC0000...) | Tous les composants corridors |
| Couleurs facteurs | 7 couleurs (#66BB6A...) | Tous les dashboards |
| Typographie section | 9px bold uppercase | Headers partout |
| Typographie items | 10px normal | Labels partout |
| Background | #0c0c14/95 | Fenetres, panneaux |
| Border | gray-700/50 | Bordures unifiees |
| Border-radius | rounded-lg (8px) | Tous les containers |
| Icon library | Lucide-React | Standard unique |

## 4.2 — Plan de correction des incoherences (7 identifiees)

| # | Incoherence | Module(s) | Correction P1 | Priorite |
|---|-----------|-----------|---------------|:--------:|
| D2 | Coords hardcodees 46.85,-71.25 | INTELLIGENCE | Synchroniser avec waypoint store global | **HAUT** |
| D3 | Espece fixe "deer" | DASHBOARD | Utiliser selectedSpecies du store | **HAUT** |
| C1 | Intelligence vs Dashboard sync | INTEL | DataFusionLayer ← store global | **HAUT** |
| D4 | Saison fixe "rut" | DASHBOARD | Calculer automatiquement depuis la date | MOYEN |
| M3 | Bouton retour absent | INTELLIGENCE | Ajouter bouton retour standard | MOYEN |
| D1 | BDRE health duplique | DASH/INTEL | Composant unique BDREHealthWidget | FAIBLE |
| M4 | Selecteur espece absent | DASHBOARD | Ajouter selecteur espece (comme Intelligence) | HAUT |

## 4.3 — Calendrier d'execution P1

| Phase | Contenu | Estimation |
|-------|---------|:----------:|
| P1-A | Synchronisation store global (D2, D3, C1, M4) | Premiere priorite |
| P1-B | Harmonisation typographique (BionicLegend reference) | Deuxieme priorite |
| P1-C | Unification composants BDRE (D1) | Troisieme priorite |
| P1-D | UX polish + boutons retour (M3, D4) | Quatrieme priorite |
| P1-E | Export PDF | Cinquieme priorite |
| P1-F | Certification finale P1 | Derniere etape |

## 4.4 — Specifications AVANT/APRES P1

### DASHBOARD (AVANT → APRES)
| Element | AVANT | APRES P1 |
|---------|:-----:|:--------:|
| Espece | "deer" (fixe) | Selecteur dynamique (orignal, chevreuil...) |
| Saison | "rut" (fixe) | Auto (date courante) |
| BDRE header | Standalone | Composant unifie BDREHealthWidget |
| Typo labels | 9-10px | 10px (BionicLegend ref) |

### INTELLIGENCE (AVANT → APRES)
| Element | AVANT | APRES P1 |
|---------|:-----:|:--------:|
| Coords | 46.85, -71.25 (fixe) | Waypoint actif (store global) |
| Bouton retour | ABSENT | Bouton retour standard |
| BDRE widget | Standalone | Composant unifie BDREHealthWidget |

### FICHE/SUPRA (AVANT → APRES)
| Element | AVANT | APRES P1 |
|---------|:-----:|:--------:|
| Typo titre | 14px | Coherent avec BionicLegend (ref 10px sections) |
| Score BDRE | Standalone | Composant unifie |

---

# ================================================================
# SECTION 5 — VERDICT
# ================================================================

| Livrable | Statut |
|----------|:------:|
| Documentation structurelle | **LIVRE** |
| Charte officielle BionicLegend | **LIVRE** |
| Preuves inter-modules | **LIVRE** |
| Integration P1 | **LIVRE** |
| Plan correction incoherences | **LIVRE** |
| Calendrier P1 | **LIVRE** |
| AVANT/APRES annotes | **LIVRE** |
| BionicLegend = LEGENDE ULTIME | **CERTIFIE** |

**PREREQUIS P1: TOUS SATISFAITS**

---

## SIGNATURES

| Role | Identifiant |
|------|-------------|
| Autorite | COMMANDANT STEEVE-MAX |
| Agent | EMERGENT E1 |
| Date | 2026-04-07 |
| Branche | BIONIC_REWRITE_P0 |
| Statut | **CERTIFIE — EN ATTENTE VALIDATION STEEVE-MAX** |
