# RAPPORT β2-ΣΤ · SNAPSHOT 2026-05-20T14:02:23Z

**Doctrine** : `P22ΩΩ_ACTIVATION_BETA2_ST_Ω`
**Commandant** : STEEVE-MAX · BCE-4X ULTIME ABSOLU
**Auto-généré** : `zerocost_seed_r5_snapshot_report.sh`
**Temps écoulé depuis activation watchdog** : 1h 17min

---

## 1. ÉTAT DAEMON β2-ΣΤ

    ═══ STATUS DAEMON β2-ΣΤ (T+4368s = 72min) ═══
      Workers vivants : 6 / 6
      SEED total OK   : 0
      FAN-OUT total OK: 0
      Débit fan-out   : 0.00 R6/s

**Watchdog supervisor** :
    zerocost-seed-r5-watchdog        RUNNING   pid 2884, uptime 1:12:54

---

## 2. PROGRESSION R2 (CIBLE 3 RF)

| Métrique | Valeur |
|---|---|
| Objets R2 totaux | 5,488 (96.0 MB) |
| Cellules R6 dans 3 RF | **107 / 1 775 (6.0%)** |
| R5 parents couverts | 32 / 284 (11.3%) |

**Cadence par fenêtre temporelle :**

| Fenêtre | Uploads | Tuiles/min |
|---|---|---|
| last_5min | 210 | 42.0 |
| last_30min | 1724 | 57.5 |
| last_1h | 3297 | 55.0 |
| last_6h | 4158 | 11.6 |

**Couverture par Réserve faunique :**

| RF | Cellules R6 | % du total RF |
|---|---|---|
| MAURICIE_RF_MASTIGOUCHE_ST_MAURICE | 53 / 412 | 12.9% |
| OUTAOUAIS_RF_PAPINEAU_VERENDRYE_SUD | 43 / 129 | 33.3% |
| LAURENTIDES_RF_LAURENTIDES_ROUGE_MATAWIN | 11 / 1234 | 0.9% |

**ETA reste 3 RF complet** (cadence 30min = 57.5 t/min) : **34.8 heures (1.5 jours)**

---

## 3. BACKEND HEALTH

    Attempt 1 : HTTP 200 · 0.315021s
    Attempt 2 : HTTP 200 · 1.925255s
    Attempt 3 : HTTP 200 · 1.946897s

**Load average** :  2.59, 3.29, 3.56
**Memory** : 22Gi/31Gi

---

## 4. GARDE-FOUS

| Mécanisme | État |
|---|---|
| Watchdog supervisor | $(sudo supervisorctl status zerocost-seed-r5-watchdog 2>&1 | awk '{print $2,$3}') |
| Workers β2-ΣΤ actifs | $(ps -ef | grep zerocost_worker_seed_r5 | grep -v grep | wc -l) / 6 |
| Anti-502 middleware | $(curl -s --max-time 3 -o /dev/null -w "HTTP %{http_code}" http://localhost:8001/api/v20/territoire/anti502/metrics) |
| Verrou Phase III | 🔒 MAINTENU |
| QUOTA600 | 🟡 APPROUVÉ_NON_ACTIVÉ |

---

## 5. CDN MANIFEST CHECK

curl: unknown --write-out variable: 'code'
    HTTP  · 0.294076s · taille 630B
    n_tiles indexées : 1260
    cells_unique : 84
    generated_at : 2026-05-19T23:55:26.104538+00:00

---

**Fin snapshot · directives pour suite** :
- `bash /app/backend/tools/zerocost_seed_r5_daemon.sh status` (status léger)
- `bash /app/backend/tools/zerocost_seed_r5_snapshot_report.sh > /app/memory/RAPPORT_BETA2_ST_T+XX_Ω.md` (nouveau snapshot)
- `tail -f /var/log/supervisor/zerocost-seed-r5-watchdog.out.log` (watchdog log)

