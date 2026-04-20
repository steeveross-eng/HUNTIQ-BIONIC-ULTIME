# EXPORT_INSTITUTIONNEL_V20_SPEC — Phase X-D

> **Module :** `/app/backend/engines/v8_institutional/export_institutionnel_v20_omega.py`
> **Endpoint :** `GET /api/v20/territoire/export/institutionnel/v20`
> **Date :** 2026-04-19

## 1. Rôle

Produit un PDF institutionnel **signé HMAC-SHA256** agrégeant les 3 rapports
de phase + hashes officiels (Document Maître, Registry Lock).

## 2. Contenu du PDF

- **Page de couverture** — Titre + horodatage UTC + protocole + commandant
- **Tableau des hashes** — Document Maître, Registry Lock, version, engines scellés
- **PHASE X-B REPORT** — rapport `PHASE_X_B_VALIDATION_REPORT.md`
- **PHASE XI REPORT** — rapport `PHASE_XI_VALIDATION_REPORT.md`
- **PHASE X-C REPORT** — rapport `PHASE_X_C_VALIDATION_REPORT.md`
- **Page de signature** — HMAC-SHA256 horodaté + payload signé + autorité

## 3. Signature numérique

| Champ | Valeur |
|-------|--------|
| Algorithme | `HMAC-SHA256` |
| Clé interne | `BCE-4X-ULTIME-ABSOLU-STEEVE-MAX-V20` (MVP ; rotation via env en prod) |
| Payload | `{now_utc}|DOCMAITRE={sha256}|REGISTRY={sha256}|ENGINES={count}` |
| Longueur signature | 64 hex (256 bits) |

## 4. Paramètres

```bash
GET /api/v20/territoire/export/institutionnel/v20
  → application/pdf (download)

GET /api/v20/territoire/export/institutionnel/v20?metadata_only=true
  → JSON { generated_at, size_bytes, signature_hmac_sha256,
           payload_signed, reports_included,
           registry_sha256, document_maitre_sha256, algorithm }
```

## 5. Headers HTTP signés

- `X-Signature-HMAC-SHA256`
- `X-Registry-SHA256`
- `X-Generated-At`
- `Content-Disposition: attachment; filename="BIONIC_OS_V20_EXPORT.pdf"`

## 6. Validation

`test_export_institutionnel.py` vérifie :

- Header `%PDF` valide
- Taille > 2 KB (confirmé ~18.5 KB)
- Champs metadata complets
- Signature 64 hex déterministe reproductible
- ≥ 3 rapports inclus

```
OK: export PDF institutionnel (18572 bytes, sig=941a405eb44c9640…, 3 rapports)
```

## 7. Vérification externe

Pour valider une signature tierce :

```python
import hmac, hashlib
key = b"BCE-4X-ULTIME-ABSOLU-STEEVE-MAX-V20"
payload = b"{generated_at}|DOCMAITRE={sha}|REGISTRY={sha}|ENGINES={n}"
assert hmac.new(key, payload, hashlib.sha256).hexdigest() == signature
```

## 8. Sealed
```
SEALED  — Phase X-D — 2026-04-19 — BCE-4X ULTIME ABSOLU
```
