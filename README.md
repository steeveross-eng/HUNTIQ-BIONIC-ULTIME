# HUNTIQ-BIONIC-ULTIME

**Version canonique V10** — Architecture modulaire + Corridors Omega + Écoforesterie + BIONIC Core

---

## Qu'est-ce que BIONIC?

HUNTIQ-BIONIC-ULTIME est une plateforme de chasse intelligente pour le Québec et le Canada.
Elle utilise des données scientifiques publiques (écoforesterie, géospatial, météo, spectral)
pour analyser les territoires, identifier les corridors fauniques et optimiser les stratégies de chasse.

**Science validates what the field confirms.™**

---

## Fonctionnalités principales

- 🎯 **Analyse territoriale** — Grilles hexagonales H3, scoring multi-facteurs, corridors Omega
- 🌲 **Écoforesterie** — Peuplements forestiers, coupes récentes, habitats par espèce (MERN/MFFP)
- 🗺️ **Cartographie WMS** — Proxy sécurisé vers les services gouvernementaux du Québec/Canada
- 🦌 **Comportement faunique** — Modèles prédictifs par espèce, saison et conditions météo
- 📊 **Scoring scientifique** — 13 critères IA pondérés (V7 bio-scoring)
- 🛒 **Marketplace** — Produits BIONIC Saline, comparaison, commandes
- 📷 **Caméras de chasse** — Gestion, upload photos, événements
- 🔔 **Notifications** — Alertes territoire, météo, activité faunique
- 👥 **Social** — Networking chasseurs, groupes, referral

---

## Stack technique

| Composant | Technologie |
|---|---|
| Frontend | React (TypeScript) |
| Backend | FastAPI (Python) |
| Base de données | MongoDB |
| Stockage | Cloudflare R2 |
| CI/CD | GitHub Actions |
| Données géospatiales | MERN, MFFP, NRCan, ESA Sentinel, NASA HLS |

---

## Architecture

Le projet est organisé en deux couches backend :

- **`backend/engines/`** — 25 moteurs scientifiques Omega V10 (scoring, corridors, écoforesterie, spectral, terrain, météo, prédictif)
- **`backend/modules/`** — ~90 modules applicatifs (auth, commerce, territoire, social, notifications)

Voir [ARCHITECTURE.md](ARCHITECTURE.md) pour la documentation complète.

---

## API

| Préfixe | Description |
|---|---|
| `/api/v1/*` | API legacy (frontend actuel) |
| `/api/v20/*` | API V10 institutionnelle (moteurs Omega) |
| `/api/v30/*` | Admin premium GIS |
| `/api/v51/*` | Moteurs temporels/solunaires |

---

## Sécurité

- Repo privé
- WMS Proxy avec whitelist stricte (SSRF patché)
- Secrets via GitHub Secrets (JWT, MongoDB, SSH)
- Aucune clé ou secret dans le code versionné

---

## Versions

| Version | Date | Notes |
|---|---|---|
| V5-ULTIME-FUSION | Mars 2026 | Fusion V2+V3+V4+BASE |
| V7 | Juin 2026 | Patch R4 Sentinel |
| **V10** | **Août 2026** | **Refactoring complet, 25 moteurs Omega** |

---

## Auteur

**BIONIC™ Team** — Steeve Ross

---

*Ce projet est privé et confidentiel. Aucune reproduction sans autorisation.*
