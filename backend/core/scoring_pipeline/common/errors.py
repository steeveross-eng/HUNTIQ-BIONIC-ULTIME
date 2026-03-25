"""
CORE Scoring Pipeline — Modele d'erreurs normalise
======================================================
Directive x3205. Hierarchie d'exceptions CORE pour tous les moteurs.
BCE-4X: Remplace les exceptions ad hoc par un modele trace et documente.
"""


class COREError(Exception):
    """Erreur de base du pipeline CORE.
    Toutes les exceptions CORE heritent de cette classe.
    Attributs:
        code: Code d'erreur unique (ex: "CORE-001")
        engine: Nom du moteur source
        detail: Description detaillee
    """
    def __init__(self, message: str, code: str = "CORE-000", engine: str = "CORE", detail: str = ""):
        self.code = code
        self.engine = engine
        self.detail = detail
        super().__init__(f"[{code}][{engine}] {message}")


class COREValidationError(COREError):
    """Erreur de validation des donnees d'entree.
    Cas: coordonnees invalides, espece inconnue, mois hors plage.
    """
    def __init__(self, message: str, engine: str = "CORE", detail: str = ""):
        super().__init__(message, code="CORE-VAL", engine=engine, detail=detail)


class CORESpeciesError(COREError):
    """Erreur liee a une espece non reconnue.
    Cas: espece non supportee par un moteur specifique.
    """
    def __init__(self, species: str, engine: str = "CORE"):
        super().__init__(
            f"Espece non reconnue: {species}",
            code="CORE-SPE", engine=engine,
            detail=f"Especes valides: CERF, ORIGNAL, OURS, DINDON, WAPITI"
        )


class COREGridError(COREError):
    """Erreur liee a la generation ou au traitement de la grille.
    Cas: taille invalide, cellule hors limites.
    """
    def __init__(self, message: str, engine: str = "CORE", detail: str = ""):
        super().__init__(message, code="CORE-GRID", engine=engine, detail=detail)


class COREBarrierError(COREError):
    """Erreur de barriere ecologique.
    Cas: tentative de traverser une barriere absolue (eau, pente).
    """
    def __init__(self, barrier_type: str, engine: str = "CORRIDORS-V10"):
        super().__init__(
            f"Barriere absolue rencontree: {barrier_type}",
            code="CORE-BAR", engine=engine,
            detail=f"Type: {barrier_type} (eau=infini, pente>max=infini)"
        )


class COREPathError(COREError):
    """Erreur de pathfinding.
    Cas: aucun chemin trouve entre deux zones.
    """
    def __init__(self, reason: str, engine: str = "CORRIDORS-V10"):
        super().__init__(
            f"Pathfinding echoue: {reason}",
            code="CORE-PATH", engine=engine,
            detail=reason
        )


class COREClassificationError(COREError):
    """Erreur de classification.
    Cas: configuration de classification inconnue.
    """
    def __init__(self, message: str, engine: str = "CORE"):
        super().__init__(message, code="CORE-CLS", engine=engine)


class COREDependencyError(COREError):
    """Erreur de dependance inter-moteur.
    Cas: module requis non disponible.
    """
    def __init__(self, source: str, target: str):
        super().__init__(
            f"Dependance non resolue: {source} -> {target}",
            code="CORE-DEP", engine=source,
            detail=f"Le module {target} est requis par {source}"
        )
