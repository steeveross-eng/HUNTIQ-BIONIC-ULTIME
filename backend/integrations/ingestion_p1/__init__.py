"""
P22ΩΩ_NDVI_LIDAR_P1_STRUCTURAL+_Ω — Module integrations.ingestion_p1
═══════════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · 2026-02-20 · BCE-4X ULTIME ABSOLU
Verrou Phase III : MAINTENU · Mode P1_STRUCTURAL+ · NE TÉLÉCHARGE RIEN.

Doctrine
--------
Conteneur d'intégrations ingestion P1 RÉELLES (anti-générique strict).

Chaque client est :
  - **CODE-READY** : implémentation officielle vendor (earthaccess, sentinelhub,
    requests sur API NRCan/MFFP)
  - **INERTE** par défaut : refuse de télécharger tant que credentials absents
    ou flag `INGESTION_P1_ARMED=1` non posé par le Commandant
  - **anti-générique strict** : aucune synthèse, aucune interpolation, aucun
    fallback de données simulées

Clients exposés :
  - nasa_hls_client.NasaHlsClient
  - esa_sentinel2_client.EsaSentinel2Client
  - nrcan_hrdem_client.NrcanHrdemClient
  - mffp_foret_ouverte_client.MffpForetOuverteClient
"""
INGESTION_P1_DOCTRINE = "P22ΩΩ_NDVI_LIDAR_P1_STRUCTURAL+_Ω"
INGESTION_P1_VERSION = "V1.0-CODE-READY-AWAITING-CREDENTIALS"

__all__ = [
    "INGESTION_P1_DOCTRINE",
    "INGESTION_P1_VERSION",
]
