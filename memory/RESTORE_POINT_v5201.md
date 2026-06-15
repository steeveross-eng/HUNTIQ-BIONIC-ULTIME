# POINT DE RESTAURATION SCELLE — BIONIC_OS_v5201
## Directive x5300-STEEVE_MAX — SECTION C
### Protocole BCE-4X GOLDEN V6+ | Autorite : STEEVE-MAX
### Date de creation : 2026-03-31 | IMMUTABLE

---

## IDENTIFIANT DU POINT DE RESTAURATION

| Champ | Valeur |
|-------|--------|
| **Version** | BIONIC_OS_v5201 |
| **Date** | 2026-03-31 |
| **Directive** | x5300-STEEVE_MAX |
| **Protocole** | BCE-4X GOLDEN V6+ |
| **Autorite** | STEEVE-MAX |
| **Statut** | SCELLE — IMMUTABLE |

---

## CONTENU DU POINT DE RESTAURATION

### ZIP #1 — Backup complet (128 MB)
- **Fichier** : `BIONIC_OS_BACKUP_COMPLET_v5201.zip`
- **Contenu** : backend (modules, engines, core, routes, bce), frontend (src, public), configs, memory
- **HTTPS** : `https://bionic-ultime-1.preview.emergentagent.com/BIONIC_OS_BACKUP_COMPLET_v5201.zip`

### ZIP #2 — 7 blocs critiques (128 MB)
- **Fichier** : `BIONIC_OS_7BLOCS_v5201.zip`
- **Contenu** :
  - BLOC 1 : Frontend complet (583 fichiers)
  - BLOC 2 : Backend complet (1470 fichiers)
  - BLOC 3 : MongoDB dump (35 fichiers, 34 collections, 703 documents)
  - BLOC 4 : Variables d'environnement (backend.env, frontend.env)
  - BLOC 5 : Assets statiques (27 fichiers)
  - BLOC 6 : Build et deploiement (4 fichiers)
  - BLOC 7 : Configuration systeme (2 fichiers)
- **HTTPS** : `https://bionic-ultime-1.preview.emergentagent.com/BIONIC_OS_7BLOCS_v5201.zip`

### MongoDB Dump (254 KB)
- **Fichier** : `BIONIC_OS_MONGODB_DUMP_v5201.zip`
- **Collections** : 34
- **Documents** : 703
- **HTTPS** : `https://bionic-ultime-1.preview.emergentagent.com/BIONIC_OS_MONGODB_DUMP_v5201.zip`

### Snapshot systeme (4 KB)
- **Fichier** : `BIONIC_OS_SNAPSHOT_v5201.json`
- **Contenu** : versions Python/Node/Yarn, inventaire backend/frontend, structure DB, gouvernance
- **HTTPS** : `https://bionic-ultime-1.preview.emergentagent.com/BIONIC_OS_SNAPSHOT_v5201.json`

---

## PROCEDURE DE RESTAURATION

### Etape 1 — Telecharger les fichiers
```bash
wget https://bionic-ultime-1.preview.emergentagent.com/BIONIC_OS_BACKUP_COMPLET_v5201.zip
wget https://bionic-ultime-1.preview.emergentagent.com/BIONIC_OS_MONGODB_DUMP_v5201.zip
wget https://bionic-ultime-1.preview.emergentagent.com/BIONIC_OS_SNAPSHOT_v5201.json
```

### Etape 2 — Extraire le code
```bash
unzip BIONIC_OS_BACKUP_COMPLET_v5201.zip -d /app/
```

### Etape 3 — Installer les dependances
```bash
cd /app/backend && pip install -r requirements.txt
cd /app/frontend && yarn install
```

### Etape 4 — Restaurer MongoDB
```bash
# Les fichiers JSON sont dans BIONIC_OS_MONGODB_DUMP_v5201.zip
unzip BIONIC_OS_MONGODB_DUMP_v5201.zip -d /tmp/restore/
# Importer chaque collection
for f in /tmp/restore/mongodb_dump/*.json; do
    col=$(basename "$f" .json)
    mongoimport --db huntiq_v6 --collection "$col" --file "$f" --jsonArray --drop
done
```

### Etape 5 — Configurer les variables d'environnement
```bash
# Verifier .env backend et frontend
# Les fichiers sont inclus dans le ZIP mais les cles sensibles
# (Stripe, JWT) doivent etre re-configurees manuellement
```

### Etape 6 — Demarrer les services
```bash
sudo supervisorctl restart backend frontend
```

### Etape 7 — Verification
```bash
curl https://[DOMAIN]/api/share/status
# Doit retourner: {"module": "share_engine", "version": "4.0.0", ...}
```

---

## SCELLEMENT

Ce point de restauration est **IMMUTABLE** et **VERSIONNE**.
- Aucune modification sans directive explicite de STEEVE-MAX
- Protocole ZERO-REGRESSION actif
- Certification BCE-4X MAX 4.1 applicable

**Protocole** : BCE-4X GOLDEN V6+
**Autorite** : STEEVE-MAX
**Merge main** : STRICTEMENT INTERDIT
