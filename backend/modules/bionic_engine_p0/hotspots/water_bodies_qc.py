"""
BIONIC V6 — Base de donnees eau embarquee Quebec
==================================================
Lacs et cours d'eau majeurs du Quebec avec coordonnees centre + rayon.
Source: Donnees geographiques du MELCCFP / Ressources naturelles Canada.

Utilise comme LANDMASK pour exclure les hotspots sur l'eau.
Chaque entree: (nom, lat_centre, lng_centre, rayon_m)

Conformite: BCE-4X GOLDEN V6+ | STEEVE-MAX x7200
"""

# Format: (nom, lat, lng, rayon_metres)
# Rayon = approximation du demi-axe principal du lac

MAJOR_WATER_BODIES_QC = [
    # ═══════════════════════════════════════
    # LACS MAJEURS DU QUEBEC
    # ═══════════════════════════════════════
    
    # Saguenay-Lac-Saint-Jean
    ("Lac Saint-Jean", 48.57, -72.06, 18000),
    ("Riviere Saguenay (embouchure)", 48.35, -70.87, 3000),
    ("Riviere Saguenay (fjord)", 48.33, -70.20, 2500),
    ("Riviere Saguenay (milieu)", 48.42, -71.05, 2000),
    
    # Laurentides
    ("Lac des Seize Iles", 46.07, -74.45, 800),
    ("Lac Tremblant", 46.22, -74.60, 2500),
    ("Lac Nominingue", 46.38, -75.07, 1500),
    ("Lac Archambault", 46.30, -74.17, 1200),
    ("Lac Ouareau", 46.30, -74.17, 1000),
    ("Reservoir Taureau", 46.68, -73.55, 5000),
    ("Lac Masson", 46.05, -74.17, 800),
    
    # Outaouais
    ("Reservoir Baskatong", 46.75, -75.78, 8000),
    ("Reservoir Cabonga", 47.28, -76.57, 5000),
    ("Lac des Trente et Un Milles", 46.22, -75.78, 3000),
    ("Reservoir Dozois", 47.50, -77.15, 6000),
    
    # Lanaudiere
    ("Reservoir Taureau (Lanaudiere)", 46.70, -73.55, 5000),
    ("Lac Archambault (Lanaudiere)", 46.30, -74.17, 1000),
    
    # Mauricie
    ("Lac Saint-Pierre", 46.20, -72.82, 8000),
    ("Reservoir Gouin", 48.35, -74.70, 15000),
    ("Lac Wayagamac", 46.62, -72.78, 1500),
    ("Reservoir Blanc", 47.33, -73.77, 3000),
    ("Reservoir Manouane", 47.75, -74.20, 4000),
    
    # Estrie
    ("Lac Megantic", 45.55, -70.87, 3500),
    ("Lac Memphremagog", 45.15, -72.22, 4000),
    ("Lac Massawippi", 45.22, -71.95, 2000),
    ("Lac Aylmer", 45.83, -71.40, 2500),
    
    # Capitale-Nationale
    ("Lac Saint-Joseph", 46.92, -71.63, 2000),
    ("Lac Beauport", 46.93, -71.28, 800),
    ("Lac Jacques-Cartier", 47.37, -71.30, 2000),
    
    # Chaudiere-Appalaches
    ("Lac Etchemin", 46.45, -70.70, 1000),
    
    # Bas-Saint-Laurent
    ("Lac Temiscouata", 47.67, -68.75, 5000),
    ("Lac Pohenegamook", 47.45, -69.22, 1500),
    
    # Abitibi-Temiscamingue
    ("Lac Abitibi (partie QC)", 48.60, -79.40, 12000),
    ("Lac Kipawa", 47.10, -78.90, 5000),
    ("Lac Simard", 48.42, -79.10, 3000),
    ("Lac Preissac", 48.33, -78.28, 3000),
    ("Reservoir Decelles", 47.50, -78.50, 5000),
    
    # Cote-Nord
    ("Reservoir Manicouagan", 51.40, -68.65, 30000),
    ("Reservoir Daniel-Johnson", 51.00, -68.00, 8000),
    ("Lac Walker", 49.80, -67.20, 2000),
    
    # Gaspesie
    ("Lac Matapedia", 47.92, -67.15, 2500),
    ("Lac Cascapedia", 48.25, -66.20, 1500),
    
    # ═══════════════════════════════════════
    # FLEUVES ET RIVIERES MAJEURS (zones larges)
    # ═══════════════════════════════════════
    ("Fleuve Saint-Laurent (Quebec-Levis)", 46.82, -71.22, 2500),
    ("Fleuve Saint-Laurent (Trois-Rivieres)", 46.35, -72.55, 3000),
    ("Fleuve Saint-Laurent (Montreal)", 45.52, -73.55, 3000),
    ("Fleuve Saint-Laurent (Sorel)", 46.05, -73.12, 4000),
    ("Riviere des Outaouais (Hull)", 45.43, -75.72, 1500),
    ("Riviere des Outaouais (Thurso)", 45.60, -75.25, 1200),
    ("Riviere Saint-Maurice (embouchure)", 46.38, -72.53, 1000),
    ("Riviere Richelieu (Chambly)", 45.45, -73.28, 800),
    
    # ═══════════════════════════════════════
    # BAIES ET ZONES COTIERES
    # ═══════════════════════════════════════
    ("Baie des Chaleurs (centre)", 48.10, -65.80, 10000),
    ("Baie James (sud)", 51.50, -79.50, 25000),
    ("Golfe Saint-Laurent (Sept-Iles)", 50.20, -66.38, 15000),
]


# ═══════════════════════════════════════
# ZONES URBAINES MAJEURES (penalite scoring)
# ═══════════════════════════════════════
MAJOR_URBAN_ZONES_QC = [
    ("Montreal", 45.50, -73.57, 15000),
    ("Quebec", 46.82, -71.22, 8000),
    ("Laval", 45.57, -73.75, 8000),
    ("Gatineau", 45.48, -75.70, 7000),
    ("Sherbrooke", 45.40, -71.90, 5000),
    ("Trois-Rivieres", 46.35, -72.55, 4000),
    ("Saguenay", 48.43, -71.07, 5000),
    ("Levis", 46.80, -71.18, 4000),
    ("Drummondville", 45.88, -72.48, 3000),
    ("Saint-Jean-sur-Richelieu", 45.30, -73.27, 3000),
    ("Rimouski", 48.45, -68.52, 3000),
]
