from fastapi import Depends, FastAPI, status
from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, engine
from app.model import Incident
from app.schemas import IncidentCreation, IncidentReponse
from fastapi import Depends, FastAPI, HTTPException, status

# Crée les tables au démarrage si elles n'existent pas.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de suivi d'incidents",
    description="API professionnelle de suivi d'incidents.",
    version="1.0.0",
)


# Le gestionnaire de session SQLAlchemy est utilisé par FastAPI via Depends.
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

def incident_to_response(incident):
    return IncidentReponse(
        id=incident.id,
        titre=incident.titre,
        service=incident.service,
        priorite=incident.priorite,
        status=incident.status,
        description=incident.description,
    )


@app.get("/")
def Bienvenue():
    return {"message": "API de suivi d'incidents. Bienvenue!"}


@app.get("/etats")
def verification_etats():
    return {"status": "ok"}


@app.post(
    "/incidents",
    response_model=IncidentReponse,
    status_code=status.HTTP_201_CREATED,
)
def creation_incident(incident: IncidentCreation, db: Session = Depends(get_db)):
    # On crée un objet SQLAlchemy, pas un objet Pydantic de réponse.
    # Le modèle `Incident` correspond à la table SQLite.
    incident_db = Incident(**incident.model_dump())

    # Ajout en base de données puis sauvegarde.
    db.add(incident_db)
    db.commit()
    db.refresh(incident_db)

    # Conversion du modèle SQLAlchemy vers le schéma de sortie FastAPI.
    return IncidentReponse(
        id=incident_db.id,
        titre=incident_db.titre,
        service=incident_db.service,
        priorite=incident_db.priorite,
        description=incident_db.description,
        status=incident_db.status,
    )

@app.get("/incidents", response_model=list[IncidentReponse])
def get_incidents(
    status: str | None = None,
    priorite: str | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(Incident)

    if status is not None:
        query = query.filter(Incident.status == status)

    if priorite is not None:
        query = query.filter(Incident.priorite == priorite)

    incidents = query.all()

    return [
        incident_to_response(incident)
        for incident in incidents
    ]


@app.get("/incidents/{incident_id}", response_model=IncidentReponse)
def get_incident_by_id(
    incident_id: int,
    db: Session = Depends(get_db)
):
    incident = (
        db.query(Incident)
        .filter(Incident.id == incident_id)
        .first()
    )

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident introuvable"
        )

    return incident_to_response(incident)