# ARCHIVE BIONIC V20-SUPRA — STRUCTURE (Phase XI-SUPRA-E / §V)

> **COMMANDANT :** STEEVE-MAX  
> **DATE :** 2026-04-20  
> **FORMAT :** tar.gz  
> **CHEMIN :** `/app/memory/ARCHIVE_BIONIC_V20_SUPRA.tar.gz`  
> **TAILLE :** 34599371 octets (~32 MB)  
> **SHA-256 :** `3fe9b6e321b13682eafb3477952a022901e3925497636c5d296c60a57782f7fd`

## Contenu de l'archive

```
BIONIC_V20_SUPRA/
├── backend/
│   ├── engines/v8_institutional/     # 36 engines SUPRA-Ω (source de vérité institutionnelle)
│   │   ├── registry_lock_omega.py
│   │   ├── self_audit_omega.py
│   │   ├── lep_ingestion_omega.py    # Phase XI-SUPRA-D
│   │   ├── visual_proof_live_playwright.py  # Phase XI-SUPRA-D
│   │   └── … (33 autres)
│   ├── modules/                       # 78 modules V5-ULTIME-FUSION
│   ├── routes/                        # Routes FastAPI
│   ├── tests/                         # 57 suites SELF-AUDIT-Ω
│   ├── server.py
│   ├── requirements.txt              # geopandas, pyogrio, playwright, fastapi…
│   └── .env                          # PLACEHOLDERS (secrets scrubés)
├── frontend/
│   ├── src/
│   │   ├── App.js                    # Routes + CaptureModeAwareChrome
│   │   ├── index.js                  # StrictMode bypass pour capture-mode
│   │   ├── pages/
│   │   │   ├── TerritoireCaptureModePage.jsx  # Phase XI-SUPRA-D
│   │   │   └── MonTerritoireBionicPage.jsx
│   │   └── components/
│   │       ├── territoire/BionicLayersV8.jsx            # 14 couches institutionnelles
│   │       ├── territoire/InstitutionalHealthPanel.jsx  # Phase XI-SUPRA-D (SLA+WS+LEP)
│   │       └── CookieConsent.jsx                        # isCaptureMode bypass
│   ├── package.json
│   ├── yarn.lock
│   ├── craco.config.js
│   └── .env                          # PLACEHOLDERS
├── memory/                            # Rapports + preuves institutionnelles
│   ├── ENGINE_REGISTRY_LOCKED.md     # Hash SHA-256 officiel
│   ├── PHASE_XI_SUPRA_D_TERRITOIRE_CAPTURE_STABLE_REPORT.md
│   ├── HEALTH_PANEL_SLA30J_INTEGRATION.md
│   ├── HEALTH_PANEL_WS_ALERTS_INTEGRATION.md
│   ├── LEP_ECCC_INTEGRATION_REPORT.md
│   ├── ENGINES_OMEGA_AUDIT_R1.md
│   ├── SECURITY_RELOCK_V20_SUPRA_REPORT.md
│   ├── ZERO_REGRESSION_SELF_AUDIT_REPORT.md
│   ├── TERRITOIRE_VISUAL_PROOF_LIVE/        # 3 captures Playwright ≥ 30 KB
│   ├── TERRITOIRE_VISUAL_PROOF/              # Captures phase XI-SUPRA-B (PIL)
│   └── PRD.md / CHANGELOG.md / ROADMAP.md
└── data/                              # Stockage persistent institutionnel
    └── territoire_omega/
        ├── data_primary_fgdb_lep/     # FGDB LEP ECCC (vide, attente upload)
        └── data_secondary_geojson_lep/ # GeoJSON (vide, attente upload)
```

## Reconstruction sur infrastructure cible

```bash
# 1. Extraire
tar -xzf ARCHIVE_BIONIC_V20_SUPRA.tar.gz
cd BIONIC_V20_SUPRA

# 2. Backend
cd backend
pip install -r requirements.txt
cp .env .env.local && vi .env.local   # Remplacer PLACEHOLDERS par vraies valeurs
# MongoDB doit être accessible via MONGO_URL

# 3. Frontend
cd ../frontend
yarn install
cp .env .env.local && vi .env.local   # REACT_APP_BACKEND_URL

# 4. Playwright (optionnel pour captures)
playwright install chromium

# 5. Supervisor (si prod)
# Restaurer les fichiers supervisor.conf à partir de /etc/supervisor/conf.d/
# Services : backend (:8001), frontend (:3000)

# 6. Ingestion LEP (après restauration réseau ECCC ou upload manuel)
curl -X POST $API/api/v20/territoire/lep/ingest -F "file=@CriticalHabitat.zip"

# 7. Validation
curl $API/api/v20/territoire/self-audit | jq '.conforme, (.suites | length)'
# Attendu : true, 57
```

## Intégrité

Fichier hash : `/app/memory/ARCHIVE_BIONIC_V20_SUPRA.sha256`

```
3fe9b6e321b13682eafb3477952a022901e3925497636c5d296c60a57782f7fd  ARCHIVE_BIONIC_V20_SUPRA.tar.gz
```

## Exclusions (taille optimisée)

- `node_modules/` (régénérable via `yarn install`)
- `__pycache__/`, `*.pyc`
- `build/`, `dist/`, `coverage/`, `.pytest_cache/`
- Anciens backups ZIP v5201 (redondants avec cette archive)
- Secrets `.env` → PLACEHOLDERS documentés
