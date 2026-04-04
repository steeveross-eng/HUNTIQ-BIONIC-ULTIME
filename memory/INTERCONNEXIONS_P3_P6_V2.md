# INTERCONNEXIONS_P3_P6_V2 — INTERCONNEXIONS INTER-MODULES BIONIC OS
## Directive x5310-STEEVE_MAX — Version 2.0.0
### Protocole BCE-4X GOLDEN V6+ | Autorite : STEEVE-MAX
### Date : 2026-04-05 | Merge MAIN : STRICTEMENT INTERDIT
### Reference : AUBO_V2.md Section 12 + INTERCONNEXIONS_P3_P6 V1 + ARCHITECTURE_INTERCONNEXION V1
### Base : V1 (209 lignes) + V1 ARCH (208 lignes) — ZERO LOSS

---

# TABLE DES MATIERES

1. [VUE D'ENSEMBLE V2](#1-vue-densemble-v2)
2. [SCHEMA D'INTERCONNEXION GLOBAL V2](#2-schema-dinterconnexion-global-v2)
3. [P3 — MARKETING x PARTAGE x ANALYTICS](#3-p3-marketing-x-partage-x-analytics)
4. [P4 — INTELLIGENCE x STRATEGIE x IA](#4-p4-intelligence-x-strategie-x-ia)
5. [P5 — MONETISATION x PAIEMENT x UPSELL](#5-p5-monetisation-x-paiement-x-upsell)
6. [P6 — TERRITOIRE x NAVIGATION x CAMERA](#6-p6-territoire-x-navigation-x-camera)
7. [MATRICE DES FLUX V2](#7-matrice-des-flux-v2)
8. [REGLES D'INTERCONNEXION V2](#8-regles-dinterconnexion-v2)
9. [CONSOLIDATION V6 — IMPACTS](#9-consolidation-v6-impacts)
10. [STATUTS ET DEPENDANCES](#10-statuts-et-dependances)
11. [RISQUES ET MITIGATIONS V2](#11-risques-et-mitigations-v2)

---

# 1. VUE D'ENSEMBLE V2

## 1.1 Changements V1 → V2

| Aspect | V1 | V2 |
|--------|-----|-----|
| Document base | INTERCONNEXIONS_P3_P6.md (209L) | Document fusionne avec ARCHITECTURE_INTERCONNEXION.md |
| Modules documentes | 5 (SUPRA, Strategie, IA, Admin, BCE) | 20+ (ajout Marketing, E-Commerce, Territoire, Social) |
| Phases couvertes | P3-P6 (SUPRA-centric) | P3-P6 (vision globale multi-pipeline) |
| Consolidation V6 | Non documente | Impacts detailles (facades, deprecated, renommages) |
| Statuts | Approximatifs | Exacts (base sur AUBO_V2 audit) |

## 1.2 Principes preserves (ZERO LOSS)

Toutes les regles V1 restent valides :
- Validation BCE-4X obligatoire sur TOUS les flux inter-modules
- Logs immutables (lecture seule)
- Rollback automatique en cas de regression
- Aucune contradiction inter-modules permise
- Admin Premium = Orchestrateur unique

---

# 2. SCHEMA D'INTERCONNEXION GLOBAL V2

```
                         ┌──────────────────────┐
                         │    BCE-4X ENGINE      │
                         │  (Gouvernance Supreme)│
                         │  15 validateurs       │
                         │  golden_state.json    │
                         └──────────┬───────────┘
                                    │
                 Validation obligatoire sur TOUS les flux
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
┌───────▼───────┐          ┌───────▼───────┐          ┌───────▼───────┐
│ ADMIN PREMIUM │          │   SUPRA v2    │          │ INTELLIGENCE  │
│ 210 endpoints │          │ bionic_engine │          │     IA        │
│ Orchestrateur │          │  _p0 (154ep)  │          │  ai_engine    │
│ Master Switch │          │ + pipeline    │          │  15 endpoints │
└───────┬───────┘          └───────┬───────┘          └───────┬───────┘
        │                          │                           │
        │    ┌─────────────────────┼─────────────────────┐     │
        │    │                     │                     │     │
        │    │         ┌───────────▼───────────┐         │     │
        └────┼────────►│  STRATEGIE DU JOUR    │◄────────┼─────┘
             │         │  strategy_master (12ep)│         │
             │         │  + predictive (7ep)    │         │
             │         └───────────────────────┘         │
             │                                           │
   ┌─────────▼─────────────────────────────────▼─────────┐
   │              MOTEURS DE DONNEES (core/)              │
   │  weather | ecology | corridors | ndvi | pressure     │
   │  geo | rest | scoring_pipeline (20 sous-moteurs)     │
   └──────────────────────────┬──────────────────────────┘
                              │
        ┌─────────────────────┼──────────────────────┐
        │                     │                      │
┌───────▼───────┐    ┌───────▼───────┐     ┌────────▼───────┐
│  P3 MARKETING │    │ P5 MONETISAT. │     │ P6 TERRITOIRE  │
│  share_engine │    │ payment_eng.  │     │ territory_eng. │
│  marketing    │    │ freemium      │     │ waypoint_eng.  │
│  seo_engine   │    │ upsell        │     │ camera_engine  │
│  tracking     │    │ products      │     │ live_heading   │
│  analytics    │    │ Stripe        │     │ trips_logger   │
│  referral     │    └───────────────┘     └────────────────┘
│  bsaa (GELE)  │
└───────────────┘
```

---

# 3. P3 — MARKETING x PARTAGE x ANALYTICS

## 3.1 Modules concernes

| Module | Prefix API | Endpoints | Statut V2 |
|--------|-----------|-----------|-----------|
| share_engine | /api/share | 11 | OPERATIONNEL (EASYlead V1 actif) |
| marketing_engine | /api/v1/marketing | 22 | OPERATIONNEL |
| marketing_calendar_engine | /api/v1/marketing-calendar | 13 | OPERATIONNEL |
| seo_engine | /api/v1/bionic/seo | 59 | OPERATIONNEL |
| tracking_engine | /api/v1/tracking-engine | 22 | OPERATIONNEL |
| analytics_engine | /api/v1/analytics | 11 | OPERATIONNEL |
| referral_engine | /api/v1/referral | 15 | OPERATIONNEL |
| contact_engine | /api/v1/contact-engine | 7 | OPERATIONNEL |
| bsaa | /api/bsaa | 9 | ARCHITECTURE DEFINIE — Implementation GELEE |

## 3.2 Flux de donnees P3

```
[PARTAGE]                           [MARKETING]                    [ANALYTICS]
share_engine                        marketing_engine               analytics_engine
    |                                    |                              |
    +--→ EASYlead generate              |                              |
    |    (screenshot + watermark)        |                              |
    |    (14 canaux sociaux)            |                              |
    |                                    |                              |
    +--→ share_events (MongoDB)         |                              |
    |    channel, template, url          |                              |
    |    has_weather, timestamp          |                              |
    |                                    |                              |
    +────────────────────────────────────▼                              |
    |    EASYlead tracking              marketing_events               |
    |    easylead_clicks (MongoDB)      marketing_contacts             |
    |                                    |                              |
    +────────────────────────────────────+──────────────────────────────▼
         |                              |                     tracking_engine
         |                              |                     sessions, events
         |                              |                     heatmaps
         |                              |                              |
         +--→ contact_engine ←──────────+                              |
         |    marketing_contacts        |                              |
         |    lead scoring              |                              |
         |                              |                              |
         +--→ referral_engine           +--→ seo_engine                |
              referral codes                 SEO x300 fournisseurs     |
              tracking                       meta tags, sitemap        |
              recompenses                                              |
                                        +--→ marketing_calendar_engine |
                                             evenements, rappels       |
                                             campagnes planifiees      |
```

## 3.3 Flux inter-modules P3

| Source | Destination | Donnee | Format | Validation BCE-4X |
|--------|------------|--------|--------|-------------------|
| share_engine | marketing_engine | Evenement partage | share_events record | Timestamp + channel valide |
| share_engine | contact_engine | Lead capture | email, source, channel | Email valide + source tracee |
| share_engine | tracking_engine | Click tracking | easylead_clicks | ref_user_id + timestamp |
| marketing_engine | analytics_engine | Campagne metrics | marketing_events | event_type + data schema |
| tracking_engine | analytics_engine | Session data | sessions, events | user_id + timestamp < 24h |
| seo_engine | marketing_engine | SEO metrics | page_rank, keywords | Score + source identifiee |
| referral_engine | marketing_engine | Referral events | code, conversion | Code valide + tracking |
| contact_engine | marketing_engine | Lead score | score, tags, status | Score 0-100 + statut valide |

## 3.4 Statut implementation P3

| Composant | Statut | Notes |
|-----------|--------|-------|
| EASYlead V1 (generate + track) | OPERATIONNEL | 14 canaux, screenshot + watermark |
| Marketing automation | OPERATIONNEL | Segmentation, campagnes |
| SEO x300 fournisseurs | OPERATIONNEL | 59 endpoints |
| Lead capture auto | OPERATIONNEL | contact_engine actif |
| Analytics tracking | OPERATIONNEL | Sessions, events, temps reponse |
| BSAA (Social Ads) | ARCHITECTURE DEFINIE | Implementation GELEE par STEEVE-MAX |

---

# 4. P4 — INTELLIGENCE x STRATEGIE x IA

## 4.1 Modules concernes

| Module | Prefix API | Endpoints | Statut V2 |
|--------|-----------|-----------|-----------|
| bionic_engine_p0 | /v1/bionic | 154 | OPERATIONNEL (10 sous-moteurs + 38 sous-routeurs) |
| strategy_master_engine | /api/v1/strategy-master | 12 | OPERATIONNEL |
| ai_engine | /api/v1/ai | 15 | OPERATIONNEL |
| recommendation_engine | /api/v1/recommendation | 11 | OPERATIONNEL |
| bionic_knowledge_engine | /api/v1/bionic/knowledge | 35 | OPERATIONNEL |
| supra_advanced | /api/v6/supra/advanced | 4 | OPERATIONNEL |
| nutrition_intelligence | /api/v6/nutrition-intelligence | 35 | OPERATIONNEL |
| predictive_engine | /api/v1/predictive | 7 | OPERATIONNEL |

## 4.2 Flux de donnees P4

```
[PIPELINE SUPRA]                    [STRATEGIE]                  [IA]
bionic_engine_p0                    strategy_master_engine        ai_engine
    |                                    |                           |
    +--→ 10 sous-moteurs               |                           |
    |    SSE→OSG→CME→WSE→VFE           |                           |
    |    →SSVL→TCVE→PME→BMPE→TFE       |                           |
    |                                    |                           |
    +--→ Score /100 + 32 criteres       |                           |
    |                                    |                           |
    +────────────────────────────────────▼                           |
    |    Scores + zones + corridors     Plans de chasse globaux     |
    |                                   Multi-especes               |
    |                                   Optimisation                |
    |                                    |                           |
    +────────────────────────────────────+───────────────────────────▼
         |                              |                    Recommandations
         |                              |                    Analyse intelligente
         |                              |                    Knowledge base
         |                              |                           |
         +--→ supra_advanced ←──────────+                           |
         |    Analyse multi-criteres    |                           |
         |                              |                           |
         +--→ nutrition_intelligence    +--→ predictive_engine      |
         |    Intelligence nutritionnelle    Probabilites succes    |
         |                                   Timing optimal        |
         |                                                          |
         +--→ bionic_knowledge_engine ←─────────────────────────────+
              Donnees scientifiques
              Base de connaissances
              Sources references
```

## 4.3 Flux inter-modules P4

| Source | Destination | Donnee | Format | Validation BCE-4X |
|--------|------------|--------|--------|-------------------|
| bionic_engine_p0 | strategy_master | Score /100 + 32 criteres | Pipeline result | all_modules_executed + species_profile |
| bionic_engine_p0 | ai_engine | Historique analyses | Array[analyses] | Minimum 3 sessions |
| strategy_master | predictive_engine | Plan de chasse | Strategy object | Coherence saison + espece |
| ai_engine | strategy_master | Recommandations IA | Predictions[] | Confidence > 60% + source |
| nutrition_intelligence | bionic_engine_p0 | Intelligence nutritionnelle | Nutrition scores | Source scientifique identifiee |
| bionic_knowledge_engine | ai_engine | Donnees scientifiques | Knowledge records | Source + date + validite |
| predictive_engine | strategy_master | Probabilite succes 24h | Number (0-100) | Modele identifie |
| supra_advanced | bionic_engine_p0 | Analyse multi-criteres | Multi-criteria scores | Coherence inter-scores |

## 4.4 Statut implementation P4

| Composant | Statut | Notes |
|-----------|--------|-------|
| Pipeline SUPRA (10 modules) | OPERATIONNEL | SSE→...→TFE sequentiel strict |
| Pipeline V7 | OPERATIONNEL | Feature flag V7 |
| 9 services scoring | OPERATIONNEL | Unified scoring orchestrator |
| Strategy master | OPERATIONNEL | Plans globaux multi-especes |
| IA engine | OPERATIONNEL | Recommandations intelligentes |
| Knowledge base | OPERATIONNEL | 35 endpoints, donnees scientifiques |
| Connexion IA → Strategie | PLANIFIE | Predictions → recommandations jour |
| ML predictif 24h | PLANIFIE | Modele ML a definir |

---

# 5. P5 — MONETISATION x PAIEMENT x UPSELL

## 5.1 Modules concernes

| Module | Prefix API | Endpoints | Statut V2 |
|--------|-----------|-----------|-----------|
| payment_engine | /api/v1/payments | 6 | OPERATIONNEL (Stripe test mode) |
| freemium_engine | /api/v1/freemium | 8 | OPERATIONNEL |
| upsell_engine | /api/v1/upsell | 6 | OPERATIONNEL |
| products_engine | /api/v1/products | 13 | OPERATIONNEL |
| cart_engine | /api/v1/cart | 7 | OPERATIONNEL |
| orders_engine | /api/v1/orders | 9 | OPERATIONNEL |
| ads_engine (FACADE) | — | — | OPERATIONNEL (redirige vers affiliate_ads + ad_spaces) |

## 5.2 Flux de donnees P5

```
[PLANS]                              [PAIEMENTS]                  [UPSELL]
freemium_engine                      payment_engine               upsell_engine
    |                                    |                           |
    +--→ Plans (Free/Premium/Pro)       |                           |
    |    Feature gating                  |                           |
    |    Quota management                |                           |
    |                                    |                           |
    +────────────────────────────────────▼                           |
    |    check-access → denied          Stripe Checkout             |
    |    → trigger upsell ──────────────────────────────────────────▼
    |                                    |                  Campagnes upsell
    |                                    |                  modal/banner/inline
    |                                    |                  A/B testing
    |                                    |                           |
    |                                    +--→ Webhook Stripe        |
    |                                    |    checkout.session.completed
    |                                    |         |                 |
    |    ←───────────────────────────────+─────────+                 |
    |    Upgrade tier (Free → Premium)   |                           |
    |    Reset quotas                    |                           |
    |                                    |                           |
    +--→ roles_engine                   +--→ orders_engine          |
         Mise a jour permissions             Creation commande       |
                                              Historique             |
```

## 5.3 Flux inter-modules P5

| Source | Destination | Donnee | Format | Validation BCE-4X |
|--------|------------|--------|--------|-------------------|
| freemium_engine | payment_engine | Plan selectionne | PackageType enum | Package valide |
| payment_engine | freemium_engine | Confirmation paiement | Webhook event | Signature Stripe verifiee |
| freemium_engine | upsell_engine | Quota atteint | TriggerEvent | Feature + user_id |
| upsell_engine | payment_engine | Conversion upsell | Redirect checkout | Campaign tracking |
| payment_engine | orders_engine | Transaction confirmee | Order creation | Montant + user_id |
| freemium_engine | roles_engine | Tier change | Subscription update | Tier valide (free/premium/pro) |
| ads_engine (FACADE) | affiliate_ads_engine | Requete pub | Redirect transparent | — |
| ads_engine (FACADE) | ad_spaces_engine | Requete espace | Redirect transparent | — |

## 5.4 Statut implementation P5

| Composant | Statut | Notes |
|-----------|--------|-------|
| Stripe Checkout | OPERATIONNEL | Mode test (sk_test_emergent) |
| Plans Free/Premium/Pro | OPERATIONNEL | Quotas et feature flags actifs |
| Upsell triggers | OPERATIONNEL | 4 types de trigger |
| Affiliation | OPERATIONNEL | 3 modules (affiliate_ads, ad_spaces, affiliate_switch) |
| ads_engine (FACADE) | OPERATIONNEL | Consolidation V6 — redirection transparente |
| Webhook Stripe | OPERATIONNEL | checkout.session.completed |
| Passage Stripe production | BLOQUE | Requiert cle Stripe production + validation STEEVE-MAX |

---

# 6. P6 — TERRITOIRE x NAVIGATION x CAMERA

## 6.1 Modules concernes

| Module | Prefix API | Endpoints | Statut V2 |
|--------|-----------|-----------|-----------|
| territory_engine | interne | 6 | OPERATIONNEL |
| waypoint_engine | /api/v1/waypoints | 8 | OPERATIONNEL |
| live_heading_engine | /api/v1/live-heading | 14 | OPERATIONNEL |
| camera_engine | /api/v1/camera | 9 | OPERATIONNEL |
| hunting_trip_logger | /api/v1/trips | 14 | OPERATIONNEL |
| geospatial_engine | /api/v1/geospatial | 33 | OPERATIONNEL (post-consolidation V6) |
| data_layers | /api/v1/data/* | 59 | OPERATIONNEL (5 couches) |

## 6.2 Flux de donnees P6

```
[TERRITOIRE]                         [NAVIGATION]                 [OBSERVATION]
territory_engine                     waypoint_engine               hunting_trip_logger
geospatial_engine                    live_heading_engine            camera_engine
data_layers                               |                           |
    |                                      |                           |
    +--→ Polygone territoire              |                           |
    |    Metadata zone                     |                           |
    |    5 couches donnees                 |                           |
    |                                      |                           |
    +──────────────────────────────────────▼                           |
    |    GPS coordonnees               Waypoints CRUD                 |
    |    Couches SIG                   Cap + direction                |
    |                                  Boussole temps reel            |
    |                                      |                           |
    +──────────────────────────────────────+───────────────────────────▼
         |                              |                    Sorties de chasse
         |                              |                    Photos, resultats
         |                              |                    Conditions meteo
         |                              |                           |
         +--→ geospatial_engine        |                           |
         |    Analyse SIG              +--→ waypoint scoring       |
         |    33 endpoints             |    (waypoint_scoring_eng) |
         |                              |                           |
         +--→ wms_engine               +--→ live_heading_engine    |
              Cartes MRNF                   Navigation boussole    |
              Proxy WMS                     Route replay           |
                                                                    |
                                       +--→ camera_engine ◄────────+
                                            Trail cameras
                                            Detection auto
                                            Analyse photos
```

## 6.3 Flux inter-modules P6

| Source | Destination | Donnee | Format | Validation BCE-4X |
|--------|------------|--------|--------|-------------------|
| territory_engine | geospatial_engine | Polygone territoire | GeoJSON | Geometrie valide (Shapely) |
| territory_engine | data_layers | Zone d'interet | Bounds | Coordonnees valides |
| waypoint_engine | live_heading_engine | Position GPS | lat/lng | GPS valide (-90/90, -180/180) |
| waypoint_engine | hunting_trip_logger | Points visites | Waypoint[] | user_id + timestamp |
| hunting_trip_logger | camera_engine | Observations | Trip record | Species + location valides |
| geospatial_engine | territory_engine | Analyse SIG | GIS results | Source + projection valides |
| data_layers | geospatial_engine | Couches donnees | Layer data | 5 couches completes |

## 6.4 Collections MongoDB P6

| Collection | Module | Documents | Champs cles |
|-----------|--------|-----------|-------------|
| hunting_trips | hunting_trip_logger | 50 | user_id, date, species, location, weather |
| user_waypoints | waypoint_engine | 2 | user_id, name, lat, lng, type |
| territory_waypoints | territory routes | 1 | user_id, latitude, longitude, name |
| territory_cameras | camera_engine | 0 | (schema defini) |
| territory_events | territory routes | 0 | (schema defini) |
| territory_photos | territory routes | 0 | (schema defini) |
| territory_users | territory routes | 0 | (schema defini) |

## 6.5 Statut implementation P6

| Composant | Statut | Notes |
|-----------|--------|-------|
| Territoire CRUD | OPERATIONNEL | Polygones, metadata |
| Waypoints | OPERATIONNEL | 2 waypoints crees, scoring actif |
| Navigation temps reel | OPERATIONNEL | Boussole + cap |
| Trail cameras | OPERATIONNEL | 9 endpoints (pas de donnees) |
| Trip logger | OPERATIONNEL | 50 sorties de chasse enregistrees |
| Geospatial post-consolidation | OPERATIONNEL | geo_engine absorbe → geospatial_engine |
| Route replay | OPERATIONNEL | Replay itineraires |

---

# 7. MATRICE DES FLUX V2

## 7.1 Matrice de dependance inter-phases

```
         P3(MKT)    P4(INTEL)   P5(MONET)   P6(TERR)
P3(MKT)    —         ◄──         ◄──          ◄──
P4(INTEL)  ──►         —          ──►          ◄──
P5(MONET)  ──►        ◄──          —           —
P6(TERR)   ──►        ──►          —            —
```

**Lecture** :
- P6 → P4 : Territoire fournit les donnees terrain pour l'analyse SUPRA
- P6 → P3 : Territoire genere des partages via share_engine (EASYlead)
- P4 → P5 : L'analyse SUPRA declenche les upgrades (quota atteint)
- P4 → P3 : L'analyse genere du contenu partageable (scores, cartes)
- P3 → P5 : Le marketing genere des conversions (leads → clients)
- P5 → P3 : Les paiements generent des evenements marketing (tracking)

## 7.2 Modules transversaux

| Module | Phases impactees | Role |
|--------|-----------------|------|
| admin_engine (210ep) | P3, P4, P5, P6 | Orchestrateur central — configuration globale |
| roles_engine (14ep) | P3, P4, P5, P6 | Permissions — acces conditionne par tier |
| bce/ (17ep) | P3, P4, P5, P6 | Validation — chaque flux inter-module |
| master_switch (19ep) | P3, P5 | Controle ON/OFF — 14 canaux partage, 9 modules sync |
| ultra_max_firewall (5ep) | Tous | Securite — geo-fencing, verrous runtime |

---

# 8. REGLES D'INTERCONNEXION V2

## 8.1 Regles V1 preservees (ZERO LOSS)

| # | Regle | Description |
|---|-------|-------------|
| R1 | Coherence inter-modules | Aucune contradiction permise entre modules |
| R2 | Validation BCE-4X | CHAQUE flux passe par validation (type, plage, coherence, timestamp, source) |
| R3 | Immutabilite logs | Les logs BCE-4X sont IMMUTABLES (lecture seule) |
| R4 | Rollback | Regression detectee → rollback vers derniere version validee |
| R5 | Scoring deterministe | Memes inputs = meme score (source_ids dynamiques) |
| R6 | Sources obligatoires | Toute recommandation cite ses sources |
| R7 | Coherence espece | L'espece doit etre coherente dans tout le pipeline |
| R8 | Admin = Orchestrateur | Aucune donnee Admin Premium n'impacte sans validation BCE-4X |

## 8.2 Regles V2 ajoutees

| # | Regle | Description |
|---|-------|-------------|
| R9 | Facades transparentes | ads_engine et learning_engine redirigent sans modifier les donnees |
| R10 | DEPRECATED exclusion | geo_engine et core/alimentation ne participent plus aux flux actifs |
| R11 | EASYlead tracking | Tout partage genere un share_event + easylead_click trackable |
| R12 | Stripe webhook-first | L'upgrade tier ne s'applique QUE sur confirmation webhook (pas optimiste) |
| R13 | Pipeline order immuable | L'ordre SSE→...→TFE ne peut etre modifie sans validation STEEVE-MAX |

---

# 9. CONSOLIDATION V6 — IMPACTS

## 9.1 Modules impactes dans les interconnexions

| Module ancien | Module nouveau | Type | Impact interconnexions |
|--------------|---------------|------|----------------------|
| geo_engine | geospatial_engine | ABSORPTION | P6 : tous les flux geo passent par geospatial_engine |
| affiliate_ads_engine | ads_engine (FACADE) | FACADE | P5 : transparence totale, endpoints preserves |
| ad_spaces_engine | ads_engine (FACADE) | FACADE | P5 : transparence totale, endpoints preserves |
| tutorial_engine | learning_engine (FACADE) | FACADE | Aucun impact — modules pedagogiques isoles |
| formations_engine | learning_engine (FACADE) | FACADE | Aucun impact — modules pedagogiques isoles |
| core/alimentation | nutrition_engine | DEPRECATION | P4 : nutrition_engine est la source unique |
| utils/ | utility_modules/ | RENOMMAGE | Aucun impact fonctionnel — resolution conflit import |

## 9.2 Flux modifies

| Flux V1 | Flux V2 | Raison |
|---------|---------|--------|
| territory → geo_engine | territory → geospatial_engine | Consolidation V6 |
| core/alimentation → nutrition | nutrition_engine direct | core/alimentation DEPRECATED |

---

# 10. STATUTS ET DEPENDANCES

## 10.1 Statut par phase

| Phase | Statut global | Modules actifs | Modules en attente |
|-------|--------------|----------------|-------------------|
| P3 (Marketing) | PARTIELLEMENT IMPLEMENTE | share_engine, marketing, seo, tracking, analytics, referral, contact | bsaa (GELE) |
| P4 (Intelligence) | ARCHITECTURE DEFINIE | pipeline 10 modules, scoring, strategy, knowledge, nutrition_intel, predictive | Connexion IA→Strategie (PLANIFIE) |
| P5 (Monetisation) | FONCTIONNEL | payment (Stripe test), freemium, upsell, products, cart, orders, affiliation | Stripe production (BLOQUE) |
| P6 (Territoire) | FONCTIONNEL | territory, waypoint, live_heading, camera, trips, geospatial, data_layers | — |

## 10.2 Dependances inter-phases

| Phase | Depend de | Bloque par |
|-------|-----------|-----------|
| P3 | P6 (contenu a partager) | BSAA implementation (GELE) |
| P4 | P6 (donnees terrain) + core/ | ML predictif (modele a definir) |
| P5 | Stripe (INTEGRE en test) | Cle Stripe production + validation STEEVE-MAX |
| P6 | core/geo + core/ndvi + core/ecology | — (aucun bloqueur) |

## 10.3 Prochaines etapes

| Priorite | Action | Phase | Bloqueur |
|----------|--------|-------|----------|
| P1 | Connexion IA → Strategie du Jour | P4 | Modele ML a definir |
| P1 | BSAA implementation | P3 | Validation STEEVE-MAX (GELE) |
| P2 | Stripe production | P5 | Cle production |
| P2 | Soil Engine V2 (donnees reelles) | P4/P6 | Sources pedologiques (IRDA) |
| P3 | ML predictif 24h | P4 | Volume donnees historiques |

---

# 11. RISQUES ET MITIGATIONS V2

## 11.1 Risques V1 preserves

| Risque | Impact | Mitigation |
|--------|--------|-----------|
| Incoherence entre modules | CRITIQUE | Validation BCE-4X systematique |
| Regression de scoring | ELEVE | Rollback automatique + alertes |
| Latence flux temps reel | MODERE | Cache local + refresh asynchrone |
| Surcharge API meteo | MODERE | Rate limiting + cache 30 min |
| Perte donnees historiques | CRITIQUE | Backup MongoDB + logs BCE-4X |

## 11.2 Risques V2 ajoutes

| Risque | Impact | Mitigation | Phase |
|--------|--------|-----------|-------|
| Facades non transparentes | MODERE | Tests integration ads_engine/learning_engine | P5 |
| geo_engine appele au lieu de geospatial | MODERE | DEPRECATED warning + redirect interne | P6 |
| EASYlead tracking incomplet | FAIBLE | Verification share_events + easylead_clicks | P3 |
| Webhook Stripe manque | ELEVE | Retry automatique + alerte > 5 min | P5 |
| Pipeline V7 regression vs Legacy | CRITIQUE | Double-run + diff BCE-4X | P4 |

---

**Protocole** : BCE-4X GOLDEN V6+
**Autorite** : STEEVE-MAX
**Version** : INTERCONNEXIONS_P3_P6_V2 2.0.0
**Base** : INTERCONNEXIONS_P3_P6 V1 (209L) + ARCHITECTURE_INTERCONNEXION V1 (208L)
**Reference** : AUBO_V2.md Section 12
**Phases documentees** : P3 (Marketing), P4 (Intelligence), P5 (Monetisation), P6 (Territoire)
**Regles d'interconnexion** : 13 (8 V1 + 5 V2)
**Merge main** : STRICTEMENT INTERDIT
