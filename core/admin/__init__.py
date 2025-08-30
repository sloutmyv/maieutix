from .cabinet import CabinetAdmin
from .sagefemme import SageFemmeAdmin
from .periode_activite import PeriodeActiviteAdmin, PeriodeActiviteInline
from .acte import ActeAdmin, TarifPeriodeAdmin
from .cadre_exercice import CadreExerciceAdmin
from .prestation import PrestationAdmin

__all__ = ['CabinetAdmin', 'SageFemmeAdmin', 'PeriodeActiviteAdmin', 'PeriodeActiviteInline', 'ActeAdmin', 'TarifPeriodeAdmin', 'CadreExerciceAdmin', 'PrestationAdmin']