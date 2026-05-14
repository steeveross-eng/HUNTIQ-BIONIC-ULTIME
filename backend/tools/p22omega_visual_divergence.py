"""
P22Ω_VISUAL_DIVERGENCE_VALIDATION
═══════════════════════════════════════════════════════════════════
Génère 5 captures PNG (1 par espèce) + 1 grille comparative 5x1
avec zones vitales + corridors V5 NATIFS depuis bundles Redis BSL.
Palette doctrinale TERRITOIRE_OMEGA_PALETTE respectée.

Commandant STEEVE-MAX · BCE-4X ULTIME ABSOLU
"""
import json
import os
import matplotlib
matplotlib.use('Agg')  # headless
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Polygon as MplPolygon
import numpy as np

# ─────────────────────────────────────────────────────────────────
# DOCTRINE PALETTE TERRITOIRE Ω (FROZEN)
# ─────────────────────────────────────────────────────────────────
PALETTE = {
    "zones": "#00A676",           # vert biologique
    "corridors_backbone": "#FFD600",  # jaune intense (veine principale)
    "corridors_subnet": "#F59E0B",    # orange ambré (subnet)
    "corridors_connector": "#06B6D4", # cyan (connector)
    "salines": "#A78BFA",         # lavande
    "hotspots": "#F59E0B",        # orange
    "background": "#0F172A",      # bleu nuit institutionnel
    "grid": "#1F2937",
    "text": "#F8FAFC",
    "title": "#FFD600",           # gold doctrine
}

ZONE_COLORS = {
    "rut":          "#E11D48",   # rouge intense
    "alimentation": "#22C55E",   # vert vif
    "repos":        "#3B82F6",   # bleu repos
    "eau":          "#0EA5E9",   # cyan eau
    "thermique":    "#F59E0B",   # orange thermique
}

OUTPUT_DIR = "/app/memory/audit_provenance/visual_divergence"
os.makedirs(OUTPUT_DIR, exist_ok=True)

SPECIES_LIST = ["chevreuil", "orignal", "ours_noir", "dindon_sauvage", "coyote"]
SPECIES_LABELS = {
    "chevreuil":      "CHEVREUIL · Odocoileus virginianus",
    "orignal":        "ORIGNAL · Alces alces",
    "ours_noir":      "OURS NOIR · Ursus americanus",
    "dindon_sauvage": "DINDON SAUVAGE · Meleagris gallopavo (HALT MFFP > 47°N)",
    "coyote":         "COYOTE · Canis latrans",
}

BSL_LAT, BSL_LON = 48.206657, -68.382422
VIEW_RADIUS = 0.012  # ~1.3 km radius


def normalize_points(pts):
    """Extrait (lat, lon) depuis divers formats Leaflet/GeoJSON."""
    out = []
    for p in pts:
        if isinstance(p, dict):
            lat = p.get("lat") or p.get("latitude")
            lon = p.get("lng") or p.get("lon") or p.get("longitude")
            if lat is not None and lon is not None:
                out.append((float(lat), float(lon)))
        elif isinstance(p, (list, tuple)) and len(p) >= 2:
            out.append((float(p[0]), float(p[1])))
    return out


def draw_species(ax, bundle, species, title_suffix=""):
    """Dessine zones + corridors + salines + hotspots pour une espèce."""
    ax.set_facecolor(PALETTE["background"])
    ax.set_xlim(BSL_LON - VIEW_RADIUS, BSL_LON + VIEW_RADIUS)
    ax.set_ylim(BSL_LAT - VIEW_RADIUS, BSL_LAT + VIEW_RADIUS)
    ax.set_aspect('equal')
    ax.grid(True, color=PALETTE["grid"], linestyle=':', alpha=0.4)
    ax.tick_params(colors=PALETTE["text"], labelsize=7)
    for spine in ax.spines.values():
        spine.set_color(PALETTE["grid"])

    # ZONES (polygones par type, couleur ZONE_COLORS)
    zones = bundle.get("zones", []) or []
    zone_labels_drawn = set()
    for z in zones:
        if z.get("excluded"):
            continue
        polygon = z.get("polygon") or []
        pts = normalize_points(polygon)
        if len(pts) < 3:
            continue
        ztype = z.get("type", "?")
        color = ZONE_COLORS.get(ztype, "#9CA3AF")
        # Matplotlib veut (x=lon, y=lat)
        verts = [(lon, lat) for (lat, lon) in pts]
        poly = MplPolygon(verts, closed=True, facecolor=color, edgecolor=color,
                          alpha=0.20, linewidth=1.2)
        ax.add_patch(poly)
        # Centre label
        if ztype not in zone_labels_drawn:
            cx = np.mean([v[0] for v in verts])
            cy = np.mean([v[1] for v in verts])
            score = z.get("score", 0)
            ax.annotate(f"{ztype}\nscore={score:.0f}", (cx, cy),
                        color=color, fontsize=6.5, ha='center', va='center',
                        weight='bold',
                        bbox=dict(boxstyle='round,pad=0.2', fc=PALETTE["background"],
                                  ec=color, alpha=0.85, lw=0.7))
            zone_labels_drawn.add(ztype)

    # CORRIDORS (lignes par hiérarchie)
    corridors = bundle.get("corridors", []) or []
    for c in corridors:
        path = c.get("path") or c.get("coords") or c.get("coordinates") or []
        pts = normalize_points(path)
        if len(pts) < 2:
            continue
        hier = c.get("hierarchy") or c.get("subnet_role") or "subnet"
        if "principale" in str(hier).lower() or "backbone" in str(hier).lower():
            color = PALETTE["corridors_backbone"]
            width = 2.5
            zorder = 4
        elif "connector" in str(hier).lower():
            color = PALETTE["corridors_connector"]
            width = 1.3
            zorder = 3
        else:
            color = PALETTE["corridors_subnet"]
            width = 1.6
            zorder = 3
        xs = [lon for (lat, lon) in pts]
        ys = [lat for (lat, lon) in pts]
        ax.plot(xs, ys, color=color, linewidth=width, alpha=0.92,
                zorder=zorder, solid_capstyle='round')

    # SALINES (markers triangulaires)
    for sal in (bundle.get("salines") or [])[:20]:
        if isinstance(sal, dict):
            lat = sal.get("lat") or (sal.get("center") or {}).get("lat")
            lon = sal.get("lng") or (sal.get("center") or {}).get("lng") or (sal.get("center") or {}).get("lon")
            if lat is not None and lon is not None:
                ax.plot(lon, lat, marker='^', color=PALETTE["salines"], markersize=6,
                        markeredgecolor='white', markeredgewidth=0.5, zorder=5)

    # HOTSPOTS (markers circulaires intensité)
    for hs in (bundle.get("hotspots") or [])[:15]:
        if isinstance(hs, dict):
            lat = hs.get("lat") or (hs.get("center") or {}).get("lat")
            lon = hs.get("lng") or (hs.get("center") or {}).get("lng") or (hs.get("center") or {}).get("lon")
            if lat is not None and lon is not None:
                intensity = hs.get("intensity", 0.5) or 0.5
                size = 3 + intensity * 6
                ax.plot(lon, lat, marker='o', color=PALETTE["hotspots"],
                        markersize=size, alpha=0.7, markeredgecolor='white',
                        markeredgewidth=0.4, zorder=6)

    # WAYPOINT BSL
    ax.plot(BSL_LON, BSL_LAT, marker='*', color='#FFFFFF', markersize=18,
            markeredgecolor='#FFD600', markeredgewidth=1.5, zorder=10)

    # Titre + metadata
    n_corr = len(corridors)
    n_zones = sum(1 for z in zones if not z.get("excluded"))
    n_hs = len(bundle.get("hotspots") or [])
    n_sal = len(bundle.get("salines") or [])
    halt = bundle.get("bio_presence_mask_halt", False)
    cache = bundle.get("cache", "?")
    v5 = bundle.get("p22sigma_v5_bundle_rewire", {}) or {}
    v5_ok = "V5 NATIF" if v5.get("applied") and not v5.get("v30_remap_fallback_applied") else "fallback"

    title = SPECIES_LABELS.get(species, species)
    if halt:
        meta = f"⚠ HALT MFFP · zones={n_zones} (audit écologique)"
    else:
        meta = f"corridors={n_corr} · zones={n_zones} · hotspots={n_hs} · salines={n_sal} · {v5_ok} · cache={cache}"

    ax.set_title(f"{title}\n{meta}{title_suffix}",
                 color=PALETTE["title"], fontsize=9, weight='bold', pad=8)
    ax.set_xlabel("longitude", color=PALETTE["text"], fontsize=7)
    ax.set_ylabel("latitude", color=PALETTE["text"], fontsize=7)


# ─────────────────────────────────────────────────────────────────
# 1. CAPTURES INDIVIDUELLES
# ─────────────────────────────────────────────────────────────────
print("═══ P22Ω_VISUAL_DIVERGENCE_VALIDATION — Rendu Matplotlib ═══")
print()

bundles = {}
for sp in SPECIES_LIST:
    path = f"/tmp/viz_{sp}.json"
    if not os.path.exists(path):
        print(f"  ✗ Manquant : {path}")
        continue
    try:
        bundles[sp] = json.load(open(path))
    except Exception as e:
        print(f"  ✗ Parse error {sp}: {e}")
        continue

    # Capture individuelle 1000x1000
    fig, ax = plt.subplots(figsize=(10, 10), dpi=100)
    fig.patch.set_facecolor(PALETTE["background"])
    draw_species(ax, bundles[sp], sp)
    out_path = f"{OUTPUT_DIR}/divergence_bsl_{sp}.png"
    plt.savefig(out_path, facecolor=PALETTE["background"], dpi=100, bbox_inches='tight')
    plt.close(fig)
    print(f"  ✓ {out_path}  ({os.path.getsize(out_path)} bytes)")

# ─────────────────────────────────────────────────────────────────
# 2. GRILLE COMPARATIVE 5x1
# ─────────────────────────────────────────────────────────────────
print()
print("Génération grille comparative 5×1 ...")
fig, axes = plt.subplots(1, 5, figsize=(40, 9), dpi=80)
fig.patch.set_facecolor(PALETTE["background"])
for i, sp in enumerate(SPECIES_LIST):
    if sp in bundles:
        draw_species(axes[i], bundles[sp], sp)
    else:
        axes[i].text(0.5, 0.5, f"{sp}\nDONNÉES MANQUANTES", color='red',
                     ha='center', va='center', transform=axes[i].transAxes)
        axes[i].set_facecolor(PALETTE["background"])

fig.suptitle("P22Ω_VISUAL_DIVERGENCE_VALIDATION · BSL (48.207, -68.382) · mois 10\nDOCTRINE BIOLOGIQUE STRICTE — TERRITOIRE Ω",
             color=PALETTE["title"], fontsize=14, weight='bold', y=0.98)
plt.tight_layout(rect=[0, 0, 1, 0.95])
grid_path = f"{OUTPUT_DIR}/divergence_bsl_grid_5x1.png"
plt.savefig(grid_path, facecolor=PALETTE["background"], dpi=80, bbox_inches='tight')
plt.close(fig)
print(f"  ✓ {grid_path}  ({os.path.getsize(grid_path)} bytes)")

# ─────────────────────────────────────────────────────────────────
# 3. RAPPORT DE METRIQUES PAR ESPECE
# ─────────────────────────────────────────────────────────────────
print()
print("═══ MÉTRIQUES PAR ESPÈCE ═══")
for sp, b in bundles.items():
    zones = b.get("zones", [])
    corridors = b.get("corridors", [])
    halt = b.get("bio_presence_mask_halt", False)
    print(f"  {sp:18s}: corridors={len(corridors):2d} zones={len(zones):2d} halt={halt} ", end="")
    if zones:
        scores = {z.get("type"): z.get("score") for z in zones if not z.get("excluded")}
        print(f" scores={scores}")
    else:
        print()

print()
print("═══ FIN P22Ω_VISUAL_DIVERGENCE_VALIDATION ═══")
