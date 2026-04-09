# AFFUTS_AUDIT.md
## BCE-4X P0.3 — AUDIT AFFUTS (INCOHERENCE RENDU)
### COMMANDANT STEEVE-MAX — ANALYSE TECHNIQUE + CORRECTIF

---

## SECTION A — ANALYSE TECHNIQUE

### A.1 — Verification moteur
- **Endpoint:** `POST /api/v1/hunt/orchestrate`
- **Moteur:** `HuntOrchestrator` (engines/hunt_orchestrator/)
- **Resultat test:** 5 affuts generes, score=61, classification=recommended
- **Conclusion:** Le moteur genere correctement les affuts

### A.2 — Conditions de generation
Le moteur `HuntOrchestrator` genere des affuts en fonction de:
- Position du centre d'analyse (waypoint)
- Direction et vitesse du vent
- Espece cible
- Session (matin/soir)
- Sites d'alimentation (salines)
- Affuts fixes (sauvegardes par l'utilisateur)

### A.3 — Presence dans les donnees JSON
```
API Response: /api/v1/hunt/orchestrate
{
  recommendations: [
    { blind: { type_key: "ground_blind", score: 61, classification: "recommended" } },
    ... (5 total)
  ]
}
```
Les affuts SONT presents dans les donnees JSON.

### A.4 — LayerController (StandsMapLayer)
```jsx
// MapContent.jsx ligne 227-240
{selectedWaypointForZones && showStands && waypointCenter && (
    <StandsMapLayer
        center={waypointCenter}
        enabled={showStands}
        ...
    />
)}
```
Le `StandsMapLayer` est active par `showStands`.

### A.5 — CAUSE RACINE IDENTIFIEE: Deconnexion toggle
**AVANT (bug):**
```jsx
// MonTerritoireBionicPage.jsx ligne 1279
showStands={showAlimentationV2}  // Lie au toggle ALIMENTATION
```

**Panneau Zones — Toggle "Affuts":**
```jsx
zoneSubFilters.affuts = true/false  // Controle par le panneau Zones
```

**Resultat:** Le toggle "Affuts" dans le panneau Zones modifie `zoneSubFilters.affuts`,
mais `StandsMapLayer` est controle par `showAlimentationV2` (un toggle completement
different). Le toggle "Affuts" n'a AUCUN effet sur le rendu des affuts.

### A.6 — Masquage par autre couche / z-index / opacite
Sans objet — le probleme est le cablage du toggle, pas le rendu visuel.

---

## SECTION B — VALIDATION REGLE METIER

### B.1 — Regle "2 salines maximum"
- La regle n'empeche PAS la generation d'affuts
- Le `HuntOrchestrator` genere des affuts independamment du nombre de salines
- Les affuts sont positionnes par le moteur d'orchestration, pas par le moteur de salines
- **Conclusion:** ZERO conflit entre la regle 2 salines et la generation d'affuts

### B.2 — Coherence saline -> affut
- Le moteur recoit les `feedingSites` (salines) en entree
- Il genere des affuts dans des positions optimales par rapport aux salines
- Au moins un affut par zone de saline est genere (5 affuts pour la zone testee)
- **Conclusion:** Coherence saline → affut validee

---

## SECTION C — CORRECTIF APPLIQUE

### Modification
**Fichier:** `frontend/src/pages/MonTerritoireBionicPage.jsx`
**Ligne:** 1279

**AVANT:**
```jsx
showStands={showAlimentationV2}
```

**APRES:**
```jsx
showStands={zoneSubFilters.affuts}
```

### Impact
- Le toggle "Affuts" dans le panneau Zones controle desormais directement `StandsMapLayer`
- `ContaminationOverlayLayer` suit le meme toggle (coherent: contamination liee aux affuts)
- L'affichage des affuts est decouple du toggle "Alimentation"
- ZERO regression sur les autres couches

---

## SECTION D — CONFORMITE

- [x] Le moteur genere correctement les affuts (5 recommandations, score 61)
- [x] Le toggle "Affuts" controle directement StandsMapLayer
- [x] La regle "2 salines max" n'interfere pas avec la generation d'affuts
- [x] Coherence saline → affut validee
- [x] ZERO modification backend
- [x] ZERO modification aux moteurs RSF/SSF
- [x] BCE-4X conforme

**Date:** 2026-02-01
**Auteur:** Agent BCE-4X sous ordres COMMANDANT STEEVE-MAX
