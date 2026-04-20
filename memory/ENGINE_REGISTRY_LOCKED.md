# ENGINE_REGISTRY_LOCKED — Phase XI-SUPRA-M

> **STATUT : SCELLÉ — SEALED — VERROUILLÉ**
> **Version registre :** V25-SUPRA-LOCKED-PHASE-XI-SUPRA-M-2026-04
> **Date de scellement :** 2026-04-20T22:00:00Z
> **Commandant :** STEEVE-MAX

---

## Hash SHA-256 officiel

```
e8c6ee62a3f0c1894313dee30355b711230ede629e208df4622de99cee2ba2b8
```

Toute altération de la liste des engines (`ENGINES_LOCKED` dans
`/app/backend/engines/v8_institutional/registry_lock_omega.py`)
invalide ce hash et fait échouer `test_engine_registry_locked`.

> **Évolution Phase XI-SUPRA-C :** registre étendu à 33 engines avec l'ajout de
> `VISUAL-PROOF-LIVE-Ω` (capture DOM Playwright Leaflet réelle sous auth).
>
> **Évolution Phase XI-SUPRA-D :** registre étendu à 36 engines avec
> `LEP-INGESTION-Ω` + alignement live.
>
> **Évolution Phase XI-SUPRA-E :** registre ramené à **35 engines** par
> directive officielle STEEVE-MAX 2026-04-20 — `EXCLUDE_LAYER
> LEP_CRITICAL_HABITAT_NATIONAL`. `LEP-INGESTION-Ω` retiré du lock.
>
> **Évolution Phase XI-SUPRA-G :** registre étendu à **36 engines** par ajout de
> `ENGINE-TERRITOIRE-ANTI-REGRESSION-Ω` (protection baseline).
>
> **Évolution Phase XI-SUPRA-H :** registre étendu à **37 engines** par ajout de
> `ENGINE-IA-CORRIDORS-Ω` (corridors biomimétiques).
>
> **Évolution Phase XI-SUPRA-K :** registre étendu à **40 engines** par ajout de
> `ENGINE-RENDU-Ω`, `ENGINE-SPECIES-PROFILES-Ω`, `ENGINE-IA-VISION-REGISTRY-Ω`.
> Rendu institutionnel des corridors verrouillé.
>
> **Évolution Phase XI-SUPRA-L :** application côté frontend
> des règles RENDU-Ω sur la couche Leaflet `CORRIDORS_OMEGA` (couleur unique
> `#FF8F00`, épaisseurs 1.2/2.0/3.0 px, opacité ≥ 0.75, minZoom=13, Z-order
> strict, PREVIEW==FINAL). Ajout endpoint visuel self-test
> `/api/v20/territoire/corridors-omega/visual-self-test` (6/6 checks OK).
> Aucun nouvel engine ajouté — renforcement frontend uniquement.
>
> **Évolution Phase XI-SUPRA-M (présente directive) :** registre étendu à
> **41 engines** par ajout de `ENGINE-IA-CORRIDORS-ORGANIC-Ω`. Legacy
> `engine_corridors.py` archivé en `_ARCHIVE_NON_ACTIVE/`. Nouvelles
> capacités : IA multi-échelles (macro vallées / micro coulées / drainage /
> slope breaks / shadow relief), géométrie organique 60–120 points,
> micro-oscillations biomimétiques, smart deviation, auto-interconnexion
> (seuil 50 m), variable thickness le long du path, hiérarchie réseau
> (veine_principale / veine_secondaire / capillaire), attraction/répulsion
> dynamique, 3 modes rendu (density / heat / veine_animale). Baseline
> `TERRITOIRE_OMEGA_STABLE` scellable via endpoint dédié.

---

## Phase XI-SUPRA-K — Nouveaux engines scellés (3)

| # | Engine | Pilier | Phase |
|---|--------|--------|-------|
| 38 | `ENGINE-RENDU-Ω` | GOUVERNANCE | XI-SUPRA-K |
| 39 | `ENGINE-SPECIES-PROFILES-Ω` | BIO-SYSTEME | XI-SUPRA-K |
| 40 | `ENGINE-IA-VISION-REGISTRY-Ω` | BIO-SYSTEME | XI-SUPRA-K |

## Documents officiels (source de vérité)

- `/app/memory/ENGINE_CORRIDORS_OMEGA_OFFICIAL_FINAL.md` — VERSION Ω canonique
- `/app/memory/RENDUS/RENDUS_CORRIDORS_OMEGA.md` — RENDU Ω canonique
- `/app/registry/species_profiles_v1.json` — registre dynamique 5 espèces
- `/app/registry/ia_vision/ia_vision_registry_v1.json` — registre IA Vision

## Endpoints Phase XI-SUPRA-K

```bash
# Rendu-Ω
curl -s .../api/v20/territoire/rendu-omega/status
curl -s .../api/v20/territoire/rendu-omega/rules
curl -X POST .../api/v20/territoire/rendu-omega/validate -d '{"corridors":[...]}'

# Species Profiles
curl -s .../api/v20/territoire/species-profiles/status
curl -s .../api/v20/territoire/species-profiles/validate
curl -s .../api/v20/territoire/species-profiles/{species_key}

# IA Vision
curl -s .../api/v20/territoire/ia-vision/status
curl -s .../api/v20/territoire/ia-vision/validate

# IA Corridors — Explain
curl -s '.../api/v20/territoire/ia-corridors/explain/{corridor_id}?lat=&lon=&species='
curl -X POST .../api/v20/territoire/ia-corridors/explain -d '{"corridor":{},"waypoint":{}}'
```

## Règles de modification

Toute modification de ce registre exige :

1. Directive Commandant STEEVE-MAX
2. Validation ENGINE-GOUVERNANCE-Ω
3. Re-calcul du hash SHA-256
4. Mise à jour `ENGINES_LOCKED` dans `registry_lock_omega.py`
5. Passage SELF-AUDIT-Ω (58/58)
6. Consignation dans `SELF_AUDIT_OMEGA_LOGS.md`

## Signature

```
SEALED  — Phase XI / X-B / X-C / X-D / XI-SUPRA / XI-SUPRA-B / XI-SUPRA-C /
         XI-SUPRA-G / XI-SUPRA-H / XI-SUPRA-K / XI-SUPRA-L / XI-SUPRA-M — 2026-04-20
SHA-256 — e8c6ee62a3f0c1894313dee30355b711230ede629e208df4622de99cee2ba2b8
TOTAL   — 41 engines scellés
STATUS  — VERROUILLÉ IRRÉVOCABLEMENT
```
