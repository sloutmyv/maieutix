from .cabinet import CabinetAdmin
from .sagefemme import SageFemmeAdmin
from .periode_activite import PeriodeActiviteAdmin, PeriodeActiviteInline
from .acte import ActeAdmin, TarifPeriodeAdmin
from .cadre_exercice import CadreExerciceAdmin
from .prestation import PrestationAdmin
from .condition_paiement import ConditionPaiementAdmin
from .caisse import CaisseAdmin
from .patient import PatientAdmin
from .antecedents import AntecedentsAdmin, FrottisCVAdmin
from .consultation_gynecologique import ConsultationGynecologiqueAdmin

__all__ = ['CabinetAdmin', 'SageFemmeAdmin', 'PeriodeActiviteAdmin', 'PeriodeActiviteInline', 'ActeAdmin', 'TarifPeriodeAdmin', 'CadreExerciceAdmin', 'PrestationAdmin', 'ConditionPaiementAdmin', 'CaisseAdmin', 'PatientAdmin', 'AntecedentsAdmin', 'FrottisCVAdmin', 'ConsultationGynecologiqueAdmin']