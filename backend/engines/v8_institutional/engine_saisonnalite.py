"""
ENGINE 12 — SAISONNALITE
PILIER: COMPORTEMENT HUMAIN
SOURCES FUSIONNEES: temporal_v1, weather_v3 (saisonnier), seasonal_metabolism_engine
"""
import math

SEASONS = {1: "hiver", 2: "hiver", 3: "printemps", 4: "printemps", 5: "printemps", 6: "ete", 7: "ete", 8: "ete", 9: "automne", 10: "automne", 11: "automne", 12: "hiver"}
ACTIVITY = {"hiver": {"repos": 0.7, "alimentation": 0.5, "deplacement": 0.3}, "printemps": {"repos": 0.4, "alimentation": 0.8, "deplacement": 0.6}, "ete": {"repos": 0.5, "alimentation": 0.7, "deplacement": 0.5}, "automne": {"repos": 0.3, "alimentation": 0.6, "deplacement": 0.8}}

def compute_saisonnalite(month, species, hour):
    saison = SEASONS.get(month, "automne")
    activity = ACTIVITY.get(saison, ACTIVITY["automne"])
    circadian = 0.8 + 0.4 * abs(math.sin((hour - 6) / 24 * 2 * math.pi))
    rut = month in [9, 10, 11] and species in ["cerf", "orignal", "wapiti"]
    return {"saison": saison, "month": month, "activity_profile": activity, "circadian_factor": round(circadian, 2), "rut_active": rut, "score_saisonnier": round((activity["alimentation"] * 40 + activity["deplacement"] * 30 + circadian * 30) * (1.2 if rut else 1.0), 1)}
