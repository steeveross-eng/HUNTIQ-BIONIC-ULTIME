"""
ENGINE_WILDLIFE_BEHAVIOR_Ω — Package squelette X199-PREPARATOIRE
===========================================================
Phase     : PHASE_XI_SUPRA_VALIDATION_ENGINES_Ω
Version   : X199-AMENDEMENT-ABSOLU
Commandant: STEEVE-MAX
Category  : etendu
Role      : Comportements animaliers saisonniers, locomotion espèces (cerf, orignal, wapiti, ours, dindon)

FEATURE FLAG : OFF (aucune activation sans ordre X200).
Ne modifie ni V30 ni le rendu.
"""
from .router import router, FEATURE_FLAG_ACTIVE

__all__ = ["router", "FEATURE_FLAG_ACTIVE"]
