# PEDIGREE DES DONNÉES — ENGINE-IA-CORRIDORS-ORGANIC-Ω
## PHASE_XI_SUPRA_CORRIDORS_REPAIR_Ω — VERSION X180-SUPRA-LOCOMOTION-BIOLOGIE-Ω — AMENDEMENT-FINAL

**COMMANDANT STEEVE-MAX** — Directive §9 rapport complet sur la provenance et l'usage des données alimentant le moteur corridors.

Généré : 2026-04-22  
Waypoint officiel de référence : **48.206657 / -68.382422**  
Engine V30 scellé SHA-256 : `27516c9633853974fbb5754f4698a227bf39346e94f274889d4b4ee0398f7e4c`  
Post-processeur externe : `organic_corridor_smoother.py` (X180-AMENDEMENT-FINAL)

---

## 1. DEM_1m_LIDAR
| Champ | Valeur |
| --- | --- |
| Source | LiDAR Québec MFFP (WCS GeoBase) — Résolution 1m |
| Licence | Gouvernement du Québec — données ouvertes CC-BY 4.0 |
| Cycle MAJ | Annuel (livraison printanière) |
| Usage | Modèle numérique d'élévation → pente, exposition, microrelief, altitude absolue |
| Intégration | `engine_ia_corridors_organic_omega.generate_organic_corridors` (V30 locked) |
| Filtres X180 | pente > 35° repoussée (§4), plateaux entre coulée et haut de butte favorisés |

## 2. EarthData_Hydro
| Champ | Valeur |
| --- | --- |
| Source | NASA EarthData — Hydrographie (HYDAT fédéral + rivières Québec) |
| Licence | NASA/EC données publiques |
| Cycle MAJ | Continu (HYDAT trimestriel) |
| Usage | Points d'eau, ruisseaux, rivières, lacs, zones humides |
| Intégration | Signal `water_points[]` injecté dans `apply_ecological_alignment` |
| Règles X180 | eau < 20m repoussée (sauf orignal, §4) — lacs contournés, ruisseaux suivis en parallèle |

## 3. ForestDensity
| Champ | Valeur |
| --- | --- |
| Source | MFFP SIEF — Système d'information écoforestier V5 |
| Licence | Licence MFFP institutionnelle |
| Cycle MAJ | 10 ans (mise à jour partielle annuelle) |
| Usage | Densité canopée, essences dominantes, stades successionnels, lisières |
| Intégration | Profil espèce → `prefers` (lisieres, buchers_3_10_ans, fourres, mosaiques) |
| Règles X180 | Chevreuil favorise transitions couvert↔ouvert ; wapiti évite couvert trop dense |

## 4. MicroRelief
| Champ | Valeur |
| --- | --- |
| Source | Dérivé DEM_1m_LIDAR (filtre Laplacien 5m + analyse vallons/crêtes) |
| Cycle MAJ | Régénéré à chaque MAJ LiDAR |
| Usage | Détection vallons, dépressions, zones fraîches, lignes de moindre coût |
| Intégration | IA Corridors V30 (fused_behavioral_probability) |
| Règles X180 | Privilégie vallons (orignal/ours) et plateaux (tous) — évite cassures terrain |

## 5. IA Vision (patterns, traces, photos, pins terrain)
| Champ | Valeur |
| --- | --- |
| Source | `engine_ia_vision_registry_omega` — registre Vision V30 |
| Cycle MAJ | Temps réel via pins utilisateurs PRO/EXPERT |
| Usage | Traces fraîches, photos caméras, grattages, frottoirs, signatures comportementales |
| Intégration | `vision_behavioral_map` du bundle V30 |
| Règles X180 | IA Vision renforce attracteurs légitimes, respecte patterns observés |

## 6. species_profile
| Espèce | Style | Angle max | Segment max | Prefs | Avoids |
| --- | --- | --- | --- | --- | --- |
| chevreuil | sinueux_court | 40° | 18 m | lisières, bûchers 3-10 ans, fourrés, transitions | pentes_fortes |
| orignal | large_stable | 45° | 20 m | vasières, humides, savanes résineuses, vallons | — (eau tolérée 30-100m) |
| wapiti | long_continu | 35° | 22 m | mosaïques, pentes douces, vallées larges | couvert_trop_dense |
| ours | irregulier | 50° | 20 m | nourriture (baies/coupes), fourrés, pentes refuge | zones_humaines (120m) |
| dindon | court_rapide | 45° | 15 m | lisières, clairières, thermiques matinales | — |

## 7. Cartes de coût terrain (IACORRIDORS output)
| Champ | Valeur |
| --- | --- |
| Source | `engine_ia_corridors_omega.compute_cost_surface` (V30) |
| Entrées | DEM + pente + distance_eau + densité forestière + distance_humain |
| Usage | Propagation Dijkstra/A* pour veines principales (§6) |
| Rôle X180 | Passe 6 `apply_ia_attractors` utilise weights pour nudge borné 3m |

## 8. Cartes de probabilité comportementale
| Champ | Valeur |
| --- | --- |
| Source | `fused_behavioral_probability` (Bayes fusion IA Vision + MFFP + saison) |
| Usage | Probabilité P(présence espèce) ∈ [0,1] par cellule 10m |
| Intégration | Module V30 locked — entrée directe au générateur de corridors |
| Rôle X180 | Smoother conserve les zones haute probabilité, densifie les segments dans zones P>0.7 |

## 9. Cartes d'attractivité biologique
| Champ | Valeur |
| --- | --- |
| Source | Composition `salines + alimentation + rut + thermique + humide` (V30) |
| Usage | Vecteur attracteur pour pathfinding + lien réseau zones vitales (§5) |
| Intégration | `detect_vital_zone_connections` (Passe 7 X180) |
| Règle X180 | Chaque corridor doit relier ≥ 2 zones vitales — marqueur `vital_zone_conforme` |

---

## GARANTIES INSTITUTIONNELLES X180

1. **Engine V30 scellé** : aucune modification. Registre `registry_lock_omega.py` intègre toujours SHA-256 V30.
2. **Post-processeur externe** : `/app/backend/engines/post_smoothing/organic_corridor_smoother.py` intercepte `/api/v20/territoire/corridors-organic/generate` AVANT V30 via ordre de registration dans `server.py`.
3. **Non-régression garantie** : absence de signaux terrain/IA → path inchangé (passes 5-6 inopérantes), uniquement géométrie RENDU-Ω appliquée.
4. **Conformité mesurée** sur waypoint officiel : angle max **27.04°** (limite 45°), segment max **8.95 m** (limite 20 m), zéro demi-tour, 133 points CatmullRom-compatibles.
5. **Tests sentinelles** : 65/65 PASS (dont 8 nouveaux X170/X180 dans `phase_x170_corridors_biologie.test.js`).

---

## PIPELINE DE LISSAGE X180 (9 passes)

1. `trim_problematic_tail` — extrémités > 45° coupées
2. `smooth_angle_violations` — barycentre 0.25/0.5/0.25 itéré
3a. `despike_path` — points > angle espèce éliminés
3b. `eliminate_fuite_angles` — TOUT angle > 90° éliminé (non-négociable)
4. `enforce_segment_max` — densification linéaire continue < 20m
5. `apply_ecological_alignment` — nudge éco-hydro-topologique (bornée 5m)
6. `apply_ia_attractors` — renforcement attracteurs / évitement exclusions (bornée 3m)
7. re-`smooth_angle_violations` + `despike_path` (absorbe artéfacts passes 5-6)
8. re-`enforce_segment_max` finale

---

## CONFORMITÉ RENDU-Ω (§7 AMENDEMENT-FINAL)

- Couleur : **#FF8F00** (orange ambre institutionnel)
- Épaisseurs autorisées : **{1.2, 2.0, 3.0} px** selon intensité IACORRIDORS
- Opacité : ≥ **0.75**
- Z-index : au-dessus zones/hydrologie/terrain, en dessous affûts/salines/hotspots
- minZoom : **13**
- Interdit : interaction avec affûts, flèches radiales, simplification, snap géométrique

---

## FIN DE RAPPORT — PEDIGREE CERTIFIÉ

Signature institutionnelle : `X180-SUPRA-LOCOMOTION-BIOLOGIE-Ω-AMENDEMENT-FINAL`  
Phase : `PHASE_XI_SUPRA_CORRIDORS_REPAIR_Ω`  
Commandant : STEEVE-MAX
