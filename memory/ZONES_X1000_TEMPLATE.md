# ZONES_X1000 — TEMPLATE DESCRIPTIF (PHASE M — À REMPLIR)

> **Statut :** TEMPLATE VIDE — prêt à remplir lors de la Phase M opérationnelle
> **Baseline legacy :** `engine_zones.py` (V1 pre-Omega, 14-20 vertices)
> **Cible :** `zones_organic_v1.py` → futur `ENGINE-ZONES-ORGANIC-Ω`
> **Gain attendu :** ×1000 en fidélité biologique, résolution spatiale et cohérence multi-échelles

---

## 1. Description biomimétique
> Comment les zones devraient être perçues par une biologiste de terrain ?
> Veines animales, flux, convergences, répulsions.
- [ ] Représentation visuelle organique (à définir)
- [ ] Perception biologique (à définir)

## 2. Logique multi-échelles
> Intégration macro (1 km) → méso (300 m) → micro (30 m) → fine (1 m LIDAR)
- [ ] Macro-vallées (DEM 1 m)
- [ ] Micro-coulées (LIDAR haute résolution)
- [ ] Drainage lines
- [ ] Slope breaks
- [ ] Shadow relief
- [ ] Mosaïque forestière

## 3. Dynamique saisonnière
> Zone de rut ≠ zone de vêlage ≠ zone hivernage
- [ ] Hiver (12-1-2)
- [ ] Pré-rut (9-10)
- [ ] Rut (10-11)
- [ ] Post-rut (12)
- [ ] Printemps (3-4-5)
- [ ] Été (6-7-8)

## 4. Dynamique comportementale
> Prudence, amplitude, vitesse, ouverture préférée par espèce
- [ ] Profil comportemental chevreuil
- [ ] Profil comportemental orignal
- [ ] Profil comportemental wapiti
- [ ] Profil comportemental ours noir
- [ ] Profil comportemental dindon sauvage

## 5. Attracteurs multi-espèces
> Une même zone peut être d'intérêt pour plusieurs espèces
- [ ] Zone alimentation partagée
- [ ] Zone repos thermique partagée
- [ ] Zone humide multi-espèces
- [ ] Zone de transition écologique

## 6. Micro-relief LIDAR
> Intégration LIDAR WCS 1 m
- [ ] Détection dépressions
- [ ] Détection crêtes
- [ ] Détection vallons
- [ ] Détection plateaux

## 7. Intégration IA Vision
> Croisement avec `vision_behavioral_map_v2`
- [ ] Zones probables repos
- [ ] Zones probables alimentation
- [ ] Zones probables thermique
- [ ] Zones probables humide
- [ ] Fiabilité terrain

## 8. Modèle prédictif
> Anticipation via cycles pluriannuels + climat futur
- [ ] Évolution saisonnière
- [ ] Pression humaine
- [ ] Changements hydrologiques

## 9. Modèle génératif
> Proposition de zones non encore identifiées
- [ ] Zones candidates alternatives
- [ ] Scénarios prospectifs
- [ ] Zones prédictives

## 10. Réseau intelligent
> Zones = nœuds du réseau corridors_organic
- [ ] Hiérarchie primaire / secondaire / marginale
- [ ] Interconnexion avec corridors_organic
- [ ] Flux dynamiques

## 11. Rendu organique
> Gradient, halo, densité, mode heat
- [ ] Couleur par type (vert alimentation, bleu repos, rouge rut)
- [ ] Gradient périphérique
- [ ] Halo d'influence
- [ ] Mode density / heat / veine_animale

## 12. Interactions corridors_organic
> Comment les zones nourrissent et sont nourries par les corridors
- [ ] Zone = start de corridor
- [ ] Zone = end de corridor
- [ ] Zone = nœud intermédiaire
- [ ] Zone = attracteur pour attraction/répulsion corridors

---

**À compléter lors de la directive Phase M opérationnelle.**
