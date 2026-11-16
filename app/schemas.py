from enum import Enum

from pydantic import BaseModel, Field
from pydantic import BaseModel, ConfigDict, Field


class Priorite(str, Enum):
    BASSE = "Basse"
    MOYENNE = "Moyenne"
    ELEVEE = "Élevée"
    CRITIQUE = "Critique"


class Status(str, Enum):
    OUVERT  = "Ouvert"
    EN_COURS = "En cours"
    RESOLU = "Résolu"


class IncidentCreation(BaseModel):
    titre: str = Field(min_length=3, max_length=120)
    service: str = Field(min_length=2, max_length=80)
    priorite: Priorite
    description: str = Field(min_length=5)
    status: Status = Status.OUVERT


class IncidentReponse(IncidentCreation):
    id: int

    model_config = ConfigDict(from_attributes=True)


class IncidentMiseAJour(BaseModel):
    priorite: Priorite | None = None
    status: Status | None = None
    description: str | None = Field(default=None, min_length=5)