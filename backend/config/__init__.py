"""BIONIC V6 - Configuration Module

P22ΩΩ_QUALITY_GROUPE_A · 2026-05-18 · STEEVE-MAX
Wildcard import remplacé par imports explicites pour clarté du namespace.
"""
from .settings import (
    ARCHITECTURE_VERSION,
    ARCHITECTURE_CREATED,
    CORE_ENGINES,
    BUSINESS_ENGINES,
    ADVANCED_ENGINES,
    SPECIAL_MODULES,
    DATA_LAYERS,
    ALL_MODULES,
    LOGGING_CONFIG,
    get_module_info,
)

__all__ = [
    "ARCHITECTURE_VERSION",
    "ARCHITECTURE_CREATED",
    "CORE_ENGINES",
    "BUSINESS_ENGINES",
    "ADVANCED_ENGINES",
    "SPECIAL_MODULES",
    "DATA_LAYERS",
    "ALL_MODULES",
    "LOGGING_CONFIG",
    "get_module_info",
]
