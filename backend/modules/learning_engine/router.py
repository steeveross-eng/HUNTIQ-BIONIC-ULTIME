"""
Learning Engine — Unified Router
Consolidation V6: tutorial_engine + formations_engine
Prefixes API originaux preserves pour zero-regression
"""
from fastapi import APIRouter

router = APIRouter()

# Import sub-routers avec prefixes preserves
from modules.tutorial_engine.router import router as tutorial_sub
from modules.formations_engine.router import router as formations_sub

# Les routers originaux gardent leurs prefixes intacts
