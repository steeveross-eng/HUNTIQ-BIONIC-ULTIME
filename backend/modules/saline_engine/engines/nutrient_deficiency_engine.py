"""
SALINE INTELLIGENCE ULTRA — Nutrient Deficiency Engine V1
Calcule % couverture besoins, deficits exacts, interactions minerales.

Interactions cles:
- Ca bloque Zn (ratio Ca/Zn > 300 = blocage)
- K bloque Mg (ratio K/Mg > 3 = blocage)
- Fe bloque P (haute Fe reduit absorption P)
- Ratios optimaux Ca:P = 1.5-2:1

Conformite: GOLDEN-BCE-4X | BCE ULTRA MAX | STEEVE-MAX x1000
"""
import logging
from typing import Dict, Any, List

logger = logging.getLogger("saline.nutrient_deficiency")

# Bioavailability factors (% absorbed from soil-available minerals)
BIOAVAILABILITY = {
    "Ca": 0.35, "P": 0.55, "K": 0.80, "Mg": 0.30,
    "Na": 0.90, "S": 0.50, "Zn": 0.20, "Cu": 0.10,
    "Mn": 0.05, "Se": 0.60,
}

# Mineral interaction rules
INTERACTIONS = [
    {"blocker": "Ca", "blocked": "Zn", "ratio_threshold": 300, "severity": "high",
     "description": "Exces de Ca reduit absorption Zn"},
    {"blocker": "K", "blocked": "Mg", "ratio_threshold": 3, "severity": "high",
     "description": "Exces de K reduit absorption Mg"},
    {"blocker": "Ca", "blocked": "P", "low_ratio": 1.0, "high_ratio": 3.0, "optimal_ratio": 1.7,
     "severity": "medium", "description": "Ratio Ca:P hors plage optimale (1.5-2:1)"},
    {"blocker": "Zn", "blocked": "Cu", "ratio_threshold": 15, "severity": "medium",
     "description": "Exces de Zn reduit absorption Cu"},
    {"blocker": "S", "blocked": "Se", "ratio_threshold": 200, "severity": "high",
     "description": "Exces de S reduit absorption Se"},
]


def analyze_deficiencies(soil: Dict, needs: Dict) -> Dict[str, Any]:
    """
    Compare soil mineral availability vs wildlife daily needs.
    Returns coverage %, deficits, and interaction warnings.
    """
    soil_minerals = soil.get("minerals", {})
    daily_needs = needs.get("daily_needs", {})

    coverage = {}
    deficits = []
    critical_deficits = []

    for mineral, need_data in daily_needs.items():
        need_mg = need_data["daily_mg"]
        soil_data = soil_minerals.get(mineral, {"value": 0})
        soil_ppm = soil_data.get("value", 0)

        # Convert soil ppm to estimated available mg (per typical saline lick area)
        bioavail = BIOAVAILABILITY.get(mineral, 0.3)
        # Assume 500g soil intake per day for cervids (typical lick consumption)
        available_mg = round(soil_ppm * 0.5 * bioavail, 2)

        pct = round((available_mg / need_mg * 100) if need_mg > 0 else 100, 1)
        deficit_mg = round(max(0, need_mg - available_mg), 1)

        status = "sufficient" if pct >= 80 else ("marginal" if pct >= 50 else "deficient")
        if pct < 30:
            status = "critical"

        entry = {
            "mineral": mineral,
            "daily_need_mg": need_mg,
            "soil_available_mg": available_mg,
            "coverage_pct": min(pct, 150),
            "deficit_mg": deficit_mg,
            "bioavailability": bioavail,
            "status": status,
        }
        coverage[mineral] = entry

        if status in ("deficient", "critical"):
            deficits.append(entry)
        if status == "critical":
            critical_deficits.append(entry)

    # Analyze mineral interactions
    interactions_detected = _check_interactions(soil_minerals)

    # Overall score
    avg_coverage = sum(c["coverage_pct"] for c in coverage.values()) / len(coverage) if coverage else 0
    overall_status = "optimal" if avg_coverage >= 80 else ("marginal" if avg_coverage >= 50 else "deficient")

    return {
        "coverage": coverage,
        "deficits": deficits,
        "critical_deficits": critical_deficits,
        "interactions": interactions_detected,
        "overall_coverage_pct": round(avg_coverage, 1),
        "overall_status": overall_status,
        "total_minerals_analyzed": len(coverage),
        "deficient_count": len(deficits),
        "critical_count": len(critical_deficits),
    }


def _check_interactions(soil_minerals: Dict) -> List[Dict]:
    detected = []
    for rule in INTERACTIONS:
        blocker_val = soil_minerals.get(rule["blocker"], {}).get("value", 0)
        blocked_val = soil_minerals.get(rule["blocked"], {}).get("value", 0)

        if blocked_val <= 0:
            continue

        if "ratio_threshold" in rule:
            ratio = blocker_val / blocked_val if blocked_val > 0 else 0
            if ratio > rule["ratio_threshold"]:
                detected.append({
                    "type": "antagonism",
                    "blocker": rule["blocker"],
                    "blocked": rule["blocked"],
                    "ratio": round(ratio, 2),
                    "threshold": rule["ratio_threshold"],
                    "severity": rule["severity"],
                    "description": rule["description"],
                    "recommendation": f"Supplementer en {rule['blocked']} pour compenser le blocage par {rule['blocker']}",
                })
        elif "optimal_ratio" in rule:
            ratio = blocker_val / blocked_val if blocked_val > 0 else 0
            if ratio < rule.get("low_ratio", 0) or ratio > rule.get("high_ratio", 999):
                detected.append({
                    "type": "imbalance",
                    "minerals": [rule["blocker"], rule["blocked"]],
                    "ratio": round(ratio, 2),
                    "optimal": rule["optimal_ratio"],
                    "severity": rule["severity"],
                    "description": rule["description"],
                })

    return detected
