#!/usr/bin/env python3
"""
phase_xvi_protocoles_omega.py — PHASE XVI · 3 PROTOCOLES SCIENTIFIQUES_Ω
═════════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ORDRE N°36

Documents institutionnels strictement déclaratifs identifiant TOUT ce qui
manque (science, données, paramètres, coefficients) pour porter à >90 :
  • NUTRITION_MASTER (actuellement 0)
  • CORRIDORS_MASTER (actuellement 40)
  • SENSORIEL_MASTER (actuellement 33.08)

Aucune modification du V30 ni du FREEZE_MASTER. Aucune logique générique.
Sortie : /app/frontend/public/reports/purge_master_omega/

8 livrables HTTPS attendus :
  PROTOCOLE_BIO_PROFILE_NUTRITION_Ω.{json,html}
  PROGRESSION_CORRIDORS_Ω.{json,html}
  PROGRESSION_SENSORIEL_Ω.{json,html}
  VALIDATION_PROTOCOLES_Ω.{json,html}
═════════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
import hashlib
import html as html_lib
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

OUT_DIR = Path("/app/frontend/public/reports/purge_master_omega")
INGRESS = "https://huntiq-restore.preview.emergentagent.com"
UTC_NOW = datetime.now(timezone.utc).isoformat(timespec="seconds")
HTTP_UA = "Mozilla/5.0 BCE-4X-OMEGA-PROTOCOLES"
ESPECES = ["CHEVREUIL", "ORIGNAL", "OURS_NOIR", "WAPITI", "DINDON_SAUVAGE"]


def sha(p):
    p = Path(p)
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def url_for(filename):
    return f"{INGRESS}/reports/purge_master_omega/" + urllib.parse.quote(filename, safe="._-")


def write_json(path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return sha(path)


def http_get_code(url):
    res = subprocess.run(
        ["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code}",
         "-A", HTTP_UA, url],
        capture_output=True, text=True, timeout=30,
    )
    return int(res.stdout.strip()) if res.stdout.strip().isdigit() else None


# ═════════════════════════════════════════════════════════════════════════
# CSS institutionnel commun
# ═════════════════════════════════════════════════════════════════════════
CSS = """<style>
:root{--bg:#0a1018;--panel:#111c2e;--panel2:#162032;--txt:#e2e8f0;--mute:#94a3b8;--accent:#06b6d4;--accent2:#22d3ee;--ok:#16a34a;--gold:#f59e0b;--dang:#dc2626;--bord:#1e293b;}
*{box-sizing:border-box;}
body{font-family:'Inter','Segoe UI',sans-serif;background:linear-gradient(180deg,#0a1018 0%,#0b1320 100%);color:var(--txt);margin:0;padding:32px 20px;}
.wrap{max-width:1320px;margin:0 auto;}
header.title{border-left:5px solid var(--gold);padding:6px 0 6px 18px;margin-bottom:22px;}
header.title h1{margin:0;font-size:24px;color:#fef3c7;letter-spacing:0.6px;}
header.title .sub{color:var(--mute);font-size:13px;margin-top:6px;}
.b-ok{background:linear-gradient(135deg,#14532d 0%,#15803d 100%);border:1px solid var(--ok);color:#dcfce7;padding:12px 22px;border-radius:8px;font-weight:700;text-align:center;margin-bottom:18px;}
.b-ko{background:linear-gradient(135deg,#7f1d1d 0%,#991b1b 100%);border:1px solid var(--dang);color:#fee2e2;padding:12px 22px;border-radius:8px;font-weight:700;text-align:center;margin-bottom:18px;}
.b-gold{background:linear-gradient(135deg,#78350f 0%,#92400e 100%);border:1px solid var(--gold);color:#fef3c7;padding:12px 22px;border-radius:8px;font-weight:700;text-align:center;margin-bottom:18px;}
h2{color:var(--gold);font-size:18px;margin:32px 0 12px;border-left:4px solid var(--gold);padding-left:12px;}
h3{color:var(--accent2);font-size:15px;margin:22px 0 10px;}
.card{background:var(--panel);border:1px solid var(--bord);border-radius:10px;padding:18px 22px;margin-bottom:18px;}
.kpi-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin-bottom:18px;}
.kpi{padding:14px 18px;background:var(--panel2);border:1px solid var(--bord);border-radius:8px;}
.kpi .num{color:var(--accent2);font-weight:700;font-size:22px;}
.kpi .lbl{color:var(--mute);font-size:10px;text-transform:uppercase;letter-spacing:0.5px;}
table{width:100%;border-collapse:collapse;font-size:11.5px;}
th,td{padding:8px 10px;border-bottom:1px solid var(--bord);text-align:left;vertical-align:top;}
th{background:var(--panel2);color:#fff;text-transform:uppercase;font-size:10.5px;letter-spacing:0.5px;}
.scroll{max-height:520px;overflow-y:auto;border:1px solid var(--bord);border-radius:6px;}
.dl{color:var(--accent2);text-decoration:none;font-weight:600;display:inline-flex;align-items:center;gap:5px;padding:6px 12px;border:1px solid rgba(6,182,212,0.35);border-radius:5px;}
.mono{font-family:'JetBrains Mono','Courier New',monospace;font-size:10px;color:var(--mute);word-break:break-all;}
.foot{margin-top:30px;padding:18px 22px;background:var(--panel);border:1px solid var(--bord);border-radius:10px;font-size:12px;color:var(--mute);}
.lbl-foot{color:var(--accent2);font-weight:600;text-transform:uppercase;font-size:10px;letter-spacing:0.5px;}
.v30-lock{margin-top:14px;padding:10px 14px;background:rgba(22,163,74,0.10);border:1px solid rgba(22,163,74,0.45);border-radius:6px;color:#4ade80;font-weight:700;text-align:center;letter-spacing:0.6px;}
.b-acc{display:inline-block;padding:2px 8px;border-radius:4px;background:rgba(6,182,212,0.18);color:var(--accent2);border:1px solid rgba(6,182,212,0.45);font-weight:700;font-size:10px;}
.b-warn{display:inline-block;padding:2px 8px;border-radius:4px;background:rgba(245,158,11,0.18);color:var(--gold);border:1px solid rgba(245,158,11,0.45);font-weight:700;font-size:10px;}
.b-dang{display:inline-block;padding:2px 8px;border-radius:4px;background:rgba(220,38,38,0.18);color:#fca5a5;border:1px solid rgba(220,38,38,0.45);font-weight:700;font-size:10px;}
.b-low{display:inline-block;padding:2px 8px;border-radius:4px;background:rgba(34,197,94,0.18);color:#86efac;border:1px solid rgba(34,197,94,0.45);font-weight:700;font-size:10px;}
.b-p0{background:#fb7185;color:#1f2937;font-weight:700;padding:2px 6px;border-radius:4px;font-size:10px;}
.b-p1{background:#fbbf24;color:#1f2937;font-weight:700;padding:2px 6px;border-radius:4px;font-size:10px;}
.b-p2{background:#22d3ee;color:#1f2937;font-weight:700;padding:2px 6px;border-radius:4px;font-size:10px;}
.cite{color:#60a5fa;font-style:italic;font-size:11px;}
</style>"""


def signature_template(typ, unit, source, range_str, semantics):
    """Helper standard pour le format institutionnel {value, signature}."""
    return {
        "type": typ, "unit": unit, "source": source,
        "range": range_str, "semantics": semantics,
    }


# ═════════════════════════════════════════════════════════════════════════
# DATA — PARAMÈTRES NUTRITION_Ω (9 paramètres × 5 espèces)
# Sources : Hewitt DG (2011) ; Lyon & Burcham (1998) ; Pelton MR (2003) ;
#           Eaton & Healy (1991) ; MFFP Québec - Plans de gestion 2020-2027 ;
#           Renecker & Hudson (1990) ; Crête (1989) hyperphagie cervidés.
# ═════════════════════════════════════════════════════════════════════════

NUTRITION_REFS = [
    {"id": "HEWITT_2011",
     "citation": "Hewitt DG (2011). Biology and Management of White-tailed Deer. CRC Press.",
     "domaine": "Cervidés — bilan énergétique, protéines, minéraux."},
    {"id": "RENECKER_HUDSON_1990",
     "citation": "Renecker LA & Hudson RJ (1990). Behavioral and thermoregulatory responses of moose to high temperatures. Can J Zool 68:122–133.",
     "domaine": "Orignal — thermorégulation et besoins énergétiques."},
    {"id": "MFFP_PG_2020_2027",
     "citation": "MFFP Québec (2020). Plans de gestion 2020-2027 (chevreuil, orignal, ours noir, wapiti, dindon sauvage).",
     "domaine": "Données saisonnières institutionnelles 5 espèces."},
    {"id": "PELTON_2003",
     "citation": "Pelton MR (2003). Black bear ecology and management. In: Wild Mammals of NA, 2nd ed.",
     "domaine": "Ours noir — hyperphagie automnale, glands, fruits."},
    {"id": "EATON_HEALY_1991",
     "citation": "Eaton SW & Healy WM (1991). Wild Turkey ecology. Stackpole Books.",
     "domaine": "Dindon sauvage — régimes saisonniers, glands, insectes."},
    {"id": "LYON_BURCHAM_1998",
     "citation": "Lyon LJ & Burcham MG (1998). Wapiti security cover and seasonal forage. USFS GTR.",
     "domaine": "Wapiti — phénologie protéines printanières, herbacées."},
    {"id": "CRETE_1989",
     "citation": "Crête M (1989). Approximation of K carrying capacity for moose in eastern Quebec. Can J Zool 67:373–380.",
     "domaine": "Orignal — capacité de support hivernale."},
]

# 9 paramètres nutrition par espèce.
# Format : {value, signature{type, unit, source, range, semantics}}
# Valeurs CIBLES INSTITUTIONNELLES — sourcées documents-types.
NUTRITION_TARGETS = {
    "CHEVREUIL": {
        "nutrition.besoins_proteines": {
            "value_target": 16.0,
            "signature": signature_template(
                "float", "% MS",  # % de matière sèche
                "HEWITT_2011 ch.4 ; MFFP_PG_2020_2027 §3.2.1",
                "[12.0..20.0]",
                "% protéines brutes/MS, valeur printemps adulte ; ration <14 = stress reproductif"
            ),
            "valeur_actuelle_bio_profile": "TEXTE_QUALITATIF (liste)",
            "score_actuel_norm": 0.0,
            "score_attendu_apres": 53.3,
        },
        "nutrition.besoins_energetiques": {
            "value_target": 2800.0,
            "signature": signature_template(
                "float", "kcal/kg MS jour",
                "HEWITT_2011 ch.4 ; CRETE_1989",
                "[1800..3500]",
                "Besoins énergétiques métaboliques en kcal/kg/jour pour adulte 60 kg"
            ),
            "valeur_actuelle_bio_profile": "TEXTE_QUALITATIF",
            "score_actuel_norm": 0.0,
            "score_attendu_apres": 56.0,
        },
        "nutrition.besoins_mineraux.sodium": {
            "value_target": 0.30,
            "signature": signature_template(
                "float", "g/kg MS",
                "HEWITT_2011 ch.4 ; MFFP_PG_2020_2027",
                "[0.10..0.80]",
                "Sodium pour gestation/lactation ; carences fréquentes en sol acide québécois"
            ),
            "score_actuel_norm": 0.0,
            "score_attendu_apres": 15.0,
        },
        "nutrition.besoins_mineraux.calcium": {
            "value_target": 4.5,
            "signature": signature_template(
                "float", "g/kg MS",
                "HEWITT_2011 ch.4",
                "[1.5..8.0]",
                "Ca pour antlérogenèse, gestation, lactation"
            ),
            "score_actuel_norm": 0.0,
            "score_attendu_apres": 90.0,
        },
        "nutrition.besoins_mineraux.magnesium": {
            "value_target": 0.45,
            "signature": signature_template(
                "float", "g/kg MS",
                "HEWITT_2011 ch.4",
                "[0.10..1.50]",
                "Mg cofacteur >300 enzymes ; carence = tétanie hivernale"
            ),
            "score_actuel_norm": 0.0,
            "score_attendu_apres": 22.5,
        },
        "nutrition.alimentation_saisonniere.printemps": {
            "value_target": {"disponibilite": True, "ration_kg": 2.5,
                             "categorie": "fourrage_riche_proteines"},
            "signature": signature_template(
                "object", "kg MS/jour + dispo",
                "MFFP_PG_2020_2027 §3.2.2 ; HEWITT_2011",
                "ration ∈ [0..5.0]",
                "Disponibilité fourrage printanier ; bourgeons, pousses, herbacées"
            ),
            "score_actuel_norm": 0.0,
            "score_attendu_apres": 100.0,
        },
        "nutrition.alimentation_saisonniere.ete": {
            "value_target": {"disponibilite": True, "ration_kg": 2.2,
                             "categorie": "vegetation_humide_riche"},
            "signature": signature_template("object", "kg MS/jour", "HEWITT_2011 ch.4", "[0..5.0]",
                                             "Sélection thermorégulation été (zones humides)"),
            "score_actuel_norm": 0.0, "score_attendu_apres": 100.0,
        },
        "nutrition.alimentation_saisonniere.automne": {
            "value_target": {"disponibilite": True, "ration_kg": 3.0,
                             "categorie": "mast_glands_fruits"},
            "signature": signature_template("object", "kg MS/jour", "HEWITT_2011 ch.4", "[0..5.0]",
                                             "Mast (glands, faînes) — pic énergétique automnal"),
            "score_actuel_norm": 0.0, "score_attendu_apres": 100.0,
        },
        "nutrition.alimentation_saisonniere.hiver": {
            "value_target": {"disponibilite": True, "ration_kg": 1.8,
                             "categorie": "ravage_thuya_branchage"},
            "signature": signature_template("object", "kg MS/jour", "MFFP_PG_2020_2027 §3.2.3", "[0..3.5]",
                                             "Ravages d'hiver, thuya, ericacees"),
            "score_actuel_norm": 0.0, "score_attendu_apres": 100.0,
        },
    },
    "ORIGNAL": {
        "nutrition.besoins_proteines": {
            "value_target": 12.0, "signature": signature_template(
                "float", "% MS", "RENECKER_HUDSON_1990 ; MFFP_PG_2020_2027",
                "[8.0..18.0]", "% protéines brutes ; adulte 450 kg"),
            "score_actuel_norm": 0.0, "score_attendu_apres": 40.0,
        },
        "nutrition.besoins_energetiques": {
            "value_target": 35000.0, "signature": signature_template(
                "float", "kcal/jour", "RENECKER_HUDSON_1990 ; CRETE_1989",
                "[20000..50000]", "Besoins métaboliques quotidiens orignal adulte"),
            "score_actuel_norm": 0.0, "score_attendu_apres": 70.0,
        },
        "nutrition.besoins_mineraux.sodium": {
            "value_target": 1.20, "signature": signature_template(
                "float", "g/kg MS", "RENECKER_HUDSON_1990",
                "[0.30..2.50]", "Sodium élevé — fréquentation salines/lichens"),
            "score_actuel_norm": 0.0, "score_attendu_apres": 60.0,
        },
        "nutrition.besoins_mineraux.calcium": {
            "value_target": 6.0, "signature": signature_template(
                "float", "g/kg MS", "HEWITT_2011 ch.4 (cervidés)",
                "[2.0..10.0]", "Ca antlérogenèse mâle, gestation femelle"),
            "score_actuel_norm": 0.0, "score_attendu_apres": 100.0,
        },
        "nutrition.besoins_mineraux.magnesium": {
            "value_target": 0.80, "signature": signature_template(
                "float", "g/kg MS", "HEWITT_2011 ch.4", "[0.20..2.00]",
                "Mg activité enzymatique"),
            "score_actuel_norm": 0.0, "score_attendu_apres": 40.0,
        },
        "nutrition.alimentation_saisonniere.printemps": {
            "value_target": {"disponibilite": True, "ration_kg": 18.0,
                             "categorie": "feuillus_bourgeons"},
            "signature": signature_template("object", "kg MS/jour", "RENECKER_HUDSON_1990",
                                             "ration ∈ [0..30.0]", "Bourgeons saule, peuplier, sorbier"),
            "score_actuel_norm": 0.0, "score_attendu_apres": 100.0,
        },
        "nutrition.alimentation_saisonniere.ete": {
            "value_target": {"disponibilite": True, "ration_kg": 22.0,
                             "categorie": "aquatique_macrophytes"},
            "signature": signature_template("object", "kg MS/jour", "RENECKER_HUDSON_1990",
                                             "[0..30.0]", "Plantes aquatiques riches en Na (Potamogeton, Nuphar)"),
            "score_actuel_norm": 0.0, "score_attendu_apres": 100.0,
        },
        "nutrition.alimentation_saisonniere.automne": {
            "value_target": {"disponibilite": True, "ration_kg": 20.0,
                             "categorie": "hyperphagie_pre_rut"},
            "signature": signature_template("object", "kg MS/jour", "CRETE_1989",
                                             "[0..30.0]", "Hyperphagie pré-rut, accumulation graisses"),
            "score_actuel_norm": 0.0, "score_attendu_apres": 100.0,
        },
        "nutrition.alimentation_saisonniere.hiver": {
            "value_target": {"disponibilite": True, "ration_kg": 12.0,
                             "categorie": "ramilles_sapinieres"},
            "signature": signature_template("object", "kg MS/jour", "CRETE_1989 ; MFFP_PG_2020_2027",
                                             "[0..18.0]", "Ramilles sapin baumier, bouleau, érable"),
            "score_actuel_norm": 0.0, "score_attendu_apres": 100.0,
        },
    },
    "OURS_NOIR": {
        "nutrition.besoins_proteines": {
            "value_target": 12.0, "signature": signature_template(
                "float", "% MS", "PELTON_2003",
                "[8.0..16.0]", "Omnivore — protéines variables saisonnières"),
            "score_actuel_norm": 0.0, "score_attendu_apres": 40.0,
        },
        "nutrition.besoins_energetiques": {
            "value_target": 8500.0, "signature": signature_template(
                "float", "kcal/jour", "PELTON_2003",
                "[3000..20000]", "Besoins métaboliques adulte — pic hyperphagie 20 000+"),
            "score_actuel_norm": 0.0, "score_attendu_apres": 100.0,
        },
        "nutrition.besoins_mineraux.sodium": {
            "value_target": 0.20, "signature": signature_template(
                "float", "g/kg MS", "PELTON_2003 ; HEWITT_2011 (omnivores)",
                "[0.05..0.50]", "Faible besoin Na (omnivore)"),
            "score_actuel_norm": 0.0, "score_attendu_apres": 10.0,
        },
        "nutrition.besoins_mineraux.calcium": {
            "value_target": 3.0, "signature": signature_template(
                "float", "g/kg MS", "PELTON_2003", "[1.0..6.0]",
                "Ca via os carcasses, fourmis, baies"),
            "score_actuel_norm": 0.0, "score_attendu_apres": 60.0,
        },
        "nutrition.besoins_mineraux.magnesium": {
            "value_target": 0.30, "signature": signature_template(
                "float", "g/kg MS", "PELTON_2003", "[0.10..0.80]",
                "Mg via végétaux verts printemps"),
            "score_actuel_norm": 0.0, "score_attendu_apres": 15.0,
        },
        "nutrition.alimentation_saisonniere.printemps": {
            "value_target": {"disponibilite": True, "ration_kg": 4.5,
                             "categorie": "carcasses_herbes_emerges"},
            "signature": signature_template("object", "kg MS/jour", "PELTON_2003",
                                             "[0..8.0]", "Sortie tanière : herbes émergentes, carcasses ongulés"),
            "score_actuel_norm": 0.0, "score_attendu_apres": 100.0,
        },
        "nutrition.alimentation_saisonniere.ete": {
            "value_target": {"disponibilite": True, "ration_kg": 6.5,
                             "categorie": "fruits_baies_insectes"},
            "signature": signature_template("object", "kg MS/jour", "PELTON_2003 ; MFFP_PG_2020_2027",
                                             "[0..10.0]", "Bleuets, framboises, fourmis bois"),
            "score_actuel_norm": 0.0, "score_attendu_apres": 100.0,
        },
        "nutrition.alimentation_saisonniere.automne": {
            "value_target": {"disponibilite": True, "ration_kg": 12.0,
                             "categorie": "hyperphagie_mast"},
            "signature": signature_template("object", "kg MS/jour", "PELTON_2003",
                                             "[0..18.0]", "Hyperphagie pré-hibernale : glands hêtres, faînes"),
            "score_actuel_norm": 0.0, "score_attendu_apres": 100.0,
        },
        "nutrition.alimentation_saisonniere.hiver": {
            "value_target": {"disponibilite": False, "ration_kg": 0.0,
                             "categorie": "hibernation"},
            "signature": signature_template("object", "kg MS/jour", "PELTON_2003",
                                             "ration_kg = 0 valide", "Hibernation — disponibilite=False conforme"),
            "score_actuel_norm": 0.0, "score_attendu_apres": 100.0,
        },
    },
    "WAPITI": {
        "nutrition.besoins_proteines": {
            "value_target": 14.0, "signature": signature_template(
                "float", "% MS", "LYON_BURCHAM_1998",
                "[10.0..20.0]", "% prot brutes printemps — graminées herbacées"),
            "score_actuel_norm": 0.0, "score_attendu_apres": 46.7,
        },
        "nutrition.besoins_energetiques": {
            "value_target": 28000.0, "signature": signature_template(
                "float", "kcal/jour", "LYON_BURCHAM_1998",
                "[15000..40000]", "Besoins métaboliques adulte 250 kg"),
            "score_actuel_norm": 0.0, "score_attendu_apres": 56.0,
        },
        "nutrition.besoins_mineraux.sodium": {
            "value_target": 0.50, "signature": signature_template(
                "float", "g/kg MS", "LYON_BURCHAM_1998 ; HEWITT_2011",
                "[0.15..1.20]", "Sodium élevé — fréquentation salines"),
            "score_actuel_norm": 0.0, "score_attendu_apres": 25.0,
        },
        "nutrition.besoins_mineraux.calcium": {
            "value_target": 5.5, "signature": signature_template(
                "float", "g/kg MS", "LYON_BURCHAM_1998", "[2.0..9.0]",
                "Ca antlérogenèse mâle wapiti"),
            "score_actuel_norm": 0.0, "score_attendu_apres": 100.0,
        },
        "nutrition.besoins_mineraux.magnesium": {
            "value_target": 0.55, "signature": signature_template(
                "float", "g/kg MS", "HEWITT_2011 ch.4", "[0.15..1.80]",
                "Mg cofacteur enzymatique"),
            "score_actuel_norm": 0.0, "score_attendu_apres": 27.5,
        },
        "nutrition.alimentation_saisonniere.printemps": {
            "value_target": {"disponibilite": True, "ration_kg": 8.5,
                             "categorie": "graminees_herbacees_pousses"},
            "signature": signature_template("object", "kg MS/jour", "LYON_BURCHAM_1998",
                                             "[0..15.0]", "Pousses graminées, herbacées riches"),
            "score_actuel_norm": 0.0, "score_attendu_apres": 100.0,
        },
        "nutrition.alimentation_saisonniere.ete": {
            "value_target": {"disponibilite": True, "ration_kg": 9.0,
                             "categorie": "vegetation_fraiche"},
            "signature": signature_template("object", "kg MS/jour", "LYON_BURCHAM_1998",
                                             "[0..15.0]", "Végétation fraîche en altitude (thermo)"),
            "score_actuel_norm": 0.0, "score_attendu_apres": 100.0,
        },
        "nutrition.alimentation_saisonniere.automne": {
            "value_target": {"disponibilite": True, "ration_kg": 10.5,
                             "categorie": "graminees_glands_pre_rut"},
            "signature": signature_template("object", "kg MS/jour", "LYON_BURCHAM_1998",
                                             "[0..15.0]", "Pré-rut : énergie pour brame + déplacements"),
            "score_actuel_norm": 0.0, "score_attendu_apres": 100.0,
        },
        "nutrition.alimentation_saisonniere.hiver": {
            "value_target": {"disponibilite": True, "ration_kg": 6.0,
                             "categorie": "ecorces_branchages"},
            "signature": signature_template("object", "kg MS/jour", "LYON_BURCHAM_1998 ; MFFP_PG_2020_2027",
                                             "[0..10.0]", "Écorces, branchages, conifères"),
            "score_actuel_norm": 0.0, "score_attendu_apres": 100.0,
        },
    },
    "DINDON_SAUVAGE": {
        "nutrition.besoins_proteines": {
            "value_target": 18.0, "signature": signature_template(
                "float", "% MS", "EATON_HEALY_1991",
                "[12.0..28.0]", "% prot brutes ; juvéniles >25%, adultes 18%"),
            "score_actuel_norm": 0.0, "score_attendu_apres": 60.0,
        },
        "nutrition.besoins_energetiques": {
            "value_target": 350.0, "signature": signature_template(
                "float", "kcal/jour", "EATON_HEALY_1991",
                "[200..500]", "Adulte 6 kg — base ratio métabolique"),
            "score_actuel_norm": 0.0, "score_attendu_apres": 7.0,
        },
        "nutrition.besoins_mineraux.sodium": {
            "value_target": 0.10, "signature": signature_template(
                "float", "g/kg MS", "EATON_HEALY_1991",
                "[0.03..0.40]", "Faible besoin Na ; eau libre majeure"),
            "score_actuel_norm": 0.0, "score_attendu_apres": 5.0,
        },
        "nutrition.besoins_mineraux.calcium": {
            "value_target": 25.0, "signature": signature_template(
                "float", "g/kg MS", "EATON_HEALY_1991 (femelles ponte)",
                "[3.0..40.0]", "Ca très élevé pour formation coquilles œufs"),
            "score_actuel_norm": 0.0, "score_attendu_apres": 100.0,
        },
        "nutrition.besoins_mineraux.magnesium": {
            "value_target": 0.50, "signature": signature_template(
                "float", "g/kg MS", "EATON_HEALY_1991", "[0.10..1.20]",
                "Mg activité musculaire/nerveuse"),
            "score_actuel_norm": 0.0, "score_attendu_apres": 25.0,
        },
        "nutrition.alimentation_saisonniere.printemps": {
            "value_target": {"disponibilite": True, "ration_kg": 0.45,
                             "categorie": "insectes_proteines_juvenile"},
            "signature": signature_template("object", "kg MS/jour", "EATON_HEALY_1991",
                                             "[0..1.0]", "Insectes pour juvéniles ; bourgeons adultes"),
            "score_actuel_norm": 0.0, "score_attendu_apres": 100.0,
        },
        "nutrition.alimentation_saisonniere.ete": {
            "value_target": {"disponibilite": True, "ration_kg": 0.35,
                             "categorie": "fruits_insectes_graines"},
            "signature": signature_template("object", "kg MS/jour", "EATON_HEALY_1991",
                                             "[0..0.8]", "Baies, sauterelles, graines"),
            "score_actuel_norm": 0.0, "score_attendu_apres": 100.0,
        },
        "nutrition.alimentation_saisonniere.automne": {
            "value_target": {"disponibilite": True, "ration_kg": 0.55,
                             "categorie": "mast_glands"},
            "signature": signature_template("object", "kg MS/jour", "EATON_HEALY_1991",
                                             "[0..1.2]", "Glands chêne, faînes, baies"),
            "score_actuel_norm": 0.0, "score_attendu_apres": 100.0,
        },
        "nutrition.alimentation_saisonniere.hiver": {
            "value_target": {"disponibilite": True, "ration_kg": 0.25,
                             "categorie": "graines_residus_culture"},
            "signature": signature_template("object", "kg MS/jour", "EATON_HEALY_1991 ; MFFP_PG_2020_2027",
                                             "[0..0.6]", "Maïs résiduel, graines, glands sous neige"),
            "score_actuel_norm": 0.0, "score_attendu_apres": 100.0,
        },
    },
}


# ═════════════════════════════════════════════════════════════════════════
# DATA — PARAMÈTRES CORRIDORS_Ω
# ═════════════════════════════════════════════════════════════════════════

CORRIDORS_REFS = [
    {"id": "FORMAN_2003",
     "citation": "Forman RTT et al. (2003). Road Ecology — Science and Solutions. Island Press.",
     "domaine": "Effets routes sur faune ; barrières et indices fragmentation."},
    {"id": "BEAUCHESNE_2014",
     "citation": "Beauchesne D et al. (2014). Connectivity for moose in fragmented landscapes. Landscape Ecol 29:1187–1201.",
     "domaine": "Orignal Québec — corridors fonctionnels."},
    {"id": "WALTER_2018",
     "citation": "Walter WD et al. (2018). White-tailed deer movement ecology. Ecol Monogr 88:67–88.",
     "domaine": "Cervidé — distances dispersion juvéniles."},
    {"id": "PROCTOR_2012",
     "citation": "Proctor MF et al. (2012). Population fragmentation and inter-ecosystem movements of grizzly/black bears. Wildl Monogr 180:1–46.",
     "domaine": "Ours — connectivité populations."},
    {"id": "FRAIR_2008",
     "citation": "Frair JL et al. (2008). Resource selection by elk. J Appl Ecol 45:1504–1513.",
     "domaine": "Wapiti — sélection corridors saisonniers."},
    {"id": "MFFP_CORRIDORS_2018",
     "citation": "MFFP Québec (2018). Atlas des corridors écologiques — réseau de connectivité 5 espèces.",
     "domaine": "Référentiel institutionnel québécois."},
    {"id": "DICKSON_2017",
     "citation": "Dickson BG et al. (2017). Circuit-theory applications to connectivity science. Conserv Biol 31:90–104.",
     "domaine": "Méthode circuit-theory pour fragmentation_penalty quantitative."},
]

# Coefficients spécifiques par espèce (P0/P1/P2)
CORRIDORS_TARGETS = {
    "CHEVREUIL": {
        "corridors.connectivite_optimum": {"value_target": 0.78, "priority": "P0",
            "signature": signature_template("float", "indice 0..1", "WALTER_2018 ; MFFP_CORRIDORS_2018",
                "[0..1]", "Connectivité Circuit-theory — > 0.7 fonctionnelle pour chevreuil")},
        "corridors.fragmentation_penalty": {"value_target": 0.32, "priority": "P0",
            "signature": signature_template("float", "indice 0..1", "FORMAN_2003 ; DICKSON_2017",
                "[0..1]", "Pénalité fragmentation ; <0.4 acceptable pour chevreuil dispersionniste")},
        "corridors.distances_typiques": {"value_target": {"juveniles_km": 18.0, "adultes_km": 4.5}, "priority": "P0",
            "signature": signature_template("object", "km", "WALTER_2018 ; HEWITT_2011",
                "juveniles ∈ [5..50], adultes ∈ [1..10]",
                "Dispersion juvéniles mâles >>> femelles (philopatrie)")},
        "corridors.tolerance_ouvertures": {"value_target": 0.85, "priority": "P1",
            "signature": signature_template("float", "indice 0..1", "WALTER_2018",
                "[0..1]", "Espèce de bordure — tolère grandes ouvertures agricoles")},
        "corridors.aversion_infrastructures": {"value_target": 0.45, "priority": "P1",
            "signature": signature_template("float", "indice 0..1", "FORMAN_2003 ; WALTER_2018",
                "[0..1]", "Aversion routes/urbanisation moyenne")},
        "corridors.distance_fuite_m": {"value_target": 80.0, "priority": "P1",
            "signature": signature_template("float", "m", "HEWITT_2011 ch.7",
                "[20..200]", "Distance fuite humain en milieu agricole")},
        "corridors.couvert_forestier_min": {"value_target": 0.35, "priority": "P0",
            "signature": signature_template("float", "fraction", "MFFP_CORRIDORS_2018",
                "[0..1]", "Couvert forestier minimum requis (corridors fonctionnels)")},
        "corridors.pente_max_deg": {"value_target": 35.0, "priority": "P2",
            "signature": signature_template("float", "degrés", "FRAIR_2008 (cervidés)",
                "[0..60]", "Pente max acceptée en déplacement")},
    },
    "ORIGNAL": {
        "corridors.connectivite_optimum": {"value_target": 0.85, "priority": "P0",
            "signature": signature_template("float", "indice 0..1", "BEAUCHESNE_2014 ; MFFP_CORRIDORS_2018",
                "[0..1]", "Connectivité critique en habitat morcelé québécois")},
        "corridors.fragmentation_penalty": {"value_target": 0.48, "priority": "P0",
            "signature": signature_template("float", "indice 0..1", "BEAUCHESNE_2014 ; FORMAN_2003",
                "[0..1]", "Pénalité fragmentation forte (espèce sensible)")},
        "corridors.distances_typiques": {"value_target": {"saisonnieres_km": 25.0, "quotidienne_km": 3.0},
            "priority": "P0",
            "signature": signature_template("object", "km", "BEAUCHESNE_2014",
                "saisonnieres ∈ [5..80]",
                "Migrations saisonnières été↔hiver moyennes 25km")},
        "corridors.tolerance_ouvertures": {"value_target": 0.25, "priority": "P1",
            "signature": signature_template("float", "indice 0..1", "BEAUCHESNE_2014",
                "[0..1]", "Faible tolérance ouvertures (préfère couvert dense)")},
        "corridors.aversion_infrastructures": {"value_target": 0.78, "priority": "P0",
            "signature": signature_template("float", "indice 0..1", "FORMAN_2003 ; BEAUCHESNE_2014",
                "[0..1]", "Forte aversion routes (collisions élevées)")},
        "corridors.distance_fuite_m": {"value_target": 250.0, "priority": "P1",
            "signature": signature_template("float", "m", "RENECKER_HUDSON_1990",
                "[100..500]", "Distance fuite humain en habitat ouvert")},
        "corridors.couvert_forestier_min": {"value_target": 0.65, "priority": "P0",
            "signature": signature_template("float", "fraction", "MFFP_CORRIDORS_2018 ; BEAUCHESNE_2014",
                "[0..1]", "Couvert forestier minimum élevé requis")},
        "corridors.pente_max_deg": {"value_target": 30.0, "priority": "P2",
            "signature": signature_template("float", "degrés", "BEAUCHESNE_2014",
                "[0..50]", "Pente max — gabarit limite mobilité")},
    },
    "OURS_NOIR": {
        "corridors.connectivite_optimum": {"value_target": 0.72, "priority": "P0",
            "signature": signature_template("float", "indice 0..1", "PROCTOR_2012 ; MFFP_CORRIDORS_2018",
                "[0..1]", "Connectivité populations métapopulation")},
        "corridors.fragmentation_penalty": {"value_target": 0.55, "priority": "P0",
            "signature": signature_template("float", "indice 0..1", "PROCTOR_2012",
                "[0..1]", "Forte pénalité — fragmentation amplifie conflits humains")},
        "corridors.distances_typiques": {"value_target": {"males_km": 35.0, "femelles_km": 8.0,
                                                            "dispersion_juv_km": 60.0}, "priority": "P0",
            "signature": signature_template("object", "km", "PROCTOR_2012",
                "males ∈ [10..150]", "Dispersion mâles >> femelles philopatriques")},
        "corridors.tolerance_ouvertures": {"value_target": 0.40, "priority": "P1",
            "signature": signature_template("float", "indice 0..1", "PELTON_2003",
                "[0..1]", "Tolérance ouvertures moyenne (recherche fruits)")},
        "corridors.aversion_infrastructures": {"value_target": 0.62, "priority": "P0",
            "signature": signature_template("float", "indice 0..1", "PROCTOR_2012 ; FORMAN_2003",
                "[0..1]", "Aversion forte infrastructures - mortalité par route")},
        "corridors.distance_fuite_m": {"value_target": 120.0, "priority": "P1",
            "signature": signature_template("float", "m", "PELTON_2003",
                "[50..300]", "Distance fuite humain ; habituation possible")},
        "corridors.couvert_forestier_min": {"value_target": 0.55, "priority": "P0",
            "signature": signature_template("float", "fraction", "PROCTOR_2012 ; MFFP_CORRIDORS_2018",
                "[0..1]", "Forêt mature requise")},
        "corridors.pente_max_deg": {"value_target": 45.0, "priority": "P2",
            "signature": signature_template("float", "degrés", "PROCTOR_2012",
                "[0..60]", "Forte tolérance pentes (escarpements)")},
    },
    "WAPITI": {
        "corridors.connectivite_optimum": {"value_target": 0.80, "priority": "P0",
            "signature": signature_template("float", "indice 0..1", "FRAIR_2008 ; MFFP_CORRIDORS_2018",
                "[0..1]", "Connectivité migrations stables pluri-annuelles")},
        "corridors.fragmentation_penalty": {"value_target": 0.42, "priority": "P0",
            "signature": signature_template("float", "indice 0..1", "FRAIR_2008",
                "[0..1]", "Pénalité fragmentation modérée — corridors larges")},
        "corridors.distances_typiques": {"value_target": {"migration_saisonniere_km": 45.0,
                                                           "quotidienne_km": 5.0}, "priority": "P0",
            "signature": signature_template("object", "km", "FRAIR_2008",
                "migration ∈ [15..120]", "Migrations saisonnières marquées")},
        "corridors.tolerance_ouvertures": {"value_target": 0.70, "priority": "P1",
            "signature": signature_template("float", "indice 0..1", "LYON_BURCHAM_1998",
                "[0..1]", "Tolère prairies et parcs ouverts")},
        "corridors.aversion_infrastructures": {"value_target": 0.55, "priority": "P0",
            "signature": signature_template("float", "indice 0..1", "FRAIR_2008",
                "[0..1]", "Aversion modérée routes")},
        "corridors.distance_fuite_m": {"value_target": 200.0, "priority": "P1",
            "signature": signature_template("float", "m", "LYON_BURCHAM_1998",
                "[80..400]", "Distance fuite supérieure au chevreuil")},
        "corridors.couvert_forestier_min": {"value_target": 0.40, "priority": "P0",
            "signature": signature_template("float", "fraction", "FRAIR_2008",
                "[0..1]", "Couvert forestier modéré requis")},
        "corridors.pente_max_deg": {"value_target": 40.0, "priority": "P2",
            "signature": signature_template("float", "degrés", "FRAIR_2008",
                "[0..50]", "Pente max — espèce montagnarde")},
    },
    "DINDON_SAUVAGE": {
        "corridors.connectivite_optimum": {"value_target": 0.65, "priority": "P0",
            "signature": signature_template("float", "indice 0..1", "EATON_HEALY_1991 ; MFFP_CORRIDORS_2018",
                "[0..1]", "Connectivité localisée (déplacements <10 km)")},
        "corridors.fragmentation_penalty": {"value_target": 0.30, "priority": "P0",
            "signature": signature_template("float", "indice 0..1", "EATON_HEALY_1991",
                "[0..1]", "Faible pénalité (s'adapte aux mosaïques)")},
        "corridors.distances_typiques": {"value_target": {"quotidienne_km": 1.5,
                                                           "saisonniere_km": 5.0}, "priority": "P0",
            "signature": signature_template("object", "km", "EATON_HEALY_1991",
                "quotidienne ∈ [0.5..3.0]", "Déplacements limités")},
        "corridors.tolerance_ouvertures": {"value_target": 0.90, "priority": "P1",
            "signature": signature_template("float", "indice 0..1", "EATON_HEALY_1991",
                "[0..1]", "Tolère champs/bordures (recherche graines)")},
        "corridors.aversion_infrastructures": {"value_target": 0.40, "priority": "P1",
            "signature": signature_template("float", "indice 0..1", "EATON_HEALY_1991",
                "[0..1]", "Aversion modérée routes ; sensible à la chasse")},
        "corridors.distance_fuite_m": {"value_target": 60.0, "priority": "P1",
            "signature": signature_template("float", "m", "EATON_HEALY_1991",
                "[20..150]", "Distance fuite (adultes méfiants)")},
        "corridors.couvert_forestier_min": {"value_target": 0.30, "priority": "P0",
            "signature": signature_template("float", "fraction", "EATON_HEALY_1991 ; MFFP_CORRIDORS_2018",
                "[0..1]", "Mosaïque forêt-champ optimale (30-50% forêt)")},
        "corridors.pente_max_deg": {"value_target": 25.0, "priority": "P2",
            "signature": signature_template("float", "degrés", "EATON_HEALY_1991",
                "[0..40]", "Pente max — terrain accidenté limite")},
    },
}


# ═════════════════════════════════════════════════════════════════════════
# DATA — PARAMÈTRES SENSORIEL_Ω
# ═════════════════════════════════════════════════════════════════════════

SENSORIEL_REFS = [
    {"id": "DEYOUNG_MILLER_2011",
     "citation": "DeYoung CA & Miller KV (2011). Behavior. In: Hewitt DG (ed.) Biology and Management of WT Deer. CRC Press.",
     "domaine": "Cervidé — communication chimique, olfaction."},
    {"id": "BLOOMFIELD_2008",
     "citation": "Bloomfield LL et al. (2008). Auditory thresholds and noise impacts. Wildl Soc Bull 36:34–42.",
     "domaine": "Sensibilité auditive faune sauvage."},
    {"id": "GAGNON_2007",
     "citation": "Gagnon JW et al. (2007). Effects of vehicular traffic on elk. J Wildl Manag 71:2318–2323.",
     "domaine": "Wapiti — bruit véhiculaire, distance perturbation."},
    {"id": "VANDERLOEFF_2014",
     "citation": "Van der Loeff IH et al. (2014). Light pollution and wildlife. Phil Trans R Soc B 370.",
     "domaine": "Pollution lumineuse — réponse comportementale."},
    {"id": "PARKER_2009",
     "citation": "Parker KL et al. (2009). Nutrition integrates environmental responses of ungulates. Funct Ecol 23:57–69.",
     "domaine": "Ongulés — seuils thermiques mortalité hivernale."},
    {"id": "POWELL_1997",
     "citation": "Powell RA et al. (1997). Ecology and behaviour of N. American Black Bears. Chapman & Hall.",
     "domaine": "Ours noir — sens, hibernation, perception."},
    {"id": "HEALY_1992",
     "citation": "Healy WM (1992). Behavior. In: Dickson JG (ed.) The Wild Turkey. Stackpole.",
     "domaine": "Dindon — vision (champ visuel, dichromate)."},
    {"id": "MFFP_NEIGE_2019",
     "citation": "MFFP Québec (2019). Tableau de bord neige et grand cervidé — seuils mortalité hivernale.",
     "domaine": "Référentiel institutionnel seuils nivologiques 5 espèces."},
]

SENSORIEL_TARGETS = {
    "CHEVREUIL": {
        "thermoregulation.seuil_stress": {"value_target": 27.0, "priority": "P0", "actuel": 27.0,
            "signature": signature_template("float", "°C", "DEYOUNG_MILLER_2011 ; HEWITT_2011",
                "[20..32]", "Stress thermique au-dessus de 27°C"),
            "deja_present": True},
        "neige.seuil_mobilite": {"value_target": 45.0, "priority": "P0", "actuel": 45.0,
            "signature": signature_template("float", "cm", "MFFP_NEIGE_2019",
                "[30..70]", "Seuil mobilité réduite au-dessus de 45 cm"),
            "deja_present": True},
        "neige.seuil_mortalite": {"value_target": 80.0, "priority": "P0", "actuel": None,
            "signature": signature_template("float", "cm", "MFFP_NEIGE_2019 ; PARKER_2009",
                "[60..120]", "Seuil mortalité hivernale (énergie+prédation+ravage)"),
            "deja_present": False},
        "olfaction.portee_m": {"value_target": 250.0, "priority": "P0",
            "signature": signature_template("float", "m", "DEYOUNG_MILLER_2011",
                "[100..500]", "Portée olfactive humain/prédateur")},
        "olfaction.sensibilite_predateur": {"value_target": 0.85, "priority": "P0",
            "signature": signature_template("float", "indice 0..1", "DEYOUNG_MILLER_2011",
                "[0..1]", "Détection coyote/loup")},
        "audition.seuil_db": {"value_target": 20.0, "priority": "P1",
            "signature": signature_template("float", "dB SPL @ 4kHz", "BLOOMFIELD_2008",
                "[15..30]", "Seuil détection auditive")},
        "vision.champ_visuel_deg": {"value_target": 310.0, "priority": "P1",
            "signature": signature_template("float", "degrés", "DEYOUNG_MILLER_2011",
                "[280..330]", "Champ panoramique très large")},
        "vision.dichromate": {"value_target": True, "priority": "P2",
            "signature": signature_template("bool", "—", "DEYOUNG_MILLER_2011",
                "True/False", "Vision dichromatique (bleu/jaune)")},
        "lumiere.sensibilite_pollution": {"value_target": 0.55, "priority": "P1",
            "signature": signature_template("float", "indice 0..1", "VANDERLOEFF_2014",
                "[0..1]", "Sensibilité éclairage artificiel")},
        "reaction.distance_perturbation_m": {"value_target": 150.0, "priority": "P0",
            "signature": signature_template("float", "m", "DEYOUNG_MILLER_2011",
                "[50..400]", "Distance déclenchement fuite")},
    },
    "ORIGNAL": {
        "thermoregulation.seuil_stress": {"value_target": 15.5, "priority": "P0", "actuel": 15.5,
            "signature": signature_template("float", "°C", "RENECKER_HUDSON_1990",
                "[12..18]", "Stress thermique très bas"),
            "deja_present": True},
        "neige.seuil_mobilite": {"value_target": 65.0, "priority": "P0", "actuel": 65.0,
            "signature": signature_template("float", "cm", "MFFP_NEIGE_2019",
                "[50..90]", "Seuil mobilité — gabarit grand"),
            "deja_present": True},
        "neige.seuil_mortalite": {"value_target": 110.0, "priority": "P0", "actuel": None,
            "signature": signature_template("float", "cm", "MFFP_NEIGE_2019 ; CRETE_1989",
                "[90..150]", "Seuil mortalité hivernale orignal"),
            "deja_present": False},
        "olfaction.portee_m": {"value_target": 350.0, "priority": "P0",
            "signature": signature_template("float", "m", "RENECKER_HUDSON_1990",
                "[150..600]", "Portée olfactive grande (museau allongé)")},
        "olfaction.sensibilite_predateur": {"value_target": 0.80, "priority": "P0",
            "signature": signature_template("float", "indice 0..1", "RENECKER_HUDSON_1990",
                "[0..1]", "Détection loup/ours noir")},
        "audition.seuil_db": {"value_target": 18.0, "priority": "P1",
            "signature": signature_template("float", "dB SPL @ 2kHz", "BLOOMFIELD_2008",
                "[12..25]", "Seuil détection — basses fréquences")},
        "vision.champ_visuel_deg": {"value_target": 295.0, "priority": "P2",
            "signature": signature_template("float", "degrés", "RENECKER_HUDSON_1990",
                "[280..310]", "Champ panoramique modéré")},
        "vision.dichromate": {"value_target": True, "priority": "P2",
            "signature": signature_template("bool", "—", "RENECKER_HUDSON_1990",
                "True/False", "Vision dichromatique cervidé")},
        "lumiere.sensibilite_pollution": {"value_target": 0.40, "priority": "P1",
            "signature": signature_template("float", "indice 0..1", "VANDERLOEFF_2014",
                "[0..1]", "Sensibilité modérée éclairage")},
        "reaction.distance_perturbation_m": {"value_target": 300.0, "priority": "P0",
            "signature": signature_template("float", "m", "RENECKER_HUDSON_1990",
                "[150..500]", "Distance fuite supérieure au chevreuil")},
    },
    "OURS_NOIR": {
        "thermoregulation.seuil_stress": {"value_target": 24.0, "priority": "P0", "actuel": None,
            "signature": signature_template("float", "°C", "POWELL_1997",
                "[20..30]", "Stress thermique — fourrure dense"),
            "deja_present": False},
        "neige.seuil_mobilite": {"value_target": 50.0, "priority": "P0", "actuel": None,
            "signature": signature_template("float", "cm", "POWELL_1997 ; MFFP_NEIGE_2019",
                "[40..80]", "Seuil mobilité (généralement en hibernation)"),
            "deja_present": False},
        "neige.seuil_mortalite": {"value_target": 150.0, "priority": "P0", "actuel": None,
            "signature": signature_template("float", "cm", "POWELL_1997",
                "Hibernation ; seuil élevé (rare exposition)",
                "Mortalité rare neige (hibernation protectrice)"),
            "deja_present": False},
        "olfaction.portee_m": {"value_target": 800.0, "priority": "P0",
            "signature": signature_template("float", "m", "POWELL_1997",
                "[500..2000]", "Portée olfactive exceptionnelle (carcasses)")},
        "olfaction.sensibilite_predateur": {"value_target": 0.40, "priority": "P1",
            "signature": signature_template("float", "indice 0..1", "POWELL_1997",
                "[0..1]", "Apex predator — peu de prédateurs")},
        "audition.seuil_db": {"value_target": 22.0, "priority": "P1",
            "signature": signature_template("float", "dB SPL @ 2kHz", "BLOOMFIELD_2008 ; POWELL_1997",
                "[15..30]", "Seuil détection auditive")},
        "vision.champ_visuel_deg": {"value_target": 230.0, "priority": "P2",
            "signature": signature_template("float", "degrés", "POWELL_1997",
                "[210..250]", "Champ visuel limité (yeux frontaux)")},
        "vision.dichromate": {"value_target": True, "priority": "P2",
            "signature": signature_template("bool", "—", "POWELL_1997",
                "True/False", "Vision dichromatique mais olfaction dominante")},
        "lumiere.sensibilite_pollution": {"value_target": 0.35, "priority": "P1",
            "signature": signature_template("float", "indice 0..1", "VANDERLOEFF_2014",
                "[0..1]", "Sensibilité faible — habitat forestier")},
        "reaction.distance_perturbation_m": {"value_target": 100.0, "priority": "P0",
            "signature": signature_template("float", "m", "POWELL_1997 ; PELTON_2003",
                "[40..250]", "Distance fuite — habituation possible")},
    },
    "WAPITI": {
        "thermoregulation.seuil_stress": {"value_target": 22.5, "priority": "P0", "actuel": 22.5,
            "signature": signature_template("float", "°C", "LYON_BURCHAM_1998",
                "[18..28]", "Stress thermique"),
            "deja_present": True},
        "neige.seuil_mobilite": {"value_target": 50.0, "priority": "P0", "actuel": 50.0,
            "signature": signature_template("float", "cm", "MFFP_NEIGE_2019 ; LYON_BURCHAM_1998",
                "[35..75]", "Seuil mobilité"),
            "deja_present": True},
        "neige.seuil_mortalite": {"value_target": 100.0, "priority": "P0", "actuel": None,
            "signature": signature_template("float", "cm", "MFFP_NEIGE_2019 ; PARKER_2009",
                "[80..140]", "Seuil mortalité hivernale wapiti"),
            "deja_present": False},
        "olfaction.portee_m": {"value_target": 280.0, "priority": "P0",
            "signature": signature_template("float", "m", "GAGNON_2007 ; LYON_BURCHAM_1998",
                "[120..500]", "Portée olfactive humain/prédateur")},
        "olfaction.sensibilite_predateur": {"value_target": 0.78, "priority": "P0",
            "signature": signature_template("float", "indice 0..1", "FRAIR_2008",
                "[0..1]", "Détection loup, couguar")},
        "audition.seuil_db": {"value_target": 19.0, "priority": "P0",
            "signature": signature_template("float", "dB SPL @ 4kHz", "BLOOMFIELD_2008",
                "[14..28]", "Sensibilité bruit véhiculaire élevée")},
        "vision.champ_visuel_deg": {"value_target": 300.0, "priority": "P1",
            "signature": signature_template("float", "degrés", "FRAIR_2008",
                "[280..320]", "Champ panoramique large")},
        "vision.dichromate": {"value_target": True, "priority": "P2",
            "signature": signature_template("bool", "—", "FRAIR_2008",
                "True/False", "Vision dichromatique")},
        "lumiere.sensibilite_pollution": {"value_target": 0.50, "priority": "P1",
            "signature": signature_template("float", "indice 0..1", "VANDERLOEFF_2014",
                "[0..1]", "Sensibilité modérée — sites brâme")},
        "reaction.distance_perturbation_m": {"value_target": 250.0, "priority": "P0",
            "signature": signature_template("float", "m", "GAGNON_2007 ; FRAIR_2008",
                "[100..500]", "Distance fuite véhicule (fermée chasse) ; >500m sites brâme")},
    },
    "DINDON_SAUVAGE": {
        "thermoregulation.seuil_stress": {"value_target": 30.0, "priority": "P0", "actuel": None,
            "signature": signature_template("float", "°C", "EATON_HEALY_1991",
                "[26..35]", "Stress thermique élevé (plumes isolantes)"),
            "deja_present": False},
        "neige.seuil_mobilite": {"value_target": 25.0, "priority": "P0", "actuel": 25.0,
            "signature": signature_template("float", "cm", "MFFP_NEIGE_2019 ; EATON_HEALY_1991",
                "[15..40]", "Seuil mobilité (gabarit petit, pattes courtes)"),
            "deja_present": True},
        "neige.seuil_mortalite": {"value_target": 50.0, "priority": "P0", "actuel": None,
            "signature": signature_template("float", "cm", "MFFP_NEIGE_2019 ; EATON_HEALY_1991",
                "[35..70]", "Seuil mortalité — accès graines bloqué"),
            "deja_present": False},
        "olfaction.portee_m": {"value_target": 30.0, "priority": "P2",
            "signature": signature_template("float", "m", "HEALY_1992",
                "[10..80]", "Olfaction faible (oiseau)")},
        "olfaction.sensibilite_predateur": {"value_target": 0.20, "priority": "P2",
            "signature": signature_template("float", "indice 0..1", "HEALY_1992",
                "[0..1]", "Olfaction marginale — vision dominante")},
        "audition.seuil_db": {"value_target": 10.0, "priority": "P0",
            "signature": signature_template("float", "dB SPL @ 2kHz", "HEALY_1992 ; BLOOMFIELD_2008",
                "[8..15]", "Audition très fine")},
        "vision.champ_visuel_deg": {"value_target": 360.0, "priority": "P0",
            "signature": signature_template("float", "degrés", "HEALY_1992 ; EATON_HEALY_1991",
                "[340..360]", "Champ panoramique total (yeux latéraux)")},
        "vision.acuite_relative": {"value_target": 8.0, "priority": "P0",
            "signature": signature_template("float", "× humain", "HEALY_1992",
                "[5..12]", "Acuité visuelle 5-8x humaine")},
        "vision.tetrachromate_uv": {"value_target": True, "priority": "P0",
            "signature": signature_template("bool", "—", "HEALY_1992",
                "True/False", "Vision tétrachromatique avec UV")},
        "lumiere.sensibilite_pollution": {"value_target": 0.65, "priority": "P1",
            "signature": signature_template("float", "indice 0..1", "VANDERLOEFF_2014 ; HEALY_1992",
                "[0..1]", "Sensibilité élevée — perchage nocturne")},
        "reaction.distance_perturbation_m": {"value_target": 80.0, "priority": "P0",
            "signature": signature_template("float", "m", "EATON_HEALY_1991",
                "[30..200]", "Distance fuite ; chasse intensifie")},
    },
}


print("[BCE-4X] Données scientifiques chargées —",
      f"NUTRITION 9×5={9 * 5} cibles · CORRIDORS 8×5={8 * 5} cibles · "
      f"SENSORIEL ~10×5={10 * 5} cibles")
