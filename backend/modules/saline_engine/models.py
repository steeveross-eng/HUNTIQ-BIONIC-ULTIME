"""
SALINE INTELLIGENCE ULTRA — Pydantic Models
Conformite: GOLDEN-BCE-4X | BCE ULTRA MAX | STEEVE-MAX x1000
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class SpeciesEnum(str, Enum):
    ORIGNAL = "orignal"
    CHEVREUIL = "chevreuil"
    OURS_NOIR = "ours_noir"
    DINDON_SAUVAGE = "dindon_sauvage"


class SexEnum(str, Enum):
    MALE = "male"
    FEMALE = "female"


class AgeEnum(str, Enum):
    JUVENILE = "juvenile"
    ADULT = "adult"
    SENIOR = "senior"


class SeasonEnum(str, Enum):
    PRINTEMPS = "printemps"
    ETE = "ete"
    PRE_RUT = "pre_rut"
    RUT = "rut"
    POST_RUT = "post_rut"
    HIVER = "hiver"
    AUTOMNE = "automne"


class SalineAnalysisRequest(BaseModel):
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lng: float = Field(..., ge=-180, le=180, description="Longitude")
    species: SpeciesEnum = SpeciesEnum.ORIGNAL
    sex: SexEnum = SexEnum.MALE
    age: AgeEnum = AgeEnum.ADULT
    month: int = Field(10, ge=1, le=12, description="Mois (1-12)")
    season: SeasonEnum = SeasonEnum.AUTOMNE


class SoilRequest(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    season: SeasonEnum = SeasonEnum.AUTOMNE


class NutrientRequest(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    species: SpeciesEnum = SpeciesEnum.ORIGNAL
    season: SeasonEnum = SeasonEnum.AUTOMNE
    sex: SexEnum = SexEnum.MALE
    age: AgeEnum = AgeEnum.ADULT


class VegetationRequest(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    month: int = Field(10, ge=1, le=12)


class HydrologyRequest(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    season: SeasonEnum = SeasonEnum.AUTOMNE


class MetabolismRequest(BaseModel):
    month: int = Field(10, ge=1, le=12)
    species: SpeciesEnum = SpeciesEnum.ORIGNAL
    sex: SexEnum = SexEnum.MALE


class HealthResponse(BaseModel):
    status: str
    engine: str
    version: str
    engines_count: int
    message: str
