"""
Ads Engine — Unified Router
Consolidation V6: affiliate_ads_engine + ad_spaces_engine
Prefixes API originaux preserves pour zero-regression
"""
from fastapi import APIRouter

router = APIRouter()

# Import sub-routers avec prefixes preserves
from modules.affiliate_ads_engine.router import router as affiliate_ads_sub
from modules.ad_spaces_engine.router import router as ad_spaces_sub

# Inclure les sous-routers (prefixes deja definis dans les routers originaux)
# Les routers originaux gardent leurs prefixes intacts
