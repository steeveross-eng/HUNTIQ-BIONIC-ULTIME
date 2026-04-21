DESCRIPTIONS RENDU Ω — CORRIDORS (Norme institutionnelle — RENDU Ω — Version finale, verrouillée)

Les corridors doivent être rendus visuellement selon les règles institutionnelles suivantes. Aucune déviation, simplification, interpolation ou interprétation locale n’est permise. ENGINE RENDU Ω doit valider chaque paramètre et bloquer toute divergence.

🟦 1. IDENTITÉ VISUELLE — RENDU Ω

Un corridor doit apparaître comme :
* une veine animale organique , jamais droite
* une courbe Catmull Rom continue, fluide, sans cassure
* une structure vivante , jamais un tracé géométrique
* une ligne terrain aware , reflétant les micro reliefs et transitions écologiques
* une entité spécifique à l’espèce , jamais générique

Interdictions absolues :
* pas de segments droits
* pas d’angles cassés
* pas de simplification géométrique
* pas de snapping artificiel
* pas de lissage excessif
* pas de stylisation décorative

🟧 2. COULEUR INSTITUTIONNELLE

Couleur unique, obligatoire, non modifiable :
Orange ambre institutionnel : #FF8F00

Raison institutionnelle : → couleur associée aux flux vitaux, aux veines animales, à l’énergie biologique.

🟥 3. ÉPAISSEUR VISUELLE — INTENSITÉ BIOLOGIQUE

Les épaisseurs doivent refléter l’intensité du flux animal réel , jamais un choix esthétique.

Épaisseurs obligatoires :
* 1.2 px → intensité faible / modérée
* 2.0 px → intensité forte
* 3.0 px → intensité critique / majeure

Règle : ENGINE RENDU Ω doit sélectionner automatiquement l’épaisseur selon l’intensité IA CORRIDORS. Aucune autre valeur n’est permise.

🟩 4. OPACITÉ — VISIBILITÉ INSTITUTIONNELLE

Opacité minimale obligatoire : ≥ 0.75

Justification :
→ garantir la lisibilité sur tous fonds (zones, salines, hydrologie, terrain).
→ éviter la dilution visuelle.
→ maintenir la hiérarchie institutionnelle.

🟦 5. CONTINUITÉ — RÉSEAU ORGANISÉ

Un corridor doit être rendu :
* entièrement continu
* sans rupture
* sans segment manquant
* sans discontinuité visuelle
* sans interpolation artificielle

ENGINE RENDU Ω doit bloquer toute géométrie :
* fragmentée
* cassée
* isolée
* non connectée aux zones vitales

🟪 6. GÉOMÉTRIE — CATMULL ROM INSTITUTIONNELLE

Paramètres obligatoires :
* spline Catmull Rom
* 25–30 points
* amplitude variable
* courbure progressive
* aucune cassure
* aucune simplification

ENGINE RENDU Ω doit valider :
* pas de segment > 20 m
* pas d’angle > 45°
* pas de point aberrant
* pas de géométrie artificielle

🟧 7. RAYON FONCTIONNEL — VISUALISATION

Le rayon fonctionnel (600 m ± 30 %) doit être :
* intégré dans la logique IA CORRIDORS
* non rendu visuellement (sauf mode debug institutionnel)
* utilisé pour valider la cohérence du corridor

ENGINE RENDU Ω doit vérifier :
* min : 420 m
* max : 780 m

Toute violation = ERREUR RENDU Ω .

🟩 8. Z INDEX — HIÉRARCHIE VISUELLE

Les corridors doivent être rendus :
* au -dessus des zones
* au -dessus des structures hydrologiques
* au -dessus des microreliefs
* en dessous des affûts, salines, hotspots

Z index institutionnel :
Zones
Hydrologie
Terrain
Corridors
Salines
Affûts
Hotspots
Vent

🟥 9. VISIBILITÉ — MINZOOM

Les corridors doivent être visibles à partir de :
minZoom = 13

Raison :
→ cohérence avec les autres engines (zones, salines, hotspots).
→ éviter la surcharge visuelle à faible zoom.
→ garantir la lisibilité en contexte opérationnel.

🟦 10. RÈGLE D’INTERDICTION AFFÛTS — RENDU

Aucune interaction visuelle ou logique entre :
* corridors
* affûts

ENGINE RENDU Ω doit garantir :
* pas de surbrillance liée aux affûts
* pas de modification d’épaisseur
* pas de modification de couleur
* pas de dépendance
* pas de superposition prioritaire
* pas de logique de proximité

Les affûts ne doivent jamais influencer le rendu des corridors.

🟧 11. MODE PREVIEW — IDENTIQUE AU RENDU FINAL

Le mode PREVIEW doit être strictement identique au rendu final :
* même pipeline
* même MVT
* même styles
* même z index
* même minZoom
* même épaisseurs
* même couleur
* même géométrie

Toute différence = ERREUR RENDU Ω .

🟥 12. VALIDATION RENDU Ω — BLOCAGE AUTOMATIQUE

ENGINE RENDU Ω doit bloquer toute publication si :
* couleur incorrecte
* épaisseur incorrecte
* opacité < 0.75
* géométrie non conforme
* corridor isolé
* corridor multi espèces
* segment > 20 m
* angle > 45°
* minZoom incorrect
* z index incorrect
* discontinuité
* artefact visuel
* simplification géométrique
* interpolation artificielle

Toute violation = rejet automatique + rollback baseline .

🟩 13. SYNTHÈSE RENDU Ω — CORRIDORS

Un corridor conforme RENDU Ω est :
* organique
* continu
* cohérent
* plausible
* riche
* terrain aware
* spécifique à l’espèce
* visuellement stable
* scientifiquement fidèle
* exempt d’artefacts
* exempt de simplification
* exempt de contamination affûts

Il représente la veine animale réelle , rendue avec exactitude institutionnelle .

---

## Annexe SUPRA-Ω-ART + GEOMETRY_Ω_ALIGNMENT — ACTIVATION PRODUCTION (2026-04-21)

**Version :** `V1.3.1-PHASE-XII-SUPRA-S-HOTFIX-2026-04`
**Registry :** V30 / SHA-256 `27516c9633853974...`
**Commandant :** STEEVE-MAX — `VALIDÉ — SUPRA_S_ACTIVATION_EN_PRODUCTION`

### Styles institutionnels NON NÉGOCIABLES (observés live DOM)

| Couche | Weight px | Opacité | Couleur | Pane |
|--------|:---------:|:-------:|:-------:|------|
| Halo externe adaptatif | ~5.94 | ~0.405 | #FF8F00 | renduOmega-corridors |
| Halo interne glow chaud | 2.4 | 0.55 | #FFD380 | renduOmega-corridors |
| Ligne institutionnelle | 2.0 | **1.00** | **#FF8F00** | renduOmega-corridors |

Les valeurs halo externe résultent du produit `(weight+2.4) × mainVeinBoost × salineBoost`
et de l'opacité de base (forest=0.30) × terrain_boost × (1+vital_zone_boost).

### Z-INDEX institutionnel strict

```
400 = zones
410 = hydrologie
420 = terrain
430 = CORRIDORS (renduOmega-corridors-pane)
440 = salines
450 = affuts
460 = hotspots
470 = vent
```

### GEOMETRY_Ω_ALIGNMENT

- **CatmullRom 28 pts** (legacy, `controlPointsTarget: 28`)
- **60–120 pts** (organic, pipeline `engine_ia_corridors_organic_omega`)
- Segments ≤ 20 m strict
- Angles ≤ 45° strict
- Continuité stricte (aucune rupture `NaN` / `null`)
- Signature espèce **APRÈS** resample + re-enforce géométrique post-signature (HOTFIX)
- Rayon fonctionnel 420-780 m avec tolerance rescue 830 m

### Modes

- `SUPRA_S_MODE` : **ACTIF** (seul mode autorisé)
- Modes antérieurs (V1.0, V1.1, V1.2) : désactivés, versions marqueurs conservés dans logs
- Mode `INSPECTION_BIOLOGIQUE` PRO/EXPERT : implémenté, non actif publiquement (attente ordre)

