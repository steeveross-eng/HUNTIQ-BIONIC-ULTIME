"""
BCE-4X — Wind Model Provider Abstraction Layer
================================================
STEEVE-MAX P0 — Architecture provider-agnostique

Couche d'abstraction pour les fournisseurs de champs de vent.
Le frontend consomme un format interne normalisé, indépendant du fournisseur.

Providers supportés:
  - V1: Open-Meteo (GFS/ICON, gratuit, 0.25° résolution)
  - Futur: modèle régional, payant, interne, etc.
"""
import httpx
import logging
import math
from datetime import datetime, timezone
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class WindGridData:
    """Format interne normalisé du champ de vent griddé."""

    def __init__(self, provider, model, resolution_deg, timestamp,
                 bounds, lats, lngs, u_grid, v_grid, speed_grid, gust_grid):
        self.provider = provider
        self.model = model
        self.resolution_deg = resolution_deg
        self.timestamp = timestamp
        self.bounds = bounds
        self.lats = lats
        self.lngs = lngs
        self.u_grid = u_grid
        self.v_grid = v_grid
        self.speed_grid = speed_grid
        self.gust_grid = gust_grid

    def to_dict(self):
        return {
            "provider": self.provider,
            "model": self.model,
            "resolution_deg": self.resolution_deg,
            "timestamp": self.timestamp,
            "bounds": self.bounds,
            "grid": {
                "rows": len(self.lats),
                "cols": len(self.lngs),
                "lats": self.lats,
                "lngs": self.lngs,
                "u": self.u_grid,
                "v": self.v_grid,
                "speed": self.speed_grid,
                "gusts": self.gust_grid,
            }
        }


class WindModelProvider(ABC):
    """Interface abstraite pour les fournisseurs de champ de vent."""

    @abstractmethod
    async def fetch_wind_grid(self, south, north, west, east,
                              resolution_deg) -> WindGridData:
        pass

    @abstractmethod
    def provider_name(self) -> str:
        pass


class OpenMeteoWindProvider(WindModelProvider):
    """
    Provider V1: Open-Meteo Forecast API
    - Modèle: GFS (global) / ICON (Europe)
    - Résolution native: 0.25° (~25km)
    - Fréquence: mise à jour ~3h
    - Gratuit, sans clé API
    """

    FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

    def provider_name(self) -> str:
        return "open-meteo"

    async def fetch_wind_grid(self, south, north, west, east,
                              resolution_deg=0.25) -> WindGridData:
        # Construire la grille de points
        lats = []
        lat = south
        while lat <= north + resolution_deg * 0.01:
            lats.append(round(lat, 4))
            lat += resolution_deg

        lngs = []
        lng = west
        while lng <= east + resolution_deg * 0.01:
            lngs.append(round(lng, 4))
            lng += resolution_deg

        # Limiter à 20x20 = 400 points max pour performance
        max_per_dim = 20
        if len(lats) > max_per_dim:
            step = len(lats) / max_per_dim
            lats = [lats[int(i * step)] for i in range(max_per_dim)]
        if len(lngs) > max_per_dim:
            step = len(lngs) / max_per_dim
            lngs = [lngs[int(i * step)] for i in range(max_per_dim)]

        if len(lats) < 2:
            lats = [south, north]
        if len(lngs) < 2:
            lngs = [west, east]

        # Aplatir les coordonnées pour l'appel API
        all_lats = []
        all_lngs = []
        for lat_val in lats:
            for lng_val in lngs:
                all_lats.append(lat_val)
                all_lngs.append(lng_val)

        lat_str = ",".join(str(l) for l in all_lats)
        lng_str = ",".join(str(l) for l in all_lngs)

        params = {
            "latitude": lat_str,
            "longitude": lng_str,
            "current": "wind_speed_10m,wind_direction_10m,wind_gusts_10m",
            "wind_speed_unit": "kmh",
            "timezone": "auto",
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(self.FORECAST_URL, params=params)
            response.raise_for_status()
            data = response.json()

        # Parser la réponse — Open-Meteo retourne un tableau si multi-locations
        rows = len(lats)
        cols = len(lngs)

        u_grid = [[0.0] * cols for _ in range(rows)]
        v_grid = [[0.0] * cols for _ in range(rows)]
        speed_grid = [[0.0] * cols for _ in range(rows)]
        gust_grid = [[0.0] * cols for _ in range(rows)]

        # Si multi-locations, data est une liste; sinon un objet
        locations = data if isinstance(data, list) else [data]

        for idx, loc in enumerate(locations):
            row = idx // cols
            col = idx % cols
            if row >= rows:
                break

            current_data = loc.get("current", {})
            speed_kmh = current_data.get("wind_speed_10m", 0) or 0
            direction_deg = current_data.get("wind_direction_10m", 0) or 0
            gusts_kmh = current_data.get("wind_gusts_10m", 0) or 0

            # Convertir direction + vitesse en composantes u/v (m/s)
            speed_ms = speed_kmh / 3.6
            dir_rad = math.radians(direction_deg)
            # Vent FROM direction_deg → u/v en météo standard
            # u = composante est-ouest (positif = vers est)
            # v = composante nord-sud (positif = vers nord)
            # Vent vient DE dir → se dirige VERS opposé
            u = -speed_ms * math.sin(dir_rad)
            v = -speed_ms * math.cos(dir_rad)

            u_grid[row][col] = round(u, 3)
            v_grid[row][col] = round(v, 3)
            speed_grid[row][col] = round(speed_kmh, 1)
            gust_grid[row][col] = round(gusts_kmh, 1)

        timestamp = datetime.now(timezone.utc).isoformat()

        return WindGridData(
            provider="open-meteo",
            model="gfs-global",
            resolution_deg=resolution_deg,
            timestamp=timestamp,
            bounds={"south": south, "north": north, "west": west, "east": east},
            lats=lats,
            lngs=lngs,
            u_grid=u_grid,
            v_grid=v_grid,
            speed_grid=speed_grid,
            gust_grid=gust_grid,
        )


# Registre des providers
_PROVIDERS = {
    "open-meteo": OpenMeteoWindProvider,
}

_active_provider = None


def get_wind_provider(name="open-meteo") -> WindModelProvider:
    """Obtenir le provider de vent actif."""
    global _active_provider
    if _active_provider is None or _active_provider.provider_name() != name:
        cls = _PROVIDERS.get(name)
        if not cls:
            raise ValueError(f"Provider inconnu: {name}. Disponibles: {list(_PROVIDERS.keys())}")
        _active_provider = cls()
    return _active_provider
