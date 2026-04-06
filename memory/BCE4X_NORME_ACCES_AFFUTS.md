# BCE-4X — NORME OFFICIELLE ACCES AFFUTS
## VERSION CONSOLIDEE A → L
## Autorite : COMMANDANT STEEVE-MAX | Date : 2026-04-06
## Statut : OBLIGATOIRE — Applicable a tout calcul d'acces affut

---

## A) NOUVELLE PASSE STRICTE WAYPOINT
- Waypoint → premier corridor = 0% foret dense obligatoire.
- Aucun segment foret > 20 m.
- Aucun segment hors-sentier.
- Detour autorise pour atteindre un corridor reel.
- Corridor virtuel obligatoire si le terrain reel le justifie.

## B) EXCLUSIONS TERRITORIALES BCE-4X (1000%)
INTERDITS : routes, highways, residentiel, eau, rivieres, ruisseaux, marecages, zones sensibles, infrastructures.
Penalite minimale : INTERDIT ou cout >= 1 000 000.
Toute violation = recalcul automatique.

## C) NORMES STEEVE-MAX
- 95% corridors reels OSM. 5% foret dense maximum.
- Sentiers > chemins > clairieres > foret dense.
- MATCHES_HUNTER=True obligatoire.
- Distance corridor → affut minimale.

## D) GUIDANCE TERRAIN STEEVE-MAX
1. Toujours suivre un corridor reel des le depart.
2. Priorite aux embranchements logiques.
3. Foret dense limitee a 20 m/segment et 5% total.
4. Approche finale : penetration 90 degres vers l'affut.
5. Aucun zigzag, aucun detour inutile.
Exemple SAL-06 : LUC → ouest ~100m, embranchement sud ~350m, penetration 90 degres est.

## E) PREUVE VISUELLE CONFORME
Corridors reels, exclusions, acces optimal, acces genere, 95/5, GUIDANCE.

## F) P2
P2 demeure gele. Aucune activation M5 ou BSAA-2.

## G) CORRIDORS VIRTUELS
- Tout waypoint injecte comme noeud du graphe.
- Connexion aux sentiers proches via corridor virtuel valide satellite.
- Segment institutionnel permanent.
- Reutilisation pour toutes les requetes futures.

## H) PRE-CERTIFICATION DES ACCES AFFUTS
- Tous les acces pre-calcules, valides et stockes.
- Utilisateurs consultent UNIQUEMENT des acces pre-certifies.
- Aucun A* brut en temps reel.
- Recalcul complet autorise SEULEMENT pour : nouvel affut, nouveau territoire, changement majeur.

## I) ARCHITECTURE LOURDE / LEGERE
1. Calcul institutionnel lourd (offline) : graphe, corridors virtuels, routage multi-affuts, certification, preuves visuelles.
2. Consultation operationnelle legere (online) : interrogation rapide < 1 seconde, affichage instantane, aucun recalcul.

## J) GESTION "AUCUNE ZONE GENEREE"
1. Audit immediat des filtres.
2. Mode resolution controlee si corridors visibles satellite.
3. Creation obligatoire corridor virtuel si terrain le permet.
4. Interdiction du "rien" si corridors existent reellement.

## K) GARANTIE DE NON-REGRESSION
- Toute disparition affuts/zones/sites = ERREUR BLOQUANTE.
- Audit obligatoire : objets attendus vs visibles.
- Interdiction du filtrage silencieux.
- Rapport obligatoire : AFFUTS_ZONES_NON_REGRESSION_REPORT.md.

## L) PRESERVATION OBJETS INSTITUTIONNELS
Objets INTOUCHABLES : affuts (fixes/mobiles), sites alimentation, zones contamination, zones ecologiques, corridors virtuels.
Les filtres BCE-4X s'appliquent UNIQUEMENT sur les trajets, JAMAIS sur les objets.
CACHE INSTITUTIONNEL PERMANENT : affuts, zones, sites, corridors, graphes locaux.
Aucun recalcul en temps reel autorise.
Disparition objet = ERREUR BLOQUANTE → audit + justification + correction.
Temps de reponse : affichage zones/affuts < 1s, acces affuts < 1s (pre-certifies).

---

**FIN DE LA NORME — APPLICABLE IMMEDIATEMENT**
