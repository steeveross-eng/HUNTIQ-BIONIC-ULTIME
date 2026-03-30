# HUNTIQ-V6 — PRD
## PROTOCOLE BCE-4X | STEEVE-MAX-x3200-V6-CORE

---

## 1. Architecture
- **Backend:** FastAPI (Python) sur port 8001
- **Frontend:** React (CRA + craco) sur port 3000
- **Base de donnees:** MongoDB
- **Branche:** `STEEVE-MAX-x3200-V6-CORE`

## 2. STANDARD GOLDEN — Implemente (30 mars 2026)

### Composants STANDARD GOLDEN
- `GoldenCard`: fond #1E293B, ZERO bordure, accent bar 4px gauche, rounded-xl, box-shadow GOLDEN
- `GoldenCollapsible`: meme standard + icone en cercle colore + badge
- `GaugeMini`: SVG 64x64 avec valeur et label integres

### SUPRA v2 — STANDARD GOLDEN APPLIQUE
**Onglet ANALYSE:**
- Score SUPRA: nombre 32px, grade badge, zones vert/jaune/rouge
- Gauge ULTRA: rating 30px ("INSUFFISANT"), carences critiques
- Sol: icone cercle amber, accent bar amber
- Metabolisme: icone cercle orange, accent bar orange
- Vegetation: icone cercle vert, accent bar vert
- Hydrologie: icone cercle bleu, accent bar bleu
- Mineraux: barres colorees mini 6px
- Besoins nutritionnels: accent bars internes par niveau
- Ecozone: ORIGNAL (Alces americanus) corrige
- Recette, Couts: accent bars colorees
- Collapsibles PREMIUM: fermes par defaut (Physiologie, Comportement, Support, Sources)

**Onglet FICHE:**
- Score global: 32px, accent bar cyan
- 5 scores: nombre 30px, barres 6px, composants detailles
- 3 guides: icones cercles, badges GUIDE
- 20 sources: collapsible

### Alignement biologique ORIGNAL
- Store Zustand: defaut ORIGNAL (remplace CHEVREUIL)
- Props selectedSpecies propagees: MonTerritoireBionicPage -> NutritionPointDetailPanel
- SupraPage lit species depuis store global
- Ecozone: "Orignal (Alces americanus)"
- Besoins: "Sortie ravage + croissance bois massifs"

### Shadow/Watermark BIONIC SUPPRIME
- BionicLogoGlobal: retire de la page principale (/)
- Conserve uniquement sur pages ADMIN Premium

### PARTAGER 200% FONCTIONNEL — 13/13 CANAUX
1. Partage OS natif (iOS/Android)
2. Gmail
3. Outlook
4. Yahoo Mail
5. Facebook
6. Messenger
7. WhatsApp
8. X (Twitter)
9. LinkedIn
10. Instagram
11. TikTok
12. SMS
13. Copier lien
- Menu GOLDEN: fond #0F172A, icones cercles, typo 16px, ZERO bordure
- Master Switch ON par defaut, 13/13 canaux actifs
- Templates: Territoire, Premium, Viral

### Typographie 16px
- Labels: 14px text-slate-400
- Valeurs: 16px font-semibold text-white
- Titres: 16px font-bold text-white
- Scores principaux: 30-40px font-black

## 3. Documents crees
- `/app/HUNTIQ-V6-import/architecture/dashboard_standards.md` — Standard GOLDEN officiel

## 4. Fichiers modifies (session)
- `/app/frontend/src/components/territoire/NutritionPointDetailPanel.jsx`
- `/app/frontend/src/components/territoire/ui/ShareBionicButton.jsx`
- `/app/frontend/src/components/BionicLogo.jsx`
- `/app/frontend/src/pages/SupraPage.jsx`
- `/app/frontend/src/pages/MonTerritoireBionicPage.jsx`
- `/app/frontend/src/stores/useBionicStore.js`
- `/app/backend/modules/share_engine/router.py`

## 5. Backlog GELE
- [ ] Propagation STANDARD GOLDEN aux autres modules (Dashboard, Analyse Territoire, etc.)
- [ ] Purge shadcn/utils
- [ ] Pression historique chasse
- [ ] BSAA-2
- [ ] Merge main — INTERDIT
